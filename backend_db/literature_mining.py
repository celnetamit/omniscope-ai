"""
Literature Mining Service - AI-powered research paper analysis and context extraction
Provides PubMed fetching, NLP analysis, summarization, and knowledge graph capabilities
"""

import requests
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
import json
import logging
import redis
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends

logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models
# ============================================================================

class PaperSearchRequest(BaseModel):
    """Request model for paper search"""
    query: str
    max_results: int = 10
    sort: str = "relevance"  # relevance, pub_date, citation_count


class PaperSummarizeRequest(BaseModel):
    """Request model for paper summarization"""
    pmid: str
    max_length: int = 150


class EntityExtractionRequest(BaseModel):
    """Request model for entity extraction"""
    text: str
    entity_types: Optional[List[str]] = None  # gene, disease, drug, pathway


class RelationshipExtractionRequest(BaseModel):
    """Request model for relationship extraction"""
    pmid: str


class NaturalLanguageQueryRequest(BaseModel):
    """Request model for natural language query"""
    query: str
    max_results: int = 5


class TopicSubscriptionRequest(BaseModel):
    """Request model for topic subscription"""
    user_id: str
    topics: List[str]
    email: str


class Paper(BaseModel):
    """Paper data model"""
    pmid: str
    title: str
    abstract: str
    authors: List[str]
    journal: str
    year: int
    citations: int = 0
    summary: Optional[str] = None
    entities: Optional[List[Dict[str, Any]]] = None
    source: str = "PubMed"
    retrieved_at: str


class Entity(BaseModel):
    """Entity data model"""
    text: str
    type: str  # gene, disease, drug, pathway
    confidence: float
    start: int
    end: int


class Relationship(BaseModel):
    """Relationship data model"""
    source: Entity
    target: Entity
    type: str  # regulates, interacts_with, associated_with
    confidence: float
    evidence: str


# ============================================================================
# Rate Limiter (reuse from integration.py)
# ============================================================================

class RateLimiter:
    """Token bucket rate limiter for API calls"""
    
    def __init__(self, redis_client: redis.Redis, key_prefix: str, max_requests: int, time_window: int):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.max_requests = max_requests
        self.time_window = time_window
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed under rate limit"""
        key = f"{self.key_prefix}:{identifier}"
        current = self.redis.get(key)
        
        if current is None:
            self.redis.setex(key, self.time_window, 1)
            return True
        
        current_count = int(current)
        if current_count < self.max_requests:
            self.redis.incr(key)
            return True
        
        return False
    
    def wait_if_needed(self, identifier: str, max_wait: int = 60):
        """Wait if rate limit is exceeded"""
        attempts = 0
        while not self.is_allowed(identifier) and attempts < max_wait:
            time.sleep(1)
            attempts += 1
        
        if attempts >= max_wait:
            raise Exception(f"Rate limit exceeded for {identifier}")


class RetryHandler:
    """Exponential backoff retry handler"""
    
    @staticmethod
    def retry_with_backoff(func, max_retries: int = 3, initial_delay: float = 1.0):
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
        
        raise last_exception


# ============================================================================
# PubMed Fetcher Service
# ============================================================================

class PubMedFetcher:
    """
    PubMed E-utilities API client for fetching research papers
    Implements caching, rate limiting, and batch retrieval
    """
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, redis_client: redis.Redis, email: str = "omniscope@example.com", 
                 api_key: Optional[str] = None):
        """
        Initialize PubMed fetcher
        
        Args:
            redis_client: Redis client for caching
            email: Email for NCBI API (required by NCBI)
            api_key: Optional API key for higher rate limits
        """
        self.redis = redis_client
        self.email = email
        self.api_key = api_key
        
        # NCBI allows 3 requests/second without API key, 10/second with key
        max_requests = 10 if api_key else 3
        self.rate_limiter = RateLimiter(redis_client, "literature_pubmed_rate_limit", max_requests, 1)
        
        self.cache_ttl = 30 * 24 * 60 * 60  # 30 days in seconds
    
    def _get_cache_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key"""
        return f"literature:pubmed:{prefix}:{identifier}"
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache"""
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    def _set_to_cache(self, key: str, data: Dict):
        """Set data to cache"""
        self.redis.setex(key, self.cache_ttl, json.dumps(data))
    
    def _make_request(self, endpoint: str, params: Dict) -> requests.Response:
        """Make API request with rate limiting and retry"""
        params['email'] = self.email
        if self.api_key:
            params['api_key'] = self.api_key
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        def request_func():
            self.rate_limiter.wait_if_needed("pubmed")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response
        
        return RetryHandler.retry_with_backoff(request_func)
    
    def search_papers(self, query: str, max_results: int = 10, sort: str = 'relevance') -> List[str]:
        """
        Search for papers using E-search
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            sort: Sort order ('relevance', 'pub_date', 'citation_count')
            
        Returns:
            List of PubMed IDs (PMIDs)
        """
        # Check cache for search results
        cache_key = self._get_cache_key("search", f"{query}_{max_results}_{sort}")
        cached_results = self._get_from_cache(cache_key)
        if cached_results:
            logger.info(f"Cache hit for search query: {query}")
            return cached_results.get('pmids', [])
        
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json',
            'sort': sort
        }
        
        response = self._make_request('esearch.fcgi', params)
        data = response.json()
        
        pmids = data.get('esearchresult', {}).get('idlist', [])
        
        # Cache search results
        self._set_to_cache(cache_key, {'pmids': pmids, 'query': query})
        
        return pmids
    
    def get_paper_info(self, pmid: str) -> Dict[str, Any]:
        """
        Get detailed paper information
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Dictionary containing paper information
        """
        # Check cache first
        cache_key = self._get_cache_key("paper", pmid)
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"Cache hit for paper {pmid}")
            return cached_data
        
        # Fetch from API
        params = {
            'db': 'pubmed',
            'id': pmid,
            'retmode': 'xml'
        }
        
        response = self._make_request('efetch.fcgi', params)
        
        # Parse XML response
        root = ET.fromstring(response.content)
        paper_data = self._parse_paper_xml(root, pmid)
        
        # Add metadata
        paper_data['source'] = 'PubMed'
        paper_data['retrieved_at'] = datetime.utcnow().isoformat()
        
        # Cache the result
        self._set_to_cache(cache_key, paper_data)
        
        return paper_data
    
    def _parse_paper_xml(self, root: ET.Element, pmid: str) -> Dict[str, Any]:
        """Parse PubMed XML response"""
        paper_data = {
            'pmid': pmid,
            'title': '',
            'abstract': '',
            'authors': [],
            'journal': '',
            'year': 0,
            'volume': '',
            'issue': '',
            'pages': '',
            'doi': '',
            'keywords': [],
            'mesh_terms': [],
            'citations': 0
        }
        
        # Find the PubmedArticle element
        article = root.find('.//PubmedArticle')
        if article is None:
            return paper_data
        
        # Extract title
        title_elem = article.find('.//ArticleTitle')
        if title_elem is not None and title_elem.text:
            paper_data['title'] = title_elem.text
        
        # Extract abstract
        abstract_elem = article.find('.//AbstractText')
        if abstract_elem is not None and abstract_elem.text:
            paper_data['abstract'] = abstract_elem.text
        
        # Extract authors
        author_list = article.find('.//AuthorList')
        if author_list is not None:
            for author in author_list.findall('.//Author'):
                last_name = author.find('LastName')
                fore_name = author.find('ForeName')
                if last_name is not None and fore_name is not None:
                    paper_data['authors'].append(f"{fore_name.text} {last_name.text}")
        
        # Extract journal
        journal_elem = article.find('.//Journal/Title')
        if journal_elem is not None and journal_elem.text:
            paper_data['journal'] = journal_elem.text
        
        # Extract publication year
        year_elem = article.find('.//PubDate/Year')
        if year_elem is not None and year_elem.text:
            try:
                paper_data['year'] = int(year_elem.text)
            except ValueError:
                pass
        
        # Extract volume and issue
        volume_elem = article.find('.//Volume')
        if volume_elem is not None and volume_elem.text:
            paper_data['volume'] = volume_elem.text
        
        issue_elem = article.find('.//Issue')
        if issue_elem is not None and issue_elem.text:
            paper_data['issue'] = issue_elem.text
        
        # Extract pages
        pages_elem = article.find('.//MedlinePgn')
        if pages_elem is not None and pages_elem.text:
            paper_data['pages'] = pages_elem.text
        
        # Extract DOI
        doi_elem = article.find('.//ArticleId[@IdType="doi"]')
        if doi_elem is not None and doi_elem.text:
            paper_data['doi'] = doi_elem.text
        
        # Extract keywords
        keyword_list = article.find('.//KeywordList')
        if keyword_list is not None:
            for keyword in keyword_list.findall('.//Keyword'):
                if keyword.text:
                    paper_data['keywords'].append(keyword.text)
        
        # Extract MeSH terms
        mesh_list = article.find('.//MeshHeadingList')
        if mesh_list is not None:
            for mesh in mesh_list.findall('.//MeshHeading/DescriptorName'):
                if mesh.text:
                    paper_data['mesh_terms'].append(mesh.text)
        
        return paper_data
    
    def get_papers_batch(self, pmids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get information for multiple papers efficiently
        
        Args:
            pmids: List of PubMed IDs
            
        Returns:
            Dictionary mapping PMIDs to paper information
        """
        results = {}
        uncached_ids = []
        
        # Check cache for each paper
        for pmid in pmids:
            cache_key = self._get_cache_key("paper", pmid)
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                results[pmid] = cached_data
            else:
                uncached_ids.append(pmid)
        
        # Fetch uncached papers in batch
        if uncached_ids:
            # Split into chunks of 200 (NCBI limit)
            chunk_size = 200
            for i in range(0, len(uncached_ids), chunk_size):
                chunk = uncached_ids[i:i + chunk_size]
                
                params = {
                    'db': 'pubmed',
                    'id': ','.join(chunk),
                    'retmode': 'xml'
                }
                
                response = self._make_request('efetch.fcgi', params)
                root = ET.fromstring(response.content)
                
                # Parse each paper
                for article in root.findall('.//PubmedArticle'):
                    pmid_elem = article.find('.//PMID')
                    if pmid_elem is not None and pmid_elem.text:
                        pmid = pmid_elem.text
                        paper_data = self._parse_paper_xml(ET.ElementTree(article).getroot(), pmid)
                        paper_data['source'] = 'PubMed'
                        paper_data['retrieved_at'] = datetime.utcnow().isoformat()
                        
                        # Cache and add to results
                        cache_key = self._get_cache_key("paper", pmid)
                        self._set_to_cache(cache_key, paper_data)
                        results[pmid] = paper_data
        
        return results
    
    def get_citations(self, pmid: str) -> List[str]:
        """
        Get papers that cite this paper
        
        Args:
            pmid: PubMed ID
            
        Returns:
            List of citing paper PMIDs
        """
        params = {
            'dbfrom': 'pubmed',
            'db': 'pubmed',
            'id': pmid,
            'linkname': 'pubmed_pubmed_citedin',
            'retmode': 'json'
        }
        
        response = self._make_request('elink.fcgi', params)
        data = response.json()
        
        citing_ids = []
        linksets = data.get('linksets', [])
        for linkset in linksets:
            for linksetdb in linkset.get('linksetdbs', []):
                citing_ids.extend(linksetdb.get('links', []))
        
        return citing_ids
    
    def get_related_papers(self, pmid: str, max_results: int = 10) -> List[str]:
        """
        Get related papers
        
        Args:
            pmid: PubMed ID
            max_results: Maximum number of related papers
            
        Returns:
            List of related paper PMIDs
        """
        params = {
            'dbfrom': 'pubmed',
            'db': 'pubmed',
            'id': pmid,
            'linkname': 'pubmed_pubmed',
            'retmode': 'json'
        }
        
        response = self._make_request('elink.fcgi', params)
        data = response.json()
        
        related_ids = []
        linksets = data.get('linksets', [])
        for linkset in linksets:
            for linksetdb in linkset.get('linksetdbs', []):
                related_ids.extend(linksetdb.get('links', []))
        
        return related_ids[:max_results]
    
    def search_by_biomarker(self, biomarker: str, max_results: int = 10) -> List[str]:
        """
        Search for papers related to a specific biomarker
        
        Args:
            biomarker: Biomarker name (gene, protein, etc.)
            max_results: Maximum number of results
            
        Returns:
            List of PubMed IDs
        """
        # Construct query for biomarker
        query = f"{biomarker}[Title/Abstract] AND (biomarker OR marker OR gene OR protein)"
        return self.search_papers(query, max_results, sort='relevance')


# ============================================================================
# NLP Pipeline with BioBERT
# ============================================================================

class NLPPipeline:
    """
    NLP pipeline using BioBERT for biomedical text understanding
    Implements entity extraction and relationship extraction
    """
    
    def __init__(self, model_name: str = "dmis-lab/biobert-v1.1"):
        """
        Initialize NLP pipeline
        
        Args:
            model_name: HuggingFace model name for BioBERT
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.ner_pipeline = None
        self._initialized = False
    
    def _lazy_init(self):
        """Lazy initialization of models to avoid loading at import time"""
        if self._initialized:
            return
        
        try:
            from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
            
            logger.info(f"Loading BioBERT model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForTokenClassification.from_pretrained(self.model_name)
            
            # Create NER pipeline
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy="simple"
            )
            
            self._initialized = True
            logger.info("BioBERT model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load BioBERT model: {e}")
            # Fallback to rule-based extraction
            self._initialized = True
    
    def extract_entities(self, text: str, entity_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Extract named entities from text
        
        Args:
            text: Input text
            entity_types: List of entity types to extract (gene, disease, drug, pathway)
            
        Returns:
            List of entity dictionaries
        """
        self._lazy_init()
        
        entities = []
        
        # Try using BioBERT NER pipeline
        if self.ner_pipeline is not None:
            try:
                ner_results = self.ner_pipeline(text)
                
                for result in ner_results:
                    entity_type = self._map_entity_type(result.get('entity_group', 'UNKNOWN'))
                    
                    # Filter by requested entity types
                    if entity_types is None or entity_type in entity_types:
                        entities.append({
                            'text': result.get('word', ''),
                            'type': entity_type,
                            'confidence': result.get('score', 0.0),
                            'start': result.get('start', 0),
                            'end': result.get('end', 0)
                        })
            except Exception as e:
                logger.warning(f"BioBERT NER failed, falling back to rule-based: {e}")
                entities = self._rule_based_extraction(text, entity_types)
        else:
            # Fallback to rule-based extraction
            entities = self._rule_based_extraction(text, entity_types)
        
        return entities
    
    def _map_entity_type(self, biobert_type: str) -> str:
        """Map BioBERT entity types to our standard types"""
        type_mapping = {
            'GENE': 'gene',
            'PROTEIN': 'gene',
            'DISEASE': 'disease',
            'CHEMICAL': 'drug',
            'DRUG': 'drug',
            'PATHWAY': 'pathway',
            'CELL_LINE': 'gene',
            'CELL_TYPE': 'gene',
            'SPECIES': 'gene'
        }
        return type_mapping.get(biobert_type.upper(), 'gene')
    
    def _rule_based_extraction(self, text: str, entity_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Fallback rule-based entity extraction using regex patterns
        
        Args:
            text: Input text
            entity_types: List of entity types to extract
            
        Returns:
            List of entity dictionaries
        """
        import re
        
        entities = []
        
        # Gene patterns (uppercase, numbers, hyphens)
        if entity_types is None or 'gene' in entity_types:
            gene_pattern = r'\b[A-Z][A-Z0-9-]{2,10}\b'
            for match in re.finditer(gene_pattern, text):
                entities.append({
                    'text': match.group(),
                    'type': 'gene',
                    'confidence': 0.6,
                    'start': match.start(),
                    'end': match.end()
                })
        
        # Disease patterns (common disease keywords)
        if entity_types is None or 'disease' in entity_types:
            disease_keywords = ['cancer', 'tumor', 'carcinoma', 'disease', 'syndrome', 'disorder', 'diabetes', 'alzheimer']
            for keyword in disease_keywords:
                pattern = rf'\b\w*{keyword}\w*\b'
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    entities.append({
                        'text': match.group(),
                        'type': 'disease',
                        'confidence': 0.5,
                        'start': match.start(),
                        'end': match.end()
                    })
        
        # Drug patterns (common drug suffixes)
        if entity_types is None or 'drug' in entity_types:
            drug_suffixes = ['mab', 'nib', 'tinib', 'ciclib', 'pril', 'olol', 'statin']
            for suffix in drug_suffixes:
                pattern = rf'\b\w+{suffix}\b'
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    entities.append({
                        'text': match.group(),
                        'type': 'drug',
                        'confidence': 0.7,
                        'start': match.start(),
                        'end': match.end()
                    })
        
        return entities
    
    def extract_relationships(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract relationships between entities
        
        Args:
            text: Input text
            entities: List of extracted entities
            
        Returns:
            List of relationship dictionaries
        """
        relationships = []
        
        # Relationship patterns
        relation_patterns = {
            'regulates': [r'regulates?', r'controls?', r'modulates?', r'affects?'],
            'interacts_with': [r'interacts? with', r'binds? to', r'associates? with'],
            'associated_with': [r'associated with', r'linked to', r'related to', r'correlated with'],
            'causes': [r'causes?', r'induces?', r'triggers?', r'leads to'],
            'treats': [r'treats?', r'therapy for', r'treatment of']
        }
        
        # Find relationships between entity pairs
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                # Get text between entities
                start = min(entity1['end'], entity2['end'])
                end = max(entity1['start'], entity2['start'])
                
                if start < end:
                    between_text = text[start:end].lower()
                    
                    # Check for relationship patterns
                    for rel_type, patterns in relation_patterns.items():
                        for pattern in patterns:
                            import re
                            if re.search(pattern, between_text):
                                relationships.append({
                                    'source': entity1,
                                    'target': entity2,
                                    'type': rel_type,
                                    'confidence': 0.7,
                                    'evidence': between_text.strip()
                                })
                                break
        
        return relationships


# ============================================================================
# Paper Summarization with T5
# ============================================================================

class PaperSummarizer:
    """
    Paper summarization using T5 model
    Implements abstractive summarization with quality scoring
    """
    
    def __init__(self, model_name: str = "t5-small"):
        """
        Initialize summarizer
        
        Args:
            model_name: HuggingFace model name for T5
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self._initialized = False
    
    def _lazy_init(self):
        """Lazy initialization of models"""
        if self._initialized:
            return
        
        try:
            from transformers import T5Tokenizer, T5ForConditionalGeneration
            
            logger.info(f"Loading T5 model: {self.model_name}")
            self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
            
            self._initialized = True
            logger.info("T5 model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load T5 model: {e}")
            self._initialized = True
    
    def summarize(self, text: str, max_length: int = 150, min_length: int = 40) -> Dict[str, Any]:
        """
        Generate abstractive summary of text
        
        Args:
            text: Input text to summarize
            max_length: Maximum summary length
            min_length: Minimum summary length
            
        Returns:
            Dictionary with summary and quality score
        """
        self._lazy_init()
        
        if self.model is None or self.tokenizer is None:
            # Fallback to extractive summarization
            return self._extractive_summarization(text, max_length)
        
        try:
            # Prepare input
            input_text = f"summarize: {text}"
            inputs = self.tokenizer.encode(
                input_text,
                return_tensors="pt",
                max_length=512,
                truncation=True
            )
            
            # Generate summary
            summary_ids = self.model.generate(
                inputs,
                max_length=max_length,
                min_length=min_length,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True
            )
            
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(text, summary)
            
            return {
                'summary': summary,
                'quality_score': quality_score,
                'method': 'abstractive',
                'model': self.model_name
            }
        except Exception as e:
            logger.error(f"T5 summarization failed: {e}")
            return self._extractive_summarization(text, max_length)
    
    def _extractive_summarization(self, text: str, max_length: int) -> Dict[str, Any]:
        """
        Fallback extractive summarization
        
        Args:
            text: Input text
            max_length: Maximum summary length
            
        Returns:
            Dictionary with summary and quality score
        """
        # Simple extractive summarization: take first N sentences
        sentences = text.split('. ')
        summary_sentences = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            if current_length + sentence_length <= max_length:
                summary_sentences.append(sentence)
                current_length += sentence_length
            else:
                break
        
        summary = '. '.join(summary_sentences)
        if summary and not summary.endswith('.'):
            summary += '.'
        
        return {
            'summary': summary,
            'quality_score': 0.6,
            'method': 'extractive',
            'model': 'rule-based'
        }
    
    def _calculate_quality_score(self, original: str, summary: str) -> float:
        """
        Calculate summary quality score
        
        Args:
            original: Original text
            summary: Generated summary
            
        Returns:
            Quality score between 0 and 1
        """
        # Simple quality metrics
        original_words = set(original.lower().split())
        summary_words = set(summary.lower().split())
        
        # Coverage: how many important words from original are in summary
        coverage = len(original_words & summary_words) / len(original_words) if original_words else 0
        
        # Compression: summary should be significantly shorter
        compression_ratio = len(summary.split()) / len(original.split()) if original else 0
        ideal_compression = 0.3  # Aim for 30% of original length
        compression_score = 1.0 - abs(compression_ratio - ideal_compression)
        
        # Combined score
        quality_score = (coverage * 0.7 + compression_score * 0.3)
        
        return min(max(quality_score, 0.0), 1.0)
    
    def summarize_paper(self, paper_data: Dict[str, Any], max_length: int = 150) -> Dict[str, Any]:
        """
        Summarize a research paper
        
        Args:
            paper_data: Paper dictionary with title and abstract
            max_length: Maximum summary length
            
        Returns:
            Dictionary with paper info and summary
        """
        title = paper_data.get('title', '')
        abstract = paper_data.get('abstract', '')
        
        if not abstract:
            return {
                'pmid': paper_data.get('pmid', ''),
                'title': title,
                'summary': title,  # Use title as fallback
                'quality_score': 0.3,
                'method': 'fallback'
            }
        
        # Combine title and abstract for context
        full_text = f"{title}. {abstract}"
        
        result = self.summarize(full_text, max_length)
        result['pmid'] = paper_data.get('pmid', '')
        result['title'] = title
        
        return result


# ============================================================================
# Literature Mining Service
# ============================================================================

class LiteratureMiningService:
    """
    Main literature mining service that coordinates all components
    """
    
    def __init__(self, redis_client: redis.Redis, email: str = "omniscope@example.com",
                 api_key: Optional[str] = None):
        """
        Initialize literature mining service
        
        Args:
            redis_client: Redis client for caching
            email: Email for NCBI API
            api_key: Optional API key for NCBI
        """
        self.pubmed_fetcher = PubMedFetcher(redis_client, email, api_key)
        self.nlp_pipeline = NLPPipeline()
        self.summarizer = PaperSummarizer()
        self.redis = redis_client
    
    def search_papers(self, query: str, max_results: int = 10, sort: str = 'relevance') -> List[Dict[str, Any]]:
        """
        Search for papers and return full information
        
        Args:
            query: Search query
            max_results: Maximum number of results
            sort: Sort order
            
        Returns:
            List of paper dictionaries
        """
        # Get PMIDs
        pmids = self.pubmed_fetcher.search_papers(query, max_results, sort)
        
        # Get full paper information
        papers_dict = self.pubmed_fetcher.get_papers_batch(pmids)
        
        # Convert to list maintaining order
        papers = [papers_dict.get(pmid, {}) for pmid in pmids if pmid in papers_dict]
        
        return papers
    
    def get_paper(self, pmid: str) -> Dict[str, Any]:
        """
        Get detailed information for a single paper
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Paper dictionary
        """
        return self.pubmed_fetcher.get_paper_info(pmid)
    
    def get_papers_for_biomarker(self, biomarker: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get papers related to a biomarker
        
        Args:
            biomarker: Biomarker name
            max_results: Maximum number of results
            
        Returns:
            List of paper dictionaries
        """
        pmids = self.pubmed_fetcher.search_by_biomarker(biomarker, max_results)
        papers_dict = self.pubmed_fetcher.get_papers_batch(pmids)
        papers = [papers_dict.get(pmid, {}) for pmid in pmids if pmid in papers_dict]
        return papers
    
    def extract_entities_from_text(self, text: str, entity_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Extract entities from text using NLP pipeline
        
        Args:
            text: Input text
            entity_types: List of entity types to extract
            
        Returns:
            List of entity dictionaries
        """
        return self.nlp_pipeline.extract_entities(text, entity_types)
    
    def extract_entities_from_paper(self, pmid: str) -> Dict[str, Any]:
        """
        Extract entities from a paper's abstract
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Dictionary with paper info and extracted entities
        """
        paper = self.get_paper(pmid)
        abstract = paper.get('abstract', '')
        
        if not abstract:
            return {
                'pmid': pmid,
                'entities': [],
                'error': 'No abstract available'
            }
        
        entities = self.nlp_pipeline.extract_entities(abstract)
        
        return {
            'pmid': pmid,
            'title': paper.get('title', ''),
            'abstract': abstract,
            'entities': entities
        }
    
    def extract_relationships_from_paper(self, pmid: str) -> Dict[str, Any]:
        """
        Extract relationships from a paper's abstract
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Dictionary with paper info, entities, and relationships
        """
        paper = self.get_paper(pmid)
        abstract = paper.get('abstract', '')
        
        if not abstract:
            return {
                'pmid': pmid,
                'entities': [],
                'relationships': [],
                'error': 'No abstract available'
            }
        
        entities = self.nlp_pipeline.extract_entities(abstract)
        relationships = self.nlp_pipeline.extract_relationships(abstract, entities)
        
        return {
            'pmid': pmid,
            'title': paper.get('title', ''),
            'abstract': abstract,
            'entities': entities,
            'relationships': relationships
        }
    
    def summarize_paper(self, pmid: str, max_length: int = 150) -> Dict[str, Any]:
        """
        Generate summary for a paper
        
        Args:
            pmid: PubMed ID
            max_length: Maximum summary length
            
        Returns:
            Dictionary with paper info and summary
        """
        paper = self.get_paper(pmid)
        return self.summarizer.summarize_paper(paper, max_length)
    
    def summarize_papers_batch(self, pmids: List[str], max_length: int = 150) -> List[Dict[str, Any]]:
        """
        Generate summaries for multiple papers
        
        Args:
            pmids: List of PubMed IDs
            max_length: Maximum summary length
            
        Returns:
            List of paper summaries
        """
        papers_dict = self.pubmed_fetcher.get_papers_batch(pmids)
        summaries = []
        
        for pmid in pmids:
            if pmid in papers_dict:
                summary = self.summarizer.summarize_paper(papers_dict[pmid], max_length)
                summaries.append(summary)
        
        return summaries


# Create router for API endpoints
router = APIRouter(prefix="/api/literature", tags=["Literature Mining"])


# Dependency to get service instance
def get_literature_service() -> LiteratureMiningService:
    """Get literature mining service instance"""
    import redis
    import os
    
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    
    ncbi_email = os.getenv("NCBI_EMAIL", "omniscope@example.com")
    ncbi_api_key = os.getenv("NCBI_API_KEY", None)
    
    return LiteratureMiningService(redis_client, ncbi_email, ncbi_api_key)


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/search")
async def search_papers(
    request: PaperSearchRequest,
    service: LiteratureMiningService = Depends(get_literature_service)
) -> Dict[str, Any]:
    """
    Search for research papers
    
    Args:
        request: Search request with query, max_results, and sort order
        
    Returns:
        Dictionary with search results
    """
    try:
        papers = service.search_papers(request.query, request.max_results, request.sort)
        
        return {
            "success": True,
            "query": request.query,
            "count": len(papers),
            "papers": papers
        }
    except Exception as e:
        logger.error(f"Paper search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Paper search failed: {str(e)}")


@router.get("/paper/{pmid}")
async def get_paper(
    pmid: str,
    service: LiteratureMiningService = Depends(get_literature_service)
) -> Dict[str, Any]:
    """
    Get detailed information for a specific paper
    
    Args:
        pmid: PubMed ID
        
    Returns:
        Paper information dictionary
    """
    try:
        paper = service.get_paper(pmid)
        
        return {
            "success": True,
            "paper": paper
        }
    except Exception as e:
        logger.error(f"Failed to fetch paper {pmid}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch paper: {str(e)}")


@router.get("/biomarker/{biomarker}/papers")
async def get_biomarker_papers(
    biomarker: str,
    max_results: int = 10,
    service: LiteratureMiningService = Depends(get_literature_service)
) -> Dict[str, Any]:
    """
    Get papers related to a specific biomarker
    
    Args:
        biomarker: Biomarker name (gene, protein, etc.)
        max_results: Maximum number of results
        
    Returns:
        Dictionary with papers related to the biomarker
    """
    try:
        papers = service.get_papers_for_biomarker(biomarker, max_results)
        
        return {
            "success": True,
            "biomarker": biomarker,
            "count": len(papers),
            "papers": papers
        }
    except Exception as e:
        logger.error(f"Failed to fetch papers for biomarker {biomarker}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch papers: {str(e)}")


@router.post("/extract-entities")
async def extract_entities(
    request: EntityExtractionRequest,
    service: LiteratureMiningService = Depends(get_literature_service)
) -> Dict[str, Any]:
    """
    Extract named entities from text
    
    Args:
        request: Entity extraction request with text and optional entity types
        
    Returns:
        Dictionary with extracted entities
    """
    try:
        entities = service.extract_entities_from_text(request.text, request.entity_types)
        
        return {
            "success": True,
            "entity_count": len(entities),
            "entities": entities
        }
    except Exception as e:
        logger.error(f"Entity extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Entity extraction failed: {str(e)}")


@router.get("/paper/{pmid}/entities")
async def extract_paper_entities(
    pmid: str,
    service: LiteratureMiningService = Depends(get_literature_service)
) -> Dict[str, Any]:
    """
    Extract entities from a paper's abstract
    
    Args:
        pmid: PubMed ID
        
    Returns:
        Dictionary with paper info and extracted entities
    """
    try:
        result = service.extract_entities_from_paper(pmid)
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Failed to extract entities from paper {pmid}: {e}")
        raise HTTPException(status_code=500, detail=f"Entity extraction failed: {str(e)}")


@router.get("/paper/{pmid}/relationships")
async def extract_paper_relationships(
    pmid: str,
    service: LiteratureMiningService = Depends(get_literature_service)
) -> Dict[str, Any]:
    """
    Extract relationships from a paper's abstract
    
    Args:
        pmid: PubMed ID
        
    Returns:
        Dictionary with paper info, entities, and relationships
    """
    try:
        result = service.extract_relationships_from_paper(pmid)
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Failed to extract relationships from paper {pmid}: {e}")
        raise HTTPException(status_code=500, detail=f"Relationship extraction failed: {str(e)}")


@router.post("/summarize")
async def summarize_paper(
    request: PaperSummarizeRequest,
    service: LiteratureMiningService = Depends(get_literature_service)
) -> Dict[str, Any]:
    """
    Generate summary for a paper
    
    Args:
        request: Summarization request with PMID and max_length
        
    Returns:
        Dictionary with paper summary
    """
    try:
        result = service.summarize_paper(request.pmid, request.max_length)
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Failed to summarize paper {request.pmid}: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")



# ============================================================================
# Knowledge Graph with Neo4j
# ============================================================================

class KnowledgeGraph:
    """
    Knowledge graph for storing and querying entity relationships
    Uses Neo4j for graph database
    """
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        """
        Initialize knowledge graph
        
        Args:
            uri: Neo4j connection URI
            user: Neo4j username
            password: Neo4j password
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self._initialized = False
    
    def _lazy_init(self):
        """Lazy initialization of Neo4j driver"""
        if self._initialized:
            return
        
        try:
            from neo4j import GraphDatabase
            
            logger.info(f"Connecting to Neo4j at {self.uri}")
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            
            self._initialized = True
            logger.info("Neo4j connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self._initialized = True
    
    def add_entities(self, entities: List[Dict[str, Any]]):
        """
        Add entities to knowledge graph
        
        Args:
            entities: List of entity dictionaries
        """
        self._lazy_init()
        
        if self.driver is None:
            logger.warning("Neo4j not available, skipping entity addition")
            return
        
        with self.driver.session() as session:
            for entity in entities:
                query = """
                MERGE (e:Entity {text: $text, type: $type})
                SET e.confidence = $confidence
                """
                session.run(query, 
                           text=entity['text'],
                           type=entity['type'],
                           confidence=entity['confidence'])
    
    def add_relationships(self, relationships: List[Dict[str, Any]]):
        """
        Add relationships to knowledge graph
        
        Args:
            relationships: List of relationship dictionaries
        """
        self._lazy_init()
        
        if self.driver is None:
            logger.warning("Neo4j not available, skipping relationship addition")
            return
        
        with self.driver.session() as session:
            for rel in relationships:
                source = rel['source']
                target = rel['target']
                rel_type = rel['type'].upper().replace(' ', '_')
                
                query = f"""
                MATCH (s:Entity {{text: $source_text}})
                MATCH (t:Entity {{text: $target_text}})
                MERGE (s)-[r:{rel_type}]->(t)
                SET r.confidence = $confidence, r.evidence = $evidence
                """
                session.run(query,
                           source_text=source['text'],
                           target_text=target['text'],
                           confidence=rel['confidence'],
                           evidence=rel.get('evidence', ''))
    
    def query_entity_relationships(self, entity_text: str, max_depth: int = 2) -> Dict[str, Any]:
        """
        Query relationships for an entity
        
        Args:
            entity_text: Entity text to query
            max_depth: Maximum relationship depth
            
        Returns:
            Dictionary with entity and its relationships
        """
        self._lazy_init()
        
        if self.driver is None:
            return {'entity': entity_text, 'relationships': [], 'error': 'Neo4j not available'}
        
        with self.driver.session() as session:
            query = """
            MATCH path = (e:Entity {text: $entity_text})-[*1..%d]-(related)
            RETURN path
            LIMIT 100
            """ % max_depth
            
            result = session.run(query, entity_text=entity_text)
            
            relationships = []
            for record in result:
                path = record['path']
                for rel in path.relationships:
                    relationships.append({
                        'source': rel.start_node['text'],
                        'target': rel.end_node['text'],
                        'type': rel.type,
                        'confidence': rel.get('confidence', 0.0)
                    })
            
            return {
                'entity': entity_text,
                'relationships': relationships
            }
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()


# ============================================================================
# Paper Ranking System
# ============================================================================

class PaperRanker:
    """
    Paper ranking system using citation count and semantic similarity
    """
    
    def __init__(self):
        """Initialize paper ranker"""
        self.sentence_transformer = None
        self._initialized = False
    
    def _lazy_init(self):
        """Lazy initialization of sentence transformer"""
        if self._initialized:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info("Loading Sentence-BERT model")
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
            self._initialized = True
            logger.info("Sentence-BERT model loaded")
        except Exception as e:
            logger.error(f"Failed to load Sentence-BERT: {e}")
            self._initialized = True
    
    def rank_papers(self, papers: List[Dict[str, Any]], query: str = None) -> List[Dict[str, Any]]:
        """
        Rank papers by relevance
        
        Args:
            papers: List of paper dictionaries
            query: Optional query for semantic similarity ranking
            
        Returns:
            Ranked list of papers with scores
        """
        self._lazy_init()
        
        # Calculate scores for each paper
        for paper in papers:
            paper['relevance_score'] = self._calculate_relevance_score(paper, query)
        
        # Sort by relevance score
        ranked_papers = sorted(papers, key=lambda p: p['relevance_score'], reverse=True)
        
        return ranked_papers
    
    def _calculate_relevance_score(self, paper: Dict[str, Any], query: str = None) -> float:
        """
        Calculate relevance score for a paper
        
        Args:
            paper: Paper dictionary
            query: Optional query for semantic similarity
            
        Returns:
            Relevance score between 0 and 1
        """
        # Citation count score (normalized)
        citation_count = paper.get('citations', 0)
        citation_score = min(citation_count / 100.0, 1.0)  # Normalize to 0-1
        
        # Recency score (newer papers get higher scores)
        year = paper.get('year', 2000)
        current_year = datetime.now().year
        recency_score = max(0, 1.0 - (current_year - year) / 20.0)  # 20 year window
        
        # Semantic similarity score
        semantic_score = 0.5  # Default
        if query and self.sentence_transformer:
            try:
                abstract = paper.get('abstract', '')
                if abstract:
                    from sentence_transformers import util
                    
                    query_embedding = self.sentence_transformer.encode(query, convert_to_tensor=True)
                    abstract_embedding = self.sentence_transformer.encode(abstract, convert_to_tensor=True)
                    
                    similarity = util.cos_sim(query_embedding, abstract_embedding)
                    semantic_score = float(similarity[0][0])
            except Exception as e:
                logger.warning(f"Semantic similarity calculation failed: {e}")
        
        # Combined score (weighted average)
        relevance_score = (
            citation_score * 0.3 +
            recency_score * 0.2 +
            semantic_score * 0.5
        )
        
        return relevance_score


# ============================================================================
# Notification System
# ============================================================================

class NotificationSystem:
    """
    Notification system for new papers
    Monitors topics and sends alerts to subscribed users
    """
    
    def __init__(self, redis_client: redis.Redis):
        """
        Initialize notification system
        
        Args:
            redis_client: Redis client for storing subscriptions
        """
        self.redis = redis_client
    
    def subscribe_user(self, user_id: str, topics: List[str], email: str):
        """
        Subscribe user to topics
        
        Args:
            user_id: User identifier
            topics: List of topics to subscribe to
            email: User email for notifications
        """
        subscription_key = f"literature:subscription:{user_id}"
        
        subscription_data = {
            'user_id': user_id,
            'email': email,
            'topics': topics,
            'subscribed_at': datetime.utcnow().isoformat()
        }
        
        self.redis.set(subscription_key, json.dumps(subscription_data))
        
        # Add to topic indexes
        for topic in topics:
            topic_key = f"literature:topic:{topic}:subscribers"
            self.redis.sadd(topic_key, user_id)
    
    def unsubscribe_user(self, user_id: str, topics: Optional[List[str]] = None):
        """
        Unsubscribe user from topics
        
        Args:
            user_id: User identifier
            topics: Optional list of topics to unsubscribe from (None = all)
        """
        subscription_key = f"literature:subscription:{user_id}"
        
        if topics is None:
            # Unsubscribe from all topics
            subscription_data = self.redis.get(subscription_key)
            if subscription_data:
                data = json.loads(subscription_data)
                topics = data.get('topics', [])
            
            self.redis.delete(subscription_key)
        else:
            # Unsubscribe from specific topics
            subscription_data = self.redis.get(subscription_key)
            if subscription_data:
                data = json.loads(subscription_data)
                current_topics = data.get('topics', [])
                updated_topics = [t for t in current_topics if t not in topics]
                data['topics'] = updated_topics
                self.redis.set(subscription_key, json.dumps(data))
        
        # Remove from topic indexes
        for topic in topics or []:
            topic_key = f"literature:topic:{topic}:subscribers"
            self.redis.srem(topic_key, user_id)
    
    def get_user_subscriptions(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's subscriptions
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with subscription data
        """
        subscription_key = f"literature:subscription:{user_id}"
        subscription_data = self.redis.get(subscription_key)
        
        if subscription_data:
            return json.loads(subscription_data)
        
        return {'user_id': user_id, 'topics': [], 'email': ''}
    
    def check_new_papers(self, topic: str, pubmed_fetcher: PubMedFetcher) -> List[Dict[str, Any]]:
        """
        Check for new papers on a topic
        
        Args:
            topic: Topic to check
            pubmed_fetcher: PubMed fetcher instance
            
        Returns:
            List of new papers
        """
        # Get last check time
        last_check_key = f"literature:topic:{topic}:last_check"
        last_check = self.redis.get(last_check_key)
        
        # Search for recent papers
        query = f"{topic} AND (\"last 7 days\"[PDat])"
        pmids = pubmed_fetcher.search_papers(query, max_results=10, sort='pub_date')
        
        # Get paper details
        papers = []
        if pmids:
            papers_dict = pubmed_fetcher.get_papers_batch(pmids)
            papers = [papers_dict[pmid] for pmid in pmids if pmid in papers_dict]
        
        # Update last check time
        self.redis.set(last_check_key, datetime.utcnow().isoformat())
        
        return papers
    
    def send_notification(self, user_email: str, topic: str, papers: List[Dict[str, Any]]):
        """
        Send notification email to user
        
        Args:
            user_email: User email address
            topic: Topic name
            papers: List of new papers
        """
        # In a real implementation, this would send an email
        # For now, just log the notification
        logger.info(f"Notification for {user_email}: {len(papers)} new papers on '{topic}'")
        
        # Store notification in Redis for retrieval
        notification_key = f"literature:notification:{user_email}:{int(time.time())}"
        notification_data = {
            'email': user_email,
            'topic': topic,
            'paper_count': len(papers),
            'papers': [p.get('pmid', '') for p in papers],
            'sent_at': datetime.utcnow().isoformat()
        }
        self.redis.setex(notification_key, 7 * 24 * 60 * 60, json.dumps(notification_data))


# ============================================================================
# Natural Language Query Interface
# ============================================================================

class NaturalLanguageQuery:
    """
    Natural language query interface for literature corpus
    Uses BERT for query understanding and answer generation
    """
    
    def __init__(self):
        """Initialize natural language query system"""
        self.qa_pipeline = None
        self._initialized = False
    
    def _lazy_init(self):
        """Lazy initialization of QA pipeline"""
        if self._initialized:
            return
        
        try:
            from transformers import pipeline
            
            logger.info("Loading QA pipeline")
            self.qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
            
            self._initialized = True
            logger.info("QA pipeline loaded")
        except Exception as e:
            logger.error(f"Failed to load QA pipeline: {e}")
            self._initialized = True
    
    def query(self, question: str, papers: List[Dict[str, Any]], max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Answer question using paper corpus
        
        Args:
            question: Natural language question
            papers: List of papers to search
            max_results: Maximum number of results
            
        Returns:
            List of answers with source papers
        """
        self._lazy_init()
        
        answers = []
        
        for paper in papers[:max_results]:
            abstract = paper.get('abstract', '')
            if not abstract:
                continue
            
            if self.qa_pipeline:
                try:
                    result = self.qa_pipeline(question=question, context=abstract)
                    
                    answers.append({
                        'answer': result['answer'],
                        'confidence': result['score'],
                        'pmid': paper.get('pmid', ''),
                        'title': paper.get('title', ''),
                        'source': 'qa_model'
                    })
                except Exception as e:
                    logger.warning(f"QA pipeline failed for paper {paper.get('pmid', '')}: {e}")
            else:
                # Fallback: simple keyword matching
                answer = self._keyword_based_answer(question, abstract)
                if answer:
                    answers.append({
                        'answer': answer,
                        'confidence': 0.5,
                        'pmid': paper.get('pmid', ''),
                        'title': paper.get('title', ''),
                        'source': 'keyword_match'
                    })
        
        # Sort by confidence
        answers.sort(key=lambda x: x['confidence'], reverse=True)
        
        return answers[:max_results]
    
    def _keyword_based_answer(self, question: str, text: str) -> Optional[str]:
        """
        Fallback keyword-based answer extraction
        
        Args:
            question: Question text
            text: Context text
            
        Returns:
            Answer string or None
        """
        # Extract keywords from question
        question_words = set(question.lower().split())
        
        # Find sentences containing question keywords
        sentences = text.split('. ')
        scored_sentences = []
        
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            overlap = len(question_words & sentence_words)
            if overlap > 0:
                scored_sentences.append((sentence, overlap))
        
        if scored_sentences:
            # Return sentence with most keyword overlap
            best_sentence = max(scored_sentences, key=lambda x: x[1])[0]
            return best_sentence
        
        return None


# Update LiteratureMiningService to include all new components
class EnhancedLiteratureMiningService(LiteratureMiningService):
    """
    Enhanced literature mining service with all advanced features
    """
    
    def __init__(self, redis_client: redis.Redis, email: str = "omniscope@example.com",
                 api_key: Optional[str] = None, neo4j_uri: str = None, neo4j_user: str = None,
                 neo4j_password: str = None):
        """
        Initialize enhanced literature mining service
        
        Args:
            redis_client: Redis client for caching
            email: Email for NCBI API
            api_key: Optional API key for NCBI
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
        """
        super().__init__(redis_client, email, api_key)
        
        # Initialize additional components
        self.knowledge_graph = KnowledgeGraph(
            uri=neo4j_uri or "bolt://localhost:7687",
            user=neo4j_user or "neo4j",
            password=neo4j_password or "password"
        )
        self.paper_ranker = PaperRanker()
        self.notification_system = NotificationSystem(redis_client)
        self.nl_query = NaturalLanguageQuery()
    
    def build_knowledge_graph_from_paper(self, pmid: str):
        """
        Extract entities and relationships from paper and add to knowledge graph
        
        Args:
            pmid: PubMed ID
        """
        result = self.extract_relationships_from_paper(pmid)
        
        entities = result.get('entities', [])
        relationships = result.get('relationships', [])
        
        self.knowledge_graph.add_entities(entities)
        self.knowledge_graph.add_relationships(relationships)
    
    def query_knowledge_graph(self, entity: str, max_depth: int = 2) -> Dict[str, Any]:
        """
        Query knowledge graph for entity relationships
        
        Args:
            entity: Entity text
            max_depth: Maximum relationship depth
            
        Returns:
            Dictionary with relationships
        """
        return self.knowledge_graph.query_entity_relationships(entity, max_depth)
    
    def rank_papers(self, papers: List[Dict[str, Any]], query: str = None) -> List[Dict[str, Any]]:
        """
        Rank papers by relevance
        
        Args:
            papers: List of papers
            query: Optional query for semantic ranking
            
        Returns:
            Ranked list of papers
        """
        return self.paper_ranker.rank_papers(papers, query)
    
    def subscribe_to_topic(self, user_id: str, topics: List[str], email: str):
        """
        Subscribe user to topics for notifications
        
        Args:
            user_id: User identifier
            topics: List of topics
            email: User email
        """
        self.notification_system.subscribe_user(user_id, topics, email)
    
    def query_literature(self, question: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Answer natural language question using literature corpus
        
        Args:
            question: Natural language question
            max_results: Maximum number of results
            
        Returns:
            List of answers with sources
        """
        # Search for relevant papers
        papers = self.search_papers(question, max_results=10)
        
        # Use NL query system to find answers
        answers = self.nl_query.query(question, papers, max_results)
        
        return answers


# Update dependency function to use enhanced service
def get_enhanced_literature_service() -> EnhancedLiteratureMiningService:
    """Get enhanced literature mining service instance"""
    import redis
    import os
    
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    
    ncbi_email = os.getenv("NCBI_EMAIL", "omniscope@example.com")
    ncbi_api_key = os.getenv("NCBI_API_KEY", None)
    
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
    
    return EnhancedLiteratureMiningService(
        redis_client, ncbi_email, ncbi_api_key,
        neo4j_uri, neo4j_user, neo4j_password
    )


# ============================================================================
# Additional API Endpoints for Advanced Features
# ============================================================================

@router.post("/knowledge-graph/build/{pmid}")
async def build_knowledge_graph(
    pmid: str,
    service: EnhancedLiteratureMiningService = Depends(get_enhanced_literature_service)
) -> Dict[str, Any]:
    """
    Build knowledge graph from paper
    
    Args:
        pmid: PubMed ID
        
    Returns:
        Success status
    """
    try:
        service.build_knowledge_graph_from_paper(pmid)
        
        return {
            "success": True,
            "message": f"Knowledge graph updated with paper {pmid}"
        }
    except Exception as e:
        logger.error(f"Failed to build knowledge graph: {e}")
        raise HTTPException(status_code=500, detail=f"Knowledge graph build failed: {str(e)}")


@router.get("/knowledge-graph/query/{entity}")
async def query_knowledge_graph(
    entity: str,
    max_depth: int = 2,
    service: EnhancedLiteratureMiningService = Depends(get_enhanced_literature_service)
) -> Dict[str, Any]:
    """
    Query knowledge graph for entity relationships
    
    Args:
        entity: Entity text
        max_depth: Maximum relationship depth
        
    Returns:
        Dictionary with relationships
    """
    try:
        result = service.query_knowledge_graph(entity, max_depth)
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Knowledge graph query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.post("/rank")
async def rank_papers(
    request: PaperSearchRequest,
    service: EnhancedLiteratureMiningService = Depends(get_enhanced_literature_service)
) -> Dict[str, Any]:
    """
    Search and rank papers by relevance
    
    Args:
        request: Search request
        
    Returns:
        Ranked list of papers
    """
    try:
        papers = service.search_papers(request.query, request.max_results, request.sort)
        ranked_papers = service.rank_papers(papers, request.query)
        
        return {
            "success": True,
            "query": request.query,
            "count": len(ranked_papers),
            "papers": ranked_papers
        }
    except Exception as e:
        logger.error(f"Paper ranking failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ranking failed: {str(e)}")


@router.post("/subscribe")
async def subscribe_to_topics(
    request: TopicSubscriptionRequest,
    service: EnhancedLiteratureMiningService = Depends(get_enhanced_literature_service)
) -> Dict[str, Any]:
    """
    Subscribe user to topics for notifications
    
    Args:
        request: Subscription request
        
    Returns:
        Success status
    """
    try:
        service.subscribe_to_topic(request.user_id, request.topics, request.email)
        
        return {
            "success": True,
            "message": f"Subscribed to {len(request.topics)} topics"
        }
    except Exception as e:
        logger.error(f"Subscription failed: {e}")
        raise HTTPException(status_code=500, detail=f"Subscription failed: {str(e)}")


@router.post("/query")
async def natural_language_query(
    request: NaturalLanguageQueryRequest,
    service: EnhancedLiteratureMiningService = Depends(get_enhanced_literature_service)
) -> Dict[str, Any]:
    """
    Answer natural language question using literature corpus
    
    Args:
        request: Query request
        
    Returns:
        List of answers with sources
    """
    try:
        answers = service.query_literature(request.query, request.max_results)
        
        return {
            "success": True,
            "question": request.query,
            "answer_count": len(answers),
            "answers": answers
        }
    except Exception as e:
        logger.error(f"Natural language query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
