# ML Framework Quick Start Guide

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the application:
```bash
python main.py
```

3. Access API documentation:
```
http://localhost:8001/docs
```

## Quick Examples

### 1. Train an AutoML Model

**Request:**
```bash
curl -X POST "http://localhost:8001/api/ml/automl/train" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "my_dataset",
    "target_column": "outcome",
    "feature_columns": ["gene1", "gene2", "gene3"],
    "problem_type": "classification",
    "time_limit": 600,
    "quality": "good_quality"
  }'
```

**Response:**
```json
{
  "job_id": "abc-123-def-456",
  "status": "pending",
  "message": "AutoML training job submitted successfully",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 2. Check Training Status

**Request:**
```bash
curl "http://localhost:8001/api/ml/jobs/abc-123-def-456/status"
```

**Response:**
```json
{
  "job_id": "abc-123-def-456",
  "status": "running",
  "progress": 65.5,
  "message": "Training in progress",
  "started_at": "2024-01-01T00:00:00Z",
  "completed_at": null,
  "error": null
}
```

### 3. Train a Deep Learning Model

**Request:**
```bash
curl -X POST "http://localhost:8001/api/ml/deep-learning/train" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "my_dataset",
    "target_column": "outcome",
    "feature_columns": ["gene1", "gene2", "gene3"],
    "architecture": "cnn_1d",
    "problem_type": "classification",
    "epochs": 100,
    "batch_size": 32,
    "learning_rate": 0.001
  }'
```

### 4. Create an Ensemble Model

**Request:**
```bash
curl -X POST "http://localhost:8001/api/ml/ensemble/create" \
  -H "Content-Type: application/json" \
  -d '{
    "model_ids": ["model1", "model2", "model3"],
    "method": "voting",
    "weights": [0.4, 0.3, 0.3]
  }'
```

### 5. Explain a Model

**Request:**
```bash
curl -X POST "http://localhost:8001/api/ml/models/model-id/explain" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "model-id",
    "method": "shap",
    "num_samples": 100
  }'
```

**Response:**
```json
{
  "model_id": "model-id",
  "method": "shap",
  "feature_importance": {
    "gene1": 0.45,
    "gene2": 0.30,
    "gene3": 0.15
  },
  "visualizations": {
    "summary_plot": "./visualizations/model-id/summary.png"
  }
}
```

### 6. List All Models

**Request:**
```bash
curl "http://localhost:8001/api/ml/models/list?skip=0&limit=10"
```

### 7. Get Model Results

**Request:**
```bash
curl "http://localhost:8001/api/ml/models/model-id/results"
```

**Response:**
```json
{
  "model_id": "model-id",
  "model_name": "AutoML_abc123",
  "model_type": "automl",
  "metrics": {
    "accuracy": 0.95,
    "f1_score": 0.94
  },
  "artifacts_path": "./models/model-id",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Available Endpoints

### Training
- `POST /api/ml/automl/train` - AutoML training
- `POST /api/ml/deep-learning/train` - Deep learning training
- `POST /api/ml/transfer-learning/train` - Transfer learning
- `POST /api/ml/ensemble/create` - Ensemble creation

### Management
- `GET /api/ml/jobs/{job_id}/status` - Job status
- `GET /api/ml/models/{model_id}/results` - Model results
- `GET /api/ml/models/list` - List models
- `DELETE /api/ml/models/{model_id}` - Delete model

### Explainability
- `POST /api/ml/models/{model_id}/explain` - Generate explanations

## Architecture Types

### Deep Learning
- `cnn_1d` - 1D Convolutional Neural Network
- `cnn_2d` - 2D Convolutional Neural Network
- `rnn` - Recurrent Neural Network
- `lstm` - Long Short-Term Memory
- `transformer` - Transformer-based model

### Ensemble Methods
- `voting` - Voting ensemble
- `stacking` - Stacking ensemble
- `blending` - Blending ensemble

### Explainability Methods
- `shap` - SHAP values
- `lime` - LIME explanations

## Configuration

### Environment Variables
```bash
export MLFLOW_TRACKING_URI="file:./mlruns"
export DATABASE_URL="sqlite:///./db/backend.db"
```

### Quality Presets (AutoML)
- `best_quality` - Highest quality, longest time
- `high_quality` - High quality, moderate time
- `good_quality` - Good balance (default)
- `medium_quality` - Faster training, lower quality

## Python Client Example

```python
import requests
import time

# Base URL
BASE_URL = "http://localhost:8001/api/ml"

# 1. Start training
response = requests.post(
    f"{BASE_URL}/automl/train",
    json={
        "dataset_id": "my_dataset",
        "target_column": "outcome",
        "feature_columns": ["gene1", "gene2", "gene3"],
        "problem_type": "classification",
        "time_limit": 600,
        "quality": "good_quality"
    }
)

job_id = response.json()["job_id"]
print(f"Job ID: {job_id}")

# 2. Poll for status
while True:
    status_response = requests.get(f"{BASE_URL}/jobs/{job_id}/status")
    status_data = status_response.json()
    
    print(f"Status: {status_data['status']} - Progress: {status_data['progress']}%")
    
    if status_data["status"] in ["completed", "failed"]:
        break
    
    time.sleep(5)

# 3. Get results
if status_data["status"] == "completed":
    model_id = status_data.get("model_id")
    results_response = requests.get(f"{BASE_URL}/models/{model_id}/results")
    results = results_response.json()
    
    print(f"Model: {results['model_name']}")
    print(f"Metrics: {results['metrics']}")
    
    # 4. Generate explanations
    explain_response = requests.post(
        f"{BASE_URL}/models/{model_id}/explain",
        json={
            "model_id": model_id,
            "method": "shap",
            "num_samples": 100
        }
    )
    
    explanations = explain_response.json()
    print(f"Feature Importance: {explanations['feature_importance']}")
```

## Troubleshooting

### Issue: Module not found errors
**Solution:** Install dependencies with `pip install -r requirements.txt`

### Issue: Training job stuck in pending
**Solution:** Check database connection and background task execution

### Issue: MLflow tracking error
**Solution:** Ensure `./mlruns` directory exists and is writable

### Issue: Out of memory during training
**Solution:** Reduce batch size or use smaller model architecture

## Next Steps

1. Explore the interactive API documentation at `/docs`
2. Review the full implementation guide in `ML_FRAMEWORK_IMPLEMENTATION.md`
3. Check the requirements document for detailed specifications
4. Test different model architectures and ensemble methods

## Support

For detailed documentation, see:
- `ML_FRAMEWORK_IMPLEMENTATION.md` - Full implementation details
- `.kiro/specs/advanced-features-upgrade/design.md` - Design specifications
- `.kiro/specs/advanced-features-upgrade/requirements.md` - Requirements
- `http://localhost:8001/docs` - Interactive API documentation
