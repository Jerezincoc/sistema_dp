import sys
import os
from pathlib import Path

# --- DESTRAVA O IMPORT DO RELATORIOS.PY ---
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
# ------------------------------------------

import customtkinter as ctk
from tkinter import messagebox
import relatorios  
from src.core.database_manager import JsonDatabaseManager

class AbaExtra(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = JsonDatabaseManager()
        self.funcionarios_dict = {}
        self.setup_ui()
        self._carregar_funcionarios()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # LADO ESQUERDO: LANÇAMENTOS EXTRA
        self.frm_extra = ctk.CTkScrollableFrame(self, label_text="Pagamentos Extraoficiais")
        self.frm_extra.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.frm_extra, text="Selecione o Funcionário:", text_color="#e67e22").pack(pady=(10, 0), padx=10, anchor="w")
        self.cb_func = ctk.CTkComboBox(self.frm_extra, width=350)
        self.cb_func.pack(pady=5, padx=10)

        self.ent_data = self._add_input(self.frm_extra, "Data do Pagamento:", "13/02/2026")
        
        ctk.CTkLabel(self.frm_extra, text="VALORES", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        self.ent_comissao = self._add_input(self.frm_extra, "Comissão (R$):")
        self.ent_premio = self._add_input(self.frm_extra, "Prémio / Bónus (R$):")
        self.ent_ajuda = self._add_input(self.frm_extra, "Ajuda de Custo (R$):")

        ctk.CTkLabel(self.frm_extra, text="DEDUÇÕES", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        self.ent_vale = self._add_input(self.frm_extra, "Vales / Adiantamentos (R$):")

        self.btn_gerar = ctk.CTkButton(
            self.frm_extra, 
            text="GERAR RECIBO EXTRA (PDF)", 
            fg_color="#e67e22", 
            hover_color="#d35400",
            command=self._processar_extra
        )
        self.btn_gerar.pack(pady=25, padx=10, fill="x")

        # LADO DIREITO: PRÉVIA
        self.txt_previa = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=13), text_color="#e67e22")
        self.txt_previa.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.txt_previa.insert("1.0", "Aguardando lançamento extra...")

    def _add_input(self, master, label, placeholder="0.00"):
        ctk.CTkLabel(master, text=label).pack(padx=10, anchor="w")
        entry = ctk.CTkEntry(master, placeholder_text=placeholder)
        entry.pack(pady=5, padx=10, fill="x")
        return entry

    def _carregar_funcionarios(self):
        regs = self.db.read_table("funcionarios")
        nomes = [f"{d['nome']}" for f_id, d in regs.items()]
        self.funcionarios_dict = {d['nome']: f_id for f_id, d in regs.items()}
        self.cb_func.configure(values=nomes)
        if nomes: self.cb_func.set(nomes[0])

    def _processar_extra(self):
        nome = self.cb_func.get()
        
        try:
            v_com = float(self.ent_comissao.get() or 0)
            v_pre = float(self.ent_premio.get() or 0)
            v_aju = float(self.ent_ajuda.get() or 0)
            v_val = float(self.ent_vale.get() or 0)
            
            total_bruto = v_com + v_pre + v_aju
            liquido = total_bruto - v_val

            # Itens para o PDF
            itens_pdf = []
            if v_com > 0: itens_pdf.append(("Comissão de Vendas", "-", v_com, 0.0))
            if v_pre > 0: itens_pdf.append(("Prémio de Desempenho", "-", v_pre, 0.0))
            if v_aju > 0: itens_pdf.append(("Ajuda de Custo", "-", v_aju, 0.0))
            if v_val > 0: itens_pdf.append(("Vale / Adiantamento", "-", 0.0, v_val))

            # 1. Prévia na tela
            self.txt_previa.delete("1.0", "end")
            self.txt_previa.insert("1.0", f"RECIBO EXTRA: {nome}\nLíquido: R$ {liquido:.2f}")

            # 2. Gera o PDF com o modelo de duas vias
            relatorios.gerar_recibo_folha(
                nome_func=nome,
                dados_cabecalho={"Competência": "PAGAMENTO EXTRA", "Data": self.ent_data.get()},
                tabela_itens=itens_pdf,
                totais={
                    "bruto": total_bruto,
                    "descontos": v_val,
                    "liquido": liquido
                }
            )

        except Exception as e:
            messagebox.showerror("Erro", f"Erro no cálculo: {e}")