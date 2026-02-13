import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from datetime import timedelta
from core import relatorios, ferramentas, calculos
from ui.widgets import FrameRubricas  # Lembre-se que renomeamos componentes para widgets

class AbaFerias(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # --- BLOCO 1: DADOS DO FUNCIONÁRIO ---
        frm_func = ttk.LabelFrame(self, text="Dados do Funcionário", padding=10)
        frm_func.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frm_func, text="Nome:").grid(row=0, column=0, sticky="w")
        self.ent_nome = ttk.Entry(frm_func, width=30)
        self.ent_nome.grid(row=0, column=1, padx=5, sticky="w")
        
        ttk.Label(frm_func, text="Cargo:").grid(row=0, column=2, sticky="w")
        self.ent_cargo = ttk.Entry(frm_func, width=20)
        self.ent_cargo.grid(row=0, column=3, padx=5, sticky="w")
        
        ttk.Label(frm_func, text="Admissão (Opcional):").grid(row=0, column=4, sticky="w")
        self.ent_adm = ttk.Entry(frm_func, width=12)
        self.ent_adm.grid(row=0, column=5, padx=5, sticky="w")
        # Máscara de data
        self.ent_adm.bind("<KeyRelease>", lambda e: self.formatar_data(e, self.ent_adm))
        
        ttk.Label(frm_func, text="Salário Base:").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_salario = ttk.Entry(frm_func, width=15)
        self.ent_salario.grid(row=1, column=1, padx=5, sticky="w")

        # --- BLOCO 2: DATAS E PERÍODOS ---
        frm_dates = ttk.LabelFrame(self, text="Datas e Períodos", padding=10)
        frm_dates.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frm_dates, text="P. Aquisitivo (Opcional):").grid(row=0, column=0)
        self.ent_aq_ini = ttk.Entry(frm_dates, width=11)
        self.ent_aq_ini.grid(row=0, column=1)
        self.ent_aq_ini.bind("<KeyRelease>", lambda e: self.formatar_data(e, self.ent_aq_ini))
        
        ttk.Label(frm_dates, text="a").grid(row=0, column=2)
        
        self.ent_aq_fim = ttk.Entry(frm_dates, width=11)
        self.ent_aq_fim.grid(row=0, column=3)
        self.ent_aq_fim.bind("<KeyRelease>", lambda e: self.formatar_data(e, self.ent_aq_fim))
        
        ttk.Separator(frm_dates, orient='horizontal').grid(row=1, column=0, columnspan=6, sticky="ew", pady=10)
        
        ttk.Label(frm_dates, text="Início Gozo:").grid(row=2, column=0)
        self.ent_gozo_ini = ttk.Entry(frm_dates, width=11)
        self.ent_gozo_ini.grid(row=2, column=1)
        self.ent_gozo_ini.bind("<KeyRelease>", lambda e: self.formatar_data(e, self.ent_gozo_ini))

        self.var_modo = tk.StringVar(value="dias")
        ttk.Radiobutton(frm_dates, text="Total por Dias", variable=self.var_modo, value="dias", command=self.alternar_modo).grid(row=2, column=2)
        ttk.Radiobutton(frm_dates, text="Pela Data Retorno", variable=self.var_modo, value="data", command=self.alternar_modo).grid(row=2, column=3)
        
        ttk.Label(frm_dates, text="Total Dias (Gozo + Abono):").grid(row=3, column=0)
        self.ent_dias = ttk.Entry(frm_dates, width=8)
        self.ent_dias.insert(0, "30")
        self.ent_dias.grid(row=3, column=1)
        
        ttk.Label(frm_dates, text="Data Retorno:").grid(row=3, column=2)
        self.ent_retorno = ttk.Entry(frm_dates, width=11)
        self.ent_retorno.grid(row=3, column=3)
        self.ent_retorno.bind("<KeyRelease>", lambda e: self.formatar_data(e, self.ent_retorno))
        
        ttk.Button(frm_dates, text="Calcular Datas", command=self.calcular_datas_preview).grid(row=3, column=4, padx=10)

        # --- EXTRAS: ABONO E DOBRA ---
        frm_extras = ttk.Frame(frm_dates)
        frm_extras.grid(row=4, column=0, columnspan=5, sticky="w", pady=10)
        
        self.var_abono = tk.BooleanVar()
        ttk.Checkbutton(frm_extras, text="Vender 1/3 (Abono Pecuniário)", variable=self.var_abono, command=self.calcular_datas_preview).pack(side="left")
        
        self.var_dobra = tk.BooleanVar()
        ttk.Checkbutton(frm_extras, text="Pagar em Dobra", variable=self.var_dobra).pack(side="left", padx=20)

        # --- BLOCO 3: MÉDIAS ---
        self.frm_medias = FrameRubricas(self, "Médias para Base de Cálculo", tipo_evento="provento")
        self.frm_medias.pack(fill=tk.X, padx=10, pady=5)
        
        # --- BLOCO 4: BOTÕES ---
        frm_btns = ttk.Frame(self)
        frm_btns.pack(fill=tk.X, padx=50, pady=20)
        ttk.Button(frm_btns, text="GERAR AVISO DE FÉRIAS", command=self.acao_gerar_aviso).pack(side="left", fill=tk.X, expand=True, padx=5)
        ttk.Button(frm_btns, text="GERAR RECIBO DE FÉRIAS", command=self.acao_gerar_recibo).pack(side="left", fill=tk.X, expand=True, padx=5)

    def formatar_data(self, event, campo):
        if event.keysym == "BackSpace": return
        texto = "".join(filter(str.isdigit, campo.get().replace("/", "")))[:8]
        novo = ""
        for i, char in enumerate(texto):
            if i in [2, 4]: novo += "/"
            novo += char
        campo.delete(0, tk.END)
        campo.insert(0, novo)

    def alternar_modo(self):
        m = self.var_modo.get()
        self.ent_dias.config(state="normal" if m=="dias" else "readonly")
        self.ent_retorno.config(state="readonly" if m=="dias" else "normal")

    def calcular_datas_preview(self):
        data_ini = ferramentas.parse_data(self.ent_gozo_ini.get())
        if not data_ini: return None
        
        if self.var_modo.get() == "dias":
            try: total_dias = int(self.ent_dias.get())
            except: return None
            
            dias_gozo = int(total_dias * (2/3 if self.var_abono.get() else 1))
            dias_abono = total_dias - dias_gozo
            data_ret = data_ini + timedelta(days=dias_gozo)
            
            self.ent_retorno.config(state="normal")
            self.ent_retorno.delete(0, tk.END)
            self.ent_retorno.insert(0, data_ret.strftime("%d/%m/%Y"))
            self.ent_retorno.config(state="readonly")
            return dias_gozo, dias_abono, data_ret
        else:
            data_ret = ferramentas.parse_data(self.ent_retorno.get())
            if not data_ret: return None
            dias_gozo = (data_ret - data_ini).days
            if self.var_abono.get():
                total_dias = int(dias_gozo / (2/3))
                dias_abono = total_dias - dias_gozo
            else:
                total_dias = dias_gozo
                dias_abono = 0
            self.ent_dias.config(state="normal")
            self.ent_dias.delete(0, tk.END)
            self.ent_dias.insert(0, str(total_dias))
            self.ent_dias.config(state="readonly")
            return dias_gozo, dias_abono, data_ret

    def acao_gerar_aviso(self):
        res = self.calcular_datas_preview()
        if not res: return
        gozo, abono, ret = res
        d_func = {"nome": self.ent_nome.get(), "cargo": self.ent_cargo.get()}
        d_ferias = {
            "inicio": self.ent_gozo_ini.get(),
            "fim": (ret - timedelta(days=1)).strftime("%d/%m/%Y"),
            "retorno": ret.strftime("%d/%m/%Y"),
            "obs": f"Com {abono} dias de abono." if abono > 0 else "Sem abono."
        }
        relatorios.gerar_aviso_ferias(d_func, d_ferias)

    def acao_gerar_recibo(self):
        res = self.calcular_datas_preview()
        if not res: 
            messagebox.showwarning("Erro", "Verifique as datas de gozo.")
            return
            
        gozo, abono, ret = res
        salario = ferramentas.str_para_float(self.ent_salario.get())
        medias = self.frm_medias.get_dados_calculados(salario)
        base = salario + medias["total"]
        valor_dia = base / 30
        
        itens = []
        # 1. Férias Gozadas
        v_ferias = valor_dia * gozo
        v_terco = v_ferias / 3
        itens.append((f"Férias Gozadas ({gozo} dias)", f"{gozo}d", v_ferias, 0.0))
        itens.append(("1/3 Constitucional s/ Férias", "33.33%", v_terco, 0.0))
        
        # 2. Dobra (se houver)
        if self.var_dobra.get():
            itens.append(("Dobra de Férias (Art. 137 CLT)", "1/1", v_ferias, 0.0))
            itens.append(("1/3 s/ Dobra de Férias", "33.33%", v_terco, 0.0))

        # 3. Abono Pecuniário
        if abono > 0:
            v_abono = valor_dia * abono
            v_terco_abono = v_abono / 3
            itens.append((f"Abono Pecuniário ({abono} dias)", f"{abono}d", v_abono, 0.0))
            itens.append(("1/3 s/ Abono Pecuniário", "33.33%", v_terco_abono, 0.0))
            
        # Preparação dos dados com campos opcionais
        d_func = {
            "nome": self.ent_nome.get(),
            "cargo": self.ent_cargo.get() or "Não Informado",
            "admissao": self.ent_adm.get() or "Não Informado",
            "aq_ini": self.ent_aq_ini.get() or "...",
            "aq_fim": self.ent_aq_fim.get() or "...",
            "gozo_ini": self.ent_gozo_ini.get(),
            "gozo_fim": (ret - timedelta(days=1)).strftime("%d/%m/%Y"),
            "dias_gozo": gozo,
            "dias_abono": abono
        }
        
        relatorios.gerar_recibo_ferias_exclusivo(d_func, itens)