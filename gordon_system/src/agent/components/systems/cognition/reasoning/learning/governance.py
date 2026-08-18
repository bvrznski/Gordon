# Learning Governance - Phase 7.24
# ===============================

"""
Canonical Learning Governance Contract.

Learning Governance evaluates the quality and validity of learning processes.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class LearningGovernance:
    """
    Governance evaluation for a learning session.
    
    Governance evaluates:
        - Learning quality and validity
        - Evidence sufficiency
        - Generalization bounds
        - Integration consistency
    
    Governance remains observational; it never modifies learning artifacts directly.
    """
    
    # Identity
    governance_id: str                        # Unique identifier
    
    # Evaluated sessions
    evaluated_sessions: List[str] = field(default_factory=list)  # Session IDs
    
    # Evaluation results
    findings: Dict[str, Any] = field(default_factory=dict)
    violations: List[str] = field(default_factory=list)
    
    # Compliance status
    is_compliant: bool = True                 # Does learning meet requirements?
    compliance_score: float = 1.0             # 0.0 to 1.0
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    # Timing
    evaluated_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    governance_policy: str = "standard"       # Which policy was used?
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        evaluated_sessions: Optional[List[str]] = None,
        governance_policy: str = "standard",
    ) -> LearningGovernance:
        """Create a new governance evaluation."""
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=evaluated_sessions or [],
            governance_policy=governance_policy,
            evaluated_at_utc=time.time(),
        )
    
    def with_finding(self, key: str, value: Any) -> LearningGovernance:
        """Return a copy with an additional finding."""
        new_findings = dict(self.findings)
        new_findings[key] = value
        return dataclass_replace(
            self,
            findings=new_findings,
        )
    
    def add_violation(self, violation: str) -> LearningGovernance:
        """Return a copy with an additional violation."""
        new_violations = list(self.violations)
        new_violations.append(violation)
        return dataclass_replace(
            self,
            violations=new_violations,
            is_compliant=False,
            compliance_score=max(0.0, self.compliance_score - 0.1),
        )
    
    def add_recommendation(self, recommendation: str) -> LearningGovernance:
        """Return a copy with an additional recommendation."""
        new_recommendations = list(self.recommendations)
        new_recommendations.append(recommendation)
        return dataclass_replace(
            self,
            recommendations=new_recommendations,
        )


@dataclass(frozen=True)
class GovernanceViolation:
    """
    A governance violation record.
    
    Violations include:
        - Missing evidence for learning
        - Overgeneralization beyond observations
        - Invalid inference patterns
        - Provenance corruption
    """
    
    # Identity
    violation_id: str                         # Unique identifier
    
    # Violation details
    violation_kind: str                       # What type of violation?
    affected_learning: str                    # Which learning was affected?
    
    # Details
    description: str = ""                     # Human-readable description
    severity: str = "warning"                 # "info", "warning", or "error"
    
    # Recovery options
    recovery_options: Tuple[str, ...] = ()    # How might this be recovered?
    
    # Timing
    detected_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "LearningGovernance",
    "GovernanceViolation",
]