# Execution Reasoning Failure - Phase 7.21
# ========================================

"""
Canonical Execution Failure handling for Phase 7.21.

Execution failures include authorization denial, resource starvation,
deadlock, livelock, partial rollback failure, and checkpoint corruption.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class FailureKind(Enum):
    """Kinds of execution failures."""
    
    AUTHORIZATION_DENIED = "authorization_denied"       # Authorization failed
    RESOURCE_STARVATION = "resource_starvation"         # Resources unavailable
    DEADLOCK = "deadlock"                               # Deadlock detected
    LIVELOCK = "livelock"                               # Livelock detected
    ROLLBACK_FAILURE = "rollback_failure"               # Rollback failed
    CHECKPOINT_CORRUPTION = "checkpoint_corruption"     # Checkpoint invalid


@dataclass(frozen=True)
class ExecutionFailure:
    """
    Execution Failure records execution failures.
    
    Failures include:
        - Authorization denial
        - Resource starvation
        - Deadlock
        - Livelock
        - Partial rollback failure
        - Checkpoint corruption
    
    Failures remain explicit and inspectable.
    """
    
    # Identity
    failure_identity: str                       # Unique failure identifier
    
    # Failure details
    failure_kind: FailureKind                   # What kind of failure?
    diagnostics: Tuple[str, ...]                # Diagnostic information
    
    # Recovery options
    recovery_options: Tuple[str, ...] = ()      # Possible recovery actions
    
    # Timestamps
    detected_at_utc: float = field(default_factory=time.time)
    resolved_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate how long the failure persisted."""
        if self.resolved_at_utc:
            return self.resolved_at_utc - self.detected_at_utc
        return 0.0
    
    @classmethod
    def create(
        cls,
        failure_kind: FailureKind,
        diagnostics: Tuple[str, ...],
        recovery_options: Tuple[str, ...] = (),
    ) -> ExecutionFailure:
        """Create a new execution failure record."""
        return cls(
            failure_identity=f"failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            diagnostics=diagnostics,
            recovery_options=recovery_options,
        )


@dataclass(frozen=True)
class FailureTrace:
    """
    Trace of failures for inspection.
    
    Enables replay and verification of failure handling decisions.
    """
    
    # Identity
    trace_identity: str
    
    # Failures in the trace
    recorded_failures: Tuple[ExecutionFailure, ...]
    
    # Diagnostics summary
    diagnostics_summary: Tuple[str, ...] = ()
    
    @classmethod
    def create(
        cls,
        recorded_failures: Tuple[ExecutionFailure, ...],
        diagnostics_summary: Tuple[str, ...] = (),
    ) -> FailureTrace:
        """Create a new failure trace."""
        return cls(
            trace_identity=f"failure_trace:{uuid.uuid4().hex[:16]}",
            recorded_failures=recorded_failures,
            diagnostics_summary=diagnostics_summary,
        )
    
    @property
    def total_failures(self) -> int:
        """Total number of recorded failures."""
        return len(self.recorded_failures)


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ExecutionFailure",
    "FailureKind",
    "FailureTrace",
]