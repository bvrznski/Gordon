# Gordon Executive Network - Phase 4.4.6 Performance Monitoring
# ===============================================================

"""
Phase 4.4.6 — Performance, Outcome, and Error Monitoring.

This is the semantic architecture through which the Executive Network evaluates
whether ongoing cognition and behavior are producing acceptable progress and outcomes.

This phase defines how the Executive Network observes, represents, assesses, and
communicates:

* progress;
* performance;
* outcomes;
* expectations;
* deviations;
* errors;
* prediction errors;
* failures;
* partial success;
* stagnation;
* regressions;
* inefficiency;
* excessive effort;
* repeated failure;
* completion evidence;
* outcome quality;
* strategy effectiveness;
* task-set effectiveness;
* control effectiveness;
* recovery effectiveness;
* commitment fulfillment progress;
* goal satisfaction progress;
* unexpected side effects;
* missing outcomes;
* delayed outcomes;
* disputed outcomes;
* uncertain outcomes.

ARCHITECTURAL PRINCIPLES:
========================

Executive Performance is:
    * Semantic - NOT runtime telemetry (CPU, GPU, latency, etc.)
    * Bounded - Limited in scope and duration
    * Evidence-backed - Based on concrete evidence
    * Revisioned - Maintains history and lineage
    * Immutable - Public contracts are frozen dataclasses

The Executive Network does NOT:
    * Run timers for stagnation assessment (uses supplied SemanticTime)
    * Directly mutate Programs, Task Sets, Goals, or Commitments
    * Execute recovery without authority
    * Replace strategy directly
    * Allocate control directly
    * Retry actions directly
    * Create threads or schedulers

INTEGRATION PRINCIPLES:
======================

The Performance Monitoring subsystem:

CONSUMES (PROJECTIONS):
    * Executive State and Context projections
    * Program, Task Set references
    * Goal and Commitment references
    * Expected outcome projections
    * Actual outcome projections
    * Evidence projections
    * Prediction error projections
    * Evaluation results

PRODUCES (PRODUCTS):
    * Performance Assessment proposals
    * Outcome Assessment reports
    * Progress Assessment summaries
    * Error Detection reports
    * Strategy Performance assessments
    * Task Set Performance assessments
    * Control Effectiveness assessments
    * Completion recommendations
    * Review proposals

CONTRACTS:
    * Integration is through well-defined contracts
    * No direct dependency on concrete implementations
    * All dependencies are via protocols or immutable projections

VERSION: 1.0.0
COMPATIBILITY: forward (phased implementation)
DEPRECATION: three_releases policy
EXTENSION STRATEGY: additive_only
"""

# =============================================================================
# IMPORTS - Performance and outcome monitoring canonical contracts
# =============================================================================

from gordon_system.src.agent.networks.executive.performance.subject import (
    ExecutivePerformanceSubject,
    ExecutivePerformanceSubjectKind,
)

from gordon_system.src.agent.networks.executive.performance.criteria import (
    ExecutivePerformanceCriteria,
    ExecutivePerformanceCriterion,
)

from gordon_system.src.agent.networks.executive.performance.evidence import (
    ExecutivePerformanceEvidence,
    ExecutivePerformanceEvidenceKind,
)

from gordon_system.src.agent.networks.executive.performance.dimension import (
    ExecutivePerformanceDimension,
    ExecutivePerformanceDimensionAssessment,
)

from gordon_system.src.agent.networks.executive.performance.status import (
    ExecutivePerformanceStatus,
)

from gordon_system.src.agent.networks.executive.performance.trend import (
    ExecutivePerformanceTrend,
)

from gordon_system.src.agent.networks.executive.performance.confidence import (
    ExecutivePerformanceConfidence,
)

from gordon_system.src.agent.networks.executive.performance.completeness import (
    ExecutivePerformanceCompleteness,
)

from gordon_system.src.agent.networks.executive.performance.validity import (
    ExecutivePerformanceValidity,
)

from gordon_system.src.agent.networks.executive.performance.provenance import (
    ExecutivePerformanceProvenance,
)

# =============================================================================
# Performance Assessment - Core contract
# =============================================================================

from gordon_system.src.agent.networks.executive.performance.assessment import (
    ExecutivePerformanceAssessment,
)

# =============================================================================
# Outcome Architecture
# =============================================================================

from gordon_system.src.agent.networks.executive.outcomes.expected import (
    ExecutiveExpectedOutcome,
)

from gordon_system.src.agent.networks.executive.outcomes.actual import (
    ExecutiveActualOutcome,
)

from gordon_system.src.agent.networks.executive.outcomes.evidence import (
    ExecutiveOutcomeEvidence,
)

from gordon_system.src.agent.networks.executive.outcomes.correspondence import (
    ExecutiveOutcomeCorrespondence,
)

from gordon_system.src.agent.networks.executive.outcomes.divergence import (
    ExecutiveOutcomeDivergence,
)

from gordon_system.src.agent.networks.executive.outcomes.quality import (
    ExecutiveOutcomeQuality,
)

from gordon_system.src.agent.networks.executive.outcomes.completeness import (
    ExecutiveOutcomeCompleteness,
)

from gordon_system.src.agent.networks.executive.outcomes.certainty import (
    ExecutiveOutcomeCertainty,
)

from gordon_system.src.agent.networks.executive.outcomes.side_effect import (
    ExecutiveOutcomeSideEffect,
)

from gordon_system.src.agent.networks.executive.outcomes.reversibility import (
    ExecutiveOutcomeReversibility,
)

from gordon_system.src.agent.networks.executive.outcomes.acceptance import (
    ExecutiveOutcomeAcceptance,
)

# =============================================================================
# Outcome Assessment
# =============================================================================

from gordon_system.src.agent.networks.executive.outcomes.assessment import (
    ExecutiveOutcomeAssessment,
)

# =============================================================================
# Progress and Completion Architecture
# =============================================================================

from gordon_system.src.agent.networks.executive.progress.baseline import (
    ExecutiveProgressBaseline,
)

from gordon_system.src.agent.networks.executive.progress.assessment import (
    ExecutiveProgressAssessment,
)

from gordon_system.src.agent.networks.executive.progress.sufficiency import (
    ExecutiveProgressSufficiency,
)

from gordon_system.src.agent.networks.executive.progress.stagnation import (
    ExecutiveStagnationAssessment,
)

from gordon_system.src.agent.networks.executive.progress.regression import (
    ExecutiveRegressionAssessment,
)

from gordon_system.src.agent.networks.executive.progress.completion import (
    ExecutiveCompletionAssessment,
)

# =============================================================================
# Error Architecture
# =============================================================================

from gordon_system.src.agent.networks.executive.errors.identity import (
    ExecutiveErrorId,
    ExecutiveErrorRevision,
    ExecutiveErrorSchemaVersion,
)

from gordon_system.src.agent.networks.executive.errors.kind import (
    ExecutiveErrorKind,
)

from gordon_system.src.agent.networks.executive.errors.status import (
    ExecutiveErrorStatus,
)

from gordon_system.src.agent.networks.executive.errors.subject import (
    ExecutiveErrorSubject,
)

from gordon_system.src.agent.networks.executive.errors.evidence import (
    ExecutiveErrorEvidence,
    ExecutiveErrorEvidenceKind,
)

from gordon_system.src.agent.networks.executive.errors.severity import (
    ExecutiveErrorSeverity,
)

from gordon_system.src.agent.networks.executive.errors.persistence import (
    ExecutiveErrorPersistence,
)

from gordon_system.src.agent.networks.executive.errors.recurrence import (
    ExecutiveErrorRecurrence,
)

from gordon_system.src.agent.networks.executive.errors.recoverability import (
    ExecutiveErrorRecoverability,
)

from gordon_system.src.agent.networks.executive.errors.attribution import (
    ExecutiveErrorAttribution,
)

from gordon_system.src.agent.networks.executive.errors.propagation import (
    ExecutiveErrorPropagation,
)

# =============================================================================
# Error Model
# =============================================================================

from gordon_system.src.agent.networks.executive.errors.model import (
    ExecutiveError,
)

from gordon_system.src.agent.networks.executive.errors.expectation_violation import (
    ExecutiveExpectationViolationAssessment,
)

# =============================================================================
# Effectiveness Assessments
# =============================================================================

from gordon_system.src.agent.networks.executive.effectiveness.strategy import (
    ExecutiveStrategyPerformanceAssessment,
)

from gordon_system.src.agent.networks.executive.effectiveness.task_set import (
    ExecutiveTaskSetPerformanceAssessment,
)

from gordon_system.src.agent.networks.executive.effectiveness.control import (
    ExecutiveControlEffectivenessAssessment,
)

from gordon_system.src.agent.networks.executive.effectiveness.decision import (
    ExecutiveDecisionQualityAssessment,
)

from gordon_system.src.agent.networks.executive.effectiveness.action import (
    ExecutiveActionOutcomeAssessment,
)

from gordon_system.src.agent.networks.executive.effectiveness.recovery import (
    ExecutiveRecoveryEffectivenessAssessment,
)

from gordon_system.src.agent.networks.executive.effectiveness.goal import (
    ExecutiveGoalProgressAssessment,
)

from gordon_system.src.agent.networks.executive.effectiveness.commitment import (
    ExecutiveCommitmentProgressAssessment,
)

# =============================================================================
# Monitoring Contracts
# =============================================================================

from gordon_system.src.agent.networks.executive.monitoring.request import (
    ExecutivePerformanceMonitoringRequest,
)

from gordon_system.src.agent.networks.executive.monitoring.scope import (
    ExecutivePerformanceMonitoringScope,
)

from gordon_system.src.agent.networks.executive.monitoring.plan import (
    ExecutivePerformanceMonitoringPlan,
)

from gordon_system.src.agent.networks.executive.monitoring.steps import (
    ExecutivePerformanceMonitoringStepKind,
)

from gordon_system.src.agent.networks.executive.monitoring.product import (
    ExecutivePerformanceMonitoringProduct,
    ExecutivePerformanceMonitoringProductKind,
)

from gordon_system.src.agent.networks.executive.monitoring.outcome import (
    ExecutivePerformanceMonitoringOutcome,
)

from gordon_system.src.agent.networks.executive.monitoring.continuation import (
    ExecutivePerformanceMonitoringContinuation,
)

from gordon_system.src.agent.networks.executive.monitoring.state import (
    ExecutivePerformanceMonitoringState,
)

# =============================================================================
# Performance Summary and Anomaly Detection
# =============================================================================

from gordon_system.src.agent.networks.executive.performance.anomaly import (
    ExecutivePerformanceAnomaly,
    ExecutivePerformanceAnomalyKind,
)

from gordon_system.src.agent.networks.executive.performance.threshold import (
    ExecutivePerformanceThreshold,
    ExecutivePerformanceThresholdSet,
)

# =============================================================================
# Recommendations and Proposals
# =============================================================================

from gordon_system.src.agent.networks.executive.performance.recommendation import (
    ExecutivePerformanceRecommendation,
    ExecutivePerformanceRecommendationKind,
)

# =============================================================================
# Serialization and Validation (for complete module export)
# =============================================================================

__all__ = [
    # Subject types
    "ExecutivePerformanceSubject",
    "ExecutivePerformanceSubjectKind",
    
    # Criteria types
    "ExecutivePerformanceCriteria",
    "ExecutivePerformanceCriterion",
    
    # Evidence types
    "ExecutivePerformanceEvidence",
    "ExecutivePerformanceEvidenceKind",
    
    # Dimension types
    "ExecutivePerformanceDimension",
    "ExecutivePerformanceDimensionAssessment",
    
    # Status and trend
    "ExecutivePerformanceStatus",
    "ExecutivePerformanceTrend",
    
    # Quality metrics
    "ExecutivePerformanceConfidence",
    "ExecutivePerformanceCompleteness",
    "ExecutivePerformanceValidity",
    "ExecutivePerformanceProvenance",
    
    # Core assessment
    "ExecutivePerformanceAssessment",
    
    # Outcome types
    "ExecutiveExpectedOutcome",
    "ExecutiveActualOutcome",
    "ExecutiveOutcomeEvidence",
    "ExecutiveOutcomeCorrespondence",
    "ExecutiveOutcomeDivergence",
    "ExecutiveOutcomeQuality",
    "ExecutiveOutcomeCompleteness",
    "ExecutiveOutcomeCertainty",
    "ExecutiveOutcomeSideEffect",
    "ExecutiveOutcomeReversibility",
    "ExecutiveOutcomeAcceptance",
    "ExecutiveOutcomeAssessment",
    
    # Progress types
    "ExecutiveProgressBaseline",
    "ExecutiveProgressAssessment",
    "ExecutiveProgressSufficiency",
    "ExecutiveStagnationAssessment",
    "ExecutiveRegressionAssessment",
    "ExecutiveCompletionAssessment",
    
    # Error identity
    "ExecutiveErrorId",
    "ExecutiveErrorRevision",
    "ExecutiveErrorSchemaVersion",
    
    # Error kinds and status
    "ExecutiveErrorKind",
    "ExecutiveErrorStatus",
    "ExecutiveErrorSubject",
    
    # Error evidence
    "ExecutiveErrorEvidence",
    "ExecutiveErrorEvidenceKind",
    
    # Error metrics
    "ExecutiveErrorSeverity",
    "ExecutiveErrorPersistence",
    "ExecutiveErrorRecurrence",
    "ExecutiveErrorRecoverability",
    "ExecutiveErrorAttribution",
    "ExecutiveErrorPropagation",
    
    # Core error type
    "ExecutiveError",
    
    # Expectation violation
    "ExecutiveExpectationViolationAssessment",
    
    # Effectiveness assessments
    "ExecutiveStrategyPerformanceAssessment",
    "ExecutiveTaskSetPerformanceAssessment",
    "ExecutiveControlEffectivenessAssessment",
    "ExecutiveDecisionQualityAssessment",
    "ExecutiveActionOutcomeAssessment",
    "ExecutiveRecoveryEffectivenessAssessment",
    "ExecutiveGoalProgressAssessment",
    "ExecutiveCommitmentProgressAssessment",
    
    # Monitoring contracts
    "ExecutivePerformanceMonitoringRequest",
    "ExecutivePerformanceMonitoringScope",
    "ExecutivePerformanceMonitoringPlan",
    "ExecutivePerformanceMonitoringStepKind",
    "ExecutivePerformanceMonitoringProduct",
    "ExecutivePerformanceMonitoringProductKind",
    "ExecutivePerformanceMonitoringOutcome",
    "ExecutivePerformanceMonitoringContinuation",
    "ExecutivePerformanceMonitoringState",
    
    # Anomaly and threshold
    "ExecutivePerformanceAnomaly",
    "ExecutivePerformanceAnomalyKind",
    "ExecutivePerformanceThreshold",
    "ExecutivePerformanceThresholdSet",
    
    # Recommendations
    "ExecutivePerformanceRecommendation",
    "ExecutivePerformanceRecommendationKind",
]