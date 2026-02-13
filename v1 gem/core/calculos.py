# Arquivo: calculos.py
from datetime import date
import config # Importa as tabelas do nosso arquivo de configuração

def calcular_inss_progressivo(salario_bruto):
    """
    Calcula INSS fatia a fatia (Progressivo - Regra Pós-Reforma).
    Usa as faixas definidas em config.py.
    """
    desconto_total = 0
    faixa_anterior = 0
    
    # Se passar do teto, a gente podia retornar o teto fixo, 
    # mas o cálculo progressivo natural já deve bater no teto.
    # Por segurança, travamos no valor máximo definido no config.
    if salario_bruto > config.INSS_TETO:
        return config.INSS_TETO_CONTRIBUICAO

    for limite, aliquota in config.INSS_FAIXAS:
        if salario_bruto > faixa_anterior:
            # A base dessa fatia é o menor entre (salario ou limite da faixa) menos o que já foi tributado
            base_faixa = min(salario_bruto, limite) - faixa_anterior
            desconto_total += base_faixa * aliquota
            faixa_anterior = limite
        else:
            break
            
    return round(desconto_total, 2)

def calcular_inss_prolabore(valor_bruto):
    """
    Calcula INSS para Sócio/Autônomo (Alíquota fixa limitada ao teto).
    """
    base = min(valor_bruto, config.INSS_TETO)
    return round(base * config.INSS_ALIQUOTA_PROLABORE, 2)

def calcular_irrf(base_calculo, num_dependentes=0):
    """
    Calcula IRRF baseando-se na tabela vigente e dedução de dependentes.
    base_calculo: Já deve vir deduzida de INSS.
    """
    # 1. Abate valor dos dependentes da base
    total_deducao_deps = num_dependentes * config.IRRF_DEDUCAO_DEPENDENTE
    base_final = base_calculo - total_deducao_deps
    
    # 2. Encontra a faixa na tabela
    # A tabela no config é [(Limite1, Aliq1, Ded1), (Limite2, Aliq2, Ded2)...]
    aliquota_aplicar = 0.0
    parcela_deduzir = 0.0
    
    for limite, aliquota, deducao in config.IRRF_TABELA:
        if base_final <= limite:
            aliquota_aplicar = aliquota
            parcela_deduzir = deducao
            break
            
    imposto = (base_final * aliquota_aplicar) - parcela_deduzir
    
    # Imposto não pode ser negativo
    return round(max(0.0, imposto), 2)

def calcular_fgts(base_calculo):
    return round(base_calculo * config.FGTS_ALIQUOTA, 2)

def calcular_avos_proporcionais(data_adm, data_dem):
    """
    Retorna (avos_13, avos_ferias) considerando regra de 15 dias.
    """
    if not data_adm or not data_dem or data_adm > data_dem:
        return 0, 0

    # --- Cálculo 13º (Ano Corrente) ---
    inicio_ano = date(data_dem.year, 1, 1)
    inicio_contagem = max(data_adm, inicio_ano)
    
    avos_13 = 0
    curr = inicio_contagem
    while curr <= data_dem:
        # Verifica se trabalhou >= 15 dias no mês corrente da iteração
        dias_trabalhados = 30 # Assume mês cheio por padrão
        
        # Se for o mês de admissão
        if curr.month == data_adm.month and curr.year == data_adm.year:
            # Dias no mês (simplificado para 30 para fim comercial ou calendário real)
            import calendar
            _, last_day = calendar.monthrange(curr.year, curr.month)
            dias_trabalhados = last_day - data_adm.day + 1
            
        # Se for mês de demissão
        if curr.month == data_dem.month and curr.year == data_dem.year:
            dias_trabalhados = data_dem.day
            
        if dias_trabalhados >= 15:
            avos_13 += 1
            
        # Avança mês
        if curr.month == 12: curr = date(curr.year + 1, 1, 1)
        else: curr = date(curr.year, curr.month + 1, 1)
        
        if avos_13 >= 12: break # Trava em 12/12

    # --- Cálculo Férias (Período Aquisitivo) ---
    aniversario = date(data_dem.year, data_adm.month, data_adm.day)
    if aniversario > data_dem:
        aniversario = date(data_dem.year - 1, data_adm.month, data_adm.day)
    
    delta = data_dem - aniversario
    meses_ferias = int(delta.days / 30)
    if (delta.days % 30) >= 15:
        meses_ferias += 1
        
    return min(avos_13, 12), min(meses_ferias, 12)