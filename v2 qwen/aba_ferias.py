import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from datetime import timedelta
import ferramentas
import relatorios
from componentes import FrameRubricas


class AbaFerias(ttk.Frame):
    """Aba para gestão de férias: aviso e recibo de pagamento."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        # --- BLOCO 1: DADOS DO FUNCIONÁRIO ---
        frm_func = ttk.LabelFrame(self, text="Dados do Funcionário", padding=10)
        frm_func.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frm_func, text="Nome:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_nome = ttk.Entry(frm_func, width=30)
        self.ent_nome.grid(row=0, column=1, padx=5, sticky="w")
        
        ttk.Label(frm_func, text="Cargo:").grid(row=0, column=2, sticky="w", padx=10)
        self.ent_cargo = ttk.Entry(frm_func, width=20)
        self.ent_cargo.grid(row=0, column=3, padx=5, sticky="w")
        
        ttk.Label(frm_func, text="Admissão (Opcional):").grid(row=0, column=4, sticky="w", padx=10)
        self.ent_adm = ttk.Entry(frm_func, width=12)
        self.ent_adm.grid(row=0, column=5, padx=5, sticky="w")
        self.ent_adm.bind("<KeyRelease>", lambda e: self._mascara_data(e, self.ent_adm))
        self.ent_adm.insert(0, datetime.datetime.now().strftime("%d/%m/%Y"))
        
        ttk.Label(frm_func, text="Salário Base:").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_salario = ttk.Entry(frm_func, width=15)
        self.ent_salario.grid(row=1, column=1, padx=5, sticky="w")
        self.ent_salario.insert(0, "0.00")
        
        # --- BLOCO 2: DATAS E PERÍODOS ---
        frm_dates = ttk.LabelFrame(self, text="Datas e Períodos", padding=10)
        frm_dates.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frm_dates, text="Período Aquisitivo (Opcional):").grid(row=0, column=0, sticky="w")
        self.ent_aq_ini = ttk.Entry(frm_dates, width=11)
        self.ent_aq_ini.grid(row=0, column=1, padx=5)
        self.ent_aq_ini.bind("<KeyRelease>", lambda e: self._mascara_data(e, self.ent_aq_ini))
        
        ttk.Label(frm_dates, text="a").grid(row=0, column=2, padx=5)
        
        self.ent_aq_fim = ttk.Entry(frm_dates, width=11)
        self.ent_aq_fim.grid(row=0, column=3, padx=5)
        self.ent_aq_fim.bind("<KeyRelease>", lambda e: self._mascara_data(e, self.ent_aq_fim))
        
        ttk.Separator(frm_dates, orient='horizontal').grid(
            row=1, column=0, columnspan=6, sticky="ew", pady=10
        )
        
        ttk.Label(frm_dates, text="Início do Gozo:").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_gozo_ini = ttk.Entry(frm_dates, width=11)
        self.ent_gozo_ini.grid(row=2, column=1, padx=5)
        self.ent_gozo_ini.bind("<KeyRelease>", lambda e: self._mascara_data(e, self.ent_gozo_ini))
        self.ent_gozo_ini.insert(0, datetime.datetime.now().strftime("%d/%m/%Y"))
        
        # Modo de cálculo
        self.var_modo = tk.StringVar(value="dias")
        ttk.Radiobutton(
            frm_dates, text="Total por Dias", variable=self.var_modo, 
            value="dias", command=self._alternar_modo
        ).grid(row=2, column=2, padx=10)
        ttk.Radiobutton(
            frm_dates, text="Pela Data de Retorno", variable=self.var_modo, 
            value="data", command=self._alternar_modo
        ).grid(row=2, column=3, padx=10)
        
        ttk.Label(frm_dates, text="Total Dias (Gozo + Abono):").grid(row=3, column=0, sticky="w", pady=5)
        self.ent_dias = ttk.Entry(frm_dates, width=8)
        self.ent_dias.insert(0, "30")
        self.ent_dias.grid(row=3, column=1, padx=5)
        
        ttk.Label(frm_dates, text="Data de Retorno:").grid(row=3, column=2, sticky="w", padx=10, pady=5)
        self.ent_retorno = ttk.Entry(frm_dates, width=11)
        self.ent_retorno.grid(row=3, column=3, padx=5)
        self.ent_retorno.bind("<KeyRelease>", lambda e: self._mascara_data(e, self.ent_retorno))
        
        ttk.Button(
            frm_dates, text="↻ Calcular Datas", 
            command=self._calcular_datas_preview, style="Accent.TButton"
        ).grid(row=3, column=4, padx=15)
        
        # --- EXTRAS: ABONO E DOBRA ---
        frm_extras = ttk.Frame(frm_dates)
        frm_extras.grid(row=4, column=0, columnspan=6, sticky="w", pady=15)
        
        self.var_abono = tk.BooleanVar()
        ttk.Checkbutton(
            frm_extras, text="Vender 1/3 (Abono Pecuniário)", 
            variable=self.var_abono, command=self._calcular_datas_preview
        ).pack(side="left", padx=5)
        
        self.var_dobra = tk.BooleanVar()
        ttk.Checkbutton(
            frm_extras, text="Pagar em Dobra (Art. 137 CLT)", 
            variable=self.var_dobra
        ).pack(side="left", padx=30)
        
        # --- BLOCO 3: MÉDIAS PARA BASE DE CÁLCULO ---
        self.frm_medias = FrameRubricas(
            self, "Médias para Base de Cálculo (Horas Extras, Adicionais...)", 
            tipo_evento="provento"
        )
        self.frm_medias.pack(fill=tk.X, padx=10, pady=5)
        
        # --- BLOCO 4: BOTÕES DE AÇÃO ---
        frm_btns = ttk.Frame(self)
        frm_btns.pack(fill=tk.X, padx=80, pady=25)
        
        ttk.Button(
            frm_btns, text="📄 GERAR AVISO DE FÉRIAS", 
            command=self._acao_gerar_aviso, style="Accent.TButton"
        ).pack(side="left", fill=tk.X, expand=True, padx=10, ipady=8)
        
        ttk.Button(
            frm_btns, text="💰 GERAR RECIBO DE FÉRIAS", 
            command=self._acao_gerar_recibo, style="Accent.TButton"
        ).pack(side="left", fill=tk.X, expand=True, padx=10, ipady=8)
    
    def _mascara_data(self, event, campo):
        """Aplica máscara de data DD/MM/AAAA ao campo de entrada."""
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab", "Escape"):
            return
        
        # Remove caracteres não numéricos e limita a 8 dígitos
        texto = "".join(filter(str.isdigit, campo.get()))[:8]
        
        # Formata com barras
        if len(texto) > 4:
            texto = f"{texto[:2]}/{texto[2:4]}/{texto[4:]}"
        elif len(texto) > 2:
            texto = f"{texto[:2]}/{texto[2:]}"
        
        # Atualiza o campo sem disparar evento recursivo
        campo.delete(0, tk.END)
        campo.insert(0, texto)
    
    def _alternar_modo(self):
        """Habilita/desabilita campos conforme modo de cálculo."""
        if self.var_modo.get() == "dias":
            self.ent_dias.config(state="normal")
            self.ent_retorno.config(state="readonly")
        else:
            self.ent_dias.config(state="readonly")
            self.ent_retorno.config(state="normal")
    
    def _calcular_datas_preview(self):
        """Calcula dias de gozo/abono e data de retorno com base no modo selecionado."""
        data_ini = ferramentas.parse_data(self.ent_gozo_ini.get())
        if not data_ini:
            messagebox.showwarning("Atenção", "Informe uma data válida para início do gozo.")
            return None
        
        try:
            if self.var_modo.get() == "dias":
                total_dias = int(self.ent_dias.get())
                if total_dias < 10 or total_dias > 30:
                    messagebox.showwarning("Atenção", "Total de dias deve estar entre 10 e 30.")
                    return None
                
                # Cálculo com abono pecuniário (1/3)
                if self.var_abono.get():
                    dias_gozo = int(total_dias * 2 / 3)
                    dias_abono = total_dias - dias_gozo
                else:
                    dias_gozo = total_dias
                    dias_abono = 0
                
                data_retorno = data_ini + timedelta(days=dias_gozo)
                
                # Atualiza campo de retorno (somente leitura)
                self.ent_retorno.config(state="normal")
                self.ent_retorno.delete(0, tk.END)
                self.ent_retorno.insert(0, data_retorno.strftime("%d/%m/%Y"))
                self.ent_retorno.config(state="readonly")
                
                return dias_gozo, dias_abono, data_retorno
            
            else:  # Modo "data"
                data_retorno = ferramentas.parse_data(self.ent_retorno.get())
                if not data_retorno or data_retorno <= data_ini:
                    messagebox.showwarning("Atenção", "Data de retorno deve ser posterior ao início do gozo.")
                    return None
                
                dias_gozo = (data_retorno - data_ini).days
                if dias_gozo < 10:
                    messagebox.showwarning("Atenção", "Período de gozo mínimo é de 10 dias.")
                    return None
                
                # Cálculo com abono pecuniário
                if self.var_abono.get():
                    total_dias = int(dias_gozo / (2 / 3))
                    dias_abono = total_dias - dias_gozo
                else:
                    total_dias = dias_gozo
                    dias_abono = 0
                
                # Atualiza campo de dias (somente leitura)
                self.ent_dias.config(state="normal")
                self.ent_dias.delete(0, tk.END)
                self.ent_dias.insert(0, str(total_dias))
                self.ent_dias.config(state="readonly")
                
                return dias_gozo, dias_abono, data_retorno
        
        except ValueError:
            messagebox.showerror("Erro", "Valor numérico inválido nos campos de dias.")
            return None
    
    def _acao_gerar_aviso(self):
        """Gera o aviso de férias com base nos dados preenchidos."""
        res = self._calcular_datas_preview()
        if not res:
            return
        
        dias_gozo, dias_abono, data_retorno = res
        
        dados_funcionario = {
            "nome": self.ent_nome.get().strip() or "Não Informado",
            "cargo": self.ent_cargo.get().strip() or "Não Informado"
        }
        
        dados_ferias = {
            "inicio": self.ent_gozo_ini.get(),
            "fim": (data_retorno - timedelta(days=1)).strftime("%d/%m/%Y"),
            "retorno": data_retorno.strftime("%d/%m/%Y"),
            "obs": f"Com {dias_abono} dias de abono pecuniário." if dias_abono > 0 else "Sem abono pecuniário."
        }
        
        try:
            relatorios.gerar_aviso_ferias(dados_funcionario, dados_ferias)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar aviso de férias:\n{str(e)}")
    
    def _acao_gerar_recibo(self):
        """Gera o recibo de férias com cálculo detalhado das verbas."""
        res = self._calcular_datas_preview()
        if not res:
            messagebox.showwarning("Atenção", "Verifique as datas de gozo antes de gerar o recibo.")
            return
        
        dias_gozo, dias_abono, data_retorno = res
        
        # Validação do salário
        try:
            salario_base = ferramentas.str_para_float(self.ent_salario.get())
            if salario_base <= 0:
                messagebox.showwarning("Atenção", "Informe um salário base válido (maior que zero).")
                self.ent_salario.focus()
                return
        except:
            messagebox.showwarning("Atenção", "Salário base inválido.")
            self.ent_salario.focus()
            return
        
        # Cálculo das médias
        medias = self.frm_medias.get_dados_calculados(salario_base)
        base_calculo = salario_base + medias['total']
        valor_dia = base_calculo / 30
        
        # Montagem dos itens do recibo
        itens = []
        
        # 1. Férias gozadas + 1/3 constitucional
        valor_ferias = valor_dia * dias_gozo
        valor_terco_ferias = valor_ferias / 3
        itens.append({
            'descricao': f"Férias Gozadas ({dias_gozo} dias)",
            'ref': f"{dias_gozo}d",
            'valor': valor_ferias,
            'desconto': 0.0
        })
        itens.append({
            'descricao': "1/3 Constitucional s/ Férias",
            'ref': "33.33%",
            'valor': valor_terco_ferias,
            'desconto': 0.0
        })
        
        # 2. Dobra de férias (Art. 137 CLT)
        if self.var_dobra.get():
            itens.append({
                'descricao': "Dobra de Férias (Art. 137 CLT)",
                'ref': "100%",
                'valor': valor_ferias,
                'desconto': 0.0
            })
            itens.append({
                'descricao': "1/3 s/ Dobra de Férias",
                'ref': "33.33%",
                'valor': valor_terco_ferias,
                'desconto': 0.0
            })
        
        # 3. Abono pecuniário + 1/3
        if dias_abono > 0:
            valor_abono = valor_dia * dias_abono
            valor_terco_abono = valor_abono / 3
            itens.append({
                'descricao': f"Abono Pecuniário ({dias_abono} dias)",
                'ref': f"{dias_abono}d",
                'valor': valor_abono,
                'desconto': 0.0
            })
            itens.append({
                'descricao': "1/3 s/ Abono Pecuniário",
                'ref': "33.33%",
                'valor': valor_terco_abono,
                'desconto': 0.0
            })
        
        # Dados do funcionário para o recibo
        dados_funcionario = {
            "nome": self.ent_nome.get().strip() or "Não Informado",
            "cargo": self.ent_cargo.get().strip() or "Não Informado",
            "admissao": self.ent_adm.get().strip() or "Não Informado",
            "aq_ini": self.ent_aq_ini.get().strip() or "...",
            "aq_fim": self.ent_aq_fim.get().strip() or "...",
            "gozo_ini": self.ent_gozo_ini.get().strip(),
            "gozo_fim": (data_retorno - timedelta(days=1)).strftime("%d/%m/%Y"),
            "dias_gozo": dias_gozo,
            "dias_abono": dias_abono
        }
        
        try:
            relatorios.gerar_recibo_ferias_exclusivo(dados_funcionario, itens)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar recibo de férias:\n{str(e)}")
            import traceback
            traceback.print_exc()