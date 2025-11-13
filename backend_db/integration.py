"""
Integration Hub - External Database Adapters
Provides adapters for connecting to external biological databases (NCBI, UniProt, KEGG, PubMed, STRING)
"""

import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
import json
import logging
import redis

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter for API calls"""
    
    def __init__(self, redis_client: redis.Redis, key_prefix: str, max_requests: int, time_window: int):
        """
        Initialize rate limiter
        
        Args:
            redis_client: Redis client instance
            key_prefix: Prefix for Redis keys
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
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
        """
        Retry function with exponential backoff
        
        Args:
            func: Function to retry
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
        """
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
                    delay *= 2  # Exponential backoff
        
        raise last_exception


class NCBIAdapter:
    """Adapter for NCBI E-utilities API"""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, redis_client: redis.Redis, email: str = "omniscope@example.com", api_key: Optional[str] = None):
        """
        Initialize NCBI adapter
        
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
        self.rate_limiter = RateLimiter(redis_client, "ncbi_rate_limit", max_requests, 1)
        
        self.cache_ttl = 7 * 24 * 60 * 60  # 7 days in seconds
    
    def _get_cache_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key"""
        return f"integration:ncbi:{prefix}:{identifier}"
    
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
            self.rate_limiter.wait_if_needed("ncbi")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response
        
        return RetryHandler.retry_with_backoff(request_func)
    
    def search_gene(self, query: str, max_results: int = 10) -> List[str]:
        """
        Search for genes using E-search
        
        Args:
            query: Search query (gene name, symbol, etc.)
            max_results: Maximum number of results to return
            
        Returns:
            List of gene IDs
        """
        params = {
            'db': 'gene',
            'term': query,
            'retmax': max_results,
            'retmode': 'json'
        }
        
        response = self._make_request('esearch.fcgi', params)
        data = response.json()
        
        return data.get('esearchresult', {}).get('idlist', [])
    
    def get_gene_info(self, gene_id: str) -> Dict[str, Any]:
        """
        Get detailed gene information
        
        Args:
            gene_id: NCBI Gene ID
            
        Returns:
            Dictionary containing gene information
        """
        # Check cache first
        cache_key = self._get_cache_key("gene", gene_id)
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"Cache hit for gene {gene_id}")
            return cached_data
        
        # Fetch from API
        params = {
            'db': 'gene',
            'id': gene_id,
            'retmode': 'xml'
        }
        
        response = self._make_request('esummary.fcgi', params)
        
        # Parse XML response
        root = ET.fromstring(response.content)
        gene_data = self._parse_gene_xml(root, gene_id)
        
        # Add metadata
        gene_data['source'] = 'NCBI'
        gene_data['retrieved_at'] = datetime.utcnow().isoformat()
        
        # Cache the result
        self._set_to_cache(cache_key, gene_data)
        
        return gene_data
    
    def _parse_gene_xml(self, root: ET.Element, gene_id: str) -> Dict[str, Any]:
        """Parse gene XML response"""
        gene_data = {
            'gene_id': gene_id,
            'symbol': '',
            'name': '',
            'description': '',
            'organism': '',
            'chromosome': '',
            'map_location': '',
            'gene_type': '',
            'summary': ''
        }
        
        # Find the DocumentSummary element
        doc_sum = root.find('.//DocumentSummary')
        if doc_sum is not None:
            # Extract fields
            for field in ['Name', 'Description', 'Organism', 'Chromosome', 'MapLocation', 'GeneType', 'Summary']:
                element = doc_sum.find(f'.//{field}')
                if element is not None and element.text:
                    key = field.lower() if field != 'Name' else 'symbol'
                    if field == 'Description':
                        key = 'name'
                    gene_data[key] = element.text
        
        return gene_data
    
    def get_gene_batch(self, gene_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get information for multiple genes
        
        Args:
            gene_ids: List of NCBI Gene IDs
            
        Returns:
            Dictionary mapping gene IDs to gene information
        """
        results = {}
        uncached_ids = []
        
        # Check cache for each gene
        for gene_id in gene_ids:
            cache_key = self._get_cache_key("gene", gene_id)
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                results[gene_id] = cached_data
            else:
                uncached_ids.append(gene_id)
        
        # Fetch uncached genes in batch
        if uncached_ids:
            # NCBI allows batch requests with comma-separated IDs
            params = {
                'db': 'gene',
                'id': ','.join(uncached_ids),
                'retmode': 'xml'
            }
            
            response = self._make_request('esummary.fcgi', params)
            root = ET.fromstring(response.content)
            
            # Parse each gene
            for doc_sum in root.findall('.//DocumentSummary'):
                gene_id = doc_sum.get('uid')
                if gene_id:
                    gene_data = self._parse_gene_xml(ET.ElementTree(doc_sum).getroot(), gene_id)
                    gene_data['source'] = 'NCBI'
                    gene_data['retrieved_at'] = datetime.utcnow().isoformat()
                    
                    # Cache and add to results
                    cache_key = self._get_cache_key("gene", gene_id)
                    self._set_to_cache(cache_key, gene_data)
                    results[gene_id] = gene_data
        
        return results
    
    def get_gene_sequence(self, gene_id: str, sequence_type: str = 'fasta') -> str:
        """
        Get gene sequence
        
        Args:
            gene_id: NCBI Gene ID
            sequence_type: Sequence format (fasta, gb, etc.)
            
        Returns:
            Sequence data as string
        """
        params = {
            'db': 'gene',
            'id': gene_id,
            'rettype': sequence_type,
            'retmode': 'text'
        }
        
        response = self._make_request('efetch.fcgi', params)
        return response.text
    
    def link_to_pubmed(self, gene_id: str) -> List[str]:
        """
        Get PubMed IDs linked to a gene
        
        Args:
            gene_id: NCBI Gene ID
            
        Returns:
            List of PubMed IDs
        """
        params = {
            'dbfrom': 'gene',
            'db': 'pubmed',
            'id': gene_id,
            'retmode': 'json'
        }
        
        response = self._make_request('elink.fcgi', params)
        data = response.json()
        
        pubmed_ids = []
        linksets = data.get('linksets', [])
        for linkset in linksets:
            for linksetdb in linkset.get('linksetdbs', []):
                pubmed_ids.extend(linksetdb.get('links', []))
        
        return pubmed_ids


class UniProtAdapter:
    """Adapter for UniProt REST API"""
    
    BASE_URL = "https://rest.uniprot.org"
    
    def __init__(self, redis_client: redis.Redis):
        """
        Initialize UniProt adapter
        
        Args:
            redis_client: Redis client for caching
        """
        self.redis = redis_client
        self.rate_limiter = RateLimiter(redis_client, "uniprot_rate_limit", 10, 1)
        self.cache_ttl = 7 * 24 * 60 * 60  # 7 days
    
    def _get_cache_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key"""
        return f"integration:uniprot:{prefix}:{identifier}"
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache"""
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    def _set_to_cache(self, key: str, data: Dict):
        """Set data to cache"""
        self.redis.setex(key, self.cache_ttl, json.dumps(data))
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """Make API request with rate limiting and retry"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        def request_func():
            self.rate_limiter.wait_if_needed("uniprot")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response
        
        return RetryHandler.retry_with_backoff(request_func)
    
    def get_protein_info(self, uniprot_id: str) -> Dict[str, Any]:
        """
        Get detailed protein information
        
        Args:
            uniprot_id: UniProt accession ID
            
        Returns:
            Dictionary containing protein information
        """
        # Check cache first
        cache_key = self._get_cache_key("protein", uniprot_id)
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"Cache hit for protein {uniprot_id}")
            return cached_data
        
        # Fetch from API
        response = self._make_request(f"uniprotkb/{uniprot_id}.json")
        data = response.json()
        
        # Parse response
        protein_data = self._parse_protein_data(data, uniprot_id)
        
        # Add metadata
        protein_data['source'] = 'UniProt'
        protein_data['retrieved_at'] = datetime.utcnow().isoformat()
        
        # Cache the result
        self._set_to_cache(cache_key, protein_data)
        
        return protein_data
    
    def _parse_protein_data(self, data: Dict, uniprot_id: str) -> Dict[str, Any]:
        """Parse UniProt JSON response"""
        protein_data = {
            'uniprot_id': uniprot_id,
            'protein_name': '',
            'gene_names': [],
            'organism': '',
            'function': '',
            'subcellular_location': [],
            'domains': [],
            'keywords': [],
            'sequence': '',
            'length': 0
        }
        
        # Extract protein names
        if 'proteinDescription' in data:
            rec_name = data['proteinDescription'].get('recommendedName', {})
            if 'fullName' in rec_name:
                protein_data['protein_name'] = rec_name['fullName'].get('value', '')
        
        # Extract gene names
        if 'genes' in data:
            for gene in data['genes']:
                if 'geneName' in gene:
                    protein_data['gene_names'].append(gene['geneName'].get('value', ''))
        
        # Extract organism
        if 'organism' in data:
            protein_data['organism'] = data['organism'].get('scientificName', '')
        
        # Extract function
        if 'comments' in data:
            for comment in data['comments']:
                if comment.get('commentType') == 'FUNCTION':
                    texts = comment.get('texts', [])
                    if texts:
                        protein_data['function'] = texts[0].get('value', '')
                elif comment.get('commentType') == 'SUBCELLULAR LOCATION':
                    locations = comment.get('subcellularLocations', [])
                    for loc in locations:
                        if 'location' in loc:
                            protein_data['subcellular_location'].append(loc['location'].get('value', ''))
        
        # Extract domains
        if 'features' in data:
            for feature in data['features']:
                if feature.get('type') == 'Domain':
                    protein_data['domains'].append(feature.get('description', ''))
        
        # Extract keywords
        if 'keywords' in data:
            protein_data['keywords'] = [kw.get('name', '') for kw in data['keywords']]
        
        # Extract sequence
        if 'sequence' in data:
            protein_data['sequence'] = data['sequence'].get('value', '')
            protein_data['length'] = data['sequence'].get('length', 0)
        
        return protein_data
    
    def search_proteins(self, query: str, max_results: int = 10) -> List[str]:
        """
        Search for proteins
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of UniProt IDs
        """
        params = {
            'query': query,
            'size': max_results,
            'format': 'json',
            'fields': 'accession'
        }
        
        response = self._make_request("uniprotkb/search", params)
        data = response.json()
        
        results = []
        for result in data.get('results', []):
            if 'primaryAccession' in result:
                results.append(result['primaryAccession'])
        
        return results
    
    def map_ids(self, from_db: str, to_db: str, identifiers: List[str]) -> Dict[str, List[str]]:
        """
        Map identifiers between databases
        
        Args:
            from_db: Source database (e.g., 'UniProtKB_AC-ID', 'Gene_Name')
            to_db: Target database (e.g., 'NCBI_GeneID', 'Ensembl')
            identifiers: List of identifiers to map
            
        Returns:
            Dictionary mapping source IDs to target IDs
        """
        # UniProt ID mapping service
        params = {
            'from': from_db,
            'to': to_db,
            'ids': ','.join(identifiers)
        }
        
        response = self._make_request("idmapping/run", params)
        job_id = response.json().get('jobId')
        
        if not job_id:
            return {}
        
        # Poll for results
        max_attempts = 30
        for attempt in range(max_attempts):
            time.sleep(1)
            status_response = self._make_request(f"idmapping/status/{job_id}")
            status_data = status_response.json()
            
            if 'results' in status_data or 'failedIds' in status_data:
                # Job complete, fetch results
                results_response = self._make_request(f"idmapping/results/{job_id}")
                results_data = results_response.json()
                
                # Parse mapping results
                mapping = {}
                for result in results_data.get('results', []):
                    from_id = result.get('from')
                    to_id = result.get('to')
                    if from_id and to_id:
                        if from_id not in mapping:
                            mapping[from_id] = []
                        mapping[from_id].append(to_id)
                
                return mapping
        
        raise Exception("ID mapping timeout")
    
    def get_protein_batch(self, uniprot_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get information for multiple proteins
        
        Args:
            uniprot_ids: List of UniProt IDs
            
        Returns:
            Dictionary mapping UniProt IDs to protein information
        """
        results = {}
        
        for uniprot_id in uniprot_ids:
            try:
                results[uniprot_id] = self.get_protein_info(uniprot_id)
            except Exception as e:
                logger.error(f"Failed to fetch protein {uniprot_id}: {e}")
                results[uniprot_id] = {'error': str(e)}
        
        return results


class KEGGAdapter:
    """Adapter for KEGG REST API"""
    
    BASE_URL = "https://rest.kegg.jp"
    
    def __init__(self, redis_client: redis.Redis):
        """
        Initialize KEGG adapter
        
        Args:
            redis_client: Redis client for caching
        """
        self.redis = redis_client
        self.rate_limiter = RateLimiter(redis_client, "kegg_rate_limit", 10, 1)
        self.cache_ttl = 7 * 24 * 60 * 60  # 7 days
    
    def _get_cache_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key"""
        return f"integration:kegg:{prefix}:{identifier}"
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache"""
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    def _set_to_cache(self, key: str, data: Dict):
        """Set data to cache"""
        self.redis.setex(key, self.cache_ttl, json.dumps(data))
    
    def _make_request(self, endpoint: str) -> requests.Response:
        """Make API request with rate limiting and retry"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        def request_func():
            self.rate_limiter.wait_if_needed("kegg")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response
        
        return RetryHandler.retry_with_backoff(request_func)
    
    def get_pathway_info(self, pathway_id: str) -> Dict[str, Any]:
        """
        Get pathway information
        
        Args:
            pathway_id: KEGG pathway ID (e.g., 'hsa00010')
            
        Returns:
            Dictionary containing pathway information
        """
        # Check cache first
        cache_key = self._get_cache_key("pathway", pathway_id)
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"Cache hit for pathway {pathway_id}")
            return cached_data
        
        # Fetch from API
        response = self._make_request(f"get/{pathway_id}")
        
        # Parse response
        pathway_data = self._parse_kegg_entry(response.text, pathway_id)
        pathway_data['pathway_id'] = pathway_id
        
        # Add metadata
        pathway_data['source'] = 'KEGG'
        pathway_data['retrieved_at'] = datetime.utcnow().isoformat()
        
        # Cache the result
        self._set_to_cache(cache_key, pathway_data)
        
        return pathway_data
    
    def _parse_kegg_entry(self, text: str, entry_id: str) -> Dict[str, Any]:
        """Parse KEGG flat file format"""
        data = {
            'entry_id': entry_id,
            'name': '',
            'description': '',
            'class': '',
            'genes': [],
            'compounds': [],
            'reactions': [],
            'modules': [],
            'diseases': []
        }
        
        current_field = None
        lines = text.split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            # Check if line starts with a field name
            if line[0] != ' ':
                parts = line.split(None, 1)
                if len(parts) >= 1:
                    current_field = parts[0]
                    value = parts[1] if len(parts) > 1 else ''
                    
                    if current_field == 'NAME':
                        data['name'] = value
                    elif current_field == 'DESCRIPTION':
                        data['description'] = value
                    elif current_field == 'CLASS':
                        data['class'] = value
            else:
                # Continuation of previous field
                value = line.strip()
                
                if current_field == 'GENE':
                    # Parse gene entries
                    if ':' in value:
                        gene_id = value.split(':')[0].strip()
                        data['genes'].append(gene_id)
                elif current_field == 'COMPOUND':
                    if value.startswith('C'):
                        compound_id = value.split()[0]
                        data['compounds'].append(compound_id)
                elif current_field == 'REACTION':
                    if value.startswith('R'):
                        reaction_id = value.split()[0]
                        data['reactions'].append(reaction_id)
                elif current_field == 'MODULE':
                    if value.startswith('M'):
                        module_id = value.split()[0]
                        data['modules'].append(module_id)
                elif current_field == 'DISEASE':
                    if value.startswith('H'):
                        disease_id = value.split()[0]
                        data['diseases'].append(disease_id)
        
        return data
    
    def search_pathways(self, query: str) -> List[Dict[str, str]]:
        """
        Search for pathways
        
        Args:
            query: Search query
            
        Returns:
            List of pathway dictionaries with id and name
        """
        response = self._make_request(f"find/pathway/{query}")
        
        results = []
        for line in response.text.split('\n'):
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 2:
                    results.append({
                        'pathway_id': parts[0],
                        'name': parts[1]
                    })
        
        return results
    
    def get_compound_info(self, compound_id: str) -> Dict[str, Any]:
        """
        Get compound information
        
        Args:
            compound_id: KEGG compound ID (e.g., 'C00002')
            
        Returns:
            Dictionary containing compound information
        """
        # Check cache first
        cache_key = self._get_cache_key("compound", compound_id)
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"Cache hit for compound {compound_id}")
            return cached_data
        
        # Fetch from API
        response = self._make_request(f"get/{compound_id}")
        
        # Parse response
        compound_data = self._parse_kegg_entry(response.text, compound_id)
        compound_data['compound_id'] = compound_id
        
        # Add metadata
        compound_data['source'] = 'KEGG'
        compound_data['retrieved_at'] = datetime.utcnow().isoformat()
        
        # Cache the result
        self._set_to_cache(cache_key, compound_data)
        
        return compound_data
    
    def get_reaction_info(self, reaction_id: str) -> Dict[str, Any]:
        """
        Get reaction information
        
        Args:
            reaction_id: KEGG reaction ID (e.g., 'R00001')
            
        Returns:
            Dictionary containing reaction information
        """
        # Check cache first
        cache_key = self._get_cache_key("reaction", reaction_id)
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"Cache hit for reaction {reaction_id}")
            return cached_data
        
        # Fetch from API
        response = self._make_request(f"get/{reaction_id}")
        
        # Parse response
        reaction_data = self._parse_kegg_entry(response.text, reaction_id)
        reaction_data['reaction_id'] = reaction_id
        
        # Add metadata
        reaction_data['source'] = 'KEGG'
        reaction_data['retrieved_at'] = datetime.utcnow().isoformat()
        
        # Cache the result
        self._set_to_cache(cache_key, reaction_data)
        
        return reaction_data
    
    def link_genes_to_pathways(self, gene_ids: List[str], organism: str = 'hsa') -> Dict[str, List[str]]:
        """
        Link genes to pathways
        
        Args:
            gene_ids: List of gene IDs
            organism: Organism code (default: 'hsa' for human)
            
        Returns:
            Dictionary mapping gene IDs to pathway IDs
        """
        results = {}
        
        for gene_id in gene_ids:
            # Format gene ID with organism prefix
            kegg_gene_id = f"{organism}:{gene_id}"
            
            try:
                response = self._make_request(f"link/pathway/{kegg_gene_id}")
                
                pathways = []
                for line in response.text.split('\n'):
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            pathways.append(parts[1])
                
                results[gene_id] = pathways
            except Exception as e:
                logger.error(f"Failed to link gene {gene_id} to pathways: {e}")
                results[gene_id] = []
        
        return results



class PubMedAdapter:
    """Adapter for PubMed E-utilities API"""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, redis_client: redis.Redis, email: str = "omniscope@example.com", api_key: Optional[str] = None):
        """
        Initialize PubMed adapter
        
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
        self.rate_limiter = RateLimiter(redis_client, "pubmed_rate_limit", max_requests, 1)
        
        self.cache_ttl = 30 * 24 * 60 * 60  # 30 days in seconds
    
    def _get_cache_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key"""
        return f"integration:pubmed:{prefix}:{identifier}"
    
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
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json',
            'sort': sort
        }
        
        response = self._make_request('esearch.fcgi', params)
        data = response.json()
        
        return data.get('esearchresult', {}).get('idlist', [])
    
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
            'mesh_terms': []
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
        Get information for multiple papers
        
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
            params = {
                'db': 'pubmed',
                'id': ','.join(uncached_ids),
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



class STRINGAdapter:
    """Adapter for STRING protein-protein interaction database API"""
    
    BASE_URL = "https://string-db.org/api"
    
    def __init__(self, redis_client: redis.Redis):
        """
        Initialize STRING adapter
        
        Args:
            redis_client: Redis client for caching
        """
        self.redis = redis_client
        self.rate_limiter = RateLimiter(redis_client, "string_rate_limit", 10, 1)
        self.cache_ttl = 7 * 24 * 60 * 60  # 7 days
    
    def _get_cache_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key"""
        return f"integration:string:{prefix}:{identifier}"
    
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
        url = f"{self.BASE_URL}/{endpoint}"
        
        def request_func():
            self.rate_limiter.wait_if_needed("string")
            response = requests.post(url, data=params, timeout=30)
            response.raise_for_status()
            return response
        
        return RetryHandler.retry_with_backoff(request_func)
    
    def get_protein_interactions(self, protein_id: str, species: int = 9606, 
                                 required_score: int = 400, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get protein-protein interactions
        
        Args:
            protein_id: Protein identifier (gene name, UniProt ID, etc.)
            species: NCBI taxonomy ID (default: 9606 for human)
            required_score: Minimum interaction score (0-1000, default: 400)
            limit: Maximum number of interactions to return
            
        Returns:
            List of interaction dictionaries
        """
        # Check cache first
        cache_key = self._get_cache_key("interactions", f"{protein_id}_{species}_{required_score}")
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"Cache hit for protein interactions {protein_id}")
            return cached_data
        
        # Fetch from API
        params = {
            'identifiers': protein_id,
            'species': species,
            'required_score': required_score,
            'limit': limit
        }
        
        response = self._make_request('json/network', params)
        interactions = response.json()
        
        # Parse interactions
        parsed_interactions = []
        for interaction in interactions:
            parsed_interactions.append({
                'protein_a': interaction.get('preferredName_A', ''),
                'protein_b': interaction.get('preferredName_B', ''),
                'score': interaction.get('score', 0),
                'nscore': interaction.get('nscore', 0),  # neighborhood score
                'fscore': interaction.get('fscore', 0),  # fusion score
                'pscore': interaction.get('pscore', 0),  # phylogenetic profile score
                'ascore': interaction.get('ascore', 0),  # coexpression score
                'escore': interaction.get('escore', 0),  # experimental score
                'dscore': interaction.get('dscore', 0),  # database score
                'tscore': interaction.get('tscore', 0),  # textmining score
            })
        
        # Add metadata
        result = {
            'protein_id': protein_id,
            'species': species,
            'interactions': parsed_interactions,
            'source': 'STRING',
            'retrieved_at': datetime.utcnow().isoformat()
        }
        
        # Cache the result
        self._set_to_cache(cache_key, result)
        
        return result
    
    def get_interaction_partners(self, protein_ids: List[str], species: int = 9606,
                                required_score: int = 400) -> Dict[str, Any]:
        """
        Get interaction partners for multiple proteins
        
        Args:
            protein_ids: List of protein identifiers
            species: NCBI taxonomy ID
            required_score: Minimum interaction score
            
        Returns:
            Dictionary with network data
        """
        params = {
            'identifiers': '\r'.join(protein_ids),
            'species': species,
            'required_score': required_score
        }
        
        response = self._make_request('json/network', params)
        interactions = response.json()
        
        # Build network structure
        nodes = set()
        edges = []
        
        for interaction in interactions:
            protein_a = interaction.get('preferredName_A', '')
            protein_b = interaction.get('preferredName_B', '')
            score = interaction.get('score', 0)
            
            nodes.add(protein_a)
            nodes.add(protein_b)
            edges.append({
                'source': protein_a,
                'target': protein_b,
                'score': score
            })
        
        return {
            'nodes': list(nodes),
            'edges': edges,
            'species': species,
            'source': 'STRING',
            'retrieved_at': datetime.utcnow().isoformat()
        }
    
    def get_enrichment(self, protein_ids: List[str], species: int = 9606) -> Dict[str, Any]:
        """
        Get functional enrichment for a set of proteins
        
        Args:
            protein_ids: List of protein identifiers
            species: NCBI taxonomy ID
            
        Returns:
            Dictionary with enrichment results
        """
        params = {
            'identifiers': '\r'.join(protein_ids),
            'species': species
        }
        
        response = self._make_request('json/enrichment', params)
        enrichment_data = response.json()
        
        # Organize by category
        enrichment_by_category = {}
        for item in enrichment_data:
            category = item.get('category', 'Unknown')
            if category not in enrichment_by_category:
                enrichment_by_category[category] = []
            
            enrichment_by_category[category].append({
                'term': item.get('term', ''),
                'description': item.get('description', ''),
                'number_of_genes': item.get('number_of_genes', 0),
                'number_of_genes_in_background': item.get('number_of_genes_in_background', 0),
                'p_value': item.get('p_value', 1.0),
                'fdr': item.get('fdr', 1.0)
            })
        
        return {
            'enrichment': enrichment_by_category,
            'species': species,
            'source': 'STRING',
            'retrieved_at': datetime.utcnow().isoformat()
        }
    
    def resolve_identifiers(self, identifiers: List[str], species: int = 9606) -> Dict[str, str]:
        """
        Resolve protein identifiers to STRING IDs
        
        Args:
            identifiers: List of protein identifiers
            species: NCBI taxonomy ID
            
        Returns:
            Dictionary mapping input identifiers to STRING IDs
        """
        params = {
            'identifiers': '\r'.join(identifiers),
            'species': species,
            'echo_query': 1
        }
        
        response = self._make_request('json/get_string_ids', params)
        data = response.json()
        
        mapping = {}
        for item in data:
            query_id = item.get('queryItem', '')
            string_id = item.get('stringId', '')
            if query_id and string_id:
                mapping[query_id] = string_id
        
        return mapping
    
    def get_homology(self, protein_id: str, source_species: int = 9606,
                    target_species: int = 10090) -> List[Dict[str, Any]]:
        """
        Get homologous proteins in another species
        
        Args:
            protein_id: Protein identifier
            source_species: Source species NCBI taxonomy ID
            target_species: Target species NCBI taxonomy ID
            
        Returns:
            List of homologous proteins
        """
        params = {
            'identifiers': protein_id,
            'species': source_species,
            'target_species': target_species
        }
        
        response = self._make_request('json/homology', params)
        homology_data = response.json()
        
        homologs = []
        for item in homology_data:
            homologs.append({
                'source_protein': item.get('stringId_A', ''),
                'target_protein': item.get('stringId_B', ''),
                'bitscore': item.get('bitscore', 0),
                'identity': item.get('identity', 0)
            })
        
        return homologs


class IntegrationHubService:
    """
    Integration Hub Service - Unified interface for all external database adapters
    """
    
    def __init__(self, redis_client: redis.Redis, ncbi_email: str = "omniscope@example.com",
                 ncbi_api_key: Optional[str] = None):
        """
        Initialize Integration Hub with all adapters
        
        Args:
            redis_client: Redis client for caching
            ncbi_email: Email for NCBI APIs
            ncbi_api_key: Optional API key for NCBI
        """
        self.ncbi = NCBIAdapter(redis_client, ncbi_email, ncbi_api_key)
        self.uniprot = UniProtAdapter(redis_client)
        self.kegg = KEGGAdapter(redis_client)
        self.pubmed = PubMedAdapter(redis_client, ncbi_email, ncbi_api_key)
        self.string = STRINGAdapter(redis_client)
    
    def get_gene_annotation(self, gene_id: str, include_sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get comprehensive gene annotation from multiple sources
        
        Args:
            gene_id: Gene identifier
            include_sources: List of sources to include (default: all)
            
        Returns:
            Dictionary with annotations from all sources
        """
        if include_sources is None:
            include_sources = ['ncbi', 'uniprot', 'kegg', 'pubmed', 'string']
        
        annotation = {
            'gene_id': gene_id,
            'sources': {}
        }
        
        # NCBI Gene
        if 'ncbi' in include_sources:
            try:
                annotation['sources']['ncbi'] = self.ncbi.get_gene_info(gene_id)
            except Exception as e:
                logger.error(f"Failed to fetch NCBI data for {gene_id}: {e}")
                annotation['sources']['ncbi'] = {'error': str(e)}
        
        # UniProt (need to map gene to protein)
        if 'uniprot' in include_sources:
            try:
                # Search for protein by gene name
                uniprot_ids = self.uniprot.search_proteins(gene_id, max_results=1)
                if uniprot_ids:
                    annotation['sources']['uniprot'] = self.uniprot.get_protein_info(uniprot_ids[0])
            except Exception as e:
                logger.error(f"Failed to fetch UniProt data for {gene_id}: {e}")
                annotation['sources']['uniprot'] = {'error': str(e)}
        
        # KEGG Pathways
        if 'kegg' in include_sources:
            try:
                pathways = self.kegg.link_genes_to_pathways([gene_id])
                annotation['sources']['kegg'] = {
                    'pathways': pathways.get(gene_id, [])
                }
            except Exception as e:
                logger.error(f"Failed to fetch KEGG data for {gene_id}: {e}")
                annotation['sources']['kegg'] = {'error': str(e)}
        
        # PubMed Literature
        if 'pubmed' in include_sources:
            try:
                pmids = self.ncbi.link_to_pubmed(gene_id)
                annotation['sources']['pubmed'] = {
                    'paper_count': len(pmids),
                    'recent_papers': pmids[:5]  # Top 5 papers
                }
            except Exception as e:
                logger.error(f"Failed to fetch PubMed data for {gene_id}: {e}")
                annotation['sources']['pubmed'] = {'error': str(e)}
        
        # STRING Interactions
        if 'string' in include_sources:
            try:
                interactions = self.string.get_protein_interactions(gene_id)
                annotation['sources']['string'] = interactions
            except Exception as e:
                logger.error(f"Failed to fetch STRING data for {gene_id}: {e}")
                annotation['sources']['string'] = {'error': str(e)}
        
        return annotation
    
    def batch_annotate_genes(self, gene_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Annotate multiple genes efficiently
        
        Args:
            gene_ids: List of gene identifiers
            
        Returns:
            Dictionary mapping gene IDs to annotations
        """
        results = {}
        
        for gene_id in gene_ids:
            results[gene_id] = self.get_gene_annotation(gene_id)
        
        return results
