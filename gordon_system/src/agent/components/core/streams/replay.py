# Stream Replay Infrastructure - Phase 3.11.6
# ============================================

"""
Canonical Replay Architecture for Gordon's Semantic Streams.

This module implements:
    - Replay request and planning
    - Bounded replay ranges
    - Replay sessions and cursors
    - Deterministic ordering preservation
    - Side-effect safety policies
    - Live-delivery handoff

Architecture Overview:

Replay Axis (Continuation of Checkpoint):
    [Checkpoint] → Replay Cursor → Bounded Replay Range → Records
    
Replay Purpose:
    - Re-observe historical committed records
    - Enable catch-up from cursor checkpoints
    - Support diagnostic analysis
    - Provide recovery input for domain reconstruction

Key Constraints:
    - Replay NEVER modifies canonical stream history
    - Replay NEVER assigns new canonical sequence numbers
    - Replay NEVER invokes side effects (actions, commands, etc.)
    - Replay preserves all integrity guarantees of original commits
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Protocol, runtime_checkable
from enum import Enum, auto
import time
import uuid


# =============================================================================
# REPLAY MODES - Purpose of the Replay
# =============================================================================


class ReplayMode(Enum):
    """
    Mode of replay operation.
    
    Each mode defines different semantics for how replay is performed and used.
    """
    
    OBSERVATIONAL = "observational"                 # For diagnostics, audit, testing
    SUBSCRIBER_CATCH_UP = "subscriber_catch_up"     # Deliver missed records to subscriber
    CURSOR_RECONSTRUCTION = "cursor_reconstruction"  # Rebuild subscriber progress from checkpoint
    VALIDATION = "validation"                        # Verify record integrity
    STATE_RECONSTRUCTION = "state_reconstruction"    # Feed history for domain reconstruction
    DIAGNOSTIC = "diagnostic"                       # Operator diagnostics and debugging
    CONTINUITY_ASSISTED = "continuity_assisted"     # Crash recovery with continuity help


# =============================================================================
# REPLAY REQUEST - Request to Perform Replay
# =============================================================================


@dataclass(frozen=True)
class ReplayRequest:
    """
    Immutable request for replay.
    
    Contains all parameters needed to plan and execute a replay operation.
    Does NOT contain live objects or runtime state.
    """
    
    # Identity
    replay_request_id: str            # Unique request ID
    
    # Stream reference (stable identifiers)
    stream_id: str                    # Which stream?
    source_generation_id: Optional[str] = None  # Specific generation, or None for latest
    
    # Replay mode and purpose
    replay_mode: ReplayMode = ReplayMode.OBSERVATIONAL
    
    # Starting point
    checkpoint_id: Optional[str] = None      # From checkpoint
    start_position: Optional[int] = None     # Sequence number (inclusive)
    
    # Ending point
    end_position: Optional[int] = None       # Sequence number (exclusive, or inclusive per policy)
    maximum_records: Optional[int] = None    # Max records to return
    maximum_bytes: Optional[int] = None      # Max bytes to return
    
    # Subscription reference (for subscriber catch-up mode)
    subscription_id: Optional[str] = None
    subscriber_id: Optional[str] = None
    
    # Policies
    delivery_policy: str = "at-least-once"   # Delivery semantics
    cursor_policy: str = "preserve"          # Cursor advancement policy
    side_effect_policy: str = "block-all"    # How to handle side-effecting records
    
    # Authorization reference (not credentials)
    authorization_context_reference: Optional[str] = None
    
    # Deadline for replay completion
    deadline_utc: Optional[float] = None
    
    # Correlation and causation
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Provenance
    requested_by: Optional[str] = None
    reason: str = "auto"
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def for_observational(
        cls,
        stream_id: str,
        start_position: int,
        maximum_records: int = 1000,
    ) -> "ReplayRequest":
        """Create an observational replay request."""
        return cls(
            replay_request_id=f"replay-{time.monotonic_ns()}-{uuid.uuid4().hex[:8]}",
            stream_id=stream_id,
            start_position=start_position,
            maximum_records=maximum_records,
            replay_mode=ReplayMode.OBSERVATIONAL,
        )
    
    @classmethod
    def for_catch_up(
        cls,
        stream_id: str,
        subscription_id: str,
        checkpoint_id: str,
    ) -> "ReplayRequest":
        """Create a catch-up replay request from a checkpoint."""
        return cls(
            replay_request_id=f"replay-{time.monotonic_ns()}-{uuid.uuid4().hex[:8]}",
            stream_id=stream_id,
            subscription_id=subscription_id,
            checkpoint_id=checkpoint_id,
            replay_mode=ReplayMode.SUBSCRIBER_CATCH_UP,
        )
    
    def is_expired(self, at_utc: Optional[float] = None) -> bool:
        """Check if this request has expired."""
        if self.deadline_utc is None:
            return False
        at = at_utc or time.time()
        return at > self.deadline_utc


# =============================================================================
# REPLAY RANGE - Bounded Range for Replay
# =============================================================================


@dataclass(frozen=True)
class ReplayRange:
    """
    Immutable replay range definition.
    
    Specifies exactly which records are eligible for replay.
    Does NOT contain live objects or runtime state.
    """
    
    # Stream and generation reference (stable identifiers)
    stream_id: str
    generation_ids: Tuple[str, ...]  # Which generations to include
    
    # Range boundaries
    start_sequence: int               # Inclusive start
    end_sequence: Optional[int] = None  # Exclusive or inclusive per policy
    
    # Bounds from retention and capacity
    earliest_retained_sequence: int   # Earliest available sequence
    latest_committed_sequence: int    # Latest committed sequence
    
    # Capacity budget for replay execution
    maximum_records: Optional[int] = None
    maximum_bytes: Optional[int] = None
    
    # Eligibility filters
    eligible_record_types: Tuple[str, ...] = field(default_factory=tuple)  # Empty = all
    eligible_schema_ids: Tuple[str, ...] = field(default_factory=tuple)   # Empty = all
    
    def is_valid(self) -> Tuple[bool, Optional[str]]:
        """
        Validate the replay range.
        
        Returns:
            (is_valid, error_message)
        """
        if self.start_sequence < 0:
            return False, "start_sequence cannot be negative"
        
        if self.earliest_retained_sequence is not None and self.start_sequence < self.earliest_retained_sequence:
            return False, f"start_sequence {self.start_sequence} is before retention boundary {self.earliest_retained_sequence}"
        
        if self.end_sequence is not None and self.start_sequence > self.end_sequence:
            return False, "start_sequence cannot be after end_sequence"
        
        return True, None
    
    def clip_to_bounds(self) -> "ReplayRange":
        """Return new range clipped to retention bounds."""
        start = max(self.start_sequence, self.earliest_retained_sequence)
        end = self.end_sequence if self.end_sequence is not None else self.latest_committed_sequence
        return dataclass_replace(
            self,
            start_sequence=start,
            end_sequence=end
        )
    
    def record_count(self) -> int:
        """Estimate number of records in range."""
        if self.end_sequence is None:
            return self.latest_committed_sequence - self.start_sequence + 1
        return max(0, self.end_sequence - self.start_sequence)


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Simple dataclass replace implementation for frozen dataclasses."""
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


# =============================================================================
# REPLAY PLAN - Validated Replay Plan
# =============================================================================


@dataclass(frozen=True)
class ReplayPlan:
    """
    Immutable validated replay plan.
    
    Created by the replay authority before execution. Contains only
    bounded metadata and references - no live objects or runtime state.
    """
    
    # Identity
    replay_plan_id: str               # Unique plan ID
    
    # Request reference
    request_id: str                   # Original request that triggered this plan
    
    # Stream and generation
    stream_id: str
    generation_ids: Tuple[str, ...]
    
    # Range (as determined during planning)
    start_sequence: int
    end_sequence: Optional[int] = None
    
    # Estimated size
    estimated_record_count: int
    estimated_bytes: int = 0          # If known
    
    # Validation results
    retention_validation: str = "valid"       # valid, boundary_exceeded, unavailable
    authorization_validation: str = "valid"   # valid, unauthorized, missing_context
    privacy_policy_version: Optional[str] = None
    trust_policy_version: Optional[str] = None
    
    # Side-effect policy (from request)
    side_effect_policy: str = "block-all"
    delivery_policy: str = "at-least-once"
    
    # Capacity budget allocated for this replay
    capacity_budget_records: int = 0
    capacity_budget_bytes: int = 0
    capacity_budget_seconds: float = 30.0  # Maximum duration
    
    # Deadline (from request)
    deadline_utc: Optional[float] = None
    
    # Planning metadata
    created_at_utc: float = field(default_factory=time.time)
    planned_by: str = "replay_authority"
    
    # Provenance
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    provenance: Dict[str, str] = field(default_factory=dict)
    
    # Status and warnings
    status: str = "planned"           # planned, admitted, running, cancelled, completed
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    
    def is_expired(self, at_utc: Optional[float] = None) -> bool:
        """Check if plan has expired."""
        if self.deadline_utc is None:
            return False
        at = at_utc or time.time()
        return at > self.deadline_utc
    
    def with_warning(self, warning: str) -> "ReplayPlan":
        """Add a warning to the plan."""
        return dataclass_replace(
            self,
            warnings=self.warnings + (warning,)
        )
    
    def mark_admitted(self) -> "ReplayPlan":
        """Mark plan as admitted for execution."""
        if self.status == "planned":
            return dataclass_replace(self, status="admitted")
        return self
    
    def mark_running(self) -> "ReplayPlan":
        """Mark plan as running."""
        if self.status in ("planned", "admitted"):
            return dataclass_replace(self, status="running")
        return self
    
    def mark_completed(self) -> "ReplayPlan":
        """Mark plan as completed."""
        return dataclass_replace(self, status="completed")


# =============================================================================
# REPLAY SESSION - Runtime Replay Execution
# =============================================================================


class ReplaySessionState(Enum):
    """
    State of a replay session.
    
    States:
        PLANNED: Plan created, not yet admitted
        ADMITTED: Admitted to execution queue
        RUNNING: Actively delivering records
        PAUSED: Temporarily suspended
        THROTTLED: Running but rate-limited
        COMPLETED: All eligible records delivered
        CANCELLED: Cancelled by request or deadline
        TIMED_OUT: Exceeded time budget
        FAILED: Failed during execution
        PARTIALLY_COMPLETED: Completed with some issues
    """
    PLANNED = "planned"
    ADMITTED = "admitted"
    RUNNING = "running"
    PAUSED = "paused"
    THROTTLED = "throttled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"


@dataclass(frozen=True)
class ReplaySession:
    """
    Runtime state of a replay session.
    
    Contains runtime progress and bounded diagnostics only. No live
    objects or long-term state.
    """
    
    # Identity
    replay_session_id: str            # Unique session ID
    
    # Plan reference (stable identifier)
    replay_plan_id: str               # Plan that governs this session
    
    # Stream reference (stable identifier)
    stream_id: str
    
    # Progress tracking
    current_sequence: int             # Next sequence to deliver
    last_delivered_sequence: Optional[int] = None  # Last delivered (if any)
    last_acknowledged_sequence: Optional[int] = None  # Last acknowledged (if applicable)
    
    # Counters
    records_delivered: int = 0
    records_acknowledged: int = 0
    records_filtered: int = 0         # Excluded by policy
    records_skipped: int = 0          # Skipped due to policy
    
    # Budget remaining
    remaining_budget_records: Optional[int] = None
    remaining_budget_bytes: Optional[int] = None
    remaining_time_seconds: float = 30.0
    
    # Deadline
    deadline_utc: Optional[float] = None
    
    # Cancellation state
    is_cancelled: bool = False
    cancelled_at_utc: Optional[float] = None
    cancellation_reason: Optional[str] = None
    
    # Session state
    state: ReplaySessionState = ReplaySessionState.PLANNED
    
    # Warnings and diagnostics
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def create(
        cls,
        replay_plan_id: str,
        stream_id: str,
        start_sequence: int,
        deadline_utc: Optional[float] = None,
    ) -> "ReplaySession":
        """Create a new replay session."""
        return cls(
            replay_session_id=f"session-{time.monotonic_ns()}-{uuid.uuid4().hex[:8]}",
            replay_plan_id=replay_plan_id,
            stream_id=stream_id,
            current_sequence=start_sequence,
            deadline_utc=deadline_utc,
        )
    
    def advance(self, delivered_count: int = 1) -> "ReplaySession":
        """Advance session after delivering records."""
        return dataclass_replace(
            self,
            current_sequence=self.current_sequence + delivered_count,
            last_delivered_sequence=self.current_sequence,
            records_delivered=self.records_delivered + delivered_count,
            remaining_budget_records=(self.remaining_budget_records or 0) - delivered_count if self.remaining_budget_records else None,
        )
    
    def acknowledge(self, acknowledged_count: int = 1) -> "ReplaySession":
        """Track acknowledgements."""
        return dataclass_replace(
            self,
            last_acknowledged_sequence=self.current_sequence - 1,
            records_acknowledged=self.records_acknowledged + acknowledged_count,
        )
    
    def add_warning(self, warning: str) -> "ReplaySession":
        """Add a warning to the session."""
        return dataclass_replace(
            self,
            warnings=self.warnings + (warning,)
        )
    
    def cancel(self, reason: Optional[str] = None) -> "ReplaySession":
        """Mark session as cancelled."""
        return dataclass_replace(
            self,
            is_cancelled=True,
            state=ReplaySessionState.CANCELLED,
            cancelled_at_utc=time.time(),
            cancellation_reason=reason,
        )
    
    def complete(self, status: str = "completed") -> "ReplaySession":
        """Mark session as completed."""
        return dataclass_replace(
            self,
            state=ReplaySessionState(status) if status in ["completed", "partially_completed"] else ReplaySessionState.COMPLETED
        )


# =============================================================================
# REPLAY CURSOR - Progress Within a Replay Session
# =============================================================================


@dataclass(frozen=True)
class ReplayCursor:
    """
    Cursor tracking progress within a replay session.
    
    This is DISTINCT from a live subscriber cursor. It tracks progress
    through replay, not through live delivery.
    """
    
    # Identity
    replay_cursor_id: str             # Unique cursor ID
    
    # Session reference (stable identifier)
    replay_session_id: str
    
    # Stream and generation reference
    stream_id: str
    generation_id: Optional[str] = None
    
    # Position
    next_sequence: int                # Next sequence to deliver
    last_delivered_sequence: Optional[int] = None  # Last delivered (if any)
    last_acknowledged_sequence: Optional[int] = None  # Last acknowledged (if any)
    
    # Version for updates
    cursor_version: int = 1
    
    # Timestamps
    updated_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    created_by: str = "replay_authority"
    
    @classmethod
    def create(
        cls,
        replay_session_id: str,
        stream_id: str,
        next_sequence: int,
    ) -> "ReplayCursor":
        """Create a new replay cursor."""
        return cls(
            replay_cursor_id=f"rcursor-{time.monotonic_ns()}-{uuid.uuid4().hex[:8]}",
            replay_session_id=replay_session_id,
            stream_id=stream_id,
            next_sequence=next_sequence,
        )
    
    def advance(self, count: int = 1) -> "ReplayCursor":
        """Advance cursor position."""
        return dataclass_replace(
            self,
            next_sequence=self.next_sequence + count,
            last_delivered_sequence=self.next_sequence - 1 if self.next_sequence > 0 else None,
            cursor_version=self.cursor_version + 1,
            updated_at_utc=time.time(),
        )
    
    def acknowledge(self, sequence: int) -> "ReplayCursor":
        """Mark a sequence as acknowledged."""
        return dataclass_replace(
            self,
            last_acknowledged_sequence=sequence,
            cursor_version=self.cursor_version + 1,
            updated_at_utc=time.time(),
        )


# =============================================================================
# REPLAY RESULT - Result of Replay Execution
# =============================================================================


@dataclass(frozen=True)
class ReplayResult:
    """
    Immutable result of a replay execution.
    
    Contains only bounded, summary statistics. Does NOT contain record
    contents or live objects.
    """
    
    # Identity
    replay_result_id: str             # Unique result ID
    
    # Session and request reference
    replay_session_id: str
    replay_request_id: Optional[str] = None  # May be None if plan-driven
    
    # Stream reference
    stream_id: str
    
    # Mode of this replay
    replay_mode: ReplayMode = ReplayMode.OBSERVATIONAL
    
    # Requested vs actual range
    start_position: int
    requested_end_position: Optional[int] = None
    actual_end_position: Optional[int] = None  # Where replay actually stopped
    
    # Statistics
    records_considered: int = 0       # Records examined
    records_delivered: int = 0        # Records delivered to subscriber
    records_filtered: int = 0         # Records filtered out by policy
    records_skipped: int = 0          # Records skipped (e.g., duplicates)
    records_acknowledged: int = 0     # Records acknowledged by subscriber
    
    # Duplicate handling
    duplicate_deliveries: int = 0     # How many times a record was redelivered
    
    # Failures
    failures: Tuple[str, ...] = field(default_factory=tuple)  # Failure messages
    
    # Cursor state (before and after)
    cursor_before: Optional[int] = None  # Subscriber cursor position before replay
    cursor_after: Optional[int] = None   # Subscriber cursor position after replay
    
    # Live handoff status
    live_handoff_status: str = "not_attempted"  # not_attempted, success, failed, skipped
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    # Status and warnings
    status: str = "pending"           # pending, running, completed, partially_completed, cancelled, timed_out, rejected
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    
    # Correlation
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Provenance
    created_by: str = "replay_authority"
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_session(cls, session: ReplaySession) -> "ReplayResult":
        """Create result from a completed session."""
        return cls(
            replay_result_id=f"result-{time.monotonic_ns()}-{uuid.uuid4().hex[:8]}",
            replay_session_id=session.replay_session_id,
            stream_id=session.stream_id,
            start_position=0,  # Would need to track start
            records_delivered=session.records_delivered,
            records_acknowledged=session.records_acknowledged,
            status="completed" if session.state == ReplaySessionState.COMPLETED else "partially_completed",
        )
    
    def complete(self) -> "ReplayResult":
        """Mark result as completed."""
        return dataclass_replace(
            self,
            status="completed",
            completed_at_utc=time.time(),
        )
    
    def fail(self, failure_message: str) -> "ReplayResult":
        """Mark result as failed with a message."""
        return dataclass_replace(
            self,
            status="failed",
            failures=self.failures + (failure_message,),
            completed_at_utc=time.time(),
        )


# =============================================================================
# LIVE-DELIVERY HANDOFF POLICY
# =============================================================================


class LiveHandoffPolicy(Enum):
    """
    Policy for handing off from replay to live delivery.
    
    Defines how replay transitions to continuous live subscription.
    """
    
    PAUSE_LIVE_THEN_HANDOFF = "pause_live_then_handoff"      # Pause live, handoff, resume
    BUFFER_LIVE_DURING_REPLAY = "buffer_live_during_replay"  # Buffer live records during replay, deliver after
    SNAPSHOT_BOUNDARY_THEN_SWITCH = "snapshot_boundary_then_switch"  # Take snapshot at boundary, switch to subscription
    MERGE_WITH_SEQUENCE_GATE = "merge_with_sequence_gate"   # Merge with sequence gate, prevent inversion
    OWNER_DEFINED = "owner_defined"                          # Owner-defined custom policy


# =============================================================================
# DUPLICATE POLICY - How to Handle Duplicate Replay
# =============================================================================


class DuplicateReplayPolicy(Enum):
    """
    Policy for handling records that were already processed.
    
    Determines what happens when replay encounters records the subscriber
    has already received and acknowledged.
    """
    
    SKIP_ALREADY_ACKNOWLEDGED = "skip_already_acknowledged"  # Don't redeliver if acknowledged
    REDELIVER_UNACKNOWLEDGED = "redeliver_unacknowledged"    # Redeliver only unacknowledged
    REDELIVER_ALL = "redeliver_all"                          # Always redeliver (idempotent consumers)
    REDELIVER_WITH_DUPLICATE_MARKER = "redeliver_with_duplicate_marker"  # Mark as duplicate
    OWNER_DEFINED = "owner_defined"                           # Owner-defined policy


# =============================================================================
# SIDE-EFFECT POLICY - How to Handle Side-Effecting Records
# =============================================================================


class SideEffectPolicy(Enum):
    """
    Policy for handling records with side effects.
    
    Side-effect records include:
        - Action authorizations (may not be re-authorized)
        - External commands (should not be repeated)
        - Payments/transactions (cannot be repeated)
        - Deletions (irreversible)
    
    Generic replay NEVER executes these. They must be filtered or blocked.
    """
    
    BLOCK_ALL = "block_all"                   # Block all side-effecting records
    FILTER_AND_REPORT = "filter_and_report"   # Filter, include in statistics
    SKIP_WITH_WARNING = "skip_with_warning"   # Skip but log warning
    OWNER_DEFINED = "owner_defined"           # Owner-defined handling


# =============================================================================
# REPLAY ADMISSION - Admission Decision
# =============================================================================


@dataclass(frozen=True)
class ReplayAdmissionResult:
    """Result of replay admission review."""
    
    decision: str                     # accept, wait, throttle, reject
    reason: str                       # Human-readable explanation
    
    # If throttled or waiting
    retry_after_seconds: Optional[float] = None
    estimated_wait_time_seconds: Optional[float] = None
    
    # Capacity information
    capacity_percent: float = 0.0     # Current capacity utilization
    
    # Request reference (for tracing)
    replay_request_id: Optional[str] = None
    correlation_id: Optional[str] = None


# =============================================================================
# REPLAY AUTHORITY - Interface for Replay Operations
# =============================================================================


@runtime_checkable
class ReplayAuthority(Protocol):
    """
    Protocol for replay authority operations.
    
    The replay authority:
        - Validates replay requests against policy
        - Creates replay plans from requests
        - Manages replay sessions
        - Enforces capacity and fairness
    
    Does NOT own canonical stream history or cursor state.
    """
    
    async def plan_replay(
        self,
        request: ReplayRequest,
    ) -> Tuple[ReplayPlan, Optional[str]]:
        """
        Plan a replay operation.
        
        Args:
            request: The replay request
        
        Returns:
            (replay_plan, error_message) - either plan or error
        """
        ...
    
    async def admit_replay(
        self,
        plan: ReplayPlan,
    ) -> Tuple[ReplaySession, Optional[str]]:
        """
        Admit a replay plan to execution.
        
        Args:
            plan: The validated replay plan
        
        Returns:
            (replay_session, error_message) - either session or error
        """
        ...
    
    async def execute_replay(
        self,
        session: ReplaySession,
    ) -> Tuple[ReplayResult, Optional[str]]:
        """
        Execute a replay session.
        
        Args:
            session: The admitted replay session
        
        Returns:
            (replay_result, error_message) - either result or error
        """
        ...
    
    async def cancel_replay(
        self,
        session_id: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Cancel a replay session.
        
        Args:
            session_id: ID of the session to cancel
        
        Returns:
            (success, error_message)
        """
        ...
    
    async def get_session(self, session_id: str) -> Optional[ReplaySession]:
        """Get current state of a replay session."""
        ...


# =============================================================================
# REPLAY INTEGRATION - Integration with Storage
# =============================================================================


@runtime_checkable
class ReplayStorage(Protocol):
    """
    Protocol for storage operations during replay.
    
    Must support:
        - Reading records in range (preserving order)
        - Checking retention boundaries
        - Verifying record integrity
    
    NOTE: This is only the storage interface. Replay semantics
          are owned by this module.
    """
    
    async def read_range(
        self,
        stream_id: str,
        generation_ids: Tuple[str, ...],
        start_sequence: int,
        end_sequence: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Tuple[Dict[str, Any], ...]:
        """
        Read records in a range.
        
        Args:
            stream_id: Stream to read from
            generation_ids: Generations to include
            start_sequence: Starting sequence (inclusive)
            end_sequence: Ending sequence (exclusive), or None for all
            limit: Maximum number of records
        
        Returns:
            Tuple of record dictionaries in canonical order
        """
        ...
    
    async def get_retention_boundary(
        self,
        stream_id: str,
    ) -> Optional[int]:
        """Get the earliest sequence available for replay."""
        ...
    
    async def verify_integrity(self, record: Dict[str, Any]) -> bool:
        """Verify a record's integrity."""
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Modes and policies
    "ReplayMode",
    "LiveHandoffPolicy",
    "DuplicateReplayPolicy",
    "SideEffectPolicy",
    
    # Request and range
    "ReplayRequest",
    "ReplayRange",
    
    # Planning
    "ReplayPlan",
    
    # Runtime session and cursor
    "ReplaySessionState",
    "ReplaySession",
    "ReplayCursor",
    
    # Results
    "ReplayResult",
    
    # Admission
    "ReplayAdmissionResult",
    
    # Authority and storage protocols
    "ReplayAuthority",
    "ReplayStorage",
]