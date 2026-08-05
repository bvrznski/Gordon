# Core Communication Observability
# ================================

"""
Observability and diagnostics for communication infrastructure.

Provides:
- Event publishing for communication activities
- Metrics collection (latency, throughput, etc.)
- Diagnostics (routing, delivery, queue health)
- Health status reporting

Communication events observe communication only - they never mutate state.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto
import threading
import time


# =============================================================================
# COMMUNICATION EVENT TYPES
# =============================================================================

class CommunicationEventType(Enum):
    """Types of events emitted by the communication system."""
    
    # Publication events
    EVENT_PUBLISHED = "event_published"
    MESSAGE_PUBLISHED = "message_published"
    SIGNAL_PUBLISHED = "signal_published"
    
    # Delivery events
    DELIVERED = "delivered"
    REJECTED = "rejected"
    FAILED = "failed"
    ACKNOWLEDGED = "acknowledged"
    
    # Subscription events
    SUBSCRIBER_REGISTERED = "subscriber_registered"
    SUBSCRIBER_UNREGISTERED = "subscriber_unregistered"
    
    # Queue events
    QUEUE_OVERFLOW = "queue_overflow"
    BACKPRESSURE_APPLIED = "backpressure_applied"
    
    # Dead letter events
    DEAD_LETTER_GENERATED = "dead_letter_generated"
    
    # Replay events
    REPLAY_STARTED = "replay_started"
    REPLAY_COMPLETED = "replay_completed"


# =============================================================================
# OBSERVABILITY EVENTS (immutable)
# =============================================================================

@dataclass(frozen=True)
class CommunicationEvent:
    """
    Immutable event emitted by communication infrastructure.
    
    Events observe only - they never mutate state or trigger behavior.
    """
    
    event_id: str = ""
    event_type_enum: CommunicationEventType = None  # type: ignore
    
    runtime_id: str = ""
    
    # Timestamps
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Context
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Details (bounded for safety)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EventPublished(CommunicationEvent):
    """Event emitted when an event is published."""
    
    envelope_id: str = ""
    event_type_name: str = ""  # The type of the original event (e.g., "task.completed")
    subscriber_count: int = 0
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        envelope_id: str,
        event_type_name: str,
        subscriber_count: int,
    ) -> "EventPublished":
        return cls(
            event_id=f"evt_pub_{time.monotonic():.6f}",
            event_type_enum=CommunicationEventType.EVENT_PUBLISHED,
            runtime_id=runtime_id,
            envelope_id=envelope_id,
            event_type_name=event_type_name,
            subscriber_count=subscriber_count,
        )


@dataclass(frozen=True)
class MessagePublished(CommunicationEvent):
    """Event emitted when a message is published."""
    
    envelope_id: str = ""
    message_type: str = ""
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        envelope_id: str,
        message_type: str,
    ) -> "MessagePublished":
        return cls(
            event_id=f"msg_pub_{time.monotonic():.6f}",
            event_type_enum=CommunicationEventType.MESSAGE_PUBLISHED,
            runtime_id=runtime_id,
            envelope_id=envelope_id,
            message_type=message_type,
        )


@dataclass(frozen=True)
class SignalPublished(CommunicationEvent):
    """Event emitted when a signal is published."""
    
    envelope_id: str = ""
    signal_type: str = ""
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        envelope_id: str,
        signal_type: str,
    ) -> "SignalPublished":
        return cls(
            event_id=f"sig_pub_{time.monotonic():.6f}",
            event_type_enum=CommunicationEventType.SIGNAL_PUBLISHED,
            runtime_id=runtime_id,
            envelope_id=envelope_id,
            signal_type=signal_type,
        )


@dataclass(frozen=True)
class DeliveryEvent(CommunicationEvent):
    """Base class for delivery-related events."""
    
    envelope_id: str = ""
    subscriber_id: str = ""
    status: str = ""  # delivered, rejected, failed, acknowledged
    
    event_type_enum: CommunicationEventType = CommunicationEventType.DELIVERED


@dataclass(frozen=True)
class SubscriberRegistered(CommunicationEvent):
    """Event emitted when a subscriber registers."""
    
    subscriber_id: str = ""
    subscription_type: str = ""
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        subscriber_id: str,
        subscription_type: str = "event",
    ) -> "SubscriberRegistered":
        return cls(
            event_id=f"sub_reg_{time.monotonic():.6f}",
            event_type_enum=CommunicationEventType.SUBSCRIBER_REGISTERED,
            runtime_id=runtime_id,
            subscriber_id=subscriber_id,
            subscription_type=subscription_type,
        )


@dataclass(frozen=True)
class SubscriberUnregistered(CommunicationEvent):
    """Event emitted when a subscriber unregisters."""
    
    subscriber_id: str = ""
    subscription_type: str = ""
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        subscriber_id: str,
        subscription_type: str = "event",
    ) -> "SubscriberUnregistered":
        return cls(
            event_id=f"sub_unreg_{time.monotonic():.6f}",
            event_type_enum=CommunicationEventType.SUBSCRIBER_UNREGISTERED,
            runtime_id=runtime_id,
            subscriber_id=subscriber_id,
            subscription_type=subscription_type,
        )


@dataclass(frozen=True)
class QueueOverflow(CommunicationEvent):
    """Event emitted when a queue overflows."""
    
    queue_name: str = ""
    overflow_policy: str = "reject"
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        queue_name: str,
        overflow_policy: str = "reject",
    ) -> "QueueOverflow":
        return cls(
            event_id=f"q_overflow_{time.monotonic():.6f}",
            event_type_enum=CommunicationEventType.QUEUE_OVERFLOW,
            runtime_id=runtime_id,
            queue_name=queue_name,
            overflow_policy=overflow_policy,
        )


@dataclass(frozen=True)
class BackpressureApplied(CommunicationEvent):
    """Event emitted when backpressure is applied."""
    
    queue_name: str = ""
    pressure_level: float = 0.0  # 0.0 to 1.0
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        queue_name: str,
        pressure_level: float,
    ) -> "BackpressureApplied":
        return cls(
            event_id=f"bp_applied_{time.monotonic():.6f}",
            event_type_enum=CommunicationEventType.BACKPRESSURE_APPLIED,
            runtime_id=runtime_id,
            queue_name=queue_name,
            pressure_level=pressure_level,
        )


@dataclass(frozen=True)
class DeadLetterGenerated(CommunicationEvent):
    """Event emitted when a message becomes a dead letter."""
    
    envelope_id: str = ""
    reason: str = "queue_overflow"  # from DeadLetterReason
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        envelope_id: str,
        reason: str = "queue_overflow",
    ) -> "DeadLetterGenerated":
        return cls(
            event_id=f"dl_gen_{time.monotonic():.6f}",
            event_type_enum=CommunicationEventType.DEAD_LETTER_GENERATED,
            runtime_id=runtime_id,
            envelope_id=envelope_id,
            reason=reason,
        )


# =============================================================================
# OBSERVABILITY EVENTS AGGREGATOR
# =============================================================================

class CommunicationEventHistory:
    """
    Bounded history of communication events.
    
    Stores events for observability, debugging, and replay purposes.
    """
    
    def __init__(self, max_events: int = 10000):
        self._max_events = max_events
        
        self._lock = threading.RLock()
        
        self._events: List[CommunicationEvent] = []
        self._by_type: Dict[str, List[CommunicationEvent]] = {}
    
    def record(self, event: CommunicationEvent) -> None:
        """Record an event."""
        with self._lock:
            self._events.append(event)
            
            # Update type index
            et = str(event.event_type_enum.value)
            if et not in self._by_type:
                self._by_type[et] = []
            self._by_type[et].append(event)
            
            # Enforce max size
            while len(self._events) > self._max_events:
                old = self._events.pop(0)
                t = str(old.event_type_enum.value)
                if t in self._by_type:
                    try:
                        self._by_type[t].remove(old)
                        if not self._by_type[t]:
                            del self._by_type[t]
                    except ValueError:
                        pass
    
    def get_by_type(self, event_type_enum: CommunicationEventType) -> List[CommunicationEvent]:
        """Get events by type."""
        with self._lock:
            return list(self._by_type.get(str(event_type_enum.value), []))
    
    def get_recent(self, limit: int = 100) -> List[CommunicationEvent]:
        """Get most recent events."""
        with self._lock:
            return list(self._events[-limit:])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event statistics by type."""
        with self._lock:
            counts: Dict[str, int] = {}
            
            for e in self._events:
                t = str(e.event_type_enum.value)
                counts[t] = counts.get(t, 0) + 1
            
            return {
                "total_events": len(self._events),
                "by_type": counts,
            }


# =============================================================================
# DIAGNOSTICS REPORT
# =============================================================================

@dataclass(frozen=True)
class DiagnosticsSnapshot:
    """
    Immutable snapshot of communication diagnostics.
    
    Captures the state of all communication infrastructure at a point in time.
    """
    
    runtime_id: str
    timestamp_utc: float = field(default_factory=time.time)
    
    # Authority states
    event_bus_state: Optional[Dict[str, Any]] = None
    message_router_state: Optional[Dict[str, Any]] = None
    signal_manager_state: Optional[Dict[str, Any]] = None
    
    # Queue states
    queue_depths: Dict[str, int] = field(default_factory=dict)
    
    # Statistics
    publish_count: int = 0
    deliver_count: int = 0
    reject_count: int = 0
    
    # Health
    overall_health: str = "unknown"  # healthy, degraded, failed


# =============================================================================
# DIAGNOSTICS PROVIDER
# =============================================================================

class DiagnosticsProvider:
    """
    Provides diagnostics for communication infrastructure.
    
    Aggregates metrics from all authorities and provides health status.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # Internal stats tracking
        self._publish_count = 0
        self._deliver_count = 0
        self._reject_count = 0
        
        # Queue depth tracking
        self._queue_depths: Dict[str, int] = {}
    
    def record_publish(self) -> None:
        """Record a publish operation."""
        with self._lock:
            self._publish_count += 1
    
    def record_deliver(self) -> None:
        """Record a delivery operation."""
        with self._lock:
            self._deliver_count += 1
    
    def record_reject(self) -> None:
        """Record a rejected message/event."""
        with self._lock:
            self._reject_count += 1
    
    def update_queue_depth(self, queue_name: str, depth: int) -> None:
        """Update the depth of a named queue."""
        with self._lock:
            self._queue_depths[queue_name] = depth
    
    def get_diagnostics(self) -> DiagnosticsSnapshot:
        """Get current diagnostics snapshot."""
        with self._lock:
            # Calculate health
            total_rejected = self._reject_count + sum(
                d for d in self._queue_depths.values() if d > 1000
            )
            
            failure_rate = (
                (self._reject_count / max(self._deliver_count, 1)) * 100
                if self._deliver_count > 0 else 0.0
            )
            
            health = "healthy"
            if total_rejected > 100:
                health = "degraded"
            elif failure_rate > 5:
                health = "failed"
            
            return DiagnosticsSnapshot(
                runtime_id="default",  # Would use actual runtime ID in real impl
                timestamp_utc=time.time(),
                queue_depths=dict(self._queue_depths),
                publish_count=self._publish_count,
                deliver_count=self._deliver_count,
                reject_count=self._reject_count,
                overall_health=health,
            )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status as dictionary."""
        return {
            "status": self.get_diagnostics().overall_health,
            "metrics": {
                "publish_count": self._publish_count,
                "deliver_count": self._deliver_count,
                "reject_count": self._reject_count,
            },
        }


__all__ = [
    # Event types
    "CommunicationEventType",
    
    # Event classes
    "CommunicationEvent",
    "EventPublished",
    "MessagePublished",
    "SignalPublished",
    "DeliveryEvent",
    "SubscriberRegistered",
    "SubscriberUnregistered",
    "QueueOverflow",
    "BackpressureApplied",
    "DeadLetterGenerated",
    
    # History and diagnostics
    "CommunicationEventHistory",
    "DiagnosticsSnapshot",
    "DiagnosticsProvider",
]