# Predictive Reasoning - Phase 7.40
# ==================================

"""
Predictive Reasoning module for Gordon Cognitive Architecture.

This module provides the **future anticipation engine** of Gordon.
It determines:

    * What is most likely to happen next;
    * How will the future evolve if nothing changes;
    * How confident should we be in predictions;
    * Where does uncertainty originate.

Predictive Reasoning produces explicit, time-indexed forecasts describing
the most probable future state given current observations and historical knowledge.
"""

from .shared import (
    # Shared Contracts
    PredictiveDescriptor,
    PredictiveSet,
    PredictionHorizon,
    ForecastingConstraints,
    PredictivePipeline,
    ObservationAnalysis,
    TrendExtraction,
    TrajectoryEstimation,
    ForecastGeneration,
    UncertaintyEstimation,
    ConsistencyAnalysis,
    ValidationResult,
    Publication,
    # Forecasts
    ForecastModel,
    ForecastIdentity,
    PredictedEvent,
    ForecastQuality,
    ConfidenceDistribution,
    # Trajectories
    TrajectoryModel,
    TrajectoryIdentity,
    TransitionSequence,
    TrajectoryConfidence,
    # Uncertainty
    ForecastUncertainty,
    UncertaintyIdentity,
    EpistemicUncertainty,
    AleatoricUncertainty,
    ConfidenceInterval,
    # Consistency
    PredictiveConsistency,
    ConsistencyIdentity,
    CrossHorizonConsistency,
    CrossModelConsistency,
    ConsistencyScore,
    # Evolution
    PredictiveEvolution,
    EvolutionIdentity,
    ForecastRevision,
    RevisionHistory,
    # Validation
    PredictiveValidation,
    ValidationResult,
    ValidationFinding,
    ValidationOutcome,
    # Failure
    PredictiveFailure,
    FailureIdentity,
    FailureKind,
    # Governance
    PredictiveGovernance,
    GovernanceIdentity,
    GovernanceFinding,
    # Health
    PredictiveHealth,
    # Diagnostics
    PredictiveDiagnostics,
    DiagnosticsRecord,
)

__all__ = [
    "PredictiveDescriptor",
    "PredictiveSet",
    "PredictionHorizon",
    "ForecastingConstraints",
    "PredictivePipeline",
    "ObservationAnalysis",
    "TrendExtraction",
    "TrajectoryEstimation",
    "ForecastGeneration",
    "UncertaintyEstimation",
    "ConsistencyAnalysis",
    "ValidationResult",
    "Publication",
    "ForecastModel",
    "ForecastIdentity",
    "PredictedEvent",
    "ForecastQuality",
    "ConfidenceDistribution",
    "TrajectoryModel",
    "TrajectoryIdentity",
    "TransitionSequence",
    "TrajectoryConfidence",
    "ForecastUncertainty",
    "UncertaintyIdentity",
    "EpistemicUncertainty",
    "AleatoricUncertainty",
    "ConfidenceInterval",
    "PredictiveConsistency",
    "ConsistencyIdentity",
    "CrossHorizonConsistency",
    "CrossModelConsistency",
    "ConsistencyScore",
    "PredictiveEvolution",
    "EvolutionIdentity",
    "ForecastRevision",
    "RevisionHistory",
    "PredictiveValidation",
    "ValidationResult",
    "ValidationFinding",
    "ValidationOutcome",
    "PredictiveFailure",
    "FailureIdentity",
    "FailureKind",
    "PredictiveGovernance",
    "GovernanceIdentity",
    "GovernanceFinding",
    "PredictiveHealth",
    "PredictiveDiagnostics",
    "DiagnosticsRecord",
]