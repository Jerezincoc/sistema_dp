from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime

class TipoContrato(Enum):
    CLT = "CLT"             # Apenas Folha Legal
    EXTRA = "EXTRA"         # Apenas Por Fora
    HIBRIDO = "HIBRIDO"     # Recebe parte na carteira e parte por fora

@dataclass
class Employee:
    id: str
    nome: str
    cpf: str
    cargo: str
    tipo_contrato: TipoContrato
    
    # --- Dados Financeiros ---
    salario_base_clt: float = 0.0
    salario_base_extra: float = 0.0
    
    # --- Variáveis Críticas de Cálculo (FOPAG) ---
    dependentes_irrf: int = 0
    dependentes_salario_familia: int = 0
    data_admissao: Optional[str] = None
    
    # --- Metadados e Auditoria ---
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Prepara o objeto para ser salvo no JSON ou futuro SQL."""
        return {
            "id": self.id,
            "nome": self.nome,
            "cpf": self.cpf,
            "cargo": self.cargo,
            "tipo_contrato": self.tipo_contrato.value,
            "salario_base_clt": self.salario_base_clt,
            "salario_base_extra": self.salario_base_extra,
            "dependentes_irrf": self.dependentes_irrf,
            "dependentes_salario_familia": self.dependentes_salario_familia,
            "data_admissao": self.data_admissao,
            "is_active": self.is_active,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Employee":
        """Reconstrói o objeto a partir do banco de dados."""
        return cls(
            id=data["id"],
            nome=data["nome"],
            cpf=data["cpf"],
            cargo=data["cargo"],
            tipo_contrato=TipoContrato(data["tipo_contrato"]),
            salario_base_clt=float(data.get("salario_base_clt", 0.0)),
            salario_base_extra=float(data.get("salario_base_extra", 0.0)),
            dependentes_irrf=int(data.get("dependentes_irrf", 0)),
            dependentes_salario_familia=int(data.get("dependentes_salario_familia", 0)),
            data_admissao=data.get("data_admissao"),
            is_active=bool(data.get("is_active", True)),
            created_at=data.get("created_at", datetime.now().isoformat())
        )