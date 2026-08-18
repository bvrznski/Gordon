# Evaluation Reasoning Subsystem - Phase 7.23
# ============================================

"""
Evaluation Reasoning provides Gordon's cognitive appraisal engine.

This module implements:
- Evaluation descriptor and lifecycle management
- Evaluation sets (targets, expectations, criteria)
- Evaluation pipeline execution
- Performance assessment (metrics, results)
- Quality estimation (accuracy, reliability, confidence)
- Objective verification (expected vs observed, acceptance thresholds)
- Cognitive appraisal (overall success, unexpected outcomes, significance)
- Failure handling (diagnostics, recovery options)
- Governance evaluation (metric validity, consistency, robustness)
- Health monitoring (evaluations completed, coverage, accuracy)

Architecture Position:
    Monitoring → Evaluation Reasoning → Learning → Adaptation

Canonical Contracts:
    - shared/     : Contract definitions (descriptors, metrics, assessments)
    - objectives/ : Objective-specific evaluations
    - performance/: Performance assessment
    - quality/    : Quality estimation
    - metrics/    : Metrics aggregation
    - appraisal/  : Cognitive appraisal
    - validation/ : Validation results
    - governance/ : Governance findings
    - diagnostics/: Diagnostic information

Evaluation Reasoning Laws:
    EVALUATION-LAW-001: Every evaluation has one immutable semantic identity
    EVALUATION-LAW-002: Evaluation operates within explicit evaluation sets
    EVALUATION-LAW-003: Every evaluation references explicit supporting observations
    EVALUATION-LAW-004: Evaluation preserves provenance
    EVALUATION-LAW-005: Evaluation preserves reasoning lineage
    EVALUATION-LAW-006: Evaluation remains independently inspectable
    EVALUATION-LAW-007: Evaluation remains deterministic given identical inputs
    EVALUATION-LAW-008: Completed evaluations remain immutable

Anti-Patterns to Avoid:
    - Evaluate without monitored evidence
    - Verify objectives implicitly
    - Confuse observation with evaluation
    - Hide failed objectives
    - Overwrite historical evaluations
    - Mix evaluation with learning
    - Bypass validation or governance
    - Lose provenance
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.evaluation.shared import (
    # Descriptor and Lifecycle
    EvaluationDescriptor,
    EvaluationMode,
    EvaluationLifecycle,
    
    # Evaluation Set
    EvaluationTarget,
    EvaluationTargetKind,
    EvaluationSet,
    
    # Pipeline
    EvaluationStage,
    PipelineStageResult,
    EvaluationPipeline,
    
    # Performance Assessment
    PerformanceMetricKind,
    PerformanceMetric,
    PerformanceAssessment,
    
    # Quality Estimation
    QualityMetricKind,
    QualityMetric,
    QualityAssessment,
    
    # Objective Verification
    VerificationResultKind,
    VerificationEvidence,
    ObjectiveVerification,
    
    # Cognitive Appraisal
    AppraisalResultKind,
    AppraisalFinding,
    CognitiveAppraisal,
    
    # Failure Handling
    FailureKind,
    EvaluationFailure,
    
    # Governance
    GovernanceFindingKind,
    GovernanceFinding,
    EvaluationGovernance,
    
    # Health Metrics
    HealthMetrics,
    EvaluationHealth,
)

__all__ = [
    # Descriptor and Lifecycle
    "EvaluationDescriptor",
    "EvaluationMode",
    "EvaluationLifecycle",
    
    # Evaluation Set
    "EvaluationTarget",
    "EvaluationTargetKind",
    "EvaluationSet",
    
    # Pipeline
    "EvaluationStage",
    "PipelineStageResult",
    "EvaluationPipeline",
    
    # Performance Assessment
    "PerformanceMetricKind",
    "PerformanceMetric",
    "PerformanceAssessment",
    
    # Quality Estimation
    "QualityMetricKind",
    "QualityMetric",
    "QualityAssessment",
    
    # Objective Verification
    "VerificationResultKind",
    "VerificationEvidence",
    "ObjectiveVerification",
    
    # Cognitive Appraisal
    "AppraisalResultKind",
    "AppraisalFinding",
    "CognitiveAppraisal",
    
    # Failure Handling
    "FailureKind",
    "EvaluationFailure",
    
    # Governance
    "GovernanceFindingKind",
    "GovernanceFinding",
    "EvaluationGovernance",
    
    # Health Metrics
    "HealthMetrics",
    "EvaluationHealth",
]