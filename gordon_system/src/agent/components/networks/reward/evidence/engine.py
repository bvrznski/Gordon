# Reward Network - Evidence Engine
# ================================

"""
Evidence engine for Phase 4.10.2.

The Evidence Engine orchestrates evidence extraction, normalization,
attribution, and graph construction from outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional

from ..evidence.evidence import RewardEvidence
from ..evidence.graph import RewardEvidenceGraph
from ..evidence.state import RewardEvidenceState
from ..evidence.request import RewardEvidenceRequest
from ..evidence.result import RewardEvidenceResult
from ..evidence.validation import (
    EvidenceValidation,
    ValidationResult,
)

# Import extractors
from ..evidence.extractors.outcome import OutcomeEvidenceExtractor
from ..evidence.extractors.goal import GoalEvidenceExtractor
from ..evidence.extractors.resource import ResourceEvidenceExtractor
from ..evidence.extractors.constraint import ConstraintEvidenceExtractor
from ..evidence.extractors.behavior import BehaviorEvidenceExtractor
from ..evidence.extractors.prediction import PredictionEvidenceExtractor
from ..evidence.extractors.context import ContextEvidenceExtractor
from ..evidence.extractors.history import HistoryEvidenceExtractor

# Import normalization and fusion
from ..evidence.normalization import EvidenceNormalizer
from ..evidence.fusion import EvidenceFusion


@dataclass(frozen=True)
class RewardEvidenceEngine:
    """
    Orchestrates evidence extraction from outcomes.

    The engine validates inputs, extracts semantic evidence, normalizes it,
    attributes provenance, constructs the evidence graph and state.

    EVIDENCE PIPELINE:
        validate request
            ↓
        validate outcomes
            ↓
        extract semantic evidence (parallel by extractor)
            ↓
        normalize evidence
            ↓
        attribute evidence
            ↓
        estimate confidence & uncertainty
            ↓
        construct evidence graph
            ↓
        construct evidence state
            ↓
        validation
            ↓
        RewardEvidenceResult

    PROPERTIES:
        • deterministic: Same inputs produce same outputs
        • immutable: No state modifications during processing
        • traceable: Full provenance preserved

    NOT RESPONSIBLE FOR:
        • Learning (reinforcement, policy updates)
        • Executive decisions
        • Action selection
        • State modification
    """

    # Extractors for different evidence domains
    outcome_extractor: OutcomeEvidenceExtractor = field(default_factory=OutcomeEvidenceExtractor)
    goal_extractor: GoalEvidenceExtractor = field(default_factory=GoalEvidenceExtractor)
    resource_extractor: ResourceEvidenceExtractor = field(default_factory=ResourceEvidenceExtractor)
    constraint_extractor: ConstraintEvidenceExtractor = field(default_factory=ConstraintEvidenceExtractor)
    behavior_extractor: BehaviorEvidenceExtractor = field(default_factory=BehaviorEvidenceExtractor)
    prediction_extractor: PredictionEvidenceExtractor = field(default_factory=PredictionEvidenceExtractor)
    context_extractor: ContextEvidenceExtractor = field(default_factory=ContextEvidenceExtractor)
    history_extractor: HistoryEvidenceExtractor = field(default_factory=HistoryEvidenceExtractor)

    # Processing components
    normalizer: EvidenceNormalizer = field(default_factory=EvidenceNormalizer)
    fusion: EvidenceFusion = field(default_factory=EvidenceFusion)

    def process(
        self,
        request: RewardEvidenceRequest,
    ) -> RewardEvidenceResult:
        """
        Process an evidence request and return a result.

        Args:
            request: The evidence processing request

        Returns:
            RewardEvidenceResult with all extracted evidence
        """
        trace = ("REQUEST_RECEIVED",)

        # Validate request
        validation_result = self._validate_request(request)
        if not validation_result.is_valid:
            return RewardEvidenceResult.create(
                state_id="invalid-request",
                evidences=tuple(),
                status="failure",
                findings=validation_result.findings,
                trace=trace + ("VALIDATION_FAILED",),
                limitations=("request_validation_failed",),
            )
        trace += ("REQUEST_VALIDATED",)

        # Validate outcomes
        outcomes = request.outcomes or tuple()
        outcome_validation = self._validate_outcomes(outcomes)
        if not outcome_validation.is_valid:
            return RewardEvidenceResult.create(
                state_id="invalid-outcomes",
                evidences=tuple(),
                status="failure",
                findings=outcome_validation.findings,
                trace=trace + ("OUTCOME_VALIDATION_FAILED",),
                limitations=("outcome_validation_failed",),
            )
        trace += ("OUTCOMES_VALIDATED",)

        # Extract evidence from each outcome
        extracted_evidences: list[RewardEvidence] = []
        for i, outcome in enumerate(outcomes):
            outcome_id = outcome.get("outcome_id", f"unknown-{i}")

            # Extract evidence using all extractors
            extractor_results = self._extract_from_outcome(
                outcome_id=outcome_id,
                outcome_data=outcome,
            )
            extracted_evidences.extend(extractor_results)
            trace += (f"EVIDENCE_EXTRACTED_FROM_OUTCOME_{i}",)

        # Normalize all extracted evidence
        normalized_evidences = self.normalizer.normalize_batch(tuple(extracted_evidences))
        trace += ("EVIDENCE_NORMALIZED",)

        # Fuse evidence where applicable
        fused_evidences = self._fuse_evidence(normalized_evidences)
        trace += ("EVIDENCE_FUSED",)

        # Construct graph
        evidence_graph = self._construct_graph(fused_evidences, trace)
        trace += ("GRAPH_CREATED",)

        # Estimate confidence and uncertainty
        confidence = self._estimate_overall_confidence(fused_evidences)
        uncertainty = self._estimate_overall_uncertainty(fused_evidences)

        # Build state
        evidence_state = RewardEvidenceState.create(
            state_id=request.identity,
            evidences=fused_evidences,
            graph=evidence_graph,
            confidence=confidence,
            uncertainty=uncertainty,
            trace=trace,
        )
        trace += ("STATE_CREATED",)

        # Final validation
        state_validation = self._validate_state(evidence_state)
        if not state_validation.is_valid:
            return RewardEvidenceResult.create(
                state_id=request.identity,
                evidences=fused_evidences,
                graph=evidence_graph,
                confidence=confidence,
                uncertainty=uncertainty,
                status="partial_success",
                findings=state_validation.findings + ("state_validation_failed",),
                trace=trace + ("STATE_VALIDATION_FAILED",),
            )
        trace += ("VALIDATION_COMPLETED",)

        return RewardEvidenceResult.create(
            state_id=request.identity,
            evidences=fused_evidences,
            graph=evidence_graph,
            confidence=confidence,
            uncertainty=uncertainty,
            status="success",
            findings=("processed_" + str(len(outcomes)) + "_outcomes",),
            trace=trace,
        )

    def _validate_request(self, request: RewardEvidenceRequest) -> ValidationResult:
        """Validate an evidence request."""
        return EvidenceValidation.validate_request(request)

    def _validate_outcomes(
        self, outcomes: Tuple[dict, ...]
    ) -> ValidationResult:
        """Validate a set of outcomes."""
        trace = ("VALIDATE_OUTCOMES",)

        for i, outcome in enumerate(outcomes):
            if not isinstance(outcome, dict):
                return ValidationResult.invalid(
                    f"INVALID_OUTCOME_TYPE_{i}",
                    "Expected dictionary",
                )

        trace += ("OUTCOMES_VALIDATED",)
        return ValidationResult.valid(trace=trace)

    def _extract_from_outcome(
        self,
        outcome_id: str,
        outcome_data: dict,
    ) -> list[RewardEvidence]:
        """
        Extract evidence from an outcome using all extractors.

        Args:
            outcome_id: The outcome identifier
            outcome_data: The outcome data dictionary

        Returns:
            List of extracted evidence items
        """
        evidences = []

        # Use each extractor to get evidence
        for extractor in (
            self.outcome_extractor,
            self.goal_extractor,
            self.resource_extractor,
            self.constraint_extractor,
            self.behavior_extractor,
            self.prediction_extractor,
            self.context_extractor,
            self.history_extractor,
        ):
            extracted = extractor.extract(outcome_id, outcome_data)
            evidences.extend(extracted)

        return evidences

    def _fuse_evidence(
        self, evidences: Tuple[RewardEvidence, ...]
    ) -> Tuple[RewardEvidence, ...]:
        """
        Fuse related evidence items.

        Args:
            evidences: All extracted evidence items

        Returns:
            Fused evidence items
        """
        if not evidences:
            return tuple()

        # Simple fusion: group by type and fuse within groups
        fused: list[RewardEvidence] = []

        # Group evidence by type for potential fusion
        by_type: dict[str, list[RewardEvidence]] = {}
        for e in evidences:
            e_type = e.evidence_type
            if e_type not in by_type:
                by_type[e_type] = []
            by_type[e_type].append(e)

        # Fuse within each type
        for e_type, items in by_type.items():
            if len(items) == 1:
                fused.append(items[0])
            else:
                # Fuse multiple from same type
                fused_item = self.fusion.fuse(tuple(items))
                if fused_item:
                    fused.append(fused_item)

        return tuple(fused)

    def _construct_graph(
        self,
        evidences: Tuple[RewardEvidence, ...],
        trace: Tuple[str, ...],
    ) -> Optional[RewardEvidenceGraph]:
        """
        Construct an evidence graph from evidence items.

        Args:
            evidences: All evidence items
            trace: Current processing trace

        Returns:
            Evidence graph or None if no evidence
        """
        if not evidences:
            return None

        node_ids = tuple(e.evidence_id for e in evidences)

        return RewardEvidenceGraph.create(
            graph_id=f"evidence-graph-{len(node_ids)}",
            nodes=node_ids,
            edges=tuple(),
            timescales=tuple(set(e.timescale for e in evidences)),
            provenance=trace[-1] if trace else None,
        )

    def _estimate_overall_confidence(
        self, evidences: Tuple[RewardEvidence, ...]
    ) -> float:
        """
        Estimate overall confidence from evidence.

        Args:
            evidences: All evidence items

        Returns:
            Overall confidence value (0.0 to 1.0)
        """
        if not evidences:
            return 0.5

        # Average confidence across all evidence
        total_confidence = sum(e.confidence for e in evidences)
        return total_confidence / len(evidences)

    def _estimate_overall_uncertainty(
        self, evidences: Tuple[RewardEvidence, ...]
    ) -> float:
        """
        Estimate overall uncertainty from evidence.

        Args:
            evidences: All evidence items

        Returns:
            Overall uncertainty value (0.0 to 1.0)
        """
        if not evidences:
            return 0.5

        # Average uncertainty across all evidence
        total_uncertainty = sum(e.uncertainty for e in evidences)
        return total_uncertainty / len(evidences)

    def _validate_state(self, state: RewardEvidenceState) -> ValidationResult:
        """Validate an evidence state."""
        trace = ("VALIDATE_STATE",)

        # Check that all evidence is valid
        for i, evidence in enumerate(state.evidences):
            if not isinstance(evidence, RewardEvidence):
                return ValidationResult.invalid(
                    f"INVALID_EVIDENCE_TYPE_{i}",
                )

        trace += ("STATE_VALIDATED",)
        return ValidationResult.valid(trace=trace)


def process_evidence_request(
    request: RewardEvidenceRequest,
) -> RewardEvidenceResult:
    """
    Convenience function to process an evidence request.

    Args:
        request: The evidence processing request

    Returns:
        RewardEvidenceResult with all extracted evidence
    """
    engine = RewardEvidenceEngine()
    return engine.process(request)