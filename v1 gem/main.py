import tkinter as tk
from tkinter import ttk, messagebox
import seguranca  # <--- O SEU ARQUIVO QUE VOCÊ MANDOU
import datetime

# Importando seus módulos de DP
from ui.tabs.aba_folha import AbaFolha
from ui.tabs.aba_ferias import AbaFerias
from ui.tabs.aba_rescisao import AbaRescisao
from ui.tabs.aba_ponto import AbaPonto

class SystemPro:
    def __init__(self, root):
        self.root = root
        self.root.title("System Pro - Gestão de DP")
        self.root.geometry("1280x800")
        
        # Estado do Sistema
        self.is_dark = True
        self.tema = {
            "dark": {"bg": "#121212", "side": "#1E1E1E", "txt": "#FFFFFF", "accent": "#0078D4"},
            "light": {"bg": "#F5F5F7", "side": "#FFFFFF", "txt": "#333333", "accent": "#005A9E"}
        }
        
        self.setup_estilos()
        self.mostrar_tela_login()

    def setup_estilos(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

    def limpar_tela(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- 1. TELA DE LOGIN (O GUARDIÃO) ---
    def mostrar_tela_login(self):
        self.limpar_tela()
        c = self.tema["dark" if self.is_dark else "light"]
        self.root.configure(bg=c["bg"])

        # Container Central
        container = tk.Frame(self.root, bg=c["bg"])
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container, text="SYSTEM PRO", font=("Segoe UI", 32, "bold"), 
                 fg=c["accent"], bg=c["bg"]).pack(pady=10)
        
        tk.Label(container, text="LOGIN DE ACESSO", font=("Segoe UI", 10, "bold"), 
                 fg=c["txt"], bg=c["bg"]).pack(pady=(0, 30))

        # Campos
        tk.Label(container, text="USUÁRIO", font=("Segoe UI", 9), fg=c["txt"], bg=c["bg"]).pack(anchor="w")
        self.ent_user = tk.Entry(container, width=35, font=("Segoe UI", 12), bd=0, highlightthickness=1)
        self.ent_user.pack(pady=5)
        self.ent_user.insert(0, "admin")

        tk.Label(container, text="SENHA", font=("Segoe UI", 9), fg=c["txt"], bg=c["bg"]).pack(anchor="w")
        self.ent_pass = tk.Entry(container, width=35, font=("Segoe UI", 12), show="*", bd=0, highlightthickness=1)
        self.ent_pass.pack(pady=5)
        self.ent_pass.bind('<Return>', lambda e: self.executar_login())

        # Botão Entrar
        btn_login = tk.Button(container, text="ENTRAR NO SISTEMA", font=("Segoe UI", 11, "bold"),
                              bg=c["accent"], fg="white", bd=0, padx=40, pady=12, 
                              cursor="hand2", command=self.executar_login)
        btn_login.pack(pady=30, fill="x")

    def executar_login(self):
        usuario = self.ent_user.get()
        senha = self.ent_pass.get()

        # USANDO A SUA FUNÇÃO DO ARQUIVO SEGURANCA.PY
        sucesso, mensagem = seguranca.verificar_login(usuario, senha)

        if sucesso:
            self.montar_dashboard()
        else:
            messagebox.showerror("Acesso Negado", mensagem)

    # --- 2. DASHBOARD (O SISTEMA PÓS-LOGIN) ---
    def montar_dashboard(self):
        self.limpar_tela()
        c = self.tema["dark" if self.is_dark else "light"]
        self.root.configure(bg=c["bg"])

        # SIDEBAR LATERAL
        self.sidebar = tk.Frame(self.root, bg=c["side"], width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="SYSTEM PRO", font=("Segoe UI", 18, "bold"), 
                 bg=c["side"], fg=c["accent"]).pack(pady=30)

        # CONTAINER DE CONTEÚDO
        self.content = tk.Frame(self.root, bg=c["bg"])
        self.content.pack(side="right", fill="both", expand=True)

        # MENU DE MÓDULOS
        itens_menu = [
            ("📄 Folha Mensal", AbaFolha),
            ("🏖️ Férias", AbaFerias),
            ("🤝 Rescisão", AbaRescisao),
            ("📅 Cartão Ponto", AbaPonto)
        ]

        for txt, cls in itens_menu:
            btn = tk.Button(self.sidebar, text=f"  {txt}", font=("Segoe UI", 11),
                            bg=c["side"], fg=c["txt"], bd=0, anchor="w",
                            padx=25, pady=15, cursor="hand2",
                            command=lambda cl=cls: self.trocar_aba(cl))
            btn.pack(fill="x")

        # Botão de Logout (Para voltar à tela de login)
        btn_logout = tk.Button(self.sidebar, text=" 🚪 Sair do Sistema", font=("Segoe UI", 10),
                               bg=c["side"], fg="#FF4444", bd=0, anchor="w",
                               padx=25, pady=20, cursor="hand2", command=self.mostrar_tela_login)
        btn_logout.pack(side="bottom", fill="x")

        # Inicia na aba de Folha
        self.trocar_aba(AbaFolha)

    def trocar_aba(self, classe_aba):
        for w in self.content.winfo_children(): w.destroy()
        aba = classe_aba(self.content)
        aba.pack(fill="both", expand=True, padx=40, pady=40)

if __name__ == "__main__":
    root = tk.Tk()
    # Centralizando a janela principal
    root.eval('tk::PlaceWindow . center')
    app = SystemPro(root)
    root.mainloop()