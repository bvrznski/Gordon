# Relational Reasoning Subsystem - Phase 7.11
# ============================================

"""
The Relational Reasoning subsystem is Gordon's structural cognition engine.

While Semantic Reasoning determines what concepts mean, Relational Reasoning
determines how those concepts organize into coherent systems.

Architecture Position:
    Knowledge → Semantic Models → Relational Reasoning → Relation Graphs → 
    Structural Inference → Reasoning Output

Canonical Contracts:
    - shared/     : Contract definitions (descriptors, entities, relations)
    - entities/   : Entity management
    - relations/  : Relation modeling  
    - graphs/     : Graph reasoning and analysis
    - composition/: Compositional reasoning
    - constraints/: Constraint propagation
    - validation/: Validation checks
    - governance/: Governance evaluation
    - diagnostics/: Diagnostics and tracing

Relational Reasoning Laws:
    RELATIONAL-LAW-001: Every Relational Session has one immutable semantic identity
    RELATIONAL-LAW-002: Relational Reasoning operates over explicit Entity Sets
    RELATIONAL-LAW-003: Every inferred relationship references explicit entities
    RELATIONAL-LAW-004: Relational Reasoning preserves provenance
    RELATIONAL-LAW-005: Relational Reasoning preserves reasoning lineage
    RELATIONAL-LAW-006: Relational Reasoning remains independently inspectable
    RELATIONAL-LAW-007: Relational Reasoning remains deterministic
    RELATIONAL-LAW-008: Completed sessions remain immutable

Anti-Patterns to Avoid:
    - Inferring relationships without explicit entities
    - Modifying Knowledge directly through reasoning
    - Hiding graph topology changes
    - Confusing storage with reasoning
    - Bypassing validation or governance
"""

# Import all shared contracts for convenience
from gordon_system.src.agent.components.systems.cognition.reasoning.relational.shared import (
    # Descriptor
    RelationalDescriptor,
    RelationalMode,
    RelationalState,
    
    # Entity Set
    RelationalEntity,
    RelationalEntitySet,
    EntityRole,
    RelationType,
    
    # Graph Construction
    GraphConstruction,
    GraphConstructionStrategy,
    
    # Structural Inference and Composition
    StructuralInferenceAnalysis,
    StructuralComposition,
    InferencePattern,
    
    # Constraint Propagation
    RelationConstraintPropagation,
    
    # Graph Analysis
    GraphAnalysis,
    
    # Refinement
    RelationalRefinement,
    
    # Validation
    RelationalValidation,
    ValidationKind,
    
    # Failure
    RelationalFailure,
    FailureKind,
    
    # Governance
    RelationalGovernance,
    
    # Health
    RelationalHealth,
    
    # Diagnostics and Trace
    RelationalTrace,
    DiagnosticsRecord,
)

__all__ = [
    # Descriptor
    "RelationalDescriptor",
    "RelationalMode",
    "RelationalState",
    
    # Entity Set
    "RelationalEntity",
    "RelationalEntitySet",
    "EntityRole",
    "RelationType",
    
    # Graph Construction
    "GraphConstruction",
    "GraphConstructionStrategy",
    
    # Structural Inference and Composition
    "StructuralInferenceAnalysis",
    "StructuralComposition",
    "InferencePattern",
    
    # Constraint Propagation
    "RelationConstraintPropagation",
    
    # Graph Analysis
    "GraphAnalysis",
    
    # Refinement
    "RelationalRefinement",
    
    # Validation
    "RelationalValidation",
    "ValidationKind",
    
    # Failure
    "RelationalFailure",
    "FailureKind",
    
    # Governance
    "RelationalGovernance",
    
    # Health
    "RelationalHealth",
    
    # Diagnostics and Trace
    "RelationalTrace",
    "DiagnosticsRecord",
]