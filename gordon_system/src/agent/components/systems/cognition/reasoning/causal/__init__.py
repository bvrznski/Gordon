# Causal Reasoning Subsystem - Phase 7.5
# =========================================

"""
The Causal Reasoning subsystem is Gordon's mechanism reasoning engine.

It models how changes propagate through systems via explicit causal mechanisms.
Causal reasoning answers:
    "Why did this happen?" (cause identification)
    "What happens if this changes?" (intervention analysis)

Architecture Position:
    Knowledge → Beliefs → World Model → Causal Reasoning → Mechanism Models
    ↓
    Intervention Analysis → Reasoning Output

Canonical Components:
    - shared/       : Contract definitions (descriptor, mechanism_set, graph_construction)
    - mechanisms/   : Causal mechanism models
    - graphs/       : Causal graph construction and manipulation
    - interventions/: Intervention analysis
    - propagation/  : Effect propagation through mechanisms
    - dependencies/ : Dependency analysis
    - validation/   : Validation of causal structures
    - governance/   : Governance evaluation
    - observability/: Observability and diagnostics

Causal Reasoning Laws:
    CAUSAL-LAW-001: Every session has one immutable semantic identity
    CAUSAL-LAW-002: Causal reasoning executes over explicit Mechanism Sets
    CAUSAL-LAW-003: Every causal relationship references explicit supporting mechanisms
    CAUSAL-LAW-004: Provenance is always preserved
    CAUSAL-LAW-005: Reasoning lineage is preserved
    CAUSAL-LAW-006: Causal reasoning remains independently inspectable
    CAUSAL-LAW-007: Causal reasoning remains deterministic
    CAUSAL-LAW-008: Completed sessions remain immutable

Anti-Patterns to Avoid:
    - Confusing correlation with causation
    - Fabricating causal mechanisms without evidence
    - Introducing hidden intervention semantics
    - Propagating effects without mechanisms
    - Executing interventions during reasoning (only analyzing)
    - Silently repairing causal graphs
    - Bypassing validation or governance
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared import (
    # Shared contracts
    CausalDescriptor,
    CausalMode,
    CausalLifecycle,
    
    MechanismSet,
    CausalMechanism,
    MechanismKind,
    
    GraphConstruction,
    
    Intervention,
    InterventionAnalysis,
    
    EffectPropagation,
    
    DependencyAnalysis,
    
    StructuralCausalModel,
    
    CausalRefinement,
    
    CounterfactualPreparation,
    
    CausalValidation,
    
    CausalFailure,
    FailureKind,
    
    CausalGovernance,
    
    CausalHealth,
    CausalDiagnostics,
)

__all__ = [
    # Shared contracts
    "CausalDescriptor",
    "CausalMode",
    "CausalLifecycle",
    
    "MechanismSet",
    "CausalMechanism",
    "MechanismKind",
    
    "GraphConstruction",
    
    "Intervention",
    "InterventionAnalysis",
    
    "EffectPropagation",
    
    "DependencyAnalysis",
    
    "StructuralCausalModel",
    
    "CausalRefinement",
    
    "CounterfactualPreparation",
    
    "CausalValidation",
    
    "CausalFailure",
    "FailureKind",
    
    "CausalGovernance",
    
    "CausalHealth",
    "CausalDiagnostics",
]