# Reasoner Set - Phase 7.13
# ==========================

"""
Canonical Reasoner Set definition.

A reasoner set defines available reasoning systems, their capabilities,
and resource constraints for meta-reasoning orchestration.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ReasonerCapability(Enum):
    """Capabilities of reasoning systems."""
    
    # Basic inference
    DEDUCTIVE = "deductive"           # From general to specific
    INDUCTIVE = "inductive"           # From specific to general
    ABDUCTIVE = "abductive"           # Best explanation inference
    ANALOGICAL = "analogical"         # Similarity-based reasoning
    
    # Advanced reasoning
    CAUSAL = "causal"                 # Cause-effect analysis
    TEMPORAL = "temporal"             # Time-based reasoning
    COUNTERFACTUAL = "counterfactual"  # What-if scenarios
    PROBABILISTIC = "probabilistic"   # Uncertainty handling
    
    # Semantic reasoning
    SEMANTIC = "semantic"             # Conceptual meaning
    RELATIONAL = "relational"         # Structural organization
    
    # Specialized
    SPATIAL = "spatial"               # Spatial reasoning
    META_REASONING = "meta_reasoning"  # Reasoning about reasoning


class DependencyKind(Enum):
    """Types of dependencies between reasoners."""
    
    DATA_DEPENDENCY = "data_dependency"      # Output of one is input to another
    CONTROL_DEPENDENCY = "control_dependency"  # Conditional execution
    RESOURCE_DEPENDENCY = "resource_dependency"  # Shared resource usage
    COMPOSITIONAL = "compositional"          # Composition chain


@dataclass(frozen=True)
class ReasonerDependency:
    """
    Represents a dependency between reasoning systems.
    
    Dependencies define the execution order and data flow between reasoners.
    """
    
    from_reasoner: str                      # Source reasoner ID
    to_reasoner: str                        # Target reasoner ID
    dependency_kind: DependencyKind         # Type of dependency
    constraint: Optional[str] = None        # Optional constraint description


@dataclass(frozen=True)
class ReasonerSet:
    """
    Set of reasoning systems available for orchestration.
    
    A reasoner set defines:
        - Available reasoning systems and their capabilities
        - Dependencies between reasoning systems
        - Resource constraints for orchestration
        - Execution priorities
    
    Reasoner Sets remain immutable during orchestration execution.
    """
    
    # Identity
    reasoner_set_id: str                    # Unique reasoner set identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Reasoners
    participating_reasoners: List[str]      # IDs of participating reasoning systems
    
    # Capabilities
    available_capabilities: List[ReasonerCapability]  # Available reasoning capabilities
    
    # Dependencies
    dependency_graph: List[ReasonerDependency] = field(default_factory=list)  # Execution dependencies
    
    # Resource constraints
    max_concurrent_reasoners: int = 1       # Maximum parallel reasoners
    total_compute_budget_seconds: float = 60.0  # Total execution budget
    memory_limit_mb: int = 512              # Memory limit per orchestration
    
    # Priorities
    default_priority: int = 0               # Default execution priority
    reasoner_priorities: Dict[str, int] = field(default_factory=dict)  # Per-reasoner priorities
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_valid(self) -> bool:
        """Validate reasoner set consistency."""
        # Check no duplicate reasoners
        if len(self.participating_reasoners) != len(set(self.participating_reasoners)):
            return False
        
        # Check dependencies reference valid reasoners
        for dep in self.dependency_graph:
            if dep.from_reasoner not in self.participating_reasoners:
                return False
            if dep.to_reasoner not in self.participating_reasoners:
                return False
        
        # Check no cycles (simplified check)
        if self._has_cycle():
            return False
        
        return True
    
    def _has_cycle(self) -> bool:
        """Check for dependency cycles using DFS."""
        graph: Dict[str, List[str]] = {r: [] for r in self.participating_reasoners}
        
        for dep in self.dependency_graph:
            if dep.from_reasoner in graph:
                graph[dep.from_reasoner].append(dep.to_reasoner)
        
        visited = set()
        rec_stack = set()
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.participating_reasoners:
            if node not in visited:
                if dfs(node):
                    return True
        
        return False
    
    def get_dependents(self, reasoner_id: str) -> List[str]:
        """Get reasoners that depend on the given reasoner."""
        result = []
        for dep in self.dependency_graph:
            if dep.from_reasoner == reasoner_id:
                result.append(dep.to_reasoner)
        return result
    
    def get_dependencies(self, reasoner_id: str) -> List[str]:
        """Get reasoners that the given reasoner depends on."""
        result = []
        for dep in self.dependency_graph:
            if dep.to_reasoner == reasoner_id:
                result.append(dep.from_reasoner)
        return result
    
    def get_execution_order(self) -> List[str]:
        """Get topologically sorted execution order."""
        # Build adjacency list
        graph: Dict[str, List[str]] = {r: [] for r in self.participating_reasoners}
        in_degree: Dict[str, int] = {r: 0 for r in self.participating_reasoners}
        
        for dep in self.dependency_graph:
            if dep.from_reasoner in graph and dep.to_reasoner in graph:
                graph[dep.from_reasoner].append(dep.to_reasoner)
                in_degree[dep.to_reasoner] += 1
        
        # Kahn's algorithm
        queue = [r for r in self.participating_reasoners if in_degree[r] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        participating_reasoners: List[str],
        available_capabilities: Optional[List[ReasonerCapability]] = None,
        max_concurrent_reasoners: int = 1,
        total_compute_budget_seconds: float = 60.0,
        memory_limit_mb: int = 512,
    ) -> ReasonerSet:
        """Create a new reasoner set."""
        if available_capabilities is None:
            available_capabilities = [ReasonerCapability.DEDUCTIVE]
        
        return cls(
            reasoner_set_id=f"reasoner_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            participating_reasoners=participating_reasoners,
            available_capabilities=available_capabilities,
            max_concurrent_reasoners=max_concurrent_reasoners,
            total_compute_budget_seconds=total_compute_budget_seconds,
            memory_limit_mb=memory_limit_mb,
        )
    
    def with_dependencies(self, dependencies: List[ReasonerDependency]) -> ReasonerSet:
        """Return a copy with updated dependencies."""
        return dataclass_replace(
            self,
            dependency_graph=dependencies,
        )
    
    def with_priority(self, reasoner_id: str, priority: int) -> ReasonerSet:
        """Return a copy with updated priority for a reasoner."""
        new_priorities = dict(self.reasoner_priorities)
        new_priorities[reasoner_id] = priority
        return dataclass_replace(
            self,
            reasoner_priorities=new_priorities,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ReasonerSet",
    "ReasonerCapability",
    "DependencyKind",
    "ReasonerDependency",
]