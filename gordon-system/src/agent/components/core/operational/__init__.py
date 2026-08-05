# Core Operational State Infrastructure
# ====================================

"""
Core operational state infrastructure for Gordon runtime.

Provides:
- Canonical operational state authority
- State transitions between readiness, admission, and operation
- Operational state synchronization
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import time


# =============================================================================
# Operational States
# =============================================================================

class OperationalState(Enum):
    """
    Operational state values for runtime execution capability.
    
    State transitions:
        INITIAL → READY (after activation)
        READY → ADMISSION_OPEN (after readiness passes)
        ADMISSION_OPEN → OPERATIONAL (ready to execute tasks)
        
        OPERATIONAL can transition to:
        - DEGRADED (on partial failure)
        - MAINTENANCE (operator requested maintenance)
        - STOPPING (on shutdown request)
        
        DEGRADED can recover back to OPERATIONAL
    """
    INITIAL = "initial"           # Not yet operational
    READY = "ready"               # Ready for admission but not open yet
    ADMISSION_OPEN = "admission_open"  # Admission is open, tasks may be queued
    OPERATIONAL = "operational"   # Fully operational, executing tasks
    DEGRADED = "degraded"         # Operational with reduced capability
    MAINTENANCE = "maintenance"   # Maintenance mode - restricted operations only
    STOPPING = "stopping"         # Graceful shutdown in progress
    STOPPED = "stopped"           # Fully stopped
    FAILED = "failed"             # Operational failure


# =============================================================================
# Operational State Transition
# =============================================================================

@dataclass(frozen=True)
class OperationalStateTransition:
    """
    A state transition record.
    
    Args:
        from_state: Previous operational state
        to_state: New operational state
        timestamp: When the transition occurred
        reason: Explanation for the transition
    """
    
    from_state: OperationalState
    to_state: OperationalState
    timestamp: float = field(default_factory=time.monotonic)
    reason: str = ""


# =============================================================================
# Operational State Store
# =============================================================================

class OperationalStateStore:
    """
    Authoritative store for runtime operational state.
    
    This is the ONE source of truth for whether the runtime can execute tasks.
    """
    
    def __init__(self, initial_state: OperationalState = OperationalState.INITIAL) -> None:
        self._state = initial_state
        self._transitions: List[OperationalStateTransition] = []
        self._lock = False
    
    @property
    def state(self) -> OperationalState:
        """Get current operational state."""
        return self._state
    
    @property
    def transitions(self) -> List[OperationalStateTransition]:
        """Get history of state transitions."""
        return list(self._transitions)
    
    # -------------------------------------------------------------------------
    # State Transitions
    # -------------------------------------------------------------------------
    
    def transition(
        self,
        to_state: OperationalState,
        reason: str = ""
    ) -> bool:
        """
        Transition to a new operational state.
        
        Args:
            to_state: Target state
            reason: Explanation for the transition
            
        Returns:
            True if transition succeeded, False otherwise
        """
        allowed_transitions = self._get_allowed_transitions(self._state)
        
        if to_state not in allowed_transitions:
            return False
        
        old_state = self._state
        self._state = to_state
        
        self._transitions.append(OperationalStateTransition(
            from_state=old_state,
            to_state=to_state,
            reason=reason
        ))
        
        return True
    
    def _get_allowed_transitions(self, state: OperationalState) -> List[OperationalState]:
        """Get list of allowed transitions from current state."""
        transitions = {
            OperationalState.INITIAL: [
                OperationalState.READY,
                OperationalState.FAILED
            ],
            OperationalState.READY: [
                OperationalState.ADMISSION_OPEN,
                OperationalState.STOPPED,
                OperationalState.FAILED
            ],
            OperationalState.ADMISSION_OPEN: [
                OperationalState.OPERATIONAL,
                OperationalState.STOPPING,
                OperationalState.STOPPED
            ],
            OperationalState.OPERATIONAL: [
                OperationalState.DEGRADED,
                OperationalState.STOPPING,
                OperationalState.STOPPED,
                OperationalState.FAILED
            ],
            OperationalState.DEGRADED: [
                OperationalState.OPERATIONAL,
                OperationalState.STOPPING,
                OperationalState.STOPPED,
                OperationalState.FAILED
            ],
            OperationalState.STOPPING: [
                OperationalState.STOPPED,
                OperationalState.FAILED
            ],
            OperationalState.STOPPED: [
                OperationalState.INITIAL,  # Restart allowed
                OperationalState.FAILED
            ],
            OperationalState.MAINTENANCE: [
                OperationalState.OPERATIONAL,  # Return from maintenance
                OperationalState.STOPPING,
                OperationalState.STOPPED,
                OperationalState.FAILED
            ],
            OperationalState.FAILED: []  # Terminal - no transitions
        }
        
        return transitions.get(state, [])
    
    # -------------------------------------------------------------------------
    # Convenience Methods
    # -------------------------------------------------------------------------
    
    def is_operational(self) -> bool:
        """Check if runtime is in an operational state (not maintenance)."""
        return self._state == OperationalState.OPERATIONAL
    
    def can_execute_work(self) -> bool:
        """Check if runtime can execute work (excludes degraded and maintenance)."""
        return self._state == OperationalState.OPERATIONAL
    
    def is_maintenance_mode(self) -> bool:
        """Check if runtime is in maintenance mode."""
        return self._state == OperationalState.MAINTENANCE
    
    def is_ready_for_admission(self) -> bool:
        """Check if runtime is ready for admission."""
        return self._state in (OperationalState.READY, OperationalState.ADMISSION_OPEN)
    
    def reset(self) -> None:
        """Reset to initial state."""
        self._state = OperationalState.INITIAL
        self._transitions.clear()


# =============================================================================
# Operational Authority
# =============================================================================

class RuntimeOperationalAuthority:
    """
    Single canonical authority for runtime operational state.
    
    This coordinates the transition from READY → ADMISSION_OPEN → OPERATIONAL
    based on readiness and admission evaluation.
    """
    
    def __init__(self) -> None:
        self._state_store = OperationalStateStore()
    
    @property
    def state(self) -> OperationalState:
        """Get current operational state."""
        return self._state_store.state
    
    @property
    def is_operational(self) -> bool:
        """Check if runtime can execute tasks."""
        return self._state_store.is_operational()
    
    async def transition_to_operational(
        self,
        readiness_ready: bool = True,
        admission_open: bool = True
    ) -> bool:
        """
        Transition the runtime to operational state.
        
        Args:
            readiness_ready: Whether readiness evaluation passed
            admission_open: Whether admission is open
            
        Returns:
            True if transition succeeded, False otherwise
        """
        # Check readiness requirement
        if not readiness_ready:
            return False
        
        # Transition chain: INITIAL → READY → ADMISSION_OPEN → OPERATIONAL
        
        current = self._state_store.state
        
        if current == OperationalState.INITIAL:
            if self._state_store.transition(OperationalState.READY, "Runtime ready"):
                current = OperationalState.READY
        
        if current == OperationalState.READY:
            if admission_open:
                if self._state_store.transition(
                    OperationalState.ADMISSION_OPEN,
                    "Admission opened"
                ):
                    current = OperationalState.ADMISSION_OPEN
            else:
                return False
        
        if current == OperationalState.ADMISSION_OPEN:
            if self._state_store.transition(
                OperationalState.OPERATIONAL,
                "Operational execution started"
            ):
                return True
        
        return current == OperationalState.OPERATIONAL
    
    async def transition_to_degraded(self, reason: str = "") -> bool:
        """Transition to degraded state."""
        return self._state_store.transition(
            OperationalState.DEGRADED,
            f"Degraded: {reason}"
        )
    
    def stop(self) -> None:
        """Initiate graceful shutdown."""
        self._state_store.transition(OperationalState.STOPPING, "Shutdown requested")
        self._state_store.transition(OperationalState.STOPPED, "Shutdown complete")
    
    async def enter_maintenance_mode(self, reason: str = "") -> bool:
        """Transition to maintenance mode."""
        return self._state_store.transition(
            OperationalState.MAINTENANCE,
            f"Maintenance mode: {reason}"
        )
    
    async def exit_maintenance_mode(self) -> bool:
        """Exit maintenance mode and return to operational."""
        if self._state_store.state == OperationalState.MAINTENANCE:
            # First return to OPERATIONAL from MAINTENANCE
            return self._state_store.transition(
                OperationalState.OPERATIONAL,
                "Maintenance complete"
            )
        return False
    
    def get_state_history(self) -> List[Dict[str, Any]]:
        """Get state transition history."""
        return [
            {
                "from": t.from_state.value,
                "to": t.to_state.value,
                "reason": t.reason
            }
            for t in self._state_store.transitions
        ]


# =============================================================================
# Factory
# =============================================================================

def create_operational_authority() -> RuntimeOperationalAuthority:
    """Create a new operational authority instance."""
    return RuntimeOperationalAuthority()


__all__ = [
    "OperationalState",
    "OperationalStateTransition",
    "OperationalStateStore",
    "RuntimeOperationalAuthority",
    "create_operational_authority",
]