# Gordon Cognitive Architecture - Phase 4.11.4
# ===========================================

"""
Global Coordination Graph Delta Computation
============================================

Delta between graph revisions for incremental updates.

GRAPHLAW-211: Deltas are immutable after computation
GRAPHLAW-212: Deltas preserve all changes for traceability
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# Import types from graph_models (must be imported after graph_models)
from .graph_models import (
    GlobalCoordinationGraph,
    GlobalCoordinationGraphIndexes,
)


# =============================================================================
# GLOBAL COORDINATION GRAPH DELTA
# =============================================================================

@dataclass(frozen=True, slots=True)
class GlobalCoordinationGraphDelta:
    """
    Immutable delta between two graph revisions.
    
    GRAPHLAW-221: Delta is immutable after computation
    GRAPHLAW-222: Delta preserves all changes for traceability
    
    DELTA-LAW-001: Every Graph Revision is derivable from one Graph Delta
    DELTA-LAW-002: Graph Deltas preserve additions
    DELTA-LAW-003: Graph Deltas preserve supersessions
    """
    identity: str
    """Unique identity for this delta."""
    
    base_graph_revision_ref: str = ""
    """Reference to the base graph revision (before)."""
    
    target_graph_revision_ref: str = ""
    """Reference to the target graph revision (after)."""
    
    added_nodes: tuple[str, ...] = ()
    """Node identities that were added."""
    
    superseded_nodes: tuple[str, ...] = ()
    """Node identities that were superseded."""
    
    deprecated_nodes: tuple[str, ...] = ()
    """Node identities that were deprecated."""
    
    invalidated_nodes: tuple[str, ...] = ()
    """Node identities that were invalidated."""
    
    status_changed_nodes: tuple[str, ...] = ()
    """Node identities whose status changed."""
    
    added_edges: tuple[str, ...] = ()
    """Edge identities that were added."""
    
    superseded_edges: tuple[str, ...] = ()
    """Edge identities that were superseded."""
    
    deprecated_edges: tuple[str, ...] = ()
    """Edge identities that were deprecated."""
    
    invalidated_edges: tuple[str, ...] = ()
    """Edge identities that were invalidated."""
    
    status_changed_edges: tuple[str, ...] = ()
    """Edge identities whose status changed."""
    
    affected_partitions: tuple[str, ...] = ()
    """Partition identities affected by this delta."""
    
    affected_domains: tuple[str, ...] = ()
    """Domain identities affected by this delta."""
    
    affected_components: tuple[str, ...] = ()
    """Component identities affected by this delta."""
    
    index_changes: dict[str, str] = field(default_factory=dict)
    """Maps from index kind to change description."""
    
    findings: tuple[str, ...] = ()
    """Findings related to the changes."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on this delta."""
    
    provenance_ref: Optional[str] = None
    """Reference to provenance record."""
    
    def has_changes(self) -> bool:
        """Check if there are any changes in this delta."""
        return (
            len(self.added_nodes) > 0 or
            len(self.superseded_nodes) > 0 or
            len(self.added_edges) > 0 or
            len(self.superseded_edges) > 0
        )
    
    def total_changes(self) -> int:
        """Return the total number of changes in this delta."""
        return (
            len(self.added_nodes) +
            len(self.superseded_nodes) +
            len(self.added_edges) +
            len(self.superseded_edges)
        )


# =============================================================================
# GRAPH REVISION BUILDER RESULT
# =============================================================================

@dataclass(frozen=True, slots=True)
class GraphRevisionBuildResult:
    """
    Result of building a graph revision.
    
    GRAPHLAW-231: Build result is immutable
    GRAPHLAW-232: Build result contains all necessary information
    """
    graph: GlobalCoordinationGraph = field(default_factory=GlobalCoordinationGraph)
    """The resulting graph."""
    
    delta: Optional["GlobalCoordinationGraphDelta"] = None
    """Delta computed during build (if applicable)."""
    
    is_incremental: bool = False
    """True if this was an incremental build."""
    
    findings: tuple[str, ...] = ()
    """Findings during construction."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on the result."""
    
    def is_valid(self) -> bool:
        """Check if the build was valid (no errors)."""
        return self.graph is not None


# =============================================================================
# INDEX BUILD RESULT
# =============================================================================

@dataclass(frozen=True, slots=True)
class IndexBuildResult:
    """
    Result of building graph indexes.
    
    GRAPHLAW-241: Index build result is immutable
    GRAPHLAW-242: Indexes are deterministic from content
    """
    indexes: GlobalCoordinationGraphIndexes = field(
        default_factory=lambda: GlobalCoordinationGraphIndexes(revision=1)
    )
    """The built indexes."""
    
    findings: tuple[str, ...] = ()
    """Findings during index construction."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on the indexes."""
    
    def is_consistent(self) -> bool:
        """Check if indexes are internally consistent."""
        return True  # Will be implemented with actual validation logic