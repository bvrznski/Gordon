# Experimental Reasoning - Phase 7.16
# ======================================

"""
Experimental Reasoning subsystem for Gordon Cognitive Architecture.

This module implements the canonical contracts and components for:
- Experiment design
- Intervention planning
- Measurement planning
- Control conditions
- Information gain estimation
- Experiment refinement
- Validation
- Governance

Experimental Reasoning is Gordon's active knowledge acquisition engine.
It designs structured experiments for acquiring evidence, transforming
uncertainty into measurable observations without executing them directly.

Reference: Phase 7.16 Specification - Experimental Reasoning
"""

from __future__ import annotations

from .shared.descriptor import (
    ExperimentalDescriptor,
    ExperimentMode,
    LifecycleState,
)

from .shared.experiment_set import (
    ExperimentSet,
    ExperimentSetIdentity,
)

from .shared.interventions import (
    Intervention,
    InterventionType,
    InterventionTarget,
    InterventionAnalysis,
)

from .shared.measurements import (
    MeasurementPlan,
    ObservedVariable,
    SamplingStrategy,
    UncertaintyEstimate,
    MeasurementPlanning,
)

from .shared.controls import (
    ControlCondition,
    ControlType,
    BaselineDefinition,
    ControlManagement,
)

from .shared.information_gain import (
    InformationGainEstimate,
    EstimationMethod,
)

from .shared.refinement import (
    ExperimentalRefinement,
)

from .shared.validation import (
    ValidationResult,
    ValidationIssue,
    ValidationReport,
)

from .shared.failure import (
    ExperimentalFailure,
    FailureKind,
    RecoveryOption,
    FailureReport,
)

from .shared.governance import (
    ExperimentalGovernance,
    GovernanceFinding,
    GovernanceEvaluation,
)

from .shared.health import (
    ExperimentalHealth,
    HealthMetric,
    HealthSummary,
)

from .shared.diagnostics import (
    DiagnosticRecord,
    DiagnosticsSummary,
    DiagnosticReport,
)

from .shared.experiment_set import (
    ExperimentSet,
    ExperimentSetIdentity,
)

from .shared.interventions import (
    Intervention,
    InterventionType,
    InterventionTarget,
    InterventionAnalysis,
)

from .shared.measurements import (
    MeasurementPlan,
    ObservedVariable,
    SamplingStrategy,
    UncertaintyEstimate,
    MeasurementPlanning,
)

from .shared.controls import (
    ControlCondition,
    ControlType,
    BaselineDefinition,
    ControlManagement,
)

from .shared.information_gain import (
    InformationGainEstimate,
    EstimationMethod,
)

from .shared.refinement import (
    ExperimentalRefinement,
)

from .shared.validation import (
    ValidationResult,
    ValidationIssue,
)

from .shared.failure import (
    ExperimentalFailure,
    FailureKind,
    RecoveryOption,
)

from .shared.governance import (
    ExperimentalGovernance,
    GovernanceFinding,
    GovernanceEvaluation,
)

from .shared.health import (
    ExperimentalHealth,
    HealthMetric,
)

from .shared.diagnostics import (
    DiagnosticRecord,
    DiagnosticsSummary,
)

__all__ = [
    # Shared Components
    "ExperimentalDescriptor",
    "ExperimentMode",
    "LifecycleState",
    "ExperimentSet",
    "ExperimentSetIdentity",
    
    # Intervention
    "Intervention",
    "InterventionType",
    "InterventionTarget",
    "InterventionAnalysis",
    
    # Measurement
    "MeasurementPlan",
    "ObservedVariable",
    "SamplingStrategy",
    "UncertaintyEstimate",
    "MeasurementPlanning",
    
    # Control
    "ControlCondition",
    "ControlType",
    "BaselineDefinition",
    "ControlManagement",
    
    # Information Gain
    "InformationGainEstimate",
    "EstimationMethod",
    
    # Refinement
    "ExperimentalRefinement",
    
    # Validation
    "ValidationResult",
    "ValidationIssue",
    "ValidationReport",
    
    # Failure
    "ExperimentalFailure",
    "FailureKind",
    "RecoveryOption",
    "FailureReport",
    
    # Governance
    "ExperimentalGovernance",
    "GovernanceFinding",
    "GovernanceEvaluation",
    
    # Health
    "ExperimentalHealth",
    "HealthMetric",
    "HealthSummary",
    
    # Diagnostics
    "DiagnosticRecord",
    "DiagnosticsSummary",
    "DiagnosticReport",
]
