# Plugin System Quick Start Guide

## Overview

The OmniScope AI Plugin System allows you to extend the platform with custom analysis methods, data processors, visualizations, and integrations. Plugins can be written in Python or R and run in isolated Docker containers for security.

## Features

- **Multi-Language Support**: Write plugins in Python or R
- **Secure Sandbox Execution**: Plugins run in isolated Docker containers
- **Security Scanning**: Automatic vulnerability detection using Bandit
- **Version Management**: Semantic versioning with update and rollback support
- **Plugin Marketplace**: Discover and share plugins with the community
- **Dependency Resolution**: Automatic dependency management
- **Extension Points**: Hook into 10+ platform extension points

## Extension Points

1. **data_import**: Import data from external sources
2. **data_export**: Export data to external formats
3. **preprocessing**: Data preprocessing and transformation
4. **feature_engineering**: Feature extraction and engineering
5. **analysis**: Custom analysis algorithms
6. **visualization**: Custom visualization types
7. **model_training**: Custom ML model training
8. **model_evaluation**: Custom model evaluation metrics
9. **report_generation**: Custom report sections
10. **integration**: Integration with external services

## Quick Start

### 1. Create a Plugin Project

```bash
# Using the SDK API
curl -X POST "http://localhost:8001/api/plugins/sdk/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_plugin",
    "language": "python",
    "author": "Your Name",
    "description": "My custom plugin",
    "category": "analysis",
    "tags": ["custom", "analysis"],
    "extension_points": ["analysis"]
  }'
```

This creates a plugin project with:
- Main plugin file (`my_plugin.py` or `my_plugin.R`)
- `manifest.json` with plugin metadata
- `README.md` with documentation template
- `.gitignore` for version control

### 2. Implement Plugin Logic

Edit the generated plugin file to implement your custom logic:

**Python Example:**
```python
def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute plugin logic"""
    data = input_data.get('data')
    parameters = input_data.get('parameters', {})
    
    # Your custom processing
    result = self.process_data(data, parameters)
    
    return {
        'data': result,
        'metadata': {'plugin_id': self.plugin_id},
        'logs': ['Processing completed'],
        'warnings': [],
        'errors': []
    }
```

**R Example:**
```r
execute = function(input_data) {
  data <- input_data$data
  parameters <- input_data$parameters
  
  # Your custom processing
  result <- .self$process_data(data, parameters)
  
  return(list(
    data = result,
    metadata = list(plugin_id = .self$plugin_id),
    logs = list("Processing completed"),
    warnings = list(),
    errors = list()
  ))
}
```

### 3. Package Plugin

```bash
# Create a tar.gz package
tar -czf my_plugin.tar.gz my_plugin/
```

### 4. Install Plugin

```bash
# Upload and install plugin
curl -X POST "http://localhost:8001/api/plugins/install" \
  -F "file=@my_plugin.tar.gz"
```

The installation process:
1. Extracts the package
2. Validates `manifest.json`
3. Runs security scan
4. Resolves dependencies
5. Stores plugin files

### 5. Enable Plugin

```bash
# Enable the plugin
curl -X POST "http://localhost:8001/api/plugins/{plugin_id}/enable"
```

### 6. Execute Plugin

```bash
# Execute plugin
curl -X POST "http://localhost:8001/api/plugins/{plugin_id}/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "values": [1, 2, 3, 4, 5]
    },
    "parameters": {
      "method": "custom"
    },
    "extension_point": "analysis"
  }'
```

## Example Plugins

### 1. Data Normalizer (Python)

Located in `plugins/examples/data_normalizer/`

Normalizes numerical data using various methods (z-score, min-max, robust).

**Usage:**
```bash
curl -X POST "http://localhost:8001/api/plugins/{plugin_id}/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
    "parameters": {"method": "zscore"},
    "extension_point": "preprocessing"
  }'
```

### 2. Correlation Analyzer (R)

Located in `plugins/examples/correlation_analyzer/`

Calculates correlation matrices and identifies significant correlations.

**Usage:**
```bash
curl -X POST "http://localhost:8001/api/plugins/{plugin_id}/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "var1": [1, 2, 3, 4, 5],
      "var2": [2, 4, 6, 8, 10],
      "var3": [1, 3, 5, 7, 9]
    },
    "parameters": {
      "method": "pearson",
      "threshold": 0.7
    },
    "extension_point": "analysis"
  }'
```

## Plugin Manifest

The `manifest.json` file contains plugin metadata:

```json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "author_email": "you@example.com",
  "description": "Plugin description",
  "language": "python",
  "entry_point": "my_plugin.py",
  "category": "analysis",
  "tags": ["custom", "analysis"],
  "extension_points": ["analysis"],
  "dependencies": ["numpy", "pandas"],
  "permissions": ["read_data", "write_data"],
  "config": {
    "param1": {
      "type": "string",
      "default": "value",
      "description": "Parameter description"
    }
  },
  "min_platform_version": "1.0.0"
}
```

## Security

### Security Scanning

All plugins are automatically scanned for:
- Dangerous code patterns (eval, exec, system calls)
- Suspicious imports
- Dependency vulnerabilities
- File permission issues

### Sandbox Execution

Plugins run in Docker containers with:
- **Resource Limits**: CPU and memory constraints
- **Network Isolation**: No network access by default
- **Capability Restrictions**: Minimal Linux capabilities
- **Process Limits**: Maximum 100 processes

### Permissions

Plugins must declare required permissions:
- `read_data`: Read data from platform
- `write_data`: Write data to platform
- `network`: Network access
- `file_system`: File system access

## API Endpoints

### Plugin Management

- `POST /api/plugins/install` - Install plugin from package
- `DELETE /api/plugins/{plugin_id}` - Uninstall plugin
- `POST /api/plugins/{plugin_id}/enable` - Enable plugin
- `POST /api/plugins/{plugin_id}/disable` - Disable plugin
- `GET /api/plugins/list` - List installed plugins
- `GET /api/plugins/{plugin_id}` - Get plugin details
- `POST /api/plugins/{plugin_id}/execute` - Execute plugin
- `GET /api/plugins/{plugin_id}/executions` - Get execution history

### Marketplace

- `POST /api/plugins/marketplace/search` - Search marketplace
- `GET /api/plugins/marketplace/featured` - Get featured plugins
- `GET /api/plugins/marketplace/categories` - Get categories
- `POST /api/plugins/{plugin_id}/rate` - Rate plugin
- `POST /api/plugins/{plugin_id}/review` - Add review

### SDK

- `POST /api/plugins/sdk/create` - Create plugin project
- `GET /api/plugins/extension-points` - Get extension points

## Version Management

### Semantic Versioning

Plugins use semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Update Plugin

```bash
# Update to new version
curl -X POST "http://localhost:8001/api/plugins/{plugin_id}/update" \
  -H "Content-Type: application/json" \
  -d '{"target_version": "1.1.0"}'
```

### Rollback Plugin

```bash
# Rollback to previous version
curl -X POST "http://localhost:8001/api/plugins/{plugin_id}/rollback" \
  -H "Content-Type: application/json" \
  -d '{
    "target_version": "1.0.0",
    "reason": "Bug in new version"
  }'
```

## Best Practices

### 1. Input Validation

Always validate input data:
```python
def validate_input(self, input_data: Dict[str, Any]) -> bool:
    if 'data' not in input_data:
        raise ValueError("Missing required field: data")
    
    if not isinstance(input_data['data'], list):
        raise ValueError("Data must be a list")
    
    return True
```

### 2. Error Handling

Handle errors gracefully:
```python
try:
    result = self.process_data(data, parameters)
    return {
        'data': result,
        'errors': []
    }
except Exception as e:
    return {
        'data': None,
        'errors': [str(e)]
    }
```

### 3. Resource Cleanup

Clean up resources:
```python
def cleanup(self):
    """Cleanup resources"""
    # Close files, connections, etc.
    pass
```

### 4. Logging

Use logs for debugging:
```python
return {
    'data': result,
    'logs': [
        'Step 1 completed',
        'Step 2 completed',
        f'Processed {len(data)} items'
    ]
}
```

### 5. Configuration

Use config for customization:
```python
def __init__(self, context: Dict[str, Any]):
    self.config = context.get('config', {})
    self.threshold = self.config.get('threshold', 0.5)
```

## Troubleshooting

### Plugin Installation Fails

**Issue**: Security scan fails
**Solution**: Review security scan results and fix identified issues

**Issue**: Dependency resolution fails
**Solution**: Check dependency specifications in manifest.json

### Plugin Execution Fails

**Issue**: Container timeout
**Solution**: Increase timeout parameter or optimize plugin code

**Issue**: Permission denied
**Solution**: Add required permissions to manifest.json

### Docker Issues

**Issue**: Docker not running
**Solution**: Start Docker daemon

**Issue**: Image pull fails
**Solution**: Check internet connection and Docker registry access

## Requirements

- Docker installed and running
- Python 3.11+ (for Python plugins)
- R 4.3+ (for R plugins)
- Bandit (for security scanning): `pip install bandit`
- Safety (for dependency scanning): `pip install safety`

## Support

For issues and questions:
- GitHub Issues: [repository-url]
- Documentation: [docs-url]
- Community Forum: [forum-url]

## License

MIT License - See LICENSE file for details
