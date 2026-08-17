# Gordon Phase 5.7.4-I: Temporal Context Engine - Constants
# ===============================================================================
"""
Constants and enumerations for the Temporal Context Engine.
"""

from __future__ import annotations

from enum import Enum
from typing import Tuple


class ContinuityState(str, Enum):
    """
    State of temporal continuity within a generation window.
    
    These states represent the lifecycle of a temporal continuity window,
    from active through to closure or degradation.
    """
    ACTIVE = "active"
    """Window is active and accepting transitions."""
    
    PAUSED = "paused"
    """Window is temporarily paused, transitions suspended."""
    
    CLOSED = "closed"
    """Window has been closed, no further transitions accepted."""
    
    DEGRADED = "degraded"
    """Window is degraded due to continuity failures."""
    
    INVALID = "invalid"
    """Window state is corrupted or invalid."""


class TransitionKind(str, Enum):
    """
    Kinds of temporal transitions.
    
    Transitions represent immutable changes to the temporal context
    from one generation to the next.
    """
    DEFAULT = "default"
    """Standard transition with no special semantics."""
    
    RESUME = "resume"
    """Resume from paused state, preserving continuity."""
    
    RESET = "reset"
    """Reset continuity window (e.g., new session)."""
    
    INTERRUPTION = "interruption"
    """Transition caused by external interruption."""
    
    DEGRADATION = "degradation"
    """Transition due to degradation event."""
    
    REPLAY = "replay"
    """Replay transition for testing or recovery."""
    
    ROLLBACK = "rollback"
    """Rollback to previous generation on failure."""
    
    SNAPSHOT_PUBLISH = "snapshot_publish"
    """Publish a new temporal snapshot."""


# =============================================================================
# BOUNDED CONSTANTS
# =============================================================================

MAX_RETENTION_HISTORY: int = 10
"""Maximum number of retained generations in history window."""

MAX_PROTENTION_EXPECTATIONS: int = 5
"""Maximum number of protentional expectations to track."""

MAX_CONTINUITY_WINDOW_SIZE: int = 20
"""Maximum size of continuity window (history + current + future)."""

DEFAULT_TRUST_LEVEL: float = 1.0
"""Default trust level for newly created temporal elements."""

DEFAULT_PRIVACY_CLASSIFICATION: str = "internal"
"""Default privacy classification for temporal context."""


# =============================================================================
# TIMESTAMP CONSTANTS - Injected via time_provider parameter
# =============================================================================

DEFAULT_RETENTION_TTL_SECONDS: float = 3600.0
"""Time-to-live for retention records (1 hour)."""

DEFAULT_PROTENTION_TTL_SECONDS: float = 60.0
"""Time-to-live for protentional expectations (1 minute)."""


__all__: Tuple[str, ...] = (
    "ContinuityState",
    "TransitionKind",
    "MAX_RETENTION_HISTORY",
    "MAX_PROTENTION_EXPECTATIONS",
    "MAX_CONTINUITY_WINDOW_SIZE",
    "DEFAULT_TRUST_LEVEL",
    "DEFAULT_PRIVACY_CLASSIFICATION",
    "DEFAULT_RETENTION_TTL_SECONDS",
    "DEFAULT_PROTENTION_TTL_SECONDS",
)