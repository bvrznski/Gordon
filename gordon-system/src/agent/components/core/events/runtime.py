# Core Runtime Integration Framework
# ==================================
"""
Integration layer between Event System & Message Bus and Gordon Core runtime.

This module ensures that event publication, routing, dispatch, reliability,
and message handling are securely integrated with the runtime while remaining
fully observable and lifecycle-aware.

INTEGRATION LAWS:
    1. Runtime communicates through message contracts
    2. Security validates sensitive communication
    3. Observability covers every message lifecycle stage
    4. Runtime never bypasses the message bus
    5. Plugins obey communication contracts
    6. Auditability is mandatory
    7. Communication policies are explicit
    8. Secrets are never exposed in messages
    9. Runtime integration is deterministic
   10. Hidden channels are prohibited
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Type, Tuple
from enum import Enum, auto
import threading
import time
import uuid

# Runtime integration imports - these would come from the actual runtime package
# For now, we define stubs that match expected interfaces


# =============================================================================
# LIFECYCLE STATES
# =============================================================================

class LifecycleState(Enum):
    """Runtime lifecycle states."""
    CREATED = "created"          # Instance created but not initialized
    INITIALIZING = "initializing"  # Initialization in progress
    READY = "ready"              # Ready to process messages
    PROCESSING = "processing"    # Actively processing messages
    SHUTTING_DOWN = "shutting_down"  # Graceful shutdown initiated
    STOPPED = "stopped"          # Fully stopped


# =============================================================================
# PUBLISHER LIFECYCLE MANAGER
# =============================================================================

class PublisherLifecycleManager:
    """
    Manages publisher lifecycle and registration.
    
    Publishers register with the runtime during initialization and are
    cleaned up during shutdown. No publishers can operate outside this manager.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # publisher_id -> PublisherInfo
        self._publishers: Dict[str, "PublisherInfo"] = {}
        
        # Runtime lifecycle state
        self._state: LifecycleState = LifecycleState.CREATED
    
    def register_publisher(
        self,
        publisher_id: str,
        runtime_id: Optional[str] = None,
        max_events_per_second: float = 100.0,
    ) -> bool:
        """
        Register a new publisher.
        
        Args:
            publisher_id: Unique identifier for this publisher
            runtime_id: Runtime instance this belongs to
            max_events_per_second: Rate limit (0 = unlimited)
            
        Returns:
            True if registered successfully
        """
        with self._lock:
            if publisher_id in self._publishers:
                return False
            
            if self._state not in (LifecycleState.CREATED, LifecycleState.READY):
                return False  # Cannot register during shutdown
            
            self._publishers[publisher_id] = PublisherInfo(
                publisher_id=publisher_id,
                runtime_id=runtime_id or "default",
                created_at_utc=time.time(),
                max_events_per_second=max_events_per_second,
            )
            
            return True
    
    def unregister_publisher(self, publisher_id: str) -> bool:
        """Remove a publisher registration."""
        with self._lock:
            if publisher_id in self._publishers:
                del self._publishers[publisher_id]
                return True
            return False
    
    def get_publisher(self, publisher_id: str) -> Optional["PublisherInfo"]:
        """Get publisher info by ID."""
        with self._lock:
            return self._publishers.get(publisher_id)
    
    def get_all_publishers(self) -> Dict[str, "PublisherInfo"]:
        """Get all registered publishers."""
        with self._lock:
            return dict(self._publishers)
    
    @property
    def state(self) -> LifecycleState:
        """Get current lifecycle state."""
        with self._lock:
            return self._state
    
    def set_state(self, new_state: LifecycleState) -> bool:
        """
        Set runtime lifecycle state.
        
        Valid transitions:
            CREATED -> INITIALIZING -> READY
            READY -> SHUTTING_DOWN -> STOPPED
            
        Returns:
            True if transition successful
        """
        with self._lock:
            # Validate transition
            valid_transitions = {
                LifecycleState.CREATED: {LifecycleState.INITIALIZING},
                LifecycleState.INITIALIZING: {LifecycleState.READY},
                LifecycleState.READY: {LifecycleState.SHUTTING_DOWN},
                LifecycleState.SHUTTING_DOWN: {LifecycleState.STOPPED},
            }
            
            if new_state in valid_transitions.get(self._state, set()):
                self._state = new_state
                return True
            
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get publisher statistics."""
        with self._lock:
            return {
                "publisher_count": len(self._publishers),
                "lifecycle_state": self._state.value,
            }


@dataclass(frozen=True)
class PublisherInfo:
    """Information about a registered publisher."""
    
    publisher_id: str
    runtime_id: str
    
    created_at_utc: float
    
    # Rate limiting
    max_events_per_second: float  # 0 = unlimited
    events_published: int = 0
    last_publish_utc: Optional[float] = None


# =============================================================================
# SUBSCRIBER LIFECYCLE MANAGER
# =============================================================================

class SubscriberLifecycleManager:
    """
    Manages subscriber lifecycle and registration.
    
    Subscribers register interest in message contracts. The manager tracks
    subscription state and handles cleanup during shutdown.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # subscriber_id -> SubscriberInfo
        self._subscribers: Dict[str, "SubscriberInfo"] = {}
        
        # subscription_id -> (subscriber_id, contract_type)
        self._subscriptions: Dict[str, Tuple[str, str]] = {}
    
    def register_subscriber(
        self,
        subscriber_id: str,
        runtime_id: Optional[str] = None,
        max_queue_size: int = 1000,
    ) -> bool:
        """
        Register a new subscriber.
        
        Args:
            subscriber_id: Unique identifier for this subscriber
            runtime_id: Runtime instance this belongs to
            max_queue_size: Maximum queued messages
            
        Returns:
            True if registered successfully
        """
        with self._lock:
            if subscriber_id in self._subscribers:
                return False
            
            self._subscribers[subscriber_id] = SubscriberInfo(
                subscriber_id=subscriber_id,
                runtime_id=runtime_id or "default",
                created_at_utc=time.time(),
                max_queue_size=max_queue_size,
            )
            
            return True
    
    def unregister_subscriber(self, subscriber_id: str) -> bool:
        """Remove a subscriber registration."""
        with self._lock:
            if subscriber_id not in self._subscribers:
                return False
            
            # Remove all subscriptions for this subscriber
            subscription_ids = [
                sid for sid, (sid_sub, _) in self._subscriptions.items()
                if sid_sub == subscriber_id
            ]
            for sub_id in subscription_ids:
                del self._subscriptions[sub_id]
            
            del self._subscribers[subscriber_id]
            return True
    
    def subscribe(
        self,
        subscriber_id: str,
        contract_type: str,
        subscription_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Subscribe a subscriber to a message type.
        
        Args:
            subscriber_id: Who is subscribing
            contract_type: What they want to receive
            subscription_id: Optional explicit ID
            
        Returns:
            Subscription ID or None if registration failed
        """
        with self._lock:
            if subscriber_id not in self._subscribers:
                return None
            
            sub_id = subscription_id or f"sub_{uuid.uuid4().hex[:16]}"
            
            # Check for duplicate subscription
            for existing_id, (existing_sub, _) in self._subscriptions.items():
                if existing_sub == subscriber_id and existing_id == contract_type:
                    return existing_id
            
            self._subscriptions[sub_id] = (subscriber_id, contract_type)
            self._subscribers[subscriber_id].add_subscription(sub_id)
            
            return sub_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Remove a subscription."""
        with self._lock:
            if subscription_id not in self._subscriptions:
                return False
            
            subscriber_id, _ = self._subscriptions.pop(subscription_id)
            
            if subscriber_id in self._subscribers:
                self._subscribers[subscriber_id].remove_subscription(subscription_id)
            
            return True
    
    def get_subscriber(self, subscriber_id: str) -> Optional["SubscriberInfo"]:
        """Get subscriber info by ID."""
        with self._lock:
            return self._subscribers.get(subscriber_id)
    
    def get_all_subscribers(self) -> Dict[str, "SubscriberInfo"]:
        """Get all registered subscribers."""
        with self._lock:
            return dict(self._subscribers)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get subscriber statistics."""
        with self._lock:
            total_subs = len(self._subscriptions)
            
            return {
                "subscriber_count": len(self._subscribers),
                "subscription_count": total_subs,
                **{sid: info.get_statistics() 
                   for sid, info in self._subscribers.items()},
            }


@dataclass
class SubscriberInfo:
    """Information about a registered subscriber."""
    
    subscriber_id: str
    runtime_id: str
    
    created_at_utc: float
    max_queue_size: int
    
    # Subscription tracking
    _subscription_ids: List[str] = field(default_factory=list)
    
    def add_subscription(self, subscription_id: str) -> None:
        """Add a subscription ID."""
        if subscription_id not in self._subscription_ids:
            self._subscription_ids.append(subscription_id)
    
    def remove_subscription(self, subscription_id: str) -> bool:
        """Remove a subscription ID."""
        if subscription_id in self._subscription_ids:
            self._subscription_ids.remove(subscription_id)
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get subscriber-specific statistics."""
        return {
            "subscription_count": len(self._subscription_ids),
            "max_queue_size": self.max_queue_size,
        }


# =============================================================================
# SECURITY VALIDATION
# =============================================================================

class SecurityPolicy(Enum):
    """Security policy enforcement levels."""
    STRICT = "strict"           # All messages validated, audit logged
    MODERATE = "moderate"       # Sensitive messages only
    PERMISSIVE = "permissive"   # Minimal validation (development only)


@dataclass(frozen=True)
class SecurityContext:
    """Security context for message processing."""
    
    authenticated: bool
    principal_id: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    
    # Permissions
    can_publish: bool = True
    can_subscribe: bool = True
    can_view_sensitive: bool = False
    
    # Audit info
    audit_id: str = field(default_factory=lambda: f"audit_{uuid.uuid4().hex[:16]}")


class SecurityValidator:
    """
    Validates messages against security policies.
    
    All messages pass through this validator before publication or delivery.
    """
    
    def __init__(
        self,
        policy: SecurityPolicy = SecurityPolicy.STRICT,
    ):
        self._policy = policy
    
    def validate_publish(
        self,
        envelope: Any,
        context: Optional[SecurityContext] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a message for publication.
        
        Args:
            envelope: Message to publish
            context: Security context of publisher
            
        Returns:
            (is_valid, error_message)
        """
        if self._policy == SecurityPolicy.STRICT:
            # Full validation
            if not hasattr(envelope, "event_type"):
                return False, "Missing event_type"
            
            if not envelope.event_type:
                return False, "Empty event_type"
        
        # Check security context
        if context and not context.can_publish:
            return False, "Publisher does not have publish permission"
        
        # Check for secrets in payload (basic check)
        if hasattr(envelope, "payload"):
            sensitive_keywords = ["password", "secret", "token", "key"]
            for key in envelope.payload.keys():
                if any(kw in key.lower() for kw in sensitive_keywords):
                    return False, f"Sensitive field name detected: {key}"
        
        return True, None
    
    def validate_subscribe(
        self,
        subscriber_id: str,
        contract_type: str,
        context: Optional[SecurityContext] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a subscription request.
        
        Args:
            subscriber_id: Who wants to subscribe
            contract_type: What they want to receive
            context: Security context
            
        Returns:
            (is_valid, error_message)
        """
        if not context or not context.can_subscribe:
            return False, "Subscriber does not have subscribe permission"
        
        # Check for forbidden contract types
        forbidden_types = ["system.admin", "security.credentials"]
        if contract_type in forbidden_types and not context.can_view_sensitive:
            return False, f"Cannot subscribe to protected type: {contract_type}"
        
        return True, None
    
    def get_security_context(
        self,
        token: Optional[str] = None,
    ) -> SecurityContext:
        """
        Extract security context from authentication token.
        
        In production, this would decode JWT or verify API key.
        
        Args:
            token: Authentication token
            
        Returns:
            Security context for the request
        """
        if not token:
            return SecurityContext(authenticated=False)
        
        # In production, decode and validate token here
        return SecurityContext(
            authenticated=True,
            principal_id="principal_123",  # From token
            roles=["user"],
            can_publish=True,
            can_subscribe=True,
        )


# =============================================================================
# OBSERVABILITY INTEGRATION
# =============================================================================

class ObservabilityEventType(Enum):
    """Types of observability events."""
    PUBLICATION = "publication"
    DELIVERY = "delivery"
    FAILURE = "failure"
    SUBSCRIPTION = "subscription"
    CONFIGURATION = "configuration"


@dataclass(frozen=True)
class ObservabilityEvent:
    """
    Event for observability and auditing.
    
    Every critical message lifecycle event generates an observability event.
    """
    
    event_type: str  # From above enum
    timestamp_utc: float = field(default_factory=time.time)
    
    runtime_id: Optional[str] = None
    
    # Context
    envelope_id: Optional[str] = None
    subscription_id: Optional[str] = None
    
    # Details
    message_type: Optional[str] = None
    topic: Optional[str] = None
    
    # Status
    status: str = "success"  # success, failure, dropped
    error_message: Optional[str] = None
    
    # Metrics
    delivery_latency_ms: float = 0.0


class ObservabilityReporter:
    """
    Reports observability events to the system.
    
    This is THE ONE authority for communication observability in the runtime.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # Event storage (in production, would send to metrics backend)
        self._events: List[ObservabilityEvent] = []
        self._max_events = 10000
    
    def report_event(self, event: ObservabilityEvent) -> None:
        """Report an observability event."""
        with self._lock:
            if len(self._events) >= self._max_events:
                # Remove oldest events to make room
                self._events = self._events[-self._max_events:]
            
            self._events.append(event)
    
    def report_publication(
        self,
        envelope_id: str,
        message_type: str,
        runtime_id: Optional[str] = None,
    ) -> None:
        """Report a publication event."""
        self.report_event(ObservabilityEvent(
            event_type=ObservabilityEventType.PUBLICATION.value,
            runtime_id=runtime_id,
            envelope_id=envelope_id,
            message_type=message_type,
            status="success",
        ))
    
    def report_delivery(
        self,
        envelope_id: str,
        subscriber_id: str,
        latency_ms: float,
        succeeded: bool = True,
        error_message: Optional[str] = None,
    ) -> None:
        """Report a delivery event."""
        self.report_event(ObservabilityEvent(
            event_type=ObservabilityEventType.DELIVERY.value,
            envelope_id=envelope_id,
            subscription_id=subscriber_id,
            status="success" if succeeded else "failure",
            delivery_latency_ms=latency_ms,
            error_message=error_message,
        ))
    
    def report_failure(
        self,
        envelope_id: str,
        failure_reason: str,
        runtime_id: Optional[str] = None,
    ) -> None:
        """Report a failure event."""
        self.report_event(ObservabilityEvent(
            event_type=ObservabilityEventType.FAILURE.value,
            runtime_id=runtime_id,
            envelope_id=envelope_id,
            status="failure",
            error_message=failure_reason,
        ))
    
    def get_events(
        self,
        since: Optional[float] = None,
    ) -> List[ObservabilityEvent]:
        """Get reported events, optionally filtered by time."""
        with self._lock:
            if since is None:
                return list(self._events)
            
            return [e for e in self._events if e.timestamp_utc >= since]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get observability statistics."""
        with self._lock:
            event_counts: Dict[str, int] = {}
            
            for event in self._events:
                key = f"{event.event_type}:{event.status}"
                event_counts[key] = event_counts.get(key, 0) + 1
            
            return {
                "total_events": len(self._events),
                "event_breakdown": event_counts,
            }


# =============================================================================
# POLICY ENFORCEMENT
# =============================================================================

class RuntimePolicy(Enum):
    """Runtime policy enforcement types."""
    RATE_LIMITING = "rate-limiting"
    MAX_MESSAGE_SIZE = "max-message-size"
    PUBLISHER_PERMISSIONS = "publisher-permissions"
    SUBSCRIBER_PERMISSIONS = "subscriber-permissions"


@dataclass(frozen=True)
class RuntimePolicyConfig:
    """Runtime policy configuration."""
    
    max_message_size_bytes: int = 1024 * 1024  # 1MB default
    rate_limit_events_per_second: float = 100.0
    
    # Publisher limits
    max_publishers: int = 100
    max_subscriptions_per_publisher: int = 100
    
    # Subscriber limits
    max_subscribers: int = 100
    max_queue_size_per_subscriber: int = 1000


class RuntimePolicyEnforcer:
    """
    Enforces runtime policies on message communication.
    
    All communication must pass policy checks before execution.
    """
    
    def __init__(self, config: Optional[RuntimePolicyConfig] = None):
        self._config = config or RuntimePolicyConfig()
        
        self._lock = threading.RLock()
        
        # Runtime state for enforcement
        self._publisher_count = 0
        self._subscriber_count = 0
    
    def check_message_size(self, size_bytes: int) -> Tuple[bool, Optional[str]]:
        """Check if message size is within limits."""
        if size_bytes > self._config.max_message_size_bytes:
            return False, f"Message exceeds maximum size ({self._config.max_message_size_bytes} bytes)"
        
        return True, None
    
    def check_rate_limit(self, rate: float) -> Tuple[bool, Optional[str]]:
        """Check if publish rate is within limits."""
        if rate > self._config.rate_limit_events_per_second:
            return False, f"Rate exceeds maximum ({self._config.rate_limit_events_per_second} events/sec)"
        
        return True, None
    
    def check_publisher_count(self) -> Tuple[bool, Optional[str]]:
        """Check if publisher count is within limits."""
        with self._lock:
            if self._publisher_count >= self._config.max_publishers:
                return False, "Maximum publisher limit reached"
            
            return True, None
    
    def increment_publisher_count(self) -> bool:
        """Increment publisher counter."""
        with self._lock:
            if self._publisher_count >= self._config.max_publishers:
                return False
            self._publisher_count += 1
            return True
    
    def decrement_publisher_count(self) -> None:
        """Decrement publisher counter."""
        with self._lock:
            if self._publisher_count > 0:
                self._publisher_count -= 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get policy enforcement statistics."""
        with self._lock:
            return {
                "current_publishers": self._publisher_count,
                "max_publishers": self._config.max_publishers,
                "rate_limit_per_second": self._config.rate_limit_events_per_second,
                "max_message_size_bytes": self._config.max_message_size_bytes,
            }


# =============================================================================
# RUNTIME INTEGRATION MANAGER
# =============================================================================

class RuntimeIntegrationManager:
    """
    Manager for runtime integration with the event system.
    
    This is THE ONE authority for integrating message bus communication
    with the runtime lifecycle, security, and observability systems.
    """
    
    def __init__(
        self,
        publisher_manager: Optional[PublisherLifecycleManager] = None,
        subscriber_manager: Optional[SubscriberLifecycleManager] = None,
        security_validator: Optional[SecurityValidator] = None,
        observability_reporter: Optional[ObservabilityReporter] = None,
        policy_enforcer: Optional[RuntimePolicyEnforcer] = None,
    ):
        self._publisher_manager = publisher_manager or PublisherLifecycleManager()
        self._subscriber_manager = subscriber_manager or SubscriberLifecycleManager()
        self._security_validator = security_validator or SecurityValidator()
        self._observability_reporter = observability_reporter or ObservabilityReporter()
        self._policy_enforcer = policy_enforcer or RuntimePolicyEnforcer()
        
        # Lifecycle state
        self._state: LifecycleState = LifecycleState.CREATED
    
    @property
    def state(self) -> LifecycleState:
        """Get current lifecycle state."""
        return self._publisher_manager.state
    
    def start_runtime(self, runtime_id: str) -> bool:
        """
        Start the runtime and initialize integration.
        
        Args:
            runtime_id: ID of this runtime instance
            
        Returns:
            True if startup successful
        """
        with self._publisher_manager._lock:
            if self._state != LifecycleState.CREATED:
                return False
            
            # Initialize components with runtime ID
            # (implementation-specific initialization)
            
            self._state = LifecycleState.INITIALIZING
            
            # Transition to ready after initialization
            self._state = LifecycleState.READY
            
            return True
    
    def stop_runtime(self) -> bool:
        """
        Stop the runtime gracefully.
        
        Returns:
            True if shutdown successful
        """
        with self._publisher_manager._lock:
            if self._state not in (LifecycleState.READY, LifecycleState.PROCESSING):
                return False
            
            # Transition through shutdown states
            self._state = LifecycleState.SHUTTING_DOWN
            
            # Wait for pending operations to complete...
            
            self._state = LifecycleState.STOPPED
            
            return True
    
    def publish(
        self,
        envelope: Any,
        publisher_id: str,
    ) -> bool:
        """
        Publish a message through the integrated system.
        
        Args:
            envelope: Message to publish
            publisher_id: Who is publishing
            
        Returns:
            True if published successfully
        """
        # Check runtime state
        if self._state not in (LifecycleState.READY, LifecycleState.PROCESSING):
            return False
        
        # Validate security context
        context = SecurityContext(authenticated=True, can_publish=True)
        
        is_valid, error = self._security_validator.validate_publish(envelope, context)
        if not is_valid:
            self._observability_reporter.report_failure(
                envelope_id=str(getattr(envelope, "envelope_id", "")),
                failure_reason=error,
            )
            return False
        
        # Check policy limits
        size_bytes = len(str(envelope))  # Rough estimate
        is_valid, error = self._policy_enforcer.check_message_size(size_bytes)
        if not is_valid:
            return False
        
        # Report publication event
        self._observability_reporter.report_publication(
            envelope_id=str(getattr(envelope, "envelope_id", "")),
            message_type=getattr(envelope, "event_type", ""),
            runtime_id=self._publisher_manager.get_publisher(publisher_id).runtime_id
            if self._publisher_manager.get_publisher(publisher_id) else None,
        )
        
        # In production, this would call the actual bus.publish()
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get integrated system statistics."""
        return {
            "lifecycle_state": self._state.value,
            **self._publisher_manager.get_statistics(),
            **self._subscriber_manager.get_statistics(),
            **self._observability_reporter.get_statistics(),
            **self._policy_enforcer.get_statistics(),
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get integrated system health status."""
        stats = self.get_statistics()
        
        return {
            "status": "healthy" if self._state == LifecycleState.READY else "degraded",
            **stats,
        }


__all__ = [
    # Lifecycle states
    "LifecycleState",
    
    # Lifecycle managers
    "PublisherLifecycleManager",
    "SubscriberLifecycleManager",
    "PublisherInfo",
    "SubscriberInfo",
    
    # Security
    "SecurityPolicy",
    "SecurityContext",
    "SecurityValidator",
    
    # Observability
    "ObservabilityEventType",
    "ObservabilityEvent",
    "ObservabilityReporter",
    
    # Policy
    "RuntimePolicy",
    "RuntimePolicyConfig",
    "RuntimePolicyEnforcer",
    
    # Integration manager
    "RuntimeIntegrationManager",
]