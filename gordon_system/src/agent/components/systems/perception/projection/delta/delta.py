# Perception Delta Projection - Phase 5.2.4
# =========================================

"""
Delta Projection: Communicates changes relative to a prior projection.

An Incremental Projection communicates changes relative to a prior projection.
Deltas preserve revision continuity and provide efficient incremental updates.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import uuid


# =============================================================================
# DELTA PROJECTION
# =============================================================================


@dataclass(frozen=True)
class PerceptionProjectionDelta:
    """
    Delta representing changes between projection revisions.
    
    A delta identifies what changed between the base revision and target revision,
    including added, updated, and removed artifacts.
    
    Fields:
        delta_identity:           Unique identifier for this delta
        base_projection_id:       ID of the base projection version
        base_revision:            Revision number of base projection
        target_revision:          Target revision number
        added_artifacts:          New artifacts in target
        updated_artifacts:        Changed artifacts (same ID, different content)
        removed_from_view_artifacts: Artifacts no longer in view
        confidence_changes:       Confidence level changes per artifact
        uncertainty_changes:      Uncertainty level changes per artifact
        provenance:               How and why this delta was created
    """
    
    delta_identity: str
    
    # Revision tracking
    base_projection_id: Optional[str] = None
    base_revision: int = 1
    target_revision: int = 2
    
    # Content changes
    added_artifacts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    updated_artifacts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    removed_from_view_artifacts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Quality changes
    confidence_changes: Dict[str, float] = field(default_factory=dict)  # artifact_id -> delta
    uncertainty_changes: Dict[str, float] = field(default_factory=dict)  # artifact_id -> delta
    
    @classmethod
    def create(
        cls,
        base_projection_id: str,
        base_revision: int,
        target_revision: int,
        added_artifacts: Optional[List[Dict[str, Any]]] = None,
        updated_artifacts: Optional[List[Dict[str, Any]]] = None,
        removed_artifacts: Optional[List[Dict[str, Any]]] = None,
    ) -> "PerceptionProjectionDelta":
        """
        Create a new Delta Projection.
        
        Args:
            base_projection_id: ID of the previous projection version
            base_revision: Revision number of previous view
            target_revision: Target revision number
            added_artifacts: New artifacts since last view
            updated_artifacts: Changed artifacts
            removed_artifacts: Artifacts no longer in view
            
        Returns:
            New PerceptionProjectionDelta instance
        """
        return cls(
            delta_identity=f"delta:{uuid.uuid4().hex[:24]}",
            base_projection_id=base_projection_id,
            base_revision=base_revision,
            target_revision=target_revision,
            added_artifacts=tuple(added_artifacts or []),
            updated_artifacts=tuple(updated_artifacts or []),
            removed_from_view_artifacts=tuple(removed_artifacts or []),
        )
    
    @classmethod
    def from_snapshot_delta(
        cls,
        snapshot: Dict[str, Any],
        previous_snapshot: Optional[Dict[str, Any]] = None,
    ) -> "PerceptionProjectionDelta":
        """
        Create a delta by comparing two snapshots.
        
        Args:
            snapshot: Current snapshot
            previous_snapshot: Previous snapshot (if any)
            
        Returns:
            New PerceptionProjectionDelta representing changes
        """
        if not previous_snapshot:
            return cls(
                delta_identity=f"delta:{uuid.uuid4().hex[:24]}",
                base_revision=0,
                target_revision=1,
                added_artifacts=tuple(snapshot.get("included_artifacts", [])),
            )
        
        # Calculate differences (simplified)
        current_ids = set(a.get("artifact_id") for a in snapshot.get("included_artifacts", []))
        previous_ids = set(a.get("artifact_id") for a in previous_snapshot.get("included_artifacts", []))
        
        added = list(current_ids - previous_ids)
        removed = list(previous_ids - current_ids)
        
        return cls(
            delta_identity=f"delta:{uuid.uuid4().hex[:24]}",
            base_projection_id=previous_snapshot.get("snapshot_identity"),
            base_revision=previous_snapshot.get("generation_revision", 1),
            target_revision=snapshot.get("generation_revision", 1),
            added_artifacts=tuple({"artifact_id": a} for a in added),
            removed_from_view_artifacts=tuple({"artifact_id": r} for r in removed),
        )
    
    @property
    def is_empty(self) -> bool:
        """Check if this delta represents no changes."""
        return (
            len(self.added_artifacts) == 0 and
            len(self.updated_artifacts) == 0 and
            len(self.removed_from_view_artifacts) == 0
        )
    
    @property
    def has_changes(self) -> bool:
        """Check if this delta represents any changes."""
        return not self.is_empty


__all__ = ["PerceptionProjectionDelta"]