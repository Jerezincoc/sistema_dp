# -*- coding: utf-8 -*-
"""
aba_folha.py
============
Aba para gestão de folha de pagamento: lançamentos e geração de recibo.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import relatorios
import ferramentas
from componentes import FrameRubricas


class AbaFolha(ttk.Frame):
    """Aba para gestão de folha de pagamento: lançamentos e geração de recibo."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
    
    def _mascara_data(self, event, campo):
        """Aplica máscara de data DD/MM/AAAA ao campo de entrada."""
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab", "Escape"):
            return
        
        texto = "".join(filter(str.isdigit, campo.get()))[:8]
        
        if len(texto) > 4:
            texto = f"{texto[:2]}/{texto[2:4]}/{texto[4:]}"
        elif len(texto) > 2:
            texto = f"{texto[:2]}/{texto[2:]}"
        
        campo.delete(0, tk.END)
        campo.insert(0, texto)
    
    def setup_ui(self):
        # --- BLOCO 1: DADOS DO CONTRATO ---
        frm_topo = ttk.LabelFrame(self, text="Dados do Contrato", padding=10)
        frm_topo.pack(fill=tk.X, padx=10, pady=5)
        
        # Linha 1: Nome, Admissão e Cargo
        ttk.Label(frm_topo, text="Funcionário:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_nome = ttk.Entry(frm_topo, width=30)
        self.ent_nome.grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(frm_topo, text="Admissão:").grid(row=0, column=2, sticky="w", padx=10)
        self.ent_admissao = ttk.Entry(frm_topo, width=10)
        self.ent_admissao.grid(row=0, column=3, sticky="w", padx=5)
        self.ent_admissao.bind("<KeyRelease>", lambda event: self._mascara_data(event, self.ent_admissao))
        self.ent_admissao.insert(0, datetime.datetime.now().strftime("%d/%m/%Y"))
        
        ttk.Label(frm_topo, text="Cargo:").grid(row=0, column=4, sticky="w", padx=10)
        self.ent_cargo = ttk.Entry(frm_topo, width=20)
        self.ent_cargo.grid(row=0, column=5, sticky="w", padx=5)
        
        # Linha 2: Salário, Dias Trabalhados e Competência
        ttk.Label(frm_topo, text="Salário Base:").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_salario = ttk.Entry(frm_topo, width=12)
        self.ent_salario.grid(row=1, column=1, sticky="w", padx=5)
        self.ent_salario.insert(0, "0.00")
        
        ttk.Label(frm_topo, text="Dias Trab.:").grid(row=1, column=2, sticky="w", padx=10)
        self.ent_dias = ttk.Entry(frm_topo, width=5)
        self.ent_dias.grid(row=1, column=3, sticky="w", padx=5)
        self.ent_dias.insert(0, "30")
        
        ttk.Label(frm_topo, text="Competência:").grid(row=1, column=4, sticky="w", padx=10)
        self.ent_comp = ttk.Entry(frm_topo, width=10)
        self.ent_comp.grid(row=1, column=5, sticky="w", padx=5)
        self.ent_comp.insert(0, datetime.datetime.now().strftime("%m/%Y"))
        
        # Linha 3: Tipo de Contrato (CLT vs Pro-labore)
        self.var_tipo = tk.StringVar(value="CLT")
        frm_radio = ttk.Frame(frm_topo)
        frm_radio.grid(row=2, column=0, columnspan=6, pady=10, sticky="w")
        
        ttk.Radiobutton(
            frm_radio, text="CLT (Padrão)", variable=self.var_tipo, 
            value="CLT", command=self._ao_mudar_tipo
        ).pack(side="left")
        
        ttk.Radiobutton(
            frm_radio, text="Pro-Labore (Sócio)", variable=self.var_tipo, 
            value="PRO", command=self._ao_mudar_tipo
        ).pack(side="left", padx=15)
        
        # --- BLOCO 2: LANÇAMENTOS ---
        self.frm_proventos = FrameRubricas(
            self, "Proventos (Créditos)", tipo_evento="provento"
        )
        self.frm_proventos.pack(fill=tk.X, padx=10, pady=5)
        
        self.frm_descontos = FrameRubricas(
            self, "Descontos (Débitos)", tipo_evento="desconto"
        )
        self.frm_descontos.pack(fill=tk.X, padx=10, pady=5)
        
        # --- BLOCO 3: BOTÕES DE AÇÃO ---
        frm_botoes = ttk.Frame(self)
        frm_botoes.pack(fill=tk.X, padx=50, pady=20)
        
        ttk.Button(
            frm_botoes, text="🧹 Limpar Tudo", 
            command=self._limpar_tela, style="Accent.TButton"
        ).pack(side="left", fill=tk.X, expand=True, padx=5, ipady=5)
        
        ttk.Button(
            frm_botoes, text="📄 GERAR RECIBO", 
            command=self._gerar_recibo, style="Accent.TButton"
        ).pack(side="left", fill=tk.X, expand=True, padx=5, ipady=5)
    
    def _ao_mudar_tipo(self):
        """Atualiza os frames de rubricas conforme o tipo de contrato."""
        tipo = self.var_tipo.get()
        self.frm_proventos.mudar_tipo_contrato(tipo)
        self.frm_descontos.mudar_tipo_contrato(tipo)
    
    def _limpar_tela(self):
        """Limpa todos os campos da interface."""
        self.ent_nome.delete(0, tk.END)
        self.ent_cargo.delete(0, tk.END)
        self.ent_salario.delete(0, tk.END)
        self.ent_salario.insert(0, "0.00")
        self.ent_dias.delete(0, tk.END)
        self.ent_dias.insert(0, "30")
        self.ent_admissao.delete(0, tk.END)
        self.ent_admissao.insert(0, datetime.datetime.now().strftime("%d/%m/%Y"))
        self.frm_proventos.limpar_tudo()
        self.frm_proventos.add_linha()
        self.frm_descontos.limpar_tudo()
        self.frm_descontos.add_linha()
    
    def _gerar_recibo(self):
        """Gera o recibo de pagamento com base nos dados preenchidos."""
        nome = self.ent_nome.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "⚠️ Preencha o nome do funcionário.")
            self.ent_nome.focus()
            return
        
        try:
            salario_contratual = ferramentas.str_para_float(self.ent_salario.get())
            if salario_contratual < 0:
                messagebox.showerror("Erro", "❌ Salário não pode ser negativo.")
                self.ent_salario.focus()
                return
        except ValueError:
            messagebox.showerror("Erro", "❌ Salário inválido. Use formato numérico (ex: 2500.50).")
            self.ent_salario.focus()
            return
        
        try:
            dias_trab = int(self.ent_dias.get())
            if dias_trab < 0 or dias_trab > 31:
                messagebox.showwarning("Atenção", "⚠️ Dias trabalhados deve estar entre 0 e 31.")
                self.ent_dias.focus()
                return
        except ValueError:
            dias_trab = 30
        
        salario_calculado = salario_contratual
        desc_salario = "Salário Base"
        
        if self.var_tipo.get() == "PRO":
            desc_salario = "Pro-Labore"
        
        if dias_trab < 30 and salario_contratual > 0:
            salario_calculado = (salario_contratual / 30) * dias_trab
            desc_salario += f" ({dias_trab}/30 dias)"
        
        dados_prov = self.frm_proventos.get_dados_calculados(salario_contratual)
        dados_desc = self.frm_descontos.get_dados_calculados(salario_contratual)
        
        itens_recibo = []
        
        itens_recibo.append({
            'descricao': desc_salario,
            'ref': f"{dias_trab}d",
            'valor': salario_calculado,
            'desconto': 0.0
        })
        
        for desc, valor in dados_prov["itens"]:
            itens_recibo.append({
                'descricao': desc,
                'ref': "-",
                'valor': valor,
                'desconto': 0.0
            })
        
        for desc, valor in dados_desc["itens"]:
            itens_recibo.append({
                'descricao': desc,
                'ref': "-",
                'valor': 0.0,
                'desconto': valor
            })
        
        cabecalho = {
            "Competência": self.ent_comp.get().strip() or datetime.datetime.now().strftime("%m/%Y"),
            "Cargo": self.ent_cargo.get().strip() or "Não Informado",
            "CPF": "",
            "Admissão": self.ent_admissao.get().strip() or "Não Informado",
            "Salário Contratual": ferramentas.formatar_moeda(salario_contratual)
        }
        
        try:
            relatorios.gerar_recibo_html(
                titulo_doc="Recibo de Pagamento",
                tipo_arquivo="Folha",
                nome_funcionario=nome,
                dados_cabecalho=cabecalho,
                tabela_itens=itens_recibo,
                totais={}
            )
        except Exception as e:
            messagebox.showerror(
                "Erro na Geração", 
                f"❌ Falha ao gerar recibo:\n{str(e)}"
            )
            import traceback
            traceback.print_exc()