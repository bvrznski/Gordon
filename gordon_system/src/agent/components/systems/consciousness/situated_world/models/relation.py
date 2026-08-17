# Gordon Phase 5.7.7: Situated World - Relation Model
# =====================================================

"""
Canonical relation model for Situated World.

Relations represent semantic connections between entities. They are:
* Typed (has a specific kind of relationship)
* Directional (source -> target)  
* Immutable (once published, never modified)
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import uuid

from gordon_system.src.agent.capabilities.consciousness.situated_world.types import EntityReference


def _generate_uuid() -> str:
    """Generate a UUID-like identifier."""
    return uuid.uuid4().hex[:8]


@dataclass(frozen=True)
class RelationKind:
    """
    Immutable relation type classification.
    
    Relations have typed kinds that define their semantic meaning.
    Examples: 'part_of', 'causes', 'affects', 'located_in', etc.
    """
    
    kind_id: str
    """Unique identifier for this relation kind."""
    
    description: str = ""
    """Human-readable description of the relation type."""
    
    directionality: str = "directed"
    """Directionality (directed, undirected)."""
    
    @classmethod
    def directed(cls, kind_id: str, description: str = "") -> "RelationKind":
        """Create a directed relation kind."""
        return cls(kind_id=kind_id, description=description, directionality="directed")
    
    @classmethod
    def undirected(cls, kind_id: str, description: str = "") -> "RelationKind":
        """Create an undirected relation kind."""
        return cls(kind_id=kind_id, description=description, directionality="undirected")


@dataclass(frozen=True)
class Relation:
    """
    Canonical immutable relation model.
    
    Rules:
        - Source and target must be different entities
        - Kind must be from known relation types  
        - Endpoints reference valid entities
        - Immutable after publication
    """
    
    relation_id: str = field(default_factory=lambda: f"rel-{_generate_uuid()}")
    """Unique identifier for this relation."""
    
    source_entity_ref: EntityReference
    """Source entity reference."""
    
    target_entity_ref: EntityReference  
    """Target entity reference."""
    
    kind: RelationKind = field(default_factory=lambda: RelationKind(kind_id="related_to"))
    """Relation type."""
    
    attributes: dict[str, object] = field(default_factory=dict)
    """Additional relation-specific attributes."""
    
    provenance: str | None = None
    """Source that proposed this relation."""
    
    trust_level: str = "medium"
    """Trust level for this relation (untrusted, medium, high)."""
    
    @classmethod
    def create(
        cls,
        source_entity_ref: EntityReference,
        target_entity_ref: EntityReference,
        kind_id: str = "related_to",
        description: str = "",
        attributes: dict[str, object] | None = None,
        provenance: str | None = None,
        trust_level: str = "medium",
    ) -> "Relation":
        """
        Create a new Relation with validation.
        
        Rules:
            - Source and target must be different entities
            - Kind is specified by kind_id
            - Attributes are additional relation properties
        """
        if source_entity_ref.entity_id == target_entity_ref.entity_id:
            raise ValueError("Source and target cannot be the same entity")
        
        return cls(
            relation_id=f"rel-{_generate_uuid()}",
            source_entity_ref=source_entity_ref,
            target_entity_ref=target_entity_ref,
            kind=RelationKind(kind_id=kind_id, description=description),
            attributes=attributes or {},
            provenance=provenance,
            trust_level=trust_level,
        )
    
    def reverse(self) -> "Relation":
        """Return new relation with source and target swapped (if undirected)."""
        if self.kind.directionality == "undirected":
            return replace(
                self,
                source_entity_ref=self.target_entity_ref,
                target_entity_ref=self.source_entity_ref,
            )
        # Directed relations cannot be reversed
        raise ValueError("Cannot reverse directed relation")
    
    def update_attributes(self, **kwargs: object) -> "Relation":
        """Return new relation with updated attributes (immutable)."""
        new_attrs = dict(self.attributes)
        new_attrs.update(kwargs)
        return replace(self, attributes=new_attrs)
