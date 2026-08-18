# World-Model Reasoning Governance - Phase 7.44
# =================================

"""
Canonical World Model Governance.

Governance evaluates world model quality without modifying artifacts.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class GovernanceFinding:
    """
    A governance evaluation finding.
    """
    
    finding_id: str
    
    kind: str
    result: str  # "pass" or "fail"
    
    description: Optional[str] = None
    severity: float = 1.0
    confidence: float = 1.0
    
    timestamp_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class WorldGovernance:
    """
    World governance evaluation.
    """
    
    governance_id: str
    
    evaluated_sessions: List[str] = field(default_factory=list)
    findings: List[GovernanceFinding] = field(default_factory=list)
    
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    
    recommendations: List[str] = field(default_factory=list)
    
    timestamp_utc: float = field(default_factory=time.time)
    provenance: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        provenance: Optional[str] = None,
    ) -> WorldGovernance:
        """Create a new world governance evaluation."""
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=[],
            findings=[],
            total_checks=0,
            passed_checks=0,
            failed_checks=0,
            recommendations=[],
            provenance=provenance,
        )
    
    def with_finding(self, finding: GovernanceFinding) -> WorldGovernance:
        """Add a governance finding."""
        new_findings = self.findings + [finding]
        
        return dataclass_replace(
            self,
            findings=new_findings,
            total_checks=self.total_checks + 1,
            passed_checks=self.passed_checks + (1 if finding.result == "pass" else 0),
            failed_checks=self.failed_checks + (0 if finding.result == "pass" else 1),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "GovernanceFinding",
    "WorldGovernance",
]