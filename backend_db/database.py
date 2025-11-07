"""
Database configuration and session management for OmniScope AI Backend
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from .models import Base
from typing import Generator

# Database URL - use SQLite for simplicity and portability
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db/backend.db")

# Create engine with appropriate settings for SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL query logging
    )
else:
    # For other databases (PostgreSQL, MySQL, etc.)
    engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    Use this in FastAPI endpoints with Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize the database - create tables and setup"""
    print("🗄️ Initializing backend database...")
    
    # Ensure the db directory exists
    db_dir = os.path.dirname(DATABASE_URL.replace("sqlite:///", ""))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"📁 Created database directory: {db_dir}")
    
    # Create all tables
    create_tables()
    print("✅ Database tables created successfully")
    
    # Test database connection
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection test successful")
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        raise

# Database utility functions
def get_db_session() -> Session:
    """Get a database session for use outside of FastAPI endpoints"""
    return SessionLocal()

def close_db_session(db: Session):
    """Close a database session"""
    db.close()