# Planning Validation - Phase 7.20
# ================================

"""
Canonical Planning Validation contracts for Phase 7.20.

Validation evaluates plan quality, dependency integrity, resource efficiency,
contingency completeness, execution readiness without modifying artifacts.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ValidationFindingKind(Enum):
    """Kinds of validation findings."""
    
    INCONSISTENT_DEPENDENCIES = "inconsistent_dependencies"  # Cycle in dependency graph
    INVALID_RESOURCE_ALLOCATION = "invalid_resource_allocation"  # Over-allocated resource
    MISSING_CONTINGENCY_PLAN = "missing_contingency_plan"     # Task has no backup
    UNSCHEDULABLE_TASK = "unschedulable_task"                 # Cannot be scheduled
    MISSING_PRECONDITION = "missing_precondition"             # Precondition not met


@dataclass(frozen=True)
class PlanningValidation:
    """
    Validation result for a planning session.
    
    Validation is observational - it evaluates without modifying artifacts.
    """
    
    # Identity
    validation_id: str                        # Unique validation identifier
    
    # Evaluated plan set
    evaluated_plan_set_id: Optional[str] = None  # Which plans were validated?
    
    # Validation results
    findings: Tuple[ValidationFinding, ...] = ()  # All findings from validation
    
    # Quality metrics
    is_valid: bool = True                     # Overall validity
    plan_count: int = 0                       # Number of plans validated
    task_count: int = 0                       # Total tasks in plans
    
    # Specific checks
    dependency_graph_valid: bool = True       # No cycles detected
    resource_allocation_valid: bool = True    # Resources not over-allocated
    contingency_plans_complete: bool = True   # All tasks have contingencies
    execution_ready: bool = False             # Ready for scheduler
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    originating_session_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        evaluated_plan_set_id: Optional[str] = None,
    ) -> PlanningValidation:
        """Create a new planning validation."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            evaluated_plan_set_id=evaluated_plan_set_id,
            execution_ready=True,  # Would be set after all checks
        )


@dataclass(frozen=True)
class ValidationFinding:
    """
    A single validation finding.
    
    Each finding records a specific issue discovered during validation.
    """
    
    # Identity
    finding_id: str                           # Unique finding identifier
    
    # Finding kind
    finding_kind: ValidationFindingKind       # What type of issue?
    
    # Location
    related_plan_id: Optional[str] = None     # Which plan has the issue?
    related_task_ids: Tuple[str, ...] = ()    # Affected tasks
    
    # Description
    description: str                          # Human-readable explanation
    severity: str = "warning"                 # "error", "warning", or "info"
    
    # Recommendation
    recommendation: Optional[str] = None      # How to fix it?
    
    # Metadata
    discovered_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        finding_kind: ValidationFindingKind,
        description: str,
        severity: str = "warning",
        related_plan_id: Optional[str] = None,
        related_task_ids: Tuple[str, ...] = (),
        recommendation: Optional[str] = None,
    ) -> ValidationFinding:
        """Create a new validation finding."""
        return cls(
            finding_id=f"finding:{uuid.uuid4().hex[:16]}",
            finding_kind=finding_kind,
            description=description,
            severity=severity,
            related_plan_id=related_plan_id,
            related_task_ids=related_task_ids,
            recommendation=recommendation,
        )


@dataclass(frozen=True)
class ValidationTrace:
    """
    Complete trace of validation operations.
    
    Each validation step is recorded for audit and debugging purposes.
    """
    
    # Identity
    trace_id: str                             # Unique trace identifier
    
    # All findings from this validation session
    all_findings: Tuple[ValidationFinding, ...] = ()
    
    # Validation steps performed
    validation_steps: Tuple[str, ...] = ()    # Step descriptions
    
    # Summary metrics
    total_findings: int = 0                   # Total issues found
    error_count: int = 0                      # Critical errors
    warning_count: int = 0                    # Warnings
    info_count: int = 0                       # Info messages
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        validation_steps: Tuple[str, ...] = (),
    ) -> ValidationTrace:
        """Create a new validation trace."""
        return cls(
            trace_id=f"validationtrace:{uuid.uuid4().hex[:16]}",
            validation_steps=validation_steps,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "PlanningValidation",
    "ValidationFindingKind",
    "ValidationFinding",
    "ValidationTrace",
]