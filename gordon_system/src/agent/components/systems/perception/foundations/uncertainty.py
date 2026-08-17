# Perception Uncertainty - Phase 5.2 Foundational Module
# ======================================================

"""
Perception Uncertainty: Represents epistemic limitations in perceptual estimates.

Uncertainty is distinct from confidence and captures the limits of what can be
known about a perceptual hypothesis.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PerceptionUncertainty:
    """
    Quantified uncertainty in a perceptual estimate.
    
    Uncertainty is distinct from confidence. While confidence measures how strongly
    we believe an estimate is correct, uncertainty captures what we cannot know
    due to limitations in evidence or measurement.
    
    Properties:
        value:  Numeric uncertainty (0.0-1.0)
        basis:  What the uncertainty represents
        sources: Sources contributing to this uncertainty
    """
    
    value: float = 0.0
    basis: str = "measurement"  # measurement, inference, missing_data, ambiguity
    
    @property
    def is_valid(self) -> bool:
        """Check if uncertainty has valid data."""
        return 0.0 <= self.value <= 1.0


__all__ = ["PerceptionUncertainty"]