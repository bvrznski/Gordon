# Deductive Reasoning Subsystem - Phase 7.1
# ===========================================

"""
The Deductive Reasoning subsystem is Gordon's formal inference engine.

Deduction derives conclusions that necessarily follow from accepted premises
through explicit application of formal inference rules.

Architecture Position:
    Knowledge → Deductive Reasoning → Validation → Planning
    
Canonical Contracts:
    - shared/     : Contract definitions (descriptors, proofs, rules)
    - inference/  : Inference engines
    - proofs/     : Proof management
    - search/     : Proof search strategies
    - validation/ : Proof validation
    - governance/: Governance evaluation

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
    - Fabricating premises implicitly
    - Inferring conclusions without proof
    - Discarding intermediate proof steps
    - Bypassing validation or governance
    - Modifying Knowledge during deduction
"""

# Import all shared contracts for convenience
from gordon_system.src.agent.components.systems.cognition.reasoning.deductive.shared import (
    # Descriptor
    DeductionDescriptor,
    DeductionState,
    
    # Premise Set
    PremiseSet,
    DeductionPremise,
    PremiseKind,
    
    # Inference Rule
    InferenceRule,
    RuleKind,
    
    # Rule Application
    RuleApplication,
    
    # Deductive Proof
    DeductiveProof,
    ProofStep,
    ProofNode,
    
    # Proof Graph
    ProofGraph,
    ProofEdge,
    
    # Contradiction
    DeductionContradiction,
    ContradictionAnalysis,
    
    # Optimization
    ProofOptimization,
    
    # Lemma
    DeductiveLemma,
    
    # Failure
    DeductionFailure,
    
    # Validation
    DeductionValidation,
    
    # Governance
    DeductionGovernance,
    
    # Health
    DeductionHealth,
)

__all__ = [
    # Descriptor
    "DeductionDescriptor",
    "DeductionState",
    
    # Premise Set
    "PremiseSet",
    "DeductionPremise",
    "PremiseKind",
    
    # Inference Rule
    "InferenceRule",
    "RuleKind",
    
    # Rule Application
    "RuleApplication",
    
    # Deductive Proof
    "DeductiveProof",
    "ProofStep",
    "ProofNode",
    
    # Proof Graph
    "ProofGraph",
    "ProofEdge",
    
    # Contradiction
    "DeductionContradiction",
    "ContradictionAnalysis",
    
    # Optimization
    "ProofOptimization",
    
    # Lemma
    "DeductiveLemma",
    
    # Failure
    "DeductionFailure",
    
    # Validation
    "DeductionValidation",
    
    # Governance
    "DeductionGovernance",
    
    # Health
    "DeductionHealth",
]