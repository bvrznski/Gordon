# Reward Network - Evidence Confidence Estimator
# ==============================================

"""
Confidence estimator for evidence.

Evidence confidence estimates how reliable the supporting evidence is.
It remains independent from reward confidence, prediction confidence,
and belief confidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True, slots=True)
class EvidenceConfidence:
    """
    Estimate of evidence reliability and certainty.

    Evidence confidence represents how reliably the supporting evidence
    was computed, based on evidence quality and estimation context.
    It is independent from reward confidence.

    CONFIDENCE INVARIANTS:
        • Confidence belongs exclusively to evidence quality
        • Evidence confidence remains independent from reward confidence
        • Evidence confidence remains independent from belief confidence
        • Evidence confidence remains independent from prediction confidence

    HIGH EVIDENCE with LOW confidence:
        - Strong supporting facts but weak provenance
        - Potential reliability concerns

    LOW EVIDENCE with HIGH confidence:
        - Weak evidence but strong quality indicators
        - Reliable assessment despite limited data
    """

    value: float  # 0.0 to 1.0
    """Confidence level in the evidence."""

    basis: str = "default"
    """Basis for this confidence (e.g., 'sufficient_evidence', 'limited_data')."""

    evidence_quality: float = 1.0
    """Quality of the underlying evidence."""

    source_reliability: float = 1.0
    """Reliability of the source subsystem."""

    context_stability: float = 1.0
    """Stability of context during evidence acquisition."""

    @property
    def is_high(self) -> bool:
        """Check if confidence is high (>= 0.7)."""
        return self.value >= 0.7

    @property
    def is_medium(self) -> bool:
        """Check if confidence is medium (0.4 to 0.7)."""
        return 0.4 <= self.value < 0.7

    @property
    def is_low(self) -> bool:
        """Check if confidence is low (< 0.4)."""
        return self.value < 0.4

    @classmethod
    def high(cls, value: float = 1.0) -> EvidenceConfidence:
        """Create a high confidence estimate."""
        return cls(
            value=value,
            basis="sufficient_evidence",
            evidence_quality=0.9,
            source_reliability=0.95,
            context_stability=0.9,
        )

    @classmethod
    def medium(cls, value: float = 0.5) -> EvidenceConfidence:
        """Create a medium confidence estimate."""
        return cls(
            value=value,
            basis="moderate_evidence",
            evidence_quality=0.6,
            source_reliability=0.7,
            context_stability=0.8,
        )

    @classmethod
    def low(cls, value: float = 0.2) -> EvidenceConfidence:
        """Create a low confidence estimate."""
        return cls(
            value=value,
            basis="limited_data",
            evidence_quality=0.3,
            source_reliability=0.5,
            context_stability=0.6,
        )


def estimate_evidence_confidence(
    evidence_count: int,
    source_reliability: float = 1.0,
) -> EvidenceConfidence:
    """
    Estimate confidence based on evidence quantity and source reliability.

    Args:
        evidence_count: Number of supporting evidence items
        source_reliability: Reliability of the source subsystem

    Returns:
        Estimated EvidenceConfidence
    """
    # Base confidence increases with more evidence (diminishing returns)
    base_confidence = min(0.95, 0.3 + 0.1 * (evidence_count**0.5))

    # Apply source reliability factor
    final_confidence = base_confidence * source_reliability

    return EvidenceConfidence(
        value=final_confidence,
        basis=f"derived_from_{evidence_count}_sources",
        evidence_quality=base_confidence,
        source_reliability=source_reliability,
    )