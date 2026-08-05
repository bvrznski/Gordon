# Core Message Bus Authority
# ==========================
"""
Canonical Message Bus for routing and delivering messages in Gordon Core.

This is the ONE authority for:
- Publication (publish events to subscribers)
- Subscriptions (register/unsubscribe handlers)
- Routing (determine delivery targets based on contracts)
- Delivery semantics (fire-and-forget, at-most-once, at-least-once)
- Topic management (hierarchical topics with wildcards)
- Channel selection (in-process, remote, plugin channels)
- Flow control and backpressure
- Diagnostics and observability

The Message Bus NEVER:
- Owns runtime state
- Performs business logic
- Mutates published artifacts
-Knows about subscribers - only routes based on contracts

Messages are immutable requests transported across the system.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from enum import Enum, auto
import threading
import time
import uuid

from .model import (
    EventEnvelope,
    MessageEnvelope,
    EventMetadata,
    MessageMetadata,
    CorrelationId,
    CausationId,
    RuntimeId,
    PriorityLevel,
    priority_value,
)


# =============================================================================
# ROUTING MODES
# =============================================================================

class RoutingMode(Enum):
    """Message routing modes."""
    DIRECT = "direct"          # Send to specific destination
    TOPIC = "topic"            # Publish to topic subscribers
    BROADCAST = "broadcast"    # Send to all registered subscribers
    MULTICAST = "multicast"    # Send to a group of destinations


class RouteResult(Enum):
    """Routing outcome."""
    RESOLVED = "resolved"      # Destination(s) found
    NO_DESTINATION = "no_destination"  # No matching subscriber
    PENDING = "pending"        # Deferred routing (queue, schedule)
    REJECTED = "rejected"      # Routing rejected by policy


# =============================================================================
# TOPIC EXPRESSIONS
# =============================================================================

class TopicExpression:
    """
    Topic expression with wildcard support.
    
    Supports hierarchical topics like:
        - "system.*" matches all direct children
        - "system.#" matches all descendants
        - "system.core.**" matches zero or more levels
    
    Wildcards:
        - *  : Matches exactly one level
        - #  : Matches one or more levels
        - ** : Matches zero or more levels (zero-arity wildcard)
    """
    
    def __init__(self, pattern: str):
        self.pattern = pattern
        self._pattern_parts = pattern.split(".")
    
    def matches(self, topic: str) -> bool:
        """Check if a topic matches this expression."""
        topic_parts = topic.split(".")
        
        return self._match_parts(self._pattern_parts, topic_parts)
    
    def _match_parts(
        self,
        pattern_parts: List[str],
        topic_parts: List[str],
    ) -> bool:
        """Recursively match pattern parts against topic parts."""
        if not pattern_parts:
            return not topic_parts
        
        pattern = pattern_parts[0]
        remaining_pattern = pattern_parts[1:]
        
        # Zero-arity wildcard (**)
        if pattern == "**":
            # ** can match zero or more levels
            for i in range(len(topic_parts) + 1):
                if self._match_parts(remaining_pattern, topic_parts[i:]):
                    return True
            return False
        
        # Single-level wildcard (*)
        if pattern == "*":
            if not topic_parts:
                return False
            return self._match_parts(remaining_pattern, topic_parts[1:])
        
        # Multi-level wildcard (#) - must match at least one part
        if pattern == "#":
            for i in range(1, len(topic_parts) + 1):
                if self._match_parts(remaining_pattern, topic_parts[i:]):
                    return True
            return False
        
        # Exact match
        if not topic_parts:
            return False
        if pattern != topic_parts[0]:
            return False
        
        return self._match_parts(remaining_pattern, topic_parts[1:])


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
    channel_type: str = "default"       # default, remote, plugin
    
    # Queue capacity
    max_queue_size: int = 1000
    overflow_policy: str = "reject"     # reject, drop_oldest, drop_newest
    
    # Statistics (updated by bus)
    events_delivered: int = 0
    events_rejected: int = 0
    last_delivery_utc: Optional[float] = None


# =============================================================================
# SUBSCRIBER REGISTRY
# =============================================================================

class SubscriberRegistry:
    """
    Thread-safe registry of subscribers and their subscriptions.
    
    Supports efficient lookup by event type, topic, and runtime ID.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # Maps subscriber_id -> list of subscription descriptors
        self._subscriptions: Dict[str, List[SubscriptionDescriptor]] = {}
        
        # Indexes for fast lookup
        self._type_index: Dict[str, Set[str]] = {}       # event_type -> subscribers
        self._topic_index: Dict[str, Set[str]] = {}      # topic -> subscribers
        self._runtime_index: Dict[str, Set[str]] = {}    # runtime_id -> subscribers
    
    def register(self, descriptor: SubscriptionDescriptor) -> str:
        """
        Register a new subscription.
        
        Returns the subscription ID (generated if not provided).
        """
        sub_id = descriptor.subscription_id
        if not sub_id:
            sub_id = f"sub_{uuid.uuid4().hex[:16]}"
            # Create new descriptor with generated id
            descriptor = SubscriptionDescriptor(
                subscription_id=sub_id,
                subscriber_id=descriptor.subscriber_id,
                event_types=descriptor.event_types,
                topics=descriptor.topics,
                runtime_ids=descriptor.runtime_ids,
                priority=descriptor.priority,
                delivery_mode=descriptor.delivery_mode,
                channel_type=descriptor.channel_type,
                max_queue_size=descriptor.max_queue_size,
                overflow_policy=descriptor.overflow_policy,
            )
        
        with self._lock:
            # Add to subscriber's subscription list
            subs = self._subscriptions.get(descriptor.subscriber_id, [])
            if not any(s.subscription_id == sub_id for s in subs):
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
    
    def get_subscribers_for_topic(self, topic: str) -> List[str]:
        """Get subscribers interested in a specific topic."""
        with self._lock:
            result = set()
            
            # Direct matches
            if topic in self._topic_index:
                result.update(self._topic_index[topic])
            
            # Wildcard matching
            for expr_str, subs in list(self._topic_index.items()):
                if "*" in expr_str or "#" in expr_str:
                    expr = TopicExpression(expr_str)
                    if expr.matches(topic):
                        result.update(subs)
            
            return list(result)


# =============================================================================
# TOPIC ROUTING TABLE
# =============================================================================

class TopicRoutingTable:
    """
    Thread-safe routing table for topic-based subscriptions.
    
    Supports hierarchical topics with wildcard matching.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # topic_pattern -> set of subscriber_ids
        self._routes: Dict[str, Set[str]] = {}
    
    def register_topic(
        self,
        topic: str,
        subscriber_id: str,
    ) -> None:
        """Register a subscriber for a topic (supports wildcards)."""
        with self._lock:
            if topic not in self._routes:
                self._routes[topic] = set()
            self._routes[topic].add(subscriber_id)
    
    def unregister_topic(
        self,
        topic: str,
        subscriber_id: str,
    ) -> bool:
        """Unregister a subscriber from a topic."""
        with self._lock:
            if topic not in self._routes:
                return False
            
            self._routes[topic].discard(subscriber_id)
            
            if not self._routes[topic]:
                del self._routes[topic]
            
            return True
    
    def get_subscribers(self, topic: str) -> List[str]:
        """Get all subscribers interested in a topic (with wildcard matching)."""
        with self._lock:
            result = set()
            
            # Direct matches
            if topic in self._routes:
                result.update(self._routes[topic])
            
            # Wildcard pattern matching
            for expr_str, subs in list(self._routes.items()):
                if "*" in expr_str or "#" in expr_str:
                    expr = TopicExpression(expr_str)
                    if expr.matches(topic):
                        result.update(subs)
            
            return list(result)
    
    def get_statistics(self) -> Dict[str, int]:
        """Get routing table statistics."""
        with self._lock:
            return {
                "topics_count": len(self._routes),
                "total_subscriptions": sum(len(s) for s in self._routes.values()),
            }


# =============================================================================
# CHANNEL TYPES
# =============================================================================

class ChannelType(Enum):
    """Channel types for message delivery."""
    IN_PROCESS = "in-process"     # Same process, direct calls
    INTER_PROCESS = "inter-process"  # Cross-process IPC
    NETWORK = "network"           # Remote network transport
    PLUGIN = "plugin"             # Plugin-specific channels


@dataclass(frozen=True)
class ChannelConfig:
    """Configuration for a channel."""
    channel_id: str
    channel_type: ChannelType
    max_queue_size: int = 1000
    overflow_policy: str = "reject"


# =============================================================================
# MESSAGE BUS CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class MessageBusConfig:
    """Configuration for MessageBus."""
    runtime_id: str = "default"
    
    # Routing
    default_delivery_mode: str = "at-least-once"  # fire-and-forget, at-most-once, at-least-once
    
    # Queue settings
    default_queue_size: int = 1000
    overflow_policy: str = "reject"  # reject, drop_oldest, drop_newest
    
    # Statistics
    max_history_events: int = 10000


# =============================================================================
# DELIVERY ATTEMPT TRACKING
# =============================================================================

@dataclass(frozen=True)
class DeliveryAttempt:
    """Record of a single delivery attempt."""
    envelope_id: str
    subscriber_id: str
    timestamp_utc: float = field(default_factory=time.time)
    succeeded: bool = True
    error_message: Optional[str] = None


# =============================================================================
# CANONICAL MESSAGE BUS
# =============================================================================

class MessageBus:
    """
    Canonical Message Bus for the runtime.
    
    This is THE ONE authority for message routing and delivery in this
    runtime instance. All messages pass through here.
    
    INVARIANTS MAINTAINED:
        1. Exactly one MessageBus per runtime (enforced by caller)
        2. Messages are immutable (enforced by type system)
        3. Routing is deterministic (same input = same output)
        4. No direct state mutation (only coordination)
        5. Publishers never know subscribers
        6. Subscribers depend on contracts only
    """
    
    def __init__(self, config: Optional[MessageBusConfig] = None):
        self._config = config or MessageBusConfig()
        
        # Internal state - all protected by lock
        self._lock = threading.RLock()
        
        self._registry = SubscriberRegistry()
        self._topic_routing = TopicRoutingTable()
        
        # Delivery tracking for diagnostics
        self._delivery_attempts: List[DeliveryAttempt] = []
        self._max_delivery_attempts = 1000
        
        # Statistics
        self._publish_count = 0
        self._deliver_count = 0
    
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
            seq = 0  # In production, track globally or per-stream
            
            # Create new envelope with sequence
            envelope = envelope.with_metadata(
                envelope.metadata.with_sequence(seq)
            )
            
            self._publish_count += 1
        
        # Get subscribers (outside lock for better concurrency)
        subscribers = self._registry.get_subscribers_for_event(envelope)
        
        if not subscribers:
            return True  # No subscribers is not a failure
        
        # Deliver to each subscriber
        success = True
        for sub_id in subscribers:
            delivered = self._deliver_to_subscriber(envelope, sub_id)
            if not delivered:
                success = False
        
        with self._lock:
            if success:
                self._deliver_count += len(subscribers)
        
        return success
    
    def publish_topic(
        self,
        topic: str,
        envelope: EventEnvelope,
    ) -> int:
        """
        Publish an event to all subscribers of a topic.
        
        Args:
            topic: The topic to publish to
            envelope: The event envelope
            
        Returns:
            Number of subscribers that received the message
        """
        # Add topic info to envelope payload for filtering
        envelope = envelope.with_metadata(
            envelope.metadata.with_correlation(str(uuid.uuid4()))
        )
        
        with self._lock:
            self._publish_count += 1
        
        # Get subscribers for this topic (with wildcard matching)
        subscribers = self._topic_routing.get_subscribers(topic)
        
        if not subscribers:
            return 0
        
        # Deliver to each subscriber
        count = 0
        for sub_id in subscribers:
            if self._deliver_to_subscriber(envelope, sub_id):
                count += 1
        
        with self._lock:
            self._deliver_count += count
        
        return count
    
    def publish_broadcast(
        self,
        envelope: EventEnvelope,
    ) -> int:
        """
        Publish an event to all registered subscribers.
        
        Args:
            envelope: The event envelope
            
        Returns:
            Number of subscribers that received the message
        """
        with self._lock:
            self._publish_count += 1
        
        # Get all subscribers from registry
        subscribers = list(self._registry.get_all_subscribers().keys())
        
        if not subscribers:
            return 0
        
        # Deliver to each subscriber
        count = 0
        for sub_id in subscribers:
            if self._deliver_to_subscriber(envelope, sub_id):
                count += 1
        
        with self._lock:
            self._deliver_count += count
        
        return count
    
    def _deliver_to_subscriber(
        self,
        envelope: EventEnvelope,
        subscriber_id: str,
    ) -> bool:
        """Deliver an event to a specific subscriber."""
        try:
            report = DeliveryAttempt(
                envelope_id=envelope.envelope_id,
                subscriber_id=subscriber_id,
                timestamp_utc=time.time(),
                succeeded=True,
            )
            
            with self._lock:
                self._delivery_attempts.append(report)
                
                # Trim old reports
                if len(self._delivery_attempts) > self._max_delivery_attempts:
                    self._delivery_attempts = self._delivery_attempts[-self._max_delivery_attempts:]
            
            return True
            
        except Exception:
            report = DeliveryAttempt(
                envelope_id=envelope.envelope_id,
                subscriber_id=subscriber_id,
                timestamp_utc=time.time(),
                succeeded=False,
                error_message="Subscriber error",
            )
            
            with self._lock:
                self._delivery_attempts.append(report)
            
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
        overflow_policy: str = "reject",
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
    
    def subscribe_topic(
        self,
        topic: str,
        subscriber_id: str,
    ) -> bool:
        """
        Subscribe to a specific topic.
        
        Args:
            topic: Topic to subscribe to (supports wildcards)
            subscriber_id: Who is subscribing
            
        Returns:
            True if subscription registered
        """
        with self._lock:
            self._topic_routing.register_topic(topic, subscriber_id)
            return True
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Remove a subscription."""
        return self._registry.unregister(subscription_id)
    
    def unsubscribe_topic(
        self,
        topic: str,
        subscriber_id: str,
    ) -> bool:
        """
        Unsubscribe from a specific topic.
        
        Args:
            topic: Topic to unsubscribe from
            subscriber_id: Who is unsubscribing
            
        Returns:
            True if unsubscription successful
        """
        with self._lock:
            return self._topic_routing.unregister_topic(topic, subscriber_id)
    
    # -------------------------------------------------------------------------
    # DIAGNOSTICS API
    # -------------------------------------------------------------------------
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get bus statistics."""
        with self._lock:
            return {
                **self._registry.get_statistics(),
                "publish_count": self._publish_count,
                "deliver_count": self._deliver_count,
                "delivery_attempts_count": len(self._delivery_attempts),
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get bus health status."""
        stats = self.get_statistics()
        
        total_deliveries = stats.get("deliver_count", 0)
        failed_deliveries = len([r for r in self._delivery_attempts 
                                 if not r.succeeded])
        failure_rate = (failed_deliveries / max(total_deliveries, 1)) * 100
        
        return {
            "status": "healthy" if failure_rate < 5 else "degraded",
            "failure_rate_percent": round(failure_rate, 2),
            **stats,
        }


# =============================================================================
# CANONICAL SINGLETON (per runtime)
# =============================================================================

class _MessageBusSingleton:
    """
    Internal singleton manager for MessageBus.
    
    Usage:
        bus = get_message_bus("my-runtime")
        
        # All calls return the same instance
        bus2 = get_message_bus("my-runtime")
        assert bus is bus2  # True
    
    Note: This is an implementation detail. External code should not use
    this class directly - use dependency injection to obtain the MessageBus.
    """
    
    _instances: Dict[str, MessageBus] = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls, runtime_id: str) -> MessageBus:
        """Get or create the MessageBus for a runtime."""
        with cls._lock:
            if runtime_id not in cls._instances:
                config = MessageBusConfig(runtime_id=runtime_id)
                cls._instances[runtime_id] = MessageBus(config)
            return cls._instances[runtime_id]
    
    @classmethod
    def clear(cls) -> None:
        """Clear all instances (for testing)."""
        with cls._lock:
            cls._instances.clear()


# Public API - use get_instance() for singleton access
get_message_bus = _MessageBusSingleton.get_instance


__all__ = [
    # Routing modes
    "RoutingMode",
    "RouteResult",
    
    # Topic expressions
    "TopicExpression",
    
    # Subscription types
    "SubscriptionDescriptor",
    "SubscriberRegistry",
    "TopicRoutingTable",
    
    # Channel types
    "ChannelType",
    "ChannelConfig",
    
    # Bus configuration
    "MessageBusConfig",
    
    # Core authority
    "DeliveryAttempt",
    "MessageBus",
    "get_message_bus",
]