"""
Integration Hub Module - API endpoints for external database integration
Provides REST API endpoints for accessing NCBI, UniProt, KEGG, PubMed, and STRING databases
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from backend_db.redis_cache import get_redis_client
from backend_db.integration import IntegrationHubService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize Integration Hub Service
redis_client = get_redis_client()
integration_hub = IntegrationHubService(redis_client)


# Request/Response Models
class GeneAnnotationRequest(BaseModel):
    gene_id: str = Field(..., description="Gene identifier")
    sources: Optional[List[str]] = Field(None, description="List of sources to query (ncbi, uniprot, kegg, pubmed, string)")


class BatchGeneRequest(BaseModel):
    gene_ids: List[str] = Field(..., description="List of gene identifiers", max_items=100)
    sources: Optional[List[str]] = Field(None, description="List of sources to query")


class PathwayQueryRequest(BaseModel):
    pathway_id: str = Field(..., description="KEGG pathway ID")


class ProteinQueryRequest(BaseModel):
    protein_id: str = Field(..., description="UniProt protein ID")


class PubMedSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    max_results: int = Field(10, description="Maximum number of results", ge=1, le=100)
    sort: str = Field("relevance", description="Sort order (relevance, pub_date, citation_count)")


class InteractionQueryRequest(BaseModel):
    protein_id: str = Field(..., description="Protein identifier")
    species: int = Field(9606, description="NCBI taxonomy ID (default: 9606 for human)")
    required_score: int = Field(400, description="Minimum interaction score (0-1000)", ge=0, le=1000)
    limit: int = Field(10, description="Maximum number of interactions", ge=1, le=100)


# API Endpoints

@router.get("/api/integration/gene/{gene_id}")
async def get_gene_annotation(
    gene_id: str,
    sources: Optional[str] = Query(None, description="Comma-separated list of sources")
):
    """
    Get comprehensive gene annotation from multiple databases
    
    Args:
        gene_id: Gene identifier (e.g., NCBI Gene ID, gene symbol)
        sources: Optional comma-separated list of sources (ncbi, uniprot, kegg, pubmed, string)
    
    Returns:
        Comprehensive gene annotation from all requested sources
    """
    try:
        source_list = sources.split(',') if sources else None
        annotation = integration_hub.get_gene_annotation(gene_id, source_list)
        return annotation
    except Exception as e:
        logger.error(f"Error fetching gene annotation for {gene_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/integration/batch-query")
async def batch_query_genes(request: BatchGeneRequest):
    """
    Query multiple genes in batch
    
    Args:
        request: Batch query request with gene IDs and optional sources
    
    Returns:
        Dictionary mapping gene IDs to their annotations
    """
    try:
        if len(request.gene_ids) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 genes per batch request")
        
        results = integration_hub.batch_annotate_genes(request.gene_ids)
        return {
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error in batch query: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/api/integration/pathway/{pathway_id}")
async def get_pathway_info(pathway_id: str):
    """
    Get KEGG pathway information
    
    Args:
        pathway_id: KEGG pathway ID (e.g., 'hsa00010')
    
    Returns:
        Pathway information including genes, compounds, and reactions
    """
    try:
        pathway_data = integration_hub.kegg.get_pathway_info(pathway_id)
        return pathway_data
    except Exception as e:
        logger.error(f"Error fetching pathway {pathway_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/integration/pathway/search")
async def search_pathways(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(10, description="Maximum results", ge=1, le=100)
):
    """
    Search for KEGG pathways
    
    Args:
        query: Search query
        max_results: Maximum number of results
    
    Returns:
        List of matching pathways
    """
    try:
        results = integration_hub.kegg.search_pathways(query)
        return {
            "count": len(results),
            "results": results[:max_results]
        }
    except Exception as e:
        logger.error(f"Error searching pathways: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/integration/protein/{protein_id}")
async def get_protein_info(protein_id: str):
    """
    Get UniProt protein information
    
    Args:
        protein_id: UniProt accession ID
    
    Returns:
        Detailed protein information
    """
    try:
        protein_data = integration_hub.uniprot.get_protein_info(protein_id)
        return protein_data
    except Exception as e:
        logger.error(f"Error fetching protein {protein_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/integration/protein/search")
async def search_proteins(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(10, description="Maximum results", ge=1, le=100)
):
    """
    Search for proteins in UniProt
    
    Args:
        query: Search query
        max_results: Maximum number of results
    
    Returns:
        List of matching protein IDs
    """
    try:
        results = integration_hub.uniprot.search_proteins(query, max_results)
        return {
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error searching proteins: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/integration/literature/search")
async def search_literature(request: PubMedSearchRequest):
    """
    Search PubMed for research papers
    
    Args:
        request: Search request with query and parameters
    
    Returns:
        List of PubMed IDs matching the query
    """
    try:
        pmids = integration_hub.pubmed.search_papers(
            request.query,
            request.max_results,
            request.sort
        )
        return {
            "count": len(pmids),
            "pmids": pmids
        }
    except Exception as e:
        logger.error(f"Error searching literature: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/integration/literature/{pmid}")
async def get_paper_info(pmid: str):
    """
    Get detailed information about a research paper
    
    Args:
        pmid: PubMed ID
    
    Returns:
        Paper information including title, abstract, authors, etc.
    """
    try:
        paper_data = integration_hub.pubmed.get_paper_info(pmid)
        return paper_data
    except Exception as e:
        logger.error(f"Error fetching paper {pmid}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/integration/literature/batch")
async def get_papers_batch(pmids: List[str]):
    """
    Get information for multiple papers
    
    Args:
        pmids: List of PubMed IDs (max 100)
    
    Returns:
        Dictionary mapping PMIDs to paper information
    """
    try:
        if len(pmids) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 papers per batch request")
        
        papers = integration_hub.pubmed.get_papers_batch(pmids)
        return {
            "count": len(papers),
            "papers": papers
        }
    except Exception as e:
        logger.error(f"Error fetching papers batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/integration/interactions")
async def get_protein_interactions(request: InteractionQueryRequest):
    """
    Get protein-protein interactions from STRING database
    
    Args:
        request: Interaction query request
    
    Returns:
        Protein interaction network data
    """
    try:
        interactions = integration_hub.string.get_protein_interactions(
            request.protein_id,
            request.species,
            request.required_score,
            request.limit
        )
        return interactions
    except Exception as e:
        logger.error(f"Error fetching interactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/integration/interactions/network")
async def get_interaction_network(
    protein_ids: List[str],
    species: int = Query(9606, description="NCBI taxonomy ID"),
    required_score: int = Query(400, description="Minimum interaction score", ge=0, le=1000)
):
    """
    Get interaction network for multiple proteins
    
    Args:
        protein_ids: List of protein identifiers (max 100)
        species: NCBI taxonomy ID
        required_score: Minimum interaction score
    
    Returns:
        Network data with nodes and edges
    """
    try:
        if len(protein_ids) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 proteins per request")
        
        network = integration_hub.string.get_interaction_partners(
            protein_ids,
            species,
            required_score
        )
        return network
    except Exception as e:
        logger.error(f"Error fetching interaction network: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/integration/enrichment")
async def get_functional_enrichment(
    protein_ids: List[str],
    species: int = Query(9606, description="NCBI taxonomy ID")
):
    """
    Get functional enrichment analysis for a set of proteins
    
    Args:
        protein_ids: List of protein identifiers (max 100)
        species: NCBI taxonomy ID
    
    Returns:
        Enrichment results by category (GO, KEGG, etc.)
    """
    try:
        if len(protein_ids) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 proteins per request")
        
        enrichment = integration_hub.string.get_enrichment(protein_ids, species)
        return enrichment
    except Exception as e:
        logger.error(f"Error fetching enrichment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/integration/status")
async def get_integration_status():
    """
    Get status of all integration adapters
    
    Returns:
        Status information for each adapter
    """
    return {
        "status": "operational",
        "adapters": {
            "ncbi": {
                "status": "active",
                "description": "NCBI Gene database adapter",
                "rate_limit": "3 req/sec (10 with API key)"
            },
            "uniprot": {
                "status": "active",
                "description": "UniProt protein database adapter",
                "rate_limit": "10 req/sec"
            },
            "kegg": {
                "status": "active",
                "description": "KEGG pathway database adapter",
                "rate_limit": "10 req/sec"
            },
            "pubmed": {
                "status": "active",
                "description": "PubMed literature database adapter",
                "rate_limit": "3 req/sec (10 with API key)"
            },
            "string": {
                "status": "active",
                "description": "STRING protein interaction database adapter",
                "rate_limit": "10 req/sec"
            }
        },
        "cache": {
            "enabled": True,
            "ttl": "7 days (30 days for PubMed)"
        }
    }
