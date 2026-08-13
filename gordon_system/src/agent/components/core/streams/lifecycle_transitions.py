# Stream Lifecycle Transitions - Phase 3.11.3
# =============================================

"""
Canonical stream lifecycle transition model.

This module provides:
    - Immutable transition contracts
    - Compare-and-transition semantics for concurrent requests
    - Lifecycle state admission matrix
    - Deterministic priority handling for conflicting requests
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import time


# =============================================================================
# LIFECYCLE REQUEST MODELS
# =============================================================================


class LifecycleRequestType(Enum):
    """Types of lifecycle requests."""
    
    # Basic transitions
    DECLARE = "declare"
    REGISTER = "register"
    INITIALIZE = "initialize"
    ACTIVATE = "activate"
    
    # Runtime control
    PAUSE = "pause"
    RESUME = "resume"
    DRAIN = "drain"
    
    # Failure recovery
    DEGRADE = "degrade"
    RECOVER = "recover"
    
    # Terminal transitions
    CLOSE = "close"
    FAIL = "fail"


@dataclass(frozen=True)
class LifecycleRequest:
    """
    Request to perform a lifecycle state transition.
    
    Contains all information needed for Core to validate and commit the transition.
    """
    
    # Identity
    stream_id: str
    runtime_instance_id: str
    
    # Request metadata
    request_id: str = field(default_factory=lambda: f"r-{time.monotonic_ns()}")
    timestamp_utc: float = field(default_factory=time.time)
    
    # State information
    expected_state: Optional[str] = None  # For compare-and-transition
    requested_transition: LifecycleRequestType
    
    # Context
    reason: str = "unspecified"
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Authority context
    authority_context: Dict[str, str] = field(default_factory=dict)
    
    # Timeout/deadline
    deadline_utc: Optional[float] = None


@dataclass(frozen=True)
class LifecycleResult:
    """
    Result of a lifecycle transition request.
    
    Truthful results distinguish between:
        - Transition committed
        - Transition rejected (invalid)
        - Transition already satisfied (no-op)
        - Conflict detected
        - Timeout occurred
        - Cancellation occurred
    """
    
    # Core result
    success: bool
    
    # For successful commits
    previous_state: str
    current_state: str
    committed_at_utc: float = field(default_factory=time.time)
    transition_id: Optional[str] = None
    
    # For non-success cases
    rejection_reason: Optional[str] = None
    is_already_satisfied: bool = False  # Requested state matches current
    is_conflict: bool = False          # Another transition committed first
    timed_out: bool = False            # Deadline exceeded before commit
    cancelled: bool = False            # Request cancelled
    
    # Partial outcomes (for partial success/failure)
    partial_failure: bool = False
    failure_description: Optional[str] = None


# =============================================================================
# COMPARE-AND-TRANSITION SEMANTICS
# =============================================================================


class CompareAndTransitionError(Exception):
    """Raised when compare-and-swap fails due to expected state mismatch."""
    
    def __init__(
        self,
        stream_id: str,
        expected_state: str,
        actual_state: str,
        message: Optional[str] = None
    ):
        self.stream_id = stream_id
        self.expected_state = expected_state
        self.actual_state = actual_state
        self.message = message or f"State mismatch: expected {expected_state}, got {actual_state}"
        super().__init__(self.message)


@dataclass(frozen=True)
class CompareAndTransitionResult:
    """
    Result of a compare-and-transition operation.
    
    A failed compare-and-swap must leave state unchanged.
    """
    
    # Success indicator
    succeeded: bool
    
    # For success
    new_state: Optional[str] = None
    transition_id: Optional[str] = None
    committed_at_utc: float = field(default_factory=time.time)
    
    # For failure
    old_state: Optional[str] = None  # Current state before attempt
    error_type: str = "unknown"      # CompareFailed, InvalidTransition, etc.
    error_message: Optional[str] = None
    
    @classmethod
    def success(cls, new_state: str, transition_id: str) -> "CompareAndTransitionResult":
        return cls(succeeded=True, new_state=new_state, transition_id=transition_id)
    
    @classmethod
    def compare_failed(cls, current_state: str, expected_state: str) -> "CompareAndTransitionResult":
        return cls(
            succeeded=False,
            old_state=current_state,
            error_type="compare_failed",
            error_message=f"Expected {expected_state}, got {current_state}"
        )
    
    @classmethod
    def invalid_transition(cls, from_state: str, to_state: str) -> "CompareAndTransitionResult":
        return cls(
            succeeded=False,
            old_state=from_state,
            error_type="invalid_transition",
            error_message=f"Invalid transition: {from_state} -> {to_state}"
        )


# =============================================================================
# LIFECYCLE ADMISSION MATRIX
# =============================================================================


class AdmissionState(Enum):
    """Operational admission state of a stream."""
    
    OPEN = "open"          # Accepts normal proposals
    PAUSED = "paused"      # Does not accept normal proposals (may allow reads)
    DRAINING = "draining"  # Rejects new, allows in-flight to complete
    CLOSED = "closed"      # No admission at all
    DEGRADED = "degraded"  # Reduced functionality


@dataclass(frozen=True)
class LifecycleAdmissionMatrix:
    """
    Matrix of which operations are allowed in each lifecycle state.
    
    This is a static policy - the actual runtime may enforce additional checks.
    """
    
    stream_id: str
    
    # Operation permissions by state
    declare_allowed: Dict[str, bool] = field(default_factory=dict)
    register_allowed: Dict[str, bool] = field(default_factory=dict)
    initialize_allowed: Dict[str, bool] = field(default_factory=dict)
    activate_allowed: Dict[str, bool] = field(default_factory=dict)
    
    publish_proposal_allowed: Dict[str, bool] = field(default_factory=dict)
    commit_record_allowed: Dict[str, bool] = field(default_factory=dict)
    
    read_committed_allowed: Dict[str, bool] = field(default_factory=dict)
    subscribe_allowed: Dict[str, bool] = field(default_factory=dict)
    
    checkpoint_allowed: Dict[str, bool] = field(default_factory=dict)
    replay_allowed: Dict[str, bool] = field(default_factory=dict)
    
    pause_allowed: Dict[str, bool] = field(default_factory=dict)
    resume_allowed: Dict[str, bool] = field(default_factory=dict)
    drain_allowed: Dict[str, bool] = field(default_factory=dict)
    
    recover_allowed: Dict[str, bool] = field(default_factory=dict)
    close_allowed: Dict[str, bool] = field(default_factory=dict)
    
    inspect_health_allowed: Dict[str, bool] = field(default_factory=dict)
    inspect_diagnostics_allowed: Dict[str, bool] = field(default_factory=dict)
    inspect_integrity_allowed: Dict[str, bool] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize default permissions."""
        # Default to False for all
        states = ["declared", "registered", "initializing", "ready", "activating",
                  "active", "pausing", "paused", "resuming", "draining", "drained",
                  "degrading", "degraded", "recovering", "closing", "closed", 
                  "failing", "failed"]
        
        for state in states:
            if not hasattr(self, f"declare_allowed"):
                continue
            # Set defaults (will be overridden by class initialization)
            pass
    
    def get_admission_state(self, lifecycle_state: str) -> AdmissionState:
        """Get the admission state for a given lifecycle state."""
        state_map = {
            "declared": AdmissionState.CLOSED,
            "registered": AdmissionState.CLOSED,
            "initializing": AdmissionState.CLOSED,
            "ready": AdmissionState.CLOSED,
            "activating": AdmissionState.OPEN,  # May or may not accept depending on policy
            "active": AdmissionState.OPEN,
            "pausing": AdmissionState.PAUSED,
            "paused": AdmissionState.PAUSED,
            "resuming": AdmissionState.OPEN,    # During resume, admission may open gradually
            "draining": AdmissionState.DRAINING,
            "drained": AdmissionState.CLOSED,
            "degrading": AdmissionState.DEGRADED,
            "degraded": AdmissionState.DEGRADED,
            "recovering": AdmissionState.CLOSED,
            "closing": AdmissionState.CLOSED,
            "closed": AdmissionState.CLOSED,
            "failing": AdmissionState.CLOSED,
            "failed": AdmissionState.CLOSED,
        }
        return state_map.get(lifecycle_state, AdmissionState.CLOSED)
    
    def can_admit_proposals(self, lifecycle_state: str) -> bool:
        """Check if proposals may be admitted in this state."""
        admission = self.get_admission_state(lifecycle_state)
        return admission == AdmissionState.OPEN
    
    def can_accept_commits(self, lifecycle_state: str) -> bool:
        """Check if commits may be accepted in this state."""
        # Commits are more restrictive than proposals
        states_with_commits = {"active", "pausing", "resuming"}
        return lifecycle_state in states_with_commits


# =============================================================================
# TRANSITION PRIORITY MODEL
# =============================================================================


class TransitionPriority(Enum):
    """Priority levels for lifecycle transitions."""
    
    # Security-critical (highest priority)
    SECURITY_FORCED_FAIL = 100     # Security violation detected
    INTEGRITY_FORCED_FAIL = 90     # Integrity failure detected
    
    # System-critical
    SHUTDOWN = 80                  # System shutdown initiated
    ADMINISTRATIVE_CLOSE = 75      # Administrative closure request
    
    # Recovery and maintenance
    RECOVERY = 70                  # Recovery operation
    DRAIN = 60                     # Graceful drain (shutdown preparation)
    
    # Normal operations
    PAUSE = 50                     # Pausing for maintenance
    RESUME = 45                    # Resuming after pause
    
    # Activation and startup
    ACTIVATE = 40                  # Activate stream
    DEGRADE = 30                   # Enter degraded mode (if policy allows)


@dataclass(frozen=True)
class TransitionPriorityContext:
    """
    Context for determining transition priority in conflicting scenarios.
    
    When multiple requests target the same stream, priorities determine
    which one gets committed first.
    """
    
    stream_id: str
    
    # Priority of each pending request
    pending_priorities: Dict[str, int] = field(default_factory=dict)
    
    # Current state (for determining if transition is even possible)
    current_state: Optional[str] = None


def resolve_conflicting_transitions(
    priorities: Dict[TransitionPriority, List[str]],
    current_state: str,
    valid_transitions: List[Tuple[str, str]],
) -> Optional[Tuple[str, TransitionPriority]]:
    """
    Resolve conflicting transitions based on priority.
    
    Args:
        priorities: Mapping from priority level to list of requested transitions
        current_state: Current lifecycle state
        valid_transitions: List of (from_state, to_state) tuples that are valid
    
    Returns:
        (transition_to_commit, priority_level) or None if no valid transition exists
    """
    # Sort by priority (highest first)
    sorted_priorities = sorted(
        priorities.items(),
        key=lambda x: x[0].value,
        reverse=True
    )
    
    for priority, transitions in sorted_priorities:
        for from_state, to_state in transitions:
            if current_state == from_state and (from_state, to_state) in valid_transitions:
                return (f"{from_state} -> {to_state}", priority)
    
    return None  # No valid transition found


# =============================================================================
# ATOMIC PUBLICATION CONTRACT
# =============================================================================


class AtomicPublicationError(Exception):
    """Raised when atomic publication contract is violated."""
    pass


@dataclass(frozen=True)
class AtomicPublicationResult:
    """
    Result of atomic lifecycle state publication.
    
    Consumers must observe either the previous valid snapshot OR the new one,
    never a mixed or partial state.
    """
    
    # Publication outcome
    published: bool
    
    # Snapshot after publication (if successful)
    snapshot: Optional[Dict[str, Any]] = None
    timestamp_utc: float = field(default_factory=time.time)
    
    # For failed publications
    error_type: str = "unknown"
    error_message: Optional[str] = None
    
    # Partial failure tracking (e.g., publication succeeded but passive events failed)
    partial_failure: bool = False
    passive_event_failed: bool = False


# =============================================================================
# LIFECYCLE HISTORY - Bounded Records
# =============================================================================


@dataclass(frozen=True)
class LifecycleHistoryEntry:
    """
    One entry in the bounded lifecycle transition history.
    
    History supports diagnostics, recovery, continuity, and auditing.
    Must remain bounded (not a general event store).
    """
    
    # Entry identity
    sequence_number: int  # Monotonic within stream instance
    
    # Transition info
    transition_id: str
    timestamp_utc: float
    previous_state: str
    committed_state: str
    
    # Context
    requested_by: Optional[str] = None
    authority_id: Optional[str] = None
    
    # Generation context
    generation_before: Optional[str] = None
    generation_after: Optional[str] = None
    
    # Metadata
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    provenance: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class LifecycleHistory:
    """
    Bounded history of lifecycle transitions for one stream instance.
    
    Retention bounds are configurable - old entries may be pruned.
    """
    
    stream_id: str
    runtime_instance_id: str
    
    # Maximum history length (configurable)
    max_entries: int = 1000
    
    # History entries in chronological order
    _entries: Tuple[LifecycleHistoryEntry, ...] = field(default_factory=tuple)
    
    def append(self, entry: LifecycleHistoryEntry) -> "LifecycleHistory":
        """Append new entry, pruning oldest if necessary."""
        new_entries = self._entries + (entry,)
        
        # Prune to max length
        if len(new_entries) > self.max_entries:
            new_entries = new_entries[-self.max_entries:]
        
        return dataclass_replace(self, _entries=new_entries)
    
    def get_latest(self) -> Optional[LifecycleHistoryEntry]:
        """Get the most recent entry."""
        if not self._entries:
            return None
        return self._entries[-1]
    
    def get_by_state(self, state: str) -> Tuple[LifecycleHistoryEntry, ...]:
        """Get all entries where committed_state equals state."""
        return tuple(e for e in self._entries if e.committed_state == state)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert history to dictionary for serialization."""
        return {
            "stream_id": self.stream_id,
            "runtime_instance_id": self.runtime_instance_id,
            "max_entries": self.max_entries,
            "entry_count": len(self._entries),
            "latest_transition_id": self.get_latest().transition_id if self.get_latest() else None,
            "history": [
                {
                    "sequence_number": e.sequence_number,
                    "transition_id": e.transition_id,
                    "timestamp_utc": e.timestamp_utc,
                    "previous_state": e.previous_state,
                    "committed_state": e.committed_state,
                    "generation_before": e.generation_before,
                    "generation_after": e.generation_after,
                }
                for e in self._entries
            ],
        }


# =============================================================================
# FAILURE MODELS - Partial Outcomes
# =============================================================================


class LifecycleFailureType(Enum):
    """Categories of lifecycle failures."""
    
    # Validation failures
    INVALID_STATE = "invalid_state"
    INVALID_TRANSITION = "invalid_transition"
    STATE_CONFLICT = "state_conflict"  # Compare-and-swap failed
    
    # Timeout/failure
    TIMEOUT = "timeout"
    DEADLINE_EXCEEDED = "deadline_exceeded"
    
    # Resource failures
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    AUTHORITY_UNAVAILABLE = "authority_unavailable"
    
    # Publication failures
    PUBLICATION_FAILED = "publication_failed"  # State changed but passive events failed
    
    # Recovery failures
    RECOVERY_FAILED = "recovery_failed"
    
    # Partial outcomes
    PARTIAL_SUCCESS = "partial_success"


@dataclass(frozen=True)
class LifecycleFailure:
    """
    Structured failure for lifecycle operations.
    
    Preserves context including retryability and partial commit status.
    """
    
    failure_type: LifecycleFailureType
    stream_id: str
    current_state: str
    
    # Context
    requested_transition: Optional[str] = None
    requested_by: Optional[str] = None
    
    # Diagnostics
    correlation_id: Optional[str] = None
    error_message: Optional[str] = None
    
    # Retry information
    retryable: bool = False
    retry_after_seconds: Optional[float] = None
    
    # Partial outcome tracking
    partial_commit_status: bool = False  # Some changes applied before failure
    committed_changes: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# DATACLASS REPLACE UTILITY
# =============================================================================


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Simple dataclass replace implementation for frozen dataclasses."""
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


# =============================================================================
# EXPORTS
# =============================================================================

from typing import Any  # Required for Any in type annotations

__all__ = [
    # Request/response models
    "LifecycleRequestType",
    "LifecycleRequest",
    "LifecycleResult",
    
    # Compare-and-transition
    "CompareAndTransitionError",
    "CompareAndTransitionResult",
    
    # Admission matrix
    "AdmissionState",
    "LifecycleAdmissionMatrix",
    
    # Priority model
    "TransitionPriority",
    "TransitionPriorityContext",
    "resolve_conflicting_transitions",
    
    # Atomic publication
    "AtomicPublicationError",
    "AtomicPublicationResult",
    
    # History
    "LifecycleHistoryEntry",
    "LifecycleHistory",
    
    # Failure models
    "LifecycleFailureType",
    "LifecycleFailure",
    
    # Utilities
    "dataclass_replace",
]