"""
Data Normalizer Plugin - OmniScope AI Plugin
Normalizes numerical data using various methods

Author: OmniScope Team
Version: 1.0.0
"""

import json
import sys
import numpy as np
from typing import Dict, Any


class DataNormalizer:
    """Data normalization plugin"""
    
    def __init__(self, context: Dict[str, Any]):
        """Initialize plugin"""
        self.context = context
        self.config = context.get('config', {})
        self.plugin_id = context.get('plugin_id')
        self.plugin_name = context.get('plugin_name')
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data"""
        if 'data' not in input_data:
            raise ValueError("Missing required field: data")
        
        parameters = input_data.get('parameters', {})
        method = parameters.get('method', 'zscore')
        
        if method not in ['zscore', 'minmax', 'robust']:
            raise ValueError(f"Invalid normalization method: {method}")
        
        return True
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin logic"""
        data = input_data.get('data')
        parameters = input_data.get('parameters', {})
        
        # Get normalization method
        method = parameters.get('method', 'zscore')
        
        # Normalize data
        normalized_data = self.normalize_data(data, method)
        
        return {
            'data': normalized_data,
            'metadata': {
                'plugin_id': self.plugin_id,
                'plugin_name': self.plugin_name,
                'method': method
            },
            'logs': [f'Data normalized using {method} method'],
            'warnings': [],
            'errors': []
        }
    
    def normalize_data(self, data: Any, method: str) -> Any:
        """Normalize data using specified method"""
        # Convert to numpy array
        arr = np.array(data)
        
        if method == 'zscore':
            # Z-score normalization
            mean = np.mean(arr, axis=0)
            std = np.std(arr, axis=0)
            normalized = (arr - mean) / (std + 1e-8)
        
        elif method == 'minmax':
            # Min-max normalization
            min_val = np.min(arr, axis=0)
            max_val = np.max(arr, axis=0)
            normalized = (arr - min_val) / (max_val - min_val + 1e-8)
        
        elif method == 'robust':
            # Robust normalization (using median and IQR)
            median = np.median(arr, axis=0)
            q75 = np.percentile(arr, 75, axis=0)
            q25 = np.percentile(arr, 25, axis=0)
            iqr = q75 - q25
            normalized = (arr - median) / (iqr + 1e-8)
        
        return normalized.tolist()
    
    def cleanup(self):
        """Cleanup resources"""
        pass


def main():
    """Main entry point"""
    # Read input from file
    with open('/plugin/input.json', 'r') as f:
        input_data = json.load(f)
    
    # Read context
    context = input_data.get('context', {})
    
    # Initialize plugin
    plugin = DataNormalizer(context)
    
    # Validate input
    plugin.validate_input(input_data)
    
    # Execute plugin
    output = plugin.execute(input_data)
    
    # Write output to file
    with open('/plugin/output.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    # Cleanup
    plugin.cleanup()


if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except Exception as e:
        error_output = {
            'data': None,
            'errors': [str(e)],
            'logs': [],
            'warnings': []
        }
        with open('/plugin/output.json', 'w') as f:
            json.dump(error_output, f, indent=2)
        sys.exit(1)
