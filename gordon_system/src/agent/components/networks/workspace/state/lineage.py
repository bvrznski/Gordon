# Workspace Lineage Module
# ========================

"""
Canonical WorkspaceLineage and related types.

WorkspaceLineage represents the complete semantic traceability from workspace state
through revisions, deltas, transitions, to certification. All lineage must be preserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class LineageNode:
    """
    A single node in the semantic lineage graph.
    
    Each node represents a semantic artifact (state, delta, transition, etc.)
    and preserves its relationship to other nodes in the lineage chain.
    
    ARCHITECTURAL INVARIANT: Lineage is acyclic. No node can be its own ancestor.
    """
    
    # Node identity
    node_id: str = ""
    """Unique identifier for this lineage node."""
    
    node_kind: str = "state"
    """Kind of artifact this node represents (state, delta, transition, etc.)"""
    
    semantic_version: str = "1.0"
    """Semantic version for compatibility tracking."""
    
    # Node content
    revision: int = 0
    """Revision number at this lineage point."""
    
    timestamp_utc: float = 0.0
    """When this node was created (seconds since epoch)."""
    
    # Source information
    produced_by: str = "lineage_node"
    """Who/what produced this node."""
    
    provenance_evidence: dict = field(default_factory=dict)
    """Evidence supporting the node's semantic validity."""


@dataclass(frozen=True)
class LineagePath:
    """
    A path through the lineage graph from one artifact to another.
    
    Lineage paths preserve traceability while maintaining architectural bounds
    and runtime neutrality. They never depend on runtime timing or state.
    
    ARCHITECTURAL INVARIANT: Every lineage path must be acyclic.
    """
    
    # Path identity
    path_id: str = ""
    """Unique identifier for this lineage path."""
    
    # Path endpoints
    start_node_id: str = ""
    """ID of the starting node in the path."""
    
    end_node_id: str = ""
    """ID of the ending node in the path."""
    
    # Path nodes (ordered sequence)
    nodes: Tuple[LineageNode, ...] = field(default_factory=tuple)
    """Ordered sequence of nodes in this lineage path."""
    
    @property
    def length(self) -> int:
        """Return the number of nodes in this path."""
        return len(self.nodes)
    
    @property
    def is_empty(self) -> bool:
        """Check if this path has no nodes."""
        return self.length == 0
    
    def verify_acyclic(self) -> bool:
        """
        Verify that this lineage path contains no cycles.
        
        Returns True if the path is acyclic (no node appears twice).
        """
        seen_ids = set()
        for node in self.nodes:
            if node.node_id in seen_ids:
                return False
            seen_ids.add(node.node_id)
        return True


@dataclass(frozen=True)
class WorkspaceLineage:
    """
    Complete semantic lineage record for a workspace state.
    
    Lineage semantics:
        - Preserves identity: every artifact maintains its unique identity
        - Preserves lineage: all connections between artifacts are traceable
        - Preserves provenance: source information is maintained throughout
        - Is acyclic: no circular dependencies or references
    
    Lineage chains follow the pattern:
        WorkspaceState -> StateRevision -> StateDelta -> Transition -> Certified State
    
    ARCHITECTURAL INVARIANT: Every state has exactly one lineage path back to its origin.
    """
    
    # Current state
    current_state_id: str = ""
    """ID of the currently active workspace state."""
    
    current_revision: int = 0
    """Revision of the current state."""
    
    # Complete lineage
    full_lineage_path: LineagePath = field(default_factory=LineagePath)
    """Complete path from origin to current state."""
    
    # Active lineage (for pending transitions)
    active_lineage_paths: Tuple[LineagePath, ...] = field(default_factory=tuple)
    """Any active lineage paths in progress."""
    
    # Lineage metrics
    total_transitions: int = 0
    """Total number of transitions recorded in lineage."""
    
    first_state_id: str = ""
    """ID of the origin state (revision 0)."""
    
    # Lineage validation
    lineage_valid: bool = True
    """Whether current lineage is valid."""
    
    lineage_intact: bool = True
    """Whether the lineage chain is intact (no gaps or inconsistencies)."""
    
    @classmethod
    def initial(cls) -> WorkspaceLineage:
        """
        Create an initial lineage record.
        
        This represents a fresh start with no history.
        """
        return cls(
            current_state_id="workspace_state_initial",
            current_revision=0,
            first_state_id="workspace_state_initial",
            total_transitions=0,
            lineage_valid=True,
            lineage_intact=True,
        )
    
    def extend_lineage(self, new_node: LineageNode) -> WorkspaceLineage:
        """
        Return a new lineage with the given node added to the path.
        
        This preserves immutability by creating a new instance.
        """
        # Create new path with extended nodes
        new_nodes = self.full_lineage_path.nodes + (new_node,)
        new_end_id = new_node.node_id if new_node.node_id else self.current_state_id
        
        return WorkspaceLineage(
            current_state_id=new_end_id,
            current_revision=self.current_revision + 1,
            full_lineage_path=LineagePath(
                path_id=f"lineage_{self.total_transitions + 1}",
                start_node_id=self.first_state_id,
                end_node_id=new_end_id,
                nodes=new_nodes,
            ),
            total_transitions=self.total_transitions + 1,
            lineage_valid=True,
            lineage_intact=True,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "LineageNode",
    "LineagePath",
    "WorkspaceLineage",
)