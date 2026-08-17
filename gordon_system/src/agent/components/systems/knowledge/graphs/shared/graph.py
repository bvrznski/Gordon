"""Knowledge Graph - Phase 6.8 Part 1.

This module implements the canonical KnowledgeGraph contract (Part 1 Section 2)
and the KnowledgeSubgraph contract (Part 1 Section 10).

The KnowledgeGraph is the actual graph structure containing node and edge
references. The GraphDescriptor (in descriptor.py) holds metadata about it.

KnowledgeGraph answers: "How is everything connected?"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# KNOWLEDGE GRAPH - Phase 6.8 Part 1 Section 2
# =============================================================================


@dataclass(frozen=True)
class KnowledgeGraph:
    """
    The canonical Knowledge Graph structure.

    Per Part 1 Section 2, the preferred model is:
        KnowledgeGraph

    Suggested fields:
        semantic_identity   - Semantic identity the graph represents
        graph_kind          - Kind of graph (semantic, epistemic, etc.)
        node_references     - References to nodes in this graph
        edge_references     - References to edges in this graph
        graph_constraints   - Constraints on the graph structure
        graph_metadata      - Additional metadata
        provenance          - Origin and evolution trail

    Per GRAPH-LAW-001: Every Knowledge Graph shall possess one immutable
    Semantic Identity.
    Per GRAPH-LAW-002: Graphs shall organize semantic artifacts only.
    Per GRAPH-LAW-003: Graphs shall preserve semantic identities of all
    referenced artifacts.
    Per GRAPH-LAW-004: Graphs shall preserve provenance.
    Per GRAPH-LAW-007: Graphs shall remain deterministic.
    Per GRAPH-LAW-008: Published Graphs shall remain immutable.

    The KnowledgeGraph is NOT:
        - a database
        - an ontology
        - an embedding index
        - a vector database
        - a memory system

    It IS a semantic organization layer that integrates every Knowledge
    Artifact into one explicit semantic network.
    """

    # Core identity (required per GRAPH-LAW-001)
    semantic_identity: str

    # Graph kind (required)
    graph_kind: str

    # Node references (required per GRAPH-LAW-002, GRAPH-LAW-003)
    node_references: Tuple[str, ...] = field(default_factory=tuple)

    # Edge references
    edge_references: Tuple[str, ...] = field(default_factory=tuple)

    # Constraints (per GRAPH-LAW-002)
    graph_constraints: Tuple[str, ...] = field(default_factory=tuple)

    # Metadata
    graph_metadata: Dict[str, Any] = field(default_factory=dict)

    # Provenance (required per GRAPH-LAW-004)
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)

    # Graph layers (per Part 1 Section 11)
    layers: Tuple[str, ...] = field(default_factory=tuple)

    # Graph revision (per GRAPH-LAW-005)
    graph_revision: int = 1

    # Lifecycle state
    lifecycle_state: str = "created"

    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        """Validate graph after creation."""
        if not self.semantic_identity:
            raise ValueError("semantic_identity cannot be empty")
        if not self.graph_kind:
            raise ValueError("graph_kind cannot be empty")

    @property
    def is_valid(self) -> bool:
        """Check if graph has valid foundational data."""
        return (
            len(self.semantic_identity) > 0 and
            self.graph_kind is not None
        )

    @property
    def node_count(self) -> int:
        """Number of nodes in this graph."""
        return len(self.node_references)

    @property
    def edge_count(self) -> int:
        """Number of edges in this graph."""
        return len(self.edge_references)

    @classmethod
    def create(
        cls,
        semantic_identity: str,
        graph_kind: str,
        node_references: Optional[List[str]] = None,
        edge_references: Optional[List[str]] = None,
        graph_constraints: Optional[List[str]] = None,
        graph_metadata: Optional[Dict[str, Any]] = None,
    ) -> "KnowledgeGraph":
        """
        Create a new Knowledge Graph.

        Args:
            semantic_identity: Semantic identity the graph represents
            graph_kind: Kind of graph (semantic, epistemic, etc.)
            node_references: References to nodes (optional)
            edge_references: References to edges (optional)
            graph_constraints: Constraints on the graph (optional)
            graph_metadata: Additional metadata (optional)

        Returns:
            New KnowledgeGraph with complete provenance
        """
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Knowledge graph initialization",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [semantic_identity],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )

        return cls(
            semantic_identity=semantic_identity,
            graph_kind=graph_kind,
            node_references=tuple(node_references or []),
            edge_references=tuple(edge_references or []),
            graph_constraints=tuple(graph_constraints or []),
            graph_metadata=dict(graph_metadata or {}),
            provenance=initial_provenance,
            created_at_utc=time.time(),
        )

    def add_node(self, node_ref: str) -> "KnowledgeGraph":
        """Add a node reference and return new graph."""
        if node_ref in self.node_references:
            return self
        return KnowledgeGraph(
            semantic_identity=self.semantic_identity,
            graph_kind=self.graph_kind,
            node_references=tuple(self.node_references + (node_ref,)),
            edge_references=self.edge_references,
            graph_constraints=self.graph_constraints,
            graph_metadata=self.graph_metadata,
            layers=self.layers,
            graph_revision=self.graph_revision + 1,
            lifecycle_state=self.lifecycle_state,
            provenance=self._append_provenance(f"Added node: {node_ref}"),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )

    def add_edge(self, edge_ref: str) -> "KnowledgeGraph":
        """Add an edge reference and return new graph."""
        if edge_ref in self.edge_references:
            return self
        return KnowledgeGraph(
            semantic_identity=self.semantic_identity,
            graph_kind=self.graph_kind,
            node_references=self.node_references,
            edge_references=tuple(self.edge_references + (edge_ref,)),
            graph_constraints=self.graph_constraints,
            graph_metadata=self.graph_metadata,
            layers=self.layers,
            graph_revision=self.graph_revision + 1,
            lifecycle_state=self.lifecycle_state,
            provenance=self._append_provenance(f"Added edge: {edge_ref}"),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )

    def add_layer(self, layer_ref: str) -> "KnowledgeGraph":
        """Add a layer reference and return new graph."""
        if layer_ref in self.layers:
            return self
        return KnowledgeGraph(
            semantic_identity=self.semantic_identity,
            graph_kind=self.graph_kind,
            node_references=self.node_references,
            edge_references=self.edge_references,
            graph_constraints=self.graph_constraints,
            graph_metadata=self.graph_metadata,
            layers=tuple(self.layers + (layer_ref,)),
            graph_revision=self.graph_revision + 1,
            lifecycle_state=self.lifecycle_state,
            provenance=self._append_provenance(f"Added layer: {layer_ref}"),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )

    def with_lifecycle_state(self, new_state: str) -> "KnowledgeGraph":
        """Transition to a new lifecycle state."""
        return KnowledgeGraph(
            semantic_identity=self.semantic_identity,
            graph_kind=self.graph_kind,
            node_references=self.node_references,
            edge_references=self.edge_references,
            graph_constraints=self.graph_constraints,
            graph_metadata=self.graph_metadata,
            layers=self.layers,
            graph_revision=self.graph_revision,
            lifecycle_state=new_state,
            provenance=self._append_provenance(f"State transition: {self.lifecycle_state} -> {new_state}"),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )

    def _append_provenance(self, request: str) -> Tuple[Dict[str, Any], ...]:
        """Append a provenance record."""
        last_chain = list(self.provenance[-1].get("revision_chain", [])) if self.provenance else []
        return tuple(self.provenance) + (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": request,
                "originating_system": "knowledge-graph-system",
                "originating_revision": self.graph_revision + 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": last_chain + [self.semantic_identity],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary for serialization."""
        return {
            "semantic_identity": self.semantic_identity,
            "graph_kind": self.graph_kind,
            "node_references": list(self.node_references),
            "edge_references": list(self.edge_references),
            "graph_constraints": list(self.graph_constraints),
            "graph_metadata": dict(self.graph_metadata),
            "provenance": [p for p in self.provenance],
            "layers": list(self.layers),
            "graph_revision": self.graph_revision,
            "lifecycle_state": self.lifecycle_state,
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeGraph":
        """Create graph from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        return cls(
            semantic_identity=data.get("semantic_identity", ""),
            graph_kind=data.get("graph_kind", "unknown"),
            node_references=tuple(data.get("node_references", [])),
            edge_references=tuple(data.get("edge_references", [])),
            graph_constraints=tuple(data.get("graph_constraints", [])),
            graph_metadata=dict(data.get("graph_metadata", {})),
            provenance=tuple(provenance),
            layers=tuple(data.get("layers", [])),
            graph_revision=int(data.get("graph_revision", 1)),
            lifecycle_state=data.get("lifecycle_state", "created"),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )


# =============================================================================
# KNOWLEDGE SUBGRAPH - Phase 6.8 Part 1 Section 10
# =============================================================================


@dataclass(frozen=True)
class KnowledgeSubgraph:
    """
    Subgraph of a Knowledge Graph.

    Per Part 1 Section 9, large graphs consist of subgraphs.
    Subgraphs remain independently versioned.

    Suggested fields:
        subgraph_identity   - Unique identifier for this subgraph
        parent_graph        - Reference to the parent graph
        participating_nodes - Nodes in this subgraph
        participating_edges - Edges in this subgraph
        scope               - Scope/description of this subgraph
        provenance          - Origin and evolution trail

    Examples of subgraph hierarchies:
        Operating System Graph
            -> Process Graph
            -> Memory Graph
            -> Scheduler Graph
    """

    # Core identity
    subgraph_identity: str

    # Parent graph reference (required)
    parent_graph: str

    # Participating elements
    participating_nodes: Tuple[str, ...] = field(default_factory=tuple)
    participating_edges: Tuple[str, ...] = field(default_factory=tuple)

    # Scope
    scope: str = ""

    # Provenance (required)
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)

    # Version (subgraphs remain independently versioned)
    subgraph_revision: int = 1

    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        """Validate subgraph after creation."""
        if not self.subgraph_identity:
            raise ValueError("subgraph_identity cannot be empty")
        if not self.parent_graph:
            raise ValueError("parent_graph cannot be empty")

    @property
    def is_valid(self) -> bool:
        """Check if subgraph has valid foundational data."""
        return (
            len(self.subgraph_identity) > 0 and
            len(self.parent_graph) > 0
        )

    @classmethod
    def create(
        cls,
        parent_graph: str,
        participating_nodes: Optional[List[str]] = None,
        participating_edges: Optional[List[str]] = None,
        scope: str = "",
    ) -> "KnowledgeSubgraph":
        """
        Create a new Knowledge Subgraph.

        Args:
            parent_graph: Identity of the parent graph
            participating_nodes: Nodes in this subgraph (optional)
            participating_edges: Edges in this subgraph (optional)
            scope: Description of this subgraph's scope (optional)

        Returns:
            New KnowledgeSubgraph with unique identity
        """
        subgraph_id = f"subgraph:{uuid.uuid4().hex[:16]}"

        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Subgraph initialization",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [subgraph_id, parent_graph],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )

        return cls(
            subgraph_identity=subgraph_id,
            parent_graph=parent_graph,
            participating_nodes=tuple(participating_nodes or []),
            participating_edges=tuple(participating_edges or []),
            scope=scope,
            provenance=initial_provenance,
            created_at_utc=time.time(),
        )

    def add_node(self, node_ref: str) -> "KnowledgeSubgraph":
        """Add a node to the subgraph and return new subgraph."""
        if node_ref in self.participating_nodes:
            return self
        return KnowledgeSubgraph(
            subgraph_identity=self.subgraph_identity,
            parent_graph=self.parent_graph,
            participating_nodes=tuple(self.participating_nodes + (node_ref,)),
            participating_edges=self.participating_edges,
            scope=self.scope,
            subgraph_revision=self.subgraph_revision + 1,
            provenance=self._append_provenance(f"Added node: {node_ref}"),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )

    def add_edge(self, edge_ref: str) -> "KnowledgeSubgraph":
        """Add an edge to the subgraph and return new subgraph."""
        if edge_ref in self.participating_edges:
            return self
        return KnowledgeSubgraph(
            subgraph_identity=self.subgraph_identity,
            parent_graph=self.parent_graph,
            participating_nodes=self.participating_nodes,
            participating_edges=tuple(self.participating_edges + (edge_ref,)),
            scope=self.scope,
            subgraph_revision=self.subgraph_revision + 1,
            provenance=self._append_provenance(f"Added edge: {edge_ref}"),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )

    def _append_provenance(self, request: str) -> Tuple[Dict[str, Any], ...]:
        """Append a provenance record."""
        last_chain = list(self.provenance[-1].get("revision_chain", [])) if self.provenance else []
        return tuple(self.provenance) + (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": request,
                "originating_system": "knowledge-graph-system",
                "originating_revision": self.subgraph_revision + 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": last_chain + [self.subgraph_identity],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert subgraph to dictionary for serialization."""
        return {
            "subgraph_identity": self.subgraph_identity,
            "parent_graph": self.parent_graph,
            "participating_nodes": list(self.participating_nodes),
            "participating_edges": list(self.participating_edges),
            "scope": self.scope,
            "provenance": [p for p in self.provenance],
            "subgraph_revision": self.subgraph_revision,
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeSubgraph":
        """Create subgraph from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        return cls(
            subgraph_identity=data.get("subgraph_identity", str(uuid.uuid4())),
            parent_graph=data.get("parent_graph", ""),
            participating_nodes=tuple(data.get("participating_nodes", [])),
            participating_edges=tuple(data.get("participating_edges", [])),
            scope=data.get("scope", ""),
            provenance=tuple(provenance),
            subgraph_revision=int(data.get("subgraph_revision", 1)),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    "KnowledgeGraph",
    "KnowledgeSubgraph",
]