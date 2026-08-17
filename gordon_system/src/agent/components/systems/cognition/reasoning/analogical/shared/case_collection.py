# Case Collection - Phase 7.4
# ===========================

"""
Canonical Case Collection Contract.

Case Collections define candidate cases for analogical reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class SourceCase:
    """
    A source case from which knowledge may be transferred.
    
    Cases may originate from:
        - Episodic memory
        - Knowledge stores
        - Previous reasoning sessions
        - External repositories
        - Simulations
    
    Cases remain explicit; they are never inferred or fabricated.
    """
    
    # Identity
    case_id: str                              # Unique identifier
    semantic_identity: str                    # Stable identity across runs
    
    # Origin information
    originating_domain: str                   # Where did this case come from?
    origin_context: str = "unknown"           # Context of origin
    
    # Semantic structure (graph-based)
    structural_representation: Dict[str, Any] = field(default_factory=dict)
    
    # Applicability criteria
    applicability_conditions: Tuple[str, ...] = ()  # When is this case applicable?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    last_used_at_utc: Optional[float] = None
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class CaseCollection:
    """
    A collection of source cases for analogical reasoning.
    
    Collections define:
        - Candidate cases
        - Retrieval constraints
        - Domain boundaries
        - Structural completeness requirements
        - Quality metrics
    
    Collections remain immutable during reasoning.
    """
    
    # Identity
    collection_id: str                        # Unique identifier
    
    # Participating cases (source cases)
    participating_cases: Tuple[SourceCase, ...] = ()
    
    # Retrieval constraints
    domain_boundaries: Tuple[str, ...] = ()   # Which domains are included?
    min_quality_score: float = 0.0            # Minimum quality threshold
    
    # Quality metrics
    structural_completeness: float = 1.0      # How complete are the cases?
    case_diversity: float = 1.0               # Variety of cases
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def case_count(self) -> int:
        """Number of cases in collection."""
        return len(self.participating_cases)
    
    @classmethod
    def create(
        cls,
        cases: Optional[List[SourceCase]] = None,
        domain_boundaries: Optional[List[str]] = None,
        min_quality_score: float = 0.0,
    ) -> CaseCollection:
        """Create a new case collection."""
        return cls(
            collection_id=f"case_collection:{uuid.uuid4().hex[:16]}",
            participating_cases=tuple(cases or []),
            domain_boundaries=tuple(domain_boundaries or []),
            min_quality_score=min_quality_score,
        )
    
    def add_case(self, case: SourceCase) -> CaseCollection:
        """Return a new collection with the case added."""
        return dataclass_replace(
            self,
            participating_cases=self.participating_cases + (case,),
        )
    
    def filter_by_domain(self, domain: str) -> CaseCollection:
        """Return cases from the specified domain."""
        filtered = tuple(
            c for c in self.participating_cases
            if c.originating_domain == domain
        )
        return dataclass_replace(
            self,
            participating_cases=filtered,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SourceCase",
    "CaseCollection",
]