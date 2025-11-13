"""
RBAC Module for OmniScope AI
Provides role and permission management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from backend_db.database import get_db
from backend_db.auth import get_current_active_user
from backend_db.rbac import (
    RBACService,
    Permissions,
    require_permission,
    require_admin
)
from backend_db.models import User, Role
from backend_db.audit import AuditService

router = APIRouter()

# Pydantic models
class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str]

class RoleUpdate(BaseModel):
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

class RoleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    permissions: List[str]

class AssignRoleRequest(BaseModel):
    user_id: str
    role_name: str

class PermissionsResponse(BaseModel):
    permissions: List[str]

@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    current_user: User = Depends(require_permission(Permissions.ROLE_READ)),
    db: Session = Depends(get_db)
):
    """
    List all roles
    """
    roles = db.query(Role).all()
    return [
        RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=role.permissions or []
        )
        for role in roles
    ]

@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str,
    current_user: User = Depends(require_permission(Permissions.ROLE_READ)),
    db: Session = Depends(get_db)
):
    """
    Get a specific role
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=role.permissions or []
    )

@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    request: Request,
    role_data: RoleCreate,
    current_user: User = Depends(require_permission(Permissions.ROLE_CREATE)),
    db: Session = Depends(get_db)
):
    """
    Create a new role
    """
    # Check if role already exists
    existing_role = db.query(Role).filter(Role.name == role_data.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists"
        )
    
    # Create role
    role = Role(
        name=role_data.name,
        description=role_data.description,
        permissions=role_data.permissions
    )
    
    db.add(role)
    db.commit()
    db.refresh(role)
    
    # Log role creation
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="role_create",
        resource="role",
        resource_id=role.id,
        result="success",
        details={"role_name": role.name},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=role.permissions or []
    )

@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    request: Request,
    role_id: str,
    role_data: RoleUpdate,
    current_user: User = Depends(require_permission(Permissions.ROLE_UPDATE)),
    db: Session = Depends(get_db)
):
    """
    Update a role
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Update fields
    if role_data.description is not None:
        role.description = role_data.description
    if role_data.permissions is not None:
        role.permissions = role_data.permissions
    
    db.commit()
    db.refresh(role)
    
    # Log role update
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="role_update",
        resource="role",
        resource_id=role.id,
        result="success",
        details={"role_name": role.name},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=role.permissions or []
    )

@router.delete("/roles/{role_id}")
async def delete_role(
    request: Request,
    role_id: str,
    current_user: User = Depends(require_permission(Permissions.ROLE_DELETE)),
    db: Session = Depends(get_db)
):
    """
    Delete a role
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    role_name = role.name
    db.delete(role)
    db.commit()
    
    # Log role deletion
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="role_delete",
        resource="role",
        resource_id=role_id,
        result="success",
        details={"role_name": role_name},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "Role deleted successfully"}

@router.post("/users/assign-role")
async def assign_role(
    request: Request,
    assign_data: AssignRoleRequest,
    current_user: User = Depends(require_permission(Permissions.ROLE_ASSIGN)),
    db: Session = Depends(get_db)
):
    """
    Assign a role to a user
    """
    user = db.query(User).filter(User.id == assign_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        RBACService.assign_role_to_user(db, user, assign_data.role_name)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Log role assignment
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="role_assign",
        resource="user",
        resource_id=user.id,
        result="success",
        details={"role_name": assign_data.role_name, "target_user": user.email},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": f"Role {assign_data.role_name} assigned to user successfully"}

@router.post("/users/remove-role")
async def remove_role(
    request: Request,
    assign_data: AssignRoleRequest,
    current_user: User = Depends(require_permission(Permissions.ROLE_ASSIGN)),
    db: Session = Depends(get_db)
):
    """
    Remove a role from a user
    """
    user = db.query(User).filter(User.id == assign_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    RBACService.remove_role_from_user(db, user, assign_data.role_name)
    
    # Log role removal
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="role_remove",
        resource="user",
        resource_id=user.id,
        result="success",
        details={"role_name": assign_data.role_name, "target_user": user.email},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": f"Role {assign_data.role_name} removed from user successfully"}

@router.get("/users/{user_id}/permissions", response_model=PermissionsResponse)
async def get_user_permissions(
    user_id: str,
    current_user: User = Depends(require_permission(Permissions.USER_READ)),
    db: Session = Depends(get_db)
):
    """
    Get all permissions for a user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    permissions = RBACService.get_user_permissions(user)
    
    return PermissionsResponse(permissions=permissions)

@router.get("/permissions/available", response_model=PermissionsResponse)
async def get_available_permissions(
    current_user: User = Depends(require_permission(Permissions.ROLE_READ))
):
    """
    Get list of all available permissions
    """
    # Get all permission constants from Permissions class
    permissions = [
        getattr(Permissions, attr)
        for attr in dir(Permissions)
        if not attr.startswith('_') and isinstance(getattr(Permissions, attr), str)
    ]
    
    return PermissionsResponse(permissions=permissions)

@router.get("/me/permissions", response_model=PermissionsResponse)
async def get_my_permissions(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's permissions
    """
    permissions = RBACService.get_user_permissions(current_user)
    
    return PermissionsResponse(permissions=permissions)
