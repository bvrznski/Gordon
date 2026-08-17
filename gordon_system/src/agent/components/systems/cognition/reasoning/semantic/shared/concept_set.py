# Semantic Concept Set - Phase 7.10
# ==================================

"""
Canonical Concept Set for Semantic Reasoning.

A Concept Set defines the participating concepts, ontology scope,
semantic domains, abstraction boundaries, and semantic constraints
for a semantic reasoning session.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, AbstractSet
from enum import Enum, auto


class ConceptKind(Enum):
    """Categories of conceptual domains."""
    
    ENTITY = "entity"                    # Concrete or abstract entities
    RELATION = "relation"                # Semantic relations
    ATTRIBUTE = "attribute"              # Properties and attributes
    EVENT = "event"                      # Temporal events
    SCHEMA = "schema"                    # Structural schemas
    PRIMITIVE = "primitive"              # Basic conceptual primitives


class ConceptSetState(Enum):
    """Concept Set lifecycle states."""
    
    CREATED = "created"
    CONCEPTS_ADDED = "concepts_added"
    ONTOLOGY_ASSIGNED = "ontology_assigned"
    DOMAINS_DEFINED = "domains_defined"
    CONSTRAINTS_APPLIED = "constraints_applied"
    FINALIZED = "finalized"


@dataclass(frozen=True)
class ConceptReference:
    """
    Reference to a concept within the semantic reasoning framework.
    
    A ConceptReference provides:
        - Stable identity (independent of representation)
        - Domain membership
        - Abstraction level
        - Provenance tracking
    """
    
    concept_id: str                        # Unique concept identifier
    concept_name: str                      # Human-readable name
    abstraction_level: int = 0             # Higher = more abstract
    conceptual_domain: ConceptKind = ConceptKind.ENTITY
    
    @classmethod
    def create(
        cls,
        concept_name: str,
        abstraction_level: int = 0,
        conceptual_domain: ConceptKind = ConceptKind.ENTITY,
    ) -> ConceptReference:
        """Create a new concept reference."""
        return cls(
            concept_id=f"concept:{uuid.uuid4().hex[:16]}",
            concept_name=concept_name,
            abstraction_level=abstraction_level,
            conceptual_domain=conceptual_domain,
        )


@dataclass(frozen=True)
class ConceptSet:
    """
    Set of concepts for semantic reasoning.
    
    A Concept Set defines:
        - Participating concepts
        - Ontology scope
        - Semantic domains
        - Abstraction boundaries
        - Semantic constraints
    
    Concept Sets remain immutable during reasoning.
    """
    
    # Identity
    concept_set_id: str                    # Unique identifier
    semantic_identity: str                 # Semantic identity (stable across runs)
    
    # Participating concepts
    participating_concepts: Tuple[ConceptReference, ...] = ()
    
    # Ontology scope
    ontology_scope: Optional[str] = None   # Which ontologies apply?
    
    # Semantic domains
    semantic_domains: Tuple[str, ...] = ()  # e.g., "physics", "biology", "math"
    
    # Abstraction boundaries
    min_abstraction_level: int = 0
    max_abstraction_level: int = 10
    
    # State
    concept_set_state: ConceptSetState = ConceptSetState.CREATED
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def concept_count(self) -> int:
        """Count of participating concepts."""
        return len(self.participating_concepts)
    
    @property
    def domain_count(self) -> int:
        """Count of semantic domains."""
        return len(self.semantic_domains)
    
    @classmethod
    def create(
        cls,
        concept_names: List[str],
        ontology_scope: Optional[str] = None,
        semantic_domains: Optional[List[str]] = None,
        min_abstraction_level: int = 0,
        max_abstraction_level: int = 10,
        semantic_identity: str = "unknown",
    ) -> ConceptSet:
        """Create a new concept set."""
        concepts = tuple(
            ConceptReference.create(name, abstraction_level=i)
            for i, name in enumerate(concept_names)
        )
        
        return cls(
            concept_set_id=f"conceptset:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            participating_concepts=concepts,
            ontology_scope=ontology_scope,
            semantic_domains=tuple(semantic_domains or []),
            min_abstraction_level=min_abstraction_level,
            max_abstraction_level=max_abstraction_level,
        )
    
    def with_concepts(self, additional_concepts: List[ConceptReference]) -> ConceptSet:
        """Return a copy with additional concepts."""
        new_concepts = self.participating_concepts + tuple(additional_concepts)
        return dataclass_replace(
            self,
            participating_concepts=new_concepts,
            concept_set_state=ConceptSetState.CONCEPTS_ADDED,
        )
    
    def with_ontology(self, ontology_uri: str) -> ConceptSet:
        """Return a copy with ontology assigned."""
        return dataclass_replace(
            self,
            ontology_scope=ontology_uri,
            concept_set_state=ConceptSetState.ONTOLOGY_ASSIGNED,
        )
    
    def finalize(self) -> ConceptSet:
        """Mark the concept set as finalized."""
        return dataclass_replace(
            self,
            concept_set_state=ConceptSetState.FINALIZED,
        )


@dataclass(frozen=True)
class SemanticConstraint:
    """
    Constraint on semantic reasoning.
    
    Constraints include:
        - Domain restrictions
        - Abstraction bounds
        - Relation type restrictions
        - Ontology consistency requirements
    """
    
    constraint_id: str                     # Unique identifier
    constraint_type: str                   # e.g., "domain", "abstraction", "relation"
    constraint_value: Any                  # Constraint specification
    is_hard_constraint: bool = True        # Hard constraints must be satisfied
    
    @classmethod
    def domain(cls, domain_name: str) -> SemanticConstraint:
        """Create a domain restriction constraint."""
        return cls(
            constraint_id=f"constraint:{uuid.uuid4().hex[:16]}",
            constraint_type="domain",
            constraint_value=domain_name,
        )
    
    @classmethod
    def abstraction_bounds(
        cls, min_level: int, max_level: int
    ) -> SemanticConstraint:
        """Create an abstraction level constraint."""
        return cls(
            constraint_id=f"constraint:{uuid.uuid4().hex[:16]}",
            constraint_type="abstraction",
            constraint_value=(min_level, max_level),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ConceptReference",
    "ConceptSet",
    "SemanticConstraint",
    "ConceptKind",
    "ConceptSetState",
]