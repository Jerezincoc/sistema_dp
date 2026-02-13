# Arquivo: aba_folha.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from core import relatorios, ferramentas, calculos
from ui.widgets import FrameRubricas  # Lembre-se que renomeamos componentes para widgets

class AbaFolha(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def formatar_data(self, event, campo):
        # Se o usuário apertar Backspace, não faz nada para permitir apagar
        if event.keysym == "BackSpace": 
            return
        
        # Pega o texto e remove as barras para reformatar
        texto = campo.get().replace("/", "")
        
        # Limita a 8 dígitos (DDMMAAAA)
        if len(texto) > 8:
            texto = texto[:8]
        
        novo_texto = ""
        for i, char in enumerate(texto):
            if i == 2 or i == 4:
                novo_texto += "/"
            novo_texto += char
        
        # Substitui o valor no campo
        campo.delete(0, "end")
        campo.insert(0, novo_texto)
        
    def setup_ui(self):
        # --- CABEÇALHO ---
        frm_topo = ttk.LabelFrame(self, text="Dados do Contrato", padding=10)
        frm_topo.pack(fill=tk.X, padx=10, pady=5)
        
        # Linha 1: Nome, Admissão e Cargo
        ttk.Label(frm_topo, text="Funcionário:").grid(row=0, column=0, sticky="w")
        self.ent_nome = ttk.Entry(frm_topo, width=30)
        self.ent_nome.grid(row=0, column=1, sticky="w", padx=5)
        
        # --- NOVO CAMPO AQUI ---
        ttk.Label(frm_topo, text="Admissão:").grid(row=0, column=2, sticky="w")
        self.ent_admissao = ttk.Entry(frm_topo, width=10)
        self.ent_admissao.grid(row=0, column=3, sticky="w", padx=5)
        self.ent_admissao.bind("<KeyRelease>", lambda event: self.formatar_data(event, self.ent_admissao))

        # (Empurrei o Cargo para a coluna 4 e 5)
        ttk.Label(frm_topo, text="Cargo:").grid(row=0, column=4, sticky="w")
        self.ent_cargo = ttk.Entry(frm_topo, width=20)
        self.ent_cargo.grid(row=0, column=5, sticky="w", padx=5)

        # Linha 2: Salário, Dias e Competência
        ttk.Label(frm_topo, text="Salário Base:").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_salario = ttk.Entry(frm_topo, width=12)
        self.ent_salario.grid(row=1, column=1, sticky="w", padx=5)
        
        ttk.Label(frm_topo, text="Dias Trab.:").grid(row=1, column=2, sticky="w")
        self.ent_dias = ttk.Entry(frm_topo, width=5)
        self.ent_dias.insert(0, "30") 
        self.ent_dias.grid(row=1, column=3, sticky="w", padx=5)

        ttk.Label(frm_topo, text="Competência:").grid(row=1, column=4, sticky="w")
        self.ent_comp = ttk.Entry(frm_topo, width=10)
        self.ent_comp.insert(0, datetime.datetime.now().strftime("%m/%Y"))
        self.ent_comp.grid(row=1, column=5, sticky="w", padx=5)

        # Linha 3: Tipo (CLT vs Pro-labore)
        self.var_tipo = tk.StringVar(value="CLT")
        frm_radio = ttk.Frame(frm_topo)
        frm_radio.grid(row=2, column=0, columnspan=6, pady=10, sticky="w")
        
        rad_clt = ttk.Radiobutton(frm_radio, text="CLT (Padrão)", variable=self.var_tipo, value="CLT", command=self.ao_mudar_tipo)
        rad_clt.pack(side="left")
        
        rad_pro = ttk.Radiobutton(frm_radio, text="Pro-Labore (Sócio)", variable=self.var_tipo, value="PRO", command=self.ao_mudar_tipo)
        rad_pro.pack(side="left", padx=15)

        # --- LANÇAMENTOS ---
        self.frm_proventos = FrameRubricas(self, "Proventos (Créditos)", tipo_evento="provento")
        self.frm_proventos.pack(fill=tk.X, padx=10, pady=5)
        
        self.frm_descontos = FrameRubricas(self, "Descontos (Débitos)", tipo_evento="desconto")
        self.frm_descontos.pack(fill=tk.X, padx=10, pady=5)
        
        # --- BOTÕES DE AÇÃO ---
        frm_botoes = ttk.Frame(self)
        frm_botoes.pack(fill=tk.X, padx=50, pady=20)
        
        btn_limpar = ttk.Button(frm_botoes, text="Limpar Tudo", command=self.limpar_tela)
        btn_limpar.pack(side="left", fill=tk.X, expand=True, padx=5)
        
        btn_calc = ttk.Button(frm_botoes, text="GERAR RECIBO", command=self.gerar_recibo)
        btn_calc.pack(side="left", fill=tk.X, expand=True, padx=5)

    def ao_mudar_tipo(self):
        novo_tipo = self.var_tipo.get()
        self.frm_proventos.mudar_tipo_contrato(novo_tipo)
        self.frm_descontos.mudar_tipo_contrato(novo_tipo)

    def limpar_tela(self):
        self.ent_nome.delete(0, tk.END)
        self.ent_cargo.delete(0, tk.END)
        self.ent_salario.delete(0, tk.END)
        self.ent_dias.delete(0, tk.END)
        self.ent_dias.insert(0, "30")
        self.frm_proventos.limpar_tudo()
        self.frm_proventos.add_linha() 
        self.frm_descontos.limpar_tudo()
        self.frm_descontos.add_linha()

    def gerar_recibo(self):
        nome = self.ent_nome.get().strip()
        cargo = self.ent_cargo.get().strip()
        comp = self.ent_comp.get().strip()
        dt_admissao = self.ent_admissao.get().strip()
        
        if not nome: return messagebox.showwarning("Atenção", "Preencha o Nome.")
        
        # AQUI MUDOU: Aceita zero, só não aceita negativo
        salario_contratual = ferramentas.str_para_float(self.ent_salario.get())
        if salario_contratual < 0: return messagebox.showerror("Erro", "Salário não pode ser negativo.")
        
        try: dias_trab = int(self.ent_dias.get())
        except: dias_trab = 30
        
        # Lógica de Descrição
        salario_calculado = salario_contratual
        desc_salario = "Salário Base"
        
        if self.var_tipo.get() == "PRO":
            desc_salario = "Pro-Labore"
        
        if dias_trab < 30:
            salario_calculado = (salario_contratual / 30) * dias_trab
            desc_salario += f" ({dias_trab}/30 dias)"

        # Coleta dados
        dados_prov = self.frm_proventos.get_dados_calculados(salario_contratual)
        dados_desc = self.frm_descontos.get_dados_calculados(salario_contratual)
        
        # Monta lista
        itens_recibo = []
        
        # Se for zero, adiciona mesmo assim (pois o usuário pode querer registrar que o fixo é zero)
        # Se preferir que suma quando é zero, basta por um if salario_calculado > 0:
        itens_recibo.append((desc_salario, f"{dias_trab}d", salario_calculado, 0.0))
        
        for n, v in dados_prov["itens"]: itens_recibo.append((n, "-", v, 0.0))
        for n, v in dados_desc["itens"]: itens_recibo.append((n, "-", 0.0, v))

        cabecalho = {
            "Competência": comp,
            "Cargo": cargo,
            "Admissão": dt_admissao,
            "Salário Contratual": ferramentas.formatar_moeda(salario_contratual)
        }
        
        relatorios.gerar_recibo_html("Recibo de Pagamento", "Folha", nome, cabecalho, itens_recibo, {})