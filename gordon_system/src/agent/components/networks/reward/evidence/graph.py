# Reward Network - Evidence Graph
# ================================

"""
Evidence graph module.

Constructs immutable graphs of evidence relationships, preserving provenance,
hierarchy, and temporal partitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True, slots=True)
class EvidenceRelationship:
    """
    Type of relationship between evidence items in the graph.

    EVIDENCE RELATIONSHIP TYPES:
        • supports: Evidence supports another piece of evidence
        • contradicts: Evidence contradicts another piece of evidence
        • depends_on: Evidence depends on another for validity
        • extends: Evidence extends another with additional context
        • duplicates: Evidence is a duplicate of another
        • derived_from: Evidence was derived from another
        • explains: Evidence explains the cause of another

    GRAPH LAWS:
        GRAPH-LAW-004: Graph edges remain explicitly typed
    """

    relationship_type: str
    """Type of relationship (see EVIDENCE RELATIONSHIP TYPES)."""

    confidence: float = 1.0
    """Confidence in this relationship."""

    context: Tuple[str, ...] = field(default_factory=tuple)
    """Context for this relationship."""


EvidenceEdge = Tuple[str, str, EvidenceRelationship]
"""
A directed edge in the evidence graph.

Format: (source_evidence_id, target_evidence_id, relationship)
"""


@dataclass(frozen=True, slots=True)
class RewardEvidenceGraph:
    """
    Immutable graph of evidence relationships.

    The graph represents semantic relationships between evidence items,
    enabling analysis of evidence support and contradiction patterns.

    GRAPH PROPERTIES:
        • nodes: Set of all evidence IDs in the graph
        • edges: Set of all directed edges
        • hierarchy: Evidence hierarchical structure
        • provenance: Graph provenance information
        • timescales: Temporal partitions in the graph

    GRAPH INVARIANTS:
        • Graph is immutable once constructed
        • Graph preserves provenance chains
        • Graph does not include reward values
        • Graph remains acyclic unless relationship explicitly requires it

    GRAPH LAWS:
        GRAPH-LAW-001: Exactly one canonical RewardEvidenceGraph exists
        GRAPH-LAW-002: RewardEvidenceGraph is immutable
        GRAPH-LAW-003: Graph nodes are RewardEvidence objects only
        GRAPH-LAW-004: Graph edges remain explicitly typed
        GRAPH-LAW-005: Graph preserves provenance
        GRAPH-LAW-006: Graph preserves hierarchy
        GRAPH-LAW-007: Graph preserves temporal partitions
    """

    graph_id: str
    """Unique identifier for this graph."""

    nodes: Tuple[str, ...]
    """Set of all evidence IDs in the graph."""

    edges: Tuple[EvidenceEdge, ...]
    """Set of all directed edges between evidence items."""

    hierarchy: Tuple[Tuple[str, int], ...] = field(default_factory=tuple)
    """Evidence hierarchy levels (evidence_id, level)."""

    timescales: Tuple[str, ...] = field(default_factory=tuple)
    """Temporal partitions in the graph."""

    provenance: Optional[str] = None
    """Provenance reference for this graph."""

    revision: int = 0
    """Revision number for versioning."""

    @property
    def node_count(self) -> int:
        """Get count of nodes in the graph."""
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        """Get count of edges in the graph."""
        return len(self.edges)

    @classmethod
    def create(
        cls,
        graph_id: str,
        nodes: Tuple[str, ...],
        edges: Tuple[EvidenceEdge, ...],
        hierarchy: Tuple[Tuple[str, int], ...] = tuple(),
        timescales: Tuple[str, ...] = tuple(),
        provenance: Optional[str] = None,
    ) -> RewardEvidenceGraph:
        """
        Create a new evidence graph.

        Args:
            graph_id: Unique identifier for this graph
            nodes: Set of all evidence IDs in the graph
            edges: Set of all directed edges between evidence items
            hierarchy: Evidence hierarchical structure
            timescales: Temporal partitions in the graph
            provenance: Provenance reference for this graph

        Returns:
            New RewardEvidenceGraph instance
        """
        return cls(
            graph_id=graph_id,
            nodes=tuple(sorted(nodes)),  # Ensure deterministic ordering
            edges=tuple(edges),
            hierarchy=tuple(sorted(hierarchy, key=lambda x: (x[0], x[1]))),
            timescales=tuple(sorted(set(timescales))),
            provenance=provenance,
        )


def build_evidence_graph(
    evidences: Tuple[str, ...],
) -> RewardEvidenceGraph:
    """
    Build a basic evidence graph from evidence IDs.

    Creates a simple graph with no edges (just nodes).

    Args:
        evidences: Tuple of evidence IDs

    Returns:
        Basic RewardEvidenceGraph
    """
    return RewardEvidenceGraph.create(
        graph_id=f"evidence-graph-{len(evidences)}-nodes",
        nodes=evidences,
        edges=tuple(),
    )


def add_support_edge(
    graph: RewardEvidenceGraph,
    source: str,
    target: str,
    confidence: float = 1.0,
) -> RewardEvidenceGraph:
    """
    Add a support edge to the evidence graph.

    Args:
        graph: The base evidence graph
        source: Source evidence ID (the supporting evidence)
        target: Target evidence ID (what is being supported)
        confidence: Confidence in this relationship

    Returns:
        New graph with added edge
    """
    new_edge = (
        source,
        target,
        EvidenceRelationship(
            relationship_type="supports",
            confidence=confidence,
        ),
    )

    return RewardEvidenceGraph.create(
        graph_id=f"{graph.graph_id}-extended",
        nodes=graph.nodes,
        edges=(*graph.edges, new_edge),
        hierarchy=graph.hierarchy,
        timescales=graph.timescales,
        provenance=graph.provenance,
    )