# Knowledge-Memory Cross-System Request
# ======================================

"""
Knowledge-Memory Request: Specification for cross-system integration operations.

This module defines the canonical request models for Knowledge-Memory Integration,
enabling semantic coordination between persistent knowledge and retained memory.
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
    Kinds of Knowledge-Memory cross-system requests.
    
    These define what kind of integration operation shall be performed when
    a request arrives from either Knowledge or Memory.
    """
    
    # Evidence retrieval
    RETRIEVE_MEMORY_EVIDENCE = "retrieve_memory_evidence"           # Get retained memory evidence
    
    # Semantic extraction
    EXTRACT_SEMANTIC_CANDIDATES = "extract_semantic_candidates"     # Extract candidates from evidence
    
    # Grounding operations
    BUILD_GROUNDING = "build_grounding"                             # Link artifacts to evidence
    
    # Persistence operations
    PREPARE_KNOWLEDGE_PERSISTENCE = "prepare_knowledge_persistence"  # Prepare for memory retention
    PERSIST_KNOWLEDGE_REVISION = "persist_knowledge_revision"       # Persist a semantic revision
    
    # Reconstruction operations
    RECONSTRUCT_KNOWLEDGE = "reconstruct_knowledge"                 # Restore from persistence
    PREPARE_ACTIVATION = "prepare_activation"                       # Prepare for Knowledge activation
    
    # Revision management
    COORDINATE_SUPERSESSION = "coordinate_supersession"             # Manage superseding revisions
    COORDINATE_CONCEPT_MERGE = "coordinate_concept_merge"           # Merge concepts
    COORDINATE_CONCEPT_SPLIT = "coordinate_concept_split"           # Split concepts
    
    # Organization operations
    COORDINATE_CONSOLIDATION = "coordinate_consolidation"           # Organize semantic structure
    COORDINATE_CONTRADICTION = "coordinate_contradiction"           # Process contradictions
    
    # Synchronization and validation
    SYNCHRONIZE_REVISIONS = "synchronize_revisions"                 # Sync knowledge/memory revisions
    REVALIDATE_INTEGRATION = "revalidate_integration"               # Revalidate after changes
    
    # Governance and diagnostics
    INSPECT_PROVENANCE = "inspect_provenance"                       # Trace provenance chain
    VALIDATE_EVIDENCE_ELIGIBILITY = "validate_evidence_eligibility"  # Check evidence eligibility
    INSPECT_INTEGRATION_HEALTH = "inspect_integration_health"       # Check integration health


# =============================================================================
# TEMPORAL SCOPE - Time window for cross-system operations
# =============================================================================


@dataclass(frozen=True)
class TemporalScope:
    """
    Temporal scope for a Knowledge-Memory operation.
    
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
            start_utc=now - 5.0,
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
# SEMANTIC SCOPE - Semantic domain for cross-system operations
# =============================================================================


@dataclass(frozen=True)
class SemanticScope:
    """
    Semantic scope for a Knowledge-Memory operation.
    
    Defines which semantic domains or artifact kinds shall be considered.
    """
    
    target_kinds: Tuple[str, ...] = ()     # Artifact kinds to include (e.g., "concept", "belief")
    exclude_kinds: Tuple[str, ...] = ()    # Artifact kinds to exclude
    ontology_context: str = ""             # Ontology context identifier
    
    @classmethod
    def all_kinds(cls) -> "SemanticScope":
        """Scope including all semantic artifact kinds."""
        return cls(target_kinds=(), exclude_kinds=())
    
    @classmethod
    def for_knowledge_artifacts(
        cls,
        kinds: Tuple[str, ...] = ("concept", "proposition", "belief"),
    ) -> "SemanticScope":
        """Scope limited to knowledge artifacts of specified kinds."""
        return cls(target_kinds=kinds, exclude_kinds=())


# =============================================================================
# CONFIDENCE CONSTRAINTS - Quality requirements
# =============================================================================


@dataclass(frozen=True)
class ConfidenceConstraints:
    """
    Constraints on confidence/uncertainty for cross-system operations.
    """
    
    minimum_evidence_confidence: float = 0.5     # Minimum confidence in evidence
    maximum_uncertainty: float = 0.5             # Maximum allowed uncertainty
    required_confidence_fields: Tuple[str, ...] = ()  # Specific fields that need minimum confidence


# =============================================================================
# CROSS-SYSTEM REQUEST - The canonical request model
# =============================================================================


@dataclass(frozen=True)
class KnowledgeMemoryRequest:
    """
    Request for cross-system Knowledge-Memory integration.
    
    Every semantic exchange between Knowledge and Memory passes through
    Integration via a KnowledgeMemoryRequest.
    
    Fields:
        request_identity:      Unique identifier for this request
        requester_identity:    ID of the requesting component/system
        request_kind:          What kind of operation is requested?
        knowledge_scope:       Semantic domain constraints from Knowledge side
        memory_scope:          Temporal/spatial scope on Memory side
        source_artifacts:      References to artifacts involved (IDs only)
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
    temporal_scope: TemporalScope = field(default_factory=TemporalScope.current)
    semantic_scope: SemanticScope = field(default_factory=SemanticScope.all_kinds)
    
    # Expected result type
    requested_result_kind: Optional[str] = None
    
    # Quality constraints
    confidence_constraints: ConfidenceConstraints = field(
        default_factory=ConfidenceConstraints
    )
    uncertainty_constraints: Dict[str, float] = field(default_factory=dict)  # field -> max_uncertainty
    
    # Authorization and compatibility
    authorization_context: Dict[str, Any] = field(default_factory=dict)
    compatibility_revision: int = 1       # Request format revision
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_evidence_retrieval_request(
        cls,
        semantic_question: str,
        requesting_knowledge_component: str,
        maximum_artifacts: int = 20,
        temporal_scope: Optional[TemporalScope] = None,
    ) -> "KnowledgeMemoryRequest":
        """
        Create a request to retrieve memory evidence for a semantic question.
        
        Args:
            semantic_question: The semantic question requiring evidence
            requesting_knowledge_component: Which Knowledge component is asking?
            maximum_artifacts: Maximum evidence artifacts to return
            temporal_scope: Time window for retrieval (optional)
        """
        return cls(
            request_identity=f"request:evidence:{uuid.uuid4().hex[:16]}",
            requester_identity=requesting_knowledge_component,
            request_kind=RequestKind.RETRIEVE_MEMORY_EVIDENCE,
            source_artifacts=(),
            temporal_scope=temporal_scope or TemporalScope.current(),
            semantic_scope=SemanticScope.all_kinds(),
            requested_result_kind="evidence_response",
            confidence_constraints=ConfidenceConstraints(
                minimum_evidence_confidence=0.5
            ),
            provenance={
                "origin": "knowledge_integration",
                "semantic_question": semantic_question,
                "created_at_utc": time.time(),
            },
        )
    
    @classmethod
    def create_extraction_request(
        cls,
        source_artifact_ids: List[str],
        target_kinds: Tuple[str, ...] = ("concept", "proposition", "belief"),
        minimum_support: int = 2,
    ) -> "KnowledgeMemoryRequest":
        """
        Create a request to extract semantic candidates from memory evidence.
        
        Args:
            source_artifact_ids: Memory artifact IDs to analyze
            target_kinds: Kinds of semantic artifacts to extract
            minimum_support: Minimum supporting evidence count
        """
        return cls(
            request_identity=f"request:extraction:{uuid.uuid4().hex[:16]}",
            requester_identity="knowledge_integration",
            request_kind=RequestKind.EXTRACT_SEMANTIC_CANDIDATES,
            source_artifacts=tuple(source_artifact_ids),
            semantic_scope=SemanticScope.for_knowledge_artifacts(target_kinds),
            confidence_constraints=ConfidenceConstraints(
                minimum_evidence_confidence=0.3
            ),
            provenance={
                "origin": "knowledge_integration",
                "extraction_kind": "pattern_based",
                "minimum_support": minimum_support,
                "created_at_utc": time.time(),
            },
        )
    
    @classmethod
    def create_grounding_request(
        cls,
        knowledge_artifact_id: str,
        candidate_memory_ids: List[str],
        minimum_support_strength: float = 0.5,
    ) -> "KnowledgeMemoryRequest":
        """
        Create a request to build grounding for a Knowledge artifact.
        
        Args:
            knowledge_artifact_id: The Knowledge artifact needing grounding
            candidate_memory_ids: Memory evidence candidates
            minimum_support_strength: Minimum required support strength
        """
        return cls(
            request_identity=f"request:grounding:{uuid.uuid4().hex[:16]}",
            requester_identity="knowledge_integration",
            request_kind=RequestKind.BUILD_GROUNDING,
            source_artifacts=tuple([knowledge_artifact_id] + candidate_memory_ids),
            confidence_constraints=ConfidenceConstraints(
                minimum_evidence_confidence=minimum_support_strength
            ),
            provenance={
                "origin": "knowledge_integration",
                "created_at_utc": time.time(),
            },
        )
    
    @classmethod
    def create_persistence_request(
        cls,
        knowledge_artifact_id: str,
        semantic_revision: int,
        persistence_purpose: str = "cross_session_continuity",
    ) -> "KnowledgeMemoryRequest":
        """
        Create a request to prepare Knowledge for Memory persistence.
        
        Args:
            knowledge_artifact_id: The Knowledge artifact to persist
            semantic_revision: Revision number of the Knowledge artifact
            persistence_purpose: Why is this being persisted?
        """
        return cls(
            request_identity=f"request:persistence:{uuid.uuid4().hex[:16]}",
            requester_identity="knowledge_integration",
            request_kind=RequestKind.PREPARE_KNOWLEDGE_PERSISTENCE,
            source_artifacts=(knowledge_artifact_id,),
            confidence_constraints=ConfidenceConstraints(
                minimum_evidence_confidence=0.5
            ),
            provenance={
                "origin": "knowledge_integration",
                "semantic_revision": semantic_revision,
                "persistence_purpose": persistence_purpose,
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
            "semantic_scope": {
                "target_kinds": list(self.semantic_scope.target_kinds),
                "exclude_kinds": list(self.semantic_scope.exclude_kinds),
                "ontology_context": self.semantic_scope.ontology_context,
            },
            "requested_result_kind": self.requested_result_kind,
            "confidence_constraints": {
                "minimum_evidence_confidence": self.confidence_constraints.minimum_evidence_confidence,
                "maximum_uncertainty": self.confidence_constraints.maximum_uncertainty,
                "required_confidence_fields": list(self.confidence_constraints.required_confidence_fields),
            },
            "uncertainty_constraints": dict(self.uncertainty_constraints),
            "authorization_context": dict(self.authorization_context),
            "compatibility_revision": self.compatibility_revision,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeMemoryRequest":
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
            semantic_scope=SemanticScope(
                target_kinds=tuple(data.get("semantic_scope", {}).get("target_kinds", [])),
                exclude_kinds=tuple(data.get("semantic_scope", {}).get("exclude_kinds", [])),
                ontology_context=data.get("semantic_scope", {}).get("ontology_context", ""),
            ),
            requested_result_kind=data.get("requested_result_kind"),
            confidence_constraints=ConfidenceConstraints(
                minimum_evidence_confidence=float(data.get("confidence_constraints", {}).get("minimum_evidence_confidence", 0.5)),
                maximum_uncertainty=float(data.get("confidence_constraints", {}).get("maximum_uncertainty", 0.5)),
                required_confidence_fields=tuple(data.get("confidence_constraints", {}).get("required_confidence_fields", [])),
            ),
            uncertainty_constraints=dict(data.get("uncertainty_constraints", {})),
            authorization_context=dict(data.get("authorization_context", {})),
            compatibility_revision=int(data.get("compatibility_revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )


__all__ = [
    "RequestKind",
    "TemporalScope",
    "SemanticScope",
    "ConfidenceConstraints",
    "KnowledgeMemoryRequest",
]