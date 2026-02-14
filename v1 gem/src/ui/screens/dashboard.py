import customtkinter as ctk
from src.core.session import SessionManager

class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, session_manager: SessionManager, on_logout: callable):
        super().__init__(master)
        self.session_manager = session_manager
        self.on_logout = on_logout
        
        # Configuração do Layout Principal (Grid)
        self.grid_columnconfigure(0, weight=0) # Menu fixo
        self.grid_columnconfigure(1, weight=1) # Conteúdo expande
        self.grid_rowconfigure(0, weight=1)

        # 1. CRIAR SIDEBAR (BARRA LATERAL)
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#2c3e50")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="SUDO SYS", font=ctk.CTkFont(size=22, weight="bold"), text_color="white").pack(pady=30)

        # Botões de Navegação
        self.btn_clt = ctk.CTkButton(self.sidebar, text="Folha Legal (CLT)", height=40, command=lambda: self._show_content("fopag"))
        self.btn_clt.pack(pady=10, padx=20, fill="x")

        self.btn_extra = ctk.CTkButton(self.sidebar, text="Gestão EXTRA", height=40, command=lambda: self._show_content("extra"))
        self.btn_extra.pack(pady=10, padx=20, fill="x")

        # Botão de Sair embaixo
        self.btn_logout = ctk.CTkButton(self.sidebar, text="Sair do Sistema", fg_color="#c0392b", hover_color="#e74c3c", command=self.on_logout)
        self.btn_logout.pack(side="bottom", pady=20, padx=20, fill="x")

        # 2. ÁREA DE CONTEÚDO
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self._show_welcome()

    def _show_content(self, view_name):
        # Limpa tudo que está na tela antes de mostrar a nova
        for widget in self.container.winfo_children():
            widget.destroy()

        if view_name == "fopag":
            from src.ui.screens.aba_folha import AbaFolha
            AbaFolha(self.container).pack(fill="both", expand=True)
        
        elif view_name == "extra":
            from src.ui.screens.aba_extra import AbaExtra
            AbaExtra(self.container).pack(fill="both", expand=True)

    def _show_welcome(self):
        user = self.session_manager.current_user
        ctk.CTkLabel(self.container, text=f"Painel de Controle", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(50, 10))
        ctk.CTkLabel(self.container, text=f"Operador: {user.username} | Nível: {user.role}", text_color="gray").pack()
        ctk.CTkLabel(self.container, text="Selecione um módulo à esquerda para processar pagamentos.", font=ctk.CTkFont(size=14)).pack(pady=40)