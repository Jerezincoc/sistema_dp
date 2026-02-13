# Arquivo: ui/interface.py
import tkinter as tk
from tkinter import ttk
from ui.tabs.aba_folha import AbaFolha
from ui.tabs.aba_ferias import AbaFerias
from ui.tabs.aba_rescisao import AbaRescisao
from ui.tabs.aba_ponto import AbaPonto
from ui.tabs.aba_custos import AbaCustos

class SistemaDPApp:
    def __init__(self, root, usuario_logado):
        self.root = root
        self.usuario_logado = usuario_logado
        self.cores = {"bg": "#121212", "sidebar": "#1E1E1E", "accent": "#0078D4", "texto": "#FFFFFF"}
        self.setup_layout()

    def setup_layout(self):
        # Aqui vai toda aquela lógica da Sidebar que fizemos
        self.sidebar = tk.Frame(self.root, bg=self.cores["sidebar"], width=240)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        # ... (Lógica de botões e navegação)