import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import relatorios


class AbaPonto(ttk.Frame):
    """Aba para geração de lista de frequência (folha de ponto)."""
    
    MESES = [(i, datetime.date(2000, i, 1).strftime('%B').capitalize()) for i in range(1, 13)]
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        # --- BLOCO 1: DADOS DA EMPRESA (CABEÇALHO DIREITO) ---
        frm_emp = ttk.LabelFrame(self, text="Informações da Empresa (Cabeçalho Direito)", padding=10)
        frm_emp.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frm_emp, text="Empresa:").grid(row=0, column=0, sticky="w", pady=2)
        self.ent_empresa = ttk.Entry(frm_emp, width=50)
        self.ent_empresa.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(frm_emp, text="CPF/CNPJ:").grid(row=0, column=2, sticky="w", padx=10)
        self.ent_cpf = ttk.Entry(frm_emp, width=20)
        self.ent_cpf.grid(row=0, column=3, padx=5, pady=2, sticky="w")
        
        ttk.Label(frm_emp, text="Endereço:").grid(row=1, column=0, sticky="w", pady=2)
        self.ent_endereco = ttk.Entry(frm_emp, width=80)
        self.ent_endereco.grid(row=1, column=1, columnspan=3, padx=5, pady=2, sticky="w")
        
        # --- BLOCO 2: DADOS DO TRABALHADOR ---
        frm_func = ttk.LabelFrame(self, text="Dados do Funcionário", padding=10)
        frm_func.pack(fill=tk.X, padx=10, pady=5)
        
        # Linha 1: Nome e Cargo (obrigatórios)
        ttk.Label(frm_func, text="Nome: *").grid(row=0, column=0, sticky="w", pady=2)
        self.ent_nome = ttk.Entry(frm_func, width=40)
        self.ent_nome.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(frm_func, text="Cargo: *").grid(row=0, column=2, sticky="w", padx=10)
        self.ent_cargo = ttk.Entry(frm_func, width=25)
        self.ent_cargo.grid(row=0, column=3, padx=5, pady=2, sticky="w")
        
        # Linha 2: CTPS e Série
        ttk.Label(frm_func, text="CTPS:").grid(row=1, column=0, sticky="w", pady=2)
        self.ent_ctps = ttk.Entry(frm_func, width=20)
        self.ent_ctps.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(frm_func, text="Série/UF:").grid(row=1, column=2, sticky="w", padx=10)
        self.ent_serie = ttk.Entry(frm_func, width=25)
        self.ent_serie.grid(row=1, column=3, padx=5, pady=2, sticky="w")
        
        # Linha 3: Jornada e Lotação
        ttk.Label(frm_func, text="Jornada:").grid(row=2, column=0, sticky="w", pady=2)
        self.ent_jornada = ttk.Entry(frm_func, width=40)
        self.ent_jornada.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        self.ent_jornada.insert(0, "8h diárias (Segunda a Sexta)")
        
        ttk.Label(frm_func, text="Lotação:").grid(row=2, column=2, sticky="w", padx=10)
        self.ent_lotacao = ttk.Entry(frm_func, width=25)
        self.ent_lotacao.grid(row=2, column=3, padx=5, pady=2, sticky="w")
        self.ent_lotacao.insert(0, "Administrativo")
        
        # --- BLOCO 3: SELEÇÃO DE PERÍODO ---
        frm_periodo = ttk.LabelFrame(self, text="Mês de Referência", padding=10)
        frm_periodo.pack(fill=tk.X, padx=10, pady=5)
        
        hoje = datetime.date.today()
        
        ttk.Label(frm_periodo, text="Mês:").grid(row=0, column=0, sticky="w")
        self.cb_mes = ttk.Combobox(
            frm_periodo,
            values=[f"{i:02d} - {nome}" for i, nome in self.MESES],
            state="readonly",
            width=20
        )
        self.cb_mes.set(f"{hoje.month:02d} - {datetime.date(2000, hoje.month, 1).strftime('%B').capitalize()}")
        self.cb_mes.grid(row=0, column=1, padx=5)
        
        ttk.Label(frm_periodo, text="Ano:").grid(row=0, column=2, sticky="w", padx=10)
        self.cb_ano = ttk.Combobox(
            frm_periodo,
            values=[str(i) for i in range(2024, 2031)],
            state="readonly",
            width=8
        )
        self.cb_ano.set(str(hoje.year))
        self.cb_ano.grid(row=0, column=3, padx=5)
        
        # --- BOTÃO DE GERAÇÃO ---
        btn_gerar = ttk.Button(
            self,
            text="📄 GERAR LISTA DE FREQUÊNCIA",
            command=self._gerar_lista,
            style="Accent.TButton"
        )
        btn_gerar.pack(pady=25, fill=tk.X, padx=120, ipady=10)
    
    def _gerar_lista(self):
        """Valida entradas e gera a lista de frequência."""
        # Validação obrigatória
        nome = self.ent_nome.get().strip().upper()
        cargo = self.ent_cargo.get().strip().upper()
        
        if not nome:
            messagebox.showwarning("Atenção", "⚠️ O campo 'Nome' é obrigatório.")
            self.ent_nome.focus()
            return
        
        if not cargo:
            messagebox.showwarning("Atenção", "⚠️ O campo 'Cargo' é obrigatório.")
            self.ent_cargo.focus()
            return
        
        # Extração do mês/ano selecionados
        try:
            mes_str = self.cb_mes.get().split(" - ")[0]
            mes = int(mes_str)
            ano = int(self.cb_ano.get())
        except (ValueError, IndexError):
            messagebox.showerror("Erro", "⚠️ Período inválido. Selecione mês e ano válidos.")
            return
        
        # Montagem dos dados para o relatório
        dados = {
            "empresa": self.ent_empresa.get().strip().upper() or "...",
            "cpf": self.ent_cpf.get().strip() or "...",
            "endereco": self.ent_endereco.get().strip().upper() or "...",
            "nome": nome,
            "cargo": cargo,
            "ctps": self.ent_ctps.get().strip() or "...",
            "serie": self.ent_serie.get().strip() or "...",
            "jornada": self.ent_jornada.get().strip() or "8h diárias",
            "lotacao": self.ent_lotacao.get().strip() or "Administrativo",
            "periodo": f"{mes:02d}/{ano}"
        }
        
        # Geração do relatório
        try:
            relatorios.gerar_lista_frequencia(dados)
        except Exception as e:
            messagebox.showerror(
                "Erro na Geração",
                f"❌ Falha ao gerar lista de frequência:\n{str(e)}"
            )
            import traceback
            traceback.print_exc()