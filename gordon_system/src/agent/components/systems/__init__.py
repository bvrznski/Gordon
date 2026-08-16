"""Systems - system-level infrastructure components."""
from gordon_system.src.agent.systems.interaction_contracts import (
    # Identity types
    SystemInteractionId,
    SystemAdmissionId,
    SystemTransitionId,

    # Lifecycle state
    SystemLifecycleState,
    is_system_terminal_state,

    # Interaction categories
    SystemInteractionCategory,

    # Context types
    SystemInteractionContext,
    SystemAdmissionContext,

    # Admission decision
    SystemAdmissionDecision,
    is_admission_terminal,

    # State access
    StateAccessMode,
    StateAccessRequest,
    StateAccessResult,

    # State mutation
    StateMutationRequest,
    StateMutationProposal,
    MutationEvaluationResult,
    MutationEvaluation,

    # State transitions
    StateTransitionRequest,
    StateTransitionMetadata,
    StateTransitionRecord,

    # Transaction boundaries
    TransactionBoundary,
    TransactionBoundaryRequest,
    TransactionCommitRequest,

    # Public records
    PublicStateAccess,
    PublicSystemInteractionRecord,

    # Protocol
    SystemExecutor,

    # Results
    SystemInteractionOutcome,
    SystemInteractionResult,

    # Failures
    SystemFailureCategory,
    SystemInteractionFailure,

    # Security
    SecurityVerification,
    PublicSecurityRecord,

    # Utility functions
    dataclass_replace,
    get_canonical_system_interaction_flow,
    ARCHITECTURAL_CONSTRAINTS,
)

__all__ = [
    # Identity types
    "SystemInteractionId",
    "SystemAdmissionId",
    "SystemTransitionId",

    # Lifecycle state
    "SystemLifecycleState",
    "is_system_terminal_state",

    # Interaction categories
    "SystemInteractionCategory",

    # Context types
    "SystemInteractionContext",
    "SystemAdmissionContext",

    # Admission decision
    "SystemAdmissionDecision",
    "is_admission_terminal",

    # State access
    "StateAccessMode",
    "StateAccessRequest",
    "StateAccessResult",

    # State mutation
    "StateMutationRequest",
    "StateMutationProposal",
    "MutationEvaluationResult",
    "MutationEvaluation",

    # State transitions
    "StateTransitionRequest",
    "StateTransitionMetadata",
    "StateTransitionRecord",

    # Transaction boundaries
    "TransactionBoundary",
    "TransactionBoundaryRequest",
    "TransactionCommitRequest",

    # Public records
    "PublicStateAccess",
    "PublicSystemInteractionRecord",

    # Protocol
    "SystemExecutor",

    # Results
    "SystemInteractionOutcome",
    "SystemInteractionResult",

    # Failures
    "SystemFailureCategory",
    "SystemInteractionFailure",

    # Security
    "SecurityVerification",
    "PublicSecurityRecord",

    # Utility functions
    "dataclass_replace",
    "get_canonical_system_interaction_flow",
    "ARCHITECTURAL_CONSTRAINTS",
]