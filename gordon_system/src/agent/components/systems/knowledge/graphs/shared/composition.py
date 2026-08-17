"""Graph Composition - Phase 6.8 Part 2.

This module implements the canonical graph composition contracts according to 
Gordon Cognitive Architecture specifications (Phase 6.8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# COMPOSITION STRATEGY - Phase 6.8 Section 15
# =============================================================================


class CompositionStrategy:
    """
    Strategies for graph composition.
    
    Per PARTITION-LAW-006: Partition merging shall remain deterministic.
    
    Strategy kinds:
        UNION         -> Combine all nodes and edges from both graphs
        INTERSECTION  -> Keep only elements present in both graphs
        DIFFERENCE    -> Remove elements of one graph from another
        MERGE         -> Combine with conflict resolution
        NESTED        -> One graph embedded within another
        
    Composition preserves graph identity (per Phase 6.8 Part 2 Section 15).
    """
    
    UNION = "union"
    INTERSECTION = "intersection"
    DIFFERENCE = "difference"
    MERGE = "merge"
    NESTED = "nested"
    
    ALL = {UNION, INTERSECTION, DIFFERENCE, MERGE, NESTED}


# =============================================================================
# GRAPH COMPOSITION - Phase 6.8 Section 15
# =============================================================================


@dataclass(frozen=True)
class GraphComposition:
    """
    Composition of multiple graphs into one.
    
    Per PARTITION-LAW-001: Graph partitions shall preserve semantic connectivity.
    Per PARTITION-LAW-003: Cross-partition edges shall remain explicit.
    
    Fields:
        composition_identity: Unique identifier for this composition
        participating_graphs: Graphs being composed
        resulting_graph: Identity of the result graph
        composition_strategy: Strategy used for composition
        
    Composition preserves graph identity - it doesn't create new semantics,
    only new organization (per Phase 6.8 Part 2 Section 15).
    """
    
    # Core identity
    composition_identity: str  # Unique composition identifier
    
    # Participating graphs
    participating_graphs: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Resulting graph reference
    resulting_graph: Dict[str, Any] = field(default_factory=dict)
    
    # Strategy (required per PARTITION-LAW-006)
    composition_strategy: str = CompositionStrategy.UNION
    
    # Cross-graph relationships
    cross_graph_edges: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Provenance
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate composition after creation."""
        if not self.composition_identity:
            raise ValueError("composition_identity cannot be empty")
        if not self.composition_strategy or self.composition_strategy not in CompositionStrategy.ALL:
            raise ValueError(f"Invalid composition_strategy: {self.composition_strategy}")
    
    @property
    def is_valid(self) -> bool:
        """Check if composition has valid foundational data."""
        return (
            len(self.composition_identity) > 0 and
            self.composition_strategy in CompositionStrategy.ALL and
            len(self.participating_graphs) >= 1
        )
    
    @classmethod
    def create_initial(
        cls,
        participating_graph_ids: List[str],
        composition_strategy: str = CompositionStrategy.UNION,
    ) -> "GraphComposition":
        """
        Create a new graph composition.
        
        Args:
            participating_graph_ids: IDs of graphs to compose
            composition_strategy: Strategy for combining graphs
            
        Returns:
            New GraphComposition with unique identity
        """
        composition_id = f"composition:{uuid.uuid4().hex[:16]}"
        
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Graph composition initialization",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [composition_id],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )
        
        participating = tuple(
            {"graph_identity": gid, "role": "participating"}
            for gid in participating_graph_ids
        )
        
        return cls(
            composition_identity=composition_id,
            participating_graphs=participating,
            resulting_graph={"composition_identity": composition_id},
            composition_strategy=composition_strategy,
            provenance=initial_provenance,
            created_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert composition to dictionary for serialization."""
        return {
            "composition_identity": self.composition_identity,
            "participating_graphs": [dict(g) for g in self.participating_graphs],
            "resulting_graph": dict(self.resulting_graph),
            "composition_strategy": self.composition_strategy,
            "cross_graph_edges": [e for e in self.cross_graph_edges],
            "provenance": [p for p in self.provenance],
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphComposition":
        """Create composition from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        participating = []
        for g_data in data.get("participating_graphs", []):
            if isinstance(g_data, dict):
                participating.append(dict(g_data))
        
        return cls(
            composition_identity=data.get("composition_identity", str(uuid.uuid4())),
            participating_graphs=tuple(participating),
            resulting_graph=dict(data.get("resulting_graph", {})),
            composition_strategy=data.get("composition_strategy", CompositionStrategy.UNION),
            cross_graph_edges=tuple(data.get("cross_graph_edges", [])),
            provenance=tuple(provenance),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )
    
    def add_participating_graph(self, graph_ref: Dict[str, Any]) -> "GraphComposition":
        """Add a graph to the composition."""
        existing_ids = {g.get("graph_identity") for g in self.participating_graphs}
        new_id = graph_ref.get("graph_identity")
        
        if new_id and new_id in existing_ids:
            return self
        
        return GraphComposition(
            composition_identity=self.composition_identity,
            participating_graphs=tuple(list(self.participating_graphs) + [graph_ref]),
            resulting_graph=self.resulting_graph,
            composition_strategy=self.composition_strategy,
            cross_graph_edges=self.cross_graph_edges,
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": f"Added graph to composition: {new_id}",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.composition_identity] if self.provenance else [self.composition_identity],
                "authority": "system",
                "timestamp_utc": time.time(),
            }]),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )
    
    def add_cross_graph_edge(self, edge_ref: Dict[str, Any]) -> "GraphComposition":
        """Add a cross-graph edge to the composition."""
        return GraphComposition(
            composition_identity=self.composition_identity,
            participating_graphs=self.participating_graphs,
            resulting_graph=self.resulting_graph,
            composition_strategy=self.composition_strategy,
            cross_graph_edges=tuple(list(self.cross_graph_edges) + [edge_ref]),
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": f"Added cross-graph edge: {edge_ref.get('edge_identity', 'unknown')}",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.composition_identity] if self.provenance else [self.composition_identity],
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
    # Composition strategy (Phase 6.8 Section 15)
    "CompositionStrategy",
    # Graph composition (Phase 6.8 Section 15)
    "GraphComposition",
]