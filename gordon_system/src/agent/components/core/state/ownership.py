# Core State Ownership - Phase 3.15.2
# ====================================

"""
Canonical ownership model for Gordon Core state aggregates.

This module extends Phase 3.15.1 with explicit ownership metadata including:

    OWNERSHIP:
        - owner identity (exactly one mutation owner per mutable aggregate)
        - owner type (kind of entity owning the state)
        - authority type (what operations are permitted)
        - acquisition evidence (how ownership was obtained)
        - acquisition timestamp
        - provenance
        - transfer policy
        - relinquish policy
        
    AUTHORITY TYPES:
        EXCLUSIVE_MUTATION  - One exclusive owner who may mutate
        SHARED_OBSERVATION  - Multiple observers, no mutation
        DERIVED_VIEW        - Derived view (observation only)
        PERSISTENCE_WRITER  - May persist but not mutate live state
        RESTORATION_AUTHORITY - May restore from persistence
        VALIDATION_AUTHORITY - May validate operations
        TRANSITION_AUTHORITY - May perform state transitions

    TRANSFER:
        Policy-based ownership transfer with evidence preservation
"""

# =============================================================================
# IMPORTS - Import-time purity maintained
# =============================================================================

from dataclasses import dataclass, field
from typing import (
    Optional,
    Tuple,
    Protocol,
    runtime_checkable,
)
from enum import Enum, auto
import time as _time_module
import uuid
from abc import ABC, abstractmethod

# =============================================================================
# OWNERSHIP AUTHORITY TYPES
# =============================================================================


class OwnershipAuthorityType(Enum):
    """
    Canonical authority types for state ownership.
    
    TYPES:
        EXCLUSIVE_MUTATION  - One exclusive owner who may mutate
        SHARED_OBSERVATION  - Multiple observers, no mutation
        DERIVED_VIEW        - Derived view (observation only)
        PERSISTENCE_WRITER  - May persist but not mutate live state
        RESTORATION_AUTHORITY - May restore from persistence
        VALIDATION_AUTHORITY - May validate operations
        TRANSITION_AUTHORITY - May perform state transitions
    
    INVARIANTS:
        AUTH-001: Exactly one EXCLUSIVE_MUTATION owner per mutable aggregate
        AUTH-002: Multiple SHARED_OBSERVATION authorities may exist
        AUTH-003: PERSISTENCE_WRITER does not imply live mutation authority
    """
    
    EXCLUSIVE_MUTATION = "exclusive_mutation"
    SHARED_OBSERVATION = "shared_observation"
    DERIVED_VIEW = "derived_view"
    PERSISTENCE_WRITER = "persistence_writer"
    RESTORATION_AUTHORITY = "restoration_authority"
    VALIDATION_AUTHORITY = "validation_authority"
    TRANSITION_AUTHORITY = "transition_authority"


# =============================================================================
# OWNERSHIP TRANSFER POLICY
# =============================================================================


class OwnershipTransferPolicy(Enum):
    """
    Canonical transfer policies for ownership.
    
    POLICIES:
        NEVER         - Transfer is prohibited
        WITH_CONSENT  - Requires current owner's consent
        WITH_POLICY   - Allowed if policy conditions are met
        AUTOMATIC     - Automatic on specific events (e.g., restart)
        CONDITIONAL   - Conditional on external factors
    
    INVARIANTS:
        POL-001: Every ownership has a defined transfer policy
        POL-002: Transfer policies are immutable once set
        POL-003: Policy violations reject transfers
    """
    
    NEVER = "never"
    WITH_CONSENT = "with_consent"
    WITH_POLICY = "with_policy"
    AUTOMATIC = "automatic"
    CONDITIONAL = "conditional"


# =============================================================================
# OWNERSHIP EVIDENCE
# =============================================================================


@dataclass(frozen=True)
class OwnershipEvidence:
    """
    Immutable ownership evidence for a state aggregate.
    
    Every mutable state must have exactly one identifiable owner.
    
    OWNERSHIP PRINCIPLES:
        - Exactly one EXCLUSIVE_MUTATION authority
        - Multiple observers may exist (SHARED_OBSERVATION, etc.)
        - Authority types are orthogonal to mutability classification
    
    INVARIANTS:
        OWN-EVID-001: Every mutable state has exactly one mutation owner
        OWN-EVID-002: Ownership evidence is immutable once created
        OWN-EVID-003: Owner identity cannot be forged (runtime isolation)
        OWN-EVID-004: Transfer creates new evidence, preserves old evidence
    """
    
    # Identity
    ownership_id: str = field(default_factory=lambda: f"own_{uuid.uuid4().hex[:20]}")
    state_id: str
    
    # Owner information
    owner_identity: str
    owner_kind: Optional[str] = None  # e.g., "lifecycle", "execution"
    
    # Authority
    authority_type: OwnershipAuthorityType = OwnershipAuthorityType.EXCLUSIVE_MUTATION
    authority_granted_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Scope of authority
    ownership_scope: str = "local"
    scope_inheritance: Tuple[str, ...] = field(default_factory=tuple)
    
    # Evidence of acquisition
    acquired_via: Optional[str] = None  # e.g., "claim", "transfer", "creation"
    acquisition_evidence_id: Optional[str] = None
    
    # Transfer eligibility
    transfer_eligible: bool = False
    transfer_policy: OwnershipTransferPolicy = OwnershipTransferPolicy.NEVER
    
    # Provenance
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    created_by_identity: Optional[str] = None
    created_via_operation_id: Optional[str] = None
    
    # Runtime binding (for isolation)
    runtime_binding: Optional[str] = None
    boot_session_binding: Optional[str] = None
    
    @classmethod
    def for_mutation_owner(
        cls,
        state_id: str,
        owner_identity: str,
        owner_kind: Optional[str] = None,
        ownership_scope: str = "local",
        runtime_binding: Optional[str] = None,
        boot_session_binding: Optional[str] = None,
    ) -> "OwnershipEvidence":
        """Create ownership evidence for a mutation owner."""
        return cls(
            state_id=state_id,
            owner_identity=owner_identity,
            owner_kind=owner_kind,
            authority_type=OwnershipAuthorityType.EXCLUSIVE_MUTATION,
            ownership_scope=ownership_scope,
            runtime_binding=runtime_binding,
            boot_session_binding=boot_session_binding,
            acquired_via="creation",
        )
    
    @classmethod
    def for_observer(
        cls,
        state_id: str,
        owner_identity: str,
        ownership_scope: str = "local",
        runtime_binding: Optional[str] = None,
    ) -> "OwnershipEvidence":
        """Create ownership evidence for an observer."""
        return cls(
            state_id=state_id,
            owner_identity=owner_identity,
            authority_type=OwnershipAuthorityType.SHARED_OBSERVATION,
            ownership_scope=ownership_scope,
            runtime_binding=runtime_binding,
            acquired_via="observation",
        )
    
    @classmethod
    def for_transfer(
        cls,
        state_id: str,
        new_owner_identity: str,
        source_evidence: "OwnershipEvidence",
        transfer_policy: OwnershipTransferPolicy = OwnershipTransferPolicy.WITH_POLICY,
    ) -> "OwnershipEvidence":
        """Create ownership evidence from a transfer."""
        return cls(
            state_id=state_id,
            owner_identity=new_owner_identity,
            authority_type=source_evidence.authority_type,
            ownership_scope=source_evidence.ownership_scope,
            transfer_eligible=True,
            transfer_policy=transfer_policy,
            acquired_via="transfer",
            acquisition_evidence_id=source_evidence.ownership_id,
            created_by_identity=source_evidence.owner_identity,
            runtime_binding=source_evidence.runtime_binding,
            boot_session_binding=source_evidence.boot_session_binding,
        )
    
    def can_transfer_to(self, target_owner: str) -> Tuple[bool, Optional[str]]:
        """
        Check if ownership can be transferred to the target owner.
        
        Returns:
            (can_transfer: bool, reason: Optional[str])
        """
        # Check transfer policy
        if self.transfer_policy == OwnershipTransferPolicy.NEVER:
            return False, "transfer_not_permitted"
        
        if self.runtime_binding and self.boot_session_binding:
            # Runtime isolation check - can only transfer within same runtime/session
            pass  # Further checks in validator
        
        # Authority type must allow transfer (non-mutation types usually don't)
        if self.authority_type != OwnershipAuthorityType.EXCLUSIVE_MUTATION:
            return False, "authority_type_does_not_allow_transfer"
        
        return True, None


# =============================================================================
# OWNERSHIP TRANSFER EVIDENCE
# =============================================================================


@dataclass(frozen=True)
class OwnershipTransferEvidence:
    """
    Immutable evidence of an ownership transfer.
    
    Transfers must create immutable evidence, never silently reassign ownership.
    
    INVARIANTS:
        XFER-001: Transfer creates new ownership evidence
        XFER-002: Source evidence is preserved in history
        XFER-003: Generation incremented where required
        XFER-004: Policy validation is recorded
    """
    
    # Identity
    transfer_id: str = field(default_factory=lambda: f"xfer_{uuid.uuid4().hex[:20]}")
    transfer_timestamp_utc: float = field(default_factory=_time_module.monotonic)
    
    # Transfer details
    state_id: str
    source_owner_identity: str
    target_owner_identity: str
    
    # Policy validation
    transfer_policy_applied: OwnershipTransferPolicy
    policy_validated: bool
    validation_failure_reason: Optional[str] = None
    
    # Authority preservation
    authority_preserved: bool = True
    new_authority_type: Optional[OwnershipAuthorityType] = None
    
    # Evidence chain
    source_evidence_id: Optional[str] = None
    generation_incremented: bool = False
    new_generation: Optional[int] = None
    
    @classmethod
    def record(
        cls,
        state_id: str,
        source_owner_identity: str,
        target_owner_identity: str,
        transfer_policy: OwnershipTransferPolicy,
        policy_validated: bool,
        source_evidence_id: Optional[str] = None,
        generation_incremented: bool = False,
        new_generation: Optional[int] = None,
    ) -> "OwnershipTransferEvidence":
        """Record a transfer of ownership."""
        return cls(
            state_id=state_id,
            source_owner_identity=source_owner_identity,
            target_owner_identity=target_owner_identity,
            transfer_policy_applied=transfer_policy,
            policy_validated=policy_validated,
            source_evidence_id=source_evidence_id,
            generation_incremented=generation_incremented,
            new_generation=new_generation,
        )


# =============================================================================
# RUNTIME ISOLATION
# =============================================================================


class RuntimeIsolationEnforcement:
    """
    Enforcement of runtime isolation for state ownership.
    
    Runtime A cannot:
        - Mutate Runtime B's state
        - Claim to be Runtime B's owner
        - Restore Runtime B's state without policy
    
    INVARIANTS:
        RT-ISO-001: State belongs to exactly one runtime
        RT-ISO-002: Owner must match state's runtime binding
        RT-ISO-003: Cross-runtime operations require explicit policy
    """
    
    @staticmethod
    def validate_runtime_binding(
        state_runtime_id: Optional[str],
        owner_runtime_id: Optional[str],
        boot_session_id: Optional[str],
        owner_boot_session_id: Optional[str],
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
        authority_types: Tuple[OwnershipAuthorityType, ...],
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that there are no conflicting authority types.
        
        Example conflict: multiple EXCLUSIVE_MUTATION authorities for same state.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        mutation_count = sum(1 for t in authority_types if t == OwnershipAuthorityType.EXCLUSIVE_MUTATION)
        
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
# OWNERSHIP DIAGNOSTICS
# =============================================================================


@dataclass(frozen=True)
class OwnershipDiagnostics:
    """
    Immutable diagnostics for state ownership.
    
    Exposes metadata without exposing mutable state.
    
    INVARIANTS:
        DIAG-OWN-001: Diagnostics are immutable once created
        DIAG-OWN-002: Diagnostics don't expose live handles or secrets
        DIAG-OWN-003: Diagnostics include full ownership history
    """
    
    # State context
    state_id: str
    domain: Optional[str] = None
    scope: Optional[str] = None
    
    # Current ownership
    current_owner_identity: Optional[str] = None
    current_authority_type: Optional[OwnershipAuthorityType] = None
    
    # Ownership history (ordered, oldest first)
    ownership_history: Tuple[str, ...] = field(default_factory=tuple)  # Owner IDs in order
    
    # Transfer history
    transfer_count: int = 0
    last_transfer_at_utc: Optional[float] = None
    
    # Validation summary
    validation_summary: str = "unknown"  # valid, invalid, pending
    
    @classmethod
    def for_state(
        cls,
        state_id: str,
        current_owner_identity: Optional[str] = None,
        current_authority_type: Optional[OwnershipAuthorityType] = None,
        ownership_history: Tuple[str, ...] = tuple(),
    ) -> "OwnershipDiagnostics":
        """Create diagnostics for a state aggregate."""
        return cls(
            state_id=state_id,
            current_owner_identity=current_owner_identity,
            current_authority_type=current_authority_type,
            ownership_history=ownership_history,
        )


# =============================================================================
# PUBLIC API
# =============================================================================

from uuid import uuid4  # Import here to avoid circular issues in __all__


__all__ = [
    # Authority types
    "OwnershipAuthorityType",
    
    # Transfer policy
    "OwnershipTransferPolicy",
    
    # Core classes
    "OwnershipEvidence",
    "OwnershipTransferEvidence",
    
    # Runtime isolation
    "RuntimeIsolationEnforcement",
    
    # Validation
    "OwnershipValidator",
    
    # Diagnostics
    "OwnershipDiagnostics",
]

# Update uuid4 in __all__ with actual function reference
__all__.insert(0, "uuid4")