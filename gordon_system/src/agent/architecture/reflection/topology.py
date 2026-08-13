"""Topology Inspector - Phase 3.12.7.
================================================================================

Deterministic topology graph inspection for Gordon Core reflection architecture.

Provides:
- TopologyPathFinder - Finds paths in topology graphs
- TopologySummary - Metrics summary
- TopologyAnalysis - Complete analysis result  
- TopologyReport - Report format
- TopologyInspector - Main inspector class
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

from ..discovery.inventory import (
    TopologyNode,
    TopologyEdge,
)


# =============================================================================
# TOPOLOGY DATA MODELS (immutable)
# =============================================================================


@dataclass(frozen=True)
class TopologySummary:
    """Summary metrics for topology."""
    total_nodes: int
    total_edges: int
    categories: Dict[str, int]
    connectivity: float  # 0.0 to 1.0


@dataclass(frozen=True)
class TopologyAnalysis:
    """Complete topology analysis result."""
    nodes: Tuple[TopologyNode, ...]
    edges: Tuple[TopologyEdge, ...]
    summary: TopologySummary
    path_finder: 'TopologyPathFinder'


@dataclass(frozen=True)
class TopologyReport:
    """Topology inspection report."""
    generated_at_utc: float
    repository_path: str
    nodes_count: int
    edges_count: int
    categories: Dict[str, int]
    connectivity: float


# =============================================================================
# TOPOLOGY PATH FINDER
# =============================================================================


class TopologyPathFinder:
    """
    Finds paths in topology graphs.
    
    Uses BFS for shortest path finding.
    Path finding is deterministic and read-only.
    """
    
    def __init__(self, edges: Tuple[TopologyEdge, ...]) -> None:
        """Initialize with topology edges."""
        self._edges = edges
        self._adjacency = self._build_adjacency(edges)
    
    def _build_adjacency(self, edges: Tuple[TopologyEdge, ...]) -> Dict[str, Set[str]]:
        """Build adjacency list from edges."""
        adj: Dict[str, Set[str]] = {}
        for edge in edges:
            if edge.from_node not in adj:
                adj[edge.from_node] = set()
            adj[edge.from_node].add(edge.to_node)
            
            # Undirected for path finding
            if edge.to_node not in adj:
                adj[edge.to_node] = set()
            adj[edge.to_node].add(edge.from_node)
        return adj
    
    def find_path(self, from_entity: str, to_entity: str) -> Optional[Tuple[str, ...]]:
        """
        Find shortest path between two entities.
        
        Returns list of node IDs forming the path, or None if no path exists.
        """
        if from_entity == to_entity:
            return (from_entity,)
        
        visited = {from_entity}
        queue: List[List[str]] = [[from_entity]]
        
        while queue:
            path = queue.pop(0)
            current = path[-1]
            
            for neighbor in self._adjacency.get(current, set()):
                if neighbor == to_entity:
                    return tuple(path + [neighbor])
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        
        return None
    
    def get_neighbors(self, node: str) -> Tuple[str, ...]:
        """Get all neighbors of a node."""
        return tuple(self._adjacency.get(node, set()))


# =============================================================================
# TOPOLOGY INSPECTOR
# =============================================================================


class TopologyInspector:
    """
    Inspector for topology relationships.
    
    Visualizes and analyzes the architectural topology.
    Topology is descriptive, not prescriptive.
    
    This inspector is:
    - Deterministic: Same input always produces same output
    - Read-only: Never modifies anything
    - Passive: Only inspects, never acts
    """
    
    def __init__(self, nodes: Tuple[TopologyNode, ...], 
                 edges: Tuple[TopologyEdge, ...]) -> None:
        """
        Initialize with topology data.
        
        Args:
            nodes: Topology nodes (immutable)
            edges: Topology edges (immutable)
        """
        self._nodes = nodes
        self._edges = edges
        self._path_finder = TopologyPathFinder(edges)
    
    def get_nodes(self) -> Tuple[TopologyNode, ...]:
        """Get all topology nodes."""
        return self._nodes
    
    def get_edges(self) -> Tuple[TopologyEdge, ...]:
        """Get all topology edges."""
        return self._edges
    
    def find_path(self, from_entity: str, to_entity: str) -> Optional[Tuple[str, ...]]:
        """
        Find a path between two entities.
        
        Returns list of node IDs forming the path, or None if no path exists.
        """
        return self._path_finder.find_path(from_entity, to_entity)
    
    def get_category_nodes(self, category: str) -> Tuple[TopologyNode, ...]:
        """Get all nodes in a specific category."""
        return tuple(n for n in self._nodes if n.category == category)
    
    def compute_metrics(self) -> Dict[str, Any]:
        """
        Compute topology metrics.
        
        Returns dictionary of computed metrics (e.g., centrality, connectivity).
        """
        adj: Dict[str, Set[str]] = {}
        for edge in self._edges:
            if edge.from_node not in adj:
                adj[edge.from_node] = set()
            adj[edge.from_node].add(edge.to_node)
            
            if edge.to_node not in adj:
                adj[edge.to_node] = set()
            adj[edge.to_node].add(edge.from_node)
        
        n = len(self._nodes)
        max_edges = n * (n - 1) / 2 if n > 1 else 1
        
        degree_centrality: Dict[str, float] = {}
        for node_id in adj:
            degree_centrality[node_id] = len(adj.get(node_id, set())) / (n - 1) if n > 1 else 0.0
        
        return {
            "total_nodes": n,
            "total_edges": len(self._edges),
            "categories": {node.category: sum(1 for x in self._nodes if x.category == node.category) 
                          for node in self._nodes},
            "connectivity": len(self._edges) / max_edges,
            "degree_centrality": degree_centrality,
        }
    
    def get_analysis(self) -> TopologyAnalysis:
        """Get complete topology analysis."""
        summary = TopologySummary(
            total_nodes=len(self._nodes),
            total_edges=len(self._edges),
            categories={n.category: sum(1 for x in self._nodes if x.category == n.category) 
                       for n in self._nodes},
            connectivity=self._compute_connectivity()
        )
        
        return TopologyAnalysis(
            nodes=self._nodes,
            edges=self._edges,
            summary=summary,
            path_finder=self._path_finder
        )
    
    def _compute_connectivity(self) -> float:
        """Compute graph connectivity metric."""
        n = len(self._nodes)
        if n <= 1:
            return 0.0
        
        max_edges = n * (n - 1) / 2
        return len(self._edges) / max_edges
    
    @property
    def adjacency(self) -> Dict[str, Set[str]]:
        """Get the adjacency list."""
        return self._path_finder._adjacency


def compute_topology_metrics(
    topology: Tuple[TopologyNode, ...],
    edges: Tuple[TopologyEdge, ...]
) -> Dict[str, Any]:
    """
    Compute topology metrics from raw data.
    
    Args:
        topology: Nodes in the topology
        edges: Edges between nodes
        
    Returns:
        Dictionary of computed metrics
    """
    n = len(topology)
    max_edges = n * (n - 1) / 2 if n > 1 else 1
    
    adj: Dict[str, Set[str]] = {}
    for edge in edges:
        if edge.from_node not in adj:
            adj[edge.from_node] = set()
        adj[edge.from_node].add(edge.to_node)
        
        if edge.to_node not in adj:
            adj[edge.to_node] = set()
        adj[edge.to_node].add(edge.from_node)
    
    degree_centrality: Dict[str, float] = {}
    for node in topology:
        degree_centrality[node.id] = len(adj.get(node.id, set())) / (n - 1) if n > 1 else 0.0
    
    return {
        "total_nodes": n,
        "total_edges": len(edges),
        "categories": {node.category: sum(1 for x in topology if x.category == node.category) 
                      for node in topology},
        "connectivity": len(edges) / max_edges,
        "degree_centrality": degree_centrality,
    }