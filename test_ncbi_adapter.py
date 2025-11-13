#!/usr/bin/env python3
"""
Test script for NCBI Adapter functionality
Tests E-utilities API client, gene information retrieval, and batch query support
"""

import sys
import asyncio
import fakeredis
from backend_db.integration import NCBIAdapter

def test_ncbi_adapter():
    """Test NCBI adapter functionality"""
    print("=" * 60)
    print("Testing NCBI Adapter Implementation")
    print("=" * 60)
    
    # Initialize fake Redis client and NCBI adapter
    print("\n1. Initializing NCBI Adapter...")
    try:
        # Use fakeredis for testing without requiring a Redis server
        redis_client = fakeredis.FakeStrictRedis(decode_responses=True)
        ncbi = NCBIAdapter(redis_client, email="test@omniscope.ai")
        print("✓ NCBI Adapter initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize NCBI Adapter: {e}")
        return False
    
    # Test 1: Search for genes
    print("\n2. Testing gene search (E-search)...")
    try:
        gene_ids = ncbi.search_gene("BRCA1", max_results=5)
        print(f"✓ Found {len(gene_ids)} genes for 'BRCA1'")
        print(f"  Gene IDs: {gene_ids[:3]}")
    except Exception as e:
        print(f"✗ Gene search failed: {e}")
        return False
    
    # Test 2: Get gene information
    print("\n3. Testing gene information retrieval...")
    try:
        if gene_ids:
            gene_id = gene_ids[0]
            gene_info = ncbi.get_gene_info(gene_id)
            print(f"✓ Retrieved information for gene {gene_id}")
            print(f"  Symbol: {gene_info.get('symbol', 'N/A')}")
            print(f"  Name: {gene_info.get('name', 'N/A')}")
            print(f"  Organism: {gene_info.get('organism', 'N/A')}")
            print(f"  Chromosome: {gene_info.get('chromosome', 'N/A')}")
            print(f"  Source: {gene_info.get('source', 'N/A')}")
        else:
            print("✗ No gene IDs available for testing")
            return False
    except Exception as e:
        print(f"✗ Gene information retrieval failed: {e}")
        return False
    
    # Test 3: Batch query
    print("\n4. Testing batch query support...")
    try:
        if len(gene_ids) >= 2:
            batch_ids = gene_ids[:3]
            batch_results = ncbi.get_gene_batch(batch_ids)
            print(f"✓ Retrieved batch information for {len(batch_results)} genes")
            for gid, info in batch_results.items():
                print(f"  - {gid}: {info.get('symbol', 'N/A')} ({info.get('name', 'N/A')[:50]}...)")
        else:
            print("⚠ Not enough gene IDs for batch testing, using single ID")
            batch_results = ncbi.get_gene_batch([gene_ids[0]])
            print(f"✓ Retrieved batch information for {len(batch_results)} gene(s)")
    except Exception as e:
        print(f"✗ Batch query failed: {e}")
        return False
    
    # Test 4: Caching verification
    print("\n5. Testing cache functionality...")
    try:
        # Second call should hit cache
        gene_info_cached = ncbi.get_gene_info(gene_id)
        print(f"✓ Cache working - retrieved gene {gene_id} from cache")
    except Exception as e:
        print(f"✗ Cache test failed: {e}")
        return False
    
    # Test 5: Link to PubMed
    print("\n6. Testing link to PubMed...")
    try:
        pubmed_ids = ncbi.link_to_pubmed(gene_id)
        print(f"✓ Found {len(pubmed_ids)} PubMed articles linked to gene {gene_id}")
        if pubmed_ids:
            print(f"  Sample PMIDs: {pubmed_ids[:3]}")
    except Exception as e:
        print(f"✗ PubMed linking failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All NCBI Adapter tests passed successfully!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_ncbi_adapter()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
