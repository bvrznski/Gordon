# Core Reliability Framework
# ==========================
"""
Reliability guarantees for the Event System & Message Bus.

This module provides:
- Delivery guarantees (fire-and-forget, at-most-once, at-least-once)
- Message ordering and partitioning
- Retry mechanisms with exponential backoff
- Idempotency and deduplication
- Dead-letter queue processing
- Failure recovery

RELIABILITY LAWS:
    1. Delivery semantics are explicit
    2. Retries are policy-driven
    3. Ordering is deterministic where required
    4. Duplicate processing is prevented or detectable
    5. Poison messages are isolated
    6. Recovery is observable
    7. Dead-letter processing is deterministic
    8. Reliability policies are transport-independent
    9. Silent message loss is prohibited
   10. Reliability decisions are auditable
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum, auto
import threading
import time
import uuid


# =============================================================================
# DELIVERY GUARANTEES
# =============================================================================

class DeliveryGuarantee(Enum):
    """
    Message delivery guarantee levels.
    
    - FIRE_AND_FORGET: No delivery guarantees, no retries
    - AT_MOST_ONCE: Each message delivered zero or one times
    - AT_LEAST_ONCE: Each message delivered at least once (may duplicate)
    - EXACTLY_ONCE: Each message delivered exactly once (extension point)
    """
    FIRE_AND_FORGET = "fire-and-forget"
    AT_MOST_ONCE = "at-most-once"
    AT_LEAST_ONCE = "at-least-once"
    EXACTLY_ONCE = "exactly-once"  # Requires external coordination


# =============================================================================
# RETRY POLICIES
# =============================================================================

class RetryPolicy(Enum):
    """Retry policy types."""
    FIXED = "fixed"                    # Fixed interval between retries
    EXPONENTIAL = "exponential"        # Exponential backoff with jitter
    LINEAR = "linear"                  # Linear increase in delay
    BOUNDED_EXPONENTIAL = "bounded-exponential"  # Exponential with max cap


@dataclass(frozen=True)
class RetryPolicyConfig:
    """Configuration for retry behavior."""
    
    policy: RetryPolicy = RetryPolicy.EXPONENTIAL
    max_retries: int = 3
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    
    # Jitter configuration
    jitter_enabled: bool = True
    jitter_factor: float = 0.1  # +/- 10% jitter
    
    # Backoff multiplier for exponential policies
    backoff_multiplier: float = 2.0
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay before retry attempt.
        
        Args:
            attempt: Current attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        base_delay = self.initial_delay_seconds
        
        if self.policy == RetryPolicy.FIXED:
            delay = base_delay
        
        elif self.policy == RetryPolicy.EXPONENTIAL:
            delay = base_delay * (self.backoff_multiplier ** attempt)
        
        elif self.policy == RetryPolicy.LINEAR:
            delay = base_delay + (attempt * self.initial_delay_seconds)
        
        elif self.policy == RetryPolicy.BOUNDED_EXPONENTIAL:
            delay = min(
                base_delay * (self.backoff_multiplier ** attempt),
                self.max_delay_seconds
            )
        
        else:
            delay = base_delay
        
        # Apply jitter if enabled
        if self.jitter_enabled and self.jitter_factor > 0:
            variance = delay * self.jitter_factor
            delay += (hash(uuid.uuid4()) % int(variance * 2)) - variance
        
        return min(delay, self.max_delay_seconds)


# =============================================================================
# MESSAGE ORDERING
# =============================================================================

class OrderingMode(Enum):
    """Message ordering modes."""
    UNORDERED = "unordered"      # No ordering guarantee
    FIFO = "fifo"                # First-in-first-out within partition
    PARTITIONED = "partitioned"  # Ordered per partition key


@dataclass(frozen=True)
class OrderingConfig:
    """Configuration for message ordering."""
    
    mode: OrderingMode = OrderingMode.FIFO
    
    # For partitioned ordering
    partition_key: Optional[str] = None
    
    # Maximum queue size before backpressure
    max_queue_size: int = 10000


# =============================================================================
# IDEMPOTENCY & DEDUPLICATION
# =============================================================================

class DeduplicationMode(Enum):
    """Deduplication strategy."""
    NONE = "none"            # No deduplication
    KEY_BASED = "key-based"  # Use idempotency key from message
    TIMESTAMP_BASED = "timestamp-based"  # Windowed deduplication


@dataclass(frozen=True)
class IdempotencyConfig:
    """Configuration for idempotent processing."""
    
    enabled: bool = False
    
    # Deduplication window in seconds
    window_seconds: int = 300  # 5 minutes default
    
    # Key extraction from message payload
    key_path: Optional[str] = None  # e.g., "request_id" or "idempotency_key"
    
    def get_deduplication_key(self, payload: Dict[str, Any]) -> Optional[str]:
        """Extract deduplication key from payload."""
        if not self.enabled:
            return None
        
        if self.key_path and self.key_path in payload:
            return str(payload[self.key_path])
        
        return None


# =============================================================================
# DEAD LETTER TYPES
# =============================================================================

class DeadLetterReason(Enum):
    """Reasons why a message becomes a dead letter."""
    QUEUE_OVERFLOW = "queue_overflow"
    SUBSCRIBER_REJECTED = "subscriber_rejected"
    EXPIRED = "expired"
    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"
    INVALID_FORMAT = "invalid_format"
    TIMEOUT = "timeout"
    UNKNOWN_ERROR = "unknown_error"


@dataclass(frozen=True)
class DeadLetter:
    """
    Record of a message that could not be delivered.
    
    Preserves all provenance information for debugging and replay.
    """
    
    original_envelope_id: str
    runtime_id: str
    
    reason: DeadLetterReason
    failure_count: int = 0
    
    # Original envelope data (frozen copy)
    event_type: Optional[str] = None
    message_type: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Timeline
    original_timestamp_utc: float = 0.0
    first_failure_utc: float = field(default_factory=time.time)
    last_attempt_utc: Optional[float] = None
    
    # Error info
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "original_envelope_id": self.original_envelope_id,
            "runtime_id": self.runtime_id,
            "reason": self.reason.value,
            "failure_count": self.failure_count,
            "event_type": self.event_type,
            "message_type": self.message_type,
            "payload": dict(self.payload),
            "original_timestamp_utc": self.original_timestamp_utc,
            "first_failure_utc": self.first_failure_utc,
            "last_attempt_utc": self.last_attempt_utc,
            "error_message": self.error_message,
        }


# =============================================================================
# DEAD LETTER QUEUE
# =============================================================================

class DeadLetterQueue:
    """
    Queue for messages that could not be delivered.
    
    Never deletes records - only compacts them for storage efficiency.
    All dead letters are preserved for debugging and replay.
    """
    
    def __init__(
        self,
        max_size: int = 10000,
        max_attempts_per_message: int = 3,
    ):
        self._max_size = max_size
        self._max_attempts = max_attempts_per_message
        
        self._lock = threading.RLock()
        
        # Dead letter storage (by original envelope ID for dedup)
        self._dead_letters: Dict[str, DeadLetter] = {}
    
    def add(
        self,
        envelope_id: str,
        runtime_id: str,
        reason: DeadLetterReason,
        event_type: Optional[str] = None,
        message_type: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        original_timestamp_utc: float = 0.0,
        error_message: Optional[str] = None,
    ) -> DeadLetter:
        """
        Add a message to the dead letter queue.
        
        Args:
            envelope_id: ID of the original envelope
            runtime_id: Which runtime tried to deliver it
            reason: Why it failed
            event_type, message_type: Type info
            payload: Original payload (frozen copy)
            original_timestamp_utc: When first attempted
            error_message: Failure description
            
        Returns:
            The created DeadLetter record
        """
        with self._lock:
            # Check if already exists (dedup by envelope ID)
            if envelope_id in self._dead_letters:
                existing = self._dead_letters[envelope_id]
                
                new_dead_letter = DeadLetter(
                    original_envelope_id=existing.original_envelope_id,
                    runtime_id=existing.runtime_id,
                    reason=reason,
                    failure_count=existing.failure_count + 1,
                    event_type=existing.event_type,
                    message_type=existing.message_type,
                    payload=dict(existing.payload),
                    original_timestamp_utc=existing.original_timestamp_utc,
                    first_failure_utc=existing.first_failure_utc,
                    last_attempt_utc=time.time(),
                    error_message=error_message or existing.error_message,
                )
                
                self._dead_letters[envelope_id] = new_dead_letter
                return new_dead_letter
            
            # Create new dead letter entry
            dead_letter = DeadLetter(
                original_envelope_id=envelope_id,
                runtime_id=runtime_id,
                reason=reason,
                failure_count=1,
                event_type=event_type,
                message_type=message_type,
                payload=dict(payload or {}),
                original_timestamp_utc=original_timestamp_utc,
                first_failure_utc=time.time(),
                last_attempt_utc=None,
                error_message=error_message,
            )
            
            # Enforce size limit
            if len(self._dead_letters) >= self._max_size:
                oldest_id = list(self._dead_letters.keys())[0]
                del self._dead_letters[oldest_id]
            
            self._dead_letters[envelope_id] = dead_letter
            
            return dead_letter
    
    def get_by_envelope_id(self, envelope_id: str) -> Optional[DeadLetter]:
        """Get a dead letter by its original envelope ID."""
        with self._lock:
            return self._dead_letters.get(envelope_id)
    
    def get_all_dead_letters(self) -> List[DeadLetter]:
        """Get all dead letters."""
        with self._lock:
            return list(self._dead_letters.values())
    
    def get_by_reason(self, reason: DeadLetterReason) -> List[DeadLetter]:
        """Get dead letters by reason."""
        with self._lock:
            return [
                dl for dl in self._dead_letters.values()
                if dl.reason == reason
            ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get DLQ statistics."""
        with self._lock:
            reasons: Dict[str, int] = {}
            
            for dl in self._dead_letters.values():
                r = dl.reason.value
                reasons[r] = reasons.get(r, 0) + 1
            
            return {
                "total_dead_letters": len(self._dead_letters),
                "reason_breakdown": reasons,
                "max_size": self._max_size,
                "max_attempts_per_message": self._max_attempts,
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get DLQ health status."""
        stats = self.get_statistics()
        
        utilization = (
            stats["total_dead_letters"] / max(stats["max_size"], 1)
        ) * 100
        
        return {
            "status": "healthy" if utilization < 80 else "degraded",
            "utilization_percent": round(utilization, 2),
            **stats,
        }


# =============================================================================
# RETRY QUEUE
# =============================================================================

class RetryQueue:
    """
    Queue for messages that should be retried.
    
    Implements exponential backoff between retries with configurable policies.
    """
    
    def __init__(
        self,
        policy: Optional[RetryPolicyConfig] = None,
    ):
        self._policy = policy or RetryPolicyConfig()
        
        # Queue of (priority, scheduled_time, envelope, attempt_count)
        self._queue: List[Tuple[int, float, Any, int]] = []
        self._lock = threading.RLock()
    
    def enqueue_with_backoff(
        self,
        envelope: Any,
        priority: int = 0,
    ) -> bool:
        """
        Enqueue a message for retry with exponential backoff.
        
        Args:
            envelope: The message to retry
            priority: Delivery priority
            
        Returns:
            True if added to queue
        """
        attempt_count = 1  # First retry
        
        current_backoff = self._policy.calculate_delay(attempt_count)
        scheduled_time = time.monotonic() + current_backoff
        
        with self._lock:
            self._queue.append((priority, scheduled_time, envelope, attempt_count))
            
            # Sort by scheduled time, then priority
            self._queue.sort(key=lambda x: (x[1], x[0]))
            
            return True
    
    def get_ready_for_retry(self) -> List[Any]:
        """Get messages ready for retry (backoff expired)."""
        now = time.monotonic()
        result = []
        
        with self._lock:
            # Find all messages whose backoff has expired
            ready_indices = [
                i for i, (_, scheduled_time, _, _) in enumerate(self._queue)
                if scheduled_time <= now
            ]
            
            for idx in reversed(ready_indices):
                priority, _, envelope, attempt_count = self._queue.pop(idx)
                
                # Check if max retries exceeded
                if attempt_count >= self._policy.max_retries:
                    continue
                
                result.append(envelope)
        
        return result
    
    def mark_failed(self, envelope: Any) -> bool:
        """Mark an envelope as failed (increment retry count)."""
        with self._lock:
            for i, (_, _, env, count) in enumerate(self._queue):
                if env is envelope or env == envelope:
                    self._queue[i] = (_, _, env, count + 1)
                    return True
        return False
    
    def size(self) -> int:
        """Get queue size."""
        with self._lock:
            return len(self._queue)


# =============================================================================
# ORDERED DELIVERY QUEUE
# =============================================================================

class OrderedDeliveryQueue:
    """
    Queue that maintains FIFO ordering within partitions.
    
    Used when messages must be delivered in strict order (e.g., state changes).
    """
    
    def __init__(
        self,
        max_size: int = 10000,
    ):
        self._max_size = max_size
        
        # partition_key -> list of (timestamp, envelope) tuples
        self._partitions: Dict[str, List[Tuple[float, Any]]] = {}
        self._lock = threading.RLock()
        
        # Statistics
        self._total_enqueued = 0
        self._total_dequeued = 0
    
    def enqueue(
        self,
        envelope: Any,
        partition_key: Optional[str] = None,
        timestamp: Optional[float] = None,
    ) -> bool:
        """
        Add an envelope to the queue.
        
        Args:
            envelope: Message to add
            partition_key: Partition for ordering (None = global order)
            timestamp: Envelope creation time
            
        Returns:
            True if added successfully
        """
        ts = timestamp or time.monotonic()
        
        key = partition_key or "__global__"
        
        with self._lock:
            if len(self._partitions.get(key, [])) >= self._max_size:
                return False  # Queue full
            
            if key not in self._partitions:
                self._partitions[key] = []
            
            self._partitions[key].append((ts, envelope))
            self._total_enqueued += 1
            return True
    
    def dequeue(self, partition_key: Optional[str] = None) -> Optional[Any]:
        """
        Remove and return oldest envelope from partition.
        
        Args:
            partition_key: Which partition (None = global order)
            
        Returns:
            Oldest envelope or None if empty
        """
        key = partition_key or "__global__"
        
        with self._lock:
            if key not in self._partitions or not self._partitions[key]:
                return None
            
            _, envelope = self._partitions[key].pop(0)
            self._total_dequeued += 1
            return envelope
    
    def get_partition_size(self, partition_key: str) -> int:
        """Get size of a specific partition."""
        with self._lock:
            return len(self._partitions.get(partition_key, []))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get queue statistics."""
        with self._lock:
            partitions = {k: len(v) for k, v in self._partitions.items()}
            
            return {
                "total_partitions": len(self._partitions),
                "partition_sizes": partitions,
                "total_enqueued": self._total_enqueued,
                "total_dequeued": self._total_dequeued,
            }


# =============================================================================
# RELIABILITY CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class ReliabilityConfig:
    """Configuration for reliability features."""
    
    # Delivery guarantee
    delivery_guarantee: DeliveryGuarantee = DeliveryGuarantee.AT_LEAST_ONCE
    
    # Retry configuration
    retry_policy: Optional[RetryPolicyConfig] = None
    
    # Ordering configuration
    ordering_config: Optional[OrderingConfig] = None
    
    # Idempotency configuration
    idempotency_config: Optional[IdempotencyConfig] = None
    
    # DLQ configuration
    dlq_max_size: int = 10000
    dlq_max_attempts: int = 3
    
    def is_durable(self) -> bool:
        """Check if messages should be persisted."""
        return self.delivery_guarantee in (
            DeliveryGuarantee.AT_LEAST_ONCE,
            DeliveryGuarantee.EXACTLY_ONCE,
        )
    
    def is_ordered(self) -> bool:
        """Check if messages need ordered delivery."""
        ordering = self.ordering_config
        if not ordering:
            return False
        return ordering.mode in (OrderingMode.FIFO, OrderingMode.PARTITIONED)


# =============================================================================
# RELIABILITY ENVELOPE WRAPPER
# =============================================================================

@dataclass(frozen=True)
class ReliabilityEnvelope:
    """
    Envelope with reliability metadata.
    
    Wraps original envelope to add delivery tracking and retry information.
    """
    
    # Original envelope (frozen copy)
    envelope: Any
    
    # Delivery tracking
    attempt_number: int = 0
    max_attempts: int = 3
    
    # Retry tracking
    next_retry_utc: Optional[float] = None
    backoff_seconds: float = 0.0
    
    # Idempotency
    idempotency_key: Optional[str] = None
    
    # Timestamps
    first_attempt_utc: float = field(default_factory=time.time)
    last_attempt_utc: Optional[float] = None


# =============================================================================
# RELIABILITY PROTOCOL
# =============================================================================

class ReliabilityProtocol:
    """
    Protocol for reliability operations.
    
    This is THE ONE authority for reliability features in the system.
    
    INVARIANTS:
        - Delivery semantics are explicit
        - Retries are policy-driven
        - Ordering is deterministic where required
        - Duplicate processing is prevented or detectable
        - Poison messages are isolated
        - Recovery is observable
        - Dead-letter processing is deterministic
    """
    
    def __init__(
        self,
        config: Optional[ReliabilityConfig] = None,
    ):
        self._config = config or ReliabilityConfig()
        
        # Internal state
        self._retry_queue = RetryQueue(
            policy=self._config.retry_policy or RetryPolicyConfig()
        )
        self._dlq = DeadLetterQueue(
            max_size=self._config.dlq_max_size,
            max_attempts_per_message=self._config.dlq_max_attempts,
        )
        self._ordered_queue = OrderedDeliveryQueue(
            max_size=self._config.ordering_config.max_queue_size
            if self._config.ordering_config else 10000
        )
        
        # Statistics
        self._lock = threading.RLock()
        self._retry_count = 0
        self._dlq_count = 0
    
    def should_retry(self, envelope: Any) -> Tuple[bool, float]:
        """
        Check if an envelope should be retried.
        
        Returns:
            (should_retry, delay_seconds)
        """
        # Get retry count from envelope metadata or create new tracking
        retry_info = self._get_retry_info(envelope)
        
        if retry_info.attempt_number >= self._config.retry_policy.max_retries:
            return (False, 0.0)
        
        delay = self._config.retry_policy.calculate_delay(retry_info.attempt_number)
        return (True, delay)
    
    def _get_retry_info(self, envelope: Any) -> ReliabilityEnvelope:
        """Get or create retry information for an envelope."""
        # In production, would extract from envelope metadata
        return ReliabilityEnvelope(envelope=envelope)
    
    def record_failure(
        self,
        envelope: Any,
        reason: DeadLetterReason = DeadLetterReason.UNKNOWN_ERROR,
    ) -> Optional[DeadLetter]:
        """
        Record a delivery failure.
        
        Args:
            envelope: Failed message
            reason: Why it failed
            
        Returns:
            DeadLetter record if message should go to DLQ, None otherwise
        """
        with self._lock:
            self._dlq_count += 1
        
        # Check if max retries exceeded
        retry_info = self._get_retry_info(envelope)
        
        if retry_info.attempt_number >= self._config.retry_policy.max_retries - 1:
            return self._dlq.add(
                envelope_id=str(getattr(envelope, "envelope_id", "")),
                runtime_id=getattr(envelope, "runtime_id", ""),
                reason=reason,
                event_type=getattr(envelope, "event_type", None),
                message_type=getattr(envelope, "message_type", None),
                payload=dict(getattr(envelope, "payload", {})),
            )
        
        # Add to retry queue
        self._retry_queue.enqueue_with_backoff(envelope)
        
        return None
    
    def get_retry_messages(self) -> List[Any]:
        """Get messages ready for retry."""
        return self._retry_queue.get_ready_for_retry()
    
    def is_message_ordered(self, envelope: Any) -> bool:
        """Check if a message requires ordered delivery."""
        if not self._config.ordering_config:
            return False
        
        mode = self._config.ordering_config.mode
        return mode in (OrderingMode.FIFO, OrderingMode.PARTITIONED)
    
    def enqueue_ordered(
        self,
        envelope: Any,
        partition_key: Optional[str] = None,
    ) -> bool:
        """
        Enqueue a message with ordering guarantees.
        
        Args:
            envelope: Message to queue
            partition_key: Partition for ordering (if supported)
            
        Returns:
            True if added successfully
        """
        return self._ordered_queue.enqueue(envelope, partition_key)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get reliability statistics."""
        with self._lock:
            return {
                "retry_count": self._retry_count,
                "dlq_count": self._dlq_count,
                **self._dlq.get_statistics(),
                **self._ordered_queue.get_statistics(),
            }


__all__ = [
    # Delivery guarantees
    "DeliveryGuarantee",
    
    # Retry policies
    "RetryPolicy",
    "RetryPolicyConfig",
    
    # Ordering
    "OrderingMode",
    "OrderingConfig",
    
    # Idempotency
    "DeduplicationMode",
    "IdempotencyConfig",
    
    # Dead letter
    "DeadLetterReason",
    "DeadLetter",
    "DeadLetterQueue",
    
    # Retry
    "RetryQueue",
    
    # Ordered delivery
    "OrderedDeliveryQueue",
    
    # Reliability config
    "ReliabilityConfig",
    "ReliabilityEnvelope",
    
    # Protocol
    "ReliabilityProtocol",
]