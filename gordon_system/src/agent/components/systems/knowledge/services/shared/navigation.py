"""Navigation Service - Phase 6.9 Part 2 Section 9.

This module implements the canonical contract for graph navigation in
Knowledge Services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# TRAVERSAL STRATEGY - Phase 6.9 Part 2 Section 9
# =============================================================================


class TraversalStrategy(Enum):
    """
    Strategies for graph navigation.
    
    Graph-Based:
        BREADTH_FIRST     -> BFS traversal
        DEPTH_FIRST       -> DFS traversal
        
    Semantic-Based:
        SEMANTIC          -> Semantic-aware traversal
        CONSTRAINT        -> Constraint-based filtering
        
    Goal-Oriented:
        PATH_FINDING      -> Find path between nodes
        REACHABILITY      -> Check reachability
        
    Mixed:
        HYBRID            -> Combined strategies
    """
    
    BREADTH_FIRST = "breadth_first"
    DEPTH_FIRST = "depth_first"
    SEMANTIC = "semantic"
    CONSTRAINT = "constraint"
    PATH_FINDING = "path_finding"
    REACHABILITY = "reachability"
    HYBRID = "hybrid"


# =============================================================================
# TERMINATION CONDITION - Phase 6.9 Part 2 Section 9
# =============================================================================


class TerminationCondition(Enum):
    """
    Conditions for navigation termination.
    
    Per NAVIGATION-LAW-005: Navigation history shall remain immutable.
    """
    
    NO_MORE_NODES = "no_more_nodes"     # No more unvisited nodes
    MAX_DEPTH_REACHED = "max_depth_reached"
    TARGET_FOUND = "target_found"
    CONSTRAINT_SATISFIED = "constraint_satisfied"
    TIMEOUT = "timeout"
    RESOURCE_LIMIT = "resource_limit"
    CUSTOM = "custom"


# =============================================================================
# NAVIGATION PATH - Phase 6.9 Part 2 Section 9
# =============================================================================


@dataclass(frozen=True)
class NavigationPath:
    """
    Path through the semantic graph.
    
    Per NAVIGATION-LAW-005: Navigation history shall remain immutable.
    
    Fields:
        path_identity: Unique identifier for this path
        start_node: Starting node of the path
        end_node: Ending node of the path (if known)
        nodes_traversed: Ordered list of nodes visited
        edges_used: Edges used to traverse between nodes
    """
    
    path_identity: str  # Unique identifier
    
    start_node: str
    end_node: Optional[str] = None
    
    nodes_traversed: Tuple[str, ...] = field(default_factory=tuple)
    edges_used: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    def __post_init__(self) -> None:
        """Validate path after creation."""
        if not self.path_identity:
            raise ValueError("path_identity cannot be empty")
    
    @property
    def length(self) -> int:
        """Number of edges in the path (nodes - 1)."""
        # For a path with N nodes, there are N-1 edges
        if len(self.nodes_traversed) <= 1:
            return 0
        return len(self.nodes_traversed) - 1
    
    @classmethod
    def create_initial(
        cls,
        start_node: str,
    ) -> "NavigationPath":
        """Create initial navigation path starting from given node."""
        return cls(
            path_identity=f"path:{uuid.uuid4().hex[:16]}",
            start_node=start_node,
            nodes_traversed=(start_node,),
        )
    
    def extend(
        self,
        next_node: str,
        edge_info: Optional[Dict[str, Any]] = None,
    ) -> "NavigationPath":
        """Extend path by one node and optionally one edge."""
        new_nodes = tuple(list(self.nodes_traversed) + [next_node])
        new_edges = tuple(list(self.edges_used) + [edge_info] if edge_info else [])
        
        return NavigationPath(
            path_identity=self.path_identity,
            start_node=self.start_node,
            end_node=next_node,
            nodes_traversed=new_nodes,
            edges_used=new_edges,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert path to dictionary."""
        return {
            "path_identity": self.path_identity,
            "start_node": self.start_node,
            "end_node": self.end_node,
            "nodes_traversed": list(self.nodes_traversed),
            "edges_used": list(self.edges_used),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NavigationPath":
        """Create path from dictionary."""
        return cls(
            path_identity=data.get("path_identity", str(uuid.uuid4())),
            start_node=data.get("start_node", ""),
            end_node=data.get("end_node"),
            nodes_traversed=tuple(data.get("nodes_traversed", [])),
            edges_used=tuple(data.get("edges_used", [])),
        )


# =============================================================================
# NAVIGATION SESSION - Phase 6.9 Part 2 Section 9
# =============================================================================


@dataclass(frozen=True)
class NavigationSession:
    """
    Session for graph navigation operations.
    
    Per NAVIGATION-LAW-005: Navigation history shall remain immutable.
    Per NAVIGATION-LAW-007: Navigation sessions shall remain inspectable.
    
    Fields:
        navigation_identity: Unique identifier for this session
        graph: Graph being navigated
        traversal_strategy: Strategy used for navigation
        
    Invariants:
        * Traversal strategies are explicit (NAVIGATION-LAW-002)
        * Constraints are explicit (NAVIGATION-LAW-003)
        * History is immutable and traceable
    """
    
    navigation_identity: str  # Unique identifier
    
    # Graph being navigated (required)
    graph: Dict[str, Any]
    
    # Traversal strategy (Per NAVIGATION-LAW-002)
    traversal_strategy: TraversalStrategy
    
    # Starting nodes (Per NAVIGATION-LAW-001 context)
    starting_nodes: Tuple[str, ...] = field(default_factory=tuple)
    
    # Constraints (Per NAVIGATION-LAW-003)
    constraints: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Navigation history
    visited_nodes: Tuple[str, ...] = field(default_factory=tuple)
    resulting_paths: Tuple[NavigationPath, ...] = field(default_factory=tuple)
    
    # Termination (Per NAVIGATION-LAW-005 context)
    termination_reason: Optional[TerminationCondition] = None
    termination_message: str = ""
    
    def __post_init__(self) -> None:
        """Validate session after creation."""
        if not self.navigation_identity:
            raise ValueError("navigation_identity cannot be empty")
    
    @property
    def node_count(self) -> int:
        """Number of nodes visited so far."""
        return len(self.visited_nodes)
    
    @classmethod
    def create_initial(
        cls,
        graph: Dict[str, Any],
        traversal_strategy: TraversalStrategy,
        starting_nodes: Optional[List[str]] = None,
    ) -> "NavigationSession":
        """
        Create a new initial navigation session.
        
        Args:
            graph: Graph to navigate
            traversal_strategy: Strategy for traversal
            starting_nodes: Initial nodes to start from (optional)
            
        Returns:
            New NavigationSession ready for navigation
        """
        return cls(
            navigation_identity=f"navigation:{uuid.uuid4().hex[:16]}",
            graph=dict(graph),
            traversal_strategy=traversal_strategy,
            starting_nodes=tuple(starting_nodes or []),
        )
    
    def visit_node(
        self,
        node_id: str,
        edge_info: Optional[Dict[str, Any]] = None,
    ) -> "NavigationSession":
        """Visit a node and record the navigation step."""
        if node_id in self.visited_nodes:
            return self  # Already visited
        
        new_paths = tuple(list(self.resulting_paths) + [
            NavigationPath(
                path_identity=f"path:{uuid.uuid4().hex[:16]}",
                start_node=self.starting_nodes[0] if self.starting_nodes else node_id,
                end_node=node_id,
                nodes_traversed=tuple(list(self.visited_nodes) + [node_id]) if self.visited_nodes else (node_id,),
                edges_used=(edge_info,) if edge_info else (),
            ),
        ])
        
        return NavigationSession(
            navigation_identity=self.navigation_identity,
            graph=dict(self.graph),
            traversal_strategy=self.traversal_strategy,
            starting_nodes=self.starting_nodes,
            constraints=self.constraints,
            visited_nodes=tuple(list(self.visited_nodes) + [node_id]),
            resulting_paths=new_paths,
            termination_reason=self.termination_reason,
            termination_message=self.termination_message,
        )
    
    def add_constraint(
        self,
        constraint: Dict[str, Any],
    ) -> "NavigationSession":
        """Add a navigation constraint."""
        return NavigationSession(
            navigation_identity=self.navigation_identity,
            graph=dict(self.graph),
            traversal_strategy=self.traversal_strategy,
            starting_nodes=self.starting_nodes,
            constraints=tuple(list(self.constraints) + [constraint]),
            visited_nodes=self.visited_nodes,
            resulting_paths=self.resulting_paths,
            termination_reason=self.termination_reason,
            termination_message=self.termination_message,
        )
    
    def terminate(
        self,
        reason: TerminationCondition,
        message: str = "",
    ) -> "NavigationSession":
        """Mark navigation as terminated."""
        return NavigationSession(
            navigation_identity=self.navigation_identity,
            graph=dict(self.graph),
            traversal_strategy=self.traversal_strategy,
            starting_nodes=self.starting_nodes,
            constraints=self.constraints,
            visited_nodes=self.visited_nodes,
            resulting_paths=self.resulting_paths,
            termination_reason=reason,
            termination_message=message,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "navigation_identity": self.navigation_identity,
            "graph": dict(self.graph),
            "traversal_strategy": self.traversal_strategy.value,
            "starting_nodes": list(self.starting_nodes),
            "constraints": list(self.constraints),
            "visited_nodes": list(self.visited_nodes),
            "resulting_paths": [p.to_dict() for p in self.resulting_paths],
            "termination_reason": self.termination_reason.value if self.termination_reason else None,
            "termination_message": self.termination_message,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NavigationSession":
        """Create session from dictionary."""
        paths = []
        for p_data in data.get("resulting_paths", []):
            if isinstance(p_data, dict):
                paths.append(NavigationPath.from_dict(p_data))
        
        return cls(
            navigation_identity=data.get("navigation_identity", str(uuid.uuid4())),
            graph=dict(data.get("graph", {})),
            traversal_strategy=TraversalStrategy(data.get("traversal_strategy", "breadth_first")),
            starting_nodes=tuple(data.get("starting_nodes", [])),
            constraints=tuple(data.get("constraints", [])),
            visited_nodes=tuple(data.get("visited_nodes", [])),
            resulting_paths=tuple(paths),
            termination_reason=TerminationCondition(data.get("termination_reason")) if data.get("termination_reason") else None,
            termination_message=data.get("termination_message", ""),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Traversal strategies (Part 2 Section 9)
    "TraversalStrategy",
    # Termination conditions
    "TerminationCondition",
    # Navigation path
    "NavigationPath",
    # Navigation session
    "NavigationSession",
]