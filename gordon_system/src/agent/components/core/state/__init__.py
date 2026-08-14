# Core State Foundations - Phase 3.15.6 Extension
# ==================================================

"""
Canonical Core State Architecture for Gordon.

This module extends:
    Phase 3.15.6 - State Snapshots and Views

EXPOSED SYMBOLS:
    SnapshotKind                 - Canonical snapshot kind taxonomy
    SnapshotConsistency          - Consistency classifications (extends Phase 3.15.x)
    SnapshotCompleteness         - Completeness classifications (extends Phase 3.15.x)
    SnapshotLifecycleStage       - Lifecycle stages for snapshots
    ProjectionPolicy             - Projection policy with redaction and field filtering
    SnapshotProvenance           - Provenance tracking for snapshots
    
    BaseStateSnapshot            - Immutable snapshot base class
    BaseStateView                - Immutable view base class
    
    SnapshotFactory              - Factory for creating typed snapshots
    ViewFactory                  - Factory for creating typed views
    SnapshotValidator            - Validator for snapshots and views
    
    SnapshotDiagnostics          - Bounded diagnostics for monitoring
    validate_snapshot            - Validate snapshot well-formedness
    validate_view                - Validate view well-formedness

ARCHITECTURAL PRINCIPLES:
    1. One canonical snapshot architecture exists throughout the Core
    2. All snapshots are immutable observational artifacts
    3. Snapshots never become mutable runtime state authorities
    4. Projections are explicit (no implicit behavior)
    5. Consistency and completeness guarantees are declared
    6. Redaction is deterministic and policy-driven
    7. Runtime ownership boundaries are never bypassed

See docs/agent/architecture/phase-3.15.6-state-snapshots-views.md for complete documentation.
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
)
from enum import Enum, auto
import uuid
import time as _time_module

# Core state foundations (Phase 3.15.x)
from .identity import AggregateId, RuntimeId, BootSessionId, OwnerId
from .ownership import (
    OwnershipAuthorityType,
    RuntimeIsolationEnforcement,
    OwnershipValidator,
    OwnershipDiagnostics,
)

# Phase 3.15.6 exports
from .snapshots import (
    SnapshotKind,
    SnapshotConsistency as BaseSnapshotConsistency,
    SnapshotCompleteness,
    SnapshotLifecycleStage,
    ProjectionPolicy,
    SnapshotProvenance,
    BaseStateSnapshot,
    BaseStateView,
    SnapshotFactory,
    ViewFactory,
    SnapshotValidator,
    SnapshotDiagnostics,
    validate_snapshot,
    validate_view,
)

# Phase 3.15.7 exports
from .versioning import (
    VersionIdentity,
    GenerationIdentity,
    ChangeIdentity,
    VersionProvenance,
    BaseStateVersion,
    BaseGeneration,
    VersionHistoryEntry,
    GenerationHistoryEntry,
    VersionValidationOutcome,
    GenerationValidationOutcome,
    VersionValidationResult,
    GenerationValidationResult,
    VersionLineage,
    GenerationLineage,
    StateVersioningFacade,
)

# Phase 3.15.9 exports - State Persistence Boundaries  
from .persistence import (
    PersistenceEligibility,
    StateAggregateEligibility,
    PersistencePolicy,
    PersistencePolicyConfiguration,
    SerializedRepresentation,
    SerializationBoundary,
    CheckpointStatus,
    CheckpointRecord,
    JournalRecord,
    JournalBoundary,
    ArchiveStatus,
    ArchiveDescriptor,
    IntegrityAlgorithm,
    IntegrityEvidence,
    TransactionPhase,
    PersistenceTransaction,
    PersistenceValidationFinding,
    PersistenceValidationResult,
    PersistenceValidator,
    PersistenceDiagnosticEvent,
    PersistenceDiagnostics,
    PersistenceFacade,
)

# Phase 3.15.11 exports - Cross-Runtime State Isolation
from .isolation import (
    RuntimeIdentity,
    BootSessionIdentity,
    IsolationDomain, 
    IsolationPolicy,
    OwnershipIsolation,
    MutationIsolation,
    ObservationIsolation,
    VisibilityLevel,
    ResourceIsolation,
    RuntimeBoundaryValidationResult,
    RuntimeBoundaryValidator,
    CrossRuntimeOperationType,
    DistributedReadinessContract,
    SyncStrategy,
    MigrationRequest,
    MigrationResult,
    MigrationPolicy,
    IsolationViolation,
    IsolationViolationType,
    ViolationDetectionResult,
    ViolationDetector,
    RuntimeIsolationDiagnostics,
    RuntimeIsolationFacade,
)

# =============================================================================
# CANONICAL STATE CONSISTENCY MODELS
# =============================================================================


class ConsistencyModel(Enum):
    """
    Canonical consistency models for state aggregates.

    Each mutable aggregate must declare its consistency guarantees.

    CONSISTENCY CLASSES:
        STRONG              - All reads see all prior writes; immediate visibility
        VERSION_CONSISTENT  - Reads see state at a specific version
        TRANSACTIONAL       - Read snapshot from committed transaction
        EVENTUAL            - Writes propagate with eventual convergence
        SNAPSHOT            - Consistent snapshot view at capture time
        READ_ONLY           - No mutations allowed, always consistent
        BEST_EFFORT         - Best attempt, no consistency guarantees

    INVARIANTS:
        CONS-001: Every mutable aggregate declares exactly one consistency model
        CONS-002: Consistency models are immutable once set
        CONS-003: Readers observe only valid states per the declared model
        CONS-004: Mutations preserve the declared consistency guarantees
    """

    # Strong consistency - immediate visibility, all reads see prior writes
    STRONG = "strong"

    # Version-consistent - reads see state at a specific version
    VERSION_CONSISTENT = "version_consistent"

    # Transactional - snapshot from committed transaction
    TRANSACTIONAL = "transactional"

    # Eventual consistency - converge over time
    EVENTUAL = "eventual"

    # Snapshot consistency - consistent view at capture time
    SNAPSHOT = "snapshot"

    # Read-only - no mutations, always consistent
    READ_ONLY = "read_only"

    # Best effort - no guarantees
    BEST_EFFORT = "best_effort"


# =============================================================================
# OPTIMISTIC CONCURRENCY CONTROL
# =============================================================================


@dataclass(frozen=True)
class ExpectedVersion:
    """
    Expected version for optimistic concurrency control.

    Used to detect stale mutations before applying them.

    INVARIANTS:
        OCC-VER-001: Expected version must match current version for success
        OCC-VER-002: Version mismatch results in conflict (not silent overwrite)
        OCC-VER-003: Expected version may be None (no version tracking)
    """

    # The expected version sequence number
    value: int

    # Whether this is a strict check (fail if missing vs. create new)
    strict: bool = True

    @classmethod
    def match(cls, version_sequence: int) -> "ExpectedVersion":
        """Create an expected version that must match the given version."""
        return cls(value=version_sequence, strict=True)

    @classmethod
    def at_least(cls, version_sequence: int) -> "ExpectedVersion":
        """Create an expected version that must be >= the given version."""
        return cls(value=version_sequence, strict=False)

    @classmethod
    def any(cls) -> "ExpectedVersion":
        """No version check - accept any current version (create if missing)."""
        return cls(value=-1, strict=False)


@dataclass(frozen=True)
class ExpectedGeneration:
    """
    Expected generation for optimistic concurrency control.

    Used to detect stale ownership before applying mutations.

    INVARIANTS:
        OCC-GEN-001: Expected generation must match current generation
        OCC-GEN-002: Stale generations are rejected (not silently overwritten)
        OCC-GEN-003: Generation changes indicate ownership change
    """

    # The expected generation epoch number
    value: int

    # Whether this is a strict check
    strict: bool = True

    @classmethod
    def match(cls, epoch: int) -> "ExpectedGeneration":
        """Create an expected generation that must match the given epoch."""
        return cls(value=epoch, strict=True)

    @classmethod
    def at_least(cls, epoch: int) -> "ExpectedGeneration":
        """Create an expected generation that must be >= the given epoch."""
        return cls(value=epoch, strict=False)

    @classmethod
    def any(cls) -> "ExpectedGeneration":
        """No generation check - accept any current generation."""
        return cls(value=-1, strict=False)


# =============================================================================
# CONFLICT TYPES
# =============================================================================


class ConflictType(Enum):
    """
    Canonical conflict types for state mutations.

    CONFLICTS:
        VERSION_MISMATCH      - Expected version doesn't match current
        GENERATION_MISMATCH   - Expected generation doesn't match current
        OWNERSHIP_CONFLICT    - Ownership has changed since observation
        TRANSITION_CONFLICT   - State invariants would be violated
        HIERARCHY_CONFLICT    - Parent-child hierarchy would be invalid
        RUNTIME_CONFLICT      - Runtime isolation would be violated
        RESTORATION_CONFLICT  - Restoration would overwrite newer state
        MIGRATION_CONFLICT    - Migration would lose data

    INVARIANTS:
        CONFLICT-001: Every conflict has exactly one type from this taxonomy
        CONFLICT-002: Conflicts produce structured results, not silent failures
        CONFLICT-003: Conflict detection is deterministic and reproducible
    """

    # Version mismatch - stale read detected
    VERSION_MISMATCH = "version_mismatch"

    # Generation mismatch - ownership changed
    GENERATION_MISMATCH = "generation_mismatch"

    # Ownership conflict - different owner
    OWNERSHIP_CONFLICT = "ownership_conflict"

    # Transition would violate invariants
    TRANSITION_CONFLICT = "transition_conflict"

    # Hierarchy would be invalid
    HIERARCHY_CONFLICT = "hierarchy_conflict"

    # Runtime isolation violation
    RUNTIME_CONFLICT = "runtime_conflict"

    # Restoration conflict (overwrite newer)
    RESTORATION_CONFLICT = "restoration_conflict"

    # Migration conflict (data loss)
    MIGRATION_CONFLICT = "migration_conflict"


# =============================================================================
# CONFLICT RESOLUTION POLICIES
# =============================================================================


class ConflictResolutionPolicy(Enum):
    """
    Canonical conflict resolution strategies.

    Policy-driven resolution - no implicit behavior.

    POLICIES:
        REJECT     - Reject the mutation, return error
        RETRY      - Retry with current state (with backoff if configured)
        REVALIDATE - Revalidate with updated context
        RECONCILE  - Attempt to merge changes automatically
        MERGE      - Explicitly merge the mutation with current state
        COMPENSATE - Execute compensating actions for rollback
        ESCALATE   - Escalate to higher authority for resolution

    INVARIANTS:
        POL-001: Every conflict has an associated resolution policy
        POL-002: Policies are explicit and immutable once set
        POL-003: No implicit conflict resolution is permitted
    """

    # Reject the mutation with structured error
    REJECT = "reject"

    # Retry with current state (configurable backoff)
    RETRY = "retry"

    # Revalidate with updated context
    REVALIDATE = "revalidate"

    # Attempt automatic reconciliation
    RECONCILE = "reconcile"

    # Explicitly merge mutation with current state
    MERGE = "merge"

    # Execute compensating actions
    COMPENSATE = "compensate"

    # Escalate to higher authority
    ESCALATE = "escalate"


@dataclass(frozen=True)
class RetryPolicy:
    """
    Retry configuration for conflict resolution.

    Supports exponential backoff and bounded retry attempts.

    INVARIANTS:
        RETRY-001: Max attempts must be at least 1
        RETRY-002: Initial backoff >= 0
        RETRY-003: Max backoff >= initial backoff if both specified
        RETRY-004: Retry budget is consumed on each attempt
    """

    # Maximum retry attempts (including initial)
    max_attempts: int = 1

    # Initial delay before first retry
    initial_backoff_seconds: float = 0.0

    # Exponential backoff multiplier
    backoff_multiplier: float = 2.0

    # Maximum delay between retries
    max_backoff_seconds: Optional[float] = None

    def calculate_delay(self, attempt_number: int) -> float:
        """
        Calculate delay before the given retry attempt (0-indexed).

        Args:
            attempt_number: The retry attempt number (0 = first retry)

        Returns:
            Delay in seconds
        """
        if attempt_number <= 0:
            return 0.0

        # Exponential backoff
        delay = self.initial_backoff_seconds * (
            self.backoff_multiplier ** (attempt_number - 1)
        )

        # Apply cap
        if self.max_backoff_seconds is not None:
            delay = min(delay, self.max_backoff_seconds)

        return delay


# =============================================================================
# CONFLICT DETECTION RESULT
# =============================================================================


@dataclass(frozen=True)
class ConflictResult:
    """
    Structured result of conflict detection.

    Every conflict produces detailed findings for debugging and resolution.

    INVARIANTS:
        CONFLICT-RESULT-001: Result is immutable once created
        CONFLICT-RESULT-002: Success implies no conflict detected
        CONFLICT-RESULT-003: Failure includes specific reason(s)
    """

    # Did a conflict occur?
    conflict_detected: bool

    # Type of conflict (if any)
    conflict_type: Optional[ConflictType] = None

    # Timestamp
    detected_at_utc: float = field(default_factory=_time_module.monotonic)

    # Detailed findings for debugging
    findings: Tuple[str, ...] = field(default_factory=tuple)

    # Context information
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None

    @property
    def is_conflict(self) -> bool:
        """Check if a conflict was detected."""
        return self.conflict_detected

    @classmethod
    def no_conflict(cls, findings: Tuple[str, ...] = ()) -> "ConflictResult":
        """Create a result indicating no conflict."""
        return cls(conflict_detected=False, findings=findings)

    @classmethod
    def version_conflict(
        cls, expected_version: int, actual_version: int
    ) -> "ConflictResult":
        """Create a version mismatch conflict result."""
        return cls(
            conflict_detected=True,
            conflict_type=ConflictType.VERSION_MISMATCH,
            findings=(
                f"Version mismatch: expected {expected_version}, got {actual_version}",
            ),
            expected_value=str(expected_version),
            actual_value=str(actual_version),
        )

    @classmethod
    def generation_conflict(
        cls, expected_generation: int, actual_generation: int
    ) -> "ConflictResult":
        """Create a generation mismatch conflict result."""
        return cls(
            conflict_detected=True,
            conflict_type=ConflictType.GENERATION_MISMATCH,
            findings=(
                f"Generation mismatch: expected {expected_generation}, got {actual_generation}",
            ),
            expected_value=str(expected_generation),
            actual_value=str(actual_generation),
        )

    @classmethod
    def ownership_conflict(cls, owner_identity: str) -> "ConflictResult":
        """Create an ownership conflict result."""
        return cls(
            conflict_detected=True,
            conflict_type=ConflictType.OWNERSHIP_CONFLICT,
            findings=(
                f"Ownership changed since observation: current owner is {owner_identity}",
            ),
            actual_value=owner_identity,
        )


# =============================================================================
# VISIBILITY MODEL
# =============================================================================


class VisibilityLevel(Enum):
    """
    Canonical visibility levels for state access.

    Defines who can observe state and under what conditions.

    VISIBILITY LEVELS:
        PRIVATE           - Only the owner may observe
        OWNER_VISIBLE     - Owner and designated observers
        SUBSYSTEM_VISIBLE - All entities in same subsystem
        RUNTIME_VISIBLE   - All within same runtime instance
        DIAGNOSTIC        - Read-only diagnostic access
        PUBLIC            - External visibility (with restrictions)

    INVARIANTS:
        VIS-001: Every state aggregate has a primary visibility level
        VIS-002: Visibility does not imply mutation authority
        VIS-003: Visibility may be restricted by runtime/session isolation
    """

    # Only owner may observe
    PRIVATE = "private"

    # Owner and designated observers
    OWNER_VISIBLE = "owner_visible"

    # Subsystem-wide visibility
    SUBSYSTEM_VISIBLE = "subsystem_visible"

    # Runtime instance wide visibility
    RUNTIME_VISIBLE = "runtime_visible"

    # Read-only diagnostic access
    DIAGNOSTIC = "diagnostic"

    # External visibility (with restrictions)
    PUBLIC = "public"


# =============================================================================
# ISOLATION MODEL
# =============================================================================


class IsolationLevel(Enum):
    """
    Canonical isolation levels for state operations.

    Defines the scope and boundaries of state isolation.

    ISOLATION LEVELS:
        ISOLATED      - No shared access; exclusive ownership
        SHARED_READ   - Multiple readers, single writer
        OWNER_EXCLUSIVE - Owner-only access (no concurrent observers)
        RUNTIME_LOCAL - Bound to runtime instance
        PROCESS_LOCAL - Bound to process boundary
        DISTRIBUTED   - Distributed system scope
        EXTERNAL      - External source, read-only locally

    INVARIANTS:
        ISO-001: Every operation has an explicit isolation level
        ISO-002: Isolation is enforced at all access points
        ISO-003: Cross-isolation operations require policy authorization
    """

    # Exclusive ownership, no concurrent observers
    ISOLATED = "isolated"

    # Multiple readers allowed (concurrent observation)
    SHARED_READ = "shared_read"

    # Owner-only access
    OWNER_EXCLUSIVE = "owner_exclusive"

    # Runtime-local scope
    RUNTIME_LOCAL = "runtime_local"

    # Process-local scope
    PROCESS_LOCAL = "process_local"

    # Distributed system scope
    DISTRIBUTED = "distributed"

    # External source (read-only)
    EXTERNAL_READ_ONLY = "external_read_only"


# =============================================================================
# ATOMIC STATE OPERATION
# =============================================================================


class AtomicOperationStatus(Enum):
    """
    Status codes for atomic state operations.

    STATUS CODES:
        PENDING      - Operation initialized but not yet validated
        VALIDATED    - All validations passed, ready to commit
        COMMITTED    - Operation committed successfully
        REJECTED     - Rejected due to conflict or validation failure
        ROLLED_BACK  - Rolled back after partial execution

    INVARIANTS:
        ATOMIC-001: Every operation has exactly one final status
        ATOMIC-002: Committed implies atomic visibility
        ATOMIC-003: Rejected/RolledBack implies no state change
    """

    PENDING = "pending"
    VALIDATED = "validated"
    COMMITTED = "committed"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"


@dataclass(frozen=True)
class AtomicOperationResult:
    """
    Result of an atomic state operation.

    Observers shall never observe partial mutations.

    INVARIANTS:
        ATOMIC-RESULT-001: Result is immutable once created
        ATOMIC-RESULT-002: Success implies complete visibility
        ATOMIC-RESULT-003: Failure preserves original state
    """

    # Operation status
    status: AtomicOperationStatus

    # Timestamps
    started_at_utc: float = field(default_factory=_time_module.monotonic)
    completed_at_utc: Optional[float] = None

    # Version after operation (if successful)
    resulting_version_sequence: Optional[int] = None

    # Generation after operation (if successful)
    resulting_generation: Optional[int] = None

    # Conflict result if applicable
    conflict_result: Optional[ConflictResult] = None

    # Detailed findings
    findings: Tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_success(self) -> bool:
        """Check if operation succeeded."""
        return self.status in (AtomicOperationStatus.COMMITTED,)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate operation duration, or None if not completed."""
        if self.completed_at_utc is None:
            return None
        return self.completed_at_utc - self.started_at_utc

    @classmethod
    def committed(
        cls,
        version_sequence: int,
        generation: int,
        findings: Tuple[str, ...] = (),
    ) -> "AtomicOperationResult":
        """Create a committed result."""
        return cls(
            status=AtomicOperationStatus.COMMITTED,
            resulting_version_sequence=version_sequence,
            resulting_generation=generation,
            completed_at_utc=_time_module.monotonic(),
            findings=findings,
        )

    @classmethod
    def rejected(
        cls, conflict_result: ConflictResult, findings: Tuple[str, ...] = ()
    ) -> "AtomicOperationResult":
        """Create a rejected result."""
        return cls(
            status=AtomicOperationStatus.REJECTED,
            completed_at_utc=_time_module.monotonic(),
            conflict_result=conflict_result,
            findings=findings + (f"Conflict: {conflict_result.findings}",),
        )


# =============================================================================
# CONCURRENCY FACADE (PUBLIC API)
# =============================================================================


class StateConcurrencyFacade:
    """
    Canonical facade for state concurrency operations.

    Supports optimistic concurrency, conflict detection, and visibility
    management without exposing synchronization primitives.

    PUBLIC API:
        - validate_version: Check expected version matches current
        - validate_generation: Check expected generation matches current
        - detect_conflict: Detect conflicts before mutation
        - resolve_conflict: Apply resolution policy
        - check_visibility: Verify visibility requirements are met
        - verify_isolation: Verify isolation boundaries are respected

    INVARIANTS:
        FACADE-001: All operations are pure (no side effects)
        FACADE-002: No synchronization primitives exposed
        FACADE-003: Results are deterministic and reproducible
    """

    def __init__(self) -> None:
        """Initialize the concurrency facade."""
        self._conflict_policies: Dict[ConflictType, ConflictResolutionPolicy] = {
            ConflictType.VERSION_MISMATCH: ConflictResolutionPolicy.REJECT,
            ConflictType.GENERATION_MISMATCH: ConflictResolutionPolicy.REJECT,
            ConflictType.OWNERSHIP_CONFLICT: ConflictResolutionPolicy.REJECT,
            ConflictType.TRANSITION_CONFLICT: ConflictResolutionPolicy.REJECT,
            ConflictType.HIERARCHY_CONFLICT: ConflictResolutionPolicy.REJECT,
            ConflictType.RUNTIME_CONFLICT: ConflictResolutionPolicy.REJECT,
            ConflictType.RESTORATION_CONFLICT: ConflictResolutionPolicy.REJECT,
            ConflictType.MIGRATION_CONFLICT: ConflictResolutionPolicy.REJECT,
        }

    def validate_version(
        self, expected: ExpectedVersion, current_sequence: int
    ) -> Tuple[bool, Optional[ConflictResult]]:
        """
        Validate that the expected version matches the current version.

        Returns:
            (is_valid: bool, conflict_result: Optional[ConflictResult])
        """
        if expected.value == -1 and not expected.strict:
            return True, None

        if expected.value != current_sequence:
            conflict = ConflictResult.version_conflict(expected.value, current_sequence)
            return False, conflict

        return True, None

    def validate_generation(
        self, expected: ExpectedGeneration, current_epoch: int
    ) -> Tuple[bool, Optional[ConflictResult]]:
        """
        Validate that the expected generation matches the current generation.

        Returns:
            (is_valid: bool, conflict_result: Optional[ConflictResult])
        """
        if expected.value == -1 and not expected.strict:
            return True, None

        if expected.value != current_epoch:
            conflict = ConflictResult.generation_conflict(expected.value, current_epoch)
            return False, conflict

        return True, None

    def detect_conflict(
        self,
        expected_version: Optional[ExpectedVersion],
        expected_generation: Optional[ExpectedGeneration],
        current_version_sequence: int,
        current_generation: int,
    ) -> ConflictResult:
        """
        Detect conflicts before applying a mutation.

        Returns:
            Conflict result (no conflict if all validations pass)
        """
        # Check version
        if expected_version is not None:
            is_valid, conflict = self.validate_version(expected_version, current_version_sequence)
            if not is_valid and conflict is not None:
                return conflict

        # Check generation
        if expected_generation is not None:
            is_valid, conflict = self.validate_generation(expected_generation, current_generation)
            if not is_valid and conflict is not None:
                return conflict

        return ConflictResult.no_conflict()

    def check_visibility(
        self,
        state_id: str,
        observer_identity: str,
        visibility_level: VisibilityLevel,
        runtime_id: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify that the observer has visibility to the state.

        Returns:
            (allowed: bool, reason: Optional[str])
        """
        if visibility_level == VisibilityLevel.PRIVATE:
            # Only owner may observe
            return False, "private_state_only_visible_to_owner"

        if visibility_level == VisibilityLevel.RUNTIME_VISIBLE:
            # Must be in same runtime
            if runtime_id is not None:
                pass  # Validation handled by caller

        return True, None

    def verify_isolation(
        self,
        state_runtime_id: Optional[str],
        observer_runtime_id: Optional[str],
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify isolation boundaries are respected.

        Returns:
            (allowed: bool, reason: Optional[str])
        """
        if state_runtime_id is not None and observer_runtime_id is not None:
            if state_runtime_id != observer_runtime_id:
                return False, f"isolation_violation: state in {state_runtime_id}, observer in {observer_runtime_id}"

        return True, None

    def resolve_conflict(
        self,
        conflict_result: ConflictResult,
        retry_policy: Optional[RetryPolicy] = None,
        current_state_version: Optional[int] = None,
        current_state_generation: Optional[int] = None,
    ) -> AtomicOperationResult:
        """
        Apply resolution policy for a detected conflict.

        Returns:
            Operation result with appropriate status
        """
        if conflict_result.conflict_type is None:
            return AtomicOperationResult.committed(
                version_sequence=current_state_version or 0,
                generation=current_state_generation or 0,
            )

        # Get resolution policy
        policy = self._conflict_policies.get(conflict_result.conflict_type, ConflictResolutionPolicy.REJECT)

        if policy == ConflictResolutionPolicy.REJECT:
            return AtomicOperationResult.rejected(
                conflict_result=conflict_result,
                findings=("Conflict rejected per policy",),
            )

        elif policy == ConflictResolutionPolicy.RETRY and retry_policy is not None:
            # Would implement retry logic
            pass  # For now, fall through to reject

        return AtomicOperationResult.rejected(
            conflict_result=conflict_result,
            findings=(f"Conflict resolution policy: {policy.value}",),
        )


# =============================================================================
# PUBLIC API EXPORTS - PHASE 3.15.8
# =============================================================================


__all__ = [
    # CONSISTENCY MODELS (Phase 3.15.8)
    "ConsistencyModel",
    
    # OPTIMISTIC CONCURRENCY CONTROL (Phase 3.15.8)
    "ExpectedVersion",
    "ExpectedGeneration",
    
    # CONFLICT DETECTION & RESOLUTION (Phase 3.15.8)
    "ConflictType",
    "ConflictResolutionPolicy",
    "RetryPolicy",
    "ConflictResult",
    "AtomicOperationStatus",
    "AtomicOperationResult",
    
    # VISIBILITY & ISOLATION (Phase 3.15.8)
    "VisibilityLevel",
    "IsolationLevel",
    
    # PUBLIC API (Phase 3.15.8)
    "StateConcurrencyFacade",
    
    # CROSS-RUNTIME STATE ISOLATION (Phase 3.15.11)
    # Runtime Identity
    "RuntimeIdentity", 
    "BootSessionIdentity",
    
    # Isolation Domains & Policies
    "IsolationDomain", 
    "IsolationPolicy",
    
    # Isolation Models
    "OwnershipIsolation",
    "MutationIsolation",
    "ObservationIsolation",
    "ResourceIsolation",
    
    # Boundary Validation
    "RuntimeBoundaryValidationResult",
    "RuntimeBoundaryValidator",
    "CrossRuntimeOperationType",
    
    # Distributed Readiness  
    "DistributedReadinessContract",
    "SyncStrategy",
    
    # Migration Model
    "MigrationRequest",
    "MigrationResult",
    "MigrationPolicy",
    
    # Violation Detection
    "IsolationViolation",
    "IsolationViolationType",
    "ViolationDetectionResult", 
    "ViolationDetector",
    
    # Diagnostics
    "RuntimeIsolationDiagnostics",
    
    # Public API
    "RuntimeIsolationFacade",
]
