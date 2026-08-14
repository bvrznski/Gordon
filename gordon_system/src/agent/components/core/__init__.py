# Core Runtime Infrastructure
# ============================

"""
Core runtime infrastructure for Gordon agent.

This package provides the foundational runtime substrate including:
- Lifecycle management
- Registry and dependency resolution
- Configuration handling
- Context management
- State management
- Synchronization primitives
- Execution and scheduling
- Observability and integrity validation
- Authority, continuity, causality tracking
- Provenance, lineage, obligations monitoring
- Temporal ordering and federation coordination

Phase 3.7: Third-stage runtime expansion with production-grade capabilities.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Import submodules for type checking
    from core import contracts, types, exceptions, lifecycle
    from core import registry, dependency, configuration, context
    from core import state, synchronization, execution, scheduling
    from core import observability, integrity, kernel, runtime
    from core import testing, health, failures, recovery, diagnostics

# Runtime imports for execution submodule
from .execution import (
    ExecutionState,
    TaskState,
    Priority,
    TaskId,
    TaskResult,
    ParentTaskRef,
    TaskDependencies,
    RetryPolicy,
    ExecutionTimeouts,
    TaskCleanupHook,
    TaskSpec,
    ExecutionContext,
    CancellationSource,
    CancellationToken,
    CleanupCoordinator,
    TaskEvent,
    TaskEventRecord,
    SchedulerError,
    DependencyError,
    TaskTimeoutError,
    TaskCancelledError,
)

from .execution.scheduler import (
    Scheduler,
    SchedulerConfig,
    ReadyQueue,
    WaitingQueue,
    SchedulerState,
)

# Phase 3.5 - Observability, Integrity, Health, Recovery
from .observability import RuntimeEvent, EventSeverity, EventCategory

# Phase 3.7 - Third-stage packages
from .lifecycle import (
    ThreadLifecycleState,
    CycleState,
    StateTransition,
    ThreadLifecycleTransitionGraph,
    CycleTransitionGraph,
    LifecycleTransitionRequest,
    LifecycleTransitionResult,
    ThreadLifecycleSnapshot,
    CycleLifecycleSnapshot,
)

# Phase 3.12.3 - Stream Infrastructure Package
from .streams import (
    IdentityType,
    IdentityCategory,
    IdentityId,
    StreamId,
    StreamRecordId,
    StreamGenerationId,
    StreamCursor,
    StreamCheckpoint,
    StreamPosition,
    StreamLifecycleState,
    StreamLifecycleTransitionGraph,
    StreamLifecycleTransition,
    StreamLifecycleSnapshot,
    StreamError,
    StreamNotFoundError,
    StreamClosedError,
    StreamPausedError,
    CapacityExceededError,
    StreamGenerationClosedError,
    validate_stream_id,
    validate_stream_lifecycle_transition,
    dataclass_replace,
)

from .registry import (
    RegistryEntry,
    Registry,
    ComponentRegistry,
    ServiceRegistry,
    RegistrySnapshot,
    EntityCategory,
    RuntimeRegistryEntry,
    RegistryMetadata,
    RuntimeRegistry,
    RuntimeRegistrySnapshot,
    RegistryObserver,
)

from .synchronization import (
    ShutdownSignal,
    AsyncLock,
    OnceGuard,
    BoundedSemaphore,
    GuardedResource,
)

from .executor import (
    ExecutorStatus,
    ExecutorTaskResult,
    ExecutorProtocol,
    WorkerInfo,
    WorkerPool,
    QueuedTask,
    PriorityTaskQueue,
    ExecutorError,
    ExecutorNotReadyError,
    ExecutorShutdownError,
    ThreadedExecutor,
)

from .engine import (
    EngineStatus,
    EngineExecutionContext,
    EngineExecutionResult,
    EngineContextManager,
    ResourceManagerConfig,
    ResourceManager,
    ResourceManagerAcquisition,
    EngineProtocol,
    EngineError,
    EngineNotReadyError,
    EngineShutdownError,
    ResourceError,
    ThreadedExecutionEngine,
)

from .manager import (
    ManagerStatus,
    ManagedEntity,
    EntityCollection,
    ResourcePoolConfig,
    ResourcePool,
    ResourceAcquisition,
    DependencyEdge,
    DependencyGraph,
    EntityManagerProtocol,
    SimpleEntityManager,
    ManagerError,
    ManagerNotReadyError,
)
# Phase 3.5 - Observability, Integrity, Health, Recovery
from .health import (
    HealthStatus,
    HealthProjection,
    ProbeDimension,
    ProbeSeverity,
    ProbeResult,
    HealthChecker,
    HealthAggregator,
    HealthReport,
)

from .failures import (
    FailureCategory,
    Recoverability,
    FailureRecord,
    RuntimeFailure,
    RuntimeRecoveryStrategy,
    AlertLevel,
    FailureDeduplicator,
    RuntimeFailureDeduplicator,
)

from .recovery import (
    RecoveryAction,
    RecoveryPolicy,
    RecoveryPolicyEvaluator,
    RecoveryDecision,
    RecoveryPlan,
    Precondition,
    RecoveryBudget,
    RecoveryResult,
    RecoveryExecutionResult,
    RecoveryCoordinator,
)

from .diagnostics import (
    DiagnosticCode,
    DiagnosticSeverity,
    DiagnosticRecord,
    DiagnosticReport,
    create_diagnostic_record,
    create_error_diagnostic,
    create_warning_diagnostic,
    create_critical_diagnostic,
)

# Phase 3.14.7 - Network Interaction Contracts
from .network_interactions import (
    NetworkParticipationRole,
    NetworkParticipation,
    NetworkActivationRequest,
    ActivationDecision,
    NetworkActivationResult,
    NetworkActivationContext,
    NetworkInteraction,
    NetworkInteractionObservabilityMetadata,
    NetworkActivationFailureType,
    NetworkInteractionFailure,
    dataclass_replace,
)

# Phase 3.7.22-I - Runtime State Infrastructure (canonical authorities)
from .runtime_state import (
    RuntimeState,
    RuntimeStateSnapshot,
    RuntimeStateTransition,
    RuntimeStateStore,
    RuntimeStateTruth,
)

# Third-stage packages exports
__all__ = [
    "contracts",
    "types", 
    "exceptions",
    
    # Lifecycle state machines (thread/cycle)
    "lifecycle",
    "ThreadLifecycleState", "CycleState", "StateTransition",
    "ThreadLifecycleTransitionGraph", "CycleTransitionGraph",
    "LifecycleTransitionRequest", "LifecycleTransitionResult",
    "ThreadLifecycleSnapshot", "CycleLifecycleSnapshot",
    
    # Phase 3.12.3 - Stream Infrastructure (canonical)
    "streams",
    # Stream identity types
    "IdentityType", "IdentityCategory",
    "IdentityId", "StreamId", "StreamRecordId", "StreamGenerationId",
    # Stream position and checkpoint types
    "StreamCursor", "StreamCheckpoint", "StreamPosition",
    # Stream lifecycle types (canonical)
    "StreamLifecycleState", "StreamLifecycleTransitionGraph",
    "StreamLifecycleTransition", "StreamLifecycleSnapshot",
    # Stream exceptions
    "StreamError", "StreamNotFoundError", "StreamClosedError",
    "StreamPausedError", "CapacityExceededError", 
    "StreamGenerationClosedError",
    # Stream utility functions
    "validate_stream_id", "validate_stream_lifecycle_transition",
    "dataclass_replace",
    
    # Phase 3.7+ - Registry
    "RegistryEntry", "Registry", "ComponentRegistry", "ServiceRegistry",
    "RegistrySnapshot", "EntityCategory", "RuntimeRegistryEntry",
    "RegistryMetadata", "RuntimeRegistry", "RuntimeRegistrySnapshot",
    "RegistryObserver",
    
    # Phase 3.7+ - Synchronization
    "ShutdownSignal", "AsyncLock", "OnceGuard", "BoundedSemaphore",
    "GuardedResource",
    
    # Phase 3.7+ - Execution
    "ExecutionState", "TaskState", "Priority", "TaskId", "TaskResult",
    "ParentTaskRef", "TaskDependencies", "RetryPolicy", "ExecutionTimeouts",
    "TaskCleanupHook", "TaskSpec", "ExecutionContext", "CancellationSource",
    "CancellationToken", "CleanupCoordinator", "TaskEvent", "TaskEventRecord",
    "SchedulerError", "DependencyError", "TaskTimeoutError", "TaskCancelledError",
    
    # Phase 3.7+ - Scheduling
    "Scheduler", "SchedulerConfig", "ReadyQueue", "WaitingQueue", "SchedulerState",
    
    # Phase 3.7+ - Executor
    "ExecutorStatus", "ExecutorTaskResult", "ExecutorProtocol", "WorkerInfo",
    "WorkerPool", "QueuedTask", "PriorityTaskQueue", "ExecutorError",
    "ExecutorNotReadyError", "ExecutorShutdownError", "ThreadedExecutor",
    
    # Phase 3.7+ - Engine
    "EngineStatus", "EngineExecutionContext", "EngineExecutionResult",
    "EngineContextManager", "ResourceManagerConfig", "ResourceManager",
    "ResourceManagerAcquisition", "EngineProtocol", "EngineError",
    "EngineNotReadyError", "EngineShutdownError", "ResourceError",
    "ThreadedExecutionEngine",
    
    # Phase 3.7+ - Manager
    "ManagerStatus", "ManagedEntity", "EntityCollection", "ResourcePoolConfig",
    "ResourcePool", "ResourceAcquisition", "DependencyEdge", "DependencyGraph",
    "EntityManagerProtocol", "SimpleEntityManager", "ManagerError",
    "ManagerNotReadyError",
    
    # Phase 3.7+ - Health
    "HealthStatus", "HealthProjection", "ProbeDimension", "ProbeSeverity",
    "ProbeResult", "HealthChecker", "HealthAggregator", "HealthReport",
    
    # Phase 3.7+ - Failures
    "FailureCategory", "Recoverability", "FailureRecord", "RuntimeFailure",
    "RuntimeRecoveryStrategy", "AlertLevel", "FailureDeduplicator",
    "RuntimeFailureDeduplicator",
    
    # Phase 3.7+ - Recovery
    "RecoveryAction", "RecoveryPolicy", "RecoveryPolicyEvaluator", "RecoveryDecision",
    "RecoveryPlan", "Precondition", "RecoveryBudget", "RecoveryResult",
    "RecoveryExecutionResult", "RecoveryCoordinator",
    
    # Phase 3.7+ - Diagnostics
    "DiagnosticCode", "DiagnosticSeverity", "DiagnosticRecord", "DiagnosticReport",
    "create_diagnostic_record", "create_error_diagnostic",
    "create_warning_diagnostic", "create_critical_diagnostic",
    
    # Phase 3.14.7 - Network Interaction Contracts
    "network_interactions",
    "NetworkParticipationRole",
    "NetworkParticipation",
    "NetworkActivationRequest",
    "ActivationDecision",
    "NetworkActivationResult",
    "NetworkActivationContext",
    "NetworkInteraction",
    "NetworkInteractionObservabilityMetadata",
    "NetworkActivationFailureType",
    "NetworkInteractionFailure",
    
     # New exports for Phase 3.5
     "RuntimeEvent", "EventSeverity", "EventCategory",
     
     # Phase 3.7.21 - Data Governance, Privacy, Provenance & Information Lifecycle
     "data_governance",
     
      # Phase 3.7.22-I - Runtime State Infrastructure
      "RuntimeState", "RuntimeStateSnapshot", "RuntimeStateTransition",
      "RuntimeStateStore", "RuntimeStateTruth",
      
       # Phase 3.7.36-I - Continuity Infrastructure
       "continuity",
       
       # Phase 3.14.7 - Network Interaction Contracts (canonical)
       "network_interactions",
  ]
