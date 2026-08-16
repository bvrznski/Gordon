# Salience Network State Validation
# ==================================
#
# Canonical implementation of validation functions (Phase 4.8.4).
#

"""
Validation framework for Salience State.

Validation is:
    - Side-effect free
    - Deterministic
    - Typed
    - Complete

Validation does NOT:
    - Modify State
    - Repair State silently
    - Acquire current time
    - Call external systems
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from .aggregate import SalienceNetworkState
    from .integrity import SalienceStateFinding, SalienceStateValidationResult, ValidationSeverity


@dataclass(frozen=True)
class SalienceStateValidationError(Exception):
    """
    Canonical exception for invalid Salience State.
    
    This exception is raised when State construction fails due to:
        - Invalid identity (empty or malformed)
        - Invalid revision (negative or out of range)
        - Invalid enum values
        - Duplicate evidence references
        - Incompatible component combinations
    
    This is NOT raised for ordinary validation findings. Use the result model
    for non-blocking issues.
    """
    
    message: str = field(default="")
    """Human-readable error description."""
    
    invalid_field: str = field(default="")
    """Field that caused the error (if applicable)."""
    
    expected_value: str = field(default="")
    """Expected value or constraint."""
    
    @property
    def is_blocking(self) -> bool:
        """Indicates this error blocks State construction."""
        return True


def validate_identity(identity: str, required: bool = True) -> Tuple[str, ...]:
    """
    Validate State identity.
    
    Args:
        identity: The state identity string to validate.
        required: Whether an identity is required (default True).
    
    Returns:
        Tuple of validation error messages (empty if valid).
    """
    errors = []
    
    if required and not identity.strip():
        errors.append("identity is required")
    
    # Additional identity format checks could be added here
    return tuple(errors)


def validate_revision(revision: int, min_value: int = 1) -> Tuple[str, ...]:
    """
    Validate State revision.
    
    Args:
        revision: The revision number to validate.
        min_value: Minimum allowed value (default 1).
    
    Returns:
        Tuple of validation error messages (empty if valid).
    """
    errors = []
    
    if revision < min_value:
        errors.append(f"revision must be >= {min_value}")
    
    return tuple(errors)


def validate_enum(value: str, valid_values: Tuple[str, ...]) -> Tuple[str, ...]:
    """
    Validate that a value is in the set of valid enum values.
    
    Args:
        value: The value to check.
        valid_values: Allowed values.
    
    Returns:
        Tuple of validation error messages (empty if valid).
    """
    errors = []
    
    if value not in valid_values:
        errors.append(f"invalid value '{value}' - must be one of {valid_values}")
    
    return tuple(errors)


def validate_salience_state(state: "SalienceNetworkState") -> "SalienceStateValidationResult":
    """
    Validate the complete State structure and semantics.
    
    This performs aggregate validation checking cross-component consistency
    without modifying State or performing computation.
    
    Args:
        state: The State to validate.
    
    Returns:
        Validation result with all findings deterministically ordered.
    """
    from .aggregate import SalienceNetworkState
    from .integrity import SalienceStateFinding, SalienceStateValidationResult, ValidationSeverity
    
    findings: list[SalienceStateFinding] = []
    
    # Identity validation
    identity_errors = validate_identity(state.identity)
    for error in identity_errors:
        findings.append(SalienceStateFinding(
            code="INVALID_IDENTITY",
            severity=ValidationSeverity.ERROR,
            path=("identity",),
            message=error,
            related_identity=None,
        ))
    
    # Revision validation
    revision_errors = validate_revision(state.revision)
    for error in revision_errors:
        findings.append(SalienceStateFinding(
            code="INVALID_REVISION",
            severity=ValidationSeverity.ERROR,
            path=("revision",),
            message=error,
            related_identity=state.identity if state.identity else None,
        ))
    
    # Schema version validation
    if not state.schema_version.strip():
        findings.append(SalienceStateFinding(
            code="MISSING_SCHEMA_VERSION",
            severity=ValidationSeverity.ERROR,
            path=("schema_version",),
            message="schema version is required",
            related_identity=state.identity if state.identity else None,
        ))
    
    # Snapshot kind validation (check against known kinds)
    valid_snapshot_kinds = ("current", "candidate", "historical", "baseline", 
                           "provisional", "superseded", "invalid")
    snapshot_errors = validate_enum(state.snapshot_kind, valid_snapshot_kinds)
    for error in snapshot_errors:
        findings.append(SalienceStateFinding(
            code="INVALID_SNAPSHOT_KIND",
            severity=ValidationSeverity.ERROR,
            path=("snapshot_kind",),
            message=error,
            related_identity=state.identity if state.identity else None,
        ))
    
    # Activation status validation
    valid_activation_status = ("inactive", "latent", "primed", "active", 
                              "elevated", "dominant", "suppressed", "degraded")
    activation_errors = validate_enum(state.activation_status, valid_activation_status)
    for error in activation_errors:
        findings.append(SalienceStateFinding(
            code="INVALID_ACTIVATION_STATUS",
            severity=ValidationSeverity.ERROR,
            path=("activation_status",),
            message=error,
            related_identity=state.identity if state.identity else None,
        ))
    
    # Readiness status validation
    valid_readiness = ("unavailable", "incomplete", "provisional", "ready", 
                      "degraded", "invalid", "stale")
    readiness_errors = validate_enum(state.readiness_status, valid_readiness)
    for error in readiness_errors:
        findings.append(SalienceStateFinding(
            code="INVALID_READINESS_STATUS",
            severity=ValidationSeverity.ERROR,
            path=("readiness_status",),
            message=error,
            related_identity=state.identity if state.identity else None,
        ))
    
    # Persistence kind validation
    valid_persistence = ("transient", "short_lived", "sustained", "persistent", 
                        "recurrent", "dormant")
    persistence_errors = validate_enum(state.persistence_kind, valid_persistence)
    for error in persistence_errors:
        findings.append(SalienceStateFinding(
            code="INVALID_PERSISTENCE_KIND",
            severity=ValidationSeverity.ERROR,
            path=("persistence_kind",),
            message=error,
            related_identity=state.identity if state.identity else None,
        ))
    
    # Decay kind validation
    valid_decay = ("none", "slow", "moderate", "rapid", "expired")
    decay_errors = validate_enum(state.decay_kind, valid_decay)
    for error in decay_errors:
        findings.append(SalienceStateFinding(
            code="INVALID_DECAY_KIND",
            severity=ValidationSeverity.ERROR,
            path=("decay_kind",),
            message=error,
            related_identity=state.identity if state.identity else None,
        ))
    
    # Competition status validation
    valid_competition = ("unresolved", "resolved", "conflicted", "suppressed")
    competition_errors = validate_enum(state.competition_status, valid_competition)
    for error in competition_errors:
        findings.append(SalienceStateFinding(
            code="INVALID_COMPETITION_STATUS",
            severity=ValidationSeverity.ERROR,
            path=("competition_status",),
            message=error,
            related_identity=state.identity if state.identity else None,
        ))
    
    # Integrity status validation
    valid_integrity = ("valid", "valid_with_warnings", "incomplete", 
                      "degraded", "invalid")
    integrity_errors = validate_enum(state.integrity_status, valid_integrity)
    for error in integrity_errors:
        findings.append(SalienceStateFinding(
            code="INVALID_INTEGRITY_STATUS",
            severity=ValidationSeverity.ERROR,
            path=("integrity_status",),
            message=error,
            related_identity=state.identity if state.identity else None,
        ))
    
    # Cross-component consistency checks
    # Invalid State should not be marked as ready
    if state.readiness_status == "ready" and state.integrity_status in ("invalid",):
        findings.append(SalienceStateFinding(
            code="READY_INVALID_STATE",
            severity=ValidationSeverity.ERROR,
            path=("readiness_status",),
            message="ready status is incompatible with invalid integrity",
            related_identity=state.identity if state.identity else None,
        ))
    
    # Dominant candidate must belong to candidates set
    dominant_candidate = state.dominant_candidate
    competition_candidates = tuple(state.competition_candidates)
    if (dominant_candidate and 
        dominant_candidate not in competition_candidates):
        findings.append(SalienceStateFinding(
            code="DOMINANT_NOT_IN_SET",
            severity=ValidationSeverity.ERROR,
            path=("dominant_candidate",),
            message="dominant candidate must belong to competition candidates set",
            related_identity=state.identity if state.identity else None,
        ))
    
    # Determine overall validity
    has_blocking = any(f.is_blocking for f in findings)
    valid = not has_blocking
    
    return SalienceStateValidationResult(
        valid=valid,
        findings=tuple(findings),
        schema_version=state.schema_version or "1.0.0",
    )