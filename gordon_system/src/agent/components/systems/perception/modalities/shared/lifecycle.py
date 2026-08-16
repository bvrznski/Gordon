# Modality Lifecycle - Phase 5.2 State Transitions
# ================================================

"""
ModalityLifecycle: The lifecycle state of a modality through its operational
history.

The lifecycle tracks a modality from discovery through activation, operation,
and termination.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# LIFECYCLE STATE - States in the modality lifecycle
# =============================================================================


class LifecycleState(Enum):
    """
    States in the modality lifecycle.
    
    DISCOVERED: Modality detected but not yet initialized
    UNAVAILABLE: Detected but temporarily inaccessible
    INITIALIZING: Currently being set up
    CALIBRATING: Calibration in progress
    READY: Initialized and calibrated, awaiting activation
    ACTIVE: Actively acquiring observations
    DEGRADED: Degraded operation (some capabilities unavailable)
    SANDBOXED: Limited by sandbox constraints
    SUSPENDED: Temporarily paused
    FAILED: Failed during operation
    TERMINATED: Permanently stopped
    """
    
    DISCOVERED = "discovered"
    UNAVAILABLE = "unavailable"
    INITIALIZING = "initializing"
    CALIBRATING = "calibrating"
    READY = "ready"
    ACTIVE = "active"
    DEGRADED = "degraded"
    SANDBOXED = "sandboxed"
    SUSPENDED = "suspended"
    FAILED = "failed"
    TERMINATED = "terminated"


# =============================================================================
# LIFECYCLE EVENT - Changes in lifecycle state
# =============================================================================


class LifecycleEvent(Enum):
    """
    Events that trigger lifecycle transitions.
    
    DISCOVERED: Modality first detected by the system
    INITIATED: Initialization process started
    CALIBRATED: Calibration completed (or skipped)
    ACTIVATED: Modality began active observation
    DEGRADED: Some capabilities became unavailable
    SANDBOXED: Sandbox constraints applied
    SUSPENDED: Operation temporarily paused
    RESUMED: Operation resumed after suspension
    FAILED: Operation failed
    TERMINATED: Lifecycle ended
    RESTARTED: Restarted from terminated state
    """
    
    DISCOVERED = "discovered"
    INITIATED = "initiated"
    CALIBRATED = "calibrated"
    ACTIVATED = "activated"
    DEGRADED = "degraded"
    SANDBOXED = "sandboxed"
    SUSPENDED = "suspended"
    RESUMED = "resumed"
    FAILED = "failed"
    TERMINATED = "terminated"
    RESTARTED = "restarted"


# =============================================================================
# LIFECYCLE TRANSITION - State change record
# =============================================================================


@dataclass(frozen=True)
class LifecycleTransition:
    """
    A single state transition in the modality lifecycle.
    
    Fields:
        from_state:         Previous lifecycle state
        to_state:           New lifecycle state
        event:              Event that triggered this transition
        
        timestamp_utc:      When the transition occurred
        
        metadata:           Additional information about the transition
        provenance:         Transition tracking
    """
    
    # Core identity (required)
    from_state: str                     # LifecycleState value
    
    to_state: str                       # LifecycleState value
    
    event: str = "unknown"              # LifecycleEvent value
    
    timestamp_utc: float = field(default_factory=time.time)
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if this transition represents a valid state change."""
        return self.from_state != self.to_state
    
    @classmethod
    def create(
        cls,
        from_state: str,
        to_state: str,
        event: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "LifecycleTransition":
        """
        Create a new lifecycle transition.
        
        Args:
            from_state: Previous state
            to_state: New state
            event: Event that triggered the change
            metadata: Additional information
            
        Returns:
            New LifecycleTransition instance
        """
        return cls(
            from_state=from_state,
            to_state=to_state,
            event=event or "manual",
            timestamp_utc=time.time(),
            metadata=metadata or {},
        )


# =============================================================================
# LIFECYCLE HISTORY - Complete transition history
# =============================================================================


@dataclass(frozen=True)
class LifecycleHistory:
    """
    Complete history of lifecycle transitions for a modality.
    
    Fields:
        transitions:        Tuple of all lifecycle transitions
        
        current_state:      Current lifecycle state
        
        created_at_utc:     When the first transition occurred
        
        terminated_at_utc:  When terminated (if applicable)
        
        revision:           History version number
    """
    
    # Core identity (required)
    transitions: Tuple[LifecycleTransition, ...] = field(default_factory=tuple)
    
    current_state: str = "discovered"
    
    created_at_utc: float = field(default_factory=time.time)
    
    terminated_at_utc: Optional[float] = None
    
    revision: int = 1
    
    @property
    def is_active(self) -> bool:
        """Check if the modality is currently active."""
        return self.current_state in ("active", "degraded", "sandboxed")
    
    @property
    def is_terminated(self) -> bool:
        """Check if the lifecycle has ended."""
        return self.current_state == "terminated"
    
    def get_transitions_since(
        self,
        state: str,
    ) -> Tuple[LifecycleTransition, ...]:
        """
        Get all transitions since reaching a particular state.
        
        Args:
            state: State to find
            
        Returns:
            Tuple of transitions after first entering that state
        """
        found = False
        result = []
        for transition in self.transitions:
            if not found and transition.to_state == state:
                found = True
            elif found:
                result.append(transition)
        return tuple(result)
    
    def get_history_snapshot(self) -> Dict[str, Any]:
        """
        Get a snapshot of the lifecycle history.
        
        Returns:
            Dictionary with summary information
        """
        state_counts: Dict[str, int] = {}
        for transition in self.transitions:
            state_counts[transition.to_state] = state_counts.get(transition.to_state, 0) + 1
        
        return {
            "current_state": self.current_state,
            "is_active": self.is_active,
            "is_terminated": self.is_terminated,
            "total_transitions": len(self.transitions),
            "state_breakdown": state_counts,
            "duration_seconds": time.time() - self.created_at_utc if not self.is_terminated else (self.terminated_at_utc or 0) - self.created_at_utc,
        }


# =============================================================================
# LIFECYCLE MANAGER - Interface for lifecycle management
# =============================================================================


class LifecycleManager:
    """
    Interface for managing modality lifecycle transitions.
    
    Implementations handle:
        - State validation and transition rules
        - Event logging
        - State persistence
        - Cleanup on termination
    """
    
    def transition_to(
        self,
        current_state: str,
        target_state: str,
        event: Optional[str] = None,
    ) -> Tuple[bool, Optional[LifecycleTransition]]:
        """
        Attempt to transition from current state to target state.
        
        Args:
            current_state: Current lifecycle state
            target_state: Desired state
            event: Event triggering the transition
            
        Returns:
            Tuple of (success, transition if successful)
        """
        raise NotImplementedError
    
    def get_valid_transitions(
        self,
        state: str,
    ) -> Tuple[str, ...]:
        """
        Get states that can be reached from the given state.
        
        Args:
            state: Current lifecycle state
            
        Returns:
            Tuple of valid target states
        """
        raise NotImplementedError


# =============================================================================
# EXPORTS
# =============================================================================

__all__: list[str] = [
    # Enums
    "LifecycleState",
    "LifecycleEvent",
    
    # Dataclasses
    "LifecycleTransition",
    "LifecycleHistory",
    
    # Classes
    "LifecycleManager",
]