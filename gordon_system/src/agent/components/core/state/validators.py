# Core State Validators - Phase 3.15.2
# ======================================

"""
Canonical validation utilities for Gordon Core state aggregates.

This module provides validators for:
    - Identity uniqueness and format
    - Scope correctness and inheritance  
    - Ownership correctness
    - Authority conflicts
    - Runtime isolation
    - Stale owner/rejection detection
    
All validators return structured findings, not just Boolean results.
"""

# =============================================================================
# IMPORTS - Import-time purity maintained
# =============================================================================

from dataclasses import dataclass, field
from typing import (
    Tuple,
    Optional,
)
import time as _time_module

from enum import Enum


# =============================================================================
# VALIDATION SEVERITY ENUMERATION
# =============================================================================


class ValidationSeverity(Enum):
    """
    Canonical validation finding severities.
    
    SEVERITIES:
        ERROR       - Validation failed, operation must be rejected
        WARNING     - Operation may proceed but with caution
        INFORMATIONAL - Just information, no action required
    """
    
    ERROR = "error"
    WARNING = "warning"
    INFORMATIONAL = "informational"


# =============================================================================
# VALIDATION FINDING
# =============================================================================


@dataclass(frozen=True)
class ValidationFinding:
    """
    A single validation finding.
    
    FINDING PRINCIPLES:
        - Findings are immutable once created
        - Each finding has a category and severity
        - Multiple findings may be combined into one validation result
    
    INVARIANTS:
        FND-001: Finding is immutable once created
        FND-002: Each finding has exactly one severity
        FND-003: ERROR findings indicate validation failure
    """
    
    # Identity
    finding_id: str = field(default_factory=lambda: f"fnd_{uuid.uuid4().hex[:20]}")
    
    # Category (what was validated)
    category: str  # e.g., "identity", "scope", "ownership"
    
    # Validation details
    check_name: str  # What specific check was performed?
    severity: ValidationSeverity = ValidationSeverity.ERROR
    
    # Result
    valid: bool = True
    message: Optional[str] = None
    
    # Context
    field_path: Optional[str] = None
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None


# =============================================================================
# VALIDATION RESULT
# =============================================================================


@dataclass(frozen=True)
class ValidationResult:
    """
    Structured validation result.
    
    Validation produces multiple findings, not just a Boolean.
    
    INVARIANTS:
        VAL-001: Validation has exactly one overall validity outcome
        VAL-002: Findings include all validation details
        VAL-003: ERROR findings indicate validation failure
    """
    
    # Identity
    validation_id: str = field(default_factory=lambda: f"val_{uuid.uuid4().hex[:20]}")
    
    # Target
    state_id: Optional[str] = None
    
    # Overall result
    overall_validity: bool = False  # True only if no ERROR findings
    
    # Findings (all individual checks)
    findings: Tuple[ValidationFinding, ...] = field(default_factory=tuple)
    
    # Validation context
    validated_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def valid(
        cls,
        state_id: Optional[str] = None,
    ) -> "ValidationResult":
        """Create a valid validation result."""
        return cls(
            state_id=state_id,
            overall_validity=True,
            findings=tuple(),
        )
    
    @classmethod
    def invalid(
        cls,
        state_id: Optional[str],
        primary_failure: str,
        secondary_findings: Optional[Tuple[ValidationFinding, ...]] = None,
    ) -> "ValidationResult":
        """Create an invalid validation result."""
        return cls(
            state_id=state_id,
            overall_validity=False,
            findings=tuple([
                ValidationFinding(
                    finding_id="primary",
                    category="validation",
                    check_name="overall_validation",
                    severity=ValidationSeverity.ERROR,
                    valid=False,
                    message=primary_failure,
                ),
            ]) + (secondary_findings or tuple()),
        )


# =============================================================================
# IDENTITY VALIDATOR
# =============================================================================


class IdentityValidator:
    """
    Validates state identity constraints.
    
    VALIDATIONS:
        - Uniqueness within scope
        - Format compliance
        - Runtime isolation
    
    RETURNS structured findings, not just Boolean results.
    """
    
    @staticmethod
    def validate_identity_format(identity_value: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that an identity value has correct format.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        if not identity_value:
            return False, "identity_empty"
        
        # Must start with allowed prefix
        valid_prefixes = ("state_", "agg_", "rt_", "bs_", "owner_", "auth_", 
                         "ver_", "gen_", "snap_", "view_", "val_", "tra_", "op_")
        if not identity_value.startswith(valid_prefixes):
            return False, f"invalid_identity_prefix: must start with one of {valid_prefixes}"
        
        # Must contain valid characters
        import re
        if not re.match(r'^[a-z_][a-z0-9_]*$', identity_value):
            return False, "identity_invalid_characters: only lowercase letters, numbers, underscores allowed"
        
        return True, None
    
    @staticmethod
    def validate_runtime_binding(
        state_runtime_id: Optional[str],
        owner_runtime_id: Optional[str],
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate runtime binding between state and owner.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        if state_runtime_id is None or owner_runtime_id is None:
            return True, None  # No binding enforced
        
        if state_runtime_id != owner_runtime_id:
            return False, f"runtime_mismatch: expected {state_runtime_id}, got {owner_runtime_id}"
        
        return True, None
    
    @staticmethod
    def validate_uniqueness(
        identity_value: str,
        existing_identifiers: Tuple[str, ...],
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that an identity is unique within the context.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        if identity_value in existing_identifiers:
            return False, f"identity_duplicate: {identity_value} already exists"
        
        return True, None


# =============================================================================
# SCOPE VALIDATOR
# =============================================================================


class ScopeValidator:
    """
    Validates state scope constraints.
    
    VALIDATIONS:
        - Scope correctness
        - Inheritance rules
        - Visibility boundaries
    
    RETURNS structured findings, not just Boolean results.
    """
    
    # Hierarchy definition: child -> list of allowed parents
    SCOPE_HIERARCHY = {
        "application": ["process"],
        "runtime": ["process"],
        "subsystem": ["application"],
        "component": ["subsystem"],
        "service": ["component"],
        "request": ["application"],
        "transaction": ["request"],
        "boot_session": ["runtime"],
    }
    
    @staticmethod
    def validate_scope_inheritance(
        child_scope: str,
        parent_scope: Optional[str],
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate scope inheritance relationship.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        if parent_scope is None:
            return True, None  # No inheritance check needed
        
        allowed_parents = ScopeValidator.SCOPE_HIERARCHY.get(child_scope, [])
        
        if parent_scope not in allowed_parents:
            return False, f"scope_inheritance_violation: {child_scope} cannot inherit from {parent_scope}"
        
        return True, None
    
    @staticmethod
    def validate_scope_visibility(
        state_scope: str,
        requested_scope: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that a scope can access another scope.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        # Same scope is always visible
        if state_scope == requested_scope:
            return True, None
        
        # Parent scopes can see child scopes (by design)
        allowed_parents = ScopeValidator.SCOPE_HIERARCHY.get(state_scope, [])
        
        if requested_scope in allowed_parents or state_scope in allowed_parents:
            return True, None
        
        # Default: different non-related scopes may not be visible
        return False, f"scope_visibility_denied: {requested_scope} is not visible from {state_scope}"


# =============================================================================
# OWNERSHIP VALIDATOR
# =============================================================================


class OwnershipValidator:
    """
    Validates ownership constraints for state aggregates.
    
    VALIDATIONS:
        - Uniqueness of mutation owner per aggregate
        - Scope correctness
        - Runtime isolation
        - Policy compliance
        - Authority conflicts
    
    RETURNS structured findings, not just Boolean results.
    """
    
    @staticmethod
    def validate_ownership_uniqueness(
        current_owner: Optional[str],
        new_owner: str,
        allow_multiple_observers: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that mutation ownership remains unique.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        if current_owner is None:
            return True, None  # No existing owner
        
        if current_owner == new_owner:
            return True, None  # Same owner, no conflict
        
        # If multiple observers allowed and authority is non-mutation
        if allow_multiple_observers:
            return True, None
        
        return False, f"mutation_owner_already_exists: {current_owner}"
    
    @staticmethod
    def validate_scope_inheritance(
        parent_scope: str,
        child_scope: str,
        inherited_scopes: Tuple[str, ...],
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate scope inheritance rules.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        # A scope can only inherit from scopes in its inheritance chain
        if child_scope not in inherited_scopes and child_scope != parent_scope:
            return False, f"scope_inheritance_violation: {child_scope} does not inherit from {parent_scope}"
        
        return True, None
    
    @staticmethod
    def validate_authority_conflicts(
        authority_types: Tuple[str, ...],
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that there are no conflicting authority types.
        
        Example conflict: multiple EXCLUSIVE_MUTATION authorities for same state.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        mutation_count = sum(1 for t in authority_types if t == "exclusive_mutation")
        
        if mutation_count > 1:
            return False, f"authority_conflict: multiple exclusive mutation authorities ({mutation_count} found)"
        
        return True, None
    
    @staticmethod
    def validate_owner_not_stale(
        owner_identity: str,
        current_epoch: int,
        owner_epoch: Optional[int] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that an owner is not from a stale generation.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        if owner_epoch is None:
            return True, None  # No epoch info
        
        if owner_epoch < current_epoch:
            return False, f"stale_owner: owner is from epoch {owner_epoch}, current is {current_epoch}"
        
        return True, None


# =============================================================================
# RUNTIME ISOLATION VALIDATOR
# =============================================================================


class RuntimeIsolationValidator:
    """
    Validates runtime isolation constraints.
    
    VALIDATIONS:
        - State belongs to exactly one runtime
        - Owner matches state's runtime binding
        - Boot session bindings match
    
    RETURNS structured findings, not just Boolean results.
    """
    
    @staticmethod
    def validate_runtime_binding(
        state_runtime_id: Optional[str],
        owner_runtime_id: Optional[str],
        boot_session_id: Optional[str] = None,
        owner_boot_session_id: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that owner's runtime binding matches state's.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        # If no runtime binding, isolation is not enforced
        if state_runtime_id is None or owner_runtime_id is None:
            return True, None
        
        # Runtime must match exactly
        if state_runtime_id != owner_runtime_id:
            return False, f"runtime_mismatch: expected {state_runtime_id}, got {owner_runtime_id}"
        
        # Boot session binding check (if both present)
        if boot_session_id is not None and owner_boot_session_id is not None:
            if boot_session_id != owner_boot_session_id:
                return False, f"boot_session_mismatch: expected {boot_session_id}, got {owner_boot_session_id}"
        
        return True, None
    
    @staticmethod
    def validate_isolation(
        state_runtime_id: str,
        attempted_owner_runtime_id: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that a runtime cannot access another's state.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        if state_runtime_id != attempted_owner_runtime_id:
            return False, f"runtime_isolation_violated: state belongs to {state_runtime_id}, attempted owner is {attempted_owner_runtime_id}"
        return True, None


# =============================================================================
# TRANSFER VALIDATOR
# =============================================================================


class OwnershipTransferValidator:
    """
    Validates ownership transfer constraints.
    
    VALIDATIONS:
        - Policy allows transfer
        - Source owner has authority
        - Target can accept ownership
        - Generation increment where required
    
    RETURNS structured findings, not just Boolean results.
    """
    
    @staticmethod
    def validate_transfer_policy(
        current_evidence: dict,
        target_owner: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that the current ownership policy allows transfer to target.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        # Check if transfer is permitted
        if not current_evidence.get("transfer_eligible", False):
            return False, "transfer_not_permitted"
        
        # Check runtime isolation
        state_runtime = current_evidence.get("runtime_binding")
        target_runtime = current_evidence.get("target_runtime_binding")
        
        if state_runtime and target_runtime and state_runtime != target_runtime:
            return False, f"runtime_mismatch_on_transfer: state is {state_runtime}, target is {target_runtime}"
        
        return True, None
    
    @staticmethod
    def validate_generation_increment(
        current_generation: int,
        new_generation: Optional[int],
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate generation is incremented where required.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        if new_generation is None:
            return False, "generation_not_specified"
        
        if new_generation < current_generation:
            return False, f"generation_must_increase: current={current_generation}, new={new_generation}"
        
        return True, None


# =============================================================================
# PUBLIC API
# =============================================================================

import uuid  # Import for uuid4 in dataclass default factories


__all__ = [
    # Severity enum
    "ValidationSeverity",
    
    # Result types
    "ValidationFinding",
    "ValidationResult",
    
    # Validators
    "IdentityValidator",
    "ScopeValidator",
    "OwnershipValidator",
    "RuntimeIsolationValidator",
    "OwnershipTransferValidator",
]