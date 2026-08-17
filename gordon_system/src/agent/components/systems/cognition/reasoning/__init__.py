# Reasoning Subsystem - Phase 7.1
# =================================

"""
The Reasoning subsystem is Gordon's cognitive transformation engine.

It transforms Knowledge into conclusions through active cognition processes.
Reasoning never modifies Knowledge directly; it proposes, and Knowledge stores.

Architecture Position:
    Knowledge → Reasoning → Planning → Decision Making → Execution

Canonical Components:
    - shared/      : Contract definitions
    - sessions/    : Active reasoning sessions
    - context/     : Working context management
    - inference/   : Inference engines
    - hypotheses/  : Hypothesis generation and evaluation
    - deliberation/: Alternative comparison
    - explanation/ : Explanatory reasoning
    - alternatives/: Alternative generation
    - governance/  : Governance evaluation
    - validation/  : Reasoning validation
    - deductive/   : Deductive reasoning contracts

Reasoning Laws:
    REASONING-LAW-001: Every session has one immutable semantic identity
    REASONING-LAW-002: Reasoning executes within explicit context
    REASONING-LAW-003: Semantic identities are preserved
    REASONING-LAW-004: Provenance is always preserved
    REASONING-LAW-005: Execution lineage is preserved
    REASONING-LAW-006: Reasoning remains independently inspectable
    REASONING-LAW-007: Reasoning remains deterministic
    REASONING-LAW-008: Completed sessions remain immutable

Deductive Reasoning Laws:
    DEDUCTION-LAW-001: Every deduction has one immutable semantic identity
    DEDUCTION-LAW-002: Deduction operates within explicit premise sets
    DEDUCTION-LAW-003: Every conclusion references explicit supporting premises
    DEDUCTION-LAW-004: Deduction preserves provenance
    DEDUCTION-LAW-005: Deduction preserves proof lineage
    DEDUCTION-LAW-006: Deduction remains independently inspectable
    DEDUCTION-LAW-007: Deduction remains deterministic
    DEDUCTION-LAW-008: Completed deductions remain immutable

Anti-Patterns to Avoid:
    - Modifying Knowledge during reasoning
    - Converting conclusions directly into beliefs
    - Hiding working assumptions
    - Discarding intermediate reasoning steps
    - Silently removing rejected alternatives
    - Fabricating supporting evidence
    - Bypassing validation or governance
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.shared import (
    ReasoningDescriptor,
    ReasoningKind,
    ReasoningState,
    
    Inference,
    InferenceTrace,
    InferenceStrategy,
    
    ReasoningHypothesis,
    HypothesisEvaluation,
    
    ReasoningAlternative,
    AlternativeComparison,
    AlternativeRanking,
    
    Deliberation,
    DeliberationPipeline,
    
    ReasoningConclusion,
    ConclusionTrace,
    ConclusionEvaluation,
    
    ReasoningPipeline,
    ReasoningSession,
    
    ReasoningValidation,
    ReasoningFailure,
    ReasoningGovernance,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.deductive import (
    # Deductive contracts
    DeductionDescriptor,
    DeductionState,
    
    PremiseSet,
    DeductionPremise,
    PremiseKind,
    
    InferenceRule,
    RuleKind,
    
    RuleApplication,
    
    DeductiveProof,
    ProofStep,
    ProofNode,
    
    ProofGraph,
    ProofEdge,
    
    DeductionContradiction,
    ContradictionAnalysis,
    
    ProofOptimization,
    
    DeductiveLemma,
    
    DeductionFailure,
    
    DeductionValidation,
    
     DeductionGovernance,
     
     DeductionHealth,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.temporal import (
    # Temporal contracts (Phase 7.8)
    TemporalDescriptor,
    TemporalMode,
    TemporalLifecycle,
    
    TemporalEvent,
    EventSet,
    EventKind,
    
    TemporalRelation,
    ChronologyGraph,
    ChronologyConstruction,
    TemporalRelationType,
    
    TemporalInterval,
    IntervalReasoning,
    
    TemporalConstraint,
    ConstraintPropagation,
    ConcurrencyAnalysis,
    ConstraintType,
    ConcurrencyType,
    
    TemporalDependencyGraph,
    DependencyNode,
    DependencyEdge,
    DependencyType,
    
    TemporalValidation,
    ValidationResult,
    ValidationType,
    
    TemporalFailure,
    FailureKind,
    
    TemporalGovernance,
    
    TemporalHealth,
    DiagnosticType,
)

__all__ = [
    # Shared contracts (exported directly)
    "ReasoningDescriptor",
    "ReasoningKind",
    "ReasoningState",
    "Inference",
    "InferenceTrace",
    "InferenceStrategy",
    "ReasoningHypothesis",
    "HypothesisEvaluation",
    "ReasoningAlternative",
    "AlternativeComparison",
    "AlternativeRanking",
    "Deliberation",
    "DeliberationPipeline",
    "ReasoningConclusion",
    "ConclusionTrace",
    "ConclusionEvaluation",
    "ReasoningPipeline",
    "ReasoningSession",
    "ReasoningValidation",
    "ReasoningFailure",
    "ReasoningGovernance",
    
    # Deductive contracts (Phase 7.1)
    "DeductionDescriptor",
    "DeductionState",
    
    "PremiseSet",
    "DeductionPremise",
    "PremiseKind",
    
    "InferenceRule",
    "RuleKind",
    
    "RuleApplication",
    
    "DeductiveProof",
    "ProofStep",
    "ProofNode",
    
    "ProofGraph",
    "ProofEdge",
    
    "DeductionContradiction",
    "ContradictionAnalysis",
    
    "ProofOptimization",
    
    "DeductiveLemma",
    
    "DeductionFailure",
    
    "DeductionValidation",
    
     "DeductionGovernance",
     
     "DeductionHealth",
     
     # Temporal contracts (Phase 7.8)
     "TemporalDescriptor",
     "TemporalMode",
     "TemporalLifecycle",
     
     "TemporalEvent",
     "EventSet",
     "EventKind",
     
     "TemporalRelation",
     "ChronologyGraph",
     "ChronologyConstruction",
     "TemporalRelationType",
     
     "TemporalInterval",
     "IntervalReasoning",
     
     "TemporalConstraint",
     "ConstraintPropagation",
     "ConcurrencyAnalysis",
     "ConstraintType",
     "ConcurrencyType",
     
     "TemporalDependencyGraph",
     "DependencyNode",
     "DependencyEdge",
     "DependencyType",
     
     "TemporalValidation",
     "ValidationResult",
     "ValidationType",
     
     "TemporalFailure",
     "FailureKind",
     
     "TemporalGovernance",
     
     "TemporalHealth",
     "DiagnosticType",
]
