import io
import uuid
from typing import Dict, Any, Optional, List
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Import database components
from backend_db import get_db, DataHarborService

# Create the FastAPI router
router = APIRouter()

# Constants for file validation
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
ALLOWED_EXTENSIONS = ["csv"]

def validate_file(file: UploadFile) -> bool:
    """
    Validate that the uploaded file is a CSV and within size limits.
    
    Args:
        file: The uploaded file to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Check file extension
    if not file.filename.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
        return False
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end of file
    file_size = file.file.tell()
    file.file.seek(0)  # Reset file position
    
    if file_size > MAX_FILE_SIZE:
        return False
    
    return True

def analyze_csv_file(file_id: str, file_content: bytes, filename: str) -> None:
    """
    Background task to analyze the uploaded CSV file.
    
    Args:
        file_id: Unique identifier for the file
        file_content: The content of the uploaded file
        filename: Original filename
    """
    from backend_db import get_db_session, close_db_session
    
    db = get_db_session()
    try:
        # Update status to processing
        DataHarborService.create_report(
            db=db,
            file_id=file_id,
            filename=filename,
            status="processing",
            message="Analysis in progress."
        )
        
        # Read the CSV file
        df = pd.read_csv(io.BytesIO(file_content))
        
        # Basic info
        rows, columns = df.shape
        duplicates = int(df.duplicated().sum())  # Convert to native int
        
        # Missing values analysis
        missing_values = {}
        for col in df.columns:
            missing_pct = float((df[col].isna().sum() / rows) * 100)  # Convert to native float
            missing_values[col] = missing_pct
        
        # Data type inference
        data_types = {}
        for col in df.columns:
            data_types[col] = str(df[col].dtype)
        
        # Generate findings based on analysis
        findings = []
        for col, pct in missing_values.items():
            if pct > 0:
                severity = "low" if pct < 5 else "medium" if pct < 20 else "high"
                findings.append({
                    "type": "missing_data",
                    "severity": severity,
                    "description": f"Column '{col}' has {pct:.1f}% missing values."
                })
        
        if duplicates > 0:
            findings.append({
                "type": "duplicate_rows",
                "severity": "medium" if duplicates < rows * 0.05 else "high",
                "description": f"Found {duplicates} duplicate rows ({duplicates/rows*100:.1f}% of data)."
            })
        
        # Generate recommendations
        recommendations = []
        for col, pct in missing_values.items():
            if 0 < pct < 10:
                recommendations.append({
                    "action": "impute_missing_values",
                    "target_column": col,
                    "suggestion": "Consider using K-Nearest Neighbor (KNN) imputation.",
                    "reasoning": f"With only {pct:.1f}% missing data, KNN is a robust method that preserves relationships between features.",
                    "learn_more_link": "https://example.com/learn/knn-imputation"
                })
            elif 10 <= pct < 30:
                recommendations.append({
                    "action": "impute_missing_values",
                    "target_column": col,
                    "suggestion": "Consider using median imputation for numerical columns or mode for categorical columns.",
                    "reasoning": f"With {pct:.1f}% missing data, simple imputation methods are appropriate.",
                    "learn_more_link": "https://example.com/learn/simple-imputation"
                })
            elif pct >= 30:
                recommendations.append({
                    "action": "consider_dropping_column",
                    "target_column": col,
                    "suggestion": "Consider dropping this column or collecting more data.",
                    "reasoning": f"With {pct:.1f}% missing data, imputation may introduce significant bias.",
                    "learn_more_link": "https://example.com/learn/missing-data-handling"
                })
        
        if duplicates > 0:
            recommendations.append({
                "action": "remove_duplicates",
                "target_column": "all",
                "suggestion": "Remove duplicate rows to ensure data quality.",
                "reasoning": "Duplicate rows can bias analysis results and model training.",
                "learn_more_link": "https://example.com/learn/handling-duplicates"
            })
        
        # Create the final report data
        report_data = {
            "summary": {
                "filename": filename,
                "rows": int(rows),  # Convert to native int
                "columns": int(columns),  # Convert to native int
                "duplicates": duplicates
            },
            "findings": findings,
            "recommendations": recommendations,
            "data_types": data_types,
            "missing_values": missing_values
        }
        
        # Update the report in database
        DataHarborService.update_report(
            db=db,
            file_id=file_id,
            status="complete",
            report_data=report_data
        )
        
        # Cleanup old reports
        DataHarborService.cleanup_old_reports(db, max_reports=100)
        
    except Exception as e:
        # Handle any errors during analysis
        DataHarborService.update_report(
            db=db,
            file_id=file_id,
            status="error",
            message=f"Error during analysis: {str(e)}"
        )
        # Log the error for debugging
        print(f"Error analyzing file {file_id}: {str(e)}")
        DataHarborService.cleanup_old_reports(db, max_reports=100)
    finally:
        close_db_session(db)

@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
) -> Dict[str, str]:
    """
    Upload a CSV file for analysis.
    
    Args:
        background_tasks: FastAPI BackgroundTasks for async processing
        file: The uploaded file
        
    Returns:
        Dict with file_id and status
    """
    # Validate the file
    if not validate_file(file):
        raise HTTPException(
            status_code=400,
            detail="Invalid file. Please upload a CSV file under 10MB."
        )
    
    # Generate a unique file ID
    file_id = str(uuid.uuid4())
    
    # Read file content
    file_content = await file.read()
    
    # Start the background task for analysis
    background_tasks.add_task(
        analyze_csv_file,
        file_id=file_id,
        file_content=file_content,
        filename=file.filename
    )
    
    # Return immediate response
    return {
        "file_id": file_id,
        "status": "processing",
        "message": "Analysis in progress."
    }

@router.get("/{file_id}/report")
async def get_report(file_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieve the analysis report for a file.
    
    Args:
        file_id: The unique identifier for the file
        db: Database session
        
    Returns:
        The analysis report or status
    """
    # Get the report from database
    report = DataHarborService.get_report(db, file_id)
    
    if not report:
        raise HTTPException(
            status_code=404,
            detail="File ID not found."
        )
    
    # Format the response to match the expected structure
    response = {
        "file_id": report.id,
        "status": report.status,
        "message": report.message
    }
    
    # Add report data if analysis is complete
    if report.status == "complete" and report.report_data:
        response["report"] = report.report_data
    
    return response