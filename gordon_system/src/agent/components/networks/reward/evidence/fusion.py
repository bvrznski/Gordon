# Reward Network - Evidence Fusion
# ================================

"""
Evidence fusion module.

Fuses multiple evidence items into integrated evidence while preserving
provenance, confidence, and uncertainty information.
"""

from __future__ import annotations

from typing import Tuple, Optional

from .evidence import (
    RewardEvidence,
    EvidenceType,
    EvidenceKind,
)


class EvidenceFusion:
    """
    Fuses multiple evidence items into integrated evidence.

    Fusion combines evidence from multiple sources while preserving
    provenance, confidence, uncertainty, and relationships. Each fusion
    is deterministic and does not create new evidence values.

    FUSION PROPERTIES:
        • is_stateless: True - no internal state
        • is_deterministic: True - same inputs always produce same output
        • preserves_evidence: True - all input evidence is preserved

    FUSION INVARIANTS:
        • Fusion never discards any evidence
        • Fusion never infers reward values
        • Fusion preserves provenance chains
        • Fusion combines confidence and uncertainty appropriately
    """

    def __init__(self) -> None:
        """Initialize the fusion engine."""
        self._fusion_strategies: dict[str, str] = {
            "evidence": "combine",
            "confidence": "weighted_average",
            "uncertainty": "max",
            "timescale": "earliest",
        }

    @property
    def is_stateless(self) -> bool:
        """Check if this fusion engine maintains no state."""
        return True

    @property
    def is_deterministic(self) -> bool:
        """Check if this fusion engine always produces same output."""
        return True

    def fuse(
        self, evidences: Tuple[RewardEvidence, ...]
    ) -> RewardEvidence | None:
        """
        Fuse multiple evidence items into a single integrated evidence.

        Args:
            evidences: Tuple of evidence items to fuse

        Returns:
            Fused Evidence or None if no valid evidence
        """
        if not evidences:
            return None

        # Filter out None values
        valid_evidences = tuple(e for e in evidences if e is not None)

        if not valid_evidences:
            return None

        # If only one evidence, return it directly
        if len(valid_evidences) == 1:
            return valid_evidences[0]

        # Perform fusion
        fused = self._fuse_multiple(valid_evidences)

        return fused

    def _fuse_multiple(
        self, evidences: Tuple[RewardEvidence, ...]
    ) -> RewardEvidence:
        """
        Fuse multiple evidence items.

        Args:
            evidences: Tuple of evidence items to fuse (at least 2)

        Returns:
            Fused Evidence
        """
        # Collect data from all evidences
        evidence_ids = tuple(e.evidence_id for e in evidences)
        evidence_types = tuple(set(e.evidence_type for e in evidences))
        evidence_kinds = tuple(set(e.evidence_kind for e in evidences))

        # Combine semantic content (join with separator)
        semantic_contents = tuple(
            e.semantic_content for e in evidences
        )
        combined_semantic = "; ".join(semantic_contents)

        # Determine relationship
        relationships = tuple(e.relationship for e in evidences)
        dominant_relationship = self._fuse_relationships(relationships)

        # Compute fused confidence
        confidences = tuple(e.confidence for e in evidences)
        fused_confidence = self._fuse_confidence(confidences)

        # Compute fused uncertainty
        uncertainties = tuple(e.uncertainty for e in evidences)
        fused_uncertainty = self._fuse_uncertainty(uncertainties)

        # Collect outcome references
        all_outcome_refs: list[str] = []
        for e in evidences:
            all_outcome_refs.extend(e.outcome_ref)
        fused_outcome_ref = tuple(set(all_outcome_refs))

        # Collect contexts
        all_contexts: list[str] = []
        for e in evidences:
            all_contexts.extend(e.context)
        fused_context = tuple(set(all_contexts))

        # Use the earliest timescale
        timescales = tuple(e.timescale for e in evidences)
        fused_timescale = self._fuse_timescales(timescales)

        # Build fused evidence
        return RewardEvidence.create(
            evidence_id=f"fusion-{'-'.join(evidence_ids[:3])}",
            evidence_type="integrated",
            evidence_kind="fused_evidence",
            outcome_ref=fused_outcome_ref,
            semantic_content=combined_semantic,
            relationship=dominant_relationship,
            confidence=fused_confidence,
            uncertainty=fused_uncertainty,
            timescale=fused_timescale,
            context=fused_context,
            derived_from=evidence_ids,
        )

    def _fuse_relationships(
        self, relationships: Tuple[str, ...]
    ) -> str:
        """
        Fuse relationship values.

        Args:
            relationships: Tuple of relationship strings

        Returns:
            Fused relationship string
        """
        if not relationships:
            return "unknown"

        # Check for contradictions
        supports_reward_count = sum(
            1 for r in relationships if r == "supports_reward"
        )
        supports_punishment_count = sum(
            1 for r in relationships if r == "supports_punishment"
        )

        if supports_reward_count > supports_punishment_count:
            return "supports_reward"
        elif supports_punishment_count > supports_reward_count:
            return "supports_punishment"
        else:
            # Return first non-unknown relationship or unknown
            for r in relationships:
                if r != "unknown":
                    return r
            return "unknown"

    def _fuse_confidence(
        self, confidences: Tuple[float, ...]
    ) -> float:
        """
        Fuse confidence values using weighted average.

        Args:
            confidences: Tuple of confidence values (0.0 to 1.0)

        Returns:
            Fused confidence value
        """
        if not confidences:
            return 0.5

        # Simple average for now
        return sum(confidences) / len(confidences)

    def _fuse_uncertainty(
        self, uncertainties: Tuple[float, ...]
    ) -> float:
        """
        Fuse uncertainty values.

        Args:
            uncertainties: Tuple of uncertainty values (0.0 to 1.0)

        Returns:
            Fused uncertainty value
        """
        if not uncertainties:
            return 0.0

        # Use maximum uncertainty for safety
        return max(uncertainties)

    def _fuse_timescales(
        self, timescales: Tuple[str, ...]
    ) -> str:
        """
        Fuse timescale values.

        Args:
            timescales: Tuple of timescale strings

        Returns:
            Fused timescale string (earliest/most specific)
        """
        if not timescales:
            return "immediate"

        # Order from immediate to longest-term
        timescale_order = {
            "immediate": 0,
            "short_term": 1,
            "medium_term": 2,
            "long_term": 3,
            "persistent": 4,
            "predicted": 5,
        }

        # Return the earliest (lowest order)
        min_order = float("inf")
        result = "immediate"
        for ts in timescales:
            order = timescale_order.get(ts, 10)
            if order < min_order:
                min_order = order
                result = ts

        return result


def fuse_evidence(
    evidences: Tuple[RewardEvidence, ...],
) -> RewardEvidence | None:
    """
    Convenience function to fuse evidence items.

    Args:
        evidences: Tuple of evidence items to fuse

    Returns:
        Fused Evidence or None
    """
    fusion = EvidenceFusion()
    return fusion.fuse(evidences)