# Execution Reasoning Orchestration - Phase 7.21
# ===============================================

"""
Canonical Execution Orchestration for Phase 7.21.

Execution orchestration is the canonical pipeline through which execution
plans are transformed into coordinated behavioral execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class OrchestrationStrategy(Enum):
    """Strategies for execution orchestration."""
    
    SEQUENTIAL = "sequential"              # Execute commands in strict sequence
    PARALLEL = "parallel"                  # Execute commands in parallel
    HYBRID = "hybrid"                      # Combined sequential-parallel
    DISTRIBUTED = "distributed"            # Distributed across agents
    ADAPTIVE = "adaptive"                  # Strategy adapts based on feedback


class ExecutionGraphState(Enum):
    """Execution graph lifecycle states."""
    
    CONSTRUCTING = "constructing"
    AUTHORIZING = "authorizing"
    SYNCHRONIZING = "synchronizing"
    EXECUTING = "executing"
    SUSPENDED = "suspended"
    ADAPTING = "adapting"
    ROLLING_BACK = "rolling_back"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class ExecutionOrchestration:
    """
    Execution Orchestration coordinates execution commands through the pipeline.
    
    Canonical pipeline flow:
        Plan Intake → Authorization → Command Sequencing → 
        Resource Synchronization → Execution Coordination → 
        Adaptation → Validation → Publication
    
    Every stage remains independently observable.
    """
    
    # Identity
    orchestration_identity: str                 # Unique orchestration identifier
    
    # Orchestration strategy
    orchestration_strategy: OrchestrationStrategy
    
    # Execution graph (sequence of command groups)
    execution_graph: Tuple[ExecutionCommandGroup, ...]
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()           # Diagnostic notes
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration if completed."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0
    
    @property
    def is_completed(self) -> bool:
        """Check if orchestration completed."""
        return self.graph_state == ExecutionGraphState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if orchestration failed."""
        return self.graph_state == ExecutionGraphState.FAILED
    
    @classmethod
    def create(
        cls,
        orchestration_strategy: OrchestrationStrategy = OrchestrationStrategy.SEQUENTIAL,
        execution_graph: Tuple[ExecutionCommandGroup, ...] = (),
        diagnostics: Tuple[str, ...] = (),
    ) -> ExecutionOrchestration:
        """Create a new execution orchestration."""
        return cls(
            orchestration_identity=f"orchestration:{uuid.uuid4().hex[:16]}",
            orchestration_strategy=orchestration_strategy,
            execution_graph=execution_graph,
            diagnostics=diagnostics,
            started_at_utc=time.time(),
        )
    
    def with_state(self, new_state: ExecutionGraphState) -> ExecutionOrchestration:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            graph_state=new_state,
            completed_at_utc=time.time() if new_state == ExecutionGraphState.COMPLETED else None,
        )
    
    def add_command_group(self, group: ExecutionCommandGroup) -> ExecutionOrchestration:
        """Return a copy with the command group added."""
        return dataclass_replace(
            self,
            execution_graph=self.execution_graph + (group,),
        )


@dataclass(frozen=True)
class ExecutionCommandGroup:
    """
    A group of commands that can be executed together.
    
    Groups enable parallel execution and synchronization points.
    """
    
    # Identity
    group_identity: str
    
    # Commands in this group
    participating_commands: Tuple[ExecutionCommand, ...]
    
    # Group type
    group_type: str = "default"                 # e.g., "parallel", "barrier"
    
    # Synchronization requirements
    requires_synchronization: bool = False
    
    @classmethod
    def create(
        cls,
        participating_commands: Tuple[ExecutionCommand, ...],
        group_type: str = "default",
        requires_synchronization: bool = False,
    ) -> ExecutionCommandGroup:
        """Create a new command group."""
        return cls(
            group_identity=f"group:{uuid.uuid4().hex[:16]}",
            participating_commands=participating_commands,
            group_type=group_type,
            requires_synchronization=requires_synchronization,
        )


@dataclass(frozen=True)
class OrchestrationTrace:
    """
    Trace of orchestration events for inspection.
    
    Enables replay and verification of orchestration decisions.
    """
    
    # Identity
    trace_identity: str
    
    # Steps in the orchestration
    orchestration_steps: Tuple[OrchestrationStep, ...]
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()
    
    @classmethod
    def create(
        cls,
        orchestration_steps: Tuple[OrchestrationStep, ...],
        diagnostics: Tuple[str, ...] = (),
    ) -> OrchestrationTrace:
        """Create a new orchestration trace."""
        return cls(
            trace_identity=f"trace:{uuid.uuid4().hex[:16]}",
            orchestration_steps=orchestration_steps,
            diagnostics=diagnostics,
        )


@dataclass(frozen=True)
class OrchestrationStep:
    """
    A single step in the orchestration pipeline.
    
    Each step records:
        - The stage name
        - Timestamps
        - Any outputs or changes
    """
    
    # Identity
    step_identity: str
    
    # Stage name
    stage_name: str                             # e.g., "authorization", "sequencing"
    
    # Timestamps
    started_at_utc: float
    completed_at_utc: Optional[float] = None
    
    # Input/output references
    input_references: Tuple[str, ...] = ()
    output_references: Tuple[str, ...] = ()
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration."""
        if self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        return time.time() - self.started_at_utc
    
    @classmethod
    def create(
        cls,
        stage_name: str,
        started_at_utc: Optional[float] = None,
        input_references: Tuple[str, ...] = (),
        output_references: Tuple[str, ...] = (),
    ) -> OrchestrationStep:
        """Create a new orchestration step."""
        return cls(
            step_identity=f"step:{uuid.uuid4().hex[:16]}",
            stage_name=stage_name,
            started_at_utc=started_at_utc or time.time(),
            input_references=input_references,
            output_references=output_references,
            completed_at_utc=time.time() if stage_name == "publication" else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ExecutionOrchestration",
    "OrchestrationStrategy",
    "ExecutionGraphState",
    "ExecutionCommandGroup",
    "OrchestrationTrace",
    "OrchestrationStep",
]