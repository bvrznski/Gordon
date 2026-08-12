# Thread Architecture Package
# ===========================

"""
Canonical Thread architecture for semantic continuity.

A Thread is NOT:
    - An operating-system thread, coroutine, task, worker, process, or scheduler entry
    - A runtime execution unit (that belongs to Core)
    - A scheduling entity (that belongs to Core)

A Thread IS:
    - The semantic owner of one continuous agent activity
    - Persistent identity across multiple finite executions
    - Purpose-driven: maintains purpose while objectives may evolve
    - Lifecycle-managed through controlled transitions

Architecture:

    src/agent/execution/threads/
        ├── __init__.py           # Package exports
        ├── base.py               # Abstract Thread, Loop, Cycle contracts (TBD)
        ├── identity.py           # Semantic Thread identity (immutable)
        ├── state.py              # Thread semantic state (controlled mutation)
        ├── lifecycle.py          # Lifecycle transitions and states
        ├── delta.py              # Semantic delta application model
        ├── relationships.py      # Parent-child Thread relationships
        ├── snapshot.py           # Immutable snapshots for persistence
        └── validation.py         # Invariant validators

Ownership Model:

    Thread: semantic continuity, identity, purpose, objectives, completion intent
    Core: runtime scheduling, lifecycle state transitions, resource allocation

Architecture Invariants:
    T-001: Thread identity is immutable (semantic, not runtime)
    T-002: A Thread has exactly one active Loop when behavior progresses
    T-003: A Thread has at most one active authoritative Cycle
    T-004: Semantic state changes occur through controlled delta application
    T-005: Thread lifecycle transitions are validated by core.lifecycle

NOTE: Base classes (Thread, Loop, Cycle) will be defined in base.py when
      concrete implementations are ready. For now, they serve as placeholders.
"""

# Identity imports
from .identity import (
    ThreadId,
    ThreadName,
    ThreadMetadata,
    ThreadDescriptor,
)

# Lifecycle imports
from .lifecycle import (
    ThreadLifecycleState as ThreadState,
    ThreadLifecycleTransitionGraph,
    ThreadLifecycleReason,
    ThreadLifecycleTransition,
    ThreadLifecycleSnapshot,
    ThreadLifecycleTransitionRequest,
    ThreadLifecycleTransitionResult,
)

# Delta imports
from .delta import (
    ThreadSemanticDelta as ThreadDelta,
    DeltaValidationResult,
    ThreadDeltaBatch,
    DeltaApplicationResult,
    ThreadDeltaValidator,
)

# Relationships imports
from .relationships import (
    RelationshipKind,
    ThreadRelationship,
    ParentChildRelationship,
    ThreadRelationshipGraph,
    ThreadRelationshipSnapshot,
)

# Snapshot imports
from .snapshot import (
    ThreadSnapshot,
    ThreadRecoveryDescriptor,
    ThreadSnapshotBuilder,
    ThreadSnapshotChain,
)

# Validation imports
from .validation import (
    ValidationResult,
    ThreadValidator,
)


__all__ = [
    # Identity
    "ThreadId",
    "ThreadName",
    "ThreadMetadata",
    "ThreadDescriptor",
    
    # Lifecycle
    "ThreadState",
    "ThreadLifecycleTransitionGraph",
    "ThreadLifecycleReason",
    "ThreadLifecycleTransition",
    "ThreadLifecycleSnapshot",
    "ThreadLifecycleTransitionRequest",
    "ThreadLifecycleTransitionResult",
    
    # Delta
    "ThreadDelta",
    "DeltaValidationResult",
    "ThreadDeltaBatch",
    "DeltaApplicationResult",
    "ThreadDeltaValidator",
    
    # Relationships
    "RelationshipKind",
    "ThreadRelationship",
    "ParentChildRelationship",
    "ThreadRelationshipGraph",
    "ThreadRelationshipSnapshot",
    
    # Snapshots
    "ThreadSnapshot",
    "ThreadRecoveryDescriptor",
    "ThreadSnapshotBuilder",
    "ThreadSnapshotChain",
    
    # Validation
    "ValidationResult",
    "ThreadValidator",
]
