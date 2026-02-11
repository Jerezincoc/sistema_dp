import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from datetime import timedelta
import relatorios
import ferramentas
import calculos
from componentes import FrameRubricas


class AbaCustos(ttk.Frame):
    """Aba para cálculo e projeção de custos trabalhistas totais."""
    
    # Constantes para cálculos (valores 2026)
    TETO_SALARIO_FAMILIA = 1819.26
    VALOR_COTA_SALARIO_FAMILIA = 62.04
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface gráfica da aba."""
        # --- BLOCO 1: DADOS BASE ---
        frm_base = ttk.LabelFrame(self, text="1. Dados de Contratação e Projeção", padding=10)
        frm_base.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frm_base, text="Salário Base:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_salario = ttk.Entry(frm_base, width=15)
        self.ent_salario.grid(row=0, column=1, padx=5)
        self.ent_salario.insert(0, "0.00")
        
        ttk.Label(frm_base, text="Filhos (<14 anos):").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.ent_filhos = ttk.Entry(frm_base, width=8)
        self.ent_filhos.grid(row=0, column=3)
        self.ent_filhos.insert(0, "0")
        
        ttk.Label(frm_base, text="Data de Admissão:").grid(row=1, column=0, pady=10, sticky="w")
        self.ent_adm = ttk.Entry(frm_base, width=15)
        self.ent_adm.grid(row=1, column=1, padx=5)
        self.ent_adm.insert(0, datetime.datetime.now().strftime("%d/%m/%Y"))
        self.ent_adm.bind("<KeyRelease>", lambda e: self._mascara_data(e, self.ent_adm))
        
        ttk.Label(frm_base, text="Meses Projetados:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.ent_meses = ttk.Entry(frm_base, width=8)
        self.ent_meses.grid(row=1, column=3)
        self.ent_meses.insert(0, "12")
        
        ttk.Label(frm_base, text="Regime Tributário:").grid(row=1, column=4, padx=10, pady=5, sticky="w")
        self.cb_regime = ttk.Combobox(
            frm_base, 
            values=["Simples Nacional", "Lucro Presumido/Real"], 
            state="readonly", 
            width=22
        )
        self.cb_regime.current(0)
        self.cb_regime.grid(row=1, column=5)
        
        # --- BLOCO 2: BENEFÍCIOS ---
        frm_ben = ttk.LabelFrame(self, text="2. Benefícios (VT e VR)", padding=10)
        frm_ben.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frm_ben, text="Escala de Trabalho:").grid(row=0, column=0, sticky="w", pady=5)
        self.cb_escala = ttk.Combobox(
            frm_ben, 
            values=["5x2 (Seg a Sex)", "6x1 (Seg a Sáb)", "6x1 (Sáb 4h)"], 
            state="readonly", 
            width=20
        )
        self.cb_escala.current(0)
        self.cb_escala.grid(row=0, column=1, padx=5)
        
        ttk.Label(frm_ben, text="VT Diário (R$):").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.ent_vt_dia = ttk.Entry(frm_ben, width=10)
        self.ent_vt_dia.grid(row=0, column=3)
        self.ent_vt_dia.insert(0, "0.00")
        
        ttk.Label(frm_ben, text="VR Diário (R$):").grid(row=1, column=0, pady=10, sticky="w")
        self.ent_vr_dia = ttk.Entry(frm_ben, width=10)
        self.ent_vr_dia.grid(row=1, column=1, padx=5)
        self.ent_vr_dia.insert(0, "0.00")
        
        ttk.Label(frm_ben, text="Desc. VR (Fixo R$):").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.ent_desc_vr = ttk.Entry(frm_ben, width=10)
        self.ent_desc_vr.grid(row=1, column=3)
        self.ent_desc_vr.insert(0, "0.00")
        
        ttk.Label(frm_ben, text="Plano Saúde/Odonto (R$):").grid(row=1, column=4, padx=10, pady=5, sticky="w")
        self.ent_saude = ttk.Entry(frm_ben, width=12)
        self.ent_saude.grid(row=1, column=5)
        self.ent_saude.insert(0, "0.00")
        
        # --- BLOCO 3: RUBRICAS MANUAIS ---
        self.frm_creditos = FrameRubricas(
            self, 
            "3. Outros Adicionais (Insalubridade, Prêmios, Comissões...)", 
            tipo_evento="provento"
        )
        self.frm_creditos.pack(fill=tk.X, padx=10, pady=2)
        
        self.frm_debitos = FrameRubricas(
            self, 
            "4. Outros Descontos (Coparticipação, Mensalidades...)", 
            tipo_evento="desconto"
        )
        self.frm_debitos.pack(fill=tk.X, padx=10, pady=2)
        
        # --- BOTÃO DE CÁLCULO ---
        btn_calc = ttk.Button(
            self, 
            text="📊 GERAR EXPLICAÇÃO DE CUSTOS PARA O CLIENTE", 
            command=self.calcular_tudo,
            style="Accent.TButton"
        )
        btn_calc.pack(pady=20, fill=tk.X, padx=100, ipady=10)
    
    def _mascara_data(self, event, entry):
        """Aplica máscara de data DD/MM/AAAA ao campo."""
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab"):
            return
        
        texto = entry.get().replace("/", "").replace(" ", "")
        if not texto.isdigit():
            entry.delete(0, tk.END)
            entry.insert(0, "")
            return
        
        texto = texto[:8]  # Limita a 8 dígitos (DDMMAAAA)
        novo = ""
        for i, char in enumerate(texto):
            if i in (2, 4):
                novo += "/"
            novo += char
        entry.delete(0, tk.END)
        entry.insert(0, novo)
    
    def _validar_entradas(self):
        """Valida campos obrigatórios e retorna True se válidos."""
        salario = ferramentas.str_para_float(self.ent_salario.get())
        if salario <= 0:
            messagebox.showwarning("Aviso", "⚠️ Informe um salário base válido (maior que zero).")
            self.ent_salario.focus()
            return False
        
        try:
            meses = int(self.ent_meses.get())
            if meses <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Aviso", "⚠️ Informe quantidade válida de meses projetados.")
            self.ent_meses.focus()
            return False
        
        return True
    
    def calcular_tudo(self):
        """Executa todos os cálculos e gera o relatório de custos."""
        if not self._validar_entradas():
            return
        
        try:
            # --- DADOS DE ENTRADA ---
            salario_base = ferramentas.str_para_float(self.ent_salario.get())
            qtd_filhos = int(self.ent_filhos.get() or 0)
            meses_proj = int(self.ent_meses.get() or 12)
            escala = self.cb_escala.get()
            regime = self.cb_regime.get()
            is_lucro = "Lucro" in regime
            
            # --- CÁLCULO DE DIAS ÚTEIS ---
            dias_uteis = 26 if "6x1" in escala else 22
            
            # --- SALÁRIO FAMÍLIA ---
            salario_familia = (
                self.VALOR_COTA_SALARIO_FAMILIA * qtd_filhos 
                if salario_base <= self.TETO_SALARIO_FAMILIA 
                else 0
            )
            
            # --- RUBRICAS MANUAIS ---
            creditos = self.frm_creditos.get_dados_calculados(salario_base)
            debitos = self.frm_debitos.get_dados_calculados(salario_base)
            base_calculo = salario_base + creditos['total']
            
            # --- VALE TRANSPORTE ---
            vt_diario = ferramentas.str_para_float(self.ent_vt_dia.get())
            vt_bruto_mes = vt_diario * dias_uteis
            vt_desconto_func = salario_base * 0.06
            vt_custo_empresa = max(0, vt_bruto_mes - vt_desconto_func)
            
            # --- VALE REFEIÇÃO ---
            vr_diario = ferramentas.str_para_float(self.ent_vr_dia.get())
            vr_bruto_mes = vr_diario * dias_uteis
            vr_desconto_func = ferramentas.str_para_float(self.ent_desc_vr.get())
            vr_custo_empresa = max(0, vr_bruto_mes - vr_desconto_func)
            
            # --- ENCARGOS PATRONAIS ---
            fgts_mes = base_calculo * 0.08
            inss_patronal_mes = base_calculo * 0.285 if is_lucro else 0
            
            # --- PROVISÕES ---
            fator_encargo = 1.285 if is_lucro else 1.0
            prov_decimo_terceiro = (base_calculo / 12) * fator_encargo
            prov_ferias = (base_calculo / 12) * fator_encargo
            prov_terco_ferias = (base_calculo / 36) * fator_encargo  # (1/3)/12 = 1/36
            
            # --- INSS DO FUNCIONÁRIO (informativo) ---
            inss_funcionario = calculos.calcular_inss_progressivo(base_calculo)
            
            # --- SAÚDE ---
            saude_empresa = ferramentas.str_para_float(self.ent_saude.get())
            
            # --- CUSTO TOTAL MENSAL ---
            custo_mensal = (
                base_calculo +
                fgts_mes +
                inss_patronal_mes +
                prov_decimo_terceiro +
                prov_ferias +
                prov_terco_ferias +
                vt_custo_empresa +
                vr_custo_empresa +
                saude_empresa +
                salario_familia -
                debitos['total']
            )
            
            # --- PREPARAR DADOS PARA RELATÓRIO ---
            dados_funcionario = {
                "meses": meses_proj,
                "escala": escala,
                "regime": regime,
                "adm_estimada": self.ent_adm.get(),
                "data_final": (
                    ferramentas.parse_data(self.ent_adm.get()) + timedelta(days=meses_proj * 30)
                ).strftime("%d/%m/%Y")
            }
            
            resumo_custos = {
                "base": base_calculo,
                "sal_familia": salario_familia,
                "vt_total_bruto": vt_bruto_mes,
                "vt_desconto": vt_desconto_func,
                "vt_empresa": vt_custo_empresa,
                "vr_total_bruto": vr_bruto_mes,
                "vr_desconto": vr_desconto_func,
                "vr_empresa": vr_custo_empresa,
                "fgts_mes": fgts_mes,
                "inss_patr": inss_patronal_mes,
                "inss_func": inss_funcionario,
                "p_13": prov_decimo_terceiro,
                "p_ferias": prov_ferias,
                "p_terco": prov_terco_ferias,
                "saude": saude_empresa,
                "debitos_manuais": debitos['total'],
                "total_mensal": custo_mensal
            }
            
            # --- GERAR RELATÓRIO ---
            relatorios.gerar_relatorio_custos_leigo(
                dados_funcionario, 
                resumo_custos, 
                custo_mensal * meses_proj
            )
            
        except Exception as e:
            messagebox.showerror(
                "Erro no Cálculo", 
                f"Ocorreu um erro ao calcular os custos:\n{str(e)}"
            )
            import traceback
            traceback.print_exc()