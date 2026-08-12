# Core Communication Envelopes
# =============================

"""
Immutable envelopes for events, messages, and signals.

Envelopes wrap artifacts with delivery context while preserving immutability.
They enable:
- Runtime-scoped delivery context
- Acknowledgement tracking
- Routing metadata

All envelope types are frozen dataclasses - once created, they never change.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum, auto
import time
import hashlib


# =============================================================================
# MESSAGE INTEGRITY
# =============================================================================
# SHA256 hash for message integrity verification (COMM-HIGH-001)

@dataclass(frozen=True)
class MessageIntegrity:
    """
    Immutable integrity metadata for messages.
    
    Provides message authentication and tamper detection via SHA256 hash.
    Used to verify that message content has not been modified in transit.
    """
    
    sha256_hash: str           # Base64-encoded SHA256 hash of payload
    version: int = 1           # Integrity schema version for evolution
    
    @classmethod
    def compute(cls, payload: Dict[str, Any], version: int = 1) -> "MessageIntegrity":
        """Compute integrity from payload."""
        payload_str = str(sorted(payload.items())) if payload else ""
        hash_value = hashlib.sha256(payload_str.encode()).hexdigest()
        return cls(sha256_hash=hash_value, version=version)
    
    def verify(self, payload: Dict[str, Any]) -> bool:
        """Verify payload matches stored hash."""
        computed = self.compute(payload, self.version)
        return computed.sha256_hash == self.sha256_hash


# =============================================================================
# ACKNOWLEDGEMENT STATES
# =============================================================================

class Acknowledgement(Enum):
    """
    Delivery acknowledgment states.
    
    States progress linearly:
        PENDING -> ACCEPTED -> DELIVERED (or REJECTED/EXPIRED/FAILED)
    """
    PENDING = "pending"         # Waiting for delivery attempt
    ACCEPTED = "accepted"       # Accepted by subscriber queue
    DELIVERED = "delivered"     # Successfully delivered to subscriber
    REJECTED = "rejected"       # Subscriber rejected (policy, validation, etc.)
    EXPIRED = "expired"         # Message expired before delivery
    FAILED = "failed"           # Delivery failed (subscriber error, timeout)


# =============================================================================
# DELIVERY CONTEXT
# =============================================================================

@dataclass(frozen=True)
class DeliveryContext:
    """
    Runtime delivery context for a single delivery attempt.
    
    Contains runtime-specific information about how an artifact was delivered.
    Never mutates after creation - new attempts create new contexts.
    """
    
    runtime_id: str              # Which runtime performed the delivery
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    subscriber_id: Optional[str] = None  # Who received it
    channel_name: Optional[str] = None   # Via which channel
    
    # Delivery mode details
    delivery_mode: str = "synchronous"   # sync, async, queued, immediate, reliable, best_effort
    priority: int = 0                    # Priority level (lower = higher)
    
    # Timing metrics (for diagnostics)
    queue_wait_ms: float = 0.0           # Time spent in queue
    delivery_latency_ms: float = 0.0     # Total delivery latency
    
    def with_subscriber(self, subscriber_id: str) -> "DeliveryContext":
        """Return copy with subscriber ID set."""
        return DeliveryContext(
            runtime_id=self.runtime_id,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            subscriber_id=subscriber_id,
            channel_name=self.channel_name,
            delivery_mode=self.delivery_mode,
            priority=self.priority,
            queue_wait_ms=self.queue_wait_ms,
            delivery_latency_ms=self.delivery_latency_ms,
        )
    
    def with_channel(self, channel: str) -> "DeliveryContext":
        """Return copy with channel name set."""
        return DeliveryContext(
            runtime_id=self.runtime_id,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            subscriber_id=self.subscriber_id,
            channel_name=channel,
            delivery_mode=self.delivery_mode,
            priority=self.priority,
            queue_wait_ms=self.queue_wait_ms,
            delivery_latency_ms=self.delivery_latency_ms,
        )


# =============================================================================
# EVENT ENVELOPE
# =============================================================================

@dataclass(frozen=True)
class EventEnvelope:
    """
    Immutable envelope wrapping an event for delivery.
    
    Events represent facts about system state. They never request behavior -
    they merely report what occurred.
    
    The envelope adds runtime delivery context while the event payload
    remains immutable.
    
    Usage:
        # Create an event with metadata
        event = Event(
            event_id=generate_event_id(),
            payload={"type": "task_completed", "task_id": "123"},
            metadata=EventMetadata(event_type="task.completed")
        )
        
        # Wrap in envelope for delivery
        envelope = EventEnvelope(
            envelope_id=str(uuid.uuid4()),
            runtime_id="runtime-abc",
            event_type=event.event_type,
            payload=dict(event.payload),
            source_runtime_id=None,
            correlation_id="req-xyz",
            causation_id=None,
        )
        
        # Publish - envelope is immutable, can't be modified
        bus.publish(envelope)
    """
    
    # Envelope identity and runtime (required fields without defaults)
    envelope_id: str             # Unique ID for this envelope instance
    runtime_id: str              # Which runtime produced this
    
    # Event payload (required before optional traceability fields)
    event_type: str              # Machine-readable type (e.g., "task.completed")
    payload: Dict[str, Any]      # Domain-specific data
    
    # Optional fields with defaults must come after required fields
    source_runtime_id: Optional[str] = None  # Original producer if different
    correlation_id: Optional[str] = None     # Groups related artifacts
    causation_id: Optional[str] = None       # What caused this event
    created_at_utc: float = field(default_factory=time.time)   # Timestamps
    monotonic_time: float = field(default_factory=time.monotonic)
    
    sequence_number: int = 0                   # Sequence for ordering within a stream
    schema_version: int = 1                    # Serialization schema version (COMM-MED-002)
    
    # Delivery tracking (read-only, updated via new envelope on retry)
    delivery_attempts: int = 0
    last_delivery_attempt_utc: Optional[float] = None
    
    def with_sequence(self, seq: int) -> "EventEnvelope":
        """Return copy with updated sequence number."""
        return EventEnvelope(
            envelope_id=self.envelope_id,
            runtime_id=self.runtime_id,
            event_type=self.event_type,
            payload=dict(self.payload),
            source_runtime_id=self.source_runtime_id,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            created_at_utc=self.created_at_utc,
            monotonic_time=self.monotonic_time,
            sequence_number=seq,
            schema_version=self.schema_version,
            delivery_attempts=self.delivery_attempts,
            last_delivery_attempt_utc=self.last_delivery_attempt_utc,
        )
    
    def with_delivery_attempt(self) -> "EventEnvelope":
        """Return copy with incremented delivery attempt count."""
        return EventEnvelope(
            envelope_id=self.envelope_id,
            runtime_id=self.runtime_id,
            event_type=self.event_type,
            payload=dict(self.payload),
            source_runtime_id=self.source_runtime_id,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            created_at_utc=self.created_at_utc,
            monotonic_time=self.monotonic_time,
            sequence_number=self.sequence_number,
            delivery_attempts=self.delivery_attempts + 1,
            last_delivery_attempt_utc=time.time(),
        )


# =============================================================================
# MESSAGE ENVELOPE
# =============================================================================

@dataclass(frozen=True)
class MessageEnvelope:
    """
    Immutable envelope wrapping a message for routing and delivery.
    
    Messages request communication but do not mutate runtime state directly.
    They are requests to be processed by recipients.
    
    The envelope contains routing metadata while the message remains immutable.
    
    Integrity is enforced via SHA256 hash of payload (COMM-HIGH-001).
    """
    
    # Envelope identity and runtime (required fields without defaults)
    envelope_id: str
    runtime_id: str
    
    # Message type and payload (required before optional fields)
    message_type: str            # e.g., "command", "query", "notification"
    payload: Dict[str, Any]
    
    # Optional fields with defaults must come after required fields
    source_runtime_id: Optional[str] = None
    destination_id: Optional[str] = None  # Target subscriber or channel
    topic: Optional[str] = None           # Topic for publish/subscribe
    routing_keys: List[str] = field(default_factory=list)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Priority (affects queue position)
    priority: int = 0
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Expiration (for delayed delivery)
    expires_at_utc: Optional[float] = None
    
    schema_version: int = 1                    # Serialization schema version (COMM-MED-002)
    
    # Message integrity (COMM-HIGH-001 - SHA256 hash of payload)
    integrity: Optional[MessageIntegrity] = None
    
    def with_destination(self, dest_id: str) -> "MessageEnvelope":
        """Return copy with destination ID set."""
        return MessageEnvelope(
            envelope_id=self.envelope_id,
            runtime_id=self.runtime_id,
            message_type=self.message_type,
            payload=dict(self.payload),
            source_runtime_id=self.source_runtime_id,
            destination_id=dest_id,
            topic=self.topic,
            routing_keys=list(self.routing_keys),
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            priority=self.priority,
            created_at_utc=self.created_at_utc,
            monotonic_time=self.monotonic_time,
            expires_at_utc=self.expires_at_utc,
        )
    
    def with_topic(self, topic: str) -> "MessageEnvelope":
        """Return copy with topic set."""
        return MessageEnvelope(
            envelope_id=self.envelope_id,
            runtime_id=self.runtime_id,
            message_type=self.message_type,
            payload=dict(self.payload),
            source_runtime_id=self.source_runtime_id,
            destination_id=self.destination_id,
            topic=topic,
            routing_keys=list(self.routing_keys),
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            priority=self.priority,
            created_at_utc=self.created_at_utc,
            monotonic_time=self.monotonic_time,
            expires_at_utc=self.expires_at_utc,
        )
    
    def is_expired(self) -> bool:
        """Check if message has expired."""
        if self.expires_at_utc is None:
            return False
        return time.time() > self.expires_at_utc
    
    def verify_integrity(self) -> bool:
        """Verify message payload integrity."""
        if self.integrity is None:
            # No integrity metadata - cannot verify
            return True
        return self.integrity.verify(self.payload)


# =============================================================================
# SIGNAL ENVELOPE
# =============================================================================

@dataclass(frozen=True)
class SignalEnvelope:
    """
    Immutable envelope wrapping a signal for propagation.
    
    Signals represent runtime transitions - state changes that occur
    without explicit requests. They never become lifecycle authorities.
    
    Usage:
        # Create a signal for a runtime transition
        signal = SignalEnvelope(
            signal_id=str(uuid.uuid4()),
            runtime_id="runtime-abc",
            signal_type="lifecycle.transition",
            payload={"from": "ready", "to": "running"}
        )
        
        # Publish to signal manager
        signal_manager.publish(signal)
    """
    
    # Envelope identity and runtime (required fields without defaults)
    envelope_id: str
    runtime_id: str
    
    # Signal payload (required before optional traceability fields)
    signal_type: str             # e.g., "lifecycle.transition", "task.cancelled"
    payload: Dict[str, Any]
    
    # Target information (optional)
    target_id: Optional[str] = None  # Specific recipient if directed
    broadcast: bool = False          # True = send to all subscribers
    
    schema_version: int = 1                    # Serialization schema version (COMM-MED-002)
    
    # Optional fields with defaults must come after required fields
    source_runtime_id: Optional[str] = None
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    created_at_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    def with_target(self, target_id: str) -> "SignalEnvelope":
        """Return copy with target ID set (directed signal)."""
        return SignalEnvelope(
            envelope_id=self.envelope_id,
            runtime_id=self.runtime_id,
            signal_type=self.signal_type,
            payload=dict(self.payload),
            target_id=target_id,
            broadcast=False,  # Directed
            source_runtime_id=self.source_runtime_id,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            created_at_utc=self.created_at_utc,
            monotonic_time=self.monotonic_time,
        )
    
    def to_broadcast(self) -> "SignalEnvelope":
        """Return copy configured as broadcast signal."""
        return SignalEnvelope(
            envelope_id=self.envelope_id,
            runtime_id=self.runtime_id,
            signal_type=self.signal_type,
            payload=dict(self.payload),
            target_id=None,
            broadcast=True,  # Broadcast to all
            source_runtime_id=self.source_runtime_id,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            created_at_utc=self.created_at_utc,
            monotonic_time=self.monotonic_time,
        )


# =============================================================================
# DELIVERY REPORT (for tracking)
# =============================================================================

@dataclass(frozen=True)
class DeliveryReport:
    """
    Immutable record of a delivery attempt's outcome.
    
    Used for observability and debugging. Never mutates - each attempt
    produces a new report.
    """
    
    envelope_id: str             # Which envelope was delivered
    runtime_id: str              # Runtime where delivery occurred
    
    delivery_time_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    subscriber_id: Optional[str] = None  # Who received it
    channel_name: Optional[str] = None   # Via which channel
    
    # Outcome
    status: Acknowledgement = Acknowledgement.PENDING
    error_message: Optional[str] = None  # If failed
    
    # Timing metrics (in milliseconds)
    queue_wait_ms: float = 0.0
    delivery_latency_ms: float = 0.0
    processing_latency_ms: float = 0.0
    
    # Delivery chain (for replay/debugging)
    previous_attempt_id: Optional[str] = None
    
    @classmethod
    def success(
        cls,
        envelope_id: str,
        runtime_id: str,
        subscriber_id: str,
        channel_name: str,
        queue_wait_ms: float,
        delivery_latency_ms: float,
        processing_latency_ms: float,
    ) -> "DeliveryReport":
        """Create a successful delivery report."""
        return cls(
            envelope_id=envelope_id,
            runtime_id=runtime_id,
            subscriber_id=subscriber_id,
            channel_name=channel_name,
            status=Acknowledgement.DELIVERED,
            queue_wait_ms=queue_wait_ms,
            delivery_latency_ms=delivery_latency_ms,
            processing_latency_ms=processing_latency_ms,
        )
    
    @classmethod
    def failure(
        cls,
        envelope_id: str,
        runtime_id: str,
        error_message: str,
        status: Acknowledgement = Acknowledgement.FAILED,
        queue_wait_ms: float = 0.0,
        delivery_latency_ms: float = 0.0,
        processing_latency_ms: float = 0.0,
    ) -> "DeliveryReport":
        """Create a failure delivery report."""
        return cls(
            envelope_id=envelope_id,
            runtime_id=runtime_id,
            status=status,
            error_message=error_message,
            queue_wait_ms=queue_wait_ms,
            delivery_latency_ms=delivery_latency_ms,
            processing_latency_ms=processing_latency_ms,
        )


__all__ = [
    # Integrity verification
    "MessageIntegrity",
    
    # Acknowledgement states
    "Acknowledgement",
    
    # Delivery context
    "DeliveryContext",
    
    # Envelopes
    "EventEnvelope",
    "MessageEnvelope",
    "SignalEnvelope",
    
    # Reports
    "DeliveryReport",
]
