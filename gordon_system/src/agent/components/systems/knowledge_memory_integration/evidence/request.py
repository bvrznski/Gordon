# Memory Evidence Request Contract
# =================================

"""
Memory Evidence Request: Request memory artifacts as retained evidence.

This module defines the canonical request model for retrieving retained
memories as evidence for Knowledge construction operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# REQUESTED ARTIFACT KINDS - What kinds of artifacts are requested?
# =============================================================================


class RequestedArtifactKinds(Enum):
    """
    Kinds of memory artifacts that may be requested as evidence.
    
    These specify what types of retained representations Knowledge needs
    for semantic operations.
    """
    
    ALL_ARTIFACTS = "all_artifacts"               # No filtering by kind
    
    # Semantic kinds
    ASSERTION = "assertion"                       # Stored assertions
    PROPOSITION = "proposition"                   # Stored propositions
    CONCEPT = "concept"                           # Stored concepts
    RELATION = "relation"                         # Stored relations
    BELIEF = "belief"                             # Stored beliefs
    MODEL = "model"                               # Stored models
    
    # Epistemic kinds
    EPISODIC_EVIDENCE = "episodic_evidence"      # First-hand experiences
    SEMANTIC_MEMORY = "semantic_memory"          # General knowledge
    PROCEDURAL_PRECEDENT = "procedural_precedent"  # Process records
    
    # Contextual kinds
    HISTORICAL_CONTEXT = "historical_context"    # Temporal background
    AUTOBIOGRAPHICAL = "autobiographical"        # Personal history


# =============================================================================
# SOURCE ROLE FILTER - Filter artifacts by source role
# =============================================================================


@dataclass(frozen=True)
class SourceRoleFilter:
    """
    Filter for evidence based on source roles.
    
    Allows Knowledge to request evidence with specific epistemic labels.
    """
    
    include_roles: Tuple[str, ...] = ()     # Roles to include (e.g., "CURRENT_OBSERVATION")
    exclude_roles: Tuple[str, ...] = ()     # Roles to exclude
    require_all_roles: bool = False         # If True, all specified roles must be present


# =============================================================================
# TEMPORAL SCOPE - Time window for evidence retrieval
# =============================================================================


@dataclass(frozen=True)
class EvidenceTemporalScope:
    """
    Temporal scope for evidence retrieval.
    
    Defines the time range over which evidence shall be retrieved.
    """
    
    start_utc: Optional[float] = None     # Earliest timestamp (seconds since epoch)
    end_utc: Optional[float] = None       # Latest timestamp
    temporal_tolerance_seconds: float = 1.0  # Time matching tolerance
    
    @classmethod
    def current(cls) -> "EvidenceTemporalScope":
        """Scope for current observations."""
        now = time.time()
        return cls(
            start_utc=now - 5.0,
            end_utc=now,
            temporal_tolerance_seconds=1.0,
        )
    
    @classmethod
    def recent(cls, duration_seconds: float = 60.0) -> "EvidenceTemporalScope":
        """Scope for recent observations."""
        now = time.time()
        return cls(
            start_utc=now - duration_seconds,
            end_utc=now,
            temporal_tolerance_seconds=1.0,
        )
    
    @classmethod
    def historical(cls, start_offset: float = 3600.0) -> "EvidenceTemporalScope":
        """Scope for historical memory retrieval."""
        now = time.time()
        return cls(
            start_utc=now - start_offset,
            end_utc=now,
            temporal_tolerance_seconds=5.0,
        )
    
    def is_empty(self) -> bool:
        """Check if scope has no temporal bounds."""
        return self.start_utc is None and self.end_utc is None


# =============================================================================
# PROVENANCE DEPTH - How deep to trace provenance chains
# =============================================================================


class ProvenanceDepth(Enum):
    """
    Levels of provenance depth for evidence retrieval.
    
    Controls how far back in the provenance chain to trace when retrieving
    memory artifacts.
    """
    
    SHALLOW = "shallow"         # Direct ancestors only (1-2 levels)
    MODERATE = "moderate"       # Several generations back
    DEEP = "deep"               # Complete provenance chain
    FULL = "full"               # All available provenance history


# =============================================================================
# EVIDENCE REQUEST - The canonical evidence request model
# =============================================================================


@dataclass(frozen=True)
class EvidenceRequest:
    """
    Request for memory artifacts as retained evidence.
    
    This request asks Memory to provide retained experiences that may support
    semantic operations. It does NOT ask Memory to determine semantic meaning -
    that is Knowledge's responsibility.
    
    Fields:
        request_identity:         Unique identifier for this request
        requesting_knowledge_component: Which Knowledge component is asking?
        semantic_question:        The semantic question requiring evidence
        requested_artifact_kinds: What kinds of artifacts are needed?
        requested_source_roles:   Source role constraints on artifacts
        temporal_scope:           Time window for retrieval
        provenance_depth:         How deep to trace provenance chains
        maximum_artifacts:        Maximum number of artifacts to return
        confidence_constraints:   Minimum confidence requirements
        authorization_context:    Authorization context for access control
        compatibility_revision:   Revision compatibility level
        provenance:               Request origin tracking
    """
    
    # Identity and metadata (required)
    request_identity: str                 # Unique ID
    requesting_knowledge_component: str   # Who is asking?
    
    # Semantic scope
    semantic_question: str                # The question needing evidence
    
    # Artifact kind constraints
    requested_artifact_kinds: Tuple[RequestedArtifactKinds, ...] = field(
        default_factory=tuple  # Empty means all kinds
    )
    
    # Source role filtering
    source_role_filter: SourceRoleFilter = field(default_factory=SourceRoleFilter)
    
    # Temporal scope
    temporal_scope: EvidenceTemporalScope = field(default_factory=EvidenceTemporalScope.current)
    
    # Provenance depth
    provenance_depth: ProvenanceDepth = ProvenanceDepth.MODERATE
    
    # Limits and constraints
    maximum_artifacts: int = 50           # Maximum number of artifacts
    maximum_representation_size_bytes: int = 1048576  # 1MB limit per artifact
    
    # Quality constraints
    confidence_minimum: float = 0.3       # Minimum confidence threshold
    uncertainty_maximum: float = 0.7      # Maximum allowed uncertainty
    
    # Authorization and compatibility
    authorization_context: Dict[str, Any] = field(default_factory=dict)
    compatibility_revision: int = 1       # Request format revision
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def for_semantic_question(
        cls,
        semantic_question: str,
        requesting_component: str,
        maximum_artifacts: int = 20,
        temporal_scope: Optional[EvidenceTemporalScope] = None,
        confidence_minimum: float = 0.3,
    ) -> "EvidenceRequest":
        """
        Create an evidence request for a semantic question.
        
        Args:
            semantic_question: The question requiring evidence
            requesting_component: Which Knowledge component is asking?
            maximum_artifacts: Maximum number of artifacts to return
            temporal_scope: Time window (optional)
            confidence_minimum: Minimum confidence threshold
        """
        return cls(
            request_identity=f"evidence:request:{uuid.uuid4().hex[:16]}",
            requesting_knowledge_component=requesting_component,
            semantic_question=semantic_question,
            requested_artifact_kinds=(),
            temporal_scope=temporal_scope or EvidenceTemporalScope.current(),
            maximum_artifacts=maximum_artifacts,
            confidence_minimum=confidence_minimum,
            provenance={
                "origin": "knowledge_integration",
                "created_at_utc": time.time(),
            },
        )
    
    @classmethod
    def for_extraction(
        cls,
        source_artifact_ids: List[str],
        requesting_component: str,
        target_kinds: Tuple[RequestedArtifactKinds, ...] = (),
        minimum_supporting_evidence: int = 2,
    ) -> "EvidenceRequest":
        """
        Create an evidence request for semantic extraction.
        
        Args:
            source_artifact_ids: IDs of artifacts to analyze
            requesting_component: Which Knowledge component is asking?
            target_kinds: Target artifact kinds for extraction (optional)
            minimum_supporting_evidence: Minimum count for pattern detection
        """
        return cls(
            request_identity=f"evidence:extraction:{uuid.uuid4().hex[:16]}",
            requesting_knowledge_component=requesting_component,
            semantic_question="Extract semantic structure from these artifacts",
            requested_artifact_kinds=target_kinds,
            maximum_artifacts=minimum_supporting_evidence * 5,  # Allow some margin
            provenance={
                "origin": "knowledge_integration",
                "extraction_kind": "pattern_based",
                "source_count": len(source_artifact_ids),
                "created_at_utc": time.time(),
            },
        )
    
    @classmethod
    def for_grounding(
        cls,
        knowledge_artifact_id: str,
        requesting_component: str,
        temporal_scope: Optional[EvidenceTemporalScope] = None,
    ) -> "EvidenceRequest":
        """
        Create an evidence request to build grounding for a Knowledge artifact.
        
        Args:
            knowledge_artifact_id: The Knowledge artifact needing grounding
            requesting_component: Which Knowledge component is asking?
            temporal_scope: Time window (optional)
        """
        return cls(
            request_identity=f"evidence:grounding:{uuid.uuid4().hex[:16]}",
            requesting_knowledge_component=requesting_component,
            semantic_question=f"What memory supports this Knowledge artifact: {knowledge_artifact_id}",
            temporal_scope=temporal_scope or EvidenceTemporalScope.current(),
            provenance={
                "origin": "knowledge_integration",
                "artifact_id": knowledge_artifact_id,
                "created_at_utc": time.time(),
            },
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if request has minimal required data."""
        return (
            len(self.request_identity) > 0 and
            len(self.semantic_question) > 0 and
            isinstance(self.temporal_scope, EvidenceTemporalScope)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary for serialization."""
        return {
            "request_identity": self.request_identity,
            "requesting_knowledge_component": self.requesting_knowledge_component,
            "semantic_question": self.semantic_question,
            "requested_artifact_kinds": [k.value for k in self.requested_artifact_kinds],
            "source_role_filter": {
                "include_roles": list(self.source_role_filter.include_roles),
                "exclude_roles": list(self.source_role_filter.exclude_roles),
                "require_all_roles": self.source_role_filter.require_all_roles,
            },
            "temporal_scope": {
                "start_utc": self.temporal_scope.start_utc,
                "end_utc": self.temporal_scope.end_utc,
                "tolerance_seconds": self.temporal_scope.temporal_tolerance_seconds,
            },
            "provenance_depth": self.provenance_depth.value,
            "maximum_artifacts": self.maximum_artifacts,
            "confidence_minimum": self.confidence_minimum,
            "uncertainty_maximum": self.uncertainty_maximum,
            "authorization_context": dict(self.authorization_context),
            "compatibility_revision": self.compatibility_revision,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidenceRequest":
        """Create request from dictionary."""
        return cls(
            request_identity=data.get("request_identity", str(uuid.uuid4())),
            requesting_knowledge_component=data.get("requesting_knowledge_component", "unknown"),
            semantic_question=data.get("semantic_question", ""),
            requested_artifact_kinds=tuple(
                RequestedArtifactKinds(v) for v in data.get("requested_artifact_kinds", [])
            ),
            source_role_filter=SourceRoleFilter(
                include_roles=tuple(data.get("source_role_filter", {}).get("include_roles", [])),
                exclude_roles=tuple(data.get("source_role_filter", {}).get("exclude_roles", [])),
                require_all_roles=data.get("source_role_filter", {}).get("require_all_roles", False),
            ),
            temporal_scope=EvidenceTemporalScope(
                start_utc=data.get("temporal_scope", {}).get("start_utc"),
                end_utc=data.get("temporal_scope", {}).get("end_utc"),
                temporal_tolerance_seconds=float(data.get("temporal_scope", {}).get("tolerance_seconds", 1.0)),
            ),
            provenance_depth=ProvenanceDepth(data.get("provenance_depth", "moderate")),
            maximum_artifacts=int(data.get("maximum_artifacts", 50)),
            confidence_minimum=float(data.get("confidence_minimum", 0.3)),
            uncertainty_maximum=float(data.get("uncertainty_maximum", 0.7)),
            authorization_context=dict(data.get("authorization_context", {})),
            compatibility_revision=int(data.get("compatibility_revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )


__all__ = [
    "RequestedArtifactKinds",
    "SourceRoleFilter",
    "EvidenceTemporalScope",
    "ProvenanceDepth",
    "EvidenceRequest",
]