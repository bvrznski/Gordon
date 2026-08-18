# Evaluation Reasoning Shared Contracts - Phase 7.23
# ===================================================

"""
Shared contract types for the evaluation reasoning subsystem.

This module provides canonical implementations of all evaluation contracts:

    EvaluationDescriptor      - Metadata about evaluation sessions
    EvaluationSet             - Set of evaluation targets and parameters
    EvaluationPipeline        - Pipeline execution workflow
    PerformanceAssessment     - Performance metrics and assessment
    QualityAssessment         - Quality metrics and estimation
    ObjectiveVerification     - Objective verification results
    CognitiveAppraisal        - Overall success appraisal
    EvaluationFailure         - Failure records with diagnostics
    EvaluationGovernance      - Governance evaluation findings
    EvaluationHealth          - Health metrics for the subsystem
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.evaluation.shared.descriptor import (
    EvaluationDescriptor,
    EvaluationMode,
    EvaluationLifecycle,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.evaluation.shared.evaluation_set import (
    EvaluationTarget,
    EvaluationTargetKind,
    EvaluationSet,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.evaluation.shared.pipeline import (
    EvaluationStage,
    PipelineStageResult,
    EvaluationPipeline,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.evaluation.shared.performance import (
    PerformanceMetricKind,
    PerformanceMetric,
    PerformanceAssessment,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.evaluation.shared.quality import (
    QualityMetricKind,
    QualityMetric,
    QualityAssessment,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.evaluation.shared.verification import (
    VerificationResultKind,
    VerificationEvidence,
    ObjectiveVerification,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.evaluation.shared.appraisal import (
    AppraisalResultKind,
    AppraisalFinding,
    CognitiveAppraisal,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.evaluation.shared.failure import (
    FailureKind,
    EvaluationFailure,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.evaluation.shared.governance import (
    GovernanceFindingKind,
    GovernanceFinding,
    EvaluationGovernance,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.evaluation.shared.health import (
    HealthMetrics,
    EvaluationHealth,
)

__all__ = [
    # Descriptor
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
    
    # Performance
    "PerformanceMetricKind",
    "PerformanceMetric",
    "PerformanceAssessment",
    
    # Quality
    "QualityMetricKind",
    "QualityMetric",
    "QualityAssessment",
    
    # Verification
    "VerificationResultKind",
    "VerificationEvidence",
    "ObjectiveVerification",
    
    # Appraisal
    "AppraisalResultKind",
    "AppraisalFinding",
    "CognitiveAppraisal",
    
    # Failure
    "FailureKind",
    "EvaluationFailure",
    
    # Governance
    "GovernanceFindingKind",
    "GovernanceFinding",
    "EvaluationGovernance",
    
    # Health
    "HealthMetrics",
    "EvaluationHealth",
]