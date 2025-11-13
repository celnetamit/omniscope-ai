"""
Role-Based Access Control (RBAC) system for OmniScope AI
Implements permission checking and role hierarchy
"""

from typing import List, Optional, Callable
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from functools import wraps
from .database import get_db
from .models import User, Role
from .auth import get_current_active_user

# Permission definitions
class Permissions:
    """Permission constants"""
    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_LIST = "user:list"
    
    # Role management
    ROLE_CREATE = "role:create"
    ROLE_READ = "role:read"
    ROLE_UPDATE = "role:update"
    ROLE_DELETE = "role:delete"
    ROLE_ASSIGN = "role:assign"
    
    # Data management
    DATA_UPLOAD = "data:upload"
    DATA_READ = "data:read"
    DATA_UPDATE = "data:update"
    DATA_DELETE = "data:delete"
    DATA_EXPORT = "data:export"
    
    # Pipeline management
    PIPELINE_CREATE = "pipeline:create"
    PIPELINE_READ = "pipeline:read"
    PIPELINE_UPDATE = "pipeline:update"
    PIPELINE_DELETE = "pipeline:delete"
    PIPELINE_EXECUTE = "pipeline:execute"
    
    # Model management
    MODEL_TRAIN = "model:train"
    MODEL_READ = "model:read"
    MODEL_UPDATE = "model:update"
    MODEL_DELETE = "model:delete"
    MODEL_DEPLOY = "model:deploy"
    
    # Results and analysis
    RESULTS_READ = "results:read"
    RESULTS_EXPORT = "results:export"
    RESULTS_SHARE = "results:share"
    
    # Workspace management
    WORKSPACE_CREATE = "workspace:create"
    WORKSPACE_READ = "workspace:read"
    WORKSPACE_UPDATE = "workspace:update"
    WORKSPACE_DELETE = "workspace:delete"
    WORKSPACE_INVITE = "workspace:invite"
    
    # Plugin management
    PLUGIN_INSTALL = "plugin:install"
    PLUGIN_EXECUTE = "plugin:execute"
    PLUGIN_MANAGE = "plugin:manage"
    
    # Audit and compliance
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"
    COMPLIANCE_MANAGE = "compliance:manage"
    
    # System administration
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_CONFIG = "system:config"

# Role definitions with permissions
ROLE_PERMISSIONS = {
    "Admin": [
        # Full access to everything
        Permissions.USER_CREATE, Permissions.USER_READ, Permissions.USER_UPDATE,
        Permissions.USER_DELETE, Permissions.USER_LIST,
        Permissions.ROLE_CREATE, Permissions.ROLE_READ, Permissions.ROLE_UPDATE,
        Permissions.ROLE_DELETE, Permissions.ROLE_ASSIGN,
        Permissions.DATA_UPLOAD, Permissions.DATA_READ, Permissions.DATA_UPDATE,
        Permissions.DATA_DELETE, Permissions.DATA_EXPORT,
        Permissions.PIPELINE_CREATE, Permissions.PIPELINE_READ, Permissions.PIPELINE_UPDATE,
        Permissions.PIPELINE_DELETE, Permissions.PIPELINE_EXECUTE,
        Permissions.MODEL_TRAIN, Permissions.MODEL_READ, Permissions.MODEL_UPDATE,
        Permissions.MODEL_DELETE, Permissions.MODEL_DEPLOY,
        Permissions.RESULTS_READ, Permissions.RESULTS_EXPORT, Permissions.RESULTS_SHARE,
        Permissions.WORKSPACE_CREATE, Permissions.WORKSPACE_READ, Permissions.WORKSPACE_UPDATE,
        Permissions.WORKSPACE_DELETE, Permissions.WORKSPACE_INVITE,
        Permissions.PLUGIN_INSTALL, Permissions.PLUGIN_EXECUTE, Permissions.PLUGIN_MANAGE,
        Permissions.AUDIT_READ, Permissions.AUDIT_EXPORT, Permissions.COMPLIANCE_MANAGE,
        Permissions.SYSTEM_ADMIN, Permissions.SYSTEM_CONFIG
    ],
    "PI": [
        # Principal Investigator - can manage projects and team
        Permissions.USER_READ, Permissions.USER_LIST,
        Permissions.DATA_UPLOAD, Permissions.DATA_READ, Permissions.DATA_UPDATE,
        Permissions.DATA_DELETE, Permissions.DATA_EXPORT,
        Permissions.PIPELINE_CREATE, Permissions.PIPELINE_READ, Permissions.PIPELINE_UPDATE,
        Permissions.PIPELINE_DELETE, Permissions.PIPELINE_EXECUTE,
        Permissions.MODEL_TRAIN, Permissions.MODEL_READ, Permissions.MODEL_UPDATE,
        Permissions.MODEL_DELETE, Permissions.MODEL_DEPLOY,
        Permissions.RESULTS_READ, Permissions.RESULTS_EXPORT, Permissions.RESULTS_SHARE,
        Permissions.WORKSPACE_CREATE, Permissions.WORKSPACE_READ, Permissions.WORKSPACE_UPDATE,
        Permissions.WORKSPACE_DELETE, Permissions.WORKSPACE_INVITE,
        Permissions.PLUGIN_EXECUTE, Permissions.PLUGIN_MANAGE,
        Permissions.AUDIT_READ
    ],
    "Researcher": [
        # Can perform analysis and create pipelines
        Permissions.DATA_UPLOAD, Permissions.DATA_READ, Permissions.DATA_EXPORT,
        Permissions.PIPELINE_CREATE, Permissions.PIPELINE_READ, Permissions.PIPELINE_UPDATE,
        Permissions.PIPELINE_EXECUTE,
        Permissions.MODEL_TRAIN, Permissions.MODEL_READ,
        Permissions.RESULTS_READ, Permissions.RESULTS_EXPORT,
        Permissions.WORKSPACE_READ, Permissions.WORKSPACE_UPDATE,
        Permissions.PLUGIN_EXECUTE
    ],
    "Analyst": [
        # Can view and analyze data
        Permissions.DATA_READ, Permissions.DATA_EXPORT,
        Permissions.PIPELINE_READ, Permissions.PIPELINE_EXECUTE,
        Permissions.MODEL_READ,
        Permissions.RESULTS_READ, Permissions.RESULTS_EXPORT,
        Permissions.WORKSPACE_READ,
        Permissions.PLUGIN_EXECUTE
    ],
    "Viewer": [
        # Read-only access
        Permissions.DATA_READ,
        Permissions.PIPELINE_READ,
        Permissions.MODEL_READ,
        Permissions.RESULTS_READ,
        Permissions.WORKSPACE_READ
    ]
}

class RBACService:
    """Service for RBAC operations"""
    
    @staticmethod
    def create_default_roles(db: Session):
        """Create default roles if they don't exist"""
        for role_name, permissions in ROLE_PERMISSIONS.items():
            existing_role = db.query(Role).filter(Role.name == role_name).first()
            if not existing_role:
                role = Role(
                    name=role_name,
                    description=f"Default {role_name} role",
                    permissions=permissions
                )
                db.add(role)
        db.commit()
    
    @staticmethod
    def get_role_by_name(db: Session, role_name: str) -> Optional[Role]:
        """Get role by name"""
        return db.query(Role).filter(Role.name == role_name).first()
    
    @staticmethod
    def assign_role_to_user(db: Session, user: User, role_name: str):
        """Assign a role to a user"""
        role = RBACService.get_role_by_name(db, role_name)
        if not role:
            raise ValueError(f"Role {role_name} not found")
        
        if role not in user.roles:
            user.roles.append(role)
            db.commit()
    
    @staticmethod
    def remove_role_from_user(db: Session, user: User, role_name: str):
        """Remove a role from a user"""
        role = RBACService.get_role_by_name(db, role_name)
        if role and role in user.roles:
            user.roles.remove(role)
            db.commit()
    
    @staticmethod
    def get_user_permissions(user: User) -> List[str]:
        """Get all permissions for a user"""
        permissions = set()
        for role in user.roles:
            if role.permissions:
                permissions.update(role.permissions)
        return list(permissions)
    
    @staticmethod
    def has_permission(user: User, permission: str) -> bool:
        """Check if user has a specific permission"""
        user_permissions = RBACService.get_user_permissions(user)
        
        # Admin has all permissions
        if Permissions.SYSTEM_ADMIN in user_permissions:
            return True
        
        return permission in user_permissions
    
    @staticmethod
    def has_any_permission(user: User, permissions: List[str]) -> bool:
        """Check if user has any of the specified permissions"""
        user_permissions = RBACService.get_user_permissions(user)
        
        # Admin has all permissions
        if Permissions.SYSTEM_ADMIN in user_permissions:
            return True
        
        return any(perm in user_permissions for perm in permissions)
    
    @staticmethod
    def has_all_permissions(user: User, permissions: List[str]) -> bool:
        """Check if user has all of the specified permissions"""
        user_permissions = RBACService.get_user_permissions(user)
        
        # Admin has all permissions
        if Permissions.SYSTEM_ADMIN in user_permissions:
            return True
        
        return all(perm in user_permissions for perm in permissions)
    
    @staticmethod
    def has_role(user: User, role_name: str) -> bool:
        """Check if user has a specific role"""
        return any(role.name == role_name for role in user.roles)

# Permission dependency functions
def require_permission(permission: str):
    """
    Dependency to require a specific permission
    Usage: @router.get("/endpoint", dependencies=[Depends(require_permission(Permissions.DATA_READ))])
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ):
        if not RBACService.has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required permission: {permission}"
            )
        return current_user
    
    return permission_checker

def require_any_permission(permissions: List[str]):
    """
    Dependency to require any of the specified permissions
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ):
        if not RBACService.has_any_permission(current_user, permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required any of: {', '.join(permissions)}"
            )
        return current_user
    
    return permission_checker

def require_all_permissions(permissions: List[str]):
    """
    Dependency to require all of the specified permissions
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ):
        if not RBACService.has_all_permissions(current_user, permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required all of: {', '.join(permissions)}"
            )
        return current_user
    
    return permission_checker

def require_role(role_name: str):
    """
    Dependency to require a specific role
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ):
        if not RBACService.has_role(current_user, role_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required role: {role_name}"
            )
        return current_user
    
    return role_checker

# Convenience dependencies for common roles
require_admin = require_role("Admin")
require_pi = require_any_permission([Permissions.SYSTEM_ADMIN, Permissions.WORKSPACE_DELETE])
require_researcher = require_any_permission([
    Permissions.SYSTEM_ADMIN,
    Permissions.PIPELINE_CREATE,
    Permissions.MODEL_TRAIN
])
