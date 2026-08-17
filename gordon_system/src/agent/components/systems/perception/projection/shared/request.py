# Perception Projection Request - Phase 5.2.4
# ============================================

"""
Projection Request: Specifies what view is required.

A Projection Request shall declare what view is required.
It shall not expose Projection implementation details.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import uuid


# =============================================================================
# UPDATE MODES
# =============================================================================


class ProjectionUpdateMode:
    """
    Specifies how updates are delivered in projection streams.
    
    Suggested modes:
        - SNAPSHOT: Single immutable view
        - STREAM: Continuous update sequence
        - INCREMENTAL: Changes relative to prior view
        - ON_DEMAND: Request/response pattern
        - PERIODIC: Scheduled updates
        - EVENT_DRIVEN: Updates on events
        - SESSION_BOUND: For session lifetime
        - REVISION_BOUND: Until specific revision
    """
    
    SNAPSHOT = "snapshot"
    STREAM = "stream"
    INCREMENTAL = "incremental"
    ON_DEMAND = "on_demand"
    PERIODIC = "periodic"
    EVENT_DRIVEN = "event_driven"
    SESSION_BOUND = "session_bound"
    REVISION_BOUND = "revision_bound"


# =============================================================================
# VISIBILITY POLICIES
# =============================================================================


class ConflictVisibility:
    """Policies for conflict visibility in projections."""
    
    FULL = "full"  # Show all conflicts with details
    SUMMARY = "summary"  # Show conflict summaries only
    MATERIAL_ONLY = "material_only"  # Show material conflicts only
    COUNT_ONLY = "count_only"  # Show conflict counts only
    HIDDEN_WITH_DISCLOSURE = "hidden_with_disclosure"  # Hide details but disclose existence
    HIDDEN = "hidden"  # Hide conflicts entirely


class AmbiguityVisibility:
    """Policies for ambiguity visibility in projections."""
    
    ALL_ALTERNATIVES = "all_alternatives"  # Show all alternatives
    TOP_ALTERNATIVES = "top_alternatives"  # Show top N alternatives
    PRIMARY_WITH_DISCLOSURE = "primary_with_disclosure"  # Primary with disclosure of others
    SUMMARY = "summary"  # Summary only
    COUNT_ONLY = "count_only"  # Count only
    HIDDEN_WITH_DISCLOSURE = "hidden_with_disclosure"
    HIDDEN = "hidden"


class MissingEvidenceVisibility:
    """Policies for missing evidence visibility in projections."""
    
    FULL = "full"  # Full details by modality and reason
    BY_MODALITY = "by_modality"  # Grouped by modality
    BY_REASON = "by_reason"  # Grouped by reason
    MATERIAL_ONLY = "material_only"
    SUMMARY = "summary"
    COUNT_ONLY = "count_only"
    HIDDEN_WITH_DISCLOSURE = "hidden_with_disclosure"
    HIDDEN = "hidden"


# =============================================================================
# PROJECTION REQUEST
# =============================================================================


@dataclass(frozen=True)
class PerceptionProjectionRequest:
    """
    Request for a perceptual projection view.
    
    Preferred fields:
        - request_identity: Unique identifier for this request
        - requester_identity: Who is making the request
        - requested_projection_kind: What kind of view is needed
        - requested_scope: Constraints on what to include
        - temporal_scope: Time boundaries
        - spatial_scope: Space boundaries
        - modality_scope: Modality constraints
        - artifact_scope: Artifact kind constraints
        - detail_level: Granularity of the view
        - update_mode: How updates are delivered
        - visibility_constraints: What to include/exclude
        - confidence_constraints: Confidence thresholds
        - uncertainty_constraints: Uncertainty limits
        - authorization_context: For access control
        - policy_context: Policy constraints
        
    A request may combine multiple scope dimensions.
    """
    
    request_identity: str
    
    # Requester identity
    requester_identity: str  # Consumer making the request
    
    # What kind of projection is requested
    requested_projection_kind: str  # percept, scene, event, workspace, snapshot, stream
    
    # Scope constraints (dimensional)
    temporal_scope: Dict[str, Any] = field(default_factory=dict)  # TemporalScope
    spatial_scope: Dict[str, Any] = field(default_factory=dict)   # SpatialScope
    modality_scope: Dict[str, Any] = field(default_factory=dict)  # ModalityScope
    artifact_scope: Dict[str, Any] = field(default_factory=dict)  # ArtifactScope
    
    # Detail level (raw_reference, feature, percept, integrated_percept, scene, event, summary, diagnostic)
    detail_level: str = "percept"
    
    # Update mode
    update_mode: str = ProjectionUpdateMode.ON_DEMAND
    
    # Visibility policies
    conflict_visibility: str = ConflictVisibility.FULL
    ambiguity_visibility: str = AmbiguityVisibility.ALL_ALTERNATIVES
    missing_evidence_visibility: str = MissingEvidenceVisibility.FULL
    
    # Confidence/uncertainty constraints
    minimum_confidence: float = 0.0
    maximum_uncertainty: float = 1.0
    
    # Consumer contract reference (for compatibility checking)
    consumer_contract_reference: str = ""
    
    # Authorization and policy context
    authorization_context: Dict[str, Any] = field(default_factory=dict)
    policy_context: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_percept(
        cls,
        requester_id: str,
        modality_ids: Optional[List[str]] = None,
        detail_level: str = "percept",
        temporal_scope: Optional[Dict[str, Any]] = None,
        spatial_scope: Optional[Dict[str, Any]] = None,
    ) -> "PerceptionProjectionRequest":
        """Create a request for Percept projections."""
        return cls(
            request_identity=f"request:{uuid.uuid4().hex[:16]}",
            requester_identity=requester_id,
            requested_projection_kind="percept",
            temporal_scope=temporal_scope or {},
            spatial_scope=spatial_scope or {},
            modality_scope={"selected": modality_ids or []} if modality_ids else {},
            detail_level=detail_level,
            update_mode=ProjectionUpdateMode.ON_DEMAND,
        )
    
    @classmethod
    def create_scene(
        cls,
        requester_id: str,
        temporal_scope: Optional[Dict[str, Any]] = None,
        spatial_scope: Optional[Dict[str, Any]] = None,
        detail_level: str = "scene",
    ) -> "PerceptionProjectionRequest":
        """Create a request for Scene projections."""
        return cls(
            request_identity=f"request:{uuid.uuid4().hex[:16]}",
            requester_identity=requester_id,
            requested_projection_kind="scene",
            temporal_scope=temporal_scope or {},
            spatial_scope=spatial_scope or {},
            detail_level=detail_level,
            update_mode=ProjectionUpdateMode.ON_DEMAND,
        )
    
    @classmethod
    def create_event(
        cls,
        requester_id: str,
        event_kinds: Optional[List[str]] = None,
        temporal_scope: Optional[Dict[str, Any]] = None,
        spatial_scope: Optional[Dict[str, Any]] = None,
        detail_level: str = "event",
    ) -> "PerceptionProjectionRequest":
        """Create a request for Event projections."""
        return cls(
            request_identity=f"request:{uuid.uuid4().hex[:16]}",
            requester_identity=requester_id,
            requested_projection_kind="event",
            temporal_scope=temporal_scope or {},
            spatial_scope=spatial_scope or {},
            artifact_scope={"event_kinds": event_kinds or []} if event_kinds else {},
            detail_level=detail_level,
            update_mode=ProjectionUpdateMode.ON_DEMAND,
        )
    
    @classmethod
    def create_workspace(
        cls,
        requester_id: str,
        temporal_window: float = 60.0,
        max_artifacts: int = 100,
        detail_level: str = "percept",
    ) -> "PerceptionProjectionRequest":
        """Create a request for Workspace projections."""
        return cls(
            request_identity=f"request:{uuid.uuid4().hex[:16]}",
            requester_identity=requester_id,
            requested_projection_kind="workspace",
            temporal_scope={"kind": "recent", "duration_seconds": temporal_window},
            spatial_scope={"global": True},
            detail_level=detail_level,
            update_mode=ProjectionUpdateMode.STREAM,
        )
    
    @classmethod
    def create_snapshot(
        cls,
        requester_id: str,
        source_revision_boundary: Dict[str, int],
        projection_kind: str = "percept",
    ) -> "PerceptionProjectionRequest":
        """Create a request for Snapshot projections."""
        return cls(
            request_identity=f"request:{uuid.uuid4().hex[:16]}",
            requester_identity=requester_id,
            requested_projection_kind="snapshot",
            temporal_scope={"revision": source_revision_boundary},
            detail_level="summary",
            update_mode=ProjectionUpdateMode.SNAPSHOT,
        )
    
    @classmethod
    def create_stream(
        cls,
        requester_id: str,
        projection_kind: str = "percept",
        starting_revision: int = 1,
    ) -> "PerceptionProjectionRequest":
        """Create a request for Stream projections."""
        return cls(
            request_identity=f"request:{uuid.uuid4().hex[:16]}",
            requester_identity=requester_id,
            requested_projection_kind="stream",
            temporal_scope={"starting_revision": starting_revision},
            detail_level="percept",
            update_mode=ProjectionUpdateMode.STREAM,
        )
    
    @classmethod
    def create_delta(
        cls,
        base_projection_id: str,
        target_revision: Dict[str, int],
    ) -> "PerceptionProjectionRequest":
        """Create a request for Incremental Delta projections."""
        return cls(
            request_identity=f"request:{uuid.uuid4().hex[:16]}",
            requester_identity="internal",
            requested_projection_kind="delta",
            temporal_scope={"base_revision": base_projection_id, "target": target_revision},
            detail_level="percept",
            update_mode=ProjectionUpdateMode.INCREMENTAL,
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if the request has valid data."""
        if not self.request_identity or len(self.request_identity) == 0:
            return False
        if not self.requester_identity or len(self.requester_identity) == 0:
            return False
        if not self.requested_projection_kind or len(self.requested_projection_kind) == 0:
            return False
        
        # Validate detail level
        valid_detail_levels = {
            "raw_reference", "feature", "percept", "integrated_percept",
            "scene", "event", "summary", "diagnostic"
        }
        if self.detail_level not in valid_detail_levels:
            return False
        
        # Validate confidence/uncertainty bounds
        if not (0.0 <= self.minimum_confidence <= 1.0):
            return False
        if not (0.0 <= self.maximum_uncertainty <= 1.0):
            return False
        if self.minimum_confidence + self.maximum_uncertainty > 1.5:
            # Very high confidence + very low uncertainty might indicate invalid config
            pass  # Not necessarily invalid
        
        return True


# =============================================================================
# REQUEST BUILDER
# =============================================================================


class PerceptionProjectionRequestBuilder:
    """Mutable builder for constructing projection requests."""
    
    def __init__(self):
        self._request_identity: str = f"request:{uuid.uuid4().hex[:16]}"
        self._requester_identity: str = "unknown"
        self._requested_projection_kind: str = "percept"
        self._temporal_scope: Dict[str, Any] = {}
        self._spatial_scope: Dict[str, Any] = {}
        self._modality_scope: Dict[str, Any] = {}
        self._artifact_scope: Dict[str, Any] = {}
        self._detail_level: str = "percept"
        self._update_mode: str = ProjectionUpdateMode.ON_DEMAND
        self._conflict_visibility: str = ConflictVisibility.FULL
        self._ambiguity_visibility: str = AmbiguityVisibility.ALL_ALTERNATIVES
        self._missing_evidence_visibility: str = MissingEvidenceVisibility.FULL
        self._minimum_confidence: float = 0.0
        self._maximum_uncertainty: float = 1.0
        self._consumer_contract_reference: str = ""
    
    def set_identity(self, identity: str) -> "PerceptionProjectionRequestBuilder":
        """Set the request identity."""
        self._request_identity = identity
        return self
    
    def set_requester(self, requester_id: str) -> "PerceptionProjectionRequestBuilder":
        """Set the requester identity."""
        self._requester_identity = requester_id
        return self
    
    def set_projection_kind(self, kind: str) -> "PerceptionProjectionRequestBuilder":
        """Set the projection kind (percept, scene, event, workspace)."""
        self._requested_projection_kind = kind
        return self
    
    def set_temporal_scope(self, scope: Dict[str, Any]) -> "PerceptionProjectionRequestBuilder":
        """Set temporal scope."""
        self._temporal_scope = dict(scope)
        return self
    
    def set_spatial_scope(self, scope: Dict[str, Any]) -> "PerceptionProjectionRequestBuilder":
        """Set spatial scope."""
        self._spatial_scope = dict(scope)
        return self
    
    def set_modality_scope(self, scope: Dict[str, Any]) -> "PerceptionProjectionRequestBuilder":
        """Set modality scope."""
        self._modality_scope = dict(scope)
        return self
    
    def set_artifact_scope(self, scope: Dict[str, Any]) -> "PerceptionProjectionRequestBuilder":
        """Set artifact scope."""
        self._artifact_scope = dict(scope)
        return self
    
    def set_detail_level(self, level: str) -> "PerceptionProjectionRequestBuilder":
        """Set detail level."""
        valid_levels = {
            "raw_reference", "feature", "percept", "integrated_percept",
            "scene", "event", "summary", "diagnostic"
        }
        if level not in valid_levels:
            raise ValueError(f"Invalid detail level: {level}")
        self._detail_level = level
        return self
    
    def set_update_mode(self, mode: str) -> "PerceptionProjectionRequestBuilder":
        """Set update mode."""
        self._update_mode = mode
        return self
    
    def set_conflict_visibility(self, visibility: str) -> "PerceptionProjectionRequestBuilder":
        """Set conflict visibility policy."""
        valid_visibilities = {
            ConflictVisibility.FULL,
            ConflictVisibility.SUMMARY,
            ConflictVisibility.MATERIAL_ONLY,
            ConflictVisibility.COUNT_ONLY,
            ConflictVisibility.HIDDEN_WITH_DISCLOSURE,
            ConflictVisibility.HIDDEN,
        }
        if visibility not in valid_visibilities:
            raise ValueError(f"Invalid conflict visibility: {visibility}")
        self._conflict_visibility = visibility
        return self
    
    def set_ambiguity_visibility(self, visibility: str) -> "PerceptionProjectionRequestBuilder":
        """Set ambiguity visibility policy."""
        self._ambiguity_visibility = visibility
        return self
    
    def set_missing_evidence_visibility(self, visibility: str) -> "PerceptionProjectionRequestBuilder":
        """Set missing evidence visibility policy."""
        self._missing_evidence_visibility = visibility
        return self
    
    def set_minimum_confidence(self, confidence: float) -> "PerceptionProjectionRequestBuilder":
        """Set minimum confidence threshold (0.0-1.0)."""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {confidence}")
        self._minimum_confidence = confidence
        return self
    
    def set_maximum_uncertainty(self, uncertainty: float) -> "PerceptionProjectionRequestBuilder":
        """Set maximum uncertainty limit (0.0-1.0)."""
        if not 0.0 <= uncertainty <= 1.0:
            raise ValueError(f"Uncertainty must be 0.0-1.0, got {uncertainty}")
        self._maximum_uncertainty = uncertainty
        return self
    
    def set_consumer_contract(self, contract_ref: str) -> "PerceptionProjectionRequestBuilder":
        """Set consumer contract reference."""
        self._consumer_contract_reference = contract_ref
        return self
    
    def build(self) -> PerceptionProjectionRequest:
        """Build an immutable request."""
        if not self._requester_identity:
            raise ValueError("requester identity is required")
        
        return PerceptionProjectionRequest(
            request_identity=self._request_identity,
            requester_identity=self._requester_identity,
            requested_projection_kind=self._requested_projection_kind,
            temporal_scope=dict(self._temporal_scope),
            spatial_scope=dict(self._spatial_scope),
            modality_scope=dict(self._modality_scope),
            artifact_scope=dict(self._artifact_scope),
            detail_level=self._detail_level,
            update_mode=self._update_mode,
            conflict_visibility=self._conflict_visibility,
            ambiguity_visibility=self._ambiguity_visibility,
            missing_evidence_visibility=self._missing_evidence_visibility,
            minimum_confidence=self._minimum_confidence,
            maximum_uncertainty=self._maximum_uncertainty,
            consumer_contract_reference=self._consumer_contract_reference,
        )


__all__ = [
    "ProjectionUpdateMode",
    "ConflictVisibility",
    "AmbiguityVisibility",
    "MissingEvidenceVisibility",
    "PerceptionProjectionRequest",
    "PerceptionProjectionRequestBuilder",
]