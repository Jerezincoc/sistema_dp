# -*- coding: utf-8 -*-
"""
interface.py
============
Interface gráfica principal do Sistema DP com abas e controle de acesso.
Corrige o problema crítico de interface vazia após login.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import traceback

# Módulos do sistema DP (com validação de importação)
try:
    from aba_folha import AbaFolha
    from aba_ferias import AbaFerias
    from aba_rescisao import AbaRescisao
    from aba_custos import AbaCustos
    from aba_ponto import AbaPonto
    MODULOS_ABAS_DISPONIVEIS = True
except ImportError as e:
    print(f"❌ ERRO AO IMPORTAR MÓDULOS DAS ABAS: {e}")
    print("⚠️ Verifique se todos os arquivos .py estão na pasta correta!")
    MODULOS_ABAS_DISPONIVEIS = False
    traceback.print_exc()


class SistemaDPApp:
    """Aplicação principal do Sistema DP com abas e controle de acesso."""
    
    def __init__(self, root, usuario_logado):
        self.root = root
        self.usuario_logado = usuario_logado
        
        # Configuração da janela principal
        self.root.title(f"Sistema DP 2026 - Usuário: {usuario_logado}")
        self._centralizar_janela(1000, 750)
        
        # Estilo visual
        style = ttk.Style()
        style.theme_use('clam')
        self._configurar_estilos(style)
        
        # Interface
        self._criar_menu_superior()
        self._criar_abas()
        self._criar_rodape()
    
    def _centralizar_janela(self, largura, altura):
        """Centraliza a janela na tela do usuário."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        pos_x = (screen_width - largura) // 2
        pos_y = (screen_height - altura) // 2
        self.root.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
        self.root.resizable(True, True)
    
    def _configurar_estilos(self, style):
        """Configura estilos personalizados para botões e elementos."""
        style.configure("Accent.TButton", 
                       foreground="white", 
                       background="#2c7be5",
                       font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton",
                 background=[("active", "#1a68d1")],
                 foreground=[("active", "white")])
        
        # Estilo para a aba selecionada
        style.configure("TNotebook.Tab", 
                       padding=[10, 5],
                       font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                 background=[("selected", "#2c7be5")],
                 foreground=[("selected", "white")])
    
    def _criar_menu_superior(self):
        """Cria a barra de menu com opções de sistema e gestão de usuários (admin only)."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Sistema (visível para todos)
        sistema_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Sistema", menu=sistema_menu)
        sistema_menu.add_command(label="Sair", command=self.root.quit)
        
        # Menu Gestão de Usuários (apenas para admin)
        if self.usuario_logado == "admin" and MODULOS_ABAS_DISPONIVEIS:
            user_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Gestão de Usuários", menu=user_menu)
            user_menu.add_command(
                label="Cadastrar Novo Usuário", 
                command=self._abrir_janela_cadastro,
                accelerator="Ctrl+U"
            )
            self.root.bind("<Control-u>", lambda e: self._abrir_janela_cadastro())
    
    def _criar_abas(self):
        """Cria e configura o notebook com todas as abas funcionais."""
        # Verifica se os módulos estão disponíveis
        if not MODULOS_ABAS_DISPONIVEIS:
            self._mostrar_erro_abas()
            return
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Instanciação das abas (com tratamento de erros)
        self.aba_folha = self._instanciar_aba(AbaFolha, "Folha Mensal")
        self.aba_ferias = self._instanciar_aba(AbaFerias, "Férias")
        self.aba_rescisao = self._instanciar_aba(AbaRescisao, "Rescisão")
        self.aba_custos = self._instanciar_aba(AbaCustos, "Custos")
        self.aba_ponto = self._instanciar_aba(AbaPonto, "Ponto")
        
        # Adição das abas ao notebook
        self._adicionar_aba(self.aba_folha, "  📄 Folha Mensal   ")
        self._adicionar_aba(self.aba_ferias, "  🏖️ Férias   ")
        self._adicionar_aba(self.aba_rescisao, "  ⚖️ Rescisão   ")
        self._adicionar_aba(self.aba_custos, "  💰 Custos   ")
        self._adicionar_aba(self.aba_ponto, "  🕒 Ponto   ")
        
        # Garante que a primeira aba seja visível
        if self.notebook.winfo_children():
            self.notebook.select(0)
    
    def _instanciar_aba(self, classe_aba, nome_aba):
        """Instancia uma aba com tratamento de erros."""
        try:
            return classe_aba(self.notebook)
        except Exception as e:
            print(f"❌ ERRO AO CRIAR ABA '{nome_aba}': {e}")
            traceback.print_exc()
            messagebox.showerror(
                "Erro na Inicialização",
                f"Não foi possível carregar a aba '{nome_aba}'.\n"
                "Verifique se o arquivo da aba está correto e completo.",
                parent=self.root
            )
            return None
    
    def _adicionar_aba(self, aba, texto):
        """Adiciona uma aba ao notebook com tratamento de erros."""
        if aba is not None:
            self.notebook.add(aba, text=texto)
        else:
            # Se a aba não foi criada, adiciona uma aba de erro
            frm_erro = ttk.Frame(self.notebook)
            lbl_erro = ttk.Label(
                frm_erro,
                text="❌ ERRO: Aba não carregada corretamente",
                font=("Segoe UI", 12, "bold"),
                foreground="red"
            )
            lbl_erro.pack(pady=20)
            self.notebook.add(frm_erro, text=f"❌ {texto}")
    
    def _criar_rodape(self):
        """Cria rodapé informativo com versão e ano."""
        ano_atual = datetime.datetime.now().year
        rodape = ttk.Label(
            self.root, 
            text=f"Sistema DP v2.0 - © {ano_atual} | Usuário: {self.usuario_logado}", 
            font=("Arial", 8),
            foreground="gray",
            anchor="center"
        )
        rodape.pack(side=tk.BOTTOM, fill=tk.X, pady=2)
    
    def _abrir_janela_cadastro(self):
        """Abre janela modal para cadastro de novos usuários (admin only)."""
        if self.usuario_logado != "admin":
            messagebox.showerror("Acesso Negado", "Apenas administradores podem criar usuários.")
            return
        
        # Cria janela modal
        top = tk.Toplevel(self.root)
        top.title("Novo Usuário")
        top.geometry("350x220")
        top.resizable(False, False)
        top.transient(self.root)
        top.grab_set()  # Foca exclusivamente nesta janela
        
        # Centraliza sobre a janela principal
        top.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - top.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - top.winfo_height()) // 2
        top.geometry(f"+{x}+{y}")
        
        # Conteúdo da janela
        ttk.Label(top, text="Cadastrar Novo Usuário", 
                 font=("Segoe UI", 12, "bold")).pack(pady=(15, 10))
        
        frame_inputs = ttk.Frame(top, padding=10)
        frame_inputs.pack(fill=tk.X, padx=20)
        
        ttk.Label(frame_inputs, text="Login:").pack(anchor="w")
        ent_user = ttk.Entry(frame_inputs, width=30)
        ent_user.pack(fill=tk.X, pady=(0, 10))
        ent_user.focus()
        
        ttk.Label(frame_inputs, text="Senha:").pack(anchor="w")
        ent_pass = ttk.Entry(frame_inputs, width=30, show="•")
        ent_pass.pack(fill=tk.X)
        
        def _salvar_usuario():
            usuario = ent_user.get().strip()
            senha = ent_pass.get().strip()
            
            # Validação básica
            if not usuario or not senha:
                messagebox.showwarning("Atenção", "Preencha ambos os campos.", parent=top)
                return
            if len(senha) < 6:
                messagebox.showwarning("Atenção", "A senha deve ter pelo menos 6 caracteres.", parent=top)
                return
            
            # Criação do usuário via módulo de segurança
            try:
                from seguranca import criar_usuario
                sucesso, msg = criar_usuario(usuario, senha)
                if sucesso:
                    messagebox.showinfo("Sucesso", f"Usuário '{usuario}' criado com sucesso!", parent=top)
                    top.destroy()
                else:
                    messagebox.showerror("Erro", msg, parent=top)
            except Exception as e:
                messagebox.showerror("Erro Crítico", f"Falha ao criar usuário:\n{str(e)}", parent=top)
        
        # Botões de ação
        frame_btns = ttk.Frame(top)
        frame_btns.pack(fill=tk.X, padx=20, pady=15)
        
        ttk.Button(
            frame_btns, 
            text="Cancelar", 
            command=top.destroy,
            width=12
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            frame_btns, 
            text="Salvar Usuário", 
            command=_salvar_usuario,
            style="Accent.TButton",
            width=15
        ).pack(side=tk.RIGHT)
        
        # Bind Enter para salvar
        ent_pass.bind("<Return>", lambda e: _salvar_usuario())
    
    def _mostrar_erro_abas(self):
        """Exibe mensagem de erro quando os módulos das abas não estão disponíveis."""
        # Limpa a janela atual
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Título
        lbl_titulo = ttk.Label(
            self.root,
            text="❌ ERRO DE INICIALIZAÇÃO",
            font=("Segoe UI", 16, "bold"),
            foreground="red"
        )
        lbl_titulo.pack(pady=(40, 20))
        
        # Mensagem de erro
        lbl_mensagem = ttk.Label(
            self.root,
            text="Não foi possível carregar as abas do sistema.\n"
                 "Verifique se todos os arquivos .py estão na pasta correta:\n\n"
                 "aba_folha.py\n"
                 "aba_ferias.py\n"
                 "aba_rescisao.py\n"
                 "aba_custos.py\n"
                 "aba_ponto.py",
            font=("Segoe UI", 10),
            justify="center"
        )
        lbl_mensagem.pack(padx=20, pady=20)
        
        # Botão de sair
        btn_sair = ttk.Button(
            self.root,
            text="Sair do Sistema",
            command=self.root.quit,
            style="Accent.TButton",
            width=15
        )
        btn_sair.pack(pady=20)
        
        # Rodapé
        rodape = ttk.Label(
            self.root,
            text="Sistema DP v2.0 - © 2026 | Erro de inicialização",
            font=("Arial", 8),
            foreground="gray"
        )
        rodape.pack(side=tk.BOTTOM, fill=tk.X, pady=2)


# =================================================================
# 🔐 PONTO DE ENTRADA SEGURO (para execução direta do módulo)
# =================================================================
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = SistemaDPApp(root, "admin")
        root.mainloop()
    except Exception as e:
        print(f"\n❌ ERRO FATAL AO INICIAR A INTERFACE:\n{e}")
        traceback.print_exc()
        input("\nPressione ENTER para sair...")