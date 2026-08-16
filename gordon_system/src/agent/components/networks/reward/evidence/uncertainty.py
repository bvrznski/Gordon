# Reward Network - Evidence Uncertainty Estimator
# ===============================================

"""
Uncertainty estimator for evidence.

Evidence uncertainty represents gaps in available information about evidence.
It is independent from confidence (which measures reliability).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class EvidenceUncertainty:
    """
    Estimate of evidence unknown information.

    Evidence uncertainty represents gaps in available information for
    evidence assessment, distinct from confidence which measures reliability
    of existing estimates.

    UNCERTAINTY KINDS:
        • high: Significant information gaps in evidence assessment
        • medium: Moderate uncertainty about some factors
        • low: Reasonable certainty about most factors
        • unknown: Cannot determine uncertainty from available data

    UNCERTAINTY INVARIANTS:
        • Uncertainty remains explicitly represented
        • Evidence uncertainty remains independent from confidence
        • Unknown uncertainty is distinguishable from low uncertainty
        • Uncertainty shall never be computed as 1 - confidence
    """

    kind: str = "unknown"
    """Uncertainty level (high, medium, low, unknown)."""

    information_gaps: Tuple[str, ...] = field(default_factory=tuple)
    """Descriptions of missing information."""

    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this uncertainty assessment."""

    @property
    def is_high(self) -> bool:
        """Check if uncertainty is high."""
        return self.kind == "high"

    @property
    def is_medium(self) -> bool:
        """Check if uncertainty is medium."""
        return self.kind == "medium"

    @property
    def is_low(self) -> bool:
        """Check if uncertainty is low."""
        return self.kind == "low"

    @property
    def is_unknown(self) -> bool:
        """Check if uncertainty is unknown."""
        return self.kind == "unknown"

    @classmethod
    def high(cls, *gaps: str) -> EvidenceUncertainty:
        """Create a high uncertainty estimate."""
        return cls(
            kind="high",
            information_gaps=gaps,
        )

    @classmethod
    def medium(cls, *gaps: str) -> EvidenceUncertainty:
        """Create a medium uncertainty estimate."""
        return cls(
            kind="medium",
            information_gaps=gaps,
        )

    @classmethod
    def low(cls, *gaps: str) -> EvidenceUncertainty:
        """Create a low uncertainty estimate."""
        return cls(
            kind="low",
            information_gaps=gaps,
        )

    @classmethod
    def unknown(cls) -> EvidenceUncertainty:
        """Create an unknown uncertainty estimate."""
        return cls(kind="unknown")


def estimate_evidence_uncertainty(
    evidence_count: int,
    missing_factors: Tuple[str, ...] = tuple(),
) -> EvidenceUncertainty:
    """
    Estimate uncertainty based on evidence quantity and missing factors.

    Args:
        evidence_count: Number of supporting evidence items
        missing_factors: List of known missing factors

    Returns:
        Estimated EvidenceUncertainty
    """
    if not evidence_count or len(missing_factors) > 3:
        return EvidenceUncertainty(kind="high", information_gaps=missing_factors)
    elif len(missing_factors) > 1:
        return EvidenceUncertainty(kind="medium", information_gaps=missing_factors)
    elif missing_factors:
        return EvidenceUncertainty(kind="low", information_gaps=missing_factors)
    else:
        return EvidenceUncertainty(kind="low")


def estimate_uncertainty_from_evidence(evidence_items: Tuple[dict, ...]) -> EvidenceUncertainty:
    """
    Estimate uncertainty from a set of evidence dictionaries.

    Args:
        evidence_items: List of evidence data dictionaries

    Returns:
        Estimated EvidenceUncertainty
    """
    if not evidence_items:
        return EvidenceUncertainty(kind="high", information_gaps=("no_evidence_provided",))

    # Count missing critical fields
    missing_fields = []
    required_fields = ("evidence_id", "semantic_content")

    for item in evidence_items:
        if not isinstance(item, dict):
            continue
        for field_name in required_fields:
            if field_name not in item:
                missing_fields.append(f"missing_{field_name}")

    unique_missing = tuple(set(missing_fields))

    if len(unique_missing) > 2:
        return EvidenceUncertainty(
            kind="high",
            information_gaps=unique_missing,
        )
    elif unique_missing:
        return EvidenceUncertainty(
            kind="medium",
            information_gaps=unique_missing,
        )
    else:
        return EvidenceUncertainty(kind="low")