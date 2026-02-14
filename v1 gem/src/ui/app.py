import customtkinter as ctk
from src.core.session import SessionManager
from src.ui.screens.login_screen import LoginScreen
from src.ui.screens.dashboard import DashboardScreen

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SUDO SYS - ERP Modular")
        self.geometry("1100x700")
        
        # Gerenciador de Sessão
        self.session_manager = SessionManager()
        
        # Container principal onde as telas serão trocadas
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        
        # Iniciar na tela de login
        self.show_login()

    def clear_container(self):
        """Limpa a tela atual para carregar a próxima."""
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_container()
        # Passa a função show_dashboard como callback de sucesso
        self.login_frame = LoginScreen(
            self.container, 
            self.session_manager, 
            on_login_success=self.show_dashboard
        )
        self.login_frame.pack(fill="both", expand=True)

    def show_dashboard(self):
        self.clear_container()
        # CARREGA O DASHBOARD REAL
        self.dashboard_frame = DashboardScreen(
            self.container, 
            self.session_manager, 
            on_logout=self.show_login
        )
        self.dashboard_frame.pack(fill="both", expand=True)