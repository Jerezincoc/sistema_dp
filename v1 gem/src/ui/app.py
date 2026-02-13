import customtkinter as ctk
from src.core.session import SessionManager
from src.ui.screens.login_screen import LoginScreen

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("v1 gem - ERP Modular")
        self.geometry("1024x768")
        self.minsize(800, 600)
        
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        self.session_manager = SessionManager()
        self.current_frame = None
        
        self.show_login()

    def _switch_frame(self, frame_class, **kwargs):
        """Destrói a tela atual e renderiza a nova de forma limpa, liberando memória."""
        if self.current_frame is not None:
            self.current_frame.destroy()
            
        self.current_frame = frame_class(self, **kwargs)
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):
        self._switch_frame(
            LoginScreen, 
            session_manager=self.session_manager, 
            on_login_success=self.show_dashboard
        )

    def show_dashboard(self):
        from src.ui.screens.dashboard import DashboardScreen
        self._switch_frame(DashboardScreen, session_manager=self.session_manager, on_logout=self.logout)
        if self.current_frame is not None:
            self.current_frame.destroy()
            
        self.current_frame = ctk.CTkFrame(self)
        self.current_frame.pack(fill="both", expand=True)
        
        user = self.session_manager.current_user
        
        msg = f"Acesso Liberado\n\nUsuário: {user.username}\nNível: {user.role.value}"
        lbl_welcome = ctk.CTkLabel(
            self.current_frame, 
            text=msg, 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        lbl_welcome.pack(expand=True)
        
        btn_logout = ctk.CTkButton(
            self.current_frame, 
            text="Sair (Logout)", 
            command=self.logout,
            fg_color="#FF4C4C",
            hover_color="#CC0000"
        )
        btn_logout.pack(pady=40)

    def logout(self):
        self.session_manager.logout()
        self.show_login()