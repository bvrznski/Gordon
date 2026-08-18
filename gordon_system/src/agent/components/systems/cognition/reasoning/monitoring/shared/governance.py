# Monitoring Governance Contract - Phase 7.22
# ===========================================

"""
Canonical Monitoring Governance.

Governance evaluates monitoring for completeness, consistency, and correctness.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class GovernanceFinding:
    """
    A finding from governance evaluation.
    """
    
    # Identity
    finding_id: str                           # Unique finding identifier
    
    # Category
    category: str                             # What kind of finding?
    severity: str = "info"                    # info, warning, error
    
    # Description
    description: str = ""                     # Human-readable explanation
    
    # Evidence
    supporting_observations: List[str] = field(default_factory=list)
    
    # Recommendation
    recommendation: Optional[str] = None      # How to fix it


@dataclass(frozen=True)
class MonitoringGovernance:
    """
    Governance evaluation for monitoring sessions.
    
    Governance evaluates:
        - Observation completeness
        - State consistency  
        - Supervision correctness
        - Anomaly quality
        - Progress estimation accuracy
    
    Governance remains observational (never modifies artifacts).
    """
    
    # Identity
    governance_id: str                        # Unique governance identifier
    
    # Evaluated sessions
    evaluated_sessions: List[str] = field(default_factory=list)
    
    # Findings
    findings: List[GovernanceFinding] = field(default_factory=list)
    
    # Violations (contract violations detected)
    violations: List[str] = field(default_factory=list)
    
    # Recommendations for improvement
    recommendations: List[str] = field(default_factory=list)
    
    # Governance metrics
    observations_checked: int = 0
    anomalies_validated: int = 0
    state_consistency_verified: bool = False
    
    # Timing
    evaluated_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def finding_count(self) -> int:
        """Get the number of findings."""
        return len(self.findings)
    
    @property
    def has_violations(self) -> bool:
        """Check if any violations exist."""
        return len(self.violations) > 0
    
    def add_finding(
        self,
        category: str,
        severity: str = "info",
        description: str = "",
        supporting_observations: Optional[List[str]] = None,
        recommendation: Optional[str] = None,
    ) -> MonitoringGovernance:
        """Add a governance finding."""
        new_findings = list(self.findings)
        
        new_findings.append(GovernanceFinding(
            finding_id=f"finding:{uuid.uuid4().hex[:16]}",
            category=category,
            severity=severity,
            description=description,
            supporting_observations=supporting_observations or [],
            recommendation=recommendation,
        ))
        
        return dataclass_replace(
            self,
            findings=new_findings,
        )
    
    def add_violation(self, violation: str) -> MonitoringGovernance:
        """Add a contract violation."""
        new_violations = list(self.violations)
        if violation not in new_violations:
            new_violations.append(violation)
        
        return dataclass_replace(
            self,
            violations=new_violations,
        )
    
    def add_recommendation(self, recommendation: str) -> MonitoringGovernance:
        """Add a governance recommendation."""
        new_recommendations = list(self.recommendations)
        if recommendation not in new_recommendations:
            new_recommendations.append(recommendation)
        
        return dataclass_replace(
            self,
            recommendations=new_recommendations,
        )
    
    def complete(self) -> MonitoringGovernance:
        """Mark governance evaluation as completed."""
        return dataclass_replace(
            self,
            completed_at_utc=time.time(),
        )
    
    @classmethod
    def create(
        cls,
        evaluated_sessions: Optional[List[str]] = None,
    ) -> MonitoringGovernance:
        """Create a new governance evaluation session."""
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=evaluated_sessions or [],
            evaluated_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "MonitoringGovernance",
    "GovernanceFinding",
]