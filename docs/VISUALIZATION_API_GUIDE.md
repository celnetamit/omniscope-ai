# Visualization API Guide

## Quick Reference

This guide provides quick examples for using the OmniScope AI visualization endpoints.

## Base URL
```
http://localhost:8001/api/visualization
```

## Endpoints

### 1. Load Protein Structure

Load and parse PDB protein structures for 3D visualization.

**Endpoint:** `POST /protein/load`

**Example: Fetch from RCSB PDB**
```python
import requests

response = requests.post(
    "http://localhost:8001/api/visualization/protein/load",
    json={"pdb_id": "1ABC"}
)

data = response.json()
print(f"Loaded {data['atom_count']} atoms")
```

**Example: Upload PDB Content**
```python
with open("protein.pdb", "r") as f:
    pdb_content = f.read()

response = requests.post(
    "http://localhost:8001/api/visualization/protein/load",
    json={
        "pdb_content": pdb_content,
        "structure_id": "my_protein"
    }
)
```

---

### 2. Generate Network Graph

Create 3D network visualizations from interaction data.

**Endpoint:** `POST /network/generate`

**Example: Gene Interaction Network**
```python
import requests

network_data = {
    "nodes": [
        {"id": "TP53", "label": "TP53", "type": "gene"},
        {"id": "MDM2", "label": "MDM2", "type": "gene"},
        {"id": "CDKN1A", "label": "CDKN1A", "type": "gene"}
    ],
    "edges": [
        {"source": "TP53", "target": "MDM2", "weight": 0.9},
        {"source": "TP53", "target": "CDKN1A", "weight": 0.85}
    ]
}

response = requests.post(
    "http://localhost:8001/api/visualization/network/generate",
    json=network_data
)

result = response.json()
print(f"Network: {result['node_count']} nodes, {result['edge_count']} edges")
print(f"Density: {result['density']:.3f}")
```

**Example: Pathway Network with Metadata**
```python
network_data = {
    "nodes": [
        {
            "id": "gene1",
            "label": "Gene 1",
            "type": "gene",
            "metadata": {
                "expression": 2.5,
                "pvalue": 0.001
            }
        }
    ],
    "edges": [
        {
            "source": "gene1",
            "target": "gene2",
            "weight": 0.8,
            "type": "activation"
        }
    ]
}
```

---

### 3. Dimensionality Reduction

Reduce high-dimensional omics data to 3D for visualization.

**Endpoint:** `POST /dimensionality-reduction`

**Example: PCA**
```python
import requests
import numpy as np

# Generate sample data: 100 samples × 500 features
data = np.random.randn(100, 500).tolist()

response = requests.post(
    "http://localhost:8001/api/visualization/dimensionality-reduction",
    json={
        "data": data,
        "method": "pca"
    }
)

result = response.json()
print(f"Variance explained: {result['total_variance_explained']:.2%}")
coordinates = result['coordinates']  # 3D coordinates for plotting
```

**Example: t-SNE with Metadata**
```python
# Sample data with group labels
data = np.random.randn(100, 500).tolist()
groups = ["control"] * 50 + ["treatment"] * 50

response = requests.post(
    "http://localhost:8001/api/visualization/dimensionality-reduction",
    json={
        "data": data,
        "method": "tsne",
        "metadata": groups,
        "metadata_name": "condition",
        "parameters": {
            "perplexity": 30
        }
    }
)

result = response.json()
coordinates = result['coordinates']
colors = result['metadata']['color_indices']  # For coloring points
```

**Example: UMAP**
```python
response = requests.post(
    "http://localhost:8001/api/visualization/dimensionality-reduction",
    json={
        "data": data,
        "method": "umap",
        "parameters": {
            "n_neighbors": 15,
            "min_dist": 0.1
        }
    }
)
```

---

## Frontend Integration

### React Component Example

```typescript
import { useState } from 'react';

function ProteinViewer({ pdbId }: { pdbId: string }) {
  const [structure, setStructure] = useState(null);
  
  const loadProtein = async () => {
    const response = await fetch('/api/visualization/protein/load', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pdb_id: pdbId })
    });
    
    const data = await response.json();
    setStructure(data);
  };
  
  return (
    <div>
      <button onClick={loadProtein}>Load Protein</button>
      {structure && (
        <div>
          <p>Atoms: {structure.atom_count}</p>
          <p>Chains: {structure.chain_count}</p>
          {/* Render with NGL Viewer */}
        </div>
      )}
    </div>
  );
}
```

---

## Error Handling

All endpoints return standard HTTP status codes:

```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        print("Invalid input:", e.response.json()['detail'])
    elif e.response.status_code == 404:
        print("Resource not found")
    elif e.response.status_code == 500:
        print("Server error:", e.response.json()['detail'])
```

---

## Method Comparison

### Dimensionality Reduction Methods

| Method | Speed | Preserves | Best For |
|--------|-------|-----------|----------|
| PCA | Fast | Global structure | Initial exploration, linear patterns |
| t-SNE | Slow | Local structure | Cluster visualization, non-linear |
| UMAP | Medium | Both | Large datasets, balanced view |

**Recommendations:**
- Start with PCA for quick overview
- Use t-SNE for detailed cluster analysis
- Use UMAP for large datasets (>10,000 samples)

---

## Performance Tips

1. **Protein Structures**
   - Cache PDB files locally
   - Use structure_id for tracking

2. **Network Graphs**
   - Limit to <5000 nodes for real-time interaction
   - Pre-compute centrality metrics if needed

3. **Dimensionality Reduction**
   - PCA: Can handle 100,000+ samples
   - t-SNE: Limit to <10,000 samples
   - UMAP: Good for 10,000-100,000 samples

---

## Complete Example: Multi-Omics Analysis

```python
import requests
import pandas as pd
import numpy as np

# 1. Load your omics data
data = pd.read_csv("expression_data.csv", index_col=0)
metadata = pd.read_csv("sample_metadata.csv")

# 2. Perform dimensionality reduction
response = requests.post(
    "http://localhost:8001/api/visualization/dimensionality-reduction",
    json={
        "data": data.values.tolist(),
        "method": "umap",
        "metadata": metadata['condition'].tolist(),
        "metadata_name": "condition"
    }
)

reduction_result = response.json()

# 3. Generate interaction network from top features
top_genes = data.var().nlargest(50).index.tolist()

nodes = [{"id": gene, "label": gene} for gene in top_genes]
edges = []  # Add correlation-based edges

network_response = requests.post(
    "http://localhost:8001/api/visualization/network/generate",
    json={"nodes": nodes, "edges": edges}
)

network_result = network_response.json()

# 4. Visualize results
print(f"Reduced {data.shape[1]} features to 3D")
print(f"Network: {network_result['node_count']} nodes")
print(f"Centrality metrics available: {list(network_result['centrality_metrics'].keys())}")
```

---

## API Documentation

For complete API documentation with interactive testing:
- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

---

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review error messages in response
3. Verify input data format matches schemas
4. Check server logs for detailed errors
