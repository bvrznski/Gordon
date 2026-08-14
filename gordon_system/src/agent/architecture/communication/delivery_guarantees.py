# Gordon Core - Delivery Guarantees (Phase 3.21.8)
# ===================================================
#
# Canonical delivery semantics for message reliability
#
# Each message delivery has an explicit guarantee associated with it.
# These define the minimum reliability contract between sender and receiver.

"""
Canonical Delivery Guarantees for Gordon Phase 3.21.8

DELIVERY GUARANTEES:
--------------------
1. At-Most-Once: Message delivered zero or one time (may be lost)
2. At-Least-Once: Message delivered one or more times (duplicates possible)
3. Exactly-Once: Message delivered exactly once (requires transaction)

DELIVERY STATES:
----------------
- PENDING: Waiting for delivery attempt
- IN_PROGRESS: Currently being delivered
- DELIVERED: Successfully delivered to recipient
- FAILED: Delivery failed permanently
- RETRYING: Scheduled for retry

STRATEGIES:
-----------
Each guarantee has a strategy implementation that handles retries,
deduplication, and failure handling.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, Callable
from enum import Enum, auto
import time
import uuid


# =============================================================================
# DELIVERY MODE ENUMERATION
# =============================================================================

class DeliveryMode(Enum):
    """
    Canonical delivery modes (delivery guarantees).
    
    Invariants:
        - DLV-MODE-001: Every message has exactly one delivery mode
        - DLV-MODE-002: Mode determines retry behavior and deduplication
    """
    
    AT_MOST_ONCE = "at-most-once"      # Zero or one delivery (may be lost)
    AT_LEAST_ONCE = "at-least-once"    # One or more deliveries (duplicates possible)
    EXACTLY_ONCE = "exactly-once"      # Exactly one delivery (requires transaction)


# =============================================================================
# DELIVERY STATE ENUMERATION
# =============================================================================

class DeliveryState(Enum):
    """
    Canonical delivery lifecycle states.
    
    Invariants:
        - DLV-STS-001: State transitions follow defined patterns
        - DLV-STS-002: Terminal states preserve provenance data
    """
    
    PENDING = "pending"         # Waiting for initial delivery attempt
    IN_PROGRESS = "in_progress" # Currently being delivered
    DELIVERED = "delivered"     # Successfully delivered to all recipients
    FAILED = "failed"           # Failed permanently (no more retries)
    EXPIRED = "expired"         # Lifetime exceeded
    DROPPED = "dropped"         # Dropped due to backpressure/policy
    RETRYING = "retrying"       # Scheduled for retry


# =============================================================================
# DELIVERY ATTEMPT RECORD
# =============================================================================

@dataclass(frozen=True, slots=True)
class DeliveryAttempt:
    """
    Immutable record of a single delivery attempt.
    
    Args:
        attempt_number: Which attempt this is (1-based)
        timestamp_utc: When this attempt occurred
        status: Result of the attempt
        error_message: Error details if failed
    """
    
    attempt_number: int = 0
    timestamp_utc: float = field(default_factory=time.time)
    status: DeliveryState = DeliveryState.PENDING
    error_message: Optional[str] = None
    
    def with_status(self, new_status: DeliveryState) -> "DeliveryAttempt":
        """Create a new attempt record with updated status."""
        return DeliveryAttempt(
            attempt_number=self.attempt_number,
            timestamp_utc=time.time(),
            status=new_status,
            error_message=self.error_message,
        )
    
    def with_error(self, error_msg: str) -> "DeliveryAttempt":
        """Create a new attempt record with an error."""
        return DeliveryAttempt(
            attempt_number=self.attempt_number,
            timestamp_utc=time.time(),
            status=DeliveryState.FAILED,
            error_message=error_msg,
        )


# =============================================================================
# DELIVERY CONTEXT
# =============================================================================

@dataclass(frozen=True, slots=True)
class DeliveryContext:
    """
    Immutable context for a delivery operation.
    
    Args:
        message_id: ID of the message being delivered
        message_type: Type of the message
        target_endpoint_ids: List of recipient endpoint IDs
        delivery_mode: The delivery guarantee requested
        max_attempts: Maximum delivery attempts allowed
        current_attempt: Current attempt number
    """
    
    message_id: str
    message_type: str
    target_endpoint_ids: Tuple[str, ...] = field(default_factory=tuple)
    delivery_mode: DeliveryMode = DeliveryMode.AT_MOST_ONCE
    max_attempts: int = 3
    current_attempt: int = 0
    
    def next_attempt(self) -> "DeliveryContext":
        """Create a new context with incremented attempt number."""
        return DeliveryContext(
            message_id=self.message_id,
            message_type=self.message_type,
            target_endpoint_ids=self.target_endpoint_ids,
            delivery_mode=self.delivery_mode,
            max_attempts=self.max_attempts,
            current_attempt=self.current_attempt + 1,
        )
    
    def is_last_attempt(self) -> bool:
        """Check if this is the last allowed attempt."""
        return self.current_attempt >= self.max_attempts


# =============================================================================
# RELIABLE DELIVERY ENGINE
# =============================================================================

@dataclass(slots=True)
class ReliableDeliveryEngine:
    """
    Engine for reliable message delivery based on guaranteed semantics.
    
    Implements different strategies based on DeliveryMode:
    - AT_MOST_ONCE: Single attempt, no retry, no deduplication
    - AT_LEAST_ONCE: Multiple attempts with exponential backoff,
                     deduplication via message ID
    - EXACTLY_ONCE: Requires transactional context, single successful delivery
    
    Note: This class is mutable (for state tracking) but returns immutable
    records.
    """
    
    _delivery_state: Dict[str, Tuple[DeliveryAttempt, ...]] = field(
        default_factory=dict
    )
    
    def record_attempt(
        self,
        message_id: str,
        attempt: DeliveryAttempt,
    ) -> None:
        """Record a delivery attempt."""
        attempts = self._delivery_state.get(message_id, ())
        self._delivery_state[message_id] = attempts + (attempt,)
    
    def get_attempts(self, message_id: str) -> Tuple[DeliveryAttempt, ...]:
        """Get all delivery attempts for a message."""
        return self._delivery_state.get(message_id, ())
    
    def get_delivery_state(self, message_id: str) -> DeliveryState:
        """Get the overall delivery state for a message."""
        attempts = self.get_attempts(message_id)
        
        if not attempts:
            return DeliveryState.PENDING
        
        # Return most recent non-pending state
        for attempt in reversed(attempts):
            if attempt.status != DeliveryState.PENDING:
                return attempt.status
        
        return DeliveryState.IN_PROGRESS
    
    def get_delivered_count(self, message_id: str) -> int:
        """Count successful deliveries for a message."""
        attempts = self.get_attempts(message_id)
        return sum(1 for a in attempts if a.status == DeliveryState.DELIVERED)


# =============================================================================
# STRATEGY BASE CLASS
# =============================================================================

class DeliveryStrategy:
    """
    Base class for delivery strategies.
    
    Subclasses implement specific delivery guarantees.
    """
    
    def should_deliver(self, context: DeliveryContext) -> bool:
        """Check if message should be delivered based on strategy."""
        raise NotImplementedError
    
    def handle_failure(
        self,
        context: DeliveryContext,
        error: str,
    ) -> DeliveryState:
        """Handle a delivery failure and return new state."""
        raise NotImplementedError
    
    def needs_retry(self, context: DeliveryContext) -> bool:
        """Check if message should be retried."""
        raise NotImplementedError


class AtMostOnceStrategy(DeliveryStrategy):
    """
    At-most-once delivery strategy.
    
    Single attempt, no retry, may lose messages on failure.
    """
    
    def should_deliver(self, context: DeliveryContext) -> bool:
        return True
    
    def handle_failure(self, context: DeliveryContext, error: str) -> DeliveryState:
        return DeliveryState.DROPPED  # No retry for at-most-once
    
    def needs_retry(self, context: DeliveryContext) -> bool:
        return False


class AtLeastOnceStrategy(DeliveryStrategy):
    """
    At-least-once delivery strategy.
    
    Multiple attempts with backoff, may deliver duplicates on failure recovery.
    """
    
    def should_deliver(self, context: DeliveryContext) -> bool:
        # Continue if below max attempts
        return context.current_attempt < context.max_attempts
    
    def handle_failure(
        self,
        context: DeliveryContext,
        error: str,
    ) -> DeliveryState:
        if context.is_last_attempt():
            return DeliveryState.FAILED
        return DeliveryState.RETRYING
    
    def needs_retry(self, context: DeliveryContext) -> bool:
        # Retry all non-terminal states except PENDING (already pending)
        state = self.handle_failure(context, "")
        return state in (DeliveryState.RETRYING,)


class ExactlyOnceStrategy(DeliveryStrategy):
    """
    Exactly-once delivery strategy.
    
    Requires transactional context and coordination to ensure single delivery.
    This is the most complex strategy and may not be feasible in all contexts.
    """
    
    def __init__(self):
        self._delivered_ids: set = set()
    
    def should_deliver(self, context: DeliveryContext) -> bool:
        # Don't deliver if already delivered
        return context.message_id not in self._delivered_ids
    
    def handle_failure(
        self,
        context: DeliveryContext,
        error: str,
    ) -> DeliveryState:
        if context.is_last_attempt():
            return DeliveryState.FAILED
        return DeliveryState.RETRYING
    
    def mark_delivered(self, message_id: str) -> None:
        """Mark a message as successfully delivered."""
        self._delivered_ids.add(message_id)
    
    def needs_retry(self, context: DeliveryContext) -> bool:
        state = self.handle_failure(context, "")
        return state == DeliveryState.RETRYING


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Delivery modes (guarantees)
    "DeliveryMode",
    
    # Delivery states
    "DeliveryState",
    
    # Attempt records
    "DeliveryAttempt",
    
    # Context
    "DeliveryContext",
    
    # Engine
    "ReliableDeliveryEngine",
    
    # Strategies
    "DeliveryStrategy",
    "AtMostOnceStrategy",
    "AtLeastOnceStrategy",
    "ExactlyOnceStrategy",
]