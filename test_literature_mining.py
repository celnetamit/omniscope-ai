"""
Test script for Literature Mining System
Tests basic functionality of PubMed fetching, NLP pipeline, and summarization
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pubmed_fetcher():
    """Test PubMed fetcher functionality"""
    print("\n" + "="*80)
    print("TEST 1: PubMed Fetcher")
    print("="*80)
    
    try:
        import redis
        from backend_db.literature_mining import PubMedFetcher
        
        # Initialize Redis client
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Test connection
        redis_client.ping()
        print("✓ Redis connection successful")
        
        # Initialize PubMed fetcher
        fetcher = PubMedFetcher(redis_client, email="test@example.com")
        print("✓ PubMed fetcher initialized")
        
        # Test paper search
        print("\nSearching for papers on 'BRCA1 breast cancer'...")
        pmids = fetcher.search_papers("BRCA1 breast cancer", max_results=3)
        print(f"✓ Found {len(pmids)} papers: {pmids}")
        
        # Test getting paper info
        if pmids:
            print(f"\nFetching details for paper {pmids[0]}...")
            paper = fetcher.get_paper_info(pmids[0])
            print(f"✓ Paper title: {paper.get('title', 'N/A')[:100]}...")
            print(f"✓ Authors: {len(paper.get('authors', []))} authors")
            print(f"✓ Year: {paper.get('year', 'N/A')}")
            print(f"✓ Abstract length: {len(paper.get('abstract', ''))} characters")
        
        # Test batch retrieval
        if len(pmids) > 1:
            print(f"\nFetching batch of {len(pmids)} papers...")
            papers_dict = fetcher.get_papers_batch(pmids)
            print(f"✓ Retrieved {len(papers_dict)} papers in batch")
        
        print("\n✅ PubMed Fetcher tests PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ PubMed Fetcher tests FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_nlp_pipeline():
    """Test NLP pipeline functionality"""
    print("\n" + "="*80)
    print("TEST 2: NLP Pipeline")
    print("="*80)
    
    try:
        from backend_db.literature_mining import NLPPipeline
        
        # Initialize NLP pipeline
        nlp = NLPPipeline()
        print("✓ NLP pipeline initialized")
        
        # Test entity extraction
        test_text = "BRCA1 mutations are associated with breast cancer and ovarian cancer. Patients may be treated with cisplatin or olaparib."
        print(f"\nTest text: {test_text}")
        
        print("\nExtracting entities...")
        entities = nlp.extract_entities(test_text)
        print(f"✓ Found {len(entities)} entities:")
        for entity in entities[:5]:  # Show first 5
            print(f"  - {entity['text']} ({entity['type']}, confidence: {entity['confidence']:.2f})")
        
        # Test relationship extraction
        print("\nExtracting relationships...")
        relationships = nlp.extract_relationships(test_text, entities)
        print(f"✓ Found {len(relationships)} relationships:")
        for rel in relationships[:3]:  # Show first 3
            print(f"  - {rel['source']['text']} --[{rel['type']}]--> {rel['target']['text']}")
        
        print("\n✅ NLP Pipeline tests PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ NLP Pipeline tests FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_summarizer():
    """Test paper summarization functionality"""
    print("\n" + "="*80)
    print("TEST 3: Paper Summarizer")
    print("="*80)
    
    try:
        from backend_db.literature_mining import PaperSummarizer
        
        # Initialize summarizer
        summarizer = PaperSummarizer()
        print("✓ Summarizer initialized")
        
        # Test summarization
        test_abstract = """
        BRCA1 is a human tumor suppressor gene that plays a critical role in DNA repair, 
        cell cycle checkpoint control, and maintenance of genomic stability. Mutations in 
        BRCA1 are associated with increased risk of breast and ovarian cancers. The protein 
        encoded by this gene is involved in homologous recombination repair of DNA double-strand 
        breaks. Loss of BRCA1 function leads to accumulation of DNA damage and genomic instability, 
        which can contribute to cancer development. Understanding BRCA1 function is important for 
        developing targeted therapies for BRCA1-mutated cancers.
        """
        
        print("\nSummarizing text...")
        result = summarizer.summarize(test_abstract, max_length=100)
        print(f"✓ Summary generated using {result['method']} method")
        print(f"✓ Quality score: {result['quality_score']:.2f}")
        print(f"✓ Summary: {result['summary'][:200]}...")
        
        print("\n✅ Summarizer tests PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Summarizer tests FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_paper_ranker():
    """Test paper ranking functionality"""
    print("\n" + "="*80)
    print("TEST 4: Paper Ranker")
    print("="*80)
    
    try:
        from backend_db.literature_mining import PaperRanker
        
        # Initialize ranker
        ranker = PaperRanker()
        print("✓ Paper ranker initialized")
        
        # Create test papers
        test_papers = [
            {
                'pmid': '1',
                'title': 'BRCA1 and DNA repair',
                'abstract': 'BRCA1 plays a role in DNA repair mechanisms.',
                'citations': 100,
                'year': 2020
            },
            {
                'pmid': '2',
                'title': 'Breast cancer genetics',
                'abstract': 'Genetic factors in breast cancer development.',
                'citations': 50,
                'year': 2022
            },
            {
                'pmid': '3',
                'title': 'BRCA1 mutations',
                'abstract': 'BRCA1 mutations increase cancer risk.',
                'citations': 200,
                'year': 2018
            }
        ]
        
        print("\nRanking papers...")
        ranked_papers = ranker.rank_papers(test_papers, query="BRCA1 DNA repair")
        print(f"✓ Ranked {len(ranked_papers)} papers")
        
        print("\nRanked order:")
        for i, paper in enumerate(ranked_papers, 1):
            print(f"  {i}. PMID {paper['pmid']}: {paper['title']}")
            print(f"     Relevance score: {paper['relevance_score']:.3f}")
        
        print("\n✅ Paper Ranker tests PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Paper Ranker tests FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_notification_system():
    """Test notification system functionality"""
    print("\n" + "="*80)
    print("TEST 5: Notification System")
    print("="*80)
    
    try:
        import redis
        from backend_db.literature_mining import NotificationSystem
        
        # Initialize Redis client
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Initialize notification system
        notif_system = NotificationSystem(redis_client)
        print("✓ Notification system initialized")
        
        # Test subscription
        user_id = "test_user_123"
        topics = ["BRCA1", "breast cancer"]
        email = "test@example.com"
        
        print(f"\nSubscribing user {user_id} to topics: {topics}")
        notif_system.subscribe_user(user_id, topics, email)
        print("✓ User subscribed")
        
        # Test getting subscriptions
        print("\nRetrieving subscriptions...")
        subscriptions = notif_system.get_user_subscriptions(user_id)
        print(f"✓ User subscribed to {len(subscriptions['topics'])} topics")
        print(f"  Topics: {subscriptions['topics']}")
        
        # Test unsubscribe
        print("\nUnsubscribing from topics...")
        notif_system.unsubscribe_user(user_id, topics)
        print("✓ User unsubscribed")
        
        print("\n✅ Notification System tests PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Notification System tests FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("LITERATURE MINING SYSTEM - TEST SUITE")
    print("="*80)
    
    results = []
    
    # Run tests
    results.append(("PubMed Fetcher", test_pubmed_fetcher()))
    results.append(("NLP Pipeline", test_nlp_pipeline()))
    results.append(("Summarizer", test_summarizer()))
    results.append(("Paper Ranker", test_paper_ranker()))
    results.append(("Notification System", test_notification_system()))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
