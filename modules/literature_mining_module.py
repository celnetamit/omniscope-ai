"""
Literature Mining Module
Provides AI-powered research paper analysis and context extraction
"""

from fastapi import APIRouter
from backend_db.literature_mining import router as literature_router

# Re-export the router from backend service
router = literature_router
