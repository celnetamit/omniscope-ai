"""
Audit logging service for OmniScope AI
Implements immutable append-only audit logs
"""

from sqlalchemy.orm import Session
from .models import AuditLog
from typing import Optional, Dict, Any
from datetime import datetime

class AuditService:
    """Service for audit logging operations"""
    
    @staticmethod
    async def log_action(
        db: Session,
        action: str,
        resource: str,
        result: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Log an action to the audit log
        
        Args:
            db: Database session
            action: Action performed (e.g., 'login', 'create_pipeline')
            resource: Resource type (e.g., 'user', 'pipeline')
            result: Result of action ('success', 'failure', 'error')
            user_id: ID of user performing action (optional)
            resource_id: ID of resource affected (optional)
            ip_address: IP address of request (optional)
            user_agent: User agent string (optional)
            details: Additional details as JSON (optional)
        
        Returns:
            Created AuditLog entry
        """
        audit_log = AuditLog(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            result=result,
            details=details
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    @staticmethod
    def get_user_audit_logs(
        db: Session,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ):
        """Get audit logs for a specific user"""
        return db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(
            AuditLog.timestamp.desc()
        ).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_resource_audit_logs(
        db: Session,
        resource: str,
        resource_id: str,
        limit: int = 100,
        offset: int = 0
    ):
        """Get audit logs for a specific resource"""
        return db.query(AuditLog).filter(
            AuditLog.resource == resource,
            AuditLog.resource_id == resource_id
        ).order_by(
            AuditLog.timestamp.desc()
        ).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_failed_actions(
        db: Session,
        limit: int = 100,
        offset: int = 0
    ):
        """Get all failed actions"""
        return db.query(AuditLog).filter(
            AuditLog.result.in_(['failure', 'error'])
        ).order_by(
            AuditLog.timestamp.desc()
        ).limit(limit).offset(offset).all()
    
    @staticmethod
    def search_audit_logs(
        db: Session,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        user_id: Optional[str] = None,
        result: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """Search audit logs with filters"""
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
        
        return query.order_by(
            AuditLog.timestamp.desc()
        ).limit(limit).offset(offset).all()
