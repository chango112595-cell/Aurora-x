"""
Intelligent Caching System
Self-contained multi-level intelligent caching with semantic cache and predictive preloading
No external APIs - uses semantic similarity, access patterns, and predictive algorithms
"""

from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from ..utils.local_embeddings import cosine_similarity, generate_embedding


class CacheLevel(Enum):
    """Cache levels"""

    L1 = "l1"  # Hot cache - most frequently accessed
    L2 = "l2"  # Warm cache - moderately accessed
    L3 = "l3"  # Cold cache - rarely accessed


@dataclass
class CacheEntry:
    """A cache entry"""

    key: str
    value: Any
    semantic_key: list[float] | None  # Semantic embedding
    access_count: int
    last_accessed: datetime
    created_at: datetime
    ttl_seconds: int | None
    cache_level: CacheLevel


class IntelligentCache:
    """
    Self-contained intelligent caching system
    Multi-level caching with semantic similarity and predictive preloading
    """

    def __init__(self, max_size_l1: int = 1000, max_size_l2: int = 5000, max_size_l3: int = 10000):
        self.max_size_l1 = max_size_l1
        self.max_size_l2 = max_size_l2
        self.max_size_l3 = max_size_l3

        # Multi-level caches
        self.l1_cache: OrderedDict[str, CacheEntry] = OrderedDict()  # Hot
        self.l2_cache: OrderedDict[str, CacheEntry] = OrderedDict()  # Warm
        self.l3_cache: OrderedDict[str, CacheEntry] = OrderedDict()  # Cold

        # Semantic cache index
        self.semantic_index: dict[str, list[float]] = {}  # key -> embedding

        # Access patterns for prediction
        self.access_patterns: list[tuple[str, datetime]] = []
        self.prediction_window = timedelta(minutes=5)

    def get(self, key: str, semantic_query: str | None = None) -> Any | None:
        """Get value from cache (with semantic fallback)"""
        # Try exact match first
        entry = self._get_exact(key)
        if entry:
            self._promote_entry(entry)
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            return entry.value

        # Try semantic match if semantic query provided
        if semantic_query:
            entry = self._get_semantic(semantic_query)
            if entry:
                self._promote_entry(entry)
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                return entry.value

        return None

    def _get_exact(self, key: str) -> CacheEntry | None:
        """Get entry by exact key"""
        # Check L1
        if key in self.l1_cache:
            return self.l1_cache[key]

        # Check L2
        if key in self.l2_cache:
            return self.l2_cache[key]

        # Check L3
        if key in self.l3_cache:
            return self.l3_cache[key]

        return None

    def _get_semantic(self, semantic_query: str) -> CacheEntry | None:
        """Get entry by semantic similarity"""
        query_embedding = generate_embedding(semantic_query)
        best_match = None
        best_similarity = 0.0

        # Search all caches
        for cache in [self.l1_cache, self.l2_cache, self.l3_cache]:
            for entry in cache.values():
                if entry.semantic_key:
                    similarity = cosine_similarity(query_embedding, entry.semantic_key)
                    if similarity > best_similarity and similarity > 0.7:  # Threshold
                        best_similarity = similarity
                        best_match = entry

        return best_match

    def set(
        self,
        key: str,
        value: Any,
        semantic_key: str | None = None,
        ttl_seconds: int | None = None,
    ):
        """Set value in cache"""
        # Generate semantic embedding if provided
        semantic_embedding = None
        if semantic_key:
            semantic_embedding = generate_embedding(semantic_key)

        # Create cache entry
        entry = CacheEntry(
            key=key,
            value=value,
            semantic_key=semantic_embedding,
            access_count=1,
            last_accessed=datetime.now(),
            created_at=datetime.now(),
            ttl_seconds=ttl_seconds,
            cache_level=CacheLevel.L1,  # Start in L1
        )

        # Store semantic index
        if semantic_embedding:
            self.semantic_index[key] = semantic_embedding

        # Add to L1 cache
        self.l1_cache[key] = entry
        self.l1_cache.move_to_end(key)  # Move to end (most recent)

        # Evict if needed
        self._evict_if_needed()

        # Record access pattern
        self.access_patterns.append((key, datetime.now()))
        if len(self.access_patterns) > 10000:
            self.access_patterns = self.access_patterns[-10000:]

    def _promote_entry(self, entry: CacheEntry):
        """Promote entry to higher cache level"""
        # Remove from current level
        if entry.key in self.l1_cache:
            del self.l1_cache[entry.key]
        elif entry.key in self.l2_cache:
            del self.l2_cache[entry.key]
        elif entry.key in self.l3_cache:
            del self.l3_cache[entry.key]

        # Promote based on access count
        if entry.access_count >= 10:
            entry.cache_level = CacheLevel.L1
            self.l1_cache[entry.key] = entry
        elif entry.access_count >= 5:
            entry.cache_level = CacheLevel.L2
            self.l2_cache[entry.key] = entry
        else:
            entry.cache_level = CacheLevel.L3
            self.l3_cache[entry.key] = entry

    def _evict_if_needed(self):
        """Evict entries if cache is full"""
        # Evict from L1 if needed
        while len(self.l1_cache) > self.max_size_l1:
            oldest_key = next(iter(self.l1_cache))
            entry = self.l1_cache.pop(oldest_key)
            # Move to L2
            entry.cache_level = CacheLevel.L2
            self.l2_cache[oldest_key] = entry

        # Evict from L2 if needed
        while len(self.l2_cache) > self.max_size_l2:
            oldest_key = next(iter(self.l2_cache))
            entry = self.l2_cache.pop(oldest_key)
            # Move to L3
            entry.cache_level = CacheLevel.L3
            self.l3_cache[oldest_key] = entry

        # Evict from L3 if needed
        while len(self.l3_cache) > self.max_size_l3:
            oldest_key = next(iter(self.l3_cache))
            del self.l3_cache[oldest_key]
            if oldest_key in self.semantic_index:
                del self.semantic_index[oldest_key]

    def predict_and_preload(self, current_keys: list[str]):
        """Predict and preload likely-to-be-accessed entries"""
        # Analyze access patterns
        recent_patterns = [
            key for key, timestamp in self.access_patterns if datetime.now() - timestamp < self.prediction_window
        ]

        # Find frequently co-accessed keys
        co_access_map: dict[str, int] = {}
        for i, key1 in enumerate(recent_patterns):
            for key2 in recent_patterns[i + 1 : i + 5]:  # Next 4 accesses
                pair = (key1, key2)
                co_access_map[pair] = co_access_map.get(pair, 0) + 1

        # Preload frequently co-accessed entries
        for (_key1, key2), count in co_access_map.items():
            if count >= 3 and key2 not in self.l1_cache:  # Preload threshold
                entry = self._get_exact(key2)
                if entry:
                    self._promote_entry(entry)

    def invalidate(self, key: str):
        """Invalidate cache entry"""
        if key in self.l1_cache:
            del self.l1_cache[key]
        if key in self.l2_cache:
            del self.l2_cache[key]
        if key in self.l3_cache:
            del self.l3_cache[key]
        if key in self.semantic_index:
            del self.semantic_index[key]

    def clear(self):
        """Clear all caches"""
        self.l1_cache.clear()
        self.l2_cache.clear()
        self.l3_cache.clear()
        self.semantic_index.clear()
        self.access_patterns.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        return {
            "l1_size": len(self.l1_cache),
            "l2_size": len(self.l2_cache),
            "l3_size": len(self.l3_cache),
            "total_entries": len(self.l1_cache) + len(self.l2_cache) + len(self.l3_cache),
            "semantic_index_size": len(self.semantic_index),
            "access_patterns": len(self.access_patterns),
        }
