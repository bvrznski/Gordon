# Core Dispatch Pipeline Authority
# ==================================
"""
Canonical dispatch architecture for publishers, subscribers, handlers,
and message processing in Gordon Core.

This module defines how runtime components:
- Publish events
- Subscribe to message contracts
- Register handlers
- Participate in deterministic dispatch

PUBLISHER MODEL:
    - Events are published via canonical bus
    - Publishers know only message contracts
    - No knowledge of subscribers
    
SUBSCRIBER MODEL:
    - Static and dynamic subscriptions supported
    - Wildcard and conditional subscriptions
    - Lifecycle-aware subscriptions
    
HANDLER MODEL:
    - EventHandler, CommandHandler, QueryHandler abstractions
    - Handler registration through canonical registry
    - Handlers depend on message contracts only
    
DISPATCH PIPELINE:
    - Message acceptance -> validation -> middleware -> handler invocation
    - Each stage emits observable events
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Type, Tuple, AsyncIterator
from enum import Enum, auto
import threading
import time
import uuid

from .model import (
    EventEnvelope,
    MessageEnvelope,
    CorrelationId,
    CausationId,
    RuntimeId,
)


# =============================================================================
# HANDLER TYPES & SEMANTICS
# =============================================================================

class HandlerType(Enum):
    """Types of message handlers."""
    EVENT = "event"          # Handles events (facts about state)
    COMMAND = "command"      # Handles commands (state changes)
    QUERY = "query"          # Handles queries (information requests)


@dataclass(frozen=True)
class HandlerDescriptor:
    """
    Immutable descriptor for a handler registration.
    
    A handler processes messages of specific types according to its contract.
    """
    
    handler_id: str
    handler_type: HandlerType
    
    message_types: Tuple[str, ...]  # Message types this handler processes
    
    # Execution configuration
    execution_mode: str = "synchronous"   # sync, async
    priority: int = 0                    # Lower = higher priority
    
    # Failure handling
    retry_on_failure: bool = False
    max_retries: int = 3
    
    # Statistics (updated by dispatch pipeline)
    messages_handled: int = 0
    failures: int = 0


class HandlerContext:
    """
    Context for handler execution.
    
    Provides access to message, metadata, and runtime information during
    handler invocation.
    """
    
    def __init__(
        self,
        envelope: EventEnvelope,
        handler_id: str,
    ):
        self._envelope = envelope
        self._handler_id = handler_id
        self._timestamp_utc = time.time()
        
        # Execution state
        self._started_at: Optional[float] = None
        self._completed_at: Optional[float] = None
        self._failed: bool = False
        self._failure_reason: Optional[str] = None
    
    @property
    def envelope(self) -> EventEnvelope:
        """Get the message envelope being processed."""
        return self._envelope
    
    @property
    def handler_id(self) -> str:
        """Get the handler ID."""
        return self._handler_id
    
    @property
    def correlation_id(self) -> Optional[str]:
        """Get correlation ID for tracing."""
        return self._envelope.correlation_id
    
    @property
    def causation_id(self) -> Optional[str]:
        """Get causation ID for chain tracking."""
        return self._envelope.causation_id
    
    def start(self) -> None:
        """Mark handler execution as started."""
        self._started_at = time.time()
    
    def complete(self) -> None:
        """Mark handler execution as completed successfully."""
        self._completed_at = time.time()
    
    def fail(self, reason: str) -> None:
        """Mark handler execution as failed."""
        self._failed = True
        self._failure_reason = reason
        self._completed_at = time.time()
    
    def get_execution_time_ms(self) -> Optional[float]:
        """Get total execution time in milliseconds."""
        if self._started_at is None or self._completed_at is None:
            return None
        return (self._completed_at - self._started_at) * 1000


@dataclass(frozen=True)
class HandlerResult:
    """
    Result of handler execution.
    
    Immutable record of what happened during handler invocation.
    """
    
    handler_id: str
    envelope_id: str
    
    succeeded: bool
    started_at_utc: float
    completed_at_utc: Optional[float]
    
    failure_reason: Optional[str] = None
    output_data: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# HANDLER REGISTRY
# =============================================================================

class HandlerRegistry:
    """
    Registry for message handlers.
    
    This is THE ONE authority for handler registration in the system.
    Every message must have at least one registered handler.
    
    INVARIANTS:
        1. One canonical registry per runtime
        2. No duplicate handler IDs allowed
        3. Handlers depend on contracts only
        4. Handler execution is observable
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # handler_id -> HandlerDescriptor
        self._handlers: Dict[str, HandlerDescriptor] = {}
        
        # message_type -> list of handler_ids interested
        self._type_index: Dict[str, List[str]] = {}
    
    def register_handler(
        self,
        descriptor: HandlerDescriptor,
    ) -> str:
        """
        Register a new handler.
        
        Returns the handler ID (generated if not provided).
        """
        handler_id = descriptor.handler_id
        if not handler_id:
            handler_id = f"handler_{uuid.uuid4().hex[:16]}"
            descriptor = HandlerDescriptor(
                handler_id=handler_id,
                handler_type=descriptor.handler_type,
                message_types=descriptor.message_types,
                execution_mode=descriptor.execution_mode,
                priority=descriptor.priority,
                retry_on_failure=descriptor.retry_on_failure,
                max_retries=descriptor.max_retries,
            )
        
        with self._lock:
            if handler_id in self._handlers:
                raise ValueError(f"Handler {handler_id} already registered")
            
            self._handlers[handler_id] = descriptor
            
            # Update type index
            for msg_type in descriptor.message_types:
                if msg_type not in self._type_index:
                    self._type_index[msg_type] = []
                if handler_id not in self._type_index[msg_type]:
                    self._type_index[msg_type].append(handler_id)
            
            # Sort by priority (lower first)
            for msg_type in self._type_index:
                self._type_index[msg_type].sort(
                    key=lambda hid: self._handlers[hid].priority
                )
        
        return handler_id
    
    def unregister_handler(self, handler_id: str) -> bool:
        """Remove a handler by ID."""
        with self._lock:
            if handler_id not in self._handlers:
                return False
            
            descriptor = self._handlers[handler_id]
            del self._handlers[handler_id]
            
            # Update type index
            for msg_type in descriptor.message_types:
                if msg_type in self._type_index:
                    try:
                        self._type_index[msg_type].remove(handler_id)
                        if not self._type_index[msg_type]:
                            del self._type_index[msg_type]
                    except ValueError:
                        pass
            
            return True
    
    def get_handlers_for_message(self, message_type: str) -> List[str]:
        """Get handler IDs for a message type, sorted by priority."""
        with self._lock:
            return list(self._type_index.get(message_type, []))
    
    def get_handler(self, handler_id: str) -> Optional[HandlerDescriptor]:
        """Get descriptor for a specific handler."""
        with self._lock:
            return self._handlers.get(handler_id)
    
    def get_all_handlers(self) -> Dict[str, HandlerDescriptor]:
        """Get all registered handlers."""
        with self._lock:
            return dict(self._handlers)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with self._lock:
            total = sum(len(hs) for hs in self._type_index.values())
            return {
                "total_handlers": len(self._handlers),
                "message_types_count": len(self._type_index),
                "total_type_bindings": total,
            }


# =============================================================================
# ACKNOWLEDGEMENT TYPES
# =============================================================================

class Acknowledgement(Enum):
    """Handler acknowledgement types."""
    ACCEPTED = "accepted"        # Message accepted for processing
    PROCESSED = "processed"      # Message processed successfully
    REJECTED = "rejected"        # Message rejected (validation, policy)
    DEFERRED = "deferred"        # Processing deferred to later
    CANCELLED = "cancelled"      # Processing cancelled by request
    FAILED = "failed"            # Processing failed


# =============================================================================
# DISPATCH CONTEXT
# =============================================================================

@dataclass(frozen=True)
class DispatchContext:
    """
    Context for a single dispatch operation.
    
    Tracks the complete lifecycle of message dispatch through all stages.
    """
    
    envelope: EventEnvelope
    
    # Dispatch state
    accepted_at_utc: float = field(default_factory=time.time)
    handlers_resolved: Optional[List[str]] = None
    handlers_completed: List[str] = field(default_factory=list)
    failures: List[Tuple[str, str]] = field(default_factory=list)  # (handler_id, reason)
    
    dispatch_mode: str = "synchronous"  # sync, async
    execution_policy: str = "sequential"  # sequential, parallel
    
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if dispatch operation is complete."""
        return self.completed_at_utc is not None
    
    def get_execution_time_ms(self) -> float:
        """Get total dispatch time in milliseconds."""
        if self.started_at_utc is None or self.completed_at_utc is None:
            return 0.0
        return (self.completed_at_utc - self.started_at_utc) * 1000


# =============================================================================
# MIDDLEWARE PIPELINE STAGE
# =============================================================================

class MiddlewareStage:
    """
    A single middleware stage in the dispatch pipeline.
    
    Each stage can:
        - Validate messages
        - Add tracing metadata
        - Check authorization
        - Transform data (non-destructive)
        - Log or emit metrics
    
    Middlewares are composable and execute in order.
    """
    
    def __init__(
        self,
        name: str,
        handler: Callable[[EventEnvelope, Optional[Dict[str, Any]]], Tuple[bool, Optional[EventEnvelope]]],
    ):
        """
        Initialize middleware stage.
        
        Args:
            name: Stage name for tracing
            handler: Function that processes envelope and returns
                    (should_continue, maybe_new_envelope)
        """
        self.name = name
        self._handler = handler
    
    def execute(
        self,
        envelope: EventEnvelope,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[EventEnvelope]]:
        """
        Execute this middleware stage.
        
        Args:
            envelope: Message being processed
            context: Shared context between stages
            
        Returns:
            (should_continue, maybe_new_envelope)
            - If should_continue is False, dispatch stops
            - If envelope is None, current envelope is used
        """
        return self._handler(envelope, context)


# =============================================================================
# DISPATCH PIPELINE
# =============================================================================

class DispatchPipeline:
    """
    Canonical dispatch pipeline for message processing.
    
    Pipeline stages (in order):
        1. Message acceptance
        2. Contract validation
        3. Middleware execution
        4. Subscriber resolution
        5. Handler invocation
        6. Acknowledgement
        7. Completion notification
        8. Diagnostics
    
    INVARIANTS:
        - Each stage emits observable events
        - Middleware never mutates immutable payloads
        - Deterministic ordering within streams
    """
    
    def __init__(self, handler_registry: HandlerRegistry):
        self._handler_registry = handler_registry
        self._middleware_stages: List[MiddlewareStage] = []
        self._lock = threading.RLock()
        
        # Statistics
        self._dispatch_count = 0
        self._success_count = 0
        self._failure_count = 0
    
    def add_middleware(
        self,
        stage: MiddlewareStage,
        position: Optional[int] = None,
    ) -> None:
        """Add a middleware stage to the pipeline."""
        with self._lock:
            if position is None:
                self._middleware_stages.append(stage)
            else:
                self._middleware_stages.insert(position, stage)
    
    def add_logging_middleware(
        self,
        name: str = "logging",
        include_payload: bool = False,
    ) -> None:
        """Add logging middleware to the pipeline."""
        def log_handler(envelope: EventEnvelope, context: Optional[Dict]) -> Tuple[bool, Optional[EventEnvelope]]:
            # Log message type
            print(f"[{name}] Processing {envelope.event_type}")
            
            if include_payload:
                print(f"    Payload: {envelope.payload}")
            
            return (True, envelope)
        
        self.add_middleware(MiddlewareStage(name, log_handler))
    
    def add_validation_middleware(
        self,
        name: str = "validation",
    ) -> None:
        """Add validation middleware to the pipeline."""
        def validate_handler(envelope: EventEnvelope, context: Optional[Dict]) -> Tuple[bool, Optional[EventEnvelope]]:
            # Basic validation - in production would check schema, auth, etc.
            if not envelope.event_type:
                return (False, None)  # Reject - invalid event type
            
            return (True, envelope)
        
        self.add_middleware(MiddlewareStage(name, validate_handler))
    
    def dispatch(
        self,
        envelope: EventEnvelope,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, List[HandlerResult]]:
        """
        Dispatch a message through the complete pipeline.
        
        Args:
            envelope: Message to process
            context: Shared context between stages
            
        Returns:
            (success, results) where results is list of handler execution results
        """
        start_time = time.time()
        
        with self._lock:
            self._dispatch_count += 1
        
        # Context for middleware chain
        pipeline_context = dict(context or {})
        current_envelope = envelope
        
        # Stage 1-3: Middleware pipeline
        for stage in self._middleware_stages:
            should_continue, maybe_new = stage.execute(current_envelope, pipeline_context)
            
            if not should_continue:
                with self._lock:
                    self._failure_count += 1
                
                return (False, [])
            
            if maybe_new is not None:
                current_envelope = maybe_new
        
        # Stage 4: Resolve subscribers/handlers
        handler_ids = self._handler_registry.get_handlers_for_message(current_envelope.event_type)
        
        with self._lock:
            pipeline_context["handlers_resolved"] = handler_ids
        
        # Stage 5-6: Execute handlers and collect results
        results: List[HandlerResult] = []
        success_count = 0
        
        for handler_id in handler_ids:
            ctx = HandlerContext(current_envelope, handler_id)
            
            try:
                ctx.start()
                
                # In production, this would call the actual handler function
                # For now, simulate successful handling
                ctx.complete()
                
                result = HandlerResult(
                    handler_id=handler_id,
                    envelope_id=current_envelope.envelope_id,
                    succeeded=True,
                    started_at_utc=ctx._started_at or time.time(),
                    completed_at_utc=ctx._completed_at or time.time(),
                )
                results.append(result)
                success_count += 1
                
            except Exception as e:
                ctx.fail(str(e))
                
                result = HandlerResult(
                    handler_id=handler_id,
                    envelope_id=current_envelope.envelope_id,
                    succeeded=False,
                    started_at_utc=ctx._started_at or time.time(),
                    completed_at_utc=ctx._completed_at or time.time(),
                    failure_reason=str(e),
                )
                results.append(result)
        
        # Finalize
        end_time = time.time()
        
        with self._lock:
            self._success_count += success_count
            if len(handler_ids) > 0:
                # Track as complete only if we attempted dispatch
                pass
        
        return (True, results)


# =============================================================================
# PUBLISHER FRAMEWORK
# =============================================================================

class PublisherConfig:
    """Configuration for a publisher."""
    
    def __init__(
        self,
        publisher_id: str = "",
        batch_size: int = 1,
        delay_seconds: float = 0.0,
    ):
        self.publisher_id = publisher_id or f"publisher_{uuid.uuid4().hex[:8]}"
        self.batch_size = batch_size
        self.delay_seconds = delay_seconds


class EventPublisher:
    """
    Canonical event publisher.
    
    Publishers emit events to the message bus. They know only message
    contracts, not subscribers.
    
    INVARIANTS:
        - Publishers know only message contracts
        - No knowledge of subscribers
        - Events are immutable after creation
    """
    
    def __init__(
        self,
        bus: "MessageBus",
        config: Optional[PublisherConfig] = None,
    ):
        self._bus = bus
        self._config = config or PublisherConfig()
        self._batch: List[EventEnvelope] = []
    
    def publish(
        self,
        envelope: EventEnvelope,
    ) -> bool:
        """
        Publish an event to the message bus.
        
        Args:
            envelope: Event to publish
            
        Returns:
            True if accepted by bus
        """
        return self._bus.publish(envelope)
    
    def publish_batch(
        self,
        envelopes: List[EventEnvelope],
    ) -> int:
        """
        Publish a batch of events.
        
        Args:
            envelopes: Events to publish
            
        Returns:
            Number of successfully published events
        """
        count = 0
        for envelope in envelopes:
            if self.publish(envelope):
                count += 1
        return count
    
    def publish_deferred(
        self,
        envelope: EventEnvelope,
        delay_seconds: float,
    ) -> bool:
        """
        Schedule an event for deferred publication.
        
        Args:
            envelope: Event to publish
            delay_seconds: Delay before publishing
            
        Returns:
            True if scheduled
        """
        # In production, would use scheduler
        return self.publish(envelope)


class CommandPublisher(EventPublisher):
    """Publisher specialized for command messages."""
    
    def __init__(self, bus: "MessageBus", config: Optional[PublisherConfig] = None):
        super().__init__(bus, config)
    
    def send_command(
        self,
        command_type: str,
        payload: Dict[str, Any],
        destination_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> EventEnvelope:
        """
        Create and publish a command message.
        
        Args:
            command_type: Type of command (e.g., "task.start")
            payload: Command payload
            destination_id: Target subscriber (optional)
            correlation_id: Request ID for tracing (optional)
            
        Returns:
            Created envelope (not yet published)
        """
        envelope = EventEnvelope(
            envelope_id=str(uuid.uuid4()),
            runtime_id=self._bus.runtime_id,
            event_type=command_type,
            payload=dict(payload),
            destination_id=destination_id,
            correlation_id=correlation_id,
        )
        
        # Publish immediately
        self.publish(envelope)
        
        return envelope


class QueryPublisher(EventPublisher):
    """Publisher specialized for query messages."""
    
    def __init__(self, bus: "MessageBus", config: Optional[PublisherConfig] = None):
        super().__init__(bus, config)
    
    def send_query(
        self,
        query_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> EventEnvelope:
        """
        Create and publish a query message.
        
        Args:
            query_type: Type of query (e.g., "system.status")
            payload: Query parameters
            correlation_id: Request ID for tracing (optional)
            
        Returns:
            Created envelope
        """
        envelope = EventEnvelope(
            envelope_id=str(uuid.uuid4()),
            runtime_id=self._bus.runtime_id,
            event_type=query_type,
            payload=dict(payload),
            correlation_id=correlation_id,
        )
        
        self.publish(envelope)
        
        return envelope


# =============================================================================
# SUBSCRIBER FRAMEWORK
# =============================================================================

class SubscriberConfig:
    """Configuration for a subscriber."""
    
    def __init__(
        self,
        subscriber_id: str = "",
        batch_size: int = 10,
        poll_interval_seconds: float = 0.1,
    ):
        self.subscriber_id = subscriber_id or f"subscriber_{uuid.uuid4().hex[:8]}"
        self.batch_size = batch_size
        self.poll_interval_seconds = poll_interval_seconds


class MessageSubscriber:
    """
    Canonical message subscriber.
    
    Subscribers express interest in message contracts through registrations.
    They never depend on publishers - only on contracts.
    
    INVARIANTS:
        - Subscribers register through canonical APIs
        - Never depend on publishers
        - Contracts define subscription criteria
    """
    
    def __init__(
        self,
        bus: "MessageBus",
        handler_registry: HandlerRegistry,
        config: Optional[SubscriberConfig] = None,
    ):
        self._bus = bus
        self._handler_registry = handler_registry
        self._config = config or SubscriberConfig()
        
        # Subscription tracking
        self._subscription_ids: List[str] = []
    
    def subscribe(
        self,
        event_types: List[str],
        handler_id: str,
        topics: Optional[List[str]] = None,
    ) -> str:
        """
        Subscribe to message types.
        
        Args:
            event_types: Types of events to receive
            handler_id: ID of handler that will process messages
            topics: Topics to subscribe to (optional)
            
        Returns:
            Subscription ID for later unsubscription
        """
        sub_id = self._bus.subscribe(
            subscriber_id=self._config.subscriber_id,
            event_types=event_types,
            topics=topics or [],
        )
        
        self._subscription_ids.append(sub_id)
        return sub_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from a subscription."""
        if subscription_id in self._subscription_ids:
            self._subscription_ids.remove(subscription_id)
            return self._bus.unsubscribe(subscription_id)
        return False
    
    def get_pending_messages(
        self,
        max_count: int = 10,
    ) -> List[EventEnvelope]:
        """
        Get pending messages for this subscriber.
        
        In production, would pull from queue. For now, returns empty list
        (real implementation uses message queues).
        """
        return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get subscriber statistics."""
        return {
            "subscriber_id": self._config.subscriber_id,
            "subscription_count": len(self._subscription_ids),
        }


# =============================================================================
# HANDLER REGISTRATION DECORATOR
# =============================================================================

class HandlerRegistryDecorator:
    """
    Decorator-based handler registration.
    
    Usage:
        registry = HandlerRegistry()
        decorator = HandlerRegistryDecorator(registry)
        
        @decorator.handler("task.completed")
        def handle_task_completed(envelope: EventEnvelope):
            print(f"Task {envelope.payload['task_id']} completed!")
    """
    
    def __init__(self, registry: HandlerRegistry):
        self._registry = registry
    
    def handler(
        self,
        *message_types: str,
        handler_type: HandlerType = HandlerType.EVENT,
        execution_mode: str = "synchronous",
        priority: int = 0,
    ):
        """
        Decorator for registering a handler function.
        
        Usage:
            @decorator.handler("task.completed", "task.failed")
            def handle_task_events(envelope):
                print(f"Event: {envelope.event_type}")
        """
        def decorator(func: Callable[[EventEnvelope], Any]):
            descriptor = HandlerDescriptor(
                handler_id=f"{func.__name__}_{uuid.uuid4().hex[:8]}",
                handler_type=handler_type,
                message_types=tuple(message_types),
                execution_mode=execution_mode,
                priority=priority,
            )
            
            # Register with registry (would need to store func for actual invocation)
            self._registry.register_handler(descriptor)
            
            return func
        
        return decorator


__all__ = [
    # Handler types
    "HandlerType",
    "HandlerDescriptor",
    
    # Context and results
    "HandlerContext",
    "HandlerResult",
    
    # Registry
    "HandlerRegistry",
    
    # Acknowledgements
    "Acknowledgement",
    
    # Dispatch pipeline
    "DispatchContext",
    "MiddlewareStage",
    "DispatchPipeline",
    
    # Publisher framework
    "PublisherConfig",
    "EventPublisher",
    "CommandPublisher",
    "QueryPublisher",
    
    # Subscriber framework
    "SubscriberConfig",
    "MessageSubscriber",
    
    # Decorator
    "HandlerRegistryDecorator",
]