from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import random
import re

# Create the router
router = APIRouter()

# Define Pydantic models for request/response
class Biomarker(BaseModel):
    gene_id: str
    gene_name: str
    type: str  # "gene", "protein", or "metabolite"
    importance_score: float
    p_value: float
    external_links: Dict[str, str]

class BiomarkerList(BaseModel):
    model_id: str
    biomarkers: List[Biomarker]

class Explanation(BaseModel):
    gene_id: str
    gene_name: str
    explanation: str
    socratic_question: str
    related_concepts: List[str]
    learn_more_link: str

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    response: str
    data: Optional[List[Dict[str, Any]]] = None

# Mock data generation
def generate_mock_biomarkers():
    """Generate a realistic-looking mock dataset of biomarkers.
    
    Returns:
        List[Biomarker]: A list of biomarker objects with realistic data.
    """
    biomarker_types = ["gene", "protein", "metabolite"]
    
    # Common biomarkers with realistic data
    biomarkers_data = [
        {"gene_id": "ENSG00000141510", "gene_name": "TP53", "type": "gene"},
        {"gene_id": "ENSG00000146648", "gene_name": "EGFR", "type": "gene"},
        {"gene_id": "ENSG00000136997", "gene_name": "MYC", "type": "gene"},
        {"gene_id": "ENSG00000157764", "gene_name": "BRAF", "type": "gene"},
        {"gene_id": "ENSG00000198786", "gene_name": "KRAS", "type": "gene"},
        {"gene_id": "ENSG00000133703", "gene_name": "ALK", "type": "gene"},
        {"gene_id": "ENSG00000141736", "gene_name": "BRCA1", "type": "gene"},
        {"gene_id": "ENSG00000139618", "gene_name": "BRCA2", "type": "gene"},
        {"gene_id": "ENSG00000185950", "gene_name": "PIK3CA", "type": "gene"},
        {"gene_id": "ENSG00000142208", "gene_name": "PTEN", "type": "gene"},
        {"gene_id": "P04637", "gene_name": "p53", "type": "protein"},
        {"gene_id": "P00533", "gene_name": "EGFR", "type": "protein"},
        {"gene_id": "P01106", "gene_name": "MYC", "type": "protein"},
        {"gene_id": "HMDB0000124", "gene_name": "Glucose", "type": "metabolite"},
        {"gene_id": "HMDB0000199", "gene_name": "Lactate", "type": "metabolite"},
    ]
    
    biomarkers = []
    for data in biomarkers_data:
        # Generate random importance score and p-value with realistic distributions
        # Top biomarkers should have higher importance scores and lower p-values
        if data["gene_name"] in ["TP53", "EGFR", "MYC", "p53"]:
            importance_score = round(random.uniform(0.9, 0.99), 2)
            p_value = round(random.uniform(0.00001, 0.001), 5)
        elif data["gene_name"] in ["BRAF", "KRAS", "ALK", "BRCA1", "BRCA2"]:
            importance_score = round(random.uniform(0.8, 0.95), 2)
            p_value = round(random.uniform(0.001, 0.01), 5)
        else:
            importance_score = round(random.uniform(0.7, 0.9), 2)
            p_value = round(random.uniform(0.01, 0.05), 5)
        
        # Generate external links based on biomarker type
        if data["type"] == "gene":
            # Extract numeric part from ENSG ID for NCBI link
            ncbi_id = data["gene_id"].replace("ENSG00000", "")
            ncbi_link = f"https://www.ncbi.nlm.nih.gov/gene/{ncbi_id}"
            ensembl_link = f"https://www.ensembl.org/Homo_sapiens/Gene/Summary?g={data['gene_id']}"
            external_links = {"NCBI": ncbi_link, "Ensembl": ensembl_link}
        elif data["type"] == "protein":
            uniprot_link = f"https://www.uniprot.org/uniprot/{data['gene_id']}"
            external_links = {"UniProt": uniprot_link}
        else:  # metabolite
            hmdb_link = f"https://www.hmdb.ca/metabolites/{data['gene_id']}"
            external_links = {"HMDB": hmdb_link}
        
        biomarkers.append(Biomarker(
            gene_id=data["gene_id"],
            gene_name=data["gene_name"],
            type=data["type"],
            importance_score=importance_score,
            p_value=p_value,
            external_links=external_links
        ))
    
    # Sort by importance score (descending)
    biomarkers.sort(key=lambda x: x.importance_score, reverse=True)
    return biomarkers

# In-memory storage for mock results
# In a real application, this would be replaced with a database
mock_results = {
    "model_001": generate_mock_biomarkers(),
    "model_002": generate_mock_biomarkers()  # Different set for second model
}

# API Routes

@router.get("/{model_id}/biomarkers", response_model=BiomarkerList)
async def get_biomarkers(model_id: str):
    """Retrieve the full list of identified biomarkers for a given completed model.
    
    Args:
        model_id: The ID of the model to retrieve biomarkers for.
        
    Returns:
        BiomarkerList: A list of biomarkers for the specified model.
    """
    if model_id not in mock_results:
        # Create a new model if it doesn't exist
        mock_results[model_id] = generate_mock_biomarkers()
    
    return BiomarkerList(
        model_id=model_id,
        biomarkers=mock_results[model_id]
    )

@router.get("/{model_id}/biomarkers/{gene_id}/explain", response_model=Explanation)
async def explain_biomarker(model_id: str, gene_id: str):
    """Provide a detailed, educational explanation for a specific biomarker.
    
    This endpoint implements the "Socratic Tutor" feature, providing not just
    information about the biomarker but also thought-provoking questions to
    encourage deeper understanding.
    
    Args:
        model_id: The ID of the model.
        gene_id: The ID of the gene/biomarker to explain.
        
    Returns:
        Explanation: Detailed information about the biomarker.
    """
    if model_id not in mock_results:
        # Create a new model if it doesn't exist
        mock_results[model_id] = generate_mock_biomarkers()
    
    # Find the biomarker
    biomarker = None
    for b in mock_results[model_id]:
        if b.gene_id == gene_id or b.gene_name == gene_id:
            biomarker = b
            break
    
    if not biomarker:
        # Return a default explanation if biomarker not found
        return Explanation(
            gene_id=gene_id,
            gene_name="Unknown",
            explanation="This biomarker was not found in the analysis results.",
            socratic_question="Why might some biomarkers be excluded from analysis?",
            related_concepts=["Data Quality", "Statistical Significance", "Filtering"],
            learn_more_link="https://example.com/learn/biomarker-analysis"
        )
    
    # Generate explanation based on biomarker type
    if biomarker.type == "gene":
        importance_percentage = int(biomarker.importance_score * 100)
        explanation = f"{biomarker.gene_name} is a top biomarker because its expression pattern consistently correlates with the sample classifications across {importance_percentage}% of the model's decision paths. It acts as a strong signal for the model's classification."
        
        # Generate socratic question based on gene function
        if biomarker.gene_name in ["TP53", "BRCA1", "BRCA2"]:
            socratic_question = f"This gene is a well-known tumor suppressor. Do you think its altered expression in your data is a cause or an effect of the disease state?"
            related_concepts = ["Tumor Suppression", "DNA Repair", "Cell Cycle Arrest"]
        elif biomarker.gene_name in ["EGFR", "ALK", "KRAS", "BRAF"]:
            socratic_question = f"This gene is often involved in cell signaling pathways. How might its dysregulation contribute to disease progression?"
            related_concepts = ["Cell Signaling", "Oncogenes", "Targeted Therapy"]
        else:
            socratic_question = f"This gene shows significant importance in the model. What biological processes might it be regulating in this context?"
            related_concepts = ["Gene Regulation", "Cellular Processes", "Molecular Pathways"]
        
        learn_more_link = f"https://example.com/learn/{biomarker.gene_name.lower()}-pathway"
    
    elif biomarker.type == "protein":
        importance_percentage = int(biomarker.importance_score * 100)
        explanation = f"The {biomarker.gene_name} protein is a significant biomarker as its abundance levels distinguish between sample groups in {importance_percentage}% of classification decisions. This suggests it may play a key role in the underlying biology."
        
        # Generate socratic question based on protein function
        if biomarker.gene_name == "p53":
            socratic_question = "The p53 protein is often called 'the guardian of the genome'. What cellular processes does it regulate to maintain genomic stability?"
            related_concepts = ["Genomic Stability", "Apoptosis", "DNA Repair"]
        elif biomarker.gene_name == "EGFR":
            socratic_question = "EGFR is a receptor tyrosine kinase. How might changes in its activity affect downstream signaling pathways?"
            related_concepts = ["Receptor Tyrosine Kinases", "Signal Transduction", "Cell Proliferation"]
        else:
            socratic_question = f"This protein shows significant importance in the model. What might be the functional consequences of its altered abundance?"
            related_concepts = ["Protein Function", "Cellular Processes", "Molecular Interactions"]
        
        learn_more_link = f"https://example.com/learn/{biomarker.gene_name.lower()}-function"
    
    else:  # metabolite
        importance_percentage = int(biomarker.importance_score * 100)
        explanation = f"The metabolite {biomarker.gene_name} is a key biomarker as its concentration differs significantly between sample groups, influencing {importance_percentage}% of the model's classification decisions. This suggests a metabolic shift in the condition being studied."
        
        # Generate socratic question based on metabolite function
        if biomarker.gene_name == "Glucose":
            socratic_question = "Glucose is a primary energy source. How might changes in glucose metabolism reflect the metabolic state of the cells in your samples?"
            related_concepts = ["Glycolysis", "Energy Metabolism", "Warburg Effect"]
        elif biomarker.gene_name == "Lactate":
            socratic_question = "Lactate production is often associated with anaerobic metabolism. What might elevated lactate levels suggest about the cellular environment?"
            related_concepts = ["Anaerobic Metabolism", "Lactic Acid Fermentation", "Cellular Hypoxia"]
        else:
            socratic_question = f"This metabolite shows significant importance in the model. What metabolic pathways might it be involved in?"
            related_concepts = ["Metabolic Pathways", "Biochemical Reactions", "Cellular Metabolism"]
        
        learn_more_link = f"https://example.com/learn/{biomarker.gene_name.lower()}-metabolism"
    
    return Explanation(
        gene_id=biomarker.gene_id,
        gene_name=biomarker.gene_name,
        explanation=explanation,
        socratic_question=socratic_question,
        related_concepts=related_concepts,
        learn_more_link=learn_more_link
    )

@router.post("/{model_id}/query", response_model=QueryResponse)
async def query_results(model_id: str, request: QueryRequest):
    """Accept a natural language question and return an answer based on the model's results.
    
    This endpoint implements a simple, rule-based query engine using keyword matching.
    It can handle queries about top biomarkers, specific genes, or types of biomarkers.
    
    Args:
        model_id: The ID of the model to query.
        request: The query request containing the natural language question.
        
    Returns:
        QueryResponse: The response to the query, including relevant data.
    """
    if model_id not in mock_results:
        # Create a new model if it doesn't exist
        mock_results[model_id] = generate_mock_biomarkers()
    
    query = request.query.lower()
    biomarkers = mock_results[model_id]
    
    # Rule 1: Check for "top" or number in query
    top_match = re.search(r'top (\d+)', query)
    if top_match or "top" in query:
        n = 5  # Default number
        if top_match:
            n = int(top_match.group(1))
            n = min(n, len(biomarkers))  # Don't exceed available biomarkers
        
        top_biomarkers = biomarkers[:n]
        data = [{"gene_name": b.gene_name, "importance_score": b.importance_score} for b in top_biomarkers]
        
        gene_names = ", ".join([b.gene_name for b in top_biomarkers])
        response = f"The top {n} biomarkers by importance score are {gene_names}. I have highlighted them in the results table for you."
        
        return QueryResponse(
            query=request.query,
            response=response,
            data=data
        )
    
    # Rule 2: Check for specific gene name in query
    for biomarker in biomarkers:
        if biomarker.gene_name.lower() in query:
            data = [{
                "gene_id": biomarker.gene_id,
                "gene_name": biomarker.gene_name,
                "type": biomarker.type,
                "importance_score": biomarker.importance_score,
                "p_value": biomarker.p_value
            }]
            
            response = f"Here are the details for {biomarker.gene_name}: It's a {biomarker.type} with an importance score of {biomarker.importance_score} and a p-value of {biomarker.p_value}."
            
            return QueryResponse(
                query=request.query,
                response=response,
                data=data
            )
    
    # Rule 3: Check for biomarker type in query
    for biomarker_type in ["gene", "protein", "metabolite"]:
        if biomarker_type in query:
            filtered_biomarkers = [b for b in biomarkers if b.type == biomarker_type]
            data = [{"gene_name": b.gene_name, "importance_score": b.importance_score} for b in filtered_biomarkers]
            
            response = f"I found {len(filtered_biomarkers)} {biomarker_type}s in the results. Here they are sorted by importance."
            
            return QueryResponse(
                query=request.query,
                response=response,
                data=data
            )
    
    # Rule 4: Check for "important" or "significant" in query
    if "important" in query or "significant" in query:
        # Define significant as importance score > 0.8 and p-value < 0.01
        significant_biomarkers = [b for b in biomarkers if b.importance_score > 0.8 and b.p_value < 0.01]
        data = [{"gene_name": b.gene_name, "importance_score": b.importance_score, "p_value": b.p_value} for b in significant_biomarkers]
        
        response = f"I found {len(significant_biomarkers)} biomarkers that are both highly important (score > 0.8) and statistically significant (p-value < 0.01)."
        
        return QueryResponse(
            query=request.query,
            response=response,
            data=data
        )
    
    # Default Rule: Fallback response
    top_biomarkers = biomarkers[:3]
    data = [{"gene_name": b.gene_name, "importance_score": b.importance_score} for b in top_biomarkers]
    
    response = "I'm not sure how to answer that, but you can start by exploring the top biomarkers in the list."
    
    return QueryResponse(
        query=request.query,
        response=response,
        data=data
    )