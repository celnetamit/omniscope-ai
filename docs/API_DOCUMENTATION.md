# OmniScope AI - API Documentation

## Table of Contents

1. [Authentication & Security](#authentication--security)
2. [Real-time Collaboration](#real-time-collaboration)
3. [Advanced ML Framework](#advanced-ml-framework)
4. [3D Visualization Engine](#3d-visualization-engine)
5. [External Database Integration Hub](#external-database-integration-hub)
6. [Automated Report Generator](#automated-report-generator)
7. [Advanced Statistical Analysis](#advanced-statistical-analysis)
8. [Distributed Processing Cluster](#distributed-processing-cluster)
9. [AI-Powered Literature Mining](#ai-powered-literature-mining)
10. [Custom Plugin System](#custom-plugin-system)
11. [Core Modules](#core-modules)
12. [Error Handling](#error-handling)
13. [Rate Limiting](#rate-limiting)

## Base URL

```
Development: http://localhost:8001
Production: https://api.omniscope.ai
```

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

---

## 1. Authentication & Security

### 1.1 User Registration

**Endpoint:** `POST /api/auth/register`

**Description:** Register a new user account

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "user_id": "uuid-string",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 1.2 User Login

**Endpoint:** `POST /api/auth/login`

**Description:** Authenticate user and receive JWT tokens

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "name": "John Doe",
    "roles": ["researcher"]
  }
}
```

### 1.3 Token Refresh

**Endpoint:** `POST /api/auth/refresh`

**Description:** Refresh access token using refresh token

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 1.4 Multi-Factor Authentication Setup

**Endpoint:** `POST /api/auth/mfa/setup`

**Description:** Initialize MFA for user account

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "backup_codes": [
    "12345678",
    "87654321",
    "11223344"
  ]
}
```

### 1.5 MFA Verification

**Endpoint:** `POST /api/auth/mfa/verify`

**Description:** Verify MFA token during login

**Request Body:**
```json
{
  "user_id": "uuid-string",
  "token": "123456"
}
```

**Response:** `200 OK`
```json
{
  "verified": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 1.6 Get User Permissions

**Endpoint:** `GET /api/auth/permissions`

**Description:** Get current user's permissions

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "user_id": "uuid-string",
  "roles": ["researcher", "analyst"],
  "permissions": [
    "data:read",
    "data:write",
    "pipeline:create",
    "model:train"
  ]
}
```

### 1.7 Logout

**Endpoint:** `POST /api/auth/logout`

**Description:** Invalidate current session

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

## 2. Real-time Collaboration

### 2.1 Create Workspace

**Endpoint:** `POST /api/collaboration/workspace/create`

**Description:** Create a new collaborative workspace

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Cancer Research Project",
  "description": "Multi-omics analysis workspace",
  "initial_pipeline": {}
}
```

**Response:** `201 Created`
```json
{
  "workspace_id": "uuid-string",
  "name": "Cancer Research Project",
  "owner_id": "uuid-string",
  "created_at": "2024-01-01T00:00:00Z",
  "websocket_url": "ws://localhost:8001/socket.io"
}
```

### 2.2 Get Workspace

**Endpoint:** `GET /api/collaboration/workspace/{workspace_id}`

**Description:** Retrieve workspace details

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "workspace_id": "uuid-string",
  "name": "Cancer Research Project",
  "owner_id": "uuid-string",
  "members": [
    {
      "user_id": "uuid-string",
      "name": "John Doe",
      "role": "owner",
      "online": true,
      "last_seen": "2024-01-01T00:00:00Z"
    }
  ],
  "pipeline_state": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 2.3 Invite User to Workspace

**Endpoint:** `POST /api/collaboration/workspace/{workspace_id}/invite`

**Description:** Invite a user to join workspace

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "email": "colleague@example.com",
  "role": "editor"
}
```

**Response:** `200 OK`
```json
{
  "invitation_id": "uuid-string",
  "workspace_id": "uuid-string",
  "invitee_email": "colleague@example.com",
  "role": "editor",
  "status": "pending"
}
```

### 2.4 Leave Workspace

**Endpoint:** `DELETE /api/collaboration/workspace/{workspace_id}/leave`

**Description:** Leave a workspace

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "message": "Successfully left workspace"
}
```

### 2.5 WebSocket Connection

**Endpoint:** `WS /socket.io`

**Description:** Establish WebSocket connection for real-time collaboration

**Connection:**
```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:8001', {
  auth: {
    token: 'your_jwt_token'
  }
});

// Join workspace
socket.emit('join_workspace', { workspace_id: 'uuid-string' });

// Listen for updates
socket.on('pipeline_update', (data) => {
  console.log('Pipeline updated:', data);
});

// Send updates
socket.emit('update_pipeline', {
  workspace_id: 'uuid-string',
  changes: { /* pipeline changes */ }
});
```

**Events:**
- `join_workspace` - Join a workspace room
- `leave_workspace` - Leave a workspace room
- `update_pipeline` - Broadcast pipeline changes
- `cursor_move` - Broadcast cursor position
- `user_joined` - Notification when user joins
- `user_left` - Notification when user leaves

## 3. Advanced ML Framework

### 3.1 AutoML Training

**Endpoint:** `POST /api/ml/automl/train`

**Description:** Start AutoML training with automatic algorithm selection

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "dataset_id": "uuid-string",
  "target_column": "disease_status",
  "feature_columns": ["gene1", "gene2", "gene3"],
  "task_type": "classification",
  "time_limit": 3600,
  "quality": "best_quality"
}
```

**Response:** `202 Accepted`
```json
{
  "job_id": "uuid-string",
  "status": "running",
  "estimated_completion": "2024-01-01T01:00:00Z",
  "status_url": "/api/ml/automl/status/uuid-string"
}
```

### 3.2 Deep Learning Training

**Endpoint:** `POST /api/ml/deep-learning/train`

**Description:** Train deep neural network model

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "dataset_id": "uuid-string",
  "architecture": "cnn_1d",
  "hyperparameters": {
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 100,
    "optimizer": "adam"
  },
  "target_column": "disease_status",
  "validation_split": 0.2
}
```

**Response:** `202 Accepted`
```json
{
  "job_id": "uuid-string",
  "status": "running",
  "progress_url": "/api/ml/deep-learning/progress/uuid-string"
}
```

### 3.3 Transfer Learning

**Endpoint:** `POST /api/ml/transfer-learning/apply`

**Description:** Apply transfer learning using pre-trained model

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "base_model_id": "uuid-string",
  "dataset_id": "uuid-string",
  "fine_tune_layers": 3,
  "epochs": 50,
  "learning_rate": 0.0001
}
```

**Response:** `202 Accepted`
```json
{
  "job_id": "uuid-string",
  "base_model": "BioBERT-v1.1",
  "status": "running"
}
```

### 3.4 Create Ensemble Model

**Endpoint:** `POST /api/ml/ensemble/create`

**Description:** Create ensemble from multiple models

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Cancer Prediction Ensemble",
  "base_models": ["model-id-1", "model-id-2", "model-id-3"],
  "method": "voting",
  "weights": [0.4, 0.3, 0.3]
}
```

**Response:** `201 Created`
```json
{
  "ensemble_id": "uuid-string",
  "name": "Cancer Prediction Ensemble",
  "base_models": 3,
  "method": "voting",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 3.5 Get Model Explanation

**Endpoint:** `GET /api/ml/models/{model_id}/explain`

**Description:** Get model interpretability metrics (SHAP, LIME)

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `method` - Explanation method (shap, lime)
- `sample_id` - Specific sample to explain (optional)

**Response:** `200 OK`
```json
{
  "model_id": "uuid-string",
  "method": "shap",
  "feature_importance": {
    "gene1": 0.45,
    "gene2": 0.32,
    "gene3": 0.23
  },
  "shap_values": [
    {
      "feature": "gene1",
      "value": 0.45,
      "base_value": 0.1
    }
  ],
  "visualization_url": "/api/ml/models/uuid-string/explain/plot"
}
```

### 3.6 Get Model Metrics

**Endpoint:** `GET /api/ml/models/{model_id}/metrics`

**Description:** Retrieve model performance metrics

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "model_id": "uuid-string",
  "metrics": {
    "accuracy": 0.92,
    "precision": 0.89,
    "recall": 0.94,
    "f1_score": 0.91,
    "auc_roc": 0.96
  },
  "confusion_matrix": [[45, 5], [3, 47]],
  "training_history": {
    "loss": [0.5, 0.3, 0.2],
    "val_loss": [0.6, 0.4, 0.3]
  }
}
```

### 3.7 List Models

**Endpoint:** `GET /api/ml/models`

**Description:** List all trained models

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `type` - Filter by model type (automl, deep_learning, ensemble)
- `limit` - Number of results (default: 50)
- `offset` - Pagination offset

**Response:** `200 OK`
```json
{
  "models": [
    {
      "model_id": "uuid-string",
      "name": "Cancer Classifier",
      "type": "automl",
      "accuracy": 0.92,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 10,
  "limit": 50,
  "offset": 0
}
```

## 4. 3D Visualization Engine

### 4.1 Load Protein Structure

**Endpoint:** `POST /api/visualization/protein/load`

**Description:** Load and parse protein structure from PDB

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "pdb_id": "1ABC",
  "source": "rcsb"
}
```

**Response:** `200 OK`
```json
{
  "structure_id": "uuid-string",
  "pdb_id": "1ABC",
  "atoms": 1234,
  "chains": ["A", "B"],
  "visualization_data": {
    "positions": [[0, 0, 0], [1, 1, 1]],
    "colors": [[255, 0, 0], [0, 255, 0]],
    "bonds": [[0, 1]]
  }
}
```

### 4.2 Generate Network Graph

**Endpoint:** `POST /api/visualization/network/generate`

**Description:** Generate 3D network graph from interaction data

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "nodes": [
    {"id": "gene1", "label": "TP53", "group": "tumor_suppressor"},
    {"id": "gene2", "label": "BRCA1", "group": "dna_repair"}
  ],
  "edges": [
    {"source": "gene1", "target": "gene2", "weight": 0.8}
  ],
  "layout": "force_directed"
}
```

**Response:** `200 OK`
```json
{
  "graph_id": "uuid-string",
  "nodes": 100,
  "edges": 250,
  "layout_data": {
    "positions": {
      "gene1": [0, 0, 0],
      "gene2": [1, 1, 1]
    }
  }
}
```

### 4.3 Dimensionality Reduction

**Endpoint:** `POST /api/visualization/dimensionality-reduction`

**Description:** Compute dimensionality reduction for visualization

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "dataset_id": "uuid-string",
  "method": "umap",
  "n_components": 3,
  "parameters": {
    "n_neighbors": 15,
    "min_dist": 0.1
  }
}
```

**Response:** `200 OK`
```json
{
  "reduction_id": "uuid-string",
  "method": "umap",
  "components": 3,
  "data": [
    {"id": "sample1", "x": 0.1, "y": 0.2, "z": 0.3, "label": "healthy"},
    {"id": "sample2", "x": 0.4, "y": 0.5, "z": 0.6, "label": "disease"}
  ],
  "variance_explained": [0.45, 0.32, 0.15]
}
```

### 4.4 Export Visualization

**Endpoint:** `GET /api/visualization/{visualization_id}/export`

**Description:** Export visualization in various formats

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `format` - Export format (png, svg, html)
- `width` - Image width in pixels (default: 1920)
- `height` - Image height in pixels (default: 1080)

**Response:** `200 OK`
```json
{
  "export_id": "uuid-string",
  "format": "png",
  "download_url": "/api/visualization/downloads/uuid-string.png",
  "expires_at": "2024-01-02T00:00:00Z"
}
```

## 5. External Database Integration Hub

### 5.1 Query Gene Information

**Endpoint:** `GET /api/integration/gene/{gene_id}`

**Description:** Retrieve gene annotations from multiple databases

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `databases` - Comma-separated list (ncbi, uniprot, kegg)

**Response:** `200 OK`
```json
{
  "gene_id": "TP53",
  "annotations": {
    "ncbi": {
      "gene_id": "7157",
      "symbol": "TP53",
      "name": "tumor protein p53",
      "description": "Acts as a tumor suppressor...",
      "chromosome": "17",
      "location": "17p13.1"
    },
    "uniprot": {
      "accession": "P04637",
      "protein_name": "Cellular tumor antigen p53",
      "function": "Acts as a tumor suppressor..."
    },
    "kegg": {
      "pathways": ["hsa04115", "hsa04110"],
      "pathway_names": ["p53 signaling pathway", "Cell cycle"]
    }
  },
  "cached": false,
  "retrieved_at": "2024-01-01T00:00:00Z"
}
```

### 5.2 Batch Query

**Endpoint:** `POST /api/integration/batch-query`

**Description:** Query multiple identifiers simultaneously

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "identifiers": ["TP53", "BRCA1", "EGFR"],
  "databases": ["ncbi", "uniprot"],
  "query_type": "gene"
}
```

**Response:** `202 Accepted`
```json
{
  "batch_id": "uuid-string",
  "total_queries": 3,
  "status": "processing",
  "results_url": "/api/integration/batch-query/uuid-string/results"
}
```

### 5.3 Get Pathway Information

**Endpoint:** `GET /api/integration/pathway/{pathway_id}`

**Description:** Retrieve pathway details from KEGG

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "pathway_id": "hsa04115",
  "name": "p53 signaling pathway",
  "description": "The p53 tumor suppressor protein...",
  "genes": ["TP53", "MDM2", "CDKN1A"],
  "compounds": ["C00002", "C00008"],
  "image_url": "https://www.kegg.jp/pathway/hsa04115.png"
}
```

### 5.4 Get Protein Information

**Endpoint:** `GET /api/integration/protein/{protein_id}`

**Description:** Retrieve protein annotations from UniProt

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "accession": "P04637",
  "protein_name": "Cellular tumor antigen p53",
  "gene_name": "TP53",
  "organism": "Homo sapiens",
  "function": "Acts as a tumor suppressor...",
  "subcellular_location": ["Nucleus", "Cytoplasm"],
  "domains": [
    {"name": "DNA-binding", "start": 102, "end": 292}
  ],
  "interactions": ["MDM2", "MDM4"]
}
```

### 5.5 Search Literature

**Endpoint:** `GET /api/integration/literature/search`

**Description:** Search PubMed for relevant papers

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `query` - Search query
- `limit` - Number of results (default: 10)
- `sort` - Sort by (relevance, date, citations)

**Response:** `200 OK`
```json
{
  "query": "TP53 cancer",
  "total_results": 15234,
  "papers": [
    {
      "pmid": "12345678",
      "title": "Role of TP53 in cancer progression",
      "authors": ["Smith J", "Doe A"],
      "journal": "Nature",
      "year": 2023,
      "abstract": "TP53 is a critical tumor suppressor...",
      "citations": 145
    }
  ]
}
```

## 6. Automated Report Generator

### 6.1 Generate Report

**Endpoint:** `POST /api/reports/generate`

**Description:** Generate publication-ready report

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Multi-Omics Analysis of Cancer Biomarkers",
  "template_id": "scientific_report",
  "format": "pdf",
  "sections": {
    "include_methods": true,
    "include_results": true,
    "include_discussion": true
  },
  "data_sources": {
    "model_id": "uuid-string",
    "dataset_id": "uuid-string",
    "analysis_ids": ["uuid-1", "uuid-2"]
  },
  "citation_style": "nature"
}
```

**Response:** `202 Accepted`
```json
{
  "report_id": "uuid-string",
  "status": "generating",
  "estimated_completion": "2024-01-01T00:00:30Z",
  "status_url": "/api/reports/uuid-string/status"
}
```

### 6.2 Download Report

**Endpoint:** `GET /api/reports/{report_id}/download`

**Description:** Download generated report

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK` (Binary file)

### 6.3 List Templates

**Endpoint:** `GET /api/reports/templates`

**Description:** Get available report templates

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "templates": [
    {
      "template_id": "scientific_report",
      "name": "Scientific Report",
      "description": "Standard scientific publication format",
      "sections": ["abstract", "introduction", "methods", "results", "discussion"],
      "formats": ["pdf", "docx", "latex"]
    },
    {
      "template_id": "executive_summary",
      "name": "Executive Summary",
      "description": "Brief overview for stakeholders",
      "sections": ["summary", "key_findings", "recommendations"],
      "formats": ["pdf", "docx"]
    }
  ]
}
```

### 6.4 Create Custom Template

**Endpoint:** `POST /api/reports/templates/custom`

**Description:** Create custom report template

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Custom Analysis Report",
  "sections": [
    {
      "title": "Executive Summary",
      "content_type": "text",
      "template": "{{ summary }}"
    },
    {
      "title": "Results",
      "content_type": "figures",
      "template": "{{ figures }}"
    }
  ],
  "citation_style": "apa",
  "format": "pdf"
}
```

**Response:** `201 Created`
```json
{
  "template_id": "uuid-string",
  "name": "Custom Analysis Report",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 6.5 Get Report Status

**Endpoint:** `GET /api/reports/{report_id}/status`

**Description:** Check report generation status

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "report_id": "uuid-string",
  "status": "completed",
  "progress": 100,
  "download_url": "/api/reports/uuid-string/download",
  "format": "pdf",
  "file_size": 2457600,
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:00:25Z"
}
```

## 7. Advanced Statistical Analysis

### 7.1 Survival Analysis

**Endpoint:** `POST /api/statistics/survival-analysis`

**Description:** Perform survival analysis (Kaplan-Meier, Cox regression)

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "dataset_id": "uuid-string",
  "method": "cox",
  "time_column": "survival_time",
  "event_column": "death_event",
  "covariates": ["age", "treatment", "gene_expression"],
  "groups": ["treatment"]
}
```

**Response:** `200 OK`
```json
{
  "analysis_id": "uuid-string",
  "method": "cox",
  "results": {
    "hazard_ratios": {
      "age": 1.05,
      "treatment": 0.65,
      "gene_expression": 1.23
    },
    "p_values": {
      "age": 0.001,
      "treatment": 0.023,
      "gene_expression": 0.045
    },
    "confidence_intervals": {
      "age": [1.02, 1.08],
      "treatment": [0.45, 0.92]
    }
  },
  "kaplan_meier_curves": {
    "treatment_A": [[0, 1.0], [30, 0.8], [60, 0.6]],
    "treatment_B": [[0, 1.0], [30, 0.9], [60, 0.8]]
  },
  "visualization_url": "/api/statistics/survival-analysis/uuid-string/plot"
}
```

### 7.2 Time-Series Analysis

**Endpoint:** `POST /api/statistics/time-series`

**Description:** Perform time-series analysis and forecasting

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "dataset_id": "uuid-string",
  "method": "prophet",
  "time_column": "date",
  "value_column": "expression_level",
  "forecast_periods": 30,
  "seasonality": "auto"
}
```

**Response:** `200 OK`
```json
{
  "analysis_id": "uuid-string",
  "method": "prophet",
  "forecast": [
    {"date": "2024-01-01", "predicted": 5.2, "lower": 4.8, "upper": 5.6},
    {"date": "2024-01-02", "predicted": 5.3, "lower": 4.9, "upper": 5.7}
  ],
  "metrics": {
    "mae": 0.15,
    "rmse": 0.23,
    "mape": 2.8
  },
  "components": {
    "trend": "increasing",
    "seasonality": "weekly"
  }
}
```

### 7.3 Multi-Omics Integration

**Endpoint:** `POST /api/statistics/multi-omics-integration`

**Description:** Integrate multiple omics datasets

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "method": "mofa",
  "omics_layers": [
    {
      "name": "genomics",
      "dataset_id": "uuid-1",
      "type": "genomics"
    },
    {
      "name": "proteomics",
      "dataset_id": "uuid-2",
      "type": "proteomics"
    }
  ],
  "n_factors": 10,
  "convergence_mode": "fast"
}
```

**Response:** `202 Accepted`
```json
{
  "job_id": "uuid-string",
  "status": "running",
  "estimated_completion": "2024-01-01T00:10:00Z"
}
```

### 7.4 Bayesian Inference

**Endpoint:** `POST /api/statistics/bayesian-inference`

**Description:** Perform Bayesian statistical inference

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "dataset_id": "uuid-string",
  "model_type": "linear_regression",
  "target": "disease_risk",
  "predictors": ["gene1", "gene2", "age"],
  "prior_distributions": {
    "gene1": {"type": "normal", "mu": 0, "sigma": 1},
    "gene2": {"type": "normal", "mu": 0, "sigma": 1}
  },
  "sampling_method": "mcmc",
  "n_samples": 2000
}
```

**Response:** `202 Accepted`
```json
{
  "job_id": "uuid-string",
  "status": "sampling",
  "progress_url": "/api/statistics/bayesian-inference/uuid-string/progress"
}
```

### 7.5 Power Analysis

**Endpoint:** `POST /api/statistics/power-analysis`

**Description:** Calculate statistical power and sample size

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "test_type": "t_test",
  "effect_size": 0.5,
  "alpha": 0.05,
  "power": 0.8,
  "calculate": "sample_size"
}
```

**Response:** `200 OK`
```json
{
  "test_type": "t_test",
  "effect_size": 0.5,
  "alpha": 0.05,
  "power": 0.8,
  "required_sample_size": 64,
  "per_group": 32,
  "recommendations": "To detect an effect size of 0.5 with 80% power at α=0.05, you need 32 samples per group."
}
```

## 8. Distributed Processing Cluster

### 8.1 Submit Processing Job

**Endpoint:** `POST /api/processing/submit-job`

**Description:** Submit job for distributed processing

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "job_name": "Large Dataset Analysis",
  "job_type": "map_reduce",
  "dataset_id": "uuid-string",
  "operation": "normalize",
  "parameters": {
    "method": "z_score",
    "axis": 0
  },
  "n_workers": 4,
  "memory_per_worker": "4GB",
  "priority": "high"
}
```

**Response:** `202 Accepted`
```json
{
  "job_id": "uuid-string",
  "status": "queued",
  "position_in_queue": 2,
  "estimated_start": "2024-01-01T00:05:00Z",
  "status_url": "/api/processing/job/uuid-string/status"
}
```

### 8.2 Get Job Status

**Endpoint:** `GET /api/processing/job/{job_id}/status`

**Description:** Check processing job status

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "job_id": "uuid-string",
  "status": "running",
  "progress": 65,
  "tasks_completed": 13,
  "tasks_total": 20,
  "workers_active": 4,
  "started_at": "2024-01-01T00:00:00Z",
  "estimated_completion": "2024-01-01T00:15:00Z",
  "resource_usage": {
    "cpu_percent": 75,
    "memory_gb": 12.5
  }
}
```

### 8.3 Get Cluster Status

**Endpoint:** `GET /api/processing/cluster/status`

**Description:** Get distributed cluster status

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "cluster_id": "uuid-string",
  "status": "healthy",
  "scheduler": {
    "address": "tcp://scheduler:8786",
    "status": "running"
  },
  "workers": [
    {
      "worker_id": "worker-1",
      "status": "busy",
      "cpu_cores": 8,
      "memory_gb": 16,
      "tasks_running": 3
    },
    {
      "worker_id": "worker-2",
      "status": "idle",
      "cpu_cores": 8,
      "memory_gb": 16,
      "tasks_running": 0
    }
  ],
  "total_workers": 4,
  "active_jobs": 2,
  "queued_jobs": 1
}
```

### 8.4 Scale Cluster

**Endpoint:** `POST /api/processing/cluster/scale`

**Description:** Scale cluster workers up or down

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "target_workers": 8,
  "worker_spec": {
    "cpu_cores": 8,
    "memory_gb": 16
  }
}
```

**Response:** `202 Accepted`
```json
{
  "message": "Cluster scaling initiated",
  "current_workers": 4,
  "target_workers": 8,
  "estimated_completion": "2024-01-01T00:02:00Z"
}
```

### 8.5 Cancel Job

**Endpoint:** `DELETE /api/processing/job/{job_id}`

**Description:** Cancel running or queued job

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "job_id": "uuid-string",
  "status": "cancelled",
  "message": "Job cancelled successfully"
}
```

## 9. AI-Powered Literature Mining

### 9.1 Search Papers

**Endpoint:** `POST /api/literature/search`

**Description:** Search for relevant research papers

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "query": "TP53 mutations in breast cancer",
  "filters": {
    "year_min": 2020,
    "year_max": 2024,
    "journal": ["Nature", "Science", "Cell"]
  },
  "limit": 20,
  "sort_by": "relevance"
}
```

**Response:** `200 OK`
```json
{
  "query": "TP53 mutations in breast cancer",
  "total_results": 1234,
  "papers": [
    {
      "pmid": "12345678",
      "title": "TP53 mutations drive breast cancer progression",
      "authors": ["Smith J", "Doe A"],
      "journal": "Nature",
      "year": 2023,
      "citations": 145,
      "relevance_score": 0.95,
      "abstract": "TP53 is frequently mutated..."
    }
  ]
}
```

### 9.2 Get Paper Details

**Endpoint:** `GET /api/literature/paper/{pmid}`

**Description:** Get detailed paper information

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "pmid": "12345678",
  "title": "TP53 mutations drive breast cancer progression",
  "authors": ["Smith J", "Doe A", "Johnson B"],
  "journal": "Nature",
  "year": 2023,
  "volume": "615",
  "pages": "123-130",
  "doi": "10.1038/nature12345",
  "abstract": "TP53 is frequently mutated in breast cancer...",
  "citations": 145,
  "references": ["11111111", "22222222"],
  "mesh_terms": ["Breast Neoplasms", "Tumor Suppressor Protein p53", "Mutation"]
}
```

### 9.3 Summarize Paper

**Endpoint:** `POST /api/literature/summarize`

**Description:** Generate AI summary of research paper

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "pmid": "12345678",
  "summary_length": "medium"
}
```

**Response:** `200 OK`
```json
{
  "pmid": "12345678",
  "summary": "This study investigates the role of TP53 mutations in breast cancer progression. The researchers found that specific TP53 mutations correlate with increased tumor aggressiveness and poor patient outcomes. The findings suggest TP53 status could serve as a prognostic biomarker.",
  "key_findings": [
    "TP53 mutations present in 65% of aggressive tumors",
    "Specific mutation types correlate with treatment resistance",
    "TP53 status predicts patient survival"
  ],
  "methodology": "Genomic sequencing of 500 breast cancer samples",
  "generated_at": "2024-01-01T00:00:00Z"
}
```

### 9.4 Extract Relationships

**Endpoint:** `POST /api/literature/extract-relationships`

**Description:** Extract biological relationships from papers

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "pmids": ["12345678", "87654321"],
  "entity_types": ["gene", "disease", "drug"]
}
```

**Response:** `200 OK`
```json
{
  "relationships": [
    {
      "source": {"text": "TP53", "type": "gene"},
      "target": {"text": "breast cancer", "type": "disease"},
      "relationship": "associated_with",
      "confidence": 0.92,
      "evidence": "TP53 mutations are frequently found in breast cancer",
      "pmid": "12345678"
    },
    {
      "source": {"text": "TP53", "type": "gene"},
      "target": {"text": "MDM2", "type": "gene"},
      "relationship": "interacts_with",
      "confidence": 0.88,
      "evidence": "MDM2 regulates TP53 activity",
      "pmid": "12345678"
    }
  ],
  "total_relationships": 45
}
```

### 9.5 Natural Language Query

**Endpoint:** `POST /api/literature/query`

**Description:** Ask questions about literature corpus

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "question": "What is the role of TP53 in cancer?",
  "context": ["12345678", "87654321"],
  "max_results": 5
}
```

**Response:** `200 OK`
```json
{
  "question": "What is the role of TP53 in cancer?",
  "answer": "TP53 acts as a tumor suppressor gene that regulates cell cycle and apoptosis. When mutated, it loses its protective function, leading to uncontrolled cell growth and cancer development.",
  "confidence": 0.89,
  "supporting_papers": [
    {
      "pmid": "12345678",
      "relevance": 0.95,
      "excerpt": "TP53 is a critical tumor suppressor..."
    }
  ],
  "generated_at": "2024-01-01T00:00:00Z"
}
```

### 9.6 Subscribe to Topic

**Endpoint:** `POST /api/literature/notifications/subscribe`

**Description:** Subscribe to notifications for new papers

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "topic": "TP53 breast cancer",
  "frequency": "weekly",
  "email": "user@example.com"
}
```

**Response:** `201 Created`
```json
{
  "subscription_id": "uuid-string",
  "topic": "TP53 breast cancer",
  "frequency": "weekly",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 9.7 Get Knowledge Graph

**Endpoint:** `GET /api/literature/knowledge-graph`

**Description:** Retrieve knowledge graph of entities and relationships

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `entity` - Central entity (e.g., "TP53")
- `depth` - Graph depth (default: 2)
- `limit` - Max nodes (default: 100)

**Response:** `200 OK`
```json
{
  "nodes": [
    {"id": "TP53", "type": "gene", "label": "TP53"},
    {"id": "breast_cancer", "type": "disease", "label": "Breast Cancer"}
  ],
  "edges": [
    {
      "source": "TP53",
      "target": "breast_cancer",
      "type": "associated_with",
      "weight": 0.92
    }
  ],
  "statistics": {
    "total_nodes": 45,
    "total_edges": 123,
    "entity_types": {"gene": 20, "disease": 15, "drug": 10}
  }
}
```

## 10. Custom Plugin System

### 10.1 List Marketplace Plugins

**Endpoint:** `GET /api/plugins/marketplace`

**Description:** Browse available plugins in marketplace

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `category` - Filter by category (data_import, analysis, visualization)
- `search` - Search query
- `sort` - Sort by (popularity, rating, recent)

**Response:** `200 OK`
```json
{
  "plugins": [
    {
      "plugin_id": "uuid-string",
      "name": "Advanced Normalization",
      "version": "1.2.0",
      "author": "Research Lab",
      "description": "Advanced data normalization methods",
      "category": "preprocessing",
      "rating": 4.5,
      "downloads": 1234,
      "price": "free",
      "languages": ["python"]
    }
  ],
  "total": 45,
  "categories": ["data_import", "preprocessing", "analysis", "visualization", "export"]
}
```

### 10.2 Install Plugin

**Endpoint:** `POST /api/plugins/install`

**Description:** Install plugin from marketplace

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "plugin_id": "uuid-string",
  "version": "1.2.0"
}
```

**Response:** `202 Accepted`
```json
{
  "installation_id": "uuid-string",
  "plugin_id": "uuid-string",
  "status": "installing",
  "progress_url": "/api/plugins/installation/uuid-string/status"
}
```

### 10.3 Enable Plugin

**Endpoint:** `POST /api/plugins/{plugin_id}/enable`

**Description:** Enable installed plugin

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "plugin_id": "uuid-string",
  "name": "Advanced Normalization",
  "status": "enabled",
  "enabled_at": "2024-01-01T00:00:00Z"
}
```

### 10.4 Disable Plugin

**Endpoint:** `POST /api/plugins/{plugin_id}/disable`

**Description:** Disable active plugin

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "plugin_id": "uuid-string",
  "status": "disabled",
  "message": "Plugin disabled successfully"
}
```

### 10.5 Uninstall Plugin

**Endpoint:** `DELETE /api/plugins/{plugin_id}/uninstall`

**Description:** Uninstall plugin

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "plugin_id": "uuid-string",
  "status": "uninstalled",
  "message": "Plugin uninstalled successfully"
}
```

### 10.6 Execute Plugin

**Endpoint:** `POST /api/plugins/{plugin_id}/execute`

**Description:** Execute plugin with input data

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "input_data": {
    "dataset_id": "uuid-string",
    "parameters": {
      "method": "quantile",
      "axis": 0
    }
  }
}
```

**Response:** `202 Accepted`
```json
{
  "execution_id": "uuid-string",
  "plugin_id": "uuid-string",
  "status": "running",
  "started_at": "2024-01-01T00:00:00Z",
  "results_url": "/api/plugins/execution/uuid-string/results"
}
```

### 10.7 Get Plugin Configuration

**Endpoint:** `GET /api/plugins/{plugin_id}/config`

**Description:** Get plugin configuration schema

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "plugin_id": "uuid-string",
  "name": "Advanced Normalization",
  "config_schema": {
    "method": {
      "type": "select",
      "options": ["z_score", "min_max", "quantile"],
      "default": "z_score",
      "description": "Normalization method"
    },
    "axis": {
      "type": "number",
      "default": 0,
      "description": "Axis to normalize (0=rows, 1=columns)"
    }
  }
}
```

### 10.8 Update Plugin

**Endpoint:** `POST /api/plugins/{plugin_id}/update`

**Description:** Update plugin to latest version

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "version": "1.3.0"
}
```

**Response:** `202 Accepted`
```json
{
  "plugin_id": "uuid-string",
  "current_version": "1.2.0",
  "target_version": "1.3.0",
  "status": "updating"
}
```

### 10.9 List Installed Plugins

**Endpoint:** `GET /api/plugins/installed`

**Description:** List all installed plugins

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "plugins": [
    {
      "plugin_id": "uuid-string",
      "name": "Advanced Normalization",
      "version": "1.2.0",
      "status": "enabled",
      "installed_at": "2024-01-01T00:00:00Z",
      "last_used": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 5
}
```

## 11. Core Modules

### 11.1 Data Harbor - Upload File

**Endpoint:** `POST /api/data/upload`

**Description:** Upload CSV file for analysis

**Headers:** `Authorization: Bearer <token>`

**Request:** Multipart form data
- `file` - CSV file (max 10MB)
- `name` - Dataset name
- `description` - Dataset description (optional)

**Response:** `201 Created`
```json
{
  "file_id": "uuid-string",
  "name": "cancer_data.csv",
  "size": 1024000,
  "rows": 500,
  "columns": 50,
  "column_names": ["gene1", "gene2", "disease_status"],
  "uploaded_at": "2024-01-01T00:00:00Z"
}
```

### 11.2 Data Harbor - Get Report

**Endpoint:** `GET /api/data/{file_id}/report`

**Description:** Get analysis report for uploaded file

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "file_id": "uuid-string",
  "statistics": {
    "rows": 500,
    "columns": 50,
    "missing_values": 25,
    "numeric_columns": 48,
    "categorical_columns": 2
  },
  "column_stats": {
    "gene1": {
      "mean": 5.2,
      "std": 1.3,
      "min": 2.1,
      "max": 8.9
    }
  }
}
```

### 11.3 The Weaver - Save Pipeline

**Endpoint:** `POST /api/pipelines/save`

**Description:** Save or update analysis pipeline

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "pipeline_id": "uuid-string",
  "project_id": "uuid-string",
  "name": "Cancer Analysis Pipeline",
  "nodes": [
    {
      "id": "node1",
      "type": "data_import",
      "config": {"file_id": "uuid-string"}
    }
  ],
  "edges": [
    {"source": "node1", "target": "node2"}
  ]
}
```

**Response:** `200 OK`
```json
{
  "pipeline_id": "uuid-string",
  "name": "Cancer Analysis Pipeline",
  "saved_at": "2024-01-01T00:00:00Z"
}
```

### 11.4 The Crucible - Train Model

**Endpoint:** `POST /api/models/train`

**Description:** Start model training

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "dataset_id": "uuid-string",
  "model_type": "random_forest",
  "target_column": "disease_status",
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 10
  }
}
```

**Response:** `202 Accepted`
```json
{
  "job_id": "uuid-string",
  "status": "training",
  "status_url": "/api/models/uuid-string/status"
}
```

### 11.5 The Insight Engine - Get Biomarkers

**Endpoint:** `GET /api/results/{model_id}/biomarkers`

**Description:** Get identified biomarkers from model

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "model_id": "uuid-string",
  "biomarkers": [
    {
      "gene_id": "TP53",
      "importance": 0.45,
      "p_value": 0.001,
      "fold_change": 2.3
    }
  ],
  "total": 25
}
```

## 12. Error Handling

All API errors follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "specific_field",
      "reason": "Detailed reason"
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req_123456"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_INPUT` | 400 | Invalid request data |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

## 13. Rate Limiting

API requests are rate-limited per user:

- **Standard Users**: 100 requests/minute
- **Premium Users**: 1000 requests/minute
- **Enterprise**: Custom limits

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

When rate limit is exceeded:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "retry_after": 60
  }
}
```

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `limit` - Number of results per page (default: 50, max: 100)
- `offset` - Number of results to skip
- `cursor` - Cursor-based pagination token (alternative to offset)

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "total": 1000,
    "limit": 50,
    "offset": 0,
    "next_cursor": "eyJpZCI6MTAwfQ=="
  }
}
```

## Webhooks

Configure webhooks to receive real-time notifications:

**Endpoint:** `POST /api/webhooks/create`

**Request Body:**
```json
{
  "url": "https://your-server.com/webhook",
  "events": ["model.training.completed", "report.generated"],
  "secret": "your_webhook_secret"
}
```

**Webhook Payload:**
```json
{
  "event": "model.training.completed",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "model_id": "uuid-string",
    "accuracy": 0.92
  },
  "signature": "sha256=..."
}
```

---

## Support

For API support:
- Documentation: https://docs.omniscope.ai
- Email: api-support@omniscope.ai
- Status Page: https://status.omniscope.ai
