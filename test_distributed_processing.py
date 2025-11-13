"""
Test script for Distributed Processing Cluster
Verifies basic functionality of the distributed processing system
"""

import sys
import time
from datetime import datetime

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from backend_db.distributed_processing import (
            DaskClusterManager,
            DataPartitioner,
            FaultToleranceManager,
            ProgressMonitor,
            ResourceManager,
            JobQueue,
            JobScheduler,
            JobPriority,
            JobStatus
        )
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_cluster_manager():
    """Test DaskClusterManager basic functionality"""
    print("\nTesting DaskClusterManager...")
    try:
        from backend_db.distributed_processing import DaskClusterManager
        
        # Create manager
        manager = DaskClusterManager(n_workers=2, memory_limit="1GB")
        print("✅ Manager created")
        
        # Start cluster
        cluster_info = manager.start_cluster()
        print(f"✅ Cluster started: {cluster_info['n_workers']} workers")
        
        # Get status
        status = manager.get_cluster_status()
        print(f"✅ Cluster status: {status['status']}")
        print(f"   - Workers: {status['n_workers']}")
        print(f"   - Cores: {status['total_cores']}")
        print(f"   - Memory: {status['total_memory']}")
        print(f"   - Dashboard: {status['dashboard_url']}")
        
        # Scale cluster
        print("\nScaling cluster to 4 workers...")
        scaled_status = manager.scale_cluster(4)
        print(f"✅ Cluster scaled: {scaled_status['n_workers']} workers")
        
        # Stop cluster
        manager.stop_cluster()
        print("✅ Cluster stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Cluster manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_partitioner():
    """Test DataPartitioner functionality"""
    print("\nTesting DataPartitioner...")
    try:
        import pandas as pd
        import numpy as np
        from backend_db.distributed_processing import DaskClusterManager, DataPartitioner
        
        # Start cluster
        manager = DaskClusterManager(n_workers=2, memory_limit="1GB")
        manager.start_cluster()
        
        # Create partitioner
        partitioner = DataPartitioner(manager.client)
        print("✅ Partitioner created")
        
        # Create sample data
        df = pd.DataFrame(np.random.randn(1000, 10))
        print(f"✅ Created sample DataFrame: {df.shape}")
        
        # Partition data
        ddf = partitioner.partition_dataframe(df, n_partitions=4)
        print(f"✅ Data partitioned: {ddf.npartitions} partitions")
        
        # Get partition info
        info = partitioner.get_partition_info(ddf)
        print(f"✅ Partition info: {info['n_partitions']} partitions")
        
        # Cleanup
        manager.stop_cluster()
        
        return True
        
    except Exception as e:
        print(f"❌ Data partitioner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_job_queue():
    """Test JobQueue and priority system"""
    print("\nTesting JobQueue...")
    try:
        from backend_db.distributed_processing import (
            DaskClusterManager,
            ResourceManager,
            JobQueue,
            JobPriority
        )
        
        # Start cluster
        manager = DaskClusterManager(n_workers=2, memory_limit="1GB")
        manager.start_cluster()
        
        # Create resource manager and queue
        resource_manager = ResourceManager(manager.client)
        queue = JobQueue(manager.client, resource_manager)
        print("✅ Queue created")
        
        # Define test function
        def test_func(x):
            return x * 2
        
        # Enqueue jobs with different priorities
        job1 = queue.enqueue_job("job1", test_func, JobPriority.LOW, 5)
        job2 = queue.enqueue_job("job2", test_func, JobPriority.HIGH, 10)
        job3 = queue.enqueue_job("job3", test_func, JobPriority.NORMAL, 15)
        
        print(f"✅ Enqueued 3 jobs")
        
        # Get queue status
        status = queue.get_queue_status()
        print(f"✅ Queue status: {status['total_queued']} queued")
        print(f"   Priority breakdown: {status['priority_breakdown']}")
        
        # Process queue
        started = queue.process_queue(max_concurrent=2)
        print(f"✅ Started {len(started)} jobs")
        
        # Wait a bit for jobs to complete
        time.sleep(2)
        
        # Check running jobs
        completed = queue.check_running_jobs()
        print(f"✅ Completed {len(completed)} jobs")
        
        # Cleanup
        manager.stop_cluster()
        
        return True
        
    except Exception as e:
        print(f"❌ Job queue test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_progress_monitor():
    """Test ProgressMonitor functionality"""
    print("\nTesting ProgressMonitor...")
    try:
        from backend_db.distributed_processing import DaskClusterManager, ProgressMonitor
        
        # Start cluster
        manager = DaskClusterManager(n_workers=2, memory_limit="1GB")
        manager.start_cluster()
        
        # Create monitor
        monitor = ProgressMonitor(manager.client)
        print("✅ Monitor created")
        
        # Track job progress
        job_id = "test_job"
        progress = monitor.track_job_progress(job_id, total_tasks=10)
        print(f"✅ Tracking job: {job_id}")
        
        # Simulate progress updates
        for i in range(5):
            monitor.update_progress(job_id, completed=2)
            current = monitor.get_progress(job_id)
            print(f"   Progress: {current['progress_percent']:.1f}%")
        
        print("✅ Progress tracking working")
        
        # Cleanup
        manager.stop_cluster()
        
        return True
        
    except Exception as e:
        print(f"❌ Progress monitor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_resource_manager():
    """Test ResourceManager functionality"""
    print("\nTesting ResourceManager...")
    try:
        from backend_db.distributed_processing import DaskClusterManager, ResourceManager
        
        # Start cluster
        manager = DaskClusterManager(n_workers=2, memory_limit="1GB")
        manager.start_cluster()
        
        # Create resource manager
        resource_mgr = ResourceManager(manager.client)
        print("✅ Resource manager created")
        
        # Get available resources
        available = resource_mgr.get_available_resources()
        print(f"✅ Available resources:")
        print(f"   - Memory: {available['available_memory_gb']:.2f}GB")
        print(f"   - Cores: {available['available_cores']}")
        
        # Set resource limits
        job_id = "test_job"
        resource_mgr.set_resource_limits(job_id, max_memory_gb=1.0, max_cores=2)
        print(f"✅ Set resource limits for {job_id}")
        
        # Check availability
        is_available = resource_mgr.check_resource_availability(job_id)
        print(f"✅ Resources available: {is_available}")
        
        # Allocate resources
        if is_available:
            allocation = resource_mgr.allocate_resources(job_id)
            print(f"✅ Allocated resources: {allocation['allocated_memory_gb']}GB")
            
            # Release resources
            resource_mgr.release_resources(job_id)
            print(f"✅ Released resources")
        
        # Cleanup
        manager.stop_cluster()
        
        return True
        
    except Exception as e:
        print(f"❌ Resource manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Distributed Processing Cluster - Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Cluster Manager", test_cluster_manager),
        ("Data Partitioner", test_data_partitioner),
        ("Job Queue", test_job_queue),
        ("Progress Monitor", test_progress_monitor),
        ("Resource Manager", test_resource_manager),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    print(f"Finished at: {datetime.now().isoformat()}")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
