# Oriented Network Lifecycle Package - Phase 4.7.9
# ===============================================

"""
Oriented Network Lifecycle - Semantic orientation evolution throughout its existence.

ARCHITECTURAL PHILOSOPHY:
    The lifecycle represents semantic evolution of Orientation.
    
    Lifecycle NEVER:
        - Owns runtime execution engines
        - Owns schedulers  
        - Owns workflow engines
        - Manages runtime state transitions
        
    Lifecycle ALWAYS:
        - Represents semantic identity preservation
        - Tracks semantic lineage and provenance
        - Defines legal transitions between states
        - Preserves immutable history

PHASE 4.7.9: Semantic lifecycle model for Oriented Network Orientation.

PUBLIC API:
    Base Models:
        BaseLifecycleModel - Abstract base for all lifecycle representations
        BaseActivationModel - Abstract base for activation semantics
        BaseTransitionModel - Abstract base for transition semantics
        BaseEvolutionModel - Abstract base for evolution semantics
        BaseCompletionModel - Abstract base for completion semantics
        BaseArchiveModel - Abstract base for archival semantics
    
    Status Models:
        CreatedOrientation
        CandidateOrientation
        ReferencedOrientation  
        ActiveOrientation
        EngagedOrientation
        MaintainedOrientation
        InterruptedOrientation
        SuspendedOrientation
        ResumedOrientation
        RecoveredOrientation
        CompletedOrientation
        ArchivedOrientation
        
    Activation Models:
        ActivationContext
        ActivationRequirement
        ActivationRelationship
        ActivationProjection
        ActivationReference
        
    Engagement Models:
        EngagedOrientation
        PartiallyEngagedOrientation
        FullyEngagedOrientation
        BackgroundEngagement
        ForegroundEngagement
        
    Deactivation Models:
        GracefulDeactivation
        DeferredDeactivation
        CompletedDeactivation
        AbortedDeactivation
        
    Suspension Models:
        TemporarySuspension
        StrategicSuspension
        ExecutiveSuspension
        ResourceSuspension
        ExternalSuspension
        
    Resumption Models:
        ImmediateResumption
        DeferredResumption
        RecoveredResumption
        ExecutiveResumption
        ContextualResumption
        
    Evolution Models:
        OrientationEvolution
        OrientationRevision
        OrientationAdaptation
        OrientationExpansion
        OrientationRefinement
        
    Termination Models:
        CompletedOrientation
        CancelledOrientation
        AbandonedOrientation
        SupersededOrientation
        ArchivedOrientation
        
    Transition Models:
        LifecycleTransition
        ActivationTransition
        EngagementTransition
        SuspensionTransition
        EvolutionTransition
        CompletionTransition
        
    History Models:
        LifecycleIdentity
        LifecycleRevision
        LifecycleLineage
        LifecycleMilestone
        LifecycleCheckpoint

VALIDATION:
    - Every lifecycle object is immutable (frozen dataclass)
    - Every transition preserves semantic identity unless explicitly terminating
    - All transitions follow explicit legal graph
"""

from __future__ import annotations

# =============================================================================
# BASE ABSTRACTIONS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.lifecycle.base_model import (
    BaseLifecycleModel,
    BaseActivationModel,
    BaseTransitionModel,
    BaseEvolutionModel,
    BaseCompletionModel,
    BaseArchiveModel,
)

# =============================================================================
# LIFECYCLE STATUS MODELS (Phase 4.7.9 - Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.lifecycle.status import (
    CreatedOrientation,
    CandidateOrientation,
    ReferencedOrientation,
    ActiveOrientation,
    EngagedOrientation,
    MaintainedOrientation,
    InterruptedOrientation,
    SuspendedOrientation,
    ResumedOrientation,
    RecoveredOrientation,
    CompletedOrientation,
    ArchivedOrientation,
    OrientationStatus,
)

# =============================================================================
# ACTIVATION MODELS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.lifecycle.activation import (
    ActivationContext,
    ActivationRequirement,
    ActivationRelationship,
    ActivationProjection,
    ActivationReference,
)

# =============================================================================
# ENGAGEMENT MODELS  
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.lifecycle.engagement import (
    EngagedOrientation,
    PartiallyEngagedOrientation,
    FullyEngagedOrientation,
    BackgroundEngagement,
    ForegroundEngagement,
)

# =============================================================================
# DEACTIVATION MODELS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.lifecycle.deactivation import (
    GracefulDeactivation,
    DeferredDeactivation,
    CompletedDeactivation,
    AbortedDeactivation,
)

# =============================================================================
# SUSPENSION MODELS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.lifecycle.suspension import (
    TemporarySuspension,
    StrategicSuspension,
    ExecutiveSuspension,
    ResourceSuspension,
    ExternalSuspension,
)

# =============================================================================
# RESUMPTION MODELS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.lifecycle.resumption import (
    ImmediateResumption,
    DeferredResumption,
    RecoveredResumption,
    ExecutiveResumption,
    ContextualResumption,
)

# =============================================================================
# EVOLUTION MODELS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.lifecycle.evolution import (
    OrientationEvolution,
    OrientationRevision,
    OrientationAdaptation,
    OrientationExpansion,
    OrientationRefinement,
)

# =============================================================================
# TERMINATION MODELS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.lifecycle.termination import (
    CompletedOrientation as TerminatedCompletedOrientation,
    CancelledOrientation,
    AbandonedOrientation,
    SupersededOrientation,
)

# =============================================================================
# TRANSITION MODELS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.lifecycle.transitions import (
    LifecycleTransition,
    ActivationTransition,
    EngagementTransition,
    SuspensionTransition,
    EvolutionTransition,
    CompletionTransition,
    TransitionGraph,
    Transitions,
)

# =============================================================================
# HISTORY MODELS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.lifecycle.history import (
    LifecycleIdentity,
    LifecycleRevision,
    LifecycleLineage,
    LifecycleMilestone,
    LifecycleCheckpoint,
)

# =============================================================================
# CONTRACTS (Phase 4.7.9 - Part 2)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.lifecycle.contracts.base import (
    LifecycleReference,
    LifecycleRelationship,
    LifecycleRequirement,
    LifecycleAuthority,
    LifecycleOwner,
    LifecycleProjection,
    ActivationReference as ActivationContractReference,
    ActivationRelationship as ActivationContractRelationship,
    ActivationRequirement as ActivationContractRequirement,
    ActivationAuthority as ActivationContractAuthority,
    ActivationOwner as ActivationContractOwner,
    ActivationProjection as ActivationContractProjection,
)

# =============================================================================
# SEMANTIC CONSTANTS
# =============================================================================

CANONICAL_LIFECYCLE_GRAPH: tuple[tuple[str, str], ...] = (
    ("Created", "Candidate"),
    ("Candidate", "Referenced"),
    ("Referenced", "Activated"),
    ("Activated", "Engaged"),
    ("Engaged", "Maintained"),
    ("Maintained", "Suspended"),
    ("Suspended", "Resumed"),
    ("Resumed", "Engaged"),
    ("Engaged", "Completed"),
    ("Completed", "Archived"),
)

TRANSITION_VALIDATION_ENABLED: bool = True

__all__ = [
    # Base abstractions
    "BaseLifecycleModel",
    "BaseActivationModel",
    "BaseTransitionModel",
    "BaseEvolutionModel",
    "BaseCompletionModel",
    "BaseArchiveModel",
    # Status models
    "CreatedOrientation",
    "CandidateOrientation",
    "ReferencedOrientation",
    "ActiveOrientation",
    "EngagedOrientation",
    "MaintainedOrientation",
    "InterruptedOrientation",
    "SuspendedOrientation",
    "ResumedOrientation",
    "RecoveredOrientation",
    "CompletedOrientation",
    "ArchivedOrientation",
    "OrientationStatus",
    # Activation models
    "ActivationContext",
    "ActivationRequirement",
    "ActivationRelationship",
    "ActivationProjection",
    "ActivationReference",
    # Engagement models
    "EngagedOrientation",
    "PartiallyEngagedOrientation",
    "FullyEngagedOrientation",
    "BackgroundEngagement",
    "ForegroundEngagement",
    # Deactivation models
    "GracefulDeactivation",
    "DeferredDeactivation",
    "CompletedDeactivation",
    "AbortedDeactivation",
    # Suspension models
    "TemporarySuspension",
    "StrategicSuspension",
    "ExecutiveSuspension",
    "ResourceSuspension",
    "ExternalSuspension",
    # Resumption models
    "ImmediateResumption",
    "DeferredResumption",
    "RecoveredResumption",
    "ExecutiveResumption",
    "ContextualResumption",
    # Evolution models
    "OrientationEvolution",
    "OrientationRevision",
    "OrientationAdaptation",
    "OrientationExpansion",
    "OrientationRefinement",
    # Termination models
    "TerminatedCompletedOrientation",
    "CancelledOrientation",
    "AbandonedOrientation",
    "SupersededOrientation",
    # Transition models
    "LifecycleTransition",
    "ActivationTransition",
    "EngagementTransition",
    "SuspensionTransition",
    "EvolutionTransition",
    "CompletionTransition",
    "TransitionGraph",
    "Transitions",
    # History models
    "LifecycleIdentity",
    "LifecycleRevision",
    "LifecycleLineage",
    "LifecycleMilestone",
    "LifecycleCheckpoint",
    # Contracts
    "LifecycleReference",
    "LifecycleRelationship",
    "LifecycleRequirement",
    "LifecycleAuthority",
    "LifecycleOwner",
    "LifecycleProjection",
    "ActivationContractReference",
    "ActivationContractRelationship",
    "ActivationContractRequirement",
    "ActivationContractAuthority",
    "ActivationContractOwner",
    "ActivationContractProjection",
    # Constants
    "CANONICAL_LIFECYCLE_GRAPH",
    "TRANSITION_VALIDATION_ENABLED",
]