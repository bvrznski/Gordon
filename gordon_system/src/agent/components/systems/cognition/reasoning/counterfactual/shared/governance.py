# Counterfactual Governance - Phase 7.6
# ====================================

"""
Counterfactual Governance evaluates reasoning quality, branch validity,
causal consistency, and other governance concerns.

Governance remains observational - it never modifies the counterfactual artifacts.
Instead, it produces findings about their state and compliance with rules.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class CounterfactualGovernance:
    """
    Governance evaluation of counterfactual reasoning results.
    
    Governance evaluates:
        - Branch validity (proper ancestry maintained)
        - Causal consistency (no logical contradictions)
        - Comparison quality (adequate comparison metrics)
        - Divergence correctness (traceable propagation paths)
        - Resource usage (within acceptable limits)
        - Provenance completeness (all tracking intact)
    
    Governance remains observational and never modifies artifacts directly.
    """
    
    # Identity
    governance_id: str                        # Unique governance identifier
    
    # Evaluated sessions/artifacts
    evaluated_session_ids: Tuple[str, ...] = ()  # Which sessions were evaluated?
    
    # Findings (what was found)
    findings: Tuple[GovernanceFinding, ...] = ()
    
    # Violations (rules that were violated)
    violations: Tuple[str, ...] = ()          # e.g., "COUNTERFUAL-LAW-003"
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def violation_count(self) -> int:
        """Number of rule violations."""
        return len(self.violations)
    
    @property
    def has_violations(self) -> bool:
        """True if any violations were found."""
        return self.violation_count > 0
    
    @classmethod
    def create(cls, session_id: str) -> CounterfactualGovernance:
        """Create a new governance evaluation record."""
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_session_ids=(session_id,),
        )
    
    def with_finding(self, finding: GovernanceFinding) -> CounterfactualGovernance:
        """Return a copy with an additional finding."""
        return dataclass_replace(
            self,
            findings=self.findings + (finding,),
        )
    
    def add_violation(self, rule_name: str) -> CounterfactualGovernance:
        """Return a copy with a violation added."""
        return dataclass_replace(
            self,
            violations=self.violations + (rule_name,),
        )


@dataclass(frozen=True)
class GovernanceRule:
    """
    A governance rule that counterfactual reasoning must follow.
    
    Rules cover:
        - Identity preservation
        - Reference world immutability  
        - Branch ancestry tracking
        - Intervention hypothetical nature
        - Divergence traceability
        - Comparison reproducibility
        - Validation and governance observability
    """
    
    # Rule identifier (e.g., "COUNTERFUAL-LAW-001")
    rule_id: str                              # e.g., "COUNTERFUAL-LAW-002"
    
    # Rule description
    description: str                          # What the rule requires
    
    # Severity if violated
    severity: str = "high"                    # "low", "medium", "high", "critical"
    
    @classmethod
    def create(cls, rule_id: str, description: str) -> GovernanceRule:
        """Create a new governance rule."""
        return cls(rule_id=rule_id, description=description)


class GovernanceFindingKind(Enum):
    """Kinds of governance findings."""
    
    PROVENANCE_INCOMPLETE = "provenance_incomplete"
    BRANCH_ANCESTRY_ERROR = "branch_ancestry_error"
    INTERVENTION_NOT_HYPOTHETICAL = "intervention_not_hypothetical"
    REFERENCE_WORLD_MODIFIED = "reference_world_modified"
    DIVERGENCE_UNRECONSTRUCTABLE = "divergence_unreconstructable"
    INVALID_BRANCH_CREATION = "invalid_branch_creation"
    MISSING_CONSTRAINT = "missing_constraint"


@dataclass(frozen=True)
class GovernanceFinding:
    """
    A specific finding from governance evaluation.
    
    Each finding describes an issue, violation, or quality assessment.
    """
    
    # Identity
    finding_id: str                           # Unique finding identifier
    
    # Finding type
    finding_kind: GovernanceFindingKind       # What kind of finding?
    
    # Description
    description: str                          # Human-readable explanation
    
    # Rule (if applicable)
    rule_name: Optional[str] = None           # Which rule was violated/checked?
    
    # Severity
    severity: str = "medium"                  # Impact assessment
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        finding_kind: GovernanceFindingKind,
        description: str,
    ) -> GovernanceFinding:
        """Create a new governance finding."""
        return cls(
            finding_id=f"governance_finding:{uuid.uuid4().hex[:16]}",
            finding_kind=finding_kind,
            description=description,
        )


@dataclass(frozen=True)
class GovernanceHealth:
    """
    Health metrics for counterfactual governance evaluation.
    
    Metrics include:
        - Sessions evaluated
        - Success/failure rates
        - Violation counts by type
        - Average evaluation time
    """
    
    # Identity
    health_id: str                            # Unique health identifier
    
    # Evaluation summary
    total_sessions_evaluated: int = 0         # Total sessions reviewed
    successful_evaluations: int = 0           # Passed all checks
    failed_evaluations: int = 0               # Had violations
    warning_evaluations: int = 0              # Minor issues found
    
    # Violation breakdown
    violation_counts: Dict[str, int] = field(default_factory=dict)  # rule_id -> count
    
    # Timing
    average_evaluation_time_seconds: float = 0.0
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def evaluation_rate(self) -> float:
        """Success rate of evaluations."""
        total = self.total_sessions_evaluated
        if total == 0:
            return 1.0
        return self.successful_evaluations / total
    
    @classmethod
    def create(cls, health_id: Optional[str] = None) -> GovernanceHealth:
        """Create a new governance health record."""
        return cls(
            health_id=health_id or f"governance_health:{uuid.uuid4().hex[:16]}",
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CounterfactualGovernance",
    "GovernanceRule",
    "GovernanceFinding",
    "GovernanceHealth",
]