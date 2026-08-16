# Motivational Projection Network - Validation (Phase 4.10.6)
# =============================================================

"""
MotivationalProjectionValidator for Phase 4.10.6.

This module defines validation functions and error types for the
motivational projection system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, List


@dataclass(frozen=True)
class ValidationIssue:
    """A single validation issue found during validation."""

    issue_id: str
    """Unique identifier for this issue."""

    severity: str = "warning"
    """Severity level (error/warning/notice)."""

    message: str = ""
    """Human-readable description of the issue."""

    context: Tuple[str, ...] = field(default_factory=tuple)
    """Context information (e.g., projection IDs involved)."""

    @property
    def is_error(self) -> bool:
        return self.severity == "error"

    @property
    def is_warning(self) -> bool:
        return self.severity == "warning"


@dataclass(frozen=True)
class ValidationResult:
    """Result of validation."""

    valid: bool
    """Whether validation passed (no errors)."""

    issues: Tuple[ValidationIssue, ...]
    """All validation issues found."""

    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Additional findings from validation."""


class MotivationalProjectionValidator:
    """
    Validator for motivational projection components.

    VALIDATION-LAW-001: Validation precedes projection.
    VALIDATION-LAW-002: Validation remains side-effect free.
    VALIDATION-LAW-003: Validation shall never mutate semantic models.
    """

    def __init__(self):
        """Initialize the validator."""
        self.issues: List[ValidationIssue] = []

    def validate_projection(self, projection: dict) -> ValidationResult:
        """
        Validate a drive projection.

        Args:
            projection: Projection data dictionary

        Returns:
            ValidationResult with any issues found
        """
        self.issues = []
        findings: List[str] = []

        # Check required fields
        if "projection_id" not in projection:
            self.issues.append(ValidationIssue(
                issue_id="MISSING_PROJECTION_ID",
                severity="error",
                message="Projection missing projection_id",
            ))

        if "target_drive" not in projection:
            self.issues.append(ValidationIssue(
                issue_id="MISSING_TARGET_DRIVE",
                severity="error",
                message="Projection missing target_drive",
            ))

        # Validate confidence/uncertainty range
        conf = projection.get("confidence", 1.0)
        unc = projection.get("uncertainty", 0.0)

        if not (0.0 <= conf <= 1.0):
            self.issues.append(ValidationIssue(
                issue_id="INVALID_CONFIDENCE",
                severity="error",
                message=f"Confidence must be in [0.0, 1.0], got {conf}",
                context=(projection.get("projection_id", "unknown"),),
            ))

        if not (0.0 <= unc <= 1.0):
            self.issues.append(ValidationIssue(
                issue_id="INVALID_UNCERTAINTY",
                severity="error",
                message=f"Uncertainty must be in [0.0, 1.0], got {unc}",
                context=(projection.get("projection_id", "unknown"),),
            ))

        if conf + unc > 1.1:
            self.issues.append(ValidationIssue(
                issue_id="CONFIDENCY_UNCERTAINTY_SUM",
                severity="warning",
                message=f"Confidence + uncertainty > 1.0 ({conf} + {unc})",
                context=(projection.get("projection_id", "unknown"),),
            ))

        findings.append(f"Projection validated: {len(self.issues)} issues")

        return ValidationResult(
            valid=all(not i.is_error for i in self.issues),
            issues=tuple(self.issues),
            findings=tuple(findings),
        )

    def validate_tension(self, tension: dict) -> ValidationResult:
        """Validate a motivational tension."""
        self.issues = []

        if "tension_id" not in tension:
            self.issues.append(ValidationIssue(
                issue_id="MISSING_TENSION_ID",
                severity="error",
                message="Tension missing tension_id",
            ))

        participants = tension.get("participating_projections", ())
        if len(participants) < 2:
            self.issues.append(ValidationIssue(
                issue_id="INSUFFICIENT_PARTICIPANTS",
                severity="error",
                message=f"Tension must have at least 2 participants, got {len(participants)}",
            ))

        return ValidationResult(
            valid=all(not i.is_error for i in self.issues),
            issues=tuple(self.issues),
        )

    def validate_synergy(self, synergy: dict) -> ValidationResult:
        """Validate a motivational synergy."""
        self.issues = []

        if "synergy_id" not in synergy:
            self.issues.append(ValidationIssue(
                issue_id="MISSING_SYNERGY_ID",
                severity="error",
                message="Synergy missing synergy_id",
            ))

        participants = synergy.get("participating_projections", ())
        if len(participants) < 2:
            self.issues.append(ValidationIssue(
                issue_id="INSUFFICIENT_PARTICIPANTS",
                severity="error",
                message=f"Synergy must have at least 2 participants, got {len(participants)}",
            ))

        return ValidationResult(
            valid=all(not i.is_error for i in self.issues),
            issues=tuple(self.issues),
        )

    def validate_field(self, field_data: dict) -> ValidationResult:
        """Validate a motivational reward field."""
        self.issues = []

        if "field_id" not in field_data:
            self.issues.append(ValidationIssue(
                issue_id="MISSING_FIELD_ID",
                severity="error",
                message="Field missing field_id",
            ))

        # Check projections exist
        projections = field_data.get("drive_projections", ())
        if len(projections) == 0:
            self.issues.append(ValidationIssue(
                issue_id="EMPTY_PROJECTIONS",
                severity="warning",
                message="Field has no projections",
            ))

        return ValidationResult(
            valid=all(not i.is_error for i in self.issues),
            issues=tuple(self.issues),
        )

    def validate_state(self, state_data: dict) -> ValidationResult:
        """Validate a motivational projection state."""
        self.issues = []

        if "state_id" not in state_data:
            self.issues.append(ValidationIssue(
                issue_id="MISSING_STATE_ID",
                severity="error",
                message="State missing state_id",
            ))

        field_data = state_data.get("motivational_reward_field", {})
        field_result = self.validate_field(field_data)
        self.issues.extend(field_result.issues)

        return ValidationResult(
            valid=all(not i.is_error for i in self.issues),
            issues=tuple(self.issues),
        )

    def validate_full_pipeline(
        self,
        projections: Tuple[dict, ...],
        tensions: Tuple[dict, ...] = (),
        synergies: Tuple[dict, ...] = (),
    ) -> ValidationResult:
        """
        Validate all components in the projection pipeline.

        Args:
            projections: All drive projections
            tensions: All tension objects (optional)
            synergies: All synergy objects (optional)

        Returns:
            ValidationResult with combined findings
        """
        self.issues = []
        all_findings: List[str] = []

        # Validate each projection
        for i, proj in enumerate(projections):
            result = self.validate_projection(proj)
            self.issues.extend(result.issues)
            if not result.valid and result.findings:
                all_findings.extend(result.findings)

        # Validate tensions
        for i, tension in enumerate(tensions):
            result = self.validate_tension(tension)
            self.issues.extend(result.issues)

        # Validate synergies
        for i, synergy in enumerate(synergies):
            result = self.validate_synergy(synergy)
            self.issues.extend(result.issues)

        return ValidationResult(
            valid=all(not i.is_error for i in self.issues),
            issues=tuple(self.issues),
            findings=tuple(all_findings),
        )


__all__ = [
    "ValidationIssue",
    "ValidationResult",
    "MotivationalProjectionValidator",
]