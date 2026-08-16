# Memory Revision - Phase 5.1 Canonical Versioning
# ==================================================

"""
Memory Revision: Versioned evolution of memory artifacts.

Every revision preserves:
    - previous revision (link to prior state)
    - change reason (why it changed)
    - semantic changes (what actually changed)
    - validation (was this valid?)
    - provenance (how was the change made?)

Revision Laws:
    REVISION-LAW-001: Revisions preserve lineage
    REVISION-LAW-002: Revisions preserve previous semantic state
    REVISION-LAW-003: Revision reasons are explicit
    REVISION-LAW-004: Revision validation precedes publication
    REVISION-LAW-005: Historical revisions are inspectable
    REVISION-LAW-006: Revision identity is unique
    REVISION-LAW-007: Revision provenance is complete
    REVISION-LAW-008: Revision processing is deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid

# Import from provenance module (circular dependency handled at runtime)
try:
    from .provenance import MemoryProvenance, MemoryProvenanceSource
except ImportError:
    # Fallback definitions if provenance not yet loaded
    class MemoryProvenance:
        pass
    class MemoryProvenanceSource:
        pass


# =============================================================================
# MEMORY REVISION CHANGE REASONS
# =============================================================================


class MemoryRevisionChangeReason(Enum):
    """
    Categories of reasons for creating a revision.
    
    These classify why an artifact was revised:
        - CONTENT_UPDATE: Content changed (corrected, updated)
        - SEMANTIC_REFINEMENT: Meaning became more precise
        - EVIDENCE_UPDATE: New supporting evidence found
        - VALIDITY_CHANGE: Validity status changed
        - CONFIDENCE_ADJUSTMENT: Confidence/uncertainty updated
        - STATUS_UPDATE: Status changed (active/dormant, etc.)
        - RELATIONSHIP_CHANGE: Relationships to other artifacts changed
        - PROVENANCE_UPDATE: Provenance information added or corrected
        - STRUCTURAL_CHANGE: Artifact structure modified
        - CORRECTION: Previous error was fixed
    """
    
    CONTENT_UPDATE = "content_update"
    SEMANTIC_REFINEMENT = "semantic_refinement"
    EVIDENCE_UPDATE = "evidence_update"
    VALIDITY_CHANGE = "validity_change"
    CONFIDENCE_ADJUSTMENT = "confidence_adjustment"
    STATUS_UPDATE = "status_update"
    RELATIONSHIP_CHANGE = "relationship_change"
    PROVENANCE_UPDATE = "provenance_update"
    STRUCTURAL_CHANGE = "structural_change"
    CORRECTION = "correction"


# =============================================================================
# REVISION LINEAGE - Tracking revision history
# =============================================================================


@dataclass(frozen=True)
class RevisionLineage:
    """
    Complete lineage of revisions for an artifact.
    
    The lineage is a list of revision IDs from oldest to newest, providing
    complete traceability of the artifact's evolution.
    
    Fields:
        revision_ids: List of all revision IDs in order (oldest first)
        current_revision_id: ID of the most recent revision
        total_revisions: Count of revisions in lineage
    """
    
    revision_ids: Tuple[str, ...]
    current_revision_id: str
    total_revisions: int = field(default=0)
    
    def __post_init__(self):
        # Ensure total_revisions is set correctly
        if self.total_revisions == 0:
            object.__setattr__(self, "total_revisions", len(self.revision_ids))
    
    @classmethod
    def from_list(cls, revision_ids: List[str]) -> "RevisionLineage":
        """
        Create a lineage from a list of revision IDs.
        
        Args:
            revision_ids: List of revision IDs (oldest first)
            
        Returns:
            New RevisionLineage with all revisions tracked
        """
        return cls(
            revision_ids=tuple(revision_ids),
            current_revision_id=revision_ids[-1] if revision_ids else "",
            total_revisions=len(revision_ids),
        )
    
    def add_revision(self, new_revision_id: str) -> "RevisionLineage":
        """Add a new revision to the lineage."""
        return dataclass_replace(
            self,
            revision_ids=self.revision_ids + (new_revision_id,),
            current_revision_id=new_revision_id,
            total_revisions=len(self.revision_ids) + 1,
        )
    
    def get_revision_at_index(self, index: int) -> Optional[str]:
        """Get the revision ID at a specific index."""
        if 0 <= index < len(self.revision_ids):
            return self.revision_ids[index]
        return None
    
    @property
    def is_first_revision(self) -> bool:
        """Check if this is the first revision (no prior revisions)."""
        return len(self.revision_ids) == 1
    
    @property
    def previous_revision_id(self) -> Optional[str]:
        """Get the ID of the immediately prior revision."""
        if len(self.revision_ids) < 2:
            return None
        return self.revision_ids[-2]


# =============================================================================
# MEMORY REVISION - Versioned evolution record
# =============================================================================


@dataclass(frozen=True)
class MemoryRevision:
    """
    Record of a memory artifact revision.
    
    A revision preserves the previous semantic state while recording what
    changed. This enables complete history inspection and rollback if needed.
    
    Fields:
        revision_identity:   Unique ID for this revision record
        previous_revision:   ID of the revision being superseded
        
        # Change tracking
        change_reason:       Why was this revision created?
        change_summary:      Brief summary of what changed
        
        # Semantic changes
        semantic_changes:    Detailed description of what changed semantically
        
        # Validation
        validation_status:   Was this revision validated?
        validation_result:   Details of the validation (if any)
        
        # Provenance
        provenance:          How was this revision created?
        
        # Timestamps
        created_at_utc:      When the revision was created
        effective_from_utc:  When this revision becomes active
        
        # Authorship
        changed_by:          Who made this change? (optional)
    """
    
    # Identity
    revision_identity: str                # Unique ID for this revision record
    
    # Revision chain tracking
    previous_revision_id: Optional[str]   # What did this supersede?
    
    # Change information
    change_reason: MemoryRevisionChangeReason  # Why was it revised?
    change_summary: str                   # Brief description of changes
    
    # Semantic details
    semantic_changes: Dict[str, Any] = field(default_factory=dict)
    
    # Validation
    validation_status: str = "unvalidated"
    validation_result: Optional[str] = None
    
    # Provenance
    provenance: MemoryProvenance = field(default_factory=MemoryProvenance)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    effective_from_utc: float = field(default_factory=time.time)
    
    # Authorship
    changed_by: Optional[str] = None
    
    @classmethod
    def create_for_artifact(
        cls,
        artifact_id: str,
        previous_revision_id: Optional[str],
        change_reason: MemoryRevisionChangeReason,
        change_summary: str,
        semantic_changes: Dict[str, Any],
        changed_by: Optional[str] = None,
    ) -> "MemoryRevision":
        """
        Create a new revision record for an artifact.
        
        Args:
            artifact_id: Which artifact is being revised?
            previous_revision_id: The ID being superseded (if any)
            change_reason: Why was this revised?
            change_summary: Brief description of changes
            semantic_changes: What actually changed?
            changed_by: Who made the change? (optional)
            
        Returns:
            New MemoryRevision with all settings applied
        """
        revision_id = f"{artifact_id}:r{uuid.uuid4().hex[:12]}"
        
        return cls(
            revision_identity=revision_id,
            previous_revision_id=previous_revision_id,
            change_reason=change_reason,
            change_summary=change_summary,
            semantic_changes=semantic_changes.copy(),
            validation_status="unvalidated",
            provenance=MemoryProvenance(
                origin=changed_by or "system",
                creation_process=f"created revision: {change_summary}",
                change_reason=str(change_reason.value),
                changed_by=changed_by,
            ),
        )
    
    def validate(self, result: str) -> "MemoryRevision":
        """Mark this revision as validated."""
        return dataclass_replace(
            self,
            validation_status="valid",
            validation_result=result,
        )
    
    def invalidate(self, reason: str) -> "MemoryRevision":
        """Mark this revision as invalid."""
        return dataclass_replace(
            self,
            validation_status="invalid",
            validation_result=reason,
        )


# =============================================================================
# MEMORY REVISION BUILDER
# =============================================================================


class MemoryRevisionBuilder:
    """
    Mutable builder for constructing revision records.
    """
    
    def __init__(self, artifact_id: str):
        self._artifact_id = artifact_id
        
        # Revision chain tracking
        self._previous_revision_id: Optional[str] = None
        
        # Change information
        self._change_reason: MemoryRevisionChangeReason = MemoryRevisionChangeReason.CONTENT_UPDATE
        self._change_summary: str = ""
        
        # Semantic changes
        self._semantic_changes: Dict[str, Any] = {}
        
        # Validation
        self._validation_status: str = "unvalidated"
        self._validation_result: Optional[str] = None
        
        # Provenance
        self._provenance = MemoryProvenance()
        
        # Timestamps
        self._created_at_utc: float = time.time()
        self._effective_from_utc: float = time.time()
        
        # Authorship
        self._changed_by: Optional[str] = None
        
        # Generate revision ID
        self._revision_identity = f"{artifact_id}:r{uuid.uuid4().hex[:12]}"
    
    def set_previous_revision(self, prev_id: str) -> "MemoryRevisionBuilder":
        """Set the previous revision ID being superseded."""
        self._previous_revision_id = prev_id
        return self
    
    def set_change_reason(self, reason: MemoryRevisionChangeReason) -> "MemoryRevisionBuilder":
        """Set why this revision was created."""
        self._change_reason = reason
        return self
    
    def set_change_summary(self, summary: str) -> "MemoryRevisionBuilder":
        """Set a brief description of the changes."""
        self._change_summary = summary
        return self
    
    def add_semantic_change(self, path: str, old_value: Any, new_value: Any) -> "MemoryRevisionBuilder":
        """Record a semantic change at a specific path."""
        self._semantic_changes[path] = {
            "old": old_value,
            "new": new_value,
        }
        return self
    
    def set_validation_status(self, status: str) -> "MemoryRevisionBuilder":
        """Set validation status (valid/invalid/unvalidated)."""
        self._validation_status = status
        return self
    
    def set_validation_result(self, result: str) -> "MemoryRevisionBuilder":
        """Set the validation result details."""
        self._validation_result = result
        return self
    
    def add_provenance_source(
        self,
        source_type: str,
        source_location: str,
        confidence: float = 1.0,
    ) -> "MemoryRevisionBuilder":
        """Add a provenance source."""
        self._provenance = self._provenance.add_source(
            MemoryProvenanceSource(source_type, source_location, confidence)
        )
        return self
    
    def set_created_at(self, timestamp_utc: float) -> "MemoryRevisionBuilder":
        """Set creation timestamp."""
        self._created_at_utc = timestamp_utc
        return self
    
    def set_changed_by(self, changer: str) -> "MemoryRevisionBuilder":
        """Set who made the change."""
        self._changed_by = changer
        return self
    
    def build(self) -> MemoryRevision:
        """
        Build an immutable MemoryRevision.
        
        Returns:
            New MemoryRevision with all settings applied
        """
        # Update provenance if changed_by is set
        provenance = self._provenance
        if self._changed_by:
            provenance = provenance.with_changed_by(self._changed_by)
            provenance = provenance.with_change_reason(str(self._change_reason.value))
        
        return MemoryRevision(
            revision_identity=self._revision_identity,
            previous_revision_id=self._previous_revision_id,
            change_reason=self._change_reason,
            change_summary=self._change_summary,
            semantic_changes=dict(self._semantic_changes),
            validation_status=self._validation_status,
            validation_result=self._validation_result,
            provenance=provenance,
            created_at_utc=self._created_at_utc,
            effective_from_utc=self._effective_from_utc,
            changed_by=self._changed_by,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(instance: MemoryRevision, **kwargs) -> MemoryRevision:
    """Replace fields in a frozen dataclass."""
    return MemoryRevision(
        revision_identity=instance.revision_identity,
        previous_revision_id=kwargs.get("previous_revision_id", instance.previous_revision_id),
        change_reason=kwargs.get("change_reason", instance.change_reason),
        change_summary=kwargs.get("change_summary", instance.change_summary),
        semantic_changes=dict(instance.semantic_changes) if "semantic_changes" not in kwargs else kwargs["semantic_changes"],
        validation_status=kwargs.get("validation_status", instance.validation_status),
        validation_result=kwargs.get("validation_result", instance.validation_result),
        provenance=kwargs.get("provenance", instance.provenance),
        created_at_utc=kwargs.get("created_at_utc", instance.created_at_utc),
        effective_from_utc=kwargs.get("effective_from_utc", instance.effective_from_utc),
        changed_by=kwargs.get("changed_by", instance.changed_by),
    )


def dataclass_replace_lineage(instance: RevisionLineage, **kwargs) -> RevisionLineage:
    """Replace fields in a frozen RevisionLineage."""
    return RevisionLineage(
        revision_ids=kwargs.get("revision_ids", instance.revision_ids),
        current_revision_id=kwargs.get("current_revision_id", instance.current_revision_id),
        total_revisions=kwargs.get("total_revisions", instance.total_revisions),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MemoryRevision",
    "MemoryRevisionChangeReason",
    "RevisionLineage",
    "MemoryRevisionBuilder",
    "dataclass_replace",
    "dataclass_replace_lineage",
]