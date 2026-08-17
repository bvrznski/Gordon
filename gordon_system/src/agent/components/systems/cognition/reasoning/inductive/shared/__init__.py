# Shared Contracts - Phase 7.2 Inductive Reasoning
# ==================================================

"""
Shared contracts for inductive reasoning.

These are the canonical data structures that all induction components use.
"""

from __future__ import annotations

# Core shared modules
from .descriptor import (
    InductionDescriptor,
    InductionSessionIdentity,
    InductionMode,
    InductionLifecycle,
)

from .observation_set import (
    InductionObservation,
    ObservationSet,
    ObservationSetIdentity,
    ObservationSource,
    ObservationKind,
)

from .pattern_search import (
    PatternCandidate,
    PatternSearch,
    PatternSearchIdentity,
    PatternSearchStrategy,
)

from .confidence import (
    InductionConfidence,
    ConfidenceComponents,
    ConfidenceCalibration,
)

from .generalization import (
    Generalization,
    GeneralizationPipeline,
    GeneralizationRefinement,
    GeneralizationCandidate,
)

from .statistics import (
    StatisticalSupport,
    StatisticalDistribution,
    StatisticalTestResult,
    StatisticalSummary,
    calculate_statistics,
)

from .hypothesis_cluster import (
    InductiveHypothesis,
    HypothesisCluster,
    HypothesisEvaluation,
    HypothesisRefinement,
)

from .outlier_analysis import (
    Outlier,
    OutlierAnalysis,
    OutlierCandidate,
    OutlierReport,
)

from .validation import (
    ValidationResult,
    ValidationFinding,
    InductionValidation,
    ValidationTrace,
    ValidationError,
)

from .governance import (
    GovernanceFinding,
    InductionGovernance,
    GovernanceEvaluation,
    GovernanceRule,
    GovernanceHealth,
)

from .failure import (
    InductionFailure,
    InductionFailureKind,
    FailureTrace,
    PartialAnalysis,
)

from .health import (
    InductionHealth,
    HealthMetrics,
    HealthSummary,
)

from .refinement import (
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