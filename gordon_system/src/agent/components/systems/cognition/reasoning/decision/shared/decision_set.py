# Decision Set - Phase 7.41
# =========================

"""
Canonical Decision Set Contract.

Decision Sets define:
    - candidate alternatives
    - evaluation constraints
    - optimization criteria
    - available resources
    - termination conditions

Decision Sets remain immutable during reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class DecisionKind(Enum):
    """Categories of decision operations."""
    
    STRATEGIC = "strategic"           # Long-term strategic choices
    OPERATIONAL = "operational"       # Short-term operational decisions
    TACTICAL = "tactical"             # Medium-term tactical choices
    POLICY = "policy"                 # Policy formation and modification
    ALLOCATION = "allocation"         # Resource allocation decisions


class DecisionState(Enum):
    """Decision session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    OPTION_GENERATION = "option_generation"
    EVALUATING = "evaluating"
    COMMITTING = "committing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class DecisionSet:
    """
    A decision set for evaluation.
    
    Decision Sets define:
        - candidate alternatives
        - evaluation constraints
        - optimization criteria
        - available resources
        - termination conditions
    
    Decision Sets remain immutable during reasoning.
    """
    
    # Identity
    decision_set_id: str                      # Unique identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Options/Alternatives
    candidate_alternatives: Tuple[str, ...]   # IDs of all candidate alternatives
    
    # Decision scope
    decision_scope: str = "unknown"           # What is being decided?
    
    # Evaluation constraints
    evaluation_constraints: Tuple[str, ...] = ()        # Constraints during evaluation
    
    # Resource limits
    max_time_seconds: float = 300.0           # Maximum evaluation time
    max_iterations: int = 100                 # Maximum iterations
    
    # Termination criteria
    min_confidence_required: float = 0.85     # Minimum confidence for commitment
    utility_threshold: Optional[float] = None # Utility must exceed this
    
    # Optimization criteria (priority order)
    optimization_criteria: Tuple[str, ...] = ("maximize_utility", "minimize_risk")
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def alternative_count(self) -> int:
        """Count of candidate alternatives."""
        return len(self.candidate_alternatives)
    
    @classmethod
    def create(
        cls,
        alternative_ids: List[str],
        decision_scope: str = "unknown",
        constraints: Optional[List[str]] = None,
        semantic_identity: Optional[str] = None,
    ) -> DecisionSet:
        """Create a new decision set."""
        return cls(
            decision_set_id=f"decision_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity or f"decision_set:{uuid.uuid4().hex[:16]}",
            candidate_alternatives=tuple(alternative_ids),
            decision_scope=decision_scope,
            evaluation_constraints=tuple(constraints or []),
        )
    
    def with_alternative(self, alternative_id: str) -> DecisionSet:
        """Return a copy with an additional alternative."""
        new_alternatives = list(self.candidate_alternatives)
        new_alternatives.append(alternative_id)
        return dataclass_replace(
            self,
            candidate_alternatives=tuple(new_alternatives),
        )
    
    def without_alternative(self, alternative_id: str) -> DecisionSet:
        """Return a copy with an alternative removed."""
        new_alternatives = tuple(a for a in self.candidate_alternatives if a != alternative_id)
        return dataclass_replace(
            self,
            candidate_alternatives=new_alternatives,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DecisionSet",
    "DecisionKind",
    "DecisionState",
]