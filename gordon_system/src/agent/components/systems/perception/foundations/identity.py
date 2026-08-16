# Perception Identity - Phase 5.2 Canonical Semantic Identifier
# =============================================================

"""
Perception Identity: Stable, immutable identifiers for perceptual entities.

Every PerceptualEntity possesses:
    - stable identity (survives revisions)
    - semantic identity (what makes this 'this')
    - entity kind (category classification)
    - revision tracking
    - provenance (origin history)

Identity Laws:
    IDENTITY-LAW-001: Every Perceptual Entity has one stable semantic identity
    IDENTITY-LAW-002: Identity remains immutable
    IDENTITY-LAW-003: Identity survives revisions
    IDENTITY-LAW-004: Identity is globally unique within the Perception System
    IDENTITY-LAW-005: Identity provenance is complete
    IDENTITY-LAW-006: Identity history is inspectable
    IDENTITY-LAW-007: Identity is never reassigned
    IDENTITY-LAW-008: Identity resolution is deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# PERCEPTION IDENTITY KINDS
# =============================================================================


class PerceptionIdentityKind(Enum):
    """
    Kinds of identity that can be assigned to perceptual entities.
    
    These define the semantic scope of identity:
        - OBSERVATION: Identity is for an observation (raw evidence)
        - SIGNAL: Identity is for a signal (sensor output)
        - FEATURE: Identity is for a feature (structured property)
        - PERCEPT: Identity is for a percept (semantic representation)
        - SCENE: Identity is for a scene (organized collection)
        - EVENT: Identity is for an event (transition between states)
    """
    
    OBSERVATION = "observation"     # Raw evidence from sensor
    SIGNAL = "signal"               # Measured sensor output
    FEATURE = "feature"             # Structured property computed from signal
    PERCEPT = "percept"             # Modality-independent representation
    SCENE = "scene"                 # Coherent collection of percepts
    EVENT = "event"                 # Meaningful transition between states


# =============================================================================
# PERCEPTION IDENTITY - Immutable Semantic Identifier
# =============================================================================


@dataclass(frozen=True)
class PerceptionIdentity:
    """
    Immutable identifier for a perceptual entity.
    
    Identity is the stable core that persists across revisions. When an entity
    is revised, it keeps the same identity but gets a new revision number.
    
    Fields:
        entity_id:               Globally unique entity ID (UUID or equivalent)
        semantic_identity:       What makes this semantically 'this'?
                                  Can be content hash for factual entities,
                                  logical equivalence for concepts
        
        # Revision tracking
        creation_revision:       First revision in this entity's chain
        current_revision:        Current revision number (0 if not tracked)
        
        # Provenance
        provenance:              Where did this identity come from? (Any type to avoid circular deps)
        
        # Timestamps
        created_at_utc:          When identity was first assigned
    """
    
    # Core identifiers (required, no defaults)
    entity_id: str                      # Globally unique identifier
    semantic_identity: str              # Semantic equivalence key
    
    # Classification - must be after required fields
    entity_kind_str: str               # What kind of thing is this?
    
    # Revision tracking - must be after required fields with defaults
    creation_revision: str             # First revision in chain
    current_revision: int = 1          # Current revision number
    
    # All optional fields below
    provenance: Any = field(default_factory=lambda: {"origin": "system"})
    
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def revision_identity(self) -> str:
        """Get the current revision's identity URI."""
        return f"{self.entity_id}:r{self.current_revision}"
    
    @property
    def identity_uri(self) -> str:
        """Get a URI-like identifier for this identity."""
        return f"perception://{self.entity_kind_str}/{self.entity_id}"
    
    @property
    def revision_uri(self) -> str:
        """Get the current revision's URI."""
        return f"{self.identity_uri}/r{self.current_revision}"
    
    @classmethod
    def create_for_entity(
        cls,
        semantic_identity: str,
        entity_kind_str: str = "unknown",
    ) -> "PerceptionIdentity":
        """
        Create a new identity for an entity.
        
        Args:
            semantic_identity: What makes this semantically 'this'?
            entity_kind_str: String representation of the kind (optional)
            
        Returns:
            New PerceptionIdentity with generated entity_id
        """
        return cls(
            entity_id=str(uuid.uuid4()),
            semantic_identity=semantic_identity,
            entity_kind_str=entity_kind_str,
            creation_revision=str(uuid.uuid4()),  # Initial revision ID
            current_revision=1,
            provenance={"origin": "system"},
            created_at_utc=time.time(),
        )
    
    @classmethod
    def from_uri(cls, uri: str) -> Optional["PerceptionIdentity"]:
        """
        Parse a perception URI back into an identity.
        
        Format: perception://{kind}/{entity_id}[/r{revision}]
        
        Args:
            uri: The URI to parse
            
        Returns:
            PerceptionIdentity if parsing succeeds, None otherwise
        """
        try:
            # Remove protocol prefix
            if not uri.startswith("perception://"):
                return None
            
            rest = uri[13:]  # Skip "perception://"
            
            # Split into parts
            parts = rest.split("/")
            if len(parts) < 2:
                return None
            
            kind_str = parts[0]
            entity_id = parts[1]
            
            # Parse revision if present
            current_revision = 1
            if len(parts) >= 4 and parts[2] == "r":
                current_revision = int(parts[3])
            
            return cls(
                entity_id=entity_id,
                semantic_identity=f"{kind_str}:{entity_id}",
                entity_kind_str=kind_str,
                creation_revision=str(uuid.uuid4()),
                current_revision=current_revision,
                provenance={"origin": "system"},
            )
        except Exception:
            return None
    
    def for_new_revision(self, new_content_hash: str) -> "PerceptionIdentity":
        """
        Create identity for a new revision of this entity.
        
        This preserves the entity_id but creates a new revision tracking
        structure. The actual revision record is created by EntityRevision.
        
        Args:
            new_content_hash: Hash of the new content
            
        Returns:
            New PerceptionIdentity with incremented current_revision
        """
        return dataclass_replace(
            self,
            current_revision=self.current_revision + 1,
            provenance={
                "origin": "system",
                "creation_process": f"New revision created with hash: {new_content_hash[:16]}...",
                "change_reason": f"Revision update for entity {self.entity_id}",
            },
        )
    
    def is_same_entity(self, other: "PerceptionIdentity") -> bool:
        """Check if two identities refer to the same entity (not revision)."""
        return (
            self.entity_id == other.entity_id
            and self.entity_kind_str == other.entity_kind_str
        )


# =============================================================================
# PERCEPTION IDENTITY BUILDER
# =============================================================================


class PerceptionIdentityBuilder:
    """
    Mutable builder for constructing perception identities.
    """
    
    def __init__(
        self,
        entity_kind_str: str = "unknown",
        semantic_identity: Optional[str] = None,
    ):
        self._entity_id: str = str(uuid.uuid4())
        self._semantic_identity = semantic_identity
        self._entity_kind_str = entity_kind_str
        
        # Revision tracking
        self._creation_revision = str(uuid.uuid4())
        self._current_revision = 1
        
        # Provenance (dict to avoid circular deps)
        self._provenance = {"origin": "system"}
        
        # Timestamps
        self._created_at_utc = time.time()
    
    def set_entity_id(self, entity_id: str) -> "PerceptionIdentityBuilder":
        """Set the entity ID."""
        self._entity_id = entity_id
        return self
    
    def set_semantic_identity(self, semantic_identity: str) -> "PerceptionIdentityBuilder":
        """Set the semantic identity."""
        self._semantic_identity = semantic_identity
        return self
    
    def set_entity_kind_str(self, kind_str: str) -> "PerceptionIdentityBuilder":
        """Set the entity kind string."""
        self._entity_kind_str = kind_str
        return self
    
    def set_creation_revision(self, revision_id: str) -> "PerceptionIdentityBuilder":
        """Set the creation revision ID."""
        self._creation_revision = revision_id
        return self
    
    def set_current_revision(self, revision_number: int) -> "PerceptionIdentityBuilder":
        """Set the current revision number."""
        if revision_number < 1:
            raise ValueError("Revision number must be >= 1")
        self._current_revision = revision_number
        return self
    
    def set_provenance_origin(self, origin: str) -> "PerceptionIdentityBuilder":
        """Set provenance origin."""
        self._provenance["origin"] = origin
        return self
    
    def set_created_at(self, timestamp_utc: float) -> "PerceptionIdentityBuilder":
        """Set creation timestamp."""
        self._created_at_utc = timestamp_utc
        return self
    
    def build(self) -> PerceptionIdentity:
        """
        Build an immutable PerceptionIdentity.
        
        Returns:
            New PerceptionIdentity with all settings applied
            
        Raises:
            ValueError: If required fields are missing
        """
        if not self._entity_id:
            raise ValueError("entity_id is required")
        
        # Set semantic identity from entity ID if not provided
        if self._semantic_identity is None:
            self._semantic_identity = f"{self._entity_kind_str}:{self._entity_id}"
        
        return PerceptionIdentity(
            entity_id=self._entity_id,
            semantic_identity=self._semantic_identity,
            entity_kind_str=self._entity_kind_str,
            creation_revision=self._creation_revision,
            current_revision=self._current_revision,
            provenance=dict(self._provenance),
            created_at_utc=self._created_at_utc,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(instance: PerceptionIdentity, **kwargs) -> PerceptionIdentity:
    """Replace fields in a frozen dataclass."""
    return PerceptionIdentity(
        entity_id=instance.entity_id,
        semantic_identity=instance.semantic_identity,
        entity_kind_str=kwargs.get("entity_kind_str", instance.entity_kind_str),
        creation_revision=kwargs.get("creation_revision", instance.creation_revision),
        current_revision=kwargs.get("current_revision", instance.current_revision),
        provenance=kwargs.get("provenance", instance.provenance),
        created_at_utc=kwargs.get("created_at_utc", instance.created_at_utc),
    )


def generate_entity_id() -> str:
    """Generate a globally unique entity ID."""
    return f"entity:{uuid.uuid4().hex[:24]}"


# =============================================================================
# EXPORTS
# =============================================================================

__all__: list[str] = [
    "PerceptionIdentity",
    "PerceptionIdentityKind",
    "PerceptionIdentityBuilder",
    "dataclass_replace",
    "generate_entity_id",
]