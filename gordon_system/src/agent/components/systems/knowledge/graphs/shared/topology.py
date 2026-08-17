"""Graph Topology - Phase 6.8 Part 2.

This module implements the canonical GraphTopology contract according to 
Gordon Cognitive Architecture specifications (Phase 6.8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# TOPOLOGY KINDS - Phase 6.8 Section 6
# =============================================================================


class TopologyKind:
    """
    Kinds of graph topologies.
    
    Per TOPOLOGY-LAW-001: Topology shall remain explicitly declared.
    Per TOPOLOGY-LAW-002: Topology constraints shall remain explicit.
    
    Topology kinds:
        TREE         -> Hierarchical tree structure
        DAG          -> Directed acyclic graph
        CYCLIC       -> Graph with possible cycles
        HETEROGENEOUS -> Mixed topology types
        HYPERGRAPH   -> Edges can connect multiple nodes
        MULTI_LAYER  -> Multiple layers of graphs
    """
    
    TREE = "tree"
    DAG = "dag"
    CYCLIC = "cyclic"
    HETEROGENEOUS = "heterogeneous"
    HYPERGRAPH = "hypergraph"
    MULTI_LAYER = "multi_layer"
    
    ALL = {TREE, DAG, CYCLIC, HETEROGENEOUS, HYPERGRAPH, MULTI_LAYER}


# =============================================================================
# GRAPH METRICS - Phase 6.8 Section 24
# =============================================================================


@dataclass(frozen=True)
class GraphMetrics:
    """
    Metrics describing graph structure and health.
    
    Per TOPOLOGY-LAW-005: Topology validation shall remain inspectable.
    
    Fields:
        node_count: Total number of nodes in the graph
        edge_count: Total number of edges in the graph
        average_degree: Average connections per node
        connected_components: Number of disconnected components
        density: Edge count relative to maximum possible
        max_depth: Maximum depth (for tree-like graphs)
        avg_path_length: Average shortest path length
        clustering_coefficient: Local clustering measure
    """
    
    node_count: int = 0
    edge_count: int = 0
    average_degree: float = 0.0
    connected_components: int = 1
    density: float = 0.0
    max_depth: int = 0
    avg_path_length: float = 0.0
    clustering_coefficient: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "average_degree": self.average_degree,
            "connected_components": self.connected_components,
            "density": self.density,
            "max_depth": self.max_depth,
            "avg_path_length": self.avg_path_length,
            "clustering_coefficient": self.clustering_coefficient,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GraphMetrics:
        """Create metrics from dictionary."""
        return cls(
            node_count=int(data.get("node_count", 0)),
            edge_count=int(data.get("edge_count", 0)),
            average_degree=float(data.get("average_degree", 0.0)),
            connected_components=int(data.get("connected_components", 1)),
            density=float(data.get("density", 0.0)),
            max_depth=int(data.get("max_depth", 0)),
            avg_path_length=float(data.get("avg_path_length", 0.0)),
            clustering_coefficient=float(data.get("clustering_coefficient", 0.0)),
        )


# =============================================================================
# GRAPH TOPOLOGY - Phase 6.8 Section 6
# =============================================================================


@dataclass(frozen=True)
class GraphTopology:
    """
    Topology descriptor for a Knowledge Graph.
    
    Per TOPOLOGY-LAW-001: Topology shall remain explicitly declared.
    Per TOPOLOGY-LAW-002: Topology constraints shall remain explicit.
    Per TOPOLOGY-LAW-003: Topology revisions shall preserve history.
    Per TOPOLOGY-LAW-004: Topology provenance shall remain complete.
    
    Fields:
        topology_identity: Unique identifier for this topology
        topology_kind: Kind of topology (tree, DAG, cyclic, etc.)
        supported_constraints: Constraints that can be validated
        graph_metrics: Structural metrics describing the graph
        
    Topology describes graph organization without defining it.
    """
    
    # Core identity
    topology_identity: str  # Unique topology identifier
    
    # Topology kind (required per TOPOLOGY-LAW-001)
    topology_kind: str
    
    # Constraints (required per TOPOLOGY-LAW-002)
    supported_constraints: Tuple[str, ...] = field(default_factory=tuple)
    
    # Graph metrics
    graph_metrics: GraphMetrics = field(default_factory=GraphMetrics)
    
    # Provenance (required per TOPOLOGY-LAW-004)
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate topology after creation."""
        if not self.topology_identity:
            raise ValueError("topology_identity cannot be empty")
        if not self.topology_kind or self.topology_kind not in TopologyKind.ALL:
            raise ValueError(f"Invalid topology_kind: {self.topology_kind}")
    
    @property
    def is_valid(self) -> bool:
        """Check if topology has valid foundational data."""
        return (
            len(self.topology_identity) > 0 and
            self.topology_kind in TopologyKind.ALL
        )
    
    @classmethod
    def create_initial(
        cls,
        topology_kind: str,
        supported_constraints: Optional[List[str]] = None,
        node_count: int = 0,
        edge_count: int = 0,
    ) -> "GraphTopology":
        """
        Create a new initial topology descriptor.
        
        Args:
            topology_kind: Kind of topology (tree, DAG, cyclic, etc.)
            supported_constraints: Validation constraints (optional)
            node_count: Initial node count
            edge_count: Initial edge count
            
        Returns:
            New GraphTopology with unique topology_identity
        """
        topology_id = f"topology:{uuid.uuid4().hex[:16]}"
        
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Topology initialization",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [topology_id],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )
        
        metrics = GraphMetrics(
            node_count=node_count,
            edge_count=edge_count,
        )
        
        return cls(
            topology_identity=topology_id,
            topology_kind=topology_kind,
            supported_constraints=tuple(supported_constraints or []),
            graph_metrics=metrics,
            provenance=initial_provenance,
            created_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert topology to dictionary for serialization."""
        return {
            "topology_identity": self.topology_identity,
            "topology_kind": self.topology_kind,
            "supported_constraints": list(self.supported_constraints),
            "graph_metrics": self.graph_metrics.to_dict(),
            "provenance": [p for p in self.provenance],
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphTopology":
        """Create topology from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        return cls(
            topology_identity=data.get("topology_identity", str(uuid.uuid4())),
            topology_kind=data.get("topology_kind", ""),
            supported_constraints=tuple(data.get("supported_constraints", [])),
            graph_metrics=GraphMetrics.from_dict(data.get("graph_metrics", {})),
            provenance=tuple(provenance),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )
    
    def with_metrics(self, new_metrics: GraphMetrics) -> "GraphTopology":
        """Update metrics and return new topology."""
        return GraphTopology(
            topology_identity=self.topology_identity,
            topology_kind=self.topology_kind,
            supported_constraints=self.supported_constraints,
            graph_metrics=new_metrics,
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Topology metrics update",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.topology_identity] if self.provenance else [self.topology_identity],
                "authority": "system",
                "timestamp_utc": time.time(),
            }]),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Topology kinds (Phase 6.8 Section 6)
    "TopologyKind",
    # Graph metrics (Phase 6.8 Section 24)
    "GraphMetrics",
    # Graph topology (Phase 6.8 Section 6)
    "GraphTopology",
]