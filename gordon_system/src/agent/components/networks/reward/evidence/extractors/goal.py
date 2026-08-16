# Reward Network - Goal Evidence Extractor
# =========================================

"""
Goal evidence extractor.

Extracts semantic evidence about goal progress, completion status,
and motivational context from outcomes.
"""

from __future__ import annotations

from typing import Tuple, Optional

from ..evidence import (
    RewardEvidence,
    EvidenceType,
    EvidenceKind,
)
from .base import EvidenceExtractor


class GoalEvidenceExtractor(EvidenceExtractor):
    """
    Extractor for goal-level semantic evidence.

    Transforms outcomes into semantic evidence about goal progress,
    completion status, and motivational context. Each extraction is
    deterministic and preserves provenance.

    EXTRACTOR PROPERTIES:
        • extractor_type: 'goal'
        • is_stateless: True
        • is_deterministic: True

    EVIDENCE KINDS PRODUCED:
        • goal_progress: Goal advancement detected
        • goal_retreat: Goal regression detected
        • goal_complete: Goal fully achieved
        • goal_abandoned: Goal no longer pursued
        • motivation_aligned: Current action aligns with goals
        • motivation_conflict: Action conflicts with existing goals

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

    extractor_type: str = "goal"

    def extract(
        self,
        outcome_id: str,
        outcome_data: dict,
    ) -> Tuple[RewardEvidence, ...]:
        """
        Extract evidence from an outcome about goals.

        Args:
            outcome_id: The Outcome ID to extract from
            outcome_data: The outcome data dictionary

        Returns:
            Tuple of extracted RewardEvidence items (empty if none found)
        """
        # Extract goal-related properties
        goal_context = self._extract_goal_context(outcome_data)
        if not goal_context:
            return ()  # No goal evidence without goal context

        goal_id, goal_status = goal_context

        # Determine evidence kind based on outcome and goal state
        evidence_kind = self._infer_evidence_kind(
            outcome_data, goal_status
        )

        # Generate semantic content
        semantic_content = self._generate_semantic_content(
            goal_id, evidence_kind, outcome_id
        )

        # Determine relationship to reward/punishment
        relationship = self._determine_relationship(evidence_kind)

        # Build evidence item
        evidence = RewardEvidence.create(
            evidence_id=f"{outcome_id}-goal-evidence",
            evidence_type="goal",
            evidence_kind=evidence_kind,
            outcome_ref=(outcome_id,),
            semantic_content=semantic_content,
            relationship=relationship,
            confidence=self._estimate_confidence(evidence_kind, outcome_data),
            uncertainty=self._estimate_uncertainty(outcome_data),
            timescale=outcome_data.get("timescale", "immediate"),
            source_subsystem=outcome_data.get("source_subsystem"),
            context=goal_context,
        )

        return (evidence,)

    def _extract_goal_context(
        self, outcome_data: dict
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract goal ID and status from outcome data.

        Args:
            outcome_data: The outcome data dictionary

        Returns:
            Tuple of (goal_id, goal_status) or (None, None)
        """
        context = outcome_data.get("context", ())
        if isinstance(context, tuple) and len(context) >= 2:
            return context[0], context[1]

        # Try extracting from context dict
        if isinstance(context, dict):
            goal_id = context.get("goal_id")
            goal_status = context.get("status")
            if goal_id:
                return goal_id, goal_status or "unknown"

        return None, None

    def _infer_evidence_kind(
        self,
        outcome_data: dict,
        goal_status: Optional[str],
    ) -> EvidenceKind:
        """
        Infer evidence kind from outcome and goal state.

        Args:
            outcome_data: The outcome data dictionary
            goal_status: Current goal status (if any)

        Returns:
            Inferred evidence kind
        """
        category = outcome_data.get("category", {})
        category_kind = category.get("kind", "unknown")

        # Check for completion indicators
        if category_kind in ("task_completed",):
            return "goal_complete" if goal_status == "in_progress" else "goal_progress"
        elif category_kind in ("task_failed",):
            return "goal_retreat"

        # Default based on goal status
        if goal_status == "completed":
            return "goal_complete"
        elif goal_status == "abandoned":
            return "goal_abandoned"
        elif goal_status == "in_progress":
            return "goal_progress"
        else:
            return "motivation_aligned"

    def _generate_semantic_content(
        self, goal_id: str, evidence_kind: EvidenceKind, outcome_id: str
    ) -> str:
        """
        Generate semantic content string for the evidence.

        Args:
            goal_id: The goal identifier
            evidence_kind: The type of evidence being produced
            outcome_id: The outcome identifier

        Returns:
            Semantic content description
        """
        kind_description = {
            "goal_progress": "goal advancement",
            "goal_retreat": "goal regression",
            "goal_complete": "goal achievement",
            "goal_abandoned": "goal discontinuation",
            "motivation_aligned": "action-goal alignment",
            "motivation_conflict": "action-goal conflict",
        }

        return f"Outcome {outcome_id} indicates {kind_description.get(evidence_kind, evidence_kind)} for goal {goal_id}"

    def _determine_relationship(self, evidence_kind: EvidenceKind) -> str:
        """
        Determine the relationship to reward/punishment.

        Args:
            evidence_kind: The evidence kind

        Returns:
            Relationship string (supports_reward, supports_punishment, etc.)
        """
        positive_kinds = {
            "goal_progress",
            "goal_complete",
            "motivation_aligned",
        }
        negative_kinds = {
            "goal_retreat",
            "goal_abandoned",
            "motivation_conflict",
        }

        if evidence_kind in positive_kinds:
            return "supports_reward"
        elif evidence_kind in negative_kinds:
            return "supports_punishment"
        else:
            return "unknown"

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
            "goal_progress": 0.8,
            "goal_retreat": 0.8,
            "goal_complete": 0.95,
            "goal_abandoned": 0.75,
            "motivation_aligned": 0.7,
            "motivation_conflict": 0.65,
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
        # Lower uncertainty if we have explicit goal info
        context = outcome_data.get("context", ())
        if isinstance(context, dict):
            if "goal_id" in context and "status" in context:
                return 0.2
        elif len(context) >= 2:
            return 0.3

        return 0.5