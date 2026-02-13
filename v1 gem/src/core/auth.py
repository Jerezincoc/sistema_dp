import hashlib
import os
import binascii
import hmac
from typing import Tuple

SYSTEM_PEPPER = "v1gem_#P3pp3r_S3cr3t_2026!@*ERP_DP"

class SecurityService:

    @staticmethod
    def _hash_password(password: str, salt: bytes) -> str:
        password_peppered = password + SYSTEM_PEPPER
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password_peppered.encode('utf-8'), salt, 100000)
        return binascii.hexlify(pwd_hash).decode('ascii')

    @staticmethod
    def generate_secure_credentials(password_plain: str) -> Tuple[str, str]:
        salt = os.urandom(16)
        pwd_hash = SecurityService._hash_password(password_plain, salt)
        salt_hex = binascii.hexlify(salt).decode('ascii')
        return pwd_hash, salt_hex

    @staticmethod
    def verify_password(stored_hash: str, stored_salt_hex: str, provided_password: str) -> bool:
        try:
            salt = binascii.unhexlify(stored_salt_hex)
            provided_hash = SecurityService._hash_password(provided_password, salt)
            return hmac.compare_digest(provided_hash, stored_hash)
        except (ValueError, TypeError):
            return False