# Reward Network - History Evidence Extractor
# ===========================================

"""
History evidence extractor.

Extracts semantic evidence about historical patterns, sequences, and temporal context.
"""

from __future__ import annotations

from typing import Tuple, Optional

from ..evidence import (
    RewardEvidence,
    EvidenceType,
    EvidenceKind,
)
from .base import EvidenceExtractor


class HistoryEvidenceExtractor(EvidenceExtractor):
    """
    Extractor for history-level semantic evidence.

    Transforms outcomes into semantic evidence about historical patterns,
    sequences, and temporal context. Each extraction is deterministic
    and preserves provenance.

    EXTRACTOR PROPERTIES:
        • extractor_type: 'history'
        • is_stateless: True
        • is_deterministic: True

    EVIDENCE KINDS PRODUCED:
        • historical_pattern: Recurring pattern detected
        • novel_event: First-time event
        • sequence_continued: Sequence maintained
        • sequence_broken: Sequence interrupted
        • temporal_consistency: Time-based consistency confirmed
        • temporal_inconsistency: Time-based inconsistency detected

    EXTRACTOR LAWS:
        EXTRACTION-LAW-001: This extractor owns exactly one evidence domain
        EXTRACTION-LAW-002: Extractors remain stateless
        EXTRACTION-LAW-003: Extractors remain deterministic
        EXTRACTION-LAW-004: Extractors preserve provenance
        EXTRACTION-LAW-005: Extractors preserve semantic identity
        EXTRACTION-LAW-006: Extractors shall not infer reward
        EXTRACTION-LAW-007: Extractors shall not invoke one another directly
        EXTRACTION-LAW-008: Extractors return immutable RewardEvidence only
    """

    extractor_type: str = "history"

    def extract(
        self,
        outcome_id: str,
        outcome_data: dict,
    ) -> Tuple[RewardEvidence, ...]:
        """
        Extract evidence from an outcome about history.

        Args:
            outcome_id: The Outcome ID to extract from
            outcome_data: The outcome data dictionary

        Returns:
            Tuple of extracted RewardEvidence items (empty if none found)
        """
        history_info = self._extract_history_context(outcome_data)
        if not history_info:
            return ()

        history_type, is_recurring, was_consistent = history_info

        evidence_kind = self._infer_evidence_kind(
            is_recurring, was_consistent
        )

        semantic_content = f"Outcome {outcome_id} indicates {'recurring' if is_recurring else 'novel'} historical pattern ('{history_type}') (consistent: {was_consistent})"

        relationship = (
            "supports_reward"
            if was_consistent
            else "supports_punishment"
        )

        evidence = RewardEvidence.create(
            evidence_id=f"{outcome_id}-history-evidence",
            evidence_type="history",
            evidence_kind=evidence_kind,
            outcome_ref=(outcome_id,),
            semantic_content=semantic_content,
            relationship=relationship,
            confidence=self._estimate_confidence(evidence_kind, outcome_data),
            uncertainty=self._estimate_uncertainty(outcome_data),
            timescale=outcome_data.get("timescale", "immediate"),
            source_subsystem=outcome_data.get("source_subsystem"),
        )

        return (evidence,)

    def _extract_history_context(
        self, outcome_data: dict
    ) -> Tuple[Optional[str], Optional[bool], Optional[bool]]:
        """
        Extract history context from outcome data.

        Args:
            outcome_data: The outcome data dictionary

        Returns:
            Tuple of (history_type, is_recurring, was_consistent) or (None, None, None)
        """
        context = outcome_data.get("context", ())
        if isinstance(context, dict):
            history_type = context.get("history_type")
            recurring = context.get("recurring")
            consistent = context.get("consistent")
            if history_type:
                return (
                    history_type
                    if isinstance(history_type, str)
                    else str(history_type),
                    bool(recurring) if recurring is not None else True,
                    bool(consistent) if consistent is not None else True,
                )

        return None, None, None

    def _infer_evidence_kind(
        self, is_recurring: Optional[bool], was_consistent: Optional[bool]
    ) -> EvidenceKind:
        """
        Infer evidence kind from history state.

        Args:
            is_recurring: Whether the pattern is recurring
            was_consistent: Whether the sequence was consistent

        Returns:
            Inferred evidence kind
        """
        if is_recurring and was_consistent:
            return "historical_pattern"
        elif not is_recurring:
            return "novel_event"
        elif was_consistent:
            return "sequence_continued"
        else:
            return "sequence_broken"

    def _estimate_confidence(
        self, evidence_kind: EvidenceKind, outcome_data: dict
    ) -> float:
        """
        Estimate confidence level for this evidence.

        Args:
            evidence_kind: The evidence kind
            outcome_data: The outcome data dictionary

        Returns:
            Confidence value (0.0 to 1.0)
        """
        base_confidence = {
            "historical_pattern": 0.85,
            "novel_event": 0.75,
            "sequence_continued": 0.8,
            "sequence_broken": 0.7,
            "temporal_consistency": 0.9,
            "temporal_inconsistency": 0.8,
        }

        return base_confidence.get(evidence_kind, 0.5)

    def _estimate_uncertainty(self, outcome_data: dict) -> float:
        """
        Estimate uncertainty level for this evidence.

        Args:
            outcome_data: The outcome data dictionary

        Returns:
            Uncertainty value (0.0 to 1.0)
        """
        context = outcome_data.get("context", ())
        if isinstance(context, dict):
            required_keys = {"history_type", "recurring"}
            if all(k in context for k in required_keys):
                return 0.2
        return 0.4