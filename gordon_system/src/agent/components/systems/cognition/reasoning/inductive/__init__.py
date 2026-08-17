# Inductive Reasoning - Phase 7.2
# ================================

"""
Canonical inductive reasoning module.

Inductive Reasoning is Gordon's knowledge expansion engine.
It derives generalized knowledge from observations through pattern discovery,
statistical inference, and hypothesis formation.

This module implements Part 3 of Phase 7.2, specifying:
- Induction Laws (normative specifications)
- Observation Laws
- Pattern Laws  
- Generalization Laws
- Statistical Laws
- Outlier Laws
- Validation Laws
- Governance Laws

Architectural Note: Inductive reasoning produces candidate assertions,
not accepted knowledge. These candidates enter the belief subsystem for
evaluation and potential acceptance as long-term knowledge.
"""

from __future__ import annotations

# Shared contracts
from .shared.descriptor import (
    InductionDescriptor,
    InductionSessionIdentity,
    InductionMode,
    InductionLifecycle,
)

from .shared.observation_set import (
    InductionObservation,
    ObservationSet,
    ObservationSetIdentity,
    ObservationSource,
    ObservationKind,
)

from .shared.pattern_search import (
    PatternCandidate,
    PatternSearch,
    PatternSearchIdentity,
    PatternSearchStrategy,
)

from .shared.confidence import (
    InductionConfidence,
    ConfidenceComponents,
    ConfidenceCalibration,
)

from .shared.generalization import (
    Generalization,
    GeneralizationPipeline,
    GeneralizationRefinement,
    GeneralizationCandidate,
)

from .shared.statistics import (
    StatisticalSupport,
    StatisticalDistribution,
    StatisticalTestResult,
    StatisticalSummary,
    calculate_statistics,
)

from .shared.hypothesis_cluster import (
    InductiveHypothesis,
    HypothesisCluster,
    HypothesisEvaluation,
    HypothesisRefinement,
)

from .shared.outlier_analysis import (
    Outlier,
    OutlierAnalysis,
    OutlierCandidate,
    OutlierReport,
)

from .shared.validation import (
    ValidationResult,
    ValidationFinding,
    InductionValidation,
    ValidationTrace,
    ValidationError,
)

from .shared.governance import (
    GovernanceFinding,
    InductionGovernance,
    GovernanceEvaluation,
    GovernanceRule,
    GovernanceHealth,
)

from .shared.failure import (
    InductionFailure,
    InductionFailureKind,
    FailureTrace,
    PartialAnalysis,
)

from .shared.health import (
    InductionHealth,
    HealthMetrics,
    HealthSummary,
)

from .shared.refinement import (
    GeneralizationRefinement,
    PatternRefinement,
    HypothesisRefinement,
    RefinementTrace,
)


__all__ = [
    # Descriptor
    "InductionDescriptor",
    "InductionSessionIdentity",
    "InductionMode",
    "InductionLifecycle",
    # Observation Set
    "InductionObservation",
    "ObservationSet",
    "ObservationSetIdentity",
    "ObservationSource",
    "ObservationKind",
    # Pattern Search
    "PatternCandidate",
    "PatternSearch",
    "PatternSearchIdentity",
    "PatternSearchStrategy",
    # Confidence
    "InductionConfidence",
    "ConfidenceComponents",
    "ConfidenceCalibration",
    # Generalization
    "Generalization",
    "GeneralizationPipeline",
    "GeneralizationRefinement",
    "GeneralizationCandidate",
    # Statistics
    "StatisticalSupport",
    "StatisticalDistribution",
    "StatisticalTestResult",
    "StatisticalSummary",
    "calculate_statistics",
    # Hypothesis Cluster
    "InductiveHypothesis",
    "HypothesisCluster",
    "HypothesisEvaluation",
    "HypothesisRefinement",
    # Outlier Analysis
    "Outlier",
    "OutlierAnalysis",
    "OutlierCandidate",
    "OutlierReport",
    # Validation
    "ValidationResult",
    "ValidationFinding",
    "InductionValidation",
    "ValidationTrace",
    "ValidationError",
    # Governance
    "GovernanceFinding",
    "InductionGovernance",
    "GovernanceEvaluation",
    "GovernanceRule",
    "GovernanceHealth",
    # Failure
    "InductionFailure",
    "InductionFailureKind",
    "FailureTrace",
    "PartialAnalysis",
    # Health
    "InductionHealth",
    "HealthMetrics",
    "HealthSummary",
    # Refinement
    "GeneralizationRefinement",
    "PatternRefinement",
    "HypothesisRefinement",
    "RefinementTrace",
]

__version__ = "1.0.0"