# Motivational Projection Network - Motivational Reward Field (Phase 4.10.6)
# ==========================================================================

"""
MotivationalRewardField model for Phase 4.10.6.

This module defines the aggregate field containing all projections,
tensions, synergies, and their relationships in motivational space.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class MotivationalRewardField:
    """
    The canonical aggregate of all motivational influences.

    FIELD-LAW-001: Exactly one MotivationalRewardField exists per evaluation.
    FIELD-LAW-002: The field remains immutable once constructed.
    FIELD-LAW-003: All projections are preserved.
    FIELD-LAW-004: Tensions and synergies remain explicit.
    
    NOT RESPONSIBLE FOR:
        • Creating or modifying drives
        • Resolving tensions automatically
        • Making executive decisions
    """
    
    field_id: str = "motivational_reward_field"
    """Unique identifier for this field."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Core components (all preserved)
    drive_projections: Tuple[str, ...] = field(default_factory=tuple)
    """Projection IDs in the field."""
    
    tensions: Tuple[str, ...] = field(default_factory=tuple)
    """Tension IDs present in the field."""
    
    synergies: Tuple[str, ...] = field(default_factory=tuple)
    """Synergy IDs present in the field."""
    
    # Metadata
    confidence: float = 0.5
    """Overall confidence in the field (0.0-1.0)."""
    
    uncertainty: float = 0.0
    """Overall uncertainty in the field (0.0-1.0)."""
    
    provenance: str = "unknown"
    """Source information for traceability."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from field construction."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this field."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Construction trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.field_id}@v{self.revision}"
    
    @property
    def total_projections(self) -> int:
        """Get count of projections in the field."""
        return len(self.drive_projections)
    
    @property
    def has_tensions(self) -> bool:
        """Check if tensions are present."""
        return len(self.tensions) > 0
    
    @property
    def has_synergies(self) -> bool:
        """Check if synergies are present."""
        return len(self.synergies) > 0
    
    def to_dict(self) -> dict:
        """Convert field to dictionary representation."""
        return {
            "field_id": self.field_id,
            "revision": self.revision,
            "projection_count": self.total_projections,
            "tension_count": len(self.tensions),
            "synergy_count": len(self.synergies),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "provenance": self.provenance,
            "findings": list(self.findings),
            "limitations": list(self.limitations),
        }
    
    @classmethod
    def create_empty(cls, field_id: str = "motivational_reward_field") -> MotivationalRewardField:
        """Create an empty motivational reward field."""
        return cls(field_id=field_id)
    
    @classmethod
    def from_components(
        cls,
        projection_ids: Tuple[str, ...],
        tension_ids: Tuple[str, ...] = tuple(),
        synergy_ids: Tuple[str, ...] = tuple(),
        confidence: float = 0.5,
        field_id: str = "motivational_reward_field",
    ) -> MotivationalRewardField:
        """
        Create a field from projection, tension, and synergy IDs.
        
        Args:
            projection_ids: All projection IDs in the field
            tension_ids: Tension IDs present
            synergy_ids: Synergy IDs present
            confidence: Overall confidence level
            field_id: Unique identifier for this field
        """
        return cls(
            field_id=field_id,
            revision=0,
            drive_projections=tuple(sorted(set(projection_ids))),
            tensions=tuple(sorted(set(tension_ids))),
            synergies=tuple(sorted(set(synergy_ids))),
            confidence=confidence,
            uncertainty=max(0.0, 1.0 - confidence),
            findings=("FIELD_CONSTRUCTED", "VALIDATION_COMPLETED"),
            trace=("PROJECTIONS_AGGREGATED", "TENSIONS_IDENTIFIED", "SYNERGIES_IDENTIFIED"),
        )


__all__ = ["MotivationalRewardField"]