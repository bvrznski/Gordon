# Stability Governance - Phase 7.26
# ==================================

"""
Canonical Stability Governance.

Governance evaluates stability correctness, homeostasis quality,
containment effectiveness, configuration safety, operational resilience,
and diagnostics.
"""

from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StabilityGovernanceFinding:
    """A finding from stability governance evaluation."""
    
    finding_id: str
    finding_type: str           # e.g., "incorrect_stabilization", "poor_homeostasis"
    severity: float             # 0.0 to 1.0
    description: str
    affected_session: Optional[str] = None


@dataclass(frozen=True)
class StabilityGovernance:
    """
    Governance evaluates stability operations.
    
    Evaluates:
        - Stability correctness (are we stabilizing what needs stabilizing?)
        - Homeostasis quality (is equilibrium assessment accurate?)
        - Containment effectiveness (are boundaries correct?)
        - Configuration safety (are proposed configs safe?)
        - Operational resilience (can we recover from failures?)
        - Diagnostics completeness (do we have enough info?)
    
    Governance remains observational and never modifies state.
    """
    
    governance_id: str
    governance_identity: str
    
    # Evaluated sessions
    evaluated_sessions: List[str] = field(default_factory=list)
    
    # Findings from evaluation
    findings: List[StabilityGovernanceFinding] = field(default_factory=list)
    
    # Violations (if any rules were broken)
    violations: List[str] = field(default_factory=list)
    
    # Recommendations for improvement
    recommendations: List[str] = field(default_factory=list)
    
    # Provenance
    provenance: str = "unknown"
    
    # Timing
    evaluated_at_utc: float = field(default_factory=time.time)
    
    @property
    def has_violations(self) -> bool:
        """Check if any violations were found."""
        return len(self.violations) > 0
    
    @property
    def finding_count(self) -> int:
        """Get the number of findings."""
        return len(self.findings)
    
    @classmethod
    def create(
        cls,
        governance_identity: str,
        evaluated_sessions: List[str] = None,
        provenance: str = "unknown",
    ) -> StabilityGovernance:
        """Create a new stability governance instance."""
        if evaluated_sessions is None:
            evaluated_sessions = []
        
        return cls(
            governance_id=f"gov:{uuid.uuid4().hex[:16]}",
            governance_identity=governance_identity,
            evaluated_sessions=evaluated_sessions,
            provenance=provenance,
        )


__all__ = [
    "StabilityGovernance",
    "StabilityGovernanceFinding",
]