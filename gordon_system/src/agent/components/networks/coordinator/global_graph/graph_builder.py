# Gordon Cognitive Architecture - Phase 4.11.4
# ===========================================

"""
Global Coordination Graph Builder
==================================

Deterministic construction of graph revisions from coordination artifacts.

GRAPHLAW-251: Construction is deterministic
GRAPHLAW-252: No runtime references are embedded in constructed graphs
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# Import types that may not be defined yet at module level (forward refs)
# These will resolve when all modules are loaded together


# =============================================================================
# GLOBAL COORDINATION GRAPH REQUEST
# =============================================================================

@dataclass(frozen=True, slots=True)
class GlobalCoordinationGraphRequest:
    """
    Immutable request for graph construction.
    
    GRAPHLAW-261: Request is immutable and complete
    GRAPHLAW-262: Request contains all necessary inputs
    
    GCG-REQ-LAW-001: Graph Requests validate before construction
    GCG-REQ-LAW-002: All request data must be immutable
    """
    identity: str = ""
    """Unique identifier for this request."""
    
    base_graph_snapshot_ref: Optional[str] = None
    """Reference to base graph snapshot (for incremental builds)."""
    
    coordination_epoch_ref: str = ""
    """Reference to the coordination epoch."""
    
    coordination_cycle_ref: str = ""
    """Reference to the coordination cycle."""
    
    coordination_plan_ref: str = ""
    """Reference to the coordination plan for this cycle."""
    
    coordination_state_ref: str = ""
    """Reference to the coordination state for this cycle."""
    
    network_projections: tuple[str, ...] = ()
    """References to network projection artifacts."""
    
    dependency_resolution_state_ref: Optional[str] = None
    """Reference to dependency resolution state."""
    
    graph_delta_ref: Optional[str] = None
    """Reference to delta (for incremental rebuilds)."""
    
    graph_policy: "GraphConstructionPolicy" = field(default_factory=lambda: GraphConstructionPolicy())
    """Policy for this construction operation."""
    
    semantic_time_ref: str = ""
    """Reference to semantic time for this request."""
    
    provenance_ref: Optional[str] = None
    """Reference to provenance record."""
    
    revision_kind: str = "incremental"
    """Kind of rebuild (from GraphRevisionKind)."""
    
    def is_full_rebuild(self) -> bool:
        """Check if this is a full rebuild request."""
        return self.base_graph_snapshot_ref is None
    
    def is_incremental(self) -> bool:
        """Check if this is an incremental build request."""
        return not self.is_full_rebuild()


# =============================================================================
# GLOBAL COORDINATION GRAPH RESULT
# =============================================================================

@dataclass(frozen=True, slots=True)
class GlobalCoordinationGraphResult:
    """
    Result of a graph construction operation.
    
    GRAPHLAW-271: Result is immutable after publication
    GRAPHLAW-272: Result contains all necessary information
    
    GCG-RES-LAW-001: Graph Results are deterministic from Requests
    GCG-RES-LAW-002: Results are published, not mutated
    """
    request_identity: str = ""
    """Reference to the originating request."""
    
    graph: "GlobalCoordinationGraph" = field(default_factory=lambda: GlobalCoordinationGraph())
    """The constructed graph."""
    
    snapshot_ref: Optional[str] = None
    """Reference to the graph snapshot."""
    
    delta: Optional["GlobalCoordinationGraphDelta"] = None
    """Computed delta (if applicable)."""
    
    indexes: "GlobalCoordinationGraphIndexes" = field(
        default_factory=lambda: GlobalCoordinationGraphIndexes(revision=1)
    )
    """Built indexes for the graph."""
    
    validation_result: str = "valid"
    """Validation result status."""
    
    findings: tuple[str, ...] = ()
    """Findings during construction."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on the result."""
    
    trace: tuple[str, ...] = ()
    """Trace events during construction."""
    
    status: str = "completed"
    """Status of this operation."""
    
    provenance_ref: Optional[str] = None
    """Reference to provenance record."""
    
    def is_successful(self) -> bool:
        """Check if the graph construction was successful."""
        return self.validation_result in ("valid", "valid_with_limitations")


# =============================================================================
# GRAPH ENTITY CANDIDATE - Pre-construction model
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationGraphNodeCandidate:
    """
    Pre-construction node candidate.
    
    GRAPHLAW-281: Candidate is immutable during extraction
    GRAPHLAW-282: Candidates are normalized before becoming canonical nodes
    
    NODE-CANDIDATE-LAW-001: Node candidates preserve semantic intent
    NODE-CANDIDATE-LAW-002: Candidates may be merged during normalization
    """
    semantic_identity: str
    """Semantic identity (not necessarily unique yet)."""
    
    kind: "CoordinationGraphNodeKind"
    """Node kind."""
    
    payload_reference: Optional[str] = None
    """Reference to payload (not payload itself)."""
    
    source_artifacts: tuple[str, ...] = ()
    """Source artifacts that produced this candidate."""
    
    semantic_scope: "SemanticScope" = field(default_factory=lambda: SemanticScope())
    """Semantic scope for this node."""
    
    domains: tuple["GraphDomainKind", ...] = ()
    """Domains containing this node."""
    
    status: "CoordinationNodeStatus" = CoordinationNodeStatus.ACTIVE
    """Current status."""
    
    confidence: float = 0.5
    """Confidence in this candidate."""
    
    uncertainty: float = 0.5
    """Uncertainty about this candidate."""
    
    provenance_ref: Optional[str] = None
    """Reference to provenance record."""


# =============================================================================
# EDGE CANDIDATE - Pre-construction model
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationGraphEdgeCandidate:
    """
    Pre-construction edge candidate.
    
    GRAPHLAW-291: Candidate is immutable during extraction
    GRAPHLAW-292: Candidates are normalized before becoming canonical edges
    
    EDGE-CANDIDATE-LAW-001: Edge candidates preserve semantic directionality
    EDGE-CANDIDATE-LAW-002: Exact duplicates may be canonicalized
    """
    semantic_identity: str = ""
    """Semantic identity (not necessarily unique yet)."""
    
    kind: "CoordinationGraphEdgeKind"
    """Edge kind."""
    
    source_identity: str
    """Source node identity."""
    
    target_identity: str
    """Target node identity."""
    
    source_artifacts: tuple[str, ...] = ()
    """Source artifacts that produced this candidate."""
    
    condition_reference: Optional[str] = None
    """Reference to any condition on this relationship."""
    
    semantic_scope: "SemanticScope" = field(default_factory=lambda: SemanticScope())
    """Semantic scope for this edge."""
    
    status: "CoordinationEdgeStatus" = CoordinationEdgeStatus.ACTIVE
    """Current status."""
    
    confidence: float = 0.5
    """Confidence in this candidate."""
    
    uncertainty: float = 0.5
    """Uncertainty about this candidate."""
    
    provenance_ref: Optional[str] = None
    """Reference to provenance record."""


# =============================================================================
# EXTRACTION RESULT
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationGraphExtraction:
    """
    Result of extracting graph entities from coordination artifacts.
    
    GRAPHLAW-301: Extraction is deterministic and immutable
    GRAPHLAW-302: Provenance is preserved throughout extraction
    
    EXTRACTION-LAW-001: Extracted candidates are deterministic from sources
    EXTRACTION-LAW-002: Source references are preserved
    """
    source_artifact_references: tuple[str, ...] = ()
    """References to source coordination artifacts."""
    
    node_candidates: tuple[CoordinationGraphNodeCandidate, ...] = ()
    """Extracted node candidates."""
    
    edge_candidates: tuple[CoordinationGraphEdgeCandidate, ...] = ()
    """Extracted edge candidates."""
    
    partition_candidates: tuple[str, ...] = ()
    """Partition candidate identifiers."""
    
    domain_candidates: tuple[str, ...] = ()
    """Domain candidate identifiers."""
    
    component_hints: tuple[str, ...] = ()
    """Component identification hints."""
    
    findings: tuple[str, ...] = ()
    """Findings during extraction."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on the extraction."""
    
    provenance_ref: Optional[str] = None
    """Reference to provenance record."""