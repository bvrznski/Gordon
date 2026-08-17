"""Graph Node - Phase 6.8 Part 2.

This module implements the canonical GraphNode contract according to 
Gordon Cognitive Architecture specifications (Phase 6.8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# NODE REFERENCE - Phase 6.8 Section 2
# =============================================================================


@dataclass(frozen=True)
class NodeReference:
    """
    Reference to a semantic artifact within a graph node.
    
    Per NODE-LAW-001: Every Node shall reference exactly one semantic artifact.
    Per NODE-LAW-003: Node revisions shall preserve artifact references.
    
    Fields:
        referenced_identity: Semantic identity of the referenced artifact
        artifact_kind: Kind of artifact (concept, assertion, belief, etc.)
        reference_type: How this node represents the artifact
        
    Reference kinds:
        CONCEPT      -> A concept entity
        ASSERTION    -> An assertion proposition
        BELIEF       -> A belief commitment
        MODEL        -> A model structure
        RELATION     -> A relation between entities
        CAPABILITY   -> A capability description
        CONTEXT      -> A context specification
        TASK         -> A task definition
        GOAL         -> A goal statement
    """
    
    referenced_identity: str
    artifact_kind: str
    reference_type: str = "direct"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node reference to dictionary."""
        return {
            "referenced_identity": self.referenced_identity,
            "artifact_kind": self.artifact_kind,
            "reference_type": self.reference_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> NodeReference:
        """Create node reference from dictionary."""
        return cls(
            referenced_identity=data.get("referenced_identity", ""),
            artifact_kind=data.get("artifact_kind", ""),
            reference_type=data.get("reference_type", "direct"),
        )


# =============================================================================
# GRAPH NODE - Phase 6.8 Section 2
# =============================================================================


@dataclass(frozen=True)
class GraphNode:
    """
    Node in a Knowledge Graph.
    
    Per NODE-LAW-001: Every Node shall reference exactly one semantic artifact.
    Per NODE-LAW-002: Nodes shall never duplicate semantic identity.
    Per NODE-LAW-004: Node provenance shall remain complete.
    Per NODE-LAW-005: Node memberships shall remain explicit.
    
    Fields:
        node_identity: Unique identifier for this graph node
        referenced_artifact: Reference to the semantic artifact
        artifact_kind: Kind of artifact being referenced
        graph_memberships: Graphs this node belongs to
        layer_memberships: Layers this node participates in
        provenance: Origin and evolution trail
        
    Node references may include:
        Concept, Assertion, Belief, Model, Relation, Capability, 
        Context, Task, Goal
    
    Nodes preserve semantic identity (NODE-LAW-003).
    """
    
    # Core identity (required - unique per NODE-LAW-002)
    node_identity: str  # Unique graph node identifier
    
    # Referenced artifact (required per NODE-LAW-001)
    referenced_artifact: NodeReference
    
    # Artifact kind (for quick lookup)
    artifact_kind: str = ""
    
    # Graph memberships
    graph_memberships: Tuple[str, ...] = field(default_factory=tuple)
    
    # Layer memberships
    layer_memberships: Tuple[str, ...] = field(default_factory=tuple)
    
    # Provenance
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate node after creation."""
        if not self.node_identity:
            raise ValueError("node_identity cannot be empty")
        if not self.referenced_artifact or not self.referenced_artifact.referenced_identity:
            raise ValueError("referenced_artifact must reference a semantic identity")
    
    @property
    def is_valid(self) -> bool:
        """Check if node has valid foundational data."""
        return (
            len(self.node_identity) > 0 and
            self.referenced_artifact is not None and
            len(self.referenced_artifact.referenced_identity) > 0
        )
    
    @property
    def referenced_identity(self) -> str:
        """Get the semantic identity of the referenced artifact."""
        return self.referenced_artifact.referenced_identity
    
    @classmethod
    def create_from_reference(
        cls,
        referenced_identity: str,
        artifact_kind: str,
        graph_memberships: Optional[List[str]] = None,
        layer_memberships: Optional[List[str]] = None,
    ) -> "GraphNode":
        """
        Create a new graph node from an artifact reference.
        
        Args:
            referenced_identity: Semantic identity of the referenced artifact
            artifact_kind: Kind of artifact being referenced
            graph_memberships: Graphs this node belongs to (optional)
            layer_memberships: Layers this node participates in (optional)
            
        Returns:
            New GraphNode with unique node_identity
            
        This method creates a new node that references an existing semantic
        artifact. The node preserves the artifact's identity (NODE-LAW-003).
        """
        node_id = f"node:{uuid.uuid4().hex[:16]}"
        
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Node creation from artifact reference",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [node_id],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            node_identity=node_id,
            referenced_artifact=NodeReference(
                referenced_identity=referenced_identity,
                artifact_kind=artifact_kind,
                reference_type="direct",
            ),
            artifact_kind=artifact_kind,
            graph_memberships=tuple(graph_memberships or []),
            layer_memberships=tuple(layer_memberships or []),
            provenance=initial_provenance,
            created_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary for serialization."""
        return {
            "node_identity": self.node_identity,
            "referenced_artifact": self.referenced_artifact.to_dict(),
            "artifact_kind": self.artifact_kind,
            "graph_memberships": list(self.graph_memberships),
            "layer_memberships": list(self.layer_memberships),
            "provenance": [p for p in self.provenance],
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphNode":
        """Create node from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        return cls(
            node_identity=data.get("node_identity", str(uuid.uuid4())),
            referenced_artifact=NodeReference.from_dict(
                data.get("referenced_artifact", {})
            ),
            artifact_kind=data.get("artifact_kind", ""),
            graph_memberships=tuple(data.get("graph_memberships", [])),
            layer_memberships=tuple(data.get("layer_memberships", [])),
            provenance=tuple(provenance),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )
    
    def add_graph_membership(self, graph_id: str) -> "GraphNode":
        """Add a graph membership and return new node."""
        if graph_id in self.graph_memberships:
            return self
        
        new_provenance = tuple(list(self.provenance) + [{
            "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
            "originating_request": f"Added to graph: {graph_id}",
            "originating_system": "knowledge-graph-system",
            "originating_revision": 1,
            "evidence_references": [],
            "grounding_references": [],
            "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.node_identity] if self.provenance else [self.node_identity],
            "authority": "system",
            "timestamp_utc": time.time(),
        }])
        
        return GraphNode(
            node_identity=self.node_identity,
            referenced_artifact=self.referenced_artifact,
            artifact_kind=self.artifact_kind,
            graph_memberships=tuple(set(self.graph_memberships) | {graph_id}),
            layer_memberships=self.layer_memberships,
            provenance=new_provenance,
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )
    
    def add_layer_membership(self, layer_id: str) -> "GraphNode":
        """Add a layer membership and return new node."""
        if layer_id in self.layer_memberships:
            return self
        
        new_provenance = tuple(list(self.provenance) + [{
            "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
            "originating_request": f"Added to layer: {layer_id}",
            "originating_system": "knowledge-graph-system",
            "originating_revision": 1,
            "evidence_references": [],
            "grounding_references": [],
            "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.node_identity] if self.provenance else [self.node_identity],
            "authority": "system",
            "timestamp_utc": time.time(),
        }])
        
        return GraphNode(
            node_identity=self.node_identity,
            referenced_artifact=self.referenced_artifact,
            artifact_kind=self.artifact_kind,
            graph_memberships=self.graph_memberships,
            layer_memberships=tuple(set(self.layer_memberships) | {layer_id}),
            provenance=new_provenance,
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )


# =============================================================================
# NODE KINDS - Phase 6.8 Section 2
# =============================================================================


class NodeKind:
    """Kinds of nodes that may appear in knowledge graphs."""
    
    CONCEPT = "concept"
    ASSERTION = "assertion"
    BELIEF = "belief"
    MODEL = "model"
    RELATION = "relation"
    CAPABILITY = "capability"
    CONTEXT = "context"
    TASK = "task"
    GOAL = "goal"
    
    ALL = {
        CONCEPT,
        ASSERTION,
        BELIEF,
        MODEL,
        RELATION,
        CAPABILITY,
        CONTEXT,
        TASK,
        GOAL,
    }


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Node reference (Phase 6.8 Section 2)
    "NodeReference",
    # Graph node (Phase 6.8 Section 2)
    "GraphNode",
    # Node kinds
    "NodeKind",
]