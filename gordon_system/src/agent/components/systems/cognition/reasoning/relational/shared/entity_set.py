# Relational Entity Set - Phase 7.11
# ====================================

"""
Canonical Relational Entity Set.

Relational reasoning operates over explicit Entity Sets.
Entity Sets define participating entities, relation taxonomy, and constraints.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class EntityRole(Enum):
    """Roles that entities can play in relational reasoning."""
    
    SOURCE = "source"           # Source of a relation (outgoing)
    TARGET = "target"           # Target of a relation (incoming)
    BOTH = "both"               # Both source and target
    CONTEXT = "context"         # Context or reference entity
    STRUCTURAL = "structural"   # Structural anchor point


class RelationType(Enum):
    """Types of relations between entities."""
    
    DEPENDS_ON = "depends_on"           # Dependency relationship
    CONNECTED_TO = "connected_to"       # Connection without dependency
    SUPPORTS = "supports"               # One entity supports another
    BLOCKS = "blocks"                   # One entity blocks another
    OWNS = "owns"                       # Ownership relationship
    CONTAINS = "contains"               # Containment relationship
    CONTROLS = "controls"               # Control/authority relationship
    REFERENCES = "references"           # Reference relationship
    COMMUNICATES_WITH = "communicates_with"  # Communication channel
    INTERACTS_WITH = "interacts_with"   # Interaction relationship
    SUBCLASS_OF = "subclass_of"         # Inheritance relationship
    INSTANCE_OF = "instance_of"         # Instance relationship
    SIMILAR_TO = "similar_to"           # Similarity relationship
    OPPOSITE_OF = "opposite_of"         # Opposite relationship


@dataclass(frozen=True)
class RelationalEntity:
    """
    Explicit entity participating in relational reasoning.
    
    Entities remain explicit and never possess implicit relations.
    """
    
    # Identity
    entity_id: str                      # Unique entity identifier
    
    # Semantic reference - where does this entity come from?
    semantic_reference: Optional[str] = None  # Reference to knowledge/semantic system
    
    # Entity role in reasoning
    entity_role: EntityRole = EntityRole.CONTEXT
    
    # Participating relations (explicit)
    participating_relations: Tuple[str, ...] = ()  # Relation IDs this entity participates in
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If derived from reasoning
    origin_context: str = "unknown"              # Where did entity originate?
    
    @property
    def is_active(self) -> bool:
        """Check if entity has active participation."""
        return len(self.participating_relations) > 0
    
    @property
    def relation_count(self) -> int:
        """Return number of participating relations."""
        return len(self.participating_relations)


@dataclass(frozen=True)
class RelationalEntitySet:
    """
    Immutable set of relational entities and constraints.
    
    Entity Sets remain immutable during reasoning.
    """
    
    # Identity
    entity_set_id: str                      # Unique identifier
    
    # Participating entities
    participating_entities: Tuple[RelationalEntity, ...] = ()   # All entities in set
    
    # Relation taxonomy - allowed relation types
    relation_taxonomy: Tuple[RelationType, ...] = (  # What relations are permitted?
        RelationType.DEPENDS_ON,
        RelationType.CONNECTED_TO,
        RelationType.SUPPORTS,
        RelationType.BLOCKS,
        RelationType.OWNS,
        RelationType.CONTAINS,
        RelationType.CONTROLS,
        RelationType.REFERENCES,
        RelationType.COMMUNICATES_WITH,
        RelationType.INTERACTS_WITH,
    )
    
    # Graph scope - what kind of graph?
    graph_scope: str = "general"            # e.g., "dependencies", "composition", "semantic"
    
    # Constraints on reasoning
    constraints: Tuple[str, ...] = ()       # Reasoning constraints
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If derived from another set
    origin_context: str = "unknown"
    
    @property
    def entity_count(self) -> int:
        """Return number of participating entities."""
        return len(self.participating_entities)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        entities: List[RelationalEntity],
        relation_taxonomy: Optional[List[RelationType]] = None,
        graph_scope: str = "general",
        constraints: Optional[List[str]] = None,
    ) -> RelationalEntitySet:
        """Create a new relational entity set."""
        return cls(
            entity_set_id=f"relational_entity_set:{uuid.uuid4().hex[:16]}",
            participating_entities=tuple(entities),
            relation_taxonomy=tuple(relation_taxonomy or []),
            graph_scope=graph_scope,
            constraints=tuple(constraints or []) if constraints else (),
            created_at_utc=time.time(),
        )
    
    def get_entity_by_id(self, entity_id: str) -> Optional[RelationalEntity]:
        """Find entity by its identifier."""
        for entity in self.participating_entities:
            if entity.entity_id == entity_id:
                return entity
        return None
    
    def filter_by_role(self, role: EntityRole) -> Tuple[RelationalEntity, ...]:
        """Return entities with a specific role."""
        return tuple(e for e in self.participating_entities if e.entity_role == role)
    
    def update_entity(
        self,
        updated_entity: RelationalEntity
    ) -> RelationalEntitySet:
        """Return new set with one entity replaced."""
        new_entities = []
        found = False
        for e in self.participating_entities:
            if e.entity_id == updated_entity.entity_id:
                new_entities.append(updated_entity)
                found = True
            else:
                new_entities.append(e)
        if not found:
            new_entities.append(updated_entity)
        
        return dataclass_replace(
            self,
            participating_entities=tuple(new_entities),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "RelationalEntity",
    "RelationalEntitySet",
    "EntityRole",
    "RelationType",
]