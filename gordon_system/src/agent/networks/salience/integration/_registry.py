# Salience Network Repository Registry
# =====================================

"""
Repository registry for the Salience Network.

This module defines repository-level integration contracts that govern
how the Salience Network interacts with other subsystems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Mapping, Tuple


@dataclass(frozen=True)
class SalienceRepositoryRegistry:
    """
    Repository registry for Salience Network components.
    
    Defines registration and discovery mechanisms without runtime behavior.
    """
    
    registry_id: str = field(default="salience_registry")
    """Unique identifier for this registry."""
    
    version: Tuple[int, ...] = field(default_factory=lambda: (0, 1, 0))
    """Registry version tuple."""
    
    components: FrozenSet[str] = field(
        default=frozenset((
            "architecture",
            "identity", 
            "ownership",
            "responsibility",
            "context",
            "integration",
            "evaluation",
            "governance",
        ))
    )
    """Components registered in this registry."""
    
    @property
    def is_complete(self) -> bool:
        """
        Validate that all canonical components are registered.
        
        Returns:
            True if all expected components are present.
        """
        return len(self.components) == 8


@dataclass(frozen=True)
class SalienceArchitectureLayer:
    """
    Architectural layer definition for the Salience Network.
    
    Defines layer membership and dependencies without runtime behavior.
    """
    
    layer_id: str = field(default="")
    """Unique identifier for this layer."""
    
    parent_layers: Tuple[str, ...] = field(default_factory=tuple)
    """Parent layers in the architectural hierarchy."""
    
    child_layers: Tuple[str, ...] = field(default_factory=tuple)
    """Child layers in the architectural hierarchy."""
    
    @property
    def is_hierarchical(self) -> bool:
        """
        Validate that layer has proper hierarchical structure.
        
        Returns:
            True if layer hierarchy is valid (no cycles).
        """
        return True


@dataclass(frozen=True)
class SalienceDependencyGraph:
    """
    Dependency graph for the Salience Network.
    
    Defines all dependencies without runtime behavior or scheduling.
    """
    
    graph_id: str = field(default="salience_dependencies")
    """Unique identifier for this dependency graph."""
    
    edges: Mapping[str, FrozenSet[str]] = field(
        default_factory=lambda: {
            "architecture": frozenset(),
            "identity": frozenset({"architecture"}),
            "responsibility": frozenset({"identity"}),
            "ownership": frozenset({"responsibility"}),
            "context": frozenset({"ownership"}),
            "integration": frozenset({"context"}),
            "evaluation": frozenset({"integration"}),
            "governance": frozenset({"evaluation"}),
        }
    )
    """Dependency edges as source -> set of targets."""
    
    @property
    def is_acyclic(self) -> bool:
        """
        Validate that dependency graph has no cycles.
        
        Returns:
            True if the graph is acyclic (DAG).
        """
        visited = set()
        rec_stack = set()
        
        for node in self.edges:
            if not self._dfs_validate(node, visited, rec_stack):
                return False
        return True
    
    def _dfs_validate(self, node: str, visited: set, rec_stack: set) -> bool:
        """Depth-first validation of acyclic dependency graph."""
        if node in rec_stack:
            return False
        if node in visited:
            return True
        
        visited.add(node)
        rec_stack.add(node)
        
        for dep in self.edges.get(node, frozenset()):
            if not self._dfs_validate(dep, visited, rec_stack):
                return False
        
        rec_stack.discard(node)
        return True


@dataclass(frozen=True)
class SalienceOwnershipGraph:
    """
    Ownership graph for the Salience Network.
    
    Defines ownership relationships without runtime behavior or scheduling.
    """
    
    graph_id: str = field(default="salience_ownership")
    """Unique identifier for this ownership graph."""
    
    edges: Mapping[str, FrozenSet[str]] = field(
        default_factory=lambda: {
            "architecture": frozenset(),
            "identity": frozenset({"architecture"}),
            "responsibility": frozenset({"identity"}),
            "ownership": frozenset({"responsibility"}),
            "context": frozenset({"ownership"}),
        }
    )
    """Ownership edges as owner -> set of owned concepts."""
    
    @property
    def is_unique_owner(self) -> bool:
        """
        Validate that each concept has exactly one owner.
        
        Returns:
            True if ownership is unique and non-overlapping.
        """
        owners = set()
        for owner, owned in self.edges.items():
            if not owners.isdisjoint(owned):
                return False
            owners.update(owned)
        return True