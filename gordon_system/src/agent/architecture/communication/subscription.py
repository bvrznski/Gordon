# Gordon Core - Publication & Subscription (Phase 3.21.7)
# =========================================================
#
# Canonical publish-subscribe patterns for message distribution
#
# Subscribers express interest in messages matching certain criteria.
# Publishers make information available without knowing who receives it.

"""
Canonical Publication & Subscription for Gordon Phase 3.21.7

SUBSCRIPTION TYPES:
-------------------
1. Filtered: Match messages based on content filters
2. Scoped: Match within a specific scope/correlation context
3. Wildcard: Use wildcard patterns in topic matching
4. Dynamic: Created at runtime (vs static configuration)

SUBSCRIBER LIFECYCLE:
---------------------
- CREATED: Subscription registered but not active
- ACTIVE: Subscribed and receiving messages
- PAUSED: Temporarily suspended
- EXPIRED: Subscription lifetime exceeded
- CANCELLED: Explicitly cancelled by subscriber

PUBLICATION CONTEXT:
--------------------
- Topic: The publication topic name
- Correlation: Correlation context for tracing
- Metadata: Additional publication information
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List, Callable
from enum import Enum, auto
import time
import uuid


# =============================================================================
# SUBSCRIPTION TYPES
# =============================================================================

class SubscriptionType(Enum):
    """
    Canonical subscription types.
    
    Invariants:
        - SUB-TP-001: Every subscription has exactly one type
        - SUB-TP-002: Type determines matching behavior
    """
    
    FILTERED = "filtered"     # Match based on content filters
    SCOPED = "scoped"         # Match within specific scope
    WILDCARD = "wildcard"     # Use wildcard pattern matching
    DYNAMIC = "dynamic"       # Runtime-created subscription


class SubscriptionState(Enum):
    """
    Canonical subscription lifecycle states.
    """
    
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


# =============================================================================
# SUBSCRIPTION IDENTITY
# =============================================================================

@dataclass(frozen=True)
class SubscriptionId:
    """
    Unique identifier for a subscription.
    
    Invariants:
        - SUB-ID-001: Every subscription has exactly one unique identity
        - SUB-ID-002: Identity is immutable once created
    """
    
    value: str
    
    @classmethod
    def generate(cls) -> "SubscriptionId":
        """Generate a new unique subscription ID."""
        return cls(value=f"sub_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# SUBSCRIPTION FILTERS
# =============================================================================

@dataclass(frozen=True)
class SubscriptionFilter:
    """
    Immutable filter for subscription matching.
    
    Args:
        message_types: Message types to match (empty = all)
        topics: Topics to subscribe to (empty = all)
        payload_patterns: Pattern matching on payload (optional)
        correlation_id: Match specific correlation context
    """
    
    message_types: Tuple[str, ...] = field(default_factory=tuple)
    topics: Tuple[str, ...] = field(default_factory=tuple)
    payload_patterns: Dict[str, str] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    
    def matches_message(self, message_type: str, topic: str) -> bool:
        """Check if this filter matches the given message type and topic."""
        # Check message types (if specified)
        if self.message_types and message_type not in self.message_types:
            return False
        
        # Check topics (if specified)
        if self.topics and topic not in self.topics:
            return False
        
        return True


# =============================================================================
# SUBSCRIPTION DESCRIPTOR
# =============================================================================

@dataclass(frozen=True, slots=True)
class SubscriptionDescriptor:
    """
    Immutable descriptor for a subscription.
    
    Args:
        subscription_id: Unique identifier
        subscriber_endpoint_id: Endpoint that subscribed
        filter: Criteria for matching messages
        delivery_mode: How messages should be delivered
        state: Current lifecycle state
        created_at_utc: When subscription was created
        expires_at_utc: When it expires (None = no expiry)
    """
    
    subscription_id: str
    subscriber_endpoint_id: str
    
    filter: SubscriptionFilter = field(default_factory=SubscriptionFilter)
    
    delivery_mode: str = "at-least-once"  # at-most-once, at-least-once, exactly-once
    state: SubscriptionState = SubscriptionState.CREATED
    
    created_at_utc: float = field(default_factory=time.time)
    expires_at_utc: Optional[float] = None
    
    @classmethod
    def create_active(
        cls,
        subscriber_endpoint_id: str,
        filter: Optional[SubscriptionFilter] = None,
        delivery_mode: str = "at-least-once",
        ttl_seconds: float = 3600.0,  # Default 1 hour
    ) -> "SubscriptionDescriptor":
        """Create an active subscription with expiry."""
        return cls(
            subscription_id=uuid.uuid4().hex[:16],
            subscriber_endpoint_id=subscriber_endpoint_id,
            filter=filter or SubscriptionFilter(),
            delivery_mode=delivery_mode,
            state=SubscriptionState.ACTIVE,
            expires_at_utc=time.time() + ttl_seconds,
        )
    
    def is_expired(self) -> bool:
        """Check if subscription has expired."""
        if self.expires_at_utc is None:
            return False
        return time.time() > self.expires_at_utc
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "subscription_id": self.subscription_id,
            "subscriber_endpoint_id": self.subscriber_endpoint_id,
            "filter_message_types": list(self.filter.message_types),
            "filter_topics": list(self.filter.topics),
            "delivery_mode": self.delivery_mode,
            "state": self.state.value,
        }


# =============================================================================
# SUBSCRIBER REGISTRY
# =============================================================================

@dataclass(slots=True)
class SubscriberRegistry:
    """
    Mutable registry for subscription descriptors.
    
    Manages subscription lifecycle and provides efficient lookup.
    
    Note: This class is mutable (for dynamic updates) but contains
    immutable descriptors.
    """
    
    _subscriptions: Dict[str, SubscriptionDescriptor] = field(default_factory=dict)
    _topic_index: Dict[str, List[str]] = field(default_factory=dict)  # topic -> [sub_ids]
    _type_index: Dict[str, List[str]] = field(default_factory=dict)   # type -> [sub_ids]
    _lock = None
    
    def _get_lock(self):
        if self._lock is None:
            import threading
            self._lock = threading.RLock()
        return self._lock
    
    def register(
        self,
        descriptor: SubscriptionDescriptor,
    ) -> str:
        """Register a subscription and return its ID."""
        lock = self._get_lock()
        with lock:
            # Update main registry
            self._subscriptions[descriptor.subscription_id] = descriptor
            
            # Update indices
            for topic in descriptor.filter.topics:
                if topic not in self._topic_index:
                    self._topic_index[topic] = []
                if descriptor.subscription_id not in self._topic_index[topic]:
                    self._topic_index[topic].append(descriptor.subscription_id)
            
            for msg_type in descriptor.filter.message_types:
                if msg_type not in self._type_index:
                    self._type_index[msg_type] = []
                if descriptor.subscription_id not in self._type_index[msg_type]:
                    self._type_index[msg_type].append(descriptor.subscription_id)
            
            return descriptor.subscription_id
    
    def unregister(self, subscription_id: str) -> bool:
        """Unregister a subscription by ID."""
        lock = self._get_lock()
        with lock:
            if subscription_id not in self._subscriptions:
                return False
            
            # Remove from main registry
            sub = self._subscriptions.pop(subscription_id)
            
            # Update indices
            for topic in sub.filter.topics:
                if topic in self._topic_index:
                    self._topic_index[topic] = [
                        s for s in self._topic_index[topic]
                        if s != subscription_id
                    ]
            
            for msg_type in sub.filter.message_types:
                if msg_type in self._type_index:
                    self._type_index[msg_type] = [
                        s for s in self._type_index[msg_type]
                        if s != subscription_id
                    ]
            
            return True
    
    def get_subscription(self, subscription_id: str) -> Optional[SubscriptionDescriptor]:
        """Get a subscription descriptor by ID."""
        return self._subscriptions.get(subscription_id)
    
    def get_subscriptions_for_topic(self, topic: str) -> Tuple[SubscriptionDescriptor, ...]:
        """Get all subscriptions matching a topic."""
        lock = self._get_lock()
        with lock:
            sub_ids = self._topic_index.get(topic, [])
            return tuple(
                self._subscriptions.get(sid)
                for sid in sub_ids
                if self._subscriptions.get(sid) is not None
            )
    
    def get_subscriptions_for_message_type(self, message_type: str) -> Tuple[SubscriptionDescriptor, ...]:
        """Get all subscriptions matching a message type."""
        lock = self._get_lock()
        with lock:
            sub_ids = self._type_index.get(message_type, [])
            return tuple(
                self._subscriptions.get(sid)
                for sid in sub_ids
                if self._subscriptions.get(sid) is not None
            )
    
    def get_all_subscriptions(self) -> Tuple[SubscriptionDescriptor, ...]:
        """Get all registered subscriptions."""
        lock = self._get_lock()
        with lock:
            return tuple(self._subscriptions.values())
    
    def count_by_state(self) -> Dict[str, int]:
        """Count subscriptions by state."""
        lock = self._get_lock()
        with lock:
            counts: Dict[str, int] = {}
            for sub in self._subscriptions.values():
                state = sub.state.value
                counts[state] = counts.get(state, 0) + 1
            return counts
    
    def cleanup_expired(self) -> Tuple[str, ...]:
        """Remove expired subscriptions and return their IDs."""
        lock = self._get_lock()
        with lock:
            expired_ids = [
                sid for sid, sub in self._subscriptions.items()
                if sub.is_expired() or sub.state == SubscriptionState.EXPIRED
            ]
            
            for sub_id in expired_ids:
                self.unregister(sub_id)
            
            return tuple(expired_ids)


# =============================================================================
# PUBLICATION CONTEXT
# =============================================================================

@dataclass(frozen=True, slots=True)
class PublicationContext:
    """
    Immutable context for a publication event.
    
    Args:
        topic: The publication topic
        correlation_id: Correlation context for tracing
        timestamp_utc: When publication occurred
        publisher_endpoint_id: Who published the message
        metadata: Additional publication information
    """
    
    topic: str
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    timestamp_utc: float = field(default_factory=time.time)
    publisher_endpoint_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# PUBLISH RESULT
# =============================================================================

class PublishResult(Enum):
    """
    Canonical publish result types.
    """
    
    SUCCESS = "success"           # Successfully published to all subscribers
    PARTIAL = "partial"           # Some subscribers received the message
    FAILED = "failed"             # Failed to deliver to any subscriber
    DROPPED = "dropped"           # Dropped due to backpressure or policy


@dataclass(frozen=True)
class PublishOutcome:
    """
    Immutable record of a publish operation outcome.
    
    Args:
        result: The overall result type
        subscribers_notified: Number of subscribers that received the message
        delivery_errors: List of errors from failed deliveries
    """
    
    result: PublishResult
    subscribers_notified: int = 0
    delivery_errors: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Subscription types and states
    "SubscriptionType",
    "SubscriptionState",
    
    # Identity
    "SubscriptionId",
    
    # Filters
    "SubscriptionFilter",
    
    # Descriptors
    "SubscriptionDescriptor",
    
    # Registry
    "SubscriberRegistry",
    
    # Publication
    "PublicationContext",
    "PublishResult",
    "PublishOutcome",
]