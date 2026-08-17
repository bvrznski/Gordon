# Gordon Phase 5.7.4-I: Temporal Context Engine - Diagnostics
# ===============================================================================
"""
Diagnostics module for temporal context observability.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class TemporalDiagnosticsSnapshot:
    """
    Immutable snapshot of temporal context diagnostics and metrics.
    
    Provides passive observability into the Temporal Context Engine without
    exposing sensitive context content. Used for monitoring and debugging.
    """
    
    timestamp_utc: float = field(default_factory=time.time)
    """When this diagnostic snapshot was captured."""
    
    # Window state
    active_window_id: Optional[str] = None
    """ID of currently active continuity window (if any)."""
    
    # Generational metrics
    current_generation: int = 0
    """Current generation number."""
    
    last_transition_generation: Optional[int] = None
    """Generation at time of last transition."""
    
    # Counters
    retention_count: int = 0
    """Number of active retention references."""
    
    protention_count: int = 0
    """Number of active protentional expectations."""
    
    continuity_window_size: int = 0
    """Current size of the continuity window."""
    
    transition_count: int = 0
    """Total transitions processed since initialization."""
    
    interruption_count: int = 0
    """Transitions caused by interruptions."""
    
    resumption_count: int = 0
    """Transitions from paused to active state."""
    
    rollback_count: int = 0
    """Rollback transitions."""
    
    # Timing metrics
    average_transition_latency_ms: float = 0.0
    """Average time in milliseconds between transition request and commit."""
    
    last_transition_timestamp_utc: Optional[float] = None
    """When the last transition occurred."""
    
    # Status flags
    has_pending_transition: bool = False
    """Whether a transition is currently pending."""
    
    continuity_integrity_status: str = "healthy"
    """Overall integrity status (healthy, degraded, critical)."""
    
    # Boundary enforcement
    retention_overflow_count: int = 0
    """Times retention bounds were exceeded."""
    
    protention_overflow_count: int = 0
    """Times protention bounds were exceeded."""
    
    invalid_transition_count: int = 0
    """Rejected transitions due to validation failures."""


__all__: Tuple[str, ...] = (
    "TemporalDiagnosticsSnapshot",
)