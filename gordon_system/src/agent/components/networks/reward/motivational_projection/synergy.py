# Motivational Projection Network - Synergy Analysis (Phase 4.10.6)
# ================================================================
#
# Motivational synergies represent cooperative relationships between
# drive projections. They are descriptive, not prescriptive.

"""
MotivationalSynergy model for Phase 4.10.6.

This module defines the canonical synergy data structure that represents
cooperative motivational influences from reward projections.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple


class SynergyType(Enum):
    """
    Canonical synergy types for motivational cooperation.

    SYNERGY-LAW-001: Every synergy references at least two DriveProjections.
    SYNERGY-LAW-002: Synergies remain immutable.
    SYNERGY-LAW-003: Synergy type remains explicit.
    SYNERGY-LAW-004: Synergies remain descriptive (never prescriptive).
    """
    
    # Types of synergies
    MUTUAL_REINFORCEMENT = "mutual_reinforcement"
    """Projections mutually reinforce each other."""
    
    COMPLEMENTARY = "complementary"
    """Projections complement each other (different aspects)."""
    
    MULTIPLYING = "multiplying"
    """Projections multiply effect when combined > sum of parts."""
    
    ADDITIVE = "additive"
    """Projections have additive effect."""
    
    CASCADE = "cascade"
    """One projection triggers cascade of others."""
    
    TEMPORAL_SYNERGY = "temporal_synergy"
    """Temporal alignment creates synergy."""
    
    HIERARCHICAL_SYNERGY = "hierarchical_synergy"
    """Cross-level alignment creates synergy."""


@dataclass(frozen=True)
class MotivationalSynergy:
    """
    A motivational synergy between projections.

    SYNERGY-LAW-005: Supporting evidence remains preserved.
    SYNERGY-LAW-006: Confidence remains independent for each synergy.
    SYNERGY-LAW-007: Synergies shall never merge projections.
    
    NOT RESPONSIBLE FOR:
        • Merging projections
        • Creating new motivational states
        • Making executive decisions
    """
    
    synergy_id: str
    """Unique identifier for this synergy."""
    
    participating_projections: Tuple[str, ...]
    """Projection IDs involved in the synergy (at least 2)."""
    
    synergy_type: SynergyType = SynergyType.ADDITIVE
    """Type of synergy between projections."""
    
    strength: float = 0.5
    """Strength of the synergistic effect (0.0-1.0)."""
    
    confidence: float = 1.0
    """Confidence in this synergy assessment (0.0-1.0)."""
    
    uncertainty: float = 0.0
    """Uncertainty in this synergy assessment (0.0-1.0)."""
    
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence IDs supporting the synergy identification."""
    
    provenance: str = "unknown"
    """Source information for traceability."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.synergy_id}@v0"
    
    @property
    def is_valid(self) -> bool:
        """Check if synergy configuration is valid."""
        return (
            len(self.participating_projections) >= 2
            and 0.0 <= self.strength <= 1.0
            and 0.0 <= self.confidence <= 1.0
            and 0.0 <= self.uncertainty <= 1.0
        )
    
    def to_dict(self) -> dict:
        """Convert synergy to dictionary representation."""
        return {
            "synergy_id": self.synergy_id,
            "participating_projections": list(self.participating_projections),
            "synergy_type": self.synergy_type.value,
            "strength": self.strength,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "supporting_evidence": list(self.supporting_evidence),
            "provenance": self.provenance,
        }
    
    @classmethod
    def create(
        cls,
        synergy_id: str,
        projection_ids: Tuple[str, ...],
        synergy_type: SynergyType = SynergyType.ADDITIVE,
        strength: float = 0.5,
        confidence: float = 1.0,
        evidence: Tuple[str, ...] = tuple(),
        provenance: str = "unknown",
    ) -> MotivationalSynergy:
        """Create a new motivational synergy."""
        return cls(
            synergy_id=synergy_id,
            participating_projections=projection_ids,
            synergy_type=synergy_type,
            strength=strength,
            confidence=confidence,
            uncertainty=max(0.0, 1.0 - confidence),
            supporting_evidence=evidence,
            provenance=provenance,
        )


__all__ = [
    "SynergyType",
    "MotivationalSynergy",
]