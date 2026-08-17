# Memory-Perception Cross-System Request
# ========================================

"""
Memory-Perception Request: Specification for cross-system operations.

A MemoryPerceptionRequest describes the desired integration without being
an artifact itself. Every request passes through Integration, never directly
between Perception and Memory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# REQUEST KINDS - What cross-system operation is requested?
# =============================================================================


class RequestKind(Enum):
    """
    Kinds of cross-system requests.
    
    These define what kind of integration operation Memory-Perception Integration
    shall perform when a request arrives.
    """
    
    # Admission operations
    PREPARE_MEMORY_CANDIDATE = "prepare_memory_candidate"     # Prepare observation for Memory admission
    
    # Recognition and recollection
    FIND_RECOGNITION_CANDIDATES = "find_recognition_candidates"  # Find similar memories
    RETRIEVE_RECOLLECTION_CONTEXT = "retrieve_recollection_context"  # Get relevant memories
    
    # Contextualization and expectation
    BUILD_CONTEXTUAL_VIEW = "build_contextual_view"           # Combine perception with context
    GENERATE_EXPECTATION = "generate_expectation"             # Generate expectations from memory
    
    # Comparison and mismatch
    COMPARE_EXPECTATION = "compare_expectation"               # Compare expectation vs observation
    EVALUATE_MISMATCH = "evaluate_mismatch"                   # Classify mismatches
    
    # Continuity and correspondence
    EVALUATE_CONTINUITY = "evaluate_continuity"               # Evaluate entity continuity across gaps
    ALIGN_TEMPORAL_CONTEXT = "align_temporal_context"         # Align perception/memory time
    ALIGN_SPATIAL_CONTEXT = "align_spatial_context"           # Align perception/memory space
    
    # Identity and synchronization
    EVALUATE_IDENTITY_CORRESPONDENCE = "evaluate_identity_correspondence"  # Check if entities match
    SYNCHRONIZE_REVISIONS = "synchronize_revisions"           # Sync Perception/Memory revisions
    
    # Governance and diagnostics
    INSPECT_PROVENANCE = "inspect_provenance"                 # Trace provenance chain
    VALIDATE_SOURCE_ROLES = "validate_source_roles"          # Validate epistemic labeling
    INSPECT_HEALTH = "inspect_health"                         # Check integration health


# =============================================================================
# TEMPORAL SCOPE - Time window for cross-system operations
# =============================================================================


@dataclass(frozen=True)
class TemporalScope:
    """
    Temporal scope for a cross-system request.
    
    Defines the time range over which integration shall operate.
    """
    
    start_utc: Optional[float] = None     # Earliest timestamp (seconds since epoch)
    end_utc: Optional[float] = None       # Latest timestamp
    tolerance_seconds: float = 1.0        # Time matching tolerance
    
    @classmethod
    def current(cls) -> "TemporalScope":
        """Scope for current observations."""
        now = time.time()
        return cls(
            start_utc=now - 5.0,  # Last 5 seconds
            end_utc=now,
            tolerance_seconds=1.0,
        )
    
    @classmethod
    def recent(cls, duration_seconds: float = 60.0) -> "TemporalScope":
        """Scope for recent observations."""
        now = time.time()
        return cls(
            start_utc=now - duration_seconds,
            end_utc=now,
            tolerance_seconds=1.0,
        )
    
    @classmethod
    def historical(cls, start_offset: float = 3600.0) -> "TemporalScope":
        """Scope for historical memory retrieval."""
        now = time.time()
        return cls(
            start_utc=now - start_offset,
            end_utc=now,
            tolerance_seconds=5.0,
        )
    
    def is_empty(self) -> bool:
        """Check if scope has no temporal bounds."""
        return self.start_utc is None and self.end_utc is None


# =============================================================================
# SPATIAL SCOPE - Spatial region for cross-system operations
# =============================================================================


@dataclass(frozen=True)
class SpatialScope:
    """
    Spatial scope for a cross-system request.
    
    Defines the spatial region over which integration shall operate.
    """
    
    reference_frame: str = "global"       # e.g., "world", "workspace", "screen"
    min_coordinates: Tuple[float, float] = (0.0, 0.0)   # Minimum (x, y)
    max_coordinates: Tuple[float, float] = (1.0, 1.0)   # Maximum (x, y)
    tolerance_meters: float = 0.5         # Spatial matching tolerance
    
    @classmethod
    def global_scope(cls) -> "SpatialScope":
        """Global spatial scope."""
        return cls(
            reference_frame="global",
            min_coordinates=(-float("inf"), -float("inf")),
            max_coordinates=(float("inf"), float("inf")),
            tolerance_meters=1.0,
        )
    
    @classmethod
    def workspace(cls) -> "SpatialScope":
        """Workspace-level spatial scope."""
        return cls(
            reference_frame="workspace",
            min_coordinates=(0.0, 0.0),
            max_coordinates=(2000.0, 1500.0),  # Typical screen/workspace
            tolerance_meters=0.5,
        )
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is within the spatial scope."""
        return (
            self.min_coordinates[0] <= x <= self.max_coordinates[0] and
            self.min_coordinates[1] <= y <= self.max_coordinates[1]
        )


# =============================================================================
# MEMORY CONSTRAINTS - Constraints on memory operations
# =============================================================================


@dataclass(frozen=True)
class MemoryConstraints:
    """
    Constraints on memory retrieval and matching.
    """
    
    maximum_candidates: int = 20          # Maximum number of candidates to return
    minimum_similarity: float = 0.3       # Minimum similarity for inclusion
    temporal_distance_weight: float = 0.5 # Weight for temporal distance in scoring
    confidence_minimum: float = 0.5       # Minimum confidence threshold
    
    max_context_artifacts: int = 10       # Maximum artifacts in context
    context_depth: int = 3                # How far back to search for context


# =============================================================================
# CROSS-SYSTEM REQUEST - The canonical request model
# =============================================================================


@dataclass(frozen=True)
class MemoryPerceptionRequest:
    """
    Request for cross-system Memory-Perception integration.
    
    Every semantic exchange between Perception and Memory passes through
    Integration via a MemoryPerceptionRequest.
    
    Fields:
        request_identity:      Unique identifier for this request
        requester_identity:    ID of the requesting component/system
        request_kind:          What kind of operation is requested?
        source_artifacts:      References to artifacts involved (IDs only)
        temporal_scope:        Time window for the operation
        spatial_scope:         Spatial region for the operation
        identity_scope:        Identity constraints (which entities to consider)
        requested_result_kind: Expected result type
        confidence_constraints: Minimum confidence requirements
        uncertainty_constraints: Maximum uncertainty allowed
        authorization_context: Authorization context for access control
        compatibility_revision: Revision compatibility level
        provenance:            Request origin tracking
    """
    
    # Identity and metadata (required)
    request_identity: str                 # Unique ID
    requester_identity: str               # Who made this request?
    request_kind: RequestKind             # What kind of operation?
    
    # Source artifacts (references only, never direct access)
    source_artifacts: Tuple[str, ...]     # Artifact IDs involved
    
    # Scope parameters
    temporal_scope: TemporalScope = field(default_factory=TemporalScope)
    spatial_scope: SpatialScope = field(default_factory=SpatialScope.global_scope)
    
    # Identity constraints (for correspondence operations)
    identity_scope: Tuple[str, ...] = field(default_factory=tuple)  # Entity IDs
    
    # Expected result type
    requested_result_kind: Optional[str] = None
    
    # Quality constraints
    confidence_constraints: Dict[str, float] = field(default_factory=dict)  # field -> min_confidence
    uncertainty_constraints: Dict[str, float] = field(default_factory=dict)  # field -> max_uncertainty
    
    # Authorization and compatibility
    authorization_context: Dict[str, Any] = field(default_factory=dict)
    compatibility_revision: int = 1       # Request format revision
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_admission_preparation(
        cls,
        source_projection_id: str,
        source_percepts: List[str],
        source_scenes: List[str],
        source_events: List[str],
        current_context: Optional[Dict[str, Any]] = None,
    ) -> "MemoryPerceptionRequest":
        """
        Create a request to prepare an observation for Memory admission.
        
        Args:
            source_projection_id: ID of the projection being admitted
            source_percepts: Percept IDs involved
            source_scenes: Scene IDs involved
            source_events: Event IDs involved
            current_context: Current workspace/task context (optional)
        """
        return cls(
            request_identity=f"request:admission:{uuid.uuid4().hex[:16]}",
            requester_identity="perception:projection",
            request_kind=RequestKind.PREPARE_MEMORY_CANDIDATE,
            source_artifacts=tuple([source_projection_id] + source_percepts + source_scenes + source_events),
            temporal_scope=TemporalScope.current(),
            identity_scope=(),
            confidence_constraints={
                "observation_confidence": 0.5,
            },
            provenance={
                "origin": "perception_integration",
                "created_at_utc": time.time(),
            },
        )
    
    @classmethod
    def create_recognition_request(
        cls,
        current_projection_id: str,
        candidate_percepts: List[str],
        recognition_scope: TemporalScope = None,
        maximum_candidates: int = 20,
    ) -> "MemoryPerceptionRequest":
        """
        Create a request to find similar memories for current perception.
        
        Args:
            current_projection_id: ID of the projection being recognized
            candidate_percepts: Percept IDs to match against memory
            recognition_scope: Time window for memory search
            maximum_candidates: Maximum candidates to return
        """
        return cls(
            request_identity=f"request:recognition:{uuid.uuid4().hex[:16]}",
            requester_identity="integration:recognition",
            request_kind=RequestKind.FIND_RECOGNITION_CANDIDATES,
            source_artifacts=tuple([current_projection_id] + candidate_percepts),
            temporal_scope=recognition_scope or TemporalScope.historical(),
            confidence_constraints={
                "similarity": 0.3,
            },
            provenance={
                "origin": "integration:recognition",
                "created_at_utc": time.time(),
            },
        )
    
    @classmethod
    def create_recollection_request(
        cls,
        trigger_projection_id: str,
        recognition_references: List[str],
        maximum_artifacts: int = 10,
    ) -> "MemoryPerceptionRequest":
        """
        Create a request to retrieve relevant memories for current perception.
        
        Args:
            trigger_projection_id: ID of the projection triggering recollection
            recognition_references: Recognition results to guide retrieval
            maximum_artifacts: Maximum artifacts to return in context
        """
        return cls(
            request_identity=f"request:recollection:{uuid.uuid4().hex[:16]}",
            requester_identity="integration:recollection",
            request_kind=RequestKind.RETRIEVE_RECOLLECTION_CONTEXT,
            source_artifacts=tuple([trigger_projection_id] + recognition_references),
            temporal_scope=TemporalScope.recent(),
            confidence_constraints={
                "relevance": 0.5,
            },
            provenance={
                "origin": "integration:recollection",
                "created_at_utc": time.time(),
            },
        )
    
    @classmethod
    def create_expectation_request(
        cls,
        trigger_projection_id: str,
        recognition_result_ids: List[str],
        recollection_context_ids: List[str],
        prediction_horizon_seconds: float = 30.0,
    ) -> "MemoryPerceptionRequest":
        """
        Create a request to generate expectations from memory.
        
        Args:
            trigger_projection_id: Current perception triggering expectation
            recognition_result_ids: Recognition results to base on
            recollection_context_ids: Recollected context for expectation
            prediction_horizon_seconds: How far ahead to predict
        """
        return cls(
            request_identity=f"request:expectation:{uuid.uuid4().hex[:16]}",
            requester_identity="integration:expectation",
            request_kind=RequestKind.GENERATE_EXPECTATION,
            source_artifacts=tuple([trigger_projection_id] + recognition_result_ids + recollection_context_ids),
            temporal_scope=TemporalScope.current(),
            confidence_constraints={
                "confidence": 0.5,
            },
            provenance={
                "origin": "integration:expectation",
                "created_at_utc": time.time(),
            },
        )
    
    @classmethod
    def create_continuity_request(
        cls,
        earlier_artifact_id: str,
        later_artifact_id: str,
        gap_seconds: float = 0.5,
    ) -> "MemoryPerceptionRequest":
        """
        Create a request to evaluate continuity across an observation gap.
        
        Args:
            earlier_artifact_id: First observed artifact
            later_artifact_id: Later observed artifact
            gap_seconds: Duration of the unobserved interval
        """
        return cls(
            request_identity=f"request:continuity:{uuid.uuid4().hex[:16]}",
            requester_identity="integration:continuity",
            request_kind=RequestKind.EVALUATE_CONTINUITY,
            source_artifacts=tuple([earlier_artifact_id, later_artifact_id]),
            temporal_scope=TemporalScope(),
            confidence_constraints={
                "continuity_confidence": 0.5,
            },
            provenance={
                "origin": "integration:continuity",
                "created_at_utc": time.time(),
                "gap_seconds": gap_seconds,
            },
        )
    
    @classmethod
    def create_identity_request(
        cls,
        observed_entity_id: str,
        remembered_entity_id: str,
    ) -> "MemoryPerceptionRequest":
        """
        Create a request to evaluate identity correspondence.
        
        Args:
            observed_entity_id: Currently observed entity ID
            remembered_entity_id: Previously remembered entity ID
        """
        return cls(
            request_identity=f"request:identity:{uuid.uuid4().hex[:16]}",
            requester_identity="integration:identity",
            request_kind=RequestKind.EVALUATE_IDENTITY_CORRESPONDENCE,
            source_artifacts=tuple([observed_entity_id, remembered_entity_id]),
            temporal_scope=TemporalScope.current(),
            confidence_constraints={
                "correspondence_confidence": 0.5,
            },
            provenance={
                "origin": "integration:identity",
                "created_at_utc": time.time(),
            },
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if request has minimal required data."""
        return (
            len(self.request_identity) > 0 and
            self.requester_identity is not None and
            isinstance(self.request_kind, RequestKind)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary for serialization."""
        return {
            "request_identity": self.request_identity,
            "requester_identity": self.requester_identity,
            "request_kind": self.request_kind.value,
            "source_artifacts": list(self.source_artifacts),
            "temporal_scope": {
                "start_utc": self.temporal_scope.start_utc,
                "end_utc": self.temporal_scope.end_utc,
                "tolerance_seconds": self.temporal_scope.tolerance_seconds,
            },
            "spatial_scope": {
                "reference_frame": self.spatial_scope.reference_frame,
                "min_coordinates": list(self.spatial_scope.min_coordinates),
                "max_coordinates": list(self.spatial_scope.max_coordinates),
                "tolerance_meters": self.spatial_scope.tolerance_meters,
            },
            "identity_scope": list(self.identity_scope),
            "requested_result_kind": self.requested_result_kind,
            "confidence_constraints": dict(self.confidence_constraints),
            "uncertainty_constraints": dict(self.uncertainty_constraints),
            "authorization_context": dict(self.authorization_context),
            "compatibility_revision": self.compatibility_revision,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryPerceptionRequest":
        """Create request from dictionary."""
        return cls(
            request_identity=data.get("request_identity", str(uuid.uuid4())),
            requester_identity=data.get("requester_identity", "unknown"),
            request_kind=RequestKind(data.get("request_kind", "unknown")),
            source_artifacts=tuple(data.get("source_artifacts", [])),
            temporal_scope=TemporalScope(
                start_utc=data.get("temporal_scope", {}).get("start_utc"),
                end_utc=data.get("temporal_scope", {}).get("end_utc"),
                tolerance_seconds=float(data.get("temporal_scope", {}).get("tolerance_seconds", 1.0)),
            ),
            spatial_scope=SpatialScope(
                reference_frame=data.get("spatial_scope", {}).get("reference_frame", "global"),
                min_coordinates=tuple(data.get("spatial_scope", {}).get("min_coordinates", [0.0, 0.0])),
                max_coordinates=tuple(data.get("spatial_scope", {}).get("max_coordinates", [1.0, 1.0])),
                tolerance_meters=float(data.get("spatial_scope", {}).get("tolerance_meters", 0.5)),
            ),
            identity_scope=tuple(data.get("identity_scope", [])),
            requested_result_kind=data.get("requested_result_kind"),
            confidence_constraints=dict(data.get("confidence_constraints", {})),
            uncertainty_constraints=dict(data.get("uncertainty_constraints", {})),
            authorization_context=dict(data.get("authorization_context", {})),
            compatibility_revision=int(data.get("compatibility_revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )


__all__ = [
    "RequestKind",
    "TemporalScope",
    "SpatialScope",
    "MemoryConstraints",
    "MemoryPerceptionRequest",
]