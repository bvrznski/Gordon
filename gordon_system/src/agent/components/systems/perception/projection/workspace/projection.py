# Perception Workspace Projection - Phase 5.2.4
# =============================================

"""
Workspace Projection: Exposes a bounded perceptual view for Workspace Network.

A Workspace Projection exposes a bounded perceptual view suitable for admission
into the Workspace Network. It may include currently relevant Percepts, active
Scene fragment, active Events, recent changes, conflicts, ambiguity, missing
evidence, modality availability, confidence, uncertainty.

The Workspace Projection does not own Workspace state. It produces a candidate
Workspace-facing perceptual representation.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import uuid


# =============================================================================
# WORKSPACE PERCEPTION CHANGE SET
# =============================================================================


@dataclass(frozen=True)
class WorkspacePerceptionChangeSet:
    """
    Set of changes between Workspace projection versions.
    
    Removal from the Workspace-facing view shall not imply perceptual deletion.
    
    Fields:
        base_projection_reference: ID of the previous projection version
        added_percepts: New percepts in this view
        updated_percepts: Percepts with changed content
        removed_from_view_percepts: Percepts no longer in view
        added_events: New events in this view
        updated_events: Events with changed content
        completed_events: Events that have ended
        scene_changes: Scene structure changes
        new_conflicts: Newly detected conflicts
        changed_conflicts: Conflicts with updated status
        missing_evidence_changes: Missing evidence updates
        modality_availability_changes: Modality availability updates
        confidence_changes: Confidence level changes
        uncertainty_changes: Uncertainty level changes
    """
    
    change_set_identity: str
    
    # Base reference
    base_projection_reference: Optional[str] = None
    
    # Percept changes
    added_percepts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    updated_percepts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    removed_from_view_percepts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Event changes
    added_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    updated_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    completed_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Scene changes
    scene_changes: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Conflict/ambiguity/missing evidence changes
    new_conflicts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    changed_conflicts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    missing_evidence_changes: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Modality availability
    modality_availability_changes: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Quality changes
    confidence_changes: Tuple[float, ...] = field(default_factory=tuple)
    uncertainty_changes: Tuple[float, ...] = field(default_factory=tuple)


# =============================================================================
# WORKSPACE PERCEPTION PROJECTION
# =============================================================================


@dataclass(frozen=True)
class WorkspacePerceptionProjection:
    """
    Candidate perceptual representation for Workspace admission.
    
    Workspace admission, capacity management and broadcasting remain owned by the
    Workspace Network. This projection produces a bounded candidate view.
    
    Fields:
        projection_identity:      Unique identifier for this projection
        source_artifacts:         IDs of all source artifacts
        active_percepts:          Currently relevant percepts
        active_scene:             Active Scene fragment (if any)
        active_events:            Active Events
        recent_changes:           Changes since last projection
        conflicts:                Conflicting interpretations
        ambiguities:              Ambiguous interpretations
        missing_evidence:         Missing evidence records
        modality_availability:    Available modalities
        confidence:               Overall projection confidence
        uncertainty:              Overall projection uncertainty
        limitations:              Limitations affecting view
        freshness_state:          How current is the projection
        revision:                 Projection revision number
    """
    
    projection_identity: str
    
    # Source references
    source_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    
    # Content (bounded by Workspace constraints)
    active_percepts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    active_scene: Optional[Dict[str, Any]] = None  # Scene structure
    active_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Recent changes (delta from previous view)
    recent_changes: Tuple[WorkspacePerceptionChangeSet, ...] = field(
        default_factory=tuple
    )
    
    # Conflict/ambiguity information
    conflicts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    ambiguities: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    missing_evidence: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Modality availability
    modality_availability: Dict[str, Dict[str, Any]] = field(
        default_factory=dict
    )  # modality_id -> {available, health, confidence}
    
    # Quality metrics
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    # Limitations (including capacity constraints)
    limitations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Freshness and revision
    freshness_state: str = "current"
    freshness_timestamp_utc: float = field(default_factory=_time.time)
    source_revision_reference: Optional[str] = None
    projection_revision: int = 1
    
    @classmethod
    def create(
        cls,
        percept_data: List[Dict[str, Any]],
        event_data: Optional[List[Dict[str, Any]]] = None,
        scene_data: Optional[Dict[str, Any]] = None,
        modalities: Optional[Dict[str, Dict[str, Any]]] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "WorkspacePerceptionProjection":
        """
        Create a new Workspace Projection.
        
        Args:
            percept_data: Active percepts for this view
            event_data: Active events (optional)
            scene_data: Active scene structure (optional)
            modalities: Modality availability map
            confidence: Overall projection confidence (0.0-1.0)
            uncertainty: Overall projection uncertainty (0.0-1.0)
            
        Returns:
            New WorkspacePerceptionProjection instance
        """
        return cls(
            projection_identity=f"workspace_projection:{uuid.uuid4().hex[:24]}",
            active_percepts=tuple(percept_data),
            active_scene=scene_data,
            active_events=tuple(event_data or []),
            modality_availability=dict(modalities or {}),
            confidence=confidence,
            uncertainty=uncertainty,
        )
    
    @classmethod
    def bounded(
        cls,
        percept_data: List[Dict[str, Any]],
        max_count: int,
        max_size_bytes: Optional[int] = None,
    ) -> "WorkspacePerceptionProjection":
        """
        Create a Workspace Projection with bounded representation.
        
        Args:
            percept_data: Available percepts
            max_count: Maximum number of percepts to include
            max_size_bytes: Maximum total size in bytes (optional)
            
        Returns:
            New WorkspacePerceptionProjection with capacity constraints
        """
        # Apply bounds (simplified: take first N)
        limited_percepts = percept_data[:max_count]
        
        limitations = []
        if len(percept_data) > max_count:
            limitations.append({
                "kind": "artifact_count_limit",
                "exceeded_by": len(percept_data) - max_count,
            })
        
        return cls(
            projection_identity=f"workspace_projection:{uuid.uuid4().hex[:24]}",
            active_percepts=tuple(limited_percepts),
            limitations=tuple(limitations),
            confidence=0.95,  # Slightly reduced due to truncation
            uncertainty=0.05,
        )
    
    @classmethod
    def from_source(
        cls,
        source_artifact_ids: List[str],
        active_percept_data: List[Dict[str, Any]],
        active_events: Optional[List[Dict[str, Any]]] = None,
        recent_change_set: Optional[WorkspacePerceptionChangeSet] = None,
    ) -> "WorkspacePerceptionProjection":
        """
        Create a Workspace Projection from source artifacts.
        
        Args:
            source_artifact_ids: All source artifact IDs
            active_percept_data: Active percepts
            active_events: Active events (optional)
            recent_change_set: Changes since last projection (optional)
            
        Returns:
            New WorkspacePerceptionProjection
        """
        changes = []
        if recent_change_set:
            changes.append(recent_change_set)
        
        return cls(
            projection_identity=f"workspace_projection:{uuid.uuid4().hex[:24]}",
            source_artifacts=tuple(source_artifact_ids),
            active_percepts=tuple(active_percept_data),
            active_events=tuple(active_events or []),
            recent_changes=tuple(changes),
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if the projection has valid data."""
        if not self.projection_identity or len(self.projection_identity) == 0:
            return False
        if not (0.0 <= self.confidence <= 1.0):
            return False
        if not (0.0 <= self.uncertainty <= 1.0):
            return False
        
        # At least one active percept or event is required for non-empty projections
        if len(self.active_percepts) == 0 and len(self.active_events) == 0:
            # Empty projection is valid for "no content" case
            return True
        
        return True


__all__ = [
    "WorkspacePerceptionChangeSet",
    "WorkspacePerceptionProjection",
]