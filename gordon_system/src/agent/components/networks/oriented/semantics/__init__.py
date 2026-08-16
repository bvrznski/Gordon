# Oriented Network Semantic Foundation
# ======================================

"""
Semantic Ontology for the Oriented Network (Phase 4.7.2)

Canonical Definition:
    The OrientedNetwork is Gordon's cognitive coordination network responsible
    for maintaining persistent intentional orientation toward active Goals,
    objectives, tasks, constraints, missions, and externally directed cognition.

Semantic Role:
    - Establishes the authoritative semantic model for intentional orientation
    - Defines canonical terminology and conceptual hierarchy
    - Maintains ownership boundaries and semantic relationships
    - Provides foundation for all subsequent implementation phases

Architectural Authority:
    - Semantics possess higher authority than implementation
    - Implementation must conform to the semantic ontology
    - Semantic definitions are stable across implementation evolution

Package Structure (Phase 4.7.2):
    semantics/
        __init__.py               This module - package initialization
        ontology.py              Canonical ontology with all concepts
        vocabulary.py            Terminology definitions and relationships
        hierarchy.py             Conceptual hierarchy (Purpose → Mission → Goal)
        ownership.py             Ownership model for each concept
        relationships.py         Semantic relationship graph
        context_semantics.py     Context orientation semantics
        goal_semantics.py        Goal/objective/task semantics
        progress_semantics.py    Progress, completion, failure semantics
        interruption_semantics.py Interruption and restoration semantics
        laws.py                  Semantic laws (ORIENTED-SEMANTIC-LAW-xxx)
        invariants.py            Semantic invariants (INV-xxx)

Public API:
    - All semantic concepts are exported for use by implementation phases
    - No runtime behavior is provided (deferred to future phases)
    - No mutable state is introduced

See Also:
    Phase 4.7.1: Scaffold, legacy retirement, architectural foundation
    Phase 4.7.3: State model with orientation content and context
"""

from __future__ import annotations

# =============================================================================
# SEMANTIC FOUNDATION IMPORTS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.semantics.ontology import (
    # Orientation concepts
    Orientation,
    Intent,
    Goal,
    Objective,
    Task,
    Mission,
    Purpose,
    Constraint,
    Dependency,
    Requirement,
    Expectation,
    Commitment,
    Continuation,
    Interruption,
    Suspension,
    Restoration,
    Context,
    Scope,
    Horizon,
    Priority,
    Progress,
    Completion,
    Alignment,
    Confidence,
    Risk,
    Recovery,
    Failure,
    
    # Ownership types
    OwnershipModel,
    OwnerType,
    SemanticLifecycle,
    CanonicalOntology,
    CANONICAL_ONTOLOGY,
)

from gordon_system.src.agent.components.networks.oriented.semantics.vocabulary import (
    Vocabulary,
    ConceptDefinition,
    SemanticRelationship,
    SemanticRelationshipType,
    CANONICAL_VOCABULARY,
)

from gordon_system.src.agent.components.networks.oriented.semantics.hierarchy import (
    HierarchyLevel,
    HierarchyEdge,
    ConceptualHierarchy,
    CANONICAL_HIERARCHY,
)

from gordon_system.src.agent.components.networks.oriented.semantics.laws import (
    ORIENTED_SEMANTIC_LAWS,
    SemanticLaw,
)

from gordon_system.src.agent.components.networks.oriented.semantics.invariants import (
    SEMANTIC_INVARIANTS,
    SemanticInvariant,
)

__all__ = [
    # Ontology - all canonical concepts
    "Orientation",
    "Intent",
    "Goal",
    "Objective",
    "Task",
    "Mission",
    "Purpose",
    "Constraint",
    "Dependency",
    "Requirement",
    "Expectation",
    "Commitment",
    "Continuation",
    "Interruption",
    "Suspension",
    "Restoration",
    "Context",
    "Scope",
    "Horizon",
    "Priority",
    "Progress",
    "Completion",
    "Alignment",
    "Confidence",
    "Risk",
    "Recovery",
    "Failure",
    
    # Ownership
    "OwnershipModel",
    "OwnerType",
    "SemanticLifecycle",
    "CanonicalOntology",
    "CANONICAL_ONTOLOGY",
    
    # Vocabulary
    "Vocabulary",
    "ConceptDefinition",
    "SemanticRelationship",
    "SemanticRelationshipType",
    "CANONICAL_VOCABULARY",
    
    # Hierarchy
    "HierarchyLevel",
    "HierarchyEdge",
    "ConceptualHierarchy",
    "CANONICAL_HIERARCHY",
    
    # Laws and Invariants
    "ORIENTED_SEMANTIC_LAWS",
    "SemanticLaw",
    "SEMANTIC_INVARIANTS",
    "SemanticInvariant",
]
