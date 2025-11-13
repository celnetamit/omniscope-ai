"""
Plugin Sandbox Service for OmniScope AI
Provides Docker-based isolated execution environment for plugins
"""

import docker
from docker.models.containers import Container
from docker.errors import DockerException, ContainerError, ImageNotFound
from typing import Dict, Any, Optional, List
import json
import tempfile
import os
import shutil
from pathlib import Path
import time


class PluginSandbox:
    """Docker-based sandbox for plugin execution"""
    
    # Resource limits
    DEFAULT_MEMORY_LIMIT = "512m"
    DEFAULT_CPU_QUOTA = 50000  # 50% of one CPU
    DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Docker images for different languages
    IMAGES = {
        'python': 'python:3.11-slim',
        'r': 'r-base:4.3.0'
    }
    
    def __init__(self):
        """Initialize Docker client"""
        try:
            self.client = docker.from_env()
            self.client.ping()
        except DockerException as e:
            raise RuntimeError(f"Failed to connect to Docker: {e}")
    
    def create_sandbox_container(
        self,
        language: str,
        plugin_id: str,
        memory_limit: str = DEFAULT_MEMORY_LIMIT,
        cpu_quota: int = DEFAULT_CPU_QUOTA,
        network_enabled: bool = False
    ) -> Dict[str, Any]:
        """
        Create a sandbox container for plugin execution
        
        Args:
            language: Programming language (python, r)
            plugin_id: Plugin ID
            memory_limit: Memory limit (e.g., "512m", "1g")
            cpu_quota: CPU quota in microseconds
            network_enabled: Whether to enable network access
        
        Returns:
            Dict: Container information
        """
        if language not in self.IMAGES:
            raise ValueError(f"Unsupported language: {language}")
        
        image = self.IMAGES[language]
        
        # Ensure image is available
        try:
            self.client.images.get(image)
        except ImageNotFound:
            print(f"Pulling Docker image: {image}")
            self.client.images.pull(image)
        
        # Container configuration
        container_name = f"plugin-{plugin_id}-{int(time.time())}"
        
        # Network configuration
        network_mode = "none" if not network_enabled else "bridge"
        
        # Create container (don't start yet)
        container = self.client.containers.create(
            image=image,
            name=container_name,
            detach=True,
            mem_limit=memory_limit,
            cpu_quota=cpu_quota,
            cpu_period=100000,  # Standard period
            network_mode=network_mode,
            read_only=False,  # Allow writing to /tmp
            security_opt=['no-new-privileges'],
            cap_drop=['ALL'],  # Drop all capabilities
            cap_add=['CHOWN', 'SETUID', 'SETGID'],  # Only essential capabilities
            pids_limit=100,  # Limit number of processes
            command='tail -f /dev/null'  # Keep container running
        )
        
        return {
            'container_id': container.id,
            'container_name': container_name,
            'image': image,
            'language': language,
            'memory_limit': memory_limit,
            'cpu_quota': cpu_quota,
            'network_enabled': network_enabled
        }
    
    def execute_in_sandbox(
        self,
        container_id: str,
        plugin_path: str,
        entry_point: str,
        input_data: Dict[str, Any],
        timeout: int = DEFAULT_TIMEOUT,
        dependencies: List[str] = None
    ) -> Dict[str, Any]:
        """
        Execute plugin in sandbox container
        
        Args:
            container_id: Container ID
            plugin_path: Path to plugin files
            entry_point: Entry point file/function
            input_data: Input data for plugin
            timeout: Execution timeout in seconds
            dependencies: List of dependencies to install
        
        Returns:
            Dict: Execution result
        """
        try:
            container = self.client.containers.get(container_id)
            
            # Start container if not running
            if container.status != 'running':
                container.start()
            
            # Create temporary directory for plugin files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy plugin files to temp directory
                if os.path.exists(plugin_path):
                    for item in os.listdir(plugin_path):
                        src = os.path.join(plugin_path, item)
                        dst = os.path.join(temp_dir, item)
                        if os.path.isfile(src):
                            shutil.copy2(src, dst)
                        elif os.path.isdir(src):
                            shutil.copytree(src, dst)
                
                # Create input data file
                input_file = os.path.join(temp_dir, 'input.json')
                with open(input_file, 'w') as f:
                    json.dump(input_data, f)
                
                # Create execution script
                exec_script = self._create_execution_script(
                    entry_point,
                    dependencies or []
                )
                script_file = os.path.join(temp_dir, 'execute.sh')
                with open(script_file, 'w') as f:
                    f.write(exec_script)
                os.chmod(script_file, 0o755)
                
                # Copy files to container
                self._copy_to_container(container, temp_dir, '/plugin')
                
                # Execute plugin
                start_time = time.time()
                exit_code, output = container.exec_run(
                    cmd='/bin/bash /plugin/execute.sh',
                    workdir='/plugin',
                    demux=True,
                    stream=False
                )
                execution_time = int((time.time() - start_time) * 1000)
                
                # Get output data
                output_data = None
                try:
                    output_file = container.exec_run(
                        'cat /plugin/output.json',
                        demux=False
                    )
                    if output_file.exit_code == 0:
                        output_data = json.loads(output_file.output.decode('utf-8'))
                except Exception:
                    pass
                
                # Parse output
                stdout = output[0].decode('utf-8') if output[0] else ''
                stderr = output[1].decode('utf-8') if output[1] else ''
                
                return {
                    'status': 'success' if exit_code == 0 else 'failure',
                    'exit_code': exit_code,
                    'output_data': output_data,
                    'stdout': stdout,
                    'stderr': stderr,
                    'execution_time': execution_time
                }
        
        except ContainerError as e:
            return {
                'status': 'error',
                'error': f"Container error: {str(e)}",
                'execution_time': 0
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'execution_time': 0
            }
    
    def _create_execution_script(
        self,
        entry_point: str,
        dependencies: List[str]
    ) -> str:
        """Create execution script for plugin"""
        script = "#!/bin/bash\nset -e\n\n"
        
        # Install dependencies
        if dependencies:
            # Detect language from entry point
            if entry_point.endswith('.py'):
                script += "# Install Python dependencies\n"
                for dep in dependencies:
                    script += f"pip install --no-cache-dir {dep} || true\n"
            elif entry_point.endswith('.R') or entry_point.endswith('.r'):
                script += "# Install R dependencies\n"
                for dep in dependencies:
                    script += f"R -e \"install.packages('{dep}', repos='https://cran.r-project.org')\" || true\n"
        
        script += "\n# Execute plugin\n"
        
        # Execute based on language
        if entry_point.endswith('.py'):
            script += f"python {entry_point}\n"
        elif entry_point.endswith('.R') or entry_point.endswith('.r'):
            script += f"Rscript {entry_point}\n"
        else:
            script += f"./{entry_point}\n"
        
        return script
    
    def _copy_to_container(
        self,
        container: Container,
        src_path: str,
        dst_path: str
    ):
        """Copy files to container"""
        import tarfile
        from io import BytesIO
        
        # Create tar archive
        tar_stream = BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            for root, dirs, files in os.walk(src_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, src_path)
                    tar.add(file_path, arcname=arcname)
        
        tar_stream.seek(0)
        
        # Copy to container
        container.put_archive(dst_path, tar_stream)
    
    def stop_container(self, container_id: str, timeout: int = 10):
        """
        Stop a sandbox container
        
        Args:
            container_id: Container ID
            timeout: Timeout in seconds
        """
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=timeout)
        except Exception as e:
            print(f"Error stopping container {container_id}: {e}")
    
    def remove_container(self, container_id: str, force: bool = True):
        """
        Remove a sandbox container
        
        Args:
            container_id: Container ID
            force: Force removal even if running
        """
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
        except Exception as e:
            print(f"Error removing container {container_id}: {e}")
    
    def get_container_stats(self, container_id: str) -> Dict[str, Any]:
        """
        Get container resource usage statistics
        
        Args:
            container_id: Container ID
        
        Returns:
            Dict: Resource usage statistics
        """
        try:
            container = self.client.containers.get(container_id)
            stats = container.stats(stream=False)
            
            # Calculate CPU percentage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
            
            # Calculate memory usage
            memory_usage = stats['memory_stats'].get('usage', 0)
            memory_limit = stats['memory_stats'].get('limit', 0)
            memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0.0
            
            return {
                'cpu_percent': round(cpu_percent, 2),
                'memory_usage': memory_usage,
                'memory_limit': memory_limit,
                'memory_percent': round(memory_percent, 2),
                'network_rx': stats['networks']['eth0']['rx_bytes'] if 'networks' in stats else 0,
                'network_tx': stats['networks']['eth0']['tx_bytes'] if 'networks' in stats else 0
            }
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def list_containers(self, plugin_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List sandbox containers
        
        Args:
            plugin_id: Filter by plugin ID
        
        Returns:
            List[Dict]: List of containers
        """
        filters = {'name': 'plugin-'}
        if plugin_id:
            filters['name'] = f'plugin-{plugin_id}-'
        
        containers = self.client.containers.list(all=True, filters=filters)
        
        return [
            {
                'id': c.id,
                'name': c.name,
                'status': c.status,
                'image': c.image.tags[0] if c.image.tags else c.image.id,
                'created': c.attrs['Created']
            }
            for c in containers
        ]
    
    def cleanup_old_containers(self, max_age_hours: int = 24):
        """
        Clean up old sandbox containers
        
        Args:
            max_age_hours: Maximum age in hours
        """
        import datetime
        
        containers = self.list_containers()
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=max_age_hours)
        
        for container_info in containers:
            created = datetime.datetime.fromisoformat(
                container_info['created'].replace('Z', '+00:00')
            )
            
            if created < cutoff_time:
                print(f"Removing old container: {container_info['name']}")
                self.remove_container(container_info['id'])
