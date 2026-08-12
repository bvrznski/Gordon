# Core Delivery Infrastructure
# ===========================

"""
Delivery modes and acknowledgements for communication.

Supports:
- Synchronous delivery (immediate, blocking)
- Asynchronous delivery (fire-and-forget)
- Queued delivery (store-and-forward)
- Immediate delivery (highest priority)
- Reliable delivery (with retries and DLQ)
- Best effort delivery (no guarantees)

Acknowledgement states track delivery progress.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto
import threading
import time


# =============================================================================
# DELIVERY MODES
# =============================================================================

class DeliveryMode(Enum):
    """
    Message delivery modes.
    
    Priority ordering (lowest to highest reliability):
        BEST_EFFORT < ASYNC < QUEUED < SYNCHRONOUS < IMMEDIATE < RELIABLE
    """
    BEST_EFFORT = "best_effort"       # No guarantees, fire-and-forget
    ASYNC = "async"                   # Asynchronous delivery (queue-based)
    QUEUED = "queued"                 # Queued for later delivery
    SYNCHRONOUS = "synchronous"       # Synchronous, blocking delivery
    IMMEDIATE = "immediate"           # Immediate delivery with no queuing
    RELIABLE = "reliable"             # Guaranteed delivery with retries


def mode_priority(mode: DeliveryMode) -> int:
    """Return numeric priority (lower = higher reliability)."""
    return {
        DeliveryMode.BEST_EFFORT: 0,
        DeliveryMode.ASYNC: 1,
        DeliveryMode.QUEUED: 2,
        DeliveryMode.SYNCHRONOUS: 3,
        DeliveryMode.IMMEDIATE: 4,
        DeliveryMode.RELIABLE: 5,
    }.get(mode, 2)


# =============================================================================
# DELIVERY STATUS
# =============================================================================

class DeliveryStatus(Enum):
    """
    Status of a delivery attempt.
    
    States progress:
        PENDING -> (ACCEPTED | REJECTED) -> (DELIVERED | FAILED)
    """
    PENDING = "pending"           # Waiting for delivery
    ACCEPTED = "accepted"         # Accepted by destination queue
    DELIVERED = "delivered"       # Successfully delivered to subscriber
    FAILED = "failed"             # Delivery failed (permanently)
    REJECTED = "rejected"         # Rejected by subscriber (policy, validation)


# =============================================================================
# DELIVERY ATTEMPT RECORD
# =============================================================================

@dataclass(frozen=True)
class DeliveryAttempt:
    """
    Immutable record of a single delivery attempt.
    
    Each retry creates a new attempt with updated state.
    """
    
    attempt_id: str
    envelope_id: str
    subscriber_id: str
    
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Status progression
    status: DeliveryStatus = DeliveryStatus.PENDING
    
    # Timing metrics (in milliseconds)
    queue_wait_ms: float = 0.0
    delivery_latency_ms: float = 0.0
    processing_latency_ms: float = 0.0
    
    # Error info (if failed)
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


# =============================================================================
# DELIVERY TRACKER
# =============================================================================

class DeliveryTracker:
    """
    Tracks delivery status for all envelopes.
    
    Provides visibility into delivery state without mutability concerns.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # envelope_id -> list of DeliveryAttempt records
        self._attempts: Dict[str, List[DeliveryAttempt]] = {}
        
        # subscriber_id -> set of envelope_ids being delivered
        self._subscriber_pending: Dict[str, set] = {}
    
    def record_attempt(
        self,
        envelope_id: str,
        subscriber_id: str,
        status: DeliveryStatus = DeliveryStatus.PENDING,
        queue_wait_ms: float = 0.0,
        delivery_latency_ms: float = 0.0,
        processing_latency_ms: float = 0.0,
    ) -> str:
        """
        Record a delivery attempt.
        
        Returns:
            The attempt ID
        """
        with self._lock:
            # Generate unique attempt ID
            attempt_id = f"attempt_{envelope_id}_{subscriber_id}_{len(self._attempts.get(envelope_id, []))}"
            
            attempt = DeliveryAttempt(
                attempt_id=attempt_id,
                envelope_id=envelope_id,
                subscriber_id=subscriber_id,
                timestamp_utc=time.time(),
                status=status,
                queue_wait_ms=queue_wait_ms,
                delivery_latency_ms=delivery_latency_ms,
                processing_latency_ms=processing_latency_ms,
                retry_count=len(self._attempts.get(envelope_id, [])),
                max_retries=3,
            )
            
            if envelope_id not in self._attempts:
                self._attempts[envelope_id] = []
            self._attempts[envelope_id].append(attempt)
            
            # Track pending for subscriber
            if status == DeliveryStatus.PENDING or status == DeliveryStatus.ACCEPTED:
                if subscriber_id not in self._subscriber_pending:
                    self._subscriber_pending[subscriber_id] = set()
                self._subscriber_pending[subscriber_id].add(envelope_id)
            
            return attempt_id
    
    def update_status(
        self,
        envelope_id: str,
        status: DeliveryStatus,
        error_message: Optional[str] = None,
    ) -> bool:
        """Update the status of a delivery attempt."""
        with self._lock:
            attempts = self._attempts.get(envelope_id)
            if not attempts:
                return False
            
            # Update last attempt
            last = attempts[-1]
            
            new_attempt = DeliveryAttempt(
                attempt_id=last.attempt_id,
                envelope_id=envelope_id,
                subscriber_id=last.subscriber_id,
                timestamp_utc=time.time(),
                status=status,
                queue_wait_ms=last.queue_wait_ms,
                delivery_latency_ms=last.delivery_latency_ms + (
                    time.monotonic() - last.timestamp_utc
                ) * 1000 if status == DeliveryStatus.DELIVERED else 0.0,
                processing_latency_ms=last.processing_latency_ms,
                retry_count=last.retry_count,
                max_retries=3,
                error_message=error_message,
            )
            
            attempts[-1] = new_attempt
            
            # Update pending tracking
            if status in (DeliveryStatus.DELIVERED, DeliveryStatus.FAILED, DeliveryStatus.REJECTED):
                for sub_id in self._subscriber_pending.keys():
                    self._subscriber_pending[sub_id].discard(envelope_id)
            
            return True
    
    def get_attempts(self, envelope_id: str) -> List[DeliveryAttempt]:
        """Get all delivery attempts for an envelope."""
        with self._lock:
            return list(self._attempts.get(envelope_id, []))
    
    def get_subscriber_pending(self, subscriber_id: str) -> set:
        """Get envelopes pending delivery to a subscriber."""
        with self._lock:
            return set(self._subscriber_pending.get(subscriber_id, set()))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get delivery tracker statistics."""
        with self._lock:
            status_counts: Dict[str, int] = {}
            
            for attempts in self._attempts.values():
                for a in attempts:
                    s = a.status.value
                    status_counts[s] = status_counts.get(s, 0) + 1
            
            return {
                "total_envelopes_tracked": len(self._attempts),
                "status_distribution": status_counts,
                "pending_deliveries": sum(len(v) for v in self._subscriber_pending.values()),
            }


# =============================================================================
# ACKNOWLEDGEMENT HANDLER
# =============================================================================

class AcknowledgementHandler:
    """
    Handles message acknowledgements with callbacks.
    
    Allows subscribers to acknowledge receipt and handle failures.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # Callbacks by envelope_id
        self._callbacks: Dict[str, Any] = {}  # Could be List[callable]
        
        # Acknowledgement timeout tracking
        self._ack_timeouts: Dict[str, float] = {}
    
    def register_callback(
        self,
        envelope_id: str,
        callback: Any,  # callable[[bool, Optional[str]], None]
    ) -> bool:
        """Register a callback for acknowledgement."""
        with self._lock:
            if envelope_id not in self._callbacks:
                self._callbacks[envelope_id] = []
            self._callbacks[envelope_id].append(callback)
            return True
    
    def remove_callback(self, envelope_id: str) -> bool:
        """Remove callbacks for an envelope."""
        with self._lock:
            if envelope_id in self._callbacks:
                del self._callbacks[envelope_id]
                return True
            return False
    
    def on_delivered(
        self,
        envelope_id: str,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> None:
        """Call registered callbacks when delivery completes."""
        with self._lock:
            callbacks = list(self._callbacks.get(envelope_id, []))
        
        for callback in callbacks:
            try:
                if callable(callback):
                    callback(success, error_message)
            except Exception:
                pass  # Don't let callback errors affect main flow
    
    def set_timeout(
        self,
        envelope_id: str,
        timeout_seconds: float,
    ) -> None:
        """Set an acknowledgement timeout for an envelope."""
        with self._lock:
            self._ack_timeouts[envelope_id] = time.time() + timeout_seconds
    
    def is_timed_out(self, envelope_id: str) -> bool:
        """Check if an envelope has exceeded its timeout."""
        with self._lock:
            if envelope_id not in self._ack_timeouts:
                return False
            return time.time() > self._ack_timeouts[envelope_id]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get acknowledgement handler statistics."""
        with self._lock:
            return {
                "tracked_envelopes": len(self._callbacks),
                "timeout_count": len(self._ack_timeouts),
            }


__all__ = [
    # Delivery modes
    "DeliveryMode",
    "mode_priority",
    
    # Status types
    "DeliveryStatus",
    
    # Attempt record
    "DeliveryAttempt",
    
    # Tracker classes
    "DeliveryTracker",
    "AcknowledgementHandler",
]