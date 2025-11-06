import uuid
import time
from typing import Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel

# Initialize the router
router = APIRouter()

# In-memory storage for training jobs
# In a production environment, this would be replaced with a database
training_jobs: Dict[str, Dict] = {}

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
def simulate_training(job_id: str, total_epochs: int = 10):
    """
    Simulates a long-running model training process.
    Updates the job status in the in-memory store with progress and metrics.
    """
    try:
        # Initialize job state
        training_jobs[job_id] = {
            "status": "running",
            "progress": {"current_epoch": 0, "total_epochs": total_epochs},
            "metrics": {"accuracy": 0.5, "loss": 1.0},
            "explanation": "Training started. The model is currently learning basic patterns from the data.",
            "final_metrics": {},
            "summary": ""
        }
        
        # Simulate training epochs
        for epoch in range(1, total_epochs + 1):
            # Simulate work being done
            time.sleep(1)
            
            # Update progress
            training_jobs[job_id]["progress"]["current_epoch"] = epoch
            
            # Simulate improving metrics
            accuracy = 0.5 + (0.45 * (epoch / total_epochs))
            loss = 1.0 - (0.8 * (epoch / total_epochs))
            training_jobs[job_id]["metrics"] = {
                "accuracy": round(accuracy, 2),
                "loss": round(loss, 2)
            }
            
            # Update explanation based on current epoch
            if epoch <= 2:
                training_jobs[job_id]["explanation"] = "Training started. The model is currently learning basic patterns from the data."
            elif 3 <= epoch <= 7:
                training_jobs[job_id]["explanation"] = "Accuracy is improving. The model is now refining its decision boundaries to reduce errors."
            elif 8 <= epoch <= 9:
                training_jobs[job_id]["explanation"] = "Performance is plateauing. The model is converging on a final solution."
            else:
                training_jobs[job_id]["explanation"] = "Training complete. The model has finished learning and is ready for evaluation."
        
        # Mark job as completed and set final results
        training_jobs[job_id]["status"] = "completed"
        training_jobs[job_id]["final_metrics"] = {
            "accuracy": 0.92,
            "auc": 0.95,
            "precision": 0.91,
            "recall": 0.93
        }
        training_jobs[job_id]["summary"] = "The XGBoost model achieved high performance on the test set, with an AUC of 0.95, indicating excellent discriminative power."
        
    except Exception as e:
        # Handle any errors during training
        training_jobs[job_id]["status"] = "failed"
        training_jobs[job_id]["explanation"] = f"Training failed due to an error: {str(e)}"

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
    background_tasks.add_task(simulate_training, job_id)
    
    # Return the job ID and initial status
    return JobResponse(
        job_id=job_id,
        status="running",
        message="Model training job started."
    )

# Route to get job status
@router.get("/{job_id}/status", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Retrieves the real-time status and progress of a training job.
    This endpoint will be polled by the frontend to update the live visualization.
    """
    # Check if job exists
    if job_id not in training_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found."
        )
    
    # Return job status
    job_data = training_jobs[job_id]
    return JobStatus(
        job_id=job_id,
        status=job_data["status"],
        progress=job_data["progress"],
        metrics=job_data["metrics"],
        explanation=job_data["explanation"]
    )

# Route to get final job results
@router.get("/{job_id}/results", response_model=JobResults)
async def get_job_results(job_id: str):
    """
    Retrieves the final, complete results of a training job.
    This endpoint should only be used after the job status is 'completed'.
    """
    # Check if job exists
    if job_id not in training_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found."
        )
    
    # Check if job is completed
    job_data = training_jobs[job_id]
    if job_data["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job with ID {job_id} is not completed yet. Current status: {job_data['status']}"
        )
    
    # Return job results
    return JobResults(
        job_id=job_id,
        status=job_data["status"],
        final_metrics=job_data["final_metrics"],
        summary=job_data["summary"]
    )