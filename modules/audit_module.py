"""
Audit Module for OmniScope AI
Provides audit log viewing and compliance reporting endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from backend_db.database import get_db
from backend_db.auth import get_current_active_user
from backend_db.rbac import Permissions, require_permission
from backend_db.models import User, AuditLog
from backend_db.audit import AuditService

router = APIRouter()

# Pydantic models
class AuditLogResponse(BaseModel):
    id: str
    timestamp: datetime
    user_id: Optional[str]
    user_email: Optional[str]
    action: str
    resource: str
    resource_id: Optional[str]
    ip_address: Optional[str]
    result: str
    details: Optional[dict]

class AuditLogListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total: int
    limit: int
    offset: int

class ComplianceReportResponse(BaseModel):
    report_type: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    total_actions: int
    failed_actions: int
    unique_users: int
    summary: dict

@router.get("/logs", response_model=AuditLogListResponse)
async def get_audit_logs(
    action: Optional[str] = Query(None, description="Filter by action"),
    resource: Optional[str] = Query(None, description="Filter by resource"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    result: Optional[str] = Query(None, description="Filter by result (success/failure/error)"),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(require_permission(Permissions.AUDIT_READ)),
    db: Session = Depends(get_db)
):
    """
    Get audit logs with optional filters
    """
    logs = AuditService.search_audit_logs(
        db=db,
        action=action,
        resource=resource,
        user_id=user_id,
        result=result,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    
    # Get total count
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource:
        query = query.filter(AuditLog.resource == resource)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if result:
        query = query.filter(AuditLog.result == result)
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    total = query.count()
    
    # Convert to response format
    log_responses = []
    for log in logs:
        user_email = None
        if log.user_id:
            user = db.query(User).filter(User.id == log.user_id).first()
            if user:
                user_email = user.email
        
        log_responses.append(AuditLogResponse(
            id=log.id,
            timestamp=log.timestamp,
            user_id=log.user_id,
            user_email=user_email,
            action=log.action,
            resource=log.resource,
            resource_id=log.resource_id,
            ip_address=log.ip_address,
            result=log.result,
            details=log.details
        ))
    
    return AuditLogListResponse(
        logs=log_responses,
        total=total,
        limit=limit,
        offset=offset
    )

@router.get("/logs/user/{user_id}", response_model=AuditLogListResponse)
async def get_user_audit_logs(
    user_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_permission(Permissions.AUDIT_READ)),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for a specific user
    """
    logs = AuditService.get_user_audit_logs(db, user_id, limit, offset)
    total = db.query(AuditLog).filter(AuditLog.user_id == user_id).count()
    
    # Convert to response format
    log_responses = []
    user = db.query(User).filter(User.id == user_id).first()
    user_email = user.email if user else None
    
    for log in logs:
        log_responses.append(AuditLogResponse(
            id=log.id,
            timestamp=log.timestamp,
            user_id=log.user_id,
            user_email=user_email,
            action=log.action,
            resource=log.resource,
            resource_id=log.resource_id,
            ip_address=log.ip_address,
            result=log.result,
            details=log.details
        ))
    
    return AuditLogListResponse(
        logs=log_responses,
        total=total,
        limit=limit,
        offset=offset
    )

@router.get("/logs/resource/{resource}/{resource_id}", response_model=AuditLogListResponse)
async def get_resource_audit_logs(
    resource: str,
    resource_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_permission(Permissions.AUDIT_READ)),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for a specific resource
    """
    logs = AuditService.get_resource_audit_logs(db, resource, resource_id, limit, offset)
    total = db.query(AuditLog).filter(
        AuditLog.resource == resource,
        AuditLog.resource_id == resource_id
    ).count()
    
    # Convert to response format
    log_responses = []
    for log in logs:
        user_email = None
        if log.user_id:
            user = db.query(User).filter(User.id == log.user_id).first()
            if user:
                user_email = user.email
        
        log_responses.append(AuditLogResponse(
            id=log.id,
            timestamp=log.timestamp,
            user_id=log.user_id,
            user_email=user_email,
            action=log.action,
            resource=log.resource,
            resource_id=log.resource_id,
            ip_address=log.ip_address,
            result=log.result,
            details=log.details
        ))
    
    return AuditLogListResponse(
        logs=log_responses,
        total=total,
        limit=limit,
        offset=offset
    )

@router.get("/logs/failed", response_model=AuditLogListResponse)
async def get_failed_actions(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_permission(Permissions.AUDIT_READ)),
    db: Session = Depends(get_db)
):
    """
    Get all failed actions
    """
    logs = AuditService.get_failed_actions(db, limit, offset)
    total = db.query(AuditLog).filter(
        AuditLog.result.in_(['failure', 'error'])
    ).count()
    
    # Convert to response format
    log_responses = []
    for log in logs:
        user_email = None
        if log.user_id:
            user = db.query(User).filter(User.id == log.user_id).first()
            if user:
                user_email = user.email
        
        log_responses.append(AuditLogResponse(
            id=log.id,
            timestamp=log.timestamp,
            user_id=log.user_id,
            user_email=user_email,
            action=log.action,
            resource=log.resource,
            resource_id=log.resource_id,
            ip_address=log.ip_address,
            result=log.result,
            details=log.details
        ))
    
    return AuditLogListResponse(
        logs=log_responses,
        total=total,
        limit=limit,
        offset=offset
    )

@router.get("/compliance/report", response_model=ComplianceReportResponse)
async def generate_compliance_report(
    start_date: datetime = Query(..., description="Start date for report"),
    end_date: datetime = Query(..., description="End date for report"),
    current_user: User = Depends(require_permission(Permissions.COMPLIANCE_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Generate a compliance report for a specific time period
    """
    # Get all logs in the period
    logs = db.query(AuditLog).filter(
        AuditLog.timestamp >= start_date,
        AuditLog.timestamp <= end_date
    ).all()
    
    total_actions = len(logs)
    failed_actions = len([log for log in logs if log.result in ['failure', 'error']])
    unique_users = len(set(log.user_id for log in logs if log.user_id))
    
    # Generate summary by action type
    action_summary = {}
    for log in logs:
        if log.action not in action_summary:
            action_summary[log.action] = {
                'total': 0,
                'success': 0,
                'failure': 0,
                'error': 0
            }
        action_summary[log.action]['total'] += 1
        action_summary[log.action][log.result] += 1
    
    # Generate summary by resource type
    resource_summary = {}
    for log in logs:
        if log.resource not in resource_summary:
            resource_summary[log.resource] = {
                'total': 0,
                'success': 0,
                'failure': 0,
                'error': 0
            }
        resource_summary[log.resource]['total'] += 1
        resource_summary[log.resource][log.result] += 1
    
    summary = {
        'actions': action_summary,
        'resources': resource_summary,
        'success_rate': (total_actions - failed_actions) / total_actions * 100 if total_actions > 0 else 0
    }
    
    return ComplianceReportResponse(
        report_type="compliance_audit",
        generated_at=datetime.utcnow(),
        period_start=start_date,
        period_end=end_date,
        total_actions=total_actions,
        failed_actions=failed_actions,
        unique_users=unique_users,
        summary=summary
    )

@router.get("/me/activity", response_model=AuditLogListResponse)
async def get_my_activity(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's activity logs
    """
    logs = AuditService.get_user_audit_logs(db, current_user.id, limit, offset)
    total = db.query(AuditLog).filter(AuditLog.user_id == current_user.id).count()
    
    # Convert to response format
    log_responses = []
    for log in logs:
        log_responses.append(AuditLogResponse(
            id=log.id,
            timestamp=log.timestamp,
            user_id=log.user_id,
            user_email=current_user.email,
            action=log.action,
            resource=log.resource,
            resource_id=log.resource_id,
            ip_address=log.ip_address,
            result=log.result,
            details=log.details
        ))
    
    return AuditLogListResponse(
        logs=log_responses,
        total=total,
        limit=limit,
        offset=offset
    )
