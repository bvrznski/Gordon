# Graph Construction - Phase 7.5
# ==============================

"""
Canonical Causal Graph Construction.

Causal graphs are directed graphs where nodes represent events/states
and edges represent causal influence.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class CausalNode:
    """
    A node in the causal graph representing an event, state, entity,
    process, or condition.
    """
    
    # Identity
    node_id: str                        # Unique node identifier
    
    # Node type
    node_type: str                      # "event", "state", "entity", "process", "condition"
    
    # Semantic content
    semantic_identity: str              # What does this node represent?
    
    # Metadata
    description: str = ""               # Human-readable description
    timestamp_utc: Optional[float] = None  # When did it occur?
    
    @classmethod
    def make_event(cls, event_name: str) -> CausalNode:
        """Create an event node."""
        return cls(
            node_id=f"node:{uuid.uuid4().hex[:8]}",
            node_type="event",
            semantic_identity=event_name,
        )
    
    @classmethod
    def make_state(cls, state_name: str) -> CausalNode:
        """Create a state node."""
        return cls(
            node_id=f"node:{uuid.uuid4().hex[:8]}",
            node_type="state",
            semantic_identity=state_name,
        )


@dataclass(frozen=True)
class CausalEdge:
    """
    An edge in the causal graph representing causal influence.
    """
    
    # Identity
    edge_id: str                        # Unique edge identifier
    
    # Connection
    source_node_id: str                 # Cause
    target_node_id: str                 # Effect
    
    # Causal strength
    strength: float = 1.0               # Strength of causal influence (0-1)
    
    # Supporting mechanism reference
    mechanism_reference: Optional[str] = None  # Which mechanism supports this?
    
    @property
    def is_causal(self) -> bool:
        """Edges in causal graphs are always causal."""
        return True


@dataclass(frozen=True)
class CausalGraph:
    """
    A directed graph representing causal relationships.
    
    Nodes represent events/states/entities/processes/conditions.
    Edges represent causal influence.
    """
    
    # Identity
    graph_id: str                       # Unique graph identifier
    semantic_identity: str              # Semantic identity (stable across runs)
    
    # Graph elements
    causal_nodes: Tuple[CausalNode, ...]  # All nodes
    causal_edges: Tuple[CausalEdge, ...]  # All edges
    
    # Confidence in the graph structure
    confidence: float = 1.0             # Graph confidence (0-1)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @property
    def node_count(self) -> int:
        """Number of nodes in the graph."""
        return len(self.causal_nodes)
    
    @property
    def edge_count(self) -> int:
        """Number of edges in the graph."""
        return len(self.causal_edges)
    
    def get_node_by_id(self, node_id: str) -> Optional[CausalNode]:
        """Get a node by its identifier."""
        for n in self.causal_nodes:
            if n.node_id == node_id:
                return n
        return None
    
    def get_outgoing_edges(self, node_id: str) -> Tuple[CausalEdge, ...]:
        """Get all edges originating from a node."""
        return tuple(e for e in self.causal_edges if e.source_node_id == node_id)
    
    def get_incoming_edges(self, node_id: str) -> Tuple[CausalEdge, ...]:
        """Get all edges terminating at a node."""
        return tuple(e for e in self.causal_edges if e.target_node_id == node_id)


@dataclass(frozen=True)
class GraphConstruction:
    """
    Result of a causal graph construction process.
    
    Construction strategy and resulting graph are preserved.
    """
    
    # Identity
    construction_id: str                # Unique construction identifier
    
    # Construction parameters
    construction_strategy: str          # e.g., "bottom_up", "top_down", "hybrid"
    
    # Resulting graph
    resulting_graph: CausalGraph        # The constructed graph
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()   # Construction diagnostics
    confidence_score: float = 1.0       # Overall confidence in construction
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if graph construction completed."""
        return len(self.diagnostics) == 0 or all(
            d.startswith("info:") for d in self.diagnostics
        )


def make_causal_graph(
    name: str,
    nodes: List[CausalNode],
    edges: List[CausalEdge],
    confidence: float = 1.0,
) -> CausalGraph:
    """Create a new causal graph."""
    return CausalGraph(
        graph_id=f"graph:{uuid.uuid4().hex[:16]}",
        semantic_identity=name,
        causal_nodes=tuple(nodes),
        causal_edges=tuple(edges),
        confidence=confidence,
    )


__all__ = [
    "CausalNode",
    "CausalEdge",
    "CausalGraph",
    "GraphConstruction",
]