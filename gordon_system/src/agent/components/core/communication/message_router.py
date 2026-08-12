# Core MessageRouter Authority
# ============================

"""
Canonical MessageRouter for routing messages to their destinations.

This is ONE authority for:
- Destination resolution (determine where a message should go)
- Routing policies (direct, topic, broadcast, multicast, priority)
- Priority routing (higher priority messages get delivery precedence)
- Directed delivery (specific recipient)
- Multicast (multiple specific recipients)
- Broadcast (all interested parties)

The MessageRouter NEVER:
- Owns runtime state
- Performs business logic
- Mutates message payloads

Messages are immutable requests transported across the system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from enum import Enum, auto
import threading
import time
import uuid

from .model import (
    MessageId,
    CorrelationId,
    CausationId,
    RuntimeId,
    PriorityLevel,
    priority_value,
)
from .envelope import MessageEnvelope, DeliveryReport, Acknowledgement


# =============================================================================
# ROUTING TYPES
# =============================================================================

class RoutingMode(Enum):
    """Message routing modes."""
    DIRECT = "direct"        # Send to specific destination
    TOPIC = "topic"          # Publish to topic subscribers
    BROADCAST = "broadcast"  # Send to all registered subscribers
    MULTICAST = "multicast"  # Send to a group of destinations


class RouteResult(Enum):
    """Routing outcome."""
    RESOLVED = "resolved"     # Destination(s) found
    NO_DESTINATION = "no_destination"  # No matching subscriber
    PENDING = "pending"       # Deferred routing (queue, schedule)
    REJECTED = "rejected"     # Routing rejected by policy


# =============================================================================
# ROUTING POLICY
# =============================================================================

@dataclass(frozen=True)
class RoutingPolicy:
    """
    Immutable routing configuration for a message.
    
    Defines how a message should be routed through the system.
    """
    
    mode: RoutingMode = RoutingMode.DIRECT
    destination_id: Optional[str] = None  # For DIRECT mode
    topic: Optional[str] = None           # For TOPIC mode
    multicast_targets: List[str] = field(default_factory=list)  # For MULTICAST
    broadcast: bool = False               # True = BROADCAST
    
    priority: PriorityLevel = PriorityLevel.NORMAL
    
    # Delivery options
    reliable: bool = False     # Ensure delivery (retry, DLQ)
    queued: bool = False       # Queue for later delivery
    immediate: bool = False    # Try immediate delivery first
    
    # Time constraints
    expires_at_utc: Optional[float] = None  # When message expires
    max_delivery_attempts: int = 3          # Retry limit


# =============================================================================
# ROUTE TABLE (mapping topics to subscribers)
# =============================================================================

class RouteTable:
    """
    Thread-safe mapping of topics and destinations to subscriber lists.
    
    Used for determining where messages should be routed.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # topic -> set of subscriber_ids
        self._topic_routes: Dict[str, Set[str]] = {}
        
        # destination_id -> set of subscribers interested
        self._direct_routes: Dict[str, Set[str]] = {}
        
        # subscriber_id -> list of topics they subscribe to
        self._subscriber_topics: Dict[str, List[str]] = {}
    
    def register_topic(self, topic: str, subscriber_id: str) -> None:
        """Register a subscriber for a topic."""
        with self._lock:
            if topic not in self._topic_routes:
                self._topic_routes[topic] = set()
            self._topic_routes[topic].add(subscriber_id)
            
            if subscriber_id not in self._subscriber_topics:
                self._subscriber_topics[subscriber_id] = []
            if topic not in self._subscriber_topics[subscriber_id]:
                self._subscriber_topics[subscriber_id].append(topic)
    
    def unregister_topic(self, topic: str, subscriber_id: str) -> bool:
        """Unregister a subscriber from a topic."""
        with self._lock:
            if topic not in self._topic_routes:
                return False
            
            self._topic_routes[topic].discard(subscriber_id)
            
            if not self._topic_routes[topic]:
                del self._topic_routes[topic]
            
            if subscriber_id in self._subscriber_topics:
                try:
                    self._subscriber_topics[subscriber_id].remove(topic)
                    if not self._subscriber_topics[subscriber_id]:
                        del self._subscriber_topics[subscriber_id]
                except ValueError:
                    pass
            
            return True
    
    def register_destination(self, destination_id: str, subscriber_id: str) -> None:
        """Register a direct route from destination to subscriber."""
        with self._lock:
            if destination_id not in self._direct_routes:
                self._direct_routes[destination_id] = set()
            self._direct_routes[destination_id].add(subscriber_id)
    
    def unregister_destination(self, destination_id: str, subscriber_id: str) -> bool:
        """Unregister a direct route."""
        with self._lock:
            if destination_id not in self._direct_routes:
                return False
            
            self._direct_routes[destination_id].discard(subscriber_id)
            
            if not self._direct_routes[destination_id]:
                del self._direct_routes[destination_id]
            
            return True
    
    def get_topic_subscribers(self, topic: str) -> List[str]:
        """Get subscribers for a topic."""
        with self._lock:
            return list(self._topic_routes.get(topic, set()))
    
    def get_destination_subscribers(self, destination_id: str) -> List[str]:
        """Get subscribers for a direct route."""
        with self._lock:
            return list(self._direct_routes.get(destination_id, set()))
    
    def get_all_subscribers(self) -> Set[str]:
        """Get all registered subscribers."""
        with self._lock:
            result = set()
            result.update(*self._topic_routes.values())
            result.update(*self._direct_routes.values())
            return result
    
    def get_statistics(self) -> Dict[str, int]:
        """Get route table statistics."""
        with self._lock:
            return {
                "topics_count": len(self._topic_routes),
                "destinations_count": len(self._direct_routes),
                "total_subscribers": len(self.get_all_subscribers()),
            }


# =============================================================================
# MESSAGE PRIORITY QUEUE
# =============================================================================

class MessageQueue:
    """
    Priority queue for messages.
    
    Supports bounded capacity, overflow policies, and priority ordering.
    """
    
    def __init__(self, max_size: int = 1000):
        self._max_size = max_size
        self._lock = threading.RLock()
        
        # List of (priority, timestamp, envelope) tuples, sorted by priority then time
        self._queue: List[Tuple[int, float, MessageEnvelope]] = []
    
    def enqueue(self, envelope: MessageEnvelope) -> bool:
        """
        Add a message to the queue.
        
        Args:
            envelope: The message envelope to add
            
        Returns:
            True if added, False if rejected (queue full)
        """
        priority = priority_value(envelope.priority)
        timestamp = time.monotonic()
        
        with self._lock:
            if len(self._queue) >= self._max_size:
                return False  # Reject - queue is full
            
            self._queue.append((priority, timestamp, envelope))
            
            # Maintain sorted order (lowest priority value first)
            self._queue.sort(key=lambda x: (x[0], x[1]))
            
            return True
    
    def dequeue(self) -> Optional[MessageEnvelope]:
        """Remove and return the highest priority message."""
        with self._lock:
            if not self._queue:
                return None
            
            _, _, envelope = self._queue.pop(0)
            return envelope
    
    def peek(self) -> Optional[MessageEnvelope]:
        """Return highest priority message without removing it."""
        with self._lock:
            if not self._queue:
                return None
            return self._queue[0][2]
    
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
            priorities = {}
            for p, _, _ in self._queue:
                priorities[p] = priorities.get(p, 0) + 1
            
            return {
                "size": len(self._queue),
                "max_size": self._max_size,
                "priority_distribution": priorities,
            }


# =============================================================================
# CANONICAL MESSAGE ROUTER
# =============================================================================

class MessageRouterConfig:
    """Configuration for MessageRouter."""
    
    def __init__(
        self,
        runtime_id: str = "default",
        default_queue_size: int = 1000,
    ):
        self.runtime_id = runtime_id
        self.default_queue_size = default_queue_size


class MessageRouter:
    """
    Canonical MessageRouter for the runtime.
    
    This is THE ONE authority for message routing in this runtime instance.
    All messages pass through here to determine their delivery path.
    
    Invariants maintained:
        1. Exactly one MessageRouter per runtime (enforced by caller)
        2. Messages are immutable (enforced by type system)
        3. Routing is deterministic (same input = same output)
        4. No direct state mutation (only coordination)
    """
    
    def __init__(self, config: Optional[MessageRouterConfig] = None):
        self._config = config or MessageRouterConfig()
        
        self._lock = threading.RLock()
        
        # Routing infrastructure
        self._route_table = RouteTable()
        self._queues: Dict[str, MessageQueue] = {}  # subscriber_id -> queue
        
        # Statistics
        self._route_count = 0
        self._enqueue_count = 0
        self._dequeue_count = 0
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this router serves."""
        return self._config.runtime_id
    
    # -------------------------------------------------------------------------
    # ROUTING API
    # -------------------------------------------------------------------------
    
    def route(
        self,
        envelope: MessageEnvelope,
        policy: Optional[RoutingPolicy] = None,
    ) -> Tuple[RouteResult, List[str]]:
        """
        Route a message to its destination(s).
        
        Args:
            envelope: The message envelope to route
            policy: Optional routing overrides
            
        Returns:
            Tuple of (result, target_subscribers)
        """
        with self._lock:
            self._route_count += 1
        
        # Apply default policy if not provided
        actual_policy = policy or RoutingPolicy()
        
        # Check expiration first
        if envelope.is_expired():
            return (RouteResult.REJECTED, [])
        
        # Determine target subscribers based on mode
        targets: List[str] = []
        
        if actual_policy.mode == RoutingMode.DIRECT:
            # Direct to specific destination
            dest = actual_policy.destination_id or envelope.destination_id
            if dest:
                targets = self._route_table.get_destination_subscribers(dest)
                if not targets:
                    return (RouteResult.NO_DESTINATION, [])
            
        elif actual_policy.mode == RoutingMode.TOPIC:
            # Publish to topic subscribers
            topic = actual_policy.topic or envelope.payload.get("_topic")
            if topic:
                targets = self._route_table.get_topic_subscribers(topic)
                if not targets:
                    return (RouteResult.NO_DESTINATION, [])
        
        elif actual_policy.mode == RoutingMode.MULTICAST:
            # Send to specific group of subscribers
            targets = list(actual_policy.multicast_targets or [])
            if not targets:
                return (RouteResult.REJECTED, [])
        
        elif actual_policy.mode == RoutingMode.BROADCAST:
            # Send to all registered subscribers
            targets = list(self._route_table.get_all_subscribers())
            if not targets:
                return (RouteResult.NO_DESTINATION, [])
        
        else:
            return (RouteResult.REJECTED, [])
        
        # If queued mode, enqueue for later delivery
        if actual_policy.queued or envelope.payload.get("_queued"):
            success = self._enqueue(envelope, actual_policy)
            if not success:
                return (RouteResult.REJECTED, [])
            
            with self._lock:
                self._enqueue_count += 1
            
            return (RouteResult.PENDING, targets)
        
        # Direct delivery (immediate or reliable)
        with self._lock:
            self._dequeue_count += len(targets)
        
        return (RouteResult.RESOLVED, targets)
    
    def _enqueue(self, envelope: MessageEnvelope, policy: RoutingPolicy) -> bool:
        """Enqueue a message for later delivery."""
        # Get or create queue for target subscribers
        targets = policy.multicast_targets or [policy.destination_id] if policy.destination_id else []
        
        if not targets:
            return False
        
        # For now, use first target's queue
        queue_key = targets[0]
        
        with self._lock:
            if queue_key not in self._queues:
                self._queues[queue_key] = MessageQueue(self._config.default_queue_size)
            
            return self._queues[queue_key].enqueue(envelope)
    
    def dequeue(self, subscriber_id: str) -> Optional[MessageEnvelope]:
        """Dequeue the next message for a subscriber."""
        with self._lock:
            queue = self._queues.get(subscriber_id)
            if queue and not queue.is_empty():
                envelope = queue.dequeue()
                self._dequeue_count += 1
                return envelope
        return None
    
    # -------------------------------------------------------------------------
    # SUBSCRIPTION API (topic-based routing)
    # -------------------------------------------------------------------------
    
    def subscribe(self, topic: str, subscriber_id: str) -> bool:
        """Subscribe to a topic."""
        with self._lock:
            self._route_table.register_topic(topic, subscriber_id)
            return True
    
    def unsubscribe(self, topic: str, subscriber_id: str) -> bool:
        """Unsubscribe from a topic."""
        with self._lock:
            return self._route_table.unregister_topic(topic, subscriber_id)
    
    def register_destination(
        self,
        destination_id: str,
        subscriber_id: str,
    ) -> bool:
        """Register a direct route."""
        with self._lock:
            self._route_table.register_destination(destination_id, subscriber_id)
            return True
    
    def unregister_destination(
        self,
        destination_id: str,
        subscriber_id: str,
    ) -> bool:
        """Unregister a direct route."""
        with self._lock:
            return self._route_table.unregister_destination(destination_id, subscriber_id)
    
    # -------------------------------------------------------------------------
    # DIAGNOSTICS API
    # -------------------------------------------------------------------------
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get router statistics."""
        with self._lock:
            queue_stats = {}
            for key, q in self._queues.items():
                queue_stats[key] = q.get_statistics()
            
            return {
                **self._route_table.get_statistics(),
                "route_count": self._route_count,
                "enqueue_count": self._enqueue_count,
                "dequeue_count": self._dequeue_count,
                "queue_sizes": {k: q.size() for k, q in self._queues.items()},
                "queue_stats": queue_stats,
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get router health status."""
        stats = self.get_statistics()
        
        # Check for any queues at capacity
        overflow_queues = [
            k for k, v in stats.get("queue_sizes", {}).items() 
            if v >= self._config.default_queue_size
        ]
        
        return {
            "status": "healthy" if not overflow_queues else "degraded",
            "overflow_queues": overflow_queues,
            **stats,
        }


__all__ = [
    # Routing modes and result types
    "RoutingMode",
    "RouteResult",
    
    # Policy
    "RoutingPolicy",
    
    # Infrastructure
    "RouteTable",
    "MessageQueue",
    
    # Core authority
    "MessageRouterConfig",
    "MessageRouter",
]