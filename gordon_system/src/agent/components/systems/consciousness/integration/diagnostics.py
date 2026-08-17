# Gordon Phase 5.7.8-I: Conscious Integration - Diagnostics Aggregation
# ===============================================================================

"""
Composite diagnostics aggregation for the integration layer.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional


@dataclass(frozen=True)
class CompositeDiagnosticsSnapshot:
    """
    Bounded diagnostics snapshot for composite context.

    Provides operational insights without exposing private context content.
    """

    # Identity
    capability_id: str = "consciousness-001"
    """Consciousness capability identity."""

    context_id: Optional[str] = None
    """Current context ID (if available)."""

    generation: int = 0
    """Current composite generation."""

    age_seconds: float = field(default_factory=lambda: time.time())
    """How long since last update."""

    # Transition history
    last_transition_id: Optional[str] = None
    """Last transition that completed."""

    last_transition_duration_seconds: float = 0.0
    """Duration of last transition."""

    last_transition_status: str = "completed"
    """Status of last transition."""

    pending_operations_count: int = 0
    """Number of pending operations."""

    # Engine statistics
    registered_engine_count: int = 0
    """Total engines registered."""

    ready_engine_count: int = 0
    """Engines currently ready."""

    active_engine_count: int = 0
    """Engines actively processing."""

    # Validation metrics
    unresolved_reference_count: int = 0
    """Number of unresolved references."""

    cross_engine_violation_count: int = 0
    """Count of invariant violations detected."""

    # Classification summaries
    degradation_state: Tuple[str, ...] = field(default_factory=tuple)
    """Current degradation modes."""

    privacy_summary: str = "internal"
    """Privacy classification of current context."""

    trust_summary: str = "medium"
    """Trust classification of current context."""

    # Lifecycle state
    lifecycle_state: str = "active"
    """Lifecycle state of Consciousness capability."""


class CompositeDiagnosticsBuilder:
    """
    Builder for composite diagnostics snapshots.
    """

    def __init__(self):
        """Initialize the builder."""
        self._engine_count = 0
        self._ready_engine_count = 0
        self._active_engine_count = 0
        self._unresolved_refs = 0
        self._violation_count = 0
        self._degradation_modes: list[str] = []
        self._lifecycle_state = "active"

    def add_engine(self, ready: bool, active: bool) -> None:
        """Add an engine's diagnostic state."""
        self._engine_count += 1
        if ready:
            self._ready_engine_count += 1
        if active:
            self._active_engine_count += 1

    def record_unresolved_reference(self) -> None:
        """Record an unresolved reference."""
        self._unresolved_refs += 1

    def record_violation(self) -> None:
        """Record a cross-engine invariant violation."""
        self._violation_count += 1

    def add_degradation_mode(self, mode: str) -> None:
        """Add a degradation mode."""
        if mode not in self._degradation_modes:
            self._degradation_modes.append(mode)

    def set_lifecycle_state(self, state: str) -> None:
        """Set the lifecycle state."""
        self._lifecycle_state = state

    def build(
        self,
        context_id: Optional[str] = None,
        generation: int = 0,
        last_transition: Optional[Dict] = None,
    ) -> CompositeDiagnosticsSnapshot:
        """
        Build a diagnostics snapshot.

        Args:
            context_id: Context ID (optional)
            generation: Generation number
            last_transition: Last transition info (optional)

        Returns:
            Diagnostics snapshot
        """
        return CompositeDiagnosticsSnapshot(
            context_id=context_id,
            generation=generation,
            age_seconds=time.time(),
            last_transition_id=last_transition.get("transition_id") if last_transition else None,
            last_transition_duration_seconds=last_transition.get("duration_seconds", 0) if last_transition else 0,
            last_transition_status=last_transition.get("status", "completed") if last_transition else "completed",
            pending_operations_count=0,
            registered_engine_count=self._engine_count,
            ready_engine_count=self._ready_engine_count,
            active_engine_count=self._active_engine_count,
            unresolved_reference_count=self._unresolved_refs,
            cross_engine_violation_count=self._violation_count,
            degradation_state=tuple(self._degradation_modes),
            privacy_summary="internal",
            trust_summary="medium",
            lifecycle_state=self._lifecycle_state,
        )

    def reset(self) -> None:
        """Reset the builder state."""
        self._engine_count = 0
        self._ready_engine_count = 0
        self._active_engine_count = 0
        self._unresolved_refs = 0
        self._violation_count = 0
        self._degradation_modes.clear()