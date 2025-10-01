from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from common.database import Base
from config.settings import settings
import secrets


class EncryptionKey(Base):
    """Encryption key rotation table"""
    __tablename__ = "encryption_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(String, unique=True, index=True, nullable=False)
    key_value = Column(String, nullable=False)  # Encrypted key value
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    rotated_at = Column(DateTime, nullable=True)


class KeyManager:
    """Manage encryption keys and rotation"""

    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def should_rotate(key: EncryptionKey) -> bool:
        """Check if key should be rotated"""
        rotation_date = key.created_at + timedelta(days=settings.KEY_ROTATION_DAYS)
        return datetime.utcnow() >= rotation_date

    @staticmethod
    def get_expiration_date() -> datetime:
        """Get expiration date for new key"""
        return datetime.utcnow() + timedelta(days=settings.KEY_ROTATION_DAYS)

    @staticmethod
    def create_key_id() -> str:
        """Create unique key ID"""
        return f"key-{datetime.utcnow().strftime('%Y%m%d')}-{secrets.token_hex(4)}"


# Key rotation utilities
def rotate_encryption_keys():
    """Rotate encryption keys (should be called by scheduled job)"""
    # Implementation for key rotation
    # This would typically:
    # 1. Generate new key
    # 2. Re-encrypt data with new key
    # 3. Deactivate old key
    # 4. Update key in key management system
    pass
