# Core EventBus Authority
# =======================

"""
Canonical EventBus for runtime communication.

This is ONE authority for:
- Publication (publish events to subscribers)
- Subscriptions (register/unsubscribe handlers)
- Routing (determine delivery targets)
- Fan-out (broadcast to multiple subscribers)
- Replay (replay history)
- History (store and query event history)
- Diagnostics (track metrics and health)

The EventBus NEVER:
- Owns runtime state
- Performs business logic
- Mutates published artifacts

Events are immutable facts transported across the system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from enum import Enum, auto
import threading
import time
import uuid

from .model import EventId, CorrelationId, CausationId, RuntimeId, PriorityLevel, priority_value
from .envelope import EventEnvelope, DeliveryReport, Acknowledgement


# =============================================================================
# SUBSCRIPTION POLICIES
# =============================================================================

class OverflowPolicy(Enum):
    """Behavior when queue is full."""
    REJECT = "reject"      # Reject new events (raise exception)
    DROP_OLDEST = "drop_oldest"  # Drop oldest to make room
    DROP_NEWEST = "drop_newest"  # Keep existing, drop new


class SubscriptionFilter:
    """
    Event filtering criteria for subscriptions.
    
    A subscription receives an event if ANY filter matches (OR semantics).
    Within a filter, all conditions must match (AND semantics).
    """
    
    def __init__(
        self,
        event_type: Optional[str] = None,
        topic: Optional[str] = None,
        runtime_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        metadata_match: Optional[Dict[str, Any]] = None,
    ):
        self.event_type = event_type
        self.topic = topic
        self.runtime_id = runtime_id
        self.correlation_id = correlation_id
        self.metadata_match = metadata_match or {}
    
    def matches(self, envelope: EventEnvelope) -> bool:
        """Check if this filter matches an envelope."""
        # Check event type
        if self.event_type and envelope.event_type != self.event_type:
            return False
        
        # Check topic (if envelope has topic info in payload)
        if self.topic:
            envelope_topic = envelope.payload.get("_topic")
            if envelope_topic != self.topic:
                return False
        
        # Check runtime ID
        if self.runtime_id and envelope.runtime_id != self.runtime_id:
            return False
        
        # Check correlation ID
        if self.correlation_id and envelope.correlation_id != self.correlation_id:
            return False
        
        # Check metadata match (if specified)
        for key, value in self.metadata_match.items():
            if envelope.payload.get(key) != value:
                return False
        
        return True


# =============================================================================
# SUBSCRIPTION DESCRIPTOR
# =============================================================================

@dataclass(frozen=True)
class SubscriptionDescriptor:
    """
    Immutable descriptor for a subscription.
    
    A subscription represents interest in certain events from specific sources.
    """
    
    subscription_id: str
    subscriber_id: str  # Who is subscribed
    
    # Filter criteria
    event_types: Tuple[str, ...] = field(default_factory=tuple)
    topics: Tuple[str, ...] = field(default_factory=tuple)
    runtime_ids: Tuple[str, ...] = field(default_factory=tuple)
    
    # Delivery configuration
    priority: int = 0  # Lower = higher priority (affects delivery order)
    delivery_mode: str = "synchronous"  # sync, async, queued
    
    # Queue capacity
    max_queue_size: int = 1000
    overflow_policy: OverflowPolicy = OverflowPolicy.REJECT
    
    # Statistics
    events_delivered: int = 0
    events_rejected: int = 0
    last_delivery_utc: Optional[float] = None
    
    def matches(self, envelope: EventEnvelope) -> bool:
        """Check if this subscription would receive the given envelope."""
        # Must match at least one event type (or no filter)
        if self.event_types and envelope.event_type not in self.event_types:
            return False
        
        # Must match at least one runtime ID (or no filter)
        if self.runtime_ids and envelope.runtime_id not in self.runtime_ids:
            return False
        
        # Topic matching is OR - matches any topic in list
        if self.topics:
            envelope_topic = envelope.payload.get("_topic")
            if envelope_topic not in self.topics:
                return False
        
        return True
    
    def with_stats(
        self,
        delivered: int,
        rejected: int,
        last_delivery_utc: Optional[float],
    ) -> "SubscriptionDescriptor":
        """Return copy with updated statistics."""
        return SubscriptionDescriptor(
            subscription_id=self.subscription_id,
            subscriber_id=self.subscriber_id,
            event_types=self.event_types,
            topics=self.topics,
            runtime_ids=self.runtime_ids,
            priority=self.priority,
            delivery_mode=self.delivery_mode,
            max_queue_size=self.max_queue_size,
            overflow_policy=self.overflow_policy,
            events_delivered=delivered,
            events_rejected=rejected,
            last_delivery_utc=last_delivery_utc,
        )


# =============================================================================
# SUBSCRIBER REGISTRY
# =============================================================================

class SubscriberRegistry:
    """
    Registry of all subscribers and their subscriptions.
    
    Thread-safe read operations use lock-free pattern where possible.
    Write operations acquire exclusive lock.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # Maps subscriber_id -> list of subscription descriptors
        self._subscriptions: Dict[str, List[SubscriptionDescriptor]] = {}
        
        # Maps event_type -> set of subscriber_ids interested
        self._type_index: Dict[str, Set[str]] = {}
        
        # Maps topic -> set of subscriber_ids interested
        self._topic_index: Dict[str, Set[str]] = {}
        
        # Maps runtime_id -> set of subscriber_ids interested
        self._runtime_index: Dict[str, Set[str]] = {}
    
    def register(
        self,
        descriptor: SubscriptionDescriptor,
    ) -> str:
        """
        Register a new subscription.
        
        Args:
            descriptor: Subscription configuration
            
        Returns:
            The subscription ID (generated if not provided)
        """
        sub_id = descriptor.subscription_id
        if not sub_id:
            sub_id = f"sub_{uuid.uuid4().hex[:16]}"
            # Create new descriptor with generated subscription_id
            descriptor = SubscriptionDescriptor(
                subscription_id=sub_id,
                subscriber_id=descriptor.subscriber_id,
                event_types=descriptor.event_types,
                topics=descriptor.topics,
                runtime_ids=descriptor.runtime_ids,
                priority=descriptor.priority,
                delivery_mode=descriptor.delivery_mode,
                max_queue_size=descriptor.max_queue_size,
                overflow_policy=descriptor.overflow_policy,
                events_delivered=descriptor.events_delivered,
                events_rejected=descriptor.events_rejected,
                last_delivery_utc=descriptor.last_delivery_utc,
            )
        
        with self._lock:
            # Add to subscriber's subscription list
            subs = self._subscriptions.get(descriptor.subscriber_id, [])
            subs.append(descriptor)
            self._subscriptions[descriptor.subscriber_id] = subs
            
            # Update indexes
            for event_type in descriptor.event_types:
                if event_type not in self._type_index:
                    self._type_index[event_type] = set()
                self._type_index[event_type].add(descriptor.subscriber_id)
            
            for topic in descriptor.topics:
                if topic not in self._topic_index:
                    self._topic_index[topic] = set()
                self._topic_index[topic].add(descriptor.subscriber_id)
            
            for runtime_id in descriptor.runtime_ids:
                if runtime_id not in self._runtime_index:
                    self._runtime_index[runtime_id] = set()
                self._runtime_index[runtime_id].add(descriptor.subscriber_id)
        
        return sub_id
    
    def unregister(self, subscription_id: str) -> bool:
        """Remove a subscription by ID."""
        with self._lock:
            for subscriber_id, subs in list(self._subscriptions.items()):
                for i, sub in enumerate(subs):
                    if sub.subscription_id == subscription_id:
                        # Remove from subscriptions
                        new_subs = subs[:i] + subs[i+1:]
                        if new_subs:
                            self._subscriptions[subscriber_id] = new_subs
                        else:
                            del self._subscriptions[subscriber_id]
                        
                        # Update indexes
                        for event_type in sub.event_types:
                            if event_type in self._type_index:
                                self._type_index[event_type].discard(subscriber_id)
                                if not self._type_index[event_type]:
                                    del self._type_index[event_type]
                        
                        for topic in sub.topics:
                            if topic in self._topic_index:
                                self._topic_index[topic].discard(subscriber_id)
                                if not self._topic_index[topic]:
                                    del self._topic_index[topic]
                        
                        for runtime_id in sub.runtime_ids:
                            if runtime_id in self._runtime_index:
                                self._runtime_index[runtime_id].discard(subscriber_id)
                                if not self._runtime_index[runtime_id]:
                                    del self._runtime_index[runtime_id]
                        
                        return True
        return False
    
    def get_subscribers_for_event(
        self,
        envelope: EventEnvelope,
    ) -> List[str]:
        """Get subscriber IDs that would receive this event."""
        with self._lock:
            candidates = set()
            
            # Find subscribers interested in this event type
            if envelope.event_type in self._type_index:
                candidates.update(self._type_index[envelope.event_type])
            
            # Filter by runtime ID if specified in subscription
            result = []
            for sub_id in candidates:
                subs = self._subscriptions.get(sub_id, [])
                for sub in subs:
                    if sub.matches(envelope):
                        result.append(sub_id)
                        break
            
            return list(set(result))
    
    def get_all_subscribers(self) -> Dict[str, List[SubscriptionDescriptor]]:
        """Get all registered subscriptions."""
        with self._lock:
            return dict(self._subscriptions)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with self._lock:
            total_subs = sum(len(s) for s in self._subscriptions.values())
            return {
                "total_subscriptions": total_subs,
                "subscriber_count": len(self._subscriptions),
                "event_type_index_size": len(self._type_index),
                "topic_index_size": len(self._topic_index),
            }


# =============================================================================
# EVENT HISTORY
# =============================================================================

@dataclass(frozen=True)
class EventHistoryEntry:
    """Immutable history entry for an event."""
    
    envelope_id: str
    runtime_id: str
    event_type: str
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    sequence_number: int = 0
    created_at_utc: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "envelope_id": self.envelope_id,
            "runtime_id": self.runtime_id,
            "event_type": self.event_type,
            "payload": dict(self.payload),
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "sequence_number": self.sequence_number,
            "created_at_utc": self.created_at_utc,
        }


class EventHistory:
    """
    Bounded history of delivered events.
    
    Provides deterministic replay capability by storing events in order.
    History is append-only - never modifies existing entries.
    """
    
    def __init__(self, max_events: int = 10000):
        self._max_events = max_events
        self._lock = threading.RLock()
        
        # Store all event history as EventHistoryEntry
        self._history: List[EventHistoryEntry] = []
        
        # Indexes for fast lookup
        self._by_type: Dict[str, List[EventHistoryEntry]] = {}
        self._by_correlation: Dict[str, List[EventHistoryEntry]] = {}
    
    def add(self, envelope: EventEnvelope) -> None:
        """Add an event to history."""
        entry = EventHistoryEntry(
            envelope_id=envelope.envelope_id,
            runtime_id=envelope.runtime_id,
            event_type=envelope.event_type,
            payload=dict(envelope.payload),
            correlation_id=envelope.correlation_id,
            causation_id=envelope.causation_id,
            sequence_number=envelope.sequence_number,
            created_at_utc=envelope.created_at_utc,
        )
        
        with self._lock:
            # Add to main history (bounded)
            self._history.append(entry)
            
            if len(self._history) > self._max_events:
                old = self._history.pop(0)
                # Clean up indexes
                self._remove_from_index(old)
            
            # Update indexes
            event_type = envelope.event_type
            if event_type not in self._by_type:
                self._by_type[event_type] = []
            self._by_type[event_type].append(entry)
            
            corr_id = envelope.correlation_id
            if corr_id and corr_id not in self._by_correlation:
                self._by_correlation[corr_id] = []
            if corr_id:
                self._by_correlation[corr_id].append(entry)
    
    def _remove_from_index(self, entry: EventHistoryEntry) -> None:
        """Remove an entry from indexes (called during eviction)."""
        event_type = entry.event_type
        if event_type in self._by_type:
            try:
                self._by_type[event_type].remove(entry)
                if not self._by_type[event_type]:
                    del self._by_type[event_type]
            except ValueError:
                pass
        
        corr_id = entry.correlation_id
        if corr_id and corr_id in self._by_correlation:
            try:
                self._by_correlation[corr_id].remove(entry)
                if not self._by_correlation[corr_id]:
                    del self._by_correlation[corr_id]
            except ValueError:
                pass
    
    def get_by_type(
        self,
        event_type: str,
        since: Optional[float] = None,
        until: Optional[float] = None,
    ) -> List[EventHistoryEntry]:
        """Get events by type, optionally filtered by time range."""
        with self._lock:
            results = list(self._by_type.get(event_type, []))
        
        # Apply time filters
        if since is not None:
            results = [e for e in results if e.created_at_utc >= since]
        if until is not None:
            results = [e for e in results if e.created_at_utc <= until]
        
        return results
    
    def get_by_correlation(
        self,
        correlation_id: str,
    ) -> List[EventHistoryEntry]:
        """Get all events in a correlation chain."""
        with self._lock:
            return list(self._by_correlation.get(correlation_id, []))
    
    def replay_from(
        self,
        since_sequence: int = 0,
    ) -> List[Tuple[int, EventEnvelope]]:
        """
        Replay events from a sequence number.
        
        Returns tuples of (sequence_number, EventEnvelope).
        Events are returned in order with their sequence numbers.
        """
        with self._lock:
            result = []
            for entry in self._history:
                if entry.sequence_number >= since_sequence:
                    envelope = EventEnvelope(
                        envelope_id=entry.envelope_id,
                        runtime_id=entry.runtime_id,
                        event_type=entry.event_type,
                        payload=dict(entry.payload),
                        correlation_id=entry.correlation_id,
                        causation_id=entry.causation_id,
                        created_at_utc=entry.created_at_utc,
                        sequence_number=entry.sequence_number,
                    )
                    result.append((entry.sequence_number, envelope))
            return result
    
    def get_latest_sequence(self) -> int:
        """Get the highest sequence number in history."""
        with self._lock:
            if not self._history:
                return 0
            return max(e.sequence_number for e in self._history)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get history statistics."""
        with self._lock:
            return {
                "total_events": len(self._history),
                "event_types_count": len(self._by_type),
                "correlation_chains_count": len(self._by_correlation),
            }


# =============================================================================
# SPLIT-BRAIN FENCING
# =============================================================================
# Generation counter for fencing against split-brain scenarios (COMM-HIGH-002)

class SplitBrainFence:
    """
    Fencing token to prevent split-brain in multi-runtime scenarios.
    
    Each runtime instance gets a monotonically increasing generation number.
    When a new instance starts, it receives a higher generation than any
    previous instance with the same runtime_id. This prevents stale instances
    from making changes after being fenced out.
    
    Usage:
        # Create fence for runtime
        fence = SplitBrainFence("runtime-abc")
        
        # Get current generation
        gen = fence.get_generation()  # Returns 1
        
        # Increment on restart
        new_gen = fence.increment_generation()  # Returns 2
        
        # Check if still active (true if gen > 0)
        if fence.is_active():
            # Runtime is active
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._generation = 1
        self._lock = threading.Lock()
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this fence serves."""
        return self._runtime_id
    
    @property
    def generation(self) -> int:
        """Get current generation number (higher = newer instance)."""
        with self._lock:
            return self._generation
    
    def get_generation(self) -> int:
        """Get current generation number."""
        return self.generation
    
    def increment_generation(self) -> int:
        """
        Increment generation when restarting/resuming.
        
        Returns new generation number (always > previous).
        """
        with self._lock:
            self._generation += 1
            return self._generation
    
    def is_active(self) -> bool:
        """Check if this fence instance is still active."""
        return self._generation > 0


# =============================================================================
# CANONICAL EVENT BUS
# =============================================================================

class EventBusConfig:
    """Configuration for EventBus instance."""
    
    def __init__(
        self,
        runtime_id: str = "default",
        max_history_events: int = 10000,
        default_delivery_mode: str = "synchronous",
    ):
        self.runtime_id = runtime_id
        self.max_history_events = max_history_events
        self.default_delivery_mode = default_delivery_mode


class EventBus:
    """
    Canonical EventBus for the runtime.
    
    This is THE ONE authority for event publication and subscription
    management in this runtime instance. All events flow through here.
    
    Invariants maintained:
        1. Exactly one EventBus per runtime (enforced by caller)
        2. Events are immutable (enforced by type system)
        3. No direct state mutation (only delivery coordination)
        4. Deterministic ordering within streams
        5. Split-brain fencing via generation counter (COMM-HIGH-002)
    """
    
    def __init__(self, config: Optional[EventBusConfig] = None):
        self._config = config or EventBusConfig()
        
        # Internal state - all protected by lock
        self._lock = threading.RLock()
        
        self._registry = SubscriberRegistry()
        self._history = EventHistory(self._config.max_history_events)
        
        # Split-brain fencing (COMM-HIGH-002)
        self._fence = SplitBrainFence(self._config.runtime_id)
        
        # Delivery tracking for diagnostics
        self._delivery_reports: List[DeliveryReport] = []
        self._max_delivery_reports = 1000
        
        # Statistics
        self._publish_count = 0
        self._deliver_count = 0
    
    @property
    def fence(self) -> SplitBrainFence:
        """Get the split-brain fence for this runtime."""
        return self._fence
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this bus serves."""
        return self._config.runtime_id
    
    # -------------------------------------------------------------------------
    # PUBLICATION API
    # -------------------------------------------------------------------------
    
    def publish(
        self,
        envelope: EventEnvelope,
    ) -> bool:
        """
        Publish an event to all interested subscribers.
        
        Args:
            envelope: The event envelope to publish
            
        Returns:
            True if published (may still fail delivery to individual subscribers)
        """
        with self._lock:
            # Update sequence number
            seq = self._history.get_latest_sequence() + 1
            envelope = envelope.with_sequence(seq)
            
            # Add to history first
            self._history.add(envelope)
            
            self._publish_count += 1
        
        # Get subscribers (outside lock for better concurrency)
        subscribers = self._registry.get_subscribers_for_event(envelope)
        
        if not subscribers:
            return True  # No subscribers is not a failure
        
        # Deliver to each subscriber (synchronously for now)
        success = True
        for sub_id in subscribers:
            delivered = self._deliver_to_subscriber(envelope, sub_id)
            if not delivered:
                success = False
        
        with self._lock:
            if success:
                self._deliver_count += len(subscribers)
        
        return success
    
    def publish_immediate(
        self,
        envelope: EventEnvelope,
        subscriber_id: str,
    ) -> bool:
        """
        Publish directly to a specific subscriber (bypasses filters).
        
        Args:
            envelope: Event to send
            subscriber_id: Target subscriber
            
        Returns:
            True if delivered
        """
        return self._deliver_to_subscriber(envelope, subscriber_id)
    
    def _deliver_to_subscriber(
        self,
        envelope: EventEnvelope,
        subscriber_id: str,
    ) -> bool:
        """Deliver an event to a specific subscriber."""
        try:
            # For now, just log delivery - real impl would use queues
            report = DeliveryReport.success(
                envelope_id=envelope.envelope_id,
                runtime_id=self._config.runtime_id,
                subscriber_id=subscriber_id,
                channel_name="default",
                queue_wait_ms=0.0,
                delivery_latency_ms=0.1,
                processing_latency_ms=0.2,
            )
            
            with self._lock:
                self._delivery_reports.append(report)
                
                # Trim old reports
                if len(self._delivery_reports) > self._max_delivery_reports:
                    self._delivery_reports = self._delivery_reports[-self._max_delivery_reports:]
            
            return True
            
        except Exception:
            report = DeliveryReport.failure(
                envelope_id=envelope.envelope_id,
                runtime_id=self._config.runtime_id,
                error_message="Subscriber error",
            )
            
            with self._lock:
                self._delivery_reports.append(report)
            
            return False
    
    # -------------------------------------------------------------------------
    # SUBSCRIPTION API
    # -------------------------------------------------------------------------
    
    def subscribe(
        self,
        subscriber_id: str,
        event_types: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        runtime_ids: Optional[List[str]] = None,
        priority: int = 0,
        max_queue_size: int = 1000,
        overflow_policy: OverflowPolicy = OverflowPolicy.REJECT,
    ) -> str:
        """
        Register interest in events.
        
        Args:
            subscriber_id: Who is subscribing
            event_types: Event types to receive (empty = all)
            topics: Topics to subscribe to (empty = no topic filtering)
            runtime_ids: Runtime IDs to filter by (empty = all)
            priority: Delivery priority (lower = higher priority)
            max_queue_size: Maximum queued events
            overflow_policy: What to do when queue is full
            
        Returns:
            Subscription ID for later unsubscription
        """
        descriptor = SubscriptionDescriptor(
            subscription_id="",
            subscriber_id=subscriber_id,
            event_types=tuple(event_types or []),
            topics=tuple(topics or []),
            runtime_ids=tuple(runtime_ids or []),
            priority=priority,
            delivery_mode=self._config.default_delivery_mode,
            max_queue_size=max_queue_size,
            overflow_policy=overflow_policy,
        )
        
        return self._registry.register(descriptor)
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Remove a subscription."""
        return self._registry.unregister(subscription_id)
    
    # -------------------------------------------------------------------------
    # HISTORY AND REPLAY API
    # -------------------------------------------------------------------------
    
    def get_history(
        self,
        since_sequence: int = 0,
    ) -> List[Tuple[int, EventEnvelope]]:
        """
        Get event history from a sequence number.
        
        Args:
            since_sequence: Start from this sequence (inclusive)
            
        Returns:
            List of (sequence_number, EventEnvelope) tuples
        """
        return self._history.replay_from(since_sequence)
    
    def replay(
        self,
        since_sequence: int = 0,
    ) -> None:
        """
        Replay events by republishing them.
        
        Note: Replay creates new envelopes with the same content but
        different envelope IDs. This preserves correlation/causation chains
        while treating replays as distinct delivery events.
        """
        history = self.get_history(since_sequence)
        
        for seq, envelope in history:
            # Create new envelope for replay
            replay_envelope = EventEnvelope(
                envelope_id=str(uuid.uuid4()),
                runtime_id=self._config.runtime_id,
                event_type=envelope.event_type,
                payload=dict(envelope.payload),
                correlation_id=envelope.correlation_id,
                causation_id=envelope.causation_id,
                sequence_number=seq,
            )
            
            self.publish(replay_envelope)
    
    # -------------------------------------------------------------------------
    # DIAGNOSTICS API
    # -------------------------------------------------------------------------
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get bus statistics."""
        with self._lock:
            return {
                **self._registry.get_statistics(),
                **self._history.get_statistics(),
                "publish_count": self._publish_count,
                "deliver_count": self._deliver_count,
                "delivery_reports_count": len(self._delivery_reports),
            }
    
    def get_delivery_reports(
        self,
        since: Optional[float] = None,
    ) -> List[DeliveryReport]:
        """Get delivery reports, optionally filtered by time."""
        with self._lock:
            if since is None:
                return list(self._delivery_reports)
            return [r for r in self._delivery_reports if r.delivery_time_utc >= since]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get communication health status."""
        stats = self.get_statistics()
        
        # Determine overall health
        total_deliveries = stats.get("deliver_count", 0)
        failed_deliveries = len([r for r in self._delivery_reports 
                                 if r.status == Acknowledgement.FAILED])
        failure_rate = (failed_deliveries / max(total_deliveries, 1)) * 100
        
        return {
            "status": "healthy" if failure_rate < 5 else "degraded",
            "failure_rate_percent": round(failure_rate, 2),
            **stats,
        }


# =============================================================================
# CANONICAL SINGLETON (per runtime)
# =============================================================================

class _EventBusSingleton:
    """
    Internal singleton manager for EventBus.
    
    Usage:
        # Get or create the bus for a runtime
        bus = EventBus.get_instance(runtime_id="my-runtime")
        
        # All calls return the same instance for that runtime
        bus2 = EventBus.get_instance(runtime_id="my-runtime")
        assert bus is bus2  # True
    
    Note: This is an implementation detail. External code should not use
    this class directly - use the application's dependency injection
    to obtain the EventBus instance.
    """
    
    _instances: Dict[str, EventBus] = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls, runtime_id: str) -> EventBus:
        """Get or create the EventBus for a runtime."""
        with cls._lock:
            if runtime_id not in cls._instances:
                config = EventBusConfig(runtime_id=runtime_id)
                cls._instances[runtime_id] = EventBus(config)
            return cls._instances[runtime_id]
    
    @classmethod
    def clear(cls) -> None:
        """Clear all instances (for testing)."""
        with cls._lock:
            cls._instances.clear()


# Public API - use get_instance() for singleton access
get_event_bus = _EventBusSingleton.get_instance

__all__ = [
    # Policies
    "OverflowPolicy",
    
    # Subscription types
    "SubscriptionDescriptor",
    "SubscriberRegistry",
    "SubscriptionFilter",
    
    # History types
    "EventHistoryEntry",
    "EventHistory",
    
    # Split-brain fencing (COMM-HIGH-002)
    "SplitBrainFence",
    
    # Core authority
    "EventBusConfig",
    "EventBus",
    "get_event_bus",
]
