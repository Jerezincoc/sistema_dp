from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any
from datetime import datetime

class Role(Enum):
    PADRAO = "PADRAO"               # Acesso restrito (ex: apenas visualização ou digitação básica)
    OPERADOR = "OPERADOR"           # Operação diária (CLT e/ou Extra, dependendo da permissão)
    ADMINISTRADOR = "ADMINISTRADOR" # Acesso total aos módulos operacionais + Configuração de Usuários
    MESTRE = "MESTRE"               # Acesso root (manutenção, auditoria profunda, logs do sistema)

class ModuloAcesso(Enum):
    CLT = "CLT"
    EXTRA = "EXTRA"
    CONFIG = "CONFIG"
    AUDITORIA = "AUDITORIA"

@dataclass
class User:
    id: str
    username: str
    password_hash: str
    salt: str
    role: Role
    modulos_permitidos: List[ModuloAcesso] = field(default_factory=list)
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_login: str | None = None

    def can_access(self, modulo: ModuloAcesso) -> bool:
        """Verifica se o usuário tem permissão para acessar um módulo específico."""
        if not self.is_active:
            return False
            
        if self.role == Role.MESTRE:
            return True  # Mestre tem acesso irrestrito a tudo
            
        if self.role == Role.ADMINISTRADOR and modulo in [ModuloAcesso.CONFIG, ModuloAcesso.CLT, ModuloAcesso.EXTRA]:
            return True  # Admin acessa configurações e módulos operacionais por padrão
            
        return modulo in self.modulos_permitidos

    def is_admin_or_master(self) -> bool:
        """Validação rápida para exibir botões de engrenagem/configuração na UI."""
        return self.role in [Role.ADMINISTRADOR, Role.MESTRE]

    def to_dict(self) -> Dict[str, Any]:
        """Serializa a entidade para salvar no JSON ou futuro Banco de Dados."""
        return {
            "id": self.id,
            "username": self.username,
            "password_hash": self.password_hash,
            "salt": self.salt,
            "role": self.role.value,
            "modulos_permitidos": [m.value for m in self.modulos_permitidos],
            "is_active": self.is_active,
            "created_at": self.created_at,
            "last_login": self.last_login
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Reconstrói a entidade a partir dos dados do JSON/Banco."""
        return cls(
            id=data["id"],
            username=data["username"],
            password_hash=data["password_hash"],
            salt=data["salt"],
            role=Role(data["role"]),
            modulos_permitidos=[ModuloAcesso(m) for m in data.get("modulos_permitidos", [])],
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", datetime.now().isoformat()),
            last_login=data.get("last_login")
        )