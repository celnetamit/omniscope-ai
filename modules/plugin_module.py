"""
Plugin Management Module for OmniScope AI
Provides API endpoints for plugin installation, management, and execution
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
import tempfile
import os
import shutil
import tarfile
from datetime import datetime

from backend_db.database import get_db
from backend_db.plugin_manager import PluginManagerService, Plugin, PluginExecution
from backend_db.plugin_sandbox import PluginSandbox
from backend_db.plugin_security import SecurityScanner
from backend_db.plugin_api import PluginAPIGateway, PluginContext, PluginInput, PluginOutput, setup_default_validators
from backend_db.plugin_marketplace import MarketplaceService, MarketplacePlugin
from backend_db.plugin_version import PluginVersionManager, SemanticVersion
from backend_db.plugin_sdk import PluginSDK

router = APIRouter(prefix="/api/plugins", tags=["Plugin System"])

# Initialize plugin gateway
plugin_gateway = PluginAPIGateway()
setup_default_validators(plugin_gateway)


# Pydantic models
class PluginInstallRequest(BaseModel):
    name: str
    version: str
    author: str
    description: str
    language: str = Field(..., pattern="^(python|r)$")
    entry_point: str
    dependencies: List[Dict[str, str]] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)


class PluginExecuteRequest(BaseModel):
    input_data: Dict[str, Any]
    parameters: Dict[str, Any] = Field(default_factory=dict)
    extension_point: str
    timeout: Optional[int] = 300


class PluginSearchRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    language: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    extension_point: Optional[str] = None
    verified_only: bool = False
    sort_by: str = "downloads"
    limit: int = 50
    offset: int = 0


class PluginRatingRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)


class PluginReviewRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: str
    review_text: str


class PluginCreateRequest(BaseModel):
    name: str
    language: str = Field(..., pattern="^(python|r)$")
    author: str
    description: str
    author_email: Optional[str] = None
    category: str = "analysis"
    tags: List[str] = Field(default_factory=list)
    extension_points: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)


# Plugin Management Endpoints

@router.post("/install")
async def install_plugin(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Install a plugin from uploaded package
    
    Upload a .tar.gz package containing plugin files and manifest.json
    """
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded file
            package_path = os.path.join(temp_dir, file.filename)
            with open(package_path, 'wb') as f:
                content = await file.read()
                f.write(content)
            
            # Extract package
            extract_dir = os.path.join(temp_dir, 'extracted')
            os.makedirs(extract_dir)
            
            with tarfile.open(package_path, 'r:gz') as tar:
                tar.extractall(extract_dir)
            
            # Find manifest.json
            manifest_path = None
            for root, dirs, files in os.walk(extract_dir):
                if 'manifest.json' in files:
                    manifest_path = os.path.join(root, 'manifest.json')
                    plugin_dir = root
                    break
            
            if not manifest_path:
                raise HTTPException(status_code=400, detail="manifest.json not found in package")
            
            # Validate manifest
            is_valid, error = PluginSDK.validate_manifest(manifest_path)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"Invalid manifest: {error}")
            
            # Load manifest
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Security scan
            scan_results = SecurityScanner.scan_plugin(
                plugin_dir,
                manifest['language'],
                manifest.get('dependencies', [])
            )
            
            if scan_results['overall_status'] == 'unsafe':
                raise HTTPException(
                    status_code=400,
                    detail=f"Security scan failed: {len(scan_results['issues'])} critical issues found"
                )
            
            # Read plugin files
            plugin_files = {}
            for root, dirs, files in os.walk(plugin_dir):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    rel_path = os.path.relpath(file_path, plugin_dir)
                    with open(file_path, 'rb') as f:
                        plugin_files[rel_path] = f.read()
            
            # Install plugin
            plugin = PluginManagerService.install_plugin(
                db=db,
                name=manifest['name'],
                version=manifest['version'],
                author=manifest['author'],
                description=manifest['description'],
                language=manifest['language'],
                entry_point=manifest['entry_point'],
                dependencies=manifest.get('dependencies', []),
                permissions=manifest.get('permissions', []),
                config=manifest.get('config', {}),
                plugin_files=plugin_files
            )
            
            # Resolve dependencies
            resolution = PluginManagerService.resolve_dependencies(db, plugin.id)
            
            return {
                "message": "Plugin installed successfully",
                "plugin_id": plugin.id,
                "name": plugin.name,
                "version": plugin.version,
                "security_scan": scan_results,
                "dependency_resolution": resolution
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{plugin_id}")
async def uninstall_plugin(
    plugin_id: str,
    db: Session = Depends(get_db)
):
    """Uninstall a plugin"""
    try:
        success = PluginManagerService.uninstall_plugin(db, plugin_id)
        return {"message": "Plugin uninstalled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{plugin_id}/enable")
async def enable_plugin(
    plugin_id: str,
    db: Session = Depends(get_db)
):
    """Enable a plugin"""
    try:
        plugin = PluginManagerService.enable_plugin(db, plugin_id)
        return {
            "message": "Plugin enabled successfully",
            "plugin_id": plugin.id,
            "name": plugin.name,
            "enabled": plugin.enabled
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{plugin_id}/disable")
async def disable_plugin(
    plugin_id: str,
    db: Session = Depends(get_db)
):
    """Disable a plugin"""
    try:
        plugin = PluginManagerService.disable_plugin(db, plugin_id)
        return {
            "message": "Plugin disabled successfully",
            "plugin_id": plugin.id,
            "name": plugin.name,
            "enabled": plugin.enabled
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_plugins(
    enabled_only: bool = False,
    language: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all installed plugins"""
    try:
        plugins = PluginManagerService.list_plugins(db, enabled_only, language)
        return {
            "plugins": [
                {
                    "id": p.id,
                    "name": p.name,
                    "version": p.version,
                    "author": p.author,
                    "description": p.description,
                    "language": p.language,
                    "enabled": p.enabled,
                    "verified": p.verified,
                    "usage_count": p.usage_count,
                    "last_used": p.last_used.isoformat() if p.last_used else None,
                    "installed_at": p.installed_at.isoformat()
                }
                for p in plugins
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{plugin_id}")
async def get_plugin(
    plugin_id: str,
    db: Session = Depends(get_db)
):
    """Get plugin details"""
    try:
        plugin = PluginManagerService.get_plugin(db, plugin_id)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        return {
            "id": plugin.id,
            "name": plugin.name,
            "version": plugin.version,
            "author": plugin.author,
            "description": plugin.description,
            "language": plugin.language,
            "entry_point": plugin.entry_point,
            "dependencies": plugin.dependencies,
            "permissions": plugin.permissions,
            "config": plugin.config,
            "enabled": plugin.enabled,
            "verified": plugin.verified,
            "usage_count": plugin.usage_count,
            "last_used": plugin.last_used.isoformat() if plugin.last_used else None,
            "installed_at": plugin.installed_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{plugin_id}/execute")
async def execute_plugin(
    plugin_id: str,
    request: PluginExecuteRequest,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Execute a plugin"""
    try:
        # Get plugin
        plugin = PluginManagerService.get_plugin(db, plugin_id)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        if not plugin.enabled:
            raise HTTPException(status_code=400, detail="Plugin is not enabled")
        
        # Create sandbox
        sandbox = PluginSandbox()
        
        # Create container
        container_info = sandbox.create_sandbox_container(
            language=plugin.language,
            plugin_id=plugin_id,
            network_enabled=False
        )
        
        try:
            # Prepare input
            plugin_input = {
                'context': {
                    'plugin_id': plugin.id,
                    'plugin_name': plugin.name,
                    'config': plugin.config,
                    'permissions': plugin.permissions
                },
                'data': request.input_data,
                'parameters': request.parameters
            }
            
            # Execute in sandbox
            result = sandbox.execute_in_sandbox(
                container_id=container_info['container_id'],
                plugin_path=plugin.install_path,
                entry_point=plugin.entry_point,
                input_data=plugin_input,
                timeout=request.timeout,
                dependencies=[dep.get('name') for dep in plugin.dependencies] if plugin.dependencies else None
            )
            
            # Record execution
            PluginManagerService.record_execution(
                db=db,
                plugin_id=plugin_id,
                user_id=user_id,
                input_data=request.input_data,
                output_data=result.get('output_data'),
                status=result['status'],
                error_message=result.get('stderr') if result['status'] != 'success' else None,
                execution_time=result.get('execution_time')
            )
            
            return {
                "status": result['status'],
                "output": result.get('output_data'),
                "execution_time": result.get('execution_time'),
                "logs": result.get('stdout', '').split('\n') if result.get('stdout') else [],
                "errors": result.get('stderr', '').split('\n') if result.get('stderr') else []
            }
        
        finally:
            # Cleanup container
            sandbox.remove_container(container_info['container_id'])
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{plugin_id}/executions")
async def get_plugin_executions(
    plugin_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get plugin execution history"""
    try:
        executions = PluginManagerService.get_plugin_executions(db, plugin_id, limit)
        return {
            "executions": [
                {
                    "id": e.id,
                    "status": e.status,
                    "execution_time": e.execution_time,
                    "started_at": e.started_at.isoformat(),
                    "completed_at": e.completed_at.isoformat() if e.completed_at else None,
                    "error_message": e.error_message
                }
                for e in executions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Marketplace Endpoints

@router.post("/marketplace/search")
async def search_marketplace(
    request: PluginSearchRequest,
    db: Session = Depends(get_db)
):
    """Search plugin marketplace"""
    try:
        plugins = MarketplaceService.search_plugins(
            db=db,
            query=request.query,
            category=request.category,
            language=request.language,
            tags=request.tags,
            extension_point=request.extension_point,
            verified_only=request.verified_only,
            sort_by=request.sort_by,
            limit=request.limit,
            offset=request.offset
        )
        
        return {
            "plugins": [
                {
                    "id": p.id,
                    "name": p.name,
                    "version": p.version,
                    "author": p.author,
                    "description": p.description,
                    "language": p.language,
                    "category": p.category,
                    "downloads": p.downloads,
                    "rating_average": p.rating_average,
                    "rating_count": p.rating_count,
                    "verified": p.verified,
                    "featured": p.featured
                }
                for p in plugins
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/marketplace/featured")
async def get_featured_plugins(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get featured plugins"""
    try:
        plugins = MarketplaceService.get_featured_plugins(db, limit)
        return {
            "plugins": [
                {
                    "id": p.id,
                    "name": p.name,
                    "version": p.version,
                    "author": p.author,
                    "description": p.description,
                    "rating_average": p.rating_average,
                    "downloads": p.downloads
                }
                for p in plugins
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/marketplace/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get all plugin categories"""
    try:
        categories = MarketplaceService.get_categories(db)
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{plugin_id}/rate")
async def rate_plugin(
    plugin_id: str,
    request: PluginRatingRequest,
    user_id: str = "anonymous",
    db: Session = Depends(get_db)
):
    """Rate a plugin"""
    try:
        rating = MarketplaceService.rate_plugin(db, plugin_id, user_id, request.rating)
        return {
            "message": "Plugin rated successfully",
            "rating": request.rating
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{plugin_id}/review")
async def add_review(
    plugin_id: str,
    request: PluginReviewRequest,
    user_id: str = "anonymous",
    db: Session = Depends(get_db)
):
    """Add a plugin review"""
    try:
        review = MarketplaceService.add_review(
            db, plugin_id, user_id,
            request.rating, request.title, request.review_text
        )
        return {
            "message": "Review added successfully",
            "review_id": review.id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# SDK Endpoints

@router.post("/sdk/create")
async def create_plugin_project(request: PluginCreateRequest):
    """Create a new plugin project using SDK"""
    try:
        project_dir = PluginSDK.create_plugin_project(
            name=request.name,
            language=request.language,
            author=request.author,
            description=request.description,
            author_email=request.author_email,
            category=request.category,
            tags=request.tags,
            extension_points=request.extension_points,
            dependencies=request.dependencies,
            permissions=request.permissions
        )
        
        return {
            "message": "Plugin project created successfully",
            "project_dir": project_dir
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/extension-points")
async def get_extension_points():
    """Get available extension points"""
    return {
        "extension_points": plugin_gateway.EXTENSION_POINTS
    }
