"""
Report Generator Module
Automated scientific report creation system with citation management
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
import uuid
import os
from pathlib import Path

# Import template engine and generators
from backend_db.report_templates import TemplateEngine
from backend_db.report_generators import PDFGenerator, DOCXGenerator, LaTeXGenerator
from backend_db.citation_manager import CitationManager
from backend_db.methods_generator import MethodsGenerator

router = APIRouter()

# Request/Response Models
class ReportSection(BaseModel):
    """Model for report section configuration"""
    title: str
    content_type: Literal["text", "figure", "table", "methods"]
    content: Optional[str] = None
    order: int
    
class ReportTemplate(BaseModel):
    """Model for report template"""
    id: Optional[str] = None
    name: str
    sections: List[ReportSection]
    citation_style: Literal["APA", "MLA", "Chicago", "Nature", "Science"] = "APA"
    format: Literal["pdf", "docx", "latex"]

class ReportGenerationRequest(BaseModel):
    """Request model for report generation"""
    title: str
    template_id: Optional[str] = None
    template: Optional[ReportTemplate] = None
    format: Literal["pdf", "docx", "latex"] = "pdf"
    citation_style: Literal["APA", "MLA", "Chicago", "Nature", "Science"] = "APA"
    data: Dict[str, Any] = Field(default_factory=dict)
    pipeline_id: Optional[str] = None
    model_id: Optional[str] = None
    include_methods: bool = True
    include_citations: bool = True

class ReportResponse(BaseModel):
    """Response model for report generation"""
    report_id: str
    title: str
    format: str
    file_path: str
    status: str
    created_at: datetime
    message: str

class TemplateListResponse(BaseModel):
    """Response model for template listing"""
    templates: List[Dict[str, Any]]
    count: int

# In-memory storage for templates and reports (in production, use database)
templates_storage: Dict[str, ReportTemplate] = {}
reports_storage: Dict[str, Dict[str, Any]] = {}

# Initialize default templates
def initialize_default_templates():
    """Initialize default report templates"""
    default_template = ReportTemplate(
        id="default_scientific",
        name="Default Scientific Report",
        sections=[
            ReportSection(title="Abstract", content_type="text", order=1),
            ReportSection(title="Introduction", content_type="text", order=2),
            ReportSection(title="Methods", content_type="methods", order=3),
            ReportSection(title="Results", content_type="text", order=4),
            ReportSection(title="Discussion", content_type="text", order=5),
            ReportSection(title="References", content_type="text", order=6),
        ],
        citation_style="APA",
        format="pdf"
    )
    templates_storage[default_template.id] = default_template

# Initialize templates on module load
initialize_default_templates()

@router.post("/api/reports/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a scientific report in the specified format
    
    Requirements: 5.1, 5.5, 5.6
    """
    try:
        # Generate unique report ID
        report_id = str(uuid.uuid4())
        
        # Determine template to use
        template = None
        if request.template_id and request.template_id in templates_storage:
            template = templates_storage[request.template_id]
        elif request.template:
            template = request.template
        else:
            template = templates_storage.get("default_scientific")
        
        if not template:
            raise HTTPException(status_code=400, detail="No valid template provided")
        
        # Initialize template engine
        template_engine = TemplateEngine()
        
        # Initialize citation manager if needed
        citation_manager = None
        if request.include_citations:
            citation_manager = CitationManager(style=request.citation_style)
        
        # Generate methods section if needed
        methods_content = None
        if request.include_methods and request.pipeline_id:
            methods_generator = MethodsGenerator()
            methods_content = methods_generator.generate_methods(
                pipeline_id=request.pipeline_id,
                model_id=request.model_id
            )
        
        # Prepare report data
        report_data = {
            "title": request.title,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "sections": template.sections,
            "data": request.data,
            "methods": methods_content,
            "citations": citation_manager.get_bibliography() if citation_manager else []
        }
        
        # Render template
        rendered_content = template_engine.render_template(
            template_name="scientific_report",
            data=report_data
        )
        
        # Create output directory
        output_dir = Path("generated_reports")
        output_dir.mkdir(exist_ok=True)
        
        # Generate report based on format
        file_path = None
        if request.format == "pdf":
            generator = PDFGenerator()
            file_path = generator.generate(
                report_id=report_id,
                title=request.title,
                content=rendered_content,
                data=report_data,
                output_dir=str(output_dir)
            )
        elif request.format == "docx":
            generator = DOCXGenerator()
            file_path = generator.generate(
                report_id=report_id,
                title=request.title,
                content=rendered_content,
                data=report_data,
                output_dir=str(output_dir)
            )
        elif request.format == "latex":
            generator = LaTeXGenerator()
            file_path = generator.generate(
                report_id=report_id,
                title=request.title,
                content=rendered_content,
                data=report_data,
                output_dir=str(output_dir)
            )
        
        # Store report metadata
        report_metadata = {
            "id": report_id,
            "title": request.title,
            "format": request.format,
            "file_path": file_path,
            "status": "completed",
            "created_at": datetime.now(),
            "template_id": template.id if hasattr(template, 'id') else None,
            "data": request.data
        }
        reports_storage[report_id] = report_metadata
        
        return ReportResponse(
            report_id=report_id,
            title=request.title,
            format=request.format,
            file_path=file_path,
            status="completed",
            created_at=datetime.now(),
            message=f"Report generated successfully in {request.format.upper()} format"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )

@router.get("/api/reports/{report_id}/download")
async def download_report(report_id: str):
    """
    Download a generated report
    
    Requirements: 5.1, 5.5
    """
    if report_id not in reports_storage:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = reports_storage[report_id]
    file_path = report["file_path"]
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/octet-stream"
    )

@router.get("/api/reports/templates", response_model=TemplateListResponse)
async def list_templates():
    """
    List all available report templates
    
    Requirements: 5.6
    """
    templates_list = [
        {
            "id": template.id,
            "name": template.name,
            "format": template.format,
            "citation_style": template.citation_style,
            "sections": len(template.sections)
        }
        for template in templates_storage.values()
    ]
    
    return TemplateListResponse(
        templates=templates_list,
        count=len(templates_list)
    )

@router.post("/api/reports/templates/custom")
async def create_custom_template(template: ReportTemplate):
    """
    Create a custom report template
    
    Requirements: 5.6
    """
    try:
        # Generate template ID if not provided
        if not template.id:
            template.id = f"custom_{str(uuid.uuid4())[:8]}"
        
        # Store template
        templates_storage[template.id] = template
        
        return {
            "message": "Custom template created successfully",
            "template_id": template.id,
            "name": template.name
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create custom template: {str(e)}"
        )

@router.get("/api/reports/{report_id}")
async def get_report_metadata(report_id: str):
    """
    Get metadata for a generated report
    """
    if report_id not in reports_storage:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = reports_storage[report_id]
    return {
        "report_id": report["id"],
        "title": report["title"],
        "format": report["format"],
        "status": report["status"],
        "created_at": report["created_at"].isoformat(),
        "file_path": report["file_path"]
    }

@router.delete("/api/reports/{report_id}")
async def delete_report(report_id: str):
    """
    Delete a generated report
    """
    if report_id not in reports_storage:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = reports_storage[report_id]
    file_path = report["file_path"]
    
    # Delete file if exists
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Remove from storage
    del reports_storage[report_id]
    
    return {
        "message": "Report deleted successfully",
        "report_id": report_id
    }
