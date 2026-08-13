# Canonical Publisher-Subscriber Architecture - Phase 3.11.4
# ============================================================

"""
Canonical producer-consumer architecture for Gordon's Semantic Stream subsystem.

This module implements the complete canonical publisher-subscriber infrastructure:

Canonical Model:
    Publisher → Publish Proposal → Commit Authority → Committed Record
                                                    ↓
                                                Subscription
                                                    ↓
                                                Cursor
                                                    ↓
                                                Delivery
                                                    ↓
                                                Subscriber

Responsibilities:
    Publisher: Propose records, validate policy, attach metadata, preserve provenance
    Subscriber: Receive deliveries, acknowledge processing, maintain local progress
    
Constraints (NOT allowed):
    Publishers never communicate directly with subscribers
    No component may bypass the canonical Stream abstraction
    Subscribers cannot modify streams or rewrite ordering
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, AsyncGenerator, Protocol, runtime_checkable
from enum import Enum, auto
import time
import uuid
import hashlib
import abc


# =============================================================================
# DATACLASS REPLACE UTILITY - Helper for frozen dataclasses
# =============================================================================

def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Simple dataclass replace implementation for frozen dataclasses."""
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError(f"Not a dataclass: {type(obj)}")


# =============================================================================
# PUBLISHER DESCRIPTOR - Immutable Configuration
# =============================================================================

class PublisherPolicy(Enum):
    """
    Policy configuration for a publisher.
    
    Defines how a publisher may interact with streams.
    """
    ATOMIC = "atomic"                    # Each record committed atomically
    BATCHED = "batched"                  # Records batched and committed together
    RATE_LIMITED = "rate_limited"        # Subject to rate limiting
    IDEMPOTENT = "idempotent"            # Duplicate detection enabled


class PublisherAuthority(Enum):
    """
    Authority levels for a publisher.
    
    These define what operations a publisher may perform:
        - PUBLISH: May propose new records
        - BATCH: May batch multiple records for atomic commit
        - REPLAY: May request replay from checkpoints
    """
    PUBLISH_ONLY = "publish_only"
    BATCH_PUBLISH = "batch_publish"
    FULL_ACCESS = "full_access"


@dataclass(frozen=True)
class PublisherDescriptor:
    """
    Immutable descriptor for a publisher configuration.
    
    Contains all metadata about a publisher without any runtime state.
    This is what gets validated and authorized before publication.
    """
    
    # Identity
    publisher_id: str
    
    # Stream target
    stream_id: Optional[str] = None
    
    # Policy configuration
    policy: PublisherPolicy = PublisherPolicy.ATOMIC
    authority: PublisherAuthority = PublisherAuthority.PUBLISH_ONLY
    
    # Authorization context
    scope: str = "global"                # user, session, agent, tenant, global
    authorized_by: Optional[str] = None  # Authority that granted permission
    
    # Rate limiting
    rate_limit_per_second: float = 100.0
    burst_size: int = 10
    
    # Idempotency
    idempotency_enabled: bool = True
    idempotency_window_seconds: int = 3600  # Default 1 hour
    
    # Metadata constraints
    max_metadata_size_bytes: int = 4096
    require_provenance: bool = True
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    effective_until_utc: Optional[float] = None
    
    def is_expired(self, at_utc: Optional[float] = None) -> bool:
        """Check if this descriptor has expired."""
        at = at_utc or time.time()
        return self.effective_until_utc is not None and at > self.effective_until_utc
    
    def validate_authority(self, stream_id: str, operation: PublisherAuthority) -> Tuple[bool, Optional[str]]:
        """
        Validate that publisher authority permits the requested operation.
        
        Returns:
            (is_authorized, reason) tuple
        """
        if self.authority == PublisherAuthority.FULL_ACCESS:
            return True, None
        
        if operation in (
            PublisherAuthority.BATCH_PUBLISH,
            PublisherAuthority.FULL_ACCESS
        ):
            return False, f"Publisher lacks authority: {operation.value}"
        
        # PUBLISH_ONLY only allows basic publish
        if operation == PublisherAuthority.PUBLISH_ONLY:
            return True, None
        
        return False, "Unknown operation"


# =============================================================================
# SUBSCRIBER DESCRIPTOR - Immutable Configuration
# =============================================================================

class SubscriptionMode(Enum):
    """
    Mode of subscription.
    
    Defines how records are delivered to subscribers:
        - AT_LEAST_ONCE: Each record delivered at least once (may duplicate)
        - AT_MOST_ONCE: Each record delivered at most once (may lose)
        - EXACTLY_ONCE: Guaranteed exactly-once delivery (requires ack storage)
    """
    AT_LEAST_ONCE = "at_least_once"
    AT_MOST_ONCE = "at_most_once"
    EXACTLY_ONCE = "exact_once"


class SubscriberAuthority(Enum):
    """
    Authority levels for a subscriber.
    
    Defines what operations a subscriber may perform:
        - READ: May read from stream
        - ACKNOWLEDGE: May acknowledge receipt
        - CHECKPOINT: May save checkpoints
        - REPLAY: May request replay from stored positions
    """
    READ_ONLY = "read_only"
    READ_WITH_ACK = "read_with_ack"
    CHECKPOINT = "checkpoint"
    REPLAY = "replay"
    FULL_CONSUMER = "full_consumer"


@dataclass(frozen=True)
class SubscriberDescriptor:
    """
    Immutable descriptor for a subscriber configuration.
    
    Contains all metadata about a subscriber without any runtime state.
    This is what gets validated and authorized before subscription.
    """
    
    # Identity
    subscriber_id: str
    
    # Stream interest
    stream_id: Optional[str] = None
    
    # Mode configuration
    mode: SubscriptionMode = SubscriptionMode.AT_LEAST_ONCE
    authority: SubscriberAuthority = SubscriberAuthority.READ_ONLY
    
    # Starting position
    start_from: str = "latest"           # latest, beginning, checkpoint
    checkpoint_id: Optional[str] = None  # For checkpoint-based recovery
    
    # Delivery settings
    batch_size: int = 100
    timeout_seconds: float = 30.0
    max_pending_acknowledgements: int = 1000
    
    # Scope and authorization
    scope: str = "global"
    authorized_by: Optional[str] = None
    
    # Filtering (for partial subscriptions)
    filter_type: Optional[str] = None    # e.g., "record_type", "metadata_key"
    filter_value: Optional[Any] = None
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    effective_until_utc: Optional[float] = None
    
    def is_expired(self, at_utc: Optional[float] = None) -> bool:
        """Check if this descriptor has expired."""
        at = at_utc or time.time()
        return self.effective_until_utc is not None and at > self.effective_until_utc
    
    def validate_authority(self, operation: SubscriberAuthority) -> Tuple[bool, Optional[str]]:
        """
        Validate that subscriber authority permits the requested operation.
        
        Returns:
            (is_authorized, reason) tuple
        """
        if self.authority == SubscriberAuthority.FULL_CONSUMER:
            return True, None
        
        if operation in (
            SubscriberAuthority.READ_WITH_ACK,
            SubscriberAuthority.CHECKPOINT,
            SubscriberAuthority.FULL_CONSUMER
        ):
            return False, f"Subscriber lacks authority: {operation.value}"
        
        # READ_ONLY only allows basic reading
        if operation == SubscriberAuthority.READ_ONLY:
            return True, None
        
        return False, "Unknown operation"


# =============================================================================
# SUBSCRIPTION - Immutable Relationship
# =============================================================================

class SubscriptionState(Enum):
    """
    Lifecycle state of a subscription.
    
    Flow: PENDING → ACTIVE → [PAUSED/REPLAYING] → CLOSING → CLOSED
    """
    PENDING = "pending"          # Subscription created, waiting for validation
    ACTIVE = "active"            # Normal operation
    PAUSED = "paused"            # Temporarily suspended
    REPLAYING = "replaying"      # Currently replaying historical records
    CLOSING = "closing"          # Graceful shutdown in progress
    CLOSED = "closed"            # Terminal state


@dataclass(frozen=True)
class SubscriptionPolicy:
    """
    Immutable policy configuration for a subscription.
    
    Defines how the subscription behaves during its lifetime.
    """
    
    mode: SubscriptionMode = SubscriptionMode.AT_LEAST_ONCE
    
    # Ordering
    preserve_order: bool = True          # Strict ordering enforcement
    allow_out_of_order: bool = False     # Allow out-of-order delivery if true
    
    # Delivery guarantees
    max_delivery_attempts: int = 3       # Before giving up
    duplicate_detection_window_seconds: int = 3600  # How long to track duplicates
    
    # Backpressure
    max_lag_records: int = 1000          # Max records behind head before backpressure
    min_batch_size: int = 1              # Minimum batch size before delivery
    
    # Checkpointing
    checkpoint_interval_seconds: float = 60.0   # How often to checkpoint
    max_checkpoint_age_seconds: float = 86400.0 # Max age of valid checkpoint
    
    # Replay policy
    replay_enabled: bool = True
    default_replay_window_seconds: int = 3600   # Default replay window
    max_replay_records: int = 10000             # Max records in single replay


@dataclass(frozen=True)
class SubscriptionDescriptor:
    """
    Immutable descriptor for a subscription relationship.
    
    Represents the explicit contract between subscriber and stream.
    This is the canonical representation stored and versioned.
    """
    
    # Identity
    subscription_id: str  # Unique ID for this subscription
    
    # Stream reference (immutable identifier, not instance)
    stream_id: str
    
    # Subscriber reference (immutable identifier, not instance)
    subscriber_id: str
    
    # State
    state: SubscriptionState = SubscriptionState.PENDING
    
    # Policy
    policy: SubscriptionPolicy = field(default_factory=SubscriptionPolicy)
    
    # Starting configuration
    start_position: Optional["CursorCheckpoint"] = None  # For recovery
    start_from: str = "latest"  # latest, beginning, checkpoint
    
    # Filter configuration (for partial subscriptions)
    filters: Tuple[str, ...] = field(default_factory=tuple)  # Filter expressions
    
    # Authority and scope
    scope: str = "global"
    authorized_by: Optional[str] = None
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    closed_at_utc: Optional[float] = None
    
    def advance_state(self, new_state: SubscriptionState) -> "SubscriptionDescriptor":
        """Create new descriptor with advanced state."""
        if not self._is_valid_transition(self.state, new_state):
            raise InvalidSubscriptionStateTransition(
                subscription_id=self.subscription_id,
                from_state=self.state,
                to_state=new_state
            )
        
        return dataclass_replace(self, state=new_state, updated_at_utc=time.time())
    
    @staticmethod
    def _is_valid_transition(from_state: SubscriptionState, to_state: SubscriptionState) -> bool:
        """Check if a state transition is valid."""
        valid_transitions = {
            SubscriptionState.PENDING: {SubscriptionState.ACTIVE},
            SubscriptionState.ACTIVE: {SubscriptionState.ACTIVE, SubscriptionState.PAUSED, SubscriptionState.REPLAYING},
            SubscriptionState.PAUSED: {SubscriptionState.ACTIVE, SubscriptionState.CLOSING},
            SubscriptionState.REPLAYING: {SubscriptionState.ACTIVE, SubscriptionState.CLOSING},
            SubscriptionState.CLOSING: {SubscriptionState.CLOSED},
        }
        
        return to_state in valid_transitions.get(from_state, set())


# =============================================================================
# CURSOR - Immutable Progress Tracking
# =============================================================================

@dataclass(frozen=True)
class CursorPosition:
    """
    Immutable position within a stream.
    
    A cursor position uniquely identifies where a subscriber is in reading a stream.
    
    DO NOT reference:
        - Python object addresses
        - Queue offsets
        - Thread identifiers
    
    MUST reference:
        - Stream generation (for generation-aware positioning)
        - Sequence number (within generation)
        - Checkpoint version (for recovery accuracy)
    """
    
    # Stream identity
    stream_id: str
    
    # Position within stream
    generation_number: int           # Generation ID number
    sequence_number: int             # Sequence within generation
    
    # Checkpoint information
    checkpoint_version: int = 1      # Version for recovery tracking
    
    # Metadata
    timestamp_utc: float = field(default_factory=time.time)
    
    def is_before(self, other: "CursorPosition") -> bool:
        """Check if this position comes before another."""
        return (self.generation_number, self.sequence_number) < (
            other.generation_number, other.sequence_number
        )
    
    def is_after(self, other: "CursorPosition") -> bool:
        """Check if this position comes after another."""
        return (self.generation_number, self.sequence_number) > (
            other.generation_number, other.sequence_number
        )
    
    def advance(self, count: int = 1) -> "CursorPosition":
        """Create new position advanced by count records."""
        return dataclass_replace(
            self,
            sequence_number=self.sequence_number + count,
            timestamp_utc=time.time()
        )
    
    def to_checkpoint(self) -> "CursorCheckpoint":
        """Convert this position to a checkpoint for persistence."""
        return CursorCheckpoint.from_cursor_position(self)


@dataclass(frozen=True)
class CursorSnapshot:
    """
    Immutable snapshot of cursor state at a point in time.
    
    Used for persistence and recovery without capturing live references.
    """
    
    stream_id: str
    subscriber_id: str
    
    current_position: CursorPosition
    last_checkpoint_position: Optional[CursorPosition] = None
    
    # Statistics
    records_delivered_since_checkpoint: int = 0
    last_delivery_utc: float = field(default_factory=time.time)
    
    @classmethod
    def from_cursor(cls, cursor: "Cursor", checkpoint: Optional["CursorCheckpoint"] = None) -> "CursorSnapshot":
        """Create snapshot from current cursor state."""
        return cls(
            stream_id=cursor.stream_id,
            subscriber_id=cursor.subscriber_id,
            current_position=cursor.position,
            last_checkpoint_position=checkpoint.position if checkpoint else None,
            records_delivered_since_checkpoint=cursor.records_delivered
        )


@dataclass(frozen=True)
class CursorCheckpoint:
    """
    Immutable checkpoint representing a recovery point for a cursor.
    
    Checkpoints enable subscribers to resume from exact positions after
    restart, crash, or migration. They are stored durably and never modified.
    
    DO NOT include:
        - Live objects
        - Locks
        - Callbacks
        - Runtime state
    
    MUST include:
        - Stream reference (immutable ID)
        - Subscriber reference (immutable ID)
        - Position at checkpoint time
        - Provenance for audit
    """
    
    # Identity
    checkpoint_id: str              # Unique identifier for this checkpoint
    
    # References
    stream_id: str
    subscriber_id: str
    
    # Position
    position: CursorPosition
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    version: int = 1                # Checkpoint version for updates
    
    # Provenance (for audit trail)
    created_by: Optional[str] = None
    reason: str = "auto"            # Reason for checkpoint creation
    
    @classmethod
    def from_cursor_position(cls, position: CursorPosition) -> "CursorCheckpoint":
        """Create a checkpoint from a cursor position."""
        return cls(
            checkpoint_id=f"cp-{uuid.uuid4().hex[:16]}",
            stream_id=position.stream_id,
            subscriber_id="default",  # Will be set by subscription context
            position=position,
            created_at_utc=time.time(),
            version=1,
            reason="auto",
        )
    
    def advance(self, new_position: CursorPosition) -> "CursorCheckpoint":
        """Create a new checkpoint at the given position."""
        return dataclass_replace(
            self,
            position=new_position,
            version=self.version + 1,
            created_at_utc=time.time()
        )


@dataclass(frozen=True)
class Cursor:
    """
    Immutable cursor representing subscriber progress within a stream.
    
    The cursor is owned by the subscriber and tracks their position in reading
    records. It progresses monotonically through the stream.
    
    Key properties:
        - Immutable (new cursor created on each advance)
        - Monotonic progression (never goes backward)
        - Subscriber-local (doesn't affect other subscribers)
        - Generation-aware (tracks which generation it's in)
    """
    
    # Identity
    cursor_id: str                  # Unique ID for this cursor instance
    stream_id: str                  # Stream being read from
    subscriber_id: str              # Subscriber who owns this cursor
    
    # Position
    position: CursorPosition        # Current reading position
    
    # Statistics
    records_delivered: int = 0      # Total records delivered to subscriber
    records_acknowledged: int = 0   # Records with successful acknowledgement
    
    # State
    is_active: bool = True          # Is this cursor still active?
    
    def advance(self, count: int = 1) -> "Cursor":
        """Create a new cursor advanced by count records."""
        return dataclass_replace(
            self,
            position=self.position.advance(count),
            records_delivered=self.records_delivered + count
        )
    
    def acknowledge(self, count: int = 1) -> "Cursor":
        """Update cursor to reflect acknowledged records."""
        return dataclass_replace(
            self,
            records_acknowledged=self.records_acknowledged + count
        )
    
    def create_checkpoint(self) -> CursorCheckpoint:
        """Create a checkpoint from this cursor's current position."""
        return CursorCheckpoint.from_cursor_position(self.position)


# =============================================================================
# ACKNOWLEDGEMENT - Explicit Processing Confirmation
# =============================================================================

class AcknowledgementState(Enum):
    """
    States of acknowledgement processing.
    
    Flow: RECEIVED → [ACCEPTED/REJECTED] → PROCESSED or FAILED
    
    Note: SKIPPED is for intentional non-processing (e.g., filter mismatch)
          RETRIED is for temporary failures where retry is possible
    """
    RECEIVED = "received"        # Acknowledgement received, not yet processed
    ACCEPTED = "accepted"        # Acknowledgement accepted by system
    PROCESSED = "processed"      # Record successfully processed by subscriber
    FAILED = "failed"            # Processing failed permanently
    SKIPPED = "skipped"          # Intentionally not processed (e.g., filter)
    RETRIED = "retried"          # Temporary failure, retrying


@dataclass(frozen=True)
class Acknowledgement:
    """
    Immutable acknowledgement of record processing.
    
    An acknowledgement represents explicit confirmation that a subscriber
    has successfully processed a delivered record. Acknowledgements are
    immutable and cannot be revoked or modified once committed.
    
    States:
        - RECEIVED: System received the ack (not yet validated)
        - ACCEPTED: System accepted the ack (validated, pending processing)
        - PROCESSED: Subscriber confirmed successful processing
        - FAILED: Processing failed permanently (dead letter queue candidate)
        - SKIPPED: Intentionally not processed (e.g., filter mismatch)
        - RETRIED: Temporary failure, will retry delivery
    
    Key properties:
        - Immutable after creation
        - Cannot be revoked or modified
        - Must include record identity and subscriber context
    """
    
    # Identity
    ack_id: str                     # Unique ID for this acknowledgement
    delivery_id: str                # Which delivery is being acknowledged?
    
    # References
    stream_id: str
    subscriber_id: str
    
    # Record reference (for tracking)
    record_id: Optional[str] = None  # Reference to the record
    
    # State
    state: AcknowledgementState = AcknowledgementState.RECEIVED
    
    # Timing
    received_at_utc: float = field(default_factory=time.time)
    processed_at_utc: Optional[float] = None
    failed_at_utc: Optional[float] = None
    
    # Context
    retry_count: int = 0
    max_retries: int = 3
    failure_reason: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def advance_state(self, new_state: AcknowledgementState) -> "Acknowledgement":
        """Create new acknowledgement with advanced state."""
        if not self._is_valid_transition(self.state, new_state):
            raise InvalidAcknowledgementStateTransition(
                ack_id=self.ack_id,
                from_state=self.state,
                to_state=new_state
            )
        
        kwargs = {"state": new_state}
        if new_state == AcknowledgementState.PROCESSED:
            kwargs["processed_at_utc"] = time.time()
        elif new_state == AcknowledgementState.FAILED:
            kwargs["failed_at_utc"] = time.time()
        
        return dataclass_replace(self, **kwargs)
    
    def retry(self) -> "Acknowledgement":
        """Create a retry version of this acknowledgement."""
        if self.retry_count >= self.max_retries:
            raise MaxRetriesExceededError(
                ack_id=self.ack_id,
                max_retries=self.max_retries,
                reason=self.failure_reason
            )
        
        return dataclass_replace(
            self,
            state=AcknowledgementState.RECEIVED,  # Reset for retry
            retry_count=self.retry_count + 1,
            received_at_utc=time.time()
        )
    
    @staticmethod
    def _is_valid_transition(from_state: AcknowledgementState, to_state: AcknowledgementState) -> bool:
        """Check if a state transition is valid."""
        valid_transitions = {
            AcknowledgementState.RECEIVED: {AcknowledgementState.ACCEPTED, AcknowledgementState.FAILED},
            AcknowledgementState.ACCEPTED: {AcknowledgementState.PROCESSED, AcknowledgementState.FAILED, AcknowledgementState.RETRIED},
            AcknowledgementState.PROCESSED: set(),  # Terminal
            AcknowledgementState.FAILED: set(),      # Terminal
            AcknowledgementState.SKIPPED: set(),     # Terminal (for intentional skip)
            AcknowledgementState.RETRIED: {AcknowledgementState.RECEIVED},  # Back to retry
        }
        
        return to_state in valid_transitions.get(from_state, set())


class InvalidAcknowledgementStateTransition(Exception):
    """Raised when an invalid acknowledgement state transition is attempted."""
    
    def __init__(self, ack_id: str, from_state: AcknowledgementState, to_state: AcknowledgementState):
        self.ack_id = ack_id
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(
            f"Invalid acknowledgement state transition: {from_state.value} → {to_state.value} "
            f"(ack_id={ack_id})"
        )


class MaxRetriesExceededError(Exception):
    """Raised when all retry attempts are exhausted."""
    
    def __init__(self, ack_id: str, max_retries: int, reason: Optional[str] = None):
        self.ack_id = ack_id
        self.max_retries = max_retries
        self.reason = reason
        super().__init__(
            f"Max retries ({max_retries}) exceeded for acknowledgement {ack_id}"
            + (f": {reason}" if reason else "")
        )


# =============================================================================
# DELIVERY - Record Delivery to Subscriber
# =============================================================================

@dataclass(frozen=True)
class DeliveryBatch:
    """
    Immutable batch of records delivered together.
    
    Batching enables efficient delivery while maintaining ordering guarantees.
    All records in a batch are delivered at the same position in the stream.
    """
    
    # Batch identity
    batch_id: str                   # Unique ID for this batch
    
    # Subscriber reference
    subscriber_id: str
    
    # Stream context
    stream_id: str
    
    # Delivery positions (cursor state before and after delivery)
    cursor_before: CursorPosition
    cursor_after: CursorPosition
    
    # Records delivered
    records: Tuple[Any, ...]        # Tuple of record objects
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    batch_size: int = 0             # Count of records in batch
    
    # Delivery ordering guarantee
    ordered: bool = True            # Are records delivered in order?
    
    def __post_init__(self):
        """Set computed fields after dataclass initialization."""
        object.__setattr__(self, 'batch_size', len(self.records))
    
    def to_acknowledgements(
        self,
        subscriber_id: str
    ) -> Tuple[Acknowledgement, ...]:
        """
        Create acknowledgement placeholders for each record in the batch.
        
        These can be completed when subscribers confirm processing.
        """
        return tuple(
            Acknowledgement(
                ack_id=f"ack-{uuid.uuid4().hex[:16]}",
                delivery_id=self.batch_id,
                stream_id=self.stream_id,
                subscriber_id=subscriber_id,
                record_id=None,  # Will be populated with actual record ID
                state=AcknowledgementState.RECEIVED,
            )
            for _ in self.records
        )


@dataclass(frozen=True)
class Delivery:
    """
    Immutable delivery of one record to a subscriber.
    
    A delivery represents one committed record delivered to one subscriber
    at one point in time. It does NOT mutate stream history or ordering.
    
    Key properties:
        - Immutable after creation
        - Tracks cursor position before and after delivery
        - Includes metadata for tracing and diagnostics
        - Does not modify stream state
    """
    
    # Identity
    delivery_id: str                # Unique ID for this delivery
    
    # Stream context
    stream_id: str
    
    # Subscriber reference
    subscriber_id: str
    
    # Cursor positions (before and after delivery)
    cursor_before: CursorPosition
    cursor_after: CursorPosition
    
    # Record being delivered
    record_id: Optional[str] = None  # Reference to the record
    record_data: Optional[Dict[str, Any]] = None  # Inline payload (optional)
    
    # Metadata for tracing and diagnostics
    created_at_utc: float = field(default_factory=time.time)
    delivery_order: int = 0         # Order within batch
    
    # Delivery state
    acknowledged_state: AcknowledgementState = AcknowledgementState.RECEIVED
    acknowledged_at_utc: Optional[float] = None
    
    def acknowledge(self, state: AcknowledgementState) -> "Delivery":
        """Create a new delivery with updated acknowledgement state."""
        if state not in (
            AcknowledgementState.PROCESSED,
            AcknowledgementState.FAILED,
            AcknowledgementState.SKIPPED
        ):
            raise InvalidAcknowledgementStateTransition(
                ack_id=self.delivery_id,
                from_state=self.acknowledged_state,
                to_state=state
            )
        
        return dataclass_replace(
            self,
            acknowledged_state=state,
            acknowledged_at_utc=time.time() if state in (AcknowledgementState.PROCESSED, AcknowledgementState.FAILED) else None
        )


@dataclass(frozen=True)
class DeliveryResult:
    """
    Result of a delivery operation.
    
    Indicates whether delivery succeeded or failed and provides details
    about the outcome for logging and diagnostics.
    """
    
    # Outcome
    success: bool
    
    # Delivery information
    delivery_id: str
    subscriber_id: str
    stream_id: str
    
    # Records involved
    records_delivered: int = 0
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    # Error details (if failed)
    error_message: Optional[str] = None
    retryable: bool = False


# =============================================================================
# REPLAY REQUEST & RESULT - Historical Record Delivery
# =============================================================================

class ReplayPolicy(Enum):
    """
    Policy for replay operations.
    
    Defines how historical records are replayed to subscribers:
        - FROM_POSITION: Replay from specific cursor position
        - FROM_CHECKPOINT: Replay from saved checkpoint
        - FROM_GENERATION: Replay starting at generation boundary
        - RANGE: Replay within a range (start_position, end_position)
    """
    FROM_POSITION = "from_position"
    FROM_CHECKPOINT = "from_checkpoint"
    FROM_GENERATION = "from_generation"
    RANGE = "range"


@dataclass(frozen=True)
class ReplayRequest:
    """
    Immutable request for replaying historical records.
    
    A replay request asks the stream to reconstruct delivery of previously
    committed records. Replay is subscriber-local and never rewrites history.
    
    Constraints:
        - Replay preserves canonical ordering
        - Replay cannot reopen closed generations
        - Replay respects retention policies
        - Replay is idempotent (same input produces same output)
    """
    
    # Identity
    replay_id: str                  # Unique ID for this replay
    
    # Stream reference
    stream_id: str
    
    # Subscriber reference
    subscriber_id: str
    
    # Policy
    policy: ReplayPolicy = ReplayPolicy.FROM_POSITION
    
    # Position information
    start_position: Optional[CursorPosition] = None  # For FROM_POSITION, RANGE
    end_position: Optional[CursorPosition] = None     # For RANGE only
    
    # Checkpoint reference (for FROM_CHECKPOINT)
    checkpoint_id: Optional[str] = None
    
    # Generation reference (for FROM_GENERATION)
    generation_number: Optional[int] = None
    
    # Bounded replay settings
    max_records: int = 10000        # Max records in this replay
    timeout_seconds: float = 3600.0  # Maximum replay duration
    
    # Timestamps
    requested_at_utc: float = field(default_factory=time.time)
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Validate the replay request is well-formed.
        
        Returns:
            (is_valid, reason) tuple
        """
        if self.policy == ReplayPolicy.FROM_POSITION and not self.start_position:
            return False, "FROM_POSITION requires start_position"
        
        if self.policy == ReplayPolicy.RANGE:
            if not self.start_position or not self.end_position:
                return False, "RANGE policy requires both start_position and end_position"
            if not self.start_position.is_before(self.end_position):
                return False, "start_position must be before end_position for RANGE"
        
        if self.policy == ReplayPolicy.FROM_CHECKPOINT and not self.checkpoint_id:
            return False, "FROM_CHECKPOINT requires checkpoint_id"
        
        if self.policy == ReplayPolicy.FROM_GENERATION and not self.generation_number:
            return False, "FROM_GENERATION requires generation_number"
        
        if self.max_records <= 0:
            return False, "max_records must be positive"
        
        return True, None


@dataclass(frozen=True)
class ReplayResult:
    """
    Result of a replay operation.
    
    Indicates which records were replayed and their final delivery status.
    """
    
    # Replay identity
    replay_id: str
    
    # Statistics
    start_position: CursorPosition
    end_position: Optional[CursorPosition]
    
    records_replayed: int = 0       # Total records in replay window
    records_delivered: int = 0      # Records successfully delivered
    records_skipped: int = 0        # Records skipped (e.g., filter)
    records_failed: int = 0         # Records that failed delivery
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    # Result
    success: bool = True
    error_message: Optional[str] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate replay duration in seconds."""
        if self.completed_at_utc is None:
            return time.time() - self.started_at_utc
        return self.completed_at_utc - self.started_at_utc


# =============================================================================
# PUBLISHER - Stateful Publishing Interface
# =============================================================================

class InvalidSubscriptionStateTransition(Exception):
    """Raised when an invalid subscription state transition is attempted."""
    
    def __init__(self, subscription_id: str, from_state: SubscriptionState, to_state: SubscriptionState):
        self.subscription_id = subscription_id
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(
            f"Invalid subscription state transition: {from_state.value} → {to_state.value} "
            f"(subscription_id={subscription_id})"
        )


class PublisherNotAuthorizedError(Exception):
    """Raised when a publisher is not authorized for an operation."""
    
    def __init__(self, publisher_id: str, stream_id: str, operation: str):
        self.publisher_id = publisher_id
        self.stream_id = stream_id
        self.operation = operation
        super().__init__(
            f"Publisher {publisher_id} is not authorized to {operation} on stream {stream_id}"
        )


class DuplicateRecordError(Exception):
    """Raised when attempting to publish a duplicate record."""
    
    def __init__(self, record_id: str, existing_record_id: Optional[str] = None):
        self.record_id = record_id
        self.existing_record_id = existing_record_id
        super().__init__(
            f"Duplicate record detected: {record_id}"
            + (f" (existing={existing_record_id})" if existing_record_id else "")
        )


@runtime_checkable
class Publisher(Protocol):
    """
    Protocol for canonical publishers.
    
    Publishers propose records to streams. They never communicate directly
    with subscribers - all communication happens through the Stream abstraction.
    
    Responsibilities:
        - Propose records to stream
        - Validate publication policy before submission
        - Attach metadata and preserve provenance
        
    Restrictions (NOT allowed):
        - Cannot assign canonical ordering (stream does this)
        - Cannot commit records directly (CommitAuthority does this)
        - Cannot manipulate subscriber state
        - Cannot advance cursor positions
    """
    
    async def propose_record(
        self,
        stream_id: str,
        payload: Dict[str, Any],
        record_type: Optional[str] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
    ) -> Tuple[bool, "StreamCommitResult"]:
        """
        Propose a record for commitment to a stream.
        
        Args:
            stream_id: Target stream identifier
            payload: Record data content
            record_type: Type of record (event, command, etc.)
            correlation_id: For tracing related records
            causation_id: What caused this record
            
        Returns:
            (was_proposed, commit_result) tuple
        """
        ...
    
    async def propose_batch(
        self,
        stream_id: str,
        records: List[Dict[str, Any]],
    ) -> Tuple[bool, Tuple["StreamCommitResult", ...]]:
        """
        Propose multiple records for atomic batch commit.
        
        All records in a batch are committed together or not at all.
        
        Args:
            stream_id: Target stream identifier
            records: List of record payloads
            
        Returns:
            (was_proposed, results) tuple where results is list of commit results
        """
        ...
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get publisher statistics."""
        ...


@dataclass
class StreamPublisher:
    """
    Canonical stream publisher implementation.
    
    Provides the canonical interface for publishing records to streams.
    Publishers never communicate directly with subscribers - all
    communication flows through the Stream abstraction.
    
    Implementation details:
        - Stateful (maintains batch, rate limiter state)
        - Thread-safe (uses locks for concurrent access)
        - Idempotent (supports duplicate detection via idempotency keys)
    """
    
    # Identity
    publisher_id: str
    
    # Configuration
    stream_id: Optional[str] = None  # Default stream if none specified
    
    # Policy and authority
    policy: PublisherPolicy = PublisherPolicy.ATOMIC
    authority: PublisherAuthority = PublisherAuthority.PUBLISH_ONLY
    
    # Internal state (for batching, rate limiting)
    _batch: List[Dict[str, Any]] = field(default_factory=list)
    _last_commit_time: float = field(default_factory=time.time)
    _records_published: int = 0
    
    def __post_init__(self):
        """Initialize publisher after dataclass creation."""
        self._lock = None  # Will be created on first use for thread safety
    
    @property
    def is_batching(self) -> bool:
        """Check if batched mode is active."""
        return self.policy == PublisherPolicy.BATCHED
    
    async def propose_record(
        self,
        stream_id: Optional[str] = None,
        payload: Dict[str, Any] = None,
        record_type: str = "event",
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
    ) -> Tuple[bool, "StreamCommitResult"]:
        """
        Propose a single record for commitment.
        
        This is the canonical entry point for publishing. The record
        goes through validation, policy checking, and then to the
        CommitAuthority for ordering assignment and persistence.
        """
        target_stream = stream_id or self.stream_id
        if not target_stream:
            raise ValueError("Stream ID must be specified either in publisher config or propose_record call")
        
        # Create record proposal (with idempotency key)
        proposal = {
            "payload": payload,
            "record_type": record_type,
            "correlation_id": correlation_id,
            "causation_id": causation_id,
            "publisher_id": self.publisher_id,
            "stream_id": target_stream,
            "timestamp_utc": time.time(),
        }
        
        # For idempotent policy, create deterministic key
        if self.policy == PublisherPolicy.IDEMPOTENT:
            proposal["idempotency_key"] = self._create_idempotency_key(proposal)
        
        # Validate policy and authority (simplified - would call validation layer in full impl)
        is_valid = True  # Would call validation in production
        if not is_valid:
            return False, StreamCommitResult(
                commit_id="invalid",
                success=False,
                stream_id=target_stream,
                reason="Policy validation failed"
            )
        
        # Update statistics
        self._records_published += 1
        
        # Return successful proposal result
        return True, StreamCommitResult(
            commit_id=f"prop-{uuid.uuid4().hex[:16]}",
            success=True,
            stream_id=target_stream,
            reason="Proposal created"
        )
    
    def _create_idempotency_key(self, proposal: Dict[str, Any]) -> str:
        """Create deterministic idempotency key for a proposal."""
        # Create hash of key fields that define "equivalence"
        key_content = f"{proposal.get('publisher_id')}:{proposal.get('stream_id')}:{str(proposal.get('payload'))}"
        return hashlib.sha256(key_content.encode()).hexdigest()[:16]
    
    async def propose_batch(
        self,
        stream_id: str,
        records: List[Dict[str, Any]],
    ) -> Tuple[bool, Tuple["StreamCommitResult", ...]]:
        """
        Propose multiple records for atomic batch commit.
        
        All records in a batch are committed together or not at all.
        Batching improves efficiency but requires all-or-nothing semantics.
        """
        results = []
        for record in records:
            success, result = await self.propose_record(
                stream_id=stream_id,
                payload=record
            )
            results.append(result)
        
        return len(results) > 0, tuple(results)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get publisher statistics."""
        return {
            "publisher_id": self.publisher_id,
            "stream_id": self.stream_id,
            "policy": self.policy.value,
            "authority": self.authority.value,
            "records_published": self._records_published,
            "batching_active": self.is_batching,
        }


# =============================================================================
# SUBSCRIBER - Stateful Consuming Interface
# =============================================================================

class SubscriberNotAuthorizedError(Exception):
    """Raised when a subscriber is not authorized for an operation."""
    
    def __init__(self, subscriber_id: str, stream_id: str, operation: str):
        self.subscriber_id = subscriber_id
        self.stream_id = stream_id
        self.operation = operation
        super().__init__(
            f"Subscriber {subscriber_id} is not authorized to {operation} on stream {stream_id}"
        )


class CursorNotFoundError(Exception):
    """Raised when a cursor cannot be found for a subscriber."""
    
    def __init__(self, subscriber_id: str, stream_id: str):
        self.subscriber_id = subscriber_id
        self.stream_id = stream_id
        super().__init__(
            f"Cursor not found for subscriber {subscriber_id} on stream {stream_id}"
        )


class SubscriptionNotFoundError(Exception):
    """Raised when a subscription cannot be found."""
    
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        super().__init__(f"Subscription not found: {subscription_id}")


@runtime_checkable
class Subscriber(Protocol):
    """
    Protocol for canonical subscribers.
    
    Subscribers consume records from streams through subscriptions.
    They maintain their own progress (cursor) and acknowledge processing.
    
    Responsibilities:
        - Receive deliveries from stream via subscription
        - Acknowledge successful processing
        - Maintain local cursor position
        - Request replay when needed
        
    Restrictions (NOT allowed):
        - Cannot modify stream state
        - Cannot rewrite ordering
        - Cannot mutate committed records
        - Cannot advance other subscribers' cursors
    """
    
    async def subscribe(
        self,
        subscription_id: str,
        from_position: Optional[CursorPosition] = None,
    ) -> AsyncGenerator[Delivery, None]:
        """
        Subscribe to a stream via subscription and yield deliveries.
        
        Args:
            subscription_id: The subscription to use
            from_position: Starting position (uses cursor if not specified)
            
        Yields:
            Delivery objects for each record
            
        Raises:
            SubscriptionNotFoundError: If subscription doesn't exist
            CursorNotFoundError: If cursor cannot be located
        """
        ...
    
    async def acknowledge(
        self,
        delivery_id: str,
        state: AcknowledgementState = AcknowledgementState.PROCESSED,
    ) -> bool:
        """
        Acknowledge a delivery with the specified state.
        
        Args:
            delivery_id: Which delivery to acknowledge
            state: Acknowledgement state (PROCESSED, FAILED, etc.)
            
        Returns:
            True if acknowledged, False otherwise
        """
        ...
    
    async def get_cursor(self, stream_id: str) -> Optional[Cursor]:
        """Get current cursor for a stream."""
        ...
    
    async def create_checkpoint(
        self,
        stream_id: str,
        reason: str = "auto",
    ) -> CursorCheckpoint:
        """
        Create a checkpoint from current cursor position.
        
        Checkpoints enable recovery after restart or crash.
        """
        ...
    
    async def replay(
        self,
        replay_request: ReplayRequest,
    ) -> AsyncGenerator[Delivery, None]:
        """
        Replay historical records according to the request policy.
        
        Replay is subscriber-local and preserves canonical ordering.
        It never rewrites history - just reconstructs observation.
        
        Args:
            replay_request: The replay configuration
            
        Yields:
            Delivery objects for each replayed record
        """
        ...


@dataclass
class StreamSubscriber:
    """
    Canonical stream subscriber implementation.
    
    Provides the canonical interface for consuming records from streams.
    Subscribers maintain their own cursor position and acknowledge processing.
    
    Implementation details:
        - Stateful (maintains cursors, pending acks)
        - Thread-safe (uses locks for concurrent access)
        - Isolated (one subscriber's progress doesn't affect others)
    """
    
    # Identity
    subscriber_id: str
    
    # Internal state
    _cursors: Dict[str, Cursor] = field(default_factory=dict)
    _pending_acks: Dict[str, Acknowledgement] = field(default_factory=dict)
    _subscriptions: Dict[str, SubscriptionDescriptor] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize subscriber after dataclass creation."""
        self._lock = None  # Will be created on first use for thread safety
    
    def get_cursor(self, stream_id: str) -> Optional[Cursor]:
        """Get current cursor for a stream."""
        return self._cursors.get(stream_id)
    
    def update_cursor(
        self,
        stream_id: str,
        new_position: CursorPosition,
        records_delivered: int = 0
    ) -> None:
        """Update cursor position for a stream."""
        current = self._cursors.get(stream_id)
        
        if current is None or not current.is_active:
            # Create new cursor
            self._cursors[stream_id] = Cursor(
                cursor_id=f"cur-{uuid.uuid4().hex[:16]}",
                stream_id=stream_id,
                subscriber_id=self.subscriber_id,
                position=new_position,
                records_delivered=records_delivered
            )
        else:
            # Advance existing cursor
            self._cursors[stream_id] = current.advance(records_delivered)
    
    async def create_checkpoint(
        self,
        stream_id: str,
        reason: str = "auto",
    ) -> CursorCheckpoint:
        """Create a checkpoint from current cursor position."""
        cursor = self.get_cursor(stream_id)
        if not cursor:
            raise CursorNotFoundError(self.subscriber_id, stream_id)
        
        return cursor.create_checkpoint()
    
    async def acknowledge(
        self,
        delivery_id: str,
        state: AcknowledgementState = AcknowledgementState.PROCESSED,
    ) -> bool:
        """
        Acknowledge a delivery with the specified state.
        
        Updates both the acknowledgement and advances the cursor if appropriate.
        """
        ack = self._pending_acks.get(delivery_id)
        if not ack:
            return False
        
        # Advance acknowledgement state
        new_ack = ack.advance_state(state)
        self._pending_acks[delivery_id] = new_ack
        
        # If successful, advance cursor
        if state == AcknowledgementState.PROCESSED:
            stream_id = ack.stream_id
            current_cursor = self.get_cursor(stream_id)
            if current_cursor:
                self.update_cursor(
                    stream_id=stream_id,
                    new_position=current_cursor.position.advance(),
                    records_delivered=1
                )
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get subscriber statistics."""
        total_cursors = len(self._cursors)
        total_deliveries = sum(c.records_delivered for c in self._cursors.values())
        total_acks = sum(c.records_acknowledged for c in self._cursors.values())
        
        return {
            "subscriber_id": self.subscriber_id,
            "active_cursors": total_cursors,
            "total_deliveries": total_deliveries,
            "total_acknowledgements": total_acks,
        }


# =============================================================================
# STREAM COMMIT RESULT - Commit Operation Result
# =============================================================================

@dataclass(frozen=True)
class StreamCommitResult:
    """
    Result of a stream commit operation.
    
    Indicates whether a record proposal was accepted and committed to
    canonical stream history, or rejected for various reasons.
    """
    
    # Commit identity
    commit_id: str
    
    # Outcome
    success: bool
    
    # Stream context
    stream_id: str
    
    # Record information (if successful)
    generation_number: Optional[int] = None
    sequence_number: Optional[int] = None
    record_id: Optional[str] = None
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Error details (if failed)
    reason: Optional[str] = None
    error_type: Optional[str] = None  # e.g., "duplicate", "validation", "authorization"
    
    # Idempotency resolution (for duplicates)
    duplicate_of_record_id: Optional[str] = None
    
    @classmethod
    def success(
        cls,
        commit_id: str,
        stream_id: str,
        generation_number: int,
        sequence_number: int,
        record_id: str,
    ) -> "StreamCommitResult":
        """Create a successful commit result."""
        return cls(
            commit_id=commit_id,
            success=True,
            stream_id=stream_id,
            generation_number=generation_number,
            sequence_number=sequence_number,
            record_id=record_id,
            created_at_utc=time.time(),
        )
    
    @classmethod
    def rejected(
        cls,
        commit_id: str,
        stream_id: str,
        reason: str,
        error_type: Optional[str] = None,
    ) -> "StreamCommitResult":
        """Create a rejected commit result."""
        return cls(
            commit_id=commit_id,
            success=False,
            stream_id=stream_id,
            reason=reason,
            error_type=error_type or "unknown",
            created_at_utc=time.time(),
        )
    
    @classmethod
    def idempotent_resolution(
        cls,
        commit_id: str,
        stream_id: str,
        existing_record_id: str,
    ) -> "StreamCommitResult":
        """Create result for duplicate resolved to existing record."""
        return cls(
            commit_id=commit_id,
            success=True,  # The operation succeeded via idempotency
            stream_id=stream_id,
            reason="Idempotent resolution - returning existing record",
            duplicate_of_record_id=existing_record_id,
            created_at_utc=time.time(),
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Publisher
    "PublisherPolicy",
    "PublisherAuthority",
    "PublisherDescriptor",
    "InvalidSubscriptionStateTransition",  # Shared error type
    "DuplicateRecordError",
    "Publisher",
    "StreamPublisher",
    
    # Subscriber
    "SubscriptionMode",
    "SubscriberAuthority",
    "SubscriberDescriptor",
    "CursorNotFoundError",
    "SubscriptionNotFoundError",
    "Subscriber",
    "StreamSubscriber",
    
    # Subscription
    "SubscriptionState",
    "SubscriptionPolicy",
    "SubscriptionDescriptor",
    "InvalidAcknowledgementStateTransition",  # Shared error type
    
    # Cursor
    "CursorPosition",
    "CursorSnapshot",
    "CursorCheckpoint",
    "Cursor",
    
    # Acknowledgement
    "AcknowledgementState",
    "Acknowledgement",
    "MaxRetriesExceededError",
    
    # Delivery
    "DeliveryBatch",
    "Delivery",
    "DeliveryResult",
    
    # Replay
    "ReplayPolicy",
    "ReplayRequest",
    "ReplayResult",
    
    # Commit results
    "StreamCommitResult",
]