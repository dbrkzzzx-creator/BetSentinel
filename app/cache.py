"""
Caching module for odds data to reduce API calls
"""
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from cachetools import TTLCache
import hashlib

# Cache for odds data (TTL: 30 seconds)
odds_cache = TTLCache(maxsize=100, ttl=30)

def get_cache_key(url, params):
    """Generate cache key from URL and parameters"""
    key_data = f"{url}_{json.dumps(params, sort_keys=True)}"
    return hashlib.md5(key_data.encode()).hexdigest()

def get_cached_odds(url, params):
    """Get cached odds if available and not expired"""
    cache_key = get_cache_key(url, params)
    return odds_cache.get(cache_key)

def cache_odds(url, params, data):
    """Cache odds data"""
    cache_key = get_cache_key(url, params)
    odds_cache[cache_key] = {
        'data': data,
        'timestamp': datetime.now().isoformat()
    }

def is_cache_valid(url, params, max_age_seconds=30):
    """Check if cached data is still valid"""
    cache_key = get_cache_key(url, params)
    cached = odds_cache.get(cache_key)
    if not cached:
        return False
    
    cached_time = datetime.fromisoformat(cached['timestamp'])
    age = (datetime.now() - cached_time).total_seconds()
    return age < max_age_seconds

