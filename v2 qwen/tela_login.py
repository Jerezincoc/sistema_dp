# -*- coding: utf-8 -*-
"""
tela_login.py
=============
Tela de autenticação segura com callbacks robustos para integração com main.py.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import seguranca


class LoginApp:
    """Interface gráfica de login com validação segura."""
    
    def __init__(self, root, on_success_callback, on_cancel_callback=None):
        """
        Inicializa a tela de login.
        
        Args:
            root: Janela Tk() principal (única instância da aplicação)
            on_success_callback: Função chamada após login bem-sucedido (recebe nome do usuário)
            on_cancel_callback: Função opcional chamada ao fechar a janela (default: root.quit)
        """
        self.root = root
        self.root.title("🔐 Autenticação - Sistema DP 2026")
        self.on_success = on_success_callback
        self.on_cancel = on_cancel_callback or root.quit
        
        # Centralização da janela
        largura, altura = 400, 280
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        x = (sw - largura) // 2
        y = (sh - altura) // 2
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._ao_fechar)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura a interface gráfica com estilo profissional."""
        # Frame principal com padding
        frm = ttk.Frame(self.root, padding=25)
        frm.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(
            frm, 
            text="🔐 LOGIN DO SISTEMA", 
            font=("Segoe UI", 16, "bold"),
            foreground="#2c7be5"
        ).pack(pady=(0, 25))
        
        # Campo Usuário
        ttk.Label(frm, text="Usuário:", font=("Segoe UI", 10)).pack(anchor="w")
        self.ent_user = ttk.Entry(frm, width=35, font=("Segoe UI", 11))
        self.ent_user.pack(fill=tk.X, pady=(0, 15))
        self.ent_user.focus()
        
        # Campo Senha
        ttk.Label(frm, text="Senha:", font=("Segoe UI", 10)).pack(anchor="w")
        self.ent_pass = ttk.Entry(frm, width=35, show="•", font=("Segoe UI", 11))
        self.ent_pass.pack(fill=tk.X, pady=(0, 20))
        
        # Botão de acesso
        btn_acessar = ttk.Button(
            frm, 
            text="✅ ACESSAR SISTEMA", 
            command=self._tentar_login,
            style="Accent.TButton"
        )
        btn_acessar.pack(fill=tk.X, ipady=8)
        
        # Dica de teclado
        ttk.Label(
            frm, 
            text="Dica: Pressione ENTER para logar", 
            font=("Segoe UI", 8), 
            foreground="gray"
        ).pack(pady=(15, 0))
        
        # CORREÇÃO CRÍTICA 1: Bind sem espaços extras nos eventos
        self.root.bind("<Return>", lambda e: self._tentar_login())
        self.ent_pass.bind("<Escape>", lambda e: self._ao_fechar())
    
    def _tentar_login(self):
        """Valida credenciais e executa callbacks apropriados."""
        usuario = self.ent_user.get().strip()
        senha = self.ent_pass.get().strip()
        
        if not usuario or not senha:
            messagebox.showwarning(
                "Atenção", 
                "⚠️ Preencha usuário e senha para continuar.", 
                parent=self.root
            )
            self.ent_user.focus() if not usuario else self.ent_pass.focus()
            return
        
        # CORREÇÃO CRÍTICA 2: Variável "mensagem" sem espaço no nome
        sucesso, mensagem = seguranca.verificar_login(usuario, senha)
        
        if sucesso:
            # Login bem-sucedido: chama callback com nome do usuário
            # CORREÇÃO CRÍTICA 3: on_success sem espaço antes do parêntese
            self.root.after(100, lambda: self.on_success(usuario))
        else:
            # Falha na autenticação
            messagebox.showerror(
                "Acesso Negado", 
                f"❌ {mensagem}\n\nDica: O usuário 'admin' com senha 'admin123' é a chave de recuperação.",
                parent=self.root
            )
            self.ent_pass.delete(0, tk.END)
            self.ent_pass.focus()
    
    def _ao_fechar(self):
        """Tratamento seguro do fechamento da janela de login."""
        if messagebox.askokcancel(
            "Cancelar Login", 
            "Deseja realmente sair do Sistema DP?", 
            parent=self.root
        ):
            self.on_cancel()


# =================================================================
# 🔒 TESTE AUTOMÁTICO (executado apenas se rodar este arquivo diretamente)
# =================================================================
if __name__ == "__main__":
    root = tk.Tk()
    
    def sucesso(usuario):
        messagebox.showinfo("Login", f"Usuário '{usuario}' autenticado com sucesso!")
        root.quit()
    
    def cancelar():
        print("Login cancelado pelo usuário")
        root.quit()
    
    app = LoginApp(root, on_success_callback=sucesso, on_cancel_callback=cancelar)
    root.mainloop()