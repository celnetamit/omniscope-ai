"""
Template Engine for Report Generation
Jinja2-based template system with custom filters and functions
"""

from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
from pathlib import Path
from typing import Dict, Any, List
import os
from datetime import datetime

class TemplateEngine:
    """
    Jinja2 template engine for report generation
    
    Requirements: 5.6
    """
    
    def __init__(self, template_dir: str = None):
        """Initialize the template engine"""
        if template_dir is None:
            # Create default template directory
            template_dir = Path("report_templates")
            template_dir.mkdir(exist_ok=True)
            self.template_dir = str(template_dir)
        else:
            self.template_dir = template_dir
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register custom filters
        self._register_custom_filters()
        
        # Register custom functions
        self._register_custom_functions()
        
        # Create default templates
        self._create_default_templates()
    
    def _register_custom_filters(self):
        """Register custom Jinja2 filters"""
        
        def format_date(value, format_string='%Y-%m-%d'):
            """Format datetime objects"""
            if isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value)
                except:
                    return value
            if isinstance(value, datetime):
                return value.strftime(format_string)
            return value
        
        def format_number(value, decimals=2):
            """Format numbers with specified decimal places"""
            try:
                return f"{float(value):.{decimals}f}"
            except:
                return value
        
        def format_pvalue(value):
            """Format p-values in scientific notation"""
            try:
                p = float(value)
                if p < 0.001:
                    return f"{p:.2e}"
                else:
                    return f"{p:.4f}"
            except:
                return value
        
        def capitalize_words(value):
            """Capitalize each word in a string"""
            return ' '.join(word.capitalize() for word in str(value).split())
        
        def truncate_text(value, length=100, suffix='...'):
            """Truncate text to specified length"""
            text = str(value)
            if len(text) <= length:
                return text
            return text[:length].rsplit(' ', 1)[0] + suffix
        
        # Register all filters
        self.env.filters['format_date'] = format_date
        self.env.filters['format_number'] = format_number
        self.env.filters['format_pvalue'] = format_pvalue
        self.env.filters['capitalize_words'] = capitalize_words
        self.env.filters['truncate_text'] = truncate_text
    
    def _register_custom_functions(self):
        """Register custom Jinja2 functions"""
        
        def current_date(format_string='%Y-%m-%d'):
            """Get current date"""
            return datetime.now().strftime(format_string)
        
        def format_citation(citation_dict, style='APA'):
            """Format a citation in specified style"""
            # Basic citation formatting
            authors = citation_dict.get('authors', 'Unknown')
            year = citation_dict.get('year', 'n.d.')
            title = citation_dict.get('title', 'Untitled')
            
            if style == 'APA':
                return f"{authors} ({year}). {title}."
            elif style == 'MLA':
                return f"{authors}. \"{title}.\" {year}."
            elif style == 'Chicago':
                return f"{authors}. {year}. {title}."
            else:
                return f"{authors} ({year}). {title}."
        
        def generate_toc(sections):
            """Generate table of contents"""
            toc = []
            for i, section in enumerate(sections, 1):
                toc.append(f"{i}. {section.get('title', 'Untitled')}")
            return '\n'.join(toc)
        
        # Add functions to environment globals
        self.env.globals['current_date'] = current_date
        self.env.globals['format_citation'] = format_citation
        self.env.globals['generate_toc'] = generate_toc
    
    def _create_default_templates(self):
        """Create default report templates"""
        
        # Base template
        base_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 40px;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        .metadata {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 30px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
        }
        .figure {
            margin: 20px 0;
            text-align: center;
        }
        .figure-caption {
            font-style: italic;
            color: #7f8c8d;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
"""
        
        # Scientific report template
        scientific_template = """
{% extends "base.html" %}

{% block content %}
<h1>{{ title }}</h1>
<div class="metadata">
    <p>Generated: {{ current_date() }}</p>
    {% if data.authors %}
    <p>Authors: {{ data.authors }}</p>
    {% endif %}
</div>

{% for section in sections %}
<section>
    <h2>{{ section.title }}</h2>
    
    {% if section.content_type == 'text' %}
        <p>{{ section.content or data.get(section.title.lower(), 'Content not provided.') }}</p>
    
    {% elif section.content_type == 'methods' %}
        {% if methods %}
        {{ methods | safe }}
        {% else %}
        <p>Methods section not available.</p>
        {% endif %}
    
    {% elif section.content_type == 'table' %}
        {% if data.tables and data.tables.get(section.title) %}
        <table>
            <thead>
                <tr>
                    {% for header in data.tables[section.title].headers %}
                    <th>{{ header }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in data.tables[section.title].rows %}
                <tr>
                    {% for cell in row %}
                    <td>{{ cell }}</td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}
    
    {% elif section.content_type == 'figure' %}
        {% if data.figures and data.figures.get(section.title) %}
        <div class="figure">
            <img src="{{ data.figures[section.title].path }}" alt="{{ section.title }}" style="max-width: 100%;">
            <p class="figure-caption">Figure: {{ data.figures[section.title].caption }}</p>
        </div>
        {% endif %}
    {% endif %}
</section>
{% endfor %}

{% if citations %}
<section>
    <h2>References</h2>
    <ol>
        {% for citation in citations %}
        <li>{{ citation }}</li>
        {% endfor %}
    </ol>
</section>
{% endif %}
{% endblock %}
"""
        
        # Write templates to files
        base_path = Path(self.template_dir) / "base.html"
        with open(base_path, 'w') as f:
            f.write(base_template)
        
        scientific_path = Path(self.template_dir) / "scientific_report.html"
        with open(scientific_path, 'w') as f:
            f.write(scientific_template)
    
    def render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        Render a template with provided data
        
        Args:
            template_name: Name of the template file (without extension)
            data: Dictionary of data to render in template
            
        Returns:
            Rendered template as string
        """
        try:
            # Add .html extension if not present
            if not template_name.endswith('.html'):
                template_name = f"{template_name}.html"
            
            # Load and render template
            template = self.env.get_template(template_name)
            return template.render(**data)
            
        except Exception as e:
            raise Exception(f"Failed to render template '{template_name}': {str(e)}")
    
    def render_string(self, template_string: str, data: Dict[str, Any]) -> str:
        """
        Render a template from string
        
        Args:
            template_string: Template content as string
            data: Dictionary of data to render in template
            
        Returns:
            Rendered template as string
        """
        try:
            template = self.env.from_string(template_string)
            return template.render(**data)
        except Exception as e:
            raise Exception(f"Failed to render template string: {str(e)}")
    
    def add_custom_filter(self, name: str, filter_func):
        """Add a custom filter to the environment"""
        self.env.filters[name] = filter_func
    
    def add_custom_function(self, name: str, func):
        """Add a custom function to the environment"""
        self.env.globals[name] = func
    
    def list_templates(self) -> List[str]:
        """List all available templates"""
        template_path = Path(self.template_dir)
        if not template_path.exists():
            return []
        return [f.name for f in template_path.glob('*.html')]
