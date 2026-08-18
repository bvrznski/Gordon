# Predictive Reasoning Shared Contracts - Phase 7.40
# ==================================================

"""
Shared contracts for the predictive reasoning subsystem.

This module exports all canonical contracts governing:

    * forecast management;
    * trajectory estimation;
    * trend analysis;
    * uncertainty estimation;
    * predictive consistency;
    * validation;
    * governance.
"""

from .descriptor import (
    PredictiveDescriptor,
)

from .predictive_set import (
    PredictiveSet,
    PredictionHorizon,
    ForecastingConstraints,
)

from .pipeline import (
    PredictivePipeline,
    ObservationAnalysis,
    TrendExtraction,
    TrajectoryEstimation,
    ForecastGeneration,
    UncertaintyEstimation,
    ConsistencyAnalysis,
    ValidationResult,
    Publication,
)

from .forecasts import (
    ForecastModel,
    ForecastIdentity,
    PredictedEvent,
    ForecastQuality,
    ConfidenceDistribution,
)

from .trajectories import (
    TrajectoryModel,
    TrajectoryIdentity,
    TransitionSequence,
    TrajectoryConfidence,
)

from .uncertainty import (
    ForecastUncertainty,
    UncertaintyIdentity,
    EpistemicUncertainty,
    AleatoricUncertainty,
    ConfidenceInterval,
)

from .consistency import (
    PredictiveConsistency,
    ConsistencyIdentity,
    CrossHorizonConsistency,
    CrossModelConsistency,
    ConsistencyScore,
)

from .evolution import (
    PredictiveEvolution,
    EvolutionIdentity,
    ForecastRevision,
    RevisionHistory,
)

from .validation import (
    PredictiveValidation,
    ValidationResult,
    ValidationFinding,
    ValidationOutcome,
)

from .failure import (
    PredictiveFailure,
    FailureIdentity,
    FailureKind,
)

from .governance import (
    PredictiveGovernance,
    GovernanceIdentity,
    GovernanceFinding,
)

from .health import (
    PredictiveHealth,
)

from .diagnostics import (
    PredictiveDiagnostics,
    DiagnosticsRecord,
)

__all__ = [
    # Shared
    "PredictiveDescriptor",
    # Set
    "PredictiveSet",
    "PredictionHorizon",
    "ForecastingConstraints",
    # Pipeline
    "PredictivePipeline",
    "ObservationAnalysis",
    "TrendExtraction",
    "TrajectoryEstimation",
    "ForecastGeneration",
    "UncertaintyEstimation",
    "ConsistencyAnalysis",
    "ValidationResult",
    "Publication",
    # Forecasts
    "ForecastModel",
    "ForecastIdentity",
    "PredictedEvent",
    "ForecastQuality",
    "ConfidenceDistribution",
    # Trajectories
    "TrajectoryModel",
    "TrajectoryIdentity",
    "TransitionSequence",
    "TrajectoryConfidence",
    # Uncertainty
    "ForecastUncertainty",
    "UncertaintyIdentity",
    "EpistemicUncertainty",
    "AleatoricUncertainty",
    "ConfidenceInterval",
    # Consistency
    "PredictiveConsistency",
    "ConsistencyIdentity",
    "CrossHorizonConsistency",
    "CrossModelConsistency",
    "ConsistencyScore",
    # Evolution
    "PredictiveEvolution",
    "EvolutionIdentity",
    "ForecastRevision",
    "RevisionHistory",
    # Validation
    "PredictiveValidation",
    "ValidationResult",
    "ValidationFinding",
    "ValidationOutcome",
    # Failure
    "PredictiveFailure",
    "FailureIdentity",
    "FailureKind",
    # Governance
    "PredictiveGovernance",
    "GovernanceIdentity",
    "GovernanceFinding",
    # Health
    "PredictiveHealth",
    # Diagnostics
    "PredictiveDiagnostics",
    "DiagnosticsRecord",
]