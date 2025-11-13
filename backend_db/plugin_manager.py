"""
Plugin Manager Service for OmniScope AI
Handles plugin lifecycle management, metadata storage, and dependency resolution
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json
import os
import shutil
from pathlib import Path

from .models import Base
from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, Integer
from sqlalchemy.sql import func


class Plugin(Base):
    """Model for plugin metadata"""
    __tablename__ = "plugins"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    version = Column(String(50), nullable=False)
    author = Column(String(255))
    description = Column(Text)
    language = Column(String(20), nullable=False)  # python, r
    entry_point = Column(String(500), nullable=False)
    dependencies = Column(JSON)  # List of dependency specifications
    permissions = Column(JSON)  # List of required permissions
    config = Column(JSON)  # Plugin configuration
    enabled = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)  # Security verification status
    install_path = Column(String(500))
    installed_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_used = Column(DateTime)
    usage_count = Column(Integer, default=0)
    rating = Column(Integer)  # Average rating from marketplace
    downloads = Column(Integer, default=0)


class PluginDependency(Base):
    """Model for plugin dependencies"""
    __tablename__ = "plugin_dependencies"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plugin_id = Column(String, nullable=False)
    dependency_name = Column(String(255), nullable=False)
    dependency_version = Column(String(50))
    dependency_type = Column(String(50))  # plugin, package, system
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


class PluginExecution(Base):
    """Model for plugin execution history"""
    __tablename__ = "plugin_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plugin_id = Column(String, nullable=False)
    user_id = Column(String)
    input_data = Column(JSON)
    output_data = Column(JSON)
    status = Column(String(50), nullable=False)  # success, failure, error
    error_message = Column(Text)
    execution_time = Column(Integer)  # milliseconds
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)


class PluginManagerService:
    """Service for managing plugin lifecycle and operations"""
    
    PLUGIN_BASE_DIR = os.getenv("PLUGIN_DIR", "./plugins")
    
    @staticmethod
    def _ensure_plugin_directory():
        """Ensure plugin directory exists"""
        os.makedirs(PluginManagerService.PLUGIN_BASE_DIR, exist_ok=True)
    
    @staticmethod
    def install_plugin(
        db: Session,
        name: str,
        version: str,
        author: str,
        description: str,
        language: str,
        entry_point: str,
        dependencies: List[Dict[str, str]] = None,
        permissions: List[str] = None,
        config: Dict[str, Any] = None,
        plugin_files: Dict[str, bytes] = None
    ) -> Plugin:
        """
        Install a new plugin
        
        Args:
            db: Database session
            name: Plugin name
            version: Plugin version (semantic versioning)
            author: Plugin author
            description: Plugin description
            language: Programming language (python, r)
            entry_point: Entry point file/function
            dependencies: List of dependencies
            permissions: List of required permissions
            config: Plugin configuration
            plugin_files: Dictionary of filename -> file content
        
        Returns:
            Plugin: Installed plugin object
        """
        PluginManagerService._ensure_plugin_directory()
        
        # Check if plugin already exists
        existing = db.query(Plugin).filter(Plugin.name == name).first()
        if existing:
            raise ValueError(f"Plugin '{name}' already installed. Use update instead.")
        
        # Create plugin directory
        plugin_id = str(uuid.uuid4())
        plugin_path = os.path.join(PluginManagerService.PLUGIN_BASE_DIR, plugin_id)
        os.makedirs(plugin_path, exist_ok=True)
        
        # Save plugin files
        if plugin_files:
            for filename, content in plugin_files.items():
                file_path = os.path.join(plugin_path, filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wb') as f:
                    f.write(content)
        
        # Create plugin record
        plugin = Plugin(
            id=plugin_id,
            name=name,
            version=version,
            author=author,
            description=description,
            language=language,
            entry_point=entry_point,
            dependencies=dependencies or [],
            permissions=permissions or [],
            config=config or {},
            enabled=False,
            verified=False,
            install_path=plugin_path
        )
        
        db.add(plugin)
        
        # Create dependency records
        if dependencies:
            for dep in dependencies:
                dependency = PluginDependency(
                    plugin_id=plugin_id,
                    dependency_name=dep.get('name'),
                    dependency_version=dep.get('version'),
                    dependency_type=dep.get('type', 'package'),
                    resolved=False
                )
                db.add(dependency)
        
        db.commit()
        db.refresh(plugin)
        
        return plugin
    
    @staticmethod
    def uninstall_plugin(db: Session, plugin_id: str) -> bool:
        """
        Uninstall a plugin
        
        Args:
            db: Database session
            plugin_id: Plugin ID
        
        Returns:
            bool: True if successful
        """
        plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
        if not plugin:
            raise ValueError(f"Plugin with ID '{plugin_id}' not found")
        
        # Remove plugin files
        if plugin.install_path and os.path.exists(plugin.install_path):
            shutil.rmtree(plugin.install_path)
        
        # Remove dependency records
        db.query(PluginDependency).filter(
            PluginDependency.plugin_id == plugin_id
        ).delete()
        
        # Remove execution history
        db.query(PluginExecution).filter(
            PluginExecution.plugin_id == plugin_id
        ).delete()
        
        # Remove plugin record
        db.delete(plugin)
        db.commit()
        
        return True
    
    @staticmethod
    def enable_plugin(db: Session, plugin_id: str) -> Plugin:
        """
        Enable a plugin
        
        Args:
            db: Database session
            plugin_id: Plugin ID
        
        Returns:
            Plugin: Updated plugin object
        """
        plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
        if not plugin:
            raise ValueError(f"Plugin with ID '{plugin_id}' not found")
        
        # Check if dependencies are resolved
        unresolved = db.query(PluginDependency).filter(
            and_(
                PluginDependency.plugin_id == plugin_id,
                PluginDependency.resolved == False
            )
        ).all()
        
        if unresolved:
            dep_names = [d.dependency_name for d in unresolved]
            raise ValueError(
                f"Cannot enable plugin. Unresolved dependencies: {', '.join(dep_names)}"
            )
        
        plugin.enabled = True
        db.commit()
        db.refresh(plugin)
        
        return plugin
    
    @staticmethod
    def disable_plugin(db: Session, plugin_id: str) -> Plugin:
        """
        Disable a plugin
        
        Args:
            db: Database session
            plugin_id: Plugin ID
        
        Returns:
            Plugin: Updated plugin object
        """
        plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
        if not plugin:
            raise ValueError(f"Plugin with ID '{plugin_id}' not found")
        
        plugin.enabled = False
        db.commit()
        db.refresh(plugin)
        
        return plugin
    
    @staticmethod
    def get_plugin(db: Session, plugin_id: str) -> Optional[Plugin]:
        """Get plugin by ID"""
        return db.query(Plugin).filter(Plugin.id == plugin_id).first()
    
    @staticmethod
    def get_plugin_by_name(db: Session, name: str) -> Optional[Plugin]:
        """Get plugin by name"""
        return db.query(Plugin).filter(Plugin.name == name).first()
    
    @staticmethod
    def list_plugins(
        db: Session,
        enabled_only: bool = False,
        language: Optional[str] = None
    ) -> List[Plugin]:
        """
        List all plugins
        
        Args:
            db: Database session
            enabled_only: Only return enabled plugins
            language: Filter by language
        
        Returns:
            List[Plugin]: List of plugins
        """
        query = db.query(Plugin)
        
        if enabled_only:
            query = query.filter(Plugin.enabled == True)
        
        if language:
            query = query.filter(Plugin.language == language)
        
        return query.order_by(Plugin.name).all()
    
    @staticmethod
    def resolve_dependencies(db: Session, plugin_id: str) -> Dict[str, Any]:
        """
        Resolve plugin dependencies
        
        Args:
            db: Database session
            plugin_id: Plugin ID
        
        Returns:
            Dict: Resolution status and details
        """
        plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
        if not plugin:
            raise ValueError(f"Plugin with ID '{plugin_id}' not found")
        
        dependencies = db.query(PluginDependency).filter(
            PluginDependency.plugin_id == plugin_id
        ).all()
        
        resolution_results = {
            'plugin_id': plugin_id,
            'plugin_name': plugin.name,
            'total_dependencies': len(dependencies),
            'resolved': 0,
            'unresolved': 0,
            'details': []
        }
        
        for dep in dependencies:
            result = {
                'name': dep.dependency_name,
                'version': dep.dependency_version,
                'type': dep.dependency_type,
                'status': 'unresolved'
            }
            
            # Check if dependency is another plugin
            if dep.dependency_type == 'plugin':
                dep_plugin = db.query(Plugin).filter(
                    Plugin.name == dep.dependency_name
                ).first()
                
                if dep_plugin and dep_plugin.enabled:
                    dep.resolved = True
                    result['status'] = 'resolved'
                    resolution_results['resolved'] += 1
                else:
                    result['status'] = 'unresolved'
                    result['message'] = 'Required plugin not installed or enabled'
                    resolution_results['unresolved'] += 1
            
            # For package dependencies, mark as resolved (actual resolution happens in sandbox)
            elif dep.dependency_type == 'package':
                dep.resolved = True
                result['status'] = 'resolved'
                result['message'] = 'Will be installed in sandbox environment'
                resolution_results['resolved'] += 1
            
            resolution_results['details'].append(result)
        
        db.commit()
        
        return resolution_results
    
    @staticmethod
    def update_plugin_config(
        db: Session,
        plugin_id: str,
        config: Dict[str, Any]
    ) -> Plugin:
        """
        Update plugin configuration
        
        Args:
            db: Database session
            plugin_id: Plugin ID
            config: New configuration
        
        Returns:
            Plugin: Updated plugin object
        """
        plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
        if not plugin:
            raise ValueError(f"Plugin with ID '{plugin_id}' not found")
        
        plugin.config = config
        db.commit()
        db.refresh(plugin)
        
        return plugin
    
    @staticmethod
    def record_execution(
        db: Session,
        plugin_id: str,
        user_id: Optional[str],
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]],
        status: str,
        error_message: Optional[str] = None,
        execution_time: Optional[int] = None
    ) -> PluginExecution:
        """
        Record plugin execution
        
        Args:
            db: Database session
            plugin_id: Plugin ID
            user_id: User ID
            input_data: Input data
            output_data: Output data
            status: Execution status
            error_message: Error message if failed
            execution_time: Execution time in milliseconds
        
        Returns:
            PluginExecution: Execution record
        """
        execution = PluginExecution(
            plugin_id=plugin_id,
            user_id=user_id,
            input_data=input_data,
            output_data=output_data,
            status=status,
            error_message=error_message,
            execution_time=execution_time,
            completed_at=datetime.utcnow() if status in ['success', 'failure', 'error'] else None
        )
        
        db.add(execution)
        
        # Update plugin usage statistics
        plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
        if plugin:
            plugin.usage_count += 1
            plugin.last_used = datetime.utcnow()
        
        db.commit()
        db.refresh(execution)
        
        return execution
    
    @staticmethod
    def get_plugin_executions(
        db: Session,
        plugin_id: str,
        limit: int = 100
    ) -> List[PluginExecution]:
        """
        Get plugin execution history
        
        Args:
            db: Database session
            plugin_id: Plugin ID
            limit: Maximum number of records
        
        Returns:
            List[PluginExecution]: Execution history
        """
        return db.query(PluginExecution).filter(
            PluginExecution.plugin_id == plugin_id
        ).order_by(
            PluginExecution.started_at.desc()
        ).limit(limit).all()
