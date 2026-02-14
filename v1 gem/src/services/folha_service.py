from typing import Dict, Any, Optional
from datetime import datetime
from src.core.database_manager import JsonDatabaseManager
from src.models.employee_model import Employee, TipoContrato
from src.modules.fopag.calc_folha import CalculadoraFopag
from src.modules.por_fora.calc_folha import CalculadoraPorFora

class FolhaService:
    """
    Orquestrador central do processamento de folha.
    Conecta o banco de dados às calculadoras puras de forma agnóstica.
    """
    def __init__(self):
        self.db = JsonDatabaseManager()

    def processar_holerite_mensal(self, 
                                  employee_id: str, 
                                  mes_ano: str, 
                                  vencimentos_extras_clt: float = 0.0,
                                  comissoes_extra: float = 0.0,
                                  bonus_extra: float = 0.0,
                                  adiantamentos_extra: float = 0.0,
                                  descontos_extra: float = 0.0) -> Optional[Dict[str, Any]]:
        """
        Gera o holerite de um funcionário para o mês específico, 
        respeitando rigorosamente seu tipo de contrato.
        """
        emp_data = self.db.get_record("funcionarios", employee_id)
        if not emp_data:
            return None

        emp = Employee.from_dict(emp_data)
        if not emp.is_active:
            return None

        resultado = {
            "employee_id": emp.id,
            "nome": emp.nome,
            "competencia": mes_ano,
            "data_processamento": datetime.now().isoformat(),
            "tipo_contrato": emp.tipo_contrato.value,
            "clt": None,
            "extra": None
        }

        # 1. Processamento CLT (Apenas para modos CLT ou HIBRIDO)
        if emp.tipo_contrato in (TipoContrato.CLT, TipoContrato.HIBRIDO):
            resultado["clt"] = CalculadoraFopag.processar_holerite_clt(
                salario_base=emp.salario_base_clt,
                vencimentos_extras=vencimentos_extras_clt,
                dependentes_irrf=emp.dependentes_irrf
            )

        # 2. Processamento EXTRA (Apenas para modos EXTRA ou HIBRIDO)
        if emp.tipo_contrato in (TipoContrato.EXTRA, TipoContrato.HIBRIDO):
            resultado["extra"] = CalculadoraPorFora.processar_pagamento_extra(
                salario_base_extra=emp.salario_base_extra,
                comissoes=comissoes_extra,
                bonus=bonus_extra,
                adiantamentos=adiantamentos_extra,
                descontos_diversos=descontos_extra
            )

        # 3. Persistência do Histórico
        id_holerite = f"{emp.id}_{mes_ano}"
        self.db.save_record("historico_holerites", id_holerite, resultado)

        return resultado