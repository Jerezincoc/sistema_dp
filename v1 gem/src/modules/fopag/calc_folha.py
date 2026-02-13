from typing import Dict, Any

class CalculadoraFopag:

    FAIXAS_INSS = [
        (1621.00, 0.075, 0.0),
        (2902.84, 0.09, 24.32),
        (4354.27, 0.12, 111.40),
        (8475.55, 0.14, 198.49)
    ]
    TETO_INSS = 8475.55
    MAX_DESCONTO_INSS = 988.10

    FAIXAS_IRRF = [
        (2259.20, 0.0, 0.0),
        (2826.65, 0.075, 169.44),
        (3751.05, 0.15, 381.44),
        (4664.68, 0.225, 662.77),
        (float('inf'), 0.275, 896.00)
    ]
    DEDUCAO_DEPENDENTE = 189.59

    @classmethod
    def calcular_inss(cls, salario_bruto: float) -> float:
        if salario_bruto <= 0:
            return 0.0
        
        if salario_bruto >= cls.TETO_INSS:
            return cls.MAX_DESCONTO_INSS

        for limite, aliquota, deducao in cls.FAIXAS_INSS:
            if salario_bruto <= limite:
                return round((salario_bruto * aliquota) - deducao, 2)
        
        return cls.MAX_DESCONTO_INSS

    @classmethod
    def calcular_irrf(cls, base_calculo: float, dependentes: int = 0) -> float:
        if base_calculo <= 0:
            return 0.0

        base_irrf = base_calculo - (dependentes * cls.DEDUCAO_DEPENDENTE)

        irrf_calculado = 0.0
        for limite, aliquota, deducao in cls.FAIXAS_IRRF:
            if base_irrf <= limite:
                irrf_calculado = (base_irrf * aliquota) - deducao
                break
        
        irrf_calculado = max(0.0, irrf_calculado)

        if base_irrf <= 5000.00:
            return 0.0
        elif base_irrf <= 7350.00:
            redutor = 978.62 - (0.133145 * base_irrf)
            irrf_calculado -= max(0.0, redutor)
            
        return max(0.0, round(irrf_calculado, 2))

    @classmethod
    def processar_holerite_clt(cls, salario_base: float, vencimentos_extras: float, dependentes_irrf: int) -> Dict[str, Any]:
        salario_bruto = salario_base + vencimentos_extras
        
        inss = cls.calcular_inss(salario_bruto)
        base_irrf = salario_bruto - inss
        irrf = cls.calcular_irrf(base_irrf, dependentes_irrf)
        
        salario_liquido = salario_bruto - inss - irrf

        return {
            "vencimentos": {
                "salario_base": round(salario_base, 2),
                "extras": round(vencimentos_extras, 2),
                "total_bruto": round(salario_bruto, 2)
            },
            "descontos": {
                "inss": inss,
                "irrf": irrf,
                "total_descontos": round(inss + irrf, 2)
            },
            "liquido": round(salario_liquido, 2)
        }