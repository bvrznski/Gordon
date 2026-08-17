# Abduction Module - Phase 7.3
# ============================

"""
Abductive Reasoning subsystem for Gordon Cognitive Architecture.

This module provides:
    - Evidence management and analysis
    - Explanation generation and comparison
    - Diagnostic reasoning
    - Causal inference
    - Information gain estimation
    - Validation and governance

The abductive reasoning engine generates plausible explanations for available evidence,
ranks competing explanations, and identifies the best explanation based on coverage,
consistency, simplicity, and causal plausibility.
"""

from agent.components.systems.cognition.reasoning.abductive.shared.descriptor import (
    AbductionDescriptor,
    AbductionSessionIdentity,
    AbductionMode,
    AbductionLifecycle,
)

from agent.components.systems.cognition.reasoning.abductive.evidence.artifact import (
    AbductionEvidence,
    EvidenceSource,
    EvidenceKind,
    EvidenceArtifact,
    EvidenceQuality,
)

from agent.components.systems.cognition.reasoning.abductive.evidence.set import (
    EvidenceSetIdentity,
    MissingEvidence,
    EvidenceSet,
)

from agent.components.systems.cognition.reasoning.abductive.explanations.candidate import (
    ExplanationCandidate,
    ExplanationGeneration,
    ExplanationStrategy,
    ComparisonMetric,
    HypothesisComparison,
    ExplanationRanking,
)

from agent.components.systems.cognition.reasoning.abductive.explanations.comparison import (
    RankingStrategy,
    InformationGainEstimate,
    EvidenceAcquisitionPlan,
    CausalExplanationGraph,
)

from agent.components.systems.cognition.reasoning.abductive.diagnostics.engine import (
    DiagnosticReasoning,
    DiagnosticSessionIdentity,
    DiagnosticMode,
    DiagnosticLifecycle,
    CandidateCause,
    FailureMode,
    FailureModeAnalysis,
)

from agent.components.systems.cognition.reasoning.abductive.validation.result import (
    ValidationResult,
    ValidationFindingKind,
    ValidationFinding,
    ValidationTrace,
    ValidationResultRecord,
    AbductionValidationError,
)

from agent.components.systems.cognition.reasoning.abductive.governance.evaluation import (
    GovernanceRule,
    GovernanceFindingKind,
    GovernanceFinding,
    AbductionGovernance,
    GovernanceHealth,
)

__all__ = [
    # Shared
    "AbductionDescriptor",
    "AbductionSessionIdentity",
    "AbductionMode",
    "AbductionLifecycle",
    
    # Evidence
    "AbductionEvidence",
    "EvidenceSource",
    "EvidenceKind",
    "EvidenceArtifact",
    "EvidenceQuality",
    "EvidenceSetIdentity",
    "MissingEvidence",
    "EvidenceSet",
    
    # Explanations
    "ExplanationCandidate",
    "ExplanationGeneration",
    "ExplanationStrategy",
    "ComparisonMetric",
    "HypothesisComparison",
    "ExplanationRanking",
    "RankingStrategy",
    "InformationGainEstimate",
    "EvidenceAcquisitionPlan",
    "CausalExplanationGraph",
    
    # Diagnostics
    "DiagnosticReasoning",
    "DiagnosticSessionIdentity",
    "DiagnosticMode",
    "DiagnosticLifecycle",
    "CandidateCause",
    "FailureMode",
    "FailureModeAnalysis",
    
    # Validation
    "ValidationResult",
    "ValidationFindingKind",
    "ValidationFinding",
    "ValidationTrace",
    "ValidationResultRecord",
    "AbductionValidationError",
    
    # Governance
    "GovernanceRule",
    "GovernanceFindingKind",
    "GovernanceFinding",
    "AbductionGovernance",
    "GovernanceHealth",
]