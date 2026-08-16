# Reward Network - Context Evidence Extractor
# ===========================================

"""
Context evidence extractor.

Extracts semantic evidence about contextual states and their relationship to outcomes.
"""

from __future__ import annotations

from typing import Tuple, Optional

from ..evidence import (
    RewardEvidence,
    EvidenceType,
    EvidenceKind,
)
from .base import EvidenceExtractor


class ContextEvidenceExtractor(EvidenceExtractor):
    """
    Extractor for context-level semantic evidence.

    Transforms outcomes into semantic evidence about contextual states
    and their relationship to the outcome. Each extraction is deterministic
    and preserves provenance.

    EXTRACTOR PROPERTIES:
        • extractor_type: 'context'
        • is_stateless: True
        • is_deterministic: True

    EVIDENCE KINDS PRODUCED:
        • context_favorable: Context supports the outcome
        • context_unfavorable: Context opposes the outcome
        • context_neutral: Context unchanged
        • context_changed: Context state changed

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

    extractor_type: str = "context"

    def extract(
        self,
        outcome_id: str,
        outcome_data: dict,
    ) -> Tuple[RewardEvidence, ...]:
        """
        Extract evidence from an outcome about context.

        Args:
            outcome_id: The Outcome ID to extract from
            outcome_data: The outcome data dictionary

        Returns:
            Tuple of extracted RewardEvidence items (empty if none found)
        """
        context_info = self._extract_context_state(outcome_data)
        if not context_info:
            return ()

        context_name, is_favorable, was_changed = context_info

        evidence_kind = self._infer_evidence_kind(
            is_favorable, was_changed
        )

        semantic_content = f"Outcome {outcome_id} indicates {'favorable' if is_favorable else 'unfavorable'} context for '{context_name}' (changed: {was_changed})"

        relationship = (
            "supports_reward"
            if is_favorable
            else "supports_punishment"
        )

        evidence = RewardEvidence.create(
            evidence_id=f"{outcome_id}-context-evidence",
            evidence_type="context",
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

    def _extract_context_state(
        self, outcome_data: dict
    ) -> Tuple[Optional[str], Optional[bool], Optional[bool]]:
        """
        Extract context name and state from outcome data.

        Args:
            outcome_data: The outcome data dictionary

        Returns:
            Tuple of (context_name, is_favorable, was_changed) or (None, None, None)
        """
        context = outcome_data.get("context", ())
        if isinstance(context, dict):
            ctx_name = context.get("name")
            favorable = context.get("favorable")
            changed = context.get("changed")
            if ctx_name:
                return (
                    ctx_name
                    if isinstance(ctx_name, str)
                    else str(ctx_name),
                    bool(favorable) if favorable is not None else True,
                    bool(changed) if changed is not None else False,
                )

        return None, None, None

    def _infer_evidence_kind(
        self, is_favorable: Optional[bool], was_changed: Optional[bool]
    ) -> EvidenceKind:
        """
        Infer evidence kind from context state.

        Args:
            is_favorable: Whether the context is favorable
            was_changed: Whether the context changed

        Returns:
            Inferred evidence kind
        """
        if is_favorable is None:
            return "context_neutral"

        if was_changed:
            if is_favorable:
                return "context_favorable"
            else:
                return "context_unfavorable"
        else:
            return "context_neutral"

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
            "context_favorable": 0.8,
            "context_unfavorable": 0.8,
            "context_neutral": 0.75,
            "context_changed": 0.7,
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
            required_keys = {"name", "favorable"}
            if all(k in context for k in required_keys):
                return 0.2
        return 0.4