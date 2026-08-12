# Lifecycle Coordinator - Canonical Authority
# =============================================

"""
Lifecycle coordinator for runtime entities.

PHASE 3.7.21 REMEDIATION:
- Lifecycle transitions are owned by records, not a central manager
- Each record tracks its own lifecycle state
- Transitions produce immutable event records

The coordinator validates and logs transitions but doesn't store state.
Records maintain their own lifecycle_state field.
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum

from .models import (
    LifecycleState,
    LifecycleEvent,
    LifecycleTransition,
)


# Valid lifecycle transitions (runtime-level states)
TRANSITIONS: Dict[LifecycleState, List[LifecycleState]] = {
    LifecycleState.CREATED: [
        LifecycleState.INITIALIZING,
        LifecycleState.FAILED,
    ],
    LifecycleState.INITIALIZING: [
        LifecycleState.READY,
        LifecycleState.FAILED,
    ],
    LifecycleState.READY: [
        LifecycleState.STARTING,
        LifecycleState.STOPPED,
        LifecycleState.FAILED,
    ],
    LifecycleState.STARTING: [
        LifecycleState.RUNNING,
        LifecycleState.STOPPING,
        LifecycleState.FAILED,
    ],
    LifecycleState.RUNNING: [
        LifecycleState.STOPPING,
        LifecycleState.FAILED,
    ],
    LifecycleState.STOPPING: [
        LifecycleState.STOPPED,
        LifecycleState.FAILED,
    ],
    LifecycleState.STOPPED: [
        LifecycleState.STARTING,  # Allow restart
        LifecycleState.FAILED,
    ],
    LifecycleState.FAILED: [],  # Terminal state
}


@dataclass(frozen=True)
class LifecycleTransitionRecord:
    """
    An immutable record of a lifecycle state transition.
    
    PHASE 3.7.21 REMEDIATION:
    - Each record owns its lifecycle_state field
    - This record captures the transition event for provenance
    - Embedded in EventEnvelope, FailureRecord, etc.
    
    Args:
        from_state: Previous lifecycle state
        to_state: New lifecycle state
        timestamp: When transition occurred
        entity_id: Entity that transitioned
        performed_by: Entity ID that initiated transition
        reason: Reason for the transition (optional)
    """
    
    from_state: LifecycleState
    to_state: LifecycleState
    timestamp: float = field(default_factory=time.time)
    entity_id: str = "system"
    performed_by: str = "system"
    reason: Optional[str] = None


class LifecycleCoordinator:
    """
    Coordinator for lifecycle state transitions.
    
    PHASE 3.7.21 REMEDIATION:
    - Validates transitions but doesn't own record state
    - Each record maintains its own lifecycle_state field
    - Transitions produce immutable records for provenance
    
    Usage:
        coordinator = LifecycleCoordinator()
        
        # Validate transition
        if coordinator.can_transition(LifecycleState.RUNNING, LifecycleState.STOPPING):
            # Record owns its state
            record.lifecycle_state = LifecycleState.STOPPING
            # Create transition record for provenance
            transition = LifecycleTransitionRecord(
                from_state=LifecycleState.RUNNING,
                to_state=LifecycleState.STOPPING,
                entity_id=record.entity_id,
                reason="shutdown"
            )
    """
    
    def __init__(self) -> None:
        """Initialize the lifecycle coordinator."""
        self._lock = threading.RLock()
        
        # Transition history for observability
        self._transition_history: List[LifecycleTransitionRecord] = []
        
        # Statistics
        self._stats = {
            "total_transitions": 0,
        }
    
    def can_transition(self, from_state: LifecycleState, to_state: LifecycleState) -> bool:
        """
        Check if a transition is valid.
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Returns:
            True if the transition is allowed
        """
        with self._lock:
            allowed = TRANSITIONS.get(from_state, [])
            return to_state in allowed
    
    def validate_transition(
        self,
        from_state: LifecycleState,
        to_state: LifecycleState,
    ) -> None:
        """
        Validate a transition and raise if invalid.
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Raises:
            ValueError: If the transition is not allowed
        """
        if not self.can_transition(from_state, to_state):
            raise ValueError(
                f"Invalid transition from {from_state.value} to {to_state.value}"
            )
    
    async def record_transition(
        self,
        from_state: LifecycleState,
        to_state: LifecycleState,
        entity_id: str = "system",
        performed_by: str = "system",
        reason: Optional[str] = None,
    ) -> LifecycleTransitionRecord:
        """
        Record a lifecycle transition for provenance.
        
        PHASE 3.7.21: The coordinator does NOT own record state.
        Records maintain their own lifecycle_state field.
        This method only creates the transition record for provenance.
        
        Args:
            from_state: Previous lifecycle state
            to_state: New lifecycle state
            entity_id: Entity that transitioned
            performed_by: Who initiated the transition
            reason: Reason for the transition
            
        Returns:
            LifecycleTransitionRecord for inclusion in other records
        """
        with self._lock:
            # Validate before recording
            if not self.can_transition(from_state, to_state):
                raise ValueError(
                    f"Invalid transition from {from_state.value} to {to_state.value}"
                )
            
            record = LifecycleTransitionRecord(
                from_state=from_state,
                to_state=to_state,
                entity_id=entity_id,
                performed_by=performed_by,
                reason=reason,
            )
            
            self._transition_history.append(record)
            self._stats["total_transitions"] += 1
            
            return record
    
    def get_transition_history(self) -> List[LifecycleTransitionRecord]:
        """Get a copy of the transition history."""
        with self._lock:
            return list(self._transition_history)
    
    @property
    def total_transitions(self) -> int:
        """Get count of recorded transitions."""
        with self._lock:
            return self._stats["total_transitions"]
    
    def is_valid_state_change(
        self,
        current: LifecycleState,
        target: LifecycleState,
    ) -> bool:
        """
        Check if a state change is valid (idempotent states allowed).
        
        Args:
            current: Current state
            target: Target state
            
        Returns:
            True if the state change is valid
        """
        # Idempotent: same state is always valid
        if current == target:
            return True
        
        return self.can_transition(current, target)


__all__ = [
    "TRANSITIONS",
    "LifecycleCoordinator",
    "LifecycleTransitionRecord",
]