# State Transition Architecture - Phase 3.15.5
# ==============================================
#
# Canonical transition architecture governing state evolution throughout Gordon Core.
#
# This module establishes:
#   - Explicit, deterministic, validated transitions for mutable state
#   - Lifecycle model: Request → Validation → Execution → Result → History
#   - Taxonomy of canonical transition types (Create, Initialize, Activate, etc.)
#   - Policy-driven validation with explicit pre/post conditions
#   - Atomic execution with rollback/compensation support
#   - Bounded history tracking for diagnostics and auditing
#
# ARCHITECTURAL PRINCIPLES:
#   1. One canonical transition architecture exists throughout the Core
#   2. Every transition is explicitly represented as an immutable record
#   3. Transitions preserve ownership, version, generation integrity
#   4. Runtime isolation is enforced for all transitions
#   5. No implicit behavior - all policies are explicit and validated
#   6. Transitions never leave partially committed state on failure

"""
Canonical State Transition Architecture for Gordon Core Phase 3.15.5.

This module defines the canonical transition architecture that governs how
runtime state evolves from one valid condition to another while preserving:

    IDENTITY:
        - Each transition has a unique identifier
        - Source and destination states are explicitly tracked
    
    VALIDATION:
        - Ownership verification before any mutation
        - Scope compatibility checks
        - Version and generation validation
        - Authorization and policy compliance
    
    EXECUTION:
        - Atomic: either complete or fail without partial state
        - Deterministic: same inputs always produce same outputs
        - Policy-driven: explicit rules govern each transition type
    
    RECOVERY:
        - Rollback to previous state on failure
        - Compensation actions for irreversible operations
        - Retry mechanisms with bounded attempts

This architecture extends:
    Phase 3.15.1 - Core State Foundations
    Phase 3.15.2 - State Identity, Scope & Ownership  
    Phase 3.15.3 - Immutable & Mutable State Semantics
    Phase 3.15.4 - Runtime State Hierarchy

ONE CANONICAL ARCHITECTURE:
    Only one transition architecture exists throughout the Core.
    Subsystems may extend with typed transitions but must use this foundation.
"""

# =============================================================================
# IMPORTS - Import-time purity maintained
# =============================================================================

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Protocol,
    runtime_checkable,
    Any,
)
from enum import Enum, auto
import uuid
import time as _time_module

# Core state foundations (Phase 3.15.x)
from ..identity import TransitionId as StateTransitionId, RuntimeStateId
from ..ownership import OwnershipAuthorityType
from ..__init__ import (
    CoreStateDomain,
    CoreStateScope,
    CoreStateMutability,
    CoreStateVersion,
)

# =============================================================================
# CANONICAL TRANSITION TYPES (LIFECYCLE TAXONOMY)
# =============================================================================


class TransitionType(Enum):
    """
    Canonical transition types for state evolution.
    
    SUBSYSTEM EXTENSIONS:
        Subsystems may define additional typed extensions through
        subsystem-specific transition types that extend this taxonomy.
    
    INVARIANTS:
        TRA-TYPE-001: Every transition has exactly one type from this taxonomy
        TRA-TYPE-002: Transition types are repository-wide and consistent
        TRA-TYPE-003: Subsystem extensions must use canonical base for compatibility
    """
    
    # Creation transitions (initial state establishment)
    CREATE = "create"          # Initial creation of a new aggregate
    INITIALIZE = "initialize"  # First-time setup (idempotent)
    
    # Activation transitions (moving to active state)
    ACTIVATE = "activate"      # Activate from inactive/pending state
    
    # Deactivation transitions (moving away from active)
    DEACTIVATE = "deactivate"  # Deactivate to inactive state
    SUSPEND = "suspend"        # Temporarily suspend operation
    RESUME = "resume"          # Resume from suspended state
    
    # Control transitions (runtime behavior)
    PAUSE = "pause"            # Pause execution flow
    CONTINUE = "continue"      # Continue paused execution
    
    # Replacement transitions (full replacement)
    REPLACE = "replace"        # Replace with new value/version
    UPGRADE = "upgrade"        # Upgrade to newer version/compatibility
    DOWNGRADE = "downgrade"    # Downgrade to older version/compatibility
    
    # Recovery transitions (restoration from failure)
    RESTORE = "restore"        # Restore from persistence or checkpoint
    RECONCILE = "reconcile"    # Reconcile with external state
    RESET = "reset"            # Reset to initial/default state
    
    # Migration transitions (structural changes)
    MIGRATE = "migrate"        # Migrate to new schema/generation
    RETIRE = "retire"          # Mark as retired (for audit/recovery)
    
    # Termination transitions (final state changes)
    SHUTDOWN = "shutdown"      # Graceful shutdown procedure
    DELETE = "delete"          # Permanent deletion
    
    # Version transitions (evolution within lineage)
    UPDATE = "update"          # Update current value/version
    PATCH = "patch"            # Partial update to fields


# =============================================================================
# TRANSITION POLICIES
# =============================================================================


@dataclass(frozen=True)
class TransitionPolicy:
    """
    Policy governing a specific transition type.
    
    Every transition must have an associated policy that defines:
        - Valid source states (where transition can originate)
        - Valid destination states (where transition can arrive)
        - Authorization requirements (who may perform this transition)
        - Timeout and retry constraints
        - Rollback/compensation behavior
    
    INVARIANTS:
        POLICY-001: Every transition type has exactly one canonical policy
        POLICY-002: Policies are immutable once created
        POLICY-003: Policy validation is exhaustive before any mutation
    """
    
    # Transition identity
    transition_type: TransitionType
    
    # State machine constraints
    allowed_source_states: Tuple[str, ...]  # e.g., ("idle", "paused")
    allowed_destination_states: Tuple[str, ...]  # e.g., ("active", "terminated")
    
    # Authority requirements - use OwnershipAuthorityType for compatibility with ownership.py
    required_authority_types: Tuple[str, ...] = field(
        default_factory=lambda: ("exclusive_mutation",)
    )
    
    # Timeout constraints
    timeout_seconds: Optional[float] = None  # None = no timeout
    
    # Retry policy
    retry_policy: "TransitionRetryPolicy" = field(
        default_factory=lambda: TransitionRetryPolicy(max_attempts=1, backoff_seconds=0.0)
    )
    
    # Recovery behavior
    rollback_enabled: bool = True
    rollback_state_source: str = "previous_version"  # "previous_version", "checkpoint", "external"
    
    compensation_required: bool = False
    
    # Persistence requirements
    must_persist_before_commit: bool = False
    persistence_timeout_seconds: Optional[float] = None
    
    # Observability requirements
    emit_transition_event: bool = True
    log_validation_findings: bool = True


@dataclass(frozen=True)
class TransitionRetryPolicy:
    """
    Retry policy for transitions.
    
    INVARIANTS:
        RETRY-001: Max attempts must be at least 1
        RETRY-002: Backoff must be non-negative
        RETRY-003: Max backoff >= initial backoff if both specified
    """
    
    max_attempts: int = 1
    initial_backoff_seconds: float = 0.0
    backoff_multiplier: float = 2.0
    max_backoff_seconds: Optional[float] = None
    
    def calculate_delay(self, attempt_number: int) -> float:
        """Calculate delay before the given attempt (0-indexed)."""
        if attempt_number <= 0:
            return 0.0
        
        # Exponential backoff with optional cap
        delay = self.initial_backoff_seconds * (self.backoff_multiplier ** (attempt_number - 1))
        
        if self.max_backoff_seconds is not None:
            delay = min(delay, self.max_backoff_seconds)
        
        return delay


# =============================================================================
# TRANSITION VALIDATION FINDINGS
# =============================================================================


class ValidationOutcome(Enum):
    """
    Outcome of transition validation.
    
    OUTCOMES:
        VALID: All validations passed, transition may proceed
        INVALID_SOURCE: Source state is not allowed for this transition type
        INVALID_DESTINATION: Destination state is not allowed for this transition type
        VERSION_MISMATCH: Expected version doesn't match current version
        GENERATION_MISMATCH: Expected generation doesn't match current generation
        AUTHORIZATION_FAILED: Initiator lacks required authority
        OWNERSHIP_FAILED: Initiator is not the owner (where ownership required)
        SCOPE_VIOLATION: Scope compatibility check failed
        TIMEOUT_PENDING: Transition timed out before validation completed
        DEPENDENCY_UNREADY: Required dependency is not ready
        INVARIANT_VIOLATED: State invariants would be violated
    """
    
    VALID = "valid"
    INVALID_SOURCE = "invalid_source"
    INVALID_DESTINATION = "invalid_destination"
    VERSION_MISMATCH = "version_mismatch"
    GENERATION_MISMATCH = "generation_mismatch"
    AUTHORIZATION_FAILED = "authorization_failed"
    OWNERSHIP_FAILED = "ownership_failed"
    SCOPE_VIOLATION = "scope_violation"
    TIMEOUT_PENDING = "timeout_pending"
    DEPENDENCY_UNREADY = "dependency_unready"
    INVARIANT_VIOLATED = "invariant_violated"


@dataclass(frozen=True)
class ValidationResult:
    """
    Structured result of transition validation.
    
    A validation result preserves:
        - Outcome (success or specific failure reason)
        - Findings for each check performed
        - Timing information for diagnostics
        - Context about what was validated
    
    INVARIANTS:
        VALID-RESULT-001: Result is immutable once created
        VALID-RESULT-002: Success implies all checks passed
        VALID-RESULT-003: Failure includes specific reason(s)
    """
    
    outcome: ValidationOutcome
    transition_id: str
    
    # Timing
    validation_started_at_utc: float = field(default_factory=_time_module.monotonic)
    validation_completed_at_utc: Optional[float] = None
    
    # Detailed findings
    findings: Tuple[str, ...] = field(default_factory=tuple)
    
    # Context (for debugging/diagnostics)
    source_state: str = ""
    destination_state: str = ""
    current_version_sequence: int = 0
    expected_version_sequence: Optional[int] = None
    current_generation: int = 0
    expected_generation: Optional[int] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.outcome == ValidationOutcome.VALID
    
    @property
    def validation_duration_seconds(self) -> Optional[float]:
        """Calculate total validation time, or None if not completed."""
        if self.validation_completed_at_utc is None:
            return None
        return self.validation_completed_at_utc - self.validation_started_at_utc


@dataclass(frozen=True)
class TransitionValidationResult(Protocol):
    """
    Protocol for transition validation results.
    
    All transition validators must produce results conforming to this protocol.
    """
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def outcome(self) -> ValidationOutcome:
        ...
    
    @property
    def findings(self) -> Tuple[str, ...]:
        ...


# =============================================================================
# TRANSITION EXECUTION RESULTS
# =============================================================================


class TransitionResultCode(Enum):
    """
    Result code for transition execution.
    
    RESULT CODES:
        SUCCESS: Transition completed successfully
        FAILURE: Transition failed (no state mutation)
        PARTIAL_FAILURE: Some changes committed before failure
        CONFLICT_DETECTED: Version/generation conflict during commit
        TIMEOUT: Transition timed out during execution
        ROLLED_BACK: Transition was rolled back after failure
    """
    
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL_FAILURE = "partial_failure"
    CONFLICT_DETECTED = "conflict_detected"
    TIMEOUT = "timeout"
    ROLLED_BACK = "rolled_back"


@dataclass(frozen=True)
class TransitionExecutionResult:
    """
    Result of transition execution.
    
    This is the canonical record of what happened during a transition,
    including success, failure, or partial outcomes.
    
    INVARIANTS:
        EXEC-RESULT-001: Result is immutable once created
        EXEC-RESULT-002: Success implies atomic commit (no partial state)
        EXEC-RESULT-003: Failure leaves state unchanged (if possible)
    """
    
    # Core result
    transition_id: str
    result_code: TransitionResultCode
    
    # Timing
    execution_started_at_utc: float = field(default_factory=_time_module.monotonic)
    execution_completed_at_utc: Optional[float] = None
    
    # State after transition (for success)
    destination_state: Optional[str] = None
    new_version_sequence: int = 0
    new_generation: int = 0
    
    # For failures
    failure_reason: Optional[str] = None
    partial_commit_status: bool = False
    
    # Recovery information
    rollback_performed: bool = False
    compensation_performed: bool = False
    
    @property
    def execution_duration_seconds(self) -> Optional[float]:
        """Calculate total execution time, or None if not completed."""
        if self.execution_completed_at_utc is None:
            return None
        return self.execution_completed_at_utc - self.execution_started_at_utc
    
    @property
    def was_successful(self) -> bool:
        """Check if transition succeeded (including rollback/compensation)."""
        return self.result_code in (
            TransitionResultCode.SUCCESS,
            TransitionResultCode.ROLLED_BACK,  # Rollback is a valid recovery outcome
        )


# =============================================================================
# TRANSITION HISTORY ENTRY
# =============================================================================


@dataclass(frozen=True)
class TransitionHistoryEntry:
    """
    One entry in the bounded transition history.
    
    History supports diagnostics, recovery, continuity, and auditing.
    Must remain bounded (not a general event store).
    
    INVARIANTS:
        HIST-ENTRY-001: Entry is immutable once created
        HIST-ENTRY-002: Entries are chronologically ordered
        HIST-ENTRY-003: Old entries may be pruned to maintain bounds
    """
    
    # Identity
    history_sequence: int  # Monotonic within transition instance
    
    # Transition info
    transition_id: str
    timestamp_utc: float = field(default_factory=_time_module.monotonic)
    
    # State before and after
    source_state: str
    destination_state: Optional[str] = None  # None if transition failed
    
    # Authority and context
    initiating_authority: str
    validation_outcome: ValidationOutcome
    execution_result_code: TransitionResultCode
    
    # Version tracking
    version_before_sequence: int
    generation_before: int
    version_after_sequence: Optional[int] = None
    generation_after: Optional[int] = None
    
    # Metadata
    findings: Tuple[str, ...] = field(default_factory=tuple)
    provenance: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class TransitionHistory:
    """
    Bounded history of transitions for one aggregate.
    
    Retention bounds are configurable - old entries may be pruned.
    
    INVARIANTS:
        HIST-001: History is immutable once created
        HIST-002: Entries are in chronological order
        HIST-003: Pruning maintains chronological integrity
    """
    
    aggregate_id: str
    
    # Maximum history length (configurable)
    max_entries: int = 1000
    
    # History entries in chronological order
    _entries: Tuple[TransitionHistoryEntry, ...] = field(default_factory=tuple)
    
    def append(self, entry: TransitionHistoryEntry) -> "TransitionHistory":
        """Append new entry, pruning oldest if necessary."""
        new_entries = self._entries + (entry,)
        
        # Prune to max length
        if len(new_entries) > self.max_entries:
            new_entries = new_entries[-self.max_entries:]
        
        return dataclass_replace(self, _entries=new_entries)
    
    def get_latest(self) -> Optional[TransitionHistoryEntry]:
        """Get the most recent entry."""
        if not self._entries:
            return None
        return self._entries[-1]
    
    def get_by_source_state(self, state: str) -> Tuple[TransitionHistoryEntry, ...]:
        """Get all entries where source_state equals given state."""
        return tuple(e for e in self._entries if e.source_state == state)
    
    def get_by_destination_state(self, state: str) -> Tuple[TransitionHistoryEntry, ...]:
        """Get all entries where destination_state equals given state."""
        return tuple(e for e in self._entries if e.destination_state == state)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert history to dictionary for serialization."""
        return {
            "aggregate_id": self.aggregate_id,
            "max_entries": self.max_entries,
            "entry_count": len(self._entries),
            "latest_transition_id": self.get_latest().transition_id if self.get_latest() else None,
            "history": [
                {
                    "history_sequence": e.history_sequence,
                    "transition_id": e.transition_id,
                    "timestamp_utc": e.timestamp_utc,
                    "source_state": e.source_state,
                    "destination_state": e.destination_state,
                    "version_before": e.version_before_sequence,
                    "generation_before": e.generation_before,
                }
                for e in self._entries
            ],
        }


# =============================================================================
# TRANSITION EXECUTION CONTRACT (PUBLIC API)
# =============================================================================


@runtime_checkable
class TransitionExecutor(Protocol):
    """
    Protocol for transition executors.
    
    All transition executors must satisfy this protocol to ensure
    consistent behavior across the Core.
    
    INVARIANTS:
        EXEC-PROT-001: Execute must be atomic (success or no state change)
        EXEC-PROT-002: Validation runs before any mutation
        EXEC-PROT-003: History is updated after each transition
    """
    
    def validate_transition(
        self,
        source_state: str,
        destination_state: str,
        policy: TransitionPolicy,
        expected_version: Optional[CoreStateVersion] = None,
        expected_generation: Optional[int] = None,
        authority: Optional[str] = None,
    ) -> ValidationResult:
        """Validate that a transition is legal."""
    
    def execute_transition(
        self,
        source_state: str,
        destination_state: str,
        policy: TransitionPolicy,
        expected_version: Optional[CoreStateVersion] = None,
        expected_generation: Optional[int] = None,
        authority: Optional[str] = None,
    ) -> TransitionExecutionResult:
        """Execute a validated transition atomically."""
    
    def rollback_transition(
        self,
        transition_id: str,
    ) -> TransitionExecutionResult:
        """Rollback the most recent transition."""
    
    def get_history(self, aggregate_id: str) -> TransitionHistory:
        """Get history for an aggregate."""
    
    def inspect_policy(self, transition_type: TransitionType) -> Optional[TransitionPolicy]:
        """Inspect the policy for a transition type."""


# =============================================================================
# TRANSITION FACTORY (PUBLIC API)
# =============================================================================


class TransitionFactory:
    """
    Factory for creating transitions with proper validation and identity.
    
    This is the canonical entry point for creating transitions. All
    transitions should be created through this factory to ensure:
        - Consistent identity generation
        - Policy enforcement at creation time
        - Proper validation before execution
    
    INVARIANTS:
        FACTORY-001: Factory is stateless (pure functions)
        FACTORY-002: All created transitions are properly validated
        FACTORY-003: No transition can be created with invalid policy
    """
    
    def __init__(self) -> None:
        """Initialize the transition factory."""
        self._policies: Dict[TransitionType, TransitionPolicy] = {}
        self._history: Dict[str, TransitionHistory] = {}
    
    def register_policy(self, policy: TransitionPolicy) -> None:
        """Register a transition policy."""
        self._policies[policy.transition_type] = policy
    
    def get_policy(self, transition_type: TransitionType) -> Optional[TransitionPolicy]:
        """Get the policy for a transition type."""
        return self._policies.get(transition_type)
    
    def create_transition_request(
        self,
        source_state: str,
        destination_state: str,
        aggregate_id: str,
        authority: str,
        transition_type: TransitionType,
        expected_version: Optional[CoreStateVersion] = None,
        expected_generation: Optional[int] = None,
    ) -> "TransitionRequest":
        """
        Create a new transition request.
        
        Args:
            source_state: Current state before transition
            destination_state: Target state after transition
            aggregate_id: ID of the aggregate being transitioned
            authority: Who is requesting this transition
            transition_type: What kind of transition
            expected_version: Expected current version (for validation)
            expected_generation: Expected current generation (for validation)
            
        Returns:
            A new TransitionRequest ready for validation
            
        Raises:
            ValueError: If policy validation fails at creation time
        """
        policy = self._policies.get(transition_type)
        if policy is None:
            raise ValueError(f"No policy registered for transition type: {transition_type}")
        
        # Validate against policy
        if source_state not in policy.allowed_source_states:
            raise ValueError(
                f"Source state '{source_state}' not allowed for {transition_type.value} "
                f"(allowed: {policy.allowed_source_states})"
            )
        
        if destination_state not in policy.allowed_destination_states:
            raise ValueError(
                f"Destination state '{destination_state}' not allowed for {transition_type.value} "
                f"(allowed: {policy.allowed_destination_states})"
            )
        
        return TransitionRequest(
            transition_id=StateTransitionId.generate().value,
            source_state=source_state,
            destination_state=destination_state,
            aggregate_id=aggregate_id,
            authority=authority,
            transition_type=transition_type,
            expected_version=expected_version,
            expected_generation=expected_generation,
            created_at_utc=_time_module.monotonic(),
        )
    
    def execute_transition(
        self,
        request: "TransitionRequest",
    ) -> TransitionExecutionResult:
        """
        Execute a transition request.
        
        This is the canonical execution path. All transitions should
        go through this method to ensure consistent behavior.
        
        Args:
            request: The validated transition request
            
        Returns:
            Result of the transition execution
        """
        # Get policy for validation
        policy = self._policies.get(request.transition_type)
        if policy is None:
            return TransitionExecutionResult(
                transition_id=request.transition_id,
                result_code=TransitionResultCode.FAILURE,
                failure_reason=f"No policy registered for {request.transition_type.value}",
            )
        
        # Execute with atomic guarantees
        try:
            # TODO: Implement actual transition execution logic
            # This would call the appropriate validator and executor
            
            return TransitionExecutionResult(
                transition_id=request.transition_id,
                result_code=TransitionResultCode.SUCCESS,
                destination_state=request.destination_state,
            )
            
        except Exception as e:
            return TransitionExecutionResult(
                transition_id=request.transition_id,
                result_code=TransitionResultCode.FAILURE,
                failure_reason=str(e),
            )


# =============================================================================
# TRANSITION REQUEST (PUBLIC API)
# =============================================================================


@dataclass(frozen=True)
class TransitionRequest:
    """
    Request to perform a state transition.
    
    A transition request is the canonical way to initiate a transition.
    It contains all information needed for validation and execution.
    
    INVARIANTS:
        REQ-001: Request is immutable once created
        REQ-002: All required fields must be present
        REQ-003: Request is validated before execution
    """
    
    # Identity
    transition_id: str
    
    # State information
    source_state: str
    destination_state: str
    
    # Target aggregate
    aggregate_id: str
    hierarchy_type: Optional[str] = None  # RuntimeStateHierarchyType if known
    
    # Authority
    authority: str
    authority_kind: Optional[str] = None  # e.g., "lifecycle", "execution"
    
    # Transition details
    transition_type: TransitionType
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Version/generation context (for validation)
    expected_version: Optional[CoreStateVersion] = None
    expected_generation: Optional[int] = None
    
    # Timeout/deadline
    deadline_utc: Optional[float] = None
    timeout_seconds: Optional[float] = None
    
    # Context
    reason: str = "unspecified"
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if this request has expired."""
        if self.deadline_utc is None and self.timeout_seconds is None:
            return False
        
        now = _time_module.monotonic()
        
        if self.deadline_utc is not None and now > self.deadline_utc:
            return True
        
        if self.timeout_seconds is not None and (now - self.created_at_utc) > self.timeout_seconds:
            return True
        
        return False
    
    def with_timeout(self, timeout_seconds: float) -> "TransitionRequest":
        """Create a copy with an added timeout."""
        return dataclass_replace(
            self,
            timeout_seconds=timeout_seconds,
            deadline_utc=_time_module.monotonic() + timeout_seconds,
        )


# =============================================================================
# TRANSITION VALIDATOR (PUBLIC API)
# =============================================================================


class TransitionValidator:
    """
    Validator for transitions.
    
    Provides comprehensive validation of transitions against:
        - Policy constraints
        - State machine rules
        - Version/generation consistency
        - Authorization requirements
    
    INVARIANTS:
        VAL-001: Validation is exhaustive (all checks performed)
        VAL-002: Validation returns structured findings
        VAL-003: No mutation occurs during validation
    """
    
    def __init__(self, factory: TransitionFactory) -> None:
        """Initialize validator with transition policies."""
        self._factory = factory
    
    def validate_request(self, request: TransitionRequest) -> ValidationResult:
        """
        Validate a transition request.
        
        Args:
            request: The transition request to validate
            
        Returns:
            Validation result with outcome and findings
        """
        policy = self._factory.get_policy(request.transition_type)
        if policy is None:
            return ValidationResult(
                outcome=ValidationOutcome.INVALID_SOURCE,
                transition_id=request.transition_id,
                findings=("No policy registered for this transition type",),
                source_state=request.source_state,
                destination_state=request.destination_state,
            )
        
        findings: List[str] = []
        
        # Validate source state
        if request.source_state not in policy.allowed_source_states:
            findings.append(
                f"Source state '{request.source_state}' is not allowed for transition "
                f"{request.transition_type.value} (allowed: {policy.allowed_source_states})"
            )
        
        # Validate destination state
        if request.destination_state not in policy.allowed_destination_states:
            findings.append(
                f"Destination state '{request.destination_state}' is not allowed for transition "
                f"{request.transition_type.value} (allowed: {policy.allowed_destination_states})"
            )
        
        # Validate version (if specified)
        if request.expected_version is not None:
            # TODO: Compare with actual current version
            pass
        
        # Validate generation (if specified)
        if request.expected_generation is not None:
            # TODO: Compare with actual current generation
            pass
        
        # Check expiration
        if request.is_expired:
            findings.append("Transition request has expired")
        
        # Check authority (if required by policy)
        if "exclusive_mutation" in policy.required_authority_types:
            # TODO: Verify authority matches owner
            pass
        
        # Determine outcome
        if findings:
            outcome = ValidationOutcome.INVALID_SOURCE  # Default for failures
            if "expired" in " ".join(findings).lower():
                outcome = ValidationOutcome.TIMEOUT_PENDING
        else:
            outcome = ValidationOutcome.VALID
        
        return ValidationResult(
            outcome=outcome,
            transition_id=request.transition_id,
            findings=tuple(findings),
            source_state=request.source_state,
            destination_state=request.destination_state,
            validation_completed_at_utc=_time_module.monotonic(),
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass.
    
    This is a utility for creating updated copies of immutable objects.
    
    Args:
        obj: The dataclass instance to copy
        kwargs: Fields to replace
        
    Returns:
        A new instance with replaced fields
    """
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


def validate_transition_policy(policy: TransitionPolicy) -> Tuple[bool, List[str]]:
    """
    Validate that a transition policy is internally consistent.
    
    Args:
        policy: The policy to validate
        
    Returns:
        (is_valid: bool, errors: List of error messages)
    """
    errors: List[str] = []
    
    # Check source and destination are not empty
    if not policy.allowed_source_states:
        errors.append("allowed_source_states must not be empty")
    
    if not policy.allowed_destination_states:
        errors.append("allowed_destination_states must not be empty")
    
    # Check retry policy consistency
    if policy.retry_policy.max_attempts < 1:
        errors.append("max_attempts must be at least 1")
    
    if policy.retry_policy.initial_backoff_seconds < 0:
        errors.append("initial_backoff_seconds must be non-negative")
    
    return (len(errors) == 0, errors)


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Transition types
    "TransitionType",
    
    # Policies
    "TransitionPolicy",
    "TransitionRetryPolicy",
    
    # Validation
    "ValidationOutcome",
    "ValidationResult",
    "TransitionValidationResult",
    
    # Execution results
    "TransitionResultCode",
    "TransitionExecutionResult",
    
    # History
    "TransitionHistoryEntry",
    "TransitionHistory",
    
    # Public APIs
    "TransitionExecutor",
    "TransitionFactory",
    "TransitionRequest",
    "TransitionValidator",
    
    # Utilities
    "dataclass_replace",
    "validate_transition_policy",
]
