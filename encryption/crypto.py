from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib
from config.settings import settings
from typing import Union


class EncryptionService:
    """Encryption service for sensitive data"""

    def __init__(self):
        self.key = self._derive_key(settings.ENCRYPTION_KEY)
        self.fernet = Fernet(self.key)

    @staticmethod
    def _derive_key(password: str, salt: bytes = None) -> bytes:
        """Derive encryption key from password"""
        if salt is None:
            salt = b'gaia-abiz-salt-2024'  # In production, use a proper salt management

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt_string(self, plaintext: str) -> str:
        """Encrypt a string using Fernet"""
        if not plaintext:
            return plaintext

        encrypted = self.fernet.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt_string(self, ciphertext: str) -> str:
        """Decrypt a string using Fernet"""
        if not ciphertext:
            return ciphertext

        try:
            decoded = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def encrypt_file(self, file_data: bytes) -> bytes:
        """Encrypt file data using AES-256"""
        key = hashlib.sha256(settings.ENCRYPTION_KEY.encode()).digest()
        iv = get_random_bytes(AES.block_size)

        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(pad(file_data, AES.block_size))

        # Prepend IV to encrypted data
        return iv + encrypted_data

    def decrypt_file(self, encrypted_data: bytes) -> bytes:
        """Decrypt file data using AES-256"""
        key = hashlib.sha256(settings.ENCRYPTION_KEY.encode()).digest()

        # Extract IV from the beginning
        iv = encrypted_data[:AES.block_size]
        ciphertext = encrypted_data[AES.block_size:]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)

        return decrypted_data

    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 (use passlib for production)"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_hash(self, password: str, hashed: str) -> bool:
        """Verify password hash"""
        return self.hash_password(password) == hashed


class FieldEncryption:
    """Field-level encryption for database columns"""

    def __init__(self, encryption_service: EncryptionService):
        self.encryption_service = encryption_service

    def encrypt_field(self, value: Union[str, None]) -> Union[str, None]:
        """Encrypt a database field"""
        if value is None:
            return None
        return self.encryption_service.encrypt_string(value)

    def decrypt_field(self, value: Union[str, None]) -> Union[str, None]:
        """Decrypt a database field"""
        if value is None:
            return None
        return self.encryption_service.decrypt_string(value)


# Singleton instance
encryption_service = EncryptionService()
field_encryption = FieldEncryption(encryption_service)
