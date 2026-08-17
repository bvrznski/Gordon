# Induction Governance - Phase 7.2
# =================================

"""
Canonical Induction Governance Contract.

Governance evaluates the quality and adherence of induction to specifications.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class GovernanceFinding:
    """
    A single finding from induction governance evaluation.
    
    Findings record specific issues or observations about the induction process.
    """
    
    # Identity
    finding_id: str                       # Unique identifier
    
    # Finding details
    finding_kind: str                     # e.g., "sampling_bias", "low_confidence"
    severity: str = "info"                # info, warning, error
    
    # Description
    description: str                      # Human-readable explanation
    affected_component: Optional[str] = None  # Which component was evaluated?
    
    # Evidence for finding
    supporting_evidence: Tuple[str, ...] = ()  # Supporting data points
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    evaluator_id: str = "default"
    provenance: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class InductionGovernance:
    """
    Governance evaluation of an induction session.
    
    A governance evaluation records:
        - Evaluated sessions
        - Findings from the evaluation
        - Violations detected
        - Recommendations for improvement
    
    Governance remains observational; it does not modify induction results directly.
    """
    
    # Identity
    governance_identity: str              # Unique identifier for this evaluation
    
    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...]   # IDs of induction sessions evaluated
    
    # Findings from governance review
    findings: Tuple[GovernanceFinding, ...]
    
    # Violations detected
    violations: Tuple[str, ...] = ()      # Names of violated laws/rules
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()  # Suggested improvements
    
    # Governance metrics
    total_checks_performed: int = 0       # How many checks?
    checks_passed: int = 0                # How many passed?
    
    # Overall assessment
    governance_score: float = 1.0         # 1.0 = perfect adherence to governance
    quality_assessment: str = "excellent" # excellent, good, fair, poor
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    evaluator_id: str = "default"
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def check_pass_rate(self) -> float:
        """Calculate the pass rate for governance checks."""
        if self.total_checks_performed == 0:
            return 1.0
        return self.checks_passed / self.total_checks_performed
    
    @property
    def violation_count(self) -> int:
        """Number of violations detected."""
        return len(self.violations)
    
    @property
    def has_violations(self) -> bool:
        """Check if any violations were found."""
        return self.violation_count > 0


@dataclass(frozen=True)
class GovernanceEvaluation:
    """
    Detailed evaluation of a single induction aspect.
    
    Used for component-level governance assessment.
    """
    
    evaluation_id: str
    
    # Evaluated component
    evaluated_component: str              # e.g., "sampling", "generalization"
    
    # Evaluation criteria and results
    criteria_passed: Tuple[str, ...] = ()
    criteria_failed: Tuple[str, ...] = ()
    
    # Scores
    quality_score: float = 0.5            # Quality of this component
    compliance_score: float = 1.0         # Compliance with rules
    
    # Recommendations for this component
    recommendations: Tuple[str, ...] = ()
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    evaluator_id: str = "default"


@dataclass(frozen=True)
class GovernanceRule:
    """
    A governance rule that induction must follow.
    
    Rules encode the normative specifications from Phase 7.2.
    """
    
    rule_id: str                          # Unique identifier
    rule_name: str                        # Human-readable name
    
    # Rule description
    rule_description: str                 # What does this rule require?
    violated_by: Optional[str] = None     # If violated, what broke it?
    
    # Rule type
    rule_kind: str = "constraint"         # constraint, recommendation, best_practice
    
    # Severity of violation
    severity_on_violation: str = "warning"  # info, warning, error
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_law: Optional[str] = None      # Which law does this implement?


@dataclass(frozen=True)
class GovernanceHealth:
    """
    Health metrics for the induction governance system.
    
    Provides diagnostic information about governance performance.
    """
    
    health_id: str
    
    # Session metrics
    sessions_evaluated: int = 0
    sessions_compliant: int = 0
    compliance_rate: float = 1.0
    
    # Findings summary
    total_findings: int = 0
    findings_by_severity: Dict[str, int] = field(default_factory=dict)
    
    # Violations summary
    total_violations: int = 0
    violations_by_kind: Dict[str, int] = field(default_factory=dict)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)


__all__ = [
    "GovernanceFinding",
    "InductionGovernance",
    "GovernanceEvaluation",
    "GovernanceRule",
    "GovernanceHealth",
]