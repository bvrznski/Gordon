# Knowledge Representation Descriptors - Phase 6.2
# ================================================

"""
Representation Descriptor: Metadata about representations independent of content.

This module provides descriptors that track:
    * Identity - Unique representation identifier
    * Kind - Type of representation (symbolic, vector, latent, hybrid)
    * Revision - Semantic revision this representation corresponds to
    * Lifecycle State - Current lifecycle state
    * Compatibility - Version compatibility information
    * Generation Context - How/when the representation was created
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# REPRESENTATION KINDS - Types of representations
# =============================================================================


class RepresentationKind(Enum):
    """
    Kinds of knowledge representations.
    
    Defines the canonical representation types supported by Gordon:
        SYMBOLIC     -> Explicit semantic structure for reasoning
        VECTOR       -> Continuous embeddings for similarity retrieval
        LATENT       -> Compressed features from neural models
        HYBRID       -> Integrated views combining multiple modalities
        EXTERNAL     -> Serialized formats for communication
    """
    
    SYMBOLIC = "symbolic"
    VECTOR = "vector"
    LATENT = "latent"
    HYBRID = "hybrid"
    EXTERNAL = "external"


# =============================================================================
# LIFECYCLE STATES - Representation maturity progression
# =============================================================================


class RepresentationLifecycleState(Enum):
    """
    States of representation lifecycle progression.
    
    Defines how representations evolve:
        CREATED      -> Initial creation (not yet validated)
        ACTIVE       -> Published and in use
        STALE        -> Needs regeneration due to model changes
        REGENERATING -> Currently being regenerated
        SUPERSEDED   -> Replaced by newer version
        ARCHIVED     -> Preserved for historical purposes
        INVALID      -> Failed validation, not for use
    """
    
    CREATED = "created"
    ACTIVE = "active"
    STALE = "stale"
    REGENERATING = "regenerating"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"
    INVALID = "invalid"


# =============================================================================
# REPRESENTATION DESCRIPTOR - Metadata container
# =============================================================================


@dataclass(frozen=True)
class RepresentationDescriptor:
    """
    Descriptor providing metadata about a representation.
    
    Descriptors provide information about representations without exposing
    their full content. This enables efficient metadata queries and tracking.
    
    Fields:
        representation_identity: Unique identifier for this representation
        semantic_identity:       Identity of the semantic artifact being represented
        representation_kind:     Type of representation (symbolic, vector, latent)
        representation_revision: Version number for this representation
        lifecycle_state:         Current lifecycle state
        compatibility:           Compatibility with other representations
        generation_context:      How/when the representation was created
        provenance:              Generation history and tracking info
    """
    
    # Identity (required)
    representation_identity: str            # Unique representation ID
    semantic_identity: str                  # Artifact being represented
    
    # Kind and revision
    representation_kind: RepresentationKind
    representation_revision: int = 1
    
    # Lifecycle
    lifecycle_state: RepresentationLifecycleState = RepresentationLifecycleState.CREATED
    
    # Compatibility tracking
    compatibility: Dict[str, Any] = field(default_factory=dict)
    
    # Generation context
    generation_context: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    provenance_identity: str = field(default_factory=lambda: f"prov:{uuid.uuid4().hex[:16]}")
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_valid(self) -> bool:
        """Check if descriptor has valid data."""
        return (
            len(self.representation_identity) > 0 and
            len(self.semantic_identity) > 0 and
            self.representation_kind is not None
        )
    
    @property
    def is_active(self) -> bool:
        """Check if representation is active and usable."""
        return self.lifecycle_state == RepresentationLifecycleState.ACTIVE
    
    @property
    def is_stale(self) -> bool:
        """Check if representation needs regeneration."""
        return self.lifecycle_state == RepresentationLifecycleState.STALE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert descriptor to dictionary for serialization."""
        return {
            "representation_identity": self.representation_identity,
            "semantic_identity": self.semantic_identity,
            "representation_kind": self.representation_kind.value if hasattr(
                self.representation_kind, 'value'
            ) else str(self.representation_kind),
            "representation_revision": self.representation_revision,
            "lifecycle_state": self.lifecycle_state.value if hasattr(
                self.lifecycle_state, 'value'
            ) else str(self.lifecycle_state),
            "compatibility": self.compatibility,
            "generation_context": self.generation_context,
            "provenance_identity": self.provenance_identity,
            "created_at_utc": self.created_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepresentationDescriptor":
        """Create descriptor from dictionary."""
        return cls(
            representation_identity=data.get("representation_identity", str(uuid.uuid4())),
            semantic_identity=data.get("semantic_identity", ""),
            representation_kind=RepresentationKind(data.get("representation_kind", "symbolic")),
            representation_revision=int(data.get("representation_revision", 1)),
            lifecycle_state=RepresentationLifecycleState(
                data.get("lifecycle_state", "created")
            ),
            compatibility=data.get("compatibility", {}),
            generation_context=data.get("generation_context", {}),
            provenance_identity=data.get("provenance_identity", f"prov:{uuid.uuid4().hex[:16]}"),
            created_at_utc=float(data.get("created_at_utc", time.time())),
        )
    
    def with_revision(self, new_revision: int) -> "RepresentationDescriptor":
        """Create new descriptor with updated revision."""
        return RepresentationDescriptor(
            representation_identity=self.representation_identity,
            semantic_identity=self.semantic_identity,
            representation_kind=self.representation_kind,
            representation_revision=new_revision,
            lifecycle_state=self.lifecycle_state,
            compatibility={**self.compatibility, "source_revision": self.representation_revision},
            generation_context=self.generation_context.copy(),
            provenance_identity=f"prov:{uuid.uuid4().hex[:16]}",
            created_at_utc=self.created_at_utc,
        )
    
    def mark_stale(self) -> "RepresentationDescriptor":
        """Mark representation as stale (needs regeneration)."""
        return RepresentationDescriptor(
            representation_identity=self.representation_identity,
            semantic_identity=self.semantic_identity,
            representation_kind=self.representation_kind,
            representation_revision=self.representation_revision,
            lifecycle_state=RepresentationLifecycleState.STALE,
            compatibility={**self.compatibility, "stale_reason": "model_updated"},
            generation_context=self.generation_context.copy(),
            provenance_identity=f"prov:{uuid.uuid4().hex[:16]}",
            created_at_utc=self.created_at_utc,
        )
    
    def mark_active(self) -> "RepresentationDescriptor":
        """Mark representation as active."""
        return RepresentationDescriptor(
            representation_identity=self.representation_identity,
            semantic_identity=self.semantic_identity,
            representation_kind=self.representation_kind,
            representation_revision=self.representation_revision,
            lifecycle_state=RepresentationLifecycleState.ACTIVE,
            compatibility={**self.compatibility, "active_reason": "regeneration_complete"},
            generation_context=self.generation_context.copy(),
            provenance_identity=f"prov:{uuid.uuid4().hex[:16]}",
            created_at_utc=time.time(),
        )


# =============================================================================
# SESSION DESCRIPTOR - Track representation sessions
# =============================================================================


@dataclass(frozen=True)
class RepresentationSession:
    """
    Session tracking multiple simultaneous representations.
    
    Sessions coordinate operations that involve multiple representations of
    the same semantic artifact.
    
    Fields:
        session_identity:       Unique session identifier
        semantic_identity:      Artifact being represented
        semantic_revision:      Revision number for this session
        participating_representations: IDs of representations involved
        operation_kind:         Type of session (reasoning, retrieval, etc.)
        lifecycle_state:        Session state tracking
        compatibility_revision: Version used during session
        provenance:             Session metadata
    """
    
    session_identity: str                  # Unique session ID
    semantic_identity: str                 # Artifact being represented
    
    # Revision info
    semantic_revision: int = 1
    
    # Participation
    participating_representations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Operation type
    operation_kind: str = "unknown"        # e.g., "reasoning", "retrieval"
    
    # Lifecycle
    lifecycle_state: RepresentationLifecycleState = RepresentationLifecycleState.CREATED
    
    # Compatibility tracking
    compatibility_revision: int = 1
    
    provenance_identity: str = field(default_factory=lambda: f"session:{uuid.uuid4().hex[:16]}")
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create_initial(
        cls,
        semantic_identity: str,
        operation_kind: str = "unknown",
        representation_ids: Optional[Tuple[str, ...]] = None,
    ) -> "RepresentationSession":
        """Create a new session."""
        return cls(
            session_identity=f"session:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            operation_kind=operation_kind,
            participating_representations=representation_ids or tuple(),
        )
    
    def add_representation(self, representation_id: str) -> "RepresentationSession":
        """Add a representation to this session."""
        return RepresentationSession(
            session_identity=self.session_identity,
            semantic_identity=self.semantic_identity,
            semantic_revision=self.semantic_revision,
            participating_representations=self.participating_representations + (representation_id,),
            operation_kind=self.operation_kind,
            lifecycle_state=self.lifecycle_state,
            compatibility_revision=self.compatibility_revision,
            provenance_identity=self.provenance_identity,
            created_at_utc=self.created_at_utc,
        )


__all__ = [
    # Kinds
    "RepresentationKind",
    
    # Lifecycle states
    "RepresentationLifecycleState",
    
    # Descriptors
    "RepresentationDescriptor",
    "RepresentationSession",
]