# Perception Projection Scope - Phase 5.2.4
# ==========================================

"""
Projection Scope: Defines what is included in a projection.

Every Projection shall possess an explicit scope that constrains what
perceptual artifacts are included in the published view.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import uuid


# =============================================================================
# TEMPORAL SCOPE
# =============================================================================


@dataclass(frozen=True)
class TemporalScope:
    """
    Defines the temporal boundaries of a projection.
    
    Temporal scope may specify:
        - current instant
        - recent interval
        - active session
        - event lifetime
        - sliding window
        - bounded history
        - since revision
        - until timestamp
        - semantic interval
    
    Original source timing shall remain inspectable.
    Projection shall not fabricate continuous coverage.
    """
    
    scope_identity: str
    
    # Time range
    start_time_utc: Optional[float] = None  # Unix timestamp, inclusive
    end_time_utc: Optional[float] = None    # Unix timestamp, exclusive
    
    # Scope kind
    temporal_kind: str = "interval"  # current, interval, window, session, history
    
    # Window configuration (for sliding windows)
    window_duration_seconds: float = 60.0
    slide_interval_seconds: float = 10.0
    
    # Semantic interpretation
    semantic_interval: Optional[str] = None  # e.g., "during_command_execution"
    
    @classmethod
    def current(cls) -> "TemporalScope":
        """Create a scope for the current instant."""
        now = _time.time()
        return cls(
            scope_identity=f"temporal:{uuid.uuid4().hex[:16]}",
            start_time_utc=now,
            end_time_utc=now,
            temporal_kind="current",
        )
    
    @classmethod
    def interval(
        cls,
        start_time: float,
        end_time: float,
    ) -> "TemporalScope":
        """Create a scope for a time interval."""
        return cls(
            scope_identity=f"temporal:{uuid.uuid4().hex[:16]}",
            start_time_utc=start_time,
            end_time_utc=end_time,
            temporal_kind="interval",
        )
    
    @classmethod
    def recent(cls, duration_seconds: float = 60.0) -> "TemporalScope":
        """Create a scope for recent events."""
        now = _time.time()
        return cls(
            scope_identity=f"temporal:{uuid.uuid4().hex[:16]}",
            start_time_utc=now - duration_seconds,
            end_time_utc=now,
            temporal_kind="window",
            window_duration_seconds=duration_seconds,
        )
    
    @classmethod
    def since(cls, timestamp: float) -> "TemporalScope":
        """Create a scope from a timestamp to now."""
        return cls(
            scope_identity=f"temporal:{uuid.uuid4().hex[:16]}",
            start_time_utc=timestamp,
            end_time_utc=_time.time(),
            temporal_kind="history",
        )
    
    @classmethod
    def session(cls, session_id: str) -> "TemporalScope":
        """Create a scope for a specific session."""
        return cls(
            scope_identity=f"temporal:{uuid.uuid4().hex[:16]}",
            temporal_kind="session",
            semantic_interval=session_id,
        )
    
    @classmethod
    def global_scope(cls) -> "TemporalScope":
        """Create a global temporal scope (no time restrictions)."""
        return cls(
            scope_identity=f"temporal:{uuid.uuid4().hex[:16]}",
            start_time_utc=0.0,
            end_time_utc=_time.time() + 365 * 24 * 3600,  # One year into future
            temporal_kind="interval",
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if the temporal scope has valid data."""
        if self.temporal_kind == "current":
            return True
        if self.temporal_kind == "interval":
            if self.start_time_utc is None or self.end_time_utc is None:
                return False
            return self.start_time_utc <= self.end_time_utc
        if self.temporal_kind in ("window", "history"):
            return self.window_duration_seconds > 0
        if self.temporal_kind == "session":
            return self.semantic_interval is not None and len(self.semantic_interval) > 0
        return False


# =============================================================================
# SPATIAL SCOPE
# =============================================================================


@dataclass(frozen=True)
class SpatialScope:
    """
    Defines the spatial boundaries of a projection.
    
    Spatial scope may specify:
        - physical region
        - screen region
        - window region
        - application hierarchy
        - filesystem subtree
        - process subtree
        - network namespace
        - container namespace
        - world-model region candidate
    
    Spatial scope may be Euclidean, topological, or hierarchical.
    These shall remain distinguishable.
    """
    
    scope_identity: str
    
    # Region definition
    region_type: str = "global"  # global, euclidean, topological, hierarchical
    
    # Euclidean coordinates (for physical space)
    min_coordinates: Optional[Tuple[float, float, float]] = None  # x, y, z
    max_coordinates: Optional[Tuple[float, float, float]] = None  # x, y, z
    
    # Screen/window region
    screen_region: Optional[Dict[str, Any]] = None
    
    # Application hierarchy
    application_paths: Tuple[str, ...] = field(default_factory=tuple)
    
    # Filesystem paths
    filesystem_paths: Tuple[str, ...] = field(default_factory=tuple)
    
    # Network namespace
    network_namespace: Optional[str] = None
    
    @classmethod
    def global_scope(cls) -> "SpatialScope":
        """Create a scope for all space."""
        return cls(
            scope_identity=f"spatial:{uuid.uuid4().hex[:16]}",
            region_type="global",
        )
    
    @classmethod
    def euclidean_region(
        cls,
        min_coords: Tuple[float, float, float],
        max_coords: Tuple[float, float, float],
    ) -> "SpatialScope":
        """Create a Euclidean spatial region."""
        return cls(
            scope_identity=f"spatial:{uuid.uuid4().hex[:16]}",
            region_type="euclidean",
            min_coordinates=min_coords,
            max_coordinates=max_coords,
        )
    
    @classmethod
    def screen_region(cls, x: int, y: int, width: int, height: int) -> "SpatialScope":
        """Create a screen region scope."""
        return cls(
            scope_identity=f"spatial:{uuid.uuid4().hex[:16]}",
            region_type="screen",
            screen_region={"x": x, "y": y, "width": width, "height": height},
        )
    
    @classmethod
    def filesystem_subtree(cls, path: str) -> "SpatialScope":
        """Create a scope for a filesystem subtree."""
        return cls(
            scope_identity=f"spatial:{uuid.uuid4().hex[:16]}",
            region_type="hierarchical",
            filesystem_paths=(path,),
        )
    
    @classmethod
    def application_hierarchy(cls, app_id: str) -> "SpatialScope":
        """Create a scope for an application hierarchy."""
        return cls(
            scope_identity=f"spatial:{uuid.uuid4().hex[:16]}",
            region_type="hierarchical",
            application_paths=(app_id,),
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if the spatial scope has valid data."""
        if self.region_type == "global":
            return True
        if self.region_type == "euclidean":
            if self.min_coordinates is None or self.max_coordinates is None:
                return False
            return all(
                c_min <= c_max
                for c_min, c_max in zip(self.min_coordinates, self.max_coordinates)
            )
        if self.region_type == "screen":
            if self.screen_region is None:
                return False
            return (
                self.screen_region.get("width", 0) > 0 and
                self.screen_region.get("height", 0) > 0
            )
        # Hierarchical and other types are always valid with paths
        return True


# =============================================================================
# MODALITY SCOPE
# =============================================================================


@dataclass(frozen=True)
class ModalityScope:
    """
    Defines which modalities are included in a projection.
    
    A Projection may include:
        - one Modality
        - one Modality Family
        - selected Modalities
        - all available Modalities
        - all participating Modalities in one Integration artifact
    
    Excluded or unavailable Modalities shall remain explicit where materially
    relevant.
    """
    
    scope_identity: str
    
    # Modality selection
    modality_kind: str = "all"  # single, family, selected, all, participating
    
    # Single modality (when modality_kind == "single")
    single_modality_id: Optional[str] = None
    
    # Family name (when modality_kind == "family")
    modality_family: Optional[str] = None
    
    # Selected modalities
    selected_modalities: Tuple[str, ...] = field(default_factory=tuple)
    
    # Exclude unavailable modalities
    exclude_unavailable: bool = True
    
    @classmethod
    def all_modalities(cls) -> "ModalityScope":
        """Create a scope for all available modalities."""
        return cls(
            scope_identity=f"modality:{uuid.uuid4().hex[:16]}",
            modality_kind="all",
        )
    
    @classmethod
    def single_modality(cls, modality_id: str) -> "ModalityScope":
        """Create a scope for a single modality."""
        return cls(
            scope_identity=f"modality:{uuid.uuid4().hex[:16]}",
            modality_kind="single",
            single_modality_id=modality_id,
        )
    
    @classmethod
    def selected_modalities(cls, modality_ids: List[str]) -> "ModalityScope":
        """Create a scope for selected modalities."""
        return cls(
            scope_identity=f"modality:{uuid.uuid4().hex[:16]}",
            modality_kind="selected",
            selected_modalities=tuple(modality_ids),
        )
    
    @classmethod
    def family(cls, family_name: str) -> "ModalityScope":
        """Create a scope for all modalities in a family."""
        return cls(
            scope_identity=f"modality:{uuid.uuid4().hex[:16]}",
            modality_kind="family",
            modality_family=family_name,
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if the modality scope has valid data."""
        if self.modality_kind in ("all", "participating"):
            return True
        if self.modality_kind == "single":
            return self.single_modality_id is not None and len(self.single_modality_id) > 0
        if self.modality_kind == "family":
            return self.modality_family is not None and len(self.modality_family) > 0
        if self.modality_kind == "selected":
            return len(self.selected_modalities) > 0
        return False


# =============================================================================
# ARTIFACT SCOPE
# =============================================================================


@dataclass(frozen=True)
class ArtifactScope:
    """
    Defines which artifact kinds are included in a projection.
    
    Artifact scope may restrict to specific kinds of Percepts, Scenes,
    Events, or other artifact types.
    """
    
    scope_identity: str
    
    # Artifact kind selection
    artifact_kind: str = "all"  # all, percept, scene, event, fused
    
    # Specific IDs
    artifact_ids: Tuple[str, ...] = field(default_factory=tuple)
    
    # Kind-specific filters
    include_fused_percepts: bool = True
    exclude_stale: bool = False
    
    @classmethod
    def all_artifacts(cls) -> "ArtifactScope":
        """Create a scope for all artifact kinds."""
        return cls(
            scope_identity=f"artifact:{uuid.uuid4().hex[:16]}",
            artifact_kind="all",
        )
    
    @classmethod
    def percepts_only(cls, include_fused: bool = True) -> "ArtifactScope":
        """Create a scope for Percepts only."""
        return cls(
            scope_identity=f"artifact:{uuid.uuid4().hex[:16]}",
            artifact_kind="percept",
            include_fused_percepts=include_fused,
        )
    
    @classmethod
    def scenes_only(cls) -> "ArtifactScope":
        """Create a scope for Scenes only."""
        return cls(
            scope_identity=f"artifact:{uuid.uuid4().hex[:16]}",
            artifact_kind="scene",
        )
    
    @classmethod
    def events_only(cls) -> "ArtifactScope":
        """Create a scope for Events only."""
        return cls(
            scope_identity=f"artifact:{uuid.uuid4().hex[:16]}",
            artifact_kind="event",
        )
    
    @classmethod
    def specific_artifacts(cls, artifact_ids: List[str]) -> "ArtifactScope":
        """Create a scope for specific artifact IDs."""
        return cls(
            scope_identity=f"artifact:{uuid.uuid4().hex[:16]}",
            artifact_kind="specific",
            artifact_ids=tuple(artifact_ids),
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if the artifact scope has valid data."""
        if self.artifact_kind in ("all", "percept", "scene", "event", "fused"):
            return True
        if self.artifact_kind == "specific":
            return len(self.artifact_ids) > 0
        return False


# =============================================================================
# FULL PROJECTION SCOPE
# =============================================================================


@dataclass(frozen=True)
class PerceptionProjectionScope:
    """
    Complete scope for a projection request.
    
    Combines all dimension-specific scopes into one cohesive constraint
    that determines which artifacts are included in the projection.
    
    A request may combine multiple scope dimensions.
    Scope composition shall remain explicit.
    """
    
    scope_identity: str
    
    temporal: TemporalScope = field(default_factory=TemporalScope.global_scope)
    spatial: SpatialScope = field(default_factory=SpatialScope.global_scope)
    modality: ModalityScope = field(default_factory=ModalityScope.all_modalities)
    artifact: ArtifactScope = field(default_factory=ArtifactScope.all_artifacts)
    
    # Resolution metadata
    resolved_at_utc: float = field(default_factory=_time.time)
    resolution_version: int = 1
    
    @classmethod
    def create(
        cls,
        temporal_scope: Optional[TemporalScope] = None,
        spatial_scope: Optional[SpatialScope] = None,
        modality_scope: Optional[ModalityScope] = None,
        artifact_scope: Optional[ArtifactScope] = None,
    ) -> "PerceptionProjectionScope":
        """
        Create a projection scope from dimension scopes.
        
        Args:
            temporal_scope: Temporal boundaries
            spatial_scope: Spatial boundaries
            modality_scope: Modality constraints
            artifact_scope: Artifact kind constraints
            
        Returns:
            New PerceptionProjectionScope instance
        """
        return cls(
            scope_identity=f"scope:{uuid.uuid4().hex[:16]}",
            temporal=temporal_scope or TemporalScope.global_scope(),
            spatial=spatial_scope or SpatialScope.global_scope(),
            modality=modality_scope or ModalityScope.all_modalities(),
            artifact=artifact_scope or ArtifactScope.all_artifacts(),
        )
    
    @classmethod
    def current_percepts(cls) -> "PerceptionProjectionScope":
        """Create a scope for current Percepts from all modalities."""
        return cls(
            scope_identity=f"scope:{uuid.uuid4().hex[:16]}",
            temporal=TemporalScope.current(),
            spatial=SpatialScope.global_scope(),
            modality=ModalityScope.all_modalities(),
            artifact=ArtifactScope.percepts_only(),
        )
    
    @classmethod
    def recent_scenes(cls, duration: float = 60.0) -> "PerceptionProjectionScope":
        """Create a scope for recent Scenes."""
        return cls(
            scope_identity=f"scope:{uuid.uuid4().hex[:16]}",
            temporal=TemporalScope.recent(duration),
            spatial=SpatialScope.global_scope(),
            modality=ModalityScope.all_modalities(),
            artifact=ArtifactScope.scenes_only(),
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if all scope dimensions are valid."""
        return (
            self.temporal.is_valid and
            self.spatial.is_valid and
            self.modality.is_valid and
            self.artifact.is_valid
        )


__all__ = [
    "TemporalScope",
    "SpatialScope",
    "ModalityScope",
    "ArtifactScope",
    "PerceptionProjectionScope",
]