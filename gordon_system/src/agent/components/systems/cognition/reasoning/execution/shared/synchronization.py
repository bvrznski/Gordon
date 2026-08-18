# Execution Reasoning Synchronization - Phase 7.21
# =================================================

"""
Canonical Execution Synchronization for Phase 7.21.

Synchronization manages parallel workers, shared resources,
mutexes, barriers, and distributed coordination.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class SynchronizationPolicy(Enum):
    """Synchronization policy types."""
    
    STRICT_ORDERING = "strict_ordering"     # Commands must execute in strict order
    BARRIER_SYNC = "barrier_sync"           # All commands must reach barrier before proceeding
    MUTEX_LOCK = "mutex_lock"               # Mutual exclusion for shared resources
    SEQUENTIAL_BARRIERS = "sequential_barriers"  # Multiple barriers with ordering


class SynchronizationState(Enum):
    """Synchronization state."""
    
    PENDING = "pending"
    WAITING = "waiting"
    SYNCHRONIZED = "synchronized"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class SynchronizationPoint:
    """
    A synchronization point in execution.
    
    Defines a barrier where commands must coordinate before proceeding.
    """
    
    # Identity
    synchronization_identity: str               # Unique sync point identifier
    
    # Waiting commands
    waiting_command_ids: Tuple[str, ...]
    
    # Policy
    synchronization_policy: SynchronizationPolicy = SynchronizationPolicy.STRICT_ORDERING
    
    # State
    synchronization_state: SynchronizationState = SynchronizationState.PENDING
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        waiting_command_ids: Tuple[str, ...],
        synchronization_policy: SynchronizationPolicy = SynchronizationPolicy.STRICT_ORDERING,
    ) -> SynchronizationPoint:
        """Create a new synchronization point."""
        return cls(
            synchronization_identity=f"sync_point:{uuid.uuid4().hex[:16]}",
            waiting_command_ids=waiting_command_ids,
            synchronization_policy=synchronization_policy,
        )
    
    def to_state(self, new_state: SynchronizationState) -> SynchronizationPoint:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            synchronization_state=new_state,
        )


@dataclass(frozen=True)
class OrderingConstraints:
    """
    Ordering constraints for execution commands.
    
    Specifies which commands must execute before others.
    """
    
    # Identity
    constraint_identity: str
    
    # Constraint type
    constraint_type: str                        # e.g., "before", "after", "parallel"
    
    # Affected command IDs
    predecessor_ids: Tuple[str, ...] = ()
    successor_ids: Tuple[str, ...] = ()
    
    @classmethod
    def create(
        cls,
        constraint_type: str,
        predecessor_ids: Tuple[str, ...] = (),
        successor_ids: Tuple[str, ...] = (),
    ) -> OrderingConstraints:
        """Create ordering constraints."""
        return cls(
            constraint_identity=f"order_constraint:{uuid.uuid4().hex[:16]}",
            constraint_type=constraint_type,
            predecessor_ids=predecessor_ids,
            successor_ids=successor_ids,
        )


@dataclass(frozen=True)
class SynchronizationGraph:
    """
    Graph of synchronization relationships.
    
    Represents all synchronization points and their dependencies.
    """
    
    # Identity
    graph_identity: str
    
    # Points in the graph
    synchronization_points: Tuple[SynchronizationPoint, ...]
    
    # Ordering constraints
    ordering_constraints: Tuple[OrderingConstraints, ...] = ()
    
    @classmethod
    def create(
        cls,
        synchronization_points: Tuple[SynchronizationPoint, ...],
        ordering_constraints: Tuple[OrderingConstraints, ...] = (),
    ) -> SynchronizationGraph:
        """Create a new synchronization graph."""
        return cls(
            graph_identity=f"sync_graph:{uuid.uuid4().hex[:16]}",
            synchronization_points=synchronization_points,
            ordering_constraints=ordering_constraints,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SynchronizationPoint",
    "SynchronizationPolicy",
    "SynchronizationState",
    "OrderingConstraints",
    "SynchronizationGraph",
]