import customtkinter as ctk
from typing import Callable
from datetime import datetime
from src.core.session import SessionManager

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master: any, session_manager: SessionManager, on_login_success: Callable[[], None]):
        super().__init__(master)
        self.session_manager = session_manager
        self.on_login_success = on_login_success
        self._setup_ui()
        self._load_last_user()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self, width=420, height=520, corner_radius=20, border_width=0)
        self.container.grid(row=0, column=0, padx=20, pady=20)
        self.container.grid_propagate(False)
        
        self.lbl_brand = ctk.CTkLabel(
            self.container, 
            text="SUDO SYS", 
            font=ctk.CTkFont(family="Roboto", size=36, weight="bold"),
            text_color="#3498db"
        )
        self.lbl_brand.pack(pady=(50, 5))

        self.lbl_subtitle = ctk.CTkLabel(
            self.container, 
            text="Acesso Corporativo", 
            font=ctk.CTkFont(family="Roboto", size=16),
            text_color="gray"
        )
        self.lbl_subtitle.pack(pady=(0, 45))

        self.entry_username = ctk.CTkEntry(
            self.container, placeholder_text="Usuário", width=300, height=45,
            font=ctk.CTkFont(family="Roboto", size=14), border_width=2, border_color="#5F6368", corner_radius=10
        )
        self.entry_username.pack(pady=(0, 20))
        self.entry_username.bind("<FocusIn>", lambda e: self.entry_username.configure(border_color="#3498db", text_color="#E8EAED"))
        self.entry_username.bind("<FocusOut>", lambda e: self.entry_username.configure(border_color="#5F6368", text_color="gray"))

        self.entry_password = ctk.CTkEntry(
            self.container, placeholder_text="Senha", show="*", width=300, height=45,
            font=ctk.CTkFont(family="Roboto", size=14), border_width=2, border_color="#5F6368", corner_radius=10
        )
        self.entry_password.pack(pady=(0, 10))
        self.entry_password.bind("<FocusIn>", lambda e: self.entry_password.configure(border_color="#3498db", text_color="#E8EAED"))
        self.entry_password.bind("<FocusOut>", lambda e: self.entry_password.configure(border_color="#5F6368", text_color="gray"))

        self.lbl_forgot = ctk.CTkLabel(
            self.container, text="Esqueci minhas credenciais", font=ctk.CTkFont(family="Roboto", size=13, underline=True),
            text_color="#3498db", cursor="hand2"
        )
        self.lbl_forgot.pack(pady=(0, 25))
        self.lbl_forgot.bind("<Button-1>", lambda e: self._open_forgot_password_modal())

        self.lbl_error = ctk.CTkLabel(self.container, text="", text_color="#e74c3c", font=ctk.CTkFont(family="Roboto", size=14))
        self.lbl_error.pack(pady=(0, 15))

        self.btn_login = ctk.CTkButton(
            self.container, text="ENTRAR NO SISTEMA", width=300, height=50,
            font=ctk.CTkFont(family="Roboto", size=15, weight="bold"),
            fg_color="#3498db", hover_color="#2980b9", corner_radius=10, command=self._attempt_login
        )
        self.btn_login.pack(pady=(0, 30))
        
        self.entry_password.bind("<Return>", lambda event: self._attempt_login())
        self.entry_username.bind("<Return>", lambda event: self._attempt_login())

    def _load_last_user(self):
        prefs = self.session_manager.db.get_record("configuracoes", "local_prefs")
        if prefs and "last_user" in prefs and prefs["last_user"]:
            self.entry_username.insert(0, prefs["last_user"])
            self.entry_password.focus()
        else:
            self.entry_username.focus()

    def _save_last_user(self, username: str):
        self.session_manager.db.save_record("configuracoes", "local_prefs", {"last_user": username})

    def _attempt_login(self):
        self.lbl_error.configure(text="")
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            self.lbl_error.configure(text="Preencha todos os campos.")
            return

        self.btn_login.configure(state="disabled", text="Autenticando...", fg_color="#5F6368")
        self.update_idletasks()
        
        success = self.session_manager.login(username, password)
        if success:
            self._save_last_user(username)
            self.on_login_success()
        else:
            self.lbl_error.configure(text="Credenciais inválidas.")
            self.btn_login.configure(state="normal", text="ENTRAR NO SISTEMA", fg_color="#3498db")
            self.entry_password.delete(0, 'end')
            self.entry_password.focus()

    def _open_forgot_password_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Recuperação")
        modal.geometry("350x280")
        modal.transient(self.master)
        modal.grab_set()
        
        modal.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - 175
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - 140
        modal.geometry(f"+{x}+{y}")

        ctk.CTkLabel(modal, text="Solicitação de Reset", font=ctk.CTkFont(family="Roboto", size=16)).pack(pady=(30, 20))
        entry_req_user = ctk.CTkEntry(modal, placeholder_text="Usuário para recuperação", width=280, height=40)
        entry_req_user.pack(pady=10)

        lbl_msg = ctk.CTkLabel(modal, text="", font=ctk.CTkFont(size=12))
        lbl_msg.pack(pady=5)

        def send_request():
            user_req = entry_req_user.get().strip()
            if not user_req:
                lbl_msg.configure(text="Informe o usuário.", text_color="#e74c3c")
                return
            
            self.session_manager.db.save_record("reset_requests", user_req, {
                "username": user_req, "status": "pendente", "data_solicitacao": datetime.now().isoformat()
            })
            lbl_msg.configure(text="Enviado ao administrador.", text_color="#2ecc71")
            btn_send.configure(state="disabled")
            modal.after(2000, modal.destroy)

        btn_send = ctk.CTkButton(modal, text="Confirmar Solicitação", command=send_request, width=280, height=40, fg_color="#3498db")
        btn_send.pack(pady=20)