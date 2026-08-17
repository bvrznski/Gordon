# Semantic Reasoning Subsystem - Phase 7.10
# ==========================================

"""
The Semantic Reasoning subsystem is Gordon's meaning reasoning engine.

Semantic Reasoning operates over conceptual structures rather than linguistic
expressions, providing canonical semantic integration across the cognitive
architecture.

Architecture Position:
    Knowledge → Semantic Reasoning → Validation → Planning
    
Canonical Contracts:
    - shared/     : Contract definitions (descriptors, concepts, relations)
    - concepts/   : Concept management
    - ontologies/: Ontology reasoning
    - relations/  : Relation inference
    - hierarchies/: Inheritance reasoning
    - governance/: Governance evaluation
    - validation/: Validation checks
    - diagnostics/: Diagnostics and tracing

Semantic Reasoning Laws:
    SEMANTIC-LAW-001: Every semantic session has one immutable semantic identity
    SEMANTIC-LAW-002: Semantic Reasoning operates over explicit Concept Sets
    SEMANTIC-LAW-003: Every inferred relation references explicit concepts
    SEMANTIC-LAW-004: Semantic Reasoning preserves provenance
    SEMANTIC-LAW-005: Semantic Reasoning preserves reasoning lineage
    SEMANTIC-LAW-006: Semantic Reasoning remains independently inspectable
    SEMANTIC-LAW-007: Semantic Reasoning remains deterministic
    SEMANTIC-LAW-008: Completed semantic sessions remain immutable

Anti-Patterns to Avoid:
    - Inferring meaning from names alone
    - Conflating concepts with language tokens
    - Introducing implicit ontology changes
    - Silently merging unrelated concepts
    - Confusing equivalence with identity
    - Hiding inheritance conflicts
    - Bypassing validation or governance
"""

# Import all shared contracts for convenience
from gordon_system.src.agent.components.systems.cognition.reasoning.semantic.shared import (
    # Descriptor
    SemanticDescriptor,
    SemanticMode,
    SemanticState,
    
    # Concept Set
    ConceptReference,
    ConceptSet,
    SemanticConstraint,
    ConceptKind,
    ConceptSetState,
    
    # Ontology Reasoning
    OntologyReasoning,
    OntologyRelation,
    
    # Inheritance
    SemanticInheritance,
    InheritanceEdge,
    ConceptHierarchy,
    InheritanceDirection,
    
    # Composition
    ConceptComposition,
    SemanticEquivalenceAnalysis,
    CompositionRule,
    RelationEvidence,
    
    # Consistency
    SemanticConsistency,
    ConsistencyViolation,
    
    # Validation
    SemanticValidation,
    ValidationFinding,
    
    # Failure
    SemanticFailure,
    
    # Governance
    SemanticGovernance,
    GovernanceViolation,
    
    # Health
    SemanticHealth,
    
    # Diagnostics and Trace
    DiagnosticsRecord,
    SemanticTrace,
)

__all__ = [
    # Descriptor
    "SemanticDescriptor",
    "SemanticMode",
    "SemanticState",
    
    # Concept Set
    "ConceptReference",
    "ConceptSet",
    "SemanticConstraint",
    "ConceptKind",
    "ConceptSetState",
    
    # Ontology Reasoning
    "OntologyReasoning",
    "OntologyRelation",
    
    # Inheritance
    "SemanticInheritance",
    "InheritanceEdge",
    "ConceptHierarchy",
    "InheritanceDirection",
    
    # Composition
    "ConceptComposition",
    "SemanticEquivalenceAnalysis",
    "CompositionRule",
    "RelationEvidence",
    
    # Consistency
    "SemanticConsistency",
    "ConsistencyViolation",
    
    # Validation
    "SemanticValidation",
    "ValidationFinding",
    
    # Failure
    "SemanticFailure",
    
    # Governance
    "SemanticGovernance",
    "GovernanceViolation",
    
    # Health
    "SemanticHealth",
    
    # Diagnostics and Trace
    "DiagnosticsRecord",
    "SemanticTrace",
]