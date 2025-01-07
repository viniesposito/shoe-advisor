from pathlib import Path
import hashlib
import time
import pickle
import logging

class QueryCache:
    def __init__(self, cache_dir: str = 'query_cache', ttl_days: int = 30):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl_seconds = ttl_days * 24 * 60 * 60
        logging.debug(f"Cache initialized at {self.cache_dir}")
        
    def _get_cache_key(self, query: str) -> str:
        """Create deterministic cache key from query"""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def _is_valid(self, timestamp: float) -> bool:
        """Check if cached item is still valid"""
        return (time.time() - timestamp) < self.ttl_seconds
    
    def get(self, query: str) -> dict:
        """Get cached response if it exists and is valid"""
        cache_key = self._get_cache_key(query)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        logging.debug(f"Looking for cache file: {cache_file}")
        
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                if self._is_valid(cached_data['timestamp']):
                    logging.debug("Cache hit!")
                    return cached_data['response']
                else:
                    logging.debug("Cache expired")
                    cache_file.unlink()  # Remove expired cache
        logging.debug("Cache miss")
        return None
    
    def set(self, query: str, response: dict):
        """Cache a response"""
        cache_key = self._get_cache_key(query)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        cache_data = {
            'timestamp': time.time(),
            'response': response
        }
        
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        logging.debug(f"Cached response at {cache_file}")