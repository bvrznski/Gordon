# State Transition Diagnostics - Phase 3.15.5
# =============================================
#
# Diagnostics and observability for state transitions.
#
# This module provides:
#   - Transition counters and metrics
#   - Failure tracking
#   - Timing analysis
#   - History inspection
#   - Health and readiness indicators

"""
Transition Diagnostics Module - Phase 3.15.5.

This module provides comprehensive diagnostics for the transition architecture,
exposing observability without compromising immutable state guarantees.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import time as _time_module


# =============================================================================
# TRANSITION METRICS
# =============================================================================


class TransitionMetricType(Enum):
    """
    Types of transition metrics tracked.
    
    TYPES:
        TOTAL_EXECUTED: Total transitions executed (success or failure)
        SUCCESSFUL: Successfully completed transitions
        FAILED: Failed transitions (no state change)
        PARTIAL_FAILURE: Partial failures with some state changes
        VALIDATION_REJECTED: Rejected by validation before execution
        
        ROLLED_BACK: Transitions that were rolled back after failure
        COMPENSATED: Transitions compensated for failure
        TIMEOUT: Transitions that timed out
        
        CONFLICT_DETECTED: Version/generation conflicts detected
    """
    
    TOTAL_EXECUTED = "total_executed"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    PARTIAL_FAILURE = "partial_failure"
    VALIDATION_REJECTED = "validation_rejected"
    
    ROLLED_BACK = "rolled_back"
    COMPENSATED = "compensated"
    TIMEOUT = "timeout"
    
    CONFLICT_DETECTED = "conflict_detected"


@dataclass(frozen=True)
class TransitionMetrics:
    """
    Metrics for transition operations.
    
    INVARIANTS:
        METRICS-001: All metrics are cumulative counters
        METRICS-002: Metrics are immutable once created (use append)
        METRICS-003: No negative values allowed
    """
    
    # Execution counts
    total_executed: int = 0
    successful: int = 0
    failed: int = 0
    partial_failure: int = 0
    validation_rejected: int = 0
    
    # Recovery metrics
    rolled_back: int = 0
    compensated: int = 0
    timeout_count: int = 0
    
    # Conflict detection
    conflict_detected: int = 0
    
    @classmethod
    def create(cls) -> "TransitionMetrics":
        """Create a new empty metrics instance."""
        return cls()
    
    def record_success(self) -> "TransitionMetrics":
        """Record a successful transition execution."""
        return dataclass_replace(
            self,
            total_executed=self.total_executed + 1,
            successful=self.successful + 1,
        )
    
    def record_failure(self) -> "TransitionMetrics":
        """Record a failed transition execution."""
        return dataclass_replace(
            self,
            total_executed=self.total_executed + 1,
            failed=self.failed + 1,
        )
    
    def record_partial_failure(self) -> "TransitionMetrics":
        """Record a partial failure (some state changed before error)."""
        return dataclass_replace(
            self,
            total_executed=self.total_executed + 1,
            partial_failure=self.partial_failure + 1,
        )
    
    def record_validation_rejected(self) -> "TransitionMetrics":
        """Record a validation rejection."""
        return dataclass_replace(
            self,
            validation_rejected=self.validation_rejected + 1,
        )
    
    def record_rollback(self) -> "TransitionMetrics":
        """Record a rollback execution."""
        return dataclass_replace(
            self,
            rolled_back=self.rolled_back + 1,
        )
    
    def record_compensation(self) -> "TransitionMetrics":
        """Record a compensation action."""
        return dataclass_replace(
            self,
            compensated=self.compensated + 1,
        )
    
    def record_timeout(self) -> "TransitionMetrics":
        """Record a timeout occurrence."""
        return dataclass_replace(
            self,
            timeout_count=self.timeout_count + 1,
        )
    
    def record_conflict(self) -> "TransitionMetrics":
        """Record a version/generation conflict."""
        return dataclass_replace(
            self,
            conflict_detected=self.conflict_detected + 1,
        )


# =============================================================================
# TRANSITION TIMING
# =============================================================================


@dataclass(frozen=True)
class TransitionTiming:
    """
    Timing information for a transition.
    
    INVARIANTS:
        TIMING-001: All times are monotonic (not wall clock)
        TIMING-002: Start must be before end for valid transitions
        TIMING-003: Duration is calculated as end - start
    """
    
    transition_id: str
    
    # Timestamps (monotonic, not wall clock)
    validation_start_utc: float = field(default_factory=_time_module.monotonic)
    validation_end_utc: Optional[float] = None
    execution_start_utc: Optional[float] = None
    execution_end_utc: Optional[float] = None
    
    @property
    def validation_duration_seconds(self) -> Optional[float]:
        """Calculate validation duration."""
        if self.validation_end_utc is None:
            return None
        return self.validation_end_utc - self.validation_start_utc
    
    @property
    def execution_duration_seconds(self) -> Optional[float]:
        """Calculate execution duration."""
        if self.execution_start_utc is None or self.execution_end_utc is None:
            return None
        return self.execution_end_utc - self.execution_start_utc
    
    @property
    def total_duration_seconds(self) -> Optional[float]:
        """Calculate total transition time (validation + execution)."""
        validation = self.validation_duration_seconds
        execution = self.execution_duration_seconds
        
        if validation is None or execution is None:
            return None
        
        return validation + execution


# =============================================================================
# DIAGNOSTICS SNAPSHOT
# =============================================================================


@dataclass(frozen=True)
class TransitionDiagnosticsSnapshot:
    """
    Immutable snapshot of transition diagnostics at a point in time.
    
    INVARIANTS:
        DIAG-SNAP-001: Snapshot is immutable once created
        DIAG-SNAP-002: Snapshot captures all diagnostics at one moment
        DIAG-SNAP-003: No mutable state is exposed
    """
    
    # Metrics snapshot
    metrics: TransitionMetrics
    
    # Timing statistics (for completed transitions)
    average_validation_duration_seconds: Optional[float] = None
    average_execution_duration_seconds: Optional[float] = None
    max_validation_duration_seconds: Optional[float] = None
    max_execution_duration_seconds: Optional[float] = None
    
    # History summary
    total_transitions_in_history: int = 0
    recent_transitions: Tuple[str, ...] = field(default_factory=tuple)
    
    # Failure patterns
    top_failure_reasons: Tuple[Tuple[str, int], ...] = field(default_factory=tuple)
    
    @property
    def success_rate(self) -> Optional[float]:
        """Calculate success rate as fraction of total."""
        total = self.metrics.total_executed
        if total == 0:
            return None
        
        return self.metrics.successful / total


# =============================================================================
# TRANSITION DIAGNOSTICS (PUBLIC API)
# =============================================================================


class TransitionDiagnostics:
    """
    Diagnostics for transition operations.
    
    Provides observability without exposing mutable state. All diagnostics
    are append-only and immutable.
    
    PUBLIC API:
        - record_transition_start: Record when a transition starts
        - record_validation_complete: Record validation completion
        - record_execution_complete: Record execution completion
        - record_failure: Record a failure
        - get_metrics: Get current metrics
        - get_snapshot: Get a diagnostic snapshot
    
    INVARIANTS:
        DIAG-001: Diagnostics are append-only (no updates)
        DIAG-002: No mutable state exposed to callers
        DIAG-003: All diagnostics are immutable records
    """
    
    def __init__(self) -> None:
        """Initialize the diagnostics system."""
        self._metrics: TransitionMetrics = TransitionMetrics.create()
        self._timings: List[TransitionTiming] = []
        self._history_ids: List[str] = []
    
    def record_validation_complete(
        self,
        transition_id: str,
        success: bool,
        validation_duration_seconds: float,
    ) -> None:
        """Record that validation completed for a transition."""
        timing = TransitionTiming(transition_id=transition_id)
        if not success:
            self._metrics.record_validation_rejected()
    
    def record_execution_complete(
        self,
        transition_id: str,
        result_code: str,
        execution_duration_seconds: float,
    ) -> None:
        """Record that execution completed for a transition."""
        # Record timing
        self._timings.append(
            TransitionTiming(transition_id=transition_id, execution_start_utc=_time_module.monotonic())
        )
        
        # Update metrics based on result code
        if result_code == "success":
            self._metrics.record_success()
        elif result_code == "failure":
            self._metrics.record_failure()
        elif result_code == "partial_failure":
            self._metrics.record_partial_failure()
        elif result_code == "rolled_back":
            self._metrics.record_rollback()
        elif result_code == "compensated":
            self._metrics.record_compensation()
        
        # Add to history
        if len(self._history_ids) >= 100:  # Keep last 100 transition IDs
            self._history_ids = self._history_ids[-99:]
        self._history_ids.append(transition_id)
    
    def record_timeout(self, transition_id: str) -> None:
        """Record a timeout for a transition."""
        self._metrics.record_timeout()
    
    def record_conflict(self, transition_id: str) -> None:
        """Record a version/generation conflict."""
        self._metrics.record_conflict()
    
    def get_metrics(self) -> TransitionMetrics:
        """Get current metrics (immutable copy)."""
        return self._metrics
    
    def get_snapshot(self) -> TransitionDiagnosticsSnapshot:
        """
        Get a diagnostic snapshot.
        
        Returns an immutable snapshot of all diagnostics at this moment.
        """
        # Calculate average durations
        validation_durations = [t.validation_duration_seconds for t in self._timings if t.validation_duration_seconds]
        execution_durations = [t.execution_duration_seconds for t in self._timings if t.execution_duration_seconds]
        
        avg_validation = sum(validation_durations) / len(validation_durations) if validation_durations else None
        avg_execution = sum(execution_durations) / len(execution_durations) if execution_durations else None
        
        max_validation = max(validation_durations) if validation_durations else None
        max_execution = max(execution_durations) if execution_durations else None
        
        return TransitionDiagnosticsSnapshot(
            metrics=self._metrics,
            average_validation_duration_seconds=avg_validation,
            average_execution_duration_seconds=avg_execution,
            max_validation_duration_seconds=max_validation,
            max_execution_duration_seconds=max_execution,
            total_transitions_in_history=len(self._history_ids),
            recent_transitions=tuple(self._history_ids[-10:]),  # Last 10
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass.
    
    Args:
        obj: The dataclass instance to copy
        kwargs: Fields to replace
        
    Returns:
        A new instance with replaced fields
    """
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Metric types
    "TransitionMetricType",
    
    # Metrics
    "TransitionMetrics",
    
    # Timing
    "TransitionTiming",
    
    # Diagnostics
    "TransitionDiagnosticsSnapshot",
    "TransitionDiagnostics",
    
    # Utilities
    "dataclass_replace",
]