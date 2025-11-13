# Advanced ML Framework Implementation

## Overview

The Advanced ML Framework has been successfully implemented for OmniScope AI, providing enterprise-grade machine learning capabilities including AutoML, deep learning, transfer learning, ensemble methods, and model explainability.

## Implementation Summary

### Components Implemented

#### 1. MLflow Integration (Task 4.1)
- **MLflowService**: Core service for experiment tracking and model registry
- **Features**:
  - Experiment creation and management
  - Run tracking with parameters and metrics
  - Model versioning and artifact storage
  - Model registry for production deployment
- **Configuration**: Uses `MLFLOW_TRACKING_URI` environment variable (defaults to `file:./mlruns`)

#### 2. AutoML Engine (Task 4.2)
- **AutoMLService**: Automated machine learning using AutoGluon
- **Features**:
  - Automatic algorithm selection
  - Hyperparameter optimization
  - Support for classification and regression
  - Configurable time limits and quality presets
- **API Endpoint**: `POST /api/ml/automl/train`

#### 3. Deep Learning Trainer (Task 4.3)
- **DeepLearningService**: PyTorch Lightning-based training
- **Supported Architectures**:
  - CNN (1D and 2D) for sequence and image data
  - RNN/LSTM for sequential data
  - Transformer models for complex patterns
- **Features**:
  - Configurable epochs, batch size, learning rate
  - Real-time training progress tracking
  - Automatic metric logging
- **API Endpoint**: `POST /api/ml/deep-learning/train`

#### 4. Transfer Learning System (Task 4.4)
- **TransferLearningService**: Pre-trained model fine-tuning
- **Features**:
  - Pre-trained model repository
  - Configurable fine-tuning layers
  - Model adaptation for omics data
- **API Endpoint**: `POST /api/ml/transfer-learning/train`

#### 5. Ensemble Model Creator (Task 4.5)
- **EnsembleService**: Combines multiple models
- **Methods**:
  - Voting: Simple or weighted voting
  - Stacking: Meta-learner on base predictions
  - Blending: Holdout set predictions
- **Features**:
  - Automatic performance evaluation
  - Configurable model weights
- **API Endpoint**: `POST /api/ml/ensemble/create`

#### 6. Model Explainability (Task 4.6)
- **ExplainabilityService**: Model interpretation
- **Methods**:
  - SHAP: Feature importance and dependence plots
  - LIME: Local interpretable explanations
- **Features**:
  - Feature importance ranking
  - Visualization generation
  - Sample-specific explanations
- **API Endpoint**: `POST /api/ml/models/{model_id}/explain`

#### 7. ML Training API Endpoints (Task 4.7)
All endpoints are integrated under `/api/ml` prefix:

**Training Endpoints**:
- `POST /api/ml/automl/train` - Start AutoML training
- `POST /api/ml/deep-learning/train` - Start deep learning training
- `POST /api/ml/transfer-learning/train` - Start transfer learning
- `POST /api/ml/ensemble/create` - Create ensemble model

**Model Management**:
- `GET /api/ml/jobs/{job_id}/status` - Get training job status
- `GET /api/ml/models/{model_id}/results` - Get model results
- `GET /api/ml/models/list` - List all models
- `DELETE /api/ml/models/{model_id}` - Delete model

**Explainability**:
- `POST /api/ml/models/{model_id}/explain` - Generate explanations

## Database Schema

### New Tables

#### ml_models
Stores trained model metadata:
```sql
- id: UUID (primary key)
- name: Model name
- type: automl, deep_learning, transfer_learning, ensemble
- architecture: Model architecture (e.g., cnn_1d, random_forest)
- hyperparameters: JSON (model hyperparameters)
- training_config: JSON (training configuration)
- metrics: JSON (performance metrics)
- artifacts_path: Path to model files
- mlflow_run_id: MLflow run identifier
- created_by: User ID
- created_at: Timestamp
- updated_at: Timestamp
```

#### training_jobs (Enhanced)
Enhanced to support ML framework:
```sql
- id: UUID (primary key)
- model_type: automl, deep_learning, transfer_learning, ensemble
- status: pending, running, completed, failed
- progress: Float (0-100)
- message: Status message
- error: Error message if failed
- model_id: Reference to created model
- started_at: Timestamp
- completed_at: Timestamp
```

## API Request/Response Models

### AutoML Training Request
```json
{
  "dataset_id": "string",
  "target_column": "string",
  "feature_columns": ["feature1", "feature2"],
  "problem_type": "classification",
  "time_limit": 600,
  "quality": "good_quality"
}
```

### Deep Learning Training Request
```json
{
  "dataset_id": "string",
  "target_column": "string",
  "feature_columns": ["feature1", "feature2"],
  "architecture": "cnn_1d",
  "problem_type": "classification",
  "epochs": 100,
  "batch_size": 32,
  "learning_rate": 0.001
}
```

### Transfer Learning Request
```json
{
  "dataset_id": "string",
  "target_column": "string",
  "feature_columns": ["feature1", "feature2"],
  "base_model": "resnet50",
  "fine_tune_layers": 3,
  "epochs": 50
}
```

### Ensemble Request
```json
{
  "model_ids": ["model1", "model2", "model3"],
  "method": "voting",
  "weights": [0.4, 0.3, 0.3]
}
```

### Explanation Request
```json
{
  "model_id": "string",
  "method": "shap",
  "sample_indices": [0, 1, 2],
  "num_samples": 100
}
```

### Training Response
```json
{
  "job_id": "uuid",
  "status": "pending",
  "message": "Training job submitted successfully",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Job Status Response
```json
{
  "job_id": "uuid",
  "status": "running",
  "progress": 45.5,
  "message": "Training epoch 45/100",
  "started_at": "2024-01-01T00:00:00Z",
  "completed_at": null,
  "error": null
}
```

### Model Results Response
```json
{
  "model_id": "uuid",
  "model_name": "AutoML_abc123",
  "model_type": "automl",
  "metrics": {
    "accuracy": 0.95,
    "f1_score": 0.94
  },
  "artifacts_path": "./models/uuid",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Explanation Response
```json
{
  "model_id": "uuid",
  "method": "shap",
  "feature_importance": {
    "feature1": 0.45,
    "feature2": 0.30,
    "feature3": 0.15
  },
  "visualizations": {
    "summary_plot": "./visualizations/uuid/summary.png",
    "dependence_plot": "./visualizations/uuid/dependence.png"
  }
}
```

## Dependencies

The following packages have been added to `requirements.txt`:

```
# Machine Learning Framework
mlflow==2.9.2
torch==2.1.2
pytorch-lightning==2.1.3
autogluon==1.0.0
scikit-learn==1.3.2
shap==0.44.0
lime==0.2.0.1
numpy==1.24.3
scipy==1.11.4
```

## Installation

To install the ML framework dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

- `MLFLOW_TRACKING_URI`: MLflow tracking server URI (default: `file:./mlruns`)
- `DATABASE_URL`: Database connection string

### Directory Structure

The ML framework creates the following directories:
```
./mlruns/          # MLflow experiment tracking
./models/          # Model artifacts
./visualizations/  # Explanation visualizations
```

## Usage Examples

### 1. Train AutoML Model

```python
import requests

response = requests.post(
    "http://localhost:8001/api/ml/automl/train",
    json={
        "dataset_id": "dataset123",
        "target_column": "outcome",
        "feature_columns": ["gene1", "gene2", "gene3"],
        "problem_type": "classification",
        "time_limit": 600,
        "quality": "good_quality"
    }
)

job_id = response.json()["job_id"]
```

### 2. Check Training Status

```python
status_response = requests.get(
    f"http://localhost:8001/api/ml/jobs/{job_id}/status"
)

print(f"Status: {status_response.json()['status']}")
print(f"Progress: {status_response.json()['progress']}%")
```

### 3. Get Model Results

```python
results_response = requests.get(
    f"http://localhost:8001/api/ml/models/{model_id}/results"
)

metrics = results_response.json()["metrics"]
print(f"Accuracy: {metrics['accuracy']}")
```

### 4. Generate Model Explanations

```python
explain_response = requests.post(
    f"http://localhost:8001/api/ml/models/{model_id}/explain",
    json={
        "model_id": model_id,
        "method": "shap",
        "num_samples": 100
    }
)

feature_importance = explain_response.json()["feature_importance"]
```

### 5. Create Ensemble Model

```python
ensemble_response = requests.post(
    "http://localhost:8001/api/ml/ensemble/create",
    json={
        "model_ids": ["model1", "model2", "model3"],
        "method": "voting",
        "weights": [0.4, 0.3, 0.3]
    }
)
```

## Architecture

### Service Layer Architecture

```
FastAPI Router (ml_framework.py)
    ↓
ML Services (ml_services.py)
    ├── MLflowService (experiment tracking)
    ├── AutoMLService (AutoGluon)
    ├── DeepLearningService (PyTorch Lightning)
    ├── TransferLearningService (pre-trained models)
    ├── EnsembleService (model combination)
    └── ExplainabilityService (SHAP/LIME)
    ↓
Database Models (models.py)
    ├── MLModel
    └── TrainingJob
```

### Background Task Processing

All training operations run as background tasks using FastAPI's `BackgroundTasks`:
- Non-blocking API responses
- Immediate job ID return
- Status polling via `/jobs/{job_id}/status`
- Progress tracking in database

## Integration with Existing Modules

The ML framework integrates seamlessly with existing OmniScope modules:

1. **Data Harbor**: Uses uploaded datasets for training
2. **The Weaver**: Can be triggered from pipeline configurations
3. **The Crucible**: Enhanced with advanced ML capabilities
4. **The Insight Engine**: Uses trained models for biomarker analysis

## Testing

### Manual Testing

1. Start the application:
```bash
python main.py
```

2. Access API documentation:
```
http://localhost:8001/docs
```

3. Test endpoints using the interactive Swagger UI

### Automated Testing

Create test files in `tests/` directory:
```python
# tests/test_ml_framework.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_automl_train():
    response = client.post(
        "/api/ml/automl/train",
        json={
            "dataset_id": "test123",
            "target_column": "outcome",
            "feature_columns": ["f1", "f2"],
            "problem_type": "classification"
        }
    )
    assert response.status_code == 200
    assert "job_id" in response.json()
```

## Future Enhancements

### Phase 1 (Current Implementation)
- ✅ MLflow integration
- ✅ AutoML with AutoGluon
- ✅ Deep learning with PyTorch Lightning
- ✅ Transfer learning
- ✅ Ensemble methods
- ✅ Model explainability (SHAP/LIME)
- ✅ API endpoints

### Phase 2 (Planned)
- [ ] GPU acceleration support
- [ ] Distributed training with multiple GPUs
- [ ] Advanced neural architectures (GANs, VAEs)
- [ ] Hyperparameter tuning with Optuna
- [ ] Model serving with TorchServe
- [ ] A/B testing framework
- [ ] Model monitoring and drift detection

### Phase 3 (Future)
- [ ] Federated learning support
- [ ] AutoML for time-series
- [ ] Neural architecture search (NAS)
- [ ] Quantum machine learning integration
- [ ] Edge deployment optimization

## Troubleshooting

### Common Issues

1. **Import Error: No module named 'mlflow'**
   - Solution: Install dependencies with `pip install -r requirements.txt`

2. **Database Error: Table not found**
   - Solution: Restart application to trigger database migration

3. **Training Job Stuck in 'pending'**
   - Solution: Check background task execution and database connection

4. **MLflow Tracking URI Error**
   - Solution: Set `MLFLOW_TRACKING_URI` environment variable

## Performance Considerations

- **AutoML**: Time limit controls training duration
- **Deep Learning**: Batch size affects memory usage
- **Ensemble**: Number of base models impacts inference time
- **Explainability**: Sample size affects computation time

## Security Considerations

- Model artifacts stored in secure directory
- User authentication required for all endpoints
- Audit logging for all training operations
- Input validation on all requests

## Compliance

The ML framework supports:
- **Model Versioning**: Full audit trail via MLflow
- **Reproducibility**: All hyperparameters logged
- **Explainability**: SHAP/LIME for regulatory compliance
- **Data Privacy**: No data stored in model artifacts

## Support

For issues or questions:
1. Check API documentation at `/docs`
2. Review logs in `./mlruns/`
3. Check database for job status
4. Consult this documentation

## Conclusion

The Advanced ML Framework provides a comprehensive, production-ready machine learning platform for OmniScope AI. All subtasks (4.1-4.7) have been successfully implemented with proper API endpoints, database models, and service layer architecture.
