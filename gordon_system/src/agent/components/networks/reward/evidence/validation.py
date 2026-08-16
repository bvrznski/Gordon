# Reward Network - Evidence Validation
# =====================================

"""
Evidence validation module.

Validates evidence requests, extracted evidence, and constructed graphs.
Produces typed validation findings without modifying semantic models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional

from .evidence import RewardEvidence


ValidationErrorType = str
"""Types of validation errors."""


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """
    Result of a validation pass.

    PROPERTIES:
        • is_valid: Whether validation passed
        • findings: List of validation findings (errors/warnings)
        • trace: Validation trace

    NOT RESPONSIBLE FOR:
        • Modifying outcomes or estimates
        • Making decisions based on validation results
    """

    is_valid: bool
    """Whether validation passed."""

    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Validation findings (errors/warnings)."""

    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Validation trace for provenance."""

    @classmethod
    def valid(cls, trace: Tuple[str, ...] = tuple()) -> ValidationResult:
        """Create a successful validation result."""
        return cls(
            is_valid=True,
            findings=tuple(),
            trace=trace or ("VALIDATION_PASSED",),
        )

    @classmethod
    def invalid(cls, *findings: str, trace: Tuple[str, ...] = tuple()) -> ValidationResult:
        """Create an invalid validation result with findings."""
        return cls(
            is_valid=False,
            findings=findings,
            trace=trace or ("VALIDATION_FAILED",),
        )


@dataclass(frozen=True, slots=True)
class EvidenceValidation:
    """
    Validator for evidence components.

    Provides static validation methods for all evidence network components
    without modifying any state.
    """

    @staticmethod
    def validate_request(request: dict) -> ValidationResult:
        """Validate an evidence request."""
        trace = ("VALIDATE_REQUEST",)

        if not isinstance(request, dict):
            return ValidationResult.invalid(
                "INVALID_REQUEST_TYPE",
                "Expected dictionary request",
            )

        # Check required fields
        if "evidence" not in request and "outcomes" not in request:
            return ValidationResult.invalid(
                "MISSING_EVIDENCE_OR_OUTCOMES_FIELD",
            )

        trace += ("REQUEST_VALIDATED",)
        return ValidationResult.valid(trace=trace)

    @staticmethod
    def validate_evidence(evidence: dict | RewardEvidence) -> ValidationResult:
        """Validate a single evidence item."""
        trace = ("VALIDATE_EVIDENCE",)

        if isinstance(evidence, RewardEvidence):
            # Already validated as RewardEvidence
            return ValidationResult.valid(trace=trace + ("EVIDENCE_VALIDATED",))

        if not isinstance(evidence, dict):
            return ValidationResult.invalid(
                "INVALID_EVIDENCE_TYPE",
                "Expected dictionary or RewardEvidence",
            )

        # Check required fields
        for field_name in ("evidence_id", "semantic_content"):
            if field_name not in evidence:
                return ValidationResult.invalid(
                    f"MISSING_{field_name.upper()}_FIELD",
                )

        trace += ("EVIDENCE_VALIDATED",)
        return ValidationResult.valid(trace=trace)

    @staticmethod
    def validate_graph(graph: dict) -> ValidationResult:
        """Validate an evidence graph."""
        trace = ("VALIDATE_GRAPH",)

        if not isinstance(graph, dict):
            return ValidationResult.invalid(
                "INVALID_GRAPH_TYPE",
                "Expected dictionary graph",
            )

        # Check required fields
        for field_name in ("nodes",):
            if field_name not in graph:
                return ValidationResult.invalid(
                    f"MISSING_{field_name.upper()}_FIELD",
                )

        trace += ("GRAPH_VALIDATED",)
        return ValidationResult.valid(trace=trace)

    @staticmethod
    def validate_state(state: dict) -> ValidationResult:
        """Validate an evidence state."""
        trace = ("VALIDATE_STATE",)

        if not isinstance(state, dict):
            return ValidationResult.invalid(
                "INVALID_STATE_TYPE",
                "Expected dictionary state",
            )

        # Check required fields
        for field_name in ("evidences",):
            if field_name not in state:
                return ValidationResult.invalid(
                    f"MISSING_{field_name.upper()}_FIELD",
                )

        trace += ("STATE_VALIDATED",)
        return ValidationResult.valid(trace=trace)


# =============================================================================
# VALIDATION CONSTANTS (Phase 4.10.2 - Part 3)
# =============================================================================

VALIDATION_ERROR_TYPES = {
    "INVALID_OUTCOME": "Outcome does not conform to schema",
    "UNKNOWN_EVIDENCE": "Evidence type or kind is unknown",
    "INVALID_SCHEMA": "Data structure violates schema",
    "INVALID_POLICY": "Policy reference is invalid",
    "UNSUPPORTED_EXTRACTOR": "Extractor type is not supported",
    "CONTRADICTORY_EVIDENCE": "Evidence items contradict each other",
    "UNKNOWN": "Unknown validation error",
}


def validate_evidence_batch(
    evidences: Tuple[dict | RewardEvidence, ...],
) -> ValidationResult:
    """
    Validate a batch of evidence items.

    Args:
        evidences: Tuple of evidence to validate

    Returns:
        Validation result
    """
    for i, evidence in enumerate(evidences):
        result = EvidenceValidation.validate_evidence(evidence)
        if not result.is_valid:
            return ValidationResult.invalid(
                *result.findings,
                f"evidence_index_{i}_failed",
            )
    return ValidationResult.valid()


def validate_graph_nodes(
    graph: dict,
    valid_node_ids: Tuple[str, ...],
) -> ValidationResult:
    """
    Validate that graph nodes are all valid evidence IDs.

    Args:
        graph: The graph dictionary to validate
        valid_node_ids: Tuple of valid node IDs

    Returns:
        Validation result
    """
    graph_nodes = set(graph.get("nodes", []))
    valid_set = set(valid_node_ids)

    invalid_nodes = graph_nodes - valid_set
    if invalid_nodes:
        return ValidationResult.invalid(
            f"invalid_nodes:{','.join(sorted(invalid_nodes))}",
        )

    return ValidationResult.valid()