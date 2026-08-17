# Temporal Dependency Graph - Phase 7.8
# ======================================

"""
Canonical Temporal Dependency Graph.

Temporal dependencies form explicit graphs for reasoning about event orderings.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum, auto


class DependencyType(Enum):
    """Types of temporal dependencies."""
    
    PRECEDENCE = "precedence"               # Event A must precede event B
    DEPENDENCY = "dependency"               # Event B depends on event A
    SYNCHRONIZATION = "synchronization"     # Events must synchronize at a point
    CAUSAL = "causal"                       # Event A causally affects event B
    TEMPORAL = "temporal"                   # Purely temporal ordering


@dataclass(frozen=True)
class DependencyNode:
    """
    Node in the temporal dependency graph.
    
    Nodes represent:
        - Events
        - Intervals
        - Milestones
    """
    
    # Identity
    node_id: str                            # Unique node identifier
    
    # Node type and content
    node_type: str                          # "event", "interval", "milestone"
    semantic_identity: str                  # Semantic identity of the referenced object
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    def __hash__(self) -> int:
        return hash(self.node_id)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, DependencyNode):
            return self.node_id == other.node_id
        return False


@dataclass(frozen=True)
class DependencyEdge:
    """
    Edge in the temporal dependency graph.
    
    Edges represent:
        - Precedence relationships
        - Dependencies
        - Synchronization requirements
    """
    
    # Identity
    edge_id: str                            # Unique edge identifier
    
    # Connection
    source_node_id: str                     # Source node ID
    target_node_id: str                     # Target node ID
    
    # Edge type and properties
    dependency_type: DependencyType         # What kind of dependency?
    direction: Tuple[str, str] = ("from", "to")  # Direction annotation
    
    # Strength and confidence
    strength: float = 1.0                   # Dependency strength (0.0 to 1.0)
    confidence: float = 1.0                 # Confidence in the dependency
    
    # Provenance
    source_edge_id: Optional[str] = None    # If derived from another edge
    origin_system: str = "unknown"          # Where did the edge originate?
    
    def __hash__(self) -> int:
        return hash(self.edge_id)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, DependencyEdge):
            return self.edge_id == other.edge_id
        return False


@dataclass(frozen=True)
class TemporalDependencyGraph:
    """
    Graph representing temporal dependencies between events.
    
    Nodes represent events/intervals/milestones. Edges represent dependencies.
    
    The graph remains inspectable.
    """
    
    # Identity
    graph_id: str                           # Unique graph identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Graph structure
    dependency_nodes: Tuple[DependencyNode, ...]
    dependency_edges: Tuple[DependencyEdge, ...]
    
    # Consistency assessment
    consistency: float = 1.0                # Consistency score (0.0 to 1.0)
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_graph_id: Optional[str] = None   # If derived from another graph
    origin_context: str = "unknown"         # Where did the graph originate?
    
    @property
    def node_count(self) -> int:
        """Return the number of nodes in this graph."""
        return len(self.dependency_nodes)
    
    @property
    def edge_count(self) -> int:
        """Return the number of edges in this graph."""
        return len(self.dependency_edges)
    
    @property
    def has_cycles(self) -> bool:
        """Check if the dependency graph contains cycles."""
        adjacency: Dict[str, Set[str]] = {node.node_id: set() for node in self.dependency_nodes}
        
        for edge in self.dependency_edges:
            if edge.target_node_id in adjacency:
                adjacency[edge.source_node_id].add(edge.target_node_id)
        
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in adjacency.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node_id in adjacency:
            if node_id not in visited:
                if dfs(node_id):
                    return True
        return False
    
    def get_successors(self, node_id: str) -> Tuple[str, ...]:
        """Get nodes that depend on the given node."""
        successors = []
        for edge in self.dependency_edges:
            if edge.source_node_id == node_id and edge.target_node_id not in successors:
                successors.append(edge.target_node_id)
        return tuple(successors)
    
    def get_predecessors(self, node_id: str) -> Tuple[str, ...]:
        """Get nodes that the given node depends on."""
        predecessors = []
        for edge in self.dependency_edges:
            if edge.target_node_id == node_id and edge.source_node_id not in predecessors:
                predecessors.append(edge.source_node_id)
        return tuple(predecessors)


@dataclass(frozen=True)
class DependencyGraphIdentity:
    """
    Immutable identity for a dependency graph.
    
    Allows replay and verification of dependency analysis results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Context
    graph_number: int = 1                     # For repeated graphs
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, graph_number: int = 1) -> DependencyGraphIdentity:
        """Create a new dependency graph identity."""
        return cls(
            semantic_identity=semantic_identity,
            graph_number=graph_number,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DependencyNode",
    "DependencyEdge",
    "TemporalDependencyGraph",
    "DependencyGraphIdentity",
    "DependencyType",
]