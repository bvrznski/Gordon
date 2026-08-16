# Reward Network - Constraint Evidence Extractor
# ==============================================

"""
Constraint evidence extractor.

Extracts semantic evidence about constraint satisfaction and violation.
"""

from __future__ import annotations

from typing import Tuple, Optional

from ..evidence import (
    RewardEvidence,
    EvidenceType,
    EvidenceKind,
)
from .base import EvidenceExtractor


class ConstraintEvidenceExtractor(EvidenceExtractor):
    """
    Extractor for constraint-level semantic evidence.

    Transforms outcomes into semantic evidence about constraints being
    satisfied or violated. Each extraction is deterministic and preserves
    provenance.

    EXTRACTOR PROPERTIES:
        • extractor_type: 'constraint'
        • is_stateless: True
        • is_deterministic: True

    EVIDENCE KINDS PRODUCED:
        • constraint_satisfied: Constraint met by outcome
        • constraint_violated: Constraint breached by outcome
        • constraint_unchanged: Constraint state unchanged

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

    extractor_type: str = "constraint"

    def extract(
        self,
        outcome_id: str,
        outcome_data: dict,
    ) -> Tuple[RewardEvidence, ...]:
        """
        Extract evidence from an outcome about constraints.

        Args:
            outcome_id: The Outcome ID to extract from
            outcome_data: The outcome data dictionary

        Returns:
            Tuple of extracted RewardEvidence items (empty if none found)
        """
        constraint_info = self._extract_constraint_context(outcome_data)
        if not constraint_info:
            return ()

        constraint_name, is_satisfied = constraint_info

        evidence_kind = (
            "constraint_satisfied" if is_satisfied else "constraint_violated"
        )

        semantic_content = f"Outcome {outcome_id} {'satisfied' if is_satisfied else 'violated'} constraint '{constraint_name}'"

        relationship = (
            "supports_reward"
            if is_satisfied
            else "supports_punishment"
        )

        evidence = RewardEvidence.create(
            evidence_id=f"{outcome_id}-constraint-evidence",
            evidence_type="constraint",
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

    def _extract_constraint_context(
        self, outcome_data: dict
    ) -> Tuple[Optional[str], Optional[bool]]:
        """
        Extract constraint name and satisfaction from outcome data.

        Args:
            outcome_data: The outcome data dictionary

        Returns:
            Tuple of (constraint_name, is_satisfied) or (None, None)
        """
        context = outcome_data.get("context", ())
        if isinstance(context, dict):
            constraint = context.get("constraint")
            satisfied = context.get("satisfied")
            if constraint:
                return (
                    constraint
                    if isinstance(constraint, str)
                    else str(constraint),
                    bool(satisfied) if satisfied is not None else True,
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
            "constraint_satisfied": 0.85,
            "constraint_violated": 0.85,
            "constraint_unchanged": 0.8,
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
            if "constraint" in context and "satisfied" in context:
                return 0.2
        return 0.4