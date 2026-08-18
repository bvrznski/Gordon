# Dialectical Governance - Phase 7.17
# ===================================

"""
Canonical Dialectical Governance Contract.

Dialectical Governance evaluates reasoning without modifying it directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DialecticalGovernance:
    """
    Governance evaluation of dialectical processes.

    Governance evaluates:
        - Argument quality (are arguments well-formed?)
        - Conflict completeness (were all conflicts analyzed?)
        - Synthesis validity (is the synthesis correct?)
        - Consensus robustness (is the consensus stable?)
        - Reasoning diversity (were multiple perspectives considered?)

    Governance remains observational; it never modifies dialectical artifacts directly.
    """

    # Identity
    governance_id: str                      # Unique identifier

    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...] = ()

    # Findings (what was found?)
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
    ) -> DialecticalGovernance:
        """Create a new governance evaluation."""
        return cls(
            governance_id=f"dialectical_governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple(session_ids or []),
        )

    def record_violation(self, violation: Dict[str, Any]) -> "DialecticalGovernance":
        """Record a governance violation."""
        return dataclass_replace(
            self,
            violations=self.violations + (violation,),
        )

    def add_recommendation(self, recommendation: str) -> "DialecticalGovernance":
        """Add a governance recommendation."""
        return dataclass_replace(
            self,
            recommendations=self.recommendations + (recommendation,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DialecticalGovernance",
]