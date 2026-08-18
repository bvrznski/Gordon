# Planning Failure - Phase 7.20
# =============================

"""
Canonical Planning Failure contracts for Phase 7.20.

Planning failures include:
    - Unsatisfied dependencies (cycles)
    - Resource exhaustion
    - Cyclic task graphs
    - Unschedulable plans
    - Missing contingencies
    
Failures are always explicit and never silently discarded.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class FailureKind(Enum):
    """Kinds of planning failures."""
    
    CYCLIC_DEPENDENCY = "cyclic_dependency"           # Dependency graph has a cycle
    RESOURCE_EXHAUSTED = "resource_exhausted"         # Not enough resources available
    UNSCHEDULABLE_TASK = "unschedulable_task"         # Task cannot be scheduled
    MISSING_CONTINGENCY = "missing_contingency"       # No contingency for critical task
    INVALID_PLAN_GRAPH = "invalid_plan_graph"         # Plan structure is invalid


@dataclass(frozen=True)
class PlanningFailure:
    """
    A planning failure record.
    
    Each failure includes diagnostics and potential recovery options.
    """
    
    # Identity
    failure_id: str                           # Unique failure identifier
    
    # Failure kind
    failure_kind: FailureKind                 # What type of failure?
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()         # Detailed diagnostic information
    affected_tasks: Tuple[str, ...] = ()      # Tasks involved in the failure
    
    # Recovery options
    recovery_options: Tuple[str, ...] = ()    # How can this be recovered?
    
    # Partial execution info
    partial_execution_possible: bool = False  # Can any part still execute?
    executable_subgraphs: Tuple[str, ...] = ()  # Which subgraphs are still valid?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    originating_session_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        failure_kind: FailureKind,
        diagnostics: Tuple[str, ...] = (),
        recovery_options: Tuple[str, ...] = (),
        affected_tasks: Tuple[str, ...] = (),
    ) -> PlanningFailure:
        """Create a new planning failure record."""
        return cls(
            failure_id=f"failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            diagnostics=diagnostics,
            recovery_options=recovery_options,
            affected_tasks=affected_tasks,
        )


@dataclass(frozen=True)
class FailureTrace:
    """
    Complete trace of all failures in a planning session.
    
    Each failure is recorded with full context for debugging and analysis.
    """
    
    # Identity
    trace_id: str                             # Unique trace identifier
    
    # All failures from this session
    all_failures: Tuple[PlanningFailure, ...] = ()
    
    # Failure recovery attempts
    recovery_attempts: Tuple[str, ...] = ()   # What was tried to recover?
    recovery_successes: int = 0               # How many recovered?
    
    # Summary metrics
    total_failures: int = 0                   # Total failures encountered
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_fully_recovered(self) -> bool:
        """Check if all failures were successfully recovered."""
        return self.recovery_successes >= self.total_failures and self.total_failures > 0
    
    @classmethod
    def create(
        cls,
    ) -> FailureTrace:
        """Create a new failure trace."""
        return cls(
            trace_id=f"failuretrace:{uuid.uuid4().hex[:16]}",
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "PlanningFailure",
    "FailureKind",
    "FailureTrace",
]