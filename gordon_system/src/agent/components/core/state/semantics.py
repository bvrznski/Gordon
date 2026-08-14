# Core State Semantics - Phase 3.15.3: Immutable & Mutable State
# ===================================================================

"""
Canonical semantics for immutable and mutable state throughout the Gordon Core.

This module extends Phases 3.15.1-3.15.2 with explicit mutability classification,
mutation boundaries, ownership-controlled mutation, and evidence generation.

ARCHITECTURAL PRINCIPLES:

    IMMUTABILITY:
        - Immutable objects never change after creation
        - Snapshots are observations at a version (not live state)
        - Views are projections (never mutation authorities)
        - Derived state is always reconstructable from source
        - Cached state can be reconstructed, not canonical truth
        
    MUTABILITY:
        - Mutable state exists only behind an owning authority
        - Exactly one owner possesses mutation authority per aggregate
        - Observers remain read-only
        - Mutation occurs only through validated operations
        
    EVIDENCE:
        - Every mutation produces versioned evidence
        - All changes are immutable records (not accessors)
        - Audit trail preserves all mutations with context
        
    BOUNDARIES:
        - Snapshots never become mutable runtime state
        - Views never become mutation authorities  
        - Derived/cached state cannot become canonical truth

MUTABILITY CLASSIFICATIONS:

    IMMUTABLE VALUE OBJECTS:
        - ImmutableValue: Pure immutable data
        - ImmutableMetadata: Immutable metadata about state
        - ImmutableSnapshot: Snapshot at a version (observation)
        - ImmutableView: Projection/filter of state
        
    MUTABLE STATE AGGREGATES:
        - OwnerMutableAggregate: Mutated only by identified owner
        - AppendOnlyAggregate: Append-only events/logs
        - DerivedState: Reconstructable from source
        - CachedState: Ephemeral, reconstructable cache
        - TransientState: Runtime-only, non-persistent
        
    MUTATION CONTROL:
        - MutationAuthority: Single owner with mutation control
        - MutationValidation: Pre-condition checks before mutation
        - MutationAuthorization: Authorization validation
        - MutationBoundary: Encapsulation boundary for mutation

VALIDATION PRINCIPLES:

    IMMUTABLE-001: Immutable objects cannot mutate
    MUTABLE-002: Mutable aggregates remain encapsulated
    OWNERSHIP-003: Ownership rules are preserved
    AUTHORIZATION-004: Mutation requires explicit authorization
    INVARIANT-005: Invariants are preserved through mutations
    VERSION-006: Version progression is monotonic and correct

MUTATION LIFECYCLE:

    Every mutation follows this canonical flow:
    
        StateOperation (request)
            ↓
        Authorization (is authority valid?)
            ↓
        OwnershipVerification (is owner authorized?)
            ↓
        PreconditionValidation (pre-conditions met?)
            ↓
        InvariantValidation (invariants preserved?)
            ↓
        Mutation (actual state change)
            ↓
        VersionIncrement (increment version/generation)
            ↓
        ChangeEvidence (create immutable evidence record)
            ↓
        ImmutableResult (return result + snapshot/view)
            ↓
        Snapshot/ViewGeneration (produce new observation)
            ↓
        Observability (emit events for observers)

IMPLEMENTATION HIERARCHY:

    CoreImmutableState          <- Base interface for all immutable state
        ├── ImmutableValueObject  <- Pure immutable data
        ├── ImmutableMetadata     <- Immutable metadata
        ├── ImmutableSnapshot     <- Snapshot at a version
        └── ImmutableView         <- Projection/filter
        
    CoreMutableAggregate        <- Base class for mutable aggregates
        ├── OwnerMutableAggregate <- Single owner mutation control
        ├── AppendOnlyAggregate   <- Append-only (events, logs)
        └── MutableStateWithDerived <- Supports derived/cached state

"""

# =============================================================================
# IMPORTS - Import-time purity maintained
# =============================================================================

from dataclasses import dataclass, field
from typing import (
    Dict,
    Any,
    Optional,
    TypeVar,
    Generic,
    Tuple,
    Protocol,
    runtime_checkable,
)
from enum import Enum, auto
import uuid
import time as _time_module
from abc import ABC, abstractmethod


# =============================================================================
# MUTABILITY CLASSIFICATION ENUMERATION
# =============================================================================


class StateMutability(Enum):
    """
    Canonical mutability classifications for state artifacts.
    
    IMMUTABLE CLASSES:
        VALUE_OBJECT      - Pure immutable data value (e.g., string, number)
        METADATA          - Immutable metadata about state
        SNAPSHOT          - Immutable snapshot of state at a version
        VIEW              - Immutable projection/view of state
        
    MUTABLE CLASSES:
        OWNER_MUTABLE     - Mutated only by identified owner
        APPEND_ONLY       - Append-only (events, logs)
        TRANSACTIONAL     - Transaction-scoped mutable state
        
    RECONSTRUCTIBLE:
        DERIVED           - Derived from other state (reconstructable)
        CACHED            - Ephemeral cache (can be rebuilt)
        EPHEMERAL         - Runtime-only, non-persistent
        
    EXTERNAL:
        EXTERNAL_READ_ONLY - External source, read-only locally
        EXTERNAL_WRITE_THROUGH - Write-through to external source
    
    INVARIANTS:
        MUT-CLASS-001: Mutability classification is explicit and immutable
        MUT-CLASS-002: Immutable states never change (snapshots, views)
        MUT-CLASS-003: Mutable states have exactly one owner
        MUT-CLASS-004: Reconstructible state cannot become canonical truth
    """
    
    # Pure immutable data
    VALUE_OBJECT = "value_object"
    METADATA = "metadata"
    
    # Immutable observations (snapshots and views)
    SNAPSHOT = "snapshot"
    VIEW = "view"
    
    # Mutable aggregates
    OWNER_MUTABLE = "owner_mutable"
    APPEND_ONLY = "append_only"
    TRANSACTIONAL = "transactional"
    
    # Reconstructible state
    DERIVED = "derived"
    CACHED = "cached"
    EPHEMERAL = "ephemeral"
    
    # External state
    EXTERNAL_READ_ONLY = "external_read_only"
    EXTERNAL_WRITE_THROUGH = "external_write_through"


# =============================================================================
# MUTATION AUTHORITY TYPE ENUMERATION
# =============================================================================


class MutationAuthorityType(Enum):
    """
    Canonical authority types for mutation operations.
    
    TYPES:
        EXCLUSIVE_MUTATION  - One exclusive owner who may mutate
        OBSERVATION         - Read-only observation authority
        VALIDATION          - Validation-only authority (no mutation)
        RECONSTRUCTION      - Reconstruction authority (no live mutation)
        
    INVARIANTS:
        AUTH-001: Exactly one EXCLUSIVE_MUTATION per mutable aggregate
        AUTH-002: Multiple OBSERVATION authorities may exist
        AUTH-003: VALIDATION does not imply mutation authority
        AUTH-004: RECONSTRUCTION does not imply live mutation
    """
    
    EXCLUSIVE_MUTATION = "exclusive_mutation"
    OBSERVATION = "observation"
    VALIDATION = "validation"
    RECONSTRUCTION = "reconstruction"


# =============================================================================
# MUTATION BOUNDARY ENUMERATION
# =============================================================================


class MutationBoundary(Enum):
    """
    Canonical boundary types for mutation control.
    
    BOUNDARIES:
        AGGREGATE_ROOT - Mutation confined to aggregate root
        FIELD_LEVEL    - Field-level mutation granularity
        TRANSACTIONAL  - Transaction-scoped boundary
        
    INVARIANTS:
        BOUND-001: Every mutation respects its boundary
        BOUND-002: Boundary violations reject mutations
        BOUND-003: Boundaries are immutable once defined
    """
    
    AGGREGATE_ROOT = "aggregate_root"
    FIELD_LEVEL = "field_level"
    TRANSACTIONAL = "transactional"


# =============================================================================
# MUTATION RESULT ENUMERATION
# =============================================================================


class MutationResult(Enum):
    """
    Canonical mutation operation results.
    
    SUCCESS RESULTS:
        CREATED       - State was created
        UPDATED       - State was updated
        APPENDED      - Value was appended to append-only state
        TRANSITIONED  - State machine transition completed
        
    REJECTION RESULTS:
        REJECTED      - Operation rejected (validation failed)
        CONFLICTED    - Version/generation conflict detected
        STALE         - Expected version doesn't match current
        UNAUTHORIZED  - Initiating authority lacks permission
        INVALID       - Operation not allowed in current state
        
    ERROR RESULTS:
        CANCELLED     - Operation was cancelled
        TIMED_OUT     - Operation exceeded deadline
        FAILED        - Operation failed (with error)
        
    INVARIANTS:
        RES-001: Every mutation produces exactly one result
        RES-002: Success results include version progression
        RES-003: Failure results include structured error information
    """
    
    # Success outcomes
    CREATED = "created"
    UPDATED = "updated"
    APPENDED = "append"
    TRANSITIONED = "transitioned"
    REPLACED = "replaced"
    
    # Rejection outcomes
    REJECTED = "rejected"
    CONFLICTED = "conflicted"
    STALE = "stale_version"
    UNAUTHORIZED = "unauthorized"
    INVALID = "invalid_operation"
    
    # Error outcomes
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    FAILED = "failed"


# =============================================================================
# MUTATION EVIDENCE - Immutable Record of Change
# =============================================================================


@dataclass(frozen=True)
class MutationEvidence:
    """
    Immutable evidence of a committed mutation.
    
    Every successful mutation produces exactly one immutable evidence record.
    Evidence does NOT provide access to current state - it's historical proof.
    
    EVIDENCE PRINCIPLES:
        - Evidence is immutable once created
        - Each evidence has previous and resulting state versions
        - Evidence includes full authority chain for audit
        - Evidence preserves context (operation, correlation, causation)
        
    INVARIANTS:
        EVD-001: Evidence is immutable once created
        EVD-002: Each evidence has a previous version reference
        EVD-003: Evidence includes initiating authority chain
        EVD-004: Evidence preserves full context for debugging/audit
    """
    
    # Identity
    evidence_id: str = field(default_factory=lambda: f"evd_{uuid.uuid4().hex[:20]}")
    
    # Target state reference
    state_id: str
    state_domain: Optional[str] = None
    
    # Version context
    previous_version_sequence: int
    resulting_version_sequence: int
    generation_at_mutation: int
    
    # Mutation details
    operation_kind: str  # e.g., "update", "append", "transition"
    affected_fields: Tuple[str, ...] = field(default_factory=tuple)
    
    # Authority chain (for audit)
    initiating_authority: str
    authorized_by_owner: bool
    authorization_method: Optional[str] = None  # e.g., "direct", "delegation"
    
    # Pre- and post-invariant state
    pre_invariant_valid: bool
    post_invariant_valid: bool
    
    # Context
    operation_id: Optional[str] = None
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Timing
    occurred_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Provenance
    source_system: Optional[str] = None
    source_operation_id: Optional[str] = None
    
    @classmethod
    def record(
        cls,
        state_id: str,
        previous_version_sequence: int,
        resulting_version_sequence: int,
        initiating_authority: str,
        operation_kind: str,
        affected_fields: Optional[Tuple[str, ...]] = None,
        pre_invariant_valid: bool = True,
        post_invariant_valid: bool = True,
        authorized_by_owner: bool = True,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
    ) -> "MutationEvidence":
        """Create immutable mutation evidence."""
        return cls(
            state_id=state_id,
            previous_version_sequence=previous_version_sequence,
            resulting_version_sequence=resulting_version_sequence,
            generation_at_mutation=0,  # Set by state owner
            operation_kind=operation_kind,
            affected_fields=affected_fields or tuple(),
            initiating_authority=initiating_authority,
            authorized_by_owner=authorized_by_owner,
            pre_invariant_valid=pre_invariant_valid,
            post_invariant_valid=post_invariant_valid,
            correlation_id=correlation_id,
            causation_id=causation_id,
        )


# =============================================================================
# MUTATION AUDIT RECORD - Complete Audit Trail
# =============================================================================


@dataclass(frozen=True)
class MutationAuditRecord:
    """
    Immutable audit record for mutation operations.
    
    Audit records provide complete traceability of all mutations including
    authorization, validation, execution, and outcome.
    
    AUDIT PRINCIPLES:
        - Audit is immutable once created
        - Full authority chain preserved (who authorized whom)
        - All validations recorded with their findings
        - Execution context fully preserved
        
    INVARIANTS:
        AUD-001: Audit record is immutable once created
        AUD-002: Authority chain is complete and unbroken
        AUD-003: Validation findings are all preserved
        AUD-004: Execution context is fully recorded
    """
    
    # Identity
    audit_id: str = field(default_factory=lambda: f"audit_{uuid.uuid4().hex[:20]}")
    
    # Mutation reference
    evidence_id: Optional[str] = None  # If mutation occurred
    
    # Authorization trail
    requested_at_utc: float
    authorized_at_utc: Optional[float] = None
    authorization_result: str = "pending"  # pending, granted, denied
    
    # Validation trail
    pre_validation_passed: bool = False
    invariant_validation_passed: bool = False
    validation_findings: Tuple[str, ...] = field(default_factory=tuple)
    
    # Execution context
    initiating_authority: str
    execution_result: str = "pending"  # pending, success, failure
    
    # Outcome
    result_code: Optional[MutationResult] = None
    resulting_version_sequence: Optional[int] = None
    
    # Timing
    completed_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def record_authorization(
        cls,
        initiating_authority: str,
        requested_at_utc: float,
        authorized: bool,
        reason: Optional[str] = None,
    ) -> "MutationAuditRecord":
        """Create audit record at authorization stage."""
        return cls(
            initiating_authority=initiating_authority,
            requested_at_utc=requested_at_utc,
            authorized_at_utc=_time_module.monotonic(),
            authorization_result="granted" if authorized else "denied",
            validation_findings=tuple([reason or ""]) if reason else tuple(),
        )
    
    @classmethod
    def record_validation(
        cls,
        initiating_authority: str,
        pre_passed: bool,
        invariant_passed: bool,
        findings: Tuple[str, ...],
    ) -> "MutationAuditRecord":
        """Create audit record at validation stage."""
        return cls(
            initiating_authority=initiating_authority,
            requested_at_utc=_time_module.monotonic(),
            pre_validation_passed=pre_passed,
            invariant_validation_passed=invariant_passed,
            validation_findings=findings,
        )
    
    @classmethod
    def complete(
        cls,
        evidence_id: str,
        result_code: MutationResult,
        resulting_version_sequence: Optional[int],
        completed_at_utc: Optional[float] = None,
    ) -> "MutationAuditRecord":
        """Complete an audit record with final outcome."""
        return cls(
            evidence_id=evidence_id,
            authorization_result="granted",
            pre_validation_passed=True,
            invariant_validation_passed=True,
            execution_result="success" if result_code.value.startswith("create") or result_code.value.startswith("update") else "failure",
            result_code=result_code,
            resulting_version_sequence=resulting_version_sequence,
            completed_at_utc=completed_at_utc or _time_module.monotonic(),
        )


# =============================================================================
# MUTATION AUTHORIZATION - Authorization Context
# =============================================================================


@dataclass(frozen=True)
class MutationAuthorization:
    """
    Immutable authorization context for mutation operations.
    
    Authorization determines whether a mutation request should proceed based on:
        - Authority validity (is the authority token valid?)
        - Ownership verification (does owner match state's owner?)
        - Permission check (does authority have permission for this operation?)
        
    INVARIANTS:
        AUTH-REQ-001: Authorization is immutable once created
        AUTH-REQ-002: Authorization does not imply execution
        AUTH-REQ-003: Authorization result is explicit (granted/denied)
    """
    
    # Identity
    authorization_id: str = field(default_factory=lambda: f"auth_{uuid.uuid4().hex[:20]}")
    
    # Target state
    state_id: str
    expected_owner_identity: Optional[str] = None
    
    # Authority token
    authority_token: str  # e.g., JWT, signature, etc.
    authority_kind: str  # e.g., "owner", "delegated", "system"
    
    # Requested operation
    requested_operation: str  # e.g., "update", "delete", "transition"
    
    # Authorization decision
    is_authorized: bool = False
    authorization_reason: Optional[str] = None
    
    # Timing
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    expires_at_utc: Optional[float] = None
    
    @classmethod
    def request(
        cls,
        state_id: str,
        authority_token: str,
        authority_kind: str,
        requested_operation: str,
        expected_owner_identity: Optional[str] = None,
    ) -> "MutationAuthorization":
        """Create an authorization request."""
        return cls(
            state_id=state_id,
            authority_token=authority_token,
            authority_kind=authority_kind,
            requested_operation=requested_operation,
            expected_owner_identity=expected_owner_identity,
        )
    
    def grant(self, reason: Optional[str] = None) -> "MutationAuthorization":
        """Grant this authorization."""
        return MutationAuthorization(
            authorization_id=self.authorization_id,
            state_id=self.state_id,
            expected_owner_identity=self.expected_owner_identity,
            authority_token=self.authority_token,
            authority_kind=self.authority_kind,
            requested_operation=self.requested_operation,
            is_authorized=True,
            authorization_reason=reason,
            created_at_utc=self.created_at_utc,
            expires_at_utc=self.expires_at_utc,
        )
    
    def deny(self, reason: str) -> "MutationAuthorization":
        """Deny this authorization."""
        return MutationAuthorization(
            authorization_id=self.authorization_id,
            state_id=self.state_id,
            expected_owner_identity=self.expected_owner_identity,
            authority_token=self.authority_token,
            authority_kind=self.authority_kind,
            requested_operation=self.requested_operation,
            is_authorized=False,
            authorization_reason=reason,
            created_at_utc=self.created_at_utc,
            expires_at_utc=self.expires_at_utc,
        )


# =============================================================================
# MUTATION VALIDATOR - Pre-mutation Validation
# =============================================================================


class MutationValidator:
    """
    Validates mutations before they occur.
    
    VALIDATIONS PERFORMED:
        - Immutable object cannot be mutated (type check)
        - Mutable aggregates remain encapsulated (no direct field access)
        - Ownership rules are respected
        - Authorization is granted for mutation operations
        - Pre-conditions are met
        - Invariants will be preserved
        
    RETURNS structured validation findings, not just Boolean results.
    """
    
    @staticmethod
    def validate_immutable_target(
        target_mutability: StateMutability,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that immutable targets cannot be mutated.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        if target_mutability in (
            StateMutability.VALUE_OBJECT,
            StateMutability.METADATA,
            StateMutability.SNAPSHOT,
            StateMutability.VIEW,
            StateMutability.EXTERNAL_READ_ONLY,
        ):
            return False, f"immutable_target: {target_mutability.value} cannot be mutated"
        
        return True, None
    
    @staticmethod
    def validate_mutable_encapsulation(
        mutation_boundary: MutationBoundary,
        field_accessed: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that mutable aggregates remain encapsulated.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        # Aggregate root boundary: only aggregate-level operations allowed
        if mutation_boundary == MutationBoundary.AGGREGATE_ROOT and field_accessed:
            return False, f"encapsulation_violation: aggregate_root boundary forbids direct field access to {field_accessed}"
        
        return True, None
    
    @staticmethod
    def validate_ownership(
        current_owner: Optional[str],
        expected_owner: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that mutation owner matches state's owner.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        if current_owner is None:
            return True, None  # No owner set yet
        
        if current_owner != expected_owner:
            return False, f"ownership_mismatch: state owned by {current_owner}, mutation requested by {expected_owner}"
        
        return True, None
    
    @staticmethod
    def validate_authorization(
        is_authorized: bool,
        reason: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that authorization is granted.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        if not is_authorized:
            return False, f"unauthorized_mutation: {reason or 'authorization denied'}"
        
        return True, None
    
    @staticmethod
    def validate_preconditions(
        preconditions_met: bool,
        missing_conditions: Tuple[str, ...] = tuple(),
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that all pre-conditions are met.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        if not preconditions_met:
            return False, f"precondition_failed: missing conditions {missing_conditions}"
        
        return True, None
    
    @staticmethod
    def validate_invariants(
        invariant_valid: bool,
        violated_invariants: Tuple[str, ...] = tuple(),
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that invariants will be preserved by mutation.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        if not invariant_valid:
            return False, f"invariant_violation: {violated_invariants}"
        
        return True, None


# =============================================================================
# MUTATION BOUNDARY ENFORCEMENT
# =============================================================================


class MutationBoundaryEnforcement:
    """
    Enforces mutation boundaries for state aggregates.
    
    BOUNDARY TYPES:
        AGGREGATE_ROOT - Only aggregate-level operations allowed
        FIELD_LEVEL    - Field-level access controlled by boundary rules
        TRANSACTIONAL  - Boundary scoped to transaction
        
    INVARIANTS:
        BOUND-ENV-001: Boundaries are enforced at mutation time
        BOUND-ENV-002: Boundary violations reject mutations
        BOUND-ENV-003: Boundaries cannot be bypassed
    """
    
    @staticmethod
    def enforce_boundary(
        target_boundary: MutationBoundary,
        operation_kind: str,
        field_accessed: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Enforce mutation boundary for an operation.
        
        Returns:
            (allowed: bool, reason: Optional[str])
        """
        if target_boundary == MutationBoundary.AGGREGATE_ROOT:
            # Only aggregate-level operations allowed
            allowed_operations = ("update", "replace", "transition")
            if field_accessed and operation_kind not in allowed_operations:
                return False, f"aggregate_root_boundary_violation: {operation_kind} cannot access individual field {field_accessed}"
        
        elif target_boundary == MutationBoundary.FIELD_LEVEL:
            # Field-level access requires boundary token
            pass  # Further validation in owner
        
        return True, None
    
    @staticmethod
    def check_transaction_boundary(
        operation_kind: str,
        transactional_state: bool,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if operation respects transaction boundary.
        
        Returns:
            (allowed: bool, reason: Optional[str])
        """
        if not transactional_state and operation_kind == "transaction":
            return False, "non_transactional_state_cannot_perform_transaction_operations"
        
        return True, None


# =============================================================================
# IMMUTABLE STATE PROTOCOL
# =============================================================================


@runtime_checkable
class CoreImmutableState(Protocol):
    """
    Protocol for all immutable state artifacts.
    
    REQUIREMENTS:
        - ImmutableValueObject: Pure immutable data value
        - ImmutableMetadata: Immutable metadata about state
        - ImmutableSnapshot: Snapshot at a version (observation)
        - ImmutableView: Projection/filter of state
        
    INVARIANTS:
        IMM-PROTO-001: Immutable states never change after creation
        IMM-PROTO-002: No mutation operations are available
        IMM-PROTO-003: All access is read-only
    """
    
    @property
    def mutability_class(self) -> StateMutability:
        """Get the mutability classification."""
        ...
    
    @property
    def state_id(self) -> str:
        """Get the state identifier."""
        ...
    
    @property
    def version_sequence(self) -> int:
        """Get the version sequence number."""
        ...


# =============================================================================
# MUTABLE STATE AGGREGATE BASE CLASS
# =============================================================================


class CoreMutableAggregate(ABC):
    """
    Base class for mutable state aggregates.
    
    Every mutable aggregate must have exactly one mutation owner and follow
    the canonical mutation lifecycle with evidence generation.
    
    AGGREGATE PRINCIPLES:
        - Exactly one EXCLUSIVE_MUTATION owner per aggregate
        - All mutations produce immutable evidence
        - Mutations are validated before execution
        - Version progression is monotonic
        
    INVARIANTS:
        MUT-AGG-001: Exactly one mutation owner per aggregate
        MUT-AGG-002: Each mutation produces immutable evidence
        MUT-AGG-003: Validation occurs before mutation
        MUT-AGG-004: Version increases after each mutation
    """
    
    _state_id: str
    _version_sequence: int
    _generation: int
    _owner_identity: Optional[str]
    _mutability_class: StateMutability
    _evidence_history: Tuple[MutationEvidence, ...]
    
    def __init__(
        self,
        state_id: str,
        owner_identity: Optional[str] = None,
        mutability_class: StateMutability = StateMutability.OWNER_MUTABLE,
        version_sequence: int = 0,
        generation: int = 0,
    ):
        """Initialize the mutable aggregate."""
        self._state_id = state_id
        self._owner_identity = owner_identity
        self._mutability_class = mutability_class
        self._version_sequence = version_sequence
        self._generation = generation
        self._evidence_history: Tuple[MutationEvidence, ...] = tuple()
    
    @property
    def state_id(self) -> str:
        """Get the state identifier."""
        return self._state_id
    
    @property
    def version(self) -> int:
        """Get the current version sequence."""
        return self._version_sequence
    
    @property
    def generation(self) -> int:
        """Get the current generation (epoch)."""
        return self._generation
    
    @property
    def owner_identity(self) -> Optional[str]:
        """Get the mutation owner identity."""
        return self._owner_identity
    
    @property
    def mutability_class(self) -> StateMutability:
        """Get the mutability classification."""
        return self._mutability_class
    
    @property
    def evidence_history(self) -> Tuple[MutationEvidence, ...]:
        """Get the immutable evidence history."""
        return self._evidence_history
    
    def _validate_mutation_authorization(
        self,
        requesting_authority: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that the requesting authority is authorized for mutation.
        
        Returns:
            (authorized: bool, reason: Optional[str])
        """
        if self._owner_identity is None:
            return True, None  # No owner set yet
        
        if requesting_authority != self._owner_identity:
            return False, f"unauthorized: {requesting_authority} is not the owner ({self._owner_identity})"
        
        return True, None
    
    def _create_mutation_evidence(
        self,
        previous_version_sequence: int,
        operation_kind: str,
        initiating_authority: str,
        affected_fields: Optional[Tuple[str, ...]] = None,
        pre_invariant_valid: bool = True,
        post_invariant_valid: bool = True,
    ) -> MutationEvidence:
        """Create immutable mutation evidence for a change."""
        return MutationEvidence.record(
            state_id=self._state_id,
            previous_version_sequence=previous_version_sequence,
            resulting_version_sequence=self._version_sequence + 1,
            initiating_authority=initiating_authority,
            operation_kind=operation_kind,
            affected_fields=affected_fields,
            pre_invariant_valid=pre_invariant_valid,
            post_invariant_valid=post_invariant_valid,
            authorized_by_owner=True,  # Set by owner
        )
    
    def _record_mutation(
        self,
        evidence: MutationEvidence,
    ) -> None:
        """Record mutation evidence (immutable, appends to history)."""
        self._evidence_history = self._evidence_history + (evidence,)
    
    @abstractmethod
    def validate_mutation(
        self,
        operation_kind: str,
        requesting_authority: str,
        preconditions_met: bool,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a mutation before execution.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        ...
    
    @abstractmethod
    def apply_mutation(
        self,
        operation_kind: str,
        requesting_authority: str,
        **kwargs,
    ) -> Tuple[MutationResult, Optional[int]]:
        """
        Apply a mutation and return the result.
        
        Returns:
            (result_code: MutationResult, new_version_sequence: Optional[int])
        """
        ...


# =============================================================================
# OWNER MUTABLE AGGREGATE
# =============================================================================


class OwnerMutableAggregate(CoreMutableAggregate):
    """
    Mutable aggregate with exactly one owner for mutation control.
    
    OWNERSHIP MODEL:
        - Exactly one EXCLUSIVE_MUTATION owner per aggregate
        - Observers may exist but cannot mutate
        - Mutation requires owner authorization
        
    MUTATION FLOW:
        1. Request (operation_kind, authority_token)
        2. Authorization check
        3. Pre-condition validation
        4. Invariant validation
        5. Apply mutation
        6. Increment version
        7. Create evidence
        8. Return result
        
    INVARIANTS:
        OWN-AGG-001: Exactly one owner per aggregate
        OWN-AGG-002: Only owner may mutate
        OWN-AGG-003: Evidence is created for every mutation
        OWN-AGG-004: Version increases after each mutation
    """
    
    def __init__(
        self,
        state_id: str,
        owner_identity: Optional[str] = None,
        version_sequence: int = 0,
        generation: int = 0,
    ):
        """Initialize the owner-mutable aggregate."""
        super().__init__(
            state_id=state_id,
            owner_identity=owner_identity,
            mutability_class=StateMutability.OWNER_MUTABLE,
            version_sequence=version_sequence,
            generation=generation,
        )
        self._data: Dict[str, Any] = {}  # Internal mutable data (encapsulated)
    
    def validate_mutation(
        self,
        operation_kind: str,
        requesting_authority: str,
        preconditions_met: bool,
    ) -> Tuple[bool, Optional[str]]:
        """Validate a mutation before execution."""
        # Check authorization
        authorized, reason = self._validate_mutation_authorization(requesting_authority)
        if not authorized:
            return False, f"authorization_failed: {reason}"
        
        # Check pre-conditions
        if not preconditions_met:
            return False, "precondition_not_met"
        
        # Check invariant preservation
        # (In a real implementation, this would check the operation against invariants)
        
        return True, None
    
    def apply_mutation(
        self,
        operation_kind: str,
        requesting_authority: str,
        **kwargs,
    ) -> Tuple[MutationResult, Optional[int]]:
        """
        Apply a mutation and return the result.
        
        Supports:
            - update: Update internal data
            - replace: Replace entire data structure
            - delete: Remove data
        
        Returns:
            (result_code: MutationResult, new_version_sequence: Optional[int])
        """
        # Validate before applying
        preconditions_met = kwargs.get("preconditions_met", True)
        is_authorized, reason = self._validate_mutation_authorization(requesting_authority)
        
        if not is_authorized:
            return MutationResult.UNAUTHORIZED, None
        
        if not preconditions_met:
            return MutationResult.REJECTED, None
        
        # Execute mutation
        previous_version = self._version_sequence
        
        if operation_kind == "update":
            # Update internal data
            for key, value in kwargs.get("updates", {}).items():
                self._data[key] = value
            
            # Create evidence
            evidence = self._create_mutation_evidence(
                previous_version,
                "update",
                requesting_authority,
                affected_fields=tuple(kwargs.get("updates", {}).keys()),
            )
            self._record_mutation(evidence)
            
            # Increment version
            self._version_sequence += 1
            
            return MutationResult.UPDATED, self._version_sequence
        
        elif operation_kind == "replace":
            # Replace entire data structure
            new_data = kwargs.get("new_data", {})
            self._data = dict(new_data) if new_data else {}
            
            evidence = self._create_mutation_evidence(
                previous_version,
                "replace",
                requesting_authority,
            )
            self._record_mutation(evidence)
            
            self._version_sequence += 1
            
            return MutationResult.REPLACED, self._version_sequence
        
        elif operation_kind == "delete":
            # Delete specific fields or all
            delete_fields = kwargs.get("fields", [])
            
            for field in delete_fields:
                self._data.pop(field, None)
            
            evidence = self._create_mutation_evidence(
                previous_version,
                "delete",
                requesting_authority,
                affected_fields=tuple(delete_fields),
            )
            self._record_mutation(evidence)
            
            self._version_sequence += 1
            
            return MutationResult.UPDATED, self._version_sequence
        
        else:
            return MutationResult.INVALID, None
    
    def get_data(self) -> Dict[str, Any]:
        """Get a read-only view of current data (snapshot)."""
        # Return a copy to ensure immutability
        return dict(self._data)
    
    def get_snapshot(self) -> "ImmutableSnapshotView":
        """Create an immutable snapshot view of current state."""
        return ImmutableSnapshotView(
            state_id=self._state_id,
            version_sequence=self._version_sequence,
            data=dict(self._data),
        )


# =============================================================================
# APPEND-ONLY AGGREGATE
# =============================================================================


class AppendOnlyAggregate(CoreMutableAggregate):
    """
    Aggregate that supports only append operations (events, logs).
    
    APPEND-ONLY PRINCIPLES:
        - New items can be appended
        - Existing items cannot be modified or deleted
        - Items have natural ordering
        - Append is idempotent with same key
        
    USE CASES:
        - Event logs
        - Audit trails
        - Time-series data
        - Change history
        
    INVARIANTS:
        APP-AGG-001: Only append operations allowed
        APP-AGG-002: Existing items immutable
        APP-AGG-003: Items have natural ordering
        APP-AGG-004: Append can be idempotent with key
    """
    
    def __init__(
        self,
        state_id: str,
        owner_identity: Optional[str] = None,
        version_sequence: int = 0,
        generation: int = 0,
    ):
        """Initialize the append-only aggregate."""
        super().__init__(
            state_id=state_id,
            owner_identity=owner_identity,
            mutability_class=StateMutability.APPEND_ONLY,
            version_sequence=version_sequence,
            generation=generation,
        )
        self._items: Dict[str, Any] = {}  # Key -> item mapping
    
    def validate_mutation(
        self,
        operation_kind: str,
        requesting_authority: str,
        preconditions_met: bool,
    ) -> Tuple[bool, Optional[str]]:
        """Validate an append operation."""
        # Only allow append operations
        if operation_kind not in ("append", "add"):
            return False, f"append_only_aggregate_only_allows_append_operations, got {operation_kind}"
        
        # Check authorization
        authorized, reason = self._validate_mutation_authorization(requesting_authority)
        if not authorized:
            return False, f"authorization_failed: {reason}"
        
        # Check pre-conditions
        if not preconditions_met:
            return False, "precondition_not_met"
        
        return True, None
    
    def apply_mutation(
        self,
        operation_kind: str,
        requesting_authority: str,
        **kwargs,
    ) -> Tuple[MutationResult, Optional[int]]:
        """
        Apply an append mutation.
        
        Args:
            key: Unique key for the appended item
            value: Value to append
            
        Returns:
            (result_code: MutationResult, new_version_sequence: Optional[int])
        """
        if operation_kind not in ("append", "add"):
            return MutationResult.INVALID, None
        
        is_authorized, reason = self._validate_mutation_authorization(requesting_authority)
        
        if not is_authorized:
            return MutationResult.UNAUTHORIZED, None
        
        key = kwargs.get("key")
        value = kwargs.get("value")
        
        if key is None or value is None:
            return MutationResult.REJECTED, None
        
        # Check for existing key (append-only: may be idempotent)
        if key in self._items:
            # Idempotent append: return same result
            evidence = self._create_mutation_evidence(
                self._version_sequence,
                "append",
                requesting_authority,
                affected_fields=(key,),
            )
            self._record_mutation(evidence)
            
            return MutationResult.CREATED, self._version_sequence
        
        # Append new item
        previous_version = self._version_sequence
        self._items[key] = value
        
        evidence = self._create_mutation_evidence(
            previous_version,
            "append",
            requesting_authority,
            affected_fields=(key,),
        )
        self._record_mutation(evidence)
        
        self._version_sequence += 1
        
        return MutationResult.APPENDED, self._version_sequence
    
    def get_items(self) -> Dict[str, Any]:
        """Get read-only view of items (snapshot)."""
        return dict(self._items)
    
    def get_snapshot(self) -> "ImmutableSnapshotView":
        """Create an immutable snapshot view."""
        return ImmutableSnapshotView(
            state_id=self._state_id,
            version_sequence=self._version_sequence,
            data=dict(self._items),
        )


# =============================================================================
# DERIVED STATE
# =============================================================================


class DerivedState:
    """
    State that is derived from other state (reconstructable).
    
    DERIVED PRINCIPLES:
        - Not canonical truth (source of truth)
        - Always reconstructable from source
        - Cache or computed value
        - Can be invalidated when source changes
        
    USE CASES:
        - Computed values from aggregates
        - Materialized views
        - Aggregated statistics
        - Cached results
        
    INVARIANTS:
        DER-AGG-001: Derived state is not canonical truth
        DER-AGG-002: Always reconstructable from source
        DER-AGG-003: Can be invalidated when source changes
        DER-AGG-004: Source tracking preserved for invalidation
    """
    
    def __init__(
        self,
        state_id: str,
        derived_from_state_ids: Tuple[str, ...],
        mutability_class: StateMutability = StateMutability.DERIVED,
    ):
        """Initialize derived state."""
        self._state_id = state_id
        self._derived_from_state_ids = derived_from_state_ids
        self._mutability_class = mutability_class
        self._value: Optional[Any] = None
        self._version_sequence: int = 0
    
    @property
    def state_id(self) -> str:
        """Get the state identifier."""
        return self._state_id
    
    @property
    def version(self) -> int:
        """Get the version sequence."""
        return self._version_sequence
    
    @property
    def mutability_class(self) -> StateMutability:
        """Get the mutability classification."""
        return self._mutability_class
    
    @property
    def derived_from_state_ids(self) -> Tuple[str, ...]:
        """Get source state IDs."""
        return self._derived_from_state_ids
    
    def get_value(self) -> Optional[Any]:
        """Get current value (can be None if not computed)."""
        return self._value
    
    def compute(self, sources: Dict[str, Any]) -> Any:
        """
        Compute derived value from source states.
        
        Returns:
            Computed value
        """
        # Implementation would compute based on sources
        # This is a placeholder for actual computation logic
        self._value = self._compute_from_sources(sources)
        self._version_sequence += 1
        return self._value
    
    def _compute_from_sources(self, sources: Dict[str, Any]) -> Any:
        """
        Compute derived value from source states.
        
        Override in subclasses with actual computation logic.
        """
        # Placeholder implementation - should be overridden
        return None
    
    def invalidate(self) -> None:
        """Invalidate the derived state (set to None)."""
        self._value = None


# =============================================================================
# CACHED STATE
# =============================================================================


class CachedState:
    """
    Ephemeral cache state that can be reconstructed.
    
    CACHE PRINCIPLES:
        - Not canonical truth
        - Can be rebuilt from source when needed
        - May be evicted for memory management
        - Version tracking for staleness detection
        
    USE CASES:
        - Computed value caching
        - Result caching
        - Lookup cache
        
    INVARIANTS:
        CACHE-AGG-001: Cache is not canonical truth
        CACHE-AGG-002: Can be rebuilt from source
        CACHE-AGG-003: May be evicted for memory management
        CACHE-AGG-004: Version tracking for staleness detection
    """
    
    def __init__(
        self,
        state_id: str,
        cache_key: str,
        ttl_seconds: float = 300.0,  # Default 5 minutes
    ):
        """Initialize cached state."""
        self._state_id = state_id
        self._cache_key = cache_key
        self._ttl_seconds = ttl_seconds
        self._value: Optional[Any] = None
        self._cached_at_utc: Optional[float] = None
        self._version_sequence: int = 0
    
    @property
    def state_id(self) -> str:
        """Get the state identifier."""
        return self._state_id
    
    @property
    def cache_key(self) -> str:
        """Get the cache key."""
        return self._cache_key
    
    @property
    def version(self) -> int:
        """Get the version sequence."""
        return self._version_sequence
    
    @property
    def mutability_class(self) -> StateMutability:
        """Get the mutability classification (ephemeral)."""
        return StateMutability.CACHED
    
    def get_value(self, sources: Dict[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        Get cached value if valid, otherwise compute from source.
        
        Returns:
            (is_valid: bool, value: Optional[Any])
        """
        if self._value is not None and self._cached_at_utc is not None:
            # Check TTL
            elapsed = _time_module.monotonic() - self._cached_at_utc
            if elapsed < self._ttl_seconds:
                return True, self._value
        
        # Cache invalid or expired, need to recompute
        computed_value = self._recompute_from_source(sources)
        self.set_value(computed_value)
        
        return False, computed_value
    
    def set_value(self, value: Any) -> None:
        """Set cached value (for manual cache population)."""
        self._value = value
        self._cached_at_utc = _time_module.monotonic()
        self._version_sequence += 1
    
    def _recompute_from_source(self, sources: Dict[str, Any]) -> Any:
        """
        Recompute value from source states.
        
        Override in subclasses with actual computation logic.
        """
        return None
    
    def invalidate(self) -> None:
        """Invalidate the cache entry."""
        self._value = None
        self._cached_at_utc = None


# =============================================================================
# TRANSIENT STATE
# =============================================================================


class TransientState:
    """
    Runtime-only state that is not persisted.
    
    TRANSIENT PRINCIPLES:
        - Exists only in runtime memory
        - Not persisted across restarts
        - May be recreated from other state if needed
        - Fast access, no durability guarantees
        
    USE CASES:
        - Runtime flags
        - Temporary computed values
        - Session-scoped state
        
    INVARIANTS:
        TRANS-AGG-001: Exists only in runtime memory
        TRANS-AGG-002: Not persisted across restarts
        TRANS-AGG-003: May be recreated from other state
        TRANS-AGG-004: Fast access, no durability guarantees
    """
    
    def __init__(
        self,
        state_id: str,
        mutability_class: StateMutability = StateMutability.EPHEMERAL,
    ):
        """Initialize transient state."""
        self._state_id = state_id
        self._mutability_class = mutability_class
        self._value: Optional[Any] = None
        self._version_sequence: int = 0
    
    @property
    def state_id(self) -> str:
        """Get the state identifier."""
        return self._state_id
    
    @property
    def version(self) -> int:
        """Get the version sequence."""
        return self._version_sequence
    
    @property
    def mutability_class(self) -> StateMutability:
        """Get the mutability classification (ephemeral)."""
        return self._mutability_class
    
    def get_value(self) -> Optional[Any]:
        """Get current value."""
        return self._value
    
    def set_value(self, value: Any, version_increment: bool = True) -> None:
        """Set value (no persistence guarantee)."""
        self._value = value
        if version_increment:
            self._version_sequence += 1
    
    def invalidate(self) -> None:
        """Invalidate the transient state."""
        self._value = None


# =============================================================================
# IMMUTABLE SNAPSHOT VIEW
# =============================================================================


@dataclass(frozen=True)
class ImmutableSnapshotView:
    """
    Immutable view of a snapshot at a specific version.
    
    SNAPSHOT PRINCIPLES:
        - Snapshot is immutable once created
        - Does NOT provide mutation access
        - Identifies source state, version, and generation
        - Can be used for observation only
        
    INVARIANTS:
        SNAP-VIEW-001: View is immutable once created
        SNAP-VIEW-002: View does not become a second mutable authority
        SNAP-VIEW-003: View identifies source state, version, and generation
    """
    
    # Identity
    view_id: str = field(default_factory=lambda: f"view_{uuid.uuid4().hex[:20]}")
    
    # Source identification
    state_id: str
    version_sequence: int
    generation: int
    
    # Snapshot content (immutable)
    data: Dict[str, Any]
    captured_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def capture(
        cls,
        state_id: str,
        version_sequence: int,
        data: Dict[str, Any],
        generation: int = 0,
    ) -> "ImmutableSnapshotView":
        """Create an immutable snapshot view."""
        return cls(
            state_id=state_id,
            version_sequence=version_sequence,
            generation=generation,
            data=dict(data),  # Copy to ensure immutability
        )
    
    def get_data(self) -> Dict[str, Any]:
        """Get a read-only copy of the snapshot data."""
        return dict(self.data)
    
    def has_field(self, field_name: str) -> bool:
        """Check if a field exists in the snapshot."""
        return field_name in self.data
    
    def get_field(self, field_name: str, default: Any = None) -> Any:
        """Get a field value from the snapshot."""
        return self.data.get(field_name, default)


# =============================================================================
# IMMUTABLE VIEW (PROJECTION)
# =============================================================================


@dataclass(frozen=True)
class ImmutableViewProjection:
    """
    Immutable view/projection of state with field selection.
    
    VIEW PRINCIPLES:
        - View is immutable once created
        - Does NOT become a hidden cache of mutable truth
        - Identifies source state, version, and projection
        
    INVARIANTS:
        PROJ-VIEW-001: View is immutable once created
        PROJ-VIEW-002: View does not become a hidden cache of mutable truth
        PROJ-VIEW-003: View identifies source state, version, and projection
    """
    
    # Identity
    view_id: str = field(default_factory=lambda: f"view_{uuid.uuid4().hex[:20]}")
    
    # Source identification
    source_state_id: str
    source_version_sequence: int
    
    # Projection specification
    included_fields: Tuple[str, ...]  # If empty, all fields included
    excluded_fields: Tuple[str, ...]
    
    # Consumer context
    view_type: str = "default"  # e.g., "list", "detail", "summary"
    
    @classmethod
    def project(
        cls,
        source_state_id: str,
        source_version_sequence: int,
        included_fields: Optional[Tuple[str, ...]] = None,
        excluded_fields: Optional[Tuple[str, ...]] = None,
        view_type: str = "default",
    ) -> "ImmutableViewProjection":
        """Create an immutable view projection."""
        return cls(
            source_state_id=source_state_id,
            source_version_sequence=source_version_sequence,
            included_fields=included_fields or tuple(),
            excluded_fields=excluded_fields or tuple(),
            view_type=view_type,
        )
    
    def apply_to_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the projection to data and return filtered result."""
        if not self.included_fields and not self.excluded_fields:
            return dict(data)
        
        # Start with all fields
        result = dict(data)
        
        # Apply exclusions first
        for field in self.excluded_fields:
            result.pop(field, None)
        
        # If inclusion list specified, filter to only those fields
        if self.included_fields:
            result = {k: v for k, v in result.items() if k in self.included_fields}
        
        return result


# =============================================================================
# MUTATION BOUNDARY VALIDATOR
# =============================================================================


class MutationBoundaryValidator:
    """
    Validates that mutations respect their boundaries.
    
    BOUNDARIES:
        AGGREGATE_ROOT - Only aggregate-level operations allowed
        FIELD_LEVEL    - Field access controlled by boundary rules
        TRANSACTIONAL  - Transaction-scoped boundary
        
    VALIDATIONS:
        - Boundary type matches mutation kind
        - Field access respects field-level boundaries
        - Transactional mutations within transaction scope
        
    RETURNS structured validation findings, not just Boolean results.
    """
    
    @staticmethod
    def validate_boundary_for_operation(
        target_boundary: MutationBoundary,
        operation_kind: str,
        fields_accessed: Tuple[str, ...],
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that an operation respects the boundary type.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        if target_boundary == MutationBoundary.AGGREGATE_ROOT:
            # Only aggregate-level operations allowed
            allowed_operations = ("update", "replace", "transition")
            for field in fields_accessed:
                if operation_kind not in allowed_operations:
                    return False, f"aggregate_root_boundary: {operation_kind} cannot access field {field}"
        
        elif target_boundary == MutationBoundary.FIELD_LEVEL:
            # Field-level access requires boundary token
            pass  # Further validation in owner
        
        elif target_boundary == MutationBoundary.TRANSACTIONAL:
            # Transactional operations require transaction context
            if operation_kind not in ("transaction", "commit", "rollback"):
                return False, f"transactional_boundary: {operation_kind} requires transaction context"
        
        return True, None
    
    @staticmethod
    def validate_field_access(
        boundary_type: MutationBoundary,
        field_path: str,
        has_boundary_token: bool,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that field access is permitted.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        if boundary_type == MutationBoundary.FIELD_LEVEL and not has_boundary_token:
            return False, f"field_level_boundary: missing boundary token for {field_path}"
        
        return True, None


# =============================================================================
# PUBLIC API - FOUNDATIONAL FACES
# =============================================================================


def validate_mutation_authorization(
    target_state_mutability: StateMutability,
    requesting_authority: str,
    state_owner: Optional[str],
    is_authorized: bool,
) -> Tuple[bool, Optional[str]]:
    """
    Validate that a mutation request is authorized.
    
    Args:
        target_state_mutability: The mutability classification of the target
        requesting_authority: Who is requesting the mutation
        state_owner: Current owner of the state (if any)
        is_authorized: Whether authorization was granted
        
    Returns:
        (valid: bool, reason: Optional[str])
    """
    # Immutable states cannot be mutated
    if target_state_mutability in (
        StateMutability.VALUE_OBJECT,
        StateMutability.METADATA,
        StateMutability.SNAPSHOT,
        StateMutability.VIEW,
        StateMutability.EXTERNAL_READ_ONLY,
    ):
        return False, f"immutable_target: {target_state_mutability.value} cannot be mutated"
    
    # Check ownership
    if state_owner is not None and requesting_authority != state_owner:
        return False, f"ownership_mismatch: expected {state_owner}, got {requesting_authority}"
    
    # Check authorization
    if not is_authorized:
        return False, "mutation_not_authorized"
    
    return True, None


def create_mutation_audit_record(
    initiating_authority: str,
    requested_at_utc: float,
    authorized: bool,
    pre_validation_passed: bool,
    invariant_validation_passed: bool,
    result_code: MutationResult,
) -> MutationAuditRecord:
    """
    Create a complete mutation audit record.
    
    Returns:
        MutationAuditRecord with all stages recorded
    """
    return MutationAuditRecord(
        audit_id=f"audit_{uuid.uuid4().hex[:20]}",
        requested_at_utc=requested_at_utc,
        authorized_at_utc=_time_module.monotonic() if authorized else None,
        authorization_result="granted" if authorized else "denied",
        pre_validation_passed=pre_validation_passed,
        invariant_validation_passed=invariant_validation_passed,
        validation_findings=tuple(),
        initiating_authority=initiating_authority,
        execution_result="success" if result_code.value in ("created", "updated", "append", "transitioned") else "failure",
        result_code=result_code,
    )


# =============================================================================
# EXPOSE FOUNDATIONAL SYMBOLS
# =============================================================================

__all__ = [
    # Mutability classifications
    "StateMutability",
    
    # Mutation authority types
    "MutationAuthorityType",
    
    # Mutation boundaries
    "MutationBoundary",
    
    # Mutation results
    "MutationResult",
    
    # Evidence and audit
    "MutationEvidence",
    "MutationAuditRecord",
    
    # Authorization and validation
    "MutationAuthorization",
    "MutationValidator",
    
    # Boundary enforcement
    "MutationBoundaryEnforcement",
    "MutationBoundaryValidator",
    
    # Immutable state protocol
    "CoreImmutableState",
    "ImmutableSnapshotView",
    "ImmutableViewProjection",
    
    # Mutable aggregate base classes
    "CoreMutableAggregate",
    "OwnerMutableAggregate",
    "AppendOnlyAggregate",
    
    # Reconstructible state
    "DerivedState",
    "CachedState",
    "TransientState",
    
    # Utility functions
    "validate_mutation_authorization",
    "create_mutation_audit_record",
]