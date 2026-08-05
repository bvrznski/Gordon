# Core Event Model & Contracts
# ============================
"""
Canonical event model, metadata, and message contracts for Gordon Core.

This module establishes the immutable contract foundation for all events,
messages, commands, and queries in the system. It provides:

- Event taxonomy: Event, Command, Query, Message abstractions
- Immutable envelopes with typed payloads
- Standardized metadata (ids, timestamps, correlations)
- Message contracts that are transport-independent

All types are frozen dataclasses - once created, they never change.

ARCHITECTURAL LAWS:
1. Every event has one canonical definition
2. Messages are immutable after publication
3. Publishers never know subscribers
4. Subscribers depend on contracts only
5. Event metadata is standardized
6. Routing is deterministic
7. Hidden channels are prohibited
8. Duplicate event definitions are prohibited
9. Event contracts are transport-independent
10. Every published event is observable
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum, auto
import uuid
import time

# =============================================================================
# UNIQUE IDENTIFIERS (NewType-style for type safety)
# =============================================================================

EventId = str
"""Unique identifier for an Event instance."""

MessageId = str
"""Unique identifier for a Message instance."""

CommandId = str
"""Unique identifier for a Command instance."""

QueryId = str
"""Unique identifier for a Query instance."""

CorrelationId = str
"""Groups related events/messages across system boundaries (e.g., request ID)."""

CausationId = str
"""Identifies the event that caused this one (causal chain)."""

PublisherId = str
"""Identifier for an event publisher."""

SubscriberId = str
"""Identifier for a message subscriber."""

TopicId = str
"""Identifier for a topic channel."""

ChannelId = str
"""Identifier for a communication channel."""

RuntimeId = str
"""Identifier for a runtime instance (enables isolation)."""

SequenceNumber = int
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
    CRITICAL = auto()      # Immediate delivery, bypass queues if needed
    EMERGENCY = auto()     # Very high priority, minimal queuing
    URGENT = auto()        # High priority, short queue wait
    HIGH = auto()          # Above normal priority
    NORMAL = auto()        # Standard priority (default)
    LOW = auto()           # Below normal priority
    BACKGROUND = auto()    # Low priority, can be batched


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
# EVENT TYPES & SEMANTICS
# =============================================================================

class EventType(Enum):
    """
    Event semantic types.
    
    Events represent facts about system state. They never request behavior -
    they merely report what occurred.
    
    - EVENT: A fact about a past state change (e.g., "task.completed")
    - COMMAND: A request to change state (e.g., "task.start")
    - QUERY: A request for information (e.g., "system.status")
    - MESSAGE: A generic communication artifact
    """
    EVENT = auto()      # Fact about what happened
    COMMAND = auto()    # Request to do something
    QUERY = auto()      # Request for information
    MESSAGE = auto()    # Generic communication


# =============================================================================
# FAILURE MODEL EXCEPTIONS
# =============================================================================

class EventError(Exception):
    """Base exception for event-related errors."""
    pass


class RoutingError(Exception):
    """Exception raised when routing fails."""
    pass


class PublicationError(Exception):
    """Exception raised when publication fails."""
    pass


class SubscriptionError(Exception):
    """Exception raised when subscription operations fail."""
    pass


class ContractError(Exception):
    """Exception raised when contract validation fails."""
    pass


class SerializationError(Exception):
    """Exception raised when serialization/deserialization fails."""
    pass


class BusError(Exception):
    """Base exception for bus-related errors."""
    pass


class TopicError(Exception):
    """Exception raised when topic operations fail."""
    pass


class ChannelError(Exception):
    """Exception raised when channel operations fail."""
    pass


class DeliveryError(Exception):
    """Exception raised when delivery fails."""
    pass


class TransportError(Exception):
    """Exception raised when transport fails."""
    pass


class FlowControlError(Exception):
    """Exception raised when flow control is triggered."""
    pass


# =============================================================================
# BASE METADATA STRUCTURE
# =============================================================================

@dataclass(frozen=True)
class EventMetadata:
    """
    Immutable metadata for events.
    
    Provides context for observability without mutability concerns.
    """
    event_type: str                    # e.g., "lifecycle.transition", "task.completed"
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Identity
    event_id: EventId = ""
    
    # Traceability
    source_runtime_id: Optional[RuntimeId] = None
    publisher_id: Optional[PublisherId] = None
    
    correlation_id: Optional[CorrelationId] = None
    causation_id: Optional[CausationId] = None
    
    # Ordering
    sequence_number: SequenceNumber = 0
    partition_key: Optional[str] = None  # For ordered delivery within partitions
    
    # Priority
    priority: PriorityLevel = PriorityLevel.NORMAL
    
    # Versioning
    schema_version: int = 1            # Serialization schema version
    event_version: int = 1             # Event type version
    
    # Delivery tracking
    delivery_attempts: int = 0
    last_delivery_attempt_utc: Optional[float] = None
    
    def with_sequence(self, seq: int) -> "EventMetadata":
        """Return copy with updated sequence number."""
        return EventMetadata(
            event_type=self.event_type,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            event_id=self.event_id,
            source_runtime_id=self.source_runtime_id,
            publisher_id=self.publisher_id,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            sequence_number=seq,
            partition_key=self.partition_key,
            priority=self.priority,
            schema_version=self.schema_version,
            event_version=self.event_version,
            delivery_attempts=self.delivery_attempts,
            last_delivery_attempt_utc=self.last_delivery_attempt_utc,
        )
    
    def with_correlation(self, corr_id: CorrelationId) -> "EventMetadata":
        """Return copy with correlation ID."""
        return EventMetadata(
            event_type=self.event_type,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            event_id=self.event_id,
            source_runtime_id=self.source_runtime_id,
            publisher_id=self.publisher_id,
            correlation_id=corr_id,
            causation_id=self.causation_id,
            sequence_number=self.sequence_number,
            partition_key=self.partition_key,
            priority=self.priority,
            schema_version=self.schema_version,
            event_version=self.event_version,
            delivery_attempts=self.delivery_attempts,
            last_delivery_attempt_utc=self.last_delivery_attempt_utc,
        )
    
    def with_causation(self, cause_id: CausationId) -> "EventMetadata":
        """Return copy with causation ID."""
        return EventMetadata(
            event_type=self.event_type,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            event_id=self.event_id,
            source_runtime_id=self.source_runtime_id,
            publisher_id=self.publisher_id,
            correlation_id=self.correlation_id,
            causation_id=cause_id,
            sequence_number=self.sequence_number,
            partition_key=self.partition_key,
            priority=self.priority,
            schema_version=self.schema_version,
            event_version=self.event_version,
            delivery_attempts=self.delivery_attempts,
            last_delivery_attempt_utc=self.last_delivery_attempt_utc,
        )
    
    def increment_delivery_attempt(self) -> "EventMetadata":
        """Return copy with incremented delivery attempt count."""
        return EventMetadata(
            event_type=self.event_type,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            event_id=self.event_id,
            source_runtime_id=self.source_runtime_id,
            publisher_id=self.publisher_id,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            sequence_number=self.sequence_number,
            partition_key=self.partition_key,
            priority=self.priority,
            schema_version=self.schema_version,
            event_version=self.event_version,
            delivery_attempts=self.delivery_attempts + 1,
            last_delivery_attempt_utc=time.time(),
        )


# =============================================================================
# MESSAGE METADATA
# =============================================================================

@dataclass(frozen=True)
class MessageMetadata:
    """
    Immutable metadata for messages.
    
    Messages request communication but do not mutate runtime state directly.
    They are requests to be processed by recipients.
    """
    message_type: str                  # e.g., "command", "query", "notification"
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Identity
    message_id: MessageId = ""
    
    # Routing
    source_runtime_id: Optional[RuntimeId] = None
    destination_id: Optional[str] = None
    
    # Traceability
    correlation_id: Optional[CorrelationId] = None
    causation_id: Optional[CausationId] = None
    
    # Priority
    priority: PriorityLevel = PriorityLevel.NORMAL
    
    # Versioning
    schema_version: int = 1


# =============================================================================
# EVENT DESCRIPTOR (contract definition)
# =============================================================================

@dataclass(frozen=True)
class EventDescriptor:
    """
    Immutable descriptor for an event type contract.
    
    Defines the contract that publishers must follow and subscribers expect.
    
    Every event MUST have one canonical descriptor in the system.
    No duplicate event definitions are allowed.
    """
    event_type: str                    # Machine-readable type (e.g., "task.completed")
    
    # Semantic classification
    event_kind: EventType = EventType.EVENT  # EVENT, COMMAND, QUERY, MESSAGE
    
    # Schema information
    schema_version: int = 1
    payload_schema: Optional[str] = None  # JSON schema or description
    
    # Ownership
    owner_id: str = ""                 # Which module/component owns this event
    
    # Semantics
    is_durable: bool = False           # Should be persisted?
    is_ordered: bool = False           # Must maintain ordering?
    
    # Delivery semantics
    delivery_mode: str = "at-least-once"  # fire-and-forget, at-most-once, at-least-once
    
    def validate_event(self, event: Any) -> bool:
        """Validate an event instance against this descriptor."""
        return True


# =============================================================================
# MESSAGE CONTRACT (transport-independent contract)
# =============================================================================

@dataclass(frozen=True)
class MessageContract:
    """
    Immutable message contract that defines delivery semantics.
    
    Contracts are transport-independent - they define WHAT to deliver,
    not HOW to deliver it.
    """
    message_type: str                  # Machine-readable type
    
    # Routing
    topics: Tuple[str, ...] = ()       # Topics this message belongs to
    routing_keys: Tuple[str, ...] = ()  # Additional routing keys
    
    # Delivery semantics
    delivery_mode: str = "at-least-once"   # fire-and-forget, at-most-once, at-least-once
    is_ordered: bool = False              # Must maintain order?
    ordering_key: Optional[str] = None    # Key for partition ordering
    
    # Reliability
    is_durable: bool = False             # Persist to storage?
    max_retries: int = 3                 # Retry attempts before DLQ
    retry_policy: str = "exponential"     # fixed, exponential
    
    # TTL
    expires_after_seconds: Optional[int] = None
    
    # Ownership
    owner_id: str = ""                   # Who owns this contract


# =============================================================================
# EVENT ENVELOPE (delivery container)
# =============================================================================

@dataclass(frozen=True)
class EventEnvelope:
    """
    Immutable envelope wrapping an event for delivery.
    
    Events represent facts about system state. They never request behavior -
    they merely report what occurred.
    """
    # Envelope identity (required - no defaults)
    envelope_id: str                   # Unique ID for this delivery instance
    
    # Runtime context (required - no defaults before optional fields)
    runtime_id: str                    # Which runtime produced this
    event_type: str                    # Machine-readable type (before metadata with default)
    
    # Event payload (required - no defaults before optional fields)
    payload: Dict[str, Any]            # Domain-specific data (immutable copy)
    
    # Metadata (optional - must come after all required fields)
    metadata: EventMetadata = field(default_factory=EventMetadata)
    
    # Runtime context optional fields
    source_runtime_id: Optional[str] = None  # Original producer if different
    
    # Correlation (optional)
    correlation_id: Optional[CorrelationId] = None
    causation_id: Optional[CausationId] = None
    
    # Delivery tracking (optional)
    created_at_utc: float = field(default_factory=time.time)
    sequence_number: int = 0
    
    def with_metadata(self, metadata: EventMetadata) -> "EventEnvelope":
        """Return copy with updated metadata."""
        return EventEnvelope(
            envelope_id=self.envelope_id,
            runtime_id=self.runtime_id,
            source_runtime_id=self.source_runtime_id,
            event_type=self.event_type,
            payload=dict(self.payload),
            metadata=metadata,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            created_at_utc=self.created_at_utc,
            sequence_number=metadata.sequence_number,
        )
    
    def with_delivery_attempt(self) -> "EventEnvelope":
        """Return copy with incremented delivery attempt count."""
        new_metadata = self.metadata.increment_delivery_attempt()
        return EventEnvelope(
            envelope_id=self.envelope_id,
            runtime_id=self.runtime_id,
            source_runtime_id=self.source_runtime_id,
            event_type=self.event_type,
            payload=dict(self.payload),
            metadata=new_metadata,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            created_at_utc=self.created_at_utc,
            sequence_number=self.sequence_number,
        )


# =============================================================================
# MESSAGE ENVELOPE (routing container)
# =============================================================================

@dataclass(frozen=True)
class MessageEnvelope:
    """
    Immutable envelope wrapping a message for routing and delivery.
    
    Messages request communication but do not mutate runtime state directly.
    They are requests to be processed by recipients.
    """
    # Envelope identity (required - no defaults)
    envelope_id: str
    
    # Runtime context (required - no defaults before optional fields)
    runtime_id: str
    message_type: str                  # e.g., "command", "query", "notification"
    
    # Message payload (required - no defaults before optional fields)
    payload: Dict[str, Any]
    
    # Metadata (optional - must come after all required fields)
    metadata: MessageMetadata = field(default_factory=MessageMetadata)
    
    # Runtime context optional fields
    source_runtime_id: Optional[str] = None
    destination_id: Optional[str] = None
    
    # Routing (optional - must come after required)
    topics: Tuple[str, ...] = field(default_factory=tuple)
    routing_keys: Tuple[str, ...] = field(default_factory=tuple)
    
    # Correlation (optional)
    correlation_id: Optional[CorrelationId] = None
    causation_id: Optional[CausationId] = None
    
    # Delivery tracking (optional)
    created_at_utc: float = field(default_factory=time.time)
    expires_at_utc: Optional[float] = None  # When message expires
    
    def is_expired(self) -> bool:
        """Check if message has expired."""
        if self.expires_at_utc is None:
            return False
        return time.time() > self.expires_at_utc


# =============================================================================
# ID GENERATORS (canonical)
# =============================================================================

def generate_event_id() -> EventId:
    """Generate a unique EventId."""
    return f"evt_{uuid.uuid4().hex[:24]}"


def generate_message_id() -> MessageId:
    """Generate a unique MessageId."""
    return f"msg_{uuid.uuid4().hex[:24]}"


def generate_command_id() -> CommandId:
    """Generate a unique CommandId."""
    return f"cmd_{uuid.uuid4().hex[:24]}"


def generate_query_id() -> QueryId:
    """Generate a unique QueryId."""
    return f"qry_{uuid.uuid4().hex[:24]}"


def generate_correlation_id() -> CorrelationId:
    """Generate a new correlation ID for grouping related artifacts."""
    return str(uuid.uuid4())


def generate_causation_id(from_event_id: EventId) -> CausationId:
    """Generate causation ID from an existing event."""
    return f"causes_{from_event_id}"


# =============================================================================
# CONTRACT REGISTRY (central contract authority)
# =============================================================================

class ContractRegistry:
    """
    Central registry for message contracts.
    
    This is THE ONE authority for message contract definitions in the system.
    Every published message MUST have a matching contract in this registry.
    """
    
    def __init__(self):
        self._contracts: Dict[str, MessageContract] = {}
        self._event_descriptors: Dict[str, EventDescriptor] = {}
        self._lock = None
    
    def register_contract(self, contract: MessageContract) -> bool:
        """Register a message contract. Returns False if duplicate."""
        if contract.message_type in self._contracts:
            return False
        self._contracts[contract.message_type] = contract
        return True
    
    def register_event_descriptor(self, descriptor: EventDescriptor) -> bool:
        """Register an event type descriptor. Returns False if duplicate."""
        if descriptor.event_type in self._event_descriptors:
            return False
        self._event_descriptors[descriptor.event_type] = descriptor
        return True
    
    def get_contract(self, message_type: str) -> Optional[MessageContract]:
        """Get contract for a message type."""
        return self._contracts.get(message_type)
    
    def get_descriptor(self, event_type: str) -> Optional[EventDescriptor]:
        """Get descriptor for an event type."""
        return self._event_descriptors.get(event_type)
    
    def validate_envelope(self, envelope: EventEnvelope) -> Tuple[bool, Optional[str]]:
        """
        Validate an envelope against its contract.
        Returns (is_valid, error_message).
        """
        descriptor = self._event_descriptors.get(envelope.event_type)
        if descriptor is None:
            return False, f"Unknown event type: {envelope.event_type}"
        return True, None
    
    def get_all_contracts(self) -> Dict[str, MessageContract]:
        """Get all registered contracts."""
        return dict(self._contracts)


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Unique identifiers
    "EventId", "MessageId", "CommandId", "QueryId",
    "CorrelationId", "CausationId", "PublisherId", "SubscriberId",
    "TopicId", "ChannelId", "RuntimeId", "SequenceNumber",
    
    # Priority
    "PriorityLevel", "priority_value",
    
    # Semantic types
    "EventType",
    
    # Failures/Exceptions
    "EventError", "RoutingError", "PublicationError", "SubscriptionError",
    "ContractError", "SerializationError", "BusError", "TopicError",
    "ChannelError", "DeliveryError", "TransportError", "FlowControlError",
    
    # Metadata
    "EventMetadata", "MessageMetadata",
    
    # Contracts
    "EventDescriptor", "MessageContract", "ContractRegistry",
    
    # Envelopes
    "EventEnvelope", "MessageEnvelope",
    
    # ID generators
    "generate_event_id", "generate_message_id", "generate_command_id",
    "generate_query_id", "generate_correlation_id", "generate_causation_id",
]