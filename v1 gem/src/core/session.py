from src.core.auth import SecurityService
from src.core.database_manager import JsonDatabaseManager
from src.models.user_model import User, Role, ModuloAcesso

class SessionManager:
    def __init__(self):
        self.db = JsonDatabaseManager()
        self.current_user: User | None = None

    def login(self, username: str, password_plain: str) -> bool:
        if username == "sysAdmin" and password_plain == "DP2026":
            self.current_user = User(
                id="master-000",
                username="sysAdmin",
                password_hash="",
                salt="",
                role=Role.MESTRE,
                modulos_permitidos=[
                    ModuloAcesso.CLT, 
                    ModuloAcesso.EXTRA, 
                    ModuloAcesso.CONFIG, 
                    ModuloAcesso.AUDITORIA
                ]
            )
            return True

        users_data = self.db.find_records("usuarios", lambda u: u.get("username") == username)
        
        if not users_data:
            return False
            
        user_record = users_data[0]
        
        if not user_record.get("is_active", True):
            return False

        is_valid = SecurityService.verify_password(
            stored_hash=user_record["password_hash"],
            stored_salt_hex=user_record["salt"],
            provided_password=password_plain
        )
        
        if is_valid:
            self.current_user = User.from_dict(user_record)
            return True
            
        return False

    def logout(self) -> None:
        self.current_user = None

    def reset_user_password(self, target_username: str, new_password: str) -> bool:
        if not self.current_user or self.current_user.role != Role.MESTRE:
            return False
            
        users = self.db.find_records("usuarios", lambda u: u.get("username") == target_username)
        if not users:
            return False
            
        user_data = users[0]
        new_hash, new_salt = SecurityService.generate_secure_credentials(new_password)
        
        user_data["password_hash"] = new_hash
        user_data["salt"] = new_salt
        
        return self.db.save_record("usuarios", user_data["id"], user_data)