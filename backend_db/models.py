"""
Database models for OmniScope AI Backend
SQLAlchemy models for all modules: Data Harbor, The Weaver, The Crucible, and The Insight Engine
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, JSON, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any
import uuid

Base = declarative_base()

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('role_id', String, ForeignKey('roles.id'), primary_key=True)
)

class User(Base):
    """Model for user authentication and profile"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    is_active = Column(Boolean, default=True)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    mfa_recovery_codes = relationship("MFARecoveryCode", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")

class Role(Base):
    """Model for role-based access control"""
    __tablename__ = "roles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSON)  # Store list of permissions
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")

class RefreshToken(Base):
    """Model for refresh token management"""
    __tablename__ = "refresh_tokens"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

class MFARecoveryCode(Base):
    """Model for MFA recovery codes"""
    __tablename__ = "mfa_recovery_codes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    code_hash = Column(String(255), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    used_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="mfa_recovery_codes")

class AuditLog(Base):
    """Model for audit logging"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(255), nullable=False)
    resource_id = Column(String)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(String(500))
    result = Column(String(50), nullable=False)  # success, failure, error
    details = Column(JSON)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

class EncryptedData(Base):
    """Model for storing encrypted sensitive data"""
    __tablename__ = "encrypted_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    data_type = Column(String(100), nullable=False)
    encrypted_value = Column(Text, nullable=False)
    encryption_key_id = Column(String(255))  # Reference to key management system
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class FileAnalysisReport(Base):
    """Model for Data Harbor - File analysis reports"""
    __tablename__ = "file_analysis_reports"
    
    id = Column(String, primary_key=True)  # file_id
    filename = Column(String, nullable=False)
    status = Column(String, nullable=False)  # processing, complete, error
    message = Column(Text)
    report_data = Column(JSON)  # Store the full analysis report as JSON
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Pipeline(Base):
    """Model for The Weaver - Pipeline configurations"""
    __tablename__ = "pipelines"
    
    id = Column(String, primary_key=True)  # pipeline_id
    project_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    pipeline_json = Column(JSON, nullable=False)  # Store nodes and edges
    warnings = Column(JSON)  # Store validation warnings
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class TrainingJob(Base):
    """Model for The Crucible - Model training jobs"""
    __tablename__ = "training_jobs"
    
    id = Column(String, primary_key=True)  # job_id
    pipeline_id = Column(String)
    data_ids = Column(JSON)  # Store list of data IDs
    model_type = Column(String)  # automl, deep_learning, transfer_learning, ensemble
    status = Column(String, nullable=False)  # pending, running, completed, failed
    progress = Column(Float, default=0.0)  # Progress percentage
    message = Column(Text)  # Status message
    metrics = Column(JSON)  # Store current metrics
    explanation = Column(Text)
    final_metrics = Column(JSON)  # Store final results
    summary = Column(Text)
    error = Column(Text)  # Error message if failed
    model_id = Column(String)  # Reference to created model
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class MLModel(Base):
    """Model for ML Framework - Trained models"""
    __tablename__ = "ml_models"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # automl, deep_learning, transfer_learning, ensemble
    architecture = Column(String(100))  # Model architecture (e.g., cnn_1d, random_forest)
    hyperparameters = Column(JSON)  # Model hyperparameters
    training_config = Column(JSON)  # Training configuration
    metrics = Column(JSON)  # Model performance metrics
    artifacts_path = Column(String(500))  # Path to model artifacts
    mlflow_run_id = Column(String(255))  # MLflow run ID
    created_by = Column(String, ForeignKey('users.id'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class BiomarkerResult(Base):
    """Model for The Insight Engine - Biomarker analysis results"""
    __tablename__ = "biomarker_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(String, nullable=False)
    gene_id = Column(String, nullable=False)
    gene_name = Column(String, nullable=False)
    biomarker_type = Column(String, nullable=False)  # gene, protein, metabolite
    importance_score = Column(Float, nullable=False)
    p_value = Column(Float, nullable=False)
    external_links = Column(JSON)  # Store external database links
    created_at = Column(DateTime, default=func.now())
    
    # Composite index for efficient queries
    __table_args__ = (
        {'sqlite_autoincrement': True}
    )

class QueryLog(Base):
    """Model for logging natural language queries"""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    response_data = Column(JSON)  # Store structured response data
    created_at = Column(DateTime, default=func.now())

class Workspace(Base):
    """Model for collaborative workspaces"""
    __tablename__ = "workspaces"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    owner_id = Column(String, ForeignKey('users.id'), nullable=False)
    pipeline_state = Column(JSON)  # Store collaborative pipeline state
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")

class WorkspaceMember(Base):
    """Model for workspace membership"""
    __tablename__ = "workspace_members"
    
    workspace_id = Column(String, ForeignKey('workspaces.id'), primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), primary_key=True)
    role = Column(String(50), nullable=False)  # owner, editor, viewer
    cursor_position = Column(JSON)  # Store last cursor position
    last_seen = Column(DateTime, default=func.now(), onupdate=func.now())
    joined_at = Column(DateTime, default=func.now())
    
    # Relationships
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User")

class Report(Base):
    """Model for generated reports"""
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    template_id = Column(String)
    content = Column(JSON)  # Store report content and metadata
    format = Column(String(20), nullable=False)  # pdf, docx, latex
    file_path = Column(String(500))
    status = Column(String(50), default='completed')  # pending, processing, completed, failed
    created_by = Column(String, ForeignKey('users.id'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())