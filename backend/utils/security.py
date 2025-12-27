"""Security utilities for handling sensitive data in Fynace application."""
import os
import secrets
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SecurityUtils:
    """Security utilities for sensitive data handling."""
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_data(data: str, salt: Optional[bytes] = None) -> tuple[str, str]:
        """Hash sensitive data with salt."""
        if salt is None:
            salt = os.urandom(32)  # 32 bytes salt
        
        # Create hash using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(data.encode()))
        
        return key.decode(), base64.b64encode(salt).decode()
    
    @staticmethod
    def verify_hash(data: str, stored_hash: str, salt: str) -> bool:
        """Verify if data matches the stored hash."""
        try:
            salt_bytes = base64.b64decode(salt.encode())
            expected_hash, _ = SecurityUtils.hash_data(data, salt_bytes)
            return expected_hash == stored_hash
        except Exception:
            return False
    
    @staticmethod
    def encrypt_data(data: str, key: Optional[bytes] = None) -> tuple[str, str]:
        """Encrypt sensitive data using Fernet encryption."""
        if key is None:
            key = Fernet.generate_key()
        
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        
        return encrypted_data.decode(), key.decode()
    
    @staticmethod
    def decrypt_data(encrypted_data: str, key: str) -> str:
        """Decrypt sensitive data."""
        f = Fernet(key.encode())
        decrypted_data = f.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Sanitize user input to prevent injection attacks."""
        # Remove potentially dangerous characters
        sanitized = input_str.replace('<', '&lt;').replace('>', '&gt;')
        sanitized = sanitized.replace('"', '&quot;').replace("'", '&#x27;')
        sanitized = sanitized.replace('/', '&#x2F;').replace('\\', '&#x5C;')
        return sanitized
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def mask_sensitive_data(data: str, visible_chars: int = 2) -> str:
        """Mask sensitive data like tokens or passwords."""
        if len(data) <= visible_chars * 2:
            return '*' * len(data)
        return data[:visible_chars] + '*' * (len(data) - visible_chars * 2) + data[-visible_chars:]

class SecurityMiddleware:
    """Security middleware for FastAPI."""
    
    @staticmethod
    def add_security_headers(response):
        """Add security headers to response."""
        # Prevent XSS attacks
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Enable HSTS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
        
        return response

class DataValidator:
    """Validate and sanitize data."""
    
    @staticmethod
    def validate_transaction_data(data: dict) -> tuple[bool, str]:
        """Validate transaction data."""
        required_fields = ["descricao", "valor", "tipo", "categoria"]
        
        for field in required_fields:
            if field not in data:
                return False, f"Campo obrigatório '{field}' ausente"
        
        # Validate valor is a positive number
        valor = data.get("valor")
        if not isinstance(valor, (int, float)) or valor <= 0:
            return False, "Valor deve ser um número positivo"
        
        # Validate tipo is either 'despesa' or 'ganho'
        tipo = data.get("tipo")
        if tipo not in ["despesa", "ganho"]:
            return False, "Tipo deve ser 'despesa' ou 'ganho'"
        
        # Validate descricao is not empty and sanitized
        descricao = data.get("descricao")
        if not descricao or not descricao.strip():
            return False, "Descrição não pode ser vazia"
        
        # Sanitize description
        sanitized_desc = SecurityUtils.sanitize_input(descricao)
        if sanitized_desc != descricao:
            return False, "Descrição contém caracteres inválidos"
        
        return True, "Validação bem-sucedida"
    
    @staticmethod
    def validate_user_data(data: dict) -> tuple[bool, str]:
        """Validate user data."""
        email = data.get("email")
        if not email or not SecurityUtils.validate_email(email):
            return False, "Email inválido"
        
        return True, "Validação bem-sucedida"