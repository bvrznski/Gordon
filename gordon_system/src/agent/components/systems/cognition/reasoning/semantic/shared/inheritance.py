# Semantic Inheritance - Phase 7.10
# ==================================

"""
Canonical Semantic Inheritance contracts.

Semantic inheritance evaluates:
    - Generalization
    - Specialization
    - Attribute inheritance
    - Constraint inheritance
    - Behavior inheritance

Inheritance remains explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class InheritanceDirection(Enum):
    """Inheritance direction."""
    
    UP = "up"       # From child to parent (generalization)
    DOWN = "down"   # From parent to child (specialization)
    BIDIRECTIONAL = "bidirectional"


@dataclass(frozen=True)
class SemanticInheritance:
    """
    Semantic inheritance result.
    
    A SemanticInheritance contains:
        - Inheritance identity
        - Parent concepts
        - Child concepts
        - Inherited properties
        - Provenance tracking
    """
    
    # Identity
    inheritance_id: str                     # Unique identifier
    
    # Reasoning goal
    reasoning_goal: str                     # What was inherited?
    
    # Parent concepts (sources of inheritance)
    parent_concepts: Tuple[str, ...] = ()
    
    # Child concepts (receivers of inheritance)
    child_concepts: Tuple[str, ...] = ()
    
    # Inherited properties
    inherited_properties: Dict[str, Any] = field(default_factory=dict)
    
    # Inheritance direction
    inheritance_direction: InheritanceDirection = InheritanceDirection.BIDIRECTIONAL
    
    # Diagnostics
    diagnostics: Tuple[DiagnosticsRecord, ...] = ()
    
    # State
    state: str = "created"
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def parent_count(self) -> int:
        """Count of parent concepts."""
        return len(self.parent_concepts)
    
    @property
    def child_count(self) -> int:
        """Count of child concepts."""
        return len(self.child_concepts)
    
    @classmethod
    def create(
        cls,
        reasoning_goal: str,
        parents: List[str],
        children: List[str],
        properties: Optional[Dict[str, Any]] = None,
    ) -> SemanticInheritance:
        """Create a new semantic inheritance record."""
        return cls(
            inheritance_id=f"inheritance:{uuid.uuid4().hex[:16]}",
            reasoning_goal=reasoning_goal,
            parent_concepts=tuple(parents),
            child_concepts=tuple(children),
            inherited_properties=properties or {},
        )
    
    def with_properties(self, properties: Dict[str, Any]) -> SemanticInheritance:
        """Return a copy with additional properties."""
        new_props = dict(self.inherited_properties)
        new_props.update(properties)
        return dataclass_replace(
            self,
            inherited_properties=new_props,
        )


@dataclass(frozen=True)
class InheritanceEdge:
    """
    Edge in an inheritance graph.
    
    Represents a parent-child relationship with inheritance metadata.
    """
    
    edge_id: str                            # Unique identifier
    source_concept: str                     # Parent concept
    target_concept: str                     # Child concept
    inherited_attributes: Tuple[str, ...] = ()  # Attributes inherited
    
    @classmethod
    def create(
        cls,
        parent: str,
        child: str,
        attributes: Optional[List[str]] = None,
    ) -> InheritanceEdge:
        """Create a new inheritance edge."""
        return cls(
            edge_id=f"edge:{uuid.uuid4().hex[:16]}",
            source_concept=parent,
            target_concept=child,
            inherited_attributes=tuple(attributes or []),
        )


@dataclass(frozen=True)
class ConceptHierarchy:
    """
    Concept hierarchy representation.
    
    A hierarchy organizes concepts by abstraction level with explicit
    parent-child relationships.
    """
    
    hierarchy_id: str                       # Unique identifier
    root_concept: str                       # Root of the hierarchy
    
    # Concepts in hierarchy (name -> level)
    concept_levels: Dict[str, int] = field(default_factory=dict)
    
    # Edges between concepts
    edges: Tuple[InheritanceEdge, ...] = ()
    
    # Diagnostics
    diagnostics: Tuple[DiagnosticsRecord, ...] = ()
    
    @property
    def concept_count(self) -> int:
        """Count of concepts in hierarchy."""
        return len(self.concept_levels)
    
    @classmethod
    def create(
        cls,
        root_concept: str,
    ) -> ConceptHierarchy:
        """Create a new concept hierarchy."""
        return cls(
            hierarchy_id=f"hierarchy:{uuid.uuid4().hex[:16]}",
            root_concept=root_concept,
            concept_levels={root_concept: 0},
        )
    
    def add_concept(self, concept: str, level: int) -> ConceptHierarchy:
        """Add a concept at the specified abstraction level."""
        new_levels = dict(self.concept_levels)
        new_levels[concept] = level
        return dataclass_replace(
            self,
            concept_levels=new_levels,
        )
    
    def add_edge(self, edge: InheritanceEdge) -> ConceptHierarchy:
        """Add an inheritance edge."""
        new_edges = tuple(self.edges) + (edge,)
        return dataclass_replace(
            self,
            edges=new_edges,
        )


@dataclass(frozen=True)
class DiagnosticsRecord:
    """
    Diagnostic record from inheritance analysis.
    """
    
    diagnostic_id: str                      # Unique identifier
    diagnostic_type: str                    # e.g., "conflict", "missing"
    message: str                            # Diagnostic message
    severity: str = "info"                  # info, warning, error
    
    @classmethod
    def info(cls, message: str) -> DiagnosticsRecord:
        """Create an info diagnostic."""
        return cls(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:16]}",
            diagnostic_type="info",
            message=message,
        )
    
    @classmethod
    def warning(cls, message: str) -> DiagnosticsRecord:
        """Create a warning diagnostic."""
        return cls(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:16]}",
            diagnostic_type="warning",
            message=message,
            severity="warning",
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SemanticInheritance",
    "InheritanceEdge",
    "ConceptHierarchy",
    "DiagnosticsRecord",
    "InheritanceDirection",
]