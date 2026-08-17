# Gordon Phase 5.7.6-I: Perspective Engine - Diagnostics
# ===============================================================================
"""
Diagnostics and observability for the Perspective Engine.

Exposes passive metrics about perspective state changes, observer activity,
and transformation patterns while maintaining privacy-aware practices.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional


@dataclass
class Diagnostics:
    """
    Passive diagnostics for perspective observability.
    
    Collects metrics about perspective operations without exposing
    sensitive context content. Provides operational insights for monitoring
    and debugging while respecting privacy boundaries.
    """
    
    # Operational counters
    _transitions_count: int = 0
    """Total perspective transitions."""
    
    _transformations_count: int = 0
    """Total viewpoint transformations."""
    
    _snapshots_published: int = 0
    """Number of snapshots published."""
    
    _invalid_transitions: int = 0
    """Transitions rejected due to conflicts or invalid state."""
    
    # Timing metrics
    _last_transition_time: float = 0.0
    """Time of last transition (for latency calculation)."""
    
    _total_transition_latency_ms: float = 0.0
    """Total time spent in transitions."""
    
    # Perspective type tracking
    _perspective_type_counts: Dict[str, int] = field(default_factory=dict)
    """Counts by perspective type."""
    
    # Observer metrics
    _observer_changes: int = 0
    """Number of observer state changes."""
    
    _active_observer_id: Optional[str] = None
    """Current active observer ID (for tracking)."""
    
    def __post_init__(self) -> None:
        """Initialize after construction."""
        self._perspective_type_counts.clear()
    
    @property
    def transitions_count(self) -> int:
        """Get total perspective transitions."""
        return self._transitions_count
    
    @property
    def transformations_count(self) -> int:
        """Get total viewpoint transformations."""
        return self._transformations_count
    
    @property
    def snapshots_published(self) -> int:
        """Get number of snapshots published."""
        return self._snapshots_published
    
    @property
    def invalid_transitions(self) -> int:
        """Get count of rejected transitions."""
        return self._invalid_transitions
    
    # ==========================================================================
    # RECORDING METHODS
    # ==========================================================================
    
    def record_transition(self, latency_ms: float = 0.0) -> None:
        """
        Record a perspective transition.
        
        Args:
            latency_ms: Transition duration in milliseconds
        """
        self._transitions_count += 1
        self._last_transition_time = 0.0  # Will be set by caller if needed
        self._total_transition_latency_ms += latency_ms
    
    def record_transformation(self) -> None:
        """Record a viewpoint transformation."""
        self._transformations_count += 1
    
    def record_snapshot_publication(self) -> None:
        """Record a snapshot publication."""
        self._snapshots_published += 1
    
    def record_invalid_transition(self, reason: str = "") -> None:
        """
        Record an invalid transition attempt.
        
        Args:
            reason: Reason for rejection (for metrics)
        """
        self._invalid_transitions += 1
        # Reason not stored to preserve privacy
    
    def record_perspective_type_change(self, new_type: str) -> None:
        """
        Record a perspective type change.
        
        Args:
            new_type: New perspective type
        """
        if new_type in self._perspective_type_counts:
            self._perspective_type_counts[new_type] += 1
        else:
            self._perspective_type_counts[new_type] = 1
    
    def record_observer_change(self, observer_id: str) -> None:
        """
        Record an observer state change.
        
        Args:
            observer_id: Observer that changed
        """
        self._observer_changes += 1
        self._active_observer_id = observer_id
    
    # ==========================================================================
    # METRICS PROPERTIES
    # ==========================================================================
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get all diagnostic metrics."""
        avg_latency = 0.0
        if self._transitions_count > 0:
            avg_latency = self._total_transition_latency_ms / self._transitions_count
        
        return {
            "transitions_total": self._transitions_count,
            "transformations_total": self._transformations_count,
            "snapshots_published": self._snapshots_published,
            "invalid_transitions": self._invalid_transitions,
            "average_transition_latency_ms": avg_latency,
            "observer_changes": self._observer_changes,
            "perspective_type_breakdown": dict(self._perspective_type_counts),
        }
    
    @property
    def health(self) -> Dict[str, bool]:
        """Get diagnostic health status."""
        return {
            "can_record": True,
            "can_report": True,
            "no_capacity_issues": self._transitions_count < 1000000,
        }
    
    # ==========================================================================
    # RESET METHODS
    # ==========================================================================
    
    def reset_metrics(self) -> None:
        """Reset all metrics to zero."""
        self._transitions_count = 0
        self._transformations_count = 0
        self._snapshots_published = 0
        self._invalid_transitions = 0
        self._total_transition_latency_ms = 0.0
        self._perspective_type_counts.clear()
        self._observer_changes = 0
        self._active_observer_id = None
    
    @classmethod
    def default(cls) -> "Diagnostics":
        """Return a diagnostics instance with default settings."""
        return cls()


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "Diagnostics",
)