# Core Communication Model
# ========================

"""
Immutable artifact identifiers and type definitions for Phase 3.7.12.

Provides:
- EventId, MessageId, SignalId - Unique identifiers for communication artifacts
- CorrelationId, CausationId - Traceability across system boundaries
- RuntimeId, SessionId - Context isolation
- SequenceNumber - Deterministic ordering within streams
- PriorityLevel - Delivery priority classification

All types are frozen dataclasses or NewType aliases.
"""

from dataclasses import dataclass, field
from typing import NewType, Dict, Any, Optional
from enum import Enum, auto
import uuid
import time


# =============================================================================
# UNIQUE IDENTIFIERS (NewType wrappers for type safety)
# =============================================================================

EventId = NewType("EventId", str)
"""Unique identifier for an Event instance."""

MessageId = NewType("MessageId", str)
"""Unique identifier for a Message instance."""

SignalId = NewType("SignalId", str)
"""Unique identifier for a Signal instance."""

CorrelationId = NewType("CorrelationId", str)
"""Groups related events/messages across system boundaries (e.g., request ID)."""

CausationId = NewType("CausationId", str)
"""Identifies the event that caused this one (causal chain)."""

RuntimeId = NewType("RuntimeId", str)
"""Identifier for a runtime instance (enables isolation)."""

SessionId = NewType("SessionId", str)
"""User/session context for correlation."""

SequenceNumber = NewType("SequenceNumber", int)
"""Monotonic sequence number within a stream."""


# =============================================================================
# PRIORITY LEVELS
# =============================================================================

class PriorityLevel(Enum):
    """
    Delivery priority levels.
    
    Priority ordering (lowest to highest):
        CRITICAL > EMERGENCY > URGENT > HIGH > NORMAL > LOW > BACKGROUND
    """
    CRITICAL = auto()    # Immediate delivery, bypass queues if needed
    EMERGENCY = auto()   # Very high priority, minimal queuing
    URGENT = auto()      # High priority, short queue wait
    HIGH = auto()        # Above normal priority
    NORMAL = auto()      # Standard priority (default)
    LOW = auto()         # Below normal priority
    BACKGROUND = auto()  # Low priority, can be batched


def priority_value(priority: PriorityLevel) -> int:
    """Return numeric priority value (lower = higher priority)."""
    return {
        PriorityLevel.CRITICAL: 0,
        PriorityLevel.EMERGENCY: 1,
        PriorityLevel.URGENT: 2,
        PriorityLevel.HIGH: 3,
        PriorityLevel.NORMAL: 4,
        PriorityLevel.LOW: 5,
        PriorityLevel.BACKGROUND: 6,
    }.get(priority, 4)


# =============================================================================
# BASE METADATA
# =============================================================================

@dataclass(frozen=True)
class EventMetadata:
    """
    Immutable metadata for events.
    
    Provides context for observability without mutability concerns.
    """
    
    event_type: str  # e.g., "lifecycle.transition", "task.activated"
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    source_id: Optional[str] = None
    runtime_id: Optional[str] = None
    
    # Traceability
    correlation_id: Optional[CorrelationId] = None
    causation_id: Optional[CausationId] = None
    
    # Ordering
    sequence_number: SequenceNumber = field(default_factory=lambda: SequenceNumber(0))
    
    def with_sequence(self, seq: int) -> "EventMetadata":
        """Return copy with updated sequence number."""
        return EventMetadata(
            event_type=self.event_type,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            source_id=self.source_id,
            runtime_id=self.runtime_id,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            sequence_number=SequenceNumber(seq),
        )
    
    def with_correlation(self, corr_id: str) -> "EventMetadata":
        """Return copy with correlation ID."""
        return EventMetadata(
            event_type=self.event_type,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            source_id=self.source_id,
            runtime_id=self.runtime_id,
            correlation_id=CorrelationId(corr_id),
            causation_id=self.causation_id,
            sequence_number=self.sequence_number,
        )
    
    def with_causation(self, cause_id: str) -> "EventMetadata":
        """Return copy with causation ID."""
        return EventMetadata(
            event_type=self.event_type,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            source_id=self.source_id,
            runtime_id=self.runtime_id,
            correlation_id=self.correlation_id,
            causation_id=CausationId(cause_id),
            sequence_number=self.sequence_number,
        )


@dataclass(frozen=True)
class MessageMetadata:
    """
    Immutable metadata for messages.
    
    Messages request communication but do not mutate state directly.
    """
    
    message_type: str  # e.g., "command", "query", "notification"
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    source_id: Optional[str] = None
    destination_id: Optional[str] = None
    runtime_id: Optional[str] = None
    
    # Traceability
    correlation_id: Optional[CorrelationId] = None
    causation_id: Optional[CausationId] = None
    
    # Priority
    priority: PriorityLevel = PriorityLevel.NORMAL
    
    def with_priority(self, priority: PriorityLevel) -> "MessageMetadata":
        """Return copy with updated priority."""
        return MessageMetadata(
            message_type=self.message_type,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            source_id=self.source_id,
            destination_id=self.destination_id,
            runtime_id=self.runtime_id,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            priority=priority,
        )


@dataclass(frozen=True)
class SignalMetadata:
    """
    Immutable metadata for signals.
    
    Signals represent runtime transitions, not state changes.
    """
    
    signal_type: str  # e.g., "lifecycle.transition", "task.cancelled"
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    source_id: Optional[str] = None
    target_id: Optional[str] = None
    runtime_id: Optional[str] = None
    
    # Traceability
    correlation_id: Optional[CorrelationId] = None
    causation_id: Optional[CausationId] = None


# =============================================================================
# ARTIFACT BASE CLASSES (for documentation, not used directly)
# =============================================================================

@dataclass(frozen=True)
class Event:
    """
    Base class for immutable event artifacts.
    
    Events represent facts about system state changes.
    They never request behavior - they merely report what occurred.
    
    All concrete events should extend this and include:
        - event_id: Unique identifier
        - payload: Domain-specific data (frozen structures)
        - metadata: Timestamps, traceability info
    
    Invariant: Events are immutable facts, never commands.
    """
    
    event_id: EventId
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: EventMetadata = field(default_factory=EventMetadata)


@dataclass(frozen=True)
class Message:
    """
    Base class for immutable message artifacts.
    
    Messages request communication but never mutate runtime state directly.
    They are requests to be processed by recipients.
    
    Invariant: Messages never change system state - only trigger reactions.
    """
    
    message_id: MessageId
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: MessageMetadata = field(default_factory=MessageMetadata)


@dataclass(frozen=True)
class Signal:
    """
    Base class for immutable signal artifacts.
    
    Signals represent runtime transitions and should never become
    lifecycle authorities themselves. They are transient state indicators.
    
    Invariant: Signals transition, they don't own state.
    """
    
    signal_id: SignalId
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: SignalMetadata = field(default_factory=SignalMetadata)


# =============================================================================
# ID GENERATORS
# =============================================================================

def generate_event_id() -> EventId:
    """Generate a unique EventId."""
    return EventId(f"evt_{uuid.uuid4().hex[:24]}")


def generate_message_id() -> MessageId:
    """Generate a unique MessageId."""
    return MessageId(f"msg_{uuid.uuid4().hex[:24]}")


def generate_signal_id() -> SignalId:
    """Generate a unique SignalId."""
    return SignalId(f"sig_{uuid.uuid4().hex[:24]}")


def generate_correlation_id() -> CorrelationId:
    """Generate a new correlation ID for grouping related artifacts."""
    return CorrelationId(str(uuid.uuid4()))


def generate_causation_id(from_event_id: EventId) -> CausationId:
    """Generate causation ID from an existing event."""
    return CausationId(f"causes_{from_event_id}")


def generate_session_id() -> SessionId:
    """Generate a new session ID."""
    return SessionId(str(uuid.uuid4()))


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Unique identifiers
    "EventId",
    "MessageId",
    "SignalId",
    "CorrelationId",
    "CausationId",
    "RuntimeId",
    "SessionId",
    "SequenceNumber",
    
    # Priority
    "PriorityLevel",
    "priority_value",
    
    # Metadata
    "EventMetadata",
    "MessageMetadata",
    "SignalMetadata",
    
    # Base classes (for reference)
    "Event",
    "Message",
    "Signal",
    
    # Generators
    "generate_event_id",
    "generate_message_id",
    "generate_signal_id",
    "generate_correlation_id",
    "generate_causation_id",
    "generate_session_id",
]