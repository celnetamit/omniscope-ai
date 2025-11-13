"""
Multi-Factor Authentication (MFA) service for OmniScope AI
Implements TOTP-based MFA with recovery codes
"""

import pyotp
import qrcode
import io
import base64
import secrets
from typing import List, Tuple
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .models import User, MFARecoveryCode

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class MFAService:
    """Service for MFA operations"""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(user_email: str, secret: str, issuer: str = "OmniScope AI") -> str:
        """
        Generate QR code for TOTP setup
        
        Returns:
            Base64 encoded PNG image
        """
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name=issuer
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    @staticmethod
    def verify_totp(secret: str, token: str) -> bool:
        """
        Verify a TOTP token
        
        Args:
            secret: User's TOTP secret
            token: 6-digit TOTP token
        
        Returns:
            True if token is valid
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # Allow 1 step before/after
    
    @staticmethod
    def generate_recovery_codes(count: int = 10) -> List[str]:
        """
        Generate recovery codes
        
        Args:
            count: Number of recovery codes to generate
        
        Returns:
            List of recovery codes
        """
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = secrets.token_hex(4).upper()
            codes.append(code)
        return codes
    
    @staticmethod
    def hash_recovery_code(code: str) -> str:
        """Hash a recovery code"""
        return pwd_context.hash(code)
    
    @staticmethod
    def verify_recovery_code(code: str, code_hash: str) -> bool:
        """Verify a recovery code against its hash"""
        return pwd_context.verify(code, code_hash)
    
    @staticmethod
    def setup_mfa(db: Session, user: User) -> Tuple[str, str, List[str]]:
        """
        Setup MFA for a user
        
        Returns:
            Tuple of (secret, qr_code_data_uri, recovery_codes)
        """
        # Generate secret
        secret = MFAService.generate_secret()
        
        # Generate QR code
        qr_code = MFAService.generate_qr_code(user.email, secret)
        
        # Generate recovery codes
        recovery_codes = MFAService.generate_recovery_codes()
        
        # Store secret (will be committed when user verifies)
        user.mfa_secret = secret
        
        # Store hashed recovery codes
        for code in recovery_codes:
            code_hash = MFAService.hash_recovery_code(code)
            recovery_code = MFARecoveryCode(
                user_id=user.id,
                code_hash=code_hash
            )
            db.add(recovery_code)
        
        return secret, qr_code, recovery_codes
    
    @staticmethod
    def enable_mfa(db: Session, user: User, token: str) -> bool:
        """
        Enable MFA after verifying the initial token
        
        Args:
            db: Database session
            user: User object
            token: TOTP token to verify
        
        Returns:
            True if MFA was enabled successfully
        """
        if not user.mfa_secret:
            return False
        
        # Verify token
        if not MFAService.verify_totp(user.mfa_secret, token):
            return False
        
        # Enable MFA
        user.mfa_enabled = True
        db.commit()
        
        return True
    
    @staticmethod
    def disable_mfa(db: Session, user: User):
        """Disable MFA for a user"""
        user.mfa_enabled = False
        user.mfa_secret = None
        
        # Delete all recovery codes
        db.query(MFARecoveryCode).filter(
            MFARecoveryCode.user_id == user.id
        ).delete()
        
        db.commit()
    
    @staticmethod
    def verify_mfa(db: Session, user: User, token: str) -> bool:
        """
        Verify MFA token (TOTP or recovery code)
        
        Args:
            db: Database session
            user: User object
            token: TOTP token or recovery code
        
        Returns:
            True if token is valid
        """
        if not user.mfa_enabled or not user.mfa_secret:
            return False
        
        # Try TOTP first
        if MFAService.verify_totp(user.mfa_secret, token):
            return True
        
        # Try recovery codes
        recovery_codes = db.query(MFARecoveryCode).filter(
            MFARecoveryCode.user_id == user.id,
            MFARecoveryCode.is_used == False
        ).all()
        
        for recovery_code in recovery_codes:
            if MFAService.verify_recovery_code(token, recovery_code.code_hash):
                # Mark as used
                recovery_code.is_used = True
                recovery_code.used_at = db.func.now()
                db.commit()
                return True
        
        return False
    
    @staticmethod
    def get_unused_recovery_codes_count(db: Session, user_id: str) -> int:
        """Get count of unused recovery codes"""
        return db.query(MFARecoveryCode).filter(
            MFARecoveryCode.user_id == user_id,
            MFARecoveryCode.is_used == False
        ).count()
    
    @staticmethod
    def regenerate_recovery_codes(db: Session, user: User) -> List[str]:
        """
        Regenerate recovery codes for a user
        
        Returns:
            List of new recovery codes
        """
        # Delete old recovery codes
        db.query(MFARecoveryCode).filter(
            MFARecoveryCode.user_id == user.id
        ).delete()
        
        # Generate new codes
        recovery_codes = MFAService.generate_recovery_codes()
        
        # Store hashed recovery codes
        for code in recovery_codes:
            code_hash = MFAService.hash_recovery_code(code)
            recovery_code = MFARecoveryCode(
                user_id=user.id,
                code_hash=code_hash
            )
            db.add(recovery_code)
        
        db.commit()
        
        return recovery_codes
