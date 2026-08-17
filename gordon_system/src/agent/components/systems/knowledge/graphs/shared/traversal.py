"""Graph Traversal - Phase 6.8 Part 2.

This module implements the canonical GraphTraversal contract according to 
Gordon Cognitive Architecture specifications (Phase 6.8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# TRAVERSAL STRATEGY - Phase 6.8 Section 15
# =============================================================================


class TraversalStrategy:
    """
    Traversal strategies for graph navigation.
    
    Per TRAVERSAL-LAW-001: Traversal strategies shall remain explicit.
    Per TRAVERSAL-LAW-002: Traversal constraints shall remain explicit.
    
    Strategy kinds:
        BREADTH_FIRST   -> Level-order traversal
        DEPTH_FIRST     -> Depth-first exploration
        WEIGHTED        -> Cost-based traversal
        SEMANTIC        -> Semantically guided traversal
        CONSTRAINT      -> Constraint-driven traversal
        GOAL_DIRECTED   -> Goal-focused search
    """
    
    BREADTH_FIRST = "breadth_first"
    DEPTH_FIRST = "depth_first"
    WEIGHTED = "weighted"
    SEMANTIC = "semantic"
    CONSTRAINT = "constraint"
    GOAL_DIRECTED = "goal_directed"
    
    ALL = {
        BREADTH_FIRST, DEPTH_FIRST, WEIGHTED,
        SEMANTIC, CONSTRAINT, GOAL_DIRECTED,
    }


# =============================================================================
# GRAPH TRAVERSAL SESSION - Phase 6.8 Section 11
# =============================================================================


@dataclass(frozen=True)
class GraphTraversalSession:
    """
    Session describing a single graph traversal execution.
    
    Per TRAVERSAL-LAW-003: Traversal history shall remain reconstructable.
    Per TRAVERSAL-LAW-004: Traversal provenance shall remain complete.
    Per TRAVERSAL-LAW-005: Traversal termination shall remain explicit.
    
    Fields:
        traversal_identity: Unique identifier for this session
        graph: Graph being traversed
        traversal_strategy: Strategy used for navigation
        starting_nodes: Starting point(s) of traversal
        visited_nodes: Nodes encountered during traversal
        traversal_constraints: Constraints applied
        
    Traversal sessions remain reproducible (per TRAVERSAL-LAW-008).
    """
    
    # Core identity
    traversal_identity: str  # Unique session identifier
    
    # Graph reference
    graph: Dict[str, Any] = field(default_factory=dict)
    
    # Strategy (required per TRAVERSAL-LAW-001)
    traversal_strategy: str = TraversalStrategy.DEPTH_FIRST
    
    # Starting points
    starting_nodes: Tuple[str, ...] = field(default_factory=tuple)
    
    # Visited nodes (history for reconstruction)
    visited_nodes: Tuple[str, ...] = field(default_factory=tuple)
    
    # Constraints (required per TRAVERSAL-LAW-002)
    traversal_constraints: Tuple[str, ...] = field(default_factory=tuple)
    
    # Results
    results: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Termination conditions
    termination_reason: str = "not_terminated"
    
    # Provenance (required per TRAVERSAL-LAW-004)
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate traversal session after creation."""
        if not self.traversal_identity:
            raise ValueError("traversal_identity cannot be empty")
        if not self.traversal_strategy or self.traversal_strategy not in TraversalStrategy.ALL:
            raise ValueError(f"Invalid traversal_strategy: {self.traversal_strategy}")
    
    @property
    def is_valid(self) -> bool:
        """Check if session has valid foundational data."""
        return (
            len(self.traversal_identity) > 0 and
            self.traversal_strategy in TraversalStrategy.ALL
        )
    
    @classmethod
    def create_initial(
        cls,
        graph_id: str,
        starting_nodes: Optional[List[str]] = None,
        traversal_strategy: str = TraversalStrategy.DEPTH_FIRST,
        constraints: Optional[List[str]] = None,
    ) -> "GraphTraversalSession":
        """
        Create a new initial traversal session.
        
        Args:
            graph_id: ID of the graph to traverse
            starting_nodes: Starting node(s) (optional)
            traversal_strategy: Strategy for navigation
            constraints: Constraints to apply (optional)
            
        Returns:
            New GraphTraversalSession with unique identity
        """
        traversal_id = f"traversal:{uuid.uuid4().hex[:16]}"
        start_tuple = tuple(starting_nodes or [])
        
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Traversal session initialization",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [traversal_id],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            traversal_identity=traversal_id,
            graph={"graph_identity": graph_id},
            traversal_strategy=traversal_strategy,
            starting_nodes=start_tuple,
            # TRAVERSAL-LAW-003: traversal history (including its origin) remains reconstructable
            visited_nodes=start_tuple,
            traversal_constraints=tuple(constraints or []),
            provenance=initial_provenance,
            created_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "traversal_identity": self.traversal_identity,
            "graph": dict(self.graph),
            "traversal_strategy": self.traversal_strategy,
            "starting_nodes": list(self.starting_nodes),
            "visited_nodes": list(self.visited_nodes),
            "traversal_constraints": list(self.traversal_constraints),
            "results": [r for r in self.results],
            "termination_reason": self.termination_reason,
            "provenance": [p for p in self.provenance],
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphTraversalSession":
        """Create session from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        return cls(
            traversal_identity=data.get("traversal_identity", str(uuid.uuid4())),
            graph=dict(data.get("graph", {})),
            traversal_strategy=data.get("traversal_strategy", TraversalStrategy.DEPTH_FIRST),
            starting_nodes=tuple(data.get("starting_nodes", [])),
            visited_nodes=tuple(data.get("visited_nodes", [])),
            traversal_constraints=tuple(data.get("traversal_constraints", [])),
            results=tuple(data.get("results", [])),
            termination_reason=data.get("termination_reason", "not_terminated"),
            provenance=tuple(provenance),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )
    
    def visit_node(self, node_id: str) -> "GraphTraversalSession":
        """Visit a node and return new session state."""
        if node_id in self.visited_nodes:
            return self
        
        return GraphTraversalSession(
            traversal_identity=self.traversal_identity,
            graph=self.graph,
            traversal_strategy=self.traversal_strategy,
            starting_nodes=self.starting_nodes,
            visited_nodes=tuple(set(self.visited_nodes) | {node_id}),
            traversal_constraints=self.traversal_constraints,
            results=self.results,
            termination_reason=self.termination_reason,
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": f"Visited node: {node_id}",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.traversal_identity] if self.provenance else [self.traversal_identity],
                "authority": "system",
                "timestamp_utc": time.time(),
            }]),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )
    
    def add_result(self, result: Dict[str, Any]) -> "GraphTraversalSession":
        """Add a traversal result and return new session state."""
        return GraphTraversalSession(
            traversal_identity=self.traversal_identity,
            graph=self.graph,
            traversal_strategy=self.traversal_strategy,
            starting_nodes=self.starting_nodes,
            visited_nodes=self.visited_nodes,
            traversal_constraints=self.traversal_constraints,
            results=tuple(list(self.results) + [result]),
            termination_reason=self.termination_reason,
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": f"Added traversal result",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.traversal_identity] if self.provenance else [self.traversal_identity],
                "authority": "system",
                "timestamp_utc": time.time(),
            }]),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )
    
    def terminate(self, reason: str) -> "GraphTraversalSession":
        """Mark traversal as terminated with a reason."""
        return GraphTraversalSession(
            traversal_identity=self.traversal_identity,
            graph=self.graph,
            traversal_strategy=self.traversal_strategy,
            starting_nodes=self.starting_nodes,
            visited_nodes=self.visited_nodes,
            traversal_constraints=self.traversal_constraints,
            results=self.results,
            termination_reason=reason,
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": f"Terminated: {reason}",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.traversal_identity] if self.provenance else [self.traversal_identity],
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
    # Traversal strategy (Phase 6.8 Section 15)
    "TraversalStrategy",
    # Graph traversal session (Phase 6.8 Section 11)
    "GraphTraversalSession",
]