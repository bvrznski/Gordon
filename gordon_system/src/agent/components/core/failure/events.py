# Failure Recovery Events
# ========================

"""
Immutable events for failure recovery operations in Phase 3.7.10.

Events are:
    - Immutable (frozen dataclass) for thread safety
    - Serializable (JSON compatible)
    - Preserved across restarts for audit trails
    - Correlated with failures and recovery attempts
    
All events must include:
    - runtime_id: Which runtime generated the event
    - failure_id: Which failure caused this event
    - logical_sequence: For ordering events
    - timestamp: When it occurred
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any
import time

from ..communication import (
    EventBus,
    EventEnvelope,
)


# =============================================================================
# Base Event Types
# =============================================================================

@dataclass(frozen=True)
class RuntimeFailureEvent:
    """
    Base event for failure recovery operations.
    
    All failure-related events extend this base type.
    
    Field ordering rules:
        - All fields without defaults must come before fields with defaults
        - This ensures proper dataclass initialization when inheriting
    
    Note: When a derived class has non-defaulted fields, all base class fields
    must have default values to avoid dataclass field ordering errors.
    """
    
    # Base required fields (with defaults for safe inheritance)
    event_id: str = ""
    runtime_id: str = ""
    failure_id: str = ""
    
    # Base optional fields with defaults
    logical_sequence: int = 0
    timestamp_utc: float = field(default_factory=time.time)
    
    source: str = ""  # Component that generated the event
    event_type: str = "unknown"
    
    payload: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Failure Events
# =============================================================================

@dataclass(frozen=True)
class FailureDetectedEvent(RuntimeFailureEvent):
    """
    Event emitted when a failure is first detected.
    
    This is the starting point of failure handling.
    """
    
    event_type: str = "failure_detected"
    
    # Detection context
    detection_method: str = ""  # How was it detected? (empty string as safe default)
    
    # Initial classification
    initial_scope: List[str] = field(default_factory=list)  # Scope of affected entities
    initial_kind: Optional[str] = None  # Initial kind (may be refined later)
    initial_severity: Optional[str] = None  # Initial severity (may be refined later)


@dataclass(frozen=True)
class FailureClassifiedEvent(RuntimeFailureEvent):
    """
    Event emitted after failure classification is complete.
    
    This includes:
        - Determined kind (TRANSIENT, RECOVERABLE, etc.)
        - Retryability assessment
        - Rollback eligibility
        - Recovery eligibility
    """
    
    event_type: str = "failure_classified"
    
    # Classification results
    kind: str = ""  # FailureKind value (empty string as safe default)
    severity: str = ""  # FailureSeverity value (empty string as safe default)
    
    # Optional fields
    retryability: Optional[bool] = None
    rollback_eligibility: Optional[bool] = None
    recovery_eligibility: Optional[bool] = None
    
    confidence: float = 0.0
    unresolved_facts: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class FailureContainedEvent(RuntimeFailureEvent):
    """
    Event emitted when failure containment is complete.
    
    Contains:
        - Containment result (success/failure)
        - Scope of containment
        - Actions executed
    """
    
    event_type: str = "failure_contained"
    
    containment_id: str = ""
    
    success: bool = False
    scope_affected: int = 0
    actions_executed: int = 0
    
    verification_passed: Optional[bool] = None


# =============================================================================
# Rollback Events
# =============================================================================

@dataclass(frozen=True)
class RollbackRequestedEvent(RuntimeFailureEvent):
    """
    Event emitted when rollback is requested.
    
    Includes:
        - Rollback scope and mode
        - Target state
        - Expected actions
    """
    
    event_type: str = "rollback_requested"
    
    rollback_id: str = ""
    
    scope: List[str] = field(default_factory=list)
    mode: str = ""  # RollbackMode value
    
    target_state_version: int = 0


@dataclass(frozen=True)
class RollbackPlannedEvent(RuntimeFailureEvent):
    """
    Event emitted when rollback plan is created.
    
    Plan includes:
        - Ordered actions
        - Dependencies between steps
        - Verification requirements
    """
    
    event_type: str = "rollback_planned"
    
    rollback_id: str = ""
    
    action_count: int = 0
    expected_duration_seconds: float = 0.0
    requires_verification: bool = True


@dataclass(frozen=True)
class RollbackStartedEvent(RuntimeFailureEvent):
    """Event emitted when rollback execution begins."""
    
    event_type: str = "rollback_started"
    
    rollback_id: str = ""
    
    step_index: int = 0
    total_steps: int = 0


@dataclass(frozen=True)
class RollbackCompletedEvent(RuntimeFailureEvent):
    """
    Event emitted when rollback completes.
    
    Includes:
        - Overall result (success/failure)
        - Verification status
        - State restored to
    """
    
    event_type: str = "rollback_completed"
    
    rollback_id: str = ""
    
    success: bool = False
    
    state_restored_to_version: int = 0
    verification_passed: Optional[bool] = None


@dataclass(frozen=True)
class RollbackFailedEvent(RuntimeFailureEvent):
    """
    Event emitted when rollback fails.
    
    Includes:
        - Step where failure occurred
        - Reason for failure
        - Whether escalation is needed
    """
    
    event_type: str = "rollback_failed"
    
    rollback_id: str = ""
    
    failed_step_index: int = 0
    failure_reason: str = ""
    requires_escalation: bool = True


# =============================================================================
# Recovery Events
# =============================================================================

@dataclass(frozen=True)
class RecoveryRequestedEvent(RuntimeFailureEvent):
    """
    Event emitted when recovery is requested.
    
    Includes:
        - Requested policy (retry, restart, etc.)
        - Expected actions
    """
    
    event_type: str = "recovery_requested"
    
    recovery_id: str = ""
    
    requested_policy: str = ""  # RecoveryPolicy value
    
    scope: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RecoveryAuthorizedEvent(RuntimeFailureEvent):
    """Event emitted when recovery request is authorized."""
    
    event_type: str = "recovery_authorized"
    
    recovery_id: str = ""
    
    approved_policy: str = ""  # May differ from requested (empty string as safe default)
    budget_remaining: int = 0


@dataclass(frozen=True)
class RecoveryPlannedEvent(RuntimeFailureEvent):
    """
    Event emitted when recovery plan is created.
    
    Plan includes:
        - Ordered actions
        - Dependencies
        - Verification requirements
    """
    
    event_type: str = "recovery_planned"
    
    recovery_id: str = ""
    
    action_count: int = 0
    expected_duration_seconds: float = 0.0


@dataclass(frozen=True)
class RecoveryStartedEvent(RuntimeFailureEvent):
    """Event emitted when recovery execution begins."""
    
    event_type: str = "recovery_started"
    
    recovery_id: str = ""
    
    phase: str = ""  # e.g., "containment", "quiescence", "rollback", "restart" (empty string as safe default)


@dataclass(frozen=True)
class RecoveryStepCompletedEvent(RuntimeFailureEvent):
    """Event emitted when a recovery step completes."""
    
    event_type: str = "recovery_step_completed"
    
    recovery_id: str = ""
    
    step_index: int = 0
    total_steps: int = 0
    
    action_performed: str = ""  # Empty string as safe default


@dataclass(frozen=True)
class RecoveryVerificationStartedEvent(RuntimeFailureEvent):
    """Event emitted when independent verification begins."""
    
    event_type: str = "recovery_verification_started"
    
    recovery_id: str = ""
    
    verifier: str = ""  # Who is verifying (empty string as safe default)


@dataclass(frozen=True)
class RecoverySucceededEvent(RuntimeFailureEvent):
    """
    Event emitted when recovery succeeds.
    
    This requires:
        - All actions completed
        - Verification passed
        - Target state restored or acceptable degraded state
    """
    
    event_type: str = "recovery_succeeded"
    
    recovery_id: str = ""
    
    final_state: str = ""  # e.g., "healthy", "degraded" (empty string as safe default)
    verification_passed: bool = True
    
    degraded_components: List[str] = field(default_factory=list)
    missing_capabilities: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RecoveryFailedEvent(RuntimeFailureEvent):
    """
    Event emitted when recovery fails.
    
    Includes:
        - Failure reason
        - Escalation path taken
        - Final state
    """
    
    event_type: str = "recovery_failed"
    
    recovery_id: str = ""
    
    failure_reason: str = ""
    escalation_path_taken: List[str] = field(default_factory=list)
    
    final_state: str = ""  # Empty string as safe default (default was "failed" but needs to match pattern)


# =============================================================================
# Retry Events
# =============================================================================

@dataclass(frozen=True)
class RetryStartedEvent(RuntimeFailureEvent):
    """Event emitted when retry begins."""
    
    event_type: str = "retry_started"
    
    operation_id: str = ""
    
    attempt_number: int = 1
    max_attempts: int = 3
    
    backoff_seconds: float = 0.0


@dataclass(frozen=True)
class RetryAttemptedEvent(RuntimeFailureEvent):
    """Event emitted when a retry attempt completes."""
    
    event_type: str = "retry_attempted"
    
    operation_id: str = ""
    
    attempt_number: int = 1
    
    succeeded: bool = False
    next_backoff_seconds: float = 0.0


@dataclass(frozen=True)
class RetryExhaustedEvent(RuntimeFailureEvent):
    """Event emitted when all retry attempts are exhausted."""
    
    event_type: str = "retry_exhausted"
    
    operation_id: str = ""
    
    total_attempts: int = 1
    last_failure_reason: str = ""


# =============================================================================
# Restart Events
# =============================================================================

@dataclass(frozen=True)
class RestartRequestedEvent(RuntimeFailureEvent):
    """Event emitted when restart is requested."""
    
    event_type: str = "restart_requested"
    
    entity_id: str = ""
    
    generation_before: int = 0
    generation_after: int = 1
    
    restart_kind: str = ""  # RestartKind value (empty string as safe default)


@dataclass(frozen=True)
class RestartStartedEvent(RuntimeFailureEvent):
    """Event emitted when restart execution begins."""
    
    event_type: str = "restart_started"
    
    entity_id: str = ""
    
    generation: int = 1


@dataclass(frozen=True)
class RestartCompletedEvent(RuntimeFailureEvent):
    """
    Event emitted when restart completes.
    
    Includes:
        - Generation number (should be incremented)
        - Verification status
        - New state
    """
    
    event_type: str = "restart_completed"
    
    entity_id: str = ""
    
    generation: int = 1
    
    verification_passed: Optional[bool] = None


@dataclass(frozen=True)
class RestartFailedEvent(RuntimeFailureEvent):
    """Event emitted when restart fails."""
    
    event_type: str = "restart_failed"
    
    entity_id: str = ""
    
    failure_reason: str = ""


# =============================================================================
# Runtime State Events
# =============================================================================

@dataclass(frozen=True)
class RuntimeDegradedEvent(RuntimeFailureEvent):
    """Event emitted when runtime enters degraded state."""
    
    event_type: str = "runtime_degraded"
    
    degraded_components: List[str] = field(default_factory=list)
    missing_capabilities: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RuntimeRestoredEvent(RuntimeFailureEvent):
    """Event emitted when runtime returns to healthy state."""
    
    event_type: str = "runtime_restored"
    
    restored_components: List[str] = field(default_factory=list)


# =============================================================================
# Corruption and Safety Events
# =============================================================================

@dataclass(frozen=True)
class CorruptionDetectedEvent(RuntimeFailureEvent):
    """Event emitted when corruption is detected."""
    
    event_type: str = "corruption_detected"
    
    corruption_kind: str = ""  # e.g., "checkpoint", "state", "queue" (empty string as safe default)
    scope: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class SplitBrainDetectedEvent(RuntimeFailureEvent):
    """Event emitted when split-brain condition is detected."""
    
    event_type: str = "split_brain_detected"
    
    conflicting_generations: List[str] = field(default_factory=list)  # Entity IDs


# =============================================================================
# Event Publisher Protocol
# =============================================================================

class FailureEventPublisher:
    """
    Protocol for publishing failure events.
    
    Implementations should be:
        - Idempotent (duplicate events don't cause issues)
        - Non-blocking (don't wait for acknowledgment)
        - Durable where required (persist critical events)
    """
    
    async def publish(self, event: RuntimeFailureEvent) -> None:
        """Publish an event."""
        raise NotImplementedError


class EventBusFailurePublisher(FailureEventPublisher):
    """
    Publishes failure events through the canonical EventBus.
    
    Integrates with Phase 3.7.12 communication infrastructure:
        - Uses EventEnvelope for transport
        - Leverages existing subscription system
        - Provides deterministic ordering via sequence numbers
    
    Usage:
        event_bus = get_event_bus(runtime_id)
        publisher = EventBusFailurePublisher(event_bus, runtime_id)
        
        await publisher.publish(FailureDetectedEvent(...))
    """
    
    def __init__(self, event_bus: EventBus, runtime_id: str):
        """
        Initialize with canonical EventBus.
        
        Args:
            event_bus: The canonical EventBus instance
            runtime_id: Runtime identifier for events
        """
        self._event_bus = event_bus
        self._runtime_id = runtime_id
    
    async def publish(self, event: RuntimeFailureEvent) -> None:
        """Publish failure event through canonical EventBus."""
        envelope = EventEnvelope(
            envelope_id=event.event_id,
            runtime_id=self._runtime_id,
            event_type=event.event_type,
            payload={
                "failure_id": event.failure_id,
                "source": event.source,
                "event_type": event.event_type,
                **event.payload,
            },
            correlation_id=None,
        )
        self._event_bus.publish(envelope)


class LoggingEventPublisher(FailureEventPublisher):
    """
    Simple publisher that logs events.
    
    This is suitable for development/testing. Production should use
    a proper event bus or message queue implementation.
    
    For Phase 3.7.27+, use EventBusFailurePublisher in production.
    """
    
    async def publish(self, event: RuntimeFailureEvent) -> None:
        """Log the event."""
        print(f"[{event.event_type}] {event.failure_id}: {event.source}")


# =============================================================================
# Event History (bounded storage)
# =============================================================================

class FailureEventHistory:
    """
    Store recent failure events for diagnostics.
    
    Provides:
        - Bounded history (max N events per failure)
        - Time-based eviction
        - Query by failure ID, event type, time range
    
    Usage:
        history = FailureEventHistory(max_events=1000)
        
        await history.record(event)
        
        # Get all events for a failure
        events = history.get_for_failure(failure_id)
        
        # Get events of specific type
        classified = history.get_by_type("failure_classified")
    """
    
    def __init__(self, max_events: int = 1000):
        self._max_events = max_events
        self._events: Dict[str, List[RuntimeFailureEvent]] = {}
        self._all_events: List[RuntimeFailureEvent] = []
        self._event_types: Dict[str, List[RuntimeFailureEvent]] = {}
    
    async def record(self, event: RuntimeFailureEvent) -> None:
        """Record an event."""
        # Add to failure-specific list
        if event.failure_id not in self._events:
            self._events[event.failure_id] = []
        
        self._events[event.failure_id].append(event)
        
        # Add to global list (bounded)
        self._all_events.append(event)
        
        # Evict old events if needed
        while len(self._all_events) > self._max_events:
            oldest = self._all_events.pop(0)
            
            # Clean up from per-failure lists
            failure_id = oldest.failure_id
            if failure_id in self._events and oldest in self._events[failure_id]:
                self._events[failure_id].remove(oldest)
        
        # Index by type
        event_type = event.event_type
        if event_type not in self._event_types:
            self._event_types[event_type] = []
        
        self._event_types[event_type].append(event)
    
    def get_for_failure(self, failure_id: str) -> List[RuntimeFailureEvent]:
        """Get all events for a specific failure."""
        return list(self._events.get(failure_id, []))
    
    def get_by_type(self, event_type: str) -> List[RuntimeFailureEvent]:
        """Get events of a specific type."""
        return list(self._event_types.get(event_type, []))
    
    def clear(self) -> None:
        """Clear all events."""
        self._events.clear()
        self._all_events.clear()
        self._event_types.clear()


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    # Base event types
    "RuntimeFailureEvent",
    "RuntimeFailureEvent",
    
    # Failure events
    "FailureDetectedEvent",
    "FailureClassifiedEvent",
    "FailureContainedEvent",
    
    # Rollback events
    "RollbackRequestedEvent",
    "RollbackPlannedEvent",
    "RollbackStartedEvent",
    "RollbackCompletedEvent",
    "RollbackFailedEvent",
    
    # Recovery events
    "RecoveryRequestedEvent",
    "RecoveryAuthorizedEvent",
    "RecoveryPlannedEvent",
    "RecoveryStartedEvent",
    "RecoveryStepCompletedEvent",
    "RecoveryVerificationStartedEvent",
    "RecoverySucceededEvent",
    "RecoveryFailedEvent",
    
    # Retry events
    "RetryStartedEvent",
    "RetryAttemptedEvent",
    "RetryExhaustedEvent",
    
    # Restart events
    "RestartRequestedEvent",
    "RestartStartedEvent",
    "RestartCompletedEvent",
    "RestartFailedEvent",
    
    # Runtime state events
    "RuntimeDegradedEvent",
    "RuntimeRestoredEvent",
    
    # Corruption and safety events
    "CorruptionDetectedEvent",
    "SplitBrainDetectedEvent",
    
    # Publisher protocols
    "FailureEventPublisher",
    "EventBusFailurePublisher",  # NEW: Phase 3.7.27 - Canonical integration
    "LoggingEventPublisher",
    
    # History
    "FailureEventHistory",
]