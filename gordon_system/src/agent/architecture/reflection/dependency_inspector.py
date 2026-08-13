"""Dependency Inspector - Phase 3.12.7.
================================================================================

Deterministic dependency graph inspection for Gordon Core reflection architecture.

Provides:
- CycleInfo - Detected cycle information
- DependencyReport - Complete analysis report  
- DependencyAnalysis - Analysis result
- DependencyInspector - Main inspector class
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

from ..discovery.inventory import (
    DependencyGraph,
    DependencyEdge,
)


# =============================================================================
# DEPENDENCY DATA MODELS (immutable)
# =============================================================================


@dataclass(frozen=True)
class CycleInfo:
    """Information about a detected cycle."""
    cycle_id: str
    nodes: Tuple[str, ...]
    length: int


@dataclass(frozen=True)
class DependencyReport:
    """Complete dependency analysis report."""
    graph: DependencyGraph
    cycles: Tuple[CycleInfo, ...]
    topological_order: Tuple[str, ...]


# =============================================================================
# DEPENDENCY INSPECTOR
# =============================================================================


class DependencyInspector:
    """
    Inspector for dependency relationships.
    
    Analyzes dependencies without validating them.
    Validation is the responsibility of Integrity.
    
    This inspector is:
    - Deterministic: Same input always produces same output
    - Read-only: Never modifies anything
    - Passive: Only inspects, never acts
    """
    
    def __init__(self, graph: DependencyGraph) -> None:
        """
        Initialize with a dependency graph.
        
        Args:
            graph: Complete dependency graph (immutable)
        """
        self._graph = graph
    
    def get_dependencies(self, entity_id: str) -> Tuple[str, ...]:
        """Get entities that the given entity depends on."""
        return self._graph.get_dependencies(entity_id)
    
    def get_dependents(self, entity_id: str) -> Tuple[str, ...]:
        """Get entities that depend on the given entity."""
        return self._graph.get_dependents(entity_id)
    
    def detect_cycles(self) -> Tuple[Tuple[str, ...], ...]:
        """
        Detect dependency cycles.
        
        Returns list of detected cycles (each cycle is a tuple of entity IDs).
        """
        return _detect_cycles_in_graph(self._graph)
    
    def topologically_sort(
        self,
        entities: Tuple[str, ...]
    ) -> Tuple[str, ...]:
        """
        Topologically sort entities by dependencies.
        
        Dependencies come first in the result.
        Raises ValueError if cycles exist.
        """
        return _topological_sort_graph(self._graph)
    
    def get_dependency_graph(self) -> DependencyGraph:
        """Get complete dependency graph."""
        return self._graph
    
    def get_analysis(self) -> DependencyReport:
        """Get complete dependency analysis."""
        cycles = self.detect_cycles()
        
        try:
            topo_order = self.topologically_sort(tuple(self._graph.vertices))
        except ValueError:
            topo_order = ()
        
        cycle_info = tuple(
            CycleInfo(
                cycle_id=f"cycle_{i}",
                nodes=cycle,
                length=len(cycle)
            )
            for i, cycle in enumerate(cycles)
        )
        
        return DependencyReport(
            graph=self._graph,
            cycles=cycle_info,
            topological_order=topo_order
        )


# =============================================================================
# CYCLE DETECTION (DFS-based)
# =============================================================================


def _detect_cycles_in_graph(graph: DependencyGraph) -> Tuple[Tuple[str, ...], ...]:
    """
    Detect cycles in a dependency graph using DFS.
    
    Args:
        graph: The dependency graph to analyze
        
    Returns:
        List of detected cycles
    """
    # Build adjacency list
    adj: Dict[str, Set[str]] = {}
    for edge in graph.edges:
        if edge.from_entity not in adj:
            adj[edge.from_entity] = set()
        adj[edge.from_entity].add(edge.to_entity)
    
    visited: Set[str] = set()
    rec_stack: Set[str] = set()
    cycles: List[List[str]] = []
    
    def dfs(node: str, path: List[str]) -> None:
        if node in rec_stack:
            # Found a cycle
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            cycles.append(cycle)
            return
        
        if node in visited:
            return
        
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in adj.get(node, set()):
            dfs(neighbor, path + [node])
        
        rec_stack.remove(node)
    
    for node in graph.vertices:
        if node not in visited:
            dfs(node, [])
    
    return tuple(tuple(c) for c in cycles)


# =============================================================================
# TOPOLOGICAL SORT (Kahn's algorithm)
# =============================================================================


def _topological_sort_graph(graph: DependencyGraph) -> Tuple[str, ...]:
    """
    Topologically sort a dependency graph.
    
    Args:
        graph: The dependency graph to sort
        
    Returns:
        List of nodes in topological order (dependencies first)
        
    Raises:
        ValueError: If the graph contains cycles
    """
    # Check for cycles first
    cycles = _detect_cycles_in_graph(graph)
    if cycles:
        raise ValueError(f"Cannot topologically sort cyclic dependencies")
    
    # Kahn's algorithm
    adj: Dict[str, Set[str]] = {}
    in_degree: Dict[str, int] = {}
    
    for edge in graph.edges:
        if edge.from_entity not in adj:
            adj[edge.from_entity] = set()
        adj[edge.from_entity].add(edge.to_entity)
        
        in_degree.setdefault(edge.from_entity, 0)
        in_degree[edge.to_entity] = in_degree.get(edge.to_entity, 0) + 1
    
    # Initialize with nodes that have no incoming edges
    queue: List[str] = [n for n in graph.vertices if in_degree.get(n, 0) == 0]
    result: List[str] = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        
        for neighbor in adj.get(node, set()):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return tuple(result)


def topologically_sort_dependencies(
    entities: Tuple[str, ...],
    dependencies: Dict[str, Set[str]]
) -> Tuple[str, ...]:
    """
    Topologically sort entities by their dependencies.
    
    Args:
        entities: List of entity IDs to sort
        dependencies: Mapping of entity_id -> set of dependency IDs
        
    Returns:
        Entities in topological order (dependencies first)
    """
    # Build graph representation
    adj: Dict[str, Set[str]] = {e: dependencies.get(e, set()) for e in entities}
    
    # Calculate in-degrees
    in_degree: Dict[str, int] = {e: 0 for e in entities}
    for entity in entities:
        for dep in adj.get(entity, set()):
            if dep in in_degree:
                pass
    
    # Kahn's algorithm
    queue = [e for e in entities if in_degree.get(e, 0) == 0]
    result: List[str] = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        
        for other in entities:
            if node in adj.get(other, set()):
                in_degree[other] -= 1
                if in_degree[other] == 0:
                    queue.append(other)
    
    return tuple(result)