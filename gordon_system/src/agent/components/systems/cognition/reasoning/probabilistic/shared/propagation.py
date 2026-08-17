# Belief and Uncertainty Propagation - Phase 7.7
# ==============================================

"""
Canonical propagation contracts for probabilistic reasoning.

Belief propagation tracks how probabilities change through dependency structures.
Uncertainty propagation preserves variance and confidence through inference chains.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DependencyStructure:
    """
    Graph structure representing dependencies between variables.
    
    Used for belief propagation and uncertainty propagation.
    """
    
    # Structure
    nodes: Tuple[str, ...] = ()           # Variables in the graph
    edges: Dict[str, List[str]] = field(default_factory=dict)  # source -> targets
    
    # Configuration
    direction: str = "directed"          # "directed" or "undirected"
    
    def add_edge(self, from_node: str, to_node: str) -> DependencyStructure:
        """Add a dependency edge."""
        new_edges = dict(self.edges)
        if from_node not in new_edges:
            new_edges[from_node] = []
        if to_node not in new_edges[from_node]:
            new_edges[from_node].append(to_node)
        
        if self.direction == "undirected":
            if to_node not in new_edges:
                new_edges[to_node] = []
            if from_node not in new_edges[to_node]:
                new_edges[to_node].append(from_node)
        
        return dataclass_replace(
            self,
            edges=new_edges,
        )
    
    def get_children(self, node: str) -> List[str]:
        """Get nodes that depend on this one (outgoing edges)."""
        return self.edges.get(node, [])
    
    def get_parents(self, target: str) -> List[str]:
        """Get nodes that this one depends on."""
        parents = []
        for source, children in self.edges.items():
            if target in children:
                parents.append(source)
        return parents
    
    def is_connected(self, node1: str, node2: str) -> bool:
        """Check if two nodes are connected (directly or indirectly)."""
        # Simple BFS
        visited = set()
        queue = [node1]
        
        while queue:
            current = queue.pop(0)
            if current == node2:
                return True
            if current in visited:
                continue
            visited.add(current)
            
            for child in self.get_children(current):
                if child not in visited:
                    queue.append(child)
        
        return False


@dataclass(frozen=True)
class PropagationPath:
    """
    A specific path through the dependency graph used for propagation.
    
    Tracks how uncertainty or belief flows from one node to another.
    """
    
    # Path information
    path_id: str                          # Unique identifier
    source_node: str                      # Starting node
    target_node: str                      # Ending node
    
    # Path steps
    intermediate_nodes: Tuple[str, ...] = ()  # Nodes in between
    
    # Configuration
    propagation_type: str = "marginal"   # "marginal", "conditional", "joint"
    
    @classmethod
    def create(cls, source: str, target: str, intermediates: List[str]) -> PropagationPath:
        """Create a new propagation path."""
        return cls(
            path_id=f"path:{uuid.uuid4().hex[:16]}",
            source_node=source,
            target_node=target,
            intermediate_nodes=tuple(intermediates),
            propagation_type="marginal",
        )


@dataclass(frozen=True)
class BeliefPropagation:
    """
    Result of propagating beliefs through a dependency structure.
    
    Shows how probability distributions change as evidence is incorporated
    through the graph.
    """
    
    # Identity
    propagation_id: str                   # Unique identifier
    
    # Input
    initial_beliefs: Dict[str, float]     # Starting probabilities per node
    propagation_path: Optional[PropagationPath] = None
    
    # Output
    final_beliefs: Dict[str, float]       # Resulting probabilities
    confidence_adjustment: float = 0.0    # How much did confidence change?
    
    # Metadata
    propagated_at_utc: float = field(default_factory=time.time)
    propagation_depth: int = 1            # How many hops through graph?
    
    @property
    def belief_change_magnitude(self) -> float:
        """Calculate total absolute change in beliefs."""
        total_change = 0.0
        for node, initial in self.initial_beliefs.items():
            final = self.final_beliefs.get(node, 0.0)
            total_change += abs(final - initial)
        return total_change


@dataclass(frozen=True)
class UncertaintyPropagation:
    """
    Result of propagating uncertainty through an inference chain.
    
    Preserves variance, confidence intervals, and distribution shape
    through propagation.
    """
    
    # Identity
    propagation_id: str                   # Unique identifier
    
    # Input uncertainty
    originating_uncertainty: float        # Initial uncertainty (e.g., entropy)
    originating_confidence: float = 0.5   # Initial confidence level
    
    # Output uncertainty
    propagated_uncertainty: float         # Resulting uncertainty
    propagated_confidence: float = 0.5    # Resulting confidence
    
    # Affected variables
    affected_variables: Tuple[str, ...] = ()  # Variables whose uncertainty changed
    
    # Propagation details
    propagation_path: Optional[PropagationPath] = None
    is_increasing: bool = False           # Did uncertainty increase?
    
    # Metadata
    propagated_at_utc: float = field(default_factory=time.time)
    
    @property
    def uncertainty_change(self) -> float:
        """Calculate absolute change in uncertainty."""
        return abs(self.propagated_uncertainty - self.originating_uncertainty)
    
    @classmethod
    def no_change(cls, variable: str, original_uncertainty: float) -> UncertaintyPropagation:
        """Create a propagation result showing no change."""
        return cls(
            propagation_id=f"propagation:{uuid.uuid4().hex[:16]}",
            originating_uncertainty=original_uncertainty,
            propagated_uncertainty=original_uncertainty,
            affected_variables=(variable,),
            is_increasing=False,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "BeliefPropagation",
    "UncertaintyPropagation",
    "PropagationPath",
    "DependencyStructure",
]