# Knowledge Concept - Phase 5.4
# =============================

"""
Knowledge Concept: Semantic categories and their organization.

Concepts define semantic categories that Gordon uses to organize understanding.
Examples include Process, File, Window, Compiler, Directory, Human, Conversation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# CONCEPT HIERARCHY - Parent-child relationships
# =============================================================================


class ConceptRelationType(Enum):
    """
    Types of relationships between concepts in the hierarchy.
    
    IS_A: Generalization/specialization (inheritance)
    INSTANCE_OF: Instance membership relation
    PART_OF: Composition/part-whole relation
    ASSOCIATED_WITH: Semantic association without direct relationship
    """
    
    IS_A = "is_a"                   # Inheritance relationship
    INSTANCE_OF = "instance_of"     # Instance to class relationship
    PART_OF = "part_of"             # Composition relationship
    ASSOCIATED_WITH = "associated_with"  # Semantic association


# =============================================================================
# CONCEPT MODEL - Canonical concept structure
# =============================================================================


@dataclass(frozen=True)
class KnowledgeConcept:
    """
    Canonical representation of a semantic category in Gordon's knowledge system.
    
    Concepts organize meaning by defining categories and their relationships
    within the semantic graph. Every concept has a canonical identity and
    preserves its revision history.
    
    Fields:
        concept_identity:      Unique identifier for this concept
        canonical_name:        Primary name for this concept
        aliases:               Alternative names for this concept
        description:           Semantic definition of this category
        attributes:            Key properties defining this concept
        examples:              Typical instances of this concept
        parent_concepts:       Generalization relationships (IS_A)
        child_concepts:        Specialization relationships (IS_A)
        relations:             Other semantic relationships
        confidence:            Semantic confidence in this concept (0.0-1.0)
        uncertainty:           Semantic uncertainty about this concept
        revision:              Revision number for traceability
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity and metadata (required)
    concept_identity: str             # Unique ID for this concept
    
    # Naming (required)
    canonical_name: str               # Primary name
    aliases: Tuple[str, ...] = field(default_factory=tuple)  # Alternative names
    
    # Definition and attributes
    description: str = ""             # Semantic definition
    attributes: Tuple[str, ...] = field(default_factory=tuple)  # Defining properties
    
    # Examples and references
    examples: Tuple[str, ...] = field(default_factory=tuple)
    
    # Hierarchy relationships
    parent_concepts: Tuple[str, str] = field(default_factory=lambda: ())  # (relation_type, concept_id)
    child_concepts: Tuple[str, str] = field(default_factory=lambda: ())   # (relation_type, concept_id)
    
    # Other semantic relations
    relations: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)  # (relation_kind, target_id)
    
    # Quality metrics (required)
    confidence: float = 0.5           # Semantic confidence (0.0-1.0)
    uncertainty: float = 0.5          # Semantic uncertainty (0.0-1.0)
    
    # Lifecycle tracking
    revision: int = 1                 # Revision number for traceability
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    @property
    def is_valid(self) -> bool:
        """Check if concept has minimal required data."""
        return (
            len(self.concept_identity) > 0 and
            len(self.canonical_name) > 0
        )
    
    @property
    def root_concepts(self) -> Tuple[str, ...]:
        """Get all root concepts (no parent relationships)."""
        roots = []
        for rel_type, parent_id in self.parent_concepts:
            # If no further parents, this is a root
            if not any(p[1] == parent_id for p in self.parent_concepts):
                roots.append(parent_id)
        return tuple(roots)
    
    def get_parent(self, relation_kind: str) -> Optional[str]:
        """Get parent concept with specified relation kind."""
        for rel_type, parent_id in self.parent_concepts:
            if rel_type == relation_kind:
                return parent_id
        return None
    
    def get_children(self, relation_kind: str) -> Tuple[str, ...]:
        """Get child concepts with specified relation kind."""
        children = []
        for rel_type, child_id in self.child_concepts:
            if rel_type == relation_kind:
                children.append(child_id)
        return tuple(children)
    
    @classmethod
    def create(
        cls,
        canonical_name: str,
        aliases: Optional[List[str]] = None,
        description: str = "",
        attributes: Optional[List[str]] = None,
        examples: Optional[List[str]] = None,
        parent_concepts: Optional[List[Tuple[str, str]]] = None,
        child_concepts: Optional[List[Tuple[str, str]]] = None,
        relations: Optional[List[Tuple[str, str]]] = None,
        confidence: float = 0.5,
        uncertainty: float = 0.5,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> "KnowledgeConcept":
        """
        Create a new concept.
        
        Args:
            canonical_name: Primary name for this concept
            aliases: Alternative names (optional)
            description: Semantic definition (optional)
            attributes: Defining properties (optional)
            examples: Typical instances (optional)
            parent_concepts: (relation_type, concept_id) tuples (optional)
            child_concepts: (relation_type, concept_id) tuples (optional)
            relations: Other semantic relationships (optional)
            confidence: Semantic confidence (0.0-1.0)
            uncertainty: Semantic uncertainty (0.0-1.0)
            provenance: Origin tracking data (optional)
        """
        return cls(
            concept_identity=f"concept:{uuid.uuid4().hex[:16]}",
            canonical_name=canonical_name,
            aliases=tuple(aliases or []),
            description=description,
            attributes=tuple(attributes or []),
            examples=tuple(examples or []),
            parent_concepts=tuple(parent_concepts or []),
            child_concepts=tuple(child_concepts or []),
            relations=tuple(relations or []),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
            provenance={
                **(provenance or {}),
                "created_at_utc": time.time(),
                "revision": 1,
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert concept to dictionary for serialization."""
        return {
            "concept_identity": self.concept_identity,
            "canonical_name": self.canonical_name,
            "aliases": list(self.aliases),
            "description": self.description,
            "attributes": list(self.attributes),
            "examples": list(self.examples),
            "parent_concepts": [list(p) for p in self.parent_concepts],
            "child_concepts": [list(c) for c in self.child_concepts],
            "relations": [list(r) for r in self.relations],
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "revision": self.revision,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeConcept":
        """Create concept from dictionary."""
        return cls(
            concept_identity=data.get("concept_identity", str(uuid.uuid4())),
            canonical_name=data.get("canonical_name", ""),
            aliases=tuple(data.get("aliases", [])),
            description=data.get("description", ""),
            attributes=tuple(data.get("attributes", [])),
            examples=tuple(data.get("examples", [])),
            parent_concepts=tuple(tuple(p) for p in data.get("parent_concepts", [])),
            child_concepts=tuple(tuple(c) for c in data.get("child_concepts", [])),
            relations=tuple(tuple(r) for r in data.get("relations", [])),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            revision=int(data.get("revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )
    
    def add_alias(
        self,
        alias: str,
    ) -> "KnowledgeConcept":
        """Create a revision with an additional alias."""
        new_aliases = list(self.aliases)
        if alias not in new_aliases:
            new_aliases.append(alias)
        
        return KnowledgeConcept(
            concept_identity=self.concept_identity,
            canonical_name=self.canonical_name,
            aliases=tuple(new_aliases),
            description=self.description,
            attributes=self.attributes,
            examples=self.examples,
            parent_concepts=self.parent_concepts,
            child_concepts=self.child_concepts,
            relations=self.relations,
            confidence=self.confidence,
            uncertainty=self.uncertainty,
            revision=self.revision + 1,
            provenance={
                **self.provenance,
                "alias_added": alias,
                "revised_at_utc": time.time(),
            },
        )
    
    def add_child(
        self,
        child_id: str,
        relation_kind: str = ConceptRelationType.IS_A.value,
    ) -> "KnowledgeConcept":
        """Create a revision with an additional child concept."""
        new_children = list(self.child_concepts)
        if (relation_kind, child_id) not in new_children:
            new_children.append((relation_kind, child_id))
        
        return KnowledgeConcept(
            concept_identity=self.concept_identity,
            canonical_name=self.canonical_name,
            aliases=self.aliases,
            description=self.description,
            attributes=self.attributes,
            examples=self.examples,
            parent_concepts=self.parent_concepts,
            child_concepts=tuple(new_children),
            relations=self.relations,
            confidence=self.confidence,
            uncertainty=self.uncertainty,
            revision=self.revision + 1,
            provenance={
                **self.provenance,
                "child_added": child_id,
                "relation_kind": relation_kind,
                "revised_at_utc": time.time(),
            },
        )
    
    def add_parent(
        self,
        parent_id: str,
        relation_kind: str = ConceptRelationType.IS_A.value,
    ) -> "KnowledgeConcept":
        """Create a revision with an additional parent concept."""
        new_parents = list(self.parent_concepts)
        if (relation_kind, parent_id) not in new_parents:
            new_parents.append((relation_kind, parent_id))
        
        return KnowledgeConcept(
            concept_identity=self.concept_identity,
            canonical_name=self.canonical_name,
            aliases=self.aliases,
            description=self.description,
            attributes=self.attributes,
            examples=self.examples,
            parent_concepts=tuple(new_parents),
            child_concepts=self.child_concepts,
            relations=self.relations,
            confidence=self.confidence,
            uncertainty=self.uncertainty,
            revision=self.revision + 1,
            provenance={
                **self.provenance,
                "parent_added": parent_id,
                "relation_kind": relation_kind,
                "revised_at_utc": time.time(),
            },
        )


# =============================================================================
# CONCEPT HIERARCHY BUILDER
# =============================================================================


class ConceptHierarchyBuilder:
    """
    Builds and validates concept hierarchies.
    
    Ensures hierarchical relationships are consistent and free of cycles.
    """
    
    def __init__(
        self,
        allow_multiple_inheritance: bool = True,
        max_hierarchy_depth: int = 10,
    ):
        """
        Initialize the builder.
        
        Args:
            allow_multiple_inheritance: Allow concepts with multiple parents
            max_hierarchy_depth: Maximum depth of inheritance hierarchy
        """
        self._allow_multiple = allow_multiple_inheritance
        self._max_depth = max_hierarchy_depth
    
    def validate_hierarchy(
        self,
        concept_id: str,
        parent_ids: List[str],
        visited: Optional[set] = None,
        depth: int = 0,
    ) -> Tuple[bool, List[str]]:
        """
        Validate that adding these parents would not create a cycle.
        
        Args:
            concept_id: The concept being validated
            parent_ids: Proposed parent concept IDs
            visited: Already visited concepts in current path (internal)
            depth: Current depth in hierarchy
            
        Returns:
            (is_valid, list_of_issues)
        """
        if visited is None:
            visited = set()
        
        issues = []
        
        # Check depth limit
        if depth > self._max_depth:
            issues.append(f"Hierarchy exceeds maximum depth ({self._max_depth})")
        
        # Check for cycles
        if concept_id in visited:
            issues.append(f"Cyclic reference detected at '{concept_id}'")
            return False, issues
        
        visited.add(concept_id)
        
        # Validate each parent
        for parent_id in parent_ids:
            if parent_id == concept_id:
                issues.append(f"Concept cannot be its own parent: {parent_id}")
            
            # Recursively check parent's parents (simplified - would need full graph)
            # In practice, this would traverse the entire hierarchy
            
            if not self._allow_multiple and len(parent_ids) > 1:
                issues.append("Multiple inheritance not allowed")
        
        return len(issues) == 0, issues
    
    def build_simple_is_a_hierarchy(
        self,
        concept_name: str,
        parent_names: List[str],
    ) -> KnowledgeConcept:
        """
        Build a simple IS_A hierarchy.
        
        Args:
            concept_name: Name of the concept being created
            parent_names: Names of parent concepts
            
        Returns:
            Concept with IS_A relationships to parents
        """
        # In practice, would look up actual IDs from a registry
        return KnowledgeConcept.create(
            canonical_name=concept_name,
            parent_concepts=[
                (ConceptRelationType.IS_A.value, f"concept:{parent.lower().replace(' ', '_')}")
                for parent in parent_names
            ],
        )


__all__ = [
    "ConceptRelationType",
    "KnowledgeConcept",
    "ConceptHierarchyBuilder",
]