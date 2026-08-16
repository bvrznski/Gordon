# Reward Network - Resource Evidence Extractor
# ============================================

"""
Resource evidence extractor.

Extracts semantic evidence about resource acquisition, loss, and state changes.
"""

from __future__ import annotations

from typing import Tuple, Optional

from ..evidence import (
    RewardEvidence,
    EvidenceType,
    EvidenceKind,
)
from .base import EvidenceExtractor


class ResourceEvidenceExtractor(EvidenceExtractor):
    """
    Extractor for resource-level semantic evidence.

    Transforms outcomes into semantic evidence about resource acquisition,
    loss, and state changes. Each extraction is deterministic and preserves
    provenance.

    EXTRACTOR PROPERTIES:
        • extractor_type: 'resource'
        • is_stateless: True
        • is_deterministic: True

    EVIDENCE KINDS PRODUCED:
        • resource_acquired: Resources gained
        • resource_lost: Resources depleted
        • resource_preserved: Resources maintained
        • resource_depleted: Resources exhausted
        • resource_renewed: Resources replenished

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

    extractor_type: str = "resource"

    def extract(
        self,
        outcome_id: str,
        outcome_data: dict,
    ) -> Tuple[RewardEvidence, ...]:
        """
        Extract evidence from an outcome about resources.

        Args:
            outcome_id: The Outcome ID to extract from
            outcome_data: The outcome data dictionary

        Returns:
            Tuple of extracted RewardEvidence items (empty if none found)
        """
        resource_info = self._extract_resource_context(outcome_data)
        if not resource_info:
            return ()

        resource_name, resource_change = resource_info

        evidence_kind = self._infer_evidence_kind(resource_change)

        semantic_content = f"Outcome {outcome_id} changed resource '{resource_name}' by {resource_change}"

        relationship = (
            "supports_reward"
            if resource_change > 0
            else "supports_punishment"
        )

        evidence = RewardEvidence.create(
            evidence_id=f"{outcome_id}-resource-evidence",
            evidence_type="resource",
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

    def _extract_resource_context(
        self, outcome_data: dict
    ) -> Tuple[Optional[str], Optional[float]]:
        """
        Extract resource name and change from outcome data.

        Args:
            outcome_data: The outcome data dictionary

        Returns:
            Tuple of (resource_name, change_amount) or (None, None)
        """
        context = outcome_data.get("context", ())
        if isinstance(context, dict):
            resource = context.get("resource")
            amount = context.get("amount")
            if resource:
                return (
                    resource
                    if isinstance(resource, str)
                    else str(resource),
                    float(amount) if amount is not None else 0.0,
                )

        return None, None

    def _infer_evidence_kind(self, change: Optional[float]) -> EvidenceKind:
        """
        Infer evidence kind from resource change.

        Args:
            change: The resource change amount (positive = gain, negative = loss)

        Returns:
            Inferred evidence kind
        """
        if change is None or change == 0:
            return "resource_preserved"
        elif change > 0:
            if change >= 1.0:
                return "resource_acquired"
            else:
                return "resource_renewed"
        else:
            if change <= -1.0:
                return "resource_lost"
            else:
                return "resource_depleted"

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
            "resource_acquired": 0.9,
            "resource_lost": 0.9,
            "resource_preserved": 0.85,
            "resource_depleted": 0.8,
            "resource_renewed": 0.75,
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
            if "resource" in context and "amount" in context:
                return 0.2
        return 0.4