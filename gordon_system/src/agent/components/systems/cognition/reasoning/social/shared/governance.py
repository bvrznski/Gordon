# Social Governance - Phase 7.32
# =============================

"""
Canonical Social Governance.

Governance evaluates:
- Model quality
- Belief quality  
- Intention quality
- Relationship quality
- Prediction quality
- Diagnostics

Governance remains observational.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


@dataclass(frozen=True)
class SocialGovernance:
    """
    Social governance evaluation result.
    
    Governance is OBSERVATIONAL - it only evaluates social artifacts,
    never modifies them directly. Produces findings and recommendations.
    """
    
    # Identity
    governance_id: str                        # Unique identifier
    
    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...] = ()
    
    # Findings (what was discovered)
    findings: Tuple[Dict[str, Any], ...] = ()
    
    # Violations (contract violations detected)
    violations: Tuple[Dict[str, Any], ...] = ()
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    governance_level: str = "default"
    
    @property
    def finding_count(self) -> int:
        """Count of governance findings."""
        return len(self.findings)
    
    @property
    def has_violations(self) -> bool:
        """Check if any violations were found."""
        return len(self.violations) > 0
    
    @classmethod
    def create(cls, sessions: List[str]) -> SocialGovernance:
        """Create a new governance evaluation."""
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple(sessions),
            created_at_utc=time.time(),
        )
    
    def with_finding(self, finding: Dict[str, Any]) -> SocialGovernance:
        """Return a copy with an additional finding."""
        return dataclass_replace(
            self,
            findings=self.findings + (finding,),
        )


@dataclass(frozen=True)
class GovernanceFinding:
    """
    A single governance finding.
    
    Includes:
        - Finding type (quality, consistency, etc.)
        - Description
        - Affected artifact
        - Severity level
    """
    
    finding_id: str                           # Unique identifier
    finding_type: str                         # quality, consistency, completeness
    description: str                          # What was found?
    affected_artifact: str                    # Which artifact is affected?
    severity: float = 0.5                     # 0.0 to 1.0
    
    @property
    def is_high_severity(self) -> bool:
        """Check if this is a high-severity finding."""
        return self.severity >= 0.8


__all__ = [
    "SocialGovernance",
    "GovernanceFinding",
]