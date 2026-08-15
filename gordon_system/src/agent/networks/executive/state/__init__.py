# Executive State Package
# =======================

"""
Executive State - The authoritative, bounded, revisioned semantic representation
of the Executive Network's currently accepted executive organization.

This package provides:

Core Types:
    - ExecutiveState: Immutable root state with bounded references and summaries
    - ExecutiveContext: Bounded immutable projection of externally owned information

Identity and Revisioning:
    - ExecutiveStateId: Unique identifier for executive states
    - ExecutiveStateRevision: Monotonic revision number for states
    - ExecutiveContextId: Unique identifier for contexts
    - ExecutiveContextRevision: Monotonic revision number for contexts

References:
    - ExecutiveStateReference: Reference to an executive state (not full state)
    - ExecutiveContextReference: Reference to a context
    - ExecutiveTaskSetReference: Reference to a task set
    - ExecutiveGoalReference: Reference to a goal
    - ExecutiveCommitmentReference: Reference to a commitment
    - ExecutiveStrategyReference: Reference to a strategy
    - ExecutiveExternalRequestReference: Reference to external requests
    - ExecutiveExternalResultReference: Reference to external results
    - ExecutiveProposalReference: Reference to executive proposals
    - ExecutiveAuthorityDecisionReference: Reference to authority decisions

State Evaluation:
    - ExecutiveStateConfidence: Classification of state confidence
    - ExecutiveStateCompleteness: Classification of state completeness
    - ExecutiveStateConsistency: Classification of state consistency
    - ExecutiveStateCoherence: Classification of state coherence
    - ExecutiveContextConfidence: Classification of context confidence
    - ExecutiveContextCompleteness: Classification of context completeness
    - ExecutiveContextFreshness: Classification of context freshness
    - ExecutiveContextConsistency: Classification of context consistency
    - ExecutiveContextValidity: Classification of context validity

Metadata:
    - ExecutiveStatePrivacy: Privacy classification for state
    - ExecutiveStateProvenance: Provenance information for state
    - ExecutiveContextPrivacy: Privacy classification for context
    - ExecutiveContextProvenance: Provenance information for context

Deltas and Transitions:
    - ExecutiveStateDelta: Immutable delta for state changes
    - ExecutiveContextDelta: Immutable delta for context changes
    - ExecutiveStateTransitionKind: Kinds of executive transitions
    - ExecutiveStateTransition: Transition from one state to another

Histories and Bounds:
    - ExecutiveStateHistoryEntry: Single entry in state history
    - ExecutiveStateHistory: Bounded history of state revisions
    - ExecutiveContextHistoryEntry: Single entry in context history
    - ExecutiveContextHistory: Bounded history of context revisions

Validation:
    - ExecutiveStateRevisionConflict: Typed error for revision conflicts
    - ExecutiveContextRevisionConflict: Typed error for context revision conflicts
    - ExecutiveStateValidation: Validation results for state
    - ExecutiveContextValidation: Validation results for context

Integrity and Serialization:
    - ExecutiveStateIntegrityAssessment: Assessment of state integrity
    - ExecutiveContextIntegrityAssessment: Assessment of context integrity
    - ExecutiveStateSerialization: Serialization results for state
    - ExecutiveContextSerialization: Serialization results for context

Configuration:
    - ExecutiveMode: Semantic executive modes (from mode module)

Public API:
    The public API consists of immutable dataclasses and enums that can be
    used to construct, validate, and manipulate executive states. All types
    are deeply immutable and safe to use in concurrent contexts.

Runtime Neutrality:
    This package does not perform any runtime operations during import or
    processing. It provides pure state types without side effects.
"""

from gordon_system.src.agent.networks.executive.state.mode import (
    ExecutiveMode,
)

from gordon_system.src.agent.networks.executive.state.model import (
    ExecutiveState,
    ExecutiveContext,
)

from gordon_system.src.agent.networks.executive.state.identity import (
    ExecutiveStateId,
    ExecutiveStateRevision,
    ExecutiveContextId,
    ExecutiveContextRevision,
    ExecutiveStateSchemaVersion,
    ExecutiveContextSchemaVersion,
)

from gordon_system.src.agent.networks.executive.state.reference import (
    ExecutiveStateReference,
    ExecutiveContextReference,
    ExecutiveTaskSetReference,
    ExecutiveGoalReference,
    ExecutiveCommitmentReference,
    ExecutiveStrategyReference,
    ExecutiveExternalRequestReference,
    ExecutiveExternalResultReference,
    ExecutiveProposalReference,
    ExecutiveAuthorityDecisionReference,
)

from gordon_system.src.agent.networks.executive.state.composition import (
    ExecutiveStateConfidence,
    ExecutiveStateCompleteness,
    ExecutiveStateConsistency,
    ExecutiveStateCoherence,
    ExecutiveContextConfidence,
    ExecutiveContextCompleteness,
    ExecutiveContextFreshness,
    ExecutiveContextConsistency,
    ExecutiveContextValidity,
)

from gordon_system.src.agent.networks.executive.state.metadata import (
    ExecutiveStatePrivacy,
    ExecutiveStateProvenance,
    ExecutiveContextPrivacy,
    ExecutiveContextProvenance,
)

from gordon_system.src.agent.networks.executive.state.delta import (
    ExecutiveStateDelta,
    ExecutiveContextDelta,
)

from gordon_system.src.agent.networks.executive.state.transition import (
    ExecutiveStateTransitionKind,
    ExecutiveStateTransition,
)

from gordon_system.src.agent.networks.executive.state.history import (
    ExecutiveStateHistoryEntry,
    ExecutiveStateHistory,
    ExecutiveContextHistoryEntry,
    ExecutiveContextHistory,
)

from gordon_system.src.agent.networks.executive.state.validation import (
    ExecutiveStateRevisionConflict,
    ExecutiveContextRevisionConflict,
    ExecutiveStateValidation,
    ExecutiveContextValidation,
)

from gordon_system.src.agent.networks.executive.state.integrity import (
    ExecutiveStateIntegrityAssessment,
    ExecutiveContextIntegrityAssessment,
)

from gordon_system.src.agent.networks.executive.state.serialization import (
    ExecutiveStateSerialization,
    ExecutiveContextSerialization,
)

__all__ = (
    # Core types
    "ExecutiveState",
    "ExecutiveContext",
    
    # Identity and revisioning
    "ExecutiveStateId",
    "ExecutiveStateRevision",
    "ExecutiveContextId",
    "ExecutiveContextRevision",
    "ExecutiveStateSchemaVersion",
    "ExecutiveContextSchemaVersion",
    
    # References
    "ExecutiveStateReference",
    "ExecutiveContextReference",
    "ExecutiveTaskSetReference",
    "ExecutiveGoalReference",
    "ExecutiveCommitmentReference",
    "ExecutiveStrategyReference",
    "ExecutiveExternalRequestReference",
    "ExecutiveExternalResultReference",
    "ExecutiveProposalReference",
    "ExecutiveAuthorityDecisionReference",
    
    # State evaluation
    "ExecutiveStateConfidence",
    "ExecutiveStateCompleteness",
    "ExecutiveStateConsistency",
    "ExecutiveStateCoherence",
    "ExecutiveContextConfidence",
    "ExecutiveContextCompleteness",
    "ExecutiveContextFreshness",
    "ExecutiveContextConsistency",
    "ExecutiveContextValidity",
    
    # Metadata
    "ExecutiveStatePrivacy",
    "ExecutiveStateProvenance",
    "ExecutiveContextPrivacy",
    "ExecutiveContextProvenance",
    
    # Deltas and transitions
    "ExecutiveStateDelta",
    "ExecutiveContextDelta",
    "ExecutiveStateTransitionKind",
    "ExecutiveStateTransition",
    
    # Histories and bounds
    "ExecutiveStateHistoryEntry",
    "ExecutiveStateHistory",
    "ExecutiveContextHistoryEntry",
    "ExecutiveContextHistory",
    
    # Validation
    "ExecutiveStateRevisionConflict",
    "ExecutiveContextRevisionConflict",
    "ExecutiveStateValidation",
    "ExecutiveContextValidation",
    
    # Integrity and serialization
    "ExecutiveStateIntegrityAssessment",
    "ExecutiveContextIntegrityAssessment",
    "ExecutiveStateSerialization",
    "ExecutiveContextSerialization",
    
    # Configuration
    "ExecutiveMode",
)