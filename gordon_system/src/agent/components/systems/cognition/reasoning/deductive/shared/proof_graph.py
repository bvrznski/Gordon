# Proof Graph - Phase 7.1
# =======================

"""
Canonical Proof Graph Contract.

Proof Graphs represent proofs as graph structures for inspection and analysis.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class NodeKind(Enum):
    """Kinds of nodes in a proof graph."""
    
    PREMISE = "premise"                       # A premise node
    INTERMEDIATE_CONCLUSION = "intermediate_conclusion"  # An intermediate result
    FINAL_CONCLUSION = "final_conclusion"     # The final result


class EdgeKind(Enum):
    """Kinds of edges in a proof graph."""
    
    DEPENDENCY = "dependency"                 # Logical dependency edge
    REFINEMENT = "refinement"                 # Refinement relationship
    EQUIVALENCE = "equivalence"               # Equivalence relationship


@dataclass(frozen=True)
class ProofNode:
    """
    A node in a proof graph.
    
    Nodes represent:
        - Premises (inputs to the proof)
        - Intermediate conclusions (results of rule applications)
        - Final conclusions (the goal of the proof)
    """
    
    # Identity
    node_id: str                            # Unique node identifier
    
    # Content
    statement: str                          # The mathematical/logical statement
    node_kind: NodeKind                     # What kind of node?
    
    # Metadata
    depth: int = 0                          # Distance from premises
    step_number: Optional[int] = None       # Step in proof sequence (if applicable)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ProofEdge:
    """
    An edge in a proof graph.
    
    Edges represent logical relationships between nodes:
        - Dependency: This node depends on that node
        - Refinement: This is a refinement of that node
        - Equivalence: These are logically equivalent
    """
    
    # Identity
    edge_id: str                            # Unique edge identifier
    
    # Connection
    source_node: str                        # Source node ID
    target_node: str                        # Target node ID
    
    # Edge type
    edge_kind: EdgeKind                     # What kind of relationship?
    
    # Provenance
    rule_applied: Optional[str] = None      # If this is a logical inference
    created_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ProofGraph:
    """
    A graph representation of a proof.
    
    A proof graph contains:
        - Nodes (premises, conclusions, intermediate results)
        - Edges (logical dependencies between nodes)
        - Dependency structure (for traversal and verification)
    
    Proof graphs remain inspectable; they enable visualization and analysis.
    """
    
    # Identity
    graph_id: str                           # Unique graph identifier
    
    # Nodes
    proof_nodes: Tuple[ProofNode, ...]      # All nodes in the graph
    
    # Edges
    proof_edges: Tuple[ProofEdge, ...]      # All edges in the graph
    
    # Dependency structure (for efficient traversal)
    dependency_structure: Dict[str, List[str]] = field(default_factory=dict)
    # Maps node_id -> list of node_ids that depend on it
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_proof_id: Optional[str] = None   # Which proof does this graph represent?
    
    @property
    def node_count(self) -> int:
        """Count of nodes."""
        return len(self.proof_nodes)
    
    @property
    def edge_count(self) -> int:
        """Count of edges."""
        return len(self.proof_edges)
    
    @property
    def root_nodes(self) -> List[str]:
        """Get nodes with no incoming dependencies (premises)."""
        dependent_nodes = {edge.target_node for edge in self.proof_edges}
        return [node.node_id for node in self.proof_nodes if node.node_id not in dependent_nodes]
    
    @property
    def leaf_nodes(self) -> List[str]:
        """Get nodes with no outgoing dependencies (final conclusions)."""
        depending_nodes = {edge.source_node for edge in self.proof_edges}
        return [node.node_id for node in self.proof_nodes if node.node_id not in depending_nodes]
    
    @classmethod
    def create(
        cls,
        proof_nodes: List[ProofNode],
        proof_edges: List[ProofEdge],
        source_proof_id: Optional[str] = None,
    ) -> ProofGraph:
        """Create a new proof graph."""
        # Build dependency structure
        dependency_structure: Dict[str, List[str]] = {}
        for node in proof_nodes:
            dependency_structure[node.node_id] = []
        
        for edge in proof_edges:
            if edge.source_node not in dependency_structure:
                dependency_structure[edge.source_node] = []
            dependency_structure[edge.source_node].append(edge.target_node)
        
        return cls(
            graph_id=f"proof_graph:{uuid.uuid4().hex[:16]}",
            proof_nodes=tuple(proof_nodes),
            proof_edges=tuple(proof_edges),
            dependency_structure=dependency_structure,
            source_proof_id=source_proof_id,
        )
    
    def get_dependencies(self, node_id: str) -> List[str]:
        """Get nodes that the given node depends on."""
        return self.dependency_structure.get(node_id, [])
    
    def dependents(self, node_id: str) -> List[str]:
        """Get nodes that depend on the given node."""
        return [
            edge.target_node
            for edge in self.proof_edges
            if edge.source_node == node_id
        ]


__all__ = [
    "ProofGraph",
    "ProofNode",
    "ProofEdge",
    "NodeKind",
    "EdgeKind",
]