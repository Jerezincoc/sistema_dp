from typing import Dict, Any

class CalculadoraPorFora:
    """
    Motor de cálculo puro para a modalidade EXTRA (Por Fora).
    Isolado de tributações oficiais. Focado em fluxo de caixa de RH:
    Comissões, Prêmios, Adiantamentos e Acertos diretos.
    """

    @classmethod
    def processar_pagamento_extra(
        cls, 
        salario_base_extra: float = 0.0, 
        comissoes: float = 0.0, 
        bonus: float = 0.0, 
        adiantamentos: float = 0.0,
        descontos_diversos: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calcula o recibo extraoficial.
        Garante que o saldo devedor seja registrado caso os descontos 
        superem os vencimentos no mês.
        """
        total_vencimentos = salario_base_extra + comissoes + bonus
        total_descontos = adiantamentos + descontos_diversos
        
        liquido_calculado = total_vencimentos - total_descontos
        
        # Se os descontos superam os ganhos, o líquido zera e gera saldo devedor
        liquido_a_pagar = max(0.0, liquido_calculado)
        saldo_devedor = abs(liquido_calculado) if liquido_calculado < 0 else 0.0

        return {
            "vencimentos": {
                "salario_base_extra": round(salario_base_extra, 2),
                "comissoes": round(comissoes, 2),
                "bonus": round(bonus, 2),
                "total_bruto": round(total_vencimentos, 2)
            },
            "descontos": {
                "adiantamentos": round(adiantamentos, 2),
                "outros_descontos": round(descontos_diversos, 2),
                "total_descontos": round(total_descontos, 2)
            },
            "liquido": round(liquido_a_pagar, 2),
            "saldo_devedor_proximo_mes": round(saldo_devedor, 2)
        }