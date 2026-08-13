# Stream Degraded Operation - Phase 3.11.7
# =========================================

"""
Degraded operation infrastructure for Gordon's Semantic Stream subsystem.

This module implements:
    
    Degraded Modes:
        - Read-only: Accept no new publications, allow read operations
        - Publication paused: Temporarily suspend publication capability
        - Delivery paused: Suspend delivery but maintain subscription state
        - Replay only: Only replay historical records (no live operation)
        - Diagnostics only: Diagnostic mode for debugging
    
    Constraints:
        - Transitions must be lifecycle-aware
        - Degraded mode is bounded in duration
        - All operations remain observable
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import time


# =============================================================================
# DEGRADED MODES (Canonical)
# =============================================================================

class DegradedMode(Enum):
    """
    Canonical degraded operation modes for streams.
    
    Modes:
        READ_ONLY: No new publications allowed, read-only access
        PUBLICATION_PAUSED: Publication suspended but delivery active
        DELIVERY_PAUSED: Delivery suspended but publication active  
        REPLAY_ONLY: Replay only, no live operations
        DIAGNOSTICS_ONLY: Diagnostic mode for debugging
    """
    
    READ_ONLY = "read_only"
    """Accept no new publications, allow read operations."""
    
    PUBLICATION_PAUSED = "publication_paused"
    """Publication suspended but delivery active."""
    
    DELIVERY_PAUSED = "delivery_paused"
    """Delivery suspended but publication active."""
    
    REPLAY_ONLY = "replay_only"
    """Replay only, no live operations."""
    
    DIAGNOSTICS_ONLY = "diagnostics_only"
    """Diagnostic mode for debugging."""
    
    MAINTENANCE_MODE = "maintenance_mode"
    """Full maintenance - no operations except recovery."""


# =============================================================================
# DEGRADED OPERATION CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class DegradedOperationConfig:
    """
    Configuration for degraded operation.
    """
    
    mode: DegradedMode = DegradedMode.READ_ONLY
    
    # Timing bounds
    max_duration_seconds: float = 300.0  # Default 5 minutes
    allow_extension: bool = False
    
    # Capability restrictions
    allow_publication: bool = False
    allow_delivery: bool = True
    allow_replay: bool = True
    allow_checkpointing: bool = True
    
    # Retry configuration during degradation
    max_retry_attempts: int = 1
    retry_delay_seconds: float = 5.0
    
    created_at_utc: float = field(default_factory=time.time)


# =============================================================================
# DEGRADED OPERATION STATE
# =============================================================================

class DegradedOperationState(Enum):
    """
    State of degraded operation.
    """
    
    NOT_DEGRADED = "not_degraded"
    """Stream operating normally."""
    
    ENTERING_DEGRADED = "entering_degraded"
    """Transitioning to degraded state."""
    
    DEGRADED_ACTIVE = "degraded_active"
    """Currently in degraded mode."""
    
    EXITING_DEGRADED = "exiting_degraded"
    """Transitioning out of degraded state."""
    
    GRACEFUL_EXIT_COMPLETE = "graceful_exit_complete"
    """Successfully exited degraded state."""


@dataclass(frozen=True)
class DegradedOperationStateSnapshot:
    """
    Snapshot of degraded operation state.
    """
    
    stream_id: str
    generation_id: int
    
    mode: DegradedMode
    state: DegradedOperationState = DegradedOperationState.NOT_DEGRADED
    
    entered_at_utc: Optional[float] = None
    scheduled_exit_at_utc: Optional[float] = None
    
    reason: str = "auto"
    
    # Metrics during degradation
    records_dropped: int = 0
    delivery_failures: int = 0


# =============================================================================
# DEGRADED MODE PLANNER
# =============================================================================

class DegradedModePlanner:
    """
    Planner for degraded operation transitions.
    
    Determines appropriate degraded mode based on failure context
    and system constraints.
    """
    
    def __init__(
        self,
        max_degradation_duration: float = 300.0,
        allow_transitions: bool = True,
    ):
        """
        Initialize degraded mode planner.
        
        Args:
            max_degradation_duration: Maximum allowed degradation duration
            allow_transitions: Allow state transitions?
        """
        self._max_duration = max_degradation_duration
        self._allow_transitions = allow_transitions
    
    def plan_degraded_mode(
        self,
        stream_id: str,
        failure_category: Any,  # StreamFailureCategory reference
        current_state: DegradedOperationStateSnapshot,
    ) -> Tuple[DegradedMode, str]:
        """
        Plan appropriate degraded mode for a failure.
        
        Args:
            stream_id: Stream identifier
            failure_category: Category of failure causing degradation
            current_state: Current degradation state
            
        Returns:
            (mode, reason) tuple
        """
        # Map failure categories to degraded modes
        mode_mapping = {
            "publication_failure": DegradedMode.READ_ONLY,
            "delivery_failure": DegradedMode.PUBLICATION_PAUSED,
            "subscriber_failure": DegradedMode.DELIVERY_PAUSED,
            "cursor_corruption": DegradedMode.REPLAY_ONLY,
            "checkpoint_corruption": DegradedMode.READ_ONLY,
            "replay_failure": DegradedMode.READ_ONLY,
            "integrity_failure": DegradedMode.READ_ONLY,
            "storage_failure": DegradedMode.MAINTENANCE_MODE,
            "authorization_failure": DegradedMode.DIAGNOSTICS_ONLY,
            "capacity_exhaustion": DegradedMode.READ_ONLY,
        }
        
        # Get appropriate mode based on failure
        category_value = (
            failure_category.value if hasattr(failure_category, 'value') 
            else str(failure_category)
        )
        
        mode = mode_mapping.get(category_value, DegradedMode.READ_ONLY)
        
        reason = f"Entering {mode.value} mode due to {category_value}"
        
        return mode, reason
    
    def can_enter_degraded(
        self,
        current_state: DegradedOperationStateSnapshot,
    ) -> Tuple[bool, str]:
        """
        Check if stream can enter degraded operation.
        
        Returns:
            (can_enter, reason) tuple
        """
        if not self._allow_transitions:
            return False, "Transitions disabled by configuration"
        
        # Check if already in degraded state
        if current_state.state != DegradedOperationState.NOT_DEGRADED:
            return False, f"Already in {current_state.state.value} state"
        
        # Check degradation duration bounds
        if current_state.mode and hasattr(current_state, 'max_duration_seconds'):
            now = time.time()
            entry_time = current_state.entered_at_utc or 0
            elapsed = now - entry_time
            
            if elapsed > self._max_duration:
                return False, f"Degradation duration exceeded: {elapsed}s > {self._max_duration}s"
        
        return True, "Can enter degraded state"


# =============================================================================
# DEGRADED OPERATION OBSERVABILITY EVENTS
# =============================================================================

class DegradedOperationEvent(Enum):
    """
    Observability events related to degraded operation.
    """
    
    ENTERED_DEGRADED = "entered_degraded"
    """Stream entered degraded operation mode."""
    
    EXITED_DEGRADED = "exited_degraded"
    """Stream exited degraded operation mode."""
    
    DEGRADED_MODE_CHANGED = "degraded_mode_changed"
    """Degraded mode changed within degradation session."""
    
    DEGRADED_DURATION_WARNING = "degraded_duration_warning"
    """Approaching maximum degradation duration."""
    
    DEGRADED_DURATION_EXCEEDED = "degraded_duration_exceeded"
    """Maximum degradation duration exceeded."""


@dataclass(frozen=True)
class DegradedOperationEventRecord:
    """
    Record of a degraded operation event.
    """
    
    event_id: str
    event_type: DegradedOperationEvent
    
    stream_id: str
    generation_id: int
    
    timestamp_utc: float = field(default_factory=time.time)
    
    current_mode: Optional[DegradedMode] = None
    new_mode: Optional[DegradedMode] = None
    
    reason: str = ""
    
    # Metrics
    duration_seconds: float = 0.0
    records_dropped: int = 0


__all__ = [
    "DegradedMode",
    "DegradedOperationConfig",
    "DegradedOperationState",
    "DegradedOperationStateSnapshot",
    "DegradedModePlanner",
    "DegradedOperationEvent",
    "DegradedOperationEventRecord",
]