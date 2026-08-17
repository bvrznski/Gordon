# Perception Scene Projection - Phase 5.2.4
# ==========================================

"""
Scene Projection: Exposes one or more perceptual Scenes.

A Scene Projection exposes one or more perceptual Scenes.
It may include participating Percepts, structural relations,
temporal extent, spatial reference frames, modality participation,
active Events, conflicts, ambiguity, missing evidence,
scene confidence, scene uncertainty.

A Scene Projection remains observational. It does not become a World Model.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import uuid


# =============================================================================
# PROJECTED SCENE STRUCTURE
# =============================================================================


@dataclass(frozen=True)
class ProjectedSceneStructure:
    """
    The structural representation of a projected Scene.
    
    Projection shaping may simplify the structure. It shall not invent missing
    relations.
    """
    
    structure_identity: str
    
    # Hierarchy
    root_structures: Tuple[str, ...] = field(default_factory=tuple)
    child_structures: Dict[str, Tuple[str, ...]] = field(default_factory=dict)  # parent -> children
    
    # Percept membership (per structural element)
    percept_membership: Dict[str, Tuple[str, ...]] = field(
        default_factory=dict
    )  # structure ID -> percept IDs
    
    # Relations
    spatial_relations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)     # e.g., "above", "beside"
    topological_relations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # connectivity
    hierarchical_relations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # containment
    
    # Temporal relations (when elements are part of a dynamic scene)
    temporal_relations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Occlusion
    occlusion_relations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Unresolved/unknown relations
    unresolved_relations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def create(
        cls,
        root_ids: List[str],
        percept_map: Optional[Dict[str, List[str]]] = None,
    ) -> "ProjectedSceneStructure":
        """
        Create a new scene structure projection.
        
        Args:
            root_ids: IDs of root structures (top-level elements)
            percept_map: Mapping of structure ID to contained percept IDs
            
        Returns:
            New ProjectedSceneStructure instance
        """
        return cls(
            structure_identity=f"scene_structure:{uuid.uuid4().hex[:16]}",
            root_structures=tuple(root_ids),
            percept_membership={
                k: tuple(v) for k, v in (percept_map or {}).items()
            },
        )


# =============================================================================
# SCENE PROJECTION
# =============================================================================


@dataclass(frozen=True)
class SceneProjection:
    """
    Projection of one or more perceptual Scenes.
    
    A Scene Projection exposes observational Scene structures only. It does not
    become a World Model.
    
    Fields:
        projection_identity:      Unique identifier for this projection
        source_scenes:            IDs of source scenes used
        projected_scene_structure: The structural representation
        participating_percepts:   Percepts in the scene
        structural_relations:     Relations between structures
        temporal_extent:          Time span covered
        spatial_reference_frames: Reference frames used
        participating_modalities: Modalities that contributed
        active_events:            Events observed in this scene
        conflicts:                Conflicting interpretations
        ambiguities:              Ambiguous interpretations
        missing_evidence:         Missing evidence records
        confidence:               Overall projection confidence
        uncertainty:              Overall projection uncertainty
        limitations:              Limitations affecting view
        freshness_state:          How current is the projection
        revision:                 Projection revision number
    """
    
    projection_identity: str
    
    # Source references
    source_scenes: Tuple[str, ...] = field(default_factory=tuple)
    
    # Structural representation
    projected_scene_structure: Optional[ProjectedSceneStructure] = None
    
    # Content
    participating_percepts: Tuple[str, ...] = field(default_factory=tuple)
    
    structural_relations: Tuple[Dict[str, Any], ...] = field(
        default_factory=tuple
    )
    
    temporal_extent: Dict[str, float] = field(
        default_factory=lambda: {"start": 0.0, "end": _time.time()}
    )  # start/end timestamps
    
    spatial_reference_frames: Tuple[str, ...] = field(default_factory=tuple)  # frame IDs
    
    participating_modalities: Tuple[str, ...] = field(default_factory=tuple)
    
    active_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    conflicts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    ambiguities: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    missing_evidence: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Quality metrics
    scene_confidence: float = 1.0
    scene_uncertainty: float = 0.0
    
    # Limitations
    limitations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Freshness and revision
    freshness_state: str = "current"
    freshness_timestamp_utc: float = field(default_factory=_time.time)
    source_revision_reference: Optional[str] = None
    projection_revision: int = 1
    
    @classmethod
    def create(
        cls,
        scene_ids: List[str],
        structure: Optional[ProjectedSceneStructure] = None,
        percept_ids: Optional[List[str]] = None,
        modalities: Optional[List[str]] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "SceneProjection":
        """
        Create a new Scene Projection.
        
        Args:
            scene_ids: IDs of source scenes
            structure: Structural representation (optional)
            percept_ids: Percepts in the scene
            modalities: Modalities that contributed
            confidence: Overall projection confidence (0.0-1.0)
            uncertainty: Overall projection uncertainty (0.0-1.0)
            
        Returns:
            New SceneProjection instance
        """
        return cls(
            projection_identity=f"scene_projection:{uuid.uuid4().hex[:24]}",
            source_scenes=tuple(scene_ids),
            projected_scene_structure=structure,
            participating_percepts=tuple(percept_ids or []),
            participating_modalities=tuple(modalities or []),
            scene_confidence=confidence,
            scene_uncertainty=uncertainty,
        )
    
    @classmethod
    def from_physical_evidence(
        cls,
        object_ids: List[str],
        spatial_relations: List[Dict[str, Any]],
        modalities: Optional[List[str]] = None,
        confidence: float = 0.85,
    ) -> "SceneProjection":
        """
        Create a Scene Projection from physical evidence.
        
        Args:
            object_ids: Identified objects
            spatial_relations: Relations between objects
            modalities: Modalities that observed these
            confidence: Confidence in the scene
            
        Returns:
            New SceneProjection representing physical scene
        """
        return cls(
            projection_identity=f"scene_projection:{uuid.uuid4().hex[:24]}",
            participating_percepts=tuple(object_ids),
            structural_relations=tuple(spatial_relations),
            participating_modalities=tuple(modalities or []),
            scene_confidence=confidence,
            scene_uncertainty=1.0 - confidence,
        )
    
    @classmethod
    def from_digital_evidence(
        cls,
        application_ids: List[str],
        hierarchical_relations: List[Dict[str, Any]],
        modalities: Optional[List[str]] = None,
        confidence: float = 0.85,
    ) -> "SceneProjection":
        """
        Create a Scene Projection from digital evidence.
        
        Args:
            application_ids: Applications/windows/tabs
            hierarchical_relations: Application hierarchy relations
            modalities: Modalities that observed these
            confidence: Confidence in the scene
            
        Returns:
            New SceneProjection representing digital scene
        """
        return cls(
            projection_identity=f"scene_projection:{uuid.uuid4().hex[:24]}",
            participating_percepts=tuple(application_ids),
            structural_relations=(),
            hierarchical_relations=tuple(hierarchical_relations),
            participating_modalities=tuple(modalities or []),
            scene_confidence=confidence,
            scene_uncertainty=1.0 - confidence,
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if the projection has valid data."""
        if not self.projection_identity or len(self.projection_identity) == 0:
            return False
        if not (0.0 <= self.scene_confidence <= 1.0):
            return False
        if not (0.0 <= self.scene_uncertainty <= 1.0):
            return False
        
        # At least one scene or percept is required for non-empty projections
        if len(self.source_scenes) == 0 and len(self.participating_percepts) == 0:
            # Empty projection is valid for "no scenes" case
            return True
        
        return True


# =============================================================================
# PROJECTION BUILDER
# =============================================================================


class SceneProjectionBuilder:
    """Mutable builder for constructing scene projections."""
    
    def __init__(self):
        self._projection_identity: str = f"scene_projection:{uuid.uuid4().hex[:24]}"
        self._source_scenes: List[str] = []
        self._structure: Optional[ProjectedSceneStructure] = None
        self._percepts: List[str] = []
        self._spatial_relations: List[Dict[str, Any]] = []
        self._topological_relations: List[Dict[str, Any]] = []
        self._hierarchical_relations: List[Dict[str, Any]] = []
        self._temporal_extent: Dict[str, float] = {"start": 0.0, "end": _time.time()}
        self._spatial_reference_frames: List[str] = []
        self._modalities: List[str] = []
        self._active_events: List[Dict[str, Any]] = []
        self._conflicts: List[Dict[str, Any]] = []
        self._ambiguities: List[Dict[str, Any]] = []
        self._missing_evidence: List[Dict[str, Any]] = []
        self._limitations: List[Dict[str, Any]] = []
        self._confidence: float = 1.0
        self._uncertainty: float = 0.0
    
    def set_identity(self, identity: str) -> "SceneProjectionBuilder":
        """Set the projection identity."""
        self._projection_identity = identity
        return self
    
    def add_source_scene(self, scene_id: str) -> "SceneProjectionBuilder":
        """Add a source scene ID."""
        if scene_id not in self._source_scenes:
            self._source_scenes.append(scene_id)
        return self
    
    def set_structure(
        self,
        structure: ProjectedSceneStructure,
    ) -> "SceneProjectionBuilder":
        """Set the structural representation."""
        self._structure = structure
        return self
    
    def add_percept(self, percept_id: str) -> "SceneProjectionBuilder":
        """Add a participating percept ID."""
        if percept_id not in self._percepts:
            self._percepts.append(percept_id)
        return self
    
    def add_spatial_relation(
        self,
        relation: Dict[str, Any],
    ) -> "SceneProjectionBuilder":
        """Add a spatial relation between structures."""
        self._spatial_relations.append(dict(relation))
        return self
    
    def add_topological_relation(
        self,
        relation: Dict[str, Any],
    ) -> "SceneProjectionBuilder":
        """Add a topological (connectivity) relation."""
        self._topological_relations.append(dict(relation))
        return self
    
    def add_hierarchical_relation(
        self,
        relation: Dict[str, Any],
    ) -> "SceneProjectionBuilder":
        """Add a hierarchical relation."""
        self._hierarchical_relations.append(dict(relation))
        return self
    
    def set_temporal_extent(
        self,
        start_time: float,
        end_time: float,
    ) -> "SceneProjectionBuilder":
        """Set temporal extent of the scene."""
        self._temporal_extent = {"start": start_time, "end": end_time}
        return self
    
    def add_spatial_reference_frame(self, frame_id: str) -> "SceneProjectionBuilder":
        """Add a spatial reference frame used in this projection."""
        if frame_id not in self._spatial_reference_frames:
            self._spatial_reference_frames.append(frame_id)
        return self
    
    def add_modality(self, modality_id: str) -> "SceneProjectionBuilder":
        """Add a contributing modality."""
        if modality_id not in self._modalities:
            self._modalities.append(modality_id)
        return self
    
    def add_active_event(
        self,
        event_data: Dict[str, Any],
    ) -> "SceneProjectionBuilder":
        """Add an active event observed in this scene."""
        self._active_events.append(dict(event_data))
        return self
    
    def add_conflict(self, conflict: Dict[str, Any]) -> "SceneProjectionBuilder":
        """Add a conflicting interpretation."""
        self._conflicts.append(dict(conflict))
        return self
    
    def add_ambiguity(self, ambiguity: Dict[str, Any]) -> "SceneProjectionBuilder":
        """Add an ambiguous interpretation."""
        self._ambiguities.append(dict(ambiguity))
        return self
    
    def add_missing_evidence(
        self,
        evidence_record: Dict[str, Any],
    ) -> "SceneProjectionBuilder":
        """Add a missing evidence record."""
        self._missing_evidence.append(dict(evidence_record))
        return self
    
    def add_limitation(
        self,
        limitation: Dict[str, Any],
    ) -> "SceneProjectionBuilder":
        """Add a limitation affecting this projection."""
        self._limitations.append(dict(limitation))
        return self
    
    def set_confidence(self, confidence: float) -> "SceneProjectionBuilder":
        """Set overall projection confidence (0.0-1.0)."""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {confidence}")
        self._confidence = confidence
        return self
    
    def set_uncertainty(self, uncertainty: float) -> "SceneProjectionBuilder":
        """Set overall projection uncertainty (0.0-1.0)."""
        if not 0.0 <= uncertainty <= 1.0:
            raise ValueError(f"Uncertainty must be 0.0-1.0, got {uncertainty}")
        self._uncertainty = uncertainty
        return self
    
    def set_freshness(self, state: str) -> "SceneProjectionBuilder":
        """Set freshness state (current, recent, stale, expired)."""
        valid_states = ("current", "recent", "stale", "expired")
        if state not in valid_states:
            raise ValueError(f"Invalid freshness state: {state}")
        self._freshness_state = state
        return self
    
    def build(self) -> SceneProjection:
        """Build an immutable SceneProjection."""
        if len(self._source_scenes) == 0 and len(self._percepts) == 0:
            raise ValueError("At least one scene or percept is required")
        
        return SceneProjection(
            projection_identity=self._projection_identity,
            source_scenes=tuple(self._source_scenes),
            projected_scene_structure=self._structure,
            participating_percepts=tuple(self._percepts),
            structural_relations=tuple(dict(r) for r in self._spatial_relations),
            temporal_extent=dict(self._temporal_extent),
            spatial_reference_frames=tuple(self._spatial_reference_frames),
            participating_modalities=tuple(self._modalities),
            active_events=tuple(dict(e) for e in self._active_events),
            conflicts=tuple(dict(c) for c in self._conflicts),
            ambiguities=tuple(dict(a) for a in self._ambiguities),
            missing_evidence=tuple(dict(m) for m in self._missing_evidence),
            limitations=tuple(dict(l) for l in self._limitations),
            scene_confidence=self._confidence,
            scene_uncertainty=self._uncertainty,
        )


__all__ = [
    "ProjectedSceneStructure",
    "SceneProjection",
    "SceneProjectionBuilder",
]