# Meta Reasoning Refinement - Phase 7.13
# =======================================

"""
Canonical Meta-Reasoning Refinement definition.

Refinement evolves meta policies based on experience and performance evaluation.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class PolicyChange:
    """
    A change made to a meta-reasoning policy during refinement.
    
    Policy changes track what was modified and why.
    """
    
    # Identity
    change_id: str                          # Unique change identifier
    
    # What changed
    policy_element: str                     # Which policy element?
    old_value: Optional[Any] = None         # Previous value (if any)
    new_value: Any                          # New value
    
    # Rationale
    change_reason: str = ""                 # Why the change?
    
    # Timing
    made_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class MetaReasoningRefinement:
    """
    Refinement of meta-reasoning policies.
    
    A refinement contains:
        - Identity and provenance  
        - Previous and refined policies
        - Supporting changes
        - Performance evidence
    
    Policy evolution preserves identity while adapting to experience.
    """
    
    # Identity
    refinement_id: str                      # Unique refinement identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Policies
    previous_policy: Dict[str, Any]         # Previous meta policy
    refined_policy: Dict[str, Any]          # Updated meta policy
    
    # Changes made
    changes: List[PolicyChange] = field(default_factory=list)  # Policy modifications
    
    # Evidence for refinement
    performance_evidence: Dict[str, float] = field(default_factory=dict)  # Metrics
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    refined_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate refinement time."""
        if self.refined_at_utc:
            return self.refined_at_utc - self.created_at_utc
        return 0.0
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        previous_policy: Dict[str, Any],
        refined_policy: Optional[Dict[str, Any]] = None,
    ) -> MetaReasoningRefinement:
        """Create a new refinement."""
        if refined_policy is None:
            refined_policy = previous_policy.copy()
        
        return cls(
            refinement_id=f"refinement:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            previous_policy=previous_policy,
            refined_policy=refined_policy,
            refined_at_utc=time.time(),
        )
    
    def with_change(self, change: PolicyChange) -> MetaReasoningRefinement:
        """Add a policy change and return updated refinement."""
        return dataclass_replace(
            self,
            changes=self.changes + [change],
        )
    
    def with_evidence(self, evidence: Dict[str, float]) -> MetaReasoningRefinement:
        """Add performance evidence and return updated refinement."""
        new_evidence = dict(self.performance_evidence)
        new_evidence.update(evidence)
        return dataclass_replace(
            self,
            performance_evidence=new_evidence,
        )
    
    def to_refined(self) -> MetaReasoningRefinement:
        """Mark refinement as complete."""
        return dataclass_replace(
            self,
            refined_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "MetaReasoningRefinement",
    "PolicyChange",
]