# World-Model Reasoning Entities - Phase 7.44
# =================================

"""
Canonical Entity Analysis and Management.

Entities represent persistent objects, agents, and entities in the world.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class EntityType(Enum):
    """Categories of entities."""
    
    OBJECT = "object"               # Physical objects
    AGENT = "agent"                 # Autonomous agents (including Gordon)
    ENTITY_GROUP = "entity_group"   # Collection of related entities
    ABSTRACT = "abstract"           # Abstract concepts with spatial/temporal extension


class EntityLifecycle(Enum):
    """Entity lifecycle states."""
    
    EMERGING = "emerging"        # First observed, identity being established
    PERSISTENT = "persistent"    # Stable entity with history
    TRANSFORMING = "transforming"  # Undergoing state change
    DISSOLVING = "dissolving"    # ceasing to exist or changing form


@dataclass(frozen=True)
class EntityIdentity:
    """
    Persistent identity for an entity.
    
    An EntityIdentity contains:
        - Stable semantic identity across world revisions
        - History of identities (for tracking transformations)
        - Confidence in identity stability
        - Provenance tracking
    """
    
    entity_id: str                      # Primary identifier
    semantic_identity: str              # Stable semantic name/label
    origin_session_id: str              # Session where first observed
    confirmed_at_utc: float             # When identity was confirmed
    
    # Identity evolution history (transformations)
    identity_history: List[Tuple[str, float]] = field(default_factory=list)  # (old_id, timestamp)
    
    # Confidence in identity
    confidence: float = 1.0             # 0.0 to 1.0
    
    @classmethod
    def create(
        cls,
        entity_id: Optional[str] = None,
        semantic_identity: str = "unknown",
        origin_session_id: str = "",
    ) -> EntityIdentity:
        """Create a new entity identity."""
        return cls(
            entity_id=entity_id or f"entity:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            origin_session_id=origin_session_id,
            confirmed_at_utc=time.time(),
        )
    
    def with_history(self, old_entity_id: str) -> EntityIdentity:
        """Add previous identity to history (for transformations)."""
        new_history = self.identity_history + [(old_entity_id, time.time())]
        return dataclass_replace(
            self,
            identity_history=new_history,
            confidence=0.85,  # Confidence reduced after transformation
        )


@dataclass(frozen=True)
class EntityState:
    """
    State of an entity at a given world revision.
    
    An EntityState contains:
        - Explicit attributes (physical properties, relational state)
        - Location and orientation
        - Temporal validity window
        - Confidence estimates
    """
    
    entity_id: str                      # Reference to entity identity
    timestamp_utc: float                # When this state was captured
    
    # Physical attributes
    position_3d: Optional[Tuple[float, float, float]] = None  # x, y, z coordinates
    orientation_quat: Optional[Tuple[float, float, float, float]] = None  # qx, qy, qz, qw
    velocity_3d: Optional[Tuple[float, float, float]] = None
    bounding_volume: Optional[Dict[str, Any]] = None         # Size/shape information
    
    # Attributes dictionary for extensibility
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # State metadata
    confidence: float = 1.0             # Confidence in this state
    visibility: bool = True             # Is entity currently observable?
    
    @classmethod
    def create(
        cls,
        entity_id: str,
        timestamp_utc: Optional[float] = None,
    ) -> EntityState:
        """Create a new entity state."""
        return cls(
            entity_id=entity_id,
            timestamp_utc=timestamp_utc or time.time(),
            confidence=1.0,
            visibility=True,
        )
    
    def with_attributes(self, **kwargs) -> EntityState:
        """Return updated state with additional attributes."""
        new_attrs = dict(self.attributes)
        new_attrs.update(kwargs)
        return dataclass_replace(self, attributes=new_attrs)


@dataclass(frozen=True)
class EntityRelationship:
    """
    Relationship between entities.
    
    Relationships represent explicit connections between entities in the world.
    """
    
    relationship_id: str                # Unique identifier
    source_entity_id: str               # Source entity
    target_entity_id: str               # Target entity
    
    # Relationship type
    relation_kind: str                  # e.g., "contains", "supports", "near"
    relation_directional: bool = True   # Is the relationship directional?
    
    # Relationship properties
    strength: float = 1.0               # Strength of connection (0.0 to 1.0)
    confidence: float = 1.0             # Confidence in this relationship
    
    @classmethod
    def create(
        cls,
        source_entity_id: str,
        target_entity_id: str,
        relation_kind: str,
        relation_directional: bool = True,
        strength: float = 1.0,
        confidence: float = 1.0,
    ) -> EntityRelationship:
        """Create a new entity relationship."""
        return cls(
            relationship_id=f"rel:{uuid.uuid4().hex[:16]}",
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relation_kind=relation_kind,
            relation_directional=relation_directional,
            strength=strength,
            confidence=confidence,
        )


@dataclass(frozen=True)
class EntityAnalysis:
    """
    Analysis result for entity management.
    
    An EntityAnalysis contains:
        - Entity identity
        - Current state and attributes
        - Known relationships
        - Lifecycle state
        - Confidence estimates
        - Provenance tracking
    """
    
    # Identity
    analysis_id: str                    # Unique analysis identifier
    entity_identity: EntityIdentity     # The analyzed entity
    
    # State and attributes
    entity_state: EntityState           # Current known state
    attributes: Dict[str, Any]          # Extracted attributes
    
    # Relationships (known connections)
    relationships: List[EntityRelationship]
    
    # Lifecycle
    lifecycle_state: EntityLifecycle = EntityLifecycle.PERSISTENT
    
    # Confidence
    confidence: float = 1.0             # Overall confidence in analysis
    
    # Provenance
    observation_sources: List[str]      # Where did we observe this?
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        entity_identity: EntityIdentity,
        entity_state: EntityState,
        observation_sources: Optional[List[str]] = None,
    ) -> EntityAnalysis:
        """Create a new entity analysis."""
        return cls(
            analysis_id=f"analysis:{uuid.uuid4().hex[:16]}",
            entity_identity=entity_identity,
            entity_state=entity_state,
            attributes=dict(entity_state.attributes),
            relationships=[],
            lifecycle_state=EntityLifecycle.PERSISTENT,
            confidence=1.0,
            observation_sources=observation_sources or [],
        )
    
    def with_relationship(self, relationship: EntityRelationship) -> EntityAnalysis:
        """Add a relationship to this entity analysis."""
        new_relationships = self.relationships + [relationship]
        return dataclass_replace(
            self,
            relationships=new_relationships,
            confidence=self.confidence * 0.95,  # Slight confidence reduction with each addition
        )
    
    def update_state(self, new_state: EntityState) -> EntityAnalysis:
        """Update entity state and return new analysis."""
        return dataclass_replace(
            self,
            entity_state=new_state,
            attributes=dict(new_state.attributes),
        )


@dataclass(frozen=True)
class EntityManagement:
    """
    Entity management contract.
    
    An entity management result contains:
        - Entity identity
        - Entity model (current state, attributes)
        - Lifecycle state
        - Confidence estimates
        - Provenance tracking
    """
    
    # Identity
    management_id: str                  # Unique management identifier
    entity_identity: EntityIdentity     # Managed entity
    
    # Model
    entity_model: Dict[str, Any]        # Complete entity model
    
    # Lifecycle
    lifecycle_state: EntityLifecycle = EntityLifecycle.PERSISTENT
    
    # Confidence
    confidence: float = 1.0             # Overall confidence in management result
    
    # Provenance
    provenance: Optional[str] = None    # Source of this management
    world_revision: int = 1             # World revision number
    
    @classmethod
    def create(
        cls,
        entity_identity: EntityIdentity,
        provenance: Optional[str] = None,
        world_revision: int = 1,
    ) -> EntityManagement:
        """Create a new entity management."""
        return cls(
            management_id=f"management:{uuid.uuid4().hex[:16]}",
            entity_identity=entity_identity,
            entity_model={},
            lifecycle_state=EntityLifecycle.PERSISTENT,
            confidence=1.0,
            provenance=provenance,
            world_revision=world_revision,
        )
    
    def with_model(self, model: Dict[str, Any]) -> EntityManagement:
        """Update management result with full entity model."""
        return dataclass_replace(
            self,
            entity_model=model,
        )


# Helper function for dataclass replacement
def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "EntityType",
    "EntityLifecycle",
    "EntityIdentity",
    "EntityState",
    "EntityRelationship",
    "EntityAnalysis",
    "EntityManagement",
]