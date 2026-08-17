# Knowledge Relation Descriptor - Phase 6.5
# =========================================

"""
Relation Descriptor: Metadata and lifecycle management for Relations.

Relations are semantic connective structures in Gordon's knowledge system.
This module provides the descriptor contract for relation metadata including:
- Relation identity and revision tracking
- Lifecycle state progression
- Publication status
- Compatibility tracking

Every Relation shall derive from this canonical base contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# SEMANTIC LIFECYCLE STATES - Relation maturity progression
# =============================================================================


class RelationLifecycleState(Enum):
    """
    States of relation lifecycle progression.
    
    Defines the maturity states a relation transitions through:
        CREATED     -> Initial creation (not yet validated)
        DRAFT       -> Work-in-progress state
        VALIDATING  -> Under validation review
        CERTIFIED   -> Passed validation, ready for publication
        ACTIVE      -> Published and in use
        REVISED     -> Has been superseded by newer revision
        SUPERSEDED  -> Replaced by another relation
        DEPRECATED  -> Marked as outdated but still referenced
        ARCHIVED    -> Preserved for historical purposes
        INVALID     -> Failed validation, not for use
    """
    
    CREATED = "created"
    DRAFT = "draft"
    VALIDATING = "validating"
    CERTIFIED = "certified"
    ACTIVE = "active"
    REVISED = "revised"
    SUPERSEDED = "superseded"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    INVALID = "invalid"


# =============================================================================
# SEMANTIC PUBLICATION STATUS - Availability states
# =============================================================================


class RelationPublicationStatus(Enum):
    """
    Publication availability statuses.
    
    Defines the publication state of a relation:
        PRIVATE     -> Not available outside creator
        INTERNAL    -> Available within organization/system
        SHARED      -> Shared with selected external parties
        ACTIVE      -> Publicly available
        RESTRICTED  -> Available under specific conditions
        SUPERSEDED  -> Replaced by newer publication
    """
    
    PRIVATE = "private"
    INTERNAL = "internal"
    SHARED = "shared"
    ACTIVE = "active"
    RESTRICTED = "restricted"
    SUPERSEDED = "superseded"


# =============================================================================
# COMPATIBILITY KINDS - Revision interaction types
# =============================================================================


class RelationCompatibilityKind(Enum):
    """
    Kinds of compatibility between relation revisions.
    
    Defines how two revisions may interact:
        FULLY_COMPATIBLE      -> Can be used interchangeably
        BACKWARD_COMPATIBLE   -> Newer works with older consumers
        FORWARD_COMPATIBLE    -> Older works with newer consumers
        PARTIALLY_COMPATIBLE  -> Some operations work, others don't
        MIGRATION_REQUIRED    -> Requires explicit migration process
        INCOMPATIBLE          -> Cannot interact without breaking
    """
    
    FULLY_COMPATIBLE = "fully_compatible"
    BACKWARD_COMPATIBLE = "backward_compatible"
    FORWARD_COMPATIBLE = "forward_compatible"
    PARTIALLY_COMPATIBLE = "partially_compatible"
    MIGRATION_REQUIRED = "migration_required"
    INCOMPATIBLE = "incompatible"


# =============================================================================
# CERTIFICATION LEVELS - Quality assurance grades
# =============================================================================


class RelationCertificationLevel(Enum):
    """
    Levels of relation certification quality.
    
    Defines the implementation quality grade:
        UNCERTIFIED   -> Not yet certified
        PARTIAL       -> Some checks passed
        CERTIFIED     -> Passed all required checks
        VERIFIED      -> Verified by independent assessment
        REFERENCE     -> Reference standard quality
    """
    
    UNCERTIFIED = "uncertified"
    PARTIAL = "partial"
    CERTIFIED = "certified"
    VERIFIED = "verified"
    REFERENCE = "reference"


# =============================================================================
# RELATION DESCRIPTOR - Canonical metadata structure
# =============================================================================


@dataclass(frozen=True)
class RelationDescriptor:
    """
    Descriptor for a semantic relation in Gordon's knowledge system.
    
    Every Relation possesses this descriptor containing:
        - Unique identity and revision tracking
        - Lifecycle state progression
        - Publication availability status
        - Compatibility between revisions
    
    This descriptor is independent from the relation content itself,
    allowing metadata operations without full relation inspection.
    
    Fields:
        relation_identity:     Unique identifier for this relation
        semantic_version:      Semantic version string (e.g., "1.0.0")
        lifecycle_state:       Maturity progression state
        publication_status:    Availability status
        compatibility_revision: Current revision in compatibility chain
        certification_level:   Quality assurance grade
        created_at_utc:        Creation timestamp
        updated_at_utc:        Last update timestamp
        provenance:            Origin tracking records
    """
    
    # Identity and versioning (required)
    relation_identity: str                    # Unique ID for this relation
    
    semantic_version: str = "1.0.0"           # Semantic version string
    
    # Lifecycle management (required)
    lifecycle_state: RelationLifecycleState = RelationLifecycleState.CREATED
    publication_status: RelationPublicationStatus = RelationPublicationStatus.PRIVATE
    
    # Compatibility tracking (required)
    compatibility_revision: int = 1           # Current revision in chain
    
    # Quality assurance (optional with defaults)
    certification_level: RelationCertificationLevel = RelationCertificationLevel.UNCERTIFIED
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    # Provenance trail (immutable tuple)
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @property
    def is_valid(self) -> bool:
        """Check if descriptor has valid foundational data."""
        return (
            len(self.relation_identity) > 0 and
            self.lifecycle_state is not None and
            self.publication_status is not None
        )
    
    @property
    def version_tuple(self) -> Tuple[int, ...]:
        """Parse semantic version into tuple of integers."""
        try:
            parts = self.semantic_version.split('.')
            return tuple(int(p) for p in parts[:3])
        except (ValueError, AttributeError):
            return (1, 0, 0)
    
    @classmethod
    def create_initial(
        cls,
        relation_identity: str,
        provenance_context: Optional[Dict[str, Any]] = None,
    ) -> "RelationDescriptor":
        """
        Create an initial relation descriptor.
        
        Args:
            relation_identity: Unique identifier for the relation
            provenance_context: Initial provenance context (optional)
            
        Returns:
            New RelationDescriptor in CREATED state with PRIVATE publication
        """
        initial_provenance = (
            {
                "provenance_identity": f"relation-prov:{uuid.uuid4().hex[:16]}",
                "originating_request": provenance_context.get("request", "") if provenance_context else "",
                "originating_system": provenance_context.get("system", "unknown") if provenance_context else "unknown",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [],
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            relation_identity=relation_identity,
            semantic_version="1.0.0",
            lifecycle_state=RelationLifecycleState.CREATED,
            publication_status=RelationPublicationStatus.PRIVATE,
            compatibility_revision=1,
            provenance=initial_provenance,
        )
    
    def with_revision(
        self,
        new_revision: int,
        change_summary: Optional[str] = None,
    ) -> "RelationDescriptor":
        """
        Create a new revision of this descriptor.
        
        Args:
            new_revision: The revision number
            change_summary: Brief description of changes (optional)
            
        Returns:
            New descriptor instance with updated revision
        """
        new_provenance = tuple(list(self.provenance) + [{
            "provenance_identity": f"relation-prov:{uuid.uuid4().hex[:16]}",
            "originating_request": f"Revision {new_revision}: {change_summary or 'unknown change'}",
            "originating_system": self.provenance[0].get("originating_system", "system") if self.provenance else "system",
            "originating_revision": new_revision,
            "evidence_references": [],
            "grounding_references": [],
            "revision_chain": [self.relation_identity],
            "timestamp_utc": time.time(),
        }])
        
        return RelationDescriptor(
            relation_identity=self.relation_identity,
            semantic_version=f"{self.version_tuple[0]}.{self.version_tuple[1]}.{new_revision}",
            lifecycle_state=RelationLifecycleState.ACTIVE if self.lifecycle_state == RelationLifecycleState.CREATED else self.lifecycle_state,
            publication_status=self.publication_status,
            compatibility_revision=new_revision,
            certification_level=self.certification_level,
            provenance=new_provenance,
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert descriptor to dictionary for serialization."""
        return {
            "relation_identity": self.relation_identity,
            "semantic_version": self.semantic_version,
            "lifecycle_state": self.lifecycle_state.value,
            "publication_status": self.publication_status.value,
            "compatibility_revision": self.compatibility_revision,
            "certification_level": self.certification_level.value,
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
            "provenance": [p for p in self.provenance],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelationDescriptor":
        """Create descriptor from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        try:
            lifecycle_state = RelationLifecycleState(data.get("lifecycle_state", "created"))
        except ValueError:
            lifecycle_state = RelationLifecycleState.CREATED
        
        try:
            publication_status = RelationPublicationStatus(data.get("publication_status", "private"))
        except ValueError:
            publication_status = RelationPublicationStatus.PRIVATE
        
        try:
            certification_level = RelationCertificationLevel(data.get("certification_level", "uncertified"))
        except ValueError:
            certification_level = RelationCertificationLevel.UNCERTIFIED
        
        return cls(
            relation_identity=data.get("relation_identity", str(uuid.uuid4())),
            semantic_version=data.get("semantic_version", "1.0.0"),
            lifecycle_state=lifecycle_state,
            publication_status=publication_status,
            compatibility_revision=int(data.get("compatibility_revision", 1)),
            certification_level=certification_level,
            provenance=tuple(provenance),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )


__all__ = [
    # Lifecycle states
    "RelationLifecycleState",
    # Publication statuses
    "RelationPublicationStatus",
    # Compatibility kinds
    "RelationCompatibilityKind",
    # Certification levels
    "RelationCertificationLevel",
    # Descriptor
    "RelationDescriptor",
]