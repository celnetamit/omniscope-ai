# Report Generator - Quick Start Guide

## Overview
The Automated Report Generator creates publication-ready scientific reports in PDF, Word, and LaTeX formats with automatic citation management and methods sections.

## Quick Start

### 1. Generate a Simple Report

```bash
curl -X POST "http://localhost:8001/api/reports/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Research Report",
    "format": "pdf",
    "citation_style": "APA",
    "data": {
      "authors": "John Doe, Jane Smith",
      "abstract": "This study investigates...",
      "introduction": "Background information...",
      "results": "We found that...",
      "discussion": "These findings suggest..."
    }
  }'
```

### 2. Download the Report

```bash
curl -X GET "http://localhost:8001/api/reports/{report_id}/download" \
  --output my_report.pdf
```

### 3. List Available Templates

```bash
curl -X GET "http://localhost:8001/api/reports/templates"
```

## Python Examples

### Generate PDF Report with Methods

```python
import requests

# Generate report
response = requests.post("http://localhost:8001/api/reports/generate", json={
    "title": "Multi-Omics Analysis of Cancer Biomarkers",
    "format": "pdf",
    "citation_style": "Nature",
    "data": {
        "authors": "Smith J, Doe A, Johnson B",
        "abstract": "We performed comprehensive multi-omics analysis...",
        "introduction": "Cancer biomarkers are essential for...",
        "results": "Our analysis identified 150 significant biomarkers...",
        "discussion": "These findings provide new insights into..."
    },
    "pipeline_id": "pipeline_123",
    "model_id": "model_456",
    "include_methods": True,
    "include_citations": True
})

report = response.json()
print(f"Report ID: {report['report_id']}")
print(f"File path: {report['file_path']}")

# Download report
download_response = requests.get(
    f"http://localhost:8001/api/reports/{report['report_id']}/download"
)
with open("my_report.pdf", "wb") as f:
    f.write(download_response.content)
```

### Generate Word Document

```python
response = requests.post("http://localhost:8001/api/reports/generate", json={
    "title": "Quarterly Research Summary",
    "format": "docx",
    "citation_style": "APA",
    "data": {
        "authors": "Research Team",
        "abstract": "Summary of Q4 2024 research activities...",
        "tables": {
            "Results": {
                "headers": ["Gene", "P-value", "Fold Change"],
                "rows": [
                    ["BRCA1", "0.001", "2.5"],
                    ["TP53", "0.003", "1.8"],
                    ["EGFR", "0.002", "3.2"]
                ]
            }
        }
    }
})
```

### Create Custom Template

```python
response = requests.post("http://localhost:8001/api/reports/templates/custom", json={
    "name": "Clinical Trial Report",
    "sections": [
        {"title": "Executive Summary", "content_type": "text", "order": 1},
        {"title": "Study Design", "content_type": "text", "order": 2},
        {"title": "Methods", "content_type": "methods", "order": 3},
        {"title": "Results", "content_type": "text", "order": 4},
        {"title": "Statistical Analysis", "content_type": "table", "order": 5},
        {"title": "Conclusions", "content_type": "text", "order": 6},
        {"title": "References", "content_type": "text", "order": 7}
    ],
    "citation_style": "AMA",
    "format": "pdf"
})

template_id = response.json()["template_id"]
print(f"Created template: {template_id}")
```

## Citation Management

### Add Citations Programmatically

```python
from backend_db.citation_manager import CitationManager, Citation

# Initialize manager
manager = CitationManager(style="APA")

# Add article citation
article = Citation(
    citation_id="smith2024",
    authors=["Smith, J.", "Doe, A.", "Johnson, B."],
    year=2024,
    title="Novel Biomarkers in Cancer Research",
    journal="Nature Medicine",
    volume="30",
    issue="5",
    pages="123-145",
    doi="10.1038/nm.2024.123",
    citation_type="article"
)
manager.add_citation(article)

# Add book citation
book = Citation(
    citation_id="jones2023",
    authors=["Jones, M."],
    year=2023,
    title="Computational Biology Methods",
    publisher="Academic Press",
    citation_type="book"
)
manager.add_citation(book)

# Format in different styles
print("APA:", manager.format_citation("smith2024", "APA"))
print("MLA:", manager.format_citation("smith2024", "MLA"))
print("Nature:", manager.format_citation("smith2024", "Nature"))

# Get full bibliography
bibliography = manager.get_bibliography()
for citation in bibliography:
    print(citation)

# Export as BibTeX
bibtex = manager.export_bibtex()
with open("references.bib", "w") as f:
    f.write(bibtex)
```

## Methods Section Generation

### Auto-Generate Methods

```python
from backend_db.methods_generator import MethodsGenerator

generator = MethodsGenerator()

# Generate from model data
methods_html = generator.generate_methods(
    pipeline_data={
        "nodes": [
            {"type": "upload"},
            {"type": "normalize"},
            {"type": "filter"},
            {"type": "feature_selection"}
        ]
    },
    model_data={
        "type": "automl",
        "architecture": "ensemble",
        "training_config": {
            "validation_split": 0.2,
            "epochs": 100,
            "batch_size": 32
        },
        "metrics": {
            "accuracy": 0.95,
            "auc": 0.98,
            "f1_score": 0.94,
            "precision": 0.93,
            "recall": 0.96
        }
    }
)

print(methods_html)

# Get software citations
citations = generator.get_software_citations()
for citation in citations:
    print(f"{citation['citation_id']}: {citation['title']}")
```

## Citation Styles

### APA (American Psychological Association)
```
Smith, J. & Doe, A. (2024). Novel Biomarkers in Cancer Research. 
Nature Medicine, 30(5), 123-145. https://doi.org/10.1038/nm.2024.123.
```

### MLA (Modern Language Association)
```
Smith, J., and Doe, A.. "Novel Biomarkers in Cancer Research". 
Nature Medicine, vol. 30, no. 5, 2024, pp. 123-145.
```

### Chicago
```
Smith, J., and Doe, A.. 2024. "Novel Biomarkers in Cancer Research." 
Nature Medicine 30, no. 5: 123-145. https://doi.org/10.1038/nm.2024.123.
```

### Nature
```
Smith, J., Doe, A.. Novel Biomarkers in Cancer Research. 
Nature Medicine 30, 123-145 (2024). https://doi.org/10.1038/nm.2024.123
```

### Science
```
Smith, J., Doe, A., Novel Biomarkers in Cancer Research. 
Nature Medicine 30, 123-145 (2024).
```

## Report Data Structure

### Complete Example

```python
report_data = {
    "title": "Comprehensive Multi-Omics Analysis",
    "format": "pdf",
    "citation_style": "Nature",
    "data": {
        "authors": "Smith J, Doe A, Johnson B",
        "abstract": "We performed comprehensive analysis...",
        "introduction": "Background and motivation...",
        "results": "Key findings and observations...",
        "discussion": "Interpretation and implications...",
        
        # Tables
        "tables": {
            "Biomarker Results": {
                "headers": ["Gene", "P-value", "Fold Change", "FDR"],
                "rows": [
                    ["BRCA1", "0.001", "2.5", "0.01"],
                    ["TP53", "0.003", "1.8", "0.02"],
                    ["EGFR", "0.002", "3.2", "0.015"]
                ]
            },
            "Model Performance": {
                "headers": ["Metric", "Training", "Validation", "Test"],
                "rows": [
                    ["Accuracy", "0.96", "0.94", "0.95"],
                    ["AUC-ROC", "0.99", "0.97", "0.98"],
                    ["F1 Score", "0.95", "0.93", "0.94"]
                ]
            }
        },
        
        # Figures
        "figures": {
            "ROC Curve": {
                "path": "figures/roc_curve.png",
                "caption": "Receiver Operating Characteristic curve showing model performance"
            },
            "Feature Importance": {
                "path": "figures/feature_importance.png",
                "caption": "Top 20 features ranked by importance score"
            }
        }
    },
    "pipeline_id": "pipeline_123",
    "model_id": "model_456",
    "include_methods": True,
    "include_citations": True
}
```

## Template Customization

### Custom Jinja2 Filters

```python
from backend_db.report_templates import TemplateEngine

engine = TemplateEngine()

# Add custom filter
def format_gene_name(value):
    """Format gene names in italics"""
    return f"<i>{value}</i>"

engine.add_custom_filter('gene_name', format_gene_name)

# Add custom function
def calculate_fdr(pvalues):
    """Calculate FDR from p-values"""
    # Implementation here
    return fdr_values

engine.add_custom_function('calculate_fdr', calculate_fdr)
```

### Custom Template

```html
{% extends "base.html" %}

{% block content %}
<h1>{{ title }}</h1>

<h2>Abstract</h2>
<p>{{ data.abstract }}</p>

<h2>Key Findings</h2>
<ul>
{% for finding in data.findings %}
    <li>{{ finding }}</li>
{% endfor %}
</ul>

<h2>Biomarkers</h2>
<table>
    <thead>
        <tr>
            <th>Gene</th>
            <th>P-value</th>
            <th>Effect Size</th>
        </tr>
    </thead>
    <tbody>
    {% for biomarker in data.biomarkers %}
        <tr>
            <td>{{ biomarker.gene | gene_name }}</td>
            <td>{{ biomarker.pvalue | format_pvalue }}</td>
            <td>{{ biomarker.effect | format_number(3) }}</td>
        </tr>
    {% endfor %}
    </tbody>
</table>
{% endblock %}
```

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/reports/generate` | Generate new report |
| GET | `/api/reports/{report_id}/download` | Download report file |
| GET | `/api/reports/templates` | List all templates |
| POST | `/api/reports/templates/custom` | Create custom template |
| GET | `/api/reports/{report_id}` | Get report metadata |
| DELETE | `/api/reports/{report_id}` | Delete report |

## Common Use Cases

### 1. Quarterly Research Report
```python
requests.post("/api/reports/generate", json={
    "title": "Q4 2024 Research Summary",
    "format": "docx",
    "citation_style": "APA",
    "data": {
        "authors": "Research Team",
        "executive_summary": "...",
        "key_achievements": "...",
        "ongoing_projects": "...",
        "future_plans": "..."
    }
})
```

### 2. Publication Manuscript
```python
requests.post("/api/reports/generate", json={
    "title": "Novel Therapeutic Targets in Cancer",
    "format": "latex",
    "citation_style": "Nature",
    "data": {...},
    "include_methods": True,
    "include_citations": True
})
```

### 3. Clinical Trial Report
```python
requests.post("/api/reports/generate", json={
    "title": "Phase II Clinical Trial Results",
    "format": "pdf",
    "citation_style": "AMA",
    "template_id": "clinical_trial_template",
    "data": {...}
})
```

## Troubleshooting

### Report Generation Fails
- Check that all required data fields are provided
- Verify file paths for figures exist
- Ensure output directory has write permissions

### Citation Formatting Issues
- Verify citation data includes all required fields
- Check that citation style is one of: APA, MLA, Chicago, Nature, Science
- Ensure author names are properly formatted

### Template Rendering Errors
- Validate template syntax
- Check that all referenced variables exist in data
- Verify custom filters are registered

## Best Practices

1. **Always include metadata**: Authors, date, affiliations
2. **Use consistent citation style**: Match journal requirements
3. **Include figure captions**: Describe what the figure shows
4. **Generate methods automatically**: Ensures reproducibility
5. **Test with small datasets first**: Verify formatting before large reports
6. **Keep templates simple**: Complex templates are harder to maintain
7. **Version control templates**: Track changes to report structure

## Support

For issues or questions:
- Check API documentation: `http://localhost:8001/docs`
- Review test examples: `test_report_generator.py`
- See implementation details: `TASK_7_IMPLEMENTATION_SUMMARY.md`

---

**Last Updated**: November 13, 2025
