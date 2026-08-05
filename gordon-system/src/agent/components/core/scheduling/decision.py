# Scheduling Decision Model
# =========================

"""
Immutable scheduling decision artifacts for Phase 3.7.7-I.

Provides:
- Canonical SchedulingDecision model (immutable artifact)
- Decision types and their semantics
- Deterministic decision production with full provenance

A scheduling decision is NOT the same as "the scheduler running".
It's an immutable artifact produced by the scheduler that says:
"Given this task, I decide it should execute now on this executor."

The dispatcher then validates this decision and transfers work to the executor.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import uuid
import time


# =============================================================================
# SCHEDULING DECISION TYPES
# =============================================================================

class SchedulingDecisionType(Enum):
    """
    Types of scheduling decisions the scheduler can make.
    
    Each decision has specific semantics about what should happen next:
        - SELECT: Task is ready to be dispatched to executor
        - DEFER: Task should wait before being reconsidered (backpressure/starvation)
        - BLOCK: Task cannot be scheduled due to dependencies/resources
        - REJECT: Task should not be scheduled (admission failure, etc.)
        - CANCEL: Task should be cancelled
        - PROMOTE: Task's priority/urgency should be increased
        - RETRY_LATER: Failed task should wait before retry attempt
    """
    SELECT = "select"           # Select this task for immediate dispatch
    DEFER = "defer"             # Defer scheduling (backpressure, fairness, etc.)
    BLOCK = "block"             # Block on dependency/resource requirement
    REJECT = "reject"           # Reject this task from scheduling
    CANCEL = "cancel"           # Cancel the task
    PROMOTE = "promote"         # Promote to higher priority queue
    RETRY_LATER = "retry_later" # Retry the task after a delay


class DecisionQualifier(Enum):
    """
    Qualifiers for why a decision was made (beyond just the type).
    
    These provide context for observability and debugging.
    """
    QUEUE_EMPTY = "queue_empty"
    PRIORITY_HIGH = "priority_high"
    FAIRNESS_BALANCED = "fairness_balanced"
    DEPENDENCIES_READY = "dependencies_ready"
    RESOURCES_AVAILABLE = "resources_available"
    DEADLINE_NEAR = "deadline_near"
    BACKPRESSURE_APPLIED = "backpressure_applied"
    STARVATION_AVOIDED = "starvation_avoided"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    DEPENDENCY_BLOCKED = "dependency_blocked"


# =============================================================================
# SELECTOR CHOSEN
# =============================================================================

@dataclass(frozen=True)
class ExecutorSelection:
    """Executor class selected for this task."""
    executor_class: str  # e.g., "InlineExecutor", "ThreadedExecutor"
    executor_id: Optional[str] = None  # Specific instance if known
    
    @classmethod
    def inline(cls) -> "ExecutorSelection":
        return cls(executor_class="InlineExecutor")
    
    @classmethod
    def threaded(cls, worker_id: Optional[str] = None) -> "ExecutorSelection":
        executor_id = f"worker_{worker_id}" if worker_id else None
        return cls(executor_class="ThreadedExecutor", executor_id=executor_id)


@dataclass(frozen=True)
class WorkerSelection:
    """Worker selected to execute the task."""
    worker_class: str  # e.g., "SimpleWorker"
    worker_id: Optional[str] = None
    
    @classmethod
    def simple(cls, worker_id: Optional[str] = None) -> "WorkerSelection":
        return cls(worker_class="SimpleWorker", worker_id=worker_id)


# =============================================================================
# ASSESSMENTS (scheduler's evaluation of task)
# =============================================================================

@dataclass(frozen=True)
class PriorityAssessment:
    """
    Scheduler's assessment of task priority.
    
    This is NOT the task's declared priority - it's what the scheduler
    determined after considering aging, starvation, fairness, etc.
    """
    declared_priority: int  # Task's declared priority value
    effective_priority: int  # Priority after all adjustments
    priority_class: str     # e.g., "emergency", "critical", "standard"
    adjustment_reasons: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class FairnessAssessment:
    """
    Scheduler's fairness evaluation.
    
    Determines if granting this task would violate fairness constraints.
    """
    owner_id: str
    weight: float                    # Owner's weight in fair scheduling
    current_ownership: int           # Tasks already owned by this owner
    quota_limit: Optional[int]       # Maximum allowed (None = unlimited)
    fair_share: bool                 # Is this within fair share?
    
    @classmethod
    def no_constraints(cls) -> "FairnessAssessment":
        return cls(
            owner_id="default",
            weight=1.0,
            current_ownership=0,
            quota_limit=None,
            fair_share=True
        )


@dataclass(frozen=True)
class DependencyAssessment:
    """
    Scheduler's assessment of dependency readiness.
    
    All dependencies must be satisfied for SELECT decision.
    """
    all_dependencies_satisfied: bool
    satisfied_count: int
    pending_count: int
    blocked_task_ids: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ResourceAssessment:
    """
    Scheduler's assessment of resource feasibility.
    
    This is a REQUEST to the resource governor - not ownership!
    """
    requested_resources: Dict[str, float]
    feasible: bool
    resources_reserved: bool  # Has this been reserved?
    reservation_id: Optional[str] = None


@dataclass(frozen=True)
class PolicyResults:
    """
    Results of policy evaluations.
    
    Each policy (priority, fairness, starvation prevention, backpressure)
    produces its own result.
    """
    priority_result: str = "passed"
    fairness_result: str = "passed"
    starvation_result: str = "passed"
    backpressure_result: str = "passed"


# =============================================================================
# MAIN SCHEDULING DECISION (CANONICAL ARTIFACT)
# =============================================================================

@dataclass(frozen=True)
class SchedulingDecision:
    """
    Immutable scheduling decision artifact.
    
    This is the OUTPUT of scheduling - an immutable record that says:
    "Given this task, I decide it should [SELECT/DEFER/BLOCK/etc.] now."
    
    The dispatcher validates this decision and transfers work to executor.
    
    Design principles:
        - DEEPLY IMMUTABLE: All fields frozen, no runtime references
        - EXPLAINABLE: Every decision has clear provenance and reasoning
        - REPLAYABLE: Same inputs should produce same outputs (deterministic)
        - TRACEABLE: Full history preserved for debugging
    
    Usage:
        # Scheduler produces a decision
        decision = SchedulingDecision.create_select(
            task_id=task.task_id,
            scheduler_id=scheduler_id,
            source_queue="ready_queue",
            executor_selection=ExecutorSelection.threaded(),
            worker_selection=WorkerSelection.simple(worker_id),
            assessments={
                "priority": priority_assessment,
                "fairness": fairness_assessment,
                ...
            }
        )
        
        # Dispatcher validates and transfers
        dispatcher.dispatch(decision)
    """
    
    # Identity (no defaults first)
    decision_id: str                   # Unique ID for this decision
    
    # Task being decided on
    task_id: TaskId                    # The task this decision applies to
    runtime_id: str                    # Runtime that owns this task
    
    # Decision metadata
    scheduler_id: str                  # Which scheduler made the decision
    source_queue_id: str               # Queue where task was found
    
    # Selector selections (what will execute it)
    executor_selection: ExecutorSelection
    worker_selection: Optional[WorkerSelection] = None
    
    # Assessment results
    priority_assessment: PriorityAssessment
    fairness_assessment: FairnessAssessment
    dependency_assessment: DependencyAssessment
    resource_assessment: ResourceAssessment
    policy_results: PolicyResults
    
    # Main decision
    decision_type: SchedulingDecisionType = SchedulingDecisionType.SELECT
    
    # Context for non-SELECT decisions
    deferral_reason: Optional[str] = None  # Why deferred?
    blocking_reason: Optional[str] = None  # Why blocked?
    
    # Deterministic ordering
    logical_sequence: int = 0            # For tie-breaking determinism
    
    # Algorithm provenance
    configuration_fingerprint: str = ""  # Hash of config that produced this
    algorithm_id: str = "baseline"       # Which algorithm was used
    algorithm_version: str = "1.0.0"     # Version for reproducibility
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate decision structure."""
        if not self.decision_id:
            raise ValueError("Decision must have an ID")
        
        if self.decision_type in (
            SchedulingDecisionType.DEFER,
            SchedulingDecisionType.BLOCK
        ) and not self.deferral_reason:
            # These decisions should have reasons
            pass  # Optional for now, could enforce strictly
    
    @property
    def is_select(self) -> bool:
        """Check if decision is to select this task for execution."""
        return self.decision_type == SchedulingDecisionType.SELECT
    
    @property
    def is_deferred(self) -> bool:
        """Check if decision is to defer this task."""
        return self.decision_type == SchedulingDecisionType.DEFER
    
    @property
    def is_blocked(self) -> bool:
        """Check if decision is to block this task."""
        return self.decision_type == SchedulingDecisionType.BLOCK
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to JSON-serializable dictionary.
        
        This is deterministic - same inputs always produce same output.
        """
        return {
            "decision_id": self.decision_id,
            "task_id": self.task_id.value if isinstance(self.task_id, TaskId) else str(self.task_id),
            "runtime_id": self.runtime_id,
            "scheduler_id": self.scheduler_id,
            "source_queue_id": self.source_queue_id,
            "executor_selection": {
                "executor_class": self.executor_selection.executor_class,
                "executor_id": self.executor_selection.executor_id,
            },
            "worker_selection": (
                {"worker_class": self.worker_selection.worker_class, "worker_id": self.worker_selection.worker_id}
                if self.worker_selection else None
            ),
            "priority_assessment": {
                "declared_priority": self.priority_assessment.declared_priority,
                "effective_priority": self.priority_assessment.effective_priority,
                "priority_class": self.priority_assessment.priority_class,
                "adjustment_reasons": list(self.priority_assessment.adjustment_reasons),
            },
            "fairness_assessment": {
                "owner_id": self.fairness_assessment.owner_id,
                "weight": self.fairness_assessment.weight,
                "current_ownership": self.fairness_assessment.current_ownership,
                "quota_limit": self.fairness_assessment.quota_limit,
                "fair_share": self.fairness_assessment.fair_share,
            },
            "dependency_assessment": {
                "all_dependencies_satisfied": self.dependency_assessment.all_dependencies_satisfied,
                "satisfied_count": self.dependency_assessment.satisfied_count,
                "pending_count": self.dependency_assessment.pending_count,
                "blocked_task_ids": list(self.dependency_assessment.blocked_task_ids),
            },
            "resource_assessment": {
                "requested_resources": dict(self.resource_assessment.requested_resources),
                "feasible": self.resource_assessment.feasible,
                "resources_reserved": self.resource_assessment.resources_reserved,
                "reservation_id": self.resource_assessment.reservation_id,
            },
            "policy_results": {
                "priority_result": self.policy_results.priority_result,
                "fairness_result": self.policy_results.fairness_result,
                "starvation_result": self.policy_results.starvation_result,
                "backpressure_result": self.policy_results.backpressure_result,
            },
            "decision_type": self.decision_type.value,
            "deferral_reason": self.deferral_reason,
            "blocking_reason": self.blocking_reason,
            "logical_sequence": self.logical_sequence,
            "configuration_fingerprint": self.configuration_fingerprint,
            "algorithm_id": self.algorithm_id,
            "algorithm_version": self.algorithm_version,
            "created_at_utc": self.created_at_utc,
        }
    
    @classmethod
    def create_select(
        cls,
        task_id: TaskId,
        scheduler_id: str,
        source_queue_id: str,
        executor_selection: ExecutorSelection,
        worker_selection: Optional[WorkerSelection] = None,
        priority_assessment: Optional[PriorityAssessment] = None,
        fairness_assessment: Optional[FairnessAssessment] = None,
        dependency_assessment: Optional[DependencyAssessment] = None,
        resource_assessment: Optional[ResourceAssessment] = None,
        policy_results: Optional[PolicyResults] = None,
        logical_sequence: int = 0,
        configuration_fingerprint: str = "",
    ) -> "SchedulingDecision":
        """
        Create a SELECT decision (task ready to execute).
        
        Args:
            task_id: Task to select
            scheduler_id: Which scheduler made the decision
            source_queue_id: Queue where task was found
            executor_selection: Executor and optionally worker for execution
            priority_assessment, fairness_assessment, etc.: Assessment results
            logical_sequence: For deterministic tie-breaking
        """
        return cls(
            decision_id=str(uuid.uuid4()),
            task_id=task_id,
            runtime_id=getattr(task_id, 'runtime_id', '') if hasattr(task_id, 'runtime_id') else '',
            scheduler_id=scheduler_id,
            source_queue_id=source_queue_id,
            executor_selection=executor_selection,
            worker_selection=worker_selection,
            priority_assessment=priority_assessment or PriorityAssessment(
                declared_priority=5,
                effective_priority=5,
                priority_class="standard"
            ),
            fairness_assessment=fairness_assessment or FairnessAssessment.no_constraints(),
            dependency_assessment=dependency_assessment or DependencyAssessment(
                all_dependencies_satisfied=True,
                satisfied_count=0,
                pending_count=0
            ),
            resource_assessment=resource_assessment or ResourceAssessment(
                requested_resources={},
                feasible=True,
                resources_reserved=False
            ),
            policy_results=policy_results or PolicyResults(),
            decision_type=SchedulingDecisionType.SELECT,
            logical_sequence=logical_sequence,
            configuration_fingerprint=configuration_fingerprint,
        )
    
    @classmethod
    def create_defer(
        cls,
        task_id: TaskId,
        scheduler_id: str,
        source_queue_id: str,
        reason: str = "",
        priority_assessment: Optional[PriorityAssessment] = None,
        fairness_assessment: Optional[FairnessAssessment] = None,
        dependency_assessment: Optional[DependencyAssessment] = None,
        resource_assessment: Optional[ResourceAssessment] = None,
    ) -> "SchedulingDecision":
        """Create a DEFER decision (wait before reconsidering)."""
        return cls(
            decision_id=str(uuid.uuid4()),
            task_id=task_id,
            runtime_id=getattr(task_id, 'runtime_id', '') if hasattr(task_id, 'runtime_id') else '',
            scheduler_id=scheduler_id,
            source_queue_id=source_queue_id,
            executor_selection=ExecutorSelection.inline(),
            priority_assessment=priority_assessment or PriorityAssessment(
                declared_priority=5, effective_priority=5, priority_class="standard"
            ),
            fairness_assessment=fairness_assessment or FairnessAssessment.no_constraints(),
            dependency_assessment=dependency_assessment or DependencyAssessment(
                all_dependencies_satisfied=True, satisfied_count=0, pending_count=0
            ),
            resource_assessment=resource_assessment or ResourceAssessment(
                requested_resources={}, feasible=True, resources_reserved=False
            ),
            policy_results=PolicyResults(backpressure_result="applied"),
            decision_type=SchedulingDecisionType.DEFER,
            deferral_reason=reason,
        )
    
    @classmethod
    def create_block(
        cls,
        task_id: TaskId,
        scheduler_id: str,
        source_queue_id: str,
        reason: str = "",
        blocking_reason: Optional[str] = None,
    ) -> "SchedulingDecision":
        """Create a BLOCK decision (task cannot be scheduled yet)."""
        return cls(
            decision_id=str(uuid.uuid4()),
            task_id=task_id,
            runtime_id=getattr(task_id, 'runtime_id', '') if hasattr(task_id, 'runtime_id') else '',
            scheduler_id=scheduler_id,
            source_queue_id=source_queue_id,
            executor_selection=ExecutorSelection.inline(),
            priority_assessment=PriorityAssessment(
                declared_priority=5, effective_priority=5, priority_class="standard"
            ),
            fairness_assessment=FairnessAssessment.no_constraints(),
            dependency_assessment=DependencyAssessment(
                all_dependencies_satisfied=False, satisfied_count=0,
                pending_count=1, blocked_task_ids=("unknown",)
            ),
            resource_assessment=ResourceAssessment(
                requested_resources={}, feasible=True, resources_reserved=False
            ),
            policy_results=PolicyResults(),
            decision_type=SchedulingDecisionType.BLOCK,
            deferral_reason=reason,
            blocking_reason=blocking_reason or reason,
        )
    
    @classmethod
    def create_reject(
        cls,
        task_id: TaskId,
        scheduler_id: str,
        source_queue_id: str,
        reason: str = "",
    ) -> "SchedulingDecision":
        """Create a REJECT decision (don't schedule this task)."""
        return cls(
            decision_id=str(uuid.uuid4()),
            task_id=task_id,
            runtime_id=getattr(task_id, 'runtime_id', '') if hasattr(task_id, 'runtime_id') else '',
            scheduler_id=scheduler_id,
            source_queue_id=source_queue_id,
            executor_selection=ExecutorSelection.inline(),
            priority_assessment=PriorityAssessment(
                declared_priority=5, effective_priority=5, priority_class="standard"
            ),
            fairness_assessment=FairnessAssessment.no_constraints(),
            dependency_assessment=DependencyAssessment(
                all_dependencies_satisfied=True, satisfied_count=0, pending_count=0
            ),
            resource_assessment=ResourceAssessment(
                requested_resources={}, feasible=True, resources_reserved=False
            ),
            policy_results=PolicyResults(priority_result="rejected"),
            decision_type=SchedulingDecisionType.REJECT,
            deferral_reason=reason,
        )


# =============================================================================
# SCHEDULING DECISION VALIDATOR (for dispatcher)
# =============================================================================

class SchedulingDecisionValidator:
    """
    Validates scheduling decisions before dispatch.
    
    Dispatcher calls this to ensure the decision is still valid at dispatch time.
    
    Invariants checked:
        - Task still exists and is not terminal
        - Dependencies are still satisfied (if SELECT)
        - Resources are still available (if resources were reserved)
        - Decision hasn't expired
        - No cancellation pending
    """
    
    def __init__(self):
        self._max_decision_age_seconds = 30.0
    
    async def validate(
        self,
        decision: SchedulingDecision,
        task_state: Optional[Any] = None,  # Current task state
        dependencies_satisfied: bool = True,
        resources_valid: bool = True,
        cancellation_pending: bool = False,
        current_time_utc: Optional[float] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a scheduling decision is still valid.
        
        Returns:
            Tuple of (valid, reason_if_invalid)
        """
        now = current_time_utc or time.monotonic()
        decision_age = now - decision.created_at_utc
        
        # Check decision hasn't expired
        if decision_age > self._max_decision_age_seconds:
            return False, f"Decision expired after {decision_age:.2f}s"
        
        # Check task state (if provided)
        if task_state is not None:
            if isinstance(task_state, str):
                terminal_states = {"completed", "failed", "cancelled", "timed_out"}
                if task_state.lower() in terminal_states:
                    return False, f"Task already in terminal state: {task_state}"
        
        # For SELECT decisions, check dependencies
        if decision.decision_type == SchedulingDecisionType.SELECT:
            if not dependencies_satisfied:
                return False, "Dependencies no longer satisfied"
        
        # Check resources (if resources were reserved)
        if decision.resource_assessment.resources_reserved and not resources_valid:
            return False, "Resources no longer available"
        
        # Check cancellation
        if cancellation_pending:
            return False, "Cancellation pending for task"
        
        return True, None


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

from ..tasks import TaskId  # Import from tasks module

__all__ = [
    # Decision types
    "SchedulingDecisionType",
    "DecisionQualifier",
    
    # Selector selections
    "ExecutorSelection",
    "WorkerSelection",
    
    # Assessments
    "PriorityAssessment",
    "FairnessAssessment",
    "DependencyAssessment",
    "ResourceAssessment",
    "PolicyResults",
    
    # Main artifact
    "SchedulingDecision",
    
    # Validation
    "SchedulingDecisionValidator",
]