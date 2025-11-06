import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Define Pydantic models for request/response bodies
class Node(BaseModel):
    id: str
    type: str
    position: Dict[str, float]

class Edge(BaseModel):
    id: str
    source: str
    target: str

class PipelineJSON(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

class SavePipelineRequest(BaseModel):
    pipeline_id: Optional[str] = None
    project_id: str
    name: str
    pipeline_json: PipelineJSON

class SavePipelineResponse(BaseModel):
    pipeline_id: str
    status: str
    message: str

class LoadPipelineResponse(BaseModel):
    pipeline_id: str
    project_id: str
    name: str
    pipeline_json: PipelineJSON
    created_at: str

class PipelineListItem(BaseModel):
    pipeline_id: str
    name: str

class ListPipelinesResponse(BaseModel):
    pipelines: List[PipelineListItem]

class SuggestionRequest(BaseModel):
    pipeline_json: PipelineJSON

class Suggestion(BaseModel):
    node_type: str
    reason: str

class SuggestionResponse(BaseModel):
    suggestions: List[Suggestion]

# In-memory storage for pipelines
# In a production environment, this would be replaced with a proper database
pipelines_db: Dict[str, Dict[str, Any]] = {}

# AI Co-pilot suggestion logic
def get_suggestions(pipeline_json: PipelineJSON) -> List[Suggestion]:
    """
    Analyzes the current pipeline state and returns a list of suggested next nodes to add.
    This is a rule-based system that follows the specified logic.
    """
    suggestions = []
    
    # Get all node types in the pipeline
    node_types = [node.type for node in pipeline_json.nodes]
    
    # Create a mapping from node ID to node for easier lookup
    node_map = {node.id: node for node in pipeline_json.nodes}
    
    # Create sets of source and target node IDs from edges
    source_ids = {edge.source for edge in pipeline_json.edges}
    target_ids = {edge.target for edge in pipeline_json.edges}
    
    # Rule 1: If the pipeline contains an UploadGenomicsData node that is not connected to anything,
    # suggest NormalizeRNASeq and QCProteomics
    upload_genomics_nodes = [node for node in pipeline_json.nodes if node.type == "UploadGenomicsData"]
    for node in upload_genomics_nodes:
        # Check if this node has outgoing edges
        has_outgoing = node.id in source_ids
        if not has_outgoing:
            suggestions.append(Suggestion(
                node_type="NormalizeRNASeq",
                reason="You have uploaded a genomics data source. Normalization is the recommended next step to prepare the data for analysis."
            ))
            suggestions.append(Suggestion(
                node_type="QCProteomics",
                reason="You have uploaded a proteomics data source. A quality control check can help identify outliers and technical variations."
            ))
    
    # If no suggestions from the above rule, check other rules
    if not suggestions:
        # Rule 2: If the pipeline contains a NormalizeRNASeq node, suggest IntegrateMOFAPlus
        if "NormalizeRNASeq" in node_types:
            suggestions.append(Suggestion(
                node_type="IntegrateMOFAPlus",
                reason="You have normalized RNA-seq data. Integration with MOFA+ can help identify shared factors across omics data."
            ))
        
        # Rule 3: If the pipeline contains an IntegrateMOFAPlus node, suggest training models
        elif "IntegrateMOFAPlus" in node_types:
            suggestions.append(Suggestion(
                node_type="TrainXGBoostModel",
                reason="You have integrated data with MOFA+. Training an XGBoost model can help identify predictive features."
            ))
            suggestions.append(Suggestion(
                node_type="TrainRandomForestModel",
                reason="You have integrated data with MOFA+. Training a Random Forest model can help identify predictive features."
            ))
        
        # Default: Suggest a generic "Data Visualization" node
        else:
            suggestions.append(Suggestion(
                node_type="DataVisualization",
                reason="Consider adding a data visualization node to explore your data."
            ))
    
    return suggestions

# Pipeline validation logic
def validate_pipeline(pipeline_json: PipelineJSON) -> List[str]:
    """
    Performs basic validation on the pipeline structure.
    Returns a list of warning messages.
    """
    warnings = []
    
    # Create a mapping from node ID to node for easier lookup
    node_map = {node.id: node for node in pipeline_json.nodes}
    
    # Create sets of source and target node IDs from edges
    source_ids = {edge.source for edge in pipeline_json.edges}
    target_ids = {edge.target for edge in pipeline_json.edges}
    
    # Check if any edge references a non-existent node
    for edge in pipeline_json.edges:
        if edge.source not in node_map:
            warnings.append(f"Edge '{edge.id}' references a non-existent source node: {edge.source}")
        if edge.target not in node_map:
            warnings.append(f"Edge '{edge.id}' references a non-existent target node: {edge.target}")
    
    # Check if any Upload... node is a source (has no incoming edges)
    upload_nodes = [node for node in pipeline_json.nodes if node.type.startswith("Upload")]
    for node in upload_nodes:
        if node.id not in target_ids:
            warnings.append(f"Upload node '{node.type}' (ID: {node.id}) is not connected to any other nodes.")
    
    # Check for circular dependencies
    def has_cycle(node_id: str, visited: Set[str], rec_stack: Set[str]) -> bool:
        """
        Helper function to detect cycles in the graph using DFS.
        """
        visited.add(node_id)
        rec_stack.add(node_id)
        
        # Get all nodes that this node has edges to
        neighbors = [edge.target for edge in pipeline_json.edges if edge.source == node_id]
        
        for neighbor in neighbors:
            if neighbor not in visited:
                if has_cycle(neighbor, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(node_id)
        return False
    
    # Check for cycles starting from each node
    visited = set()
    for node in pipeline_json.nodes:
        if node.id not in visited:
            if has_cycle(node.id, visited, set()):
                warnings.append(f"Cycle detected in the pipeline starting from node '{node.type}' (ID: {node.id})")
                break
    
    return warnings

# Create the APIRouter
router = APIRouter()

# Define the routes
@router.post("/save", response_model=SavePipelineResponse)
async def save_pipeline(request: SavePipelineRequest):
    """
    Saves a pipeline's structure. If a pipeline_id is provided in the body, it updates the existing pipeline.
    If not, it creates a new one.
    """
    # Validate the pipeline
    warnings = validate_pipeline(request.pipeline_json)
    
    # Generate a new pipeline_id if not provided
    pipeline_id = request.pipeline_id or str(uuid.uuid4())
    
    # Save the pipeline
    pipelines_db[pipeline_id] = {
        "pipeline_id": pipeline_id,
        "project_id": request.project_id,
        "name": request.name,
        "pipeline_json": request.pipeline_json.dict(),
        "created_at": datetime.now().isoformat(),
        "warnings": warnings
    }
    
    # Log warnings for debugging
    if warnings:
        print(f"Warnings for pipeline {pipeline_id}:")
        for warning in warnings:
            print(f"  - {warning}")
    
    return SavePipelineResponse(
        pipeline_id=pipeline_id,
        status="saved",
        message=f"Pipeline saved successfully. {len(warnings)} warning(s) found."
    )

@router.get("/{pipeline_id}", response_model=LoadPipelineResponse)
async def load_pipeline(pipeline_id: str):
    """
    Retrieves the full JSON structure of a single saved pipeline.
    """
    if pipeline_id not in pipelines_db:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    pipeline = pipelines_db[pipeline_id]
    return LoadPipelineResponse(**pipeline)

@router.get("/project/{project_id}/list", response_model=ListPipelinesResponse)
async def list_pipelines(project_id: str):
    """
    Returns a list of all pipeline names and IDs associated with a given project.
    """
    # Filter pipelines by project_id
    project_pipelines = [
        {"pipeline_id": pipeline_id, "name": pipeline["name"]}
        for pipeline_id, pipeline in pipelines_db.items()
        if pipeline["project_id"] == project_id
    ]
    
    return ListPipelinesResponse(pipelines=project_pipelines)

@router.post("/suggest", response_model=SuggestionResponse)
async def suggest_nodes(request: SuggestionRequest):
    """
    Analyzes the current pipeline state and returns a list of suggested next nodes to add.
    """
    suggestions = get_suggestions(request.pipeline_json)
    return SuggestionResponse(suggestions=suggestions)