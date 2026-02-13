# Arquivo: config.py
# Este arquivo contém todas as tabelas e constantes legais.
# Fácil de atualizar quando a legislação mudar.

# --- TABELA INSS 2026 (Progressiva) ---
INSS_TETO = 8475.55
INSS_TETO_CONTRIBUICAO = 998.00  # Valor máximo descontado (aprox)

# Lista de tuplas: (Limite da Faixa, Alíquota)
INSS_FAIXAS = [
    (1621.00, 0.075),  # 7.5%
    (2902.84, 0.090),  # 9%
    (4354.27, 0.120),  # 12%
    (8475.55, 0.140)   # 14%
]

# Alíquota fixa para Pro-Labore / Autônomos
INSS_ALIQUOTA_PROLABORE = 0.11

# --- TABELA IRRF 2026 (Progressiva) ---
# Dedução por dependente legal
IRRF_DEDUCAO_DEPENDENTE = 189.59

# Lista de tuplas: (Limite, Alíquota, Parcela a Deduzir)
IRRF_TABELA = [
    (2428.80, 0.000, 0.00),     # Isento
    (2826.65, 0.075, 182.16),   # 7.5%
    (3751.05, 0.150, 394.16),   # 15%
    (4664.68, 0.225, 675.49),   # 22.5%
    (float('inf'), 0.275, 908.73) # 27.5% (Acima de tudo)
]

# --- PARAMETROS GERAIS ---
FGTS_ALIQUOTA = 0.08
DIVISOR_HORAS_MENSAL = 220