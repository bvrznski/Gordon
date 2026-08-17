# Perception Snapshot Projection - Phase 5.2.4
# ============================================

"""
Snapshot Projection: Captures one immutable perceptual view at a specific revision.

A Snapshot Projection captures one immutable perceptual view at a specific semantic
revision. Snapshots remain stable even when Perception continues evolving.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import uuid


# =============================================================================
# SNAPSHOT PROJECTION
# =============================================================================


@dataclass(frozen=True)
class PerceptionSnapshotProjection:
    """
    Immutable snapshot of a perceptual view at a specific revision.
    
    A Snapshot captures one stable semantic view. It remains stable even when
    Perception continues evolving.
    
    Fields:
        snapshot_identity:     Unique identifier for this snapshot
        projection_kind:       Kind of projection captured (percept, scene, event)
        source_revision:       Source artifact revisions at time of capture
        temporal_scope:        Temporal boundaries
        spatial_scope:         Spatial boundaries
        included_artifacts:    Artifact IDs in this snapshot
        excluded_summary:      Summary of what was excluded
        confidence:            Confidence level at time of snapshot
        uncertainty:           Uncertainty at time of snapshot
        limitations:           Limitations affecting the view
        provenance:            How and why this snapshot was created
    """
    
    snapshot_identity: str
    
    # Snapshot metadata
    projection_kind: str  # percept, scene, event, workspace
    generation_revision: int = 1
    
    # Source information
    source_revisions: Dict[str, int] = field(default_factory=dict)  # artifact_id -> revision
    generation_timestamp_utc: float = field(default_factory=_time.time)
    
    # Scope (for context)
    temporal_scope: Optional[Dict[str, Any]] = None
    spatial_scope: Optional[Dict[str, Any]] = None
    
    # Content
    included_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    excluded_artifact_summary: Dict[str, int] = field(
        default_factory=dict
    )  # reason -> count
    
    # Quality metrics
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    # Limitations
    limitations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def create(
        cls,
        projection_kind: str,
        artifact_ids: List[str],
        source_revisions: Optional[Dict[str, int]] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "PerceptionSnapshotProjection":
        """
        Create a new Snapshot Projection.
        
        Args:
            projection_kind: Kind of projection (percept, scene, event)
            artifact_ids: IDs of included artifacts
            source_revisions: Source artifact revisions at time of snapshot
            confidence: Confidence level (0.0-1.0)
            uncertainty: Uncertainty level (0.0-1.0)
            
        Returns:
            New PerceptionSnapshotProjection instance
        """
        return cls(
            snapshot_identity=f"snapshot:{uuid.uuid4().hex[:24]}",
            projection_kind=projection_kind,
            source_revisions=dict(source_revisions or {}),
            included_artifacts=tuple(artifact_ids),
            confidence=confidence,
            uncertainty=uncertainty,
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if the snapshot has valid data."""
        if not self.snapshot_identity or len(self.snapshot_identity) == 0:
            return False
        if not self.projection_kind or len(self.projection_kind) == 0:
            return False
        if not (0.0 <= self.confidence <= 1.0):
            return False
        if not (0.0 <= self.uncertainty <= 1.0):
            return False
        
        # At least one artifact for non-empty snapshots
        if len(self.included_artifacts) == 0:
            return True  # Empty snapshot is valid for "no content" case
        
        return True


__all__ = ["PerceptionSnapshotProjection"]