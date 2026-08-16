# Memory Projection - Phase 5.1 Canonical Immutable View
# =======================================================

"""
Memory Projection: Immutable views over the memory substrate.

Consumers receive projections - never the substrate itself.
This maintains encapsulation and prevents direct mutation.

Projection Laws:
    PROJECTION-LAW-001: Projections are immutable
    PROJECTION-LAW-002: Projections expose semantic artifacts only
    PROJECTION-LAW-003: Projections never expose substrate internals
    PROJECTION-LAW-004: Projection revisions preserve lineage
    PROJECTION-LAW-005: Projection provenance is complete
    PROJECTION-LAW-006: Projection validation precedes publication
    PROJECTION-LAW-007: Projection consumers never mutate projections
    PROJECTION-LAW-008: Projection generation is deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# PROJECTION BOUNDARY - Scope definition
# =============================================================================


class ProjectionBoundary(Enum):
    """
    Types of boundaries for projections.
    
    | Boundary       | Description                                       |
    |----------------|--------------------------------------------------|
    | GLOBAL         | Entire substrate                                  |
    | ROOT_ARTIFACT  | Subgraph rooted at specific artifact             |
    | ARTIFACT_KIND  | All artifacts of a specific kind                 |
    | RELATION_TYPE  | Artifacts connected by specific relation         |
    | TIME_RANGE     | Artifacts created within time range              |
    | VALIDITY_STATE | Artifacts with specific validity status          |
    """
    
    GLOBAL = "global"
    ROOT_ARTIFACT = "root_artifact"
    ARTIFACT_KIND = "artifact_kind"
    RELATION_TYPE = "relation_type"
    TIME_RANGE = "time_range"
    VALIDITY_STATE = "validity_state"


# =============================================================================
# MEMORY PROJECTION - Immutable view over substrate
# =============================================================================


@dataclass(frozen=True)
class MemoryProjection:
    """
    Immutable projection of memory state at a point in time.
    
    A projection is a snapshot view that consumers can safely use without
    risk of mutation. The actual substrate remains unchanged.
    
    Fields:
        projection_identity: Unique ID for this projection record
        
        # Projection scope
        boundary:           What defines the projection's scope?
        boundary_value:     Value for boundary type (artifact_id, kind, etc.)
        
        # Content
        projected_artifacts: Tuple of artifact IDs included
        projected_revisions: Mapping of artifact -> revision info
        
        # Timestamps
        created_at_utc:     When this projection was generated
        semantic_time_utc:  What point in time does this represent?
        
        # Revision tracking
        revision_number:    Which projection in chain (1 = first)
        previous_projection_id: ID of prior projection (if any)
        
        # Validation
        validation_status:  Was this projection validated? ("valid", "invalid")
        
        # Provenance
        generated_by:       Who/what generated this projection?
        provenance:         How was it generated?
    """
    
    projection_identity: str              # Unique ID for this projection record
    
    # Projection scope
    boundary: ProjectionBoundary = ProjectionBoundary.GLOBAL
    boundary_value: Optional[str] = None  # Value depends on boundary type
    
    # Content - what's included in this view?
    projected_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    projected_revisions: Dict[str, int] = field(default_factory=dict)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    semantic_time_utc: float = field(default_factory=time.time)
    
    # Revision tracking
    revision_number: int = 1
    previous_projection_id: Optional[str] = None
    
    # Validation
    validation_status: str = "unvalidated"  # valid, invalid, unvalidated
    
    # Provenance
    generated_by: Optional[str] = None
    provenance: Optional[str] = None      # How was it generated?
    
    @property
    def projection_id(self) -> str:
        """Get the projection's unique ID."""
        return self.projection_identity
    
    @classmethod
    def create_for_artifact(
        cls,
        root_artifact_id: str,
        artifacts_in_scope: Tuple[str, ...],
        revisions: Dict[str, int],
        generated_by: Optional[str] = None,
    ) -> "MemoryProjection":
        """
        Create a projection for a specific artifact's subgraph.
        
        Args:
            root_artifact_id: The central artifact
            artifacts_in_scope: All related artifacts (including root)
            revisions: Mapping of artifact ID to revision number
            generated_by: Who generated this? (optional)
            
        Returns:
            New MemoryProjection with ROOT_ARTIFACT boundary
        """
        return cls(
            projection_identity=str(uuid.uuid4()),
            boundary=ProjectionBoundary.ROOT_ARTIFACT,
            boundary_value=root_artifact_id,
            projected_artifacts=artifacts_in_scope,
            projected_revisions=dict(revisions),
            revision_number=1,
            generated_by=generated_by,
            provenance=f"subgraph projection for artifact {root_artifact_id}",
        )
    
    @classmethod
    def create_global(
        cls,
        artifacts: Tuple[str, ...],
        revisions: Dict[str, int],
        generated_by: Optional[str] = None,
    ) -> "MemoryProjection":
        """
        Create a global projection (entire substrate).
        
        Args:
            artifacts: All artifact IDs in the substrate
            revisions: Mapping of artifact ID to revision number
            generated_by: Who generated this? (optional)
            
        Returns:
            New MemoryProjection with GLOBAL boundary
        """
        return cls(
            projection_identity=str(uuid.uuid4()),
            boundary=ProjectionBoundary.GLOBAL,
            projected_artifacts=artifacts,
            projected_revisions=dict(revisions),
            revision_number=1,
            generated_by=generated_by,
            provenance="global substrate projection",
        )
    
    def get_revision_for_artifact(self, artifact_id: str) -> int:
        """Get the revision number for an artifact in this projection."""
        return self.projected_revisions.get(artifact_id, 0)
    
    def has_artifact(self, artifact_id: str) -> bool:
        """Check if an artifact is included in this projection."""
        return artifact_id in self.projected_artifacts
    
    @property
    def artifact_count(self) -> int:
        """Count of artifacts in this projection."""
        return len(self.projected_artifacts)


# =============================================================================
# MEMORY SNAPSHOT - Immutable point-in-time view
# =============================================================================


@dataclass(frozen=True)
class MemorySnapshot:
    """
    Immutable snapshot of memory at a specific semantic time.
    
    Snapshots are for historical inspection - they can never be modified after
    creation. They're the ultimate source of truth for "what was known."
    
    Fields:
        snapshot_identity: Unique ID for this snapshot record
        
        # State
        projected_state:   Full state captured in this snapshot
        
        revision_number:   Which snapshot in chain (1 = first)
        
        # Timestamps
        semantic_time_utc: What point in time does this represent?
        created_at_utc:    When was the snapshot taken?
        
        # Provenance
        captured_by:       Who/what captured this state?
        provenance:        Why and how was it captured?
    """
    
    snapshot_identity: str                # Unique ID for this snapshot record
    
    # State
    projected_state: MemoryProjection     # What was captured?
    
    revision_number: int = 1              # Which snapshot in chain
    
    # Timestamps
    semantic_time_utc: float = field(default_factory=time.time)
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    captured_by: Optional[str] = None     # Who captured this?
    provenance: Optional[str] = None      # Why was it captured?


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace_projection(instance: MemoryProjection, **kwargs) -> MemoryProjection:
    """Replace fields in a frozen MemoryProjection."""
    return MemoryProjection(
        projection_identity=instance.projection_identity,
        boundary=kwargs.get("boundary", instance.boundary),
        boundary_value=kwargs.get("boundary_value", instance.boundary_value),
        projected_artifacts=kwargs.get("projected_artifacts", instance.projected_artifacts),
        projected_revisions=dict(instance.projected_revisions) if "projected_revisions" not in kwargs else kwargs["projected_revisions"],
        created_at_utc=kwargs.get("created_at_utc", instance.created_at_utc),
        semantic_time_utc=kwargs.get("semantic_time_utc", instance.semantic_time_utc),
        revision_number=kwargs.get("revision_number", instance.revision_number),
        previous_projection_id=kwargs.get("previous_projection_id", instance.previous_projection_id),
        validation_status=kwargs.get("validation_status", instance.validation_status),
        generated_by=kwargs.get("generated_by", instance.generated_by),
        provenance=kwargs.get("provenance", instance.provenance),
    )


def dataclass_replace_snapshot(instance: MemorySnapshot, **kwargs) -> MemorySnapshot:
    """Replace fields in a frozen MemorySnapshot."""
    return MemorySnapshot(
        snapshot_identity=instance.snapshot_identity,
        projected_state=kwargs.get("projected_state", instance.projected_state),
        revision_number=kwargs.get("revision_number", instance.revision_number),
        semantic_time_utc=kwargs.get("semantic_time_utc", instance.semantic_time_utc),
        created_at_utc=kwargs.get("created_at_utc", instance.created_at_utc),
        captured_by=kwargs.get("captured_by", instance.captured_by),
        provenance=kwargs.get("provenance", instance.provenance),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MemoryProjection",
    "ProjectionBoundary",
    "MemorySnapshot",
    "dataclass_replace_projection",
    "dataclass_replace_snapshot",
]