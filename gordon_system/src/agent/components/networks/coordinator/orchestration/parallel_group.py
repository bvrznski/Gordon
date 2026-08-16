# Gordon Cognitive Architecture - Phase 4.11.7
# ===========================================
"""
Parallel Execution Group Model
==============================

Groups of stages that can execute in parallel.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ParallelExecutionGroup:
    """
    Immutable parallel execution group model.
    
    PARALLEL-LAW-001: Only semantically independent stages may execute in parallel
    PARALLEL-LAW-002: Parallel execution shall preserve semantic equivalence with serial execution
    PARALLEL-LAW-003: Parallel groups shall remain explicit
    
    Parallel groups execute semantically independently.
    """
    
    identity: str = ""
    """Unique identity for this group."""
    
    stages: tuple[str, ...] = ()
    """Stage identities in this parallel group."""
    
    synchronization_barrier: str = ""
    """Barrier identity that joins this group."""
    
    completion_policy: str = ""
    """Policy for completing this group."""
    
    provenance_ref: str = ""
    """Reference to provenance record."""
    
    @classmethod
    def create(
        cls,
        stages: tuple[str, ...],
        synchronization_barrier: str = "",
        completion_policy: str = "",
    ) -> ParallelExecutionGroup:
        """
        Create a new parallel execution group.
        
        Args:
            stages: Stage identities in this group
            synchronization_barrier: Barrier that joins the group
            completion_policy: Policy for completing the group
            
        Returns:
            A new ParallelExecutionGroup instance
        """
        return cls(
            identity=f"parallel-group:{len(stages)}stages",
            stages=tuple(stages),
            synchronization_barrier=synchronization_barrier,
            completion_policy=completion_policy or "all_stages_complete",
            provenance_ref="",
        )
    
    def __str__(self) -> str:
        return f"ParallelExecutionGroup({self.identity}, stages={len(self.stages)})"