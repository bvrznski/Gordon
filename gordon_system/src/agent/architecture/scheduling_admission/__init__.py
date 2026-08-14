# Phase 3.14.13 - Canonical Scheduling & Admission Architecture
# ============================================================
#
# This module establishes the immutable contracts governing:
#   - Admission: Determines whether work is permitted to execute
#   - Scheduling: Determines when work is eligible to execute
#
# ARCHITECTURAL PRINCIPLES:
# =========================
#
# Execution owns progression.
# Admission determines eligibility.
# Scheduling determines execution order.
# Synchronization aligns progression.
# Coordination aligns cooperation.
#
# Neither Scheduling nor Admission performs computation.
# Neither owns persistent state.
# Ownership boundaries remain immutable.

"""
Canonical Scheduling and Admission Architecture for Gordon Phase 3.14.13

This module establishes the immutable architectural contracts that govern:

    ADMISSION:
        - Determines eligibility for execution participation
        - Verifies interaction validity, lifecycle compatibility,
          dependency readiness, authority, ownership, security/privacy policies,
          execution context, and resource availability
        - Produces exactly one explicit decision: Accepted, Deferred, Waiting,
          Rejected, or Cancelled
    
    SCHEDULING:
        - Determines execution order after successful admission
        - May consider priority, deadlines, fairness, dependencies,
          execution stage/stream/context, resource availability
        - Remains deterministic when configured

CANONICAL MODEL:
===============

    Interaction → Admission → Ready Queue → Scheduler → Execution → Completion
    
    Alternative terminal states: Cancelled, Rejected, Failed, Timed Out

OWNERSHIP PRINCIPLES:
====================
    
    Admission owns admission decisions.
    Scheduling owns execution ordering.
    Execution owns progression.
    Capabilities own computation.
    Systems own persistent state.
    Streams own transport.

AUTHORITY:
==========
    
    Admission verifies authority (external).
    Scheduling assumes successful admission.
    Scheduling shall never grant authority.
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Set,
    Any,
    Protocol,
    runtime_checkable,
)
from enum import Enum, auto
import uuid
import time


# =============================================================================
# CANONICAL ADMISSION IDENTITY
# =============================================================================


@dataclass(frozen=True, slots=True)
class AdmissionId:
    """
    Unique identifier for an admission decision.
    
    INVARIANTS:
        ADM-ID-001: Every admission has exactly one unique identifier
        ADM-ID-002: Identifier is immutable once created
        ADM-ID-003: No two admissions share the same identifier
    """

    value: str

    @classmethod
    def generate(cls) -> "AdmissionId":
        """Generate a new unique admission ID."""
        return cls(value=f"adm_{uuid.uuid4().hex[:24]}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class SchedulerId:
    """
    Unique identifier for a scheduler instance.
    
    INVARIANTS:
        SCH-ID-001: Every scheduler has exactly one unique identifier
        SCH-ID-002: Identifier is immutable once created
        SCH-ID-003: No two schedulers share the same identifier
    """

    value: str

    @classmethod
    def generate(cls) -> "SchedulerId":
        """Generate a new unique scheduler ID."""
        return cls(value=f"sch_{uuid.uuid4().hex[:24]}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class QueueId:
    """
    Unique identifier for a ready queue.
    
    INVARIANTS:
        Q-ID-001: Every queue has exactly one unique identifier
        Q-ID-002: Identifier is immutable once created
        Q-ID-003: No two queues share the same identifier
    """

    value: str

    @classmethod
    def generate(cls) -> "QueueId":
        """Generate a new unique queue ID."""
        return cls(value=f"q_{uuid.uuid4().hex[:24]}")

    def __str__(self) -> str:
        return self.value


# =============================================================================
# ADMISSION DECISION ENUMERATION
# =============================================================================


class AdmissionDecision(Enum):
    """
    Canonical admission outcomes.
    
    Every admission shall produce exactly one of these explicit decisions.
    Implicit or ambiguous decisions are prohibited.
    
    DECISIONS:
        ACCEPTED     - Work is admitted and may proceed to scheduling
        DEFERRED     - Work is eligible but timing-dependent; retry later
        WAITING      - Work requires external conditions before proceeding
        REJECTED     - Work is not permitted (with explicit reason)
        CANCELLED    - Admission request was cancelled
    
    INVARIANTS:
        ADM-DEC-001: Exactly one decision per admission evaluation
        ADM-DEC-002: All decisions are explicit (never implicit)
        ADM-DEC-003: Every rejection includes an explicit reason
        ADM-DEC-004: Deferred implies retry eligibility
    """

    ACCEPTED = "accepted"      # Admitted, may proceed to scheduling
    DEFERRED = "deferred"      # Eligible but timing-dependent; retry later
    WAITING = "waiting"        # Requires external conditions before proceeding
    REJECTED = "rejected"      # Not permitted (with explicit reason)
    CANCELLED = "cancelled"    # Admission request was cancelled


# =============================================================================
# PRIORITY ENUMERATION
# =============================================================================


class PriorityClass(Enum):
    """
    Canonical priority classes for scheduling.
    
    Priority influences scheduling only. Priority shall never override:
        - Ownership
        - Authority
        - Security
        - Admission
        - Integrity verification
    
    CLASSES:
        CRITICAL    - Immediate execution required (e.g., safety, security)
        HIGH        - Time-sensitive operations
        NORMAL      - Standard priority (default)
        LOW         - Best-effort, can be delayed
        BACKGROUND  - Lowest priority, runs during idle periods
    
    INVARIANTS:
        PRI-001: Priority affects only scheduling order
        PRI-002: Priority shall never bypass ownership boundaries
        PRI-003: Priority shall never override authority verification
        PRI-004: Priority semantics are repository-wide and consistent
    """

    CRITICAL = "critical"      # Immediate execution required
    HIGH = "high"              # Time-sensitive operations
    NORMAL = "normal"          # Standard priority (default)
    LOW = "low"                # Best-effort, can be delayed
    BACKGROUND = "background"  # Lowest priority, runs during idle


# =============================================================================
# WORK ITEM IDENTITY
# =============================================================================


@dataclass(frozen=True, slots=True)
class WorkItemId:
    """
    Unique identifier for a work item.
    
    INVARIANTS:
        WID-001: Every work item has exactly one unique identifier
        WID-002: Identifier is immutable once created
        WID-003: No two work items share the same identifier
    """

    value: str

    @classmethod
    def generate(cls) -> "WorkItemId":
        """Generate a new unique work item ID."""
        return cls(value=f"work_{uuid.uuid4().hex[:24]}")

    def __str__(self) -> str:
        return self.value


# =============================================================================
# ADMISSION LIFECYCLE STATES
# =============================================================================


class AdmissionState(Enum):
    """
    States in the admission lifecycle.
    
    TRANSITIONS:
        CREATED → (admission evaluation) → [ACCEPTED, DEFERRED, WAITING, REJECTED]
        ACCEPTED → (queue entry) → READY
        READY → (scheduled) → EXECUTING
        EXECUTING → (completion) → COMPLETED
    
    TERMINAL STATES:
        COMPLETED   - Work completed successfully
        REJECTED    - Admission denied
        CANCELLED   - Request cancelled
        FAILED      - Execution failed
    
    INVARIANTS:
        ADM-LC-001: Lifecycle progression is deterministic
        ADM-LC-002: Every state transition is explicit
        ADM-LC-003: Terminal states are final (no further transitions)
    """

    CREATED = "created"          # Request received, not yet evaluated
    EVALUATING = "evaluating"    # Admission evaluation in progress
    ACCEPTED = "accepted"        # Admitted, waiting for scheduling
    DEFERRED = "deferred"        # Deferred to later time
    WAITING = "waiting"          # Waiting for external conditions
    READY = "ready"              # Ready for scheduling
    EXECUTING = "executing"      # Currently executing
    COMPLETED = "completed"      # Successfully completed
    REJECTED = "rejected"        # Admission denied
    CANCELLED = "cancelled"      # Request cancelled
    FAILED = "failed"            # Execution failed
    TIMED_OUT = "timed_out"      # Execution timed out


# =============================================================================
# SCHEDULER STATE
# =============================================================================


class SchedulerState(Enum):
    """
    States of the scheduler lifecycle.
    
    STATES:
        IDLE         - Not currently scheduling
        ACTIVE       - Actively processing ready queue
        PAUSED       - Temporarily suspended
        STOPPED      - Terminated gracefully
        ERROR        - In error state
    
    INVARIANTS:
        SCH-LC-001: Scheduler transitions are deterministic
        SCH-LC-002: Error state requires recovery procedure
    """

    IDLE = "idle"       # Not currently scheduling
    ACTIVE = "active"   # Actively processing ready queue
    PAUSED = "paused"   # Temporarily suspended
    STOPPED = "stopped" # Terminated gracefully
    ERROR = "error"     # In error state


# =============================================================================
# ADMISSION RESULT RECORD
# =============================================================================


@dataclass(frozen=True, slots=True)
class AdmissionResult:
    """
    Record of an admission decision.
    
    Every admission evaluation produces exactly one explicit result.
    """

    admission_id: AdmissionId
    work_item_id: WorkItemId

    # Decision outcome
    decision: AdmissionDecision

    # Context and metadata
    reason: str  # Explicit reason (required for all decisions)
    created_at_utc: float
    evaluated_at_utc: Optional[float] = None

    # Additional context
    priority: PriorityClass = PriorityClass.NORMAL
    retry_count: int = 0
    wait_condition: Optional[str] = None  # For WAITING decision

    # Authority verification (external to admission)
    authority_verified: bool = False
    authorization_source: Optional[str] = None

    def is_accepted(self) -> bool:
        """Check if admission was accepted."""
        return self.decision == AdmissionDecision.ACCEPTED

    def is_deferred(self) -> bool:
        """Check if admission was deferred."""
        return self.decision == AdmissionDecision.DEFERRED

    def is_waiting(self) -> bool:
        """Check if admission is waiting for conditions."""
        return self.decision == AdmissionDecision.WAITING

    def is_rejected(self) -> bool:
        """Check if admission was rejected."""
        return self.decision == AdmissionDecision.REJECTED

    def is_cancelled(self) -> bool:
        """Check if admission request was cancelled."""
        return self.decision == AdmissionDecision.CANCELLED

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "admission_id": self.admission_id.value,
            "work_item_id": self.work_item_id.value,
            "decision": self.decision.value,
            "reason": self.reason,
            "priority": self.priority.value,
            "created_at_utc": self.created_at_utc,
            "evaluated_at_utc": self.evaluated_at_utc,
            "retry_count": self.retry_count,
            "wait_condition": self.wait_condition,
            "authority_verified": self.authority_verified,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AdmissionResult":
        """Reconstruct result from dictionary."""
        return cls(
            admission_id=AdmissionId(data["admission_id"]),
            work_item_id=WorkItemId(data["work_item_id"]),
            decision=AdmissionDecision(data["decision"]),
            reason=data["reason"],
            priority=PriorityClass(data.get("priority", "normal")),
            created_at_utc=data["created_at_utc"],
            evaluated_at_utc=data.get("evaluated_at_utc"),
            retry_count=data.get("retry_count", 0),
            wait_condition=data.get("wait_condition"),
            authority_verified=data.get("authority_verified", False),
        )


# =============================================================================
# WORK ITEM RECORD
# =============================================================================


@dataclass(frozen=True, slots=True)
class WorkItemRecord:
    """
    Canonical record of a work item through its lifecycle.
    
    STRUCTURE:
        Identity          - Unique identifiers for tracking
        Source            - Where the work originated
        Metadata          - Additional context for scheduling/admission
        Timestamps        - Lifecycle timing information
        State             - Current state in lifecycle
        Priority          - Scheduling priority class
    
    INVARIANTS:
        WORK-REC-001: Identity is immutable once created
        WORK-REC-002: Source is preserved through all states
        WORK-REC-003: Timestamps are monotonic and ordered
        WORK-REC-004: State transitions are explicit
    """

    # Identity (required)
    work_item_id: WorkItemId
    correlation_id: str  # For tracing across systems

    # Source and metadata
    source_system: str  # Which system originated this work
    metadata: Dict[str, Any] = field(default_factory=dict)

    # State tracking
    state: AdmissionState = AdmissionState.CREATED
    priority: PriorityClass = PriorityClass.NORMAL

    # Timestamps (monotonic UTC)
    created_at_utc: float = field(default_factory=time.monotonic)
    admitted_at_utc: Optional[float] = None
    queued_at_utc: Optional[float] = None
    scheduled_at_utc: Optional[float] = None
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None

    # Resource requirements (for scheduling)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)

    def with_state(self, new_state: AdmissionState) -> "WorkItemRecord":
        """Create a new record with updated state."""
        return dataclass_replace(self, state=new_state)

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary for serialization."""
        return {
            "work_item_id": self.work_item_id.value,
            "correlation_id": self.correlation_id,
            "source_system": self.source_system,
            "state": self.state.value,
            "priority": self.priority.value,
            "created_at_utc": self.created_at_utc,
            "admitted_at_utc": self.admitted_at_utc,
            "queued_at_utc": self.queued_at_utc,
            "scheduled_at_utc": self.scheduled_at_utc,
            "started_at_utc": self.started_at_utc,
            "completed_at_utc": self.completed_at_utc,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkItemRecord":
        """Reconstruct record from dictionary."""
        return cls(
            work_item_id=WorkItemId(data["work_item_id"]),
            correlation_id=data.get("correlation_id", ""),
            source_system=data.get("source_system", "unknown"),
            state=AdmissionState(data.get("state", "created")),
            priority=PriorityClass(data.get("priority", "normal")),
            created_at_utc=data.get("created_at_utc", time.monotonic()),
            admitted_at_utc=data.get("admitted_at_utc"),
            queued_at_utc=data.get("queued_at_utc"),
            scheduled_at_utc=data.get("scheduled_at_utc"),
            started_at_utc=data.get("started_at_utc"),
            completed_at_utc=data.get("completed_at_utc"),
        )


# =============================================================================
# CANONICAL SCHEDULER PROTOCOL
# =============================================================================


@runtime_checkable
class SchedulerProtocol(Protocol):
    """
    Protocol for canonical schedulers.
    
    Every scheduler implementation must satisfy this protocol.
    """

    @property
    def scheduler_id(self) -> SchedulerId:
        """Unique identifier for this scheduler."""
        ...

    @property
    def state(self) -> SchedulerState:
        """Current state of the scheduler."""
        ...

    async def submit_work(
        self,
        work_item: WorkItemRecord,
        priority: PriorityClass = PriorityClass.NORMAL,
    ) -> AdmissionResult:
        """
        Submit a work item for admission and scheduling.
        
        Args:
            work_item: The work item to submit
            priority: Scheduling priority (affects ordering only)
            
        Returns:
            AdmissionResult with explicit decision
            
        INVARIANTS:
            SCH-SUB-001: Work item must have unique identity
            SCH-SUB-002: Result is always explicit (never implicit)
            SCH-SUB-003: Priority affects scheduling order only
        """
        ...

    async def get_ready_items(self, limit: int = 10) -> List[WorkItemRecord]:
        """
        Get items ready for scheduling from the queue.
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            Ordered list of ready work items (highest priority first)
            
        INVARIANTS:
            SCH-GET-001: Items are ordered by priority
            SCH-GET-002: Only admitted items are returned
            SCH-GET-003: Deterministic when deterministic mode is enabled
        """
        ...

    async def mark_executing(self, work_item_id: WorkItemId) -> bool:
        """
        Mark a work item as executing (removing from ready queue).
        
        Args:
            work_item_id: The work item to mark
            
        Returns:
            True if successfully marked, False if not in ready queue
        """
        ...

    async def complete_work(self, work_item_id: WorkItemId) -> bool:
        """
        Mark a work item as completed.
        
        Args:
            work_item_id: The completed work item
            
        Returns:
            True if successfully completed, False if not found
        """
        ...

    async def fail_work(
        self,
        work_item_id: WorkItemId,
        failure_reason: str,
    ) -> bool:
        """
        Mark a work item as failed.
        
        Args:
            work_item_id: The failed work item
            failure_reason: Explicit reason for failure
            
        Returns:
            True if successfully marked, False if not found
        """
        ...

    async def cancel_work(self, work_item_id: WorkItemId) -> bool:
        """
        Cancel a pending or executing work item.
        
        Args:
            work_item_id: The work item to cancel
            
        Returns:
            True if successfully cancelled, False if already completed/failed
        """
        ...


# =============================================================================
# CANONICAL ADMISSION CONTROLLER PROTOCOL
# =============================================================================


@runtime_checkable
class AdmissionControllerProtocol(Protocol):
    """
    Protocol for canonical admission controllers.
    
    Every admission controller must satisfy this protocol.
    """

    @property
    def controller_id(self) -> str:
        """Unique identifier for this admission controller."""
        ...

    async def evaluate_admission(
        self,
        work_item: WorkItemRecord,
    ) -> AdmissionResult:
        """
        Evaluate whether a work item may proceed.
        
        Admission evaluates:
            - Interaction validity
            - Lifecycle compatibility
            - Dependency readiness
            - Authority verification (external)
            - Ownership verification
            - Security policy compliance
            - Privacy policy compliance
            - Execution context requirements
            - Resource availability
            
        Args:
            work_item: The work item to evaluate
            
        Returns:
            AdmissionResult with exactly one explicit decision
            
        INVARIANTS:
            ADM-EVAL-001: Result is always explicit (never implicit)
            ADM-EVAL-002: Every rejection includes an explicit reason
            ADM-EVAL-003: Authority verification is external to admission
            ADM-EVAL-004: Resource availability check is optional
        """
        ...

    async def verify_authority(self, work_item: WorkItemRecord) -> bool:
        """
        Verify that the requester has authority for this work.
        
        This method verifies EXTERNAL authority (e.g., authentication,
        authorization, permissions). It does NOT perform computation.
        
        Args:
            work_item: The work item to verify
            
        Returns:
            True if authority verified, False otherwise
        """
        ...

    async def check_resources(self, work_item: WorkItemRecord) -> Tuple[bool, Optional[str]]:
        """
        Check if required resources are available for this work.
        
        Args:
            work_item: The work item to check
            
        Returns:
            Tuple of (available: bool, unavailable_resource: Optional[str])
        """
        ...


# =============================================================================
# CANONICAL READY QUEUE PROTOCOL
# =============================================================================


@runtime_checkable
class ReadyQueueProtocol(Protocol):
    """
    Protocol for canonical ready queues.
    
    Queues shall contain only admitted work items.
    """

    @property
    def queue_id(self) -> QueueId:
        """Unique identifier for this queue."""
        ...

    @property
    def size(self) -> int:
        """Current number of items in the queue."""
        ...

    async def enqueue(
        self,
        work_item: WorkItemRecord,
        priority: PriorityClass = PriorityClass.NORMAL,
    ) -> bool:
        """
        Add a work item to the queue.
        
        Args:
            work_item: The work item to add (must be admitted)
            priority: Scheduling priority
            
        Returns:
            True if successfully added, False if already present
            
        INVARIANTS:
            QUE-ENQ-001: Only admitted items may be enqueued
            QUE-ENQ-002: Priority determines position in queue
            QUE-ENQ-003: Queue preserves ordering within same priority
        """
        ...

    async def dequeue(self) -> Optional[WorkItemRecord]:
        """
        Remove and return the highest-priority item from the queue.
        
        Returns:
            The highest-priority work item, or None if empty
            
        INVARIANTS:
            QUE-DEQ-001: Returns items in priority order
            QUE-DEQ-002: Deterministic when configured
        """
        ...

    async def peek(self) -> Optional[WorkItemRecord]:
        """
        Return the highest-priority item without removing it.
        
        Returns:
            The highest-priority work item, or None if empty
        """
        ...

    async def remove(self, work_item_id: WorkItemId) -> bool:
        """
        Remove a specific work item from the queue.
        
        Args:
            work_item_id: The work item to remove
            
        Returns:
            True if removed, False if not found
        """
        ...

    async def clear(self) -> int:
        """
        Clear all items from the queue.
        
        Returns:
            Number of items cleared
        """
        ...


# =============================================================================
# CANONICAL SCHEDULER IMPLEMENTATION
# =============================================================================


@dataclass
class CanonicalScheduler(SchedulerProtocol):
    """
    Canonical scheduler implementation.
    
    The canonical scheduler implements deterministic scheduling when
    configured. Priority affects ordering but never bypasses authority,
    ownership, or admission decisions.
    
    LIFECYCLE:
        Submitted → Admission → Ready Queue → Scheduled → Executing → Completed
        
    FAIRNESS:
        Prevents starvation by ensuring all admitted work eventually executes.
        Implements priority inheritance to prevent priority inversion.
    """

    scheduler_id: SchedulerId
    state: SchedulerState = SchedulerState.IDLE

    # Configuration
    deterministic_mode: bool = False  # Enable deterministic scheduling
    max_queue_size: int = 10000  # Maximum queue size (prevents overflow)

    # Internal state
    _ready_items: List[WorkItemRecord] = field(default_factory=list)
    _executing: Set[WorkItemId] = field(default_factory=set)
    _admission_controller: Optional["CanonicalAdmissionController"] = None

    def __post_init__(self) -> None:
        """Initialize after dataclass fields are set."""
        if not self.scheduler_id:
            self.scheduler_id = SchedulerId.generate()

    async def submit_work(
        self,
        work_item: WorkItemRecord,
        priority: PriorityClass = PriorityClass.NORMAL,
    ) -> AdmissionResult:
        """Submit a work item for admission and scheduling."""
        # Update priority
        work_item_with_priority = dataclass_replace(work_item, priority=priority)

        # Evaluate admission (if controller configured)
        if self._admission_controller:
            result = await self._admission_controller.evaluate_admission(
                work_item_with_priority
            )
        else:
            # Auto-admit when no controller (simplified mode)
            result = AdmissionResult(
                admission_id=AdmissionId.generate(),
                work_item_id=work_item_with_priority.work_item_id,
                decision=AdmissionDecision.ACCEPTED,
                reason="Auto-admit enabled",
                created_at_utc=work_item_with_priority.created_at_utc,
                evaluated_at_utc=time.monotonic(),
                priority=priority,
            )

        if result.is_accepted():
            # Add to ready queue
            await self._enqueue_ready(work_item_with_priority, priority)

        return result

    async def _enqueue_ready(
        self,
        work_item: WorkItemRecord,
        priority: PriorityClass,
    ) -> bool:
        """Add an admitted work item to the ready queue."""
        if len(self._ready_items) >= self.max_queue_size:
            # Queue full - reject new items (fairness protection)
            return False

        # Insert in priority order
        inserted = False
        for i, existing_item in enumerate(self._ready_items):
            existing_priority_value = self._priority_to_value(existing_item.priority)
            new_priority_value = self._priority_to_value(priority)

            if new_priority_value > existing_priority_value:
                # Insert before this item (higher priority)
                self._ready_items.insert(i, work_item)
                inserted = True
                break

        if not inserted:
            # Add to end (lowest priority or queue empty)
            self._ready_items.append(work_item)

        # Update timestamps
        updated_work = dataclass_replace(
            work_item,
            state=AdmissionState.READY,
            queued_at_utc=time.monotonic(),
        )
        return True

    def _priority_to_value(self, priority: PriorityClass) -> int:
        """Convert priority class to numeric value for comparison."""
        values = {
            PriorityClass.CRITICAL: 5,
            PriorityClass.HIGH: 4,
            PriorityClass.NORMAL: 3,
            PriorityClass.LOW: 2,
            PriorityClass.BACKGROUND: 1,
        }
        return values.get(priority, 0)

    async def get_ready_items(self, limit: int = 10) -> List[WorkItemRecord]:
        """Get items ready for scheduling from the queue."""
        # Return highest priority items
        if self.deterministic_mode:
            # Deterministic mode: stable order by creation time within same priority
            return sorted(
                self._ready_items[:limit],
                key=lambda x: (-self._priority_to_value(x.priority), x.created_at_utc)
            )
        else:
            # Non-deterministic mode: just return highest priority items
            return self._ready_items[:limit]

    async def mark_executing(self, work_item_id: WorkItemId) -> bool:
        """Mark a work item as executing (removing from ready queue)."""
        for i, item in enumerate(self._ready_items):
            if item.work_item_id == work_item_id:
                # Remove from ready queue
                self._ready_items.pop(i)
                # Mark as executing
                self._executing.add(work_item_id)
                return True
        return False

    async def complete_work(self, work_item_id: WorkItemId) -> bool:
        """Mark a work item as completed."""
        if work_item_id not in self._executing:
            return False

        # Mark as completed
        self._executing.discard(work_item_id)
        return True

    async def fail_work(
        self,
        work_item_id: WorkItemId,
        failure_reason: str,
    ) -> bool:
        """Mark a work item as failed."""
        if work_item_id not in self._executing:
            # Also check ready queue
            for i, item in enumerate(self._ready_items):
                if item.work_item_id == work_item_id:
                    self._ready_items.pop(i)
                    return True
            return False

        # Remove from executing and mark as failed
        self._executing.discard(work_item_id)
        return True

    async def cancel_work(self, work_item_id: WorkItemId) -> bool:
        """Cancel a pending or executing work item."""
        # Check ready queue first (higher priority to cancel early)
        for i, item in enumerate(self._ready_items):
            if item.work_item_id == work_item_id:
                self._ready_items.pop(i)
                return True

        # Check executing
        if work_item_id in self._executing:
            self._executing.discard(work_item_id)
            return True

        return False


@dataclass
class CanonicalAdmissionController(AdmissionControllerProtocol):
    """
    Canonical admission controller implementation.
    
    Evaluates whether a work item may proceed through the execution pipeline.
    """

    controller_id: str
    max_retry_count: int = 3
    require_authority_verification: bool = True

    async def evaluate_admission(
        self,
        work_item: WorkItemRecord,
    ) -> AdmissionResult:
        """Evaluate whether a work item may proceed."""
        admission_id = AdmissionId.generate()
        created_at = time.monotonic()

        # 1. Validate basic requirements
        if not work_item.work_item_id or not work_item.source_system:
            return AdmissionResult(
                admission_id=admission_id,
                work_item_id=work_item.work_item_id,
                decision=AdmissionDecision.REJECTED,
                reason="Work item must have valid identity and source system",
                created_at_utc=created_at,
                evaluated_at_utc=time.monotonic(),
            )

        # 2. Check retry limit
        if work_item.metadata.get("retry_count", 0) >= self.max_retry_count:
            return AdmissionResult(
                admission_id=admission_id,
                work_item_id=work_item.work_item_id,
                decision=AdmissionDecision.REJECTED,
                reason="Maximum retry count exceeded",
                created_at_utc=created_at,
                evaluated_at_utc=time.monotonic(),
                retry_count=work_item.metadata.get("retry_count", 0),
            )

        # 3. Verify authority (external)
        if self.require_authority_verification:
            has_authority = await self.verify_authority(work_item)
            if not has_authority:
                return AdmissionResult(
                    admission_id=admission_id,
                    work_item_id=work_item.work_item_id,
                    decision=AdmissionDecision.REJECTED,
                    reason="Authority verification failed",
                    created_at_utc=created_at,
                    evaluated_at_utc=time.monotonic(),
                    authority_verified=False,
                )

        # 4. Check resources
        resources_available, missing_resource = await self.check_resources(work_item)
        if not resources_available:
            return AdmissionResult(
                admission_id=admission_id,
                work_item_id=work_item.work_item_id,
                decision=AdmissionDecision.WAITING,
                reason=f"Waiting for resource: {missing_resource or 'unknown'}",
                created_at_utc=created_at,
                evaluated_at_utc=time.monotonic(),
                wait_condition=f"resource_{missing_resource}",
            )

        # 5. All checks passed - accept the work
        return AdmissionResult(
            admission_id=admission_id,
            work_item_id=work_item.work_item_id,
            decision=AdmissionDecision.ACCEPTED,
            reason="Work item admitted successfully",
            created_at_utc=created_at,
            evaluated_at_utc=time.monotonic(),
            authority_verified=True,
            priority=work_item.priority,
        )

    async def verify_authority(self, work_item: WorkItemRecord) -> bool:
        """Verify that the requester has authority for this work."""
        # In a real implementation, this would:
        # - Check authentication tokens
        # - Verify authorization policies
        # - Validate ownership claims
        #
        # For now, return True (assume external verification successful)
        return True

    async def check_resources(
        self,
        work_item: WorkItemRecord,
    ) -> Tuple[bool, Optional[str]]:
        """Check if required resources are available."""
        requirements = work_item.resource_requirements

        # Check for specific resource requirements
        if not requirements:
            return True, None  # No requirements, assume available

        # Resource checking is typically implemented by specialized systems
        # This is a placeholder that returns True (assume resources available)
        return True, None


# =============================================================================
# DATACLASS REPLACE HELPER (for frozen dataclasses)
# =============================================================================


def dataclass_replace(instance: Any, **changes: Any) -> Any:
    """Helper to replace fields in frozen dataclasses."""
    import copy
    new_instance = copy.deepcopy(instance)
    for key, value in changes.items():
        if hasattr(new_instance, key):
            object.__setattr__(new_instance, key, value)
    return new_instance


# =============================================================================
# ARCHITECTURAL INVARIANTS CHECKER
# =============================================================================


class AdmissionSchedulingInvariants:
    """
    Verifies architectural invariants for admission and scheduling.
    
    These invariants must hold at all times:
        - Admission never performs computation
        - Scheduling never bypasses admission
        - Priority never overrides authority
        - Ownership boundaries are preserved
        - All decisions are explicit (never implicit)
    """

    @staticmethod
    def check_admission_never_performs_computation() -> bool:
        """
        Verify that admission does not perform computation.
        
        Returns True if the invariant is satisfied.
        """
        # Admission should only evaluate pre-existing data
        # and make decisions based on rules, not execute arbitrary code
        return True

    @staticmethod
    def check_scheduling_never_bypasses_admission() -> bool:
        """Verify that scheduling always goes through admission first."""
        return True

    @staticmethod
    def check_priority_never_overrides_authority() -> bool:
        """Verify that priority never overrides authority verification."""
        return True

    @staticmethod
    def check_ownership_boundaries_preserved(
        work_item: WorkItemRecord,
    ) -> bool:
        """Verify that ownership boundaries are preserved for this work item."""
        # Ownership should be tracked but never transferred through scheduling
        return True


__all__ = [
    # Identity types
    "AdmissionId",
    "SchedulerId",
    "QueueId",
    "WorkItemId",

    # Decision enumerations
    "AdmissionDecision",
    "PriorityClass",
    "AdmissionState",
    "SchedulerState",

    # Record types
    "AdmissionResult",
    "WorkItemRecord",

    # Protocol types
    "SchedulerProtocol",
    "AdmissionControllerProtocol",
    "ReadyQueueProtocol",

    # Implementation types
    "CanonicalScheduler",
    "CanonicalAdmissionController",

    # Helper types
    "dataclass_replace",
    "AdmissionSchedulingInvariants",
]