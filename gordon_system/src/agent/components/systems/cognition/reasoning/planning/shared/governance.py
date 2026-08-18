# Planning Governance - Phase 7.20
# ================================

"""
Canonical Planning Governance contracts for Phase 7.20.

Governance evaluates plan quality, dependency integrity, resource efficiency,
contingency completeness, execution readiness without modifying artifacts.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class PlanningGovernance:
    """
    Governance evaluation for a planning session.
    
    Governance is observational - it evaluates without modifying artifacts.
    
    Governance rules include:
        - Detect cyclic dependency graphs
        - Validate resource allocations
        - Ensure deterministic planning
        - Verify plan quality metrics
    """
    
    # Identity
    governance_id: str                        # Unique governance identifier
    
    # Evaluated sessions
    evaluated_sessions: Tuple[PlanningSessionGovernance, ...] = ()
    
    # Findings from governance review
    findings: Tuple[GovernanceFinding, ...] = ()
    
    # Violations detected
    violations: Tuple[str, ...] = ()          # Rule violations found
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()     # How to improve?
    
    # Quality metrics
    total_plans_evaluated: int = 0            # Number of plans reviewed
    dependency_integrity_valid: bool = True   # No cycles detected
    resource_efficiency_valid: bool = True    # Resources properly allocated
    contingency_completeness_valid: bool = True  # All tasks have contingencies
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        evaluated_sessions: Tuple[PlanningSessionGovernance, ...] = (),
    ) -> PlanningGovernance:
        """Create a new planning governance record."""
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=evaluated_sessions,
        )


@dataclass(frozen=True)
class GovernanceFindingKind(Enum):
    """Kinds of governance findings."""
    
    CYCLIC_DEPENDENCY = "cyclic_dependency"
    INVALID_RESOURCE_ALLOCATION = "invalid_resource_allocation"
    NONDETERMINISTIC_PLANNING = "nondeterministic_planning"
    MISSING_CONTINGENCY_PLAN = "missing_contingency_plan"
    PROVENANCE_INCOMPLETE = "provenance_incomplete"


@dataclass(frozen=True)
class GovernanceFinding:
    """
    A governance finding about a planning session.
    
    Each finding records a specific governance evaluation result.
    """
    
    # Identity
    finding_id: str                           # Unique finding identifier
    
    # Finding kind
    finding_kind: GovernanceFindingKind       # What was found?
    
    # Description
    description: str                          # Human-readable explanation
    
    # Affected entity
    affected_session_id: Optional[str] = None  # Which session?
    affected_plan_id: Optional[str] = None     # Which plan?
    
    # Severity
    severity: str = "warning"                 # "error", "warning", or "info"
    
    # Metadata
    discovered_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        finding_kind: GovernanceFindingKind,
        description: str,
        severity: str = "warning",
        affected_session_id: Optional[str] = None,
        affected_plan_id: Optional[str] = None,
    ) -> GovernanceFinding:
        """Create a new governance finding."""
        return cls(
            finding_id=f"governance_finding:{uuid.uuid4().hex[:16]}",
            finding_kind=finding_kind,
            description=description,
            severity=severity,
            affected_session_id=affected_session_id,
            affected_plan_id=affected_plan_id,
        )


@dataclass(frozen=True)
class PlanningSessionGovernance:
    """
    Governance evaluation for a single planning session.
    
    Each session is evaluated for compliance with governance rules.
    """
    
    # Identity
    governance_id: str                        # Unique governance identifier
    
    # Session being evaluated
    evaluated_session_id: Optional[str] = None  # Which session?
    
    # Compliance results
    laws_violated: Tuple[str, ...] = ()       # Which Planning Laws were violated?
    rules_violated: Tuple[str, ...] = ()      # Other governance rules
    
    # Quality metrics
    plan_quality_score: float = 1.0           # 0.0 to 1.0
    dependency_integrity_score: float = 1.0   # How clean are the dependencies?
    
    # Determinism check
    is_deterministic: bool = True             # Same input → same output?
    
    # Provenance completeness
    provenance_complete: bool = True          # All tracking in place?
    
    # Metadata
    evaluated_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        evaluated_session_id: Optional[str] = None,
    ) -> PlanningSessionGovernance:
        """Create a new session governance record."""
        return cls(
            governance_id=f"session_governance:{uuid.uuid4().hex[:16]}",
            evaluated_session_id=evaluated_session_id,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "PlanningGovernance",
    "GovernanceFindingKind",
    "GovernanceFinding",
    "PlanningSessionGovernance",
]