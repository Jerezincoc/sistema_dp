import tkinter as tk
from tkinter import ttk
import calendar
import config
import ferramentas


class FrameRubricas(ttk.LabelFrame):
    """
    Componente reutilizável para gestão de rubricas trabalhistas (proventos/descontos).
    Gera itens no formato compatível com relatorios.py refatorado (dicionários).
    """
    
    def __init__(self, parent, title, tipo_evento="provento"):
        super().__init__(parent, text=title, padding=10)
        self.tipo_evento = tipo_evento
        self.linhas = []  # Lista de dicionários com widgets de cada linha
        
        # --- LISTAS DE RUBRICAS ---
        self.opcoes_clt_prov = [
            "Selecione...", "Hora Extra 50%", "Hora Extra 100%", "Adicional Noturno (20%)",
            "DSR s/ Variáveis", "Feriado Trabalhado (100%)", "Premiação", "Gratificação",
            "Reembolso", "Comissão", "OUTROS (Digite o nome)"
        ]
        self.opcoes_clt_desc = [
            "Selecione...", "Faltas (Dias)", "DSR s/ Faltas", "Atrasos (Minutos)",
            "Adiantamento Salarial", "Vale Transporte", "Vale Alimentação", "OUTROS (Digite o nome)"
        ]
        
        self.opcoes_pro_prov = ["Selecione...", "Pro-Labore", "Distribuição de Lucros", "Reembolso Despesas"]
        self.opcoes_pro_desc = ["Selecione...", "INSS (Retido)", "IRRF (Retido)", "OUTROS (Digite o nome)"]
        
        # Define lista inicial (padrão CLT)
        self.lista_atual = self.opcoes_clt_prov if tipo_evento == "provento" else self.opcoes_clt_desc
        
        # --- CABEÇALHOS ---
        ttk.Label(self, text="Rubrica / Evento", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=2)
        ttk.Label(self, text="Descrição (se Outros)", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky="w", padx=2)
        ttk.Label(self, text="Qtd/Valor", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky="w", padx=2)
        ttk.Label(self, text="Unidade", font=("Segoe UI", 8, "italic")).grid(row=0, column=3, sticky="w", padx=5)
        
        # Botão Adicionar
        btn_add = ttk.Button(self, text="+ Item", command=self.add_linha, width=8)
        btn_add.grid(row=0, column=5, padx=10, sticky="e")
        
        self.add_linha()
    
    def mudar_tipo_contrato(self, tipo):
        """Atualiza as opções do combobox conforme tipo de contrato (CLT/Pro-Labore)."""
        self.limpar_tudo()
        
        if tipo == "CLT":
            self.lista_atual = self.opcoes_clt_prov if self.tipo_evento == "provento" else self.opcoes_clt_desc
        else:  # PRO
            self.lista_atual = self.opcoes_pro_prov if self.tipo_evento == "provento" else self.opcoes_pro_desc
        
        self.add_linha()
    
    def limpar_tudo(self):
        """Remove visualmente todas as linhas e limpa a lista interna."""
        for linha in self.linhas[:]:  # Cópia para evitar modificação durante iteração
            try:
                linha["cb"].destroy()
                linha["ent_desc"].destroy()
                linha["ent_val"].destroy()
                linha["lbl_unid"].destroy()
                linha["btn_del"].destroy()
            except:
                pass
        self.linhas.clear()
    
    def remover_linha(self, linha_dict):
        """Remove uma linha específica da interface e da lista interna."""
        try:
            linha_dict["cb"].destroy()
            linha_dict["ent_desc"].destroy()
            linha_dict["ent_val"].destroy()
            linha_dict["lbl_unid"].destroy()
            linha_dict["btn_del"].destroy()
            self.linhas.remove(linha_dict)
        except Exception as e:
            print(f"Erro ao remover linha: {e}")
    
    def add_linha(self):
        """Adiciona uma nova linha de entrada de rubrica."""
        row_idx = len(self.linhas) + 1
        
        # 1. Combobox de rubricas
        cb_rubrica = ttk.Combobox(self, values=self.lista_atual, width=25, state="readonly")
        cb_rubrica.current(0)
        cb_rubrica.grid(row=row_idx, column=0, padx=2, pady=2, sticky="w")
        
        # 2. Campo de descrição (para "OUTROS")
        ent_desc = ttk.Entry(self, width=20, state="disabled")
        ent_desc.grid(row=row_idx, column=1, padx=2, pady=2, sticky="w")
        
        # 3. Campo de valor/quantidade
        ent_valor = ttk.Entry(self, width=10)
        ent_valor.grid(row=row_idx, column=2, padx=2, pady=2, sticky="w")
        
        # 4. Label de unidade
        lbl_unid = ttk.Label(self, text="-", width=12, anchor="w")
        lbl_unid.grid(row=row_idx, column=3, padx=5, pady=2, sticky="w")
        
        # 5. Botão remover
        btn_del = tk.Button(
            self, text="✕", fg="red", font=("Arial", 10, "bold"),
            padx=4, pady=0, relief="flat", cursor="hand2",
            command=lambda ld=linha_dict: self.remover_linha(ld) if (linha_dict := next((l for l in self.linhas if l["cb"] == cb_rubrica), None)) else None
        )
        btn_del.grid(row=row_idx, column=4, padx=2, pady=2)
        
        # Dicionário com referências aos widgets
        linha_dict = {
            "cb": cb_rubrica,
            "ent_desc": ent_desc,
            "ent_val": ent_valor,
            "lbl_unid": lbl_unid,
            "btn_del": btn_del
        }
        
        # Bind de evento para atualizar unidade/descrição
        cb_rubrica.bind("<<ComboboxSelected>>", lambda e, ld=linha_dict: self.ao_mudar_rubrica(ld))
        self.linhas.append(linha_dict)
    
    def ao_mudar_rubrica(self, linha_dict):
        """Atualiza unidade e habilita/desabilita campos conforme rubrica selecionada."""
        escolha = linha_dict["cb"].get()
        
        # Resetar estado
        linha_dict["ent_desc"].config(state="disabled")
        linha_dict["ent_desc"].delete(0, tk.END)
        
        # Definir unidade conforme rubrica
        if "Hora" in escolha or "Noturno" in escolha:
            linha_dict["lbl_unid"].config(text="Horas")
        elif "Dias" in escolha or "Feriado" in escolha or "Faltas" in escolha:
            linha_dict["lbl_unid"].config(text="Dias")
        elif "OUTROS" in escolha:
            linha_dict["lbl_unid"].config(text="Valor (R$)")
            linha_dict["ent_desc"].config(state="normal")
            linha_dict["ent_desc"].focus()
        else:
            linha_dict["lbl_unid"].config(text="Valor (R$)")
    
    def get_dados_calculados(self, salario_base):
        """
        Calcula valores das rubricas com base no salário.
        Retorna dicionário com:
          - 'total': soma dos valores
          - 'itens': lista de dicionários no formato compatível com relatorios.py:
            {'descricao': str, 'ref': str, 'valor': float, 'desconto': float}
        """
        total_geral = 0.0
        lista_itens = []
        
        # Valores unitários
        val_hora = salario_base / config.DIVISOR_HORAS_MENSAL if salario_base > 0 else 0
        val_dia = salario_base / 30 if salario_base > 0 else 0
        
        for linha in self.linhas[:]:  # Iterar cópia para segurança
            try:
                escolha = linha["cb"].get().strip()
                if escolha == "Selecione..." or not escolha:
                    continue
                
                # Obter quantidade/valor digitado
                qtd_valor_input = ferramentas.str_para_float(linha["ent_val"].get())
                if qtd_valor_input <= 0:
                    continue
                
                valor_final = 0.0
                descricao_final = escolha
                ref_final = "-"
                
                # --- LÓGICA DE CÁLCULO POR RUBRICA ---
                # ⚠️ ORDEM IMPORTANTE: Verificar DSR ANTES de Faltas para evitar confusão
                
                if "Hora Extra 50%" in escolha:
                    valor_final = val_hora * qtd_valor_input * 1.50
                    descricao_final = f"Hora Extra 50%"
                    ref_final = f"{qtd_valor_input:.1f}h"
                
                elif "Hora Extra 100%" in escolha or "Feriado Trabalhado" in escolha:
                    valor_final = val_hora * qtd_valor_input * 2.00
                    descricao_final = "Feriado Trabalhado (100%)" if "Feriado" in escolha else "Hora Extra 100%"
                    ref_final = f"{qtd_valor_input:.1f}h"
                
                elif "Adicional Noturno" in escolha:
                    valor_final = val_hora * qtd_valor_input * 0.20
                    descricao_final = "Adic. Noturno 20%"
                    ref_final = f"{qtd_valor_input:.1f}h"
                
                elif "DSR" in escolha:
                    # DSR geralmente já vem calculado como valor monetário
                    valor_final = qtd_valor_input
                    descricao_final = escolha
                    ref_final = f"R$ {qtd_valor_input:.2f}"
                
                elif "Faltas" in escolha:
                    valor_final = val_dia * qtd_valor_input
                    descricao_final = f"Faltas"
                    ref_final = f"{int(qtd_valor_input)} dia(s)"
                
                elif "Atrasos" in escolha:
                    # Atrasos: converter minutos para fração de dia (considerando 8h = 480min)
                    valor_final = (qtd_valor_input / 480) * val_dia
                    descricao_final = "Atrasos"
                    ref_final = f"{int(qtd_valor_input)} min"
                
                elif "OUTROS" in escolha:
                    desc_manual = linha["ent_desc"].get().strip()
                    descricao_final = desc_manual if desc_manual else "Outros"
                    valor_final = qtd_valor_input
                    ref_final = f"R$ {qtd_valor_input:.2f}"
                
                else:
                    # Rubricas com valor fixo já digitado
                    valor_final = qtd_valor_input
                    ref_final = f"R$ {qtd_valor_input:.2f}"
                
                # Determinar se é provento ou desconto
                if self.tipo_evento == "provento":
                    item = {
                        'descricao': descricao_final,
                        'ref': ref_final,
                        'valor': round(valor_final, 2),
                        'desconto': 0.0
                    }
                else:
                    item = {
                        'descricao': descricao_final,
                        'ref': ref_final,
                        'valor': 0.0,
                        'desconto': round(valor_final, 2)
                    }
                
                total_geral += valor_final
                lista_itens.append(item)
            
            except Exception as e:
                print(f"Erro ao processar rubrica '{escolha}': {e}")
                continue
        
        return {
            "total": round(total_geral, 2),
            "itens": lista_itens
        }