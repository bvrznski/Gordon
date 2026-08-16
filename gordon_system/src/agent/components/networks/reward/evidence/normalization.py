# Reward Network - Evidence Normalization
# ========================================

"""
Evidence normalization module.

Normalizes heterogeneous evidence into canonical semantic representations.
Normalization converts evidence from various formats into standard evidence items
without changing meaning.
"""

from __future__ import annotations

from typing import Tuple, Optional

from .evidence import (
    RewardEvidence,
    EvidenceType,
    EvidenceKind,
)
from .extractors.base import EvidenceExtractor


class EvidenceNormalizer:
    """
    Normalizes evidence from various formats into canonical RewardEvidence.

    Normalization converts heterogeneous evidence into standard semantic
    representations while preserving meaning. Each normalization is
    deterministic and idempotent.

    NORMALIZATION PROPERTIES:
        • is_stateless: True - no internal state
        • is_deterministic: True - same input always produces same output
        • preserves_semantics: True - meaning unchanged

    NORMALIZATION INVARIANTS:
        • Normalization never creates new evidence, only restructures existing
        • Normalization never discards evidence
        • Normalization never infers reward values
    """

    def __init__(self) -> None:
        """Initialize the normalizer."""
        self._normalized_types: set[str] = {
            "outcome",
            "goal",
            "resource",
            "constraint",
            "behavior",
            "prediction",
            "context",
            "history",
        }

    @property
    def is_stateless(self) -> bool:
        """Check if this normalizer maintains no state."""
        return True

    @property
    def is_deterministic(self) -> bool:
        """Check if this normalizer always produces same output."""
        return True

    def normalize(
        self, evidence: dict | RewardEvidence
    ) -> Tuple[RewardEvidence, ...]:
        """
        Normalize evidence into canonical RewardEvidence format.

        Args:
            evidence: The evidence to normalize (dict or RewardEvidence)

        Returns:
            Tuple of normalized RewardEvidence items
        """
        if isinstance(evidence, RewardEvidence):
            # Already normalized
            return (evidence,)

        # Handle dictionary evidence
        return self._normalize_dict(evidence)

    def _normalize_dict(self, evidence: dict) -> Tuple[RewardEvidence, ...]:
        """
        Normalize dictionary evidence into RewardEvidence.

        Args:
            evidence: Dictionary representation of evidence

        Returns:
            Tuple containing one normalized RewardEvidence item
        """
        # Extract required fields with defaults
        evidence_id = evidence.get("evidence_id", "unknown")
        evidence_type = evidence.get("evidence_type", "unknown")
        evidence_kind = evidence.get("evidence_kind", "unknown")
        outcome_ref = tuple(evidence.get("outcome_ref", []))
        semantic_content = evidence.get("semantic_content", "")

        # Extract optional fields with defaults
        relationship = evidence.get("relationship", "unknown")
        confidence = float(evidence.get("confidence", 0.5))
        uncertainty = float(evidence.get("uncertainty", 0.0))
        timescale = evidence.get("timescale", "immediate")
        source_subsystem = evidence.get("source_subsystem")
        provenance = evidence.get("provenance")
        context = tuple(evidence.get("context", ()))

        # Build normalized evidence
        normalized = RewardEvidence.create(
            evidence_id=evidence_id,
            evidence_type=evidence_type,
            evidence_kind=evidence_kind,
            outcome_ref=outcome_ref,
            semantic_content=semantic_content,
            relationship=relationship,
            confidence=confidence,
            uncertainty=uncertainty,
            timescale=timescale,
            source_subsystem=source_subsystem,
            provenance=provenance,
            context=context,
        )

        return (normalized,)

    def normalize_batch(
        self, evidences: Tuple[dict | RewardEvidence, ...]
    ) -> Tuple[RewardEvidence, ...]:
        """
        Normalize a batch of evidence items.

        Args:
            evidences: Tuple of evidence to normalize

        Returns:
            Tuple of all normalized RewardEvidence items
        """
        result: list[RewardEvidence] = []
        for evidence in evidences:
            result.extend(self.normalize(evidence))
        return tuple(result)


def normalize_evidence(
    evidence: dict | RewardEvidence,
) -> Tuple[RewardEvidence, ...]:
    """
    Normalize a single evidence item into canonical format.

    Args:
        evidence: The evidence to normalize

    Returns:
        Tuple containing the normalized Evidence
    """
    normalizer = EvidenceNormalizer()
    return normalizer.normalize(evidence)