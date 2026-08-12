# Core Runtime Interfaces
# =======================

"""
Canonical Runtime Contracts for Gordon Core - Phase 3.8.12

This module defines the canonical interface contracts that represent stable
runtime boundaries between subsystems. These interfaces define HOW the runtime
operates, not WHAT the agent does.

ARCHITECTURAL PRINCIPLES:
- Interfaces represent stable behavioral boundaries, not organizational convenience
- Consumers depend on interfaces; implementations depend on Core primitives
- No circular interface ownership
- Minimal surface area with maximum flexibility for implementation
- Each interface has one responsibility and clear ownership

INTERFACE FAMILIES:

lifecycle.py     - Component lifecycle state transitions
component.py     - Base component contract for all runtime entities
service.py       - Service abstraction (long-running background processes)
daemon.py        - Daemon abstraction ( autonomous background workers)
execution.py     - Task execution contracts
scheduling.py    - Scheduling and timing contracts
communication.py - Inter-component communication protocols
events.py        - Event bus protocol
state.py         - State store protocols
registry.py      - Entity registry protocols
providers.py     - Provider interface abstractions
plugins.py       - Plugin loading and lifecycle
configuration.py - Configuration source abstractions
persistence.py   - Persistence provider contracts
resources.py     - Resource management abstractions (see resources/interfaces.py)
health.py        - Health check contracts
integrity.py     - Integrity verification contracts
observability.py - Observability instrumentation contracts
security.py      - Security boundary contracts

EXCLUSION CRITERION:
The following domain concepts are NEVER in Core:
- cognition, planning, reasoning, memory semantics
- identity, goals, values, emotions, imagination
- perception semantics, world modelling
"""

from .__meta__ import VERSION, __version__

# Lifecycle interfaces
from .lifecycle import (
    LifecycleState,
    LifecycleEvent,
    ILifecycleController,
    IComponentLifecycle,
    LifecycleTransitionError,
    _VALID_TRANSITIONS,
)

# Component interfaces
from .component import (
    ComponentId,
    ComponentMetadata,
    IComponent,
    ILifecycleComponent,
    IManagedComponent,
    IComponentFactory,
    ComponentCreationError,
)

# Events interfaces
from .events import (
    DeliveryMode,
    TopicExpression,
    SubscriptionDescriptor,
    EventEnvelope,
    IEventPublisher,
    IEventSubscriber,
    IEventRegistry,
    IEventBus,
)

# Configuration interfaces
from .configuration import (
    ConfigValueType,
    ConfigEntry,
    IConfigurationSource,
    IConfigurationProvider,
    ConfigurationError,
    MissingConfigurationError,
)

# Persistence interfaces
from .persistence import (
    RecordId,
    PersistenceOperation,
    PersistenceResult,
    IPersistenceStore,
    IPersistenceRepository,
    PersistenceError,
    RecordNotFoundError,
    OptimisticLockError,
)

# Scheduling interfaces
from .scheduling import (
    ScheduleType,
    Schedule,
    ScheduledTask,
    IScheduler,
    ISchedulerListener,
    SchedulingError,
    DuplicateScheduleError,
    UnknownScheduleError,
)

# Health interfaces
from .health import (
    HealthStatus,
    HealthCheckResult,
    IHealthChecker,
    IHealthRegistry,
    IHealthObserver,
    HealthCheckError,
    ComponentUnhealthyError,
)

# Integrity interfaces
from .integrity import (
    IntegrityAlgorithm,
    IntegrityResult,
    IntegrityRecord,
    IIntegrityVerifier,
    IIntegrityStore,
    IIntegrityObserver,
    IntegrityError,
    HashMismatchError,
)

# Registry interfaces
from .registry import (
    EntityRecord,
    IRegistry,
    IRegistryObserver,
    RegistryError,
    EntityNotFoundError,
)

__all__ = [
    # Version info
    "VERSION",
    "__version__",
    
    # Lifecycle
    "LifecycleState",
    "LifecycleEvent",
    "ILifecycleController",
    "IComponentLifecycle",
    "LifecycleTransitionError",
    "_VALID_TRANSITIONS",
    
    # Component
    "ComponentId",
    "ComponentMetadata",
    "IComponent",
    "ILifecycleComponent",
    "IManagedComponent",
    "IComponentFactory",
    "ComponentCreationError",
    
    # Events
    "DeliveryMode",
    "TopicExpression",
    "SubscriptionDescriptor",
    "EventEnvelope",
    "IEventPublisher",
    "IEventSubscriber",
    "IEventRegistry",
    "IEventBus",
    
    # Configuration
    "ConfigValueType",
    "ConfigEntry",
    "IConfigurationSource",
    "IConfigurationProvider",
    "ConfigurationError",
    "MissingConfigurationError",
    
    # Persistence
    "RecordId",
    "PersistenceOperation",
    "PersistenceResult",
    "IPersistenceStore",
    "IPersistenceRepository",
    "PersistenceError",
    "RecordNotFoundError",
    "OptimisticLockError",
    
    # Scheduling
    "ScheduleType",
    "Schedule",
    "ScheduledTask",
    "IScheduler",
    "ISchedulerListener",
    "SchedulingError",
    "DuplicateScheduleError",
    "UnknownScheduleError",
    
    # Health
    "HealthStatus",
    "HealthCheckResult",
    "IHealthChecker",
    "IHealthRegistry",
    "IHealthObserver",
    "HealthCheckError",
    "ComponentUnhealthyError",
    
    # Integrity
    "IntegrityAlgorithm",
    "IntegrityResult",
    "IntegrityRecord",
    "IIntegrityVerifier",
    "IIntegrityStore",
    "IIntegrityObserver",
    "IntegrityError",
    "HashMismatchError",
    
    # Registry
    "EntityRecord",
    "IRegistry",
    "IRegistryObserver",
    "RegistryError",
    "EntityNotFoundError",
]