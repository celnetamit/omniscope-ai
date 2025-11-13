"""
Authentication Module for OmniScope AI
Provides OAuth2/OIDC authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta

from backend_db.database import get_db
from backend_db.auth import (
    AuthService,
    get_current_user,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from backend_db.models import User
from backend_db.audit import AuditService
from backend_db.mfa import MFAService

router = APIRouter()

# Pydantic models for request/response
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    is_active: bool
    mfa_enabled: bool
    roles: list

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class MFASetupResponse(BaseModel):
    secret: str
    qr_code: str
    recovery_codes: list

class MFAVerifyRequest(BaseModel):
    token: str

class MFALoginRequest(BaseModel):
    token: str
    temp_token: str

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        await AuditService.log_action(
            db=db,
            action="register_failed",
            resource="user",
            result="failure",
            details={"reason": "email_already_exists", "email": user_data.email},
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = AuthService.get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log successful registration
    await AuditService.log_action(
        db=db,
        user_id=new_user.id,
        action="register",
        resource="user",
        resource_id=new_user.id,
        result="success",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        is_active=new_user.is_active,
        mfa_enabled=new_user.mfa_enabled,
        roles=[role.name for role in new_user.roles]
    )

@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password to get access and refresh tokens
    """
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        await AuditService.log_action(
            db=db,
            action="login_failed",
            resource="user",
            result="failure",
            details={"reason": "invalid_credentials", "email": form_data.username},
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if MFA is enabled
    if user.mfa_enabled:
        # Return a temporary token that requires MFA verification
        access_token = AuthService.create_access_token(
            data={"sub": user.id, "mfa_required": True},
            expires_delta=timedelta(minutes=5)
        )
        
        await AuditService.log_action(
            db=db,
            user_id=user.id,
            action="login_mfa_required",
            resource="user",
            resource_id=user.id,
            result="success",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token="",
            token_type="bearer",
            expires_in=300  # 5 minutes
        )
    
    # Create tokens
    access_token = AuthService.create_access_token(
        data={"sub": user.id, "email": user.email}
    )
    refresh_token = AuthService.create_refresh_token(user.id, db)
    
    # Log successful login
    await AuditService.log_action(
        db=db,
        user_id=user.id,
        action="login",
        resource="user",
        resource_id=user.id,
        result="success",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    refresh_token = AuthService.verify_refresh_token(db, refresh_data.refresh_token)
    
    if not refresh_token:
        await AuditService.log_action(
            db=db,
            action="token_refresh_failed",
            resource="token",
            result="failure",
            details={"reason": "invalid_refresh_token"},
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user = AuthService.get_user_by_id(db, refresh_token.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token = AuthService.create_access_token(
        data={"sub": user.id, "email": user.email}
    )
    
    # Log token refresh
    await AuditService.log_action(
        db=db,
        user_id=user.id,
        action="token_refresh",
        resource="token",
        result="success",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_data.refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/logout")
async def logout(
    request: Request,
    refresh_token: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Logout user and revoke refresh token
    """
    if refresh_token:
        AuthService.revoke_refresh_token(db, refresh_token)
    
    # Log logout
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="logout",
        resource="user",
        resource_id=current_user.id,
        result="success",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "Successfully logged out"}

@router.post("/logout-all")
async def logout_all(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Logout from all devices by revoking all refresh tokens
    """
    AuthService.revoke_all_user_tokens(db, current_user.id)
    
    # Log logout from all devices
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="logout_all",
        resource="user",
        resource_id=current_user.id,
        result="success",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "Successfully logged out from all devices"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        is_active=current_user.is_active,
        mfa_enabled=current_user.mfa_enabled,
        roles=[role.name for role in current_user.roles]
    )

@router.post("/change-password")
async def change_password(
    request: Request,
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    # Verify old password
    if not AuthService.verify_password(password_data.old_password, current_user.password_hash):
        await AuditService.log_action(
            db=db,
            user_id=current_user.id,
            action="change_password_failed",
            resource="user",
            resource_id=current_user.id,
            result="failure",
            details={"reason": "invalid_old_password"},
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    # Update password
    current_user.password_hash = AuthService.get_password_hash(password_data.new_password)
    db.commit()
    
    # Revoke all existing tokens
    AuthService.revoke_all_user_tokens(db, current_user.id)
    
    # Log password change
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="change_password",
        resource="user",
        resource_id=current_user.id,
        result="success",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "Password changed successfully. Please login again."}


# MFA Endpoints

@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Setup MFA for the current user
    Returns secret, QR code, and recovery codes
    """
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled"
        )
    
    secret, qr_code, recovery_codes = MFAService.setup_mfa(db, current_user)
    
    # Don't commit yet - user needs to verify first
    db.commit()
    
    # Log MFA setup initiation
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="mfa_setup_initiated",
        resource="user",
        resource_id=current_user.id,
        result="success",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return MFASetupResponse(
        secret=secret,
        qr_code=qr_code,
        recovery_codes=recovery_codes
    )

@router.post("/mfa/enable")
async def enable_mfa(
    request: Request,
    verify_data: MFAVerifyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Enable MFA after verifying the initial token
    """
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled"
        )
    
    success = MFAService.enable_mfa(db, current_user, verify_data.token)
    
    if not success:
        await AuditService.log_action(
            db=db,
            user_id=current_user.id,
            action="mfa_enable_failed",
            resource="user",
            resource_id=current_user.id,
            result="failure",
            details={"reason": "invalid_token"},
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    # Log MFA enabled
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="mfa_enabled",
        resource="user",
        resource_id=current_user.id,
        result="success",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "MFA enabled successfully"}

@router.post("/mfa/disable")
async def disable_mfa(
    request: Request,
    verify_data: MFAVerifyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Disable MFA for the current user
    """
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    # Verify token before disabling
    if not MFAService.verify_mfa(db, current_user, verify_data.token):
        await AuditService.log_action(
            db=db,
            user_id=current_user.id,
            action="mfa_disable_failed",
            resource="user",
            resource_id=current_user.id,
            result="failure",
            details={"reason": "invalid_token"},
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    MFAService.disable_mfa(db, current_user)
    
    # Log MFA disabled
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="mfa_disabled",
        resource="user",
        resource_id=current_user.id,
        result="success",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "MFA disabled successfully"}

@router.post("/mfa/verify", response_model=TokenResponse)
async def verify_mfa_login(
    request: Request,
    mfa_data: MFALoginRequest,
    db: Session = Depends(get_db)
):
    """
    Complete MFA login by verifying the TOTP token
    """
    # Verify the temporary token
    try:
        payload = AuthService.verify_token(mfa_data.temp_token)
        user_id = payload.get("sub")
        mfa_required = payload.get("mfa_required")
        
        if not mfa_required:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA not required for this token"
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid temporary token"
        )
    
    user = AuthService.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Verify MFA token
    if not MFAService.verify_mfa(db, user, mfa_data.token):
        await AuditService.log_action(
            db=db,
            user_id=user.id,
            action="mfa_verify_failed",
            resource="user",
            resource_id=user.id,
            result="failure",
            details={"reason": "invalid_mfa_token"},
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA token"
        )
    
    # Create full access tokens
    access_token = AuthService.create_access_token(
        data={"sub": user.id, "email": user.email}
    )
    refresh_token = AuthService.create_refresh_token(user.id, db)
    
    # Log successful MFA verification
    await AuditService.log_action(
        db=db,
        user_id=user.id,
        action="mfa_verify_success",
        resource="user",
        resource_id=user.id,
        result="success",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.get("/mfa/recovery-codes/count")
async def get_recovery_codes_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get count of unused recovery codes
    """
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    count = MFAService.get_unused_recovery_codes_count(db, current_user.id)
    
    return {"unused_codes": count}

@router.post("/mfa/recovery-codes/regenerate")
async def regenerate_recovery_codes(
    request: Request,
    verify_data: MFAVerifyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate recovery codes
    """
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    # Verify token before regenerating
    if not MFAService.verify_mfa(db, current_user, verify_data.token):
        await AuditService.log_action(
            db=db,
            user_id=current_user.id,
            action="recovery_codes_regenerate_failed",
            resource="user",
            resource_id=current_user.id,
            result="failure",
            details={"reason": "invalid_token"},
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    recovery_codes = MFAService.regenerate_recovery_codes(db, current_user)
    
    # Log recovery codes regeneration
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="recovery_codes_regenerated",
        resource="user",
        resource_id=current_user.id,
        result="success",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"recovery_codes": recovery_codes}
