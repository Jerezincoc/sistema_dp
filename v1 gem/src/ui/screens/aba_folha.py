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
import relatorios  # O motor que acabaste de criar
from src.core.database_manager import JsonDatabaseManager
from src.services.folha_service import FolhaService

class AbaFolha(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = JsonDatabaseManager()
        self.folha_service = FolhaService()
        self.funcionarios_dict = {}
        self.setup_ui()
        self._carregar_funcionarios()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # LADO ESQUERDO: LANÇAMENTOS
        self.frm_lança = ctk.CTkScrollableFrame(self, label_text="Lançamentos CLT (Rubricas)")
        self.frm_lança.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.frm_lança, text="Funcionário:").pack(padx=10, anchor="w")
        self.cb_func = ctk.CTkComboBox(self.frm_lança, width=350)
        self.cb_func.pack(pady=5, padx=10)

        self.ent_comp = self._add_input(self.frm_lança, "Competência (MM/AAAA):", "02/2026")
        self.ent_dias = self._add_input(self.frm_lança, "Dias Trabalhados:", "30")

        # Seção de Vencimentos
        ctk.CTkLabel(self.frm_lança, text="PROVENTOS", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        self.ent_gratifica = self._add_input(self.frm_lança, "Gratificação / Comissões (R$):")
        self.ent_peric = self._add_input(self.frm_lança, "Periculosidade (R$):")
        self.ent_insalub = self._add_input(self.frm_lança, "Insalubridade (R$):")

        # Seção de Descontos
        ctk.CTkLabel(self.frm_lança, text="DESCONTOS", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        self.ent_faltas = self._add_input(self.frm_lança, "Faltas / Atrasos (R$):")
        self.ent_vale = self._add_input(self.frm_lança, "Adiantamento / Vales (R$):")

        self.btn_processar = ctk.CTkButton(self.frm_lança, text="GERAR HOLERITE (DUAS VIAS)", 
                                          fg_color="#27ae60", hover_color="#219150",
                                          command=self._executar_calculo)
        self.btn_processar.pack(pady=25, padx=10, fill="x")

        # LADO DIREITO: PRÉVIA
        self.txt_previa = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=13))
        self.txt_previa.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.txt_previa.insert("1.0", "Aguardando cálculo...")

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

    def _executar_calculo(self):
        nome = self.cb_func.get()
        f_id = self.funcionarios_dict.get(nome)
        
        try:
            # Chama o cálculo matemático
            res = self.folha_service.processar_holerite_mensal(
                employee_id=f_id,
                mes_ano=self.ent_comp.get(),
                vencimentos_extras_clt=float(self.ent_gratifica.get() or 0)
            )
            
            clt = res["clt"]
            
            # Monta os itens para o PDF conforme os teus lançamentos
            itens_recibo = [
                ("Salário Base", f"{self.ent_dias.get()}d", clt['vencimentos']['salario_base'], 0.0),
                ("INSS", "-", 0.0, clt['descontos']['inss']),
                ("IRRF", "-", 0.0, clt['descontos']['irrf'])
            ]

            # Adiciona rubricas extras se tiverem valor
            if float(self.ent_gratifica.get() or 0) > 0:
                itens_recibo.append(("Gratificação", "-", float(self.ent_gratifica.get()), 0.0))
            if float(self.ent_vale.get() or 0) > 0:
                itens_recibo.append(("Adiantamento", "-", 0.0, float(self.ent_vale.get())))

            # 1. Atualiza Prévia
            self.txt_previa.delete("1.0", "end")
            self.txt_previa.insert("1.0", f"RESUMO CLT: {res['nome']}\nLíquido: R$ {clt['liquido']:.2f}")

            # 2. Chama o teu relatorios.py
            relatorios.gerar_recibo_folha(
                nome_func=res["nome"],
                dados_cabecalho={"Competência": res["competencia"]},
                tabela_itens=itens_recibo,
                totais={
                    "bruto": clt['vencimentos']['total_bruto'],
                    "descontos": clt['descontos']['total_descontos'],
                    "liquido": clt['liquido']
                }
            )
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao processar: {e}")