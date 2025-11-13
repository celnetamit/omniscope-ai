"""
Plugin Development SDK for OmniScope AI
Provides tools and templates for plugin development
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class PluginTemplate:
    """Plugin template generator"""
    
    PYTHON_TEMPLATE = '''"""
{plugin_name} - OmniScope AI Plugin
{description}

Author: {author}
Version: {version}
"""

import json
import sys
from typing import Dict, Any


class {class_name}:
    """Main plugin class"""
    
    def __init__(self, context: Dict[str, Any]):
        """
        Initialize plugin
        
        Args:
            context: Plugin execution context
        """
        self.context = context
        self.config = context.get('config', {{}})
        self.plugin_id = context.get('plugin_id')
        self.plugin_name = context.get('plugin_name')
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data
        
        Args:
            input_data: Input data to validate
        
        Returns:
            bool: True if valid
        
        Raises:
            ValueError: If validation fails
        """
        # TODO: Implement input validation
        if 'data' not in input_data:
            raise ValueError("Missing required field: data")
        
        return True
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute plugin logic
        
        Args:
            input_data: Input data
        
        Returns:
            Dict: Output data
        """
        # TODO: Implement plugin logic
        data = input_data.get('data')
        parameters = input_data.get('parameters', {{}})
        
        # Example processing
        result = self.process_data(data, parameters)
        
        return {{
            'data': result,
            'metadata': {{
                'plugin_id': self.plugin_id,
                'plugin_name': self.plugin_name
            }},
            'logs': ['Processing completed successfully'],
            'warnings': [],
            'errors': []
        }}
    
    def process_data(self, data: Any, parameters: Dict[str, Any]) -> Any:
        """
        Process data
        
        Args:
            data: Input data
            parameters: Processing parameters
        
        Returns:
            Processed data
        """
        # TODO: Implement data processing
        return data
    
    def cleanup(self):
        """Cleanup resources"""
        pass


def main():
    """Main entry point for plugin execution"""
    # Read input from file
    with open('/plugin/input.json', 'r') as f:
        input_data = json.load(f)
    
    # Read context
    context = input_data.get('context', {{}})
    
    # Initialize plugin
    plugin = {class_name}(context)
    
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
        error_output = {{
            'data': None,
            'errors': [str(e)],
            'logs': [],
            'warnings': []
        }}
        with open('/plugin/output.json', 'w') as f:
            json.dump(error_output, f, indent=2)
        sys.exit(1)
'''
    
    R_TEMPLATE = '''# {plugin_name} - OmniScope AI Plugin
# {description}
#
# Author: {author}
# Version: {version}

library(jsonlite)

# Main plugin class
{class_name} <- setRefClass(
  "{class_name}",
  
  fields = list(
    context = "list",
    config = "list",
    plugin_id = "character",
    plugin_name = "character"
  ),
  
  methods = list(
    initialize = function(context) {{
      "Initialize plugin"
      .self$context <- context
      .self$config <- context$config
      .self$plugin_id <- context$plugin_id
      .self$plugin_name <- context$plugin_name
    }},
    
    validate_input = function(input_data) {{
      "Validate input data"
      # TODO: Implement input validation
      if (!"data" %in% names(input_data)) {{
        stop("Missing required field: data")
      }}
      return(TRUE)
    }},
    
    execute = function(input_data) {{
      "Execute plugin logic"
      # TODO: Implement plugin logic
      data <- input_data$data
      parameters <- input_data$parameters
      
      # Example processing
      result <- .self$process_data(data, parameters)
      
      return(list(
        data = result,
        metadata = list(
          plugin_id = .self$plugin_id,
          plugin_name = .self$plugin_name
        ),
        logs = list("Processing completed successfully"),
        warnings = list(),
        errors = list()
      ))
    }},
    
    process_data = function(data, parameters) {{
      "Process data"
      # TODO: Implement data processing
      return(data)
    }},
    
    cleanup = function() {{
      "Cleanup resources"
    }}
  )
)

# Main entry point
main <- function() {{
  # Read input from file
  input_data <- fromJSON("/plugin/input.json")
  
  # Read context
  context <- input_data$context
  
  # Initialize plugin
  plugin <- {class_name}$new(context)
  
  # Validate input
  plugin$validate_input(input_data)
  
  # Execute plugin
  output <- plugin$execute(input_data)
  
  # Write output to file
  write_json(output, "/plugin/output.json", auto_unbox = TRUE, pretty = TRUE)
  
  # Cleanup
  plugin$cleanup()
}}

# Run main function
tryCatch(
  {{
    main()
    quit(status = 0)
  }},
  error = function(e) {{
    error_output <- list(
      data = NULL,
      errors = list(as.character(e)),
      logs = list(),
      warnings = list()
    )
    write_json(error_output, "/plugin/output.json", auto_unbox = TRUE, pretty = TRUE)
    quit(status = 1)
  }}
)
'''
    
    MANIFEST_TEMPLATE = '''{
  "name": "{plugin_name}",
  "version": "{version}",
  "author": "{author}",
  "author_email": "{author_email}",
  "description": "{description}",
  "language": "{language}",
  "entry_point": "{entry_point}",
  "category": "{category}",
  "tags": {tags},
  "extension_points": {extension_points},
  "dependencies": {dependencies},
  "permissions": {permissions},
  "config": {{
    "param1": {{
      "type": "string",
      "default": "value",
      "description": "Parameter description"
    }}
  }},
  "min_platform_version": "1.0.0"
}
'''
    
    README_TEMPLATE = '''# {plugin_name}

{description}

## Installation

```bash
# Install plugin via OmniScope AI plugin manager
```

## Usage

```python
# Example usage
```

## Configuration

- `param1`: Parameter description

## Requirements

{requirements}

## Author

{author} ({author_email})

## License

{license}

## Version

{version}
'''
    
    @staticmethod
    def generate_plugin(
        output_dir: str,
        plugin_name: str,
        language: str,
        author: str,
        description: str,
        version: str = "1.0.0",
        author_email: str = "",
        category: str = "analysis",
        tags: list = None,
        extension_points: list = None,
        dependencies: list = None,
        permissions: list = None,
        license: str = "MIT"
    ) -> Dict[str, str]:
        """
        Generate plugin template
        
        Args:
            output_dir: Output directory
            plugin_name: Plugin name
            language: Programming language (python, r)
            author: Author name
            description: Plugin description
            version: Plugin version
            author_email: Author email
            category: Plugin category
            tags: Plugin tags
            extension_points: Extension points
            dependencies: Dependencies
            permissions: Required permissions
            license: License type
        
        Returns:
            Dict: Generated file paths
        """
        if language not in ['python', 'r']:
            raise ValueError(f"Unsupported language: {language}")
        
        # Create output directory
        plugin_dir = os.path.join(output_dir, plugin_name)
        os.makedirs(plugin_dir, exist_ok=True)
        
        # Generate class name
        class_name = ''.join(word.capitalize() for word in plugin_name.split('_'))
        
        # Default values
        tags = tags or ['custom']
        extension_points = extension_points or ['analysis']
        dependencies = dependencies or []
        permissions = permissions or []
        
        generated_files = {}
        
        # Generate main plugin file
        if language == 'python':
            entry_point = f"{plugin_name}.py"
            plugin_code = PluginTemplate.PYTHON_TEMPLATE.format(
                plugin_name=plugin_name,
                description=description,
                author=author,
                version=version,
                class_name=class_name
            )
            
            plugin_file = os.path.join(plugin_dir, entry_point)
            with open(plugin_file, 'w') as f:
                f.write(plugin_code)
            generated_files['plugin'] = plugin_file
            
            # Generate requirements.txt
            if dependencies:
                req_file = os.path.join(plugin_dir, 'requirements.txt')
                with open(req_file, 'w') as f:
                    f.write('\n'.join(dependencies))
                generated_files['requirements'] = req_file
        
        else:  # R
            entry_point = f"{plugin_name}.R"
            plugin_code = PluginTemplate.R_TEMPLATE.format(
                plugin_name=plugin_name,
                description=description,
                author=author,
                version=version,
                class_name=class_name
            )
            
            plugin_file = os.path.join(plugin_dir, entry_point)
            with open(plugin_file, 'w') as f:
                f.write(plugin_code)
            generated_files['plugin'] = plugin_file
        
        # Generate manifest.json
        manifest = PluginTemplate.MANIFEST_TEMPLATE.format(
            plugin_name=plugin_name,
            version=version,
            author=author,
            author_email=author_email,
            description=description,
            language=language,
            entry_point=entry_point,
            category=category,
            tags=json.dumps(tags),
            extension_points=json.dumps(extension_points),
            dependencies=json.dumps(dependencies),
            permissions=json.dumps(permissions)
        )
        
        manifest_file = os.path.join(plugin_dir, 'manifest.json')
        with open(manifest_file, 'w') as f:
            f.write(manifest)
        generated_files['manifest'] = manifest_file
        
        # Generate README.md
        requirements = '\n'.join(f"- {dep}" for dep in dependencies) if dependencies else "None"
        
        readme = PluginTemplate.README_TEMPLATE.format(
            plugin_name=plugin_name,
            description=description,
            requirements=requirements,
            author=author,
            author_email=author_email,
            license=license,
            version=version
        )
        
        readme_file = os.path.join(plugin_dir, 'README.md')
        with open(readme_file, 'w') as f:
            f.write(readme)
        generated_files['readme'] = readme_file
        
        # Generate .gitignore
        gitignore_content = '''__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.Rhistory
.RData
.Rproj.user
'''
        gitignore_file = os.path.join(plugin_dir, '.gitignore')
        with open(gitignore_file, 'w') as f:
            f.write(gitignore_content)
        generated_files['gitignore'] = gitignore_file
        
        return generated_files


class PluginSDK:
    """SDK utilities for plugin development"""
    
    @staticmethod
    def create_plugin_project(
        name: str,
        language: str,
        output_dir: str = "./plugins",
        **kwargs
    ) -> str:
        """
        Create a new plugin project
        
        Args:
            name: Plugin name
            language: Programming language
            output_dir: Output directory
            **kwargs: Additional template parameters
        
        Returns:
            str: Project directory path
        """
        files = PluginTemplate.generate_plugin(
            output_dir=output_dir,
            plugin_name=name,
            language=language,
            **kwargs
        )
        
        project_dir = os.path.dirname(files['plugin'])
        
        print(f"✅ Plugin project created: {project_dir}")
        print("\nGenerated files:")
        for file_type, file_path in files.items():
            print(f"  - {file_type}: {file_path}")
        
        return project_dir
    
    @staticmethod
    def validate_manifest(manifest_path: str) -> tuple[bool, Optional[str]]:
        """
        Validate plugin manifest
        
        Args:
            manifest_path: Path to manifest.json
        
        Returns:
            tuple: (is_valid, error_message)
        """
        required_fields = [
            'name', 'version', 'author', 'description',
            'language', 'entry_point'
        ]
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Check required fields
            for field in required_fields:
                if field not in manifest:
                    return False, f"Missing required field: {field}"
            
            # Validate language
            if manifest['language'] not in ['python', 'r']:
                return False, f"Invalid language: {manifest['language']}"
            
            # Validate version format
            version_pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$'
            import re
            if not re.match(version_pattern, manifest['version']):
                return False, f"Invalid version format: {manifest['version']}"
            
            return True, None
        
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def package_plugin(plugin_dir: str, output_file: Optional[str] = None) -> str:
        """
        Package plugin for distribution
        
        Args:
            plugin_dir: Plugin directory
            output_file: Output file path (optional)
        
        Returns:
            str: Package file path
        """
        import tarfile
        
        if not output_file:
            plugin_name = os.path.basename(plugin_dir)
            output_file = f"{plugin_name}.tar.gz"
        
        with tarfile.open(output_file, 'w:gz') as tar:
            tar.add(plugin_dir, arcname=os.path.basename(plugin_dir))
        
        print(f"✅ Plugin packaged: {output_file}")
        
        return output_file
