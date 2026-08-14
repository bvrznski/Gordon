# Alerting Network Package
# =========================

"""
AlertingNetwork - Gordon's exogenous attention-demand coordination Network.

Canonical Definition:
    The AlertingNetwork is Gordon's exogenous-attention coordination Network,
    responsible for transforming externally originating or unexpectedly emerging
    signals into structured, explainable, bounded assessments of attentional
    demand.

Architectural Role:
    Exogenous Attention Demand Assessment

Public API:
    - AlertingNetworkProtocol: Abstract interface for assessment and state
    - AlertingNetworkConfig: Immutable configuration with nested value objects
    - AlertingNetworkDependencies: Narrow dependency container
    - AlertingInput: Canonical input contract
    - AlertingAssessment: Canonical output assessment contract
    - AlertingResetRequest: State reset request specification
    
Computational State (Phase 4.1.2):
    - AlertingSignal: Normalized observation (independent of perception)
    - AlertingFeature: Extracted measurable properties
    - AlertingEvidence: Aggregates features with confidence
    - AlertingHistory: Bounded history of signals
    - AlertingBaseline: Adaptive baseline for deviation detection
    - HabituationState: Response attenuation with repeated exposure
    - RefractoryState: Suppression after recent alerts
    - TemporalState: Recent observations and rolling statistics
    - NetworkState: Complete bounded computational state

This package does NOT:
    - Perform endogenous focus maintenance (future FocusingNetwork)
    - Authorize interruption or behavioral change
    - Schedule execution or manage runtime state
    - Route arbitrary events or commands
"""

from gordon_system.src.agent.components.networks.alerting.enums import (
    AlertingModality,
    AlertingSource,
    AlertingSourceKind,
    AlertingLevel,
    AlertingRecommendation,
    AlertingReasonCategory,
    AlertingStateTransition,
)
from gordon_system.src.agent.components.networks.alerting.models import (
    AlertingContext,
    AlertingInput,
    AlertingFeatures,
    AlertingModulation,
    AlertingReason,
    AlertingProvenance,
    AlertingStateTransitionRecord,
    AlertingAssessment,
    AlertingNetworkStateSnapshot,
    AlertingResetRequest,
)
from gordon_system.src.agent.components.networks.alerting.configuration import (
    AlertingNetworkConfig,
)
from gordon_system.src.agent.components.networks.alerting.protocol import (
    AlertingNetworkProtocol,
)
from gordon_system.src.agent.components.networks.alerting.demand_estimator import (
    AlertingDemandEstimator,
    DemandEstimatorConfig,
    EvidenceSummary,
    ModulationSummary,
)

# Phase 4.1.5 Pipeline Components
from gordon_system.src.agent.components.networks.alerting.network import (
    AlertingNetwork,
)
from gordon_system.src.agent.components.networks.alerting.constants import (
    MIN_INTENSITY,
    MAX_INTENSITY,
    FEATURE_MIN,
    FEATURE_MAX,
    DEFAULT_HABITUATION_COEFFICIENT,
    REFRACTORY_ATTENUATION_FACTOR,
)
from gordon_system.src.agent.components.networks.alerting.states import (
    # Signal models
    AlertingSignal,
    AlertingFeature,
    AlertingEvidence,
    # State models
    AlertingHistory,
    AlertingBaseline,
    HabituationState,
    RefractoryState,
    TemporalState,
    NetworkState,
    StateTransition,
    # Validation functions
    validate_signal,
    validate_feature,
    validate_evidence,
    validate_history,
    validate_baseline,
    validate_habituation,
    validate_refractory,
    validate_temporal,
    validate_network_state,
    validate_snapshot_consistency,
)

# Phase 4.1.5 Public API (Pipeline Components)
from gordon_system.src.agent.components.networks.alerting.features.analyzers import (
    FeatureAggregator,
)

__all__ = (
    # Enums
    "AlertingModality",
    "AlertingSource",
    "AlertingSourceKind",
    "AlertingLevel",
    "AlertingRecommendation",
    "AlertingReasonCategory",
    "AlertingStateTransition",
    # Models/Contracts (Phase 4.1.1)
    "AlertingContext",
    "AlertingInput",
    "AlertingFeatures",
    "AlertingModulation",
    "AlertingReason",
    "AlertingProvenance",
    "AlertingStateTransitionRecord",
    "AlertingAssessment",
    "AlertingNetworkStateSnapshot",
    "AlertingResetRequest",
    # Configuration (Phase 4.1.1)
    "AlertingNetworkConfig",
    # Protocol (Phase 4.1.1)
    "AlertingNetworkProtocol",
    # Computational State (Phase 4.1.2) - Signal models
    "AlertingSignal",
    "AlertingFeature",
    "AlertingEvidence",
    # Computational State (Phase 4.1.2) - State models
    "AlertingHistory",
    "AlertingBaseline",
    "HabituationState",
    "RefractoryState",
    "TemporalState",
    "NetworkState",
    "StateTransition",
    # Validation functions (Phase 4.1.2)
    "validate_signal",
    "validate_feature",
    "validate_evidence",
    "validate_history",
    "validate_baseline",
    "validate_habituation",
    "validate_refractory",
    "validate_temporal",
    "validate_network_state",
    "validate_snapshot_consistency",
    # Demand Estimator (Phase 4.1.4)
    "AlertingDemandEstimator",
    "DemandEstimatorConfig",
     "EvidenceSummary",
     "ModulationSummary",
     # Phase 4.1.5 Pipeline Components
     "AlertingNetwork",
     "FeatureAggregator",
     # Constants
     "MIN_INTENSITY",
     "MAX_INTENSITY",
     "FEATURE_MIN",
     "FEATURE_MAX",
     "DEFAULT_HABITUATION_COEFFICIENT",
     "REFRACTORY_ATTENUATION_FACTOR",
)
