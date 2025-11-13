"""
Data Encryption Service for OmniScope AI
Implements AES-256 encryption for sensitive data
"""

import os
import base64
from typing import Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from sqlalchemy.orm import Session
from .models import EncryptedData

class EncryptionService:
    """Service for data encryption and decryption"""
    
    def __init__(self):
        # Get encryption key from environment or generate one
        self.master_key = os.getenv("ENCRYPTION_MASTER_KEY")
        if not self.master_key:
            # Generate a key if not provided (for development only)
            self.master_key = Fernet.generate_key().decode()
            print("⚠️  WARNING: Using generated encryption key. Set ENCRYPTION_MASTER_KEY in production!")
        
        # Ensure key is bytes
        if isinstance(self.master_key, str):
            self.master_key = self.master_key.encode()
    
    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derive an encryption key from the master key using PBKDF2
        
        Args:
            salt: Salt for key derivation
        
        Returns:
            Derived encryption key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(self.master_key))
    
    def encrypt(self, data: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
        """
        Encrypt data using AES-256
        
        Args:
            data: Plain text data to encrypt
            salt: Optional salt for key derivation (generated if not provided)
        
        Returns:
            Tuple of (encrypted_data, salt) both base64 encoded
        """
        if salt is None:
            salt = os.urandom(16)
        
        # Derive encryption key
        key = self._derive_key(salt)
        
        # Create Fernet cipher
        cipher = Fernet(key)
        
        # Encrypt data
        encrypted_data = cipher.encrypt(data.encode())
        
        # Return base64 encoded encrypted data and salt
        return (
            base64.b64encode(encrypted_data).decode(),
            base64.b64encode(salt).decode()
        )
    
    def decrypt(self, encrypted_data: str, salt: str) -> str:
        """
        Decrypt data using AES-256
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            salt: Base64 encoded salt used for encryption
        
        Returns:
            Decrypted plain text data
        """
        # Decode from base64
        encrypted_bytes = base64.b64decode(encrypted_data)
        salt_bytes = base64.b64decode(salt)
        
        # Derive encryption key
        key = self._derive_key(salt_bytes)
        
        # Create Fernet cipher
        cipher = Fernet(key)
        
        # Decrypt data
        decrypted_data = cipher.decrypt(encrypted_bytes)
        
        return decrypted_data.decode()
    
    def encrypt_field(self, data: str) -> str:
        """
        Encrypt a field and return in format: salt:encrypted_data
        
        Args:
            data: Plain text data to encrypt
        
        Returns:
            Encrypted data in format "salt:encrypted_data"
        """
        encrypted_data, salt = self.encrypt(data)
        return f"{salt}:{encrypted_data}"
    
    def decrypt_field(self, encrypted_field: str) -> str:
        """
        Decrypt a field in format: salt:encrypted_data
        
        Args:
            encrypted_field: Encrypted data in format "salt:encrypted_data"
        
        Returns:
            Decrypted plain text data
        """
        try:
            salt, encrypted_data = encrypted_field.split(':', 1)
            return self.decrypt(encrypted_data, salt)
        except Exception as e:
            raise ValueError(f"Invalid encrypted field format: {e}")
    
    def store_encrypted_data(
        self,
        db: Session,
        data_type: str,
        plain_data: str,
        key_id: Optional[str] = None
    ) -> EncryptedData:
        """
        Encrypt and store data in database
        
        Args:
            db: Database session
            data_type: Type of data being encrypted
            plain_data: Plain text data to encrypt
            key_id: Optional key management system reference
        
        Returns:
            EncryptedData model instance
        """
        encrypted_field = self.encrypt_field(plain_data)
        
        encrypted_data = EncryptedData(
            data_type=data_type,
            encrypted_value=encrypted_field,
            encryption_key_id=key_id
        )
        
        db.add(encrypted_data)
        db.commit()
        db.refresh(encrypted_data)
        
        return encrypted_data
    
    def retrieve_encrypted_data(
        self,
        db: Session,
        data_id: str
    ) -> Optional[str]:
        """
        Retrieve and decrypt data from database
        
        Args:
            db: Database session
            data_id: ID of encrypted data record
        
        Returns:
            Decrypted plain text data or None if not found
        """
        encrypted_data = db.query(EncryptedData).filter(
            EncryptedData.id == data_id
        ).first()
        
        if not encrypted_data:
            return None
        
        return self.decrypt_field(encrypted_data.encrypted_value)
    
    def hash_data(self, data: str) -> str:
        """
        Create a one-way hash of data (for anonymization)
        
        Args:
            data: Data to hash
        
        Returns:
            Base64 encoded hash
        """
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(data.encode())
        hash_bytes = digest.finalize()
        return base64.b64encode(hash_bytes).decode()

# Global encryption service instance
encryption_service = EncryptionService()

# Helper functions for easy access
def encrypt_data(data: str) -> str:
    """Encrypt data and return in format: salt:encrypted_data"""
    return encryption_service.encrypt_field(data)

def decrypt_data(encrypted_field: str) -> str:
    """Decrypt data from format: salt:encrypted_data"""
    return encryption_service.decrypt_field(encrypted_field)

def hash_data(data: str) -> str:
    """Create a one-way hash of data"""
    return encryption_service.hash_data(data)
