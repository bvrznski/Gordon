# Gordon Phase 5.7.2-I: Experiential Field Snapshot
# ===============================================================================
#
# Immutable field snapshot and content model for the experiential field.
#

"""
Immutable snapshot model for Experiential Field Builder.

This module defines:
    - ExperientialFieldSnapshot: The immutable, versioned field state
    - FieldContent: A content item within the field
    - FieldRelation: Relations between content items
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional, Set


# =============================================================================
# FIELD CONTENT
# =============================================================================

@dataclass(frozen=True)
class FieldContent:
    """
    Immutable content item within the experiential field.
    
    Each content item represents a contribution that has been validated,
    normalized, and accepted into the current field state. Content items
    preserve source provenance and classification metadata.
    
    NOT included (external to field):
        - Full payload data (only bounded references)
        - Runtime state (locks, threads, callbacks)
        - Action authority
    """
    
    # Identity (required fields first - no defaults before defaults)
    content_id: str
    """Unique identifier for this content item."""
    
    content_kind: str
    """Type of content (workspace, perceptual, etc.)."""
    
    source_id: str
    """Source that contributed this content."""
    
    # Classification (optional with defaults)
    contribution_id: Optional[str] = None
    """Contribution that produced this content (for provenance)."""
    
    privacy_classification: str = "internal"
    """Privacy level of this content."""
    
    trust_classification: str = "untrusted"
    """Trust level of this content."""
    
    source_generation: int = 0
    """Source generation at time of contribution."""
    
    # Content reference (bounded)
    summary: Optional[str] = None
    """Short bounded summary of the content."""
    
    representation_reference: Optional[str] = None
    """Reference to full content representation (not embedded)."""
    
    # Timing and freshness
    freshness_utc: float = field(default_factory=time.time)
    """When this content was created/fresh."""
    
    lifetime_seconds: float = 3600.0  # Default 1 hour
    """Expected lifetime for this content."""
    
    salience_reference: Optional[str] = None
    """Reference to salience score/assignment."""
    
    attention_reference: Optional[str] = None
    """Reference to attention focus indicator."""
    
    priority_reference: Optional[str] = None
    """Reference to priority assignment."""
    
    provenance: Optional[str] = None
    """Provenance chain for this content item."""
    
    @classmethod
    def from_contribution(
        cls,
        contribution_id: str,
        source_id: str,
        content_kind: str,
        representation_reference: Optional[str] = None,
        summary: Optional[str] = None,
        privacy_classification: str = "internal",
        trust_classification: str = "untrusted",
        source_generation: int = 0,
    ) -> "FieldContent":
        """
        Create a FieldContent from a contribution.
        
        Args:
            contribution_id: ID of the contributing envelope
            source_id: Source submitting the contribution
            content_kind: Kind/type of content
            representation_reference: Reference to full payload (optional)
            summary: Short bounded summary (optional)
            privacy_classification: Privacy level
            trust_classification: Trust level  
            source_generation: Source's generation at time of submission
            
        Returns:
            New FieldContent with contribution metadata
        """
        import uuid
        content_id = f"content-{uuid.uuid4().hex[:8]}"
        
        return cls(
            content_id=content_id,
            contribution_id=contribution_id,
            source_id=source_id,
            content_kind=content_kind,
            representation_reference=representation_reference,
            summary=summary,
            privacy_classification=privacy_classification,
            trust_classification=trust_classification,
            source_generation=source_generation,
        )


# =============================================================================
# FIELD RELATION
# =============================================================================

@dataclass(frozen=True)
class FieldRelation:
    """
    Immutable relation between content items in the field.
    
    Relations represent associations, dependencies, and connections
    between field contents. They enable experiential binding without
    merging semantic meaning.
    """
    
    # Identity
    relation_id: str
    """Unique identifier for this relation."""
    
    # Content references (by ID)
    source_content_id: str
    """ID of the content that is the relation source."""
    
    target_content_id: str
    """ID of the content that is the relation target."""
    
    # Relation kind
    relation_kind: str
    """
    Type of relation. Predefined kinds include:
        - same_object: Both contents refer to the same entity
        - part_of: Source is part of target
        - located_relative_to: Spatial/temporal relationship
        - associated_with: General association
        - conflicts_with: Contents are in conflict
        - supports: Source supports/validates target
    """
    
    # Directionality (for asymmetric relations)
    directed: bool = True
    """Whether this relation is directed."""
    
    # Confidence and metadata
    confidence: float = 1.0
    """Confidence level for this relation."""
    
    provenance: Optional[str] = None
    """Provenance for this relation (optional)."""
    
    @classmethod
    def create_same_object(
        cls,
        content_id_1: str,
        content_id_2: str,
    ) -> "FieldRelation":
        """
        Create a same-object relation between two content items.
        
        This indicates both contents refer to the same entity.
        
        Args:
            content_id_1: First content ID
            content_id_2: Second content ID (same object)
            
        Returns:
            New FieldRelation with same_object kind
        """
        import uuid
        return cls(
            relation_id=f"rel-{uuid.uuid4().hex[:8]}",
            source_content_id=content_id_1,
            target_content_id=content_id_2,
            relation_kind="same_object",
            directed=False,
        )
    
    @classmethod
    def create_part_of(
        cls,
        part_content_id: str,
        whole_content_id: str,
    ) -> "FieldRelation":
        """
        Create a part-of relation.
        
        Args:
            part_content_id: Content that is the part
            whole_content_id: Content that contains the part
            
        Returns:
            New FieldRelation with part_of kind
        """
        import uuid
        return cls(
            relation_id=f"rel-{uuid.uuid4().hex[:8]}",
            source_content_id=part_content_id,
            target_content_id=whole_content_id,
            relation_kind="part_of",
            directed=True,
        )


# =============================================================================
# EXPERIENTIAL FIELD SNAPSHOT
# =============================================================================

@dataclass(frozen=True)
class ExperientialFieldSnapshot:
    """
    Immutable snapshot of the experiential field at a point in time.
    
    A field snapshot represents the complete, bounded current-context state
    after construction. Snapshots are versioned by generation and may be
    superseded by newer generations through atomic transitions.
    
    Snapshot properties:
        - Immutable: Once created, never modified
        - Bounded: All collections respect capacity limits
        - Versioned: Has explicit field_id and generation
        - Provenance-preserving: Links to previous generation where applicable
    
    NOT included (external):
        - Runtime state objects
        - Full payloads (only references)
        - External service connections
    """
    
    # Identity and versioning
    field_id: str
    """Unique identifier for this logical field."""
    
    generation: int = 0
    """Current generation number (strictly monotonic)."""
    
    previous_generation: Optional[int] = None
    """Previous generation (for lineage tracking)."""
    
    transition_id: Optional[str] = None
    """Transition that produced this snapshot (if any)."""
    
    # Contents (bounded set)
    contents: Tuple[FieldContent, ...] = field(default_factory=tuple)
    """All content items in the field."""
    
    relations: Tuple[FieldRelation, ...] = field(default_factory=tuple)
    """All relations between content items."""
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    """When this snapshot was created."""
    
    # Status and health
    build_status: str = "valid"
    """Current status (building, valid, degraded, invalid)."""
    
    degradation_modes: Tuple[str, ...] = field(default_factory=tuple)
    """Any degradation modes active in this snapshot."""
    
    # Summary information (bounded, computed from contents)
    content_count: int = 0
    """Number of content items (computed from contents tuple)."""
    
    relation_count: int = 0
    """Number of relations (computed from relations tuple)."""
    
    source_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Set of unique source IDs in this snapshot."""
    
    privacy_summary: str = "internal"
    """Summary privacy classification of all contents."""
    
    trust_summary: str = "medium"
    """Summary trust classification of all contents."""
    
    # Provenance
    provenance: Optional[str] = None
    """Provenance information for this snapshot."""
    
    def __post_init__(self):
        """Post-initialization validation and computed fields."""
        object.__setattr__(self, "content_count", len(self.contents))
        object.__setattr__(self, "relation_count", len(self.relations))
        
        # Extract unique source IDs
        source_ids_set: Set[str] = set()
        for content in self.contents:
            source_ids_set.add(content.source_id)
        object.__setattr__(self, "source_ids", tuple(sorted(source_ids_set)))
    
    @classmethod
    def initial(cls, field_id: str) -> "ExperientialFieldSnapshot":
        """
        Create an initial empty snapshot.
        
        Args:
            field_id: ID for this logical field
            
        Returns:
            Initial snapshot with zero contents and generation 0
        """
        return cls(
            field_id=field_id,
            generation=0,
            previous_generation=None,
            created_at_utc=time.time(),
            build_status="valid",
        )
    
    def next_generation(self, transition_id: str) -> "ExperientialFieldSnapshot":
        """
        Create the next generation snapshot from this one.
        
        This returns a new snapshot with incrementing generation number
        and preserving previous-generation references for lineage.
        
        Args:
            transition_id: ID of the transition producing this generation
            
        Returns:
            New ExperientialFieldSnapshot with generation + 1
        """
        return ExperientialFieldSnapshot(
            field_id=self.field_id,
            generation=self.generation + 1,
            previous_generation=self.generation,
            transition_id=transition_id,
            created_at_utc=time.time(),
            contents=self.contents,  # Retain same content structure initially
            relations=self.relations,
            build_status="valid",
        )
    
    @property
    def is_empty(self) -> bool:
        """Check if this snapshot has no contents."""
        return len(self.contents) == 0
    
    @property
    def is_valid(self) -> bool:
        """Check if this snapshot's status indicates validity."""
        return self.build_status in ("valid", "building")
    
    @property
    def is_degraded(self) -> bool:
        """Check if this snapshot is in degraded mode."""
        return len(self.degradation_modes) > 0


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "FieldContent",
    "FieldRelation",
    "ExperientialFieldSnapshot",
)