# -*- coding: utf-8 -*-
"""
ferramentas.py
==============
Utilitários compartilhados para formatação, parsing e recursos do sistema DP.
"""

import datetime
import sys
import os
from typing import Optional, Union


def obter_caminho_recurso(relativo: str) -> str:
    """
    Retorna o caminho absoluto do recurso, funcionando tanto em script Python 
    quanto em executável compilado (PyInstaller).
    
    Args:
        relativo: Caminho relativo ao diretório raiz do projeto
        
    Returns:
        Caminho absoluto para o recurso
    """
    if getattr(sys, 'frozen', False):
        # Modo PyInstaller: recursos estão na pasta _MEIPASS
        base_path = sys._MEIPASS
    else:
        # Modo script: pasta atual do arquivo
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relativo)


def formatar_moeda(valor: Union[float, int, None]) -> str:
    """
    Formata valor numérico para padrão monetário brasileiro (R$ 1.234,56).
    
    Args:
        valor: Valor numérico ou None (tratado como 0.0)
        
    Returns:
        String formatada no padrão brasileiro
        
    Examples:
        >>> formatar_moeda(1250.5)
        'R$ 1.250,50'
        >>> formatar_moeda(None)
        'R$ 0,00'
    """
    if valor is None:
        valor = 0.0
    
    # Formatação robusta: separador de milhar = ponto, decimal = vírgula
    valor_abs = abs(valor)
    inteiro = int(valor_abs)
    decimal = int(round((valor_abs - inteiro) * 100))
    
    # Formatar parte inteira com separador de milhar
    partes = []
    while inteiro > 0:
        partes.append(f"{inteiro % 1000:03d}" if inteiro >= 1000 else f"{inteiro}")
        inteiro //= 1000
    parte_inteira = ".".join(reversed(partes)) if partes else "0"
    
    sinal = "-" if valor < 0 else ""
    return f"{sinal}R$ {parte_inteira},{decimal:02d}"


def parse_data(data_str: Optional[str]) -> Optional[datetime.date]:
    """
    Converte string no formato 'DD/MM/AAAA' para objeto datetime.date.
    
    Args:
        data_str: String de data ou None
        
    Returns:
        Objeto date válido ou None se a conversão falhar
        
    Examples:
        >>> parse_data("25/12/2026")
        datetime.date(2026, 12, 25)
        >>> parse_data("31/02/2026")  # Data inválida
        None
    """
    if not data_str or not isinstance(data_str, str):
        return None
    
    try:
        # Remover espaços extras e normalizar
        data_limpa = data_str.strip()
        return datetime.datetime.strptime(data_limpa, "%d/%m/%Y").date()
    except (ValueError, TypeError):
        return None


def str_para_float(valor_str: Optional[str]) -> float:
    """
    Converte string de valor monetário brasileiro para float.
    Trata formatos: "1.200,50", "R$ 1200,50", "1200.50", etc.
    
    Args:
        valor_str: String representando valor monetário
        
    Returns:
        Valor numérico float (0.0 em caso de erro)
        
    Examples:
        >>> str_para_float("1.200,50")
        1200.5
        >>> str_para_float("R$ 2.500,00")
        2500.0
        >>> str_para_float("1200.50")  # Formato US
        1200.5
    """
    if not valor_str:
        return 0.0
    
    # Converter para string e remover caracteres não numéricos (exceto vírgula e ponto)
    limpo = str(valor_str).strip().replace("R$", "").replace(" ", "")
    
    # Caso especial: string vazia após limpeza
    if not limpo:
        return 0.0
    
    # Estratégia robusta para formatos brasileiros:
    # 1. Se houver vírgula E ponto → remover pontos (milhar) e substituir vírgula por ponto (decimal)
    # 2. Se houver apenas vírgula → substituir por ponto
    # 3. Se houver apenas ponto → assumir formato US (ponto como decimal)
    
    if "," in limpo and "." in limpo:
        # Formato BR com milhar: "1.200,50" → remover pontos de milhar
        limpo = limpo.replace(".", "").replace(",", ".")
    elif "," in limpo:
        # Formato BR sem milhar: "1200,50" → substituir vírgula por ponto
        limpo = limpo.replace(",", ".")
    # else: formato US já está correto ("1200.50")
    
    try:
        return float(limpo)
    except ValueError:
        return 0.0