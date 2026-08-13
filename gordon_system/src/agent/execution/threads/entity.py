# Canonical ExecutionThread Entity
# ================================
#
# PHASE 3.10.7 UPDATE - Immutable canonical ExecutionThread with controlled state transitions.
#
# An ExecutionThread is not an operating-system thread, coroutine, or runtime worker.
# An ExecutionThread IS:
#     - Semantic continuity: identity and state persistence across cycles
#     - Ownership of objectives, context, and artifacts  
#     - Parent-child relationship management
#     - Revision-controlled semantic deltas through delta application only
#
# IMPORTANT: ExecutionThread is now IMMUTABLE. State changes MUST go through delta
# application, not direct attribute mutation.

"""
Canonical ExecutionThread entity with controlled operations.

An ExecutionThread represents one continuous semantic activity within Gordon.
It owns:
    - semantic identity (ExecutionThreadId)
    - continuity across multiple finite executions  
    - purpose (enduring reason for existence)
    - objectives (current targets that may evolve)
    - accepted semantic state
    - active Loop association (at most one)
    - at most one active Cycle association
    - parent and child ExecutionThread relationships

An ExecutionThread does NOT own:
    - operating-system threads
    - asyncio task management  
    - worker pools
    - scheduling algorithms
    - runtime resource ownership

Canonical Relationship Model:

    ExecutionDomain
    └── ExecutionThread (this module)
        ├── ThreadState (state.py)
        ├── ThreadHistory (not yet implemented)
        ├── relationships (relationships.py)
        │   ├── ParentChildRelationship
        │   └── ThreadRelationshipGraph  
        ├── active_loop_id
        └── active_cycle_id
            │
            ▼
        ExecutionLoop (loops/__init__.py)
            ├── LoopPolicy
            ├── LoopState
            ├── BehavioralMode
            └── LoopDecision

Cardinality:
    ExecutionThread 1 ─── 0..1 active ExecutionLoop
    ExecutionThread 1 ─── 0..1 active Cycle

Invariants:
    T-001: ExecutionThread identity is immutable (ExecutionThreadId)
    T-002: Revision increases after every accepted delta  
    T-003: At most one active ExecutionLoop exists
    T-004: At most one authoritative active Cycle exists
    T-005: Terminal ExecutionThreads reject new delta application attempts

USAGE:
    # Create an execution thread with semantic identity
    from agent.execution.threads import ExecutionThread, ExecutionThreadId, ThreadLifecycleState
    
    thread = ExecutionThread(
        id=ExecutionThreadId.generate(),
        lifecycle_state=ThreadLifecycleState.CREATED,
        parent_thread_id=None,
        child_thread_ids=(),
        active_loop_id=None,
        active_cycle_id=None,
    )
    
    # Get snapshot for Loop evaluation
    snapshot = ExecutionThreadSnapshot.from_thread(thread)
    
    # Use delta application to mutate state (not direct attribute access!)
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple

# Import identity types - use canonical Execution* names
from .identity import ThreadId

# Import lifecycle - semantic states from threads.lifecycle
from .lifecycle import ThreadLifecycleState

# Import state for semantic content  
from .state import ThreadSemanticState


@dataclass(frozen=True)
class ExecutionThread:
    """
    Immutable canonical ExecutionThread entity.
    
    All state changes must go through delta application, not direct mutation.
    
    Fields:
        id: Unique semantic identity (ExecutionThreadId) - immutable
        lifecycle_state: Current lifecycle state (from threads.lifecycle)
        parent_thread_id: Parent if any
        child_thread_ids: Children created by this thread
        active_loop_id: Reference to the active Loop (at most one)
        active_cycle_id: Reference to the active Cycle (at most one)  
        terminal_reason: Reason for terminal state if applicable
    
    A semantic continuity entity.

    This is not an operating-system thread, worker thread, or concurrency primitive.
    """
    
    # Identity (immutable) - no defaults
    id: ThreadId
    
    # Lifecycle state (semantic intent)
    lifecycle_state: ThreadLifecycleState = ThreadLifecycleState.CREATED
    
    # Relationships - stored directly
    parent_thread_id: Optional[str] = None  # Parent if any
    child_thread_ids: Tuple[str, ...] = ()  # Children created by this thread
    
    # Active components (optional) - at most one each  
    active_loop_id: Optional[str] = None
    active_cycle_id: Optional[str] = None
    
    # Terminal state tracking
    terminal_reason: Optional[str] = None


@dataclass(frozen=True)
class ExecutionThreadSnapshot:
    """
    Read-only snapshot of an ExecutionThread's state for Loop evaluation.
    
    Contains only semantic information needed for behavioral decisions.
    Does NOT contain mutable runtime details or Core implementation references.
    
    Used by Loop to make cycle selection and continuation policy decisions.
    """
    
    id: ThreadId
    lifecycle_state: ThreadLifecycleState
    
    # Semantic content (derived from thread state)
    state: ThreadSemanticState = field(default_factory=lambda: ThreadSemanticState(thread_id=""))
    
    # Relationship info (all optional, must come first in frozen dataclass)
    parent_thread_id: Optional[str] = None
    child_thread_ids: Tuple[str, ...] = ()
    
    # Active components (optional) - at most one each  
    active_loop_id: Optional[str] = None
    active_cycle_id: Optional[str] = None
    
    # Terminal state tracking
    terminal_reason: Optional[str] = None


# =============================================================================
# Export all public symbols
# =============================================================================

# Backward compatibility aliases
Thread = ExecutionThread
ThreadSnapshot = ExecutionThreadSnapshot

__all__ = [
    "ExecutionThread",      # Canonical immutable ExecutionThread entity
    "ExecutionThreadSnapshot",  # Read-only snapshot for Loop evaluation
    
    # Backward compatibility aliases (deprecated, will be removed in future)
    "Thread",
    "ThreadSnapshot",
]
