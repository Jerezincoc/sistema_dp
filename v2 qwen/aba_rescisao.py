import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from datetime import timedelta
import relatorios
import ferramentas
from componentes import FrameRubricas


class AbaRescisao(ttk.Frame):
    """Aba para gestão de rescisão contratual e geração de TRCT."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
    
    def _mascara_data(self, event, campo):
        """Aplica máscara de data DD/MM/AAAA ao campo de entrada."""
        # Permitir teclas de navegação e edição
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab", "Escape"):
            return
        
        # Extrair apenas dígitos e limitar a 8 caracteres
        texto = "".join(filter(str.isdigit, campo.get()))[:8]
        
        # Formatar com barras conforme digitação
        if len(texto) > 4:
            texto = f"{texto[:2]}/{texto[2:4]}/{texto[4:]}"
        elif len(texto) > 2:
            texto = f"{texto[:2]}/{texto[2:]}"
        
        # Atualizar campo sem disparar evento recursivo
        campo.delete(0, tk.END)
        campo.insert(0, texto)
    
    def setup_ui(self):
        # --- BLOCO 1: DADOS BÁSICOS ---
        frm_dados = ttk.LabelFrame(self, text="Dados da Rescisão", padding=10)
        frm_dados.pack(fill=tk.X, padx=10, pady=5)
        
        # Linha 1: Nome, Cargo e Salário
        ttk.Label(frm_dados, text="Funcionário:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_nome = ttk.Entry(frm_dados, width=25)
        self.ent_nome.grid(row=0, column=1, padx=5)
        
        ttk.Label(frm_dados, text="Cargo:").grid(row=0, column=2, sticky="w", padx=10)
        self.ent_cargo = ttk.Entry(frm_dados, width=15)
        self.ent_cargo.grid(row=0, column=3, padx=5)
        
        ttk.Label(frm_dados, text="Salário Base:").grid(row=0, column=4, sticky="w", padx=10)
        self.ent_salario = ttk.Entry(frm_dados, width=12)
        self.ent_salario.grid(row=0, column=5, padx=5)
        self.ent_salario.insert(0, "0.00")
        
        # Linha 2: Datas de Admissão e Rescisão
        ttk.Label(frm_dados, text="Admissão:").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_adm = ttk.Entry(frm_dados, width=12)
        self.ent_adm.grid(row=1, column=1, padx=5)
        self.ent_adm.bind("<KeyRelease>", lambda event: self._mascara_data(event, self.ent_adm))
        self.ent_adm.insert(0, datetime.datetime.now().strftime("%d/%m/%Y"))
        
        ttk.Label(frm_dados, text="Afastamento:").grid(row=1, column=2, sticky="w", padx=10)
        self.ent_rescisao = ttk.Entry(frm_dados, width=12)
        self.ent_rescisao.grid(row=1, column=3, padx=5)
        self.ent_rescisao.bind("<KeyRelease>", lambda event: self._mascara_data(event, self.ent_rescisao))
        self.ent_rescisao.insert(0, datetime.datetime.now().strftime("%d/%m/%Y"))
        
        # Linha 3: Causa e Aviso Prévio
        ttk.Label(frm_dados, text="Causa:").grid(row=2, column=0, sticky="w", pady=5)
        self.cb_causa = ttk.Combobox(
            frm_dados,
            values=[
                "Dispensa sem Justa Causa",
                "Pedido de Demissão",
                "Dispensa com Justa Causa",
                "Término de Contrato",
                "Acordo Comum"
            ],
            state="readonly",
            width=22
        )
        self.cb_causa.current(0)
        self.cb_causa.grid(row=2, column=1, padx=5)
        
        ttk.Label(frm_dados, text="Aviso Prévio:").grid(row=2, column=2, sticky="w", padx=10)
        self.cb_aviso = ttk.Combobox(
            frm_dados,
            values=["Trabalhado", "Indenizado", "Dispensa"],
            state="readonly",
            width=12
        )
        self.cb_aviso.current(0)
        self.cb_aviso.grid(row=2, column=3, padx=5)
        
        # --- BLOCO 2: AVOS E FÉRIAS ---
        frm_avos = ttk.LabelFrame(self, text="Avos e Férias Vencidas", padding=10)
        frm_avos.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frm_avos, text="13º (Avos):").grid(row=0, column=0, padx=5)
        self.ent_avos_13 = ttk.Entry(frm_avos, width=5)
        self.ent_avos_13.grid(row=0, column=1)
        self.ent_avos_13.insert(0, "0")
        
        ttk.Label(frm_avos, text="Férias Prop. (Avos):").grid(row=0, column=2, padx=15)
        self.ent_avos_ferias = ttk.Entry(frm_avos, width=5)
        self.ent_avos_ferias.grid(row=0, column=3)
        self.ent_avos_ferias.insert(0, "0")
        
        ttk.Label(frm_avos, text="Férias Vencidas (Qtd):").grid(row=0, column=4, padx=15)
        self.ent_ferias_venc = ttk.Entry(frm_avos, width=5)
        self.ent_ferias_venc.grid(row=0, column=5)
        self.ent_ferias_venc.insert(0, "0")
        
        ttk.Button(
            frm_avos, text="↻ Calcular Avos Automaticamente", 
            command=self.calcular_avos_auto, style="Accent.TButton"
        ).grid(row=0, column=6, padx=20)
        
        # --- BLOCO 3: FGTS E MULTAS ---
        frm_fgts = ttk.LabelFrame(self, text="FGTS e Multas Rescisórias", padding=10)
        frm_fgts.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frm_fgts, text="Saldo FGTS p/ Cálculo (R$):").grid(row=0, column=0, sticky="w")
        self.ent_fgts_saldo = ttk.Entry(frm_fgts, width=15)
        self.ent_fgts_saldo.grid(row=0, column=1, padx=5)
        self.ent_fgts_saldo.insert(0, "0.00")
        
        ttk.Button(
            frm_fgts, text="💰 Estimar Saldo (Base: Salário × Meses × 8%)", 
            command=self.estimar_saldo_fgts, style="Accent.TButton"
        ).grid(row=0, column=2, padx=15)
        
        # Opções de regra FGTS
        self.var_regra_fgts = tk.StringVar(value="saldo_multa")
        ttk.Radiobutton(
            frm_fgts, text="Saldo + Multa Rescisória (Padrão)", 
            variable=self.var_regra_fgts, value="saldo_multa"
        ).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        ttk.Radiobutton(
            frm_fgts, text="Somente Saldo (Sem Multa)", 
            variable=self.var_regra_fgts, value="apenas_saldo"
        ).grid(row=1, column=1, padx=5, pady=8, sticky="w")
        ttk.Radiobutton(
            frm_fgts, text="Não Calcular FGTS", 
            variable=self.var_regra_fgts, value="nada"
        ).grid(row=1, column=2, padx=5, pady=8, sticky="w")
        
        # --- BLOCO 4: RUBRICAS PERSONALIZADAS ---
        self.frm_creditos = FrameRubricas(
            self, "Lançamentos de CRÉDITO (Verbas Rescisórias)", 
            tipo_evento="provento"
        )
        self.frm_creditos.pack(fill=tk.X, padx=10, pady=2)
        
        self.frm_debitos = FrameRubricas(
            self, "Lançamentos de DÉBITO (Descontos)", 
            tipo_evento="desconto"
        )
        self.frm_debitos.pack(fill=tk.X, padx=10, pady=2)
        
        # --- BOTÃO DE GERAÇÃO ---
        btn_gerar = ttk.Button(
            self,
            text="📄 GERAR TERMO DE RESCISÃO FINAL",
            command=self.gerar_rescisao,
            style="Accent.TButton"
        )
        btn_gerar.pack(pady=20, fill=tk.X, padx=120, ipady=12)
    
    def estimar_saldo_fgts(self):
        """Estima saldo FGTS com base no tempo de serviço e salário."""
        d_adm = ferramentas.parse_data(self.ent_adm.get())
        d_res = ferramentas.parse_data(self.ent_rescisao.get())
        salario = ferramentas.str_para_float(self.ent_salario.get())
        
        if not d_adm or not d_res or salario <= 0:
            messagebox.showwarning(
                "Atenção", 
                "⚠️ Preencha Admissão, Data de Rescisão e Salário para estimar o saldo FGTS."
            )
            return
        
        # Cálculo aproximado de meses trabalhados
        meses = (d_res.year - d_adm.year) * 12 + (d_res.month - d_adm.month)
        if meses <= 0:
            meses = 1
        
        saldo_estimado = (salario * meses) * 0.08
        
        self.ent_fgts_saldo.delete(0, tk.END)
        self.ent_fgts_saldo.insert(0, f"{saldo_estimado:.2f}")
    
    def calcular_avos_auto(self):
        """Calcula automaticamente avos de 13º e férias com base nas datas."""
        d_adm = ferramentas.parse_data(self.ent_adm.get())
        d_res = ferramentas.parse_data(self.ent_rescisao.get())
        
        if not d_adm or not d_res:
            messagebox.showwarning("Atenção", "⚠️ Informe as datas de Admissão e Rescisão para calcular os avos.")
            return
        
        # Cálculo de avos do 13º salário
        meses_13 = d_res.month
        if d_res.day < 15:
            meses_13 -= 1
        
        if d_adm.year == d_res.year:
            meses_13 = meses_13 - (d_adm.month - 1)
            if d_adm.day > 15:
                meses_13 -= 1
        
        meses_13 = max(0, meses_13)
        
        # Cálculo de avos de férias proporcionais
        dias_trabalhados = (d_res - d_adm).days
        meses_ferias = (dias_trabalhados % 365) // 30
        if (dias_trabalhados % 30) >= 15:
            meses_ferias += 1
        
        meses_ferias = max(0, meses_ferias)
        
        # Atualizar campos
        self.ent_avos_13.delete(0, tk.END)
        self.ent_avos_13.insert(0, str(meses_13))
        
        self.ent_avos_ferias.delete(0, tk.END)
        self.ent_avos_ferias.insert(0, str(meses_ferias))
    
    def gerar_rescisao(self):
        """Valida entradas e gera o termo de rescisão com cálculo detalhado."""
        # Validação do nome
        nome = self.ent_nome.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "⚠️ Informe o nome do funcionário.")
            self.ent_nome.focus()
            return
        
        # Validação do salário
        try:
            salario = ferramentas.str_para_float(self.ent_salario.get())
            if salario <= 0:
                messagebox.showwarning("Atenção", "⚠️ Salário base deve ser maior que zero.")
                self.ent_salario.focus()
                return
        except:
            messagebox.showwarning("Atenção", "⚠️ Salário inválido. Use formato numérico (ex: 2500.50).")
            self.ent_salario.focus()
            return
        
        # Validação das datas
        d_adm = ferramentas.parse_data(self.ent_adm.get())
        d_res = ferramentas.parse_data(self.ent_rescisao.get())
        
        if not d_adm:
            messagebox.showwarning("Atenção", "⚠️ Data de admissão inválida.")
            self.ent_adm.focus()
            return
        
        if not d_res:
            messagebox.showwarning("Atenção", "⚠️ Data de rescisão inválida.")
            self.ent_rescisao.focus()
            return
        
        if d_res < d_adm:
            messagebox.showwarning("Atenção", "⚠️ Data de rescisão não pode ser anterior à admissão.")
            self.ent_rescisao.focus()
            return
        
        # Coleta de dados
        causa = self.cb_causa.get()
        aviso = self.cb_aviso.get()
        regra_fgts = self.var_regra_fgts.get()
        
        # --- CÁLCULO DAS VERBAS RESCISÓRIAS ---
        verbas = []
        
        # 1. Saldo de salário
        dias_trab = d_res.day
        v_saldo = (salario / 30) * dias_trab
        verbas.append({
            'descricao': f"Saldo de Salário ({dias_trab} dias)",
            'valor': v_saldo,
            'desconto': 0.0
        })
        
        # 2. 13º salário proporcional
        try:
            a13 = int(self.ent_avos_13.get())
            if a13 > 0:
                v_13 = (salario / 12) * a13
                verbas.append({
                    'descricao': f"13º Salário Proporcional ({a13}/12)",
                    'valor': v_13,
                    'desconto': 0.0
                })
        except:
            pass
        
        # 3. Férias proporcionais + 1/3
        try:
            af = int(self.ent_avos_ferias.get())
            if af > 0:
                v_ferias_prop = (salario / 12) * af
                verbas.append({
                    'descricao': f"Férias Proporcionais ({af}/12)",
                    'valor': v_ferias_prop,
                    'desconto': 0.0
                })
                verbas.append({
                    'descricao': "1/3 Constitucional s/ Férias Prop.",
                    'valor': v_ferias_prop / 3,
                    'desconto': 0.0
                })
        except:
            pass
        
        # 4. Férias vencidas + 1/3
        try:
            fv = int(self.ent_ferias_venc.get())
            if fv > 0:
                v_ferias_venc = salario * fv
                verbas.append({
                    'descricao': f"Férias Vencidas ({fv} período(s))",
                    'valor': v_ferias_venc,
                    'desconto': 0.0
                })
                verbas.append({
                    'descricao': "1/3 Constitucional s/ Férias Vencidas",
                    'valor': v_ferias_venc / 3,
                    'desconto': 0.0
                })
        except:
            pass
        
        # 5. Aviso prévio indenizado
        if aviso == "Indenizado":
            verbas.append({
                'descricao': "Aviso Prévio Indenizado",
                'valor': salario,
                'desconto': 0.0
            })
        
        # 6. Rubricas de crédito personalizadas
        creditos = self.frm_creditos.get_dados_calculados(salario)
        for desc, valor in creditos["itens"]:
            verbas.append({
                'descricao': desc,
                'valor': valor,
                'desconto': 0.0
            })
        
        # 7. Rubricas de débito personalizadas
        debitos = self.frm_debitos.get_dados_calculados(salario)
        for desc, valor in debitos["itens"]:
            verbas.append({
                'descricao': desc,
                'valor': 0.0,
                'desconto': valor
            })
        
        # --- CÁLCULO DO FGTS ---
        saldo_caixa = ferramentas.str_para_float(self.ent_fgts_saldo.get())
        base_fgts_mes = v_saldo + (salario if aviso == "Indenizado" else 0)
        valor_fgts_mes = base_fgts_mes * 0.08
        
        # Multa rescisória conforme causa
        perc_multa = 0
        if regra_fgts == "saldo_multa":
            if "sem Justa Causa" in causa:
                perc_multa = 40
            elif "Acordo" in causa:
                perc_multa = 20
            # Justa causa e pedido de demissão = 0%
        
        multa_valor = (saldo_caixa + valor_fgts_mes) * (perc_multa / 100)
        
        # --- TOTAIS FINAIS ---
        bruto = sum(v['valor'] for v in verbas)
        descontos = sum(v['desconto'] for v in verbas)
        liquido_venc = bruto - descontos
        
        # FGTS total (saldo + depósito do mês + multa)
        fgts_total_geral = saldo_caixa + valor_fgts_mes + multa_valor
        
        # Líquido final = líquido das verbas + todo o FGTS disponível
        liquido_final = liquido_venc + fgts_total_geral
        
        # --- PREPARAÇÃO DOS DADOS PARA RELATÓRIO ---
        dados_func = {
            "nome": nome,
            "cargo": self.ent_cargo.get().strip() or "Não Informado",
            "adm": self.ent_adm.get().strip(),
            "rescisao": self.ent_rescisao.get().strip(),
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
            "fgts_total_geral": fgts_total_geral,
            "liquido_final": liquido_final
        }
        
        # --- GERAÇÃO DO RELATÓRIO ---
        try:
            relatorios.gerar_trct_html(dados_func, verbas, totais_res)
        except Exception as e:
            messagebox.showerror(
                "Erro na Geração",
                f"❌ Falha ao gerar termo de rescisão:\n{str(e)}"
            )
            import traceback
            traceback.print_exc()