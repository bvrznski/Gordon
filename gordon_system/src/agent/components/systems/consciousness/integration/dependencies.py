# Gordon Phase 5.7.8-I: Conscious Integration - Dependency Graph
# ===============================================================================

"""
Dependency graph for engine ordering and cycle detection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Dict, List, Set


@dataclass(frozen=True)
class EngineDependencyOrder:
    """
    Deterministic engine dependency order.

    Defines the canonical order in which engines should be processed during
    integration transitions. This ensures deterministic snapshot collection
    and prevents ordering-dependent race conditions.
    """

    # Canonical dependency order
    dependencies: Tuple[str, ...] = field(
        default=(
            "experiential_field",
            "intentional_context",
            "temporal_context",
            "presence",
            "awareness",
            "perspective",
            "situated_world",
            "conscious_integration",
        )
    )

    def get_index(self, engine_id: str) -> int:
        """Get the position index for an engine in the dependency order."""
        try:
            return self.dependencies.index(engine_id)
        except ValueError:
            raise ValueError(f"Engine not in dependency graph: {engine_id}")

    def get_before(self, engine_id: str) -> Tuple[str, ...]:
        """Get all engines that must be processed before this one."""
        idx = self.get_index(engine_id)
        return self.dependencies[:idx]

    def get_after(self, engine_id: str) -> Tuple[str, ...]:
        """Get all engines that depend on this one."""
        idx = self.get_index(engine_id)
        return self.dependencies[idx + 1 :]

    def is_before(self, first: str, second: str) -> bool:
        """Check if first must be processed before second."""
        return self.get_index(first) < self.get_index(second)


@dataclass
class DependencyGraph:
    """
    Explicit dependency graph for engine registration and ordering.

    This class tracks engine dependencies and validates that no cycles exist.
    It is used during engine registration to reject invalid dependency structures.
    """

    # Direct dependencies: engine_id -> tuple of required engine IDs
    _direct_dependencies: Dict[str, Tuple[str, ...]] = field(default_factory=dict)

    # Reverse dependencies: engine_id -> set of engines that depend on it
    _reverse_deps: Dict[str, Set[str]] = field(default_factory=dict)

    def add_engine(self, engine_id: str, required: Tuple[str, ...] = ()) -> None:
        """
        Register an engine with its dependencies.

        Args:
            engine_id: The engine identifier
            required: Tuple of engine IDs that this engine requires
        """
        # Validate all dependencies exist first
        for req in required:
            if req not in self._direct_dependencies and req != engine_id:
                raise ValueError(f"Unknown dependency for {engine_id}: {req}")

        self._direct_dependencies[engine_id] = required

        # Build reverse dependencies
        if engine_id not in self._reverse_deps:
            self._reverse_deps[engine_id] = set()

        for req in required:
            if req != engine_id:  # Don't add self-reference
                self._reverse_deps[req].add(engine_id)

    def get_dependencies(self, engine_id: str) -> Tuple[str, ...]:
        """Get direct dependencies of an engine."""
        return self._direct_dependencies.get(engine_id, ())

    def get_dependents(self, engine_id: str) -> Set[str]:
        """Get engines that depend on this one."""
        return self._reverse_deps.get(engine_id, set())

    def detect_cycle(self) -> Tuple[bool, List[str]]:
        """
        Detect if the dependency graph contains a cycle.

        Returns:
            Tuple of (has_cycle, cycle_path if found)
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for dep in self._direct_dependencies.get(node, ()):
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(dep)
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for node in self._direct_dependencies:
            if node not in visited:
                if dfs(node):
                    return True, path

        return False, []

    def validate_no_cycles(self) -> None:
        """
        Validate that no dependency cycles exist.

        Raises:
            ValueError: If a cycle is detected
        """
        has_cycle, _ = self.detect_cycle()
        if has_cycle:
            raise ValueError("Dependency graph contains a cycle")

    def get_topological_order(self) -> Tuple[str, ...]:
        """
        Get a topologically sorted order of engine IDs.

        This provides a valid processing order where all dependencies come
        before dependents.

        Returns:
            Tuple of engine IDs in dependency order

        Raises:
            ValueError: If cycles exist
        """
        self.validate_no_cycles()

        # Kahn's algorithm for topological sort
        in_degree: Dict[str, int] = {node: 0 for node in self._direct_dependencies}

        # Count incoming edges (dependencies)
        for node in self._direct_dependencies:
            for dep in self._direct_dependencies[node]:
                if dep in in_degree:
                    pass  # dep has a dependency on something else

        # Actually count how many engines depend ON each engine
        for node in self._direct_dependencies:
            for dep in self._direct_dependencies[node]:
                if dep != node:
                    in_degree[dep] = in_degree.get(dep, 0) + 1

        # Find nodes with no incoming edges (roots - engines nothing depends on)
        queue: List[str] = [
            n for n in self._direct_dependencies if in_degree.get(n, 0) == 0
        ]

        result: List[str] = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            # Reduce in-degree of dependents
            for dependent in self._reverse_deps.get(node, set()):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(self._direct_dependencies):
            raise ValueError("Dependency graph contains a cycle")

        return tuple(reversed(result))

    def get_canonical_order(self) -> Tuple[str, ...]:
        """
        Get the canonical processing order.

        This uses the predefined dependency order when available, falling back
        to topological sort if custom dependencies are present.
        """
        # Use predefined order for known engines
        from .constants import DEPENDENCY_ORDER

        registered = set(self._direct_dependencies)
        canonical = tuple(eid for eid in DEPENDENCY_ORDER if eid in registered)

        # Add any unregistered engines at the end
        extra = tuple(eid for eid in self._direct_dependencies if eid not in canonical)

        return canonical + extra


def build_default_dependency_graph() -> DependencyGraph:
    """
    Build the default dependency graph with canonical dependencies.

    Returns:
        Pre-configured dependency graph
    """
    from .constants import (
        ENGINE_ID_EXPERIENTIAL_FIELD,
        ENGINE_ID_INTENTIONAL_CONTEXT,
        ENGINE_ID_TEMPORAL_CONTEXT,
        ENGINE_ID_PRESENCE,
        ENGINE_ID_AWARENESS,
        ENGINE_ID_PERSPECTIVE,
        ENGINE_ID_SITUATED_WORLD,
    )

    graph = DependencyGraph()

    # Canonical dependency chain
    graph.add_engine(ENGINE_ID_EXPERIENTIAL_FIELD, ())

    graph.add_engine(
        ENGINE_ID_INTENTIONAL_CONTEXT,
        (ENGINE_ID_EXPERIENTIAL_FIELD,),
    )

    graph.add_engine(
        ENGINE_ID_TEMPORAL_CONTEXT,
        (ENGINE_ID_INTENTIONAL_CONTEXT,),
    )

    graph.add_engine(
        ENGINE_ID_PRESENCE,
        (
            ENGINE_ID_TEMPORAL_CONTEXT,
            ENGINE_ID_EXPERIENTIAL_FIELD,
        ),
    )

    graph.add_engine(
        ENGINE_ID_AWARENESS,
        (ENGINE_ID_PRESENCE,),
    )

    # Perspective may reference Situated World
    graph.add_engine(
        ENGINE_ID_PERSPECTIVE,
        (ENGINE_ID_SITUATED_WORLD,),
    )

    graph.add_engine(
        ENGINE_ID_SITUATED_WORLD,
        (
            ENGINE_ID_INTENTIONAL_CONTEXT,
            ENGINE_ID_TEMPORAL_CONTEXT,
            ENGINE_ID_PRESENCE,
            ENGINE_ID_PERSPECTIVE,
        ),
    )

    # Integration layer
    graph.add_engine(
        "conscious_integration",
        (
            ENGINE_ID_EXPERIENTIAL_FIELD,
            ENGINE_ID_INTENTIONAL_CONTEXT,
            ENGINE_ID_TEMPORAL_CONTEXT,
            ENGINE_ID_PRESENCE,
            ENGINE_ID_AWARENESS,
            ENGINE_ID_PERSPECTIVE,
            ENGINE_ID_SITUATED_WORLD,
        ),
    )

    return graph