# Semantic Reasoning Shared Contracts - Phase 7.10
# ================================================

"""
Shared contracts for the Semantic Reasoning subsystem.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.semantic.shared.descriptor import (
    SemanticDescriptor,
    SemanticMode,
    SemanticState,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.semantic.shared.concept_set import (
    ConceptReference,
    ConceptSet,
    SemanticConstraint,
    ConceptKind,
    ConceptSetState,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.semantic.shared.ontology import (
    OntologyReasoning,
    OntologyRelation,
    DiagnosticsRecord as OntologyDiagnosticsRecord,
    OntologyReasoningState,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.semantic.shared.inheritance import (
    SemanticInheritance,
    InheritanceEdge,
    ConceptHierarchy,
    InheritanceDirection,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.semantic.shared.composition import (
    ConceptComposition,
    SemanticEquivalenceAnalysis,
    CompositionRule,
    RelationEvidence,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.semantic.shared.consistency import (
    SemanticConsistency,
    ConsistencyViolation,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.semantic.shared.validation import (
    SemanticValidation,
    ValidationFinding,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.semantic.shared.failure import (
    SemanticFailure,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.semantic.shared.governance import (
    SemanticGovernance,
    GovernanceViolation,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.semantic.shared.health import (
    SemanticHealth,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.semantic.shared.diagnostics import (
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
    "OntologyDiagnosticsRecord",
    "OntologyReasoningState",
    
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