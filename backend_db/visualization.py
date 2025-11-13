"""
Visualization API endpoints for OmniScope AI
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
import json
from modules.visualization_module import (
    ProteinStructureParser,
    NetworkGraphGenerator,
    DimensionalityReduction,
    prepare_omics_data_for_visualization
)

router = APIRouter(prefix="/api/visualization", tags=["visualization"])


# Request/Response Models
class ProteinLoadRequest(BaseModel):
    pdb_id: Optional[str] = Field(None, description="PDB ID to fetch from RCSB")
    pdb_content: Optional[str] = Field(None, description="PDB file content")
    structure_id: str = Field(default="structure", description="Structure identifier")


class ProteinLoadResponse(BaseModel):
    structure_id: str
    pdb_content: str
    atoms: List[Dict[str, Any]]
    residues: List[Dict[str, Any]]
    chains: List[Dict[str, Any]]
    atom_count: int
    residue_count: int
    chain_count: int


class NetworkNode(BaseModel):
    id: str
    label: Optional[str] = None
    type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NetworkEdge(BaseModel):
    source: str
    target: str
    weight: Optional[float] = 1.0
    type: Optional[str] = None


class NetworkGenerateRequest(BaseModel):
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]


class NetworkGenerateResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    node_count: int
    edge_count: int
    density: float
    is_connected: bool
    centrality_metrics: Optional[Dict[str, Dict[str, float]]] = None


class DimensionalityReductionRequest(BaseModel):
    data: List[List[float]] = Field(..., description="Data matrix (samples x features)")
    method: str = Field(default="pca", description="Method: pca, tsne, or umap")
    metadata: Optional[List[Any]] = Field(None, description="Sample metadata for coloring")
    metadata_name: Optional[str] = Field("group", description="Name of metadata field")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Method-specific parameters")


class DimensionalityReductionResponse(BaseModel):
    method: str
    coordinates: List[List[float]]
    n_samples: int
    n_features: int
    metadata: Optional[Dict[str, Any]] = None
    explained_variance: Optional[List[float]] = None
    total_variance_explained: Optional[float] = None
    perplexity: Optional[float] = None
    kl_divergence: Optional[float] = None
    n_neighbors: Optional[int] = None


class ExportRequest(BaseModel):
    visualization_type: str = Field(..., description="Type: protein, network, or dimensionality")
    format: str = Field(..., description="Format: png, svg, or html")
    data: Dict[str, Any] = Field(..., description="Visualization data")


# API Endpoints

@router.post("/protein/load", response_model=ProteinLoadResponse)
async def load_protein_structure(request: ProteinLoadRequest):
    """
    Load and parse protein structure from PDB ID or content
    
    Requirements: 3.1, 3.3
    """
    try:
        parser = ProteinStructureParser()
        
        # Get PDB content
        if request.pdb_id:
            pdb_content = parser.fetch_pdb_from_id(request.pdb_id)
        elif request.pdb_content:
            pdb_content = request.pdb_content
        else:
            raise HTTPException(
                status_code=400,
                detail="Either pdb_id or pdb_content must be provided"
            )
        
        # Parse structure
        structure_data = parser.parse_pdb_file(pdb_content, request.structure_id)
        
        return ProteinLoadResponse(**structure_data)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/protein/summary")
async def get_protein_summary(request: ProteinLoadRequest):
    """Get summary statistics of protein structure"""
    try:
        parser = ProteinStructureParser()
        
        # Get PDB content
        if request.pdb_id:
            pdb_content = parser.fetch_pdb_from_id(request.pdb_id)
        elif request.pdb_content:
            pdb_content = request.pdb_content
        else:
            raise HTTPException(
                status_code=400,
                detail="Either pdb_id or pdb_content must be provided"
            )
        
        # Get summary
        summary = parser.get_structure_summary(pdb_content)
        
        return summary
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/network/generate", response_model=NetworkGenerateResponse)
async def generate_network_graph(request: NetworkGenerateRequest):
    """
    Generate 3D network graph from nodes and edges
    
    Requirements: 3.2
    """
    try:
        generator = NetworkGraphGenerator()
        
        # Convert Pydantic models to dicts
        nodes = [node.model_dump() for node in request.nodes]
        edges = [edge.model_dump() for edge in request.edges]
        
        # Flatten metadata into node dict
        for node in nodes:
            if node.get('metadata'):
                node.update(node.pop('metadata'))
        
        # Generate network
        network_data = generator.create_network_from_interactions(nodes, edges)
        
        # Calculate centrality metrics
        try:
            centrality_metrics = generator.calculate_centrality_metrics()
            network_data["centrality_metrics"] = centrality_metrics
        except Exception as e:
            # Centrality calculation might fail for some graphs
            network_data["centrality_metrics"] = None
        
        return NetworkGenerateResponse(**network_data)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/dimensionality-reduction", response_model=DimensionalityReductionResponse)
async def perform_dimensionality_reduction(request: DimensionalityReductionRequest):
    """
    Perform dimensionality reduction to 3D
    
    Requirements: 3.4
    """
    try:
        reducer = DimensionalityReduction()
        
        # Convert data to numpy array
        data_array = np.array(request.data)
        
        if data_array.ndim != 2:
            raise HTTPException(
                status_code=400,
                detail="Data must be a 2D array (samples x features)"
            )
        
        if data_array.shape[1] < 3:
            raise HTTPException(
                status_code=400,
                detail="Data must have at least 3 features for dimensionality reduction"
            )
        
        # Perform reduction
        result = reducer.reduce_to_3d(
            data_array,
            method=request.method,
            **request.parameters
        )
        
        # Add metadata if provided
        if request.metadata:
            if len(request.metadata) != data_array.shape[0]:
                raise HTTPException(
                    status_code=400,
                    detail="Metadata length must match number of samples"
                )
            result = reducer.add_metadata_coloring(
                result,
                request.metadata,
                request.metadata_name
            )
        
        return DimensionalityReductionResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ImportError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/export")
async def export_visualization(request: ExportRequest):
    """
    Export visualization in specified format
    
    Requirements: 3.5
    
    Note: This endpoint returns metadata for client-side export.
    Actual rendering is done in the frontend.
    """
    try:
        supported_formats = ["png", "svg", "html"]
        if request.format not in supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Format must be one of: {', '.join(supported_formats)}"
            )
        
        supported_types = ["protein", "network", "dimensionality"]
        if request.visualization_type not in supported_types:
            raise HTTPException(
                status_code=400,
                detail=f"Type must be one of: {', '.join(supported_types)}"
            )
        
        # Return export configuration
        # Actual export is handled client-side using canvas.toBlob, etc.
        return {
            "visualization_type": request.visualization_type,
            "format": request.format,
            "data": request.data,
            "export_ready": True,
            "instructions": {
                "png": "Use canvas.toBlob() or renderer.domElement.toDataURL()",
                "svg": "Use SVGRenderer or serialize SVG elements",
                "html": "Serialize complete scene with embedded data"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "visualization",
        "features": [
            "protein_structure_viewer",
            "network_graph_3d",
            "dimensionality_reduction"
        ]
    }
