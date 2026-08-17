# Observation Set - Phase 7.2
# ============================

"""
Canonical Observation Set Contract.

Observation Sets define the data over which induction operates.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ObservationSource(Enum):
    """Sources of observations."""
    
    PERCEPTION = "perception"           # Direct sensory input
    MEMORY = "memory"                   # Stored experiences
    KNOWLEDGE = "knowledge"             # Existing beliefs
    EXECUTION_HISTORY = "execution_history"  # Past actions/results
    SIMULATION = "simulation"           # Simulated outputs
    EXTERNAL_SOURCE = "external_source"   # External systems


class ObservationKind(Enum):
    """Kinds of observations."""
    
    FACTUAL = "factual"                 # Empirical fact
    RELATIONAL = "relational"           # Relationship between entities
    TEMPORAL = "temporal"               # Time-ordered sequence
    STATISTICAL = "statistical"         # Aggregated statistics
    EXCEPTIONAL = "exceptional"         # Deviating from pattern


@dataclass(frozen=True)
class InductionObservation:
    """
    Single observation in an induction session.
    
    Each observation records:
        - Source and kind of the observation
        - Confidence level
        - Supporting evidence
        - Provenance tracking
    """
    
    # Identity
    observation_id: str                   # Unique observation identifier
    
    # Content
    observation_content: Any              # The actual observed data
    observation_kind: ObservationKind     # What kind of observation?
    
    # Quality metrics
    confidence: float = 1.0               # Confidence in this observation (0-1)
    quality_score: float = 1.0            # Overall quality (0-1)
    
    # Source info
    observation_source: ObservationSource = ObservationSource.PERCEPTION
    source_id: Optional[str] = None       # ID of the source system/entity
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)  # How was this obtained?
    
    @property
    def effective_confidence(self) -> float:
        """Confidence adjusted by quality."""
        return max(0.0, min(1.0, self.confidence * self.quality_score))


@dataclass(frozen=True)
class ObservationSet:
    """
    Set of observations for induction to analyze.
    
    An observation set defines:
        - Participating observations
        - Selection criteria used
        - Quality constraints applied
        - Temporal scope
        - Provenance tracking
    
    Observation Sets remain immutable during analysis.
    """
    
    # Identity
    observation_set_identity: str         # Unique identifier for this set
    
    # Observations (as tuples for immutability)
    observations: Tuple[InductionObservation, ...]
    
    # Constraints and filters applied
    observation_constraints: Dict[str, Any] = field(default_factory=dict)
    observation_quality: float = 0.5      # Minimum quality threshold
    
    # Selection metadata
    selection_criterion: str = "all"      # How were observations selected?
    temporal_scope_start_utc: Optional[float] = None
    temporal_scope_end_utc: Optional[float] = None
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def observation_count(self) -> int:
        """Number of observations in the set."""
        return len(self.observations)
    
    @property
    def average_confidence(self) -> float:
        """Average confidence across all observations."""
        if not self.observations:
            return 0.0
        return sum(o.confidence for o in self.observations) / len(self.observations)
    
    def filter_by_quality(self, min_quality: float) -> ObservationSet:
        """Return a new set with only high-quality observations."""
        filtered = tuple(o for o in self.observations if o.quality_score >= min_quality)
        return dataclass_replace(
            self,
            observations=filtered,
            observation_constraints={**self.observation_constraints, "min_quality": min_quality},
        )
    
    def filter_by_source(self, source: ObservationSource) -> ObservationSet:
        """Return a new set with only observations from a specific source."""
        filtered = tuple(o for o in self.observations if o.observation_source == source)
        return dataclass_replace(
            self,
            observations=filtered,
            observation_constraints={**self.observation_constraints, "source": source.value},
        )
    
    def filter_by_kind(self, kind: ObservationKind) -> ObservationSet:
        """Return a new set with only observations of a specific kind."""
        filtered = tuple(o for o in self.observations if o.observation_kind == kind)
        return dataclass_replace(
            self,
            observations=filtered,
            observation_constraints={**self.observation_constraints, "kind": kind.value},
        )
    
    def get_subsample(self, n: int) -> ObservationSet:
        """Return a random subsample of n observations."""
        if n >= len(self.observations):
            return self
        # Simple implementation - in production use proper sampling
        subsample = self.observations[:n]
        return dataclass_replace(
            self,
            observations=subsample,
            observation_constraints={**self.observation_constraints, "subsample_size": n},
        )


@dataclass(frozen=True)
class ObservationSetIdentity:
    """
    Immutable identity for an observation set.
    
    Allows replay and verification of induction results.
    """
    
    semantic_identity: str                # Stable identity across runs
    selection_criterion: str              # How were observations selected?
    constraints_hash: str                 # Hash of applied constraints
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        selection_criterion: str,
        constraints: Dict[str, Any],
    ) -> ObservationSetIdentity:
        """Create a new observation set identity."""
        import hashlib
        constraints_str = str(sorted(constraints.items()))
        return cls(
            semantic_identity=semantic_identity,
            selection_criterion=selection_criterion,
            constraints_hash=hashlib.md5(constraints_str.encode()).hexdigest()[:16],
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "InductionObservation",
    "ObservationSet",
    "ObservationSetIdentity",
    "ObservationSource",
    "ObservationKind",
]