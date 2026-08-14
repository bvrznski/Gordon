# Agent Execution Architecture (Phase 3.10.8)
# ===========================================

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
                 agent.execution  ← This module (Phase 3.10.8)
                        │
                        ▼
              core.contracts / interfaces
                        │
                        ▼
             core runtime services

Canonical Structure:

    src/agent/execution/
        ├── __init__.py         # Package exports
        ├── __meta__.py         # Metadata
        ├── __tree__.py         # Tree structure documentation
        │
        ├── types/              # Neutral value types and identifiers
        ├── contracts/          # Core boundary protocols  
        ├── registry/           # Unit type registries
        ├── threads/            # Thread implementations (long-lived semantic activity)
        ├── loops/              # Loop policy implementations (continuation policy)
        ├── cycles/             # Cycle definitions (finite semantic progressions)
        └── streams/            # Stream implementations (ordered information flow)

Ownership Model:

    Thread: semantic continuity, identity, completion intent
    Loop: repetition policy, cycle selection decision, continuation policy  
    Cycle: finite semantic pass, stage progression
    Stream: ordered semantic information flow between producers and consumers

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
    LAW-004: Streams represent semantic information flow, not runtime mechanics

For detailed documentation, see the submodules and architecture documents.
"""

# =============================================================================
# CANONICAL EXECUTION STRUCTURE (Phase 3.10.8)
# =============================================================================

from .types import (
    AdvancementLease,
    LeaseAcquisitionResult,
    CancellationSource,
    CancellationReason,
    CancellationRequest,
    CancellationToken,
    ExecutionCancelledError,
    CancellationOutcome,
    ExecutionInterruptionType,
    InterruptionRequest,
    InterruptionOutcome,
    ExecutionThreadId,
    ExecutionLoopId,
    ExecutionLoopDecisionId,
    ExecutionCycleId,
    ExecutionStageId,
    ExecutionThreadKind,
    ExecutionThreadStatus,
    is_terminal_status,
    get_allowed_transitions,
    ExecutionThreadPurpose,
    ExecutionObjectiveStatus,
    ExecutionThreadObjective,
    ExecutionArtifactReference,
    ExecutionParticipantReference,
    ExecutionPlanReference,
    ExecutionMonitoringTarget,
    ExecutionObservationReference,
    ExecutionAlertCondition,
    ExecutionConversationThreadState,
    ExecutionTaskThreadState,
    ExecutionMonitoringThreadState,
    ExecutionInternalThreadState,
    ExecutionThreadState,
    ExecutionThreadTerminalReason,
    ExecutionState,
    LifecycleState,
    ExecutionCycleResult,
    ExecutionPriority,
    ExecutionResourceBudget,
    ExecutionCancellationReason,
    ExecutionCancellationView,
    ExecutionTimestamp,
)

from .checkpoint import (
    CycleCheckpoint,
    CycleResumptionDescriptor,
    CheckpointValidationResult,
    CheckpointValidation,
)

from .events import (
    ExecutionEventType,
    EventCorrelation,
    EventCorrelationContext,
    ExecutionEvent,
)

from .failures_extended import (
    ExecutionFailureCategory,
    ExecutionFailureLayer,
    ExecutionFailure,
    classify_failure,
    is_retryable,
)

# =============================================================================
# THREADS PACKAGE
# =============================================================================

from .threads import (
    ThreadId,
    ThreadLifecycleState,
    ThreadLifecycleTransitionGraph,
    ThreadLifecycleReason,
    ThreadLifecycleSnapshot,
    ThreadLifecycleTransitionRequest,
    ThreadLifecycleTransitionResult,
    ThreadSemanticDelta as ThreadDelta,
    DeltaValidationResult,
    ThreadDeltaBatch,
    DeltaApplicationResult,
    ThreadDeltaValidator,
    RelationshipKind,
    ThreadRelationship,
    ParentChildRelationship,
    ThreadRelationshipGraph,
    ThreadRelationshipSnapshot,
    SnapshotClass as ExecutionThreadSnapshot,
    ExecutionThread,
    ExecutionLoopId,  # Alias
    ExecutionCycleId,  # Alias
)

# Backward compatibility
Thread = ExecutionThread

from .threads.concrete import (
    ConversationPurpose,
    ConversationParticipant,
    ConversationState,
    ConversationThread,
    ConversationSnapshot,
    TaskStatus,
    TaskConstraints,
    TaskPlan,
    TaskProgress,
    TaskState,
    TaskThread,
    TaskSnapshot,
    ObservationType,
    MonitoringTarget,
    Baseline,
    MonitoringState,
    MonitoringThread,
    MonitoringSnapshot,
    InternalPurpose,
    InternalContext,
    InternalState,
    InternalThread,
    InternalSnapshot,
)

# =============================================================================
# LOOPS PACKAGE
# =============================================================================

from .loops import (
    LoopKind,
    BehavioralMode,
    DecisionType,
    ExecutionLoopDecision,
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
    LoopPolicy,
    LoopContext,
    CycleOutcome as LoopCycleOutcome,
    LoopState,
    ExecutionLoop,
    StandardPolicy,
    PolicyError,
    InvalidModeTransitionError,
)

from .loops.concrete import (
    ConversationBehavior,
    ConversationPolicyState,
    ConversationPolicy,
    create_conversation_policy,
    TaskBehavior,
    TaskPolicyState,
    TaskPolicy,
    create_task_policy,
    PlanningPolicyState,
    PlanningPolicy,
    create_planning_policy,
    MonitoringPolicyState,
    MonitoringPolicy,
    create_monitoring_policy,
    RecoveryPolicyState,
    RecoveryPolicy,
    create_recovery_policy,
    IdleBehavior,
    IdlePolicyState,
    IdlePolicy,
    create_idle_policy,
)

# =============================================================================
# CYCLES PACKAGE
# =============================================================================

from .cycles import (
    CycleProgressionState,
    StageProgressionState,
    CycleOutcomeStatus,
    CycleIdentity,
    ThreadReference,
    LoopDecisionReference,
    StageDefinition as CycleStageDefinition,
    StageDefinitionValidation as CycleStageDefinitionValidation,
    CycleDefinition,
    CycleDefinitionValidation,
    CycleContext,
    StageResult as CycleStageResult,
    SemanticDelta as CycleSemanticDelta,
    DeltaValidationResult as CycleDeltaValidationResult,
    CycleOutcome,
    CycleInterruptionReason,
    CycleValidationResult,
    validate_cycle_ownership,
)

from .cycles.concrete import (
    InterpretationStage,
    InterpretationCycle,
    ResponseStage,
    ResponseCycle,
    PlanningStage,
    PlanningCycle,
    ExecutionStage,
    ExecutionCycle,
    EvaluationStage,
    EvaluationCycle,
    ObservationStage,
    ObservationCycle,
    ReflectionStage,
    ReflectionCycle,
    create_cycle_from_kind,
)

# =============================================================================
# STREAMS PACKAGE
# =============================================================================

# Streams - semantic information flow domains (will be populated as needed)
from . import streams  # noqa: F401

__all__ = (
    [
        "AdvancementLease",
        "LeaseAcquisitionResult",
        "CancellationSource",
        "CancellationReason",
        "CancellationRequest",
        "CancellationToken",
        "ExecutionCancelledError",
        "CancellationOutcome",
        "ExecutionInterruptionType",
        "InterruptionRequest",
        "InterruptionOutcome",
        "ExecutionThreadId",
        "ExecutionLoopId",
        "ExecutionLoopDecisionId",
        "ExecutionCycleId",
        "ExecutionStageId",
        "ExecutionThreadKind",
        "ExecutionThreadStatus",
        "is_terminal_status",
        "get_allowed_transitions",
        "ExecutionThreadPurpose",
        "ExecutionObjectiveStatus",
        "ExecutionThreadObjective",
        "ExecutionArtifactReference",
        "ExecutionParticipantReference",
        "ExecutionPlanReference",
        "ExecutionMonitoringTarget",
        "ExecutionObservationReference",
        "ExecutionAlertCondition",
        "ExecutionConversationThreadState",
        "ExecutionTaskThreadState",
        "ExecutionMonitoringThreadState",
        "ExecutionInternalThreadState",
        "ExecutionThreadState",
        "ExecutionThreadTerminalReason",
        "ExecutionState",
        "LifecycleState",
        "ExecutionCycleResult",
        "ExecutionPriority",
        "ExecutionResourceBudget",
        "ExecutionCancellationReason",
        "ExecutionCancellationView",
        "ExecutionTimestamp",
        "CycleCheckpoint",
        "CycleResumptionDescriptor",
        "CheckpointValidationResult",
        "CheckpointValidation",
        "ExecutionEventType",
        "EventCorrelation",
        "EventCorrelationContext",
        "ExecutionEvent",
        "ExecutionFailureCategory",
        "ExecutionFailureLayer",
        "ExecutionFailure",
        "classify_failure",
        "is_retryable",
    ]
    + [
        "ThreadId",
        "ThreadLifecycleState",
        "ThreadLifecycleTransitionGraph",
        "ThreadLifecycleReason",
        "ThreadLifecycleSnapshot",
        "ThreadLifecycleTransitionRequest",
        "ThreadLifecycleTransitionResult",
        "ThreadDelta",
        "DeltaValidationResult",
        "ThreadDeltaBatch",
        "DeltaApplicationResult",
        "ThreadDeltaValidator",
        "RelationshipKind",
        "ThreadRelationship",
        "ParentChildRelationship",
        "ThreadRelationshipGraph",
        "ThreadRelationshipSnapshot",
        "ExecutionThreadSnapshot",
        "ExecutionThread",
        "Thread",
    ]
    + [
        "ConversationPurpose",
        "ConversationParticipant",
        "ConversationState",
        "ConversationThread",
        "ConversationSnapshot",
        "TaskStatus",
        "TaskConstraints",
        "TaskPlan",
        "TaskProgress",
        "TaskState",
        "TaskThread",
        "TaskSnapshot",
        "ObservationType",
        "MonitoringTarget",
        "Baseline",
        "MonitoringState",
        "MonitoringThread",
        "MonitoringSnapshot",
        "InternalPurpose",
        "InternalContext",
        "InternalState",
        "InternalThread",
        "InternalSnapshot",
    ]
    + [
        "LoopKind",
        "BehavioralMode",
        "DecisionType",
        "ExecutionLoopDecision",
        "ContinueDecision",
        "SuspendDecision",
        "AwaitInputDecision",
        "CompleteDecision",
        "TerminateDecision",
        "RejectOutcomeDecision",
        "RequestRecoveryDecision",
        "DelegateDecision",
        "SwitchModeDecision",
        "ReplacePolicyDecision",
        "LoopPolicy",
        "LoopContext",
        "LoopCycleOutcome",
        "LoopState",
        "ExecutionLoop",
        "StandardPolicy",
        "PolicyError",
        "InvalidModeTransitionError",
    ]
    + [
        "ConversationBehavior",
        "ConversationPolicyState",
        "ConversationPolicy",
        "create_conversation_policy",
        "TaskBehavior",
        "TaskPolicyState",
        "TaskPolicy",
        "create_task_policy",
        "PlanningPolicyState",
        "PlanningPolicy",
        "create_planning_policy",
        "MonitoringPolicyState",
        "MonitoringPolicy",
        "create_monitoring_policy",
        "RecoveryPolicyState",
        "RecoveryPolicy",
        "create_recovery_policy",
        "IdleBehavior",
        "IdlePolicyState",
        "IdlePolicy",
        "create_idle_policy",
    ]
    + [
        "CycleProgressionState",
        "StageProgressionState",
        "CycleOutcomeStatus",
        "CycleIdentity",
        "ThreadReference",
        "LoopDecisionReference",
        "CycleStageDefinition",
        "CycleStageDefinitionValidation",
        "CycleDefinition",
        "CycleDefinitionValidation",
        "CycleContext",
        "CycleStageResult",
        "CycleSemanticDelta",
        "CycleDeltaValidationResult",
        "CycleOutcome",
        "CycleInterruptionReason",
        "CycleValidationResult",
        "validate_cycle_ownership",
    ]
    + [
        "InterpretationStage",
        "InterpretationCycle",
        "ResponseStage",
        "ResponseCycle",
        "PlanningStage",
        "PlanningCycle",
        "ExecutionStage",
        "ExecutionCycle",
        "EvaluationStage",
        "EvaluationCycle",
        "ObservationStage",
        "ObservationCycle",
        "ReflectionStage",
        "ReflectionCycle",
        "create_cycle_from_kind",
    ]
)