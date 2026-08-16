# Motivational Projection Network - Projection Graph (Phase 4.10.6)
# ================================================================
#
# The ProjectionGraph represents relationships between drive projections.
# It never contains executable behavior, only semantic relationships.

"""
ProjectionGraph model for Phase 4.10.6.

This module defines the canonical projection graph data structure that represents
relationships between DriveProjections in motivational space.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, Dict, Set


class GraphEdgeType(Enum):
    """
    Canonical edge types for projection graphs.

    GRAPH-LAW-001: ProjectionGraph remains immutable.
    GRAPH-LAW-002: All edges remain explicitly typed.
    GRAPH-LAW-003: Edge semantics remain descriptive (never prescriptive).
    """
    
    # Positive relationships
    SUPPORTS = "supports"
    """Projection A supports projection B (mutually reinforcing)."""
    
    REINFORCES = "reinforces"
    """Projection A reinforces projection B (strengthens presence)."""
    
    SYNERGIZES_WITH = "synergizes_with"
    """Projections synergize (combined effect > sum of parts)."""
    
    # Negative relationships
    CONFLICTS_WITH = "conflicts_with"
    """Projection A conflicts with projection B (opposing values)."""
    
    COMPETES_WITH = "competes_with"
    """Projection A competes with projection B (zero-sum potential)."""
    
    SUPPRESSES = "suppresses"
    """Projection A suppresses projection B (reduces effect)."""
    
    # Hierarchical relationships
    DERIVED_FROM = "derived_from"
    """Projection A is derived from projection B."""
    
    # Temporal relationships
    PRECEDES = "precedes"
    """Projection A temporally precedes projection B."""
    
    PARALLEL_TO = "parallel_to"
    """Projections occur in parallel (independent timing)."""
    
    # Unknown relationship
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class GraphEdge:
    """
    An edge in the projection graph.

    GRAPH-LAW-004: Edges preserve provenance.
    GRAPH-LAW-005: Edge confidence remains independent.
    GRAPH-LAW-006: Edges shall never contain executable behavior.
    """
    
    source_projection_id: str
    """Source projection ID."""
    
    target_projection_id: str
    """Target projection ID."""
    
    edge_type: GraphEdgeType = GraphEdgeType.UNKNOWN
    """Type of relationship between projections."""
    
    confidence: float = 1.0
    """Confidence in the edge (0.0-1.0)."""
    
    provenance: str = "unknown"
    """Source information for traceability."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.source_projection_id}→{self.edge_type.value}→{self.target_projection_id}"
    
    def to_dict(self) -> dict:
        """Convert edge to dictionary representation."""
        return {
            "edge_id": self.canonical_identity,
            "source_projection_id": self.source_projection_id,
            "target_projection_id": self.target_projection_id,
            "edge_type": self.edge_type.value,
            "confidence": self.confidence,
            "provenance": self.provenance,
        }
    
    @classmethod
    def create(
        cls,
        source: str,
        target: str,
        edge_type: GraphEdgeType = GraphEdgeType.UNKNOWN,
        confidence: float = 1.0,
        provenance: str = "unknown",
    ) -> GraphEdge:
        """Create a new graph edge."""
        return cls(
            source_projection_id=source,
            target_projection_id=target,
            edge_type=edge_type,
            confidence=confidence,
            provenance=provenance,
        )


@dataclass(frozen=True)
class ProjectionGraph:
    """
    An immutable graph of projection relationships.

    GRAPH-LAW-007: Graph preserves hierarchy.
    GRAPH-LAW-008: Graph preserves temporal partitions.
    
    NOT RESPONSIBLE FOR:
        • Executing projections
        • Modifying drive states
        • Making decisions
    """
    
    graph_id: str = "projection_graph"
    """Unique identifier for this graph."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    nodes: Tuple[str, ...] = field(default_factory=tuple)
    """All projection IDs (nodes in the graph)."""
    
    edges: Tuple[GraphEdge, ...] = field(default_factory=tuple)
    """Edges representing relationships between projections."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.graph_id}@v{self.revision}"
    
    @property
    def node_count(self) -> int:
        """Get count of nodes (projections)."""
        return len(self.nodes)
    
    @property
    def edge_count(self) -> int:
        """Get count of edges."""
        return len(self.edges)
    
    @property
    def adjacency_list(self) -> Dict[str, Set[str]]:
        """
        Build an adjacency list representation.
        
        Returns:
            Dict mapping source node to set of target nodes
        """
        adj: Dict[str, Set[str]] = {}
        for edge in self.edges:
            src = edge.source_projection_id
            if src not in adj:
                adj[src] = set()
            adj[src].add(edge.target_projection_id)
        return adj
    
    def get_outgoing(self, node: str) -> Tuple[GraphEdge, ...]:
        """Get all outgoing edges from a node."""
        return tuple(e for e in self.edges if e.source_projection_id == node)
    
    def get_incoming(self, node: str) -> Tuple[GraphEdge, ...]:
        """Get all incoming edges to a node."""
        return tuple(e for e in self.edges if e.target_projection_id == node)
    
    def has_edge(
        self,
        source: str,
        target: str,
        edge_type: GraphEdgeType = None,
    ) -> bool:
        """Check if an edge exists between two nodes."""
        for edge in self.edges:
            if (edge.source_projection_id == source 
                and edge.target_projection_id == target):
                if edge_type is None or edge.edge_type == edge_type:
                    return True
        return False
    
    def find_conflicts(self) -> Tuple[GraphEdge, ...]:
        """Find all conflict edges in the graph."""
        return tuple(
            e for e in self.edges
            if e.edge_type in (
                GraphEdgeType.CONFLICTS_WITH,
                GraphEdgeType.COMPETES_WITH,
                GraphEdgeType.SUPPRESSES,
            )
        )
    
    def find_supports(self) -> Tuple[GraphEdge, ...]:
        """Find all support edges in the graph."""
        return tuple(
            e for e in self.edges
            if e.edge_type in (
                GraphEdgeType.SUPPORTS,
                GraphEdgeType.REINFORCES,
                GraphEdgeType.SYNERGIZES_WITH,
            )
        )
    
    def to_dict(self) -> dict:
        """Convert graph to dictionary representation."""
        return {
            "graph_id": self.graph_id,
            "revision": self.revision,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "nodes": list(self.nodes),
            "edges": [e.to_dict() for e in self.edges],
        }
    
    @classmethod
    def create_empty(cls, graph_id: str = "projection_graph") -> ProjectionGraph:
        """Create an empty projection graph."""
        return cls(graph_id=graph_id)
    
    @classmethod
    def from_nodes_and_edges(
        cls,
        nodes: Tuple[str, ...],
        edges: Tuple[GraphEdge, ...],
        graph_id: str = "projection_graph",
    ) -> ProjectionGraph:
        """Create a graph from nodes and edges."""
        return cls(
            graph_id=graph_id,
            revision=0,
            nodes=tuple(sorted(set(nodes))),
            edges=edges,
        )
    
    @classmethod
    def from_edges(
        cls,
        edges: Tuple[GraphEdge, ...],
        graph_id: str = "projection_graph",
    ) -> ProjectionGraph:
        """Create a graph from edges, extracting nodes."""
        nodes = set()
        for edge in edges:
            nodes.add(edge.source_projection_id)
            nodes.add(edge.target_projection_id)
        
        return cls(
            graph_id=graph_id,
            revision=0,
            nodes=tuple(sorted(nodes)),
            edges=edges,
        )


__all__ = [
    "GraphEdgeType",
    "GraphEdge",
    "ProjectionGraph",
]