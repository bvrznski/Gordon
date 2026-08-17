"""Graph Partition - Phase 6.8 Part 2.

This module implements the canonical graph partition contracts according to 
Gordon Cognitive Architecture specifications (Phase 6.8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# PARTITION STRATEGY - Phase 6.8 Section 17
# =============================================================================


class PartitionStrategy:
    """
    Strategies for graph partitioning.
    
    Per PARTITION-LAW-005: Partition revisions shall preserve lineage.
    
    Strategy kinds:
        DOMAIN      -> Partition by domain/subject area
        ONTOLOGY    -> Partition by ontology structure
        CAPABILITY  -> Partition by capability boundaries
        CONTEXT     -> Partition by contextual boundaries
        WORKSPACE   -> Partition by workspace/separation
        TIME        -> Partition by temporal boundaries
        
    Partitions remain explicit (per PARTITION-LAW-002).
    """
    
    DOMAIN = "domain"
    ONTOLOGY = "ontology"
    CAPABILITY = "capability"
    CONTEXT = "context"
    WORKSPACE = "workspace"
    TIME = "time"
    
    ALL = {DOMAIN, ONTOLOGY, CAPABILITY, CONTEXT, WORKSPACE, TIME}


# =============================================================================
# GRAPH PARTITION - Phase 6.8 Section 17
# =============================================================================


@dataclass(frozen=True)
class GraphPartition:
    """
    Partition of a graph into subgraphs.
    
    Per PARTITION-LAW-001: Graph partitions shall preserve semantic connectivity.
    Per PARTITION-LAW-002: Partition boundaries shall remain explicit.
    Per PARTITION-LAW-003: Cross-partition edges shall remain explicit.
    
    Fields:
        partition_identity: Unique identifier for this partition
        partition_strategy: Strategy used for partitioning
        participating_nodes: Nodes in this partition
        participating_edges: Edges in this partition
        partition_constraints: Constraints applied to the partition
        
    Partitions preserve graph identity while enabling focused navigation.
    """
    
    # Core identity
    partition_identity: str  # Unique partition identifier
    
    # Strategy (required per PARTITION-LAW-005)
    partition_strategy: str = PartitionStrategy.DOMAIN
    
    # Partition content
    participating_nodes: Tuple[str, ...] = field(default_factory=tuple)
    participating_edges: Tuple[str, ...] = field(default_factory=tuple)
    
    # Constraints (required per PARTITION-LAW-001)
    partition_constraints: Tuple[str, ...] = field(default_factory=tuple)
    
    # Cross-partition edges
    cross_partition_edges: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Provenance
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate partition after creation."""
        if not self.partition_identity:
            raise ValueError("partition_identity cannot be empty")
        if not self.partition_strategy or self.partition_strategy not in PartitionStrategy.ALL:
            raise ValueError(f"Invalid partition_strategy: {self.partition_strategy}")
    
    @property
    def is_valid(self) -> bool:
        """Check if partition has valid foundational data."""
        return (
            len(self.partition_identity) > 0 and
            self.partition_strategy in PartitionStrategy.ALL
        )
    
    @classmethod
    def create_initial(
        cls,
        strategy: str = PartitionStrategy.DOMAIN,
        node_ids: Optional[List[str]] = None,
        edge_ids: Optional[List[str]] = None,
    ) -> "GraphPartition":
        """
        Create a new graph partition.
        
        Args:
            strategy: Strategy for partitioning
            node_ids: Nodes to include (optional)
            edge_ids: Edges to include (optional)
            
        Returns:
            New GraphPartition with unique identity
        """
        partition_id = f"partition:{uuid.uuid4().hex[:16]}"
        
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Graph partition initialization",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [partition_id],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            partition_identity=partition_id,
            partition_strategy=strategy,
            participating_nodes=tuple(node_ids or []),
            participating_edges=tuple(edge_ids or []),
            provenance=initial_provenance,
            created_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert partition to dictionary for serialization."""
        return {
            "partition_identity": self.partition_identity,
            "partition_strategy": self.partition_strategy,
            "participating_nodes": list(self.participating_nodes),
            "participating_edges": list(self.participating_edges),
            "partition_constraints": list(self.partition_constraints),
            "cross_partition_edges": [e for e in self.cross_partition_edges],
            "provenance": [p for p in self.provenance],
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphPartition":
        """Create partition from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        return cls(
            partition_identity=data.get("partition_identity", str(uuid.uuid4())),
            partition_strategy=data.get("partition_strategy", PartitionStrategy.DOMAIN),
            participating_nodes=tuple(data.get("participating_nodes", [])),
            participating_edges=tuple(data.get("participating_edges", [])),
            partition_constraints=tuple(data.get("partition_constraints", [])),
            cross_partition_edges=tuple(data.get("cross_partition_edges", [])),
            provenance=tuple(provenance),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )
    
    def add_node(self, node_id: str) -> "GraphPartition":
        """Add a node to the partition."""
        if node_id in self.participating_nodes:
            return self
        
        return GraphPartition(
            partition_identity=self.partition_identity,
            partition_strategy=self.partition_strategy,
            participating_nodes=tuple(set(self.participating_nodes) | {node_id}),
            participating_edges=self.participating_edges,
            partition_constraints=self.partition_constraints,
            cross_partition_edges=self.cross_partition_edges,
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": f"Added node to partition: {node_id}",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.partition_identity] if self.provenance else [self.partition_identity],
                "authority": "system",
                "timestamp_utc": time.time(),
            }]),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )
    
    def add_edge(self, edge_id: str) -> "GraphPartition":
        """Add an edge to the partition."""
        if edge_id in self.participating_edges:
            return self
        
        return GraphPartition(
            partition_identity=self.partition_identity,
            partition_strategy=self.partition_strategy,
            participating_nodes=self.participating_nodes,
            participating_edges=tuple(set(self.participating_edges) | {edge_id}),
            partition_constraints=self.partition_constraints,
            cross_partition_edges=self.cross_partition_edges,
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": f"Added edge to partition: {edge_id}",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.partition_identity] if self.provenance else [self.partition_identity],
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
    # Partition strategy (Phase 6.8 Section 17)
    "PartitionStrategy",
    # Graph partition (Phase 6.8 Section 17)
    "GraphPartition",
]