# Arquivo: aba_custos.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from datetime import timedelta
import relatorios
import ferramentas
import calculos
from componentes import FrameRubricas

class AbaCustos(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # --- BLOCO 1: DADOS BASE ---
        frm_base = ttk.LabelFrame(self, text="1. Dados de Contratação e Projeção", padding=10)
        frm_base.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frm_base, text="Salário Base:").grid(row=0, column=0, sticky="w")
        self.ent_salario = ttk.Entry(frm_base, width=15); self.ent_salario.grid(row=0, column=1, padx=5)
        
        ttk.Label(frm_base, text="Filhos (<14 anos):").grid(row=0, column=2, padx=10)
        self.ent_filhos = ttk.Entry(frm_base, width=8); self.ent_filhos.insert(0, "0"); self.ent_filhos.grid(row=0, column=3)

        ttk.Label(frm_base, text="Est. Admissão:").grid(row=1, column=0, pady=10, sticky="w")
        self.ent_adm = ttk.Entry(frm_base, width=15); self.ent_adm.insert(0, datetime.datetime.now().strftime("%d/%m/%Y")); self.ent_adm.grid(row=1, column=1, padx=5)
        self.ent_adm.bind("<KeyRelease>", lambda e: self.mascara_data(e, self.ent_adm))

        ttk.Label(frm_base, text="Meses Projetados:").grid(row=1, column=2, padx=10)
        self.ent_meses = ttk.Entry(frm_base, width=8); self.ent_meses.insert(0, "12"); self.ent_meses.grid(row=1, column=3)

        ttk.Label(frm_base, text="Regime Empresa:").grid(row=1, column=4, padx=10)
        self.cb_regime = ttk.Combobox(frm_base, values=["Simples Nacional", "Lucro Presumido/Real"], state="readonly", width=20)
        self.cb_regime.current(0); self.cb_regime.grid(row=1, column=5)

        # --- BLOCO 2: BENEFÍCIOS (CUSTO X DESCONTO) ---
        frm_ben = ttk.LabelFrame(self, text="2. Benefícios (VT e VR)", padding=10)
        frm_ben.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frm_ben, text="Escala:").grid(row=0, column=0, sticky="w")
        self.cb_escala = ttk.Combobox(frm_ben, values=["5x2 (Seg a Sex)", "6x1 (Seg a Sáb)", "6x1 (Sáb 4h)"], state="readonly", width=18)
        self.cb_escala.current(0); self.cb_escala.grid(row=0, column=1, padx=5)

        ttk.Label(frm_ben, text="VT Diário (R$):").grid(row=0, column=2, padx=10)
        self.ent_vt_dia = ttk.Entry(frm_ben, width=10); self.ent_vt_dia.insert(0, "0"); self.ent_vt_dia.grid(row=0, column=3)

        ttk.Label(frm_ben, text="VR Diário (R$):").grid(row=1, column=0, pady=10, sticky="w")
        self.ent_vr_dia = ttk.Entry(frm_ben, width=10); self.ent_vr_dia.insert(0, "0"); self.ent_vr_dia.grid(row=1, column=1, padx=5)

        ttk.Label(frm_ben, text="Desc. VR (Fixo R$):").grid(row=1, column=2, padx=10)
        self.ent_desc_vr = ttk.Entry(frm_ben, width=10); self.ent_desc_vr.insert(0, "0"); self.ent_desc_vr.grid(row=1, column=3)

        ttk.Label(frm_ben, text="Plano Saúde/Odonto:").grid(row=1, column=4, padx=10)
        self.ent_saude = ttk.Entry(frm_ben, width=12); self.ent_saude.insert(0, "0"); self.ent_saude.grid(row=1, column=5)

        # --- BLOCO 3: RUBRICAS MANUAIS ---
        self.frm_creditos = FrameRubricas(self, "3. Outros Adicionais (Insalubridade, Prêmios, Comissões...)", tipo_evento="provento")
        self.frm_creditos.pack(fill=tk.X, padx=10, pady=2)
        
        self.frm_debitos = FrameRubricas(self, "4. Outros Descontos (Coparticipação, Mensalidades...)", tipo_evento="desconto")
        self.frm_debitos.pack(fill=tk.X, padx=10, pady=2)

        # --- BOTÃO ---
        btn_calc = ttk.Button(self, text="GERAR EXPLICAÇÃO DE CUSTOS PARA O CLIENTE", command=self.calcular_tudo)
        btn_calc.pack(pady=20, fill=tk.X, padx=100, ipady=10)

    def mascara_data(self, event, entry):
        if event.keysym == "BackSpace": return
        v = entry.get().replace("/", "")
        if len(v) > 8: v = v[:8]
        novo = ""
        for i, char in enumerate(v):
            if i in [2, 4]: novo += "/"
            novo += char
        entry.delete(0, tk.END); entry.insert(0, novo)

    def calcular_tudo(self):
        salario = ferramentas.str_para_float(self.ent_salario.get())
        if salario <= 0: return messagebox.showwarning("Aviso", "Informe o salário base.")
        
        meses = int(self.ent_meses.get() or 1)
        escala = self.cb_escala.get()
        dias_uteis = 26 if "6x1" in escala else 22
        
        # 1. SALÁRIO FAMÍLIA (Base 2026)
        limite_sf = 1819.26 # Teto para direito
        valor_sf_cota = 62.04 # Valor por filho
        qtd_filhos = int(self.ent_filhos.get() or 0)
        total_sf = valor_sf_cota * qtd_filhos if salario <= limite_sf else 0

        # 2. ADICIONAIS E DESCONTOS MANUAIS
        creditos = self.frm_creditos.get_dados_calculados(salario)
        debitos = self.frm_debitos.get_dados_calculados(salario)
        base_calculo = salario + creditos['total']

        # 3. VALE TRANSPORTE (Lógica de Desconto 6%)
        vt_bruto_mes = ferramentas.str_para_float(self.ent_vt_dia.get()) * dias_uteis
        vt_desconto_func = salario * 0.06
        vt_real_empresa = max(0, vt_bruto_mes - vt_desconto_func)

        # 4. VALE REFEIÇÃO (VR Diário x Dias)
        vr_bruto_mes = ferramentas.str_para_float(self.ent_vr_dia.get()) * dias_uteis
        vr_desconto_func = ferramentas.str_para_float(self.ent_desc_vr.get())
        vr_real_empresa = max(0, vr_bruto_mes - vr_desconto_func)

        # 5. ENCARGOS PATRONAIS
        is_lucro = "Lucro" in self.cb_regime.get()
        fgts_mes = base_calculo * 0.08
        inss_patr_mes = base_calculo * 0.285 if is_lucro else 0
        taxa_enc = 1.285 if is_lucro else 1.0

        # 6. PROVISÕES (Separadas p/ Leigo)
        prov_13 = (base_calculo / 12) * taxa_enc
        prov_ferias = (base_calculo / 12) * taxa_enc
        prov_terco = (base_calculo / 3 / 12) * taxa_enc
        
        # 7. INSS INFORMATIVO DO FUNCIONÁRIO
        inss_func = calculos.calcular_inss_progressivo(base_calculo)
        
        saude = ferramentas.str_para_float(self.ent_saude.get())

        total_mensal = base_calculo + fgts_mes + inss_patr_mes + prov_13 + prov_ferias + prov_terco + vt_real_empresa + vr_real_empresa + saude - debitos['total']

        # Envio para o Relatório
        dados_f = {
            "meses": meses, "escala": escala, "regime": self.cb_regime.get(),
            "adm_estimada": self.ent_adm.get(), "data_final": (ferramentas.parse_data(self.ent_adm.get()) + timedelta(days=meses*30)).strftime("%d/%m/%Y")
        }
        
        resumo = {
            "base": base_calculo, "sal_familia": total_sf,
            "vt_total_bruto": vt_bruto_mes, "vt_desconto": vt_desconto_func, "vt_empresa": vt_real_empresa,
            "vr_total_bruto": vr_bruto_mes, "vr_desconto": vr_desconto_func, "vr_empresa": vr_real_empresa,
            "fgts_mes": fgts_mes, "inss_patr": inss_patr_mes, "inss_func": inss_func,
            "p_13": prov_13, "p_ferias": prov_ferias, "p_terco": prov_terco,
            "saude": saude, "debitos_manuais": debitos['total'], "total_mensal": total_mensal
        }
        
        relatorios.gerar_relatorio_custos_leigo(dados_f, resumo, total_mensal * meses)