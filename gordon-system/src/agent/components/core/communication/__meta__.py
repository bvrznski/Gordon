# Core Communication Package Metadata
# ====================================

"""
Package: src.agent.components.core.communication
Phase: 3.8.1 - Canonical Communication Runtime

This module provides the canonical local communication infrastructure for Gordon.

ARCHITECTURAL OWNERSHIP
-----------------------

The communication package is responsible for:

Infrastructure:
    - Typed message contracts (commands, queries, events, requests)
    - Message envelopes with transport metadata
    - Handler registration and dispatch
    - Routing and delivery semantics
    - Request-response correlation with bounded cleanup
    - Local in-process transport with bounded queues

NOT RESPONSIBLE FOR:
    - Cognition, reasoning, or planning
    - Business logic implementation
    - State ownership (only transports state changes)
    - Task scheduling (uses existing scheduler)
    - Service registration (uses existing registry)

PUBLIC API CATEGORIES
---------------------

Contracts (immutable data structures):
    - Command: Request for state-changing operation (single handler)
    - Query: Request for information (may have multiple handlers)
    - Event: Report of completed fact (published to subscribers)
    - Request/Response: Typed request-response with correlation

Identities:
    - CommandId, QueryId, RequestId, ResponseId
    - HandlerId, MiddlewareId

Metadata:
    - CommandMetadata, QueryMetadata, RequestMetadata
    - HandlerMetadata, MiddlewareContext

Results:
    - CommandResult, QueryResult, HandlerResult, MiddlewareResult
    - DeliveryResult (local transport)

Infrastructure:
    - LocalTransport: In-process message delivery
    - HandlerRegistry: Handler registration with lifecycle support
    - HandlerChain: Middleware chain for cross-cutting concerns
    - PendingRequestRegistry: Bounded request tracking

Middleware:
    - ValidationMiddleware, AuthorizationMiddleware, TracingMiddleware
    - DeadLetterMiddleware, RateLimitMiddleware, EnrichmentMiddleware

LIFECYCLE
---------

The communication runtime requires explicit lifecycle management:

1. Construct with configuration
2. Start transport (enables message delivery)
3. Register handlers (for commands, queries)
4. Send/publish messages (delivered to handlers)
5. Stop transport (waits for in-flight work)

LIFECYCLE STATES:
    - CREATED: Initial state, no workers running
    - STARTING: Transport initialization
    - RUNNING: Accepting and delivering messages
    - STOPPING: Graceful shutdown, draining queue
    - STOPPED: All workers finished

DELIVERY SEMANTICS (Local Transport)
------------------------------------

The local transport provides:

Bounded Operation:
    - Fixed-size queues (never grow unbounded)
    - Backpressure via queue full handling
    - Dead-letter storage for undeliverable messages

Delivery Modes:
    - SYNCHRONOUS: Block until handler completes (single handler)
    - ASYNCHRONOUS: Fire-and-forget to worker queue (fan-out)
    - IMMEDIATE: Execute without queuing (direct call)

Reliability:
    - Retry on transient failures with exponential backoff
    - Dead-letter for permanent failures after max retries
    - Cleanup of pending requests on shutdown

ORDERING GUARANTEES
-------------------

Within a single message stream (per handler):
    - FIFO ordering preserved
    - Concurrent handlers may execute out of order
    - Per-correlation-id ordering via trace context

No global ordering:
    - Different message types can interleave
    - Different handlers can process concurrently

BACKPRESSURE BEHAVIOR
---------------------

When queue is at capacity:
    1. New messages rejected (QueueFullError)
    2. Existing queued messages processed first
    3. Backpressure propagates to sender

SHUTDOWN BEHAVIOR
-----------------

On transport.stop():
    1. No new messages accepted
    2. Wait for in-flight work to complete
    3. Drain queue (process remaining messages)
    4. Cancel pending requests with timeout
    5. Report any unresolved communication

DEPENDENCIES
------------

Core:
    - threading: Synchronization primitives
    - asyncio: Async dispatch workers
    - dataclasses: Immutable contracts
    - enum: Type classification

Optional:
    - failure/events: Integration with failure events (Phase 3.7.27)

EXTENSION POINTS
----------------

Future distributed extension can use:

1. Transport interface:
   - LocalTransport implements LocalDeliveryProtocol
   - RemoteTransport can implement same protocol
   - Swap transport without changing caller code

2. Serialization layer:
   - Envelopes are serializable (no runtime objects)
   - Network transport can serialize/deserialize
   - Contract versions for backward compatibility

3. Middleware chain:
   - Add/remove middleware at runtime
   - Cross-cutting concerns via middleware
   - Custom validation/authorization policies

IMPLEMENTATION STATUS
---------------------

Phase 3.8.1 - Implementation Complete:

✓ Command contracts (single handler semantics)
✓ Query contracts (multiple handler support)
✓ Request-Response correlation with bounded cleanup
✓ Handler registries with lifecycle ownership
✓ Middleware chain for cross-cutting concerns
✓ Local transport with bounded queues
✓ Dead-letter handling for undeliverable messages
✓ Backpressure via bounded queue capacity
✓ Synchronous and asynchronous delivery modes
✓ Integration hooks (no breaking changes)

Remaining (Phase 3.9.x):
    - Distributed transport adapter
    - Full serialization support
    - Cross-runtime correlation propagation
"""

# Package metadata
PACKAGE_NAME = "src.agent.components.core.communication"
PHASE_VERSION = "3.8.1"

# API version for compatibility tracking
API_VERSION = (1, 0, 0)  # major.minor.patch

# Status
STATUS = "PRODUCTION"  # DRAFT, BETA, PRODUCTION, DEPRECATED