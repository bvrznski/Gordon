# Knowledge Representation - Symbolic Structure - Phase 6.2
# =========================================================

"""
Symbolic Structure: The canonical reasoning representation in Gordon.

This module provides:
    * SymbolicStructure - Full symbolic structure with entities, relations, attributes
    * SymbolicProjection - Task-specific views that project from full structure
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# SYMBOLIC STRUCTURE - Full symbolic representation
# =============================================================================


@dataclass(frozen=True)
class SymbolicStructure:
    """
    Complete symbolic structure representing a semantic artifact.
    
    Provides all semantic information in an explicit, inspectable format
    suitable for reasoning operations.
    
    Fields:
        structure_identity:  Unique identifier for this structure
        semantic_identity:   Identity of the represented artifact
        entities:            Named objects with unique identity
        attributes:          Properties of entities
        relations:           Semantic connections between entities
        constraints:         Rules governing valid configurations
        ontology_revision:   Revision of ontology used for structure
        confidence:          Confidence in the structure (0.0 to 1.0)
        uncertainty:         Uncertainty about the structure
    """
    
    # Identity (required)
    structure_identity: str                # Unique structure ID
    
    semantic_identity: str                 # Artifact being represented
    
    # Core components (required)
    entities: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)     # Entities in the structure
    attributes: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)   # Entity attributes
    relations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)    # Relations between entities
    
    # Metadata (optional, with defaults)
    constraints: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Validity constraints
    ontology_revision: int = 1              # Ontology version used
    confidence: float = 1.0                 # Confidence in structure (0.0 to 1.0)
    uncertainty: float = 0.0                # Uncertainty about structure
    
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def entity_count(self) -> int:
        """Get number of entities."""
        return len(self.entities)
    
    @property
    def attribute_count(self) -> int:
        """Get number of attributes."""
        return len(self.attributes)
    
    @property
    def relation_count(self) -> int:
        """Get number of relations."""
        return len(self.relations)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert structure to dictionary for serialization."""
        return {
            "structure_identity": self.structure_identity,
            "semantic_identity": self.semantic_identity,
            "entities": [e for e in self.entities],
            "attributes": [a for a in self.attributes],
            "relations": [r for r in self.relations],
            "constraints": [c for c in self.constraints],
            "ontology_revision": self.ontology_revision,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "created_at_utc": self.created_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SymbolicStructure":
        """Create structure from dictionary."""
        return cls(
            structure_identity=data.get("structure_identity", str(uuid.uuid4())),
            semantic_identity=data.get("semantic_identity", ""),
            entities=tuple(data.get("entities", [])),
            attributes=tuple(data.get("attributes", [])),
            relations=tuple(data.get("relations", [])),
            constraints=tuple(data.get("constraints", [])),
            ontology_revision=int(data.get("ontology_revision", 1)),
            confidence=float(data.get("confidence", 1.0)),
            uncertainty=float(data.get("uncertainty", 0.0)),
        )
    
    @classmethod
    def create_initial(
        cls,
        semantic_identity: str,
        entities: Tuple[Dict[str, Any], ...] = tuple(),
        attributes: Tuple[Dict[str, Any], ...] = tuple(),
        relations: Tuple[Dict[str, Any], ...] = tuple(),
    ) -> "SymbolicStructure":
        """Create initial symbolic structure."""
        return cls(
            structure_identity=f"structure:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            entities=entities,
            attributes=attributes,
            relations=relations,
        )


# =============================================================================
# SYMBOLIC PROJECTION - Task-specific views
# =============================================================================


@dataclass(frozen=True)
class SymbolicProjection:
    """
    Projection of symbolic structure for a specific task or context.
    
    Creates a focused view by selecting components from the full structure
    while preserving semantic integrity.
    
    Fields:
        projection_identity: Unique identifier for this projection
        semantic_identity:   Identity of the represented artifact
        projected_components: IDs of components included in projection
        omitted_components:  IDs of components intentionally excluded
        projection_scope:    Purpose or context of this projection
        confidence:          Confidence in the projection (0.0 to 1.0)
        uncertainty:         Uncertainty about the projection
    """
    
    # Identity (required)
    projection_identity: str               # Unique projection ID
    
    semantic_identity: str                 # Artifact being represented
    
    # Projection content
    projected_components: Tuple[str, ...] = field(default_factory=tuple)  # Included components
    omitted_components: Tuple[str, ...] = field(default_factory=tuple)    # Excluded components
    
    # Metadata (optional, with defaults)
    projection_scope: str = "general"      # e.g., "reasoning", "retrieval"
    confidence: float = 1.0                # Confidence in projection
    uncertainty: float = 0.0               # Uncertainty about projection
    
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def component_count(self) -> int:
        """Get number of components in projection."""
        return len(self.projected_components)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert projection to dictionary for serialization."""
        return {
            "projection_identity": self.projection_identity,
            "semantic_identity": self.semantic_identity,
            "projected_components": [c for c in self.projected_components],
            "omitted_components": [c for c in self.omitted_components],
            "projection_scope": self.projection_scope,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "created_at_utc": self.created_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SymbolicProjection":
        """Create projection from dictionary."""
        return cls(
            projection_identity=data.get("projection_identity", str(uuid.uuid4())),
            semantic_identity=data.get("semantic_identity", ""),
            projected_components=tuple(data.get("projected_components", [])),
            omitted_components=tuple(data.get("omitted_components", [])),
            projection_scope=data.get("projection_scope", "general"),
            confidence=float(data.get("confidence", 1.0)),
            uncertainty=float(data.get("uncertainty", 0.0)),
        )
    
    @classmethod
    def create_for_task(
        cls,
        semantic_identity: str,
        task_type: str = "reasoning",
        component_ids: Optional[Tuple[str, ...]] = None,
    ) -> "SymbolicProjection":
        """Create projection for a specific task type."""
        return cls(
            projection_identity=f"projection:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            projected_components=component_ids or tuple(),
            projection_scope=task_type,
        )


__all__ = [
    # Full structure
    "SymbolicStructure",
    
    # Task-specific views
    "SymbolicProjection",
]