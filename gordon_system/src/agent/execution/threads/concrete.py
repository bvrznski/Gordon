# Concrete Execution Thread Types
# ================================
#
# PHASE 3.10.9 - First production-quality execution taxonomy implementation.
#
# This module implements the canonical semantic thread types:
#     - ConversationThread: Continuous interaction with external participants
#     - TaskThread: Bounded semantic objectives (implement, refactor, analyze)
#     - MonitoringThread: Durable observation obligations over time
#     - InternalThread: Autonomous internally initiated work

"""
Concrete Execution Thread Types for Gordon.

Each thread type implements the canonical ownership model:

    Thread: owns identity, continuity, semantic state, lifecycle intent
    Loop: owns continuation policy (which cycle to select next)
    Cycle: owns finite semantic pass with terminal outcome
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import uuid

# Import base types from threads for canonical identity
from .identity import ThreadId, ThreadName, ThreadMetadata
from .lifecycle import ThreadLifecycleState, ThreadLifecycleReason
from .state import ThreadSemanticState, BehavioralMode, ThreadObjective
from .relationships import ParentChildRelationship, ThreadRelationship
from .delta import ThreadSemanticDelta

# Import loop types from loops package for type annotations
from ..loops import LoopKind, BehavioralMode as LoopBehavioralMode


# =============================================================================
# ConversationThread
# =============================================================================

class ConversationPurpose(Enum):
    """
    Semantic purposes of a conversation.
    
    This defines the high-level objective of the conversation.
    """
    INFORMATION_REQUEST = "information_request"
    TASK_ASSIGNMENT = "task_assignment"
    CLARIFICATION = "clarification"
    FEEDBACK = "feedback"
    PLANNING_DISCUSSION = "planning_discussion"
    STATUS_UPDATE = "status_update"
    DELEGATION = "delegation"
    GENERAL_CONVERSATION = "general_conversation"


@dataclass(frozen=True)
class ConversationParticipant:
    """Information about a conversation participant."""
    role: str  # e.g., "user", "external_system", "other_agent"
    identity: Optional[str] = None
    name: Optional[str] = None


@dataclass(frozen=True)
class ConversationState:
    """
    Semantic state owned by ConversationThread.
    
    This is the persistent semantic state of a conversation, including:
        - Purpose and context
        - Participant information  
        - Accepted context (what's been acknowledged as understood)
        - Unresolved questions
        - Commitments and decisions made
        - Dialogue history references
    """
    purpose: ConversationPurpose
    participants: Tuple[ConversationParticipant, ...] = ()
    
    # Conversation progress
    accepted_context: Dict[str, Any] = field(default_factory=dict)
    unresolved_questions: List[str] = field(default_factory=list)
    accepted_commitments: List[str] = field(default_factory=list)
    accepted_decisions: List[str] = field(default_factory=list)
    
    # Dialogue references (for context continuity)
    dialogue_history_references: List[str] = field(default_factory=list)
    
    # Child task delegation
    delegated_child_tasks: List[str] = field(default_factory=list)  # TaskThread IDs
    
    # Completion criteria
    completion_criteria_met: bool = False


@dataclass(frozen=True)
class ConversationThread:
    """
    Represents one continuous interaction with an external participant.
    
    A ConversationThread survives multiple user messages, clarification requests,
    delegated tasks and responses. It owns conversational continuity.
    
    It does NOT own:
        - Planning algorithms (belongs to PlanningLoop when active)
        - Response generation (belongs to Capabilities invoked by cycles)
        - Execution policy (belongs to Loop)
    
    Lifecycle transitions:
        CREATED → ACTIVE → WAITING_FOR_PARTICIPANT → RESUMED
        ↓
        DELEGATING_TASKS → COMPLETING → COMPLETED
    
    Typical Loops:
        ConversationLoop, ClarificationLoop, WaitingLoop
    """
    
    # Identity (immutable - no defaults)
    id: ThreadId
    name: str  # Human-readable conversation identifier
    
    # Purpose and participants
    purpose: ConversationPurpose = ConversationPurpose.GENERAL_CONVERSATION
    participants: Tuple[ConversationParticipant, ...] = ()
    
    # State ownership (semantic continuity)
    state: ConversationState = field(default_factory=lambda: ConversationState(purpose=ConversationPurpose.GENERAL_CONVERSATION))
    
    # Lifecycle state (from threads.lifecycle - owned by Thread, not Core)
    lifecycle_state: ThreadLifecycleState = ThreadLifecycleState.CREATED
    
    # Active components (at most one each)
    active_loop_id: Optional[str] = None
    active_cycle_id: Optional[str] = None
    
    # Parent-child relationships (optional)
    parent_thread_id: Optional[str] = None
    child_thread_ids: Tuple[str, ...] = ()
    
    # Revision tracking
    semantic_revision: int = 0
    
    # Terminal state tracking
    terminal_reason: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        purpose: ConversationPurpose,
        participants: Tuple[ConversationParticipant, ...] = (),
        name: Optional[str] = None,
        parent_thread_id: Optional[str] = None,
    ) -> "ConversationThread":
        """
        Create a new ConversationThread.
        
        Args:
            purpose: The semantic purpose of this conversation
            participants: Participants in the conversation (user, external systems)
            name: Human-readable identifier (auto-generated if not provided)
            parent_thread_id: Parent thread if this is delegated work
        """
        thread_name = name or f"conversation-{uuid.uuid4().hex[:12]}"
        
        return cls(
            id=ThreadId(value=str(uuid.uuid4())),
            name=thread_name,
            purpose=purpose,
            participants=participants,
            parent_thread_id=parent_thread_id,
        )
    
    def with_state(self, new_state: ConversationState) -> "ConversationThread":
        """Create new thread instance with updated state."""
        return dataclass_replace(self, state=new_state)
    
    def increment_revision(self) -> "ConversationThread":
        """Increment semantic revision and return new instance."""
        return dataclass_replace(self, semantic_revision=self.semantic_revision + 1)
    
    def to_conversation_snapshot(self) -> "ConversationSnapshot":
        """Create immutable snapshot for Loop evaluation."""
        return ConversationSnapshot.from_thread(self)


@dataclass(frozen=True)
class ConversationSnapshot:
    """
    Read-only snapshot of ConversationThread state for Loop evaluation.
    
    Contains only semantic information needed for behavioral decisions.
    Does NOT contain runtime scheduling details or Core implementation references.
    """
    id: str
    name: str
    purpose: ConversationPurpose
    
    # Semantic state
    participants: Tuple[ConversationParticipant, ...] = ()
    accepted_context: Dict[str, Any] = field(default_factory=dict)
    unresolved_questions: List[str] = field(default_factory=list)
    accepted_commitments: List[str] = field(default_factory=list)
    accepted_decisions: List[str] = field(default_factory=list)
    
    # Progress
    dialogue_history_references: List[str] = field(default_factory=list)
    delegated_child_tasks: List[str] = field(default_factory=list)
    completion_criteria_met: bool = False
    
    # Lifecycle state (semantic intent)
    lifecycle_state: ThreadLifecycleState = ThreadLifecycleState.CREATED
    
    # Active components (optional) - at most one each
    active_loop_id: Optional[str] = None
    active_cycle_id: Optional[str] = None
    
    # Relationships
    parent_thread_id: Optional[str] = None
    child_thread_ids: Tuple[str, ...] = ()
    
    # Revision tracking
    semantic_revision: int = 0
    terminal_reason: Optional[str] = None
    
    @classmethod
    def from_thread(cls, thread: ConversationThread) -> "ConversationSnapshot":
        """Create snapshot from a ConversationThread."""
        return cls(
            id=thread.id.value,
            name=thread.name,
            purpose=thread.purpose,
            participants=thread.participants,
            accepted_context=thread.state.accepted_context,
            unresolved_questions=list(thread.state.unresolved_questions),
            accepted_commitments=list(thread.state.accepted_commitments),
            accepted_decisions=list(thread.state.accepted_decisions),
            dialogue_history_references=list(thread.state.dialogue_history_references),
            delegated_child_tasks=list(thread.state.delegated_child_tasks),
            completion_criteria_met=thread.state.completion_criteria_met,
            lifecycle_state=thread.lifecycle_state,
            active_loop_id=thread.active_loop_id,
            active_cycle_id=thread.active_cycle_id,
            parent_thread_id=thread.parent_thread_id,
            child_thread_ids=thread.child_thread_ids,
            semantic_revision=thread.semantic_revision,
            terminal_reason=thread.terminal_reason,
        )


# =============================================================================
# TaskThread
# =============================================================================

class TaskStatus(Enum):
    """
    Semantic status of a TaskThread.
    
    These describe the lifecycle stage of task execution:
        - DEFINING: Objective is being formalized
        - PLANNING: Work breakdown and plan creation
        - EXECUTING: Plan is being executed
        - EVALUATING: Results are being evaluated against criteria
        - RECOVERING: Recovering from failed execution
        - REPORTING: Producing final output or summary
        - COMPLETING: Finalization before termination
    """
    DEFINING = "defining"
    PLANNING = "planning"
    EXECUTING = "executing"
    EVALUATING = "evaluating"
    RECOVERING = "recovering"
    REPORTING = "reporting"
    COMPLETING = "completing"


@dataclass(frozen=True)
class TaskConstraints:
    """
    Constraints that must be satisfied during task execution.
    
    These are hard and soft constraints that define what constitutes
    successful completion of the task.
    """
    time_budget_seconds: Optional[int] = None  # Maximum execution time
    resource_limits: Dict[str, int] = field(default_factory=dict)  # Resource constraints
    quality_threshold: float = 0.8  # Minimum acceptance threshold (0.0-1.0)
    required_outcome_types: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class TaskPlan:
    """
    Accepted executable plan for a task.
    
    This is the plan that has been selected and committed to execution.
    It contains all necessary steps to achieve the objective.
    """
    plan_id: str
    steps: List[str] = field(default_factory=list)  # Step descriptions
    dependencies: Dict[str, List[str]] = field(default_factory=dict)  # step_name -> dependencies
    assumptions: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class TaskProgress:
    """
    Progress tracking for a TaskThread.
    
    This tracks execution progress, not semantic state changes.
    """
    current_step_index: int = 0
    steps_completed: int = 0
    total_steps: int = 0
    
    # Execution history (for recovery and audit)
    completed_executions: List[str] = field(default_factory=list)
    failed_executions: List[str] = field(default_factory=list)
    
    # Artifacts produced
    produced_artifacts: List[str] = field(default_factory=list)
    
    # Progress metrics
    confidence: float = 0.0  # Confidence in completion (0.0-1.0)


@dataclass(frozen=True)
class TaskState:
    """
    Semantic state owned by TaskThread.
    
    This is the persistent semantic state of a task, including:
        - Objective and definition
        - Accepted plan
        - Constraints
        - Progress tracking
        - History of execution attempts
        - Artifacts produced
        - Unresolved blockers
    """
    objective: str  # The semantic objective being pursued
    
    # Plan and commitment
    accepted_plan: Optional[TaskPlan] = None
    constraints: TaskConstraints = field(default_factory=TaskConstraints)
    
    # Progress
    status: TaskStatus = TaskStatus.DEFINING
    progress: TaskProgress = field(default_factory=TaskProgress)
    
    # Semantic history (for continuity across recovery)
    execution_history: List[str] = field(default_factory=list)  # Summary of what happened
    produced_artifacts: Dict[str, Any] = field(default_factory=dict)  # ID → artifact data
    
    # Current state
    unresolved_blockers: List[str] = field(default_factory=list)
    
    # Completion criteria
    completion_criteria_met: bool = False


@dataclass(frozen=True)
class TaskThread:
    """
    Represents one bounded semantic objective.
    
    Examples:
        - implement subsystem
        - refactor package  
        - analyze repository
        - prepare documentation
        - investigate runtime failure
        - generate report
    
    A TaskThread owns work continuity. It survives many execution iterations,
    planning revisions, recovery attempts, and interruptions.
    
    It does NOT own:
        - Planning policy (belongs to PlanningLoop when active)
        - Execution policy (belongs to Loop)
    
    Lifecycle transitions:
        CREATED → PLANNING → EXECUTING → RECOVERING → EVALUATING
        ↓
        REPORTING → COMPLETING → COMPLETED
    
    Typical Loops:
        TaskLoop, PlanningLoop, RecoveryLoop
    """
    
    # Identity (immutable - no defaults)
    id: ThreadId
    name: str  # Human-readable task identifier
    
    # Objective and state
    objective: str = ""
    state: TaskState = field(default_factory=TaskState)
    
    # Lifecycle state (semantic intent)
    lifecycle_state: ThreadLifecycleState = ThreadLifecycleState.CREATED
    
    # Active components (at most one each)
    active_loop_id: Optional[str] = None
    active_cycle_id: Optional[str] = None
    
    # Parent-child relationships (optional)
    parent_thread_id: Optional[str] = None
    child_thread_ids: Tuple[str, ...] = ()
    
    # Revision tracking
    semantic_revision: int = 0
    
    # Terminal state tracking
    terminal_reason: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        objective: str,
        name: Optional[str] = None,
        parent_thread_id: Optional[str] = None,
    ) -> "TaskThread":
        """
        Create a new TaskThread.
        
        Args:
            objective: The semantic objective to pursue
            name: Human-readable identifier (auto-generated if not provided)
            parent_thread_id: Parent thread if this is delegated work
        """
        task_name = name or f"task-{uuid.uuid4().hex[:12]}"
        
        return cls(
            id=ThreadId(value=str(uuid.uuid4())),
            name=task_name,
            objective=objective,
            parent_thread_id=parent_thread_id,
        )
    
    def with_state(self, new_state: TaskState) -> "TaskThread":
        """Create new thread instance with updated state."""
        return dataclass_replace(self, state=new_state)
    
    def increment_revision(self) -> "TaskThread":
        """Increment semantic revision and return new instance."""
        return dataclass_replace(self, semantic_revision=self.semantic_revision + 1)
    
    def to_task_snapshot(self) -> "TaskSnapshot":
        """Create immutable snapshot for Loop evaluation."""
        return TaskSnapshot.from_thread(self)


@dataclass(frozen=True)
class TaskSnapshot:
    """
    Read-only snapshot of TaskThread state for Loop evaluation.
    """
    id: str
    name: str
    objective: str
    
    # Semantic state
    accepted_plan: Optional[Dict[str, Any]] = None  # Plan as dict for serialization
    constraints: Dict[str, Any] = field(default_factory=dict)  # Constraints as dict
    status: str = TaskStatus.DEFINING.value
    progress: Dict[str, Any] = field(default_factory=dict)
    
    # History and artifacts
    execution_history: List[str] = field(default_factory=list)
    produced_artifacts: Dict[str, Any] = field(default_factory=dict)
    
    unresolved_blockers: List[str] = field(default_factory=list)
    completion_criteria_met: bool = False
    
    # Lifecycle state (semantic intent)
    lifecycle_state: ThreadLifecycleState = ThreadLifecycleState.CREATED
    
    # Active components
    active_loop_id: Optional[str] = None
    active_cycle_id: Optional[str] = None
    
    # Relationships
    parent_thread_id: Optional[str] = None
    child_thread_ids: Tuple[str, ...] = ()
    
    # Revision tracking
    semantic_revision: int = 0
    terminal_reason: Optional[str] = None
    
    @classmethod
    def from_thread(cls, thread: TaskThread) -> "TaskSnapshot":
        """Create snapshot from a TaskThread."""
        plan_dict = None
        if thread.state.accepted_plan:
            plan_dict = {
                "plan_id": thread.state.accepted_plan.plan_id,
                "steps": list(thread.state.accepted_plan.steps),
                "dependencies": dict(thread.state.accepted_plan.dependencies),
                "assumptions": list(thread.state.accepted_plan.assumptions),
                "risks": list(thread.state.accepted_plan.risks),
            }
        
        return cls(
            id=thread.id.value,
            name=thread.name,
            objective=thread.objective,
            accepted_plan=plan_dict,
            constraints={
                "time_budget_seconds": thread.state.constraints.time_budget_seconds,
                "resource_limits": dict(thread.state.constraints.resource_limits),
                "quality_threshold": thread.state.constraints.quality_threshold,
                "required_outcome_types": list(thread.state.constraints.required_outcome_types),
            },
            status=thread.state.status.value,
            progress={
                "current_step_index": thread.state.progress.current_step_index,
                "steps_completed": thread.state.progress.steps_completed,
                "total_steps": thread.state.progress.total_steps,
                "completed_executions": list(thread.state.progress.completed_executions),
                "failed_executions": list(thread.state.progress.failed_executions),
                "produced_artifacts": list(thread.state.progress.produced_artifacts),
                "confidence": thread.state.progress.confidence,
            },
            execution_history=list(thread.state.execution_history),
            produced_artifacts=dict(thread.state.produced_artifacts),
            unresolved_blockers=list(thread.state.unresolved_blockers),
            completion_criteria_met=thread.state.completion_criteria_met,
            lifecycle_state=thread.lifecycle_state,
            active_loop_id=thread.active_loop_id,
            active_cycle_id=thread.active_cycle_id,
            parent_thread_id=thread.parent_thread_id,
            child_thread_ids=thread.child_thread_ids,
            semantic_revision=thread.semantic_revision,
            terminal_reason=thread.terminal_reason,
        )


# =============================================================================
# MonitoringThread
# =============================================================================

class ObservationType(Enum):
    """
    Types of observations a monitoring thread may make.
    
    These classify what kind of semantic change is being observed:
        - STATE_CHANGE: System state has changed
        - METRIC_THRESHOLD: A metric exceeded threshold
        - PATTERN_DETECTED: A pattern was identified in data
        - ANOMALY_DETECTED: Something unexpected occurred
        - CONDITION_MET: An expected condition became true
    """
    STATE_CHANGE = "state_change"
    METRIC_THRESHOLD = "metric_threshold"
    PATTERN_DETECTED = "pattern_detected"
    ANOMALY_DETECTED = "anomaly_detected"
    CONDITION_MET = "condition_met"


@dataclass(frozen=True)
class MonitoringTarget:
    """
    The subject being monitored.
    
    This identifies what the monitoring thread is observing.
    """
    target_type: str  # e.g., "service", "resource", "metric", "system_state"
    identifier: str  # e.g., "api-server-1", "memory_usage", "database_connections"
    scope: Optional[str] = None  # Additional context (e.g., environment, region)


@dataclass(frozen=True)
class Baseline:
    """
    Accepted baseline for monitoring comparisons.
    
    This is what the thread considers "normal" state.
    """
    metric_name: str
    expected_value: float
    acceptable_range: Tuple[float, float]  # (min, max) inclusive
    observation_count: int = 0  # How many observations formed this baseline?
    last_updated_at: float = 0.0  # timestamp


@dataclass(frozen=True)
class MonitoringState:
    """
    Semantic state owned by MonitoringThread.
    
    This is the persistent semantic state of monitoring, including:
        - Monitored subject
        - Observation criteria
        - Baseline for comparison
        - History of observations
        - Detected changes and their significance
        - Escalation conditions
    """
    target: MonitoringTarget
    observation_criteria: List[str] = field(default_factory=list)  # What to look for
    
    # Baseline (for comparison)
    baseline: Optional[Baseline] = None
    
    # Observation history
    observations: List[Dict[str, Any]] = field(default_factory=list)  # Recent observations
    detected_changes: List[Dict[str, Any]] = field(default_factory=list)  # Significant changes
    
    # Escalation state
    escalation_conditions: List[str] = field(default_factory=list)
    current_escalation_level: int = 0  # 0 = no escalation, higher = more severe
    
    # Completion criteria
    completion_criteria_met: bool = False


@dataclass(frozen=True)
class MonitoringThread:
    """
    Represents a durable obligation to observe semantic change over time.
    
    Examples:
        - runtime monitoring
        - health monitoring  
        - repository monitoring
        - environment monitoring
        - service monitoring
        - cognitive monitoring
    
    A MonitoringThread owns observation continuity. It does NOT own runtime
    timing or scheduling - Core decides when observation becomes possible.
    
    Lifecycle transitions:
        CREATED → OBSERVING → WAITING → OBSERVING → ESCALATING → WAITING
        ↓
        COMPLETED
    
    Typical Loops:
        MonitoringLoop, WaitingLoop
    """
    
    # Identity (immutable - no defaults)
    id: ThreadId
    name: str  # Human-readable monitoring identifier
    
    # Semantic state
    state: MonitoringState = field(default_factory=MonitoringState)
    
    # Lifecycle state (semantic intent)
    lifecycle_state: ThreadLifecycleState = ThreadLifecycleState.CREATED
    
    # Active components (at most one each)
    active_loop_id: Optional[str] = None
    active_cycle_id: Optional[str] = None
    
    # Parent-child relationships (optional)
    parent_thread_id: Optional[str] = None
    child_thread_ids: Tuple[str, ...] = ()
    
    # Revision tracking
    semantic_revision: int = 0
    
    # Terminal state tracking
    terminal_reason: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        target: MonitoringTarget,
        name: Optional[str] = None,
        parent_thread_id: Optional[str] = None,
    ) -> "MonitoringThread":
        """
        Create a new MonitoringThread.
        
        Args:
            target: What to monitor
            name: Human-readable identifier (auto-generated if not provided)
            parent_thread_id: Parent thread if this is delegated work
        """
        mon_name = name or f"monitor-{uuid.uuid4().hex[:12]}"
        
        return cls(
            id=ThreadId(value=str(uuid.uuid4())),
            name=mon_name,
            state=MonitoringState(target=target),
            parent_thread_id=parent_thread_id,
        )
    
    def with_state(self, new_state: MonitoringState) -> "MonitoringThread":
        """Create new thread instance with updated state."""
        return dataclass_replace(self, state=new_state)
    
    def increment_revision(self) -> "MonitoringThread":
        """Increment semantic revision and return new instance."""
        return dataclass_replace(self, semantic_revision=self.semantic_revision + 1)
    
    def to_monitoring_snapshot(self) -> "MonitoringSnapshot":
        """Create immutable snapshot for Loop evaluation."""
        return MonitoringSnapshot.from_thread(self)


@dataclass(frozen=True)
class MonitoringSnapshot:
    """
    Read-only snapshot of MonitoringThread state for Loop evaluation.
    """
    id: str
    name: str
    
    # Target and criteria
    target_type: str = ""
    target_identifier: str = ""
    observation_criteria: List[str] = field(default_factory=list)
    
    # Baseline (for comparison)
    baseline_metric_name: Optional[str] = None
    baseline_expected_value: Optional[float] = None
    baseline_acceptable_min: Optional[float] = None
    baseline_acceptable_max: Optional[float] = None
    
    # State
    current_escalation_level: int = 0
    detected_changes_count: int = 0
    
    # Progress
    observation_count: int = 0
    
    # Completion criteria
    completion_criteria_met: bool = False
    
    # Lifecycle state (semantic intent)
    lifecycle_state: ThreadLifecycleState = ThreadLifecycleState.CREATED
    
    # Active components
    active_loop_id: Optional[str] = None
    active_cycle_id: Optional[str] = None
    
    # Relationships
    parent_thread_id: Optional[str] = None
    child_thread_ids: Tuple[str, ...] = ()
    
    # Revision tracking
    semantic_revision: int = 0
    terminal_reason: Optional[str] = None
    
    @classmethod
    def from_thread(cls, thread: MonitoringThread) -> "MonitoringSnapshot":
        """Create snapshot from a MonitoringThread."""
        baseline = thread.state.baseline
        return cls(
            id=thread.id.value,
            name=thread.name,
            target_type=thread.state.target.target_type,
            target_identifier=thread.state.target.identifier,
            observation_criteria=list(thread.state.observation_criteria),
            baseline_metric_name=baseline.metric_name if baseline else None,
            baseline_expected_value=baseline.expected_value if baseline else None,
            baseline_acceptable_min=baseline.acceptable_range[0] if baseline else None,
            baseline_acceptable_max=baseline.acceptable_range[1] if baseline else None,
            current_escalation_level=thread.state.current_escalation_level,
            detected_changes_count=len(thread.state.detected_changes),
            observation_count=len(thread.state.observations),
            completion_criteria_met=thread.state.completion_criteria_met,
            lifecycle_state=thread.lifecycle_state,
            active_loop_id=thread.active_loop_id,
            active_cycle_id=thread.active_cycle_id,
            parent_thread_id=thread.parent_thread_id,
            child_thread_ids=thread.child_thread_ids,
            semantic_revision=thread.semantic_revision,
            terminal_reason=thread.terminal_reason,
        )


# =============================================================================
# InternalThread
# =============================================================================

class InternalPurpose(Enum):
    """
    Purposes of internally initiated work.
    
    These represent autonomous internal activities:
        - REFLECTION: Thinking about past execution and learning
        - CONSOLIDATION: Consolidating fragmented state
        - MAINTENANCE: Internal system maintenance
        - IDLE_COGNITION: Meaningful activity during idle periods
        - VALIDATION: Verifying system integrity
    """
    REFLECTION = "reflection"
    CONSOLIDATION = "consolidation"
    MAINTENANCE = "maintenance"
    IDLE_COGNITION = "idle_cognition"
    VALIDATION = "validation"


@dataclass(frozen=True)
class InternalContext:
    """
    Context for internally initiated semantic work.
    
    This is the internal state and motivation for internal threads.
    """
    activation_reason: str  # Why was this thread activated?
    internal_objective: Optional[str] = None  # What specific objective? (optional)
    related_thread_ids: List[str] = field(default_factory=list)  # Threads this relates to


@dataclass(frozen=True)
class InternalState:
    """
    Semantic state owned by InternalThread.
    
    This is the persistent semantic state of internal work, including:
        - Activation reason
        - Internal objective
        - Accepted insight (if any)
        - Generated adjustments
        - Completion condition
    """
    purpose: InternalPurpose
    context: InternalContext = field(default_factory=InternalContext)
    
    # Progress
    accepted_insight: Optional[str] = None
    generated_adjustments: List[str] = field(default_factory=list)  # What was adjusted?
    
    # Completion
    completion_condition_met: bool = False


@dataclass(frozen=True)
class InternalThread:
    """
    Represents autonomous internally initiated semantic work.
    
    Examples:
        - reflection on execution patterns
        - consolidation of fragmented state  
        - contradiction resolution
        - maintenance tasks
        - idle cognition during waiting periods
        - self-evaluation
    
    An InternalThread exists independently of explicit user requests and owns
    internally generated semantic objectives.
    
    Lifecycle transitions:
        CREATED → IDLE → REFLECTING → CONSOLIDATING → MAINTAINING → COMPLETED
    
    Typical Loops:
        ReflectionLoop, IdleLoop, ConsolidationLoop
    """
    
    # Identity (immutable - no defaults)
    id: ThreadId
    name: str  # Human-readable internal thread identifier
    
    # Semantic state
    state: InternalState = field(default_factory=InternalState)
    
    # Lifecycle state (semantic intent)
    lifecycle_state: ThreadLifecycleState = ThreadLifecycleState.CREATED
    
    # Active components (at most one each)
    active_loop_id: Optional[str] = None
    active_cycle_id: Optional[str] = None
    
    # Parent-child relationships (optional)
    parent_thread_id: Optional[str] = None
    child_thread_ids: Tuple[str, ...] = ()
    
    # Revision tracking
    semantic_revision: int = 0
    
    # Terminal state tracking
    terminal_reason: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        purpose: InternalPurpose,
        context: Optional[InternalContext] = None,
        name: Optional[str] = None,
        parent_thread_id: Optional[str] = None,
    ) -> "InternalThread":
        """
        Create a new InternalThread.
        
        Args:
            purpose: The internal activity being performed
            context: Context for this internal work (optional)
            name: Human-readable identifier (auto-generated if not provided)
            parent_thread_id: Parent thread that triggered this (if any)
        """
        int_name = name or f"internal-{uuid.uuid4().hex[:12]}"
        
        return cls(
            id=ThreadId(value=str(uuid.uuid4())),
            name=int_name,
            state=InternalState(purpose=purpose, context=context or InternalContext(activation_reason="initiated")),
            parent_thread_id=parent_thread_id,
        )
    
    def with_state(self, new_state: InternalState) -> "InternalThread":
        """Create new thread instance with updated state."""
        return dataclass_replace(self, state=new_state)
    
    def increment_revision(self) -> "InternalThread":
        """Increment semantic revision and return new instance."""
        return dataclass_replace(self, semantic_revision=self.semantic_revision + 1)
    
    def to_internal_snapshot(self) -> "InternalSnapshot":
        """Create immutable snapshot for Loop evaluation."""
        return InternalSnapshot.from_thread(self)


@dataclass(frozen=True)
class InternalSnapshot:
    """
    Read-only snapshot of InternalThread state for Loop evaluation.
    """
    id: str
    name: str
    
    # Purpose and context
    purpose: str = ""
    activation_reason: str = ""
    
    # State
    accepted_insight: Optional[str] = None
    generated_adjustments_count: int = 0
    
    # Completion
    completion_condition_met: bool = False
    
    # Lifecycle state (semantic intent)
    lifecycle_state: ThreadLifecycleState = ThreadLifecycleState.CREATED
    
    # Active components
    active_loop_id: Optional[str] = None
    active_cycle_id: Optional[str] = None
    
    # Relationships
    parent_thread_id: Optional[str] = None
    child_thread_ids: Tuple[str, ...] = ()
    
    # Revision tracking
    semantic_revision: int = 0
    terminal_reason: Optional[str] = None
    
    @classmethod
    def from_thread(cls, thread: InternalThread) -> "InternalSnapshot":
        """Create snapshot from an InternalThread."""
        return cls(
            id=thread.id.value,
            name=thread.name,
            purpose=thread.state.purpose.value,
            activation_reason=thread.state.context.activation_reason,
            accepted_insight=thread.state.accepted_insight,
            generated_adjustments_count=len(thread.state.generated_adjustments),
            completion_condition_met=thread.state.completion_condition_met,
            lifecycle_state=thread.lifecycle_state,
            active_loop_id=thread.active_loop_id,
            active_cycle_id=thread.active_cycle_id,
            parent_thread_id=thread.parent_thread_id,
            child_thread_ids=thread.child_thread_ids,
            semantic_revision=thread.semantic_revision,
            terminal_reason=thread.terminal_reason,
        )


# =============================================================================
# Utility Functions
# =============================================================================

def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    import dataclasses
    if hasattr(obj, '__dataclass_fields__'):
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


# =============================================================================
# Export all public symbols
# =============================================================================

__all__ = [
    # Conversation thread types
    "ConversationPurpose",
    "ConversationParticipant",
    "ConversationState",
    "ConversationThread",
    "ConversationSnapshot",
    
    # Task thread types
    "TaskStatus",
    "TaskConstraints",
    "TaskPlan",
    "TaskProgress",
    "TaskState",
    "TaskThread",
    "TaskSnapshot",
    
    # Monitoring thread types
    "ObservationType",
    "MonitoringTarget",
    "Baseline",
    "MonitoringState",
    "MonitoringThread",
    "MonitoringSnapshot",
    
    # Internal thread types
    "InternalPurpose",
    "InternalContext",
    "InternalState",
    "InternalThread",
    "InternalSnapshot",
]