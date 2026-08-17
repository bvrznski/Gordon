# Causal Governance - Phase 7.5
# =============================

"""
Canonical Causal Governance.

Governance evaluates causal structures without modifying them.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class GovernanceFinding:
    """
    A single governance evaluation finding.
    """
    
    # Identity
    finding_id: str                     # Unique finding identifier
    
    # Finding type
    finding_type: str                   # "valid", "warning", "error"
    
    # What was evaluated
    evaluated_element: Optional[str] = None  # Which element?
    
    # Description
    description: str                    # What was found?
    
    # Recommendation (if any)
    recommendation: Optional[str] = None  # How to fix?


@dataclass(frozen=True)
class CausalGovernance:
    """
    Governance evaluation for causal reasoning.
    
    Governance remains observational - it never modifies causal artifacts directly.
    """
    
    # Identity
    governance_id: str                  # Unique governance identifier
    
    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...]  # Which sessions were evaluated?
    
    # Findings
    findings: Tuple[GovernanceFinding, ...]  # All findings
    
    # Violations (if any)
    violations: Tuple[str, ...] = ()    # Policy violations
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()  # Improvement suggestions
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @property
    def is_compliant(self) -> bool:
        """Check if all evaluated sessions are compliant."""
        return len(self.violations) == 0 and len(
            f for f in self.findings if f.finding_type == "error"
        ) == 0
    
    @property
    def finding_count(self) -> int:
        """Total number of findings."""
        return len(self.findings)


@dataclass(frozen=True)
class GovernanceReport:
    """
    A complete governance report with all stages.
    
    From initial check to final evaluation.
    """
    
    # Identity
    report_id: str                      # Unique report identifier
    
    # Evaluated artifacts
    evaluated_artifacts: Tuple[str, ...]  # What was evaluated?
    
    # Detailed findings
    detailed_findings: Tuple[GovernanceFinding, ...]
    
    # Summary statistics
    total_findings: int = 0             # Total findings
    error_count: int = 0                # Number of errors
    warning_count: int = 0              # Number of warnings
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None


def make_governance_evaluation(
    sessions: Tuple[str, ...],
    findings: List[GovernanceFinding],
) -> CausalGovernance:
    """Create a new governance evaluation."""
    return CausalGovernance(
        governance_id=f"governance:{uuid.uuid4().hex[:16]}",
        evaluated_sessions=sessions,
        findings=tuple(findings),
    )


__all__ = [
    "GovernanceFinding",
    "CausalGovernance",
    "GovernanceReport",
]