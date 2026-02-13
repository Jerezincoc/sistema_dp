# Arquivo: ferramentas.py
import datetime
import sys
import os

def obter_caminho_recurso(relativo):
    """ Retorna o caminho real do arquivo, seja rodando script ou no EXE """
    if getattr(sys, 'frozen', False):
        # Se for EXE, o PyInstaller extrai para esta pasta temporária
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relativo)

def formatar_moeda(valor):
    """
    Recebe um float (ex: 1250.5) e retorna string formatada (R$ 1.250,50)
    """
    if valor is None: valor = 0.0
    # Truque do replace para inverter ponto e vírgula padrão US -> BR
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def parse_data(data_str):
    """
    Converte string 'DD/MM/AAAA' para objeto Date do Python.
    Retorna None se a data for inválida.
    """
    try:
        return datetime.datetime.strptime(data_str, "%d/%m/%Y").date()
    except (ValueError, TypeError):
        return None

def str_para_float(valor_str):
    """
    Converte inputs sujos do usuário (ex: '1.200,50' ou 'R$ 1000') para float (1200.50).
    Essencial para evitar erro de cálculo.
    """
    if not valor_str: return 0.0
    
    # Remove R$ e espaços
    limpo = str(valor_str).replace("R$", "").strip()
    
    # Lógica para tratar ponto de milhar e vírgula decimal
    if "," in limpo:
        # Se tem vírgula, assumimos que é decimal. Removemos os pontos de milhar antes.
        limpo = limpo.replace(".", "").replace(",", ".")
    
    try:
        return float(limpo)
    except ValueError:
        return 0.0