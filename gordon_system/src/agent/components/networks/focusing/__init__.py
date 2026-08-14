# Focusing Network Package
# =========================

"""
Gordon's endogenous attention-policy computation network scaffold.

The FocusingNetwork computes focus policies for Gordon's cognitive architecture.
It determines what deserves sustained attention, how strongly, for how long,
with what precision, and under which constraints - without executing actions
or owning cognition itself.

Architecture:
    Core → Execution → Capabilities → Attention Capability → Focusing Network

See Also:
    - AlertingNetwork: Computes "what deserves unexpected attention?"
    - FocusingNetwork: Computes "what should remain the focus?"

Phase 4.2.2 - Canonical Computational Substrate:
    This phase establishes the immutable computational models upon which every
    future algorithm in the Focusing Network operates.

    Exports:
        • Identity types (FocusTargetId, CandidateId, AssessmentId, etc.)
        • ProvenanceRecord (for tracking origin without runtime references)
        • FocusTarget (immutable representation of attention target)
        • FocusCandidate (transient candidate during evaluation)
        • FocusAssessmentReference (link to assessment without circular deps)
        • Descriptor objects (single responsibility, independently replaceable):
          - PriorityDescriptor
          - RelevanceDescriptor
          - SuppressionDescriptor
          - PrecisionDescriptor
          - PersistenceDescriptor
          - AllocationDescriptor
          - BiasDescriptor
        • State classes (bounded, explicit state representations):
          - FocusState, PriorityState, RelevanceState, etc.
        • FocusingNetworkState (complete composed state)
        • StateTransition (explicit transition model)
        • FocusSnapshot (immutable snapshot of state at point in time)
        • ValidationResult and validation functions

NO BEHAVIOR:
    This phase does NOT implement algorithms. Future phases add:
        • priority computation
        • competition analysis
        • suppression logic
        • allocation algorithms
        • precision estimation
        • persistence algorithms
        • assessment generation
"""

from gordon_system.src.agent.components.networks.focusing.__meta__ import __version__
from gordon_system.src.agent.components.networks.focusing.enums import (
    FocusModality,
    FocusSource,
    PriorityLevel,
    PrecisionBandwidth,
    PersistenceMode,
    BiasModality,
)
from gordon_system.src.agent.components.networks.focusing.constants import (
    SUPPRESSION_THRESHOLD,
    COMPETITION_THRESHOLD,
    PERSISTENCE_INCREASE_THRESHOLD,
    SHIFT_ALLOWANCE_THRESHOLD,
    DEFAULT_DECAY_RATE,
    MAX_HISTORY_LENGTH,
)
from gordon_system.src.agent.components.networks.focusing.configuration import (
    FocusingNetworkConfig,
)

# Contract interfaces (phase 4.2.1 scaffolding only - no implementations yet)
from gordon_system.src.agent.components.networks.focusing.contracts import (
    FocusCandidateProvider,
    FocusContextProvider,
    FocusAssessmentConsumer,
    FocusDiagnosticsSink,
    FocusStateProvider,
    FocusConfigurationProvider,
    FocusInputConsumer,
)

# Architectural tree for navigation
from gordon_system.src.agent.components.networks.focusing.__tree__ import FocusingArchitecture

# Network orchestration (protocol only, implementation deferred)
from gordon_system.src.agent.components.networks.focusing.protocol import (
    FocusingNetworkProtocol,
)

# =============================================================================
# PHASE 4.2.2: Canonical Computational Models
# =============================================================================

from gordon_system.src.agent.components.networks.focusing.models import (
    # Identity types (stable, independent identifiers)
    FocusTargetId,
    CandidateId,
    AssessmentId,
    TransitionId,
    SnapshotId,
    
    # Provenance (preserves origin without runtime references)
    ProvenanceRecord,
    
    # Primary computational entities
    FocusTarget,
    FocusCandidate,
    FocusAssessmentReference,
    
    # Descriptor objects (single responsibility, independently replaceable)
    PriorityDescriptor,
    RelevanceDescriptor,
    SuppressionDescriptor,
    PrecisionDescriptor,
    PersistenceDescriptor,
    AllocationDescriptor,
    BiasDescriptor,
    
    # State classes (bounded, explicit state representations)
    FocusState,
    PriorityState,
    RelevanceState,
    SuppressionState,
    PersistenceState,
    PrecisionState,
    AllocationState,
    BiasState,
    HistoryState,
    DiagnosticsState,
    
    # Composition
    FocusingNetworkState,
    
    # Transitions and snapshots
    StateTransition,
    FocusSnapshot,
    
    # Validation
    ValidationResult,
    validate_focus_target,
    validate_focus_candidate,
    validate_history_state,
    validate_network_state,
    
    # Utilities
    dataclass_replace,
)

# Network orchestration (protocol only, implementation deferred)
from gordon_system.src.agent.components.networks.focusing.protocol import (
    FocusingNetworkProtocol,
)

from gordon_system.src.agent.components.networks.focusing.priority.estimators import (
    GoalRelevanceEstimator,
    ContextRelevanceEstimator,
    PolicyModulator,
    HistoricalPriorityModel,
    PriorityAggregator,
    PriorityNormalizer,
    PriorityConfidenceEstimator,
    PriorityAssessment,
    RelevanceAssessment,
    PriorityEvidence,
    PriorityComponent,
    PriorityVector,
    PriorityBreakdown,
    PriorityConfidence,
    PriorityExplanation,
    PrioritySummary,
    PriorityState,
    PriorityHistory,
    PrioritySnapshots,
)

# =============================================================================
# PHASE 4.2.4: Competition Resolution and Suppression Model
# =============================================================================

from gordon_system.src.agent.components.networks.focusing.competition import (
    # Relationship types
    CompetitionRelationship,
    
    # Competition descriptors (immutable data)
    CompetitionDescriptor,
    CompetitionContribution,
    CompetitionEvidence,
    CompetitionBreakdown,
    CompetitionExplanation,
    CompetitionConfidence,
    SuppressionDescriptor,
    SuppressionContribution,
    SuppressionEvidence,
    SuppressionSummary,
    
    # Assessment outputs
    CompetitionAssessment,
    SuppressionAssessment,
    DominanceAssessment,
    CompatibilityAssessment,
    ConflictAssessment,
    
    # Matrix representation
    CompetitionMatrix,
    CompetitionMatrixEntry,
    
    # State classes (for persistence)
    CompetitionState,
    SuppressionState,
    CompetitionHistory,
    CompetitionSnapshots,
    
    # Diagnostic data
    CompetitionDiagnostics,
    
    # Algorithm estimators
    CompetitionAnalyzer,
    ConflictDetector,
    CompatibilityEstimator,
    SuppressionEstimator,
    DominanceAnalyzer,
)

__all__ = [
    "__version__",
    "FocusModality",
    "FocusSource",
    "PriorityLevel",
    "PrecisionBandwidth",
    "PersistenceMode",
    "BiasModality",
    "SUPPRESSION_THRESHOLD",
    "COMPETITION_THRESHOLD",
    "PERSISTENCE_INCREASE_THRESHOLD",
    "SHIFT_ALLOWANCE_THRESHOLD",
    "DEFAULT_DECAY_RATE",
    "MAX_HISTORY_LENGTH",
    "FocusingNetworkConfig",
    # Contract interfaces
    "FocusCandidateProvider",
    "FocusContextProvider",
    "FocusAssessmentConsumer",
    "FocusDiagnosticsSink",
    "FocusStateProvider",
    "FocusConfigurationProvider",
    "FocusInputConsumer",
    # Architecture navigation
    "FocusingArchitecture",
    # Protocol interfaces (no implementation)
    "FocusingNetworkProtocol",
    # =============================================================================
    # PHASE 4.2.3: Goal-Directed Relevance Estimation and Priority Aggregation
    # =============================================================================
    
    # Estimators (algorithms)
    "GoalRelevanceEstimator",
    "ContextRelevanceEstimator",
    "PolicyModulator",
    "HistoricalPriorityModel",
    "PriorityAggregator",
    "PriorityNormalizer",
    "PriorityConfidenceEstimator",
    
    # Immutable assessment outputs
    "PriorityAssessment",
    "RelevanceAssessment",
    "PriorityEvidence",
    "PriorityComponent",
    "PriorityVector",
    "PriorityBreakdown",
    "PriorityConfidence",
    "PriorityExplanation",
    "PrioritySummary",
    
    # State (for persistence)
    "PriorityState",
    "PriorityHistory",
    "PrioritySnapshots",
    
    # =============================================================================
    # PHASE 4.2.4: Competition Resolution and Suppression Model
    # =============================================================================
    
    # Relationship types
    "CompetitionRelationship",
    
    # Competition descriptors (immutable data)
    "CompetitionDescriptor",
    "CompetitionContribution",
    "CompetitionEvidence",
    "CompetitionBreakdown",
    "CompetitionExplanation",
    "CompetitionConfidence",
    "SuppressionDescriptor",
    "SuppressionContribution",
    "SuppressionEvidence",
    "SuppressionSummary",
    
    # Assessment outputs
    "CompetitionAssessment",
    "SuppressionAssessment",
    "DominanceAssessment",
    "CompatibilityAssessment",
    "ConflictAssessment",
    
    # Matrix representation
    "CompetitionMatrix",
    "CompetitionMatrixEntry",
    
    # State classes (for persistence)
    "CompetitionState",
    "SuppressionState",
    "CompetitionHistory",
    "CompetitionSnapshots",
    
    # Diagnostic data
    "CompetitionDiagnostics",
    
    # Algorithm estimators
    "CompetitionAnalyzer",
    "ConflictDetector",
    "CompatibilityEstimator",
    "SuppressionEstimator",
    "DominanceAnalyzer",
    
    # =============================================================================
    # PHASE 4.2.2: Canonical Computational Models
    # =============================================================================
    
    # Identity types (stable, independent identifiers)
    "FocusTargetId",
    "CandidateId",
    "AssessmentId",
    "TransitionId",
    "SnapshotId",
    
    # Provenance (preserves origin without runtime references)
    "ProvenanceRecord",
    
    # Primary computational entities
    "FocusTarget",
    "FocusCandidate",
    "FocusAssessmentReference",
    
    # Descriptor objects (single responsibility, independently replaceable)
    "PriorityDescriptor",
    "RelevanceDescriptor",
    "SuppressionDescriptor",
    "PrecisionDescriptor",
    "PersistenceDescriptor",
    "AllocationDescriptor",
    "BiasDescriptor",
    
    # State classes (bounded, explicit state representations)
    "FocusState",
    "PriorityState",
    "RelevanceState",
    "SuppressionState",
    "PersistenceState",
    "PrecisionState",
    "AllocationState",
    "BiasState",
    "HistoryState",
    "DiagnosticsState",
    
    # Composition
    "FocusingNetworkState",
    
    # Transitions and snapshots
    "StateTransition",
    "FocusSnapshot",
    
    # Validation
    "ValidationResult",
    "validate_focus_target",
    "validate_focus_candidate",
    "validate_history_state",
    "validate_network_state",
    
    # Utilities
    "dataclass_replace",
]