import customtkinter as ctk
from src.core.session import SessionManager
from src.models.user_model import ModuloAcesso, Role

class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master: any, session_manager: SessionManager, on_logout: callable):
        super().__init__(master)
        self.session_manager = session_manager
        self.on_logout = on_logout
        self.user = self.session_manager.current_user
        
        self._setup_layout()

    def _setup_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- MENU LATERAL (SIDEBAR) ---
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        lbl_brand = ctk.CTkLabel(
            self.sidebar, 
            text="SUDO SYS", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#3498db"
        )
        lbl_brand.pack(pady=(30, 5))
        
        lbl_user = ctk.CTkLabel(
            self.sidebar, 
            text=f"Olá, {self.user.username}\n[{self.user.role.value}]", 
            font=ctk.CTkFont(size=12)
        )
        lbl_user.pack(pady=(0, 30))

        # --- BOTÕES DE NAVEGAÇÃO (Com controle de acesso) ---
        if self.user.can_access(ModuloAcesso.CLT):
            btn_fopag = ctk.CTkButton(self.sidebar, text="Folha Legal (CLT)", command=lambda: self._show_content("fopag"))
            btn_fopag.pack(pady=10, padx=20, fill="x")

        if self.user.can_access(ModuloAcesso.EXTRA):
            btn_extra = ctk.CTkButton(self.sidebar, text="Gestão Extra (Por Fora)", fg_color="#e67e22", hover_color="#d35400", command=lambda: self._show_content("extra"))
            btn_extra.pack(pady=10, padx=20, fill="x")

        # Separador para área administrativa
        ctk.CTkFrame(self.sidebar, height=2, fg_color="gray30").pack(pady=20, padx=20, fill="x")

        if self.user.can_access(ModuloAcesso.CONFIG):
            btn_config = ctk.CTkButton(self.sidebar, text="Configurações", fg_color="transparent", border_width=1, command=lambda: self._show_content("config"))
            btn_config.pack(pady=10, padx=20, fill="x")

        # Botão de Logout fixo no rodapé
        btn_logout = ctk.CTkButton(self.sidebar, text="Sair do Sistema", fg_color="#e74c3c", hover_color="#c0392b", command=self.on_logout)
        btn_logout.pack(side="bottom", pady=20, padx=20, fill="x")

        # --- ÁREA PRINCIPAL DE CONTEÚDO ---
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)
        
        # Inicia com uma tela de boas-vindas vazia
        self.current_view = None
        self._show_content("welcome")

    def _show_content(self, view_name: str):
        """Gerencia a troca de telas dentro da área principal do Dashboard."""
        if self.current_view is not None:
            self.current_view.destroy()

        self.current_view = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.current_view.grid(row=0, column=0, sticky="nsew")

        if view_name == "welcome":
            ctk.CTkLabel(self.current_view, text="Selecione um módulo no menu lateral.", font=ctk.CTkFont(size=18)).pack(expand=True)
        elif view_name == "fopag":
            ctk.CTkLabel(self.current_view, text="Módulo FOPAG (CLT) - Em Desenvolvimento", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=50)
        elif view_name == "extra":
            ctk.CTkLabel(self.current_view, text="Módulo EXTRA (Por Fora) - Em Desenvolvimento", font=ctk.CTkFont(size=24, weight="bold"), text_color="#e67e22").pack(pady=50)
        elif view_name == "config":
            ctk.CTkLabel(self.current_view, text="Painel de Configurações Administrativas", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=50)