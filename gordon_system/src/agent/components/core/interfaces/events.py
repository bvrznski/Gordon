# Core Events Interface
# =====================

"""
Core events interface - defines the contract for event publishing and subscription.

This is a BEHAVIORAL contract that allows different event bus implementations
while maintaining consistent semantics across the runtime.

ARCHITECTURAL PRINCIPLES:
- Event delivery is async by default (fire-and-forget)
- Publishers don't know about subscribers (decoupled)
- Subscribers depend only on contracts, not implementation
- Events are immutable once published
"""

from typing import Protocol, Optional, List, Tuple, Callable, Any, Dict, Set
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid


class DeliveryMode(Enum):
    """
    Event delivery semantics.
    
    - FIRE_AND_FORGET: No confirmation required, best performance
    - AT_MOST_ONCE: Delivery confirmed once, may lose messages on failure
    - AT_LEAST_ONCE: Delivery confirmed with retries, possible duplicates
    - EXACTLY_ONCE: Guaranteed single delivery (requires transaction support)
    """
    FIRE_AND_FORGET = "fire-and-forget"
    AT_MOST_ONCE = "at-most-once"
    AT_LEAST_ONCE = "at-least-once"
    EXACTLY_ONCE = "exactly-once"


class TopicExpression:
    """
    Topic expression with wildcard matching.
    
    Wildcard syntax:
        - *   : Matches exactly one topic level
        - #   : Matches one or more levels
        - **  : Matches zero or more levels
    
    Examples:
        "system.*"       -> matches "system.core", "system.logging"
        "system.#"       -> matches "system.core", "system.core.worker"
        "system.**"      -> matches "" (zero levels) and all descendants
        "system.core.*"  -> matches "system.core.worker", not "system.core"
    """
    
    def __init__(self, pattern: str):
        self.pattern = pattern
        self._parts = pattern.split(".")
    
    def matches(self, topic: str) -> bool:
        """Check if a topic matches this expression."""
        topic_parts = topic.split(".")
        return self._match_parts(self._parts, topic_parts)
    
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
            for i in range(len(topic_parts) + 1):
                if self._match_parts(remaining_pattern, topic_parts[i:]):
                    return True
            return False
        
        # Single-level wildcard (*)
        if pattern == "*":
            if not topic_parts:
                return False
            return self._match_parts(remaining_pattern, topic_parts[1:])
        
        # Multi-level wildcard (#)
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


@dataclass(frozen=True)
class SubscriptionDescriptor:
    """
    Immutable descriptor for a subscription.
    
    A subscription represents interest in certain events from specific sources.
    """
    
    subscription_id: str
    subscriber_id: str
    
    # Filter criteria
    event_types: Tuple = field(default_factory=tuple)  # type: ignore
    topics: Tuple = field(default_factory=tuple)  # type: ignore
    runtime_ids: Tuple = field(default_factory=tuple)  # type: ignore
    
    # Delivery configuration
    delivery_mode: str = "at-least-once"
    priority: int = 0
    max_queue_size: int = 1000
    overflow_policy: str = "reject"  # reject, drop_oldest, drop_newest


@dataclass(frozen=True)
class EventEnvelope:
    """
    Immutable envelope wrapping an event.
    
    The envelope contains metadata about the event while the payload
    is immutable application data.
    """
    
    event_id: str
    event_type: str
    timestamp_utc: float
    
    # Routing information
    source_runtime_id: str = ""
    topic: str = "default"
    
    # Correlation (for request-response patterns)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Priority and delivery constraints
    priority: int = 0
    expiry_utc: Optional[float] = None
    
    @classmethod
    def create(
        cls,
        event_type: str,
        payload: Any,
        source_runtime_id: str = "",
        topic: str = "default",
    ) -> "EventEnvelope":
        """Create a new event envelope."""
        return cls(
            event_id=uuid.uuid4().hex,
            event_type=event_type,
            timestamp_utc=time.time(),
            source_runtime_id=source_runtime_id,
            topic=topic,
            correlation_id=None,
            causation_id=None,
            priority=0,
            expiry_utc=None,
        )
    
    def with_metadata(self, **kwargs: Any) -> "EventEnvelope":
        """Create a copy of this envelope with updated metadata."""
        return EventEnvelope(
            event_id=self.event_id,
            event_type=self.event_type,
            timestamp_utc=time.time(),
            source_runtime_id=kwargs.get("source_runtime_id", self.source_runtime_id),
            topic=kwargs.get("topic", self.topic),
            correlation_id=kwargs.get("correlation_id", self.correlation_id),
            causation_id=kwargs.get("causation_id", self.causation_id),
            priority=kwargs.get("priority", self.priority),
            expiry_utc=kwargs.get("expiry_utc", self.expiry_utc),
        )


class IEventPublisher(Protocol):
    """
    Interface for event publishing.
    
    Publishers send events to the bus without knowing which subscribers
    will receive them. This is the key decoupling mechanism in the runtime.
    """
    
    async def publish(self, envelope: EventEnvelope) -> bool:
        """
        Publish an event to all interested subscribers.
        
        Args:
            envelope: The event envelope to publish
            
        Returns:
            True if published (delivery to individual subscribers may still fail)
            
        Note: This method should NOT block waiting for subscriber acknowledgment
        unless the delivery mode requires it. Default is fire-and-forget.
        """
        ...
    
    async def publish_topic(self, topic: str, envelope: EventEnvelope) -> int:
        """
        Publish an event to all subscribers of a topic.
        
        Args:
            topic: The topic to publish to (supports wildcards)
            envelope: The event envelope
            
        Returns:
            Number of subscribers that received the message
        """
        ...
    
    async def broadcast(self, envelope: EventEnvelope) -> int:
        """
        Publish an event to all registered subscribers.
        
        Args:
            envelope: The event envelope
            
        Returns:
            Number of subscribers that received the message
        """
        ...


class IEventSubscriber(Protocol):
    """
    Interface for event subscription management.
    
    Subscribers register interest in events without knowing which publishers
    will send them. This is the other key decoupling mechanism.
    """
    
    def subscribe(
        self,
        subscriber_id: str,
        event_types: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        runtime_ids: Optional[List[str]] = None,
        delivery_mode: str = "at-least-once",
        priority: int = 0,
    ) -> str:
        """
        Register interest in events.
        
        Args:
            subscriber_id: Unique identifier for this subscriber
            event_types: Event types to receive (empty = all)
            topics: Topics to subscribe to (empty = no filtering)
            runtime_ids: Runtime IDs to filter by (empty = all)
            delivery_mode: Delivery semantics
            priority: Delivery priority (lower = higher priority)
            
        Returns:
            Subscription ID for later unsubscription
        """
        ...
    
    def subscribe_topic(self, topic: str, subscriber_id: str) -> bool:
        """
        Subscribe to a specific topic.
        
        Args:
            topic: Topic pattern (supports wildcards)
            subscriber_id: Subscriber identifier
            
        Returns:
            True if subscription registered
        """
        ...
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Remove a subscription by ID.
        
        Args:
            subscription_id: The subscription to remove
            
        Returns:
            True if found and removed
        """
        ...
    
    def unsubscribe_topic(self, topic: str, subscriber_id: str) -> bool:
        """
        Unsubscribe from a specific topic.
        
        Args:
            topic: Topic pattern
            subscriber_id: Subscriber identifier
            
        Returns:
            True if subscription was active
        """
        ...


class IEventRegistry(Protocol):
    """
    Interface for managing event subscriptions and lookups.
    
    This is an internal interface for efficient subscriber lookup,
    not typically used directly by application code.
    """
    
    def get_subscribers_for_event(self, envelope: EventEnvelope) -> List[str]:
        """
        Get subscriber IDs that would receive this event.
        
        Args:
            envelope: The event to route
            
        Returns:
            List of matching subscriber IDs
        """
        ...
    
    def get_subscribers_for_topic(self, topic: str) -> List[str]:
        """
        Get subscribers interested in a specific topic.
        
        Args:
            topic: Topic pattern (supports wildcards)
            
        Returns:
            List of subscriber IDs subscribed to this topic
        """
        ...
    
    def get_all_subscribers(self) -> Dict[str, List[SubscriptionDescriptor]]:
        """
        Get all registered subscriptions.
        
        Returns:
            Dictionary mapping subscriber_id to list of descriptors
        """
        ...


class IEventBus(IEventPublisher, IEventSubscriber, Protocol):
    """
    Complete event bus interface - combines publisher and subscriber capabilities.
    
    This is the canonical contract for event bus implementations in Gordon.
    Any implementation must support both publishing and subscription management.
    """
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this bus serves."""
        ...
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get bus statistics for observability."""
        ...
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get current health status of the event bus.
        
        Returns:
            Dictionary with status information suitable for health checks
        """
        ...


__all__ = [
    "DeliveryMode",
    "TopicExpression",
    "SubscriptionDescriptor",
    "EventEnvelope",
    "IEventPublisher",
    "IEventSubscriber",
    "IEventRegistry",
    "IEventBus",
]