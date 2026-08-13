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
        ├── types/          # Neutral value types and identifiers
        ├── contracts/      # Core boundary protocols
        ├── registry/       # Unit type registries
        ├── base.py         # Base classes and protocols
        ├── threads/        # Canonical Thread implementations (Phase 3.10.8)
        ├── loops/          # Canonical Loop policy implementations (Phase 3.10.8)
        └── cycles/         # Canonical Cycle definitions (Phase 3.10.8)

Ownership Model:

    Thread: semantic continuity, identity, completion intent
    Loop: repetition policy, cycle selection decision, continuation policy  
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

# =============================================================================
# PHASE 3.10.8 - CANONICAL EXECUTION ENTITY EXPORTS
# =============================================================================
# PHASE 3.10.9 - Concrete execution taxonomy implementation
# =============================================================================

# =============================================================================
# PHASE 3.10.14 - Execution Hardening Exports
# =============================================================================

from .types import (
    # Advancement Lease (Enforcement 1)
    AdvancementLease,
    LeaseAcquisitionResult,
    
    # Cancellation Model (Enhancement 2)
    CancellationSource,
    CancellationReason,
    CancellationRequest,
    CancellationToken,
    ExecutionCancelledError,
    CancellationOutcome,
    
    # Preemption and Interruption (Enhancement 3)
    ExecutionInterruptionType,
    InterruptionRequest,
    InterruptionOutcome,
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
    ExecutionLayer,  # Backward compatibility
    ExecutionFailure,
    classify_failure,
    is_retryable,
)

# Identity types (semantic, immutable)
from .types import (
    ExecutionThreadId,
    ExecutionLoopId,
    ExecutionLoopDecisionId,
    ExecutionCycleId,
    ExecutionStageId,
)

# Thread lifecycle states
from .types import (
    ExecutionThreadKind,
    ExecutionThreadStatus,
    is_terminal_status,
    get_allowed_transitions,
)

# Thread semantic types
from .types import (
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
)

# Runtime state types
from .types import (
    ExecutionState,
    LifecycleState,
    ExecutionCycleResult,
)

# =============================================================================
# PHASE 3.10.9 - Concrete Thread Types
# =============================================================================

from .threads.concrete import (
    # Conversation thread types
    ConversationPurpose,
    ConversationParticipant,
    ConversationState,
    ConversationThread,
    ConversationSnapshot,
    
    # Task thread types
    TaskStatus,
    TaskConstraints,
    TaskPlan,
    TaskProgress,
    TaskState,
    TaskThread,
    TaskSnapshot,
    
    # Monitoring thread types
    ObservationType,
    MonitoringTarget,
    Baseline,
    MonitoringState,
    MonitoringThread,
    MonitoringSnapshot,
    
    # Internal thread types
    InternalPurpose,
    InternalContext,
    InternalState,
    InternalThread,
    InternalSnapshot,
)

# Priority and resources
from .types import (
    ExecutionPriority,
    ExecutionResourceBudget,
    ExecutionCancellationReason,
    ExecutionCancellationView,
    ExecutionTimestamp,
)

# Failures (contract-level)
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

# =============================================================================
# THREAD ARCHITECTURE (Phase 3.10.7/3.10.8 - IMMUTABLE CANONICAL MODEL)
# =============================================================================

from .threads import (
    # Identity
    ThreadId,
    
    # Lifecycle (semantic intent)
    ThreadLifecycleState,  # Thread owns intent, Core owns runtime transitions
    ThreadLifecycleTransitionGraph,
    ThreadLifecycleReason,
    ThreadLifecycleSnapshot,
    ThreadLifecycleTransitionRequest,
    ThreadLifecycleTransitionResult,
    
    # Delta (controlled state change - no direct mutation!)
    ThreadSemanticDelta as ThreadDelta,
    DeltaValidationResult,
    ThreadDeltaBatch,
    DeltaApplicationResult,
    ThreadDeltaValidator,
    
    # Relationships
    RelationshipKind,
    ThreadRelationship,
    ParentChildRelationship,
    ThreadRelationshipGraph,
    ThreadRelationshipSnapshot,
    
    # Snapshots (immutable views)
    SnapshotClass as ExecutionThreadSnapshot,
    
    # Canonical ExecutionThread entity - IMMUTABLE!
    ExecutionThread,  # Immutable semantic artifact with controlled delta application
    
    # Backward compatibility alias
    Thread as ExecutionThreadAlias,  # Deprecated: use ExecutionThread instead
)

# Backward compatibility: Thread is now aliased to ExecutionThread
Thread = ExecutionThread

# =============================================================================
# LOOP ARCHITECTURE (Phase 3.10.8)
# PHASE 3.10.9 - Concrete Loop Implementations
# =============================================================================

from .loops import (
    # Kinds and modes
    LoopKind,
    BehavioralMode,
    
    # Decisions
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
    
    # Protocol and context
    LoopPolicy,
    LoopContext,
    CycleOutcome as LoopCycleOutcome,  # Renamed to avoid conflict
    LoopState,
    
    # Coordinator (canonical Loop)
    ExecutionLoop,
    StandardPolicy,
    
    # Errors
    PolicyError,
    InvalidModeTransitionError,
)

# =============================================================================
# PHASE 3.10.9 - Concrete Loop Policies
# =============================================================================

from .loops.concrete import (
    # Conversation loop
    ConversationBehavior,
    ConversationPolicyState,
    ConversationPolicy,
    create_conversation_policy,
    
    # Task loop
    TaskBehavior,
    TaskPolicyState,
    TaskPolicy,
    create_task_policy,
    
    # Planning loop
    PlanningPolicyState,
    PlanningPolicy,
    create_planning_policy,
    
    # Monitoring loop
    MonitoringPolicyState,
    MonitoringPolicy,
    create_monitoring_policy,
    
    # Recovery loop
    RecoveryPolicyState,
    RecoveryPolicy,
    create_recovery_policy,
    
    # Idle loop
    IdleBehavior,
    IdlePolicyState,
    IdlePolicy,
    create_idle_policy,
)

# =============================================================================
# STAGE ARCHITECTURE (Phase 3.10.8 - NEW)
# =============================================================================

from .stages import (
    # Status types
    StageStatus,
    
    # Identity
    StageIdentity,
    
    # Definition
    ExecutionStageDefinition,
    StageDefinitionValidation,
    
    # Context and result
    StageContext,
    ExecutionStageResult,
    
    # Capability request and outcome
    CapabilityRequest,
    CapabilityOutcome,
    
    # Protocol
    ExecutionStage,
    CapabilityPort as StageCapabilityPort,
)

# =============================================================================
# CYCLE ARCHITECTURE (Phase 3.10.8)
# PHASE 3.10.9 - Concrete Cycle Implementations
# =============================================================================

from .cycles import (
    # Progression states (semantic)
    CycleProgressionState,
    StageProgressionState,
    
    # Outcome status (terminal)
    CycleOutcomeStatus,
    
    # Identity types
    CycleIdentity,
    ThreadReference,
    LoopDecisionReference,
    
    # Definition types
    StageDefinition as CycleStageDefinition,  # Renamed to avoid conflict with stages
    StageDefinitionValidation as CycleStageDefinitionValidation,
    CycleDefinition,
    CycleDefinitionValidation,
    
    # Context and result types
    CycleContext,
    StageResult as CycleStageResult,
    SemanticDelta as CycleSemanticDelta,  # Renamed to avoid conflict with stages
    DeltaValidationResult as CycleDeltaValidationResult,
    CycleOutcome,  # Canonical cycle outcome
    
    # Failure/interruption
    CycleInterruptionReason,
    
    # Validation
    CycleValidationResult,
    validate_cycle_ownership,
)

# =============================================================================
# PHASE 3.10.9 - Concrete Cycle Types
# =============================================================================

from .cycles.concrete import (
    # Interpretation cycle (Conversation)
    InterpretationStage,
    InterpretationCycle,
    
    # Response cycle (Conversation)
    ResponseStage,
    ResponseCycle,
    
    # Planning cycle (Task)
    PlanningStage,
    PlanningCycle,
    
    # Execution cycle (Task)
    ExecutionStage,
    ExecutionCycle,
    
    # Evaluation cycle (Task)
    EvaluationStage,
    EvaluationCycle,
    
    # Observation cycle (Monitoring)
    ObservationStage,
    ObservationCycle,
    
    # Reflection cycle (Internal)
    ReflectionStage,
    ReflectionCycle,
    
    create_cycle_from_kind,
)

# =============================================================================
# INTEGRATION ARCHITECTURE (Phase 3.10.8 - NEW)
# =============================================================================

from .integration import (
    # Capability Port
    CapabilityPort as IntegrationCapabilityPort,
    CapabilityOutcome as IntegrationCapabilityOutcome,
    
    # Runtime Port
    ExecutionRuntimePort as IntegrationExecutionRuntimePort,
    
    # Runtime types
    ExecutionHandle as IntegrationExecutionHandle,
    LifecycleTransitionResult as IntegrationLifecycleTransitionResult,
    StageDefinition as IntegrationStageDefinition,
    
    # Minimal flow components
    ExecutionFlow as IntegrationExecutionFlow,
    MinimalThread,
    MinimalLoop,
    MinimalCycle,
    
    # Utilities
    create_minimal_flow,
)

# =============================================================================
# COORDINATOR ARCHITECTURE (Phase 3.10.10)
# =============================================================================

from .coordinator import (
    # Identifiers (semantic)
    ThreadId as ExecutionThreadId,  # Alias for compatibility
    LoopId as ExecutionLoopId,      # Alias for compatibility  
    CycleId as ExecutionCycleId,    # Alias for compatibility
    
    # Loop decisions (Thread-local continuation)
    LoopDecisionKind,
    LoopDecision,
    AwaitCondition,
    
    # Thread state management
    ThreadSnapshot,
    ThreadSemanticDelta,
    CommitResult,
    ThreadDeltaCommitResult,
    
    # Cycle execution
    CycleOutcome as ExecutionCycleOutcome,  # Alias for compatibility
    StageResult,
    
    # Coordinator protocol and implementation
    ExecutionCoordinator,
    SimpleExecutionCoordinator,
)

# =============================================================================
# STAGE ARCHITECTURE EXPORTS (added to __all__ below)
# =============================================================================

_STAGES_EXPORTS = [
    "StageStatus",
    "StageIdentity",
    "ExecutionStageDefinition",
    "StageDefinitionValidation",
    "StageContext",
    "ExecutionStageResult",
    "CapabilityRequest",
    "CapabilityOutcome",
    "ExecutionStage",
    "StageCapabilityPort",
]

# =============================================================================
# INTEGRATION ARCHITECTURE EXPORTS (added to __all__ below)
# =============================================================================

_INTEGRATION_EXPORTS = [
    "IntegrationCapabilityPort",
    "IntegrationCapabilityOutcome",
    "IntegrationExecutionRuntimePort",
    "IntegrationExecutionHandle",
    "IntegrationLifecycleTransitionResult",
    "IntegrationStageDefinition",
    "IntegrationExecutionFlow",
    "MinimalThread",
    "MinimalLoop",
    "MinimalCycle",
    "create_minimal_flow",
]

# =============================================================================
# PUBLIC API EXPORTS (Canonical Entity Names)
# =============================================================================

# =============================================================================
# PHASE 3.10.9 - Add concrete exports to __all__
# =============================================================================
# =============================================================================
# PHASE 3.10.14 - Add hardening exports to __all__
# =============================================================================

_HARDENING_EXPORTS = [
    # Advancement Lease (Enforcement 1)
    "AdvancementLease",
    "LeaseAcquisitionResult",
    
    # Cancellation Model (Enhancement 2)
    "CancellationSource",
    "CancellationReason",
    "CancellationRequest",
    "CancellationToken",
    "ExecutionCancelledError",
    "CancellationOutcome",
    
    # Preemption and Interruption (Enhancement 3)
    "ExecutionInterruptionType",
    "InterruptionRequest",
    "InterruptionOutcome",
    
    # Checkpoint (Enhancement 4)
    "CycleCheckpoint",
    "CycleResumptionDescriptor",
    "CheckpointValidationResult",
    "CheckpointValidation",
    
    # Events (Enhancement 14)
    "ExecutionEventType",
    "EventCorrelation",
    "EventCorrelationContext",
    "ExecutionEvent",
    
    # Failure Provenance (Enhancement 16)
    "ExecutionFailureCategory",
    "ExecutionFailureLayer",
    "ExecutionLayer",  # Backward compatibility
    "ExecutionFailure",
    "classify_failure",
    "is_retryable",
]

_CONCRETE_THREAD_EXPORTS = [
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

_CONCRETE_LOOP_EXPORTS = [
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

_CONCRETE_CYCLE_EXPORTS = [
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

# =============================================================================
# PHASE 3.10.10 - Coordinator exports
# =============================================================================

_COORDINATOR_EXPORTS = [
    "LoopDecisionKind",
    "LoopDecision",
    "AwaitCondition",
    "ThreadSnapshot",
    "ThreadSemanticDelta",
    "CommitResult",
    "ThreadDeltaCommitResult",
    "ExecutionCycleOutcome",  # Alias for compatibility
    "StageResult",
    "ExecutionCoordinator",
    "SimpleExecutionCoordinator",
]

__all__ = (
    _STAGES_EXPORTS 
    + _INTEGRATION_EXPORTS 
    + _COORDINATOR_EXPORTS
    + _HARDENING_EXPORTS  # PHASE 3.10.14 additions
    + _CONCRETE_THREAD_EXPORTS 
    + _CONCRETE_LOOP_EXPORTS 
    + _CONCRETE_CYCLE_EXPORTS 
    + [
    # Identity types
    "ExecutionThreadId",
    "ExecutionLoopId",
    "ExecutionLoopDecisionId",
    "ExecutionCycleId",
    "ExecutionStageId",
    
    # Thread lifecycle states (semantic)
    "ExecutionThreadStatus",
    "is_terminal_status",
    "get_allowed_transitions",
    
    # Thread semantic types
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
    
    # Runtime state types
    "ExecutionState",
    "LifecycleState",
    "ExecutionCycleResult",
    
    # Priority and resources
    "ExecutionPriority",
    "ExecutionResourceBudget",
    "ExecutionCancellationReason",
    "ExecutionCancellationView",
    "ExecutionTimestamp",
    
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
    
     # Thread architecture (IMMUTABLE CANONICAL - Phase 3.10.7/3.10.8)
     "ThreadId",                        # Semantic identity (immutable)
     "ThreadLifecycleState",            # Thread owns semantic intent
     "ExecutionThreadSnapshot",         # Controlled state change via delta application
     "DeltaValidationResult",
     "ThreadDeltaBatch",
     "DeltaApplicationResult",
     "ThreadDeltaValidator",
     "RelationshipKind",
     "ThreadRelationship",
     "ParentChildRelationship",
     "ThreadRelationshipGraph",
     "ExecutionThreadSnapshot",         # Immutable snapshot for Loop evaluation
     "ExecutionThread",                 # IMMUTABLE canonical ExecutionThread entity!
     "Thread",                          # Backward compatibility alias (deprecated)
    
    # Loop architecture
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
    
    # Cycle architecture
    "CycleProgressionState",
    "StageProgressionState",
    "CycleOutcomeStatus",
    "CycleIdentity",
    "ThreadReference",
    "LoopDecisionReference",
    "StageDefinition",
    "StageDefinitionValidation",
    "CycleDefinition",
    "CycleDefinitionValidation",
    "CycleContext",
    "StageResult",
    "CycleSemanticDelta",
    "CycleDeltaValidationResult",
    "CycleOutcome",
    "CycleInterruptionReason",
    "CycleValidationResult",
    "validate_cycle_ownership",
]
)
