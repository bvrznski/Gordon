# Knowledge Concepts - Phase 6.3
# ==============================

"""
Knowledge Concepts - Gordon's Semantic Vocabulary Engine.

The Concept subsystem is the foundation of Gordon's semantic cognition.
Concepts are abstract semantic categories that organize meaning. They do not
represent observations, beliefs, or truth - they define what kinds of things
exist and how they relate.

Core Principles:
- Concepts are timeless and immutable semantic identities
- Instances are concrete realizations observed in the world
- Hierarchies organize concepts through generalization/specialization
- Ontologies categorize concepts within knowledge domains

Subsystems:
    shared       - Core contracts and abstractions
    instances    - Instance management and classification
    properties   - Semantic property system
    prototypes   - Prototype representations
    similarity   - Concept similarity computation
    discovery    - Novel concept detection
    refinement   - Concept refinement and evolution
    evolution    - Concept lifecycle tracking
    boundaries   - Semantic boundary definitions
    governance   - Semantic integrity evaluation

Example Usage:

    # Create a new concept
    from gordon_system.src.agent.components.systems.knowledge.concepts import (
        Concept, ConceptIdentity, PropertyKind
    )
    
    identity = ConceptIdentity.create("Animal")
    animal = Concept(
        identity=identity.identity,
        canonical_name="Animal",
        description="A living organism that feeds on organic matter",
        properties=("living", "mobile", "sensitive"),
        ontologies=("biology",),
        confidence=1.0
    )
    
    # Create an instance
    from gordon_system.src.agent.components.systems.knowledge.concepts import (
        ConceptInstance, PropertyKind
    )
    
    rover = ConceptInstance(
        identity="instance:rover-uuid",
        concept_ids=(animal.identity,),
        name="Rover",
        properties={
            "has_tail": True,
            "barks": True,
            "color": "brown"
        }
    )

Architecture:
    Perception -> Percepts -> Knowledge-Perception Grounding ->
    Concept Candidates -> Concept Validation -> Concept ->
    Beliefs -> Reasoning -> Planning -> Action
"""

from __future__ import annotations

# Core contracts and types (shared)
from .shared.contract import (
    # Identity
    ConceptIdentity,
    # Canonical concepts
    Concept,
    ConceptInstance,
    ClassificationKind,
    ConceptClassification,
    # Properties
    PropertyKind,
    ConceptProperty,
    # Prototypes
    ConceptPrototype,
    # Abstraction hierarchy operations
    ConceptAbstraction,
    ConceptSpecialization,
    ConceptGeneralization,
)

# Validation utilities
from .validation import (
    ValidationFinding,
    ValidationResult,
    validate_concept_identity,
    validate_canonical_name,
    validate_confidence,
    ConceptValidationEngine,
    validate_concept_fast,
    validate_instance_fast,
)

# Module initialization
from . import shared, instances

__all__ = [
    # Identity
    "ConceptIdentity",
    # Core concepts
    "Concept",
    "ConceptInstance",
    "ClassificationKind",
    "ConceptClassification",
    # Properties
    "PropertyKind",
    "ConceptProperty",
    # Prototypes
    "ConceptPrototype",
    # Abstraction hierarchy operations
    "ConceptAbstraction",
    "ConceptSpecialization",
    "ConceptGeneralization",
    # Validation
    "ValidationFinding",
    "ValidationResult",
    "validate_concept_identity",
    "validate_canonical_name",
    "validate_confidence",
    "ConceptValidationEngine",
    "validate_concept_fast",
    "validate_instance_fast",
    # Modules
    "shared",
    "instances",
]