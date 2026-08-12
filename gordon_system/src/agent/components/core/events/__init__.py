# Core Events Infrastructure
# ========================
"""
Canonical Event System & Message Bus for Gordon Core.

This package provides the authoritative event infrastructure including:
- Event taxonomy and model (Event, Command, Query, Message)
- Event envelopes and metadata contracts
- Event bus with routing and delivery semantics
- Publisher/Subscriber frameworks with handler dispatch
- Reliability guarantees (retries, ordering, idempotency)
- Runtime integration and observability

Phase 3.8.5: Event System & Message Bus foundation.

All components enforce immutable artifacts and deterministic routing.

ARCHITECTURAL LAWS:
1. Every event has one canonical definition
2. Messages are immutable after publication
3. Publishers never know subscribers
4. Subscribers depend on contracts only
5. Event metadata is standardized
6. Routing is deterministic
7. Hidden channels are prohibited
8. Duplicate event definitions are prohibited
9. Event contracts are transport-independent
10. Every published event is observable

PACKAGE STRUCTURE:
    model.py      - Event taxonomy, contracts, metadata, envelopes
    bus.py        - Message Bus, routing, topics, delivery semantics
    dispatch.py   - Publishers, subscribers, handlers, dispatch pipeline
    reliability.py - Reliability guarantees, retries, ordering, DLQ
    runtime.py    - Runtime integration, security, observability

TESTING:
    tests/test_events_phase_3_8_5*.py - Test suite
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import (
        EventId, MessageId, CommandId, QueryId,
        CorrelationId, CausationId, PublisherId, SubscriberId,
        TopicId, ChannelId, RuntimeId, SequenceNumber,
        PriorityLevel, EventType, EventMetadata, MessageMetadata,
        EventDescriptor, MessageContract, ContractRegistry,
        EventEnvelope, MessageEnvelope,
        generate_event_id, generate_message_id, generate_command_id,
        generate_query_id, generate_correlation_id, generate_causation_id
    )
    
    from .bus import (
        RoutingMode, RouteResult, TopicExpression, SubscriptionDescriptor,
        SubscriberRegistry, TopicRoutingTable, ChannelType, ChannelConfig,
        MessageBusConfig, DeliveryAttempt, MessageBus, get_message_bus
    )
    
    from .dispatch import (
        HandlerType, HandlerDescriptor, HandlerContext, HandlerResult,
        HandlerRegistry, Acknowledgement, DispatchContext, MiddlewareStage,
        DispatchPipeline, PublisherConfig, EventPublisher, CommandPublisher,
        QueryPublisher, SubscriberConfig, MessageSubscriber,
        HandlerRegistryDecorator
    )
    
    from .reliability import (
        DeliveryGuarantee, RetryPolicy, RetryPolicyConfig, OrderingMode,
        OrderingConfig, DeduplicationMode, IdempotencyConfig,
        DeadLetterReason, DeadLetter, DeadLetterQueue, RetryQueue,
        OrderedDeliveryQueue, ReliabilityConfig, ReliabilityEnvelope,
        ReliabilityProtocol
    )
    
    from .runtime import (
        LifecycleState, PublisherLifecycleManager, SubscriberLifecycleManager,
        PublisherInfo, SubscriberInfo, SecurityPolicy, SecurityContext,
        SecurityValidator, ObservabilityEventType, ObservabilityEvent,
        ObservabilityReporter, RuntimePolicy, RuntimePolicyConfig,
        RuntimePolicyEnforcer, RuntimeIntegrationManager
    )

# Re-export core types for convenience
from .model import (
    EventId, MessageId, CommandId, QueryId,
    CorrelationId, CausationId, PublisherId, SubscriberId,
    TopicId, ChannelId, RuntimeId, SequenceNumber,
    PriorityLevel, EventType, EventMetadata, MessageMetadata,
    EventDescriptor, MessageContract, ContractRegistry,
    EventEnvelope, MessageEnvelope,
    generate_event_id, generate_message_id, generate_command_id,
    generate_query_id, generate_correlation_id, generate_causation_id
)

from .bus import (
    RoutingMode, RouteResult, TopicExpression, SubscriptionDescriptor,
    SubscriberRegistry, TopicRoutingTable, ChannelType, ChannelConfig,
    MessageBusConfig, DeliveryAttempt, MessageBus, get_message_bus
)

from .dispatch import (
    HandlerType, HandlerDescriptor, HandlerContext, HandlerResult,
    HandlerRegistry, Acknowledgement, DispatchContext, MiddlewareStage,
    DispatchPipeline, PublisherConfig, EventPublisher, CommandPublisher,
    QueryPublisher, SubscriberConfig, MessageSubscriber,
    HandlerRegistryDecorator
)

from .reliability import (
    DeliveryGuarantee, RetryPolicy, RetryPolicyConfig, OrderingMode,
    OrderingConfig, DeduplicationMode, IdempotencyConfig,
    DeadLetterReason, DeadLetter, DeadLetterQueue, RetryQueue,
    OrderedDeliveryQueue, ReliabilityConfig, ReliabilityEnvelope,
    ReliabilityProtocol
)

from .runtime import (
    LifecycleState, PublisherLifecycleManager, SubscriberLifecycleManager,
    PublisherInfo, SubscriberInfo, SecurityPolicy, SecurityContext,
    SecurityValidator, ObservabilityEventType, ObservabilityEvent,
    ObservabilityReporter, RuntimePolicy, RuntimePolicyConfig,
    RuntimePolicyEnforcer, RuntimeIntegrationManager
)

__all__ = [
    # Core types (model)
    "EventId", "MessageId", "CommandId", "QueryId",
    "CorrelationId", "CausationId", "PublisherId", "SubscriberId",
    "TopicId", "ChannelId", "RuntimeId", "SequenceNumber",
    "PriorityLevel", "EventType", "EventMetadata", "MessageMetadata",
    "EventDescriptor", "MessageContract", "ContractRegistry",
    "EventEnvelope", "MessageEnvelope",
    "generate_event_id", "generate_message_id", "generate_command_id",
    "generate_query_id", "generate_correlation_id", "generate_causation_id",
    
    # Bus (bus)
    "RoutingMode", "RouteResult", "TopicExpression", "SubscriptionDescriptor",
    "SubscriberRegistry", "TopicRoutingTable", "ChannelType", "ChannelConfig",
    "MessageBusConfig", "DeliveryAttempt", "MessageBus", "get_message_bus",
    
    # Dispatch (dispatch.py)
    "HandlerType", "HandlerDescriptor", "HandlerContext", "HandlerResult",
    "HandlerRegistry", "Acknowledgement", "DispatchContext", "MiddlewareStage",
    "DispatchPipeline", "PublisherConfig", "EventPublisher", "CommandPublisher",
    "QueryPublisher", "SubscriberConfig", "MessageSubscriber",
    "HandlerRegistryDecorator",
    
    # Reliability (reliability.py)
    "DeliveryGuarantee", "RetryPolicy", "RetryPolicyConfig", "OrderingMode",
    "OrderingConfig", "DeduplicationMode", "IdempotencyConfig",
    "DeadLetterReason", "DeadLetter", "DeadLetterQueue", "RetryQueue",
    "OrderedDeliveryQueue", "ReliabilityConfig", "ReliabilityEnvelope",
    "ReliabilityProtocol",
    
    # Runtime integration (runtime.py)
    "LifecycleState", "PublisherLifecycleManager", "SubscriberLifecycleManager",
    "PublisherInfo", "SubscriberInfo", "SecurityPolicy", "SecurityContext",
    "SecurityValidator", "ObservabilityEventType", "ObservabilityEvent",
    "ObservabilityReporter", "RuntimePolicy", "RuntimePolicyConfig",
    "RuntimePolicyEnforcer", "RuntimeIntegrationManager",
]

__version__ = "1.0.0"