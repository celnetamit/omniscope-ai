"""
Redis cache configuration and utilities for OmniScope AI.
Provides connection pooling, key naming conventions, and TTL policies.
"""

import redis
from redis.connection import ConnectionPool
from typing import Optional, Any, Dict
import json
import os
from datetime import timedelta


class RedisCache:
    """Redis cache manager with connection pooling and standardized key naming."""
    
    # TTL policies (in seconds)
    TTL_POLICIES = {
        'session': 86400,           # 24 hours
        'integration_gene': 604800,  # 7 days
        'integration_pathway': 604800,  # 7 days
        'literature_paper': 2592000,  # 30 days
        'rate_limit': 60,            # 1 minute
        'temp': 3600,                # 1 hour
    }
    
    # Key prefixes for namespacing
    KEY_PREFIXES = {
        'session': 'session',
        'integration': 'integration',
        'literature': 'literature',
        'rate_limit': 'rate_limit',
        'cache': 'cache',
    }
    
    def __init__(self, host: str = None, port: int = None, db: int = 0, password: str = None):
        """
        Initialize Redis cache with connection pool.
        
        Args:
            host: Redis host (defaults to REDIS_HOST env var or 'localhost')
            port: Redis port (defaults to REDIS_PORT env var or 6379)
            db: Redis database number
            password: Redis password (defaults to REDIS_PASSWORD env var)
        """
        self.host = host or os.getenv('REDIS_HOST', 'localhost')
        self.port = port or int(os.getenv('REDIS_PORT', 6379))
        self.db = db
        self.password = password or os.getenv('REDIS_PASSWORD')
        
        # Create connection pool
        self.pool = ConnectionPool(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=True,
            max_connections=50,
            socket_timeout=5,
            socket_connect_timeout=5,
        )
        
        self.client = redis.Redis(connection_pool=self.pool)
    
    def _build_key(self, prefix: str, *parts: str) -> str:
        """
        Build a standardized cache key.
        
        Args:
            prefix: Key prefix from KEY_PREFIXES
            *parts: Additional key components
            
        Returns:
            Formatted cache key (e.g., 'integration:gene:BRCA1')
        """
        return ':'.join([prefix] + list(parts))
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis GET error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache with optional TTL.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            serialized = json.dumps(value)
            if ttl:
                return self.client.setex(key, ttl, serialized)
            else:
                return self.client.set(key, serialized)
        except Exception as e:
            print(f"Redis SET error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted, False otherwise
        """
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            print(f"Redis DELETE error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            print(f"Redis EXISTS error: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a counter.
        
        Args:
            key: Cache key
            amount: Amount to increment by
            
        Returns:
            New value after increment or None on error
        """
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            print(f"Redis INCREMENT error: {e}")
            return None
    
    def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration time for a key.
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return bool(self.client.expire(key, ttl))
        except Exception as e:
            print(f"Redis EXPIRE error: {e}")
            return False
    
    # Convenience methods for specific use cases
    
    def cache_session(self, session_id: str, data: Dict) -> bool:
        """Cache user session data."""
        key = self._build_key(self.KEY_PREFIXES['session'], session_id)
        return self.set(key, data, self.TTL_POLICIES['session'])
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get user session data."""
        key = self._build_key(self.KEY_PREFIXES['session'], session_id)
        return self.get(key)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete user session."""
        key = self._build_key(self.KEY_PREFIXES['session'], session_id)
        return self.delete(key)
    
    def cache_gene_annotation(self, gene_id: str, data: Dict) -> bool:
        """Cache gene annotation from external database."""
        key = self._build_key(self.KEY_PREFIXES['integration'], 'gene', gene_id)
        return self.set(key, data, self.TTL_POLICIES['integration_gene'])
    
    def get_gene_annotation(self, gene_id: str) -> Optional[Dict]:
        """Get cached gene annotation."""
        key = self._build_key(self.KEY_PREFIXES['integration'], 'gene', gene_id)
        return self.get(key)
    
    def cache_pathway(self, pathway_id: str, data: Dict) -> bool:
        """Cache pathway information."""
        key = self._build_key(self.KEY_PREFIXES['integration'], 'pathway', pathway_id)
        return self.set(key, data, self.TTL_POLICIES['integration_pathway'])
    
    def get_pathway(self, pathway_id: str) -> Optional[Dict]:
        """Get cached pathway information."""
        key = self._build_key(self.KEY_PREFIXES['integration'], 'pathway', pathway_id)
        return self.get(key)
    
    def cache_paper(self, pmid: str, data: Dict) -> bool:
        """Cache research paper data."""
        key = self._build_key(self.KEY_PREFIXES['literature'], 'paper', pmid)
        return self.set(key, data, self.TTL_POLICIES['literature_paper'])
    
    def get_paper(self, pmid: str) -> Optional[Dict]:
        """Get cached paper data."""
        key = self._build_key(self.KEY_PREFIXES['literature'], 'paper', pmid)
        return self.get(key)
    
    def check_rate_limit(self, user_id: str, endpoint: str, limit: int = 100) -> bool:
        """
        Check if user has exceeded rate limit for an endpoint.
        
        Args:
            user_id: User identifier
            endpoint: API endpoint
            limit: Maximum requests per minute
            
        Returns:
            True if within limit, False if exceeded
        """
        key = self._build_key(self.KEY_PREFIXES['rate_limit'], user_id, endpoint)
        
        # Get current count
        current = self.client.get(key)
        
        if current is None:
            # First request, set counter with TTL
            self.client.setex(key, self.TTL_POLICIES['rate_limit'], 1)
            return True
        
        current_count = int(current)
        if current_count >= limit:
            return False
        
        # Increment counter
        self.client.incr(key)
        return True
    
    def health_check(self) -> bool:
        """
        Check if Redis connection is healthy.
        
        Returns:
            True if Redis is accessible, False otherwise
        """
        try:
            return self.client.ping()
        except Exception as e:
            print(f"Redis health check failed: {e}")
            return False
    
    def close(self):
        """Close Redis connection pool."""
        try:
            self.pool.disconnect()
        except Exception as e:
            print(f"Error closing Redis connection: {e}")


# Global cache instance
_cache_instance: Optional[RedisCache] = None


def get_redis_cache() -> RedisCache:
    """
    Get or create global Redis cache instance.
    
    Returns:
        RedisCache instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance


def get_redis_client() -> redis.Redis:
    """
    Get raw Redis client for direct operations.
    
    Returns:
        redis.Redis client instance
    """
    cache = get_redis_cache()
    return cache.client
