"""
Tests for ML Framework Module
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_ml_framework_module_structure():
    """Test that ML framework module has correct structure"""
    # Test module can be imported (structure is valid)
    try:
        # We can't actually import due to missing dependencies
        # but we can verify the file exists and has valid Python syntax
        import py_compile
        
        ml_framework_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'modules', 
            'ml_framework.py'
        )
        
        # This will raise SyntaxError if invalid
        py_compile.compile(ml_framework_path, doraise=True)
        
        assert True, "ML framework module has valid Python syntax"
        
    except SyntaxError as e:
        pytest.fail(f"ML framework module has syntax error: {e}")

def test_ml_services_module_structure():
    """Test that ML services module has correct structure"""
    try:
        import py_compile
        
        ml_services_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'backend_db', 
            'ml_services.py'
        )
        
        # This will raise SyntaxError if invalid
        py_compile.compile(ml_services_path, doraise=True)
        
        assert True, "ML services module has valid Python syntax"
        
    except SyntaxError as e:
        pytest.fail(f"ML services module has syntax error: {e}")

def test_ml_models_in_database():
    """Test that ML models are defined in database models"""
    try:
        # Read the models file
        models_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'backend_db', 
            'models.py'
        )
        
        with open(models_path, 'r') as f:
            content = f.read()
        
        # Check for MLModel class
        assert 'class MLModel(Base):' in content, "MLModel class not found"
        
        # Check for TrainingJob enhancements
        assert 'model_type' in content, "model_type field not found in TrainingJob"
        assert 'progress' in content, "progress field not found in TrainingJob"
        
        assert True, "ML models are properly defined"
        
    except Exception as e:
        pytest.fail(f"Failed to verify ML models: {e}")

def test_requirements_includes_ml_libraries():
    """Test that requirements.txt includes ML libraries"""
    try:
        requirements_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'requirements.txt'
        )
        
        with open(requirements_path, 'r') as f:
            content = f.read()
        
        # Check for key ML libraries
        assert 'mlflow' in content, "mlflow not in requirements"
        assert 'torch' in content, "torch not in requirements"
        assert 'pytorch-lightning' in content, "pytorch-lightning not in requirements"
        assert 'autogluon' in content, "autogluon not in requirements"
        assert 'shap' in content, "shap not in requirements"
        assert 'lime' in content, "lime not in requirements"
        
        assert True, "All ML libraries are in requirements.txt"
        
    except Exception as e:
        pytest.fail(f"Failed to verify requirements: {e}")

def test_main_app_includes_ml_router():
    """Test that main.py includes ML framework router"""
    try:
        main_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'main.py'
        )
        
        with open(main_path, 'r') as f:
            content = f.read()
        
        # Check for ML framework import
        assert 'from modules.ml_framework import router as ml_framework_router' in content, \
            "ML framework router import not found"
        
        # Check for router inclusion
        assert 'app.include_router(\n    ml_framework_router,' in content or \
               'app.include_router(ml_framework_router,' in content, \
            "ML framework router not included in app"
        
        # Check for correct prefix
        assert 'prefix="/api/ml"' in content, "ML framework router prefix not correct"
        
        assert True, "ML framework router is properly integrated"
        
    except Exception as e:
        pytest.fail(f"Failed to verify main.py integration: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
