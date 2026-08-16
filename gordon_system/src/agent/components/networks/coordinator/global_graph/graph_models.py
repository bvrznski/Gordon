# Gordon Cognitive Architecture - Phase 4.11.4
# ===========================================

"""
Global Coordination Graph Core Data Models
===========================================

Canonical immutable models for graph structure.

GRAPHLAW-111: All models are deeply frozen (frozen=True, slots=True)
GRAPHLAW-112: Models have no runtime references
GRAPHLAW-113: Model identity is deterministic from content
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# =============================================================================
# IMPORT ENUMS (defined first to enable cross-references in models)
# =============================================================================

from .enums import (
    CoordinationGraphNodeKind,
    CoordinationGraphEdgeKind,
    CoordinationNodeStatus,
    CoordinationEdgeStatus,
    GraphRevisionKind,
    ComponentKind,
    GraphPartitionKind,
    GraphDomainKind,
    SemanticScope,
)


# =============================================================================
# GRAPH IDENTITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class GlobalCoordinationGraphIdentity:
    """
    Immutable identity for a Global Coordination Graph.
    
    GRAPHLAW-121: Graph identity is stable across revisions
    GRAPHLAW-122: Identity is independent from revision number
    GRAPHLAW-123: Identity preserves provenance
    
    GCG-ID-LAW-001: Graph identity shall remain immutable
    GCG-ID-LAW-002: Equivalent semantic graphs have equivalent identities
    """
    architecture_identity: str = "gordon-cognitive-architecture-v4"
    """Architecture version identifier."""
    
    graph_contract_version: str = "1.0.0"
    """Contract version for this graph model."""
    
    membership_revision: int = 1
    """Revision number of the coordinated network membership."""
    
    provenance_ref: Optional[str] = None
    """Reference to identity provenance record."""


# =============================================================================
# GRAPH REVISION IDENTITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class GlobalCoordinationGraphRevisionIdentity:
    """
    Immutable identity for a graph revision.
    
    GRAPHLAW-131: Revision identity is deterministic from content
    GRAPHLAW-132: Revision identity preserves parent reference
    
    GCG-REV-LAW-001: Every published graph belongs to exactly one revision
    GCG-REV-LAW-002: Revision lineage remains complete
    """
    graph_identity_ref: str = ""
    """Reference to the base graph identity."""
    
    revision_number: int = 1
    """Revision sequence number."""
    
    parent_revision_ref: Optional[str] = None
    """Reference to previous revision (empty for initial)."""
    
    def __str__(self) -> str:
        return f"gcg-revision:{self.graph_identity_ref}:{self.revision_number}"


# =============================================================================
# GLOBAL COORDINATION GRAPH
# =============================================================================

@dataclass(frozen=True, slots=True)
class GlobalCoordinationGraph:
    """
    Immutable canonical graph structure.
    
    GRAPHLAW-141: Graph is immutable after construction
    GRAPHLAW-142: Graph has no runtime references
    GRAPHLAW-143: Graph preserves revision lineage
    
    GCG-LAW-001: Every published graph possesses stable identity
    GCG-LAW-002: Revisions are immutable
    GCG-LAW-003: Historical information is preserved
    """
    identity: GlobalCoordinationGraphRevisionIdentity
    """Unique revision identity."""
    
    base_graph_identity: GlobalCoordinationGraphIdentity = field(default_factory=GlobalCoordinationGraphIdentity)
    """Base graph identity for this revision."""
    
    nodes: tuple[CoordinationGraphNode, ...] = ()
    """All graph nodes (canonical and immutable)."""
    
    edges: tuple[CoordinationGraphEdge, ...] = ()
    """All graph edges (canonical and immutable)."""
    
    partitions: tuple[CoordinationGraphPartition, ...] = ()
    """Semantic partitions of the graph."""
    
    domains: tuple[CoordinationGraphDomain, ...] = ()
    """Semantic domains in the graph."""
    
    components: tuple[CoordinationGraphComponent, ...] = ()
    """Connected components in the graph topology."""
    
    indexes: GlobalCoordinationGraphIndexes = field(default_factory=lambda: GlobalCoordinationGraphIndexes(revision=1))
    """Immutable graph indexes for efficient lookup."""
    
    findings: tuple[str, ...] = ()
    """Findings discovered during construction/validation."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on graph completeness or quality."""
    
    provenance_ref: Optional[str] = None
    """Reference to provenance record."""
    
    revision_kind: str = "initial"
    """Kind of this graph revision (from GraphRevisionKind)."""
    
    @property
    def node_count(self) -> int:
        """Return the number of nodes in the graph."""
        return len(self.nodes)
    
    @property
    def edge_count(self) -> int:
        """Return the number of edges in the graph."""
        return len(self.edges)


# =============================================================================
# COORDINATION GRAPH NODE
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationGraphNode:
    """
    Immutable node in the coordination graph.
    
    GRAPHLAW-151: Node is immutable after construction
    GRAPHLAW-152: Node identity is deterministic from content
    GRAPHLAW-153: Node kind is explicit
    
    NODE-LAW-001: Every node possesses stable semantic identity
    NODE-LAW-002: Node kind remains explicit
    NODE-LAW-003: Node payload is referenced, not duplicated
    """
    identity: str
    """Unique semantic identity for this node."""
    
    kind: CoordinationGraphNodeKind
    """Kind of node (from CoordinationGraphNodeKind)."""
    
    payload_reference: Optional[str] = None
    """Reference to payload (not the payload itself)."""
    
    semantic_scope: SemanticScope = field(default_factory=SemanticScope)
    """Semantic scope for this node."""
    
    domains: tuple[GraphDomainKind, ...] = ()
    """Domains containing this node."""
    
    partitions: tuple[GraphPartitionKind, ...] = ()
    """Partitions containing this node."""
    
    status: CoordinationNodeStatus = CoordinationNodeStatus.ACTIVE
    """Current status of the node."""
    
    confidence: float = 1.0
    """Confidence in this node's validity (0.0 to 1.0)."""
    
    uncertainty: float = 0.0
    """Uncertainty about this node (0.0 to 1.0)."""
    
    provenance_ref: Optional[str] = None
    """Reference to provenance record."""
    
    revision: int = 1
    """Revision number of this node."""
    
    @property
    def is_active(self) -> bool:
        """Check if node is currently active."""
        return self.status == CoordinationNodeStatus.ACTIVE


# =============================================================================
# COORDINATION GRAPH EDGE
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationGraphEdge:
    """
    Immutable edge in the coordination graph.
    
    GRAPHLAW-161: Edge is immutable after construction
    GRAPHLAW-162: Edge identity is deterministic from content
    GRAPHLAW-163: Edges are directed
    
    EDGE-LAW-001: Every edge possesses stable semantic identity
    EDGE-LAW-002: Edges are always directed
    EDGE-LAW-003: Edge kind remains explicit
    """
    identity: str
    """Unique semantic identity for this edge."""
    
    source_node: str
    """Identity of the source node."""
    
    target_node: str
    """Identity of the target node."""
    
    kind: CoordinationGraphEdgeKind
    """Kind of edge (from CoordinationGraphEdgeKind)."""
    
    condition_reference: Optional[str] = None
    """Reference to any condition on this relationship."""
    
    semantic_scope: SemanticScope = field(default_factory=SemanticScope)
    """Semantic scope for this edge."""
    
    status: CoordinationEdgeStatus = CoordinationEdgeStatus.ACTIVE
    """Current status of the edge."""
    
    confidence: float = 1.0
    """Confidence in this edge's validity (0.0 to 1.0)."""
    
    uncertainty: float = 0.0
    """Uncertainty about this edge (0.0 to 1.0)."""
    
    provenance_ref: Optional[str] = None
    """Reference to provenance record."""
    
    revision: int = 1
    """Revision number of this edge."""
    
    @property
    def is_active(self) -> bool:
        """Check if edge is currently active."""
        return self.status == CoordinationEdgeStatus.ACTIVE


# =============================================================================
# COORDINATION GRAPH PARTITION
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationGraphPartition:
    """
    Immutable partition of the graph.
    
    GRAPHLAW-171: Partition is immutable
    GRAPHLAW-172: Partitions may overlap (nodes in multiple partitions)
    
    PARTITION-LAW-001: Partitions remain semantic
    PARTITION-LAW-002: Partitions may overlap
    """
    identity: str
    """Unique identity for this partition."""
    
    kind: GraphPartitionKind
    """Kind of partition (from GraphPartitionKind)."""
    
    member_nodes: tuple[str, ...] = ()
    """Node identities in this partition."""
    
    member_edges: tuple[str, ...] = ()
    """Edge identities in this partition."""
    
    boundary_nodes: tuple[str, ...] = ()
    """Nodes at the partition boundary."""
    
    inbound_edges: tuple[str, ...] = ()
    """Edges entering this partition."""
    
    outbound_edges: tuple[str, ...] = ()
    """Edges leaving this partition."""
    
    domain_references: tuple[GraphDomainKind, ...] = ()
    """Domains referenced by this partition."""
    
    status: CoordinationNodeStatus = CoordinationNodeStatus.ACTIVE
    """Partition status."""
    
    confidence: float = 1.0
    """Confidence in partition boundaries."""
    
    provenance_ref: Optional[str] = None
    """Reference to provenance record."""
    
    revision: int = 1
    """Revision number of this partition."""


# =============================================================================
# COORDINATION GRAPH DOMAIN
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationGraphDomain:
    """
    Immutable domain in the graph.
    
    GRAPHLAW-181: Domain is immutable
    GRAPHLAW-182: Domains may overlap (nodes in multiple domains)
    
    DOMAIN-LAW-001: Domains represent semantic operating contexts
    DOMAIN-LAW-002: Nodes may belong to multiple domains
    """
    identity: str
    """Unique identity for this domain."""
    
    kind: GraphDomainKind
    """Kind of domain (from GraphDomainKind)."""
    
    member_nodes: tuple[str, ...] = ()
    """Node identities in this domain."""
    
    member_edges: tuple[str, ...] = ()
    """Edge identities in this domain."""
    
    cross_domain_dependencies: tuple[str, ...] = ()
    """Dependencies between nodes in different domains."""
    
    cross_domain_constraints: tuple[str, ...] = ()
    """Constraints spanning multiple domains."""
    
    active_cycle_references: tuple[str, ...] = ()
    """Coordination cycles relevant to this domain."""
    
    status: CoordinationNodeStatus = CoordinationNodeStatus.ACTIVE
    """Domain status."""
    
    confidence: float = 1.0
    """Confidence in domain boundaries."""
    
    provenance_ref: Optional[str] = None
    """Reference to provenance record."""
    
    revision: int = 1
    """Revision number of this domain."""


# =============================================================================
# COORDINATION GRAPH COMPONENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationGraphComponent:
    """
    Immutable connected component in the graph.
    
    GRAPHLAW-191: Component is immutable
    GRAPHLAW-192: Components are derived from topology
    
    COMPONENT-LAW-001: Components derive from graph topology
    COMPONENT-LAW-002: Component identity remains stable
    """
    identity: str
    """Unique identity for this component."""
    
    kind: ComponentKind
    """Kind of component (from ComponentKind)."""
    
    node_references: tuple[str, ...] = ()
    """Node identities in this component."""
    
    edge_references: tuple[str, ...] = ()
    """Edge references within this component."""
    
    root_nodes: tuple[str, ...] = ()
    """Root nodes (no inbound edges)."""
    
    leaf_nodes: tuple[str, ...] = ()
    """Leaf nodes (no outbound edges)."""
    
    entry_edges: tuple[str, ...] = ()
    """Edges entering this component from outside."""
    
    exit_edges: tuple[str, ...] = ()
    """Edges leaving this component to outside."""
    
    cycle_classifications: tuple[str, ...] = ()
    """Cycles in this component."""
    
    status: CoordinationNodeStatus = CoordinationNodeStatus.ACTIVE
    """Component status."""
    
    provenance_ref: Optional[str] = None
    """Reference to provenance record."""
    
    revision: int = 1
    """Revision number of this component."""


# =============================================================================
# GLOBAL COORDINATION GRAPH INDEXES
# =============================================================================

@dataclass(frozen=True, slots=True)
class GlobalCoordinationGraphIndexes:
    """
    Immutable indexes for graph lookups.
    
    GRAPHLAW-201: Indexes are derived structures (not canonical truth)
    GRAPHLAW-202: Indexes are immutable after construction
    GRAPHLAW-203: Indexes preserve deterministic ordering
    
    INDEX-LAW-001: Indexes are derived structures
    INDEX-LAW-002: Indexes do not become canonical graph
    """
    revision: int = 1
    """Revision number these indexes apply to."""
    
    node_by_identity: dict[str, str] = field(default_factory=dict)
    """Map from identity string to canonical node reference (identity)."""
    
    edge_by_identity: dict[str, str] = field(default_factory=dict)
    """Map from identity string to canonical edge reference (identity)."""
    
    nodes_by_kind: dict[CoordinationGraphNodeKind, tuple[str, ...]] = field(default_factory=dict)
    """Grouped node identities by kind."""
    
    edges_by_kind: dict[CoordinationGraphEdgeKind, tuple[str, ...]] = field(default_factory=dict)
    """Grouped edge identities by kind."""
    
    projections_by_network: dict[str, tuple[str, ...]] = field(default_factory=dict)
    """Network projection nodes grouped by network identity."""
    
    capabilities_by_provider: dict[str, tuple[str, ...]] = field(default_factory=dict)
    """Capabilities provided by each provider (node identity)."""
    
    providers_by_capability: dict[str, tuple[str, ...]] = field(default_factory=dict)
    """Provider candidates for each capability."""
    
    requirements_by_requester: dict[str, tuple[str, ...]] = field(default_factory=dict)
    """Requirements grouped by requesting network."""
    
    dependencies_by_dependent: dict[str, tuple[str, ...]] = field(default_factory=dict)
    """Dependencies where key is the dependent node."""
    
    dependents_by_prerequisite: dict[str, tuple[str, ...]] = field(default_factory=dict)
    """Dependents grouped by prerequisite node."""
    
    nodes_by_domain: dict[GraphDomainKind, tuple[str, ...]] = field(default_factory=dict)
    """Nodes grouped by domain."""
    
    nodes_by_partition: dict[GraphPartitionKind, tuple[str, ...]] = field(default_factory=dict)
    """Nodes grouped by partition."""
    
    components_by_kind: dict[ComponentKind, tuple[str, ...]] = field(default_factory=dict)
    """Components grouped by kind."""
    
    def get_node_identity(self, node_id: str) -> Optional[str]:
        """Get the canonical identity reference for a node."""
        return self.node_by_identity.get(node_id)
    
    def get_edge_identity(self, edge_id: str) -> Optional[str]:
        """Get the canonical identity reference for an edge."""
        return self.edge_by_identity.get(edge_id)