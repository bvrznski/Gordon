# Topology Analysis - Phase 7.9
# =============================

"""
Canonical Topological Analysis.

Topology evaluates:
    connectivity, containment, reachability, adjacency, separation, boundary relationships.
    
Topology remains independent of metric distance.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class TopologicalGraph:
    """
    Explicit topological graph representation.
    
    Nodes represent spatial regions or entities.
    Edges represent topological relationships between them.
    """
    
    # Identity
    graph_id: str                           # Unique identifier
    
    # Nodes - participating entities
    nodes: Tuple[str, ...] = ()             # Node IDs (entity identifiers)
    
    # Edges - topological relationships
    edges: Tuple[Tuple[str, str, str], ...] = ()  # (from_node, to_node, relationship_type)
    
    # Invariants preserved by this graph
    invariants: Tuple[str, ...] = ()
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""
    
    @property
    def node_count(self) -> int:
        """Return number of nodes in graph."""
        return len(self.nodes)
    
    @property
    def edge_count(self) -> int:
        """Return number of edges in graph."""
        return len(self.edges)
    
    def get_neighbors(self, node: str) -> Tuple[str, ...]:
        """Get all neighboring nodes (connected by any edge)."""
        neighbors = set()
        for from_node, to_node, _ in self.edges:
            if from_node == node:
                neighbors.add(to_node)
            elif to_node == node:
                neighbors.add(from_node)
        return tuple(neighbors)


class ConnectivityKind(Enum):
    """Kinds of topological connectivity relationships."""
    
    CONTAINS = "contains"                   # A contains B (A is superset of B)
    WITHIN = "within"                     # A is within B (A is subset of B)
    CONTAINED_IN = "contained_in"         # A is contained in B (same as within)
    OVERLAPS = "overlaps"                 # A and B overlap (intersection non-empty, neither contains other)
    ADJACENT = "adjacent"                 # A and B share a boundary but interiors disjoint
    TOUCHES = "touches"                   # A touches B (boundaries intersect)
    DISJOINT = "disjoint"                 # A and B are completely separate
    CONNECTED = "connected"               # There is a path between nodes
    PATH_CONNECTED = "path_connected"     # There is a continuous path between nodes


@dataclass(frozen=True)
class TopologyAnalysis:
    """
    Result of topological analysis on spatial entities.
    
    Topology evaluates connectivity, containment, reachability,
    adjacency, separation, and boundary relationships.
    """
    
    # Identity
    analysis_id: str                        # Unique identifier
    
    # Graph representation
    graph: TopologicalGraph                 # The computed topological graph
    
    # Invariants determined
    invariants_determined: Tuple[str, ...] = ()
    
    # Connectivity properties
    is_connected: bool = False              # Is the entire space connected?
    component_count: int = 1                # Number of connected components
    
    # Reachability analysis
    reachability_matrix: Tuple[Tuple[bool, ...], ...] = ()  # from_idx -> to_idx可达性
    
    # Boundary relationships
    boundary_pairs: Tuple[Tuple[str, str], ...] = ()
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        graph: TopologicalGraph,
    ) -> TopologyAnalysis:
        """Create a new topology analysis result."""
        return cls(
            analysis_id=f"topology:{uuid.uuid4().hex[:16]}",
            graph=graph,
            created_at_utc=time.time(),
            source_descriptor_id=semantic_identity,
        )
    
    def get_relationship(self, from_node: str, to_node: str) -> Optional[str]:
        """Get relationship type between two nodes."""
        for f, t, rel in self.graph.edges:
            if f == from_node and t == to_node:
                return rel
            if t == from_node and f == to_node:
                # Relationships may be symmetric or we need reverse lookup
                pass
        return None
    
    def get_connected_components(self) -> Tuple[Tuple[str, ...], ...]:
        """Return nodes grouped by connectivity."""
        if not self.graph.nodes:
            return ()
        
        visited = set()
        components = []
        
        for node in self.graph.nodes:
            if node not in visited:
                # BFS to find all connected nodes
                component = []
                queue = [node]
                while queue:
                    current = queue.pop(0)
                    if current not in visited:
                        visited.add(current)
                        component.append(current)
                        for neighbor in self.graph.get_neighbors(current):
                            if neighbor not in visited:
                                queue.append(neighbor)
                components.append(tuple(component))
        
        return tuple(components)


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "TopologyAnalysis",
    "TopologicalGraph",
    "ConnectivityKind",
]