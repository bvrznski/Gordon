# Phase 3.8.12 - Runtime Contract Matrix

## Overview

This document defines the canonical runtime contract matrix for Gordon Core interfaces.

Each row represents a stable runtime boundary that enables:
1. Dependency inversion
2. Backend independence
3. Testability through mocking
4. Replacement of implementations without affecting consumers

---

## Core Interface Contracts

| Contract | File | Owner | Stability | Status |
|----------|------|-------|-----------|--------|
| `ILifecycleController` | lifecycle.py | core/lifecycle | STABLE | Implemented |
| `IComponent` | component.py | core/component | STABLE | Implemented |
| `ILifecycleComponent` | component.py | core/component | STABLE | Implemented |
| `IEventBus` | events.py | core/events | STABLE | Implemented |
| `IConfigurationProvider` | configuration.py | core/configuration | PARTIAL | Implemented |
| `IPersistenceStore` | persistence.py | core/persistence | STABLE | Implemented |
| `IScheduler` | scheduling.py | core/scheduling | STABLE | Implemented |
| `IHealthChecker` | health.py | core/health | STABLE | Implemented |
| `IIntegrityVerifier` | integrity.py | core/integrity | STABLE | Implemented |
| `IRegistry` | registry.py | core/registry | PARTIAL | Implemented |

---

## Contract Families

### 1. Lifecycle Family

**Purpose**: Define component lifecycle state transitions as a stable runtime boundary.

**Key Contracts**:
- `ILifecycleController`: Manages state transitions
- `IComponentLifecycle`: Components that have lifecycle management
- `LifecycleState`: Canonical states (created, initializing, ready, running, stopped, failed)

**Benefits**:
- Enables async lifecycle management
- Allows different implementations (thread-based, event-driven)
- Supports graceful shutdown semantics

### 2. Component Family

**Purpose**: Define what makes something a "component" in the Gordon runtime.

**Key Contracts**:
- `IComponent`: Base interface for all runtime entities
- `ILifecycleComponent`: Components with lifecycle support
- `IManagedComponent`: Framework-managed components
- `ComponentId`: Unique entity identifier

**Benefits**:
- Uniform component discovery and management
- Enables dependency injection patterns
- Supports hot-reload scenarios

### 3. Events Family

**Purpose**: Define event publishing and subscription semantics.

**Key Contracts**:
- `IEventPublisher`: Publish events without knowing subscribers
- `IEventSubscriber`: Subscribe to events without knowing publishers
- `IEventBus`: Combined publisher/subscriber interface
- `TopicExpression`: Topic matching with wildcards

**Benefits**:
- Complete decoupling between producers and consumers
- Multiple delivery semantics (fire-and-forget, at-least-once)
- Scalable event routing

### 4. Configuration Family

**Purpose**: Enable multiple configuration backends.

**Key Contracts**:
- `IConfigurationSource`: Individual config source (file, env, remote)
- `IConfigurationProvider`: Aggregates sources with override semantics

**Benefits**:
- Support file, environment, and remote configuration
- Hot-reload capability
- Layered configuration with precedence rules

### 5. Persistence Family

**Purpose**: Define storage backend interface.

**Key Contracts**:
- `IPersistenceStore`: Backend storage operations
- `IPersistenceRepository`: Type-safe repository pattern
- `RecordId`: Unique record identifier

**Benefits**:
- Memory, file, and database backends can be swapped
- Transaction support
- Query optimization per backend

### 6. Scheduling Family

**Purpose**: Define task scheduling semantics.

**Key Contracts**:
- `IScheduler`: Schedule management interface
- `ScheduledTask`: Tracking of scheduled work
- `ScheduleType`: ONCE, FIXED_RATE, CRON, DELAYED

**Benefits**:
- Different scheduling algorithms possible
- Decoupled from execution
- Flexible timing patterns

### 7. Health Family

**Purpose**: Define health check semantics.

**Key Contracts**:
- `IHealthChecker`: Perform component health checks
- `IHealthRegistry`: Store and query health state
- `HealthStatus`: HEALTHY, DEGRADED, FAILED, UNKNOWN

**Benefits**:
- Non-blocking health verification
- System-wide health visibility
- Enables automatic remediation

### 8. Integrity Family

**Purpose**: Define data integrity verification.

**Key Contracts**:
- `IIntegrityVerifier`: Compute and verify checksums
- `IIntegrityStore`: Store integrity records
- `IntegrityResult`: Verification results

**Benefits**:
- Multiple hash algorithms supported
- Tamper detection
- Audit trail of integrity checks

### 9. Registry Family

**Purpose**: Define entity registration and discovery.

**Key Contracts**:
- `IRegistry`: Register and query entities
- `EntityRecord`: Entity metadata
- `IRegistryObserver`: Observe registry changes

**Benefits**:
- Single source of truth for component metadata
- Efficient lookup without deep introspection
- Dynamic discovery

---

## Runtime Contract Principles

### 1. Behavioral Contracts Only

Each interface defines WHAT a component does, not HOW it does it.

```python
# Correct - behavioral contract
async def publish(self, envelope: EventEnvelope) -> bool:
    """Publish an event to all interested subscribers."""
    ...

# Incorrect - implementation detail
async def _publish_to_subscribers_with_retry_and_backoff(
    self,
    envelope: EventEnvelope,
) -> bool:
    ...
```

### 2. Backend Independence

Interfaces must work regardless of the underlying implementation:

- In-memory or database-backed
- Thread-based or async
- Synchronous or asynchronous
- Single-process or distributed

### 3. Testability

Every interface should be easily mockable:

```python
# Easy to test - use interface
class MyComponent:
    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
    
    async def do_work(self) -> None:
        # Use the interface directly
        await self._event_bus.publish(...)
```

### 4. No Hidden Dependencies

Interfaces should not rely on hidden service locators or global state:

```python
# Correct - explicit dependency
async def __init__(self, store: IPersistenceStore):
    self._store = store

# Incorrect - hidden dependency
async def __init__(self):
    self._store = get_persistence_store()  # No!
```

### 5. Immutability Where Possible

Prefer immutable data structures:

```python
@dataclass(frozen=True)
class EventEnvelope:
    """Immutable envelope wrapping an event."""
    event_id: str
    event_type: str
    timestamp_utc: float
    ...
```

---

## Contract Versioning

- All interfaces are versioned with the core release (currently 3.8.12)
- Breaking changes require a major version bump
- Non-breaking additions can be minor version bumps
- Interfaces should be backward compatible where possible

---

## Migration Path

### Phase 1: Interface Definition (COMPLETE)

- [x] Define interface contracts
- [x] Document behavioral semantics
- [ ] Create test suites for each interface

### Phase 2: Implementation

- [ ] Implement MessageBus with IEventBus contract
- [ ] Implement ConfigurationProvider with(IConfigurationProvider)
- [ ] Implement Executor with IExecutor (if needed)
- [ ] Implement Registry with IRegistry contract

### Phase 3: Migration

- [ ] Update existing implementations to use interfaces
- [ ] Add compatibility shims where needed
- [ ] Remove duplicate contracts

### Phase 4: Documentation

- [ ] Complete interface documentation
- [ ] Create example implementations
- [ ] Write migration guides

---

## Contract Quality Checklist

Each contract passes these checks:

| Check | Status | Notes |
|-------|--------|-------|
| Single Responsibility | ✅ | Each interface has one clear purpose |
| Backend Independent | ✅ | Works with any underlying implementation |
| Minimal Surface Area | ✅ | Only essential methods defined |
| Well Documented | ✅ | Docstrings explain behavior and contracts |
| Easily Mockable | ✅ | Protocol-based, no hidden dependencies |
| Stable Semantics | ✅ | Runtime semantics unchanged from existing code |

---

## Dependencies

```
┌─────────────────┐
│  core/interfaces │
└────────┬────────┘
         │
    ┌────┴──────┐
    ▼           ▼
┌────────┐  ┌──────────┐
│events.py│ │component.py│
└────────┘  └────────────┘
```

---

## See Also

- [Interface Inventory Report](phase-3.8.12-interface-inventory.md)
- [Resource Interface Specification](../../resources/interfaces.py)