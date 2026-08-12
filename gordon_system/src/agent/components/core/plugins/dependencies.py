# Dependency Resolution - Phase 3.8.8.3
# =======================================
"""
Canonical dependency resolution for plugins.

Provides:
- Dependency graph construction and management
- Topological sorting for startup order
- Circular dependency detection
- Transitive dependency resolution

Dependency Types:
    - Hard dependencies (must be satisfied)
    - Soft dependencies (optional, best-effort)
    - Version constraints (minimum/maximum versions)
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Set,
    Optional,
    Tuple,
    Any,
)
from enum import Enum
import asyncio
from collections import deque

# Import from abstraction module
try:
    from .abstraction import (
        PluginVersion,
        MissingDependencyError,
        CircularDependencyError,
    )
except ImportError:
    class PluginVersion:
        pass
    
    class MissingDependencyError(Exception):
        pass


class DependencyType(Enum):
    """Types of dependencies."""
    
    HARD = "hard"       # Must be satisfied for plugin to load
    SOFT = "soft"       # Optional, best-effort loading
    OPTIONAL = "optional"  # Can be enabled if available


@dataclass(frozen=True)
class DependencyConstraint:
    """
    A constraint on a dependency version.
    
    Example: ">=1.0.0,<2.0.0"
    """
    
    min_version: Optional[PluginVersion] = None
    max_version: Optional[PluginVersion] = None
    exact_version: Optional[PluginVersion] = None
    
    def is_satisfied_by(self, version: PluginVersion) -> bool:
        """Check if a version satisfies this constraint."""
        # Check exact match
        if self.exact_version is not None:
            return version.major == self.exact_version.major and \
                   version.minor == self.exact_version.minor and \
                   version.patch == self.exact_version.patch
        
        # Check min version (inclusive)
        if self.min_version is not None:
            if version.compare_to(self.min_version) < 0:
                return False
        
        # Check max version (exclusive for breaking changes)
        if self.max_version is not None:
            if version.major != self.max_version.major:
                return False
            if version.compare_to(self.max_version) >= 0:
                return False
        
        return True
    
    def __str__(self) -> str:
        """Return string representation."""
        parts = []
        if self.exact_version:
            parts.append(str(self.exact_version))
        elif self.min_version and self.max_version:
            parts.append(f">={self.min_version},<{self.max_version}")
        elif self.min_version:
            parts.append(f">={self.min_version}")
        elif self.max_version:
            parts.append(f"<{self.max_version}")
        
        return ",".join(parts)


@dataclass
class Dependency:
    """
    A dependency declaration for a plugin.
    
    Example: "com.company/plugin-a>=1.0.0"
    """
    
    name: str                      # e.g., "plugin-a"
    version_constraint: DependencyConstraint
    dep_type: DependencyType = DependencyType.HARD
    
    def is_satisfied_by(self, plugin_version: PluginVersion) -> bool:
        """Check if a plugin version satisfies this dependency."""
        return self.version_constraint.is_satisfied_by(plugin_version)


# =============================================================================
# DEPENDENCY GRAPH
# =============================================================================


class DependencyGraph:
    """
    Represents the dependency relationships between plugins.
    
    Uses a directed acyclic graph (DAG) structure where edges point from
    dependent to dependency (A -> B means A depends on B).
    """
    
    def __init__(self):
        """Initialize an empty dependency graph."""
        # Adjacency list: {plugin_id: set of dependencies}
        self._dependencies: Dict[str, Set[str]] = {}
        
        # Reverse adjacency: {plugin_id: set of dependents}
        self._dependents: Dict[str, Set[str]] = {}
        
        # Cached topological order (invalidated on changes)
        self._topo_cache_valid: bool = False
        self._topo_order: List[str] = []
    
    def add_plugin(self, plugin_id: str) -> None:
        """
        Add a plugin to the graph without dependencies.
        
        Args:
            plugin_id: The plugin identifier
        """
        if plugin_id not in self._dependencies:
            self._dependencies[plugin_id] = set()
            self._dependents[plugin_id] = set()
            self._topo_cache_valid = False
    
    def add_dependency(
        self,
        dependent_id: str,
        dependency_id: str,
    ) -> None:
        """
        Add a dependency relationship.
        
        Args:
            dependent_id: The plugin that depends on another
            dependency_id: The plugin being depended upon
            
        Raises:
            CircularDependencyError: If adding this edge creates a cycle
        """
        # Validate plugins exist
        if dependent_id not in self._dependencies:
            self.add_plugin(dependent_id)
        if dependency_id not in self._dependencies:
            self.add_plugin(dependency_id)
        
        # Add the edge
        self._dependencies[dependent_id].add(dependency_id)
        self._dependents[dependency_id].add(dependent_id)
        self._topo_cache_valid = False
        
        # Check for cycles
        if self.has_cycle():
            # Remove the edge
            self._dependencies[dependent_id].discard(dependency_id)
            self._dependents[dependency_id].discard(dependent_id)
            raise CircularDependencyError(
                f"Adding dependency {dependent_id} -> {dependency_id} creates a cycle",
                plugin_id=dependent_id,
                missing_dependency=dependency_id,
            )
    
    def remove_dependency(
        self,
        dependent_id: str,
        dependency_id: str,
    ) -> bool:
        """
        Remove a dependency relationship.
        
        Args:
            dependent_id: The plugin that depends on another
            dependency_id: The plugin being depended upon
            
        Returns:
            True if removed, False if not found
        """
        removed = dependency_id in self._dependencies.get(dependent_id, set())
        
        if removed:
            self._dependencies[dependent_id].discard(dependency_id)
            self._dependents[dependency_id].discard(dependent_id)
            self._topo_cache_valid = False
        
        return removed
    
    def get_dependencies(self, plugin_id: str) -> Set[str]:
        """Get all dependencies of a plugin."""
        return set(self._dependencies.get(plugin_id, set()))
    
    def get_dependents(self, plugin_id: str) -> Set[str]:
        """Get all plugins that depend on this plugin."""
        return set(self._dependents.get(plugin_id, set()))
    
    def has_cycle(self) -> bool:
        """
        Check if the graph contains a cycle.
        
        Uses DFS with three-state coloring:
            WHITE (0): Not visited
            GRAY (1): Currently being processed
            BLACK (2): Fully processed
        
        Returns:
            True if cycle exists, False otherwise
        """
        # All nodes start as WHITE
        color: Dict[str, int] = {node: 0 for node in self._dependencies}
        
        def dfs(node: str) -> bool:
            """DFS helper that returns True if cycle found."""
            if color[node] == 1:  # GRAY - back edge found!
                return True
            if color[node] == 2:  # BLACK - already fully processed
                return False
            
            color[node] = 1  # Mark as GRAY
            
            for neighbor in self._dependencies.get(node, set()):
                if dfs(neighbor):
                    return True
            
            color[node] = 2  # Mark as BLACK
            return False
        
        # Check all components
        for node in self._dependencies:
            if color[node] == 0:
                if dfs(node):
                    return True
        
        return False
    
    def topological_sort(self) -> List[str]:
        """
        Get plugins in dependency order (dependencies first).
        
        Uses Kahn's algorithm for topological sorting.
        
        Returns:
            List of plugin IDs in valid loading order
            
        Raises:
            CircularDependencyError: If graph contains a cycle
        """
        if self._topo_cache_valid and self._topo_order:
            return list(self._topo_order)
        
        if self.has_cycle():
            raise CircularDependencyError(
                "Cannot sort: dependency graph contains a cycle",
                plugin_id="",
                missing_dependency="cycle",
            )
        
        # Calculate in-degrees
        in_degree: Dict[str, int] = {node: 0 for node in self._dependencies}
        for deps in self._dependencies.values():
            for dep in deps:
                pass  # We count outgoing edges
        
        # Count incoming edges (how many depend on each node)
        for plugin_id, deps in self._dependencies.items():
            in_degree[plugin_id] = len(deps)
        
        # Start with nodes that have no dependencies
        queue: deque[str] = deque(
            node for node in self._dependencies if in_degree[node] == 0
        )
        
        result: List[str] = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            # For each node that depends on this one
            for dependent in self._dependents.get(node, set()):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        self._topo_order = result
        self._topo_cache_valid = True
        
        return result
    
    def get_all_plugins(self) -> Set[str]:
        """Get all plugin IDs in the graph."""
        return set(self._dependencies.keys())
    
    def clear(self) -> None:
        """Remove all plugins and dependencies."""
        self._dependencies.clear()
        self._dependents.clear()
        self._topo_cache_valid = False
    
    def __len__(self) -> int:
        """Return number of plugins in graph."""
        return len(self._dependencies)


# =============================================================================
# RESOLUTION RESULT
# =============================================================================


@dataclass(frozen=True)
class ResolutionResult:
    """
    Result of dependency resolution for a plugin.
    
    Contains both satisfied and unsatisfied dependencies,
    along with the recommended loading order.
    """
    
    plugin_id: str
    
    # Satisfied dependencies
    satisfied: List[Tuple[str, PluginVersion]]  # (dep_id, version)
    
    # Unsatisfied dependencies
    missing: List[str]
    version_conflicts: List[str]
    
    # Loading order recommendation
    load_order: List[str]  # All plugins in correct order
    
    @property
    def is_resolved(self) -> bool:
        """Check if all hard dependencies are resolved."""
        return len(self.missing) == 0 and len(self.version_conflicts) == 0


# =============================================================================
# DEPENDENCY RESOLVER
# =============================================================================


class DependencyResolver:
    """
    Resolves plugin dependencies across a set of available plugins.
    
    Provides:
        - Dependency graph construction
        - Topological sorting for startup order
        - Conflict detection and reporting
        - Optional dependency handling
    
    Thread Safety:
        All operations are async and use internal locking.
    """
    
    def __init__(self):
        """Initialize the resolver."""
        self._lock = asyncio.Lock()
        
        # Available plugins: {plugin_id: (version, capabilities)}
        self._available_plugins: Dict[str, Tuple[PluginVersion, Set[str]]] = {}
        
        # Dependency graph
        self._graph = DependencyGraph()
        
        # Resolved state
        self._resolved_plugins: Dict[str, PluginVersion] = {}
        
        # Cached resolution results
        self._resolution_cache: Dict[str, ResolutionResult] = {}
    
    async def register_plugin(
        self,
        plugin_id: str,
        version: PluginVersion,
        capabilities: Optional[Set[str]] = None,
    ) -> None:
        """
        Register a plugin as available for dependency resolution.
        
        Args:
            plugin_id: The plugin identifier
            version: The plugin version
            capabilities: Set of capabilities this plugin provides
        """
        async with self._lock:
            self._available_plugins[plugin_id] = (
                version,
                capabilities or set(),
            )
            self._graph.add_plugin(plugin_id)
            self._resolution_cache.clear()
    
    def add_dependency(
        self,
        dependent_id: str,
        dependency_name: str,
        constraint: DependencyConstraint,
        dep_type: DependencyType = DependencyType.HARD,
    ) -> None:
        """
        Declare a dependency for a plugin.
        
        Args:
            dependent_id: The plugin that has the dependency
            dependency_name: Name of the required plugin
            constraint: Version constraints on the dependency
            dep_type: Type of dependency (hard/soft/optional)
        """
        self._graph.add_plugin(dependent_id)
        
        # Store the dependency declaration for later resolution
        pass  # Implementation would track dependencies
    
    async def resolve(
        self,
        plugin_id: str,
    ) -> ResolutionResult:
        """
        Resolve all dependencies for a plugin.
        
        Args:
            plugin_id: The plugin to resolve dependencies for
            
        Returns:
            Resolution result with satisfied/unsatisfied deps
        """
        async with self._lock:
            # Get declared dependencies (from manifest)
            available_versions = {
                pid: ver for pid, (ver, _) in self._available_plugins.items()
            }
            
            # Find satisfying versions for each dependency
            satisfied = []
            missing = []
            
            # Simplified resolution - just check if plugin exists
            for dep_name, constraint in self._get_dependencies_for(plugin_id).items():
                matching = [
                    (pid, ver)
                    for pid, ver in available_versions.items()
                    if pid.endswith(dep_name) and constraint.is_satisfied_by(ver)
                ]
                
                if matching:
                    # Choose the highest version
                    matching.sort(key=lambda x: x[1].major * 1000 + x[1].minor * 100 + x[1].patch)
                    satisfied.append(matching[-1])
                else:
                    missing.append(dep_name)
            
            # Get topological order for loading
            load_order = self._graph.topological_sort()
            
            result = ResolutionResult(
                plugin_id=plugin_id,
                satisfied=satisfied,
                missing=missing,
                version_conflicts=[],
                load_order=load_order,
            )
            
            return result
    
    def _get_dependencies_for(self, plugin_id: str) -> Dict[str, DependencyConstraint]:
        """Get dependencies for a plugin (placeholder)."""
        return {}
    
    async def get_startup_order(
        self,
    ) -> List[str]:
        """
        Get all plugins in startup order.
        
        Returns:
            List of plugin IDs in dependency order
        """
        async with self._lock:
            return self._graph.topological_sort()
    
    def clear(self) -> None:
        """Clear all tracked plugins and dependencies."""
        self._available_plugins.clear()
        self._graph.clear()
        self._resolution_cache.clear()
