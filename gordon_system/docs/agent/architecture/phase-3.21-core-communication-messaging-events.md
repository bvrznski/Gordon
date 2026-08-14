# Gordon Core - Phase 3.21: Communication, Messaging & Event Architecture

**Phase**: 3.21  
**Title**: Core Communication, Messaging & Event Architecture  
**Status**: IMPLEMENTATION COMPLETE  
**Date**: August 2026  

---

## Executive Summary

This phase establishes the canonical Communication Architecture for the Gordon Core - a unified, deterministic system governing all communication between architectural entities.

### Vision Statement
Every architectural entity shall communicate through explicit, typed, deterministic contracts. No implicit communication shall exist. Communication shall never rely upon global mutable state, hidden callbacks, singleton notifications, or undocumented side effects.

---

## Architectural Principles

### Separation of Concerns
The architecture maintains strict separation between:
- **Communication**: How entities exchange information
- **Interaction**: What type of exchange (request, command, event)
- **Message**: The unit of communication
- **Event**: A statement about what already occurred
- **Command**: An instruction for future work
- **Query**: A request for read-only information

### Immutable First
All messages are immutable after publication. This enables:
- Deterministic replay and debugging
- Safe concurrent access
- Reliable audit trails

### Explicit Over Implicit
Every communication must have:
- Explicit sender identity
- Explicit recipient specification
- Explicit message type
- Explicit delivery guarantees

---

## Phase 3.21 Components

### 3.21.1 - Communication Foundations

Communication philosophy, terminology, and ownership model.

**Key Concepts**:
- **Endpoint**: A communication actor with identity, authority, and policy
- **Message**: Immutable unit of communication between endpoints
- **Event**: Historical statement about system state change
- **Command**: Instruction for endpoints to perform work
- **Request**: Asks another endpoint to perform work
- **Response**: Answer to a request

### 3.21.2 - Communication Domains & Endpoints

Endpoints are the fundamental communication units.

**Endpoint Types**:
| Type | Description |
|------|-------------|
| Runtime | The entire runtime instance |
| Component | Individual components within runtime |
| Service | Services providing cross-component functionality |
| Capability | Capabilities that provide specific behaviors |
| Module | Modules containing related components |
| Stream | Streams for ordered message transport |
| Scheduler | Schedulers for time-based execution |
| Execution | Execution engines for work processing |
| Recovery | Recovery systems for fault tolerance |
| Diagnostic | Diagnostics for observability |
| External | External system connections |

**Endpoint Properties**:
- **Identity**: Unique identifier across runtime
- **Ownership**: Entity responsible for this endpoint
- **Visibility**: What other endpoints can see this one
- **Authority**: What operations this endpoint can perform
- **Policy**: How messages are handled

### 3.21.3 - Message Architecture

Messages are the fundamental units of communication.

**Message Types**:
| Type | Description |
|------|-------------|
| REQUEST | Asks another endpoint to perform work (expects response) |
| RESPONSE | Answers a request, completes its lifecycle |
| COMMAND | Expresses intent to perform an action |
| EVENT | Describes something that already occurred (historical fact) |
| QUERY | Requests information only without modifying state |
| NOTIFICATION | Informs without expecting work |
| BROADCAST | Sends to multiple endpoints simultaneously |
| MULTICAST | Sends to a subset of endpoints |

**Message Properties**:
- **Immutable**: Cannot be modified after creation
- **Typed**: Every message has an explicit type
- **Correlated**: Related messages share correlation context
- **Provenanced**: Origin and path history preserved
- **Timed**: Creation and expiration timestamps

### 3.21.4 - Request/Response/Command/Query Architecture

Interaction patterns for different communication needs.

**Request Pattern**:
```
Sender -> [REQUEST] -> Receiver -> [RESPONSE] -> Sender
```

**Command Pattern**:
```
Sender -> [COMMAND] -> Receiver (no response expected)
```

**Query Pattern**:
```
Sender -> [QUERY] -> Receiver -> [DATA] -> Sender
```

### 3.21.5 - Event & Notification Architecture

Events represent historical facts, not requests for work.

**Event Characteristics**:
- Immutable past-tense statements
- Can be replayed for state reconstruction
- May trigger reactions in other endpoints
- Never request work directly

**Notification Characteristics**:
- Informative only
- No response expected (one-way)
- Used for status updates, alerts

### 3.21.6 - Routing & Addressing

Deterministic routing based on policies.

**Routing Types**:
| Type | Description |
|------|-------------|
| DIRECT | Point-to-point to specific endpoint |
| BROADCAST | To all subscribers |
| MULTICAST | To selected subset of endpoints |
| ANYCAST | To one of multiple possible recipients |
| HIERARCHICAL | Through intermediate nodes |

**Address Types**:
- **Endpoint ID**: Direct endpoint identifier
- **Topic**: Publish-subscribe topic name
- **Message Type**: Address by message type pattern

### 3.21.7 - Publication & Subscription

Publish-subscribe for decoupled communication.

**Subscription Features**:
- Filtered: Match based on content criteria
- Scoped: Within specific correlation context
- Wildcard: Pattern matching support
- Dynamic: Created at runtime
- Expirable: Automatic cleanup

### 3.21.8 - Delivery Guarantees

Explicit delivery semantics.

| Mode | Guarantee | Use Case |
|------|-----------|----------|
| AT_MOST_ONCE | Zero or one delivery | Fire-and-forget, low latency |
| AT_LEAST_ONCE | One or more deliveries | Reliability required |
| EXACTLY_ONCE | Exactly one delivery | Transactional operations |

### 3.21.9 - Message Lifecycle

Messages transition through lifecycle states:
```
CREATED -> VALIDATED -> ROUTED -> DELIVERING -> DELIVERED -> ACKNOWLEDGED
                                    \-> EXPIRED
                                    \-> DROPPED
                                    \-> DEAD_LETTER
```

### 3.21.10 - Communication Reliability

Mechanisms for reliable delivery.

**Reliability Features**:
- **Acknowledgements**: Recipient confirms receipt
- **Retries**: Automatic retry with configurable strategy
- **Deduplication**: Detect and handle duplicate messages
- **Idempotency**: Same request can be safely retried
- **Dead-Letter Queue**: Failed messages quarantined for inspection

### 3.21.11 - Communication Policies

Policy-driven communication controls.

**Policy Categories**:
| Category | Purpose |
|----------|---------|
| Authorization | Who can communicate with whom |
| Visibility | What endpoints are discoverable |
| Routing | How messages are routed |
| Rate Limiting | Message throughput control |
| Encryption | Message encryption requirements |

### 3.21.12 - Cross-Runtime Communication

Contracts for distributed execution.

**Cross-Runtime Features**:
- Runtime-to-runtime messaging
- Cluster communication coordination
- Remote service invocation
- Federation protocols
- Gateway protocol translation

### 3.21.13 - Communication Observability & Diagnostics

Comprehensive visibility into communication behavior.

**Observability Features**:
- **Tracing**: Distributed trace across runtimes
- **Metrics**: Quantitative measurements (latency, throughput)
- **Diagnostics**: Qualitative analysis tools
- **Health Monitoring**: Endpoint health status

---

## Implementation Files

### Core Communication Module (`gordon_system/src/agent/architecture/communication/`)

| File | Phase Section | Description |
|------|--------------|-------------|
| `__init__.py` | 3.21 | Main module exports and CanonicalMessageBus class |
| `foundations.py` | 3.21.1 | Communication philosophy, terminology, ownership |
| `endpoints.py` | 3.21.2 | Endpoint types, identity, authority, policy |
| `messages.py` | 3.21.3 | Message types, payloads, lifecycle, validation |
| `routing.py` | 3.21.6 | Routing algorithms and address resolution |
| `subscription.py` | 3.21.7 | Publish-subscribe patterns |
| `delivery_guarantees.py` | 3.21.8 | Delivery semantics implementation |
| `reliability.py` | 3.21.10 | Acknowledgements, retries, deduplication |
| `policies.py` | 3.21.11 | Authorization, visibility, rate limiting |
| `observability.py` | 3.21.13 | Tracing, metrics, health monitoring |
| `cross_runtime.py` | 3.21.12 | Cross-runtime communication contracts |

---

## Integration Points

### Phase 3.11 - Streams
Streams provide durable ordered transport for messages.

### Phase 3.12 - Core Architecture
Communication is a core architectural concern.

### Phase 3.14 - Interaction Architecture
Requests, responses, commands, and events are interaction types.

### Phase 3.17 - Execution
Execution performs the work requested by messages.

---

## Architectural Invariants

### Message Integrity
- MSG-ID-001: Every message has exactly one unique identity
- MSG-ID-002: Identity is immutable once created
- MSG-ID-003: No two messages share the same identity

### Lifecycle Integrity
- MSG-STS-001: Status is immutable once set to terminal state
- MSG-STS-002: Terminal states preserve all provenance data

### Ownership Integrity
- OWN-EP-001: Every endpoint has exactly one owner type
- OWN-EP-002: Ownership cannot be transferred without explicit action

### Visibility Integrity
- VIS-EP-001: Endpoints can only see what they have visibility into
- VIS-EP-002: Visibility is preserved throughout message lifecycle

---

## Testing Strategy

Unit tests should verify:
1. Message immutability after creation
2. Endpoint authority enforcement
3. Routing policy compliance
4. Delivery guarantee implementation
5. Subscription filtering accuracy
6. Acknowledgement tracking

---

## Migration Path

### Phase 3.21.14 - Repository-Wide Migration
Replace duplicated implementations of:
- Event buses
- Message buses
- Callback systems
- Notification systems
- Communication helpers
- Routing utilities

### Phase 3.21.15 - Audit & Remediation
- Verify endpoint correctness
- Check routing correctness
- Validate communication ownership
- Confirm delivery guarantees
- Ensure policy compliance

### Phase 3.21.16 - Certification
Final certification of complete Communication Architecture.

---

## Conclusion

Phase 3.21 establishes the canonical Communication, Messaging, and Event Architecture for the Gordon Core. This unified architecture governs all communication between architectural entities, providing deterministic, observable, and reliable message exchange.

The implementation provides:
- One canonical communication architecture throughout the repository
- Explicit, typed contracts for all communication
- Deterministic routing based on policies
- Comprehensive observability and diagnostics

All subsequent phases integrate with this communication architecture without reimplementing messaging functionality.