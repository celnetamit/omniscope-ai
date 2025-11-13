"""
Anonymization Module for OmniScope AI
Provides data anonymization and GDPR compliance endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend_db.database import get_db
from backend_db.auth import get_current_active_user
from backend_db.rbac import Permissions, require_permission
from backend_db.models import User
from backend_db.anonymization import AnonymizationService
from backend_db.audit import AuditService

router = APIRouter()

# Pydantic models
class PIIDetectionRequest(BaseModel):
    text: str

class PIIDetectionResponse(BaseModel):
    detected_pii: Dict[str, List[str]]
    pii_count: int

class AnonymizeTextRequest(BaseModel):
    text: str
    method: str = 'mask'  # mask, hash, remove
    pii_types: Optional[List[str]] = None

class AnonymizeTextResponse(BaseModel):
    original_text: str
    anonymized_text: str
    detected_pii: Dict[str, List[str]]

class AnonymizeDatasetRequest(BaseModel):
    data: Dict[str, Any]
    field_config: Dict[str, Dict[str, Any]]

class AnonymizeDatasetResponse(BaseModel):
    anonymized_data: Dict[str, Any]
    report: Dict[str, Any]

class KAnonymityCheckRequest(BaseModel):
    dataset: List[Dict[str, Any]]
    quasi_identifiers: List[str]
    k: int = 5

class KAnonymityCheckResponse(BaseModel):
    satisfies_k_anonymity: bool
    k: int
    group_sizes: List[int]

class GDPRDeleteRequest(BaseModel):
    user_id: str
    tables: List[str]

class GDPRDeleteResponse(BaseModel):
    deleted_counts: Dict[str, Any]
    timestamp: str

@router.post("/detect-pii", response_model=PIIDetectionResponse)
async def detect_pii(
    request_data: PIIDetectionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Detect PII in text
    """
    detected_pii = AnonymizationService.detect_pii(request_data.text)
    pii_count = sum(len(values) for values in detected_pii.values())
    
    return PIIDetectionResponse(
        detected_pii=detected_pii,
        pii_count=pii_count
    )

@router.post("/anonymize-text", response_model=AnonymizeTextResponse)
async def anonymize_text(
    request: Request,
    request_data: AnonymizeTextRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Anonymize PII in text
    """
    detected_pii = AnonymizationService.detect_pii(request_data.text)
    
    anonymized_text = AnonymizationService.anonymize_text(
        request_data.text,
        method=request_data.method,
        pii_types=request_data.pii_types
    )
    
    # Log anonymization
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="anonymize_text",
        resource="data",
        result="success",
        details={
            "method": request_data.method,
            "pii_detected": list(detected_pii.keys())
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return AnonymizeTextResponse(
        original_text=request_data.text,
        anonymized_text=anonymized_text,
        detected_pii=detected_pii
    )

@router.post("/anonymize-dataset", response_model=AnonymizeDatasetResponse)
async def anonymize_dataset(
    request: Request,
    request_data: AnonymizeDatasetRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Anonymize a dataset based on field configuration
    """
    anonymized_data = AnonymizationService.anonymize_dataset(
        request_data.data,
        request_data.field_config
    )
    
    report = AnonymizationService.generate_anonymization_report(
        request_data.data,
        anonymized_data
    )
    
    # Log anonymization
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="anonymize_dataset",
        resource="data",
        result="success",
        details={
            "fields_anonymized": report['fields_anonymized'],
            "pii_detected": report['pii_detected']
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return AnonymizeDatasetResponse(
        anonymized_data=anonymized_data,
        report=report
    )

@router.post("/check-k-anonymity", response_model=KAnonymityCheckResponse)
async def check_k_anonymity(
    request_data: KAnonymityCheckRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Check if dataset satisfies k-anonymity
    """
    satisfies = AnonymizationService.k_anonymity_check(
        request_data.dataset,
        request_data.quasi_identifiers,
        request_data.k
    )
    
    # Calculate group sizes
    groups = {}
    for record in request_data.dataset:
        key = tuple(record.get(qi) for qi in request_data.quasi_identifiers)
        if key not in groups:
            groups[key] = 0
        groups[key] += 1
    
    group_sizes = sorted(groups.values())
    
    return KAnonymityCheckResponse(
        satisfies_k_anonymity=satisfies,
        k=request_data.k,
        group_sizes=group_sizes
    )

@router.post("/gdpr/delete-user-data", response_model=GDPRDeleteResponse)
async def gdpr_delete_user_data(
    request: Request,
    request_data: GDPRDeleteRequest,
    current_user: User = Depends(require_permission(Permissions.COMPLIANCE_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Delete user data for GDPR compliance (right to erasure)
    """
    # Verify user exists
    target_user = db.query(User).filter(User.id == request_data.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete user data
    deleted_counts = AnonymizationService.gdpr_delete_user_data(
        db,
        request_data.user_id,
        request_data.tables
    )
    
    # Log GDPR deletion
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="gdpr_delete_user_data",
        resource="user",
        resource_id=request_data.user_id,
        result="success",
        details={
            "target_user": target_user.email,
            "tables": request_data.tables,
            "deleted_counts": deleted_counts
        },
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    from datetime import datetime
    return GDPRDeleteResponse(
        deleted_counts=deleted_counts,
        timestamp=datetime.utcnow().isoformat()
    )

@router.get("/gdpr/user-data-export/{user_id}")
async def gdpr_export_user_data(
    request: Request,
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Export user data for GDPR compliance (right to data portability)
    """
    # Users can only export their own data unless they have compliance permission
    if current_user.id != user_id:
        from backend_db.rbac import RBACService
        if not RBACService.has_permission(current_user, Permissions.COMPLIANCE_MANAGE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
    
    # Get user
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Collect user data
    user_data = {
        'user_profile': {
            'id': target_user.id,
            'email': target_user.email,
            'name': target_user.name,
            'created_at': target_user.created_at.isoformat() if target_user.created_at else None,
            'roles': [role.name for role in target_user.roles]
        },
        'audit_logs': [],
        'export_timestamp': datetime.utcnow().isoformat()
    }
    
    # Get audit logs
    from backend_db.models import AuditLog
    audit_logs = db.query(AuditLog).filter(
        AuditLog.user_id == user_id
    ).order_by(AuditLog.timestamp.desc()).limit(1000).all()
    
    for log in audit_logs:
        user_data['audit_logs'].append({
            'timestamp': log.timestamp.isoformat(),
            'action': log.action,
            'resource': log.resource,
            'result': log.result
        })
    
    # Log data export
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="gdpr_export_user_data",
        resource="user",
        resource_id=user_id,
        result="success",
        details={"target_user": target_user.email},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return user_data
