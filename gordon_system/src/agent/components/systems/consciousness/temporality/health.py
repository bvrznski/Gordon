# Gordon Phase 5.7.4-I: Temporal Context Engine - Health
# ===============================================================================
"""
Health module for temporal context state monitoring.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class TemporalHealthSnapshot:
    """
    Immutable snapshot of temporal context health and readiness.
    
    Provides a bounded health view without exposing context content. Used for
    runtime state monitoring and integration coordination.
    """
    
    timestamp_utc: float = field(default_factory=time.time)
    """When this health snapshot was captured."""
    
    # State indicators
    is_initialized: bool = False
    """Whether the engine has been initialized."""
    
    is_ready: bool = False
    """Whether the engine is ready to accept transitions."""
    
    is_active: bool = False
    """Whether the engine is currently processing transitions."""
    
    # Window health
    continuity_window_state: str = "unknown"
    """State of the current continuity window (active, paused, closed, degraded)."""
    
    # Status flags
    has_pending_transition: bool = False
    """Whether a transition is pending commit."""
    
    integrity_status: str = "healthy"
    """Overall integrity status (healthy, degraded, critical)."""
    
    # Last known state
    last_generation: int = 0
    """Last committed generation number."""
    
    last_valid_snapshot_id: Optional[str] = None
    """ID of the last successfully published snapshot."""
    
    # Timing
    initialized_at_utc: Optional[float] = None
    """When initialization occurred."""
    
    last_health_check_utc: float = field(default_factory=time.time)
    """When this health check was performed."""


__all__: Tuple[str, ...] = (
    "TemporalHealthSnapshot",
)