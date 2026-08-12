# Execution Types
# ===============

"""
Immutable, deterministic value types for execution components.

This module defines neutral types that can safely cross Core-Execution boundaries.
All types are immutable and use stable serialization formats.
"""

from dataclasses import dataclass, field
from typing import NewType, Tuple, Optional
from enum import Enum, auto
import uuid


# =============================================================================
# Identifier Types (Neutral - no semantics)
# =============================================================================

ExecutionId = NewType("ExecutionId", str)
ThreadId = NewType("ThreadId", str)
LoopId = NewType("LoopId", str)
CycleId = NewType("CycleId", str)
StageId = NewType("StageId", str)
CheckpointId = NewType("CheckpointId", str)
CorrelationId = NewType("CorrelationId", str)


@dataclass(frozen=True)
class ExecutionIdentifier:
    """Unique identifier for an execution unit."""
    
    value: ExecutionId
    
    @classmethod
    def generate(cls) -> "ExecutionIdentifier":
        """Generate a new unique execution identifier."""
        return cls(value=ExecutionId(str(uuid.uuid4())))
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# Lifecycle States (Neutral - no semantics)
# =============================================================================

class ExecutionState(Enum):
    """
    Execution state machine states.
    
    These describe the lifecycle phase, not behavioral meaning.
    Transitions are deterministic and controlled by Core.
    """
    
    # Initial states
    CREATED = "created"         # Unit created but not yet submitted
    QUEUED = "queued"           # In ready queue, awaiting scheduling
    
    # Running states
    RUNNING = "running"         # Currently executing
    
    # Terminal states (success/failure)
    COMPLETED = "completed"     # Execution succeeded
    FAILED = "failed"           # Execution failed with error
    
    # Cancellation states
    CANCELLING = "cancelling"   # Cancellation requested, cleaning up
    CANCELLED = "cancelled"     # Cancellation completed


class LifecycleState(Enum):
    """
    Thread lifecycle state (distinct from execution state).
    
    Answers: "What is this runtime entity's lifecycle phase?"
    """
    
    NEW = "new"                 # Just created
    READY = "ready"             # Ready for first cycle
    ACTIVE = "active"           # Running cycles
    PAUSED = "paused"           # Temporarily suspended
    TERMINATING = "terminating" # Requested termination, cleaning up
    TERMINATED = "terminated"   # Terminated completely
    FAILED = "failed"           # Failed during any phase


class CycleResult(Enum):
    """
    Result of a cycle execution.
    
    This determines what the Loop should do next:
        - COMPLETED: Cycle finished successfully, thread may terminate
        - CONTINUE: Cycle completed but should run again (same or different)
        - WAIT: Cycle cannot proceed yet, wait for external event
        - DELEGATE: Defer to another cycle/thread
        - FAIL: Cycle failed and cannot recover
    """
    
    COMPLETED = "completed"
    CONTINUE = "continue"
    WAIT = "wait"
    DELEGATE = "delegate"
    FAIL = "fail"


# =============================================================================
# Priority Levels (Neutral - no semantics)
# =============================================================================

class Priority(Enum):
    """
    Execution priority levels.
    
    Lower numeric value = higher priority (runs first).
    These are metadata values; cognition decides which units get which priority.
    Core obeys but doesn't invent priorities.
    """
    
    CRITICAL = 0   # Must run immediately
    HIGH = 1       # High importance, short delay acceptable
    NORMAL = 2     # Standard priority
    LOW = 3        # Can be delayed if needed


# =============================================================================
# Resource Budget (Neutral - no semantics)
# =============================================================================

@dataclass(frozen=True)
class ResourceBudget:
    """
    Resource budget allocation for execution.
    
    Specifies constraints on how resources may be consumed.
    """
    
    # Time-based
    timeout_seconds: Optional[float] = None
    
    # Execution count limits
    max_cycles: Optional[int] = None
    max_iterations: Optional[int] = None
    
    # Resource consumption
    context_tokens: Optional[int] = None
    max_retries: Optional[int] = None


# =============================================================================
# Cancellation (Neutral - no semantics)
# =============================================================================

class CancellationReason(Enum):
    """Reason for cancellation request."""
    
    TIMEOUT = "timeout"
    USER_REQUEST = "user_request"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    FAILURE = "failure"
    PARENT_CANCELLED = "parent_cancelled"
    DEADLINE_EXCEEDED = "deadline_exceeded"


@dataclass(frozen=True)
class CancellationView:
    """
    Read-only cancellation state view.
    
    Execution units can check for cancellation requests
    and respond appropriately.
    """
    
    is_requested: bool
    reason: Optional[CancellationReason] = None


# =============================================================================
# Timestamp (Neutral - no semantics)
# =============================================================================

@dataclass(frozen=True)
class Timestamp:
    """Monotonic timestamp for lifecycle events."""
    
    value: float  # monotonic time in seconds
    
    @classmethod
    def now(cls) -> "Timestamp":
        """Create a timestamp from current monotonic time."""
        import time
        return cls(value=time.monotonic())
    
    def elapsed_since(self, other: "Timestamp") -> float:
        """Return elapsed time since another timestamp."""
        return self.value - other.value


# =============================================================================
# Export all types
# =============================================================================

__all__ = [
    # Identifiers
    "ExecutionId",
    "ThreadId", 
    "LoopId",
    "CycleId",
    "StageId",
    "CheckpointId",
    "CorrelationId",
    
    # Identifier wrappers
    "ExecutionIdentifier",
    
    # Lifecycle states
    "ExecutionState",
    "LifecycleState",
    "CycleResult",
    
    # Priority and resources
    "Priority",
    "ResourceBudget",
    
    # Cancellation
    "CancellationReason",
    "CancellationView",
    
    # Time
    "Timestamp",
]