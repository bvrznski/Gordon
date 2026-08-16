# Salience Network Competition Graph
# ===================================

"""
Canonical competition graph model (Phase 4.8.6).

The CompetitionGraph represents relationships between candidates:
    - Dominance edges (who has higher priority)
    - Inhibition edges (who suppresses whom)
    - Facilitation edges (who reinforces whom)
    - Equivalence edges (equal priority candidates)

GRAPH INVARIANTS:
    COMPETITION-GRAPH-INV-001: Nodes are candidate state identities
    COMPETITION-GRAPH-INV-002: Edges have exactly one relationship type
    COMPETITION-GRAPH-INV-003: Graph is immutable (frozen dataclass)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class CompetitionGraph:
    """
    Immutable competition graph.
    
    The graph represents semantic relationships between candidates without
    modifying candidate states.
    
    GRAPH INVARIANTS:
        COMPETITION-GRAPH-INV-001: All nodes reference valid candidates
        COMPETITION-GRAPH-INV-002: No duplicate edges (same source, target, type)
        COMPETITION-GRAPH-INV-003: Graph is acyclic where required
    """
    
    # Candidate nodes in graph
    candidate_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Set of all candidate state identities."""
    
    # Dominance edges (directed)
    dominance_edges: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """
    Directed edges: (dominating_candidate_id, dominated_candidate_id)
    Example: ("A", "B") means A dominates B
    """
    
    # Inhibition edges (directed)
    inhibition_edges: Tuple[Tuple[str, str, str], ...] = field(default_factory=tuple)
    """
    Edges: (inhibitor_id, target_id, strength_label)
    Strength label: unknown, soft, moderate, strong
    """
    
    # Facilitation edges (undirected)
    facilitation_edges: Tuple[Tuple[str, str, str], ...] = field(default_factory=tuple)
    """
    Edges: (candidate_a_id, candidate_b_id, strength_label)
    Mutual reinforcement of salience
    """
    
    # Equivalence edges (undirected)
    equivalence_edges: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """Pairs of candidates with equal priority."""
    
    @property
    def node_count(self) -> int:
        """Return number of candidate nodes."""
        return len(self.candidate_ids)
    
    @property
    def edge_count(self) -> int:
        """Return total number of edges."""
        return (
            len(self.dominance_edges)
            + len(self.inhibition_edges)
            + len(self.facilitation_edges)
            + len(self.equivalence_edges)
        )
    
    def get_dominance_relationship(self, candidate_a: str, candidate_b: str) -> str:
        """
        Get dominance relationship between two candidates.
        
        Returns:
            'dominates', 'dominated_by', 'equivalent', or 'unknown'
        """
        if (candidate_a, candidate_b) in self.dominance_edges:
            return "dominates"
        elif (candidate_b, candidate_a) in self.dominance_edges:
            return "dominated_by"
        
        # Check equivalence
        for a, b in self.equivalence_edges:
            if (a == candidate_a and b == candidate_b) or (a == candidate_b and b == candidate_a):
                return "equivalent"
        
        return "unknown"