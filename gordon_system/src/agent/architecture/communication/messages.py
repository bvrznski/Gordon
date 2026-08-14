# Gordon Core - Message Architecture (Phase 3.21.3)
# ==================================================
#
# Canonical message types and structures for communication
#
# Messages are the fundamental units of communication between endpoints.
# This module defines immutable, typed messages with rich metadata.

"""
Canonical Message Architecture for Gordon Phase 3.21.3

MESSAGE TYPES:
--------------
1. Request: Asks another endpoint to perform work (expects response)
2. Response: Answers a request, completes its lifecycle
3. Command: Expresses intent to perform an action
4. Event: Describes something that already occurred (historical fact)
5. Query: Requests information only without modifying state
6. Notification: Informs without expecting work
7. Broadcast: Sends to multiple endpoints simultaneously
8. Multicast: Sends to a subset of endpoints

MESSAGE INTEGRITY:
------------------
- Immutability: Messages cannot be modified after creation
- Typing: Every message has an explicit type
- Validation: Messages must pass validation before delivery
- Correlation: Related messages are linked via correlation ID
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, TypeVar, Generic, Union
from enum import Enum, auto
import time
import uuid


# =============================================================================
# MESSAGE TYPES ENUMERATION
# =============================================================================

class MessageType(Enum):
    """
    Canonical message types.
    
    Every message shall belong to exactly one type.
    """
    
    REQUEST = "request"         # Asks another endpoint to perform work
    RESPONSE = "response"       # Answers a request, completes its lifecycle
    COMMAND = "command"         # Expresses intent to perform an action
    EVENT = "event"             # Describes something that already occurred
    QUERY = "query"             # Requests information only (read-only)
    NOTIFICATION = "notification"  # Informs without expecting work
    BROADCAST = "broadcast"     # Sends to multiple endpoints simultaneously
    MULTICAST = "multicast"     # Sends to a subset of endpoints


# =============================================================================
# MESSAGE PRIORITY LEVELS
# =============================================================================

class MessagePriority(Enum):
    """
    Canonical message priority levels.
    
    Lower values indicate higher priority (0 = highest).
    """
    
    CRITICAL = 0    # Immediate processing required
    HIGH = 1        # Processing within short timeframe
    NORMAL = 2      # Standard processing priority
    LOW = 3         # Processing when resources available
    BACKGROUND = 4  # Lowest priority, can be deferred


# =============================================================================
# MESSAGE STATUS ENUMERATION
# =============================================================================

class MessageStatus(Enum):
    """
    Canonical message status values.
    
    Invariants:
        - MSG-STS-001: Status is immutable once set to terminal state
        - MSG-STS-002: Terminal states preserve all provenance data
    """
    
    CREATED = "created"           # Message created but not yet validated
    VALIDATED = "validated"       # Validation passed, ready for routing
    ROUTED = "routed"             # Routed to target endpoints
    DELIVERING = "delivering"     # Currently being delivered
    DELIVERED = "delivered"       # Successfully delivered
    ACKNOWLEDGED = "acknowledged" # Acknowledged by recipient
    EXPIRED = "expired"           # Message lifetime exceeded
    DROPPED = "dropped"           # Dropped due to policy violations
    DEAD_LETTER = "dead_letter"   # Moved to dead-letter queue


# =============================================================================
# MESSAGE IDENTITY
# =============================================================================

@dataclass(frozen=True)
class MessageId:
    """
    Unique identifier for a message.
    
    Invariants:
        - MSG-ID-001: Every message has exactly one unique identity
        - MSG-ID-002: Identity is immutable once created
        - MSG-ID-003: No two messages share the same identity
    """
    
    value: str
    
    @classmethod
    def generate(cls) -> "MessageId":
        """Generate a new unique message ID."""
        return cls(value=f"msg_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# CORRELATION CONTEXT
# =============================================================================

@dataclass(frozen=True)
class MessageCorrelation:
    """
    Immutable correlation context for message relationships.
    
    Enables tracing of related messages across the system.
    
    Args:
        correlation_id: Links all related messages together
        causation_id: The specific message that caused this one
        parent_message_id: If this is a child of another message
        originating_thread_id: Which thread started the chain
    """
    
    correlation_id: str  # All related messages share same correlation ID
    causation_id: Optional[str] = None  # Direct cause
    parent_message_id: Optional[str] = None  # Parent in hierarchy
    originating_thread_id: Optional[str] = None  # Root thread ID
    
    @classmethod
    def create_root(cls) -> "MessageCorrelation":
        """Create a root correlation context (no parents/causation)."""
        return cls(correlation_id=uuid.uuid4().hex[:16])
    
    @classmethod
    def create_child(
        cls,
        parent_correlation: "MessageCorrelation",
        causation_id: str,
    ) -> "MessageCorrelation":
        """Create a child correlation context."""
        return cls(
            correlation_id=parent_correlation.correlation_id,
            causation_id=causation_id,
            parent_message_id=causation_id,
        )


# =============================================================================
# MESSAGE PROVENANCE
# =============================================================================

@dataclass(frozen=True)
class MessageProvenance:
    """
    Immutable provenance record for a message.
    
    Args:
        source_runtime_id: Runtime where message originated
        source_endpoint_id: Endpoint that created the message
        creation_timestamp_utc: When it was created (UTC wall time)
        monotonic_time: Monotonic clock at creation
        sequence_number: Order number within correlation chain
    """
    
    source_runtime_id: str
    source_endpoint_id: str
    creation_timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    sequence_number: int = 1
    
    def next_in_chain(self) -> "MessageProvenance":
        """Create the next message in the correlation chain."""
        return MessageProvenance(
            source_runtime_id=self.source_runtime_id,
            source_endpoint_id=self.source_endpoint_id,
            creation_timestamp_utc=time.time(),
            monotonic_time=time.monotonic(),
            sequence_number=self.sequence_number + 1,
        )


# =============================================================================
# MESSAGE PAYLOAD (Generic)
# =============================================================================

T = TypeVar("T")


@dataclass(frozen=True)
class MessagePayload(Generic[T]):
    """
    Generic message payload container.
    
    Args:
        data: The actual message content (typed)
        schema_version: Version of the payload schema
        encoding: Encoding format (e.g., "json", "protobuf")
        size_bytes: Size of the serialized payload
    """
    
    data: T
    schema_version: str = "1.0"
    encoding: str = "json"
    size_bytes: int = 0


# =============================================================================
# CANONICAL MESSAGE BASE CLASS
# =============================================================================

@dataclass(frozen=True, slots=True)
class CanonicalMessage:
    """
    Immutable canonical message base class.
    
    Every message in the Gordon architecture shall inherit from this or
    implement equivalent semantics.
    
    Invariants:
        - MSG-001: Messages are immutable after creation
        - MSG-002: Each message has exactly one type
        - MSG-003: Message identity is unique and immutable
        - MSG-004: Correlation preserves relationship chains
        - MSG-005: Provenance is preserved throughout lifecycle
    
    Args:
        message_id: Unique identifier for this message instance
        message_type: The type of this message (Request, Command, etc.)
        
        # Content
        payload: The actual message content
        
        # Correlation
        correlation: Context linking related messages
        
        # Lifecycle
        status: Current lifecycle status
        timestamp_utc: When this was created/modified
        
        # Provenance
        provenance: Where this message came from
        
        # Routing
        target_endpoint_ids: Intended recipients (empty = broadcast)
        
        # Priority and delivery
        priority: Delivery priority level
        expiry_utc: When this message expires (None = no expiry)
    """
    
    # Identity
    message_id: str
    message_type: MessageType
    
    # Content
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Correlation
    correlation: MessageCorrelation = field(default_factory=MessageCorrelation.create_root)
    
    # Lifecycle
    status: MessageStatus = MessageStatus.CREATED
    timestamp_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Optional[MessageProvenance] = None
    
    # Routing
    target_endpoint_ids: Tuple[str, ...] = field(default_factory=tuple)
    
    # Priority and delivery
    priority: MessagePriority = MessagePriority.NORMAL
    expiry_utc: Optional[float] = None
    
    @classmethod
    def create(
        cls,
        message_type: MessageType,
        payload: Dict[str, Any],
        source_endpoint_id: str,
        target_endpoint_ids: Optional[Tuple[str, ...]] = None,
    ) -> "CanonicalMessage":
        """Create a new canonical message with defaults."""
        return cls(
            message_id=uuid.uuid4().hex[:16],
            message_type=message_type,
            payload=dict(payload),
            provenance=MessageProvenance(
                source_runtime_id="",
                source_endpoint_id=source_endpoint_id,
            ),
            target_endpoint_ids=target_endpoint_ids or (),
        )
    
    @classmethod
    def create_request(
        cls,
        payload: Dict[str, Any],
        source_endpoint_id: str,
        target_endpoint_id: Optional[str] = None,
    ) -> "CanonicalMessage":
        """Create a new request message."""
        return cls.create(
            message_type=MessageType.REQUEST,
            payload=dict(payload),
            source_endpoint_id=source_endpoint_id,
            target_endpoint_ids=(target_endpoint_id,) if target_endpoint_id else (),
        )
    
    @classmethod
    def create_command(
        cls,
        payload: Dict[str, Any],
        source_endpoint_id: str,
        target_endpoint_id: Optional[str] = None,
    ) -> "CanonicalMessage":
        """Create a new command message."""
        return cls.create(
            message_type=MessageType.COMMAND,
            payload=dict(payload),
            source_endpoint_id=source_endpoint_id,
            target_endpoint_ids=(target_endpoint_id,) if target_endpoint_id else (),
        )
    
    @classmethod
    def create_event(
        cls,
        event_name: str,
        event_data: Dict[str, Any],
        source_endpoint_id: str,
    ) -> "CanonicalMessage":
        """Create a new event message."""
        return cls.create(
            message_type=MessageType.EVENT,
            payload={"event": event_name, **event_data},
            source_endpoint_id=source_endpoint_id,
        )
    
    @classmethod
    def create_response(
        cls,
        request_message_id: str,
        payload: Dict[str, Any],
        source_endpoint_id: str,
    ) -> "CanonicalMessage":
        """Create a new response message (reply to a request)."""
        # Create correlation chain from the request
        correlation = MessageCorrelation.create_root()
        
        return cls(
            message_id=uuid.uuid4().hex[:16],
            message_type=MessageType.RESPONSE,
            payload=dict(payload),
            correlation=correlation,
            provenance=MessageProvenance(
                source_runtime_id="",
                source_endpoint_id=source_endpoint_id,
            ),
            target_endpoint_ids=(request_message_id,),  # Response goes back to request origin
        )
    
    def with_status(self, new_status: MessageStatus) -> "CanonicalMessage":
        """Create a copy of this message with updated status."""
        if self.status == MessageStatus.DEAD_LETTER and new_status != MessageStatus.DEAD_LETTER:
            raise ValueError("Cannot change status from DEAD_LETTER")
        
        return CanonicalMessage(
            message_id=self.message_id,
            message_type=self.message_type,
            payload=dict(self.payload),
            correlation=self.correlation,
            status=new_status,
            timestamp_utc=time.time(),
            provenance=self.provenance,
            target_endpoint_ids=tuple(self.target_endpoint_ids),
            priority=self.priority,
            expiry_utc=self.expiry_utc,
        )
    
    def is_expired(self) -> bool:
        """Check if this message has expired."""
        if self.expiry_utc is None:
            return False
        return time.time() > self.expiry_utc
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "status": self.status.value,
            "correlation_id": self.correlation.correlation_id,
            "timestamp_utc": self.timestamp_utc,
            "payload": dict(self.payload),
        }
    
    def __hash__(self) -> int:
        """Hash based on immutable message_id."""
        return hash(self.message_id)
    
    def __eq__(self, other: object) -> bool:
        """Equality based on immutable message_id."""
        if not isinstance(other, CanonicalMessage):
            return False
        return self.message_id == other.message_id


# =============================================================================
# MESSAGE CONCRETE SUBTYPES
# =============================================================================

@dataclass(frozen=True, slots=True)
class RequestMessage(CanonicalMessage):
    """
    A Request message asks another endpoint to perform work.
    
    Request-specific properties:
        - request_id: Optional ID of the original request (for retries)
        - response_expected: Whether a response is expected
        - timeout_seconds: How long to wait for response
    """
    
    # Identity override with explicit type
    message_type: MessageType = field(default=MessageType.REQUEST, init=False)
    
    # Request-specific properties
    request_id: Optional[str] = None  # For idempotent requests
    response_expected: bool = True
    timeout_seconds: float = 30.0


@dataclass(frozen=True, slots=True)
class ResponseMessage(CanonicalMessage):
    """
    A Response message answers a Request and completes its lifecycle.
    
    Response-specific properties:
        - request_message_id: Which request this answers
        - success: Whether the request was successful
        - error_message: Error details if failed
    """
    
    # Identity override with explicit type
    message_type: MessageType = field(default=MessageType.RESPONSE, init=False)
    
    # Response-specific properties
    request_message_id: str = ""
    success: bool = True
    error_message: Optional[str] = None


@dataclass(frozen=True, slots=True)
class CommandMessage(CanonicalMessage):
    """
    A Command message expresses intent to perform an action.
    
    Command-specific properties:
        - command_type: Type of command being issued
        - idempotency_key: For safe retries (same key = same result)
    """
    
    # Identity override with explicit type
    message_type: MessageType = field(default=MessageType.COMMAND, init=False)
    
    # Command-specific properties
    command_type: str = "unknown"
    idempotency_key: Optional[str] = None


@dataclass(frozen=True, slots=True)
class EventMessage(CanonicalMessage):
    """
    An Event message describes something that already occurred.
    
    Event-specific properties:
        - event_name: Human-readable name of the event
        - event_timestamp_utc: When the event actually occurred
        - is_historical: Whether this is a historical replay
    """
    
    # Identity override with explicit type
    message_type: MessageType = field(default=MessageType.EVENT, init=False)
    
    # Event-specific properties
    event_name: str = ""
    event_timestamp_utc: float = field(default_factory=time.time)
    is_historical: bool = False


@dataclass(frozen=True, slots=True)
class QueryMessage(CanonicalMessage):
    """
    A Query message requests information only without modifying state.
    
    Query-specific properties:
        - query_type: Type of query (e.g., "read", "filter", "aggregate")
        - result_expected: Whether results are expected
    """
    
    # Identity override with explicit type
    message_type: MessageType = field(default=MessageType.QUERY, init=False)
    
    # Query-specific properties
    query_type: str = ""
    result_expected: bool = True


@dataclass(frozen=True, slots=True)
class NotificationMessage(CanonicalMessage):
    """
    A Notification message informs without expecting work.
    
    Notification-specific properties:
        - importance: How urgent this notification is
        - is_one_way: Whether no acknowledgment is expected
    """
    
    # Identity override with explicit type
    message_type: MessageType = field(default=MessageType.NOTIFICATION, init=False)
    
    # Notification-specific properties
    importance: str = "normal"  # low, normal, high, critical
    is_one_way: bool = True


# =============================================================================
# MESSAGE VALIDATION RESULT
# =============================================================================

class MessageValidationResult(Enum):
    """
    Canonical message validation result types.
    """
    
    PENDING = "pending"           # Not yet validated
    VALID = "valid"               # Passed all validation checks
    INVALID = "invalid"           # Failed validation
    EXPIRED = "expired"           # Message has expired
    AUTHORIZATION_FAILED = "authorization_failed"  # Missing authorization


@dataclass(frozen=True)
class MessageValidation:
    """
    Record of message validation.
    
    Args:
        result: The validation outcome
        timestamp_utc: When validation occurred
        validator_id: Which validator performed the check
        errors: List of validation error messages (if any)
    """
    
    result: MessageValidationResult = MessageValidationResult.PENDING
    timestamp_utc: float = field(default_factory=time.time)
    validator_id: Optional[str] = None
    errors: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# MESSAGE DELIVERY METADATA
# =============================================================================

@dataclass(frozen=True)
class DeliveryMetadata:
    """
    Metadata about message delivery.
    
    Args:
        delivery_attempts: How many times this was attempted
        last_delivery_attempt_utc: When the most recent attempt occurred
        next_delivery_attempt_utc: When to retry (if applicable)
        delivery_error: Error from last failed delivery attempt
        acknowledged_by: Which recipients have acknowledged
    """
    
    delivery_attempts: int = 0
    last_delivery_attempt_utc: Optional[float] = None
    next_delivery_attempt_utc: Optional[float] = None
    delivery_error: Optional[str] = None
    acknowledged_by: Tuple[str, ...] = field(default_factory=tuple)
    
    def with_attempt(self) -> "DeliveryMetadata":
        """Create a new metadata with incremented delivery attempt."""
        return DeliveryMetadata(
            delivery_attempts=self.delivery_attempts + 1,
            last_delivery_attempt_utc=time.time(),
            next_delivery_attempt_utc=None,
            delivery_error=self.delivery_error,
            acknowledged_by=tuple(self.acknowledged_by),
        )
    
    def with_acknowledgement(self, endpoint_id: str) -> "DeliveryMetadata":
        """Create a new metadata with additional acknowledgement."""
        return DeliveryMetadata(
            delivery_attempts=self.delivery_attempts,
            last_delivery_attempt_utc=self.last_delivery_attempt_utc,
            next_delivery_attempt_utc=self.next_delivery_attempt_utc,
            delivery_error=self.delivery_error,
            acknowledged_by=tuple(set(self.acknowledged_by) | {endpoint_id}),
        )


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Message types
    "MessageType",
    
    # Priority and status
    "MessagePriority",
    "MessageStatus",
    
    # Identity
    "MessageId",
    
    # Correlation
    "MessageCorrelation",
    
    # Provenance
    "MessageProvenance",
    
    # Payload
    "MessagePayload",
    
    # Base message
    "CanonicalMessage",
    
    # Concrete types
    "RequestMessage",
    "ResponseMessage",
    "CommandMessage",
    "EventMessage",
    "QueryMessage",
    "NotificationMessage",
    
    # Validation and delivery
    "MessageValidationResult",
    "MessageValidation",
    "DeliveryMetadata",
]