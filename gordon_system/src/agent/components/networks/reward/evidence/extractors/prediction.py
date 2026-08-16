# Reward Network - Prediction Evidence Extractor
# ==============================================

"""
Prediction evidence extractor.

Extracts semantic evidence about prediction accuracy and prediction errors.
"""

from __future__ import annotations

from typing import Tuple, Optional

from ..evidence import (
    RewardEvidence,
    EvidenceType,
    EvidenceKind,
)
from .base import EvidenceExtractor


class PredictionEvidenceExtractor(EvidenceExtractor):
    """
    Extractor for prediction-level semantic evidence.

    Transforms outcomes into semantic evidence about predictive processing
    accuracy and errors. Each extraction is deterministic and preserves
    provenance.

    EXTRACTOR PROPERTIES:
        • extractor_type: 'prediction'
        • is_stateless: True
        • is_deterministic: True

    EVIDENCE KINDS PRODUCED:
        • prediction_success: Predictive accuracy confirmed
        • prediction_failure: Prediction error occurred
        • prediction_improved: Prediction model improved
        • prediction_degraded: Prediction model degraded
        • unexpected_success: Unpredicted positive outcome
        • unexpected_failure: Unpredicted negative outcome

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

    extractor_type: str = "prediction"

    def extract(
        self,
        outcome_id: str,
        outcome_data: dict,
    ) -> Tuple[RewardEvidence, ...]:
        """
        Extract evidence from an outcome about predictions.

        Args:
            outcome_id: The Outcome ID to extract from
            outcome_data: The outcome data dictionary

        Returns:
            Tuple of extracted RewardEvidence items (empty if none found)
        """
        prediction_info = self._extract_prediction_context(outcome_data)
        if not prediction_info:
            return ()

        prediction_name, is_success, is_expected = prediction_info

        evidence_kind = self._infer_evidence_kind(
            is_success, is_expected
        )

        semantic_content = f"Outcome {outcome_id} indicates {'successful' if is_success else 'failed'} prediction for '{prediction_name}' (expected: {is_expected})"

        relationship = (
            "supports_reward"
            if is_success and is_expected
            else "supports_punishment"
            if not is_success
            else "unknown"
        )

        evidence = RewardEvidence.create(
            evidence_id=f"{outcome_id}-prediction-evidence",
            evidence_type="prediction",
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

    def _extract_prediction_context(
        self, outcome_data: dict
    ) -> Tuple[Optional[str], Optional[bool], Optional[bool]]:
        """
        Extract prediction name and success state from outcome data.

        Args:
            outcome_data: The outcome data dictionary

        Returns:
            Tuple of (prediction_name, is_success, is_expected) or (None, None, None)
        """
        context = outcome_data.get("context", ())
        if isinstance(context, dict):
            prediction = context.get("prediction")
            success = context.get("success")
            expected = context.get("expected")
            if prediction:
                return (
                    prediction
                    if isinstance(prediction, str)
                    else str(prediction),
                    bool(success) if success is not None else True,
                    bool(expected) if expected is not None else True,
                )

        return None, None, None

    def _infer_evidence_kind(
        self, is_success: Optional[bool], is_expected: Optional[bool]
    ) -> EvidenceKind:
        """
        Infer evidence kind from prediction success and expectation.

        Args:
            is_success: Whether the prediction succeeded
            is_expected: Whether the outcome was expected

        Returns:
            Inferred evidence kind
        """
        if is_success is None:
            return "prediction_improved"

        if is_success:
            if is_expected:
                return "prediction_success"
            else:
                return "unexpected_success"
        else:
            if is_expected:
                return "prediction_failure"
            else:
                return "unexpected_failure"

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
            "prediction_success": 0.95,
            "prediction_failure": 0.95,
            "prediction_improved": 0.85,
            "prediction_degraded": 0.8,
            "unexpected_success": 0.7,
            "unexpected_failure": 0.7,
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
            if "prediction" in context and "success" in context:
                return 0.2
        return 0.4