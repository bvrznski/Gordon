# Execution Events
# ================
#
# PHASE 3.10.14 - Observability and Replay Enhancements

"""
Execution events for observability, replay, and debugging.

Events are:
    - Immutable
    - Observational (do not affect execution semantics)
    - Timestamped with monotonic time
    - Correlated through ID chains

Event Categories:
    - Lifecycle: Thread/Loop/Cycle creation, state transitions
    - Execution: Stage start/completion/failure
    - Decision: Loop decisions, cycle selection
    - Outcome: Cycle completion, delta commit results
    - Delegation: Child thread creation and completion
    - Cancellation: Requested, completed
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, Any
from enum import Enum
import uuid


# =============================================================================
# Event Categories
# =============================================================================

class ExecutionEventType(Enum):
    """
    Categories of execution events.
    
    These help organize events by type and enable efficient filtering.
    """
    
    # Lifecycle events (creation, state transitions)
    THREAD_CREATED = "thread_created"
    THREAD_ACTIVATED = "thread_activated"
    THREAD_SUSPENDED = "thread_suspended"
    THREAD_RESUMED = "thread_resumed"
    THREAD_COMPLETED = "thread_completed"
    THREAD_FAILED = "thread_failed"
    
    # Loop events (selection, replacement)
    LOOP_SELECTED = "loop_selected"
    LOOP_REPLACED = "loop_replaced"
    
    # Cycle events (start, completion, failure)
    CYCLE_STARTED = "cycle_started"
    STAGE_STARTED = "stage_started"
    STAGE_COMPLETED = "stage_completed"
    CYCLE_COMPLETED = "cycle_completed"
    
    # Outcome events
    DELTA_COMMITTED = "delta_committed"
    DELTA_REJECTED = "delta_rejected"
    
    # Delegation events
    CHILD_THREAD_CREATED = "child_thread_created"
    CHILD_THREAD_COMPLETED = "child_thread_completed"
    
    # Cancellation events
    CANCELLATION_REQUESTED = "cancellation_requested"
    CANCELLATION_COMPLETED = "cancellation_completed"
    
    # Advancement events (one coordinator advancement)
    ADVANCEMENT_STARTED = "advance_started"
    ADVANCEMENT_COMPLETED = "advance_completed"


# =============================================================================
# Event Correlation IDs
# =============================================================================

@dataclass(frozen=True, slots=True)
class EventCorrelation:
    """
    Correlation identifiers for tracing execution across components.
    
    These enable causal and temporal tracking of events:
        - correlation_id: One complete advancement (coordinator loop iteration)
        - causation_id: What caused this event (parent event)
        - parent_thread_id: If child of another thread
        - originating_cycle_id: Which cycle started the work
        - originating_stage_id: Which stage started the work
    """
    
    correlation_id: str  # One coordinator advancement
    causation_id: Optional[str] = None  # What caused this event?
    
    # Hierarchy tracking
    parent_thread_id: Optional[str] = None
    originating_cycle_id: Optional[str] = None
    originating_stage_id: Optional[str] = None
    
    # Delegation tracking
    delegation_id: Optional[str] = None
    invocation_id: Optional[str] = None  # Capability invocation


@dataclass(frozen=True, slots=True)
class EventCorrelationContext:
    """
    Context for generating correlated events.
    
    Contains correlation information that gets propagated through execution.
    """
    
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    
    def with_causation(self, event_id: str) -> "EventCorrelation":
        """Create a new correlation with the given event as causation."""
        return EventCorrelation(
            correlation_id=self.correlation_id,
            causation_id=event_id,
        )


# =============================================================================
# Base Event
# =============================================================================

@dataclass(frozen=True, slots=True)
class ExecutionEvent:
    """
    A single execution event for observability and replay.
    
    Events are immutable, timestamped, and correlated with IDs.
    They do NOT affect execution semantics - they're observational only.
    """
    
    # Identity
    event_id: str  # Unique identifier for this event instance
    
    # Correlation (for tracing across components)
    correlation_id: str  # What advancement does this belong to?
    causation_id: Optional[str] = None  # What caused this event?
    
    # Timing
    timestamp_utc: float  # When did it happen? (monotonic time)
    
    # Context
    thread_id: str  # Which thread is this about?
    loop_id: Optional[str] = None  # Which loop (if any)?
    cycle_id: Optional[str] = None  # Which cycle (if any)?
    stage_id: Optional[str] = None  # Which stage (if any)?
    
    # Event type and payload
    event_type: ExecutionEventType
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "timestamp_utc": self.timestamp_utc,
            "thread_id": self.thread_id,
            "loop_id": self.loop_id,
            "cycle_id": self.cycle_id,
            "stage_id": self.stage_id,
            "event_type": self.event_type.value,
            "payload": dict(self.payload),
        }
    
    def with_correlation(self, correlation: EventCorrelation) -> "ExecutionEvent":
        """Create new event with updated correlation context."""
        return dataclass_replace(self, 
            correlation_id=correlation.correlation_id,
            causation_id=correlation.causation_id,
        )


# =============================================================================
# Event Factories
# =============================================================================

def thread_created_event(
    thread_id: str,
    timestamp_utc: float,
    event_correlation: EventCorrelation,
) -> ExecutionEvent:
    """Create a thread created event."""
    return ExecutionEvent(
        event_id=uuid.uuid4().hex[:16],
        correlation_id=event_correlation.correlation_id,
        causation_id=None,  # First event in the chain
        timestamp_utc=timestamp_utc,
        thread_id=thread_id,
        event_type=ExecutionEventType.THREAD_CREATED,
        payload={"source": "execution_coordinator"},
    )


def loop_selected_event(
    thread_id: str,
    loop_id: str,
    timestamp_utc: float,
    event_correlation: EventCorrelation,
) -> ExecutionEvent:
    """Create a loop selected event."""
    return ExecutionEvent(
        event_id=uuid.uuid4().hex[:16],
        correlation_id=event_correlation.correlation_id,
        causation_id=None,
        timestamp_utc=timestamp_utc,
        thread_id=thread_id,
        loop_id=loop_id,
        event_type=ExecutionEventType.LOOP_SELECTED,
        payload={"selected_by": "coordinator"},
    )


def cycle_started_event(
    thread_id: str,
    cycle_id: str,
    loop_id: Optional[str],
    source_revision: int,
    timestamp_utc: float,
    event_correlation: EventCorrelation,
) -> ExecutionEvent:
    """Create a cycle started event."""
    return ExecutionEvent(
        event_id=uuid.uuid4().hex[:16],
        correlation_id=event_correlation.correlation_id,
        causation_id=None,
        timestamp_utc=timestamp_utc,
        thread_id=thread_id,
        loop_id=loop_id,
        cycle_id=cycle_id,
        event_type=ExecutionEventType.CYCLE_STARTED,
        payload={
            "source_revision": source_revision,
        },
    )


def stage_started_event(
    thread_id: str,
    cycle_id: str,
    stage_id: str,
    timestamp_utc: float,
    event_correlation: EventCorrelation,
) -> ExecutionEvent:
    """Create a stage started event."""
    return ExecutionEvent(
        event_id=uuid.uuid4().hex[:16],
        correlation_id=event_correlation.correlation_id,
        causation_id=None,
        timestamp_utc=timestamp_utc,
        thread_id=thread_id,
        cycle_id=cycle_id,
        stage_id=stage_id,
        event_type=ExecutionEventType.STAGE_STARTED,
    )


def stage_completed_event(
    thread_id: str,
    cycle_id: str,
    stage_id: str,
    status: str,  # completed, failed, skipped
    timestamp_utc: float,
    event_correlation: EventCorrelation,
) -> ExecutionEvent:
    """Create a stage completed event."""
    return ExecutionEvent(
        event_id=uuid.uuid4().hex[:16],
        correlation_id=event_correlation.correlation_id,
        causation_id=None,
        timestamp_utc=timestamp_utc,
        thread_id=thread_id,
        cycle_id=cycle_id,
        stage_id=stage_id,
        event_type=ExecutionEventType.STAGE_COMPLETED,
        payload={"status": status},
    )


def cycle_completed_event(
    thread_id: str,
    cycle_id: str,
    status: str,  # completed, interrupted, failed
    timestamp_utc: float,
    event_correlation: EventCorrelation,
) -> ExecutionEvent:
    """Create a cycle completed event."""
    return ExecutionEvent(
        event_id=uuid.uuid4().hex[:16],
        correlation_id=event_correlation.correlation_id,
        causation_id=None,
        timestamp_utc=timestamp_utc,
        thread_id=thread_id,
        cycle_id=cycle_id,
        event_type=ExecutionEventType.CYCLE_COMPLETED,
        payload={"status": status},
    )


def delta_committed_event(
    thread_id: str,
    revision: int,
    timestamp_utc: float,
    event_correlation: EventCorrelation,
) -> ExecutionEvent:
    """Create a delta committed event."""
    return ExecutionEvent(
        event_id=uuid.uuid4().hex[:16],
        correlation_id=event_correlation.correlation_id,
        causation_id=None,
        timestamp_utc=timestamp_utc,
        thread_id=thread_id,
        event_type=ExecutionEventType.DELTA_COMMITTED,
        payload={"new_revision": revision},
    )


def delta_rejected_event(
    thread_id: str,
    reason: str,
    timestamp_utc: float,
    event_correlation: EventCorrelation,
) -> ExecutionEvent:
    """Create a delta rejected event."""
    return ExecutionEvent(
        event_id=uuid.uuid4().hex[:16],
        correlation_id=event_correlation.correlation_id,
        causation_id=None,
        timestamp_utc=timestamp_utc,
        thread_id=thread_id,
        event_type=ExecutionEventType.DELTA_REJECTED,
        payload={"reason": reason},
    )


def cancellation_requested_event(
    thread_id: str,
    reason: str,
    source: str,  # user, timeout, parent, system
    timestamp_utc: float,
    event_correlation: EventCorrelation,
) -> ExecutionEvent:
    """Create a cancellation requested event."""
    return ExecutionEvent(
        event_id=uuid.uuid4().hex[:16],
        correlation_id=event_correlation.correlation_id,
        causation_id=None,
        timestamp_utc=timestamp_utc,
        thread_id=thread_id,
        event_type=ExecutionEventType.CANCELLATION_REQUESTED,
        payload={"reason": reason, "source": source},
    )


def advancement_started_event(
    thread_id: str,
    timestamp_utc: float,
    event_correlation: EventCorrelation,
) -> ExecutionEvent:
    """Create an advancement started event."""
    return ExecutionEvent(
        event_id=uuid.uuid4().hex[:16],
        correlation_id=event_correlation.correlation_id,
        causation_id=None,
        timestamp_utc=timestamp_utc,
        thread_id=thread_id,
        event_type=ExecutionEventType.ADVANCEMENT_STARTED,
    )


def advancement_completed_event(
    thread_id: str,
    outcome: str,  # success, failure, yielded
    timestamp_utc: float,
    event_correlation: EventCorrelation,
) -> ExecutionEvent:
    """Create an advancement completed event."""
    return ExecutionEvent(
        event_id=uuid.uuid4().hex[:16],
        correlation_id=event_correlation.correlation_id,
        causation_id=None,
        timestamp_utc=timestamp_utc,
        thread_id=thread_id,
        event_type=ExecutionEventType.ADVANCEMENT_COMPLETED,
        payload={"outcome": outcome},
    )


# =============================================================================
# Helper Functions
# =============================================================================

def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    import dataclasses
    if hasattr(obj, '__dataclass_fields__'):
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


# =============================================================================
# Export all public symbols
# =============================================================================

__all__ = [
    # Enums
    "ExecutionEventType",
    
    # Correlation types
    "EventCorrelation",
    "EventCorrelationContext",
    
    # Event types
    "ExecutionEvent",
    
    # Factories
    "thread_created_event",
    "loop_selected_event",
    "cycle_started_event",
    "stage_started_event",
    "stage_completed_event",
    "cycle_completed_event",
    "delta_committed_event",
    "delta_rejected_event",
    "cancellation_requested_event",
    "advancement_started_event",
    "advancement_completed_event",
    
    # Helpers
    "dataclass_replace",
]