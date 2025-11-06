"""
Database service layer for OmniScope AI Backend
CRUD operations for all modules
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from .models import FileAnalysisReport, Pipeline, TrainingJob, BiomarkerResult, QueryLog

class DataHarborService:
    """Database service for Data Harbor module"""
    
    @staticmethod
    def create_report(db: Session, file_id: str, filename: str, status: str, message: str = None) -> FileAnalysisReport:
        """Create a new file analysis report"""
        report = FileAnalysisReport(
            id=file_id,
            filename=filename,
            status=status,
            message=message
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report
    
    @staticmethod
    def update_report(db: Session, file_id: str, status: str, report_data: Dict = None, message: str = None) -> Optional[FileAnalysisReport]:
        """Update an existing file analysis report"""
        report = db.query(FileAnalysisReport).filter(FileAnalysisReport.id == file_id).first()
        if report:
            report.status = status
            if report_data:
                report.report_data = report_data
            if message:
                report.message = message
            report.updated_at = datetime.now()
            db.commit()
            db.refresh(report)
        return report
    
    @staticmethod
    def get_report(db: Session, file_id: str) -> Optional[FileAnalysisReport]:
        """Get a file analysis report by ID"""
        return db.query(FileAnalysisReport).filter(FileAnalysisReport.id == file_id).first()
    
    @staticmethod
    def cleanup_old_reports(db: Session, max_reports: int = 100):
        """Remove old reports to manage storage"""
        total_reports = db.query(FileAnalysisReport).count()
        if total_reports > max_reports:
            # Keep the most recent reports
            reports_to_delete = db.query(FileAnalysisReport)\
                .order_by(desc(FileAnalysisReport.created_at))\
                .offset(max_reports)\
                .all()
            
            for report in reports_to_delete:
                db.delete(report)
            db.commit()

class WeaverService:
    """Database service for The Weaver module"""
    
    @staticmethod
    def save_pipeline(db: Session, pipeline_id: str, project_id: str, name: str, 
                     pipeline_json: Dict, warnings: List[str] = None) -> Pipeline:
        """Save or update a pipeline"""
        pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
        
        if pipeline:
            # Update existing pipeline
            pipeline.name = name
            pipeline.pipeline_json = pipeline_json
            pipeline.warnings = warnings or []
            pipeline.updated_at = datetime.now()
        else:
            # Create new pipeline
            pipeline = Pipeline(
                id=pipeline_id,
                project_id=project_id,
                name=name,
                pipeline_json=pipeline_json,
                warnings=warnings or []
            )
            db.add(pipeline)
        
        db.commit()
        db.refresh(pipeline)
        return pipeline
    
    @staticmethod
    def get_pipeline(db: Session, pipeline_id: str) -> Optional[Pipeline]:
        """Get a pipeline by ID"""
        return db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    
    @staticmethod
    def list_pipelines(db: Session, project_id: str) -> List[Pipeline]:
        """List all pipelines for a project"""
        return db.query(Pipeline)\
            .filter(Pipeline.project_id == project_id)\
            .order_by(desc(Pipeline.updated_at))\
            .all()

class CrucibleService:
    """Database service for The Crucible module"""
    
    @staticmethod
    def create_training_job(db: Session, job_id: str, pipeline_id: str, data_ids: List[str]) -> TrainingJob:
        """Create a new training job"""
        job = TrainingJob(
            id=job_id,
            pipeline_id=pipeline_id,
            data_ids=data_ids,
            status="running",
            progress={"current_epoch": 0, "total_epochs": 10},
            metrics={"accuracy": 0.5, "loss": 1.0},
            explanation="Training started. The model is currently learning basic patterns from the data."
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    
    @staticmethod
    def update_training_job(db: Session, job_id: str, status: str = None, progress: Dict = None, 
                           metrics: Dict = None, explanation: str = None, 
                           final_metrics: Dict = None, summary: str = None) -> Optional[TrainingJob]:
        """Update a training job"""
        job = db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
        if job:
            if status:
                job.status = status
            if progress:
                job.progress = progress
            if metrics:
                job.metrics = metrics
            if explanation:
                job.explanation = explanation
            if final_metrics:
                job.final_metrics = final_metrics
            if summary:
                job.summary = summary
            job.updated_at = datetime.now()
            db.commit()
            db.refresh(job)
        return job
    
    @staticmethod
    def get_training_job(db: Session, job_id: str) -> Optional[TrainingJob]:
        """Get a training job by ID"""
        return db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
    
    @staticmethod
    def cleanup_old_jobs(db: Session, max_jobs: int = 50):
        """Remove old completed/failed jobs"""
        # Keep running jobs
        running_jobs = db.query(TrainingJob).filter(TrainingJob.status == "running").count()
        
        # Remove old completed/failed jobs if we exceed the limit
        total_jobs = db.query(TrainingJob).count()
        if total_jobs > max_jobs:
            jobs_to_delete = db.query(TrainingJob)\
                .filter(TrainingJob.status.in_(["completed", "failed"]))\
                .order_by(desc(TrainingJob.updated_at))\
                .offset(max(0, max_jobs - running_jobs))\
                .all()
            
            for job in jobs_to_delete:
                db.delete(job)
            db.commit()

class InsightEngineService:
    """Database service for The Insight Engine module"""
    
    @staticmethod
    def save_biomarkers(db: Session, model_id: str, biomarkers: List[Dict]) -> List[BiomarkerResult]:
        """Save biomarker results for a model"""
        # First, remove existing biomarkers for this model
        db.query(BiomarkerResult).filter(BiomarkerResult.model_id == model_id).delete()
        
        # Add new biomarkers
        biomarker_objects = []
        for biomarker in biomarkers:
            biomarker_obj = BiomarkerResult(
                model_id=model_id,
                gene_id=biomarker["gene_id"],
                gene_name=biomarker["gene_name"],
                biomarker_type=biomarker["type"],
                importance_score=biomarker["importance_score"],
                p_value=biomarker["p_value"],
                external_links=biomarker["external_links"]
            )
            biomarker_objects.append(biomarker_obj)
            db.add(biomarker_obj)
        
        db.commit()
        return biomarker_objects
    
    @staticmethod
    def get_biomarkers(db: Session, model_id: str) -> List[BiomarkerResult]:
        """Get all biomarkers for a model"""
        return db.query(BiomarkerResult)\
            .filter(BiomarkerResult.model_id == model_id)\
            .order_by(desc(BiomarkerResult.importance_score))\
            .all()
    
    @staticmethod
    def get_biomarker(db: Session, model_id: str, gene_id: str) -> Optional[BiomarkerResult]:
        """Get a specific biomarker"""
        return db.query(BiomarkerResult)\
            .filter(and_(BiomarkerResult.model_id == model_id, 
                        BiomarkerResult.gene_id == gene_id))\
            .first()
    
    @staticmethod
    def log_query(db: Session, model_id: str, query: str, response: str, response_data: Dict = None) -> QueryLog:
        """Log a natural language query"""
        query_log = QueryLog(
            model_id=model_id,
            query=query,
            response=response,
            response_data=response_data
        )
        db.add(query_log)
        db.commit()
        db.refresh(query_log)
        return query_log