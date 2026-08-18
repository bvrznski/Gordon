# Executive Synchronization - Phase 7.30
# =======================================

"""
Executive Synchronization Management.

Synchronization evaluates:
    - Event ordering across subsystems
    - State consistency guarantees
    - Dependency barriers
    - Resource synchronization

Synchronization remains explicit and inspectable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any

from .shared import (
    ExecutiveSet,
    SubsystemType,
    SyncState,
    SynchronizationManagement,
)


@dataclass(frozen=True)
class SynchronizationBarrier:
    """
    A synchronization barrier that subsystems must wait at.
    
    A barrier specifies:
        - Which subsystems must reach the barrier
        - What state they must be in
        - Timeout constraints
    """
    
    # Identity
    barrier_id: str                             # Unique identifier
    
    # Subsystems involved
    waiting_subsystems: Tuple[str, ...]         # Who must wait?
    completed_subsystems: Tuple[str, ...] = ()  # Who has passed?
    
    # State requirements (subsystem -> required state)
    state_requirements: Dict[str, str] = field(default_factory=dict)
    
    # Timeout
    timeout_seconds: float = 60.0               # Default 60 seconds
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_passed(self) -> bool:
        """Check if all subsystems have passed the barrier."""
        return len(self.waiting_subsystems) == len(self.completed_subsystems)
    
    @classmethod
    def create(
        cls,
        subsystems: List[str],
        state_requirements: Optional[Dict[str, str]] = None,
        timeout_seconds: float = 60.0,
    ) -> "SynchronizationBarrier":
        """Create a new synchronization barrier."""
        return cls(
            barrier_id=f"sync_barrier:{uuid.uuid4().hex[:16]}",
            waiting_subsystems=tuple(subsystems),
            state_requirements=state_requirements or {},
            timeout_seconds=timeout_seconds,
        )
    
    def with_completion(self, subsystem: str) -> "SynchronizationBarrier":
        """Record that a subsystem has passed the barrier."""
        if subsystem in self.completed_subsystems:
            return self  # Already completed
        
        new_completed = self.completed_subsystems + (subsystem,)
        return dataclass_replace(
            self,
            completed_subsystems=new_completed,
        )


@dataclass(frozen=True)
class SynchronizationPlan:
    """
    Explicit synchronization plan for multiple subsystems.
    
    A plan specifies:
        - Barriers at which to synchronize
        - Dependencies between barriers
        - Timeout strategy
    """
    
    # Identity
    plan_id: str                                # Unique identifier
    
    # Description
    description: str                            # What does this sync do?
    scope: Tuple[str, ...] = ()                 # Affected subsystems
    
    # Barriers in order
    barriers: Tuple[SynchronizationBarrier, ...] = ()
    
    # Timeout policy
    timeout_policy: str = "fail_fast"           # fail_fast, wait_all, retry
    
    # Timing
    planned_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        description: str,
        scope: Optional[List[str]] = None,
    ) -> "SynchronizationPlan":
        """Create a new synchronization plan."""
        return cls(
            plan_id=f"sync_plan:{uuid.uuid4().hex[:16]}",
            description=description,
            scope=tuple(scope or []),
        )


@dataclass(frozen=True)
class Synchronizer:
    """
    Global executive synchronizer that manages state consistency.
    
    The synchronizer ensures that subsystems reach consistent states
    before proceeding to next phases of execution.
    """
    
    # Identity
    synchronizer_id: str                        # Unique identifier
    
    # Policy
    synchronization_policy: str                 # Policy name
    
    # Current barriers (by ID)
    active_barriers: Dict[str, SynchronizationBarrier] = field(default_factory=dict)
    
    # Completed synchronizations (history)
    completed_synchronizations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Metrics
    total_syncs: int = 0
    successful_syncs: int = 0
    
    @classmethod
    def create(
        cls,
        policy: str = "default",
    ) -> "Synchronizer":
        """Create a new synchronizer."""
        return cls(
            synchronizer_id=f"synchronizer:{uuid.uuid4().hex[:16]}",
            synchronization_policy=policy,
        )
    
    def add_barrier(self, barrier: SynchronizationBarrier) -> "Synchronizer":
        """Add a barrier to the active set."""
        new_barriers = dict(self.active_barriers)
        new_barriers[barrier.barrier_id] = barrier
        return dataclass_replace(self, active_barriers=new_barriers)
    
    def record_completion(
        self,
        barrier_id: str,
        subsystem: str,
    ) -> Tuple[SynchronizationBarrier, "Synchronizer"]:
        """Record a subsystem completing a barrier."""
        if barrier_id not in self.active_barriers:
            raise ValueError(f"Unknown barrier: {barrier_id}")
        
        barrier = self.active_barriers[barrier_id]
        completed_barrier = barrier.with_completion(subsystem)
        
        new_barriers = dict(self.active_barriers)
        del new_barriers[barrier_id]  # Remove from active
        
        return completed_barrier, dataclass_replace(
            self,
            active_barriers=new_barriers,
            completed_synchronizations=self.completed_synchronizations + ({
                "barrier_id": barrier_id,
                "subsystem": subsystem,
                "timestamp_utc": time.time(),
            },),
            total_syncs=self.total_syncs + 1,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SynchronizationBarrier",
    "SynchronizationPlan",
    "Synchronizer",
]