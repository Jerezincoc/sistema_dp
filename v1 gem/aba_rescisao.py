# Arquivo: aba_rescisao.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from datetime import timedelta
import relatorios
import ferramentas
from componentes import FrameRubricas

class AbaRescisao(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # --- BLOCO 1: DADOS BÁSICOS ---
        frm_dados = ttk.LabelFrame(self, text="Dados da Rescisão", padding=10)
        frm_dados.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frm_dados, text="Funcionário:").grid(row=0, column=0, sticky="w")
        self.ent_nome = ttk.Entry(frm_dados, width=25)
        self.ent_nome.grid(row=0, column=1, padx=5)
        
        ttk.Label(frm_dados, text="Cargo:").grid(row=0, column=2)
        self.ent_cargo = ttk.Entry(frm_dados, width=15)
        self.ent_cargo.grid(row=0, column=3, padx=5)
        
        ttk.Label(frm_dados, text="Salário Base:").grid(row=0, column=4)
        self.ent_salario = ttk.Entry(frm_dados, width=12)
        self.ent_salario.grid(row=0, column=5, padx=5)

        ttk.Label(frm_dados, text="Adm:").grid(row=1, column=0, pady=10)
        self.ent_adm = ttk.Entry(frm_dados, width=12)
        self.ent_adm.grid(row=1, column=1, padx=5)
        # Aplicando a máscara de data
        self.ent_adm.bind("<KeyRelease>", lambda event: self.formatar_data(event, self.ent_adm))

        ttk.Label(frm_dados, text="Afastamento:").grid(row=1, column=2)
        self.ent_rescisao = ttk.Entry(frm_dados, width=12)
        self.ent_rescisao.grid(row=1, column=3, padx=5)
        self.ent_rescisao.bind("<KeyRelease>", lambda event: self.formatar_data(event, self.ent_rescisao))

        ttk.Label(frm_dados, text="Causa:").grid(row=2, column=0)
        self.cb_causa = ttk.Combobox(frm_dados, values=[
            "Dispensa sem Justa Causa", "Pedido de Demissão", 
            "Dispensa com Justa Causa", "Término de Contrato", "Acordo Comum"
        ], state="readonly", width=22)
        self.cb_causa.current(0)
        self.cb_causa.grid(row=2, column=1)

        ttk.Label(frm_dados, text="Aviso:").grid(row=2, column=2)
        self.cb_aviso = ttk.Combobox(frm_dados, values=["Trabalhado", "Indenizado", "Dispensa"], state="readonly", width=12)
        self.cb_aviso.current(0)
        self.cb_aviso.grid(row=2, column=3)

        # --- BLOCO 2: AVOS E FÉRIAS ---
        frm_avos = ttk.LabelFrame(self, text="Avos e Férias Vencidas", padding=10)
        frm_avos.pack(fill=tk.X, padx=10, pady=5)
        
        self.ent_avos_13 = ttk.Entry(frm_avos, width=5); self.ent_avos_13.grid(row=0, column=1)
        ttk.Label(frm_avos, text="13º (Avos)").grid(row=0, column=0, padx=5)

        self.ent_avos_ferias = ttk.Entry(frm_avos, width=5); self.ent_avos_ferias.grid(row=0, column=3)
        ttk.Label(frm_avos, text="Férias Prop (Avos)").grid(row=0, column=2, padx=5)

        self.ent_ferias_venc = ttk.Entry(frm_avos, width=5); self.ent_ferias_venc.insert(0, "0"); self.ent_ferias_venc.grid(row=0, column=5)
        ttk.Label(frm_avos, text="Férias Vencidas (Qtd)").grid(row=0, column=4, padx=5)

        ttk.Button(frm_avos, text="Calcular Avos Auto", command=self.calcular_avos_auto).grid(row=0, column=6, padx=20)

        # --- BLOCO 3: REGRAS DE FGTS ---
        frm_fgts = ttk.LabelFrame(self, text="FGTS e Multas", padding=10)
        frm_fgts.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frm_fgts, text="Saldo p/ Multa (R$):").grid(row=0, column=0)
        self.ent_fgts_saldo = ttk.Entry(frm_fgts, width=15); self.ent_fgts_saldo.grid(row=0, column=1, padx=5)
        
        # Botão para calcular saldo estimado baseado no tempo
        ttk.Button(frm_fgts, text="Estimativa de Saldo (Meses)", command=self.estimar_saldo_fgts).grid(row=0, column=2, padx=10)

        self.var_regra_fgts = tk.StringVar(value="saldo_multa")
        ttk.Radiobutton(frm_fgts, text="Saldo + Multa", variable=self.var_regra_fgts, value="saldo_multa").grid(row=1, column=0, padx=5, pady=5)
        ttk.Radiobutton(frm_fgts, text="Somente Saldo", variable=self.var_regra_fgts, value="apenas_saldo").grid(row=1, column=1, padx=5)
        ttk.Radiobutton(frm_fgts, text="Não calcular", variable=self.var_regra_fgts, value="nada").grid(row=1, column=2, padx=5)

        # --- BLOCO 4: RUBRICAS ---
        self.frm_creditos = FrameRubricas(self, "Lançamentos de CRÉDITO", tipo_evento="provento")
        self.frm_creditos.pack(fill=tk.X, padx=10, pady=2)
        
        self.frm_debitos = FrameRubricas(self, "Lançamentos de DÉBITO", tipo_evento="desconto")
        self.frm_debitos.pack(fill=tk.X, padx=10, pady=2)

        ttk.Button(self, text="GERAR TERMO DE RESCISÃO FINAL", command=self.gerar_rescisao).pack(pady=15, fill=tk.X, padx=100, ipady=8)

    # FUNÇÃO DA MÁSCARA DE DATA
    def formatar_data(self, event, entry):
        # Ignora se for a tecla Backspace
        if event.keysym == "BackSpace": return
        
        conteudo = entry.get().replace("/", "")
        novo_texto = ""
        
        if len(conteudo) > 8: conteudo = conteudo[:8] # Limite
        
        for i, char in enumerate(conteudo):
            if i == 2 or i == 4:
                novo_texto += "/"
            novo_texto += char
            
        entry.delete(0, tk.END)
        entry.insert(0, novo_texto)

    def estimar_saldo_fgts(self):
        """Calcula saldo aproximado: Salário * Meses entre Adm/Res * 8%"""
        d_adm = ferramentas.parse_data(self.ent_adm.get())
        d_res = ferramentas.parse_data(self.ent_rescisao.get())
        salario = ferramentas.str_para_float(self.ent_salario.get())
        
        if not d_adm or not d_res or salario <= 0:
            return messagebox.showwarning("Atenção", "Preencha Adm, Rescisão e Salário para estimar.")
            
        meses = (d_res.year - d_adm.year) * 12 + (d_res.month - d_adm.month)
        if meses <= 0: meses = 1
        
        saldo_estimado = (salario * meses) * 0.08
        self.ent_fgts_saldo.delete(0, tk.END)
        self.ent_fgts_saldo.insert(0, f"{saldo_estimado:.2f}")

    # (Manter o restante das funções calcular_avos_auto e gerar_rescisao igual ao anterior)
    def calcular_avos_auto(self):
        d_adm = ferramentas.parse_data(self.ent_adm.get())
        d_res = ferramentas.parse_data(self.ent_rescisao.get())
        if not d_adm or not d_res: return
        m13 = d_res.month
        if d_res.day < 15: m13 -= 1
        if d_adm.year == d_res.year:
            m13 = m13 - (d_adm.month - 1)
            if d_adm.day > 15: m13 -= 1
        meses_f = ((d_res - d_adm).days % 365) // 30
        if ((d_res - d_adm).days % 30) >= 15: meses_f += 1
        self.ent_avos_13.delete(0, tk.END); self.ent_avos_13.insert(0, str(max(0, m13)))
        self.ent_avos_ferias.delete(0, tk.END); self.ent_avos_ferias.insert(0, str(max(0, meses_f)))

    def gerar_rescisao(self):
        nome = self.ent_nome.get()
        salario = ferramentas.str_para_float(self.ent_salario.get())
        causa = self.cb_causa.get()
        aviso = self.cb_aviso.get()
        regra_fgts = self.var_regra_fgts.get()
        if not nome or salario <= 0: return messagebox.showwarning("Erro", "Dados incompletos.")
        verbas = []
        d_res = ferramentas.parse_data(self.ent_rescisao.get())
        dias = d_res.day if d_res else 30
        v_saldo = (salario / 30) * dias
        verbas.append((f"Saldo de Salário ({dias} dias)", v_saldo, 0.0))
        try:
            a13 = int(self.ent_avos_13.get())
            if a13 > 0: verbas.append((f"13º Salário ({a13}/12)", (salario/12)*a13, 0.0))
            af = int(self.ent_avos_ferias.get())
            if af > 0:
                v_f = (salario/12)*af
                verbas.append((f"Férias Prop. ({af}/12)", v_f, 0.0))
                verbas.append(("1/3 s/ Férias Prop.", v_f/3, 0.0))
            fv = int(self.ent_ferias_venc.get())
            if fv > 0:
                v_fv = salario * fv
                verbas.append((f"Férias Vencidas ({fv} período/s)", v_fv, 0.0))
                verbas.append(("1/3 s/ Férias Vencidas", v_fv/3, 0.0))
        except: pass
        if aviso == "Indenizado": verbas.append(("Aviso Prévio Indenizado", salario, 0.0))
        c_extras = self.frm_creditos.get_dados_calculados(salario)
        for n, v in c_extras["itens"]: verbas.append((n, v, 0.0))
        d_extras = self.frm_debitos.get_dados_calculados(salario)
        for n, v in d_extras["itens"]: verbas.append((n, 0.0, v))
        saldo_caixa = ferramentas.str_para_float(self.ent_fgts_saldo.get())
        base_fgts_mes = v_saldo + (salario if aviso == "Indenizado" else 0)
        valor_fgts_mes = base_fgts_mes * 0.08
        multa_valor = 0.0
        perc_multa = 0
        if regra_fgts == "saldo_multa":
            perc_multa = 40 if "sem Justa Causa" in causa else (20 if "Acordo" in causa else 0)
            multa_valor = (saldo_caixa + valor_fgts_mes) * (perc_multa / 100)
       # --- CÁLCULO DOS TOTAIS FINAIS ---
        bruto = sum(v for n, v, d in verbas)
        descontos = sum(d for n, v, d in verbas)
        
        if regra_fgts == "nada":
            saldo_caixa = valor_fgts_mes = multa_valor = 0.0

        # Soma tudo o que envolve FGTS
        total_fgts_devido = saldo_caixa + valor_fgts_mes + multa_valor
        
        # Líquido das verbas (Vencimentos - Descontos)
        liquido_venc = bruto - descontos
        
        # A MUDANÇA ESTÁ AQUI: Somamos o Líquido das Verbas + TODO o FGTS
        liquido_final = liquido_venc + total_fgts_devido

        dados_f = {
            "nome": nome, 
            "cargo": self.ent_cargo.get(), 
            "adm": self.ent_adm.get(), 
            "rescisao": self.ent_rescisao.get(), 
            "causa": causa, 
            "aviso_tipo": aviso
        }
        
        totais_res = {
            "bruto": bruto, 
            "descontos": descontos, 
            "liquido_venc": liquido_venc, 
            "fgts_informado": saldo_caixa, 
            "fgts_mes": valor_fgts_mes, 
            "perc_multa": perc_multa, 
            "multa_valor": multa_valor, 
            "fgts_total_geral": total_fgts_devido, 
            "liquido_final": liquido_final # Agora leva o valor cheio!
        }
        
        relatorios.gerar_trct_html(dados_f, verbas, totais_res)