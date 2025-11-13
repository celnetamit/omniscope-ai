"""
3D Visualization Module for OmniScope AI
Handles protein structure parsing, network generation, and dimensionality reduction
"""

from typing import Dict, List, Optional, Any, Tuple
import json
import io
from Bio import PDB
from Bio.PDB import PDBIO, Select
import networkx as nx
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import numpy as np
import pandas as pd


class ProteinStructureParser:
    """Parse and process PDB protein structure files"""
    
    def __init__(self):
        self.parser = PDB.PDBParser(QUIET=True)
        self.io = PDBIO()
    
    def parse_pdb_file(self, pdb_content: str, structure_id: str = "structure") -> Dict[str, Any]:
        """
        Parse PDB file content and extract structure information
        
        Args:
            pdb_content: PDB file content as string
            structure_id: Identifier for the structure
            
        Returns:
            Dictionary containing structure data for NGL Viewer
        """
        try:
            # Parse PDB content
            pdb_io = io.StringIO(pdb_content)
            structure = self.parser.get_structure(structure_id, pdb_io)
            
            # Extract structure information
            atoms = []
            residues = []
            chains = []
            
            for model in structure:
                for chain in model:
                    chain_id = chain.get_id()
                    chains.append({
                        "id": chain_id,
                        "residue_count": len(list(chain.get_residues()))
                    })
                    
                    for residue in chain:
                        res_id = residue.get_id()
                        residues.append({
                            "chain": chain_id,
                            "name": residue.get_resname(),
                            "number": res_id[1],
                            "insertion_code": res_id[2]
                        })
                        
                        for atom in residue:
                            coord = atom.get_coord()
                            atoms.append({
                                "serial": atom.get_serial_number(),
                                "name": atom.get_name(),
                                "element": atom.element,
                                "residue": residue.get_resname(),
                                "chain": chain_id,
                                "x": float(coord[0]),
                                "y": float(coord[1]),
                                "z": float(coord[2])
                            })
            
            return {
                "structure_id": structure_id,
                "pdb_content": pdb_content,
                "atoms": atoms,
                "residues": residues,
                "chains": chains,
                "atom_count": len(atoms),
                "residue_count": len(residues),
                "chain_count": len(chains)
            }
            
        except Exception as e:
            raise ValueError(f"Failed to parse PDB file: {str(e)}")
    
    def fetch_pdb_from_id(self, pdb_id: str) -> str:
        """
        Fetch PDB file content from RCSB PDB database
        
        Args:
            pdb_id: PDB identifier (e.g., "1ABC")
            
        Returns:
            PDB file content as string
        """
        try:
            from urllib import request
            url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
            with request.urlopen(url) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to fetch PDB {pdb_id}: {str(e)}")
    
    def get_structure_summary(self, pdb_content: str) -> Dict[str, Any]:
        """Get summary statistics of protein structure"""
        structure_data = self.parse_pdb_file(pdb_content)
        
        return {
            "atom_count": structure_data["atom_count"],
            "residue_count": structure_data["residue_count"],
            "chain_count": structure_data["chain_count"],
            "chains": structure_data["chains"]
        }


class NetworkGraphGenerator:
    """Generate 3D network graphs for pathway and interaction data"""
    
    def __init__(self):
        self.graph = None
    
    def create_network_from_interactions(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create network graph from node and edge data
        
        Args:
            nodes: List of node dictionaries with 'id', 'label', and optional metadata
            edges: List of edge dictionaries with 'source', 'target', and optional 'weight'
            
        Returns:
            Network data formatted for 3D visualization
        """
        # Create NetworkX graph
        G = nx.Graph()
        
        # Add nodes
        for node in nodes:
            G.add_node(
                node['id'],
                label=node.get('label', node['id']),
                **{k: v for k, v in node.items() if k not in ['id', 'label']}
            )
        
        # Add edges
        for edge in edges:
            G.add_edge(
                edge['source'],
                edge['target'],
                weight=edge.get('weight', 1.0),
                **{k: v for k, v in edge.items() if k not in ['source', 'target', 'weight']}
            )
        
        self.graph = G
        
        # Calculate 3D layout using spring layout
        pos_3d = self._calculate_3d_layout(G)
        
        # Prepare node data with positions
        node_data = []
        for node_id in G.nodes():
            node_attrs = G.nodes[node_id]
            pos = pos_3d[node_id]
            node_data.append({
                "id": node_id,
                "label": node_attrs.get('label', node_id),
                "x": float(pos[0]),
                "y": float(pos[1]),
                "z": float(pos[2]),
                "degree": G.degree(node_id),
                **{k: v for k, v in node_attrs.items() if k != 'label'}
            })
        
        # Prepare edge data
        edge_data = []
        for source, target in G.edges():
            edge_attrs = G.edges[source, target]
            edge_data.append({
                "source": source,
                "target": target,
                "weight": edge_attrs.get('weight', 1.0),
                **{k: v for k, v in edge_attrs.items() if k != 'weight'}
            })
        
        return {
            "nodes": node_data,
            "edges": edge_data,
            "node_count": len(node_data),
            "edge_count": len(edge_data),
            "density": nx.density(G),
            "is_connected": nx.is_connected(G)
        }
    
    def _calculate_3d_layout(self, G: nx.Graph) -> Dict[str, Tuple[float, float, float]]:
        """Calculate 3D positions for nodes using force-directed layout"""
        # Use spring layout with 3 dimensions
        pos = nx.spring_layout(G, dim=3, iterations=50, seed=42)
        return pos
    
    def calculate_centrality_metrics(self) -> Dict[str, Dict[str, float]]:
        """Calculate various centrality metrics for the network"""
        if self.graph is None:
            raise ValueError("No graph created. Call create_network_from_interactions first.")
        
        return {
            "degree_centrality": nx.degree_centrality(self.graph),
            "betweenness_centrality": nx.betweenness_centrality(self.graph),
            "closeness_centrality": nx.closeness_centrality(self.graph),
            "eigenvector_centrality": nx.eigenvector_centrality(self.graph, max_iter=1000)
        }


class DimensionalityReduction:
    """Perform dimensionality reduction for 3D visualization"""
    
    def __init__(self):
        self.fitted_model = None
        self.method = None
    
    def reduce_to_3d(
        self,
        data: np.ndarray,
        method: str = "pca",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Reduce high-dimensional data to 3D
        
        Args:
            data: Input data matrix (samples x features)
            method: Reduction method ('pca', 'tsne', 'umap')
            **kwargs: Additional parameters for the reduction method
            
        Returns:
            Dictionary with 3D coordinates and metadata
        """
        if method.lower() == "pca":
            return self._pca_reduction(data, **kwargs)
        elif method.lower() == "tsne":
            return self._tsne_reduction(data, **kwargs)
        elif method.lower() == "umap":
            return self._umap_reduction(data, **kwargs)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'pca', 'tsne', or 'umap'")
    
    def _pca_reduction(self, data: np.ndarray, **kwargs) -> Dict[str, Any]:
        """Perform PCA reduction to 3D"""
        n_components = 3
        pca = PCA(n_components=n_components, **kwargs)
        
        # Fit and transform
        coords_3d = pca.fit_transform(data)
        
        self.fitted_model = pca
        self.method = "pca"
        
        return {
            "method": "pca",
            "coordinates": coords_3d.tolist(),
            "explained_variance": pca.explained_variance_ratio_.tolist(),
            "total_variance_explained": float(pca.explained_variance_ratio_.sum()),
            "n_samples": data.shape[0],
            "n_features": data.shape[1]
        }
    
    def _tsne_reduction(self, data: np.ndarray, **kwargs) -> Dict[str, Any]:
        """Perform t-SNE reduction to 3D"""
        n_components = 3
        perplexity = kwargs.pop('perplexity', min(30, data.shape[0] - 1))
        
        tsne = TSNE(
            n_components=n_components,
            perplexity=perplexity,
            random_state=42,
            **kwargs
        )
        
        # Fit and transform
        coords_3d = tsne.fit_transform(data)
        
        self.fitted_model = tsne
        self.method = "tsne"
        
        return {
            "method": "tsne",
            "coordinates": coords_3d.tolist(),
            "perplexity": perplexity,
            "kl_divergence": float(tsne.kl_divergence_),
            "n_samples": data.shape[0],
            "n_features": data.shape[1]
        }
    
    def _umap_reduction(self, data: np.ndarray, **kwargs) -> Dict[str, Any]:
        """Perform UMAP reduction to 3D"""
        try:
            import umap
        except ImportError:
            raise ImportError("UMAP not installed. Install with: pip install umap-learn")
        
        n_components = 3
        n_neighbors = kwargs.pop('n_neighbors', min(15, data.shape[0] - 1))
        
        reducer = umap.UMAP(
            n_components=n_components,
            n_neighbors=n_neighbors,
            random_state=42,
            **kwargs
        )
        
        # Fit and transform
        coords_3d = reducer.fit_transform(data)
        
        self.fitted_model = reducer
        self.method = "umap"
        
        return {
            "method": "umap",
            "coordinates": coords_3d.tolist(),
            "n_neighbors": n_neighbors,
            "n_samples": data.shape[0],
            "n_features": data.shape[1]
        }
    
    def add_metadata_coloring(
        self,
        reduction_result: Dict[str, Any],
        metadata: List[Any],
        metadata_name: str = "group"
    ) -> Dict[str, Any]:
        """
        Add metadata for color coding points
        
        Args:
            reduction_result: Result from reduce_to_3d
            metadata: List of metadata values (same length as samples)
            metadata_name: Name of the metadata field
            
        Returns:
            Updated result with metadata
        """
        if len(metadata) != len(reduction_result["coordinates"]):
            raise ValueError("Metadata length must match number of samples")
        
        # Add metadata to result
        reduction_result["metadata"] = {
            "name": metadata_name,
            "values": metadata
        }
        
        # If metadata is categorical, create color mapping
        unique_values = list(set(metadata))
        if len(unique_values) <= 20:  # Treat as categorical if <= 20 unique values
            color_map = {val: i for i, val in enumerate(unique_values)}
            reduction_result["metadata"]["color_indices"] = [
                color_map[val] for val in metadata
            ]
            reduction_result["metadata"]["unique_values"] = unique_values
        
        return reduction_result


# Utility functions for data preparation
def prepare_omics_data_for_visualization(
    data: pd.DataFrame,
    sample_metadata: Optional[pd.DataFrame] = None
) -> Tuple[np.ndarray, Optional[List[Any]]]:
    """
    Prepare omics data for dimensionality reduction
    
    Args:
        data: DataFrame with samples as rows and features as columns
        sample_metadata: Optional DataFrame with sample metadata
        
    Returns:
        Tuple of (data_matrix, metadata_values)
    """
    # Convert to numpy array
    data_matrix = data.values
    
    # Extract metadata if provided
    metadata_values = None
    if sample_metadata is not None and len(sample_metadata) > 0:
        # Use first column as default metadata
        metadata_values = sample_metadata.iloc[:, 0].tolist()
    
    return data_matrix, metadata_values
