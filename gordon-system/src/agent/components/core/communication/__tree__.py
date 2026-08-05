# Core Communication Package Tree Metadata
# ==========================================

"""
Package tree structure for src.agent.components.core.communication.

This module describes the package structure and component relationships.
"""

from typing import Dict, List, Any


def get_package_structure() -> Dict[str, Any]:
    """
    Get the complete package structure as a nested dictionary.
    
    Returns:
        Dictionary describing package hierarchy with metadata
    """
    return {
        "path": "src.agent.components.core.communication",
        "name": "communication",
        "description": "Canonical local communication infrastructure for Gordon",
        "phase": "3.8.1",
        
        # Module structure
        "modules": [
            {
                "name": "__init__",
                "type": "package_entry",
                "exports": [
                    # Core identifiers (Phase 3.7.12)
                    "EventId", "MessageId", "SignalId",
                    "CorrelationId", "CausationId", "RuntimeId",
                    "SessionId", "SequenceNumber", "PriorityLevel",
                    
                    # Envelopes
                    "EventEnvelope", "MessageEnvelope", "SignalEnvelope",
                    "DeliveryContext", "Acknowledgement",
                    
                    # Authorities (Phase 3.7.12)
                    "EventBus", "EventBusConfig", "get_event_bus",
                    "MessageRouter", "RoutingPolicy",
                    "SignalManager", "CommunicationCoordinator",
                    
                    # Subscription management
                    "SubscriberRegistry", "SubscriptionDescriptor",
                    "SubscriptionPolicy", "SubscriptionSnapshot",
                    
                    # Queue infrastructure
                    "BoundedQueue", "PriorityQueue", "DeadLetterQueue",
                    
                    # Delivery and channels
                    "DeliveryMode", "DeliveryStatus",
                    "Channel", "ChannelDescriptor", "ChannelStatistics",
                    
                    # Replay
                    "ReplayEngine", "ReplayHistory",
                    
                    # Phase 3.8.1 New: Commands
                    "Command", "CommandId", "CommandMetadata",
                    "CommandResult", "CommandHandlerRegistry",
                    "DuplicateHandlerError", "ShutdownCommand",
                    "RestartCommand", "CancelTaskCommand",
                    
                    # Phase 3.8.1 New: Queries
                    "Query", "QueryId", "QueryMetadata",
                    "QueryResult", "QueryHandlerRegistry",
                    
                    # Phase 3.8.1 New: Request-Response
                    "Request", "Response", "RequestId", "ResponseId",
                    "PendingRequestRegistry", "RequestTimeoutError",
                    "ResponseMismatchError",
                    
                    # Phase 3.8.1 New: Handlers
                    "HandlerResult", "HandlerId", "HandlerMetadata",
                    "CommandHandler", "QueryHandler", "EventHandler",
                    "HandlerRegistry", "HandlerChain",
                    "LoggingHandler", "FailingHandler", "DelayedHandler",
                    
                    # Phase 3.8.1 New: Middleware
                    "Middleware", "MiddlewareContext", "MiddlewareChain",
                    "ValidationMiddleware", "AuthorizationMiddleware",
                    "TracingMiddleware", "DeadLetterMiddleware",
                    "RateLimitMiddleware", "EnrichmentMiddleware",
                    
                    # Phase 3.8.1 New: Local Transport
                    "LocalTransport", "LocalDeliveryProtocol",
                ],
            },
            {
                "name": "model",
                "type": "module",
                "description": "Core identifier types and metadata structures",
                "exports": [
                    "EventId", "MessageId", "SignalId",
                    "CorrelationId", "CausationId",
                    "RuntimeId", "SessionId", "SequenceNumber",
                    "PriorityLevel", "priority_value",
                    "EventMetadata", "MessageMetadata", "SignalMetadata",
                    "Event", "Message", "Signal",
                    "generate_event_id", "generate_message_id",
                    "generate_signal_id", "generate_correlation_id",
                    "generate_causation_id", "generate_session_id",
                ],
            },
            {
                "name": "envelope",
                "type": "module",
                "description": "Transport envelopes with delivery context",
                "exports": [
                    "MessageIntegrity", "Acknowledgement",
                    "DeliveryContext", "EventEnvelope",
                    "MessageEnvelope", "SignalEnvelope",
                    "DeliveryReport",
                ],
            },
            {
                "name": "event_bus",
                "type": "module",
                "description": "Canonical event publication and subscription authority",
                "exports": [
                    "OverflowPolicy", "SubscriptionDescriptor",
                    "SubscriberRegistry", "SubscriptionFilter",
                    "EventHistoryEntry", "EventHistory",
                    "SplitBrainFence", "EventBusConfig", "EventBus",
                    "get_event_bus",
                ],
            },
            {
                "name": "message_router",
                "type": "module",
                "description": "Canonical message routing authority",
                "exports": [
                    "RoutingMode", "RouteResult", "RoutingPolicy",
                    "RouteTable", "MessageQueue", "MessageRouterConfig",
                    "MessageRouter",
                ],
            },
            {
                "name": "signal_manager",
                "type": "module",
                "description": "Canonical signal management authority",
                "exports": [
                    "SignalType", "SignalScope", "SignalDescriptor",
                    "SignalHistoryEntry", "SignalHistory", "SignalRegistry",
                    "SignalManagerConfig", "SignalManager",
                ],
            },
            {
                "name": "coordinator",
                "type": "module",
                "description": "Orchestration of communication authorities",
                "exports": [
                    "CoordinatorConfig", "CommunicationState", "CommunicationCoordinator",
                ],
            },
            {
                "name": "subscriber",
                "type": "module",
                "description": "Subscriber registry and lifecycle management",
                "exports": [
                    "SubscriptionPolicy", "SubscriptionPolicyConfig",
                    "SubscriptionDescriptor", "SubscriptionSnapshot",
                    "SubscriberRegistry", "SubscriberLifecycleManager",
                ],
            },
            {
                "name": "queues",
                "type": "module",
                "description": "Bounded queue infrastructure with backpressure",
                "exports": [
                    "OverflowPolicy", "BackpressurePolicy",
                    "BackpressureState", "DeadLetterReason", "DeadLetter",
                    "DeadLetterQueue", "RetryQueue", "BoundedQueue",
                    "PriorityQueueConfig", "PriorityQueue", "QueueFullError",
                ],
            },
            {
                "name": "channels",
                "type": "module",
                "description": "Channel abstraction for communication endpoints",
                "exports": [
                    "ChannelType", "ChannelMode", "ChannelPolicy",
                    "ChannelStatistics", "ChannelDescriptor", "Channel",
                    "InternalChannel", "ExternalChannelConfig",
                    "ExternalChannel", "ChannelManagerConfig", "ChannelManager",
                ],
            },
            {
                "name": "delivery",
                "type": "module",
                "description": "Delivery modes and acknowledgements",
                "exports": [
                    "DeliveryMode", "mode_priority", "DeliveryStatus",
                    "DeliveryAttempt", "DeliveryTracker",
                    "AcknowledgementHandler",
                ],
            },
            {
                "name": "replay",
                "type": "module",
                "description": "Deterministic replay engine using immutable history",
                "exports": [
                    "ReplayState", "ReplayHistoryEntry", "ReplayHistory",
                    "ReplayConfig", "ReplayEngine", "ReplayEngineFactory",
                ],
            },
            {
                "name": "observability",
                "type": "module",
                "description": "Communication observability and diagnostics",
                "exports": [
                    "CommunicationEventType", "CommunicationEvent",
                    "EventPublished", "MessagePublished", "SignalPublished",
                    "DeliveryEvent", "SubscriberRegistered",
                    "SubscriberUnregistered", "QueueOverflow",
                    "BackpressureApplied", "DeadLetterGenerated",
                    "CommunicationEventHistory", "DiagnosticsSnapshot",
                    "DiagnosticsProvider",
                ],
            },
            {
                # Phase 3.8.1 New
                "name": "commands",
                "type": "module",
                "description": "Command contracts for state-changing operations",
                "exports": [
                    "CommandResultType", "CommandId", "CommandMetadata",
                    "Command", "CommandHandler", "CommandResult",
                    "CommandHandlerRegistry", "DuplicateHandlerError",
                    "ShutdownCommand", "RestartCommand", "CancelTaskCommand",
                ],
            },
            {
                # Phase 3.8.1 New
                "name": "queries",
                "type": "module",
                "description": "Query contracts for information retrieval",
                "exports": [
                    "QueryConsistency", "QueryId", "QueryMetadata",
                    "Query", "QueryHandler", "QueryResult",
                    "QueryHandlerRegistry", "GetStateQuery", "GetMetricsQuery",
                    "ListComponentsQuery",
                ],
            },
            {
                # Phase 3.8.1 New
                "name": "requests",
                "type": "module",
                "description": "Request-response correlation infrastructure",
                "exports": [
                    "RequestState", "ResponseType", "RequestId", "ResponseId",
                    "RequestMetadata", "Request", "Response",
                    "RequestTimeoutError", "ResponseMismatchError",
                    "PendingRequestRegistry", "RequestClient",
                ],
            },
            {
                # Phase 3.8.1 New
                "name": "handlers",
                "type": "module",
                "description": "Handler protocols and registries",
                "exports": [
                    "HandlerResultType", "HandlerId", "HandlerMetadata",
                    "HandlerResult", "CommandHandler", "QueryHandler",
                    "EventHandler", "HandlerRegistry", "DuplicateHandlerError",
                    "HandlerChain", "HandlerChainError", "LoggingHandler",
                    "FailingHandler", "DelayedHandler",
                ],
            },
            {
                # Phase 3.8.1 New
                "name": "middleware",
                "type": "module",
                "description": "Middleware for cross-cutting concerns",
                "exports": [
                    "MiddlewarePhase", "MiddlewareResultType", "MiddlewareId",
                    "MiddlewareContext", "Middleware",
                    "ValidationMiddleware", "AuthorizationMiddleware",
                    "TracingMiddleware", "DeadLetterMiddleware",
                    "RateLimitMiddleware", "EnrichmentMiddleware",
                    "MiddlewareChain",
                ],
            },
            {
                # Phase 3.8.1 New
                "name": "local",
                "type": "module",
                "description": "Local in-process transport layer",
                "exports": [
                    "DeliveryMode", "DeliveryResult", "LocalTransportConfig",
                    "LocalTransport", "LocalDeliveryProtocol",
                ],
            },
        ],
        
        # Package metadata
        "metadata": {
            "phase": "3.8.1",
            "status": "production",
            "api_version": (1, 0, 0),
            "lifecycle_required": True,
            "bounded_queues": True,
            "delivery_guarantees": [
                "best_effort_local",
                "at_most_once_async",
                "synchronous_immediate",
            ],
            "ordering_guarantees": {
                "per_stream": "fifo",
                "global": "none",
                "per_correlation_id": "via_trace_context",
            },
        },
    }


def get_module_dependencies() -> Dict[str, List[str]]:
    """
    Get module-level dependencies.
    
    Returns:
        Dictionary mapping module names to their imports
    """
    return {
        "__init__": [
            "model",
            "envelope",
            "event_bus",
            "message_router",
            "signal_manager",
            "coordinator",
            "subscriber",
            "queues",
            "channels",
            "delivery",
            "replay",
            "observability",
            "commands",      # Phase 3.8.1
            "queries",       # Phase 3.8.1
            "requests",      # Phase 3.8.1
            "handlers",      # Phase 3.8.1
            "middleware",    # Phase 3.8.1
            "local",         # Phase 3.8.1
        ],
        "model": [],
        "envelope": ["model"],
        "event_bus": ["model", "envelope"],
        "message_router": ["model", "envelope"],
        "signal_manager": ["model", "envelope"],
        "coordinator": ["event_bus", "message_router", "signal_manager"],
        "subscriber": ["model"],
        "queues": [],
        "channels": ["queues"],
        "delivery": ["envelope"],
        "replay": [],
        "observability": [],
        # Phase 3.8.1 modules
        "commands": [],
        "queries": [],
        "requests": ["model"],
        "handlers": [],
        "middleware": [],
        "local": ["queues", "handlers"],
    }


def get_architecture_constraints() -> Dict[str, Any]:
    """
    Get architecture constraints for the communication package.
    
    Returns:
        Dictionary of constraint definitions
    """
    return {
        # Ownership boundaries
        "does_not_own": [
            "runtime_state",
            "cognition",
            "reasoning",
            "planning",
            "memory_semantics",
            "goals",
            "values",
            "personality",
        ],
        
        # Dependencies on other packages
        "requires": [
            "src.agent.components.core.types",  # For core type definitions
        ],
        
        # Integration points
        "integrates_with": [
            "lifecycle",      # Startup/shutdown coordination
            "runtime",        # Runtime assembly integration
            "scheduling",     # Priority coordination
            "tasks",          # Task execution correlation
            "signals",        # Cancellation/shutdown propagation
            "observability",  # Tracing/metrics
        ],
        
        # Invariants maintained
        "invariants": [
            "bounded_queues",
            "no_background_workers_at_import",
            "explicit_lifecycle_start_stop",
            "immutable_messages",
            "single_handler_for_commands_by_default",
            "bounded_pending_requests_with_cleanup",
        ],
    }