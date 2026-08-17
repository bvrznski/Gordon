# Pattern Search - Phase 7.2
# ===========================

"""
Canonical Pattern Search Contract.

Pattern Discovery discovers regularities, clusters, and relationships.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class PatternSearchStrategy(Enum):
    """Strategies for pattern discovery."""
    
    FREQUENCY_ANALYSIS = "frequency_analysis"           # Count occurrences
    CORRELATION_DISCOVERY = "correlation_discovery"     # Find statistical associations
    CLUSTER_DETECTION = "cluster_detection"             # Group similar items
    SEQUENCE_ANALYSIS = "sequence_analysis"             # Analyze ordered patterns
    TEMPORAL_PATTERN = "temporal_pattern"               # Time-based patterns
    CO_OCCURRENCE = "co_occurrence"                     # Joint occurrences
    DEPENDENCY_GRAPH = "dependency_graph"               # Causal/functional dependencies


@dataclass(frozen=True)
class PatternCandidate:
    """
    Candidate pattern discovered during analysis.
    
    Each pattern records:
        - The observations that support it
        - Support measure (how many observations match)
        - Confidence in the pattern
        - Provenance tracking
    
    Patterns remain candidates until validated.
    """
    
    # Identity
    pattern_identity: str                 # Unique identifier for this pattern
    
    # Participation
    supporting_observations: Tuple[str, ...]  # Observation IDs supporting this pattern
    
    # Pattern content (descriptive)
    pattern_description: str              # Human-readable description
    pattern_kind: str                     # e.g., "temporal_sequence", "correlation"
    
    # Support metrics
    support_measure: float = 0.0          # Number or proportion of observations matching
    coverage: float = 0.0                 # Proportion of data covered
    
    # Confidence
    confidence: float = 0.5               # Confidence in this pattern (0-1)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    search_strategy_used: Optional[PatternSearchStrategy] = None
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def strength(self) -> float:
        """Combined measure of support and confidence."""
        return self.support_measure * self.confidence
    
    def has_minimum_support(self, min_support: float) -> bool:
        """Check if pattern meets minimum support threshold."""
        return self.support_measure >= min_support


@dataclass(frozen=True)
class PatternSearch:
    """
    Pattern search operation over an observation set.
    
    A pattern search records:
        - The strategy used
        - All discovered patterns
        - Statistical support for each pattern
        - Provenance tracking
    
    Pattern searches are deterministic and reproducible.
    """
    
    # Identity
    search_identity: str                  # Unique identifier for this search
    
    # Search configuration
    search_strategy: PatternSearchStrategy  # What strategy was used?
    observation_set_identity: str         # Which observations were analyzed?
    
    # Results
    discovered_patterns: Tuple[PatternCandidate, ...]
    patterns_with_minimum_support: int = 0  # How many met the threshold?
    
    # Statistical support summary
    total_observations_analyzed: int = 0
    pattern_discovery_rate: float = 0.0   # Patterns found per observation
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    search_parameters: Dict[str, Any] = field(default_factory=dict)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def pattern_count(self) -> int:
        """Number of patterns discovered."""
        return len(self.discovered_patterns)
    
    @property
    def average_confidence(self) -> float:
        """Average confidence across all discovered patterns."""
        if not self.discovered_patterns:
            return 0.0
        return sum(p.confidence for p in self.discovered_patterns) / len(self.discovered_patterns)


@dataclass(frozen=True)
class PatternSearchIdentity:
    """
    Immutable identity for a pattern search.
    
    Allows replay and verification of pattern discovery results.
    """
    
    semantic_identity: str                # Stable identity across runs
    observation_set_hash: str             # Hash of the analyzed set
    strategy_used: str                    # Which strategy was applied?
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        observation_set_hash: str,
        strategy: PatternSearchStrategy,
    ) -> PatternSearchIdentity:
        """Create a new pattern search identity."""
        import hashlib
        return cls(
            semantic_identity=semantic_identity,
            observation_set_hash=observation_set_hash[:16],
            strategy_used=strategy.value,
        )


__all__ = [
    "PatternCandidate",
    "PatternSearch",
    "PatternSearchIdentity",
    "PatternSearchStrategy",
]