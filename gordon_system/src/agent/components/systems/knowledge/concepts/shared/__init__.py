# Knowledge Concepts - Shared Infrastructure - Phase 6.3
# =======================================================

"""
Shared Infrastructure for Gordon's Concept Subsystem.

This package provides the foundational abstractions, contracts, and utilities
that enable concept formation, categorization, abstraction, ontology membership,
and semantic hierarchy management.
"""

from __future__ import annotations

# Core contracts
from .contract import (
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
]