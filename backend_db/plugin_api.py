"""
Plugin API Gateway for OmniScope AI
Provides standardized interface for plugin execution with validation
"""

from typing import Dict, Any, Optional, List, Callable
from pydantic import BaseModel, Field, validator
from datetime import datetime
import json
import time


class PluginContext(BaseModel):
    """Context provided to plugins during execution"""
    plugin_id: str
    plugin_name: str
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    execution_id: str
    config: Dict[str, Any] = Field(default_factory=dict)
    permissions: List[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True


class PluginInput(BaseModel):
    """Standardized input format for plugins"""
    data: Any
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('data')
    def validate_data(cls, v):
        """Validate input data"""
        if v is None:
            raise ValueError("Input data cannot be None")
        return v


class PluginOutput(BaseModel):
    """Standardized output format for plugins"""
    data: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
    logs: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    execution_time: Optional[int] = None  # milliseconds
    
    class Config:
        arbitrary_types_allowed = True


class PluginInterface:
    """Base interface that all plugins must implement"""
    
    def __init__(self, context: PluginContext):
        """
        Initialize plugin with context
        
        Args:
            context: Plugin execution context
        """
        self.context = context
        self.config = context.config
    
    def validate_input(self, input_data: PluginInput) -> bool:
        """
        Validate input data
        
        Args:
            input_data: Input data to validate
        
        Returns:
            bool: True if valid
        
        Raises:
            ValueError: If validation fails
        """
        raise NotImplementedError("Plugins must implement validate_input()")
    
    def execute(self, input_data: PluginInput) -> PluginOutput:
        """
        Execute plugin logic
        
        Args:
            input_data: Input data
        
        Returns:
            PluginOutput: Execution result
        """
        raise NotImplementedError("Plugins must implement execute()")
    
    def cleanup(self):
        """Cleanup resources after execution"""
        pass


class PluginAPIGateway:
    """Gateway for plugin execution with validation and error handling"""
    
    # Extension points where plugins can hook into
    EXTENSION_POINTS = {
        'data_import': 'Import data from external sources',
        'data_export': 'Export data to external formats',
        'preprocessing': 'Data preprocessing and transformation',
        'feature_engineering': 'Feature extraction and engineering',
        'analysis': 'Custom analysis algorithms',
        'visualization': 'Custom visualization types',
        'model_training': 'Custom ML model training',
        'model_evaluation': 'Custom model evaluation metrics',
        'report_generation': 'Custom report sections',
        'integration': 'Integration with external services'
    }
    
    def __init__(self):
        """Initialize plugin gateway"""
        self.validators: Dict[str, Callable] = {}
        self.transformers: Dict[str, Callable] = {}
    
    def register_validator(
        self,
        extension_point: str,
        validator: Callable[[PluginInput], bool]
    ):
        """
        Register input validator for extension point
        
        Args:
            extension_point: Extension point name
            validator: Validation function
        """
        if extension_point not in self.EXTENSION_POINTS:
            raise ValueError(f"Unknown extension point: {extension_point}")
        
        self.validators[extension_point] = validator
    
    def register_transformer(
        self,
        extension_point: str,
        transformer: Callable[[Any], Any]
    ):
        """
        Register output transformer for extension point
        
        Args:
            extension_point: Extension point name
            transformer: Transformation function
        """
        if extension_point not in self.EXTENSION_POINTS:
            raise ValueError(f"Unknown extension point: {extension_point}")
        
        self.transformers[extension_point] = transformer
    
    def validate_input(
        self,
        extension_point: str,
        input_data: PluginInput
    ) -> tuple[bool, Optional[str]]:
        """
        Validate plugin input
        
        Args:
            extension_point: Extension point name
            input_data: Input data to validate
        
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Basic validation
            if not isinstance(input_data, PluginInput):
                return False, "Input must be PluginInput instance"
            
            # Extension point specific validation
            if extension_point in self.validators:
                validator = self.validators[extension_point]
                if not validator(input_data):
                    return False, f"Validation failed for {extension_point}"
            
            return True, None
        
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def validate_output(
        self,
        output_data: PluginOutput
    ) -> tuple[bool, Optional[str]]:
        """
        Validate plugin output
        
        Args:
            output_data: Output data to validate
        
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            if not isinstance(output_data, PluginOutput):
                return False, "Output must be PluginOutput instance"
            
            if output_data.data is None:
                return False, "Output data cannot be None"
            
            return True, None
        
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def execute_plugin(
        self,
        plugin: PluginInterface,
        input_data: PluginInput,
        extension_point: str,
        timeout: Optional[int] = None
    ) -> PluginOutput:
        """
        Execute plugin with validation and error handling
        
        Args:
            plugin: Plugin instance
            input_data: Input data
            extension_point: Extension point name
            timeout: Execution timeout in seconds
        
        Returns:
            PluginOutput: Execution result
        """
        start_time = time.time()
        
        try:
            # Validate input
            is_valid, error_msg = self.validate_input(extension_point, input_data)
            if not is_valid:
                return PluginOutput(
                    data=None,
                    errors=[f"Input validation failed: {error_msg}"]
                )
            
            # Plugin-specific input validation
            try:
                plugin.validate_input(input_data)
            except Exception as e:
                return PluginOutput(
                    data=None,
                    errors=[f"Plugin input validation failed: {str(e)}"]
                )
            
            # Execute plugin
            output = plugin.execute(input_data)
            
            # Validate output
            is_valid, error_msg = self.validate_output(output)
            if not is_valid:
                return PluginOutput(
                    data=None,
                    errors=[f"Output validation failed: {error_msg}"]
                )
            
            # Apply output transformer if registered
            if extension_point in self.transformers:
                transformer = self.transformers[extension_point]
                output.data = transformer(output.data)
            
            # Add execution time
            execution_time = int((time.time() - start_time) * 1000)
            output.execution_time = execution_time
            
            return output
        
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            return PluginOutput(
                data=None,
                errors=[f"Plugin execution failed: {str(e)}"],
                execution_time=execution_time
            )
        
        finally:
            # Cleanup
            try:
                plugin.cleanup()
            except Exception as e:
                print(f"Plugin cleanup error: {e}")
    
    def create_context(
        self,
        plugin_id: str,
        plugin_name: str,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        config: Dict[str, Any] = None,
        permissions: List[str] = None
    ) -> PluginContext:
        """
        Create plugin execution context
        
        Args:
            plugin_id: Plugin ID
            plugin_name: Plugin name
            user_id: User ID
            workspace_id: Workspace ID
            config: Plugin configuration
            permissions: User permissions
        
        Returns:
            PluginContext: Execution context
        """
        import uuid
        
        return PluginContext(
            plugin_id=plugin_id,
            plugin_name=plugin_name,
            user_id=user_id,
            workspace_id=workspace_id,
            execution_id=str(uuid.uuid4()),
            config=config or {},
            permissions=permissions or []
        )
    
    def wrap_data(
        self,
        data: Any,
        parameters: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> PluginInput:
        """
        Wrap data in PluginInput format
        
        Args:
            data: Input data
            parameters: Execution parameters
            metadata: Additional metadata
        
        Returns:
            PluginInput: Wrapped input
        """
        return PluginInput(
            data=data,
            parameters=parameters or {},
            metadata=metadata or {}
        )


# Example plugin validators for different extension points
def validate_data_import_input(input_data: PluginInput) -> bool:
    """Validate input for data import plugins"""
    params = input_data.parameters
    
    # Check required parameters
    if 'source' not in params:
        raise ValueError("Missing required parameter: source")
    
    if 'format' not in params:
        raise ValueError("Missing required parameter: format")
    
    return True


def validate_preprocessing_input(input_data: PluginInput) -> bool:
    """Validate input for preprocessing plugins"""
    # Data should be a DataFrame-like structure
    data = input_data.data
    
    if not hasattr(data, 'shape'):
        raise ValueError("Input data must have shape attribute (DataFrame-like)")
    
    return True


def validate_analysis_input(input_data: PluginInput) -> bool:
    """Validate input for analysis plugins"""
    params = input_data.parameters
    
    # Check for required analysis parameters
    if 'method' not in params:
        raise ValueError("Missing required parameter: method")
    
    return True


def validate_visualization_input(input_data: PluginInput) -> bool:
    """Validate input for visualization plugins"""
    params = input_data.parameters
    
    # Check for required visualization parameters
    if 'chart_type' not in params:
        raise ValueError("Missing required parameter: chart_type")
    
    return True


# Register default validators
def setup_default_validators(gateway: PluginAPIGateway):
    """Setup default validators for extension points"""
    gateway.register_validator('data_import', validate_data_import_input)
    gateway.register_validator('preprocessing', validate_preprocessing_input)
    gateway.register_validator('analysis', validate_analysis_input)
    gateway.register_validator('visualization', validate_visualization_input)
