# Gordon Phase 5.7.8-I: Conscious Integration - Health Aggregation
# ===============================================================================

"""
Composite health aggregation for the integration layer.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional


@dataclass(frozen=True)
class EngineHealth:
    """Health status of a single engine."""

    engine_id: str
    state: str = "unknown"
    ready: bool = False
    active: bool = False

    # Error information
    last_error: Optional[str] = None
    last_error_timestamp: Optional[float] = None


@dataclass(frozen=True)
class CompositeHealthSnapshot:
    """
    Bounded health snapshot for composite context.
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

    # Engine health summary
    required_engines_ready: Tuple[str, ...] = field(default_factory=tuple)
    """Required engines that are ready."""

    optional_engines_available: Tuple[str, ...] = field(default_factory=tuple)
    """Optional engines that are available."""

    all_engines_ready: bool = False
    """Whether all registered engines are ready."""

    # Composite state
    state: str = "unknown"
    """Overall composite health state."""

    initialized: bool = False
    """Whether capability is initialized."""

    ready: bool = False
    """Whether capability is ready for operations."""

    active: bool = False
    """Whether capability is actively processing."""

    # Degradation info
    degradation_modes: Tuple[str, ...] = field(default_factory=tuple)
    """Current degradation modes."""

    last_failure_category: Optional[str] = None
    """Category of last failure (if any)."""

    @classmethod
    def from_engine_health(
        cls,
        engine_healths: Dict[str, EngineHealth],
        context_id: str = None,
        generation: int = 0,
    ) -> "CompositeHealthSnapshot":
        """
        Create a composite health snapshot from individual engine health.

        Args:
            engine_healths: Map of engine_id -> EngineHealth
            context_id: Context ID (optional)
            generation: Generation number (optional)

        Returns:
            Aggregated CompositeHealthSnapshot
        """
        required = ("experiential_field", "presence", "perspective")
        optional = (
            "intentional_context",
            "temporal_context",
            "awareness",
            "situated_world",
        )

        required_ready = tuple(
            eid for eid in required if engine_healths.get(eid, EngineHealth(engine_id=eid)).ready
        )
        optional_available = tuple(
            eid for eid in optional if engine_healths.get(eid, EngineHealth(engine_id=eid)).state != "unknown"
        )

        all_ready = all(
            engine_healths.get(eid, EngineHealth(engine_id=eid)).ready
            for eid in required
        )
        all_registered_ready = all(
            engine_healths.get(eid, EngineHealth(engine_id=eid)).ready
            for eid in engine_healths.keys()
        )

        # Determine state based on engine health and degradation modes
        if not all_ready:
            state = "degraded"
        elif all_registered_ready and len(required_ready) == len(required):
            state = "active"
        else:
            state = "ready"

        return cls(
            context_id=context_id,
            generation=generation,
            required_engines_ready=tuple(set(engine_healths.keys()) & set(required)),
            optional_engines_available=optional_available,
            all_engines_ready=all_registered_ready,
            state=state,
            initialized=True,
            ready=state in ("ready", "active"),
            active=state == "active",
        )


class CompositeHealthAggregator:
    """
    Aggregates health from individual engines into composite health.
    """

    def __init__(self):
        """Initialize the aggregator."""
        self._engine_health: Dict[str, EngineHealth] = {}
        self._last_update_time = time.time()

    @property
    def last_update_seconds(self) -> float:
        """Get seconds since last update."""
        return time.time() - self._last_update_time

    def update_engine_health(
        self, engine_id: str, state: str, ready: bool, active: bool
    ) -> None:
        """
        Update health for a single engine.

        Args:
            engine_id: Engine identifier
            state: Engine state (ready, active, degraded, failed)
            ready: Whether the engine is ready
            active: Whether the engine is active
        """
        self._engine_health[engine_id] = EngineHealth(
            engine_id=engine_id,
            state=state,
            ready=ready,
            active=active,
        )
        self._last_update_time = time.time()

    def remove_engine(self, engine_id: str) -> None:
        """Remove an engine from health tracking."""
        if engine_id in self._engine_health:
            del self._engine_health[engine_id]

    def get_composite_health(
        self,
        context_id: Optional[str] = None,
        generation: int = 0,
    ) -> CompositeHealthSnapshot:
        """
        Get the current composite health snapshot.

        Args:
            context_id: Context ID (optional)
            generation: Generation number (optional)

        Returns:
            Composite health snapshot
        """
        return CompositeHealthSnapshot.from_engine_health(
            engine_healths=self._engine_health,
            context_id=context_id,
            generation=generation,
        )

    def reset(self) -> None:
        """Reset the aggregator state."""
        self._engine_health.clear()
        self._last_update_time = time.time()


def compute_composite_health_state(
    required_engines_ready: int,
    optional_engines_available: int,
    total_required: int,
    degradation_modes: Tuple[str, ...] = (),
) -> str:
    """
    Compute the composite health state.

    Args:
        required_engines_ready: Number of ready required engines
        optional_engines_available: Number of available optional engines
        total_required: Total number of required engines
        degradation_modes: Current degradation modes

    Returns:
        Health state string
    """
    if len(degradation_modes) > 0:
        return "degraded"

    if required_engines_ready == total_required:
        if optional_engines_available >= total_required - 2:
            return "active"
        else:
            return "ready"

    if required_engines_ready > 0:
        return "degraded"

    return "unhealthy"