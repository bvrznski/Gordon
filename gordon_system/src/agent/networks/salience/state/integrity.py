# Salience Network Integrity State
# ================================
#
# Canonical implementation of validation findings (Phase 4.8.4).
#

"""
Integrity and validation representation for Salience State.

IntegrityState represents structural and semantic soundness without repair.
Validation finds issues; IntegrityState represents them semantically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple


class ValidationSeverity(Enum):
    """
    Canonical severity levels for validation findings.
    
    SEVERITY HIERARCHY:
        - INFO: Informational only, no blocking impact
        - WARNING: Non-blocking concern that may affect reliability
        - ERROR: Blocking issue preventing normal use
        - FATAL: Critical failure requiring immediate attention
    
    INTEGRITY INVARIANTS:
        - SALIENCE-INTEGRITY-INV-001: Severity determines blocking status
        - SALIENCE-INTEGRITY-INV-002: INFO never blocks
        - SALIENCE-INTEGRITY-INV-003: ERROR/FATAL block usage
    """
    
    INFO = auto()
    """Informational finding, non-blocking."""
    
    WARNING = auto()
    """Non-blocking concern that may affect reliability."""
    
    ERROR = auto()
    """Blocking issue preventing normal State use."""
    
    FATAL = auto()
    """Critical failure requiring immediate attention."""


@dataclass(frozen=True)
class SalienceStateFinding:
    """
    Canonical validation finding representation.
    
    A finding describes a specific validation result with:
        - Semantic code for deterministic handling
        - Severity level determining blocking status
        - Path to the problematic field
        - Human-readable message
        - Optional related State identity
    
    INTEGRITY INVARIANTS:
        - SALIENCE-INTEGRITY-FINDING-INV-001: Code is stable and deterministic
        - SALIENCE-INTEGRITY-FINDING-INV-002: Path is fully qualified
        - SALIENCE-INTEGRITY-FINDING-INV-003: Severity determines blocking
    
    FINDING CODES:
        - INVALID_IDENTITY: State identity is malformed or absent
        - INVALID_REVISION: Revision number is invalid
        - INVALID_ENUM: Enum value not in allowed set
        - MISSING_REQUIRED_FIELD: Required field is absent
        - INCOMPATIBLE_COMBINATION: Component combination is semantically invalid
    """
    
    code: str = field(default="")
    """Stable semantic code identifying the finding type."""
    
    severity: ValidationSeverity = field(default=ValidationSeverity.ERROR)
    """Semantic severity of this finding."""
    
    path: Tuple[str, ...] = field(default_factory=tuple)
    """
    Fully qualified path to the problematic field:
        - ("aggregate", "identity") for top-level identity
        - ("assessment", "significance") for nested assessment field
    """
    
    message: str = field(default="")
    """Human-readable description of the finding."""
    
    related_identity: str | None = field(default=None)
    """Related State identity where applicable."""
    
    @property
    def is_blocking(self) -> bool:
        """
        Indicates whether this finding blocks normal State usage.
        
        Blocking findings are ERROR or FATAL severity.
        """
        return self.severity in (ValidationSeverity.ERROR, ValidationSeverity.FATAL)


class SalienceStateFindingCode:
    """
    Canonical finding codes for validation findings.
    
    Codes must be:
        - Stable across versions
        - Deterministic (not based on random values)
        - Hierarchical where applicable
        - Lowercase snake_case
    
    CODE CATEGORIES:
        IDENTITY: Invalid or missing identity
        REVISION: Invalid revision number
        ENUM: Invalid enum value
        COMPOSITION: Structural composition issues
        CONSISTENCY: Cross-component consistency failures
    """
    
    INVALID_IDENTITY = "invalid_identity"
    """State identity is malformed or absent."""
    
    INVALID_REVISION = "invalid_revision"
    """Revision number is invalid."""
    
    INVALID_ENUM = "invalid_enum"
    """Enum value not in allowed set."""
    
    MISSING_REQUIRED_FIELD = "missing_required_field"
    """Required field is absent."""
    
    INCOMPATIBLE_COMBINATION = "incompatible_combination"
    """Component combination is semantically invalid."""
    
    DOMINANT_NOT_IN_SET = "dominant_not_in_set"
    """Dominant candidate not in candidates set."""
    
    EVIDENCE_CONFLICT = "evidence_conflict"
    """Evidence appears both supporting and contradicting."""
    
    PROVENANCE_MISSING = "provenance_missing"
    """Provenance information is incomplete."""


@dataclass(frozen=True)
class SalienceStateValidationResult:
    """
    Canonical validation result representation.
    
    A validation result contains:
        - Overall validity (True if no blocking findings)
        - Ordered list of all findings
        - Schema version for compatibility tracking
    
    VALIDATION INVARIANTS:
        - SALIENCE-VALIDATION-RESULT-INV-001: Validity is computed from findings
        - SALIENCE-VALIDATION-RESULT-INV-002: Findings are deterministically ordered
        - SALIENCE-VALIDATION-RESULT-INV-003: Schema version tracks compatibility
    
    VALIDATION LAWS:
        - SALIENCE-VALIDATION-RESULT-LAW-001: No blocking finding = valid
        - SALIENCE-VALIDATION-RESULT-LAW-002: Ordering is deterministic
        - SALIENCE-VALIDATION-RESULT-LAW-003: Schema version is explicit
    """
    
    valid: bool = field(default=True)
    """True if no blocking findings, False otherwise."""
    
    findings: Tuple[SalienceStateFinding, ...] = field(default_factory=tuple)
    """All validation findings in deterministic order."""
    
    schema_version: str = field(default="1.0.0")
    """Schema version at time of validation."""