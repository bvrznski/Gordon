# Adaptation Set - Phase 7.25
# ============================

"""
Canonical Adaptation Set.

An adaptation set defines the candidates, constraints, and policies for an
adaptation session.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class AdaptationCandidate:
    """
    A candidate adaptation that may be applied.
    
    Candidates remain explicit and are evaluated before application.
    """
    
    # Identity
    candidate_identity: str                # Unique candidate identifier
    
    # Classification
    candidate_type: str                    # Type of adaptation (behavior, context, config)
    
    # Scope
    adaptation_scope: Optional[str] = None  # What this adaptation affects
    
    # Expected outcome
    expected_effect: str                   # Expected behavioral change
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AdaptationSet:
    """
    A set of adaptations to be considered during an adaptation session.
    
    An adaptation set defines:
        - Candidate adaptations
        - Context constraints
        - Configuration policies
        - Rollback policies
        - Adaptation boundaries
    
    Sets remain immutable during reasoning to ensure determinism.
    """
    
    # Identity
    adaptation_set_identity: str           # Unique set identifier
    
    # Candidates
    participating_adaptations: Tuple[AdaptationCandidate, ...] = field(default_factory=tuple)
    
    # Scope and constraints
    adaptation_scope: Optional[str] = None
    operational_constraints: Dict[str, Any] = field(default_factory=dict)
    
    # Policies
    rollback_policy: str = "immediate"     # How rollbacks should be performed
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    context_hash: Optional[str] = None     # Hash of the context for determinism
    
    @property
    def candidate_count(self) -> int:
        """Count number of candidate adaptations."""
        return len(self.participating_adaptations)
    
    @classmethod
    def create(
        cls,
        adaptation_candidates: List[AdaptationCandidate],
        scope: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None,
        rollback_policy: str = "immediate",
    ) -> AdaptationSet:
        """Create a new adaptation set."""
        return cls(
            adaptation_set_identity=f"set:{uuid.uuid4().hex[:16]}",
            participating_adaptations=tuple(adaptation_candidates),
            adaptation_scope=scope,
            operational_constraints=constraints or {},
            rollback_policy=rollback_policy,
            context_hash=None,  # Set by caller
        )
    
    def with_candidate(self, candidate: AdaptationCandidate) -> AdaptationSet:
        """Return a new set with an additional candidate."""
        return dataclass_replace(
            self,
            participating_adaptations=self.participating_adaptations + (candidate,),
        )
    
    def without_candidate(self, candidate_identity: str) -> AdaptationSet:
        """Return a new set without a specific candidate."""
        filtered = tuple(c for c in self.participating_adaptations 
                        if c.candidate_identity != candidate_identity)
        return dataclass_replace(
            self,
            participating_adaptations=filtered,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AdaptationSet",
    "AdaptationCandidate",
]