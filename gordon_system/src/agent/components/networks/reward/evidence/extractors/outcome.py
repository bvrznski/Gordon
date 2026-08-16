# Reward Network - Outcome Evidence Extractor
# ===========================================

"""
Outcome evidence extractor.

Extracts semantic evidence from outcomes based on their category, context,
and properties. Produces outcome-level evidence items.
"""

from __future__ import annotations

from typing import Tuple, Optional

from ..evidence import (
    RewardEvidence,
    EvidenceType,
    EvidenceKind,
)
from .base import EvidenceExtractor


class OutcomeEvidenceExtractor(EvidenceExtractor):
    """
    Extractor for outcome-level semantic evidence.

    Transforms outcomes into semantic evidence supporting or contradicting
    reward estimates. Each extraction is deterministic and preserves provenance.

    EXTRACTOR PROPERTIES:
        • extractor_type: 'outcome'
        • is_stateless: True
        • is_deterministic: True

    EVIDENCE KINDS PRODUCED:
        • goal_progress: Goal advancement detected from completed tasks
        • goal_retreat: Goal regression from failed tasks
        • resource_acquired: Resources gained from successful outcomes
        • resource_lost: Resources lost from failed outcomes
        • constraint_satisfied: Constraints met by outcome
        • constraint_violated: Constraints breached by outcome
        • prediction_success: Predictive accuracy confirmed
        • prediction_failure: Prediction error occurred

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

    extractor_type: str = "outcome"

    # Map outcome category kinds to evidence kinds
    CATEGORY_TO_EVIDENCE_KIND: dict[str, EvidenceKind] = {
        "task_completed": "goal_progress",
        "task_failed": "goal_retreat",
        "goal_progress": "goal_progress",
        "resource_acquired": "resource_acquired",
        "resource_lost": "resource_lost",
        "prediction_success": "prediction_success",
        "prediction_failure": "prediction_failure",
        "social_interaction_positive": "constraint_satisfied",
        "social_interaction_negative": "constraint_violated",
        "learning_opportunity": "knowledge_gained",
    }

    def extract(
        self,
        outcome_id: str,
        outcome_data: dict,
    ) -> Tuple[RewardEvidence, ...]:
        """
        Extract evidence from an outcome.

        Args:
            outcome_id: The Outcome ID to extract from
            outcome_data: The outcome data dictionary

        Returns:
            Tuple of extracted RewardEvidence items (empty if none found)
        """
        # Extract outcome properties
        category = outcome_data.get("category", {})
        category_kind = category.get("kind", "unknown")
        context = outcome_data.get("context", tuple())
        source_subsystem = outcome_data.get("source_subsystem")

        # Get evidence kind from category mapping
        evidence_kind = self.CATEGORY_TO_EVIDENCE_KIND.get(
            category_kind, self._infer_evidence_kind(category_kind)
        )

        # Generate semantic content based on category
        semantic_content = self._generate_semantic_content(
            category_kind, outcome_id, context
        )

        # Determine relationship to reward/punishment
        relationship = self._determine_relationship(category_kind)

        # Build evidence item
        evidence = RewardEvidence.create(
            evidence_id=f"{outcome_id}-evidence",
            evidence_type="outcome",
            evidence_kind=evidence_kind,
            outcome_ref=(outcome_id,),
            semantic_content=semantic_content,
            relationship=relationship,
            confidence=self._estimate_confidence(category_kind, outcome_data),
            uncertainty=self._estimate_uncertainty(outcome_data),
            timescale=outcome_data.get("timescale", "immediate"),
            source_subsystem=source_subsystem,
            context=tuple(context) if isinstance(context, list) else context,
        )

        return (evidence,)

    def _infer_evidence_kind(self, category_kind: str) -> EvidenceKind:
        """
        Infer evidence kind from category kind.

        Args:
            category_kind: The outcome category kind

        Returns:
            Inferred evidence kind
        """
        if "success" in category_kind or "complete" in category_kind:
            return "goal_progress"
        elif "fail" in category_kind or "error" in category_kind:
            return "goal_retreat"
        elif "gain" in category_kind or "acquire" in category_kind:
            return "resource_acquired"
        elif "loss" in category_kind or "deplete" in category_kind:
            return "resource_lost"
        else:
            return "unknown"

    def _generate_semantic_content(
        self,
        category_kind: str,
        outcome_id: str,
        context: Tuple[str, ...],
    ) -> str:
        """
        Generate semantic content string for the evidence.

        Args:
            category_kind: The outcome category kind
            outcome_id: The outcome identifier
            context: Semantic context

        Returns:
            Semantic content description
        """
        parts = [f"Outcome {outcome_id}"]
        if context:
            parts.append(f"in context {context[0] if context else ''}")
        parts.append(f"produced {category_kind.replace('_', ' ')}")
        return " ".join(parts)

    def _determine_relationship(self, category_kind: str) -> str:
        """
        Determine the relationship to reward/punishment.

        Args:
            category_kind: The outcome category kind

        Returns:
            Relationship string (supports_reward, supports_punishment, etc.)
        """
        if "success" in category_kind or "complete" in category_kind:
            return "supports_reward"
        elif "fail" in category_kind or "error" in category_kind:
            return "supports_punishment"
        elif "positive" in category_kind or "gain" in category_kind:
            return "supports_reward"
        elif "negative" in category_kind or "loss" in category_kind:
            return "supports_punishment"
        else:
            return "unknown"

    def _estimate_confidence(
        self, category_kind: str, outcome_data: dict
    ) -> float:
        """
        Estimate confidence level for this evidence.

        Args:
            category_kind: The outcome category kind
            outcome_data: The outcome data dictionary

        Returns:
            Confidence value (0.0 to 1.0)
        """
        # Base confidence on outcome clarity
        base_confidence = {
            "task_completed": 0.9,
            "task_failed": 0.9,
            "goal_progress": 0.85,
            "resource_acquired": 0.8,
            "resource_lost": 0.8,
            "prediction_success": 0.95,
            "prediction_failure": 0.95,
        }

        return base_confidence.get(category_kind, 0.5)

    def _estimate_uncertainty(self, outcome_data: dict) -> float:
        """
        Estimate uncertainty level for this evidence.

        Args:
            outcome_data: The outcome data dictionary

        Returns:
            Uncertainty value (0.0 to 1.0)
        """
        # Lower uncertainty if we have more information
        context = outcome_data.get("context", ())
        if len(context) >= 2:
            return 0.1
        elif len(context) == 1:
            return 0.3
        else:
            return 0.5