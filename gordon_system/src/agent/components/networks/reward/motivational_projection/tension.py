# Motivational Projection Network - Tension Analysis (Phase 4.10.6)
# ================================================================
#
# Motivational tensions represent conflicts between drive projections.
# They are descriptive, not prescriptive - no resolution occurs here.

"""
MotivationalTension model for Phase 4.10.6.

This module defines the canonical tension data structure that represents
conflicting motivational influences from reward projections.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple


class TensionType(Enum):
    """
    Canonical tension types for motivational conflicts.

    TENSION-LAW-001: Every tension references at least two DriveProjections.
    TENSION-LAW-002: Tensions remain immutable.
    TENSION-LAW-003: Conflict type remains explicit.
    TENSION-LAW-004: No automatic resolution occurs here.
    """
    
    # Types of motivational tensions
    DIRECT_CONFLICT = "direct_conflict"
    """Projections have directly opposing effects on the same drive."""
    
    COMPETING_PRIORITIES = "competing_priorities"
    """Projections promote competing high-level goals."""
    
    TEMPORAL_CONFLICT = "temporal_conflict"
    """Short-term vs long-term projection conflicts."""
    
    HIERARCHICAL_CONFLICT = "hierarchical_conflict"
    """Conflicts between different hierarchy levels (e.g., action vs mission)."""
    
    SEMANTIC_CONFLICT = "semantic_conflict"
    """Projections have semantically incompatible values."""
    
    # Strength indicators
    WEAK_TENSION = "weak_tension"
    """Low-severity tension that may be easily resolved elsewhere."""
    
    STRONG_TENSION = "strong_tension"
    """High-severity tension requiring executive arbitration."""


@dataclass(frozen=True)
class MotivationalTension:
    """
    A motivational tension between projections.

    TENSION-LAW-005: Supporting evidence remains preserved.
    TENSION-LAW-006: Confidence remains independent for each tension.
    TENSION-LAW-007: Tensions remain unresolved (descriptive only).
    
    NOT RESPONSIBLE FOR:
        • Resolving tensions automatically
        • Creating executive priorities
        • Modifying projections
    """
    
    tension_id: str
    """Unique identifier for this tension."""
    
    participating_projections: Tuple[str, ...]
    """Projection IDs involved in the tension (at least 2)."""
    
    tension_type: TensionType = TensionType.DIRECT_CONFLICT
    """Type of tension between projections."""
    
    severity: float = 0.5
    """Severity of the tension (0.0-1.0)."""
    
    confidence: float = 1.0
    """Confidence in this tension assessment (0.0-1.0)."""
    
    uncertainty: float = 0.0
    """Uncertainty in this tension assessment (0.0-1.0)."""
    
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence IDs supporting the tension identification."""
    
    provenance: str = "unknown"
    """Source information for traceability."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.tension_id}@v0"
    
    @property
    def is_valid(self) -> bool:
        """Check if tension configuration is valid."""
        return (
            len(self.participating_projections) >= 2
            and 0.0 <= self.severity <= 1.0
            and 0.0 <= self.confidence <= 1.0
            and 0.0 <= self.uncertainty <= 1.0
        )
    
    def to_dict(self) -> dict:
        """Convert tension to dictionary representation."""
        return {
            "tension_id": self.tension_id,
            "participating_projections": list(self.participating_projections),
            "tension_type": self.tension_type.value,
            "severity": self.severity,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "supporting_evidence": list(self.supporting_evidence),
            "provenance": self.provenance,
        }
    
    @classmethod
    def create(
        cls,
        tension_id: str,
        projection_ids: Tuple[str, ...],
        tension_type: TensionType = TensionType.DIRECT_CONFLICT,
        severity: float = 0.5,
        confidence: float = 1.0,
        evidence: Tuple[str, ...] = tuple(),
        provenance: str = "unknown",
    ) -> MotivationalTension:
        """Create a new motivational tension."""
        return cls(
            tension_id=tension_id,
            participating_projections=projection_ids,
            tension_type=tension_type,
            severity=severity,
            confidence=confidence,
            uncertainty=max(0.0, 1.0 - confidence),
            supporting_evidence=evidence,
            provenance=provenance,
        )


__all__ = [
    "TensionType",
    "MotivationalTension",
]