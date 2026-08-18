# Executive Coordination - Phase 7.30
# ====================================

"""
Executive Coordination Management.

Coordination evaluates:
    - Goal interactions between subsystems
    - Mission dependencies
    - Resource competition  
    - Attention conflicts
    - Execution ordering

Coordination remains explicit and inspectable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any

from .shared import (
    ExecutiveSet,
    SubsystemType,
    CoordinationManagement,
)


@dataclass(frozen=True)
class ExecutiveCoordinator:
    """
    Global executive coordinator that manages subsystem interactions.
    
    The coordinator ensures that all subsystems work together coherently
    toward the executive goal without conflicts or resource contention.
    """
    
    # Identity
    coordinator_id: str                         # Unique identifier
    
    # Coordination session
    coordination_session_id: str                # Session being coordinated
    executive_set: ExecutiveSet                 # Participating subsystems
    
    # Policy
    coordination_policy: str = "default"
    
    # Coordination state
    active_subsystems: Tuple[str, ...] = ()     # Currently active
    pending_subsystems: Tuple[str, ...] = ()    # Waiting to start
    completed_subsystems: Tuple[str, ...] = ()  # Finished
    
    # Metrics
    coordination_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    @property
    def is_active(self) -> bool:
        """Check if coordinator is actively coordinating."""
        return len(self.active_subsystems) > 0
    
    @classmethod
    def create(
        cls,
        coordination_session_id: str,
        executive_set: ExecutiveSet,
        policy: str = "default",
    ) -> "ExecutiveCoordinator":
        """Create a new executive coordinator."""
        return cls(
            coordinator_id=f"coordinator:{uuid.uuid4().hex[:16]}",
            coordination_session_id=coordination_session_id,
            executive_set=executive_set,
            coordination_policy=policy,
            started_at_utc=time.time(),
        )
    
    def with_subsystem_state(
        self,
        active: Optional[List[str]] = None,
        pending: Optional[List[str]] = None,
        completed: Optional[List[str]] = None,
    ) -> "ExecutiveCoordinator":
        """Return a copy with updated subsystem states."""
        return dataclass_replace(
            self,
            active_subsystems=tuple(active or []),
            pending_subsystems=tuple(pending or []),
            completed_subsystems=tuple(completed or []),
        )


@dataclass(frozen=True)
class CoordinationPlan:
    """
    Explicit coordination plan for executing coordinated tasks.
    
    A coordination plan specifies:
        - Subsystem execution order
        - Resource allocation per subsystem
        - Synchronization points
        - Contingency plans
    """
    
    # Identity
    plan_id: str                                # Unique identifier
    
    # Plan details
    description: str                            # What does this plan do?
    scope: Tuple[str, ...] = ()                 # Affected subsystems
    
    # Steps (ordered execution)
    steps: Tuple[Dict[str, Any], ...] = ()      # Execution steps
    
    # Synchronization points
    sync_points: Tuple[int, ...] = ()           # Step indices where sync occurs
    
    # Dependencies (step index -> list of dependent step indices)
    dependencies: Dict[int, List[int]] = field(default_factory=dict)
    
    # Timing
    planned_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        description: str,
        scope: Optional[List[str]] = None,
    ) -> "CoordinationPlan":
        """Create a new coordination plan."""
        return cls(
            plan_id=f"coord_plan:{uuid.uuid4().hex[:16]}",
            description=description,
            scope=tuple(scope or []),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ExecutiveCoordinator",
    "CoordinationPlan",
]