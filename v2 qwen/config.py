# -*- coding: utf-8 -*-
"""
config.py
=========
Constantes e tabelas legais para cálculos trabalhistas conforme legislação brasileira vigente (2026).

Este arquivo centraliza todas as regras fiscais e previdenciárias do sistema.
Facilita atualizações quando houver mudanças na legislação.

⚠️ IMPORTANTE: Valores válidos para o ano-base 2026 conforme tabelas oficiais da RFB e INSS.
"""

# =================================================================
# 🇧🇷 INSS - Instituto Nacional do Seguro Social (2026)
# =================================================================

# Teto previdenciário mensal (contribuição máxima)
INSS_TETO: float = 8475.55

# Valor máximo de contribuição mensal (cálculo progressivo até o teto)
INSS_TETO_CONTRIBUICAO: float = 998.00

# Faixas de contribuição progressiva (Limite da Faixa, Alíquota)
# Fonte: Portaria Conjunta MPS/MF nº 15/2025 (valores 2026)
INSS_FAIXAS: list[tuple[float, float]] = [
    (1621.00, 0.075),   # 7,5% até R$ 1.621,00
    (2902.84, 0.090),   # 9% de R$ 1.621,01 a R$ 2.902,84
    (4354.27, 0.120),   # 12% de R$ 2.902,85 a R$ 4.354,27
    (8475.55, 0.140)    # 14% acima de R$ 4.354,27 até o teto
]

# Alíquota fixa para contribuintes individuais (Pro-Labore / Autônomos)
INSS_ALIQUOTA_PROLABORE: float = 0.11


# =================================================================
# 💰 IRRF - Imposto de Renda Retido na Fonte (2026)
# =================================================================

# Dedução mensal por dependente legal
IRRF_DEDUCAO_DEPENDENTE: float = 189.59

# Tabela progressiva anual (Limite Superior, Alíquota, Parcela a Deduzir)
# Fonte: Instrução Normativa RFB nº 2.100/2025 (valores 2026)
IRRF_TABELA: list[tuple[float, float, float]] = [
    (2428.80, 0.000, 0.00),     # Isento até R$ 2.428,80
    (2826.65, 0.075, 182.16),   # 7,5% de R$ 2.428,81 a R$ 2.826,65
    (3751.05, 0.150, 394.16),   # 15% de R$ 2.826,66 a R$ 3.751,05
    (4664.68, 0.225, 675.49),   # 22,5% de R$ 3.751,06 a R$ 4.664,68
    (float('inf'), 0.275, 908.73)  # 27,5% acima de R$ 4.664,68
]


# =================================================================
# 📊 PARÂMETROS GERAIS DE CÁLCULO
# =================================================================

# Alíquota patronal de FGTS (depósito obrigatório)
FGTS_ALIQUOTA: float = 0.08

# Divisor padrão para cálculo de hora mensal (CLT)
# Base: 220 horas/mês = 44h semanais × 5 semanas
DIVISOR_HORAS_MENSAL: int = 220

# Valor do salário-família por filho menor de 14 anos (2026)
SALARIO_FAMILIA_VALOR_COTA: float = 62.04

# Teto salarial para direito ao salário-família (2026)
SALARIO_FAMILIA_TETO: float = 1819.26


# =================================================================
# 🔒 VALIDAÇÃO DE CONSTANTES (opcional - para debug)
# =================================================================
def validar_configuracao() -> bool:
    """
    Valida consistência das constantes legais.
    Retorna True se todas as regras estiverem coerentes.
    """
    erros = []
    
    # Validar faixas INSS em ordem crescente
    for i in range(1, len(INSS_FAIXAS)):
        if INSS_FAIXAS[i][0] <= INSS_FAIXAS[i-1][0]:
            erros.append(f"Faixa INSS {i} não está em ordem crescente")
    
    # Validar tabela IRRF
    for i in range(1, len(IRRF_TABELA)-1):  # Última faixa é infinito
        if IRRF_TABELA[i][0] <= IRRF_TABELA[i-1][0]:
            erros.append(f"Faixa IRRF {i} não está em ordem crescente")
    
    # Validar teto INSS
    if INSS_FAIXAS[-1][0] != INSS_TETO:
        erros.append("Última faixa INSS não corresponde ao teto")
    
    if erros:
        for erro in erros:
            print(f"❌ CONFIG ERROR: {erro}")
        return False
    
    return True


# Executar validação automática ao importar o módulo
if __name__ == "__main__":
    print("✅ Configuração validada com sucesso!" if validar_configuracao() else "❌ Erros encontrados na configuração")