"""Knowledge Cache - Phase 6.9 Part 2 Section 18.

This module implements the canonical contract for caching in Knowledge Services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# CACHE INVALIDATION POLICY - Phase 6.9 Part 2 Section 18
# =============================================================================


class InvalidationPolicy(Enum):
    """
    Cache invalidation policies.
    
    Per CACHE-LAW-003: Cache invalidation policies shall remain explicit.
    
    Types:
        NONE          -> Never invalidate (read-only)
        LRU           -> Least Recently Used
        TTL           -> Time-To-Live based
        EXPLICIT      -> Manual/instruction-based
        STALE         -> Based on staleness detection
    """
    
    NONE = "none"
    LRU = "lru"
    TTL = "ttl"
    EXPLICIT = "explicit"
    STALE = "stale"


# =============================================================================
# FRESHNESS POLICY - Phase 6.9 Part 2 Section 18
# =============================================================================


class FreshnessPolicy(Enum):
    """
    Cache freshness policies.
    
    Per CACHE-LAW-004: Cache freshness shall remain explicit.
    
    Types:
        STRICT        -> Always require fresh data
        ACCEPTABLE    -> Accept slightly stale data
        RELAXED       -> Allow significantly stale data
    """
    
    STRICT = "strict"
    ACCEPTABLE = "acceptable"
    RELAXED = "relaxed"


# =============================================================================
# KNOWLEDGE CACHE - Phase 6.9 Part 2 Section 18
# =============================================================================


@dataclass(frozen=True)
class KnowledgeCache:
    """
    Cache for knowledge service results.
    
    Per CACHE-LAW-001: Caches shall remain auxiliary structures.
    Per CACHE-LAW-007: Cache contents shall remain independently inspectable.
    
    Fields:
        cache_identity: Unique identifier for this cache
        cached_artifacts: Artifacts currently in the cache
        
    Invariants:
        * Caches are auxiliary (not canonical authority - CACHE-LAW-002)
        * Invalidations are explicit (CACHE-LAW-003)
        * Freshness is tracked (CACHE-LAW-004)
        * Provenance is complete (CACHE-LAW-005)
    """
    
    cache_identity: str  # Unique identifier
    
    cached_artifacts: Dict[str, Any] = field(default_factory=dict)
    
    # Invalidation policy (Per CACHE-LAW-003)
    invalidation_policy: InvalidationPolicy = InvalidationPolicy.LRU
    
    # Freshness policy (Per CACHE-LAW-004)
    freshness_policy: FreshnessPolicy = FreshnessPolicy.STRICT
    
    # Cache statistics
    hit_count: int = 0
    miss_count: int = 0
    
    # Provenance (Per CACHE-LAW-005)
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    def __post_init__(self) -> None:
        """Validate cache after creation."""
        if not self.cache_identity:
            raise ValueError("cache_identity cannot be empty")
    
    @property
    def size(self) -> int:
        """Number of cached artifacts."""
        return len(self.cached_artifacts)
    
    @property
    def hit_rate(self) -> float:
        """Cache hit rate (0.0 - 1.0)."""
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0.0
        return self.hit_count / total
    
    @classmethod
    def create_initial(
        cls,
        policy: InvalidationPolicy = InvalidationPolicy.LRU,
        freshness: FreshnessPolicy = FreshnessPolicy.STRICT,
    ) -> "KnowledgeCache":
        """
        Create initial knowledge cache.
        
        Args:
            policy: Invalidations policy to use
            freshness: Freshness policy to use
            
        Returns:
            New KnowledgeCache with empty contents
        """
        return cls(
            cache_identity=f"cache:{uuid.uuid4().hex[:16]}",
            invalidation_policy=policy,
            freshness_policy=freshness,
            provenance=(
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": "Knowledge cache initialization",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ),
        )
    
    def add_entry(
        self,
        key: str,
        value: Any,
    ) -> "KnowledgeCache":
        """Add an entry to the cache."""
        new_cache = dict(self.cached_artifacts)
        new_cache[key] = value
        
        return KnowledgeCache(
            cache_identity=self.cache_identity,
            cached_artifacts=new_cache,
            invalidation_policy=self.invalidation_policy,
            freshness_policy=self.freshness_policy,
            hit_count=self.hit_count,
            miss_count=self.miss_count,
            provenance=tuple(list(self.provenance) + [
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": f"Cache add: {key}",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ]),
        )
    
    def get_entry(
        self,
        key: str,
    ) -> Tuple[Optional[Any], bool]:
        """
        Get an entry from the cache.
        
        Returns:
            Tuple of (value, was_hit) - value is None if not found
        """
        value = self.cached_artifacts.get(key)
        was_hit = value is not None
        
        # Update statistics
        return value, was_hit
    
    def invalidate(self, key: str) -> "KnowledgeCache":
        """Remove an entry from the cache."""
        new_cache = dict(self.cached_artifacts)
        if key in new_cache:
            del new_cache[key]
        
        return KnowledgeCache(
            cache_identity=self.cache_identity,
            cached_artifacts=new_cache,
            invalidation_policy=self.invalidation_policy,
            freshness_policy=self.freshness_policy,
            hit_count=self.hit_count,
            miss_count=self.miss_count,
            provenance=tuple(list(self.provenance) + [
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": f"Cache invalidate: {key}",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ]),
        )
    
    def clear(self) -> "KnowledgeCache":
        """Clear all entries from the cache."""
        return KnowledgeCache(
            cache_identity=self.cache_identity,
            cached_artifacts={},
            invalidation_policy=self.invalidation_policy,
            freshness_policy=self.freshness_policy,
            hit_count=0,
            miss_count=0,
            provenance=tuple(list(self.provenance) + [
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": "Cache clear",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ]),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cache to dictionary."""
        return {
            "cache_identity": self.cache_identity,
            "cached_artifacts": dict(self.cached_artifacts),
            "invalidation_policy": self.invalidation_policy.value,
            "freshness_policy": self.freshness_policy.value,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "provenance": list(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeCache":
        """Create cache from dictionary."""
        return cls(
            cache_identity=data.get("cache_identity", str(uuid.uuid4())),
            cached_artifacts=dict(data.get("cached_artifacts", {})),
            invalidation_policy=InvalidationPolicy(data.get("invalidation_policy", "lru")),
            freshness_policy=FreshnessPolicy(data.get("freshness_policy", "strict")),
            hit_count=int(data.get("hit_count", 0)),
            miss_count=int(data.get("miss_count", 0)),
            provenance=tuple(data.get("provenance", [])),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Invalidation policies (Part 2 Section 18)
    "InvalidationPolicy",
    # Freshness policies (Part 2 Section 18)
    "FreshnessPolicy",
    # Knowledge cache
    "KnowledgeCache",
]