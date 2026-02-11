# Arquivo: interface.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime

# IMPORTANTE: Importar o módulo de segurança para poder criar usuários
import seguranca 

# Importa as abas
from aba_folha import AbaFolha
from aba_ferias import AbaFerias
from aba_rescisao import AbaRescisao
from aba_custos import AbaCustos
from aba_ponto import AbaPonto
class SistemaDPApp:
    def __init__(self, root, usuario_logado):
        self.root = root
        self.usuario_logado = usuario_logado
        self.root.title(f"Sistema DP 2026 - Usuário: {usuario_logado}")
        
        # Centraliza
        largura = 1000
        altura = 750
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        pos_x = (screen_width // 2) - (largura // 2)
        pos_y = (screen_height // 2) - (altura // 2)
        self.root.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
        
        style = ttk.Style()
        style.theme_use('clam')

        # --- NOVO: BARRA DE MENU SUPERIOR ---
        self.criar_menu_superior()
        # ------------------------------------

        # Criação das Abas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.aba_folha = AbaFolha(self.notebook)
        self.aba_ferias = AbaFerias(self.notebook)
        self.aba_rescisao = AbaRescisao(self.notebook)
        self.aba_custos = AbaCustos(self.notebook)
        self.aba_ponto = AbaPonto(self.notebook)
        
        self.notebook.add(self.aba_folha, text="  Folha Mensal  ")
        self.notebook.add(self.aba_ferias, text="  Férias  ")
        self.notebook.add(self.aba_rescisao, text="  Rescisão  ")
        self.notebook.add(self.aba_custos, text="  Custos  ")
        self.notebook.add(self.aba_ponto, text="  Ponto  ")
        
        lbl_rodape = ttk.Label(root, text=f"Sistema DP v2.0 - {datetime.datetime.now().year}", font=("Arial", 8), foreground="gray")
        lbl_rodape.pack(side=tk.BOTTOM, pady=2)

    def criar_menu_superior(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Sistema (Todos vêem)
        arquivo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Sistema", menu=arquivo_menu)
        arquivo_menu.add_command(label="Sair", command=self.root.quit)
        
        # --- A TRAVA: Só cria o menu se for o admin ---
        if self.usuario_logado == "admin":
            user_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Gestão de Usuários", menu=user_menu)
            user_menu.add_command(label="Cadastrar Novo Usuário", command=self.abrir_janela_cadastro)

    def abrir_janela_cadastro(self):
        # Cria uma janelinha por cima (Toplevel)
        top = tk.Toplevel(self.root)
        top.title("Novo Usuário")
        top.geometry("300x200")
        top.resizable(False, False)
        
        # Centraliza a janelinha no pai
        x = self.root.winfo_x() + (self.root.winfo_width()//2) - 150
        y = self.root.winfo_y() + (self.root.winfo_height()//2) - 100
        top.geometry(f"+{x}+{y}")
        
        ttk.Label(top, text="Cadastrar Novo Acesso", font=("Arial", 10, "bold")).pack(pady=10)
        
        ttk.Label(top, text="Novo Login:").pack()
        ent_user = ttk.Entry(top)
        ent_user.pack(pady=2)
        
        ttk.Label(top, text="Nova Senha:").pack()
        ent_pass = ttk.Entry(top, show="*")
        ent_pass.pack(pady=2)
        
        def salvar():
            u = ent_user.get().strip()
            s = ent_pass.get().strip()
            if not u or not s:
                messagebox.showwarning("Atenção", "Preencha tudo.", parent=top)
                return
            
            # Chama nosso módulo de segurança existente
            sucesso, msg = seguranca.criar_usuario(u, s)
            
            if sucesso:
                messagebox.showinfo("Sucesso", f"Usuário '{u}' criado!", parent=top)
                top.destroy()
            else:
                messagebox.showerror("Erro", msg, parent=top)
                
        ttk.Button(top, text="Salvar Usuário", command=salvar).pack(pady=15, fill=tk.X, padx=20)