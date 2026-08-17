# Probabilistic Reasoning Shared Contracts - Phase 7.7
# ======================================================

"""
Canonical shared contracts for the Probabilistic Reasoning subsystem.

This module provides fundamental building blocks:
- Descriptors: Expose probabilistic metadata independently of execution
- Evidence Sets: Define available evidence with source weights and dependencies
- Bayesian Pipelines: Implement canonical inference flow
- Propagation: Track uncertainty through dependency structures
- Fusion Pipelines: Integrate multiple evidence sources
- Calibration: Evaluate confidence accuracy and calibration metrics
- Uncertainty: Represent epistemic and aleatoric uncertainty explicitly
"""

from .descriptor import (
    ProbabilisticMode,
    ProbabilisticLifecycle,
    ProbabilisticDescriptor,
   ProbabilisticSessionIdentity,
)

from .evidence_set import (
    ProbabilityEvidenceSet,
    EvidenceSource,
    SourceWeight,
    DependencyGraph,
)

from .bayesian_pipeline import (
    BayesianInferencePipeline,
    PriorDistribution,
    LikelihoodModel,
    PosteriorDistribution,
)

from .propagation import (
    BeliefPropagation,
    UncertaintyPropagation,
    PropagationPath,
    DependencyStructure,
)

from .fusion_pipeline import (
    EvidenceFusionPipeline,
    FusionStrategy,
    FusedDistribution,
)

from .calibration import (
    ConfidenceCalibration,
    CalibrationMetrics,
    CalibrationAdjustment,
)

from .uncertainty import (
    UncertaintyAnalysis,
    EpistemicUncertainty,
    AleatoricUncertainty,
    UncertaintyComponent,
)

from .refinement import (
    ProbabilityModelRefinement,
    RefinementChange,
)

from .validation import (
    ProbabilisticValidationResult,
    ValidationFinding,
    ValidationRule,
)

from .failure import (
    ProbabilisticFailure,
    FailureKind,
)

from .governance import (
    ProbabilisticGovernance,
    GovernanceFinding,
    GovernanceViolation,
    GovernanceRecommendation,
)

from .health import (
    ProbabilisticHealth,
    HealthMetric,
    HealthStatus,
)

__all__ = [
    # Descriptors
    "ProbabilisticMode",
    "ProbabilisticLifecycle", 
    "ProbabilisticDescriptor",
    "ProbabilisticSessionIdentity",
    
    # Evidence
    "ProbabilityEvidenceSet",
    "EvidenceSource", 
    "SourceWeight",
    "DependencyGraph",
    
    # Bayesian Inference
    "BayesianInferencePipeline",
    "PriorDistribution",
    "LikelihoodModel",
    "PosteriorDistribution",
    
    # Propagation
    "BeliefPropagation",
    "UncertaintyPropagation",
    "PropagationPath",
    "DependencyStructure",
    
    # Fusion
    "EvidenceFusionPipeline",
    "FusionStrategy",
    "FusedDistribution",
    
    # Calibration
    "ConfidenceCalibration",
    "CalibrationMetrics",
    "CalibrationAdjustment",
    
    # Uncertainty
    "UncertaintyAnalysis",
    "EpistemicUncertainty", 
    "AleatoricUncertainty",
    "UncertaintyComponent",
    
    # Refinement
    "ProbabilityModelRefinement",
    "RefinementChange",
    
    # Validation
    "ProbabilisticValidationResult",
    "ValidationFinding",
    "ValidationRule",
    
    # Failure
    "ProbabilisticFailure",
    "FailureKind",
    
    # Governance
    "ProbabilisticGovernance",
    "GovernanceFinding",
    "GovernanceViolation",
    "GovernanceRecommendation",
    
    # Health
    "ProbabilisticHealth", 
    "HealthMetric",
    "HealthStatus",
]