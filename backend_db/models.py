"""
Database models for OmniScope AI Backend
SQLAlchemy models for all modules: Data Harbor, The Weaver, The Crucible, and The Insight Engine
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any

Base = declarative_base()

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
    pipeline_id = Column(String, nullable=False)
    data_ids = Column(JSON)  # Store list of data IDs
    status = Column(String, nullable=False)  # running, completed, failed
    progress = Column(JSON)  # Store progress information
    metrics = Column(JSON)  # Store current metrics
    explanation = Column(Text)
    final_metrics = Column(JSON)  # Store final results
    summary = Column(Text)
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