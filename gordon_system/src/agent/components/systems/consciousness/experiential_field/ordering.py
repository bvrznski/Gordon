# Gordon Phase 5.7.2-I: Experiential Field Deterministic Ordering
# ===============================================================================
#
# Deterministic ordering for field construction.
#

"""
Deterministic ordering module for Experiential Field Builder.

This module provides deterministic ordering of contributions and content items:
    - Stable sorting keys based on priority, freshness, source identity
    - Tie-breaking rules for equivalent inputs
    - Order preservation for determinism guarantees
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass(frozen=True)
class OrderingKey:
    """
    A key used for deterministic ordering.
    
    The ordering key is computed from contribution properties to ensure
    that equivalent inputs produce identically ordered results.
    """
    
    priority_class: int = 0
    """Priority class (lower = higher priority)."""
    
    freshness_utc: float = 0.0
    """Contribution creation timestamp."""
    
    source_id_hash: str = ""
    """Hash of source ID for consistent ordering across sources."""
    
    contribution_id: str = ""
    """Unique contribution ID for final tie-breaking."""
    
    def __lt__(self, other: "OrderingKey") -> bool:
        """
        Compare two ordering keys.
        
        Ordering priority:
            1. Lower priority class first
            2. Fresher contributions first (higher timestamp)
            3. Lower source_id hash lexicographically
            4. Lower contribution_id lexicographically
        """
        if self.priority_class != other.priority_class:
            return self.priority_class < other.priority_class
        
        # Fresher comes first (higher timestamp = more recent)
        if self.freshness_utc != other.freshness_utc:
            return self.freshness_utc > other.freshness_utc
        
        if self.source_id_hash != other.source_id_hash:
            return self.source_id_hash < other.source_id_hash
        
        return self.contribution_id < other.contribution_id


@dataclass
class DeterministicOrderer:
    """
    Provides deterministic ordering for contributions and content items.
    
    This orderer ensures that given the same set of inputs, the output
    is always in the same order, enabling reproducibility and testing.
    """
    
    # Configuration
    default_priority_class: int = 0
    """Default priority class when not specified."""
    
    def compute_ordering_key(self, content_kind: str, freshness_utc: float, source_id: str, contribution_id: str) -> OrderingKey:
        """
        Compute an ordering key from contribution properties.
        
        Args:
            content_kind: Kind of content (affects priority)
            freshness_utc: When contribution was created
            source_id: Source that submitted the contribution
            contribution_id: Unique ID of the contribution
            
        Returns:
            An OrderingKey for deterministic sorting
        """
        # Map kind to priority class (lower number = higher priority)
        kind_priority_map: dict[str, int] = {
            "workspace": 0,
            "perceptual": 1,
            "memory": 2,
            "working_memory": 3,
            "salience": 4,
            "attention": 5,
            "personality": 6,
            "motivation": 7,
            "cognition": 8,
            "action_feedback": 9,
        }
        
        priority = kind_priority_map.get(content_kind, self.default_priority_class)
        
        # Compute a consistent hash for source_id
        source_hash = str(hash(source_id))
        
        return OrderingKey(
            priority_class=priority,
            freshness_utc=freshness_utc,
            source_id_hash=source_hash,
            contribution_id=contribution_id,
        )
    
    def sort_content(self, content_items: List[Tuple[str, float, str, str]]) -> List[Tuple[OrderingKey, Tuple[str, float, str, str]]]:
        """
        Sort content items deterministically.
        
        Args:
            content_items: List of (kind, freshness_utc, source_id, contribution_id) tuples
            
        Returns:
            Sorted list of (ordering_key, original_tuple) pairs
        """
        keyed_items = [
            (self.compute_ordering_key(*item), item)
            for item in content_items
        ]
        
        # Sort by ordering key
        keyed_items.sort(key=lambda x: x[0])
        
        return keyed_items
    
    def sort_contributions(
        self,
        contributions: List[Tuple[str, float, str, str, int]]
    ) -> List[Tuple[OrderingKey, Tuple[str, float, str, str, int]]]:
        """
        Sort contribution tuples deterministically.
        
        Args:
            contributions: List of (kind, freshness_utc, source_id, contribution_id, priority_class) tuples
            
        Returns:
            Sorted list of (ordering_key, original_tuple) pairs
        """
        # Build items with kind_priority from the mapping
        def make_key(c: Tuple[str, float, str, str, int]) -> OrderingKey:
            kind, freshness_utc, source_id, contrib_id, _ = c
            return self.compute_ordering_key(kind, freshness_utc, source_id, contrib_id)
        
        keyed_items = [(make_key(item), item) for item in contributions]
        keyed_items.sort(key=lambda x: x[0])
        
        return keyed_items


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "OrderingKey",
    "DeterministicOrderer",
)
