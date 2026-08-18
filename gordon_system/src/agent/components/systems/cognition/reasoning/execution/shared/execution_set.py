# Execution Reasoning Execution Set - Phase 7.21
# ===============================================

"""
Canonical Execution Set for Phase 7.21.

Execution Sets define the execution commands, orchestration scope,
and constraints that govern how behavior is coordinated.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class CommandKind(Enum):
    """Kinds of execution commands."""
    
    TASK_ACTIVATION = "task_activation"           # Activate a task for execution
    PARALLEL_EXECUTION = "parallel_execution"     # Execute commands in parallel
    RESOURCE_ACQUISITION = "resource_acquisition"  # Acquire resources
    CHECKPOINT_CREATE = "checkpoint_create"        # Create a checkpoint
    ROLLBACK_REQUEST = "rollback_request"          # Request rollback
    TERMINATION_REQUEST = "termination_request"    # Terminate execution


class CommandState(Enum):
    """Execution command lifecycle states."""
    
    PENDING = "pending"
    AUTHORIZED = "authorized"
    INITIALIZING = "initializing"
    EXECUTING = "executing"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass(frozen=True)
class ExecutionCommand:
    """
    Execution Command describes authorized operational behavior.
    
    Commands include:
        - Task activation
        - Parallel execution triggers
        - Resource acquisition requests
        - Checkpoint creation
        - Rollback requests
        - Termination requests
    
    Commands remain explicit and independently inspectable.
    """
    
    # Identity
    command_identity: str                       # Unique command identifier
    
    # Originating task
    originating_task: str                       # Which task initiated this?
    
    # Command kind
    command_kind: CommandKind                   # What kind of command?
    
    # Execution constraints
    execution_constraints: Tuple[str, ...] = ()  # Explicit constraints
    
    # State
    command_state: CommandState = CommandState.PENDING
    
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
        """Check if command completed."""
        return self.command_state in (CommandState.COMPLETED, CommandState.ROLLED_BACK)
    
    @property
    def is_failed(self) -> bool:
        """Check if command failed."""
        return self.command_state == CommandState.FAILED
    
    @classmethod
    def create(
        cls,
        originating_task: str,
        command_kind: CommandKind,
        execution_constraints: Tuple[str, ...] = (),
    ) -> ExecutionCommand:
        """Create a new execution command."""
        return cls(
            command_identity=f"cmd:{uuid.uuid4().hex[:16]}",
            originating_task=originating_task,
            command_kind=command_kind,
            execution_constraints=execution_constraints,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: CommandState) -> ExecutionCommand:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            command_state=new_state,
            completed_at_utc=time.time() if new_state == CommandState.COMPLETED else None,
        )


@dataclass(frozen=True)
class ExecutionSet:
    """
    Execution Set defines the execution commands that form an orchestration.
    
    Execution Sets define:
        - Execution commands
        - Execution graphs
        - Resource reservations
        - Authorization policies
        - Rollback boundaries
    
    Execution Sets remain immutable during orchestration.
    """
    
    # Identity
    execution_set_identity: str                 # Unique set identifier
    
    # Participating commands
    participating_commands: Tuple[ExecutionCommand, ...]
    
    # Orchestration scope
    orchestration_scope: str                    # What is being orchestrated?
    
    # Execution constraints
    execution_constraints: Tuple[str, ...] = ()
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def command_count(self) -> int:
        """Number of participating commands."""
        return len(self.participating_commands)
    
    @classmethod
    def create(
        cls,
        orchestration_scope: str,
        participating_commands: Tuple[ExecutionCommand, ...] = (),
        execution_constraints: Tuple[str, ...] = (),
    ) -> ExecutionSet:
        """Create a new execution set."""
        return cls(
            execution_set_identity=f"exec_set:{uuid.uuid4().hex[:16]}",
            orchestration_scope=orchestration_scope,
            participating_commands=participating_commands,
            execution_constraints=execution_constraints,
        )
    
    def add_command(self, command: ExecutionCommand) -> ExecutionSet:
        """Return a new set with the command added."""
        return dataclass_replace(
            self,
            participating_commands=self.participating_commands + (command,),
        )


@dataclass(frozen=True)
class CommandConstruction:
    """
    Command construction metadata for execution orchestration.
    
    Tracks how commands were constructed and authorized.
    """
    
    # Identity
    construction_identity: str
    
    # Source plan
    originating_plan_id: str                    # Which plan generated this?
    
    # Construction strategy
    construction_strategy: str                  # How was this built?
    
    # Dependencies
    dependency_ids: Tuple[str, ...] = ()        # Commands this depends on
    
    # Authorization
    authorization_status: str = "pending"       # Has this been authorized?
    
    @classmethod
    def create(
        cls,
        originating_plan_id: str,
        construction_strategy: str,
        dependency_ids: Tuple[str, ...] = (),
    ) -> CommandConstruction:
        """Create a new command construction record."""
        return cls(
            construction_identity=f"construction:{uuid.uuid4().hex[:16]}",
            originating_plan_id=originating_plan_id,
            construction_strategy=construction_strategy,
            dependency_ids=dependency_ids,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ExecutionCommand",
    "CommandKind",
    "CommandState",
    "ExecutionSet",
    "CommandConstruction",
]