# Meta Reasoning Governance - Phase 7.13
# =======================================

"""
Canonical Meta-Reasoning Governance definition.

Governance provides observational evaluation of meta-reasoning execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class GovernanceFindings:
    """
    Findings from governance evaluation of meta-reasoning.
    
    Governance findings are observational - they don't modify artifacts.
    """
    
    # Identity
    finding_id: str                         # Unique finding identifier
    
    # Evaluation results
    evaluated_items: List[str] = field(default_factory=list)  # What was evaluated?
    issues_found: List[str] = field(default_factory=list)     # Problems detected
    recommendations: List[str] = field(default_factory=list)  # Improvement suggestions
    
    # Timing
    evaluated_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class GovernanceViolation:
    """
    A governance violation - a deviation from policy.
    
    Violations are explicit and traceable.
    """
    
    # Identity
    violation_id: str                       # Unique violation identifier
    
    # Policy
    violated_policy: str                    # Which policy?
    policy_requirement: str                 # What was required?
    
    # Violation details
    description: str = ""                   # What happened?
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)  # Execution context
    
    # Timing
    detected_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class MetaReasoningGovernance:
    """
    Governance evaluation of meta-reasoning execution.
    
    A governance result contains:
        - Identity and provenance
        - Evaluated sessions or artifacts
        - Findings and violations
        - Recommendations (if any)
    
    Governance remains observational (does not modify artifacts).
    """
    
    # Identity
    governance_id: str                      # Unique governance identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Evaluated sessions
    evaluated_sessions: List[str] = field(default_factory=list)  # Session IDs
    
    # Findings
    findings: List[GovernanceFindings] = field(default_factory=list)  # Evaluations
    
    # Violations
    violations: List[GovernanceViolation] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)  # Suggested improvements
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate governance time."""
        if self.completed_at_utc:
            return self.completed_at_utc - self.created_at_utc
        return 0.0
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
    ) -> MetaReasoningGovernance:
        """Create a new governance session."""
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
        )
    
    def add_finding(self, finding: GovernanceFindings) -> MetaReasoningGovernance:
        """Add a finding and return updated governance."""
        return dataclass_replace(
            self,
            findings=self.findings + [finding],
        )
    
    def add_violation(self, violation: GovernanceViolation) -> MetaReasoningGovernance:
        """Add a violation and return updated governance."""
        return dataclass_replace(
            self,
            violations=self.violations + [violation],
        )
    
    def with_recommendation(self, recommendation: str) -> MetaReasoningGovernance:
        """Add a recommendation and return updated governance."""
        return dataclass_replace(
            self,
            recommendations=self.recommendations + [recommendation],
        )
    
    def to_completed(self) -> MetaReasoningGovernance:
        """Mark governance as completed."""
        return dataclass_replace(
            self,
            completed_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "MetaReasoningGovernance",
    "GovernanceFindings",
    "GovernanceViolation",
]