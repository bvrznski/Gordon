# Gordon Cognitive Architecture - Phase 4.11.7
# ===========================================
"""
Execution Dependency Graph Model
================================

The dependency graph for orchestration execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class DependencyEdge:
    """
    Immutable dependency edge model.
    
    DEPENDENCY-LAW-001: Execution dependencies remain explicit
    DEPENDENCY-LAW-002: Dependency graphs remain acyclic unless explicitly declared
    DEPENDENCY-LAW-003: Dependency kinds remain explicit
    
    Suggested dependency kinds per spec:
        DATA - data flow dependency
        CONTROL - control flow dependency
        RESOURCE - resource access dependency
        SYNCHRONIZATION - synchronization barrier requirement
        VALIDATION - validation result dependency
    """
    
    source_stage: str = ""
    """Stage identity that produces the dependency."""
    
    destination_stage: str = ""
    """Stage identity that requires the dependency."""
    
    dependency_kind: str = ""  # DependencyKind.*
    """Type of dependency."""
    
    mandatory: bool = True
    """Whether this dependency is mandatory."""
    
    provenance_ref: str = ""
    """Reference to provenance record."""
    
    def __str__(self) -> str:
        return f"DependencyEdge({self.source_stage} -> {self.destination_stage}, kind={self.dependency_kind})"


@dataclass(frozen=True, slots=True)
class ExecutionDependencyGraph:
    """
    Immutable execution dependency graph model.
    
    DEPENDENCY-LAW-001: Dependencies remain explicit
    DEPENDENCY-LAW-002: Dependency graphs remain acyclic unless explicitly declared
    DEPENDENCY-LAW-003: Dependency kinds remain explicit
    
    The graph is a DAG by default. Cycles require explicit declaration.
    """
    
    identity: str = ""
    """Unique identity for this dependency graph."""
    
    stages: tuple[str, ...] = ()
    """Stage identities in the graph."""
    
    edges: tuple[DependencyEdge, ...] = ()
    """Dependency edges between stages."""
    
    parallel_groups: tuple[str, ...] = ()
    """Group identifiers for parallel execution."""
    
    is_cyclic: bool = False
    """Whether this graph contains cycles (requires explicit approval)."""
    
    provenance_ref: str = ""
    """Reference to provenance record."""
    
    @classmethod
    def create(
        cls,
        stages: tuple[str, ...],
        edges: tuple[DependencyEdge, ...] = (),
        parallel_groups: tuple[str, ...] = (),
        is_cyclic: bool = False,
    ) -> ExecutionDependencyGraph:
        """
        Create a new execution dependency graph.
        
        Args:
            stages: Stage identities in the graph
            edges: Dependency edges between stages
            parallel_groups: Group identifiers for parallel execution
            is_cyclic: Whether this graph contains cycles
            
        Returns:
            A new ExecutionDependencyGraph instance
        """
        return cls(
            identity=f"dep-graph:{len(stages)}stages:{len(edges)}edges",
            stages=tuple(stages),
            edges=tuple(edges),
            parallel_groups=tuple(parallel_groups),
            is_cyclic=is_cyclic,
            provenance_ref="",
        )
    
    def get_successors(self, stage_id: str) -> tuple[str, ...]:
        """Get stages that depend on the given stage."""
        successors = []
        for edge in self.edges:
            if edge.source_stage == stage_id:
                successors.append(edge.destination_stage)
        return tuple(successors)
    
    def get_predecessors(self, stage_id: str) -> tuple[str, ...]:
        """Get stages that the given stage depends on."""
        predecessors = []
        for edge in self.edges:
            if edge.destination_stage == stage_id:
                predecessors.append(edge.source_stage)
        return tuple(predecessors)
    
    def __str__(self) -> str:
        return f"ExecutionDependencyGraph({len(self.stages)} stages, {len(self.edges)} edges)"