# Core State Diagnostics - Phase 3.15.2
# =======================================

"""
Canonical diagnostics utilities for Gordon Core state aggregates.

Diagnostics provide:
    - State identity metadata
    - Owner information (without exposing mutable state)
    - Scope context
    - Runtime and session bindings
    - Authority and generation tracking
    - Validation and transfer history
    
All diagnostics are immutable and bounded in size.
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


# =============================================================================
# STATE DIAGNOSTICS
# =============================================================================


@dataclass(frozen=True)
class StateDiagnostics:
    """
    Immutable bounded diagnostics for a state aggregate.
    
    Diagnostics are for debugging and monitoring, not for state logic.
    
    DIAGNOSTIC PRINCIPLES:
        - Diagnostics are immutable once created
        - Diagnostics are bounded (not unbounded append-only)
        - Diagnostics don't include live handles or secrets
    
    INVARIANTS:
        DIAG-001: Diagnostics are immutable once created
        DIAG-002: Diagnostics are bounded in size
        DIAG-003: Diagnostics don't expose live handles
    """
    
    # State identity
    state_id: str
    domain: Optional[str] = None
    scope: Optional[str] = None
    
    # Runtime binding (for isolation)
    runtime_id: Optional[str] = None
    boot_session_id: Optional[str] = None
    
    # Ownership
    owner_identity: Optional[str] = None
    owner_kind: Optional[str] = None  # e.g., "lifecycle", "execution"
    
    # Authority
    authority_type: Optional[str] = None  # e.g., "exclusive_mutation"
    
    # Version and generation
    version_sequence: int = 0
    generation: int = 0
    
    # Mutability classification
    mutability_class: str = "versioned_aggregate"  # e.g., "immutable", "mutable"
    
    # Last operation reference
    last_operation_id: Optional[str] = None
    last_change_id: Optional[str] = None
    
    # Validation summary
    validation_summary: str = "unknown"  # valid, invalid, pending
    
    # Snapshot and view summary (counts)
    snapshot_count: int = 0
    view_count: int = 0
    
    # Failure summary
    failure_count: int = 0
    last_failure_id: Optional[str] = None
    
    # Persistence eligibility
    persistence_eligible: bool = False
    restoration_eligible: bool = False
    
    # Bounded diagnostics history (oldest first, max 10 items)
    recent_findings: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def for_state(
        cls,
        state_id: str,
        domain: Optional[str] = None,
        scope: Optional[str] = None,
        owner_identity: Optional[str] = None,
        owner_kind: Optional[str] = None,
        authority_type: Optional[str] = None,
        version_sequence: int = 0,
        generation: int = 0,
        mutability_class: str = "versioned_aggregate",
    ) -> "StateDiagnostics":
        """Create diagnostics for a state aggregate."""
        return cls(
            state_id=state_id,
            domain=domain,
            scope=scope,
            owner_identity=owner_identity,
            owner_kind=owner_kind,
            authority_type=authority_type,
            version_sequence=version_sequence,
            generation=generation,
            mutability_class=mutability_class,
        )
    
    def add_finding(self, finding: str) -> "StateDiagnostics":
        """Add a finding to diagnostics history (bounded)."""
        # Keep only last 10 findings
        new_findings = tuple(list(self.recent_findings)[-9:] + [finding])
        return dataclass_replace(self, recent_findings=new_findings)


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
    current_authority_type: Optional[str] = None
    
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
        current_authority_type: Optional[str] = None,
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
# RUNTIME DIAGNOSTICS
# =============================================================================


@dataclass(frozen=True)
class RuntimeDiagnostics:
    """
    Immutable diagnostics for a runtime instance.
    
    INVARIANTS:
        DIAG-RT-001: Diagnostics are immutable once created
        DIAG-RT-002: Runtime identity is preserved
        DIAG-RT-003: Session information is bounded
    """
    
    # Runtime identification
    runtime_id: str
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Boot session
    boot_session_id: Optional[str] = None
    
    # State management statistics
    state_count: int = 0
    mutation_owner_states: int = 0
    observer_states: int = 0
    
    # Active operations
    active_operations: int = 0
    pending_transfers: int = 0
    
    # Runtime metadata
    process_id: Optional[str] = None
    host_name: Optional[str] = None
    
    @classmethod
    def for_runtime(
        cls,
        runtime_id: str,
        boot_session_id: Optional[str] = None,
    ) -> "RuntimeDiagnostics":
        """Create diagnostics for a runtime instance."""
        return cls(runtime_id=runtime_id, boot_session_id=boot_session_id)


# =============================================================================
# SCOPE DIAGNOSTICS
# =============================================================================


@dataclass(frozen=True)
class ScopeDiagnostics:
    """
    Immutable diagnostics for a scope context.
    
    INVARIANTS:
        DIAG-SCOPE-001: Diagnostics are immutable once created
        DIAG-SCOPE-002: Scope hierarchy is preserved
        DIAG-SCOPE-003: Visibility boundaries are recorded
    """
    
    # Scope identification
    scope_id: str
    scope_type: str  # e.g., "application", "runtime", "component"
    
    # Parent scope (for inheritance tracking)
    parent_scope_id: Optional[str] = None
    
    # State counts within this scope
    state_count: int = 0
    mutation_owner_states: int = 0
    
    # Runtime binding
    runtime_binding: Optional[str] = None
    
    # Isolation boundaries
    isolation_boundary: str = "scope"  # e.g., "scope", "runtime"
    
    @classmethod
    def for_scope(
        cls,
        scope_id: str,
        scope_type: str,
        parent_scope_id: Optional[str] = None,
    ) -> "ScopeDiagnostics":
        """Create diagnostics for a scope."""
        return cls(scope_id=scope_id, scope_type=scope_type, parent_scope_id=parent_scope_id)


# =============================================================================
# VALIDATION DIAGNOSTICS
# =============================================================================


@dataclass(frozen=True)
class ValidationDiagnostics:
    """
    Immutable diagnostics for validation results.
    
    INVARIANTS:
        DIAG-VAL-001: Diagnostics are immutable once created
        DIAG-VAL-002: Validation history is preserved
        DIAG-VAL-003: Findings are bounded
    """
    
    # Validation identification
    validation_id: str
    
    # Target state
    state_id: Optional[str] = None
    
    # Overall result
    overall_validity: bool = False
    
    # Findings summary
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    
    # Validation context
    validator_identity: Optional[str] = None
    validated_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Findings (bounded)
    findings_summary: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def for_validation(
        cls,
        validation_id: str,
        overall_validity: bool,
        error_count: int = 0,
        warning_count: int = 0,
        info_count: int = 0,
    ) -> "ValidationDiagnostics":
        """Create diagnostics for a validation."""
        return cls(
            validation_id=validation_id,
            overall_validity=overall_validity,
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
        )


# =============================================================================
# TRANSFER DIAGNOSTICS
# =============================================================================


@dataclass(frozen=True)
class TransferDiagnostics:
    """
    Immutable diagnostics for ownership transfers.
    
    INVARIANTS:
        DIAG-XFER-001: Diagnostics are immutable once created
        DIAG-XFER-002: Transfer history is preserved
        DIAG-XFER-003: Evidence chain is recorded
    """
    
    # Transfer identification
    transfer_id: str
    
    # State and ownership
    state_id: str
    source_owner_identity: str
    target_owner_identity: str
    
    # Policy information
    transfer_policy_applied: str  # e.g., "with_consent", "automatic"
    policy_validated: bool = True
    
    # Generation tracking
    generation_incremented: bool = False
    old_generation: Optional[int] = None
    new_generation: Optional[int] = None
    
    # Evidence chain
    source_evidence_id: Optional[str] = None
    transfer_timestamp_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def for_transfer(
        cls,
        transfer_id: str,
        state_id: str,
        source_owner_identity: str,
        target_owner_identity: str,
        transfer_policy_applied: str,
        policy_validated: bool,
    ) -> "TransferDiagnostics":
        """Create diagnostics for a transfer."""
        return cls(
            transfer_id=transfer_id,
            state_id=state_id,
            source_owner_identity=source_owner_identity,
            target_owner_identity=target_owner_identity,
            transfer_policy_applied=transfer_policy_applied,
            policy_validated=policy_validated,
        )


# =============================================================================
# PUBLIC API
# =============================================================================

from dataclasses import replace as dataclass_replace


__all__ = [
    # Diagnostics types
    "StateDiagnostics",
    "OwnershipDiagnostics",
    "RuntimeDiagnostics",
    "ScopeDiagnostics",
    "ValidationDiagnostics",
    "TransferDiagnostics",
]