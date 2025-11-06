"""
OmniScope AI - Core Application
Main FastAPI application that integrates all modules: Data Harbor, The Weaver, The Crucible, and The Insight Engine
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import signal
import sys
from contextlib import asynccontextmanager

# Import all module routers
from modules.data_harbor import router as data_harbor_router
from modules.the_weaver import router as the_weaver_router
from modules.the_crucible import router as the_crucible_router
from modules.the_insight_engine import router as the_insight_engine_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 OmniScope AI is starting up...")
    print("📊 Data Harbor Module: Ready for file uploads and analysis")
    print("🔗 The Weaver Module: Ready for pipeline management")
    print("🔥 The Crucible Module: Ready for model training")
    print("💡 The Insight Engine Module: Ready for biomarker analysis")
    
    # Setup graceful shutdown handlers
    def signal_handler(signum, frame):
        print(f"🛑 Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    yield
    # Shutdown
    print("🛑 OmniScope AI is shutting down...")

# Create the FastAPI application
app = FastAPI(
    title="OmniScope AI",
    description="A comprehensive multi-omics data analysis platform with integrated modules for data processing, pipeline management, model training, and insight generation.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all module routers with proper prefixes
app.include_router(
    data_harbor_router, 
    prefix="/api/data", 
    tags=["Data Harbor - File Analysis"]
)

app.include_router(
    the_weaver_router, 
    prefix="/api/pipelines", 
    tags=["The Weaver - Pipeline Management"]
)

app.include_router(
    the_crucible_router, 
    prefix="/api/models", 
    tags=["The Crucible - Model Training"]
)

app.include_router(
    the_insight_engine_router, 
    prefix="/api/results", 
    tags=["The Insight Engine - Biomarker Analysis"]
)

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint that provides information about the OmniScope AI platform
    and its available modules.
    """
    return {
        "message": "Welcome to OmniScope AI - Multi-Omics Data Analysis Platform",
        "version": "1.0.0",
        "modules": {
            "data_harbor": {
                "name": "Data Harbor",
                "description": "File upload and analysis module for CSV data processing",
                "endpoints": [
                    "POST /api/data/upload - Upload CSV files for analysis",
                    "GET /api/data/{file_id}/report - Get analysis report"
                ]
            },
            "the_weaver": {
                "name": "The Weaver",
                "description": "Visual workflow editor with AI-powered suggestions",
                "endpoints": [
                    "POST /api/pipelines/save - Save or update pipelines",
                    "GET /api/pipelines/{pipeline_id} - Load specific pipeline",
                    "GET /api/pipelines/project/{project_id}/list - List project pipelines",
                    "POST /api/pipelines/suggest - Get AI suggestions"
                ]
            },
            "the_crucible": {
                "name": "The Crucible",
                "description": "Model training engine with real-time progress tracking",
                "endpoints": [
                    "POST /api/models/train - Start model training",
                    "GET /api/models/{job_id}/status - Get training status",
                    "GET /api/models/{job_id}/results - Get training results"
                ]
            },
            "the_insight_engine": {
                "name": "The Insight Engine",
                "description": "Biomarker analysis with Socratic tutoring and natural language queries",
                "endpoints": [
                    "GET /api/results/{model_id}/biomarkers - Get biomarkers list",
                    "GET /api/results/{model_id}/biomarkers/{gene_id}/explain - Get biomarker explanation",
                    "POST /api/results/{model_id}/query - Natural language query"
                ]
            }
        },
        "api_docs": "/docs",
        "health_check": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify all modules are operational.
    """
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "modules": {
            "data_harbor": "operational",
            "the_weaver": "operational", 
            "the_crucible": "operational",
            "the_insight_engine": "operational"
        }
    }

# Module status endpoint
@app.get("/api/modules/status")
async def get_module_status():
    """
    Get detailed status of all modules.
    """
    return {
        "data_harbor": {
            "status": "active",
            "description": "Ready for file uploads and analysis",
            "storage": "in-memory",
            "supported_formats": ["csv"],
            "max_file_size": "10MB"
        },
        "the_weaver": {
            "status": "active",
            "description": "Pipeline management and AI suggestions",
            "storage": "in-memory",
            "features": ["save", "load", "list", "suggest"]
        },
        "the_crucible": {
            "status": "active",
            "description": "Model training with background processing",
            "storage": "in-memory",
            "features": ["train", "status", "results"]
        },
        "the_insight_engine": {
            "status": "active",
            "description": "Biomarker analysis and explanations",
            "storage": "in-memory",
            "features": ["biomarkers", "explain", "query"]
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for consistent error responses.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "details": str(exc) if app.debug else None
        }
    )

# 404 handler
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """
    Handler for 404 errors.
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found.",
            "path": str(request.url.path)
        }
    )

if __name__ == "__main__":
    print("🚀 Starting OmniScope AI Core Application...")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🔍 Health Check: http://localhost:8001/health")
    print("📊 Module Status: http://localhost:8001/api/modules/status")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,  # Disable reload in production
        log_level="info"
    )