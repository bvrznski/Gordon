# Gordon Core - Communication Reliability (Phase 3.21.10)
# =========================================================
#
# Canonical reliability mechanisms for message delivery
#
# Implements acknowledgements, retries, deduplication, replay protection,
# and dead-letter handling.

"""
Canonical Communication Reliability for Gordon Phase 3.21.10

RELIABILITY MECHANISMS:
-----------------------
1. Acknowledgement: Recipient confirms receipt of message
2. Retry: Failed messages are retried with backoff
3. Deduplication: Duplicate messages detected and handled
4. Replay Protection: Prevents replay attacks on idempotent messages
5. Dead-Letter Queue: Messages that fail permanently are quarantined

IDEMPOTENCY:
------------
Messages can be marked as idempotent (safe to retry with same result).
Idempotency keys ensure the same operation isn't executed multiple times.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple
from enum import Enum, auto
import time
import uuid


# =============================================================================
# ACKNOWLEDGEMENT POLICIES
# =============================================================================

class AcknowledgementMode(Enum):
    """
    Canonical acknowledgement modes.
    
    Invariants:
        - ACK-Mode-001: Mode determines when and what acknowledgment is required
    """
    
    NONE = "none"              # No acknowledgment required (fire-and-forget)
    RECEIVER = "receiver"      # Receiver acknowledges receipt
    SENDER = "sender"          # Sender must confirm delivery
    BOTH = "both"              # Both sender and receiver acknowledge


@dataclass(frozen=True, slots=True)
class AcknowledgementPolicy:
    """
    Immutable policy for message acknowledgements.
    
    Args:
        mode: The acknowledgement mode to use
        timeout_seconds: How long to wait for acknowledgment
        max_retries: Maximum retry attempts after ack failure
        idempotency_enabled: Whether duplicate detection is enabled
    """
    
    mode: AcknowledgementMode = AcknowledgementMode.NONE
    timeout_seconds: float = 30.0
    max_retries: int = 3
    idempotency_enabled: bool = True


# =============================================================================
# RETRY STRATEGIES
# =============================================================================

class RetryStrategy(Enum):
    """
    Canonical retry strategies.
    
    Invariants:
        - RET-STRAT-001: Strategy determines backoff timing between retries
    """
    
    IMMEDIATE = "immediate"    # Retry immediately without delay
    LINEAR = "linear"          # Fixed delay between retries
    EXPONENTIAL = "exponential"  # Delay doubles with each retry
    JITTERED = "jittered"      # Randomized delay to prevent thundering herd


@dataclass(frozen=True, slots=True)
class RetryConfig:
    """
    Immutable retry configuration.
    
    Args:
        strategy: The retry strategy to use
        max_retries: Maximum number of retry attempts
        base_delay_seconds: Base delay for linear/exponential strategies
        max_delay_seconds: Maximum delay cap
        jitter_fraction: Randomization factor (0.0 = no jitter, 1.0 = full)
    """
    
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    max_retries: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    jitter_fraction: float = 0.2


# =============================================================================
# DEAD LETTER CONFIGURATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class DeadLetterConfig:
    """
    Immutable dead-letter queue configuration.
    
    Args:
        enabled: Whether dead-letter handling is enabled
        max_attempts_before_dlq: How many failures before moving to DLQ
        retention_days: How long messages stay in DLQ
        notification_enabled: Whether to notify on DLQ entries
    """
    
    enabled: bool = True
    max_attempts_before_dlq: int = 3
    retention_days: float = 7.0
    notification_enabled: bool = False


# =============================================================================
# IDEMPOTENCY KEY
# =============================================================================

@dataclass(frozen=True)
class IdempotencyKey:
    """
    Immutable key for idempotency checking.
    
    Invariants:
        - IDEM-KEY-001: Same key = same operation result
        - IDEM-KEY-002: Key is derived from message content
    """
    
    value: str
    
    @classmethod
    def generate(cls, message_content: Dict[str, Any]) -> "IdempotencyKey":
        """Generate an idempotency key from message content."""
        # Simple hash-based generation for now
        import hashlib
        content_str = str(sorted(message_content.items()))
        hash_val = hashlib.sha256(content_str.encode()).hexdigest()[:16]
        return cls(value=f"idem_{hash_val}")
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# REPLAY PROTECTION CONTEXT
# =============================================================================

@dataclass(frozen=True, slots=True)
class ReplayProtectionContext:
    """
    Immutable context for replay protection.
    
    Args:
        message_timestamp_utc: When the original message was created
        sender_identity: Identity of the original sender
        nonce: Unique value to prevent replay attacks
        max_age_seconds: Maximum age for valid message
    """
    
    message_timestamp_utc: float = field(default_factory=time.time)
    sender_identity: str = ""
    nonce: Optional[str] = None
    max_age_seconds: float = 300.0  # 5 minutes default
    
    def is_expired(self) -> bool:
        """Check if this context has expired."""
        return time.time() > self.message_timestamp_utc + self.max_age_seconds


# =============================================================================
# ACKNOWLEDGEMENT RECORD
# =============================================================================

@dataclass(frozen=True, slots=True)
class AcknowledgementRecord:
    """
    Immutable record of an acknowledgment.
    
    Args:
        message_id: ID of the acknowledged message
        recipient_id: Who sent the acknowledgment
        timestamp_utc: When acknowledgment occurred
        ack_type: Type of acknowledgment (received, processed, etc.)
    """
    
    message_id: str
    recipient_id: str
    timestamp_utc: float = field(default_factory=time.time)
    ack_type: str = "received"  # received, processed, committed


# =============================================================================
# RELIABILITY STATE
# =============================================================================

@dataclass(slots=True)
class ReliabilityState:
    """
    Mutable state for reliability tracking.
    
    Tracks delivery attempts, acknowledgments, and retry status.
    
    Note: This class is mutable but provides immutable snapshots.
    """
    
    _delivery_attempts: Dict[str, int] = field(default_factory=dict)
    _acknowledgements: Dict[str, Tuple[AcknowledgementRecord, ...]] = field(
        default_factory=dict
    )
    _retry_status: Dict[str, bool] = field(default_factory=dict)  # msg_id -> should_retry
    
    def record_attempt(self, message_id: str) -> None:
        """Record a delivery attempt."""
        current = self._delivery_attempts.get(message_id, 0)
        self._delivery_attempts[message_id] = current + 1
    
    def get_attempts(self, message_id: str) -> int:
        """Get the number of attempts for a message."""
        return self._delivery_attempts.get(message_id, 0)
    
    def record_acknowledgement(
        self,
        message_id: str,
        record: AcknowledgementRecord,
    ) -> None:
        """Record an acknowledgment."""
        records = self._acknowledgements.get(message_id, ())
        self._acknowledgements[message_id] = records + (record,)
    
    def get_acknowledgements(
        self,
        message_id: str,
    ) -> Tuple[AcknowledgementRecord, ...]:
        """Get all acknowledgments for a message."""
        return self._acknowledgements.get(message_id, ())
    
    def should_retry(self, message_id: str) -> bool:
        """Check if a message should be retried."""
        return self._retry_status.get(message_id, True)
    
    def mark_no_retry(self, message_id: str) -> None:
        """Mark that a message should not be retried."""
        self._retry_status[message_id] = False
    
    def reset_state(self, message_id: str) -> None:
        """Reset state for a message (e.g., after successful delivery)."""
        if message_id in self._delivery_attempts:
            del self._delivery_attempts[message_id]
        if message_id in self._acknowledgements:
            del self._acknowledgements[message_id]


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Acknowledgement policies
    "AcknowledgementMode",
    "AcknowledgementPolicy",
    
    # Retry strategies
    "RetryStrategy",
    "RetryConfig",
    
    # Dead letter configuration
    "DeadLetterConfig",
    
    # Idempotency
    "IdempotencyKey",
    
    # Replay protection
    "ReplayProtectionContext",
    
    # Acknowledgement records
    "AcknowledgementRecord",
    
    # State tracking
    "ReliabilityState",
]