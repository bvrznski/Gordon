# Probabilistic Reasoning - Phase 7.7
# ===================================

"""
Probabilistic Reasoning is Gordon's uncertainty management engine.

Unlike the Belief subsystem, which maintains epistemic commitments,
Probabilistic Reasoning represents uncertainty itself as a first-class cognitive
object.

This separation is important:

Beliefs answer:     "What does Gordon currently accept?"
Probabilistic:      "How uncertain is Gordon about every alternative?"

# Architecture

cognition/
└── reasoning/
    └── probabilistic/
        ├── shared/          # Shared contracts (descriptors, pipelines, etc.)
        │   ├── descriptor.py
        │   ├── evidence_set.py
        │   ├── bayesian_pipeline.py
        │   ├── propagation.py
        │   ├── fusion_pipeline.py
        │   ├── calibration.py
        │   ├── uncertainty.py
        │   ├── refinement.py
        │   ├── validation.py
        │   ├── failure.py
        │   ├── governance.py
        │   └── health.py
        ├── distributions/     # Probability distribution implementations
        ├── inference/         # Bayesian inference algorithms
        ├── propagation/       # Belief propagation engines
        ├── observability/     # Monitoring and logging
        └── validation/        # Validation layer

# Probabilistic Laws

## Global Probabilistic Laws

PROBABILISTIC-LAW-001: Every session has one immutable Semantic Identity.
PROBABILISTIC-LAW-002: Reasoning executes over one explicit Evidence Set.
PROBABILISTIC-LAW-003: Every posterior references explicit priors and evidence.
PROBABILISTIC-LAW-004: Probabilistic Reasoning preserves provenance.
PROBABILISTIC-LAW-005: Probabilistic Reasoning preserves reasoning lineage.
PROBABILISTIC-LAW-006: Probabilistic Reasoning remains independently inspectable.
PROBABILISTIC-LAW-007: Deterministic given identical evidence, priors and configuration.
PROBABILISTIC-LAW-008: Completed Probabilistic Sessions remain immutable.

## Probability Model Laws

MODEL-LAW-001: Every model has one explicit identity.
MODEL-LAW-002: Variables are explicitly represented.
MODEL-LAW-003: Dependencies are explicit.
MODEL-LAW-004: Model provenance is complete.
MODEL-LAW-005: Revisions preserve history.
MODEL-LAW-006: No implicit assumptions.
MODEL-LAW-007: Models are independently inspectable.
MODEL-LAW-008: Equivalent models produce equivalent inference.

## Prior Laws

PRIOR-LAW-001: Every prior has one explicit origin.
PRIOR-LAW-002: Prior confidence is explicit.
PRIOR-LAW-003: Prior applicability is explicit.
PRIOR-LAW-004: Prior provenance is complete.
PRIOR-LAW-005: Revisions preserve history.
PRIOR-LAW-006: Priors are never fabricated.
PRIOR-LAW-007: Priors are independently inspectable.
PRIOR-LAW-008: Equivalent priors produce equivalent posteriors.

## Bayesian Inference Laws

BAYES-LAW-001: Likelihood functions remain explicit.
BAYES-LAW-002: Posterior distributions remain reconstructable.
BAYES-LAW-003: Inference assumptions are explicit.
BAYES-LAW-004: Inference provenance is complete.
BAYES-LAW-005: Revisions preserve history.
BAYES-LAW-006: Posteriors never replace accepted Beliefs automatically.
BAYES-LAW-007: Inference remains independently inspectable.
BAYES-LAW-008: Equivalent priors and evidence produce equivalent posteriors.

## Uncertainty Laws

UNCERTAINTY-LAW-001: Uncertainty is a first-class cognitive artifact.
UNCERTAINTY-LAW-002: Epistemic and aleatoric uncertainty are distinguishable.
UNCERTAINTY-LAW-003: Uncertainty sources are explicit.
UNCERTAINTY-LAW-004: Uncertainty provenance is complete.
UNCERTAINTY-LAW-005: Revisions preserve history.
UNCERTAINTY-LAW-006: Uncertainty is never silently discarded.
UNCERTAINTY-LAW-007: Uncertainty remains independently inspectable.
UNCERTAINTY-LAW-008: Equivalent inference produces equivalent uncertainty.

## Calibration Laws

CALIBRATION-LAW-001: Calibration metrics remain explicit.
CALIBRATION-LAW-002: Prediction performance is measurable.
CALIBRATION-LAW-003: Confidence errors are explicit.
CALIBRATION-LAW-004: Calibration provenance is complete.
CALIBRATION-LAW-005: Revisions preserve history.
CALIBRATION-LAW-006: Calibration never modifies Probability Models directly.
CALIBRATION-LAW-007: Calibration remains independently inspectable.
CALIBRATION-LAW-008: Equivalent prediction histories produce equivalent calibration.

## Propagation Laws

PROPAGATION-LAW-001: Propagation preserves dependency structure.
PROPAGATION-LAW-002: Propagation paths remain reconstructable.
PROPAGATION-LAW-003: Joint dependencies are explicit.
PROPAGATION-LAW-004: Propagation provenance is complete.
PROPAGATION-LAW-005: Revisions preserve history.
PROPAGATION-LAW-006: Dependency constraints are never ignored.
PROPAGATION-LAW-007: Propagation remains independently inspectable.
PROPAGATION-LAW-008: Equivalent graphs produce equivalent propagation.

## Validation Laws

VALIDATION-LAW-001: Validation remains observational.
VALIDATION-LAW-002: Validation preserves findings.
VALIDATION-LAW-003: Poor calibration is distinguished from incorrect inference.
VALIDATION-LAW-004: Validation provenance is complete.
VALIDATION-LAW-005: Validation history is immutable.
VALIDATION-LAW-006: Validation never modifies probabilistic artifacts directly.
VALIDATION-LAW-007: Validation remains independently inspectable.
VALIDATION-LAW-008: Equivalent sessions produce equivalent validation results.

## Failure Laws

FAILURE-LAW-001: Probabilistic Failures remain explicit.
FAILURE-LAW-002: Failure causes are identifiable.
FAILURE-LAW-003: Partial inference results remain reconstructable.
FAILURE-LAW-004: Recovery strategies are explicit.
FAILURE-LAW-005: Failure provenance is complete.
FAILURE-LAW-006: Failures never silently discard evidence.
FAILURE-LAW-007: Failures remain independently inspectable.
FAILURE-LAW-008: Equivalent failures produce equivalent diagnostics.

## Governance Laws

GOVERNANCE-LAW-001: Governance remains observational.
GOVERNANCE-LAW-002: Invalid models are detected.
GOVERNANCE-LAW-003: Calibration drift is detected.
GOVERNANCE-LAW-004: Nondeterministic inference is detected.
GOVERNANCE-LAW-005: Governance preserves findings.
GOVERNANCE-LAW-006: Provenance is preserved.
GOVERNANCE-LAW-007: Governance never modifies probabilistic artifacts directly.
GOVERNANCE-LAW-008: Equivalent sessions produce equivalent governance evaluations.

# Anti-Patterns

Reject implementations that:
- Fabricate priors
- Hide likelihood functions
- Discard uncertainty estimates
- Convert posteriors to Beliefs automatically
- Ignore dependency structures
- Silently recalibrate models
- Bypass validation or governance
- Lose provenance
- Violate deterministic execution

# Future Extensions

* Hybrid probabilistic inference (symbolic + neural)
* Hierarchical uncertainty representation
* Meta-uncertainty about reasoning processes
* Confidence-aware planning
"""

from __future__ import annotations

# Import shared contracts
from .shared.descriptor import (
    ProbabilisticMode,
    ProbabilisticLifecycle,
    ProbabilisticDescriptor,
    ProbabilisticSessionIdentity,
)

from .shared.evidence_set import (
    ProbabilityEvidenceSet,
    EvidenceSource,
    SourceWeight,
    DependencyGraph,
    EvidenceQuality,
    DependencyType,
)

from .shared.bayesian_pipeline import (
    BayesianInferencePipeline,
    PriorDistribution,
    LikelihoodModel,
    PosteriorDistribution,
)

from .shared.propagation import (
    BeliefPropagation,
    UncertaintyPropagation,
    PropagationPath,
    DependencyStructure,
)

from .shared.fusion_pipeline import (
    EvidenceFusionPipeline,
    FusionStrategy,
    FusedDistribution,
)

from .shared.calibration import (
    ConfidenceCalibration,
    CalibrationMetrics,
    CalibrationAdjustment,
)

from .shared.uncertainty import (
    UncertaintyAnalysis,
    EpistemicUncertainty,
    AleatoricUncertainty,
    UncertaintyComponent,
)

from .shared.refinement import (
    ProbabilityModelRefinement,
    RefinementChange,
)

from .shared.validation import (
    ProbabilisticValidationResult,
    ValidationFinding,
    ValidationRule,
)

from .shared.failure import (
    ProbabilisticFailure,
    FailureKind,
)

from .shared.governance import (
    ProbabilisticGovernance,
    GovernanceFinding,
    GovernanceViolation,
    GovernanceRecommendation,
)

from .shared.health import (
    ProbabilisticHealth,
    HealthMetric,  # type: ignore
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
    "EvidenceQuality",
    "DependencyType",
    
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