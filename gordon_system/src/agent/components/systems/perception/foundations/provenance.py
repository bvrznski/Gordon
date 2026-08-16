# Perception Provenance - Phase 5.2 Canonical Origin Tracking
# ===========================================================

"""
Perception Provenance: Complete origin tracking for perceptual entities.

Every PerceptualEntity preserves provenance:
    - origin (where it came from)
    - originating system (which process created it)
    - creation process (how it was made)
    - supporting sources (evidence backing it)
    - evidence (direct proof)
    - revision lineage (history of changes)
    - semantic_time (when it became meaningful)

Provenance Laws:
    PROVENANCE-LAW-001: Every entity has complete provenance
    PROVENANCE-LAW-002: Provenance survives revisions
    PROVENANCE-LAW-003: Provenance identifies originating systems
    PROVENANCE-LAW-004: Supporting evidence is inspectable
    PROVENANCE-LAW-005: Transformation history is explicit
    PROVENANCE-LAW-006: Historical provenance is never deleted silently
    PROVENANCE-LAW-007: Historical provenance remains inspectable
    PROVENANCE-LAW-008: Provenance evaluation is deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum, auto
import time
import uuid


# =============================================================================
# PERCEPTION PROVENANCE SOURCE - A single source of information
# =============================================================================


@dataclass(frozen=True)
class PerceptionProvenanceSource:
    """
    A single provenance source (where information came from).
    
    Fields:
        source_type:         Category of the source (observation, inference,
                             document, external_api, etc.)
        source_location:     Where to find the source (file path, URL, etc.)
        confidence:          0.0-1.0 trust in this source
        accessed_at_utc:     When we accessed the source
        notes:               Additional context about the source
    """
    
    source_type: str                      # observation, inference, document, api, etc.
    source_location: str                  # file path, URL, memory reference
    confidence: float = 1.0              # Trust in this source (0.0-1.0)
    accessed_at_utc: float = field(default_factory=time.time)
    notes: Optional[str] = None           # Additional context


# =============================================================================
# PERCEPTION PROVENANCE - Complete origin tracking
# =============================================================================


@dataclass(frozen=True)
class PerceptionProvenance:
    """
    Complete provenance record for a perceptual entity.
    
    Every entity has complete provenance showing where it came from, who
    created it, and what transformations it underwent. Provenance survives
    all revisions and changes.
    
    Fields:
        origin:               Primary source (person, system, event)
        originating_system:   Which system first processed this?
        creation_process:     How was this entity created?
        
        # Supporting evidence
        supporting_sources:   List of sources that support this content
        direct_evidence:      Direct proof of the content
        
        # Transformation history
        transformation_history: List of transformations applied
        
        # Revision lineage
        revision_lineage:     Full chain of revisions (most recent first)
        previous_revision_id: ID of immediately prior revision
        
        # Semantic time
        semantic_time_utc:    When this became semantically meaningful
        created_at_utc:       When the record was created
        
        # Change tracking
        change_reason:        Why was this revision created?
        changed_by:           Who made the change (optional)
        
        # Validation
        validation_status:    Status of provenance validation
    """
    
    # Core origin
    origin: str                           # Primary source identifier
    originating_system: Optional[str] = None  # System that first processed
    
    # Creation process
    creation_process: Optional[str] = None  # How was this created?
    
    # Supporting evidence
    supporting_sources: Tuple[PerceptionProvenanceSource, ...] = field(
        default_factory=tuple
    )
    direct_evidence: Optional[str] = None   # Direct proof reference
    
    # Transformation history
    transformation_history: Tuple[str, ...] = field(default_factory=tuple)
    
    # Revision lineage
    revision_lineage: Tuple[str, ...] = field(default_factory=tuple)
    previous_revision_id: Optional[str] = None
    
    # Semantic time
    semantic_time_utc: float = field(default_factory=time.time)
    created_at_utc: float = field(default_factory=time.time)
    
    # Change tracking
    change_reason: Optional[str] = None
    changed_by: Optional[str] = None
    
    # Validation
    validation_status: str = "unvalidated"
    
    def add_source(
        self,
        source_type: str,
        source_location: str,
        confidence: float = 1.0,
    ) -> "PerceptionProvenance":
        """Add a provenance source to this record."""
        new_source = PerceptionProvenanceSource(
            source_type=source_type,
            source_location=source_location,
            confidence=confidence,
        )
        return dataclass_replace_provenance(
            self,
            supporting_sources=self.supporting_sources + (new_source,),
        )
    
    def extend(
        self,
        change_reason: str,
        changed_by: Optional[str] = None,
        previous_revision_id: Optional[str] = None,
    ) -> "PerceptionProvenance":
        """
        Create a new provenance record for a revision.
        
        Args:
            change_reason: Why was this revision created?
            changed_by: Who made the change (optional)
            previous_revision_id: ID of prior revision (optional)
            
        Returns:
            New PerceptionProvenance with updated lineage
        """
        # Build new revision ID
        new_revision_id = f"{previous_revision_id}:r{len(self.revision_lineage) + 1}" if previous_revision_id else str(uuid.uuid4())
        
        return dataclass_replace_provenance(
            self,
            semantic_time_utc=time.time(),
            change_reason=change_reason,
            changed_by=changed_by,
            revision_lineage=(new_revision_id,) + self.revision_lineage,
            previous_revision_id=previous_revision_id,
        )
    
    def with_change_reason(self, reason: str) -> "PerceptionProvenance":
        """Set the change reason."""
        return dataclass_replace_provenance(self, change_reason=reason)
    
    def with_changed_by(self, changer: str) -> "PerceptionProvenance":
        """Set who made the change."""
        return dataclass_replace_provenance(self, changed_by=changer)
    
    def with_revision_identity(self, revision_id: str) -> "PerceptionProvenance":
        """Add a revision identity to the lineage."""
        new_lineage = (revision_id,) + self.revision_lineage
        return dataclass_replace_provenance(self, revision_lineage=new_lineage)
    
    @property
    def is_complete(self) -> bool:
        """Check if provenance has essential information."""
        return (
            len(self.origin) > 0 and 
            self.created_at_utc > 0.0 and
            self.validation_status in ("unvalidated", "valid")
        )
    
    @classmethod
    def from_observation(
        cls,
        observation: str,
        observer: Optional[str] = None,
        source_location: Optional[str] = None,
    ) -> "PerceptionProvenance":
        """
        Create provenance for an observed entity.
        
        Args:
            observation: What was observed?
            observer: Who/what observed it? (optional)
            source_location: Where was it observed? (optional)
            
        Returns:
            New PerceptionProvenance with observation context
        """
        return cls(
            origin=observer or "unknown_observer",
            creation_process=f"observed: {observation}",
            supporting_sources=(
                PerceptionProvenanceSource(
                    source_type="observation",
                    source_location=source_location or "perception",
                    confidence=1.0,
                ),
            ) if source_location else tuple(),
            semantic_time_utc=time.time(),
            created_at_utc=time.time(),
        )
    
    @classmethod
    def from_inference(
        cls,
        premise: str,
        conclusion: str,
        inference_system: str,
        confidence: float = 1.0,
    ) -> "PerceptionProvenance":
        """
        Create provenance for an inferred entity.
        
        Args:
            premise: What was the reasoning basis?
            conclusion: What was concluded?
            inference_system: Which system made the inference?
            confidence: Trust in the inference (optional)
            
        Returns:
            New PerceptionProvenance with inference context
        """
        return cls(
            origin=inference_system,
            originating_system=inference_system,
            creation_process=f"inferred from '{premise}' to get '{conclusion}'",
            supporting_sources=(
                PerceptionProvenanceSource(
                    source_type="inference",
                    source_location=inference_system,
                    confidence=confidence,
                ),
            ),
            semantic_time_utc=time.time(),
            created_at_utc=time.time(),
        )


# =============================================================================
# PERCEPTION PROVENANCE BUILDER
# =============================================================================


class PerceptionProvenanceBuilder:
    """
    Mutable builder for constructing provenance records.
    """
    
    def __init__(self):
        self._origin: str = "unknown"
        self._originating_system: Optional[str] = None
        self._creation_process: Optional[str] = None
        
        self._supporting_sources: List[PerceptionProvenanceSource] = []
        self._direct_evidence: Optional[str] = None
        
        self._transformation_history: List[str] = []
        
        self._revision_lineage: List[str] = []
        self._previous_revision_id: Optional[str] = None
        
        self._semantic_time_utc: float = time.time()
        self._created_at_utc: float = time.time()
        
        self._change_reason: Optional[str] = None
        self._changed_by: Optional[str] = None
        
        self._validation_status: str = "unvalidated"
    
    def set_origin(self, origin: str) -> "PerceptionProvenanceBuilder":
        """Set the primary source."""
        self._origin = origin
        return self
    
    def set_originating_system(self, system: str) -> "PerceptionProvenanceBuilder":
        """Set the originating system."""
        self._originating_system = system
        return self
    
    def set_creation_process(self, process: str) -> "PerceptionProvenanceBuilder":
        """Set how the entity was created."""
        self._creation_process = process
        return self
    
    def add_supporting_source(
        self,
        source_type: str,
        source_location: str,
        confidence: float = 1.0,
    ) -> "PerceptionProvenanceBuilder":
        """Add a supporting source."""
        self._supporting_sources.append(
            PerceptionProvenanceSource(
                source_type=source_type,
                source_location=source_location,
                confidence=confidence,
            )
        )
        return self
    
    def set_direct_evidence(self, evidence: str) -> "PerceptionProvenanceBuilder":
        """Set direct evidence reference."""
        self._direct_evidence = evidence
        return self
    
    def add_transformation(self, transformation: str) -> "PerceptionProvenanceBuilder":
        """Record a transformation applied to this entity."""
        self._transformation_history.append(transformation)
        return self
    
    def add_to_lineage(self, revision_id: str) -> "PerceptionProvenanceBuilder":
        """Add to the revision lineage."""
        self._revision_lineage.insert(0, revision_id)
        return self
    
    def set_previous_revision(self, prev_id: str) -> "PerceptionProvenanceBuilder":
        """Set the previous revision ID."""
        self._previous_revision_id = prev_id
        return self
    
    def set_semantic_time(self, timestamp_utc: float) -> "PerceptionProvenanceBuilder":
        """Set semantic time (when it became meaningful)."""
        self._semantic_time_utc = timestamp_utc
        return self
    
    def set_created_at(self, timestamp_utc: float) -> "PerceptionProvenanceBuilder":
        """Set creation timestamp."""
        self._created_at_utc = timestamp_utc
        return self
    
    def set_change_reason(self, reason: str) -> "PerceptionProvenanceBuilder":
        """Set the change reason."""
        self._change_reason = reason
        return self
    
    def set_changed_by(self, changer: str) -> "PerceptionProvenanceBuilder":
        """Set who made the change."""
        self._changed_by = changer
        return self
    
    def set_validation_status(self, status: str) -> "PerceptionProvenanceBuilder":
        """Set validation status."""
        self._validation_status = status
        return self
    
    def build(self) -> PerceptionProvenance:
        """
        Build an immutable PerceptionProvenance.
        
        Returns:
            New PerceptionProvenance with all settings applied
        """
        return PerceptionProvenance(
            origin=self._origin,
            originating_system=self._originating_system,
            creation_process=self._creation_process,
            supporting_sources=tuple(self._supporting_sources),
            direct_evidence=self._direct_evidence,
            transformation_history=tuple(self._transformation_history),
            revision_lineage=tuple(self._revision_lineage),
            previous_revision_id=self._previous_revision_id,
            semantic_time_utc=self._semantic_time_utc,
            created_at_utc=self._created_at_utc,
            change_reason=self._change_reason,
            changed_by=self._changed_by,
            validation_status=self._validation_status,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace_provenance(instance: PerceptionProvenance, **kwargs) -> PerceptionProvenance:
    """Replace fields in a frozen provenance dataclass."""
    return PerceptionProvenance(
        origin=kwargs.get("origin", instance.origin),
        originating_system=kwargs.get("originating_system", instance.originating_system),
        creation_process=kwargs.get("creation_process", instance.creation_process),
        supporting_sources=kwargs.get("supporting_sources", instance.supporting_sources),
        direct_evidence=kwargs.get("direct_evidence", instance.direct_evidence),
        transformation_history=kwargs.get("transformation_history", instance.transformation_history),
        revision_lineage=kwargs.get("revision_lineage", instance.revision_lineage),
        previous_revision_id=kwargs.get("previous_revision_id", instance.previous_revision_id),
        semantic_time_utc=kwargs.get("semantic_time_utc", instance.semantic_time_utc),
        created_at_utc=kwargs.get("created_at_utc", instance.created_at_utc),
        change_reason=kwargs.get("change_reason", instance.change_reason),
        changed_by=kwargs.get("changed_by", instance.changed_by),
        validation_status=kwargs.get("validation_status", instance.validation_status),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "PerceptionProvenance",
    "PerceptionProvenanceSource",
    "PerceptionProvenanceBuilder",
    "dataclass_replace_provenance",
]