# Experimental Reasoning - Governance
# ===================================

"""
Canonical Governance contracts.

Governance evaluates experiment validity and quality without modifying artifacts.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ExperimentalGovernance:
    """
    Governance evaluation for experimental reasoning.
    
    Governance remains observational - it never modifies experimental artifacts directly.
    It evaluates:
        - Experiment validity
        - Measurement quality
        - Control integrity
        - Information gain
        - Resource efficiency
        - Diagnostics
    
    Governance findings are purely observational and descriptive.
    """
    
    # Identity
    governance_id: str                          # Unique identifier
    
    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...] = ()    # Session identities evaluated
    
    # Governance findings
    validity_issues: Tuple[str, ...] = ()       # Validity-related issues found
    quality_issues: Tuple[str, ...] = ()        # Quality-related issues found
    control_integrity_issues: Tuple[str, ...] = ()  # Control-related issues
    
    # Evaluation results
    overall_governance_status: str = "valid"   # "valid", "warning", "invalid"
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()       # Suggestions for improvement
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    origin_context: str = "unknown"
    
    @property
    def has_issues(self) -> bool:
        """Check if any governance issues were found."""
        return len(self.validity_issues) > 0 or len(self.quality_issues) > 0
    
    @property
    def issue_count(self) -> int:
        """Get total number of issues found."""
        return len(self.validity_issues) + len(self.quality_issues) + len(self.control_integrity_issues)


@dataclass(frozen=True)
class GovernanceFinding:
    """
    A specific finding from governance evaluation.
    
    Includes the issue, its severity, and recommended action.
    """
    
    # Identity
    finding_id: str                             # Unique identifier
    
    # Finding details
    category: str = "general"                   # e.g., "validity", "quality", "controls"
    severity: float = 0.5                       # Severity level (0-1)
    description: str = ""                       # What was found?
    
    # Recommended action
    recommended_action: Optional[str] = None    # How to address this finding?
    
    @property
    def is_critical(self) -> bool:
        """Check if this finding is critical."""
        return self.severity >= 0.8
    
    @property
    def is_warning(self) -> bool:
        """Check if this finding is a warning."""
        return 0.3 <= self.severity < 0.8


@dataclass(frozen=True)
class GovernanceEvaluation:
    """
    Complete governance evaluation for an experiment design.
    
    Includes all findings and overall assessment.
    """
    
    # Identity
    evaluation_id: str                          # Unique identifier
    
    # Experiment info
    experiment_identity: str                    # Evaluated experiment
    evaluation_timestamp_utc: float = field(default_factory=time.time)
    
    # Evaluation details
    is_valid: bool = True                       # Overall validity
    findings: Tuple[GovernanceFinding, ...] = ()  # All findings
    
    @property
    def finding_count(self) -> int:
        """Get total number of findings."""
        return len(self.findings)
    
    @property
    def critical_findings(self) -> Tuple[GovernanceFinding, ...]:
        """Get all critical findings."""
        return tuple(f for f in self.findings if f.is_critical)
    
    @classmethod
    def create(
        cls,
        experiment_identity: str,
        is_valid: bool = True,
        findings: List[GovernanceFinding] = None,
    ) -> GovernanceEvaluation:
        """Create a new governance evaluation."""
        return cls(
            evaluation_id=f"governance:{uuid.uuid4().hex[:16]}",
            experiment_identity=experiment_identity,
            is_valid=is_valid,
            findings=tuple(findings or []),
        )


__all__ = [
    "ExperimentalGovernance",
    "GovernanceFinding",
    "GovernanceEvaluation",
]