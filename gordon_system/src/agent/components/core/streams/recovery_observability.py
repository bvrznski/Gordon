# Stream Recovery Observability - Phase 3.11.7
# ============================================

"""
Observability infrastructure for stream recovery operations.

This module implements observability for the recovery lifecycle:
    
    Failure Detection → Recovery Planning → Checkpoint Restoration → 
    Replay Execution → Validation → Resumption
    
All events are passive (observational only) and never affect runtime behavior.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import time


# =============================================================================
# OBSERVABILITY EVENTS
# =============================================================================

class RecoveryEventType(Enum):
    """
    Types of recovery-related observability events.
    
    Event Categories:
        FAILURE: Failure detection and classification
        PLANNING: Recovery planning decisions
        RESTORATION: Checkpoint restoration operations
        REPLAY: Replay-assisted recovery operations
        VALIDATION: Integrity and state validation
        RESUMPTION: Stream resumption after recovery
    """
    
    # Failure events
    FAILURE_DETECTED = "failure_detected"
    """A failure was detected."""
    
    FAILURE_CLASSIFIED = "failure_classified"
    """Failure was classified with category and severity."""
    
    # Planning events
    RECOVERY_PLANNED = "recovery_planned"
    """Recovery plan was created."""
    
    PLAN_EXECUTING = "plan_executing"
    """Recovery plan is executing."""
    
    PLAN_COMPLETED = "plan_completed"
    """Recovery plan completed successfully."""
    
    PLAN_FAILED = "plan_failed"
    """Recovery plan failed."""
    
    # Checkpoint events
    CHECKPOINT_SELECTED = "checkpoint_selected"
    """A checkpoint was selected for restoration."""
    
    CHECKPOINT_VALIDATED = "checkpoint_validated"
    """Checkpoint integrity verified."""
    
    CHECKPOINT_RESTORED = "checkpoint_restored"
    """Checkpoint restored successfully."""
    
    # Replay events
    REPLAY_STARTED = "replay_started"
    """Replay operation started."""
    
    REPLAY_RECORD_RECEIVED = "replay_record_received"
    """Record received during replay."""
    
    REPLAY_COMPLETED = "replay_completed"
    """Replay completed successfully."""
    
    # Validation events
    INTEGRITY_CHECK_PASSED = "integrity_check_passed"
    """Integrity check passed."""
    
    INTEGRITY_CHECK_FAILED = "integrity_check_failed"
    """Integrity check failed."""
    
    VALIDATION_COMPLETED = "validation_completed"
    """Validation completed."""
    
    # Resumption events
    RESUMPTION_INITIATED = "resumption_initiated"
    """Resumption process initiated."""
    
    RESUMPTION_COMPLETED = "resumption_completed"
    """Stream resumed successfully."""
    
    # Degraded operation events
    DEGRADED_MODE_ENTERED = "degraded_mode_entered"
    """Entered degraded operation mode."""
    
    DEGRADED_MODE_EXITED = "degraded_mode_exited"
    """Exited degraded operation mode."""


@dataclass(frozen=True)
class RecoveryEvent:
    """
    Immutable recovery observability event.
    """
    
    event_id: str
    event_type: RecoveryEventType
    
    timestamp_utc: float = field(default_factory=time.time)
    
    # Context
    stream_id: Optional[str] = None
    generation_id: Optional[int] = None
    
    session_id: Optional[str] = None  # Recovery session ID
    plan_id: Optional[str] = None     # Recovery plan ID
    
    # Event-specific data
    failure_category: Optional[str] = None
    severity: Optional[str] = None
    
    decision: Optional[str] = None  # RecoveryDecision value
    checkpoint_id: Optional[str] = None
    
    record_count: int = 0  # Records affected (replay, etc.)
    
    duration_seconds: float = 0.0
    
    status: str = "success"  # success, failure, warning
    error_message: str = ""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp_utc": self.timestamp_utc,
            "stream_id": self.stream_id,
            "generation_id": self.generation_id,
            "session_id": self.session_id,
            "plan_id": self.plan_id,
            "failure_category": self.failure_category,
            "severity": self.severity,
            "decision": self.decision,
            "checkpoint_id": self.checkpoint_id,
            "record_count": self.record_count,
            "duration_seconds": self.duration_seconds,
            "status": self.status,
            "error_message": self.error_message,
            "metadata": dict(self.metadata),
        }


# =============================================================================
# OBSERVABILITY REPORTER
# =============================================================================

class RecoveryObservabilityReporter:
    """
    Reporter for recovery observability events.
    
    This is a passive observer - it only records events, never affects behavior.
    """
    
    def __init__(self):
        """Initialize the observability reporter."""
        self._events: List[RecoveryEvent] = []
        self._event_counter = 0
    
    def record_event(self, event: RecoveryEvent) -> None:
        """
        Record a recovery event.
        
        Args:
            event: The event to record
        """
        self._events.append(event)
    
    def failure_detected(
        self,
        stream_id: str,
        category: str,
        severity: str,
        generation_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RecoveryEvent:
        """Record a failure detection event."""
        self._event_counter += 1
        event = RecoveryEvent(
            event_id=f"ev:{time.monotonic_ns()}:{self._event_counter}",
            event_type=RecoveryEventType.FAILURE_DETECTED,
            stream_id=stream_id,
            generation_id=generation_id,
            failure_category=category,
            severity=severity,
            metadata=metadata or {},
        )
        self.record_event(event)
        return event
    
    def recovery_planned(
        self,
        stream_id: str,
        decision: str,
        plan_id: Optional[str] = None,
        generation_id: Optional[int] = None,
        checkpoint_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RecoveryEvent:
        """Record a recovery planning event."""
        self._event_counter += 1
        event = RecoveryEvent(
            event_id=f"ev:{time.monotonic_ns()}:{self._event_counter}",
            event_type=RecoveryEventType.RECOVERY_PLANNED,
            stream_id=stream_id,
            generation_id=generation_id,
            plan_id=plan_id,
            decision=decision,
            checkpoint_id=checkpoint_id,
            metadata=metadata or {},
        )
        self.record_event(event)
        return event
    
    def replay_started(
        self,
        stream_id: str,
        checkpoint_id: Optional[str] = None,
        generation_id: Optional[int] = None,
        record_count: int = 0,
    ) -> RecoveryEvent:
        """Record a replay started event."""
        self._event_counter += 1
        event = RecoveryEvent(
            event_id=f"ev:{time.monotonic_ns()}:{self._event_counter}",
            event_type=RecoveryEventType.REPLAY_STARTED,
            stream_id=stream_id,
            generation_id=generation_id,
            checkpoint_id=checkpoint_id,
            record_count=record_count,
        )
        self.record_event(event)
        return event
    
    def validation_completed(
        self,
        stream_id: str,
        success: bool,
        error_message: str = "",
        generation_id: Optional[int] = None,
    ) -> RecoveryEvent:
        """Record a validation completion event."""
        self._event_counter += 1
        event = RecoveryEvent(
            event_id=f"ev:{time.monotonic_ns()}:{self._event_counter}",
            event_type=RecoveryEventType.VALIDATION_COMPLETED,
            stream_id=stream_id,
            generation_id=generation_id,
            status="success" if success else "failure",
            error_message=error_message,
        )
        self.record_event(event)
        return event
    
    def get_events(
        self,
        event_type: Optional[RecoveryEventType] = None,
        stream_id: Optional[str] = None,
    ) -> List[RecoveryEvent]:
        """
        Get recorded events, optionally filtered.
        
        Args:
            event_type: Filter by event type (None = all)
            stream_id: Filter by stream ID (None = all)
            
        Returns:
            List of matching events
        """
        result = self._events
        
        if event_type is not None:
            result = [e for e in result if e.event_type == event_type]
        
        if stream_id is not None:
            result = [e for e in result if e.stream_id == stream_id]
        
        return result
    
    @property
    def total_events(self) -> int:
        """Get total number of recorded events."""
        return len(self._events)
    
    @property
    def last_event(self) -> Optional[RecoveryEvent]:
        """Get the most recent event."""
        return self._events[-1] if self._events else None


# =============================================================================
# METRICS AND STATISTICS
# =============================================================================

@dataclass(frozen=True)
class RecoveryMetrics:
    """
    Metrics collected during recovery operations.
    """
    
    # Counters
    failures_detected: int = 0
    recoveries_attempted: int = 0
    recoveries_successful: int = 0
    recoveries_failed: int = 0
    
    # Timing
    total_recovery_time_seconds: float = 0.0
    average_recovery_time_seconds: float = 0.0
    max_recovery_time_seconds: float = 0.0
    
    # Operations
    checkpoints_restored: int = 0
    replay_sessions_started: int = 0
    validation_checks_performed: int = 0
    
    # Degradation
    degradation_entries: int = 0
    degradation_exits: int = 0
    
    # Error breakdown
    failure_categories: Dict[str, int] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """Calculate recovery success rate."""
        if self.recoveries_attempted == 0:
            return 1.0
        return self.recoveries_successful / self.recoveries_attempted


class RecoveryMetricsCollector:
    """
    Collector for recovery metrics.
    
    Tracks statistics about recovery operations over time.
    """
    
    def __init__(self):
        """Initialize the metrics collector."""
        self._metrics = RecoveryMetrics()
        self._current_recovery_start: Optional[float] = None
    
    def record_failure(self, category: str) -> None:
        """Record a failure detection."""
        self._metrics.failures_detected += 1
        current_count = self._metrics.failure_categories.get(category, 0)
        self._metrics.failure_categories[category] = current_count + 1
    
    def start_recovery(self) -> float:
        """Mark the start of a recovery attempt."""
        self._current_recovery_start = time.time()
        self._metrics.recoveries_attempted += 1
        return self._current_recovery_start
    
    def complete_recovery(self, success: bool) -> None:
        """Record completion of a recovery attempt."""
        if self._current_recovery_start is not None:
            duration = time.time() - self._current_recovery_start
            
            if success:
                self._metrics.recoveries_successful += 1
                self._metrics.total_recovery_time_seconds += duration
                
                if duration > self._metrics.max_recovery_time_seconds:
                    self._metrics.max_recovery_time_seconds = duration
                
                # Update average (with protection against division by zero)
                total_count = (
                    self._metrics.recoveries_successful + 
                    self._metrics.recoveries_failed
                )
                if total_count > 0:
                    self._metrics.average_recovery_time_seconds = (
                        self._metrics.total_recovery_time_seconds / total_count
                    )
            else:
                self._metrics.recoveries_failed += 1
    
    def record_checkpoint_restored(self) -> None:
        """Record a checkpoint restoration."""
        self._metrics.checkpoints_restored += 1
    
    def record_replay_started(self) -> None:
        """Record a replay session started."""
        self._metrics.replay_sessions_started += 1
    
    def record_validation_performed(self, passed: bool) -> None:
        """Record a validation check."""
        self._metrics.validation_checks_performed += 1
    
    @property
    def metrics(self) -> RecoveryMetrics:
        """Get current metrics snapshot."""
        return self._metrics


__all__ = [
    "RecoveryEventType",
    "RecoveryEvent",
    "RecoveryObservabilityReporter",
    "RecoveryMetrics",
    "RecoveryMetricsCollector",
]