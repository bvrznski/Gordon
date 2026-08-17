# Deductive Reasoning Shared Contracts - Phase 7.1
# =====================================================

"""
Shared contract types for the deductive reasoning subsystem.

This module provides canonical implementations of all deductive reasoning contracts:

    DeductionDescriptor   - Metadata about deduction operations
    PremiseSet            - Set of accepted premises
    InferenceRule         - Formal inference rule
    RuleApplication       - Application of a rule to premises
    DeductiveProof        - Constructed proof from deductions
    ProofGraph            - Graph representation of proofs
    Contradiction         - Detected contradiction with analysis
    ProofOptimization     - Optimized version of a proof
    DeductionFailure      - Failure record for deduction sessions
    DeductionGovernance   - Governance evaluation
    DeductionHealth       - Health metrics
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.deductive.shared.descriptor import (
    DeductionDescriptor,
    DeductionState,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.deductive.shared.premise_set import (
    PremiseSet,
    DeductionPremise,
    PremiseKind,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.deductive.shared.inference_rule import (
    InferenceRule,
    RuleKind,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.deductive.shared.rule_application import (
    RuleApplication,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.deductive.shared.deductive_proof import (
    DeductiveProof,
    ProofStep,
    ProofNode,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.deductive.shared.proof_graph import (
    ProofGraph,
    ProofEdge,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.deductive.shared.contradiction import (
    DeductionContradiction,
    ContradictionAnalysis,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.deductive.shared.optimization import (
    ProofOptimization,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.deductive.shared.lemma import (
    DeductiveLemma,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.deductive.shared.failure import (
    DeductionFailure,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.deductive.shared.validation import (
    DeductionValidation,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.deductive.shared.governance import (
    DeductionGovernance,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.deductive.shared.health import (
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