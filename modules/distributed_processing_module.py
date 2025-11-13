"""
Distributed Processing Module for OmniScope AI
Provides API endpoints for distributed data processing using Dask
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from backend_db.database import get_db
from backend_db.distributed_processing import (
    get_cluster_manager,
    ensure_cluster_running,
    JobScheduler,
    JobPriority,
    JobStatus,
    ProcessingJob,
    ClusterMetrics,
    DataPartitioner,
    DistributedDataLoader
)

import pandas as pd
import numpy as np
from dask import delayed

router = APIRouter(prefix="/api/processing")


# Pydantic models for API
class JobSubmitRequest(BaseModel):
    """Request model for job submission"""
    operation: str = Field(..., description="Operation to perform (e.g., 'aggregate', 'transform', 'analyze')")
    dataset_id: Optional[str] = Field(None, description="Dataset identifier")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")
    priority: str = Field("NORMAL", description="Job priority: LOW, NORMAL, HIGH, CRITICAL")
    max_memory_gb: float = Field(2.0, description="Maximum memory allocation in GB")
    max_cores: int = Field(2, description="Maximum CPU cores")


class JobStatusResponse(BaseModel):
    """Response model for job status"""
    job_id: str
    status: str
    priority: str
    progress: Optional[float] = None
    result: Optional[Dict] = None
    error_message: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class ClusterStatusResponse(BaseModel):
    """Response model for cluster status"""
    status: str
    scheduler_address: Optional[str] = None
    dashboard_url: Optional[str] = None
    n_workers: int
    total_cores: int
    total_memory: str
    used_memory: str
    memory_usage_percent: float
    active_tasks: int


class ClusterScaleRequest(BaseModel):
    """Request model for cluster scaling"""
    n_workers: int = Field(..., ge=1, le=32, description="Target number of workers")


class DataPartitionRequest(BaseModel):
    """Request model for data partitioning"""
    dataset_id: str = Field(..., description="Dataset identifier")
    partition_size_mb: Optional[int] = Field(None, description="Target partition size in MB")
    n_partitions: Optional[int] = Field(None, description="Number of partitions")


# Global scheduler instance
_scheduler: Optional[JobScheduler] = None


def get_scheduler() -> JobScheduler:
    """Get or create global scheduler instance"""
    global _scheduler
    
    if _scheduler is None:
        ensure_cluster_running()
        manager = get_cluster_manager()
        _scheduler = JobScheduler(manager.client)
    
    return _scheduler


# Example processing functions
@delayed
def aggregate_data(data: pd.DataFrame, column: str, operation: str) -> Dict:
    """Aggregate data by column"""
    if operation == "mean":
        result = data[column].mean()
    elif operation == "sum":
        result = data[column].sum()
    elif operation == "count":
        result = data[column].count()
    else:
        raise ValueError(f"Unknown operation: {operation}")
    
    return {"column": column, "operation": operation, "result": float(result)}


@delayed
def transform_data(data: pd.DataFrame, transformation: str) -> pd.DataFrame:
    """Transform data"""
    if transformation == "normalize":
        return (data - data.mean()) / data.std()
    elif transformation == "log":
        return np.log1p(data)
    else:
        raise ValueError(f"Unknown transformation: {transformation}")


# API Endpoints

@router.post("/cluster/start")
async def start_cluster(db: Session = Depends(get_db)):
    """
    Start the Dask cluster
    
    Returns cluster information including dashboard URL
    """
    try:
        manager = get_cluster_manager()
        
        if manager.is_running():
            return {
                "message": "Cluster is already running",
                "cluster_info": manager.get_cluster_status()
            }
        
        cluster_info = manager.start_cluster()
        
        return {
            "message": "Cluster started successfully",
            "cluster_info": cluster_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start cluster: {str(e)}")


@router.post("/cluster/stop")
async def stop_cluster():
    """
    Stop the Dask cluster
    """
    try:
        manager = get_cluster_manager()
        
        if not manager.is_running():
            return {"message": "Cluster is not running"}
        
        manager.stop_cluster()
        
        return {"message": "Cluster stopped successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop cluster: {str(e)}")


@router.get("/cluster/status", response_model=ClusterStatusResponse)
async def get_cluster_status():
    """
    Get current cluster status and metrics
    """
    try:
        manager = get_cluster_manager()
        status = manager.get_cluster_status()
        
        return ClusterStatusResponse(**status)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cluster status: {str(e)}")


@router.post("/cluster/scale")
async def scale_cluster(request: ClusterScaleRequest):
    """
    Scale the cluster to specified number of workers
    """
    try:
        manager = get_cluster_manager()
        
        if not manager.is_running():
            raise HTTPException(status_code=400, detail="Cluster is not running")
        
        cluster_info = manager.scale_cluster(request.n_workers)
        
        return {
            "message": f"Cluster scaled to {request.n_workers} workers",
            "cluster_info": cluster_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scale cluster: {str(e)}")


@router.post("/jobs/submit")
async def submit_job(request: JobSubmitRequest, db: Session = Depends(get_db)):
    """
    Submit a job for distributed processing
    
    Returns job ID for tracking
    """
    try:
        ensure_cluster_running()
        scheduler = get_scheduler()
        
        # Parse priority
        try:
            priority = JobPriority[request.priority.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid priority: {request.priority}")
        
        # Create processing function based on operation
        if request.operation == "aggregate":
            # Example: aggregate operation
            def job_func():
                # In production, load actual data from dataset_id
                data = pd.DataFrame(np.random.randn(1000, 10))
                column = request.parameters.get("column", 0)
                operation = request.parameters.get("operation", "mean")
                return aggregate_data(data, column, operation).compute()
        
        elif request.operation == "transform":
            # Example: transform operation
            def job_func():
                data = pd.DataFrame(np.random.randn(1000, 10))
                transformation = request.parameters.get("transformation", "normalize")
                return transform_data(data, transformation).compute().to_dict()
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation: {request.operation}")
        
        # Submit job
        job_id = scheduler.submit_job(
            job_func,
            priority=priority,
            max_memory_gb=request.max_memory_gb,
            max_cores=request.max_cores
        )
        
        # Save to database
        job = ProcessingJob(
            id=job_id,
            type=request.operation,
            dataset_id=request.dataset_id,
            operation=request.operation,
            parameters=request.parameters,
            priority=priority,
            status=JobStatus.PENDING,
            n_workers=request.max_cores,
            memory_per_worker=f"{request.max_memory_gb}GB"
        )
        
        db.add(job)
        db.commit()
        
        return {
            "message": "Job submitted successfully",
            "job_id": job_id,
            "status": "pending"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit job: {str(e)}")


@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get status of a specific job
    """
    try:
        # Get from database
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # Get live status from scheduler if available
        scheduler = get_scheduler()
        live_status = scheduler.get_job_status(job_id)
        
        if live_status:
            # Update database with live status
            job.status = live_status.get('status', job.status)
        
        return JobStatusResponse(
            job_id=job.id,
            status=job.status,
            priority=JobPriority(job.priority).name,
            progress=job.progress,
            result=job.result,
            error_message=job.error_message,
            created_at=job.created_at.isoformat(),
            started_at=job.started_at.isoformat() if job.started_at else None,
            completed_at=job.completed_at.isoformat() if job.completed_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str, db: Session = Depends(get_db)):
    """
    Cancel a running or queued job
    """
    try:
        scheduler = get_scheduler()
        
        success = scheduler.cancel_job(job_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # Update database
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if job:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            db.commit()
        
        return {
            "message": "Job cancelled successfully",
            "job_id": job_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")


@router.get("/jobs/list")
async def list_jobs(
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all jobs with optional status filter
    """
    try:
        query = db.query(ProcessingJob)
        
        if status:
            query = query.filter(ProcessingJob.status == status)
        
        jobs = query.order_by(ProcessingJob.created_at.desc()).limit(limit).all()
        
        return {
            "total": len(jobs),
            "jobs": [
                {
                    "job_id": job.id,
                    "type": job.type,
                    "operation": job.operation,
                    "status": job.status,
                    "priority": JobPriority(job.priority).name,
                    "progress": job.progress,
                    "created_at": job.created_at.isoformat()
                }
                for job in jobs
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


@router.get("/queue/status")
async def get_queue_status():
    """
    Get current job queue status
    """
    try:
        scheduler = get_scheduler()
        status = scheduler.get_scheduler_status()
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get queue status: {str(e)}")


@router.post("/data/partition")
async def partition_data(request: DataPartitionRequest):
    """
    Partition data for distributed processing
    """
    try:
        ensure_cluster_running()
        manager = get_cluster_manager()
        partitioner = DataPartitioner(manager.client)
        
        # In production, load actual data from dataset_id
        # For now, create sample data
        data = pd.DataFrame(np.random.randn(10000, 50))
        
        ddf = partitioner.partition_dataframe(
            data,
            partition_size_mb=request.partition_size_mb,
            n_partitions=request.n_partitions
        )
        
        info = partitioner.get_partition_info(ddf)
        
        return {
            "message": "Data partitioned successfully",
            "dataset_id": request.dataset_id,
            "partition_info": info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to partition data: {str(e)}")


@router.get("/metrics/cluster")
async def get_cluster_metrics(db: Session = Depends(get_db)):
    """
    Get cluster metrics history
    """
    try:
        metrics = db.query(ClusterMetrics).order_by(
            ClusterMetrics.timestamp.desc()
        ).limit(100).all()
        
        return {
            "total": len(metrics),
            "metrics": [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "n_workers": m.n_workers,
                    "total_memory": m.total_memory,
                    "used_memory": m.used_memory,
                    "total_cores": m.total_cores,
                    "active_tasks": m.active_tasks
                }
                for m in metrics
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for distributed processing service
    """
    try:
        manager = get_cluster_manager()
        is_running = manager.is_running()
        
        return {
            "status": "healthy" if is_running else "degraded",
            "cluster_running": is_running,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
