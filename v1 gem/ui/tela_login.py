import tkinter as tk
from tkinter import ttk, messagebox
import seguranca

class LoginApp:
    def __init__(self, root, on_success_callback):
        self.root = root
        self.root.title("Autenticação - DP 2026")
        self.on_success = on_success_callback
        
        # Centralização da janela
        w, h = 350, 250
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        root.resizable(False, False)
        self.setup_ui()
        
    def setup_ui(self):
        frm = ttk.Frame(self.root, padding=25)
        frm.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frm, text="LOGIN DO SISTEMA", font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        ttk.Label(frm, text="Usuário:").pack(anchor="w")
        self.ent_user = ttk.Entry(frm)
        self.ent_user.pack(fill=tk.X, pady=(0, 10))
        self.ent_user.focus()
        
        ttk.Label(frm, text="Senha:").pack(anchor="w")
        self.ent_pass = ttk.Entry(frm, show="*")
        self.ent_pass.pack(fill=tk.X, pady=(0, 20))
        
        # O erro acontecia aqui porque a função abaixo não era localizada
        btn = ttk.Button(frm, text="ACESSAR", command=self.tentar_entrar)
        btn.pack(fill=tk.X, ipady=5)
        
        # Faz o botão Enter do teclado também tentar o login
        self.root.bind('<Return>', lambda e: self.tentar_entrar())

    # ATENÇÃO: Esta função deve estar na mesma linha (coluna) que o 'def setup_ui'
# No arquivo tela_login.py, altere apenas o final da função tentar_entrar:

    def tentar_entrar(self):
        user = self.ent_user.get().strip()
        pwd = self.ent_pass.get().strip()
        
        sucesso, msg = seguranca.verificar_login(user, pwd)
        
        if sucesso:
            self.root.destroy()
            # AQUI A MUDANÇA: Passamos o 'user' para a função de sucesso
            self.on_success(user) 
        else:
            messagebox.showerror("Erro de Acesso", msg)
