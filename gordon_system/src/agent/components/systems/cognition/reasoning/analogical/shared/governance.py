# Analogy Governance - Phase 7.4
# =============================

"""
Canonical Analogy Governance Contract.

Governance evaluates analogies without modifying them directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class AnalogyGovernance:
    """
    Governance evaluation of an analogy session.
    
    Governance evaluates:
        - Mapping quality (are mappings structurally sound?)
        - Transfer correctness (is transfer done properly?)
        - Schema validity (are schemas valid abstractions?)
        - Structural consistency (is the overall structure coherent?)
        - False analogies (are we making invalid comparisons?)
        - Diagnostics (what can be improved?)
    
    Governance remains observational; it never modifies analogy artifacts directly.
    """
    
    # Identity
    governance_id: str                        # Unique identifier
    
    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...] = ()  # Which sessions were evaluated?
    
    # Findings
    findings: Tuple[Dict[str, Any], ...] = ()  # What did we find?
    
    # Violations (policy breaches)
    violations: Tuple[Dict[str, Any], ...] = ()
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()
    
    # Overall assessment
    is_compliant: bool = False                # Passed all governance checks?
    
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
    ) -> AnalogyGovernance:
        """Create a new governance evaluation."""
        return cls(
            governance_id=f"analogy_governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple(session_ids or []),
        )
    
    def record_violation(self, violation: Dict[str, Any]) -> "AnalogyGovernance":
        """Record a governance violation."""
        return dataclass_replace(
            self,
            violations=self.violations + (violation,),
        )
    
    def add_recommendation(self, recommendation: str) -> "AnalogyGovernance":
        """Add a governance recommendation."""
        return dataclass_replace(
            self,
            recommendations=self.recommendations + (recommendation,),
        )


@dataclass(frozen=True)
class GovernanceFindings:
    """
    Aggregated governance findings across multiple sessions.
    
    Used for reporting and system improvement.
    """
    
    # Identity
    findings_id: str                          # Unique identifier
    
    # Findings by category
    mapping_quality_issues: Tuple[str, ...] = ()
    transfer_errors: Tuple[str, ...] = ()
    schema_issues: Tuple[str, ...] = ()
    false_analogies_detected: Tuple[str, ...] = ()
    
    # Metrics
    total_sessions_evaluated: int = 0
    compliant_sessions: int = 0
    non_compliant_sessions: int = 0
    
    # Metadata
    generated_at_utc: float = field(default_factory=time.time)
    
    @property
    def pass_rate(self) -> float:
        """Calculate compliance pass rate."""
        if self.total_sessions_evaluated == 0:
            return 1.0
        return self.compliant_sessions / self.total_sessions_evaluated
    
    @classmethod
    def create(cls) -> GovernanceFindings:
        """Create a new findings set."""
        return cls(
            findings_id=f"governance_findings:{uuid.uuid4().hex[:16]}",
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AnalogyGovernance",
    "GovernanceFindings",
]