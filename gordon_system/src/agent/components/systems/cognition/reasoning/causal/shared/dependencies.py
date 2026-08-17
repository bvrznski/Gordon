# Dependency Analysis - Phase 7.5
# ===============================

"""
Canonical Dependency Analysis.

Dependency analysis discovers required causes, optional causes,
enabling conditions, blocking conditions, and indirect causes.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Optional, Any
from enum import Enum, auto


class DependencyKind(Enum):
    """Kinds of dependencies between events."""
    
    REQUIRED_CAUSE = "required_cause"         # Must be present for effect
    OPTIONAL_CAUSE = "optional_cause"         # Can cause effect but not required
    ENABLING_CONDITION = "enabling_condition"  # Makes effect possible
    BLOCKING_CONDITION = "blocking_condition"  # Prevents effect if active
    INDIRECT_CAUSE = "indirect_cause"         # Causes effect through intermediates


@dataclass(frozen=True)
class Dependency:
    """
    A dependency between two events in the causal model.
    
    Describes how one event depends on another.
    """
    
    # Identity
    dependency_id: str                  # Unique dependency identifier
    
    # Dependencies
    cause_event: str                    # The cause
    effect_event: str                   # The effect
    kind: DependencyKind                # What type of dependency?
    
    # Strength (0-1)
    strength: float = 1.0               # How strongly does cause affect effect?
    
    # Conditions
    conditions: Tuple[str, ...] = ()    # Additional conditions
    
    @property
    def is_necessary(self) -> bool:
        """Check if this dependency represents a necessary condition."""
        return self.kind in (DependencyKind.REQUIRED_CAUSE, DependencyKind.ENABLING_CONDITION)
    
    @property
    def is_sufficient(self) -> bool:
        """Check if this dependency represents a sufficient condition."""
        return self.kind == DependencyKind.REQUIRED_CAUSE


@dataclass(frozen=True)
class DependencyGraph:
    """
    A graph representing all dependencies in the causal model.
    
    Nodes are events; edges represent dependencies.
    """
    
    # Identity
    graph_id: str                       # Unique graph identifier
    
    # Dependencies
    dependencies: Tuple[Dependency, ...]  # All dependencies
    
    # Source nodes (events without incoming dependencies)
    source_nodes: Tuple[str, ...]       # Initial causes
    
    # Sink nodes (events without outgoing dependencies)
    sink_nodes: Tuple[str, ...]         # Final effects
    
    @property
    def dependency_count(self) -> int:
        """Number of dependencies in the graph."""
        return len(self.dependencies)
    
    def get_dependencies_for_event(self, event: str) -> Tuple[Dependency, ...]:
        """Get all dependencies involving a specific event."""
        return tuple(
            d for d in self.dependencies
            if d.cause_event == event or d.effect_event == event
        )
    
    def get_causes_of(self, effect: str) -> Tuple[Dependency, ...]:
        """Get all dependencies that cause the given effect."""
        return tuple(d for d in self.dependencies if d.effect_event == effect)
    
    def get_effects_of(self, cause: str) -> Tuple[Dependency, ...]:
        """Get all dependencies caused by the given event."""
        return tuple(d for d in self.dependencies if d.cause_event == cause)


@dataclass(frozen=True)
class DependencyAnalysis:
    """
    Complete dependency analysis result.
    
    Identifies all causal relationships and their types.
    """
    
    # Identity
    analysis_id: str                    # Unique analysis identifier
    
    # Dependencies found
    dependencies: Tuple[Dependency, ...]  # All discovered dependencies
    
    # Dependency graph
    dependency_graph: DependencyGraph   # Graph representation
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()   # Analysis diagnostics
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @property
    def dependency_count(self) -> int:
        """Number of dependencies analyzed."""
        return len(self.dependencies)


def make_dependency(
    cause: str,
    effect: str,
    kind: DependencyKind,
    strength: float = 1.0,
    conditions: Tuple[str, ...] = (),
) -> Dependency:
    """Create a new dependency."""
    return Dependency(
        dependency_id=f"dep:{uuid.uuid4().hex[:8]}",
        cause_event=cause,
        effect_event=effect,
        kind=kind,
        strength=strength,
        conditions=conditions,
    )


def make_dependency_graph(
    name: str,
    dependencies: List[Dependency],
) -> DependencyGraph:
    """Create a new dependency graph."""
    deps_tuple = tuple(dependencies)
    
    # Find source and sink nodes
    all_causes = {d.cause_event for d in deps_tuple}
    all_effects = {d.effect_event for d in deps_tuple}
    
    source_nodes = tuple(all_causes - all_effects)
    sink_nodes = tuple(all_effects - all_causes)
    
    return DependencyGraph(
        graph_id=f"dep_graph:{uuid.uuid4().hex[:16]}",
        dependencies=deps_tuple,
        source_nodes=source_nodes,
        sink_nodes=sink_nodes,
    )


__all__ = [
    "DependencyKind",
    "Dependency",
    "DependencyGraph",
    "DependencyAnalysis",
]