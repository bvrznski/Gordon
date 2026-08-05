# Core Communication Infrastructure
# ==================================

"""
Phase 3.7.12 - Event Bus, Messaging, Signals & Runtime Communication

Production communication architecture with:
- Exactly one canonical EventBus per runtime
- Exactly one canonical MessageRouter per runtime
- Exactly one canonical SignalManager per runtime
- Exactly one canonical CommunicationCoordinator per runtime
- Typed immutable events, messages, and signals
- Deterministic routing with policies (direct, topic, broadcast, multicast)
- Bounded queues with backpressure and dead-letter support
- Replay support using immutable history

Communication is infrastructure.
Communication never owns runtime state.
Communication never performs business logic.
Communication transports immutable artifacts only.

The canonical pipeline:

    Publisher
            ↓
    Immutable Event
            ↓
    Validation
            ↓
    Routing
            ↓
    Event Bus
            ↓
    Delivery
            ↓
    Subscribers
            ↓
    Acknowledgement
            ↓
    Diagnostics
            ↓
    History
"""

from .model import (
    EventId,
    MessageId,
    SignalId,
    CorrelationId,
    CausationId,
    RuntimeId,
    SessionId,
    SequenceNumber,
    PriorityLevel,
)

from .envelope import (
    EventEnvelope,
    MessageEnvelope,
    SignalEnvelope,
    DeliveryContext,
    Acknowledgement,
)

from .event_bus import EventBus, EventBusConfig, get_event_bus
from .message_router import MessageRouter, RoutingPolicy
from .signal_manager import SignalManager
from .coordinator import CommunicationCoordinator

from .subscriber import (
    SubscriberRegistry,
    SubscriptionDescriptor,
    SubscriptionPolicy,
    SubscriptionSnapshot,
)

from .queues import BoundedQueue, PriorityQueue, DeadLetterQueue
from .delivery import DeliveryMode, DeliveryStatus
from .channels import Channel, ChannelDescriptor, ChannelStatistics
from .replay import ReplayEngine, ReplayHistory

# New communication types (Phase 3.8.1)
from .commands import (
    Command,
    CommandId,
    CommandMetadata,
    CommandResult,
    CommandHandlerRegistry,
    DuplicateHandlerError,
    ShutdownCommand,
    RestartCommand,
    CancelTaskCommand,
)

from .queries import (
    Query,
    QueryId,
    QueryMetadata,
    QueryResult,
    QueryHandlerRegistry,
)

from .requests import (
    Request,
    Response,
    RequestId,
    ResponseId,
    PendingRequestRegistry,
    RequestTimeoutError,
    ResponseMismatchError,
)

from .handlers import (
    HandlerResult,
    HandlerId,
    HandlerMetadata,
    CommandHandler,
    QueryHandler,
    EventHandler,
    HandlerRegistry,
    HandlerChain,
    LoggingHandler,
    FailingHandler,
    DelayedHandler,
)

from .middleware import (
    Middleware,
    MiddlewareContext,
    MiddlewareChain,
    ValidationMiddleware,
    AuthorizationMiddleware,
    TracingMiddleware,
    DeadLetterMiddleware,
    RateLimitMiddleware,
    EnrichmentMiddleware,
)

from .local import (
    LocalTransport,
    LocalDeliveryProtocol,
    DeliveryMode,
    DeliveryResult,
)

from .integration import (
    CommunicationLifecycleConfig,
    CommunicationLifecycleAdapter,
    SignalPropagationAdapter,
)

# Failure event integration (Phase 3.7.27)
try:
    from ..failure.events import EventBusFailurePublisher
except ImportError:
    # Optional dependency - failure events may not be available in all contexts
    pass

__all__ = [
    # Core identifiers (existing)
    "EventId",
    "MessageId",
    "SignalId",
    "CorrelationId",
    "CausationId",
    "RuntimeId",
    "SessionId",
    "SequenceNumber",
    "PriorityLevel",
    
    # Envelopes (existing)
    "EventEnvelope",
    "MessageEnvelope",
    "SignalEnvelope",
    "DeliveryContext",
    "Acknowledgement",
    
    # Authorities (existing)
    "EventBus",
    "EventBusConfig",
    "get_event_bus",  # Phase 3.7.27 - Convenience function for singleton access
    "MessageRouter",
    "RoutingPolicy",
    "SignalManager",
    "CommunicationCoordinator",
    
    # Subscription management (existing)
    "SubscriberRegistry",
    "SubscriptionDescriptor",
    "SubscriptionPolicy",
    "SubscriptionSnapshot",
    
    # Queue infrastructure (existing)
    "BoundedQueue",
    "PriorityQueue",
    "DeadLetterQueue",
    
    # Delivery (existing)
    "DeliveryMode",
    "DeliveryStatus",
    
    # Channels (existing)
    "Channel",
    "ChannelDescriptor",
    "ChannelStatistics",
    
    # Replay (existing)
    "ReplayEngine",
    "ReplayHistory",
    
    # ==================
    # PHASE 3.8.1 NEW: COMMUNICATION CONTRACTS
    # ==================
    
    # Commands
    "Command",
    "CommandId",
    "CommandMetadata",
    "CommandResult",
    "CommandHandlerRegistry",
    "DuplicateHandlerError",
    "ShutdownCommand",
    "RestartCommand",
    "CancelTaskCommand",
    
    # Queries
    "Query",
    "QueryId",
    "QueryMetadata",
    "QueryResult",
    "QueryHandlerRegistry",
    
    # Request-Response
    "Request",
    "Response",
    "RequestId",
    "ResponseId",
    "PendingRequestRegistry",
    "RequestTimeoutError",
    "ResponseMismatchError",
    
    # Handlers
    "HandlerResult",
    "HandlerId",
    "HandlerMetadata",
    "CommandHandler",
    "QueryHandler",
    "EventHandler",
    "HandlerRegistry",
    "HandlerChain",
    "LoggingHandler",
    "FailingHandler",
    "DelayedHandler",
    
    # Middleware
    "Middleware",
    "MiddlewareContext",
    "MiddlewareChain",
    "ValidationMiddleware",
    "AuthorizationMiddleware",
    "TracingMiddleware",
    "DeadLetterMiddleware",
    "RateLimitMiddleware",
    "EnrichmentMiddleware",
    
    # Local Transport
    "LocalTransport",
    "LocalDeliveryProtocol",
    "DeliveryMode",  # Also defined in local.py
    "DeliveryResult",  # Also defined in local.py
    
    # Integration (lifecycle, signals)
    "CommunicationLifecycleConfig",
    "CommunicationLifecycleAdapter",
    "SignalPropagationAdapter",
]
