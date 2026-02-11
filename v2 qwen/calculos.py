"""
Módulo de cálculos trabalhistas conforme legislação brasileira vigente (2026).
Contém funções para INSS, IRRF, FGTS e cálculo proporcional de avos.
"""
from datetime import date, datetime
import calendar
from typing import Tuple
import config


def calcular_inss_progressivo(salario_bruto: float) -> float:
    """
    Calcula o INSS com alíquotas progressivas (regra pós-reforma).
    
    Args:
        salario_bruto: Valor bruto do salário para cálculo
        
    Returns:
        Valor do desconto INSS arredondado para 2 casas decimais
        
    Observação:
        Respeita o teto previdenciário definido em config.INSS_TETO
    """
    if salario_bruto <= 0:
        return 0.0
    
    # Aplicar teto previdenciário
    if salario_bruto >= config.INSS_TETO:
        return round(config.INSS_TETO_CONTRIBUICAO, 2)
    
    desconto_total = 0.0
    faixa_anterior = 0.0
    
    for limite, aliquota in config.INSS_FAIXAS:
        if salario_bruto <= faixa_anterior:
            break
        
        base_faixa = min(salario_bruto, limite) - faixa_anterior
        desconto_total += base_faixa * aliquota
        faixa_anterior = limite
    
    return round(desconto_total, 2)


def calcular_inss_prolabore(valor_bruto: float) -> float:
    """
    Calcula INSS para sócios/autônomos (alíquota fixa de 11% com teto).
    
    Args:
        valor_bruto: Valor do pro-labore
        
    Returns:
        Valor do INSS arredondado para 2 casas decimais
    """
    if valor_bruto <= 0:
        return 0.0
    
    base = min(valor_bruto, config.INSS_TETO)
    return round(base * config.INSS_ALIQUOTA_PROLABORE, 2)


def calcular_irrf(base_calculo: float, num_dependentes: int = 0) -> float:
    """
    Calcula o Imposto de Renda Retido na Fonte (IRRF).
    
    Args:
        base_calculo: Base de cálculo já deduzida do INSS
        num_dependentes: Quantidade de dependentes para dedução
        
    Returns:
        Valor do imposto devido (nunca negativo)
    """
    if base_calculo <= 0:
        return 0.0
    
    # Dedução por dependentes
    deducao_dependentes = num_dependentes * config.IRRF_DEDUCAO_DEPENDENTE
    base_final = max(0.0, base_calculo - deducao_dependentes)
    
    # Encontrar faixa tributária
    aliquota = 0.0
    parcela_deduzir = 0.0
    
    for limite, aliq, ded in config.IRRF_TABELA:
        if base_final <= limite:
            aliquota = aliq
            parcela_deduzir = ded
            break
    
    imposto = (base_final * aliquota) - parcela_deduzir
    return round(max(0.0, imposto), 2)


def calcular_fgts(base_calculo: float) -> float:
    """
    Calcula o depósito mensal de FGTS (8% sobre a base de cálculo).
    
    Args:
        base_calculo: Base para cálculo do FGTS (salário + adicionais)
        
    Returns:
        Valor do depósito FGTS arredondado para 2 casas decimais
    """
    if base_calculo <= 0:
        return 0.0
    
    return round(base_calculo * config.FGTS_ALIQUOTA, 2)


def calcular_avos_proporcionais(data_adm: date, data_dem: date) -> Tuple[int, int]:
    """
    Calcula avos proporcionais de 13º salário e férias conforme CLT.
    
    Regras aplicadas:
    - 13º salário: 1 avo por mês com ≥15 dias trabalhados no ano corrente
    - Férias: 1 avo por mês completo no último período aquisitivo (≥15 dias = +1 avo)
    
    Args:
        data_adm: Data de admissão do empregado
        data_dem: Data de demissão/rescisão
        
    Returns:
        Tupla (avos_13, avos_ferias) com valores entre 0 e 12
        
    Raises:
        ValueError: Se datas forem inválidas ou admissão posterior à demissão
    """
    # Validação de datas
    if not isinstance(data_adm, date) or not isinstance(data_dem, date):
        raise ValueError("Datas devem ser objetos datetime.date")
    
    if data_adm > data_dem:
        raise ValueError("Data de admissão não pode ser posterior à data de demissão")
    
    # --- CÁLCULO DO 13º SALÁRIO ---
    # Considera apenas o ano corrente da demissão
    inicio_ano = date(data_dem.year, 1, 1)
    inicio_contagem = max(data_adm, inicio_ano)
    
    avos_13 = 0
    mes_atual = inicio_contagem.month
    ano_atual = inicio_contagem.year
    
    # Iterar pelos meses do ano corrente até a data de demissão
    while mes_atual <= data_dem.month and ano_atual == data_dem.year:
        # Determinar dias trabalhados no mês
        if mes_atual == data_adm.month and ano_atual == data_adm.year:
            # Mês de admissão: dias a partir da data de admissão
            _, ultimo_dia = calendar.monthrange(ano_atual, mes_atual)
            dias_trabalhados = ultimo_dia - data_adm.day + 1
        elif mes_atual == data_dem.month and ano_atual == data_dem.year:
            # Mês de demissão: dias até a data de demissão
            dias_trabalhados = data_dem.day
        else:
            # Meses completos
            dias_trabalhados = 30  # Simplificação comercial (CLT admite 30 dias)
        
        if dias_trabalhados >= 15:
            avos_13 += 1
        
        mes_atual += 1
    
    # --- CÁLCULO DAS FÉRIAS PROPORCIONAIS ---
    # Determinar início do último período aquisitivo
    if data_dem.month >= data_adm.month:
        ano_base = data_dem.year - 1
    else:
        ano_base = data_dem.year - 2
    
    try:
        inicio_aquisitivo = date(ano_base, data_adm.month, data_adm.day)
    except ValueError:
        # Caso dia 29/30/31 não exista no mês (ex: 31/02), ajustar para último dia do mês
        ultimo_dia = calendar.monthrange(ano_base, data_adm.month)[1]
        inicio_aquisitivo = date(ano_base, data_adm.month, ultimo_dia)
    
    # Garantir que início do período seja anterior à admissão original
    while inicio_aquisitivo > data_adm:
        inicio_aquisitivo = date(inicio_aquisitivo.year - 1, inicio_aquisitivo.month, inicio_aquisitivo.day)
    
    # Calcular dias trabalhados no período aquisitivo
    dias_trabalhados = (data_dem - inicio_aquisitivo).days
    meses_completos = dias_trabalhados // 30
    dias_restantes = dias_trabalhados % 30
    
    avos_ferias = meses_completos
    if dias_restantes >= 15:
        avos_ferias += 1
    
    # Limitar a 12 avos (máximo legal)
    return min(avos_13, 12), min(avos_ferias, 12)