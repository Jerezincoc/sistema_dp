# Arquivo: ui/widgets.py
import tkinter as tk
from tkinter import ttk
from core import config, ferramentas  # <-- Ajustado para a nova pasta

class FrameRubricas(ttk.LabelFrame):
    # ... (O resto do seu código original do componentes.py permanece igual)
    def __init__(self, parent, title, tipo_evento="provento"):
        super().__init__(parent, text=title, padding=10)
        self.tipo_evento = tipo_evento
        self.linhas = [] # Guarda os widgets de cada linha
        
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
        self.opcoes_pro_desc = ["Selecione...", "INSS (Retido)", "IRRF (Retido)", "OUTROS"]

        # Define qual lista usar inicialmente (Padrão CLT)
        self.lista_atual = self.opcoes_clt_prov if tipo_evento == "provento" else self.opcoes_clt_desc

        # Cabeçalhos
        ttk.Label(self, text="Rubrica / Evento", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(self, text="Descrição (se Outros)", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky="w")
        ttk.Label(self, text="Qtd/Valor", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky="w")
        ttk.Label(self, text="Unidade", font=("Segoe UI", 8, "italic")).grid(row=0, column=3, sticky="w")
        
        # Botão Adicionar
        btn_add = ttk.Button(self, text="+ Item", command=self.add_linha, width=8)
        btn_add.grid(row=0, column=5, padx=10, sticky="e")
        
        self.add_linha()

    def mudar_tipo_contrato(self, tipo):
        """Atualiza a lista do Combobox quando muda CLT/Pro-Labore"""
        # Limpa tudo primeiro para evitar confusão
        self.limpar_tudo()
        
        if tipo == "CLT":
            self.lista_atual = self.opcoes_clt_prov if self.tipo_evento == "provento" else self.opcoes_clt_desc
        else:
            self.lista_atual = self.opcoes_pro_prov if self.tipo_evento == "provento" else self.opcoes_pro_desc
            
        # Adiciona uma linha nova vazia com as novas opções
        self.add_linha()

    def limpar_tudo(self):
        """Apaga todas as linhas da tela"""
        for linha in self.linhas:
            # Destroi os widgets visuais
            for widget in linha.values():
                if isinstance(widget, tk.Widget):
                    widget.destroy()
        self.linhas = []

    def remover_linha(self, frame_linha, linha_dict):
        """Remove uma linha específica"""
        # Remove visualmente
        for widget in linha_dict.values():
            if isinstance(widget, tk.Widget):
                widget.destroy()
        # Remove da lista de dados
        if linha_dict in self.linhas:
            self.linhas.remove(linha_dict)

    def add_linha(self):
        row_idx = len(self.linhas) + 1
        
        # 1. Combobox
        cb_rubrica = ttk.Combobox(self, values=self.lista_atual, width=25, state="readonly")
        cb_rubrica.current(0)
        cb_rubrica.grid(row=row_idx, column=0, padx=2, pady=2)
        
        # 2. Descrição (Outros)
        ent_desc = ttk.Entry(self, width=20, state="disabled")
        ent_desc.grid(row=row_idx, column=1, padx=2)
        
        # 3. Valor
        ent_valor = ttk.Entry(self, width=10)
        ent_valor.grid(row=row_idx, column=2, padx=2)
        
        # 4. Unidade
        lbl_unid = ttk.Label(self, text="-")
        lbl_unid.grid(row=row_idx, column=3, padx=5)
        
        # 5. Botão Remover (X)
        # Precisamos de um truque (closure) para o botão saber qual linha apagar
        btn_del = tk.Button(self, text="X", fg="red", font=("Arial", 8, "bold"), padx=2, pady=0)
        btn_del.grid(row=row_idx, column=4, padx=2)
        
        # Dicionário que guarda os widgets dessa linha
        linha_data = {
            "cb": cb_rubrica,
            "ent_desc": ent_desc,
            "ent_val": ent_valor,
            "lbl_unid": lbl_unid,
            "btn_del": btn_del
        }
        
        # Configura o comando do botão remover passando a própria linha
        btn_del.config(command=lambda: self.remover_linha(None, linha_data))
        
        cb_rubrica.bind("<<ComboboxSelected>>", lambda e, ld=linha_data: self.ao_mudar_rubrica(ld))
        self.linhas.append(linha_data)

    def ao_mudar_rubrica(self, linha_data):
        escolha = linha_data["cb"].get()
        
        linha_data["ent_desc"].config(state="disabled")
        linha_data["ent_desc"].delete(0, tk.END)
        
        if "Hora" in escolha or "Noturno" in escolha:
            linha_data["lbl_unid"].config(text="Horas")
        elif "Dias" in escolha or "Feriado" in escolha or "Faltas (Dias)" in escolha:
            linha_data["lbl_unid"].config(text="Dias")
        elif "OUTROS" in escolha:
            linha_data["lbl_unid"].config(text="Valor (R$)")
            linha_data["ent_desc"].config(state="normal")
            linha_data["ent_desc"].focus()
        else:
            linha_data["lbl_unid"].config(text="Valor (R$)")

    def get_dados_calculados(self, salario_base):
        total_geral = 0.0
        lista_itens = []
        
        val_hora = salario_base / config.DIVISOR_HORAS_MENSAL if salario_base > 0 else 0
        val_dia = salario_base / 30 if salario_base > 0 else 0

        for linha in self.linhas:
            # Verifica se o widget ainda existe (caso tenha sido apagado mas ficado na memória)
            try:
                escolha = linha["cb"].get()
            except:
                continue 

            if escolha == "Selecione...": continue
            
            qtd_valor_input = ferramentas.str_para_float(linha["ent_val"].get())
            if qtd_valor_input <= 0: continue
            
            valor_final = 0.0
            nome_final = escolha

            # --- LÓGICA DE CÁLCULO ---
            if "Hora Extra 50%" in escolha:
                valor_final = val_hora * qtd_valor_input * 1.50
                nome_final = f"Hora Extra 50% ({qtd_valor_input}h)"
            
            elif "Hora Extra 100%" in escolha or "Feriado" in escolha:
                valor_final = val_hora * qtd_valor_input * 2.00
                nome_final = f"{escolha} ({qtd_valor_input}h/d)"
                
            elif "Adicional Noturno" in escolha:
                valor_final = val_hora * qtd_valor_input * 0.20
                nome_final = f"Adic. Noturno 20% ({qtd_valor_input}h)"

            # CORREÇÃO DO ERRO DE "DSR" VIRANDO "FALTAS"
            # A ordem importa: verifica DSR primeiro
            elif "DSR" in escolha:
                valor_final = qtd_valor_input # DSR geralmente digitamos o valor calculado
                nome_final = escolha # Mantém o nome DSR

            elif "Faltas" in escolha:
                valor_final = val_dia * qtd_valor_input
                nome_final = f"Faltas ({int(qtd_valor_input)} dias)"

            elif "OUTROS" in escolha:
                desc_manual = linha["ent_desc"].get().strip()
                nome_final = desc_manual if desc_manual else "Outros"
                valor_final = qtd_valor_input
            
            else:
                valor_final = qtd_valor_input

            total_geral += valor_final
            lista_itens.append((nome_final, valor_final))
                
        return {"total": total_geral, "itens": lista_itens}