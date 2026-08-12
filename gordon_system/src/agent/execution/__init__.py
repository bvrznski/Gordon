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
        │                   # (Runtime state machines in core.lifecycle)
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

# Runtime state machines are defined in core.lifecycle and used via import
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
    ExecutionLoop as BaseExecutionLoop,  # Legacy base class
    ExecutionCycle,
    ExecutionStage,
)

# Import Loop architecture (Phase 3.10.4) - behavioral policy controller
try:
    from .loops import (
        # Modes
        LoopMode,
        # Decisions
        DecisionType,
        LoopDecision,
        ContinueDecision,
        SuspendDecision,
        AwaitInputDecision,
        CompleteDecision,
        TerminateDecision,
        RejectOutcomeDecision,
        RequestRecoveryDecision,
        DelegateDecision,
        SwitchModeDecision,
        ReplacePolicyDecision,
        # Protocol and context
        LoopPolicy,
        LoopContext,
        CycleOutcome,
        LoopState,
        # Coordinator
        ExecutionLoop,  # Canonical Loop (replaces base.ExecutionLoop)
        StandardPolicy,
        # Errors
        PolicyError,
        InvalidModeTransitionError,
    )
except ImportError:
    # Graceful fallback for import errors during development
    pass

# Import Thread architecture modules (Phase 3.10.3)
try:
    from .threads import (
        ThreadId as ThreadIdV2,  # Semantic Thread identity
        ThreadState,
        ThreadLifecycleTransitionGraph as ThreadLifecyclGraph,
        ThreadLifecycleReason,
        ThreadLifecycleTransition,
        ThreadLifecycleSnapshot,
        ThreadDelta,
        DeltaValidationResult,
        RelationshipKind,
        ThreadRelationship,
        ParentChildRelationship,
        ThreadRelationshipGraph,
        ThreadSnapshot,
    )
except ImportError:
    # Graceful fallback for import errors during development
    pass


# Exports from both sources (using alias to avoid conflict)
from .types import (
    ExecutionId as _ExecutionId,  # Keep original type export
)

from .loops import (
    # Modes
    LoopMode as _LoopMode,  # For type compatibility
)

__all__ = [
    # Types (original types from types module)
    "ExecutionId",  # via alias to avoid conflict with threads.ThreadId
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
    
    # Thread architecture (Phase 3.10.3) - semantic thread identity via threads module
    "ThreadIdV2",  # Semantic ThreadId from threads module
    "ThreadState",
    "ThreadLifecycleTransitionGraph",
    "ThreadLifecycleState",
    "ThreadDelta",
    "DeltaValidationResult",
    "RelationshipKind",
    "ThreadRelationship",
    "ParentChildRelationship",
    "ThreadSnapshot",
]
