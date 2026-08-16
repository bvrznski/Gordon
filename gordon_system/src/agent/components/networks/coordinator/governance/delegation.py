# Gordon Cognitive Architecture - Phase 4.11.9
# ===========================================

"""
Cognitive Coordination Governance (CCG) - Delegation System
===========================================================

Explicit delegation of authority with revocation.
Delegation transfers authority only - not responsibility.

Following:
* DELEGATION-LAW-001 through DELEGATION-LAW-008
"""

from __future__ import annotations

from dataclasses import dataclass, field


# =============================================================================
# DELEGATION DEFINITION
# =============================================================================

@dataclass(frozen=True, slots=True)
class Delegation:
    """
    Immutable delegation of authority.
    
    Delegation transfers authority only - not responsibility.
    
    DELEGATION-LAW-001: Delegation shall remain explicit
    DELEGATION-LAW-002: Delegation shall transfer authority only
    DELEGATION-LAW-003: Responsibility shall never be delegated
    DELEGATION-LAW-004: Delegation conditions shall remain explicit
    DELEGATION-LAW-005: Delegation revocation shall remain explicit
    DELEGATION-LAW-006: Delegation shall preserve provenance
    DELEGATION-LAW-007: Historical delegations shall remain inspectable
    DELEGATION-LAW-008: Delegation evaluation shall remain deterministic
    
    CCG-DELE-INV-001: Delegation is immutable (deeply frozen)
    CCG-DELE-INV-002: Delegation has no runtime references
    """
    delegation_id: str
    """Unique identifier for this delegation."""
    
    delegating_authority: str
    """Identity of the authority delegating."""
    
    receiving_authority: str
    """Identity of the authority receiving."""
    
    delegated_permissions: tuple[str, ...]
    """Permissions being delegated."""
    
    validity_conditions: tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must hold for delegation to be valid."""
    
    revocation_policy: str = "manual"
    """How this delegation can be revoked (manual, automatic, time_limited)."""
    
    delegation_duration_seconds: int | None = None
    """Duration in seconds if time-limited, None for indefinite."""
    
    created_at_sequence: int = 0
    """Sequence number when delegation was created."""
    
    effective_after_sequence: int = 0
    """Sequence number after which this becomes active."""
    
    provenance_ref: str | None = None
    """Reference to provenance record."""
    
    @classmethod
    def create(
        cls,
        delegation_id: str,
        delegating_authority: str,
        receiving_authority: str,
        permissions: tuple[str, ...],
        conditions: tuple[str, ...] | None = None,
        revocation_policy: str = "manual",
        duration_seconds: int | None = None,
        created_sequence: int = 0,
        effective_after_sequence: int = 0,
    ) -> Delegation:
        """
        Create a new delegation.
        
        Args:
            delegation_id: Unique identifier
            delegating_authority: Authority delegating
            receiving_authority: Authority receiving
            permissions: Permissions being delegated
            conditions: Validity conditions
            revocation_policy: How it can be revoked
            duration_seconds: Duration if time-limited
            created_sequence: Creation sequence number
            effective_after_sequence: When it becomes active
            
        Returns:
            A new Delegation instance
        """
        return cls(
            delegation_id=delegation_id,
            delegating_authority=delegating_authority,
            receiving_authority=receiving_authority,
            delegated_permissions=permissions,
            validity_conditions=conditions or (),
            revocation_policy=revocation_policy,
            delegation_duration_seconds=duration_seconds,
            created_at_sequence=created_sequence,
            effective_after_sequence=effective_after_sequence,
            provenance_ref=None,
        )
    
    def is_valid(self, current_sequence: int) -> bool:
        """
        Check if the delegation is valid at a given sequence.
        
        Args:
            current_sequence: The current sequence number
            
        Returns:
            True if the delegation is currently valid
        """
        if self.effective_after_sequence > current_sequence:
            return False
        if self.delegation_duration_seconds is not None:
            # In real implementation, would check actual time elapsed
            pass
        return True
    
    def can_perform(self, permission: str) -> bool:
        """
        Check if this delegation includes a specific permission.
        
        Args:
            permission: The permission to check
            
        Returns:
            True if the delegation includes this permission
        """
        return permission in self.delegated_permissions


# =============================================================================
# DELEGATION HIERARCHY
# =============================================================================

@dataclass(frozen=True, slots=True)
class DelegationHierarchy:
    """
    Immutable hierarchy of delegations for an authority.
    
    CCG-DELE-HIER-INV-001: Hierarchy is immutable
    CCG-DELE-HIER-INV-002: Hierarchy has no runtime references
    """
    authority_identity: str
    """The authority that is the subject of this hierarchy."""
    
    incoming_delegations: tuple[Delegation, ...] = field(default_factory=tuple)
    """Delegations TO this authority from others."""
    
    outgoing_delegations: tuple[Delegation, ...] = field(default_factory=tuple)
    """Delegations FROM this authority to others."""
    
    direct_permissions: tuple[str, ...] = field(default_factory=tuple)
    """Direct permissions not delegated."""
    
    @classmethod
    def create(
        cls,
        authority_identity: str,
        incoming: tuple[Delegation, ...] | None = None,
        outgoing: tuple[Delegation, ...] | None = None,
        direct_permissions: tuple[str, ...] | None = None,
    ) -> DelegationHierarchy:
        """
        Create a new delegation hierarchy.
        
        Args:
            authority_identity: The authority identity
            incoming: Incoming delegations
            outgoing: Outgoing delegations
            direct_permissions: Direct permissions
            
        Returns:
            A new DelegationHierarchy instance
        """
        return cls(
            authority_identity=authority_identity,
            incoming_delegations=incoming or (),
            outgoing_delegations=outgoing or (),
            direct_permissions=direct_permissions or (),
        )
    
    def get_all_active_permissions(self, current_sequence: int) -> tuple[str, ...]:
        """
        Get all permissions active for this authority.
        
        Args:
            current_sequence: The current sequence number
            
        Returns:
            Tuple of all active permission identifiers
        """
        permissions = set(self.direct_permissions)
        
        for delegation in self.incoming_delegations:
            if delegation.is_valid(current_sequence):
                permissions.update(delegation.delegated_permissions)
        
        return tuple(sorted(permissions))
    
    def can_perform(self, permission: str, current_sequence: int) -> bool:
        """
        Check if this authority can perform a specific operation.
        
        Args:
            permission: The permission to check
            current_sequence: The current sequence number
            
        Returns:
            True if the authority has this permission
        """
        return permission in self.get_all_active_permissions(current_sequence)


# =============================================================================
# DELEGATION VALIDATION RESULT
# =============================================================================

@dataclass(frozen=True, slots=True)
class DelegationValidationResult:
    """
    Immutable result of delegation validation.
    
    CCG-DELE-VAL-INV-001: Result is immutable
    CCG-DELE-VAL-INV-002: Result has no runtime references
    
    CCG-DELE-VAL-LAW-001: Validation results preserve evidence
    CCG-DELE-VAL-LAW-002: Validation results are deterministic
    """
    delegation_id: str
    """Identity of the validated delegation."""
    
    validation_passed: bool
    """Whether the delegation is valid."""
    
    authority_valid: bool = True
    """Whether both delegating and receiving authorities are valid."""
    
    permissions_valid: bool = True
    """Whether delegated permissions are valid."""
    
    conditions_satisfied: bool = True
    """Whether validity conditions are satisfied."""
    
    not_revoked: bool = True
    """Whether delegation has not been revoked."""
    
    evidence: tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting the validation result."""
    
    @classmethod
    def of_valid(cls, delegation_id: str) -> DelegationValidationResult:
        """
        Create a valid delegation validation result.
        
        Args:
            delegation_id: The validated delegation identity
            
        Returns:
            A new DelegationValidationResult instance
        """
        return cls(
            delegation_id=delegation_id,
            validation_passed=True,
            authority_valid=True,
            permissions_valid=True,
            conditions_satisfied=True,
            not_revoked=True,
        )
    
    @classmethod
    def of_invalid(cls, delegation_id: str) -> DelegationValidationResult:
        """
        Create an invalid delegation validation result.
        
        Args:
            delegation_id: The validated delegation identity
            
        Returns:
            A new DelegationValidationResult instance
        """
        return cls(
            delegation_id=delegation_id,
            validation_passed=False,
        )
    
    def is_valid(self) -> bool:
        """Check if the delegation validation passed."""
        return self.validation_passed
    
    def has_issues(self) -> tuple[str, ...]:
        """Get list of issues found during validation."""
        issues = []
        if not self.authority_valid:
            issues.append("invalid_authority")
        if not self.permissions_valid:
            issues.append("invalid_permissions")
        if not self.conditions_satisfied:
            issues.append("unsatisfied_conditions")
        if not self.not_revoked:
            issues.append("revoked_delegation")
        return tuple(issues)