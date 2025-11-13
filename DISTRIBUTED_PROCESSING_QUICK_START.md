# Distributed Processing Cluster - Quick Start Guide

## Overview

The Distributed Processing Cluster provides cloud-scale data processing capabilities using Dask for parallel and distributed computing. This module enables processing of large datasets that exceed single-machine memory limits.

## Features

### 1. Dask Cluster Management
- **Scheduler**: Coordinates distributed tasks across workers
- **Worker Pool**: Auto-scaling worker nodes
- **Dashboard**: Real-time monitoring at http://localhost:8787
- **Resource Management**: CPU and memory allocation

### 2. Data Partitioning
- **Automatic Chunking**: Splits large datasets efficiently
- **Partition Optimization**: Balances partition sizes
- **Distributed Loading**: Loads data from multiple sources
- **Format Support**: CSV, Parquet, JSON

### 3. Fault Tolerance
- **Automatic Retry**: Failed tasks retry automatically
- **Worker Failure Detection**: Monitors worker health
- **Task Rescheduling**: Moves tasks to healthy workers
- **Checkpointing**: Saves job state for recovery

### 4. Progress Monitoring
- **Real-time Tracking**: Live progress updates
- **Completion Percentage**: Accurate progress calculation
- **ETA Estimation**: Predicts completion time
- **Visualization**: Progress charts and metrics

### 5. Resource Management
- **CPU Allocation**: Manages core distribution
- **Memory Limits**: Enforces memory constraints
- **Usage Monitoring**: Tracks resource consumption
- **Optimization**: Recommends scaling actions

### 6. Job Queue with Priority
- **Priority Levels**: LOW, NORMAL, HIGH, CRITICAL
- **Queue Management**: FIFO with priority override
- **Concurrent Execution**: Multiple jobs in parallel
- **Job Cancellation**: Stop running or queued jobs

## API Endpoints

### Cluster Management

#### Start Cluster
```bash
POST /api/processing/cluster/start
```

Response:
```json
{
  "message": "Cluster started successfully",
  "cluster_info": {
    "status": "running",
    "scheduler_address": "tcp://127.0.0.1:8786",
    "dashboard_url": "http://127.0.0.1:8787",
    "n_workers": 4,
    "total_cores": 8,
    "total_memory": "8.00GB"
  }
}
```

#### Get Cluster Status
```bash
GET /api/processing/cluster/status
```

Response:
```json
{
  "status": "running",
  "n_workers": 4,
  "total_cores": 8,
  "total_memory": "8.00GB",
  "used_memory": "2.50GB",
  "memory_usage_percent": 31.25,
  "active_tasks": 12
}
```

#### Scale Cluster
```bash
POST /api/processing/cluster/scale
Content-Type: application/json

{
  "n_workers": 8
}
```

#### Stop Cluster
```bash
POST /api/processing/cluster/stop
```

### Job Management

#### Submit Job
```bash
POST /api/processing/jobs/submit
Content-Type: application/json

{
  "operation": "aggregate",
  "dataset_id": "dataset_123",
  "parameters": {
    "column": "expression_level",
    "operation": "mean"
  },
  "priority": "HIGH",
  "max_memory_gb": 4.0,
  "max_cores": 4
}
```

Response:
```json
{
  "message": "Job submitted successfully",
  "job_id": "job_abc123",
  "status": "pending"
}
```

#### Get Job Status
```bash
GET /api/processing/jobs/{job_id}/status
```

Response:
```json
{
  "job_id": "job_abc123",
  "status": "running",
  "priority": "HIGH",
  "progress": 45.5,
  "created_at": "2024-01-01T10:00:00Z",
  "started_at": "2024-01-01T10:00:05Z"
}
```

#### Cancel Job
```bash
POST /api/processing/jobs/{job_id}/cancel
```

#### List Jobs
```bash
GET /api/processing/jobs/list?status=running&limit=50
```

Response:
```json
{
  "total": 3,
  "jobs": [
    {
      "job_id": "job_abc123",
      "type": "aggregate",
      "operation": "aggregate",
      "status": "running",
      "priority": "HIGH",
      "progress": 45.5,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### Queue Management

#### Get Queue Status
```bash
GET /api/processing/queue/status
```

Response:
```json
{
  "scheduler_running": true,
  "queue_status": {
    "total_queued": 5,
    "total_running": 3,
    "total_completed": 12,
    "priority_breakdown": {
      "HIGH": 2,
      "NORMAL": 3
    }
  },
  "resource_usage": {
    "cluster_resources": {
      "total_memory_gb": 8.0,
      "used_memory_gb": 3.2,
      "available_memory_gb": 4.8,
      "memory_usage_percent": 40.0,
      "total_cores": 8,
      "used_cores": 5,
      "available_cores": 3
    }
  }
}
```

### Data Partitioning

#### Partition Data
```bash
POST /api/processing/data/partition
Content-Type: application/json

{
  "dataset_id": "dataset_123",
  "partition_size_mb": 100,
  "n_partitions": 10
}
```

Response:
```json
{
  "message": "Data partitioned successfully",
  "dataset_id": "dataset_123",
  "partition_info": {
    "n_partitions": 10,
    "columns": ["gene_id", "expression_level", "p_value"],
    "estimated_size_mb": 950.5
  }
}
```

### Metrics

#### Get Cluster Metrics
```bash
GET /api/processing/metrics/cluster
```

Response:
```json
{
  "total": 100,
  "metrics": [
    {
      "timestamp": "2024-01-01T10:00:00Z",
      "n_workers": 4,
      "total_memory": "8.00GB",
      "used_memory": "3.20GB",
      "total_cores": 8,
      "active_tasks": 12
    }
  ]
}
```

## Usage Examples

### Python Client Example

```python
import requests
import time

BASE_URL = "http://localhost:8001"

# Start the cluster
response = requests.post(f"{BASE_URL}/api/processing/cluster/start")
print(response.json())

# Submit a job
job_data = {
    "operation": "aggregate",
    "dataset_id": "my_dataset",
    "parameters": {
        "column": "expression_level",
        "operation": "mean"
    },
    "priority": "HIGH",
    "max_memory_gb": 2.0,
    "max_cores": 2
}

response = requests.post(
    f"{BASE_URL}/api/processing/jobs/submit",
    json=job_data
)
job_id = response.json()["job_id"]
print(f"Job submitted: {job_id}")

# Monitor job progress
while True:
    response = requests.get(
        f"{BASE_URL}/api/processing/jobs/{job_id}/status"
    )
    status = response.json()
    
    print(f"Status: {status['status']}, Progress: {status.get('progress', 0)}%")
    
    if status['status'] in ['completed', 'failed', 'cancelled']:
        break
    
    time.sleep(2)

# Get final result
if status['status'] == 'completed':
    print(f"Result: {status.get('result')}")
```

### JavaScript/TypeScript Example

```typescript
const BASE_URL = 'http://localhost:8001';

// Start cluster
async function startCluster() {
  const response = await fetch(`${BASE_URL}/api/processing/cluster/start`, {
    method: 'POST'
  });
  return await response.json();
}

// Submit job
async function submitJob(jobData) {
  const response = await fetch(`${BASE_URL}/api/processing/jobs/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(jobData)
  });
  return await response.json();
}

// Monitor job
async function monitorJob(jobId) {
  const response = await fetch(
    `${BASE_URL}/api/processing/jobs/${jobId}/status`
  );
  return await response.json();
}

// Usage
const cluster = await startCluster();
console.log('Cluster started:', cluster);

const job = await submitJob({
  operation: 'aggregate',
  dataset_id: 'my_dataset',
  parameters: { column: 'expression_level', operation: 'mean' },
  priority: 'HIGH',
  max_memory_gb: 2.0,
  max_cores: 2
});

console.log('Job submitted:', job.job_id);

// Poll for status
const interval = setInterval(async () => {
  const status = await monitorJob(job.job_id);
  console.log(`Status: ${status.status}, Progress: ${status.progress}%`);
  
  if (['completed', 'failed', 'cancelled'].includes(status.status)) {
    clearInterval(interval);
    console.log('Final result:', status.result);
  }
}, 2000);
```

## Configuration

### Environment Variables

```bash
# Dask cluster configuration
DASK_N_WORKERS=4                    # Number of worker processes
DASK_THREADS_PER_WORKER=2           # Threads per worker
DASK_MEMORY_LIMIT=2GB               # Memory limit per worker

# Job queue configuration
MAX_CONCURRENT_JOBS=4               # Maximum concurrent jobs
JOB_CHECK_INTERVAL=5                # Queue check interval (seconds)

# Resource limits
DEFAULT_MAX_MEMORY_GB=2.0           # Default memory per job
DEFAULT_MAX_CORES=2                 # Default cores per job
```

### Docker Compose Configuration

```yaml
services:
  backend:
    environment:
      - DASK_N_WORKERS=8
      - DASK_THREADS_PER_WORKER=2
      - DASK_MEMORY_LIMIT=4GB
    ports:
      - "8787:8787"  # Dask dashboard
```

## Monitoring

### Dask Dashboard

Access the Dask dashboard at http://localhost:8787 to monitor:
- Worker status and resource usage
- Task progress and execution
- Memory and CPU utilization
- Task graphs and dependencies

### Health Check

```bash
GET /api/processing/health
```

Response:
```json
{
  "status": "healthy",
  "cluster_running": true,
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## Best Practices

### 1. Resource Allocation
- Set appropriate memory limits based on data size
- Allocate cores based on computation complexity
- Monitor resource usage and adjust as needed

### 2. Job Priority
- Use CRITICAL for time-sensitive operations
- Use HIGH for important analysis tasks
- Use NORMAL for routine processing
- Use LOW for background tasks

### 3. Data Partitioning
- Partition large datasets (>1GB) for better performance
- Use 100MB partition size as a starting point
- Adjust based on available memory and workers

### 4. Error Handling
- Jobs automatically retry up to 3 times
- Check job status regularly
- Handle failed jobs appropriately

### 5. Cluster Scaling
- Scale up for heavy workloads
- Scale down during idle periods
- Monitor memory usage to prevent OOM errors

## Troubleshooting

### Cluster Won't Start
- Check if port 8787 is available
- Verify sufficient system resources
- Check logs for error messages

### Jobs Stuck in Queue
- Check resource availability
- Verify cluster is running
- Check job priority and queue status

### Out of Memory Errors
- Reduce partition size
- Increase worker memory limit
- Scale up cluster with more workers

### Slow Performance
- Increase number of workers
- Optimize partition sizes
- Check network latency
- Monitor dashboard for bottlenecks

## Requirements

### Python Dependencies
```
dask[complete]==2024.1.0
distributed==2024.1.0
bokeh==3.3.2
pandas>=2.0.0
numpy>=1.24.0
```

### System Requirements
- Minimum 4GB RAM (8GB+ recommended)
- Multi-core CPU (4+ cores recommended)
- Network connectivity for distributed workers
- Sufficient disk space for data and checkpoints

## Integration with Other Modules

### ML Framework
- Distribute model training across workers
- Parallel hyperparameter tuning
- Batch prediction on large datasets

### Statistical Analysis
- Parallel statistical computations
- Large-scale data transformations
- Multi-omics integration processing

### Data Harbor
- Process large uploaded files
- Parallel data validation
- Distributed feature extraction

## Support

For issues or questions:
1. Check the Dask dashboard for cluster status
2. Review job logs in the database
3. Monitor resource usage metrics
4. Consult the API documentation at /docs
