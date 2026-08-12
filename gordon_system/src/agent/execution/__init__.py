# Agent Execution Architecture
# ===========================

"""
Agent execution provides the behavioral organization of the autonomous agent.

Execution is NOT:
    - Cognition (that belongs to cognition subsystem)
    - Runtime infrastructure (that belongs to Core)
    - Scheduling (that belongs to Core)
    - Resource arbitration (that belongs to Core)

Execution IS:
    - Behavioral continuity across bounded semantic passes
    - Thread lifecycle management
    - Cycle selection policy
    - Semantic state projection

Architecture Layers:

    Cognition / Memory / Perception / Planning / Action
                        │
                        ▼
                 agent.execution  ← This module
                        │
                        ▼
              core.contracts / interfaces
                        │
                        ▼
               core runtime services

Canonical Structure:

    src/agent/execution/
        ├── types/          # Neutral value types and identifiers
        ├── contracts/      # Core boundary protocols
        ├── lifecycle/      # State machines and transitions
        ├── registry/       # Unit type registries
        ├── base.py         # Base classes and protocols
        ├── threads/        # Concrete thread implementations (future)
        ├── loops/          # Concrete loop implementations (future)
        └── cycles/         # Concrete cycle implementations (future)

Ownership Model:

    Thread: semantic continuity, identity, completion intent
    Loop: repetition policy, cycle selection decision
    Cycle: finite semantic pass, stage progression

Core Contracts Used:

    - ExecutableUnit: Core can invoke this generically
    - LifecyclePort: Express lifecycle intent
    - ExecutionRuntimePort: Submit execution work
    - CheckpointPort: Save/restore state
    - ObservabilityPort: Emit trace records

Architectural Laws:

    LAW-001: No thread may invoke another thread directly
    LAW-002: A cycle must not depend on global state beyond declared context
    LAW-003: Loops must not own scheduling infrastructure

For detailed documentation, see the submodules and architecture documents.
"""

from .types import (
    ExecutionId,
    ThreadId,
    LoopId,
    CycleId,
    StageId,
    CheckpointId,
    CorrelationId,
    ExecutionIdentifier,
    ExecutionState,
    LifecycleState,
    CycleResult,
    Priority,
    ResourceBudget,
    CancellationReason,
    CancellationView,
    Timestamp,
)

from .types.failures import (
    FailureCategory,
    ContractFailure,
    ExecutionRejected,
    ExecutionUnavailable,
    LifecycleConflict,
    InvalidTransition,
    CheckpointUnavailable,
    CheckpointCorrupted,
    RecoveryUnavailable,
    ResourceDenied,
    ResourceRevoked,
    ExecutionTimedOut,
    ContractViolation,
    SerializationFailure,
)

from .contracts import (
    ExecutableUnit,
    RuntimeExecutionContext,
    ExecutionOutcome,
    ExecutionStatus,
    ExecutionRequest,
    ExecutionHandle,
    LifecyclePort,
    ExecutionRuntimePort,
    CheckpointPort,
    CancellationView as CancellationViewContract,
    ObservabilityPort,
    ExecutionFactoryPort,
    SemanticSnapshot,
    ContinuationDescriptor,
    CheckpointReference,
)

from ..components.core.lifecycle import (
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

from .registry import (
    ExecutionUnitType,
    UnitDescriptor,
    ExecutionRegistry,
    get_registry,
    reset_registry,
)

from .base import (
    ExecutionThread,
    ExecutionLoop,
    ExecutionCycle,
    ExecutionStage,
)


__all__ = [
    # Types
    "ExecutionId",
    "ThreadId",
    "LoopId",
    "CycleId",
    "StageId",
    "CheckpointId",
    "CorrelationId",
    "ExecutionIdentifier",
    "ExecutionState",
    "LifecycleState",
    "CycleResult",
    "Priority",
    "ResourceBudget",
    "CancellationReason",
    "CancellationView",
    "Timestamp",
    
    # Failures
    "FailureCategory",
    "ContractFailure",
    "ExecutionRejected",
    "ExecutionUnavailable",
    "LifecycleConflict",
    "InvalidTransition",
    "CheckpointUnavailable",
    "CheckpointCorrupted",
    "RecoveryUnavailable",
    "ResourceDenied",
    "ResourceRevoked",
    "ExecutionTimedOut",
    "ContractViolation",
    "SerializationFailure",
    
    # Contracts
    "ExecutableUnit",
    "RuntimeExecutionContext",
    "ExecutionOutcome",
    "ExecutionStatus",
    "ExecutionRequest",
    "ExecutionHandle",
    "LifecyclePort",
    "ExecutionRuntimePort",
    "CheckpointPort",
    "CancellationViewContract",
    "ObservabilityPort",
    "ExecutionFactoryPort",
    "SemanticSnapshot",
    "ContinuationDescriptor",
    "CheckpointReference",
    
    # Lifecycle
    "ThreadLifecycleState",
    "CycleState",
    "StateTransition",
    "ThreadLifecycleTransitionGraph",
    "CycleTransitionGraph",
    "LifecycleTransitionRequest",
    "LifecycleTransitionResult",
    "ThreadLifecycleSnapshot",
    "CycleLifecycleSnapshot",
    
    # Registry
    "ExecutionUnitType",
    "UnitDescriptor",
    "ExecutionRegistry",
    "get_registry",
    "reset_registry",
    
    # Base classes
    "ExecutionThread",
    "ExecutionLoop",
    "ExecutionCycle",
    "ExecutionStage",
]