# Reasoning Orchestration - Phase 7.13
# =====================================

"""
Canonical Reasoning Orchestration definition.

Orchestration manages the execution of reasoning systems, including
parallel execution, dependencies, and resource allocation.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class OrchestrationPolicy(Enum):
    """Orchestration policy types."""
    
    SEQUENTIAL = "sequential"               # Execute reasoners in order
    PARALLEL = "parallel"                   # Execute reasoners simultaneously
    HIERARCHICAL = "hierarchical"           # Top-down execution hierarchy
    ADAPTIVE = "adaptive"                   # Dynamic strategy adjustment
    CONSENSUS = "consensus"                 # Require consensus among reasoners


@dataclass(frozen=True)
class ExecutionStep:
    """
    A single step in the orchestration plan.
    
    Each step represents one or more reasoners to be executed.
    """
    
    # Identity
    step_id: str                            # Unique step identifier
    
    # Reasoners in this step
    reasoner_ids: List[str]                 # IDs of reasoners to execute
    
    # Execution mode
    is_parallel: bool = False               # Run in parallel?
    
    # Dependencies
    depends_on_steps: List[str] = field(default_factory=list)  # Required predecessors
    
    # Timing constraints
    max_duration_seconds: Optional[float] = None  # Time limit for step


@dataclass(frozen=True)
class SynchronizationPoint:
    """
    A point where orchestration waits for synchronization.
    
    Used to coordinate parallel reasoning paths.
    """
    
    # Identity
    sync_id: str                            # Unique sync identifier
    
    # Waiting for these steps to complete
    wait_for_steps: List[str]               # Step IDs to wait for
    
    # Merge strategy
    merge_strategy: OrchestrationPolicy = OrchestrationPolicy.SEQUENTIAL


@dataclass(frozen=True)
class ExecutionGraph:
    """
    Graph representation of orchestration execution plan.
    
    Defines the complete dependency graph for reasoning execution.
    """
    
    # Identity
    graph_id: str                           # Unique graph identifier
    
    # Steps
    steps: List[ExecutionStep]              # All execution steps
    
    # Synchronization points
    sync_points: List[SynchronizationPoint] = field(default_factory=list)
    
    # Entry and exit points
    entry_step_ids: List[str]               # Initial steps to start with
    exit_step_ids: List[str]                # Final steps for completion
    
    @property
    def is_valid(self) -> bool:
        """Validate execution graph."""
        # Check all referenced steps exist
        step_ids = {step.step_id for step in self.steps}
        
        for step in self.steps:
            for dep_id in step.depends_on_steps:
                if dep_id not in step_ids:
                    return False
        
        for sync_point in self.sync_points:
            for wait_id in sync_point.wait_for_steps:
                if wait_id not in step_ids:
                    return False
        
        # Check entry steps exist
        for entry_id in self.entry_step_ids:
            if entry_id not in step_ids:
                return False
        
        # Check exit steps exist
        for exit_id in self.exit_step_ids:
            if exit_id not in step_ids:
                return False
        
        return True


@dataclass(frozen=True)
class ReasoningOrchestration:
    """
    Orchestration plan for reasoning execution.
    
    An orchestration contains:
        - Identity and provenance
        - Execution graph definition
        - Synchronization points
        - Policy configuration
    
    Orchestration remains explicit and inspectable at all times.
    """
    
    # Identity
    orchestration_id: str                   # Unique orchestration identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Execution plan
    execution_graph: ExecutionGraph         # The execution graph
    
    # Policy configuration
    policy: OrchestrationPolicy = OrchestrationPolicy.SEQUENTIAL
    
    # Resource limits per step
    resource_limits_per_step: Dict[str, float] = field(default_factory=dict)
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate orchestration duration."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0
    
    @property
    def step_count(self) -> int:
        """Count total steps in orchestration."""
        return len(self.execution_graph.steps)
    
    def get_ready_steps(self, completed_step_ids: List[str]) -> List[ExecutionStep]:
        """Get steps that are ready to execute given completed steps."""
        ready = []
        
        for step in self.execution_graph.steps:
            if step.step_id in completed_step_ids:
                continue
            
            # Check dependencies
            deps_met = all(
                dep_id in completed_step_ids 
                for dep_id in step.depends_on_steps
            )
            
            if deps_met:
                ready.append(step)
        
        return ready
    
    def get_next_sync_points(self, completed_step_ids: List[str]) -> List[SynchronizationPoint]:
        """Get synchronization points triggered by completed steps."""
        triggered = []
        
        for sync_point in self.execution_graph.sync_points:
            if all(
                wait_id in completed_step_ids 
                for wait_id in sync_point.wait_for_steps
            ):
                triggered.append(sync_point)
        
        return triggered
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        steps: List[ExecutionStep],
        entry_step_ids: Optional[List[str]] = None,
        exit_step_ids: Optional[List[str]] = None,
        policy: OrchestrationPolicy = OrchestrationPolicy.SEQUENTIAL,
    ) -> ReasoningOrchestration:
        """Create a new orchestration."""
        if entry_step_ids is None and steps:
            entry_step_ids = [steps[0].step_id]
        
        if exit_step_ids is None and steps:
            exit_step_ids = [steps[-1].step_id]
        
        graph = ExecutionGraph(
            graph_id=f"exec_graph:{uuid.uuid4().hex[:16]}",
            steps=steps,
            entry_step_ids=entry_step_ids or [],
            exit_step_ids=exit_step_ids or [],
        )
        
        return cls(
            orchestration_id=f"orchestration:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            execution_graph=graph,
            policy=policy,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ReasoningOrchestration",
    "ExecutionGraph",
    "ExecutionStep",
    "SynchronizationPoint",
    "OrchestrationPolicy",
]