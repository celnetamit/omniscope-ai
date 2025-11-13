"""
ML Framework Module
Provides advanced machine learning capabilities including AutoML, deep learning,
transfer learning, ensemble methods, and model explainability.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
import uuid
import os
import json

# Import ML services
from backend_db.ml_services import (
    MLflowService,
    AutoMLService,
    DeepLearningService,
    TransferLearningService,
    EnsembleService,
    ExplainabilityService
)
from backend_db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

# ============================================================================
# Request/Response Models
# ============================================================================

class AutoMLTrainRequest(BaseModel):
    """Request model for AutoML training"""
    dataset_id: str
    target_column: str
    feature_columns: List[str]
    problem_type: Literal["classification", "regression"]
    time_limit: int = Field(default=600, description="Time limit in seconds")
    quality: Literal["best_quality", "high_quality", "good_quality", "medium_quality"] = "good_quality"
    
class DeepLearningTrainRequest(BaseModel):
    """Request model for deep learning training"""
    dataset_id: str
    target_column: str
    feature_columns: List[str]
    architecture: Literal["cnn_1d", "cnn_2d", "rnn", "lstm", "transformer"]
    problem_type: Literal["classification", "regression"]
    epochs: int = Field(default=100, ge=1, le=1000)
    batch_size: int = Field(default=32, ge=1, le=512)
    learning_rate: float = Field(default=0.001, gt=0, lt=1)
    
class TransferLearningRequest(BaseModel):
    """Request model for transfer learning"""
    dataset_id: str
    target_column: str
    feature_columns: List[str]
    base_model: str
    fine_tune_layers: int = Field(default=3, ge=1)
    epochs: int = Field(default=50, ge=1, le=500)
    
class EnsembleRequest(BaseModel):
    """Request model for ensemble creation"""
    model_ids: List[str] = Field(min_items=2)
    method: Literal["voting", "stacking", "blending"]
    weights: Optional[List[float]] = None
    
class ExplainRequest(BaseModel):
    """Request model for model explanation"""
    model_id: str
    method: Literal["shap", "lime"]
    sample_indices: Optional[List[int]] = None
    num_samples: int = Field(default=100, ge=1, le=1000)

class TrainingResponse(BaseModel):
    """Response model for training job submission"""
    job_id: str
    status: str
    message: str
    created_at: datetime

class JobStatusResponse(BaseModel):
    """Response model for job status"""
    job_id: str
    status: Literal["pending", "running", "completed", "failed"]
    progress: float = Field(ge=0, le=100)
    message: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

class ModelResultsResponse(BaseModel):
    """Response model for model results"""
    model_id: str
    model_name: str
    model_type: str
    metrics: Dict[str, Any]
    artifacts_path: str
    created_at: datetime

class ExplanationResponse(BaseModel):
    """Response model for model explanations"""
    model_id: str
    method: str
    feature_importance: Dict[str, float]
    visualizations: Dict[str, str]
    
# ============================================================================
# AutoML Endpoints
# ============================================================================

@router.post("/automl/train", response_model=TrainingResponse)
async def train_automl(
    request: AutoMLTrainRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Train an AutoML model using AutoGluon.
    Automatically selects the best algorithm and hyperparameters.
    """
    try:
        job_id = str(uuid.uuid4())
        
        # Initialize AutoML service
        automl_service = AutoMLService(db)
        
        # Submit training job to background
        background_tasks.add_task(
            automl_service.train,
            job_id=job_id,
            dataset_id=request.dataset_id,
            target_column=request.target_column,
            feature_columns=request.feature_columns,
            problem_type=request.problem_type,
            time_limit=request.time_limit,
            quality=request.quality
        )
        
        return TrainingResponse(
            job_id=job_id,
            status="pending",
            message="AutoML training job submitted successfully",
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit AutoML training: {str(e)}")

# ============================================================================
# Deep Learning Endpoints
# ============================================================================

@router.post("/deep-learning/train", response_model=TrainingResponse)
async def train_deep_learning(
    request: DeepLearningTrainRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Train a deep learning model using PyTorch Lightning.
    Supports CNN, RNN, LSTM, and Transformer architectures.
    """
    try:
        job_id = str(uuid.uuid4())
        
        # Initialize deep learning service
        dl_service = DeepLearningService(db)
        
        # Submit training job to background
        background_tasks.add_task(
            dl_service.train,
            job_id=job_id,
            dataset_id=request.dataset_id,
            target_column=request.target_column,
            feature_columns=request.feature_columns,
            architecture=request.architecture,
            problem_type=request.problem_type,
            epochs=request.epochs,
            batch_size=request.batch_size,
            learning_rate=request.learning_rate
        )
        
        return TrainingResponse(
            job_id=job_id,
            status="pending",
            message=f"Deep learning training job submitted for {request.architecture} architecture",
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit deep learning training: {str(e)}")

# ============================================================================
# Transfer Learning Endpoints
# ============================================================================

@router.post("/transfer-learning/train", response_model=TrainingResponse)
async def train_transfer_learning(
    request: TransferLearningRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Apply transfer learning using pre-trained models.
    Fine-tunes the model on your specific dataset.
    """
    try:
        job_id = str(uuid.uuid4())
        
        # Initialize transfer learning service
        tl_service = TransferLearningService(db)
        
        # Submit training job to background
        background_tasks.add_task(
            tl_service.train,
            job_id=job_id,
            dataset_id=request.dataset_id,
            target_column=request.target_column,
            feature_columns=request.feature_columns,
            base_model=request.base_model,
            fine_tune_layers=request.fine_tune_layers,
            epochs=request.epochs
        )
        
        return TrainingResponse(
            job_id=job_id,
            status="pending",
            message=f"Transfer learning job submitted with base model: {request.base_model}",
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit transfer learning: {str(e)}")

# ============================================================================
# Ensemble Endpoints
# ============================================================================

@router.post("/ensemble/create", response_model=TrainingResponse)
async def create_ensemble(
    request: EnsembleRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create an ensemble model combining multiple base models.
    Supports voting, stacking, and blending methods.
    """
    try:
        job_id = str(uuid.uuid4())
        
        # Initialize ensemble service
        ensemble_service = EnsembleService(db)
        
        # Submit ensemble creation to background
        background_tasks.add_task(
            ensemble_service.create_ensemble,
            job_id=job_id,
            model_ids=request.model_ids,
            method=request.method,
            weights=request.weights
        )
        
        return TrainingResponse(
            job_id=job_id,
            status="pending",
            message=f"Ensemble creation job submitted using {request.method} method",
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create ensemble: {str(e)}")

# ============================================================================
# Model Explainability Endpoints
# ============================================================================

@router.post("/models/{model_id}/explain", response_model=ExplanationResponse)
async def explain_model(
    model_id: str,
    request: ExplainRequest,
    db: Session = Depends(get_db)
):
    """
    Generate model explanations using SHAP or LIME.
    Provides feature importance and interpretability visualizations.
    """
    try:
        # Initialize explainability service
        explainability_service = ExplainabilityService(db)
        
        # Generate explanations
        explanation = explainability_service.explain(
            model_id=model_id,
            method=request.method,
            sample_indices=request.sample_indices,
            num_samples=request.num_samples
        )
        
        return ExplanationResponse(
            model_id=model_id,
            method=request.method,
            feature_importance=explanation["feature_importance"],
            visualizations=explanation["visualizations"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {str(e)}")

# ============================================================================
# Job Status and Results Endpoints
# ============================================================================

@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the status of a training job.
    """
    try:
        mlflow_service = MLflowService(db)
        status = mlflow_service.get_job_status(job_id)
        
        if not status:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return JobStatusResponse(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@router.get("/models/{model_id}/results", response_model=ModelResultsResponse)
async def get_model_results(
    model_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the results and metrics for a trained model.
    """
    try:
        mlflow_service = MLflowService(db)
        results = mlflow_service.get_model_results(model_id)
        
        if not results:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
        
        return ModelResultsResponse(**results)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model results: {str(e)}")

@router.get("/models/list")
async def list_models(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all trained models with pagination.
    """
    try:
        mlflow_service = MLflowService(db)
        models = mlflow_service.list_models(skip=skip, limit=limit)
        
        return {
            "models": models,
            "total": len(models),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")

@router.delete("/models/{model_id}")
async def delete_model(
    model_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a trained model and its artifacts.
    """
    try:
        mlflow_service = MLflowService(db)
        success = mlflow_service.delete_model(model_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
        
        return {"message": f"Model {model_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete model: {str(e)}")
