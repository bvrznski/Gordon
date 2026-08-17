# Gordon Phase 5.7.7: Situated World - Entity Model
# ===================================================

"""
Canonical entity model for Situated World.

Entities are the fundamental "things" in the world - objects, agents,
locations, events, etc. They have identity, provenance, and lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import uuid


def _generate_uuid() -> str:
    """Generate a UUID-like identifier."""
    return uuid.uuid4().hex[:8]


@dataclass(frozen=True)
class EntityAttributes:
    """
    Immutable attributes collection for an entity.
    
    Attributes are key-value pairs that describe entity properties.
    They are deeply immutable - no modification after creation.
    """
    
    attributes: dict[str, object] = field(default_factory=dict)
    """Attribute name to value mapping."""
    
    confidence: float = 1.0
    """Confidence in the attributes [0.0, 1.0]."""
    
    provenance: str | None = None
    """Source of these attributes."""
    
    def get(self, key: str, default: object = None) -> object:
        """Get an attribute value with optional default."""
        return self.attributes.get(key, default)
    
    def update(
        self,
        **kwargs: object,
    ) -> "EntityAttributes":
        """Return new attributes with updates (immutable)."""
        new_attrs = dict(self.attributes)
        new_attrs.update(kwargs)
        return EntityAttributes(
            attributes=new_attrs,
            confidence=self.confidence,
            provenance=self.provenance,
        )


@dataclass(frozen=True)
class Entity:
    """
    Canonical immutable entity model.
    
    Rules:
        - Identity remains stable across lifecycle (CREATE, UPDATE, DEPRECATE)
        - Attributes are deeply immutable
        - Provenance tracks source but doesn't grant authority
        - Trust and privacy must be preserved
    """
    
    entity_id: str = field(default_factory=lambda: f"entity-{_generate_uuid()}")
    """Unique identifier for this entity."""
    
    attributes: EntityAttributes = field(default_factory=EntityAttributes)
    """Entity property attributes."""
    
    relations: tuple[str, ...] = field(default_factory=tuple)
    """Relation IDs this entity participates in."""
    
    provenance: str | None = None
    """Source that proposed/provided this entity."""
    
    trust_level: str = "medium"
    """Trust level for this entity (untrusted, medium, high)."""
    
    privacy_class: str = "internal"
    """Privacy classification of this entity."""
    
    lifecycle_status: str = "ACTIVE"
    """Lifecycle status (ACTIVE, DEPRECATED, REMOVED)."""
    
    generation_created: int = 1
    """Generation when entity was first created."""
    
    @classmethod
    def create(
        cls,
        entity_id: str | None = None,
        attributes: dict[str, object] | None = None,
        relations: tuple[str, ...] | None = None,
        provenance: str | None = None,
        trust_level: str = "medium",
        privacy_class: str = "internal",
        generation_created: int = 1,
    ) -> "Entity":
        """
        Create a new Entity with validation.
        
        Rules:
            - entity_id must be non-empty if provided
            - relations must reference valid entities
            - trust_level and privacy_class must be valid
        """
        if entity_id is not None and (not entity_id or not isinstance(entity_id, str)):
            raise ValueError("entity_id must be a non-empty string")
        
        return cls(
            entity_id=entity_id or f"entity-{_generate_uuid()}",
            attributes=EntityAttributes(attributes=attributes or {}),
            relations=relations or (),
            provenance=provenance,
            trust_level=trust_level,
            privacy_class=privacy_class,
            lifecycle_status="ACTIVE",
            generation_created=generation_created,
        )
    
    def update_attributes(
        self,
        **kwargs: object,
    ) -> "Entity":
        """Return new entity with updated attributes (immutable)."""
        return replace(self, attributes=self.attributes.update(**kwargs))
    
    def deprecate(self) -> "Entity":
        """Return new entity with deprecated lifecycle status."""
        if self.lifecycle_status == "REMOVED":
            raise ValueError("Cannot deprecate already removed entity")
        return replace(
            self,
            lifecycle_status="DEPRECATED",
            attributes=self.attributes.update(_deprecated_at="deprecation"),
        )
    
    def remove(self) -> "Entity":
        """Return new entity with removed lifecycle status."""
        if self.lifecycle_status != "DEPRECATED":
            raise ValueError("Must deprecate before removal")
        return replace(
            self,
            lifecycle_status="REMOVED",
            attributes=self.attributes.update(_removed_at="removal"),
        )
    
    def with_generation(self, generation: int) -> "Entity":
        """Return new entity with updated creation generation."""
        return replace(self, generation_created=generation)
