import uuid
import time
from typing import Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import database components
from backend_db import get_db, CrucibleService, get_db_session, close_db_session

# Initialize the router
router = APIRouter()

# Pydantic models for request/response validation
class TrainingRequest(BaseModel):
    pipeline_id: str
    data_ids: List[str]

class JobStatus(BaseModel):
    job_id: str
    status: str  # 'running', 'completed', 'failed'
    progress: Dict[str, int]
    metrics: Dict[str, float]
    explanation: str

class JobResults(BaseModel):
    job_id: str
    status: str
    final_metrics: Dict[str, float]
    summary: str

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

# Background task to simulate model training
def simulate_training(job_id: str, pipeline_id: str, data_ids: List[str], total_epochs: int = 10):
    """
    Simulates a long-running model training process.
    Updates the job status in the database with progress and metrics.
    """
    db = get_db_session()
    try:
        # Create initial job in database
        CrucibleService.create_training_job(
            db=db,
            job_id=job_id,
            pipeline_id=pipeline_id,
            data_ids=data_ids
        )
        
        # Simulate training epochs
        for epoch in range(1, total_epochs + 1):
            # Simulate work being done
            time.sleep(1)
            
            # Update progress
            progress = {"current_epoch": epoch, "total_epochs": total_epochs}
            
            # Simulate improving metrics
            accuracy = 0.5 + (0.45 * (epoch / total_epochs))
            loss = 1.0 - (0.8 * (epoch / total_epochs))
            metrics = {
                "accuracy": round(accuracy, 2),
                "loss": round(loss, 2)
            }
            
            # Update explanation based on current epoch
            if epoch <= 2:
                explanation = "Training started. The model is currently learning basic patterns from the data."
            elif 3 <= epoch <= 7:
                explanation = "Accuracy is improving. The model is now refining its decision boundaries to reduce errors."
            elif 8 <= epoch <= 9:
                explanation = "Performance is plateauing. The model is converging on a final solution."
            else:
                explanation = "Training complete. The model has finished learning and is ready for evaluation."
            
            # Update job in database
            CrucibleService.update_training_job(
                db=db,
                job_id=job_id,
                progress=progress,
                metrics=metrics,
                explanation=explanation
            )
        
        # Mark job as completed and set final results
        final_metrics = {
            "accuracy": 0.92,
            "auc": 0.95,
            "precision": 0.91,
            "recall": 0.93
        }
        summary = "The XGBoost model achieved high performance on the test set, with an AUC of 0.95, indicating excellent discriminative power."
        
        CrucibleService.update_training_job(
            db=db,
            job_id=job_id,
            status="completed",
            final_metrics=final_metrics,
            summary=summary
        )
        
        # Cleanup old jobs
        CrucibleService.cleanup_old_jobs(db, max_jobs=50)
        
    except Exception as e:
        # Handle any errors during training
        CrucibleService.update_training_job(
            db=db,
            job_id=job_id,
            status="failed",
            explanation=f"Training failed due to an error: {str(e)}"
        )
        print(f"Training job {job_id} failed: {str(e)}")
        CrucibleService.cleanup_old_jobs(db, max_jobs=50)
    finally:
        close_db_session(db)

# Route to start a new training job
@router.post("/train", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_training_job(request: TrainingRequest, background_tasks: BackgroundTasks):
    """
    Starts a model training job in the background.
    Immediately returns a job_id for tracking.
    """
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Add the training simulation to background tasks
    background_tasks.add_task(simulate_training, job_id, request.pipeline_id, request.data_ids)
    
    # Return the job ID and initial status
    return JobResponse(
        job_id=job_id,
        status="running",
        message="Model training job started."
    )

# Route to get job status
@router.get("/{job_id}/status", response_model=JobStatus)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Retrieves the real-time status and progress of a training job.
    This endpoint will be polled by the frontend to update the live visualization.
    """
    # Get job from database
    job = CrucibleService.get_training_job(db, job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found."
        )
    
    # Return job status
    return JobStatus(
        job_id=job_id,
        status=job.status,
        progress=job.progress,
        metrics=job.metrics,
        explanation=job.explanation
    )

# Route to get final job results
@router.get("/{job_id}/results", response_model=JobResults)
async def get_job_results(job_id: str, db: Session = Depends(get_db)):
    """
    Retrieves the final, complete results of a training job.
    This endpoint should only be used after the job status is 'completed'.
    """
    # Get job from database
    job = CrucibleService.get_training_job(db, job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found."
        )
    
    # Check if job is completed
    if job.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job with ID {job_id} is not completed yet. Current status: {job.status}"
        )
    
    # Return job results
    return JobResults(
        job_id=job_id,
        status=job.status,
        final_metrics=job.final_metrics,
        summary=job.summary
    )