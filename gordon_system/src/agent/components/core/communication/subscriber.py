# Core Subscriber Registry
# ========================

"""
Subscriber registry with policies and lifecycle management.

Provides:
- Explicit registration (no implicit subscriptions from imports)
- Subscription descriptors with filtering
- Priority-based delivery ordering
- Lifecycle ownership tracking
- Bounded subscriptions per runtime
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum, auto
import threading
import time


# =============================================================================
# SUBSCRIPTION POLICIES
# =============================================================================

class SubscriptionPolicy(Enum):
    """Policies for subscription behavior."""
    ACCEPT_ALL = "accept_all"         # Accept all messages when queue is full
    REJECT_NEW = "reject_new"         # Reject new messages, drop oldest
    DROP_OLDEST = "drop_oldest"       # Evict oldest to make room
    PRIORITY_ONLY = "priority_only"   # Only accept high-priority messages


@dataclass(frozen=True)
class SubscriptionPolicyConfig:
    """Immutable configuration for subscription policy."""
    
    max_queue_size: int = 1000
    overflow_policy: SubscriptionPolicy = SubscriptionPolicy.REJECT_NEW
    
    # Priority handling
    min_priority: int = 0              # Minimum priority accepted
    max_priority: int = 100            # Maximum priority accepted
    
    # Lifecycle
    auto_acknowledge: bool = True      # Auto-ACK after delivery
    requires_confirmation: bool = False  # Wait for ACK before removing


# =============================================================================
# SUBSCRIPTION DESCRIPTOR
# =============================================================================

@dataclass(frozen=True)
class SubscriptionDescriptor:
    """
    Immutable descriptor for a subscription.
    
    Created at registration time, never modified. For updates,
    unregister and re-register with new configuration.
    """
    
    subscription_id: str
    subscriber_id: str
    
    # Filter criteria (all must match - AND semantics)
    event_types: Tuple[str, ...] = field(default_factory=tuple)
    topics: Tuple[str, ...] = field(default_factory=tuple)
    runtime_ids: Tuple[str, ...] = field(default_factory=tuple)
    
    # Delivery configuration
    priority: int = 0                  # Lower = higher delivery priority
    delivery_mode: str = "synchronous"  # sync, async, queued
    
    # Queue settings
    max_queue_size: int = 1000
    overflow_policy: SubscriptionPolicy = SubscriptionPolicy.REJECT_NEW
    
    # Lifecycle tracking
    registered_at_utc: float = field(default_factory=time.time)
    last_modified_utc: Optional[float] = None
    
    # Statistics (updated at delivery time)
    delivered_count: int = 0
    rejected_count: int = 0
    failed_count: int = 0
    
    def with_priority(self, priority: int) -> "SubscriptionDescriptor":
        """Return copy with updated priority."""
        return SubscriptionDescriptor(
            subscription_id=self.subscription_id,
            subscriber_id=self.subscriber_id,
            event_types=self.event_types,
            topics=self.topics,
            runtime_ids=self.runtime_ids,
            priority=priority,
            delivery_mode=self.delivery_mode,
            max_queue_size=self.max_queue_size,
            overflow_policy=self.overflow_policy,
            registered_at_utc=self.registered_at_utc,
            last_modified_utc=time.time() if self.last_modified_utc else None,
            delivered_count=self.delivered_count,
            rejected_count=self.rejected_count,
            failed_count=self.failed_count,
        )
    
    def with_max_queue_size(self, size: int) -> "SubscriptionDescriptor":
        """Return copy with updated queue size."""
        return SubscriptionDescriptor(
            subscription_id=self.subscription_id,
            subscriber_id=self.subscriber_id,
            event_types=self.event_types,
            topics=self.topics,
            runtime_ids=self.runtime_ids,
            priority=self.priority,
            delivery_mode=self.delivery_mode,
            max_queue_size=size,
            overflow_policy=self.overflow_policy,
            registered_at_utc=self.registered_at_utc,
            last_modified_utc=time.time() if self.last_modified_utc else None,
            delivered_count=self.delivered_count,
            rejected_count=self.rejected_count,
            failed_count=self.failed_count,
        )


# =============================================================================
# SUBSCRIPTION SNAPSHOT
# =============================================================================

@dataclass(frozen=True)
class SubscriptionSnapshot:
    """
    Immutable snapshot of subscription state at a point in time.
    
    Used for observability and debugging without exposing mutable internals.
    """
    
    subscription_id: str
    subscriber_id: str
    
    event_types: List[str]
    topics: List[str]
    runtime_ids: List[str]
    
    priority: int
    delivery_mode: str
    
    queue_depth: int
    delivered_count: int
    rejected_count: int
    
    registered_at_utc: float
    last_delivery_utc: Optional[float]


# =============================================================================
# SUBSCRIBER REGISTRY
# =============================================================================

class SubscriberRegistry:
    """
    Thread-safe registry for managing subscriptions.
    
    Invariants maintained:
        1. Explicit registration required (no implicit subscriptions)
        2. Subscriptions are immutable descriptors
        3. No import-time subscription behavior
        4. Bounded subscriptions per runtime
    """
    
    def __init__(
        self,
        max_subscribers_per_runtime: int = 1000,
        max_total_subscriptions: int = 10000,
    ):
        self._max_per_runtime = max_subscribers_per_runtime
        self._max_total_subs = max_total_subscriptions
        
        self._lock = threading.RLock()
        
        # subscription_id -> descriptor
        self._subscriptions: Dict[str, SubscriptionDescriptor] = {}
        
        # subscriber_id -> list of subscription_ids
        self._subscriber_index: Dict[str, List[str]] = {}
        
        # event_type -> set of subscription_ids
        self._event_type_index: Dict[str, Set[str]] = {}
        
        # topic -> set of subscription_ids
        self._topic_index: Dict[str, Set[str]] = {}
    
    def register(
        self,
        subscriber_id: str,
        event_types: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        runtime_ids: Optional[List[str]] = None,
        priority: int = 0,
        max_queue_size: int = 1000,
    ) -> Tuple[bool, str]:
        """
        Register a new subscription.
        
        Args:
            subscriber_id: Who is subscribing
            event_types: Event types to receive (empty = all)
            topics: Topics to subscribe to (empty = no filtering)
            runtime_ids: Runtime IDs to filter by (empty = all)
            priority: Delivery priority (lower = higher)
            max_queue_size: Queue capacity
            
        Returns:
            Tuple of (success, subscription_id)
        """
        with self._lock:
            # Check limits
            if len(self._subscriptions) >= self._max_total_subs:
                return False, "max_subscriptions_reached"
            
            subscriber_count = len([
                sid for sid in self._subscriber_index.keys()
                if sid == subscriber_id
            ])
            
            if subscriber_count >= self._max_per_runtime:
                return False, "max_subscribers_exceeded"
            
            # Generate subscription ID
            sub_id = f"sub_{subscriber_id}_{len(self._subscriptions)}"
            
            descriptor = SubscriptionDescriptor(
                subscription_id=sub_id,
                subscriber_id=subscriber_id,
                event_types=tuple(event_types or []),
                topics=tuple(topics or []),
                runtime_ids=tuple(runtime_ids or []),
                priority=priority,
                max_queue_size=max_queue_size,
            )
            
            # Add to storage
            self._subscriptions[sub_id] = descriptor
            
            if subscriber_id not in self._subscriber_index:
                self._subscriber_index[subscriber_id] = []
            self._subscriber_index[subscriber_id].append(sub_id)
            
            # Update indexes
            for et in event_types or []:
                if et not in self._event_type_index:
                    self._event_type_index[et] = set()
                self._event_type_index[et].add(sub_id)
            
            for t in topics or []:
                if t not in self._topic_index:
                    self._topic_index[t] = set()
                self._topic_index[t].add(sub_id)
            
            return True, sub_id
    
    def unregister(self, subscription_id: str) -> bool:
        """Remove a subscription by ID."""
        with self._lock:
            if subscription_id not in self._subscriptions:
                return False
            
            descriptor = self._subscriptions[subscription_id]
            
            # Remove from storage
            del self._subscriptions[subscription_id]
            
            # Update subscriber index
            sub_list = self._subscriber_index.get(descriptor.subscriber_id, [])
            if subscription_id in sub_list:
                sub_list.remove(subscription_id)
                if not sub_list:
                    del self._subscriber_index[descriptor.subscriber_id]
            
            # Remove from indexes
            for et in descriptor.event_types:
                if et in self._event_type_index:
                    self._event_type_index[et].discard(subscription_id)
                    if not self._event_type_index[et]:
                        del self._event_type_index[et]
            
            for t in descriptor.topics:
                if t in self._topic_index:
                    self._topic_index[t].discard(subscription_id)
                    if not self._topic_index[t]:
                        del self._topic_index[t]
            
            return True
    
    def get_subscriptions_for_event(
        self,
        event_type: str,
        runtime_id: Optional[str] = None,
    ) -> List[SubscriptionDescriptor]:
        """Get subscriptions that would receive a specific event."""
        with self._lock:
            # Get candidates from event type index
            candidate_ids = self._event_type_index.get(event_type, set())
            
            result = []
            
            for sub_id in candidate_ids:
                desc = self._subscriptions.get(sub_id)
                
                if not desc:
                    continue
                
                # Check runtime filter
                if runtime_id and desc.runtime_ids:
                    if runtime_id not in desc.runtime_ids:
                        continue
                
                result.append(desc)
            
            return result
    
    def get_subscriptions_for_subscriber(
        self,
        subscriber_id: str,
    ) -> List[SubscriptionDescriptor]:
        """Get all subscriptions for a specific subscriber."""
        with self._lock:
            sub_ids = self._subscriber_index.get(subscriber_id, [])
            return [
                self._subscriptions[sub_id]
                for sub_id in sub_ids
                if sub_id in self._subscriptions
            ]
    
    def update_stats(
        self,
        subscription_id: str,
        delivered: int = 0,
        rejected: int = 0,
        failed: int = 0,
    ) -> Optional[SubscriptionDescriptor]:
        """Update delivery statistics for a subscription."""
        with self._lock:
            if subscription_id not in self._subscriptions:
                return None
            
            desc = self._subscriptions[subscription_id]
            
            new_desc = SubscriptionDescriptor(
                subscription_id=desc.subscription_id,
                subscriber_id=desc.subscriber_id,
                event_types=desc.event_types,
                topics=desc.topics,
                runtime_ids=desc.runtime_ids,
                priority=desc.priority,
                delivery_mode=desc.delivery_mode,
                max_queue_size=desc.max_queue_size,
                overflow_policy=desc.overflow_policy,
                registered_at_utc=desc.registered_at_utc,
                last_modified_utc=time.time(),
                delivered_count=desc.delivered_count + delivered,
                rejected_count=desc.rejected_count + rejected,
                failed_count=desc.failed_count + failed,
            )
            
            self._subscriptions[subscription_id] = new_desc
            
            return new_desc
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with self._lock:
            return {
                "total_subscriptions": len(self._subscriptions),
                "subscriber_count": len(self._subscriber_index),
                "event_type_index_size": len(self._event_type_index),
                "topic_index_size": len(self._topic_index),
            }
    
    def get_snapshot(
        self,
        subscriber_id: Optional[str] = None,
    ) -> List[SubscriptionSnapshot]:
        """Get snapshot of all subscriptions."""
        with self._lock:
            result = []
            
            for sub_id, desc in self._subscriptions.items():
                if subscriber_id and desc.subscriber_id != subscriber_id:
                    continue
                
                # Calculate queue depth (not tracked here - would need runtime)
                result.append(SubscriptionSnapshot(
                    subscription_id=desc.subscription_id,
                    subscriber_id=desc.subscriber_id,
                    event_types=list(desc.event_types),
                    topics=list(desc.topics),
                    runtime_ids=list(desc.runtime_ids),
                    priority=desc.priority,
                    delivery_mode=desc.delivery_mode,
                    queue_depth=0,  # Not tracked in registry
                    delivered_count=desc.delivered_count,
                    rejected_count=desc.rejected_count,
                    registered_at_utc=desc.registered_at_utc,
                    last_delivery_utc=None,
                ))
            
            return result


# =============================================================================
# SUBSCRIBER LIFECYCLE MANAGER
# =============================================================================

class SubscriberLifecycleManager:
    """
    Manages subscriber lifecycle with explicit ownership.
    
    Subscribers are explicitly registered and can be cleanly stopped.
    """
    
    def __init__(self, registry: SubscriberRegistry):
        self._registry = registry
        self._lock = threading.RLock()
        
        # Track running subscribers
        self._active_subscribers: Set[str] = set()
        self._stopped_subscribers: Set[str] = set()
    
    def activate(self, subscriber_id: str) -> bool:
        """Activate a subscriber for receiving messages."""
        with self._lock:
            if subscriber_id in self._active_subscribers:
                return True  # Already active
            
            if subscriber_id in self._stopped_subscribers:
                return False  # Permanently stopped
            
            self._active_subscribers.add(subscriber_id)
            
            # Get subscriptions and update stats
            for sub_desc in self._registry.get_subscriptions_for_subscriber(subscriber_id):
                self._registry.update_stats(
                    sub_desc.subscription_id,
                    delivered=0,  # Just activated
                )
            
            return True
    
    def deactivate(self, subscriber_id: str) -> bool:
        """Deactivate a subscriber (stop receiving messages)."""
        with self._lock:
            if subscriber_id not in self._active_subscribers:
                return False
            
            self._active_subscribers.discard(subscriber_id)
            self._stopped_subscribers.add(subscriber_id)
            
            # Final stats update
            for sub_desc in self._registry.get_subscriptions_for_subscriber(subscriber_id):
                self._registry.update_stats(
                    sub_desc.subscription_id,
                    delivered=0,  # Deactivated
                )
            
            return True
    
    def is_active(self, subscriber_id: str) -> bool:
        """Check if a subscriber is active."""
        with self._lock:
            return subscriber_id in self._active_subscribers
    
    def get_active_count(self) -> int:
        """Get count of active subscribers."""
        with self._lock:
            return len(self._active_subscribers)
    
    def get_all_active(self) -> List[str]:
        """Get all active subscriber IDs."""
        with self._lock:
            return list(self._active_subscribers)


__all__ = [
    # Policy types
    "SubscriptionPolicy",
    "SubscriptionPolicyConfig",
    
    # Descriptor type
    "SubscriptionDescriptor",
    
    # Snapshot type
    "SubscriptionSnapshot",
    
    # Registry
    "SubscriberRegistry",
    
    # Lifecycle
    "SubscriberLifecycleManager",
]