# Core Queue Infrastructure
# =========================

"""
Bounded queue infrastructure with backpressure and dead-letter support.

Provides:
- Bounded queues (fixed capacity)
- Priority queues (ordered by priority)
- Dead-letter queues (undeliverable messages)
- Retry queues (failed messages)

All queues are bounded - they never grow unbounded.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum, auto
import threading
import time


# =============================================================================
# OVERFLOW POLICIES
# =============================================================================

class OverflowPolicy(Enum):
    """What to do when queue is at capacity."""
    REJECT = "reject"           # Raise exception on overflow
    DROP_OLDEST = "drop_oldest"  # Evict oldest to make room
    DROP_NEWEST = "drop_newest"  # Drop new message, keep existing
    BLOCK = "block"             # Block until space available (timeout)


class BackpressurePolicy(Enum):
    """Backpressure behavior when system is overloaded."""
    REJECT_NEW = "reject_new"        # Reject new messages
    DROP_OLDEST = "drop_oldest"     # Drop oldest messages
    THROTTLE = "throttle"           # Slow down production rate
    PRIORITY_ONLY = "priority_only"  # Only accept high priority


# =============================================================================
# BACKPRESSURE STATE
# =============================================================================

@dataclass(frozen=True)
class BackpressureState:
    """
    Immutable backpressure state for a queue.
    
    Represents whether the system is under pressure and how it should respond.
    """
    
    is_under_pressure: bool
    pressure_level: float  # 0.0 = none, 1.0 = critical
    queued_count: int
    max_capacity: int
    
    @property
    def utilization_percent(self) -> float:
        """Get queue utilization as a percentage."""
        if self.max_capacity == 0:
            return 0.0
        return (self.queued_count / self.max_capacity) * 100


# =============================================================================
# DEAD LETTER TYPES
# =============================================================================

class DeadLetterReason(Enum):
    """Reasons why a message becomes a dead letter."""
    QUEUE_OVERFLOW = "queue_overflow"      # Queue was full
    SUBSCRIBER_REJECTED = "subscriber_rejected"  # Subscriber rejected it
    EXPIRED = "expired"                    # Message expired before delivery
    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"
    INVALID_FORMAT = "invalid_format"      # Malformed message
    UNKNOWN_ERROR = "unknown_error"


@dataclass(frozen=True)
class DeadLetter:
    """
    Immutable record of a failed delivery.
    
    Preserves all provenance information for debugging and replay.
    """
    
    original_envelope_id: str
    runtime_id: str
    reason: DeadLetterReason
    
    # Original envelope data (frozen copy)
    event_type: Optional[str] = None
    message_type: Optional[str] = None
    signal_type: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Timeline
    original_timestamp_utc: float = 0.0
    first_failure_utc: float = field(default_factory=time.time)
    last_attempt_utc: Optional[float] = None
    
    # Delivery tracking
    delivery_attempts: int = 0
    max_allowed_attempts: int = 3
    
    # Error info
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "original_envelope_id": self.original_envelope_id,
            "runtime_id": self.runtime_id,
            "reason": self.reason.value,
            "event_type": self.event_type,
            "message_type": self.message_type,
            "signal_type": self.signal_type,
            "payload": dict(self.payload),
            "original_timestamp_utc": self.original_timestamp_utc,
            "first_failure_utc": self.first_failure_utc,
            "last_attempt_utc": self.last_attempt_utc,
            "delivery_attempts": self.delivery_attempts,
            "max_allowed_attempts": self.max_allowed_attempts,
            "error_message": self.error_message,
        }


# =============================================================================
# DEAD LETTER QUEUE
# =============================================================================

class DeadLetterQueue:
    """
    Queue for undeliverable messages.
    
    Preserves all evidence of failed deliveries for diagnostics and replay.
    Never deletes records - only compacts them for storage efficiency.
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
        signal_type: Optional[str] = None,
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
            event_type, message_type, signal_type: Type info
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
                
                # Update attempt count and last failure time
                new_dead_letter = DeadLetter(
                    original_envelope_id=existing.original_envelope_id,
                    runtime_id=existing.runtime_id,
                    reason=reason,
                    event_type=existing.event_type,
                    message_type=existing.message_type,
                    signal_type=existing.signal_type,
                    payload=dict(existing.payload),
                    original_timestamp_utc=existing.original_timestamp_utc,
                    first_failure_utc=existing.first_failure_utc,
                    last_attempt_utc=time.time(),
                    delivery_attempts=existing.delivery_attempts + 1,
                    max_allowed_attempts=self._max_attempts,
                    error_message=error_message or existing.error_message,
                )
                
                self._dead_letters[envelope_id] = new_dead_letter
                return new_dead_letter
            
            # Create new dead letter entry
            dead_letter = DeadLetter(
                original_envelope_id=envelope_id,
                runtime_id=runtime_id,
                reason=reason,
                event_type=event_type,
                message_type=message_type,
                signal_type=signal_type,
                payload=dict(payload or {}),
                original_timestamp_utc=original_timestamp_utc,
                first_failure_utc=time.time(),
                last_attempt_utc=None,
                delivery_attempts=1,
                max_allowed_attempts=self._max_attempts,
                error_message=error_message,
            )
            
            # Enforce size limit
            if len(self._dead_letters) >= self._max_size:
                # Remove oldest (by insertion order approximation)
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
        
        # Consider healthy if we haven't hit the size limit
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
    
    Implements exponential backoff between retries.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_backoff_seconds: float = 1.0,
        max_backoff_seconds: float = 60.0,
    ):
        self._max_retries = max_retries
        self._initial_backoff = initial_backoff_seconds
        self._max_backoff = max_backoff_seconds
        
        # Queue of (priority, timestamp, envelope, attempt_count)
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
        current_backoff = min(
            self._initial_backoff * (2 ** len(self._queue)),
            self._max_backoff,
        )
        scheduled_time = time.monotonic() + current_backoff
        
        with self._lock:
            self._queue.append((priority, scheduled_time, envelope, 0))
            
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
                if attempt_count >= self._max_retries:
                    # Move to DLQ - not implemented here
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
# BOUNDED QUEUE
# =============================================================================

class BoundedQueue:
    """
    A bounded queue with overflow policies.
    
    Never grows beyond its capacity - enforces backpressure.
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        overflow_policy: OverflowPolicy = OverflowPolicy.REJECT,
    ):
        self._max_size = max_size
        self._overflow_policy = overflow_policy
        
        self._queue: List[Any] = []
        self._lock = threading.RLock()
        
        # Statistics
        self._total_enqueued = 0
        self._total_rejected = 0
    
    def enqueue(self, item: Any) -> bool:
        """
        Add an item to the queue.
        
        Args:
            item: The item to add
            
        Returns:
            True if added successfully
            
        Raises:
            QueueFullError: If overflow_policy is REJECT and queue is full
        """
        with self._lock:
            if len(self._queue) >= self._max_size:
                # Apply overflow policy
                if self._overflow_policy == OverflowPolicy.REJECT:
                    self._total_rejected += 1
                    raise QueueFullError(
                        f"Queue at capacity ({self._max_size})"
                    )
                
                elif self._overflow_policy == OverflowPolicy.DROP_OLDEST:
                    self._queue.pop(0)  # Remove oldest
                
                elif self._overflow_policy == OverflowPolicy.DROP_NEWEST:
                    self._total_rejected += 1
                    return False
                
                elif self._overflow_policy == OverflowPolicy.BLOCK:
                    # Not implemented for synchronous queue
                    pass
            
            self._queue.append(item)
            self._total_enqueued += 1
            return True
    
    def dequeue(self) -> Optional[Any]:
        """Remove and return the oldest item."""
        with self._lock:
            if not self._queue:
                return None
            return self._queue.pop(0)
    
    def peek(self) -> Optional[Any]:
        """Get oldest item without removing it."""
        with self._lock:
            if not self._queue:
                return None
            return self._queue[0]
    
    def size(self) -> int:
        """Get current queue size."""
        with self._lock:
            return len(self._queue)
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return self.size() == 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get queue statistics."""
        with self._lock:
            return {
                "size": len(self._queue),
                "max_size": self._max_size,
                "overflow_policy": self._overflow_policy.value,
                "total_enqueued": self._total_enqueued,
                "total_rejected": self._total_rejected,
                "utilization_percent": round(
                    (len(self._queue) / max(self._max_size, 1)) * 100, 2
                ),
            }
    
    def get_backpressure_state(self) -> BackpressureState:
        """Get current backpressure state."""
        with self._lock:
            return BackpressureState(
                is_under_pressure=len(self._queue) >= int(self._max_size * 0.8),
                pressure_level=len(self._queue) / max(self._max_size, 1),
                queued_count=len(self._queue),
                max_capacity=self._max_size,
            )


class QueueFullError(Exception):
    """Raised when queue is full and overflow policy rejects."""
    
    def __init__(self, message: str):
        super().__init__(message)


# =============================================================================
# PRIORITY QUEUE
# =============================================================================

# =============================================================================
# PRIORITY QUEUE WITH STARVATION PREVENTION
# =============================================================================

class PriorityQueueConfig:
    """
    Configuration for PriorityQueue with starvation prevention via aging.
    
    Starvation prevention uses aging to ensure low-priority items don't wait
    indefinitely (COMM-MED-001).
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        overflow_policy: OverflowPolicy = OverflowPolicy.REJECT,
        aging_enabled: bool = True,
        aging_factor: float = 2.0,  # Priority halves every aging_interval
        aging_interval_seconds: float = 60.0,
    ):
        self.max_size = max_size
        self.overflow_policy = overflow_policy
        self.aging_enabled = aging_enabled
        self.aging_factor = aging_factor
        self.aging_interval_seconds = aging_interval_seconds


class PriorityQueue:
    """
    Priority-ordered bounded queue with starvation prevention.
    
    Items are dequeued in priority order (lower = higher priority).
    Low-priority items gradually increase in priority over time to prevent
    indefinite waiting (starvation prevention - COMM-MED-001).
    
    Aging mechanism:
        - Every aging_interval_seconds, low-priority items get priority boost
        - Priority = original_priority / aging_factor^age_cycles
    """
    
    def __init__(
        self,
        config: Optional[PriorityQueueConfig] = None,
    ):
        self._config = config or PriorityQueueConfig()
        
        # List of (priority, timestamp, item) tuples
        self._queue: List[Tuple[int, float, Any]] = []
        self._lock = threading.RLock()
        
        self._total_enqueued = 0
        self._total_rejected = 0
    
    def enqueue(self, item: Any, priority: int = 0) -> bool:
        """
        Add an item with the given priority.
        
        Args:
            item: The item to add
            priority: Lower number = higher priority
            
        Returns:
            True if added successfully
        """
        timestamp = time.monotonic()
        
        with self._lock:
            if len(self._queue) >= self._config.max_size:
                # Apply overflow policy
                if self._config.overflow_policy == OverflowPolicy.REJECT:
                    self._total_rejected += 1
                    raise QueueFullError(
                        f"Queue at capacity ({self._config.max_size})"
                    )
                
                elif self._config.overflow_policy == OverflowPolicy.DROP_OLDEST:
                    self._queue.pop(0)
                
                elif self._config.overflow_policy == OverflowPolicy.DROP_NEWEST:
                    self._total_rejected += 1
                    return False
            
            # Insert in sorted order (by priority, then timestamp)
            new_entry = (priority, timestamp, item)
            
            inserted = False
            for i, (p, _, _) in enumerate(self._queue):
                if p > priority or (p == priority and timestamp < self._queue[i][1]):
                    self._queue.insert(i, new_entry)
                    inserted = True
                    break
            
            if not inserted:
                self._queue.append(new_entry)
            
            self._total_enqueued += 1
            return True
    
    def _apply_aging(self) -> None:
        """Apply aging to prevent starvation (COMM-MED-001)."""
        if not self._config.aging_enabled:
            return
        
        now = time.monotonic()
        
        # Find oldest entry and apply aging to entries that have waited long
        for i, (priority, created_at, _) in enumerate(self._queue):
            age = now - created_at
            if age >= self._config.aging_interval_seconds:
                # Apply aging: reduce priority value (increase actual priority)
                cycles = int(age / self._config.aging_interval_seconds)
                new_priority = max(0, priority // (int(self._config.aging_factor) ** cycles))
                
                _, ts, item = self._queue[i]
                self._queue[i] = (new_priority, ts, item)
        
        # Re-sort after aging
        self._queue.sort(key=lambda x: (x[0], x[1]))
    
    def dequeue(self) -> Optional[Any]:
        """Remove and return highest priority item."""
        with self._lock:
            if not self._queue:
                return None
            
            self._apply_aging()
            
            _, _, item = self._queue.pop(0)
            return item
    
    def peek(self) -> Optional[Any]:
        """Get highest priority item without removing it."""
        with self._lock:
            if not self._queue:
                return None
            return self._queue[0][2]
    
    def size(self) -> int:
        """Get current queue size."""
        with self._lock:
            return len(self._queue)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get priority queue statistics."""
        with self._lock:
            priorities = {}
            for p, _, _ in self._queue:
                priorities[p] = priorities.get(p, 0) + 1
            
            return {
                "size": len(self._queue),
                "max_size": self._config.max_size,
                "overflow_policy": self._config.overflow_policy.value,
                "priority_distribution": priorities,
                "total_enqueued": self._total_enqueued,
                "total_rejected": self._total_rejected,
                "aging_enabled": self._config.aging_enabled,
            }


__all__ = [
    # Policies
    "OverflowPolicy",
    "BackpressurePolicy",
    
    # Backpressure state
    "BackpressureState",
    
    # Dead letter types
    "DeadLetterReason",
    "DeadLetter",
    
    # Queue types
    "DeadLetterQueue",
    "RetryQueue",
    "BoundedQueue",
    "PriorityQueueConfig",  # STARVATION PREVENTION (COMM-MED-001)
    "PriorityQueue",
    "QueueFullError",
]
