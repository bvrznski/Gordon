# Reward Network - Behavior Evidence Extractor
# ============================================

"""
Behavior evidence extractor.

Extracts semantic evidence about behavior reinforcement and suppression.
"""

from __future__ import annotations

from typing import Tuple, Optional

from ..evidence import (
    RewardEvidence,
    EvidenceType,
    EvidenceKind,
)
from .base import EvidenceExtractor


class BehaviorEvidenceExtractor(EvidenceExtractor):
    """
    Extractor for behavior-level semantic evidence.

    Transforms outcomes into semantic evidence about behaviors being
    reinforced or suppressed. Each extraction is deterministic and preserves
    provenance.

    EXTRACTOR PROPERTIES:
        • extractor_type: 'behavior'
        • is_stateless: True
        • is_deterministic: True

    EVIDENCE KINDS PRODUCED:
        • behavior_reinforced: Behavior strengthened by outcome
        • behavior_suppressed: Behavior weakened by outcome
        • behavior_stable: Behavior unchanged
        • behavior_rewarded: Behavior followed by positive outcome
        • behavior_punished: Behavior followed by negative outcome

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

    extractor_type: str = "behavior"

    def extract(
        self,
        outcome_id: str,
        outcome_data: dict,
    ) -> Tuple[RewardEvidence, ...]:
        """
        Extract evidence from an outcome about behavior.

        Args:
            outcome_id: The Outcome ID to extract from
            outcome_data: The outcome data dictionary

        Returns:
            Tuple of extracted RewardEvidence items (empty if none found)
        """
        behavior_info = self._extract_behavior_context(outcome_data)
        if not behavior_info:
            return ()

        behavior_name, is_reinforced = behavior_info

        evidence_kind = (
            "behavior_reinforced" if is_reinforced else "behavior_suppressed"
        )

        semantic_content = f"Outcome {outcome_id} {'reinforced' if is_reinforced else 'suppressed'} behavior '{behavior_name}'"

        relationship = (
            "supports_reward"
            if is_reinforced
            else "supports_punishment"
        )

        evidence = RewardEvidence.create(
            evidence_id=f"{outcome_id}-behavior-evidence",
            evidence_type="behavior",
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

    def _extract_behavior_context(
        self, outcome_data: dict
    ) -> Tuple[Optional[str], Optional[bool]]:
        """
        Extract behavior name and reinforcement state from outcome data.

        Args:
            outcome_data: The outcome data dictionary

        Returns:
            Tuple of (behavior_name, is_reinforced) or (None, None)
        """
        context = outcome_data.get("context", ())
        if isinstance(context, dict):
            behavior = context.get("behavior")
            reinforced = context.get("reinforced")
            if behavior:
                return (
                    behavior
                    if isinstance(behavior, str)
                    else str(behavior),
                    bool(reinforced) if reinforced is not None else True,
                )

        return None, None

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
            "behavior_reinforced": 0.8,
            "behavior_suppressed": 0.8,
            "behavior_stable": 0.75,
            "behavior_rewarded": 0.85,
            "behavior_punished": 0.85,
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
            if "behavior" in context and "reinforced" in context:
                return 0.2
        return 0.4