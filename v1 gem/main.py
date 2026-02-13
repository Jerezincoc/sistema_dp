import tkinter as tk
from tkinter import ttk, messagebox
import seguranca
import os

# Imports das abas (Mantenha os seus imports aqui)
from ui.tabs.aba_folha import AbaFolha
from ui.tabs.aba_ferias import AbaFerias
from ui.tabs.aba_rescisao import AbaRescisao
from ui.tabs.aba_ponto import AbaPonto
from ui.tabs.aba_custos import AbaCustos
from ui.tabs.aba_usuarios import AbaUsuarios # Será movida para Opções em breve

class SystemPro:
    def __init__(self, root):
        self.root = root
        self.root.title("System Pro 2026")
        self.root.geometry("1300x850")
        
        self.is_dark = True
        self.perfil_usuario = "OBSERVADOR" # Nível padrão por segurança
        self.nome_aba_ativa = ""
        self.botoes_menu = {}
        
        # Paleta de Cores
        self.temas = {
            "dark": {"bg": "#121212", "card": "#1E1E1E", "sidebar": "#181818", "txt": "#FFFFFF", "accent": "#0078D4", "hover": "#333333"},
            "light": {"bg": "#F5F5F7", "card": "#FFFFFF", "sidebar": "#EBEBEB", "txt": "#1C1C1E", "accent": "#005A9E", "hover": "#D1D1D1"}
        }
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.mostrar_tela_login()

    # --- 🖌️ O MOTOR DE TEMAS "MATA-CINZA" ---
    def aplicar_tema_full(self, container=None):
        """ Percorre todos os widgets recursivamente e força a cor do tema """
        t = self.temas["dark" if self.is_dark else "light"]
        alvo = container if container else self.root
        
        alvo.configure(bg=t["bg"])
        
        for widget in alvo.winfo_children():
            # Se for um widget padrão (tk.Label, tk.Frame, etc)
            try:
                if isinstance(widget, (tk.Frame, tk.Label, tk.LabelFrame, tk.Canvas)):
                    widget.configure(bg=t["bg"], fg=t["txt"] if hasattr(widget, 'fg') else None)
                elif isinstance(widget, tk.Button):
                    # Botões da Sidebar a gente pula pois eles têm estilo próprio
                    if widget.master != self.sidebar:
                        widget.configure(bg=t["accent"], fg="white")
                elif isinstance(widget, tk.Entry):
                    widget.configure(bg=t["card"], fg=t["txt"], insertbackground=t["txt"])
            except:
                pass
            
            # Chama a função para os filhos deste widget (Recursividade)
            if widget.winfo_children():
                self.aplicar_tema_full(widget)

    def verificar_acesso(self):
        u = self.ent_user.get()
        s = self.ent_pass.get()
        
        # Agora o verificar_login retorna (Sucesso, Perfil)
        sucesso, perfil = seguranca.verificar_login(u, s)
        
        if sucesso:
            self.perfil_usuario = perfil
            self.montar_dashboard()
        else:
            messagebox.showerror("Acesso Negado", "Usuário ou Senha incorretos.")

    def montar_dashboard(self):
        for w in self.root.winfo_children(): w.destroy()
        t = self.temas["dark" if self.is_dark else "light"]

        # 1. SIDEBAR
        self.sidebar = tk.Frame(self.root, bg=t["sidebar"], width=260)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # 2. ÁREA DE CONTEÚDO
        self.content_area = tk.Frame(self.root, bg=t["bg"])
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- 🛡️ FILTRO DE HIERARQUIA NO MENU ---
        # Lista: (Texto, Classe, Nível Mínimo)
        menu_config = [
            ("📄 Folha Mensal", AbaFolha, 1),      # Operador+
            ("🏖️ Férias", AbaFerias, 1),           # Operador+
            ("🤝 Rescisão", AbaRescisao, 1),       # Operador+
            ("📅 Cartão Ponto", AbaPonto, 1),       # Operador+
            ("💰 Custos Mensais", AbaCustos, 2),    # Admin+
        ]

        # Peso do utilizador atual
        peso_user = seguranca.NIVEIS.get(self.perfil_usuario, 0)

        for txt, cls, nivel_min in menu_config:
            if peso_user >= nivel_min:
                btn = tk.Button(self.sidebar, text=f"  {txt}", font=("Segoe UI", 11),
                                bg=t["sidebar"], fg=t["txt"], bd=0, anchor="w",
                                padx=25, pady=15, cursor="hand2",
                                command=lambda c=cls, n=txt: self.trocar_aba(c, n))
                btn.pack(fill="x")
                self.botoes_menu[txt] = btn

        # --- BOTÃO DE OPÇÕES (ADMIN/MESTRE APENAS) ---
        if peso_user >= 2:
            btn_opt = tk.Button(self.sidebar, text="  ⚙️ Opções do Sistema", font=("Segoe UI", 11, "bold"),
                                bg=t["sidebar"], fg=t["accent"], bd=0, anchor="w",
                                padx=25, pady=15, cursor="hand2",
                                command=lambda: self.abrir_aba_opcoes())
            btn_opt.pack(side="bottom", fill="x", pady=5)

        self.aplicar_tema_full()
        self.trocar_aba(AbaFolha, "📄 Folha Mensal")

    def abrir_aba_opcoes(self):
        """ 
        Aqui criaremos a aba que você pediu: sem sidebar, 
        com gestão de usuários e tabelas.
        """
        messagebox.showinfo("System Pro", f"Acesso nível {self.perfil_usuario} autorizado!")
        # Próximo passo: Criar a AbaOpcoes real