# Executive Governance - Phase 7.30
# ==================================

"""
Executive Governance Module.

Governance evaluates executive decisions without modifying them directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any

from .shared import (
    ExecutiveDescriptor,
    ExecutiveSet,
    ViolationType,
    ExecutiveGovernance,
)


@dataclass(frozen=True)
class GovernanceEvaluation:
    """
    A governance evaluation of an executive session.
    
    Governance evaluates:
        - Coordination correctness
        - Arbitration quality  
        - Directive correctness
        - Synchronization quality
    
    Governance remains observational and never modifies executive artifacts directly.
    """
    
    # Identity
    evaluation_id: str                          # Unique identifier
    
    # Evaluated session
    evaluated_session_id: str                   # Which executive session?
    
    # Evaluation details
    findings: Tuple[Dict[str, Any], ...] = ()   # What was good?
    violations: Tuple[ViolationType, ...] = ()  # What went wrong?
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()
    
    # Overall assessment
    is_compliant: bool = True                   # Passed all checks?
    
    # Timing
    evaluated_at_utc: float = field(default_factory=time.time)
    
    @property
    def violation_count(self) -> int:
        """Count of governance violations."""
        return len(self.violations)
    
    @classmethod
    def create(
        cls,
        evaluated_session_id: str,
    ) -> "GovernanceEvaluation":
        """Create a new governance evaluation."""
        return cls(
            evaluation_id=f"governance_eval:{uuid.uuid4().hex[:16]}",
            evaluated_session_id=evaluated_session_id,
        )
    
    def record_violation(self, violation: ViolationType) -> "GovernanceEvaluation":
        """Record a governance violation."""
        return dataclass_replace(
            self,
            violations=self.violations + (violation,),
            is_compliant=False,
        )
    
    def add_recommendation(self, recommendation: str) -> "GovernanceEvaluation":
        """Add a governance recommendation."""
        return dataclass_replace(
            self,
            recommendations=self.recommendations + (recommendation,),
        )


@dataclass(frozen=True)
class GovernanceAuthority:
    """
    Authority to perform governance evaluations.
    
    Defines:
        - Which executive sessions can be evaluated
        - What rules apply
        - Evaluation scope
    """
    
    # Identity
    authority_id: str                           # Unique identifier
    
    # Scope
    evaluated_session_ids: Tuple[str, ...] = ()  # Which sessions?
    
    # Rules (by ID)
    rules: Dict[str, str] = field(default_factory=dict)  # rule_id -> description
    
    @classmethod
    def create(
        cls,
        session_ids: Optional[List[str]] = None,
    ) -> "GovernanceAuthority":
        """Create a new governance authority."""
        return cls(
            authority_id=f"governance_authority:{uuid.uuid4().hex[:16]}",
            evaluated_session_ids=tuple(session_ids or []),
        )


@dataclass(frozen=True)
class GovernanceHistory:
    """
    History of all governance evaluations.
    
    Preserves complete lineage of governance decisions for auditability.
    """
    
    # Identity
    history_id: str                             # Unique identifier
    
    # Evaluations (ordered chronologically)
    evaluations: Tuple[GovernanceEvaluation, ...] = ()
    
    # Summary statistics
    total_evaluations: int = 0
    compliant_count: int = 0
    
    @classmethod
    def create(cls, history_id: Optional[str] = None) -> "GovernanceHistory":
        """Create a new governance history."""
        return cls(
            history_id=history_id or f"governance_history:{uuid.uuid4().hex[:16]}",
        )
    
    def add_evaluation(self, evaluation: GovernanceEvaluation) -> "GovernanceHistory":
        """Add an evaluation to the history."""
        total = self.total_evaluations + 1
        compliant = self.compliant_count + (1 if evaluation.is_compliant else 0)
        
        return dataclass_replace(
            self,
            evaluations=self.evaluations + (evaluation,),
            total_evaluations=total,
            compliant_count=compliant,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "GovernanceEvaluation",
    "GovernanceAuthority", 
    "GovernanceHistory",
]
