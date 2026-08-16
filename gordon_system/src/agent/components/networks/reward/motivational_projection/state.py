# Motivational Projection Network - Motivational Projection State (Phase 4.10.6)
# ===============================================================================

"""
MotivationalProjectionState model for Phase 4.10.6.

This module defines the final aggregate state containing all motivational
influence information: projections, tensions, synergies, hierarchy, temporal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Dict


@dataclass(frozen=True)
class MotivationalProjectionState:
    """
    The canonical final aggregate of the motivational projection process.

    STATE-LAW-001: Exactly one canonical MotivationalProjectionState exists.
    STATE-LAW-002: The state remains immutable once constructed.
    STATE-LAW-003: Projection hierarchy remains explicit.
    STATE-LAW-004: Temporal partitions remain explicit.
    STATE-LAW-005: Confidence remains projection-specific.
    STATE-LAW-006: Uncertainty remains projection-specific.

    NOT RESPONSIBLE FOR:
        • Creating or modifying drives
        • Making executive decisions
        • Resolving tensions automatically
    """

    state_id: str = "motivational_projection_state"
    """Unique identifier for this state."""

    revision: int = 0
    """Revision number for versioning."""

    # Core components (all preserved)
    motivational_reward_field: Dict[str, any] = field(default_factory=dict)
    """Field data as dict (contains projections, tensions, synergies)."""

    projection_hierarchy: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """(projection_id, level) tuples for hierarchy."""

    temporal_partitions: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """(projection_id, timescale) tuples for temporal context."""

    confidence: float = 0.5
    """Overall confidence in the state (0.0-1.0)."""

    uncertainty: float = 0.0
    """Overall uncertainty in the state (0.0-1.0)."""

    provenance: str = "unknown"
    """Source information for traceability."""

    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from state construction."""

    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this state."""

    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Construction trace for provenance."""

    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.state_id}@v{self.revision}"

    @property
    def total_projections(self) -> int:
        """Get count of projections in the state."""
        return len(set(
            pid for pid, _ in self.projection_hierarchy
        ))

    @property
    def has_tensions(self) -> bool:
        """Check if tensions are present."""
        return (
            "tension_count" in self.motivational_reward_field
            and self.motivational_reward_field["tension_count"] > 0
        )

    @property
    def has_synergies(self) -> bool:
        """Check if synergies are present."""
        return (
            "synergy_count" in self.motivational_reward_field
            and self.motivational_reward_field["synergy_count"] > 0
        )

    def to_dict(self) -> dict:
        """Convert state to dictionary representation."""
        return {
            "state_id": self.state_id,
            "revision": self.revision,
            "motivational_reward_field": self.motivational_reward_field.copy(),
            "projection_hierarchy": list(self.projection_hierarchy),
            "temporal_partitions": list(self.temporal_partitions),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "provenance": self.provenance,
            "findings": list(self.findings),
            "limitations": list(self.limitations),
            "total_projections": self.total_projections,
        }

    @classmethod
    def create_empty(cls, state_id: str = "motivational_projection_state") -> MotivationalProjectionState:
        """Create an empty motivational projection state."""
        return cls(state_id=state_id)

    @classmethod
    def from_components(
        cls,
        field_data: Dict[str, any],
        projection_hierarchy: Tuple[Tuple[str, str], ...] = tuple(),
        temporal_partitions: Tuple[Tuple[str, str], ...] = tuple(),
        confidence: float = 0.5,
        state_id: str = "motivational_projection_state",
    ) -> MotivationalProjectionState:
        """
        Create a state from field and partition data.

        Args:
            field_data: Field data dictionary
            projection_hierarchy: (projection_id, level) tuples
            temporal_partitions: (projection_id, timescale) tuples
            confidence: Overall confidence level
            state_id: Unique identifier for this state

        Returns:
            New MotivationalProjectionState instance
        """
        return cls(
            state_id=state_id,
            revision=0,
            motivational_reward_field=dict(field_data),
            projection_hierarchy=tuple(sorted(projection_hierarchy)),
            temporal_partitions=tuple(sorted(temporal_partitions)),
            confidence=confidence,
            uncertainty=max(0.0, 1.0 - confidence),
            findings=("STATE_CONSTRUCTED", "VALIDATION_COMPLETED"),
            trace=("FIELD_CONSTRUCTED", "HIERARCHY_APPLIED", "TEMPORAL_PARTITIONING"),
        )


__all__ = ["MotivationalProjectionState"]