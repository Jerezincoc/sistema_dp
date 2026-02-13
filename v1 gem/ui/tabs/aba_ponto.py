import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from core import relatorios, ferramentas, calculos
from ui.widgets import FrameRubricas  # Lembre-se que renomeamos componentes para widgets

class AbaPonto(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # --- BLOCO 1: DADOS DA EMPRESA (OPCIONAIS) ---
        frm_emp = ttk.LabelFrame(self, text="Informações da Empresa (Cabeçalho Direito)", padding=10)
        frm_emp.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frm_emp, text="Empresa:").grid(row=0, column=0, sticky="w")
        self.ent_empresa = ttk.Entry(frm_emp, width=50)
        self.ent_empresa.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(frm_emp, text="CPF/CNPJ:").grid(row=0, column=2, sticky="w")
        self.ent_cpf = ttk.Entry(frm_emp, width=20)
        self.ent_cpf.grid(row=0, column=3, padx=5, pady=2, sticky="w")
        
        ttk.Label(frm_emp, text="Endereço:").grid(row=1, column=0, sticky="w")
        self.ent_endereco = ttk.Entry(frm_emp, width=80)
        self.ent_endereco.grid(row=1, column=1, columnspan=3, padx=5, pady=2, sticky="w")

        # --- BLOCO 2: DADOS DO TRABALHADOR ---
        frm_func = ttk.LabelFrame(self, text="Dados do Funcionário", padding=10)
        frm_func.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frm_func, text="Nome: *").grid(row=0, column=0, sticky="w")
        self.ent_nome = ttk.Entry(frm_func, width=40)
        self.ent_nome.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(frm_func, text="Cargo: *").grid(row=0, column=2, sticky="w")
        self.ent_cargo = ttk.Entry(frm_func, width=25)
        self.ent_cargo.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(frm_func, text="CTPS/Série:").grid(row=1, column=0, sticky="w")
        self.ent_ctps = ttk.Entry(frm_func, width=20)
        self.ent_ctps.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(frm_func, text="Série/UF:").grid(row=1, column=2, sticky="w")
        self.ent_serie = ttk.Entry(frm_func, width=25)
        self.ent_serie.grid(row=1, column=3, padx=5, pady=2, sticky="w")
        
        ttk.Label(frm_func, text="Jornada:").grid(row=2, column=0, sticky="w")
        self.ent_jornada = ttk.Entry(frm_func, width=40)
        self.ent_jornada.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(frm_func, text="Lotação:").grid(row=2, column=2, sticky="w")
        self.ent_lotacao = ttk.Entry(frm_func, width=25)
        self.ent_lotacao.grid(row=2, column=3, padx=5, pady=2, sticky="w")

        # --- BLOCO 3: SELEÇÃO DE PERÍODO ---
        frm_periodo = ttk.LabelFrame(self, text="Mês de Referência", padding=10)
        frm_periodo.pack(fill=tk.X, padx=10, pady=5)
        
        hoje = datetime.date.today()
        
        self.cb_mes = ttk.Combobox(frm_periodo, values=[str(i).zfill(2) for i in range(1, 13)], width=5, state="readonly")
        self.cb_mes.set(hoje.strftime("%m"))
        self.cb_mes.grid(row=0, column=0, padx=5)
        
        self.cb_ano = ttk.Combobox(frm_periodo, values=[str(i) for i in range(2024, 2031)], width=7, state="readonly")
        self.cb_ano.set("2026")
        self.cb_ano.grid(row=0, column=1, padx=5)

        # Botão de Geração
        ttk.Button(self, text="GERAR LISTA DE FREQUÊNCIA", command=self.acao_gerar).pack(pady=20, fill=tk.X, padx=100)

    def acao_gerar(self):
        # Validação de campos obrigatórios
        if not self.ent_nome.get() or not self.ent_cargo.get():
            messagebox.showwarning("Atenção", "Nome e Cargo são obrigatórios!")
            return
            
        # Coleta de dados (Tratando os opcionais com "...")
        dados = {
            "empresa": self.ent_empresa.get().upper() or "...",
            "cpf": self.ent_cpf.get() or "...",
            "endereco": self.ent_endereco.get().upper() or "...",
            "nome": self.ent_nome.get().upper(),
            "cargo": self.ent_cargo.get().upper(),
            "ctps": self.ent_ctps.get() or "...",
            "serie": self.ent_serie.get() or "...",
            "jornada": self.ent_jornada.get() or "...",
            "lotacao": self.ent_lotacao.get() or "...",
            "mes": int(self.cb_mes.get()),
            "ano": int(self.cb_ano.get())
        }
        
        relatorios.gerar_lista_frequencia(dados)