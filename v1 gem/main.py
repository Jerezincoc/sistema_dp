import tkinter as tk
from tkinter import ttk, messagebox
import os
import seguranca 

# Imports das abas conforme a estrutura de pastas core/ui
try:
    from ui.tabs.aba_folha import AbaFolha
    from ui.tabs.aba_ferias import AbaFerias
    from ui.tabs.aba_rescisao import AbaRescisao
    from ui.tabs.aba_ponto import AbaPonto
    from ui.tabs.aba_custos import AbaCustos
    from ui.tabs.aba_usuarios import AbaUsuarios
except ImportError as e:
    print(f"Erro de Importação: {e}. Verifique se as pastas core/ui existem.")

class SystemPro:
    def __init__(self, root):
        self.root = root
        self.root.title("System Pro 2026")
        self.root.geometry("1300x850")
        
        # --- ESTADOS E CONFIGURAÇÕES ---
        self.is_dark = True
        self.nome_aba_ativa = ""
        self.aba_instanciada = None
        self.botoes_menu = {}
        self.PATH_LAST_USER = os.path.join(os.getcwd(), ".last_user")
        
        # Paleta de Cores "System Pro"
        self.temas = {
            "dark": {
                "bg": "#121212", "card": "#1E1E1E", "sidebar": "#181818",
                "texto": "#FFFFFF", "accent": "#0078D4", "hover": "#333333"
            },
            "light": {
                "bg": "#F5F5F7", "card": "#FFFFFF", "sidebar": "#EBEBEB",
                "texto": "#1C1C1E", "accent": "#005A9E", "hover": "#D1D1D1"
            }
        }
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Inicia pela tela de login
        self.mostrar_tela_login()

    def aplicar_estilo_global(self):
        t = self.temas["dark" if self.is_dark else "light"]
        self.root.configure(bg=t["bg"])
        
        # Matando o Cinza Geladeira no TTK
        self.style.configure("TFrame", background=t["bg"])
        self.style.configure("TLabel", background=t["bg"], foreground=t["texto"], font=("Segoe UI", 10))
        self.style.configure("TLabelframe", background=t["card"], foreground=t["accent"], bordercolor=t["hover"])
        self.style.configure("TLabelframe.Label", background=t["card"], foreground=t["accent"], font=("Segoe UI", 10, "bold"))
        self.style.configure("TEntry", fieldbackground=t["card"], foreground=t["texto"], insertbackground=t["texto"])
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"))

    # --- 🔐 TELA DE LOGIN ---
    def mostrar_tela_login(self):
        for w in self.root.winfo_children(): w.destroy()
        self.aplicar_estilo_global()
        t = self.temas["dark" if self.is_dark else "light"]

        # Card de Login centralizado
        card = tk.Frame(self.root, bg=t["card"], padx=45, pady=45, highlightthickness=1, highlightbackground=t["hover"])
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="SYSTEM PRO", font=("Segoe UI", 26, "bold"), bg=t["card"], fg=t["accent"]).pack(pady=(0, 10))
        tk.Label(card, text="LOGIN DE ACESSO", font=("Segoe UI", 9, "bold"), bg=t["card"], fg=t["texto"]).pack(pady=(0, 30))

        # Campo Usuário com Memória
        tk.Label(card, text="USUÁRIO", font=("Segoe UI", 9), bg=t["card"], fg=t["texto"]).pack(anchor="w")
        self.ent_user = tk.Entry(card, width=35, font=("Segoe UI", 12), bd=0, bg=t["bg"], fg=t["texto"], insertbackground=t["texto"])
        self.ent_user.pack(pady=(5, 20), ipady=10)

        # Lógica de preenchimento do último logado
        if os.path.exists(self.PATH_LAST_USER):
            with open(self.PATH_LAST_USER, "r") as f: self.ent_user.insert(0, f.read().strip())
        else:
            self.ent_user.insert(0, "admin")

        # Campo Senha
        tk.Label(card, text="SENHA", font=("Segoe UI", 9), bg=t["card"], fg=t["texto"]).pack(anchor="w")
        self.ent_pass = tk.Entry(card, width=35, font=("Segoe UI", 12), show="*", bd=0, bg=t["bg"], fg=t["texto"], insertbackground=t["texto"])
        self.ent_pass.pack(pady=(5, 30), ipady=10)
        self.ent_pass.bind('<Return>', lambda e: self.verificar_acesso())

        # Botão Acessar
        tk.Button(card, text="ENTRAR NO SISTEMA", font=("Segoe UI", 11, "bold"),
                  bg=t["accent"], fg="white", bd=0, pady=12, cursor="hand2",
                  activebackground=t["accent"], command=self.verificar_acesso).pack(fill="x")

    def verificar_acesso(self):
        u = self.ent_user.get()
        s = self.ent_pass.get()
        sucesso, msg = seguranca.verificar_login(u, s)
        
        if sucesso:
            # Salva o usuário para a próxima vez
            with open(self.PATH_LAST_USER, "w") as f: f.write(u)
            self.montar_dashboard()
        else:
            messagebox.showerror("Acesso Negado", msg)

    # --- 📊 DASHBOARD ---
    def montar_dashboard(self):
        for w in self.root.winfo_children(): w.destroy()
        t = self.temas["dark" if self.is_dark else "light"]
        self.aplicar_estilo_global()

        # Sidebar Lateral
        self.sidebar = tk.Frame(self.root, bg=t["sidebar"], width=260)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="SYSTEM PRO", font=("Segoe UI", 18, "bold"), 
                 bg=t["sidebar"], fg=t["accent"], pady=35).pack()

        # Área de Conteúdo Principal
        self.content_area = tk.Frame(self.root, bg=t["bg"])
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        menu = [
            ("📄 Folha Mensal", AbaFolha),
            ("🏖️ Férias", AbaFerias),
            ("🤝 Rescisão", AbaRescisao),
            ("📅 Cartão Ponto", AbaPonto),
            ("💰 Custos Mensais", AbaCustos),
            ("👥 Gestão Usuários", AbaUsuarios)
        ]

        for txt, cls in menu:
            btn = tk.Button(self.sidebar, text=f"  {txt}", font=("Segoe UI", 11),
                            bg=t["sidebar"], fg=t["texto"], bd=0, anchor="w",
                            padx=30, pady=18, cursor="hand2",
                            command=lambda c=cls, n=txt: self.trocar_aba(c, n))
            btn.pack(fill="x")
            self.botoes_menu[txt] = btn

        # Botões de Rodapé da Sidebar
        tk.Button(self.sidebar, text="🚪 SAIR DO SISTEMA", font=("Segoe UI", 9, "bold"),
                  bg=t["sidebar"], fg="#FF4444", bd=0, pady=15, command=self.mostrar_tela_login).pack(side="bottom", fill="x")
        
        tk.Button(self.sidebar, text="🌓 MUDAR TEMA", font=("Segoe UI", 9),
                  bg=t["sidebar"], fg=t["texto"], bd=0, pady=10, command=self.toggle_tema).pack(side="bottom", fill="x")

        # Inicia na aba de Folha
        self.trocar_aba(AbaFolha, "📄 Folha Mensal")

    def toggle_tema(self):
        self.is_dark = not self.is_dark
        self.aplicar_estilo_global()
        if self.aba_instanciada:
            self.trocar_aba(self.aba_instanciada.__class__, self.nome_aba_ativa)

    def trocar_aba(self, classe_aba, nome):
        for w in self.content_area.winfo_children(): w.destroy()
        self.nome_aba_ativa = nome
        self.aba_instanciada = classe_aba(self.content_area)
        self.aba_instanciada.pack(fill="both", expand=True, padx=35, pady=35)
        self.atualizar_menu_visual()

    def atualizar_menu_visual(self):
        t = self.temas["dark" if self.is_dark else "light"]
        for nome, btn in self.botoes_menu.items():
            if nome == self.nome_aba_ativa:
                btn.config(bg=t["accent"], fg="white")
            else:
                btn.config(bg=t["sidebar"], fg=t["texto"])

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemPro(root)
    root.mainloop()