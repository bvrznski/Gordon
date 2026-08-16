# Gordon Cognitive Architecture - Phase 4.5.5
# Action Evaluation Validation
# ============================

"""
Validation utilities for Action Evaluation types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# VALIDATION RESULT TYPES
# =============================================================================

@dataclass(frozen=True, slots=True)
class EvaluationValidationResult:
    """
    Result of validating an evaluation artifact.

    PROPERTIES:
        - is_valid: Whether the artifact passed validation
        - errors: List of validation error messages
        - warnings: List of validation warning messages
        - normalized: Whether the artifact was normalized during validation
    """

    is_valid: bool = True
    """Whether the artifact passed validation."""

    errors: Tuple[str, ...] = field(default_factory=tuple)
    """List of validation error messages."""

    warnings: Tuple[str, ...] = field(default_factory=tuple)
    """List of validation warning messages."""

    normalized: bool = False
    """Whether the artifact was normalized during validation."""

    @classmethod
    def valid(cls) -> EvaluationValidationResult:
        """Create a valid validation result."""
        return cls(is_valid=True)

    @classmethod
    def invalid(cls, errors: Tuple[str, ...]) -> EvaluationValidationResult:
        """Create an invalid validation result with errors."""
        return cls(is_valid=False, errors=errors)

    @classmethod
    def with_warnings(
        cls,
        warnings: Tuple[str, ...],
        normalized: bool = False,
    ) -> EvaluationValidationResult:
        """Create a valid result with warnings."""
        return cls(is_valid=True, warnings=warnings, normalized=normalized)


# =============================================================================
# VALIDATION RULES FOR EVALUATION ARTIFACTS
# =============================================================================

def validate_dimension_score(score: float) -> Tuple[str, ...]:
    """
    Validate that a dimension score is within valid bounds.

    Args:
        score: The score to validate (0.0 to 1.0)

    Returns:
        Empty tuple if valid, error messages otherwise
    """
    errors = []
    if not isinstance(score, (int, float)):
        errors.append(f"Score must be numeric, got {type(score).__name__}")
    elif score < 0.0 or score > 1.0:
        errors.append(f"Score must be between 0.0 and 1.0, got {score}")
    return tuple(errors)


def validate_confidence_uncertainty_pair(
    confidence: float,
    uncertainty: float,
) -> Tuple[str, ...]:
    """
    Validate a confidence-uncertainty pair.

    Confidence and uncertainty are distinct but should be reasonable.
    This doesn't enforce sum = 1.0 (they can both be low or both high).

    Args:
        confidence: Confidence level (0.0 to 1.0)
        uncertainty: Uncertainty level (0.0 to 1.0)

    Returns:
        Empty tuple if valid, error messages otherwise
    """
    errors = []

    confidence_errors = validate_dimension_score(confidence)
    errors.extend(confidence_errors)

    uncertainty_errors = validate_dimension_score(uncertainty)
    errors.extend(uncertainty_errors)

    return tuple(errors)


def validate_candidate_id(candidate_id: str) -> Tuple[str, ...]:
    """
    Validate a candidate ID.

    Args:
        candidate_id: The candidate ID to validate

    Returns:
        Empty tuple if valid, error messages otherwise
    """
    errors = []
    if not isinstance(candidate_id, str):
        errors.append(f"Candidate ID must be a string, got {type(candidate_id).__name__}")
    elif len(candidate_id) == 0:
        errors.append("Candidate ID cannot be empty")
    return tuple(errors)


def validate_evaluation_revision(revision: int) -> Tuple[str, ...]:
    """
    Validate an evaluation revision number.

    Args:
        revision: The revision number to validate

    Returns:
        Empty tuple if valid, error messages otherwise
    """
    errors = []
    if not isinstance(revision, int):
        errors.append(f"Revision must be an integer, got {type(revision).__name__}")
    elif revision < 1:
        errors.append(f"Revision must be >= 1, got {revision}")
    return tuple(errors)


# =============================================================================
# VALIDATOR FOR COMPLEX ARTIFACTS
# =============================================================================

@dataclass(frozen=True, slots=True)
class EvaluationValidator:
    """
    Validator for Action Evaluation artifacts.
    """

    @classmethod
    def validate_dimension_result(
        cls,
        dimension_name: str,
        score: float,
        confidence: float,
        uncertainty: float,
    ) -> EvaluationValidationResult:
        """
        Validate a dimension result.

        Args:
            dimension_name: Name of the dimension
            score: Dimension score (0.0 to 1.0)
            confidence: Confidence in assessment (0.0 to 1.0)
            uncertainty: Uncertainty about assessment (0.0 to 1.0)

        Returns:
            Validation result with any errors/warnings
        """
        errors = []

        if not dimension_name or len(dimension_name) == 0:
            errors.append("Dimension name cannot be empty")

        score_errors = validate_dimension_score(score)
        errors.extend(score_errors)

        confidence_errors, uncertainty_errors = (
            validate_confidence_uncertainty_pair(confidence, uncertainty)
        )
        errors.extend(confidence_errors)
        errors.extend(uncertainty_errors)

        if errors:
            return EvaluationValidationResult.invalid(tuple(errors))

        return EvaluationValidationResult.valid()

    @classmethod
    def validate_conflict_record(
        cls,
        conflict_id: str,
        conflict_type: str,
        affected_candidates: Tuple[str, ...],
        severity: float,
    ) -> EvaluationValidationResult:
        """
        Validate a conflict record.

        Args:
            conflict_id: Unique identifier for the conflict
            conflict_type: Type of conflict
            affected_candidates: IDs of candidates involved
            severity: Conflict severity (0.0 to 1.0)

        Returns:
            Validation result with any errors/warnings
        """
        errors = []

        id_errors = validate_candidate_id(conflict_id)
        errors.extend(id_errors)

        if not isinstance(affected_candidates, tuple):
            errors.append("Affected candidates must be a tuple")

        severity_errors = validate_dimension_score(severity)
        errors.extend(severity_errors)

        if errors:
            return EvaluationValidationResult.invalid(tuple(errors))

        return EvaluationValidationResult.valid()

    @classmethod
    def validate_interference_record(
        cls,
        interference_id: str,
        strength: float,
    ) -> EvaluationValidationResult:
        """
        Validate an interference record.

        Args:
            interference_id: Unique identifier for the interference
            strength: Interference strength (0.0 to 1.0)

        Returns:
            Validation result with any errors/warnings
        """
        errors = []

        id_errors = validate_candidate_id(interference_id)
        errors.extend(id_errors)

        strength_errors = validate_dimension_score(strength)
        errors.extend(strength_errors)

        if errors:
            return EvaluationValidationResult.invalid(tuple(errors))

        return EvaluationValidationResult.valid()