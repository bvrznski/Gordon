# Evaluation Set - Phase 7.23
# ===========================

"""
Canonical Evaluation Set for Gordon's Evaluation Reasoning subsystem.

An Evaluation Set defines:
- evaluation targets
- reference expectations
- evaluation criteria
- metric definitions
- acceptance policies

Evaluation Sets remain immutable during assessment.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class EvaluationTargetKind(Enum):
    """Kinds of evaluation targets."""
    
    EXECUTION_SESSION = "execution_session"
    PLAN = "plan"
    DECISION = "decision"
    STRATEGY = "strategy"
    REASONING_SESSION = "reasoning_session"
    TOOL = "tool"
    ENVIRONMENT_INTERACTION = "environment_interaction"


@dataclass(frozen=True)
class EvaluationTarget:
    """
    An evaluation target is the entity being evaluated.
    
    A target contains:
        - Identity (unique identifier)
        - Target type
        - Reference expectation (what was expected)
        - Evaluation context (where it occurred)
        - Provenance tracking
    
    Targets remain explicit and independently inspectable.
    """
    
    target_id: str                      # Unique target identifier
    target_type: EvaluationTargetKind  # What kind of entity?
    reference_expectation: Optional[str] = None  # Expected outcome/state
    evaluation_context: Dict[str, Any] = field(default_factory=dict)  # Contextual data
    provenance: Optional[str] = None   # How was this target selected?
    
    @property
    def is_complete(self) -> bool:
        """Check if target has complete information."""
        return self.target_id and self.target_type


@dataclass(frozen=True)
class EvaluationSet:
    """
    An Evaluation Set defines all parameters for a single evaluation session.
    
    An evaluation set contains:
        - Evaluation set identity
        - Participating targets (what is being evaluated)
        - Evaluation scope (what aspects to assess)
        - Evaluation constraints (rules and policies)
        - Provenance tracking
    
    The evaluation set remains immutable during assessment, ensuring
    reproducibility of evaluation results.
    """
    
    # Identity
    evaluation_set_id: str              # Unique set identifier
    semantic_identity: str              # Semantic identity for traceability
    
    # Targets
    participating_targets: List[EvaluationTarget] = field(default_factory=list)
    
    # Evaluation parameters
    evaluation_scope: Optional[str] = None  # Scope description
    evaluation_constraints: Dict[str, Any] = field(default_factory=dict)  # Rules/policies
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    evaluated_at_utc: Optional[float] = None
    
    # Provenance
    source_evaluation_set_id: Optional[str] = None   # If refined from another set
    origin_context: str = "unknown"                  # Where did evaluation originate?
    
    @property
    def target_count(self) -> int:
        """Return number of targets in this set."""
        return len(self.participating_targets)
    
    @property
    def has_targets(self) -> bool:
        """Check if there are any targets."""
        return len(self.participating_targets) > 0
    
    def get_target_by_id(self, target_id: str) -> Optional[EvaluationTarget]:
        """Find a target by its ID."""
        for target in self.participating_targets:
            if target.target_id == target_id:
                return target
        return None
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        targets: List[EvaluationTarget],
        scope: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None,
        origin_context: str = "unknown",
        source_evaluation_set_id: Optional[str] = None,
    ) -> EvaluationSet:
        """Create a new evaluation set."""
        return cls(
            evaluation_set_id=f"evalset:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            participating_targets=list(targets),
            evaluation_scope=scope,
            evaluation_constraints=constraints or {},
            origin_context=origin_context,
            source_evaluation_set_id=source_evaluation_set_id,
            created_at_utc=time.time(),
        )
    
    def with_updated_targets(self, new_targets: List[EvaluationTarget]) -> EvaluationSet:
        """Return a copy with updated targets."""
        return dataclass_replace(
            self,
            participating_targets=list(new_targets),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "EvaluationTarget",
    "EvaluationTargetKind",
    "EvaluationSet",
]