"""
Distributed Processing Service for OmniScope AI
Provides Dask cluster management, job scheduling, and monitoring
"""

import os
import uuid
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor

from dask.distributed import Client, LocalCluster, as_completed
from dask import delayed
import dask.dataframe as dd
import pandas as pd
import numpy as np

from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text
from .models import Base


class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobPriority(int, Enum):
    """Job priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class ProcessingJob(Base):
    """Database model for processing jobs"""
    __tablename__ = "processing_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String, nullable=False)  # map_reduce, parallel_apply, custom
    dataset_id = Column(String)
    operation = Column(String, nullable=False)
    parameters = Column(JSON)
    priority = Column(Integer, default=JobPriority.NORMAL)
    status = Column(String, default=JobStatus.PENDING)
    progress = Column(Float, default=0.0)
    result = Column(JSON)
    error_message = Column(Text)
    n_workers = Column(Integer, default=4)
    memory_per_worker = Column(String, default="2GB")
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_by = Column(String)


class ClusterMetrics(Base):
    """Database model for cluster metrics"""
    __tablename__ = "cluster_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow)
    n_workers = Column(Integer)
    total_memory = Column(String)
    used_memory = Column(String)
    total_cores = Column(Integer)
    used_cores = Column(Integer)
    active_tasks = Column(Integer)
    queued_tasks = Column(Integer)
    metrics_data = Column(JSON)


class DaskClusterManager:
    """
    Manages Dask cluster lifecycle, configuration, and monitoring
    """
    
    def __init__(self, n_workers: int = 4, threads_per_worker: int = 2, 
                 memory_limit: str = "2GB"):
        """
        Initialize Dask cluster manager
        
        Args:
            n_workers: Number of worker processes
            threads_per_worker: Number of threads per worker
            memory_limit: Memory limit per worker
        """
        self.n_workers = n_workers
        self.threads_per_worker = threads_per_worker
        self.memory_limit = memory_limit
        self.cluster: Optional[LocalCluster] = None
        self.client: Optional[Client] = None
        self._is_running = False
        
    def start_cluster(self) -> Dict[str, Any]:
        """
        Start the Dask cluster with scheduler and workers
        
        Returns:
            Cluster information including dashboard URL
        """
        try:
            # Create local cluster with specified configuration
            self.cluster = LocalCluster(
                n_workers=self.n_workers,
                threads_per_worker=self.threads_per_worker,
                memory_limit=self.memory_limit,
                dashboard_address=':8787',
                silence_logs=False
            )
            
            # Create client connected to cluster
            self.client = Client(self.cluster)
            self._is_running = True
            
            cluster_info = {
                "status": "running",
                "scheduler_address": self.cluster.scheduler_address,
                "dashboard_url": self.cluster.dashboard_link,
                "n_workers": len(self.cluster.workers),
                "total_cores": self.cluster.total_cores,
                "total_memory": self.cluster.total_memory,
                "started_at": datetime.utcnow().isoformat()
            }
            
            print(f"✅ Dask cluster started: {cluster_info['scheduler_address']}")
            print(f"📊 Dashboard available at: {cluster_info['dashboard_url']}")
            
            return cluster_info
            
        except Exception as e:
            print(f"❌ Failed to start Dask cluster: {e}")
            raise
    
    def stop_cluster(self):
        """Stop the Dask cluster and cleanup resources"""
        try:
            if self.client:
                self.client.close()
                self.client = None
            
            if self.cluster:
                self.cluster.close()
                self.cluster = None
            
            self._is_running = False
            print("✅ Dask cluster stopped successfully")
            
        except Exception as e:
            print(f"❌ Error stopping Dask cluster: {e}")
            raise
    
    def scale_cluster(self, n_workers: int) -> Dict[str, Any]:
        """
        Scale the cluster to specified number of workers
        
        Args:
            n_workers: Target number of workers
            
        Returns:
            Updated cluster information
        """
        if not self.cluster:
            raise RuntimeError("Cluster is not running")
        
        try:
            self.cluster.scale(n_workers)
            self.n_workers = n_workers
            
            # Wait for workers to be ready
            time.sleep(2)
            
            return self.get_cluster_status()
            
        except Exception as e:
            print(f"❌ Failed to scale cluster: {e}")
            raise
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """
        Get current cluster status and metrics
        
        Returns:
            Cluster status information
        """
        if not self._is_running or not self.client:
            return {
                "status": "stopped",
                "n_workers": 0,
                "total_cores": 0,
                "total_memory": "0GB"
            }
        
        try:
            # Get scheduler info
            scheduler_info = self.client.scheduler_info()
            
            # Calculate resource usage
            workers = scheduler_info.get('workers', {})
            total_memory = sum(w.get('memory_limit', 0) for w in workers.values())
            used_memory = sum(w.get('metrics', {}).get('memory', 0) for w in workers.values())
            total_cores = sum(w.get('nthreads', 0) for w in workers.values())
            
            # Get task information
            tasks = self.client.processing()
            
            status = {
                "status": "running",
                "scheduler_address": self.cluster.scheduler_address,
                "dashboard_url": self.cluster.dashboard_link,
                "n_workers": len(workers),
                "total_cores": total_cores,
                "total_memory": f"{total_memory / (1024**3):.2f}GB",
                "used_memory": f"{used_memory / (1024**3):.2f}GB",
                "memory_usage_percent": (used_memory / total_memory * 100) if total_memory > 0 else 0,
                "active_tasks": len(tasks),
                "workers": [
                    {
                        "id": worker_id,
                        "address": info.get('address'),
                        "nthreads": info.get('nthreads'),
                        "memory_limit": f"{info.get('memory_limit', 0) / (1024**3):.2f}GB",
                        "memory_used": f"{info.get('metrics', {}).get('memory', 0) / (1024**3):.2f}GB"
                    }
                    for worker_id, info in workers.items()
                ]
            }
            
            return status
            
        except Exception as e:
            print(f"❌ Error getting cluster status: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def monitor_cluster(self, db: Session) -> ClusterMetrics:
        """
        Monitor cluster and save metrics to database
        
        Args:
            db: Database session
            
        Returns:
            ClusterMetrics object
        """
        status = self.get_cluster_status()
        
        metrics = ClusterMetrics(
            n_workers=status.get('n_workers', 0),
            total_memory=status.get('total_memory', '0GB'),
            used_memory=status.get('used_memory', '0GB'),
            total_cores=status.get('total_cores', 0),
            used_cores=0,  # Calculate from active tasks
            active_tasks=status.get('active_tasks', 0),
            queued_tasks=0,  # Will be updated by job queue
            metrics_data=status
        )
        
        db.add(metrics)
        db.commit()
        db.refresh(metrics)
        
        return metrics
    
    def is_running(self) -> bool:
        """Check if cluster is running"""
        return self._is_running and self.client is not None


# Global cluster manager instance
_cluster_manager: Optional[DaskClusterManager] = None


def get_cluster_manager() -> DaskClusterManager:
    """
    Get or create global cluster manager instance
    
    Returns:
        DaskClusterManager instance
    """
    global _cluster_manager
    
    if _cluster_manager is None:
        # Get configuration from environment
        n_workers = int(os.getenv("DASK_N_WORKERS", "4"))
        threads_per_worker = int(os.getenv("DASK_THREADS_PER_WORKER", "2"))
        memory_limit = os.getenv("DASK_MEMORY_LIMIT", "2GB")
        
        _cluster_manager = DaskClusterManager(
            n_workers=n_workers,
            threads_per_worker=threads_per_worker,
            memory_limit=memory_limit
        )
    
    return _cluster_manager


def ensure_cluster_running():
    """Ensure cluster is running, start if not"""
    manager = get_cluster_manager()
    if not manager.is_running():
        manager.start_cluster()



class DataPartitioner:
    """
    Handles automatic data partitioning for distributed processing
    """
    
    def __init__(self, client: Client):
        """
        Initialize data partitioner
        
        Args:
            client: Dask client instance
        """
        self.client = client
    
    def partition_dataframe(self, df: pd.DataFrame, 
                           partition_size_mb: Optional[int] = None,
                           n_partitions: Optional[int] = None) -> dd.DataFrame:
        """
        Partition a pandas DataFrame for distributed processing
        
        Args:
            df: Input pandas DataFrame
            partition_size_mb: Target partition size in MB (auto-calculated if None)
            n_partitions: Number of partitions (auto-calculated if None)
            
        Returns:
            Dask DataFrame with optimized partitions
        """
        # Calculate DataFrame size in MB
        df_size_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        
        # Auto-calculate partition size if not provided
        if partition_size_mb is None:
            # Target 100MB per partition by default
            partition_size_mb = 100
        
        # Calculate optimal number of partitions
        if n_partitions is None:
            n_partitions = max(1, int(df_size_mb / partition_size_mb))
            # Ensure at least one partition per worker
            n_workers = len(self.client.scheduler_info()['workers'])
            n_partitions = max(n_partitions, n_workers)
        
        # Create Dask DataFrame with calculated partitions
        ddf = dd.from_pandas(df, npartitions=n_partitions)
        
        print(f"📊 Partitioned DataFrame: {df_size_mb:.2f}MB into {n_partitions} partitions")
        
        return ddf
    
    def partition_csv(self, file_path: str, 
                     blocksize: str = "100MB") -> dd.DataFrame:
        """
        Load and partition a CSV file for distributed processing
        
        Args:
            file_path: Path to CSV file
            blocksize: Size of each partition (e.g., "100MB", "1GB")
            
        Returns:
            Dask DataFrame with partitioned data
        """
        try:
            # Read CSV with automatic partitioning
            ddf = dd.read_csv(file_path, blocksize=blocksize)
            
            print(f"📊 Loaded CSV with {ddf.npartitions} partitions")
            
            return ddf
            
        except Exception as e:
            print(f"❌ Error partitioning CSV: {e}")
            raise
    
    def partition_array(self, arr: np.ndarray, 
                       chunk_size: Optional[int] = None) -> Any:
        """
        Partition a numpy array for distributed processing
        
        Args:
            arr: Input numpy array
            chunk_size: Size of each chunk (auto-calculated if None)
            
        Returns:
            Dask array with optimized chunks
        """
        import dask.array as da
        
        # Calculate optimal chunk size
        if chunk_size is None:
            # Target 100MB chunks
            target_size_mb = 100
            element_size = arr.dtype.itemsize
            chunk_size = int((target_size_mb * 1024 * 1024) / element_size)
            chunk_size = min(chunk_size, arr.shape[0])
        
        # Create Dask array with chunks
        darr = da.from_array(arr, chunks=chunk_size)
        
        print(f"📊 Partitioned array: shape {arr.shape} into chunks of {chunk_size}")
        
        return darr
    
    def optimize_partitions(self, ddf: dd.DataFrame) -> dd.DataFrame:
        """
        Optimize partition sizes for better performance
        
        Args:
            ddf: Dask DataFrame
            
        Returns:
            Optimized Dask DataFrame
        """
        # Repartition to balance partition sizes
        n_workers = len(self.client.scheduler_info()['workers'])
        optimal_partitions = max(n_workers * 2, ddf.npartitions)
        
        if ddf.npartitions != optimal_partitions:
            ddf = ddf.repartition(npartitions=optimal_partitions)
            print(f"📊 Repartitioned to {optimal_partitions} partitions")
        
        return ddf
    
    def get_partition_info(self, ddf: dd.DataFrame) -> Dict[str, Any]:
        """
        Get information about DataFrame partitions
        
        Args:
            ddf: Dask DataFrame
            
        Returns:
            Partition information
        """
        return {
            "n_partitions": ddf.npartitions,
            "columns": list(ddf.columns),
            "dtypes": {col: str(dtype) for col, dtype in ddf.dtypes.items()},
            "estimated_size_mb": ddf.memory_usage(deep=True).sum().compute() / (1024 * 1024)
        }


class DistributedDataLoader:
    """
    Handles distributed data loading from various sources
    """
    
    def __init__(self, client: Client):
        """
        Initialize distributed data loader
        
        Args:
            client: Dask client instance
        """
        self.client = client
        self.partitioner = DataPartitioner(client)
    
    def load_from_database(self, connection_string: str, query: str,
                          partition_column: Optional[str] = None,
                          n_partitions: int = 4) -> dd.DataFrame:
        """
        Load data from database with partitioning
        
        Args:
            connection_string: Database connection string
            query: SQL query to execute
            partition_column: Column to partition on
            n_partitions: Number of partitions
            
        Returns:
            Dask DataFrame with partitioned data
        """
        try:
            if partition_column:
                # Load with partitioning on specific column
                ddf = dd.read_sql_table(
                    query,
                    connection_string,
                    index_col=partition_column,
                    npartitions=n_partitions
                )
            else:
                # Load without specific partitioning
                df = pd.read_sql(query, connection_string)
                ddf = self.partitioner.partition_dataframe(df, n_partitions=n_partitions)
            
            print(f"📊 Loaded data from database with {ddf.npartitions} partitions")
            
            return ddf
            
        except Exception as e:
            print(f"❌ Error loading from database: {e}")
            raise
    
    def load_from_files(self, file_pattern: str, 
                       file_type: str = "csv") -> dd.DataFrame:
        """
        Load data from multiple files with automatic partitioning
        
        Args:
            file_pattern: File pattern (e.g., "data/*.csv")
            file_type: File type (csv, parquet, json)
            
        Returns:
            Dask DataFrame with partitioned data
        """
        try:
            if file_type == "csv":
                ddf = dd.read_csv(file_pattern)
            elif file_type == "parquet":
                ddf = dd.read_parquet(file_pattern)
            elif file_type == "json":
                ddf = dd.read_json(file_pattern)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            print(f"📊 Loaded {file_type} files with {ddf.npartitions} partitions")
            
            return ddf
            
        except Exception as e:
            print(f"❌ Error loading files: {e}")
            raise
    
    def save_partitioned_data(self, ddf: dd.DataFrame, 
                             output_path: str,
                             format: str = "parquet"):
        """
        Save partitioned data to disk
        
        Args:
            ddf: Dask DataFrame
            output_path: Output directory path
            format: Output format (parquet, csv)
        """
        try:
            if format == "parquet":
                ddf.to_parquet(output_path, engine='pyarrow')
            elif format == "csv":
                ddf.to_csv(output_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            print(f"✅ Saved partitioned data to {output_path}")
            
        except Exception as e:
            print(f"❌ Error saving partitioned data: {e}")
            raise



class FaultToleranceManager:
    """
    Manages fault tolerance for distributed processing tasks
    """
    
    def __init__(self, client: Client, max_retries: int = 3, 
                 retry_delay: int = 5):
        """
        Initialize fault tolerance manager
        
        Args:
            client: Dask client instance
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.client = client
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.failed_tasks: Dict[str, int] = {}
        self.worker_failures: Dict[str, int] = {}
    
    def execute_with_retry(self, func: Callable, *args, 
                          task_id: Optional[str] = None,
                          **kwargs) -> Any:
        """
        Execute a function with automatic retry on failure
        
        Args:
            func: Function to execute
            task_id: Optional task identifier
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        if task_id is None:
            task_id = str(uuid.uuid4())
        
        retry_count = 0
        last_error = None
        
        while retry_count <= self.max_retries:
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Reset failure count on success
                if task_id in self.failed_tasks:
                    del self.failed_tasks[task_id]
                
                return result
                
            except Exception as e:
                retry_count += 1
                last_error = e
                
                # Track failure
                self.failed_tasks[task_id] = retry_count
                
                print(f"⚠️ Task {task_id} failed (attempt {retry_count}/{self.max_retries}): {e}")
                
                if retry_count <= self.max_retries:
                    print(f"🔄 Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"❌ Task {task_id} failed after {self.max_retries} retries")
                    raise last_error
        
        raise last_error
    
    def detect_worker_failure(self) -> List[str]:
        """
        Detect failed workers in the cluster
        
        Returns:
            List of failed worker IDs
        """
        try:
            scheduler_info = self.client.scheduler_info()
            workers = scheduler_info.get('workers', {})
            
            # Check worker status
            failed_workers = []
            for worker_id, info in workers.items():
                status = info.get('status', 'unknown')
                if status in ['closed', 'closing', 'error']:
                    failed_workers.append(worker_id)
                    self.worker_failures[worker_id] = self.worker_failures.get(worker_id, 0) + 1
            
            if failed_workers:
                print(f"⚠️ Detected {len(failed_workers)} failed workers")
            
            return failed_workers
            
        except Exception as e:
            print(f"❌ Error detecting worker failures: {e}")
            return []
    
    def reschedule_task(self, task_future, exclude_workers: Optional[List[str]] = None):
        """
        Reschedule a failed task on a different worker
        
        Args:
            task_future: Future object of the failed task
            exclude_workers: List of worker IDs to exclude
        """
        try:
            # Cancel the failed task
            task_future.cancel()
            
            # Get available workers
            scheduler_info = self.client.scheduler_info()
            workers = scheduler_info.get('workers', {})
            
            if exclude_workers:
                available_workers = [w for w in workers.keys() if w not in exclude_workers]
            else:
                available_workers = list(workers.keys())
            
            if not available_workers:
                raise RuntimeError("No available workers for rescheduling")
            
            print(f"🔄 Rescheduling task on different worker")
            
            # Task will be automatically rescheduled by Dask
            
        except Exception as e:
            print(f"❌ Error rescheduling task: {e}")
            raise
    
    def get_failure_stats(self) -> Dict[str, Any]:
        """
        Get statistics about task and worker failures
        
        Returns:
            Failure statistics
        """
        return {
            "failed_tasks": len(self.failed_tasks),
            "task_failures": dict(self.failed_tasks),
            "failed_workers": len(self.worker_failures),
            "worker_failures": dict(self.worker_failures),
            "max_retries": self.max_retries
        }
    
    def reset_failure_tracking(self):
        """Reset failure tracking counters"""
        self.failed_tasks.clear()
        self.worker_failures.clear()
        print("✅ Failure tracking reset")


class TaskRescheduler:
    """
    Handles automatic task rescheduling on worker failures
    """
    
    def __init__(self, client: Client):
        """
        Initialize task rescheduler
        
        Args:
            client: Dask client instance
        """
        self.client = client
        self.pending_reschedules: List[Dict] = []
    
    def monitor_and_reschedule(self, futures: List, 
                               check_interval: int = 5) -> List:
        """
        Monitor task futures and reschedule failed tasks
        
        Args:
            futures: List of task futures to monitor
            check_interval: Interval to check task status (seconds)
            
        Returns:
            List of completed results
        """
        results = []
        failed_futures = []
        
        try:
            # Use as_completed to monitor futures
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"⚠️ Task failed: {e}")
                    failed_futures.append(future)
            
            # Reschedule failed tasks
            if failed_futures:
                print(f"🔄 Rescheduling {len(failed_futures)} failed tasks")
                for future in failed_futures:
                    # Retry the task
                    try:
                        result = future.retry()
                        results.append(result)
                    except Exception as e:
                        print(f"❌ Task failed after retry: {e}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error in monitor_and_reschedule: {e}")
            raise
    
    def create_checkpoint(self, job_id: str, state: Dict) -> str:
        """
        Create a checkpoint for job state
        
        Args:
            job_id: Job identifier
            state: Job state to checkpoint
            
        Returns:
            Checkpoint ID
        """
        checkpoint_id = f"{job_id}_{int(time.time())}"
        checkpoint_path = f"./checkpoints/{checkpoint_id}.json"
        
        os.makedirs("./checkpoints", exist_ok=True)
        
        with open(checkpoint_path, 'w') as f:
            json.dump(state, f)
        
        print(f"✅ Created checkpoint: {checkpoint_id}")
        
        return checkpoint_id
    
    def restore_from_checkpoint(self, checkpoint_id: str) -> Dict:
        """
        Restore job state from checkpoint
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            Restored job state
        """
        checkpoint_path = f"./checkpoints/{checkpoint_id}.json"
        
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_id}")
        
        with open(checkpoint_path, 'r') as f:
            state = json.load(f)
        
        print(f"✅ Restored from checkpoint: {checkpoint_id}")
        
        return state



class ProgressMonitor:
    """
    Monitors and tracks progress of distributed processing tasks
    """
    
    def __init__(self, client: Client):
        """
        Initialize progress monitor
        
        Args:
            client: Dask client instance
        """
        self.client = client
        self.job_progress: Dict[str, Dict] = {}
    
    def track_job_progress(self, job_id: str, total_tasks: int) -> Dict[str, Any]:
        """
        Initialize progress tracking for a job
        
        Args:
            job_id: Job identifier
            total_tasks: Total number of tasks in the job
            
        Returns:
            Initial progress information
        """
        self.job_progress[job_id] = {
            "total_tasks": total_tasks,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "progress_percent": 0.0,
            "started_at": datetime.utcnow().isoformat(),
            "estimated_completion": None,
            "status": "running"
        }
        
        return self.job_progress[job_id]
    
    def update_progress(self, job_id: str, completed: int = 0, 
                       failed: int = 0) -> Dict[str, Any]:
        """
        Update progress for a job
        
        Args:
            job_id: Job identifier
            completed: Number of newly completed tasks
            failed: Number of newly failed tasks
            
        Returns:
            Updated progress information
        """
        if job_id not in self.job_progress:
            raise ValueError(f"Job {job_id} not being tracked")
        
        progress = self.job_progress[job_id]
        progress["completed_tasks"] += completed
        progress["failed_tasks"] += failed
        
        # Calculate progress percentage
        total = progress["total_tasks"]
        done = progress["completed_tasks"] + progress["failed_tasks"]
        progress["progress_percent"] = (done / total * 100) if total > 0 else 0
        
        # Estimate completion time
        if progress["completed_tasks"] > 0:
            started = datetime.fromisoformat(progress["started_at"])
            elapsed = (datetime.utcnow() - started).total_seconds()
            rate = progress["completed_tasks"] / elapsed
            remaining = total - done
            eta_seconds = remaining / rate if rate > 0 else 0
            progress["estimated_completion"] = (
                datetime.utcnow().timestamp() + eta_seconds
            )
        
        # Update status
        if done >= total:
            progress["status"] = "completed"
            progress["completed_at"] = datetime.utcnow().isoformat()
        
        return progress
    
    def get_progress(self, job_id: str) -> Dict[str, Any]:
        """
        Get current progress for a job
        
        Args:
            job_id: Job identifier
            
        Returns:
            Progress information
        """
        if job_id not in self.job_progress:
            return {
                "error": "Job not found",
                "job_id": job_id
            }
        
        return self.job_progress[job_id]
    
    def get_all_progress(self) -> Dict[str, Dict]:
        """
        Get progress for all tracked jobs
        
        Returns:
            Dictionary of job progress information
        """
        return dict(self.job_progress)
    
    def monitor_futures(self, job_id: str, futures: List) -> Dict[str, Any]:
        """
        Monitor a list of futures and update progress
        
        Args:
            job_id: Job identifier
            futures: List of Dask futures to monitor
            
        Returns:
            Final progress information
        """
        # Initialize tracking
        self.track_job_progress(job_id, len(futures))
        
        completed_count = 0
        failed_count = 0
        
        # Monitor futures as they complete
        for future in as_completed(futures):
            try:
                future.result()
                completed_count += 1
                self.update_progress(job_id, completed=1)
            except Exception as e:
                failed_count += 1
                self.update_progress(job_id, failed=1)
                print(f"⚠️ Task failed: {e}")
            
            # Print progress update
            progress = self.get_progress(job_id)
            print(f"📊 Progress: {progress['progress_percent']:.1f}% "
                  f"({progress['completed_tasks']}/{progress['total_tasks']} completed)")
        
        return self.get_progress(job_id)
    
    def create_progress_visualization(self, job_id: str) -> Dict[str, Any]:
        """
        Create visualization data for progress
        
        Args:
            job_id: Job identifier
            
        Returns:
            Visualization data
        """
        progress = self.get_progress(job_id)
        
        if "error" in progress:
            return progress
        
        return {
            "job_id": job_id,
            "chart_type": "progress_bar",
            "data": {
                "completed": progress["completed_tasks"],
                "failed": progress["failed_tasks"],
                "remaining": progress["total_tasks"] - progress["completed_tasks"] - progress["failed_tasks"],
                "total": progress["total_tasks"]
            },
            "metrics": {
                "progress_percent": progress["progress_percent"],
                "status": progress["status"],
                "estimated_completion": progress.get("estimated_completion")
            }
        }
    
    def cleanup_completed_jobs(self, max_age_hours: int = 24):
        """
        Remove progress tracking for old completed jobs
        
        Args:
            max_age_hours: Maximum age of completed jobs to keep (hours)
        """
        current_time = datetime.utcnow()
        jobs_to_remove = []
        
        for job_id, progress in self.job_progress.items():
            if progress["status"] == "completed" and "completed_at" in progress:
                completed_at = datetime.fromisoformat(progress["completed_at"])
                age_hours = (current_time - completed_at).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.job_progress[job_id]
        
        if jobs_to_remove:
            print(f"🧹 Cleaned up {len(jobs_to_remove)} old job progress records")


class RealTimeProgressTracker:
    """
    Provides real-time progress tracking with WebSocket support
    """
    
    def __init__(self, client: Client):
        """
        Initialize real-time progress tracker
        
        Args:
            client: Dask client instance
        """
        self.client = client
        self.monitor = ProgressMonitor(client)
        self.callbacks: Dict[str, List[Callable]] = {}
    
    def register_callback(self, job_id: str, callback: Callable):
        """
        Register a callback for progress updates
        
        Args:
            job_id: Job identifier
            callback: Callback function to call on progress update
        """
        if job_id not in self.callbacks:
            self.callbacks[job_id] = []
        
        self.callbacks[job_id].append(callback)
    
    def notify_progress(self, job_id: str, progress: Dict):
        """
        Notify all registered callbacks of progress update
        
        Args:
            job_id: Job identifier
            progress: Progress information
        """
        if job_id in self.callbacks:
            for callback in self.callbacks[job_id]:
                try:
                    callback(progress)
                except Exception as e:
                    print(f"⚠️ Error in progress callback: {e}")
    
    async def track_with_updates(self, job_id: str, futures: List,
                                 update_interval: float = 1.0):
        """
        Track progress with periodic updates
        
        Args:
            job_id: Job identifier
            futures: List of futures to monitor
            update_interval: Interval between updates (seconds)
        """
        self.monitor.track_job_progress(job_id, len(futures))
        
        # Monitor in background
        while True:
            progress = self.monitor.get_progress(job_id)
            
            # Notify callbacks
            self.notify_progress(job_id, progress)
            
            # Check if completed
            if progress["status"] == "completed":
                break
            
            await asyncio.sleep(update_interval)
    
    def get_live_metrics(self, job_id: str) -> Dict[str, Any]:
        """
        Get live metrics for a job
        
        Args:
            job_id: Job identifier
            
        Returns:
            Live metrics including cluster status
        """
        progress = self.monitor.get_progress(job_id)
        
        # Get cluster metrics
        scheduler_info = self.client.scheduler_info()
        workers = scheduler_info.get('workers', {})
        
        return {
            "job_progress": progress,
            "cluster_metrics": {
                "active_workers": len(workers),
                "total_cores": sum(w.get('nthreads', 0) for w in workers.values()),
                "memory_usage": sum(w.get('metrics', {}).get('memory', 0) for w in workers.values())
            },
            "timestamp": datetime.utcnow().isoformat()
        }



class ResourceManager:
    """
    Manages CPU and memory allocation for distributed processing
    """
    
    def __init__(self, client: Client):
        """
        Initialize resource manager
        
        Args:
            client: Dask client instance
        """
        self.client = client
        self.resource_limits: Dict[str, Dict] = {}
        self.resource_usage: Dict[str, Dict] = {}
    
    def set_resource_limits(self, job_id: str, 
                           max_memory_gb: float = 8.0,
                           max_cores: int = 4):
        """
        Set resource limits for a job
        
        Args:
            job_id: Job identifier
            max_memory_gb: Maximum memory in GB
            max_cores: Maximum number of CPU cores
        """
        self.resource_limits[job_id] = {
            "max_memory_gb": max_memory_gb,
            "max_cores": max_cores,
            "max_memory_bytes": max_memory_gb * 1024 ** 3
        }
        
        print(f"✅ Set resource limits for job {job_id}: "
              f"{max_memory_gb}GB memory, {max_cores} cores")
    
    def get_available_resources(self) -> Dict[str, Any]:
        """
        Get currently available cluster resources
        
        Returns:
            Available resources information
        """
        try:
            scheduler_info = self.client.scheduler_info()
            workers = scheduler_info.get('workers', {})
            
            total_memory = 0
            used_memory = 0
            total_cores = 0
            used_cores = 0
            
            for worker_info in workers.values():
                total_memory += worker_info.get('memory_limit', 0)
                used_memory += worker_info.get('metrics', {}).get('memory', 0)
                total_cores += worker_info.get('nthreads', 0)
                # Estimate used cores from task count
                used_cores += len(worker_info.get('processing', {}))
            
            available_memory = total_memory - used_memory
            available_cores = total_cores - used_cores
            
            return {
                "total_memory_gb": total_memory / (1024 ** 3),
                "used_memory_gb": used_memory / (1024 ** 3),
                "available_memory_gb": available_memory / (1024 ** 3),
                "memory_usage_percent": (used_memory / total_memory * 100) if total_memory > 0 else 0,
                "total_cores": total_cores,
                "used_cores": used_cores,
                "available_cores": available_cores,
                "core_usage_percent": (used_cores / total_cores * 100) if total_cores > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ Error getting available resources: {e}")
            return {}
    
    def check_resource_availability(self, job_id: str) -> bool:
        """
        Check if resources are available for a job
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if resources are available, False otherwise
        """
        if job_id not in self.resource_limits:
            return True  # No limits set
        
        limits = self.resource_limits[job_id]
        available = self.get_available_resources()
        
        memory_available = available.get('available_memory_gb', 0) >= limits['max_memory_gb']
        cores_available = available.get('available_cores', 0) >= limits['max_cores']
        
        return memory_available and cores_available
    
    def allocate_resources(self, job_id: str) -> Dict[str, Any]:
        """
        Allocate resources for a job
        
        Args:
            job_id: Job identifier
            
        Returns:
            Allocated resources information
        """
        if not self.check_resource_availability(job_id):
            raise RuntimeError(f"Insufficient resources for job {job_id}")
        
        limits = self.resource_limits.get(job_id, {})
        
        allocation = {
            "job_id": job_id,
            "allocated_memory_gb": limits.get('max_memory_gb', 0),
            "allocated_cores": limits.get('max_cores', 0),
            "allocated_at": datetime.utcnow().isoformat()
        }
        
        self.resource_usage[job_id] = allocation
        
        print(f"✅ Allocated resources for job {job_id}")
        
        return allocation
    
    def release_resources(self, job_id: str):
        """
        Release resources allocated to a job
        
        Args:
            job_id: Job identifier
        """
        if job_id in self.resource_usage:
            del self.resource_usage[job_id]
            print(f"✅ Released resources for job {job_id}")
        
        if job_id in self.resource_limits:
            del self.resource_limits[job_id]
    
    def monitor_resource_usage(self) -> Dict[str, Any]:
        """
        Monitor current resource usage across all jobs
        
        Returns:
            Resource usage statistics
        """
        available = self.get_available_resources()
        
        return {
            "cluster_resources": available,
            "active_jobs": len(self.resource_usage),
            "job_allocations": dict(self.resource_usage),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def enforce_resource_limits(self, job_id: str) -> bool:
        """
        Enforce resource limits for a job
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if within limits, False if exceeded
        """
        if job_id not in self.resource_limits:
            return True
        
        limits = self.resource_limits[job_id]
        current_usage = self.get_job_resource_usage(job_id)
        
        memory_ok = current_usage['memory_gb'] <= limits['max_memory_gb']
        cores_ok = current_usage['cores'] <= limits['max_cores']
        
        if not memory_ok:
            print(f"⚠️ Job {job_id} exceeded memory limit: "
                  f"{current_usage['memory_gb']:.2f}GB > {limits['max_memory_gb']}GB")
        
        if not cores_ok:
            print(f"⚠️ Job {job_id} exceeded core limit: "
                  f"{current_usage['cores']} > {limits['max_cores']}")
        
        return memory_ok and cores_ok
    
    def get_job_resource_usage(self, job_id: str) -> Dict[str, Any]:
        """
        Get current resource usage for a specific job
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job resource usage
        """
        # This is a simplified implementation
        # In production, you'd track actual per-job usage
        
        if job_id not in self.resource_usage:
            return {
                "memory_gb": 0,
                "cores": 0
            }
        
        allocation = self.resource_usage[job_id]
        
        return {
            "memory_gb": allocation.get('allocated_memory_gb', 0),
            "cores": allocation.get('allocated_cores', 0),
            "allocated_at": allocation.get('allocated_at')
        }
    
    def optimize_resource_allocation(self) -> Dict[str, Any]:
        """
        Optimize resource allocation across jobs
        
        Returns:
            Optimization recommendations
        """
        available = self.get_available_resources()
        
        recommendations = []
        
        # Check if cluster is underutilized
        if available['memory_usage_percent'] < 50:
            recommendations.append({
                "type": "scale_down",
                "reason": "Low memory utilization",
                "action": "Consider reducing number of workers"
            })
        
        # Check if cluster is overutilized
        if available['memory_usage_percent'] > 90:
            recommendations.append({
                "type": "scale_up",
                "reason": "High memory utilization",
                "action": "Consider adding more workers"
            })
        
        if available['core_usage_percent'] > 90:
            recommendations.append({
                "type": "scale_up",
                "reason": "High CPU utilization",
                "action": "Consider adding more workers"
            })
        
        return {
            "current_usage": available,
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }



class JobQueue:
    """
    Priority-based job queue for distributed processing
    """
    
    def __init__(self, client: Client, resource_manager: ResourceManager):
        """
        Initialize job queue
        
        Args:
            client: Dask client instance
            resource_manager: Resource manager instance
        """
        self.client = client
        self.resource_manager = resource_manager
        self.queue: List[Dict] = []
        self.running_jobs: Dict[str, Dict] = {}
        self.completed_jobs: Dict[str, Dict] = {}
    
    def enqueue_job(self, job_id: str, job_func: Callable, 
                   priority: JobPriority = JobPriority.NORMAL,
                   *args, **kwargs) -> str:
        """
        Add a job to the queue
        
        Args:
            job_id: Job identifier
            job_func: Function to execute
            priority: Job priority level
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Job ID
        """
        job = {
            "job_id": job_id,
            "function": job_func,
            "args": args,
            "kwargs": kwargs,
            "priority": priority,
            "status": JobStatus.PENDING,
            "enqueued_at": datetime.utcnow().isoformat(),
            "attempts": 0
        }
        
        self.queue.append(job)
        
        # Sort queue by priority (higher priority first)
        self.queue.sort(key=lambda x: x['priority'], reverse=True)
        
        print(f"✅ Job {job_id} enqueued with priority {priority.name}")
        
        return job_id
    
    def dequeue_job(self) -> Optional[Dict]:
        """
        Remove and return the highest priority job from queue
        
        Returns:
            Job dictionary or None if queue is empty
        """
        if not self.queue:
            return None
        
        # Get highest priority job
        job = self.queue.pop(0)
        
        return job
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current queue status
        
        Returns:
            Queue status information
        """
        priority_counts = {}
        for job in self.queue:
            priority = job['priority'].name
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            "total_queued": len(self.queue),
            "total_running": len(self.running_jobs),
            "total_completed": len(self.completed_jobs),
            "priority_breakdown": priority_counts,
            "queue": [
                {
                    "job_id": job['job_id'],
                    "priority": job['priority'].name,
                    "status": job['status'],
                    "enqueued_at": job['enqueued_at']
                }
                for job in self.queue
            ]
        }
    
    def process_queue(self, max_concurrent: int = 4) -> List[str]:
        """
        Process jobs from the queue
        
        Args:
            max_concurrent: Maximum number of concurrent jobs
            
        Returns:
            List of started job IDs
        """
        started_jobs = []
        
        while len(self.running_jobs) < max_concurrent and self.queue:
            job = self.dequeue_job()
            
            if job is None:
                break
            
            # Check resource availability
            job_id = job['job_id']
            if not self.resource_manager.check_resource_availability(job_id):
                # Re-queue the job
                self.queue.insert(0, job)
                print(f"⏸️ Job {job_id} waiting for resources")
                break
            
            # Start the job
            try:
                self.start_job(job)
                started_jobs.append(job_id)
            except Exception as e:
                print(f"❌ Failed to start job {job_id}: {e}")
                job['status'] = JobStatus.FAILED
                job['error'] = str(e)
                self.completed_jobs[job_id] = job
        
        return started_jobs
    
    def start_job(self, job: Dict):
        """
        Start executing a job
        
        Args:
            job: Job dictionary
        """
        job_id = job['job_id']
        
        # Allocate resources
        self.resource_manager.allocate_resources(job_id)
        
        # Submit job to Dask
        future = self.client.submit(
            job['function'],
            *job['args'],
            **job['kwargs'],
            priority=job['priority']
        )
        
        job['future'] = future
        job['status'] = JobStatus.RUNNING
        job['started_at'] = datetime.utcnow().isoformat()
        job['attempts'] += 1
        
        self.running_jobs[job_id] = job
        
        print(f"🚀 Started job {job_id}")
    
    def check_running_jobs(self) -> List[str]:
        """
        Check status of running jobs and move completed ones
        
        Returns:
            List of completed job IDs
        """
        completed = []
        
        for job_id, job in list(self.running_jobs.items()):
            future = job.get('future')
            
            if future is None:
                continue
            
            if future.done():
                try:
                    result = future.result()
                    job['result'] = result
                    job['status'] = JobStatus.COMPLETED
                    job['completed_at'] = datetime.utcnow().isoformat()
                    
                    print(f"✅ Job {job_id} completed successfully")
                    
                except Exception as e:
                    job['status'] = JobStatus.FAILED
                    job['error'] = str(e)
                    job['completed_at'] = datetime.utcnow().isoformat()
                    
                    print(f"❌ Job {job_id} failed: {e}")
                
                # Release resources
                self.resource_manager.release_resources(job_id)
                
                # Move to completed
                self.completed_jobs[job_id] = job
                del self.running_jobs[job_id]
                completed.append(job_id)
        
        return completed
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if cancelled, False if not found
        """
        # Check if in queue
        for i, job in enumerate(self.queue):
            if job['job_id'] == job_id:
                job['status'] = JobStatus.CANCELLED
                self.completed_jobs[job_id] = job
                del self.queue[i]
                print(f"🛑 Cancelled queued job {job_id}")
                return True
        
        # Check if running
        if job_id in self.running_jobs:
            job = self.running_jobs[job_id]
            future = job.get('future')
            
            if future:
                future.cancel()
            
            job['status'] = JobStatus.CANCELLED
            job['completed_at'] = datetime.utcnow().isoformat()
            
            self.resource_manager.release_resources(job_id)
            self.completed_jobs[job_id] = job
            del self.running_jobs[job_id]
            
            print(f"🛑 Cancelled running job {job_id}")
            return True
        
        return False
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """
        Get status of a specific job
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status or None if not found
        """
        # Check queue
        for job in self.queue:
            if job['job_id'] == job_id:
                return {
                    "job_id": job_id,
                    "status": job['status'],
                    "priority": job['priority'].name,
                    "enqueued_at": job['enqueued_at']
                }
        
        # Check running
        if job_id in self.running_jobs:
            job = self.running_jobs[job_id]
            return {
                "job_id": job_id,
                "status": job['status'],
                "priority": job['priority'].name,
                "started_at": job.get('started_at'),
                "attempts": job.get('attempts', 0)
            }
        
        # Check completed
        if job_id in self.completed_jobs:
            job = self.completed_jobs[job_id]
            return {
                "job_id": job_id,
                "status": job['status'],
                "priority": job['priority'].name,
                "completed_at": job.get('completed_at'),
                "error": job.get('error')
            }
        
        return None
    
    def cleanup_completed_jobs(self, max_age_hours: int = 24):
        """
        Remove old completed jobs
        
        Args:
            max_age_hours: Maximum age of completed jobs to keep (hours)
        """
        current_time = datetime.utcnow()
        jobs_to_remove = []
        
        for job_id, job in self.completed_jobs.items():
            if 'completed_at' in job:
                completed_at = datetime.fromisoformat(job['completed_at'])
                age_hours = (current_time - completed_at).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.completed_jobs[job_id]
        
        if jobs_to_remove:
            print(f"🧹 Cleaned up {len(jobs_to_remove)} old completed jobs")


class JobScheduler:
    """
    Schedules and manages job execution with priority and resource awareness
    """
    
    def __init__(self, client: Client):
        """
        Initialize job scheduler
        
        Args:
            client: Dask client instance
        """
        self.client = client
        self.resource_manager = ResourceManager(client)
        self.job_queue = JobQueue(client, self.resource_manager)
        self.progress_monitor = ProgressMonitor(client)
        self._scheduler_running = False
    
    def submit_job(self, job_func: Callable, 
                  priority: JobPriority = JobPriority.NORMAL,
                  max_memory_gb: float = 2.0,
                  max_cores: int = 2,
                  *args, **kwargs) -> str:
        """
        Submit a job for execution
        
        Args:
            job_func: Function to execute
            priority: Job priority level
            max_memory_gb: Maximum memory allocation
            max_cores: Maximum CPU cores
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        # Set resource limits
        self.resource_manager.set_resource_limits(
            job_id,
            max_memory_gb=max_memory_gb,
            max_cores=max_cores
        )
        
        # Enqueue job
        self.job_queue.enqueue_job(
            job_id,
            job_func,
            priority=priority,
            *args,
            **kwargs
        )
        
        # Process queue
        self.job_queue.process_queue()
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """
        Get status of a job
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status
        """
        return self.job_queue.get_job_status(job_id)
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if cancelled successfully
        """
        return self.job_queue.cancel_job(job_id)
    
    def start_scheduler(self, check_interval: int = 5):
        """
        Start the job scheduler loop
        
        Args:
            check_interval: Interval to check queue (seconds)
        """
        self._scheduler_running = True
        
        print("🚀 Job scheduler started")
        
        while self._scheduler_running:
            # Check running jobs
            completed = self.job_queue.check_running_jobs()
            
            if completed:
                print(f"✅ {len(completed)} jobs completed")
            
            # Process queue
            started = self.job_queue.process_queue()
            
            if started:
                print(f"🚀 Started {len(started)} jobs")
            
            # Wait before next check
            time.sleep(check_interval)
    
    def stop_scheduler(self):
        """Stop the job scheduler"""
        self._scheduler_running = False
        print("🛑 Job scheduler stopped")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """
        Get overall scheduler status
        
        Returns:
            Scheduler status information
        """
        return {
            "scheduler_running": self._scheduler_running,
            "queue_status": self.job_queue.get_queue_status(),
            "resource_usage": self.resource_manager.monitor_resource_usage(),
            "timestamp": datetime.utcnow().isoformat()
        }
