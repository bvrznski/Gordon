# Core Dependency Management
# ==========================

"""
Core runtime dependency management.

Provides explicit dependency declaration, graph representation,
topological ordering, and cycle detection.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
from enum import Enum


@dataclass(frozen=True)
class Dependency:
    """A dependency relationship (this depends on that)."""
    
    from_entity: str  # The dependent entity
    to_entity: str    # The required entity
    required: bool = True
    
    def __hash__(self) -> int:
        return hash((self.from_entity, self.to_entity))


@dataclass(frozen=True)
class DependencyGraph:
    """
    Immutable dependency graph representation.
    
    Dependencies are directional: A -> B means "A depends on B"
    """
    
    _edges: Dict[str, Set[str]] = field(default_factory=dict)  # from -> set of to
    _reverse_edges: Dict[str, Set[str]] = field(default_factory=dict)  # to -> set of from
    
    @classmethod
    def create(cls, dependencies: List[Dependency]) -> "DependencyGraph":
        """Create a graph from a list of dependencies."""
        edges: Dict[str, Set[str]] = {}
        reverse_edges: Dict[str, Set[str]] = {}
        
        for dep in dependencies:
            # Add forward edge: from -> to
            if dep.from_entity not in edges:
                edges[dep.from_entity] = set()
            edges[dep.from_entity].add(dep.to_entity)
            
            # Add reverse edge: to <- from
            if dep.to_entity not in reverse_edges:
                reverse_edges[dep.to_entity] = set()
            reverse_edges[dep.to_entity].add(dep.from_entity)
        
        return cls(_edges=edges, _reverse_edges=reverse_edges)
    
    @property
    def nodes(self) -> Set[str]:
        """Get all unique nodes in the graph."""
        all_nodes: Set[str] = set()
        for from_node, to_nodes in self._edges.items():
            all_nodes.add(from_node)
            all_nodes.update(to_nodes)
        return all_nodes
    
    @property
    def edges(self) -> List[Tuple[str, str]]:
        """Get all edges as (from, to) tuples."""
        result: List[Tuple[str, str]] = []
        for from_node, to_nodes in self._edges.items():
            for to_node in to_nodes:
                result.append((from_node, to_node))
        return result
    
    def get_dependencies(self, entity: str) -> Set[str]:
        """Get entities that the given entity depends on."""
        return set(self._edges.get(entity, set()))
    
    def get_dependents(self, entity: str) -> Set[str]:
        """Get entities that depend on the given entity."""
        return set(self._reverse_edges.get(entity, set()))
    
    def has_cycle(self) -> bool:
        """
        Check if the graph contains a cycle.
        
        Returns:
            True if there is a cycle, False otherwise
        """
        # Use DFS with three states: unvisited, visiting, visited
        state: Dict[str, str] = {node: "unvisited" for node in self.nodes}
        
        def dfs(node: str) -> bool:
            """Return True if cycle found."""
            if state.get(node) == "visiting":
                return True  # Back edge found - cycle exists
            if state.get(node) == "visited":
                return False
            
            state[node] = "visiting"
            
            for neighbor in self._edges.get(node, set()):
                if dfs(neighbor):
                    return True
            
            state[node] = "visited"
            return False
        
        for node in self.nodes:
            if state[node] == "unvisited":
                if dfs(node):
                    return True
        
        return False
    
    def find_cycle(self) -> Optional[List[str]]:
        """
        Find a cycle in the graph if one exists.
        
        Returns:
            List of nodes forming a cycle, or None if no cycle
        """
        state: Dict[str, str] = {node: "unvisited" for node in self.nodes}
        parent: Dict[str, Optional[str]] = {}
        
        def dfs(node: str) -> Optional[List[str]]:
            """Return cycle path if found."""
            if state.get(node) == "visiting":
                # Found back edge - reconstruct cycle
                cycle = [node]
                current = parent[node]
                while current and current != node:
                    cycle.append(current)
                    current = parent.get(current)
                cycle.reverse()
                return cycle
            
            if state.get(node) == "visited":
                return None
            
            state[node] = "visiting"
            
            for neighbor in self._edges.get(node, set()):
                parent[neighbor] = node
                result = dfs(neighbor)
                if result:
                    return result
            
            state[node] = "visited"
            return None
        
        for node in self.nodes:
            if state[node] == "unvisited":
                cycle = dfs(node)
                if cycle:
                    return cycle
        
        return None
    
    def topological_sort(self) -> List[str]:
        """
        Perform topological sort on the graph.
        
        Returns:
            List of nodes in dependency order (dependencies first)
            
        Raises:
            ValueError: If graph contains a cycle
        """
        if self.has_cycle():
            cycle = self.find_cycle()
            raise ValueError(f"Cannot topologically sort cyclic graph. Cycle: {cycle}")
        
        # Kahn's algorithm
        in_degree: Dict[str, int] = {node: 0 for node in self.nodes}
        for from_node, to_nodes in self._edges.items():
            for to_node in to_nodes:
                in_degree[from_node] = in_degree.get(from_node, 0) + 1
        
        # Start with nodes that have no incoming edges (no dependencies)
        queue: List[str] = [n for n in self.nodes if in_degree[n] == 0]
        result: List[str] = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # For each entity that depends on this node
            for dependent in self._reverse_edges.get(node, set()):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        return result
    
    def reverse_topological_sort(self) -> List[str]:
        """
        Perform reverse topological sort (dependencies last).
        
        Returns:
            List of nodes in reverse dependency order (dependents first)
        """
        return list(reversed(self.topological_sort()))
    
    def without_node(self, node: str) -> "DependencyGraph":
        """Return a new graph with the given node removed."""
        new_edges: Dict[str, Set[str]] = {}
        
        for from_node, to_nodes in self._edges.items():
            if from_node != node:
                filtered = {t for t in to_nodes if t != node}
                if filtered or from_node in self.nodes - {node}:
                    new_edges[from_node] = filtered
        
        return DependencyGraph(_edges=new_edges)
    
    def is_empty(self) -> bool:
        """Check if graph has no edges."""
        return len(self._edges) == 0


class DependencyResolver:
    """
    Resolve dependencies and determine startup/shutdown order.
    """
    
    @staticmethod
    def resolve_order(graph: DependencyGraph, entities: List[str]) -> List[str]:
        """
        Resolve the execution order for given entities based on dependencies.
        
        Args:
            graph: The dependency graph
            entities: List of entity names to order
            
        Returns:
            Entities in dependency-satisfying order
            
        Raises:
            ValueError: If dependencies cannot be satisfied (cycle or missing)
        """
        # Get full dependency info
        all_nodes = graph.nodes
        
        # Check if requested entities are in the graph
        for entity in entities:
            if entity not in all_nodes:
                raise ValueError(f"Entity '{entity}' not found in dependency graph")
        
        # Get topological order and filter to just our entities
        full_order = graph.topological_sort()
        ordered_entities = [e for e in full_order if e in set(entities)]
        
        return ordered_entities
    
    @staticmethod
    def find_missing_dependencies(
        graph: DependencyGraph,
        entities: List[str]
    ) -> Dict[str, List[str]]:
        """
        Find missing dependencies for the given entities.
        
        Args:
            graph: The dependency graph
            entities: Entities to check
            
        Returns:
            Mapping of entity -> list of missing dependencies
        """
        missing: Dict[str, List[str]] = {}
        all_nodes = graph.nodes
        
        for entity in entities:
            deps = graph.get_dependencies(entity)
            missing_deps = [d for d in deps if d not in all_nodes]
            if missing_deps:
                missing[entity] = missing_deps
        
        return missing


__all__ = [
    "Dependency",
    "DependencyGraph",
    "DependencyResolver",
]
