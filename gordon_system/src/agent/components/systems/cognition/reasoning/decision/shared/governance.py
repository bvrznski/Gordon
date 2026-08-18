# Decision Governance - Phase 7.19
# ===============================

"""
Canonical Decision Governance Contract.

Governance evaluates decision quality, utility estimation,
confidence calibration, policy compliance, and diagnostics.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DecisionGovernance:
    """
    Governance evaluation for decision sessions.
    
    Governance remains observational; it never modifies decision artifacts directly.
    """
    
    # Identity
    governance_id: str                      # Unique identifier
    
    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...] = ()  # Session IDs evaluated
    
    # Findings (quality issues detected)
    findings: Tuple[str, ...] = ()          # Quality findings
    
    # Violations (contract violations)
    violations: Tuple[str, ...] = ()        # Contract violations
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()   # How to improve?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def governance_passed(self) -> bool:
        """Check if governance evaluation passed (no violations)."""
        return len(self.violations) == 0
    
    @classmethod
    def create(
        cls,
        evaluated_sessions: Optional[List[str]] = None,
        findings: Optional[List[str]] = None,
        violations: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None,
    ) -> DecisionGovernance:
        """Create a new governance evaluation."""
        return cls(
            governance_id=f"decision_governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple(evaluated_sessions or []),
            findings=tuple(findings or []),
            violations=tuple(violations or []),
            recommendations=tuple(recommendations or []),
        )


__all__ = [
    "DecisionGovernance",
]