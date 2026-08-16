# Reward Network - Evidence Extractor Base Classes
# ================================================

"""
Base classes for evidence extractors.

Extractors are stateless components that extract semantic evidence from outcomes.
Each extractor owns exactly one evidence domain and produces immutable evidence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple

from ..evidence import RewardEvidence


class EvidenceExtractor(ABC):
    """
    Base class for evidence extractors.

    Extractors are stateless components that transform outcomes into semantic
    evidence. Each extractor owns exactly one evidence domain and produces
    immutable evidence items.

    EXTRACTOR LAWS:
        EXTRACTION-LAW-001: Every extractor owns exactly one evidence domain
        EXTRACTION-LAW-002: Extractors remain stateless
        EXTRACTION-LAW-003: Extractors remain deterministic
        EXTRACTION-LAW-004: Extractors preserve provenance
        EXTRACTION-LAW-005: Extractors preserve semantic identity
        EXTRACTION-LAW-006: Extractors shall not infer reward
        EXTRACTION-LAW-007: Extractors shall not invoke one another directly
        EXTRACTION-LAW-008: Extractors return immutable RewardEvidence only

    PROPERTIES:
        • extractor_type: Canonical type of evidence this extractor produces
        • is_stateless: Whether this extractor maintains no state
        • is_deterministic: Whether this extractor always produces same output
    """

    # Class-level properties (not instance-level)
    extractor_type: str = "unknown"
    """Canonical type of evidence this extractor produces."""

    @abstractmethod
    def extract(self, outcome_id: str, outcome_data: dict) -> Tuple[RewardEvidence, ...]:
        """
        Extract evidence from an outcome.

        Args:
            outcome_id: The Outcome ID to extract from
            outcome_data: The outcome data dictionary

        Returns:
            Tuple of extracted RewardEvidence items (empty if none found)
        """

    @property
    def is_stateless(self) -> bool:
        """Check if this extractor maintains no state."""
        return True

    @property
    def is_deterministic(self) -> bool:
        """Check if this extractor always produces same output for same input."""
        return True