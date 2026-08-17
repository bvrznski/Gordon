"""Graph Edge - Phase 6.8 Part 2.

This module implements the canonical GraphEdge contract according to 
Gordon Cognitive Architecture specifications (Phase 6.8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# EDGE DIRECTION - Phase 6.8 Section 5
# =============================================================================


class EdgeDirection:
    """
    Direction types for graph edges.
    
    Per EDGE-LAW-003: Edge direction shall remain explicit.
    
    Direction kinds:
        DIRECTED     -> One-way relationship (source -> target)
        UNDIRECTED   -> Two-way relationship (source <-> target)
        INVERSE      -> Inverse of a directed relationship
    """
    
    DIRECTED = "directed"
    UNDIRECTED = "undirected"
    INVERSE = "inverse"
    
    ALL = {DIRECTED, UNDIRECTED, INVERSE}


# =============================================================================
# GRAPH EDGE - Phase 6.8 Section 5
# =============================================================================


@dataclass(frozen=True)
class GraphEdge:
    """
    Edge in a Knowledge Graph.
    
    Per EDGE-LAW-001: Every Edge shall reference exactly one Relation.
    Per EDGE-LAW-002: Edges shall preserve endpoint identities.
    Per EDGE-LAW-003: Edge direction shall remain explicit.
    Per EDGE-LAW-004: Inverse edges shall remain explicitly represented.
    
    Fields:
        edge_identity: Unique identifier for this graph edge
        referenced_relation: Reference to the Relation artifact
        source_node: Source node identity
        target_node: Target node identity
        direction: Direction of the relationship
        
    Edges reference Relation artifacts but never replace them 
    (per Phase 6.8 Part 2 Section 5).
    """
    
    # Core identity
    edge_identity: str  # Unique graph edge identifier
    
    # Referenced relation (required per EDGE-LAW-001)
    referenced_relation: Dict[str, Any]  # Reference to Relation artifact
    
    # Endpoints (required per EDGE-LAW-002)
    source_node: str
    target_node: str
    
    # Direction (required per EDGE-LAW-003)
    direction: str = EdgeDirection.DIRECTED
    
    # Provenance
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate edge after creation."""
        if not self.edge_identity:
            raise ValueError("edge_identity cannot be empty")
        if not self.referenced_relation or "referenced_identity" not in self.referenced_relation:
            raise ValueError("referenced_relation must reference a Relation identity")
        if not self.source_node:
            raise ValueError("source_node cannot be empty")
        if not self.target_node:
            raise ValueError("target_node cannot be empty")
    
    @property
    def is_valid(self) -> bool:
        """Check if edge has valid foundational data."""
        return (
            len(self.edge_identity) > 0 and
            "referenced_identity" in self.referenced_relation and
            len(self.referenced_relation["referenced_identity"]) > 0 and
            len(self.source_node) > 0 and
            len(self.target_node) > 0
        )
    
    @property
    def referenced_relation_id(self) -> str:
        """Get the semantic identity of the referenced relation."""
        return self.referenced_relation.get("referenced_identity", "")
    
    @classmethod
    def create_from_relation(
        cls,
        source_node: str,
        target_node: str,
        relation_id: str,
        direction: str = EdgeDirection.DIRECTED,
    ) -> "GraphEdge":
        """
        Create a new graph edge from a Relation reference.
        
        Args:
            source_node: Source node identity
            target_node: Target node identity  
            relation_id: Semantic identity of the Relation artifact
            direction: Direction of the relationship
            
        Returns:
            New GraphEdge with unique edge_identity
            
        This method creates an edge that references an existing Relation
        artifact. The edge preserves the relation's identity (EDGE-LAW-002).
        """
        edge_id = f"edge:{uuid.uuid4().hex[:16]}"
        
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Edge creation from relation reference",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [edge_id],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            edge_identity=edge_id,
            referenced_relation={
                "referenced_identity": relation_id,
                "artifact_kind": "relation",
                "reference_type": "direct",
            },
            source_node=source_node,
            target_node=target_node,
            direction=direction,
            provenance=initial_provenance,
            created_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary for serialization."""
        return {
            "edge_identity": self.edge_identity,
            "referenced_relation": dict(self.referenced_relation),
            "source_node": self.source_node,
            "target_node": self.target_node,
            "direction": self.direction,
            "provenance": [p for p in self.provenance],
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphEdge":
        """Create edge from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        return cls(
            edge_identity=data.get("edge_identity", str(uuid.uuid4())),
            referenced_relation=dict(data.get("referenced_relation", {})),
            source_node=data.get("source_node", ""),
            target_node=data.get("target_node", ""),
            direction=data.get("direction", EdgeDirection.DIRECTED),
            provenance=tuple(provenance),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )
    
    def with_inverse_direction(self) -> "GraphEdge":
        """Create an edge with inverse direction."""
        return GraphEdge(
            edge_identity=f"{self.edge_identity}_inverse",
            referenced_relation=self.referenced_relation,
            source_node=self.target_node,
            target_node=self.source_node,
            direction=EdgeDirection.INVERSE,
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": f"Inverse edge from {self.edge_identity}",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.edge_identity] if self.provenance else [self.edge_identity],
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
    # Edge direction (Phase 6.8 Section 5)
    "EdgeDirection",
    # Graph edge (Phase 6.8 Section 5)
    "GraphEdge",
]