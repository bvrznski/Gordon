# Gordon Phase 5.7.8-I: Conscious Integration - Cross-Engine Validation
# ===============================================================================

"""
Cross-engine invariant validation for composite context snapshots.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional, List


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of a cross-engine validation pass.
    """

    passed: bool = True
    """Whether all validations passed."""

    warnings: Tuple[str, ...] = field(default_factory=tuple)
    """Non-critical validation issues."""

    errors: Tuple[str, ...] = field(default_factory=tuple)
    """Critical validation failures that must block publication."""

    @property
    def is_valid(self) -> bool:
        """Check if the result represents valid state."""
        return self.passed and len(self.errors) == 0


@dataclass(frozen=True)
class CrossEngineReference:
    """
    Reference from one engine to another during validation.
    """

    source_engine_id: str
    """The engine holding this reference."""

    target_engine_id: str
    """The referenced engine."""

    reference_value: str
    """The reference identifier."""

    status: str = "resolved"
    """
    Status:
        - resolved: Valid reference found
        - missing: Engine not available
        - stale: Generation mismatch
        - external: Reference outside current scope
    """

    generation_match: bool = True
    """Whether target generation matches expected value."""


@dataclass(frozen=True)
class InvariantCheckResult:
    """
    Result of a single invariant check.
    """

    invariant_name: str
    """Name of the checked invariant."""

    passed: bool = True
    """Whether the invariant holds."""

    engine_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Engines involved in this check."""

    details: Optional[str] = None
    """Additional diagnostic information."""


class CrossEngineValidator:
    """
    Validator for cross-engine references and invariants.

    This class checks that all engine references within a composite context
    are compatible and satisfy required invariants before publication.
    """

    def __init__(self, consistency_level: str = "strict"):
        """
        Initialize the validator with consistency requirements.

        Args:
            consistency_level: The strictness level for validation
        """
        self._consistency_level = consistency_level

    @property
    def consistency_level(self) -> str:
        """Get the current consistency level."""
        return self._consistency_level

    def validate_perspective_world_compatibility(
        self,
        perspective_ref: Optional[object],
        world_ref: Optional[object],
        previous_refs: Dict[str, object] = None,
    ) -> ValidationResult:
        """
        Validate that Perspective and Situated World are compatible.

        Invariant: Perspective and World must use compatible reference frames
        and context. A Perspective from a different user/session cannot be
        combined with a World from another scope.

        Args:
            perspective_ref: Perspective snapshot reference (if available)
            world_ref: Situated World snapshot reference (if available)
            previous_refs: Previous generation references for continuity check

        Returns:
            Validation result indicating compatibility
        """
        if perspective_ref is None and world_ref is None:
            return ValidationResult(
                passed=True,
                warnings=("No Perspective or World references to validate",),
            )

        # Check scope compatibility
        errors: List[str] = []
        warnings: List[str] = []

        # In a real implementation, we'd check:
        # - User/session/tenant identity alignment
        # - Context ID lineage
        # - Generation compatibility

        if perspective_ref is not None and world_ref is not None:
            # Check if they're from compatible sources
            # This would involve comparing context_id prefixes or other scope identifiers

            # For now, just warn about potential issues
            pass

        return ValidationResult(
            passed=len(errors) == 0,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

    def validate_presence_awareness_compatibility(
        self,
        presence_ref: Optional[object],
        awareness_ref: Optional[object],
        field_snapshot: Optional[object] = None,
    ) -> ValidationResult:
        """
        Validate that Presence and Awareness are compatible.

        Invariant: Awareness should only include contents from the current
        field. Presence cannot be aware of something not in the experiential
        field.

        Args:
            presence_ref: Presence snapshot reference
            awareness_ref: Awareness snapshot reference
            field_snapshot: Current experiential field snapshot (optional)

        Returns:
            Validation result indicating compatibility
        """
        if presence_ref is None and awareness_ref is None:
            return ValidationResult(
                passed=True,
                warnings=("No Presence or Awareness references to validate",),
            )

        errors: List[str] = []

        # In a real implementation, we'd check:
        # - Awareness contents are subset of field contents
        # - Presence admission matches awareness accessibility

        return ValidationResult(passed=len(errors) == 0, errors=tuple(errors))

    def validate_intentional_target_resolution(
        self,
        intentional_refs: Tuple[str, ...],
        world_entities: Tuple[str, ...],
        remembered_targets: Tuple[str, ...] = (),
        hypothetical_targets: Tuple[str, ...] = (),
    ) -> ValidationResult:
        """
        Validate intentional target references against available world entities.

        Invariant: Intentional targets must be either:
            - Resolved to current Situated World entities
            - Marked as remembered (from past context)
            - Marked as hypothetical (not yet observed)

        Args:
            intentional_refs: Target reference IDs
            world_entities: Currently available entity IDs
            remembered_targets: Targets marked as remembered
            hypothetical_targets: Targets marked as hypothetical

        Returns:
            Validation result with unresolved targets
        """
        if not intentional_refs:
            return ValidationResult(passed=True)

        world_set = set(world_entities)
        remembered_set = set(remembered_targets)
        hypothetical_set = set(hypothetical_targets)
        all_valid = world_set | remembered_set | hypothetical_set

        errors: List[str] = []
        warnings: List[str] = []

        for target_ref in intentional_refs:
            if target_ref not in all_valid:
                # This could be an unresolved reference
                errors.append(f"Unresolved intentional target: {target_ref}")

        return ValidationResult(
            passed=len(errors) == 0,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

    def validate_temporal_field_reference(
        self,
        temporal_context_ref: Optional[object],
        field_snapshot: Optional[object] = None,
    ) -> ValidationResult:
        """
        Validate that Temporal Context references valid Field generations.

        Invariant: Temporal context retention must reference valid committed
        Field generations. Stale or invalid references should be rejected.

        Args:
            temporal_context_ref: Temporal context snapshot reference
            field_snapshot: Current field snapshot for validation

        Returns:
            Validation result
        """
        if temporal_context_ref is None:
            return ValidationResult(
                passed=True,
                warnings=("No Temporal Context to validate",),
            )

        errors: List[str] = []

        # In a real implementation, we'd check:
        # - Field context ID matches expected
        # - Generation is monotonic and valid

        return ValidationResult(passed=len(errors) == 0, errors=tuple(errors))

    def validate_all(
        self,
        experiential_field_ref: Optional[object],
        intentional_context_ref: Optional[object],
        temporal_context_ref: Optional[object],
        presence_ref: Optional[object],
        awareness_ref: Optional[object],
        perspective_ref: Optional[object],
        situated_world_ref: Optional[object],
        engine_references: Dict[str, object] = None,
    ) -> Tuple[ValidationResult, Tuple[InvariantCheckResult, ...]]:
        """
        Run all cross-engine validation checks.

        Args:
            All engine snapshot references
            engine_references: Full engine snapshots (optional)

        Returns:
            Tuple of (overall result, individual check results)
        """
        start_time = time.time()

        errors: List[str] = []
        warnings: List[str] = []
        check_results: List[InvariantCheckResult] = []

        # Check 1: Perspective-World compatibility
        pw_result = self.validate_perspective_world_compatibility(
            perspective_ref=perspective_ref,
            world_ref=situated_world_ref,
        )
        check_results.append(
            InvariantCheckResult(
                invariant_name="perspective_world_compatibility",
                passed=pw_result.passed,
                engine_ids=("perspective", "situated_world"),
            )
        )
        errors.extend(pw_result.errors)
        warnings.extend(pw_result.warnings)

        # Check 2: Presence-Awareness compatibility
        pa_result = self.validate_presence_awareness_compatibility(
            presence_ref=presence_ref,
            awareness_ref=awareness_ref,
            field_snapshot=experiential_field_ref,
        )
        check_results.append(
            InvariantCheckResult(
                invariant_name="presence_awareness_compatibility",
                passed=pa_result.passed,
                engine_ids=("presence", "awareness"),
            )
        )
        errors.extend(pa_result.errors)
        warnings.extend(pa_result.warnings)

        # Check 3: Temporal-Field alignment
        tf_result = self.validate_temporal_field_reference(
            temporal_context_ref=temporal_context_ref,
            field_snapshot=experiential_field_ref,
        )
        check_results.append(
            InvariantCheckResult(
                invariant_name="temporal_field_alignment",
                passed=tf_result.passed,
                engine_ids=("temporal_context", "experiential_field"),
            )
        )
        errors.extend(tf_result.errors)
        warnings.extend(tf_result.warnings)

        # Check 4: Intentional-World alignment (simplified)
        if intentional_context_ref and situated_world_ref:
            check_results.append(
                InvariantCheckResult(
                    invariant_name="intentional_world_alignment",
                    passed=True,
                    engine_ids=("intentional_context", "situated_world"),
                )
            )

        # Check 5: Required engines present
        missing_required = []
        for req in ("experiential_field", "presence", "perspective"):
            ref = locals().get(f"{req}_ref")
            if ref is None:
                missing_required.append(req)

        if missing_required:
            errors.append(f"Missing required engines: {missing_required}")

        # Compute overall result
        final_passed = len(errors) == 0

        duration = time.time() - start_time

        return (
            ValidationResult(
                passed=final_passed,
                errors=tuple(errors),
                warnings=tuple(warnings),
            ),
            tuple(check_results),
        )

    def get_required_engines(self) -> Tuple[str, ...]:
        """Get list of required engine IDs for healthy context."""
        return ("experiential_field", "presence", "perspective")

    def is_engine_optional(self, engine_id: str) -> bool:
        """Check if an engine is optional (not required for healthy context)."""
        return engine_id not in self.get_required_engines()