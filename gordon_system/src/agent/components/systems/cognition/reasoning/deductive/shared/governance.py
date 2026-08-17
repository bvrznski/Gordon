# Deduction Governance - Phase 7.1
# ================================

"""
Canonical Deduction Governance Contract.

Deduction Governance evaluates reasoning without modifying it directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DeductionGovernance:
    """
    Governance evaluation of deduction.
    
    Governance evaluates:
        - Proof validity (is the reasoning sound?)
        - Rule correctness (are rules applied correctly?)
        - Trace completeness (is all reasoning recorded?)
        - Contradiction handling (were contradictions properly analyzed?)
        - Resource efficiency (did it complete within limits?)
    
    Governance remains observational; it never modifies deductions directly.
    """
    
    # Identity
    governance_id: str                      # Unique identifier
    
    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...] = ()
    
    # Findings
    findings: Tuple[Dict[str, Any], ...] = ()
    
    # Violations (policy breaches)
    violations: Tuple[Dict[str, Any], ...] = ()
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()
    
    # Overall assessment
    is_compliant: bool = False              # Passed all governance checks?
    
    # Timing
    evaluated_at_utc: float = field(default_factory=time.time)
    
    @property
    def violation_count(self) -> int:
        """Count of governance violations."""
        return len(self.violations)
    
    @classmethod
    def create(
        cls,
        session_ids: Optional[List[str]] = None,
    ) -> DeductionGovernance:
        """Create a new governance evaluation."""
        return cls(
            governance_id=f"deduction_governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple(session_ids or []),
        )
    
    def record_violation(self, violation: Dict[str, Any]) -> "DeductionGovernance":
        """Record a governance violation."""
        return dataclass_replace(
            self,
            violations=self.violations + (violation,),
        )
    
    def add_recommendation(self, recommendation: str) -> "DeductionGovernance":
        """Add a governance recommendation."""
        return dataclass_replace(
            self,
            recommendations=self.recommendations + (recommendation,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DeductionGovernance",
]