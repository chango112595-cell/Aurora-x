"""
Aurora Redis Cache Manager
Centralized caching layer for performance optimization
"""

import pickle
from collections.abc import Callable
from functools import wraps
from typing import Any

try:
    import redis
    from redis.asyncio import Redis as AsyncRedis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from cachetools import LRUCache, TTLCache


class CacheManager:
    """
    Unified cache manager supporting both Redis and in-memory caching.
    Falls back to in-memory cache if Redis is unavailable.
    """

    def __init__(
        """
              Init  
            
            Args:
                redis_url: redis url
                default_ttl: default ttl
                max_memory_items: max memory items
            """
        self,
        redis_url: str = "redis://localhost:6379/0",
        default_ttl: int = 300,  # 5 minutes
        max_memory_items: int = 1000,
    ):
        self.default_ttl = default_ttl
        self.redis_url = redis_url
        self.redis_client: redis.Redis | None = None
        self.async_redis_client: AsyncRedis | None = None

        # In-memory cache as fallback
        self.memory_cache = TTLCache(maxsize=max_memory_items, ttl=default_ttl)
        self.lru_cache = LRUCache(maxsize=max_memory_items)

        # Try to connect to Redis
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=False, socket_connect_timeout=2)
                # Test connection
                self.redis_client.ping()
                self.using_redis = True
            except Exception as e:
                print(f"Aurora Warning: Redis not available, using in-memory cache: {e}")
                self.using_redis = False
        else:
            print("Aurora Warning: Redis library not installed, using in-memory cache")
            self.using_redis = False

    def get(self, key: str) -> Any | None:
        """Get value from cache."""
        try:
            if self.using_redis and self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return pickle.loads(value)
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            print(f"Aurora Cache Error (get): {e}")
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache with optional TTL."""
        try:
            ttl = ttl or self.default_ttl

            if self.using_redis and self.redis_client:
                serialized = pickle.dumps(value)
                return self.redis_client.setex(key, ttl, serialized)
            else:
                self.memory_cache[key] = value
                return True
        except Exception as e:
            print(f"Aurora Cache Error (set): {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if self.using_redis and self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                return True
        except Exception as e:
            print(f"Aurora Cache Error (delete): {e}")
            return False

    def clear(self, pattern: str | None = None) -> int:
        """Clear cache entries matching pattern."""
        try:
            if self.using_redis and self.redis_client:
                if pattern:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        return self.redis_client.delete(*keys)
                    return 0
                else:
                    return self.redis_client.flushdb()
            else:
                count = len(self.memory_cache)
                self.memory_cache.clear()
                return count
        except Exception as e:
            print(f"Aurora Cache Error (clear): {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            if self.using_redis and self.redis_client:
                return bool(self.redis_client.exists(key))
            else:
                return key in self.memory_cache
        except Exception as e:
            print(f"Aurora Cache Error (exists): {e}")
            return False

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        try:
            if self.using_redis and self.redis_client:
                info = self.redis_client.info("stats")
                return {
                    "type": "redis",
                    "total_keys": self.redis_client.dbsize(),
                    "hits": info.get("keyspace_hits", 0),
                    "misses": info.get("keyspace_misses", 0),
                    "hit_rate": self._calculate_hit_rate(info.get("keyspace_hits", 0), info.get("keyspace_misses", 0)),
                }
            else:
                return {
                    "type": "memory",
                    "total_keys": len(self.memory_cache),
                    "max_size": self.memory_cache.maxsize,
                    "ttl": self.memory_cache.ttl,
                }
        except Exception as e:
            print(f"Aurora Cache Error (stats): {e}")
            return {"type": "unknown", "error": str(e)}

    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage."""
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0


# Global cache manager instance
_cache_manager: CacheManager | None = None


def get_cache() -> CacheManager:
    """Get or create global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results.

    Args:
        ttl: Time to live in seconds (default: 300)
        key_prefix: Prefix for cache key (default: function name)

    Example:
        @cached(ttl=600, key_prefix="user")
        def get_user(user_id: int):
            return fetch_user_from_db(user_id)
    """

    def decorator(func: Callable) -> Callable:
        """
            Decorator
            
            Args:
                func: func
        
            Returns:
                Result of operation
            """
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
                Wrapper
                
                Returns:
                    Result of operation
                """
            cache = get_cache()

            # Build cache key
            prefix = key_prefix or func.__name__
            key_parts = [str(arg) for arg in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
            cache_key = f"{prefix}:{':'.join(key_parts)}"

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            return result

        # Add cache control methods
        wrapper.cache_clear = lambda: get_cache().clear(f"{key_prefix or func.__name__}:*")
        wrapper.cache_info = lambda: get_cache().get_stats()

        return wrapper

    return decorator


def invalidate_cache(pattern: str):
    """Invalidate cache entries matching pattern."""
    cache = get_cache()
    return cache.clear(pattern)


# Export public API
__all__ = [
    "CacheManager",
    "get_cache",
    "cached",
    "invalidate_cache",
]
