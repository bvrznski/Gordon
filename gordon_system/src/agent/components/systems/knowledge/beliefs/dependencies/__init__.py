# Knowledge Belief System - Dependencies Module - Phase 6.6
# ===========================================================

"""
Dependencies module for belief dependency management.

This module handles the graph of epistemic dependencies between beliefs,
enabling efficient propagation of confidence, uncertainty, and state changes.
"""

from __future__ import annotations

import uuid
import time


class BeliefDependencyManager:
    """
    Manages belief dependency relationships.
    
    Tracks which beliefs depend on which other beliefs for their
    epistemic support.
    """
    
    def __init__(self):
        """Initialize the manager."""
        self._edges: dict = {}  # {dependent_id: [supporting_ids]}
        self._reverse_edges: dict = {}  # {supporting_id: [dependent_ids]}
        self._edge_kinds: dict = {}  # {(dep, sup): kind}
    
    @property
    def node_count(self) -> int:
        """Get count of unique nodes."""
        all_nodes = set(self._edges.keys()) | set(self._reverse_edges.keys())
        return len(all_nodes)
    
    @property
    def edge_count(self) -> int:
        """Get total number of dependency edges."""
        return sum(len(v) for v in self._edges.values())
    
    def add_dependency(
        self,
        dependent_id: str,
        supporting_id: str,
        kind: str = "evidence",
    ) -> dict:
        """
        Add a dependency edge.
        
        Args:
            dependent_id: Belief that depends on another
            supporting_id: Belief being depended upon
            kind: Kind of dependency (default: "evidence")
            
        Returns:
            Record dictionary with edge info
        """
        if dependent_id not in self._edges:
            self._edges[dependent_id] = []
        
        # Avoid duplicate edges
        if supporting_id not in self._edges[dependent_id]:
            self._edges[dependent_id].append(supporting_id)
        
        if supporting_id not in self._reverse_edges:
            self._reverse_edges[supporting_id] = []
        self._reverse_edges[supporting_id].append(dependent_id)
        
        edge_key = (dependent_id, supporting_id)
        self._edge_kinds[edge_key] = kind
        
        return {
            "dependent_id": dependent_id,
            "supporting_id": supporting_id,
            "kind": kind,
            "timestamp_utc": time.time(),
        }
    
    def remove_dependency(
        self,
        dependent_id: str,
        supporting_id: str,
    ) -> bool:
        """
        Remove a dependency edge.
        
        Args:
            dependent_id: Belief that was depending
            supporting_id: Belief being depended upon
            
        Returns:
            True if edge was removed, False if not found
        """
        removed = False
        
        if dependent_id in self._edges:
            if supporting_id in self._edges[dependent_id]:
                self._edges[dependent_id].remove(supporting_id)
                removed = True
        
        if supporting_id in self._reverse_edges:
            if dependent_id in self._reverse_edges[supporting_id]:
                self._reverse_edges[supporting_id].remove(dependent_id)
        
        edge_key = (dependent_id, supporting_id)
        if edge_key in self._edge_kinds:
            del self._edge_kinds[edge_key]
        
        return removed
    
    def get_dependents(self, belief_id: str) -> list:
        """Get beliefs that depend on the given belief."""
        return list(self._edges.get(belief_id, []))
    
    def get_supporters(self, belief_id: str) -> list:
        """Get beliefs that the given belief depends on."""
        return list(self._reverse_edges.get(belief_id, []))
    
    def get_all_beliefs(self) -> set:
        """Get all beliefs in the graph."""
        return set(self._edges.keys()) | set(self._reverse_edges.keys())
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "edges": {k: list(v) for k, v in self._edges.items()},
            "reverse_edges": {k: list(v) for k, v in self._reverse_edges.items()},
            "kinds": {
                f"{k[0]}->{k[1]}": v
                for k, v in self._edge_kinds.items()
            },
        }


class DependencyGraph:
    """
    Represents a complete dependency graph.
    
    Provides methods for traversing the dependency structure and
    calculating dependency metrics.
    """
    
    def __init__(self):
        """Initialize the graph."""
        self._manager = BeliefDependencyManager()
    
    @property
    def node_count(self) -> int:
        """Get count of nodes."""
        return self._manager.node_count
    
    @property
    def edge_count(self) -> int:
        """Get count of edges."""
        return self._manager.edge_count
    
    def add_edge(
        self,
        dependent_id: str,
        supporting_id: str,
        kind: str = "evidence",
    ):
        """Add an edge to the graph."""
        self._manager.add_dependency(dependent_id, supporting_id, kind)
    
    def remove_edge(self, dependent_id: str, supporting_id: str):
        """Remove an edge from the graph."""
        self._manager.remove_dependency(dependent_id, supporting_id)
    
    def get_upstream_beliefs(self, belief_id: str) -> list:
        """
        Get all upstream beliefs (dependencies) for a belief.
        
        Args:
            belief_id: The belief to trace
            
        Returns:
            List of all upstream belief IDs
        """
        result = []
        to_process = [belief_id]
        processed = set()
        
        while to_process:
            current = to_process.pop(0)
            if current in processed:
                continue
            processed.add(current)
            
            supporters = self._manager.get_supporters(current)
            for s in supporters:
                if s not in result and s not in processed:
                    result.append(s)
                    to_process.append(s)
        
        return result
    
    def get_downstream_beliefs(self, belief_id: str) -> list:
        """
        Get all downstream beliefs (dependents) for a belief.
        
        Args:
            belief_id: The belief to trace
            
        Returns:
            List of all downstream belief IDs
        """
        result = []
        to_process = [belief_id]
        processed = set()
        
        while to_process:
            current = to_process.pop(0)
            if current in processed:
                continue
            processed.add(current)
            
            dependents = self._manager.get_dependents(current)
            for d in dependents:
                if d not in result and d not in processed:
                    result.append(d)
                    to_process.append(d)
        
        return result
    
    def get_path(
        self,
        from_belief: str,
        to_belief: str,
    ) -> list | None:
        """
        Find a path between two beliefs.
        
        Args:
            from_belief: Starting belief
            to_belief: Target belief
            
        Returns:
            List of belief IDs forming the path, or None if no path
        """
        # BFS for shortest path
        visited = {from_belief}
        queue = [(from_belief, [from_belief])]
        
        while queue:
            current, path = queue.pop(0)
            
            if current == to_belief:
                return path
            
            dependents = self._manager.get_dependents(current)
            for d in dependents:
                if d not in visited:
                    visited.add(d)
                    queue.append((d, path + [d]))
        
        return None
    
    def has_cycle(self) -> bool:
        """
        Check if the graph contains any cycles.
        
        Returns:
            True if a cycle exists, False otherwise
        """
        # DFS-based cycle detection
        visited = set()
        rec_stack = set()
        
        all_nodes = self._manager.get_all_beliefs()
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self._manager.get_dependents(node):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in all_nodes:
            if node not in visited:
                if dfs(node):
                    return True
        
        return False


class DependencyPropagationEngine:
    """
    Engine for propagating metrics through dependency graph.
    
    Implements strategies for propagating confidence, uncertainty,
    and belief state changes.
    """
    
    def __init__(self):
        """Initialize the engine."""
        self._propagation_count = 0
    
    @property
    def total_propagations(self) -> int:
        """Get total number of propagation operations."""
        return self._propagation_count
    
    def propagate_average(
        self,
        source_values: list[float],
    ) -> float:
        """
        Propagate using average strategy.
        
        Args:
            source_values: Values from upstream beliefs
            
        Returns:
            Averaged value
        """
        if not source_values:
            return 0.5
        
        result = sum(source_values) / len(source_values)
        self._propagation_count += 1
        return result
    
    def propagate_weighted(
        self,
        source_values: list[float],
        weights: list[float] = None,
    ) -> float:
        """
        Propagate using weighted average strategy.
        
        Args:
            source_values: Values from upstream beliefs
            weights: Optional weights for each value
            
        Returns:
            Weighted average value
        """
        if not source_values:
            return 0.5
        
        if weights is None or len(weights) != len(source_values):
            weights = [1.0] * len(source_values)
        
        total_weight = sum(weights)
        weighted_sum = sum(v * w for v, w in zip(source_values, weights))
        
        result = weighted_sum / total_weight if total_weight > 0 else 0.5
        self._propagation_count += 1
        return result
    
    def propagate_min(
        self,
        source_values: list[float],
    ) -> float:
        """
        Propagate using minimum strategy (conservative).
        
        Args:
            source_values: Values from upstream beliefs
            
        Returns:
            Minimum value
        """
        if not source_values:
            return 0.5
        
        result = min(source_values)
        self._propagation_count += 1
        return result
    
    def propagate_max(
        self,
        source_values: list[float],
    ) -> float:
        """
        Propagate using maximum strategy (optimistic).
        
        Args:
            source_values: Values from upstream beliefs
            
        Returns:
            Maximum value
        """
        if not source_values:
            return 0.5
        
        result = max(source_values)
        self._propagation_count += 1
        return result


__all__ = [
    "BeliefDependencyManager",
    "DependencyGraph",
    "DependencyPropagationEngine",
]