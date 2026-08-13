# Core Communication Interface
# ============================

"""
Core communication interface - defines contracts for inter-component messaging.

This interface allows different transport mechanisms (in-memory, network,
message queues) while providing a consistent way to send and receive messages.

ARCHITECTURAL PRINCIPLES:
- Message sending is async by default (fire-and-forget)
- Senders don't know about receivers (decoupled)
- Receivers depend only on contracts, not implementation
- Messages are immutable once sent
- Communication is reliable within runtime boundaries
"""

from typing import Protocol, Optional, List, Callable, Any, Dict
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid


class DeliveryMode(Enum):
    """Message delivery semantics."""
    
    FIRE_AND_FORGET = "fire-and-forget"  # No confirmation required
    AT_MOST_ONCE = "at-most-once"        # Delivery confirmed once, may lose on failure
    AT_LEAST_ONCE = "at-least-once"      # Delivery confirmed with retries, possible duplicates
    EXACTLY_ONCE = "exactly-once"        # Guaranteed single delivery (requires transaction)


@dataclass(frozen=True)
class MessageId:
    """Unique identifier for a message."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "MessageId":
        """Generate a new unique message ID."""
        return cls(value=f"msg_{uuid.uuid4().hex[:16]}")
    
    @classmethod
    def from_string(cls, s: str) -> "MessageId":
        """Create a MessageId from a string."""
        return cls(value=s)


@dataclass(frozen=True)
class CorrelationChain:
    """
    Chain of correlated messages for request-response patterns.
    
    Args:
        correlation_id: ID linking all related messages
        causation_id: ID of the message that caused this one (for tracing)
    """
    
    correlation_id: str
    causation_id: Optional[str] = None


@dataclass(frozen=True)
class MessageEnvelope:
    """
    Immutable envelope wrapping a message.
    
    Args:
        message_id: Unique identifier for this message instance
        message_type: Type/class of the message (for routing)
        timestamp_utc: When this envelope was created
        source_component_id: Which component sent this message
        target_component_id: Intended recipient (if any)
        priority: Delivery priority (lower = higher priority)
        expiry_utc: When this message expires (optional)
        payload: The actual message content
    """
    
    message_id: str
    message_type: str
    timestamp_utc: float
    source_component_id: str
    
    # Routing information
    target_component_id: Optional[str] = None
    topic: str = "default"
    
    # Correlation (for request-response patterns)
    correlation_chain: Optional[CorrelationChain] = None
    
    # Priority and delivery constraints
    priority: int = 0
    expiry_utc: Optional[float] = None
    
    payload: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        message_type: str,
        payload: Dict[str, Any],
        source_component_id: str,
        target_component_id: Optional[str] = None,
        topic: str = "default",
    ) -> "MessageEnvelope":
        """Create a new message envelope."""
        return cls(
            message_id=uuid.uuid4().hex,
            message_type=message_type,
            timestamp_utc=time.time(),
            source_component_id=source_component_id,
            target_component_id=target_component_id,
            topic=topic,
            correlation_chain=None,
            priority=0,
            expiry_utc=None,
            payload=payload,
        )
    
    def with_correlation(self, correlation_id: str) -> "MessageEnvelope":
        """Add a correlation chain to this envelope."""
        return MessageEnvelope(
            message_id=self.message_id,
            message_type=self.message_type,
            timestamp_utc=time.time(),
            source_component_id=self.source_component_id,
            target_component_id=self.target_component_id,
            topic=self.topic,
            correlation_chain=CorrelationChain(correlation_id=correlation_id),
            priority=self.priority,
            expiry_utc=self.expiry_utc,
            payload=dict(self.payload),
        )
    
    def with_metadata(self, **kwargs: Any) -> "MessageEnvelope":
        """Create a copy of this envelope with updated metadata."""
        return MessageEnvelope(
            message_id=self.message_id,
            message_type=self.message_type,
            timestamp_utc=time.time(),
            source_component_id=kwargs.get("source_component_id", self.source_component_id),
            target_component_id=kwargs.get("target_component_id", self.target_component_id),
            topic=kwargs.get("topic", self.topic),
            correlation_chain=kwargs.get("correlation_chain", self.correlation_chain),
            priority=kwargs.get("priority", self.priority),
            expiry_utc=kwargs.get("expiry_utc", self.expiry_utc),
            payload=dict(self.payload),
        )


@dataclass(frozen=True)
class SubscriptionDescriptor:
    """
    Immutable descriptor for a subscription.
    
    Args:
        subscription_id: Unique ID for this subscription
        subscriber_component_id: Which component is subscribing
        message_types: Message types to receive (empty = all)
        topics: Topics to subscribe to (empty = no filtering)
    """
    
    subscription_id: str
    subscriber_component_id: str
    
    # Filter criteria
    message_types: tuple = field(default_factory=tuple)  # type: ignore
    topics: tuple = field(default_factory=tuple)  # type: ignore


class IMessageSender(Protocol):
    """
    Interface for message sending.
    
    Senders transmit messages to other components without knowing which
    receivers will get them. This is the key decoupling mechanism in the runtime.
    """
    
    @property
    def sender_id(self) -> str:
        """Get the unique ID of this sender."""
        ...
    
    async def send(
        self,
        envelope: MessageEnvelope,
    ) -> bool:
        """
        Send a message to its target (or broadcast if no target).
        
        Args:
            envelope: The message envelope to send
            
        Returns:
            True if sent (delivery to receiver may still fail)
            
        Note: This method should NOT block waiting for receiver acknowledgment
        unless the delivery mode requires it. Default is fire-and-forget.
        """
        ...
    
    async def send_to(
        self,
        target_component_id: str,
        envelope: MessageEnvelope,
    ) -> bool:
        """
        Send a message to a specific component (bypasses filtering).
        
        Args:
            target_component_id: The recipient component ID
            envelope: The message envelope
            
        Returns:
            True if delivered to the target
        """
        ...
    
    async def broadcast(
        self,
        envelope: MessageEnvelope,
    ) -> int:
        """
        Send a message to all registered subscribers.
        
        Args:
            envelope: The message envelope
            
        Returns:
            Number of subscribers that received the message
        """
        ...


class IMessageReceiver(Protocol):
    """
    Interface for message receiving/subscription management.
    
    Receivers register interest in messages without knowing which senders
    will produce them. This is the other key decoupling mechanism.
    """
    
    @property
    def receiver_id(self) -> str:
        """Get the unique ID of this receiver."""
        ...
    
    def subscribe(
        self,
        subscriber_component_id: str,
        message_types: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        delivery_mode: str = "at-least-once",
        priority: int = 0,
    ) -> str:
        """
        Register interest in messages.
        
        Args:
            subscriber_component_id: Which component is subscribing
            message_types: Message types to receive (empty = all)
            topics: Topics to subscribe to (empty = no filtering)
            delivery_mode: Delivery semantics
            priority: Delivery priority (lower = higher priority)
            
        Returns:
            Subscription ID for later unsubscription
        """
        ...
    
    def subscribe_topic(
        self,
        topic: str,
        subscriber_component_id: str,
    ) -> bool:
        """
        Subscribe to a specific topic.
        
        Args:
            topic: Topic pattern (supports wildcards)
            subscriber_component_id: Subscriber component ID
            
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
    
    def unsubscribe_topic(
        self,
        topic: str,
        subscriber_component_id: str,
    ) -> bool:
        """
        Unsubscribe from a specific topic.
        
        Args:
            topic: Topic pattern
            subscriber_component_id: Subscriber component ID
            
        Returns:
            True if subscription was active
        """
        ...


class IMessageRegistry(Protocol):
    """
    Interface for managing subscriptions and message lookups.
    
    This is an internal interface for efficient subscriber lookup,
    not typically used directly by application code.
    """
    
    @property
    def registry_id(self) -> str:
        """Get the unique ID of this registry."""
        ...
    
    def get_receivers_for_message(
        self,
        envelope: MessageEnvelope,
    ) -> List[str]:
        """
        Get receiver IDs that would receive this message.
        
        Args:
            envelope: The message to route
            
        Returns:
            List of matching subscriber component IDs
        """
        ...
    
    def get_all_subscriptions(self) -> Dict[str, List[SubscriptionDescriptor]]:
        """
        Get all registered subscriptions.
        
        Returns:
            Dictionary mapping subscriber_component_id to list of descriptors
        """
        ...


class IMessageBus(IMessageSender, IMessageReceiver, Protocol):
    """
    Complete message bus interface - combines sender and receiver capabilities.
    
    This is the canonical contract for message bus implementations in Gordon.
    Any implementation must support both sending and subscription management.
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
        Get current health status of the message bus.
        
        Returns:
            Dictionary with status information suitable for health checks
        """
        ...


class MessageError(Exception):
    """Raised when message operations fail."""
    pass


class DeliveryFailedError(MessageError):
    """Raised when message delivery fails."""
    
    def __init__(self, envelope: MessageEnvelope, reason: str):
        super().__init__(
            f"Delivery failed for {envelope.message_id} to {envelope.target_component_id}: {reason}"
        )
        self.envelope = envelope
        self.reason = reason


__all__ = [
    "DeliveryMode",
    "MessageId",
    "CorrelationChain",
    "MessageEnvelope",
    "SubscriptionDescriptor",
    "IMessageSender",
    "IMessageReceiver",
    "IMessageRegistry",
    "IMessageBus",
    "MessageError",
    "DeliveryFailedError",
]