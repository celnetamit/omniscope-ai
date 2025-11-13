# Literature Mining System - Quick Start Guide

## Overview

The AI-powered literature mining system provides comprehensive research paper analysis and context extraction capabilities for OmniScope AI. It integrates PubMed fetching, NLP analysis with BioBERT, paper summarization with T5, knowledge graph storage with Neo4j, paper ranking, notification system, and natural language query interface.

## Features Implemented

### 1. PubMed Fetcher (Task 10.1) ✅
- E-utilities API integration for paper search and retrieval
- Batch paper fetching for efficiency
- Redis caching with 30-day TTL
- Rate limiting (3 req/s without API key, 10 req/s with key)
- Citation and related paper retrieval
- Biomarker-specific paper search

### 2. NLP Pipeline with BioBERT (Task 10.2) ✅
- Entity extraction for genes, diseases, drugs, and pathways
- BioBERT-based named entity recognition
- Fallback rule-based extraction
- Confidence scoring for entities
- Support for custom entity types

### 3. Paper Summarization with T5 (Task 10.3) ✅
- Abstractive summarization using T5 model
- Quality scoring for summaries
- Fallback extractive summarization
- Batch summarization support
- Configurable summary length

### 4. Entity and Relationship Extraction (Task 10.4) ✅
- Named entity recognition from paper abstracts
- Relationship extraction between entities
- Relationship types: regulates, interacts_with, associated_with, causes, treats
- Evidence extraction from text
- Confidence scoring

### 5. Knowledge Graph with Neo4j (Task 10.5) ✅
- Entity and relationship storage in Neo4j
- Graph query interface
- Multi-hop relationship traversal
- Automatic graph building from papers
- Lazy initialization for optional Neo4j dependency

### 6. Paper Ranking System (Task 10.6) ✅
- Citation count ranking
- Semantic similarity using Sentence-BERT
- Recency scoring
- Combined relevance score
- Query-based ranking

### 7. Notification System (Task 10.7) ✅
- Topic subscription management
- New paper monitoring
- Email notification support
- Redis-based subscription storage
- Notification history tracking

### 8. Natural Language Query Interface (Task 10.8) ✅
- Question answering using BERT
- Query understanding
- Answer generation from paper corpus
- Confidence scoring
- Fallback keyword-based matching

### 9. API Endpoints (Task 10.9) ✅
- `/api/literature/search` - Search papers
- `/api/literature/paper/{pmid}` - Get paper details
- `/api/literature/biomarker/{biomarker}/papers` - Get biomarker papers
- `/api/literature/extract-entities` - Extract entities from text
- `/api/literature/paper/{pmid}/entities` - Extract paper entities
- `/api/literature/paper/{pmid}/relationships` - Extract relationships
- `/api/literature/summarize` - Summarize paper
- `/api/literature/knowledge-graph/build/{pmid}` - Build knowledge graph
- `/api/literature/knowledge-graph/query/{entity}` - Query knowledge graph
- `/api/literature/rank` - Rank papers by relevance
- `/api/literature/subscribe` - Subscribe to topics
- `/api/literature/query` - Natural language query

## Prerequisites

### Required Services
1. **Redis** - For caching and subscriptions
   ```bash
   docker run -d -p 6379:6379 redis:latest
   ```

2. **Neo4j** (Optional) - For knowledge graph
   ```bash
   docker run -d -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/password \
     neo4j:latest
   ```

### Environment Variables
```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# NCBI API Configuration
NCBI_EMAIL=your-email@example.com
NCBI_API_KEY=your-api-key  # Optional, for higher rate limits

# Neo4j Configuration (Optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

### Python Dependencies
The following packages are required (already in requirements.txt):
```
transformers==4.36.2
sentence-transformers==2.2.2
spacy==3.7.2
scispacy==0.5.3
neo4j==5.15.0
torch==2.1.2
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage Examples

### 1. Search for Papers
```bash
curl -X POST "http://localhost:8001/api/literature/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "BRCA1 breast cancer",
    "max_results": 10,
    "sort": "relevance"
  }'
```

### 2. Get Paper Details
```bash
curl "http://localhost:8001/api/literature/paper/12345678"
```

### 3. Search Papers for Biomarker
```bash
curl "http://localhost:8001/api/literature/biomarker/TP53/papers?max_results=10"
```

### 4. Extract Entities from Text
```bash
curl -X POST "http://localhost:8001/api/literature/extract-entities" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "BRCA1 mutations are associated with breast cancer risk.",
    "entity_types": ["gene", "disease"]
  }'
```

### 5. Extract Entities from Paper
```bash
curl "http://localhost:8001/api/literature/paper/12345678/entities"
```

### 6. Extract Relationships from Paper
```bash
curl "http://localhost:8001/api/literature/paper/12345678/relationships"
```

### 7. Summarize Paper
```bash
curl -X POST "http://localhost:8001/api/literature/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "pmid": "12345678",
    "max_length": 150
  }'
```

### 8. Build Knowledge Graph from Paper
```bash
curl -X POST "http://localhost:8001/api/literature/knowledge-graph/build/12345678"
```

### 9. Query Knowledge Graph
```bash
curl "http://localhost:8001/api/literature/knowledge-graph/query/BRCA1?max_depth=2"
```

### 10. Rank Papers by Relevance
```bash
curl -X POST "http://localhost:8001/api/literature/rank" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "BRCA1 therapeutic targets",
    "max_results": 10,
    "sort": "relevance"
  }'
```

### 11. Subscribe to Topics
```bash
curl -X POST "http://localhost:8001/api/literature/subscribe" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "topics": ["BRCA1", "breast cancer", "immunotherapy"],
    "email": "user@example.com"
  }'
```

### 12. Natural Language Query
```bash
curl -X POST "http://localhost:8001/api/literature/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the role of BRCA1 in DNA repair?",
    "max_results": 5
  }'
```

## Integration with OmniScope AI

### Using with Biomarker Analysis
When a biomarker is identified through The Insight Engine, automatically fetch relevant literature:

```python
# In your analysis code
biomarker = "TP53"

# Get papers for biomarker
response = requests.get(f"http://localhost:8001/api/literature/biomarker/{biomarker}/papers")
papers = response.json()['papers']

# Extract entities and relationships
for paper in papers[:5]:
    pmid = paper['pmid']
    
    # Get relationships
    rel_response = requests.get(f"http://localhost:8001/api/literature/paper/{pmid}/relationships")
    relationships = rel_response.json()['relationships']
    
    # Build knowledge graph
    requests.post(f"http://localhost:8001/api/literature/knowledge-graph/build/{pmid}")
```

### Automated Literature Context
Add literature context to analysis results:

```python
def enrich_with_literature(gene_id: str):
    # Search for papers
    search_response = requests.post(
        "http://localhost:8001/api/literature/search",
        json={"query": gene_id, "max_results": 5}
    )
    papers = search_response.json()['papers']
    
    # Summarize papers
    summaries = []
    for paper in papers:
        summary_response = requests.post(
            "http://localhost:8001/api/literature/summarize",
            json={"pmid": paper['pmid'], "max_length": 100}
        )
        summaries.append(summary_response.json())
    
    return {
        'gene_id': gene_id,
        'papers': papers,
        'summaries': summaries
    }
```

## Performance Considerations

### Caching
- Paper data cached for 30 days in Redis
- Search results cached to reduce API calls
- Entity extraction results can be cached

### Rate Limiting
- NCBI E-utilities: 3 requests/second (10 with API key)
- Implement exponential backoff for retries
- Use batch operations when possible

### Model Loading
- Models are lazy-loaded on first use
- BioBERT, T5, and Sentence-BERT loaded only when needed
- Consider pre-loading models for production

### Scalability
- Redis for distributed caching
- Neo4j for scalable graph storage
- Async processing for batch operations

## Troubleshooting

### Issue: Models not loading
**Solution**: Ensure transformers and torch are installed:
```bash
pip install transformers torch sentence-transformers
```

### Issue: Neo4j connection failed
**Solution**: Neo4j is optional. The system will work without it, but knowledge graph features will be disabled. Check Neo4j is running:
```bash
docker ps | grep neo4j
```

### Issue: Rate limit exceeded
**Solution**: 
1. Get NCBI API key for higher limits
2. Implement request queuing
3. Increase cache TTL

### Issue: Out of memory
**Solution**:
1. Use smaller models (t5-small instead of t5-base)
2. Process papers in smaller batches
3. Increase system memory

## Architecture

```
┌──────────────────┐
│  PubMed API      │
└────────┬─────────┘
         │
┌────────┴─────────┐
│  NLP Pipeline    │
│  (BioBERT, T5)   │
└────────┬─────────┘
         │
┌────────┴─────────┐
│  Knowledge Graph │
│  (Neo4j)         │
└──────────────────┘
```

## Next Steps

1. **Enhance NLP Models**: Fine-tune BioBERT on domain-specific data
2. **Improve Ranking**: Add more ranking signals (journal impact factor, author reputation)
3. **Real-time Notifications**: Implement email/webhook notifications
4. **Advanced Queries**: Support complex graph queries
5. **Visualization**: Add knowledge graph visualization
6. **Export**: Support exporting literature reviews

## API Documentation

Full API documentation available at:
```
http://localhost:8001/docs#/AI-Powered%20Literature%20Mining
```

## Support

For issues or questions:
1. Check logs: `tail -f dev.log`
2. Verify services: `docker ps`
3. Test endpoints: Use Swagger UI at `/docs`

## References

- PubMed E-utilities: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- BioBERT: https://github.com/dmis-lab/biobert
- T5: https://huggingface.co/docs/transformers/model_doc/t5
- Neo4j: https://neo4j.com/docs/
- Sentence-BERT: https://www.sbert.net/
