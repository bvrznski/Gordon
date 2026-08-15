# Gordon Executive Network Runtime Participation Semantics - Phase 4.4.10A.2
# ============================================================================

"""
Executive Runtime Participation Specification.

This is Phase 4.4.10A.2: Executive Coordination and Runtime Participation.

The Executive Network participates in runtime without depending on concrete
implementations. This module defines semantic participation concepts without
introducing scheduler, thread, coroutine, or asyncio constructs.

IMPLEMENTATION STATUS:
=====================

This package is entirely runtime-neutral.
It defines semantic participation semantics, NOT implementations.

No scheduler, loop, coroutine, thread, executor,
asyncio construct, process, callback, or runtime
implementation is introduced here.

VERSION: 1.0.0
COMPATIBILITY: forward (phased implementation)
DEPRECATION: three_releases policy
EXTENSION STRATEGY: additive_only
"""

# =============================================================================
# IMPORTS
# =============================================================================

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional
from enum import Enum, auto


# =============================================================================
# EXECUTIVE ACTIVATION KINDS - Semantic activation states (NOT runtime states)
# =============================================================================


class ExecutiveActivationKind(Enum):
    """
    Kinds of executive activation.
    
    These are semantic activation descriptions, NOT process or thread states:
        INITIAL: First-time activation
        RESUMPTION: Resuming from suspension
        WAKEUP: Waking from idle/dormant state
        CONTEXT_SWITCH: Switching to new context
        PRIORITY_INVERSION: Handling higher-priority event
    
    These are NOT:
        • Process states
        • Thread states
        • Scheduler states
        • Runtime activation flags
    """
    
    INITIAL = "initial"
    RESUMPTION = "resumption"
    WAKEUP = "wakeup"
    CONTEXT_SWITCH = "context_switch"
    PRIORITY_INVERSION = "priority_inversion"


# =============================================================================
# EXECUTIVE INVOCATION KINDS - How Executive is invoked (semantic, not runtime)
# =============================================================================


class ExecutiveInvocationKind(Enum):
    """
    Kinds of executive invocation.
    
    These are semantic invocation descriptions:
        EXTERNAL_REQUEST: External system requests coordination
        EVENT_DRIVEN: Responding to an event
        PERIODIC_CHECK: Periodic evaluation check
        PRIORITY_CHANGE: Priority change triggers evaluation
        CONTEXT_UPDATE: Context update triggers evaluation
    
    These are NOT:
        • Scheduler decisions
        • Thread wakeups
        • Coroutine yields
        • Timer interrupts
    """
    
    EXTERNAL_REQUEST = "external_request"
    EVENT_DRIVEN = "event_driven"
    PERIODIC_CHECK = "periodic_check"
    PRIORITY_CHANGE = "priority_change"
    CONTEXT_UPDATE = "context_update"


# =============================================================================
# EXECUTIVE PARTICIPATION KINDS - How Executive participates in runtime
# =============================================================================


class ExecutiveParticipationKind(Enum):
    """
    Kinds of executive participation.
    
    These are semantic participation descriptions:
        ACTIVE_PARTICIPATION: Actively coordinating subsystems
        PASSIVE_MONITORING: Monitoring without active coordination
        COORDINATION_WAIT: Waiting for subsystem responses
        DELIBERATION_MODE: Evaluating options before deciding
    
    These are NOT:
        • Process states
        • Thread states
        • Scheduler decisions
        • Runtime state transitions
    """
    
    ACTIVE_PARTICIPATION = "active_participation"
    PASSIVE_MONITORING = "passive_monitoring"
    COORDINATION_WAIT = "coordination_wait"
    DELIBERATION_MODE = "deliberation_mode"


# =============================================================================
# EXECUTIVE CYCLE PARTICIPATION - How Executive participates in cycles
# =============================================================================


@dataclass(frozen=True)
class ExecutiveCycleParticipation:
    """
    Semantic cycle participation record.
    
    This describes HOW Executive participates in a cognitive cycle,
    NOT HOW the cycle is implemented (no threads, loops, etc.).
    """
    
    cycle_id: str = field(default_factory=lambda: f"cycle_{id({})}")
    """Unique identifier for this cycle."""
    
    activation_kind: ExecutiveActivationKind = ExecutiveActivationKind.INITIAL
    """How Executive was activated in this cycle."""
    
    invocation_kind: ExecutiveInvocationKind = ExecutiveInvocationKind.EXTERNAL_REQUEST
    """How Executive was invoked."""
    
    participation_kind: ExecutiveParticipationKind = ExecutiveParticipationKind.ACTIVE_PARTICIPATION
    """How Executive participated in the cycle."""
    
    subsystems_coordination: Tuple[str, ...] = ()
    """Subsystems coordinated in this cycle."""
    
    decisions_made: int = 0
    """Number of executive decisions made."""
    
    coordination_requests: int = 0
    """Number of coordination requests issued."""
    
    responses_received: int = 0
    """Number of subsystem responses received."""


# =============================================================================
# EXECUTIVE SCHEDULING PARTICIPATION - Semantic scheduling (no runtime)
# =============================================================================


@dataclass(frozen=True)
class ExecutiveSchedulingParticipation:
    """
    Semantic scheduling participation record.
    
    This describes HOW Executive relates to scheduling concepts,
    NOT HOW scheduling is implemented (no threads, timers, etc.).
    """
    
    priority_level: int = 50
    """Priority level for coordination (0-100, arbitrary scale)."""
    
    wait_conditions: Tuple[str, ...] = ()
    """Conditions that must be met before resuming."""
    
    resume_triggers: Tuple[str, ...] = ()
    """Events that will trigger resumption."""
    
    timeout_reference: Optional[float] = None
    """Timeout reference (arbitrary time unit, not real-time)."""
    
    yield_points: Tuple[str, ...] = ()
    """Points where coordination may yield to other systems."""


# =============================================================================
# EXECUTIVE WAKE CONDITIONS - Semantic wake conditions (not runtime events)
# =============================================================================


@dataclass(frozen=True)
class ExecutiveWakeConditions:
    """
    Semantic wake condition specification.
    
    These define WHEN Executive should participate, NOT HOW
    wake signals are implemented (no interrupts, timers, etc.).
    """
    
    # Activation triggers (semantic descriptions)
    external_request_received: bool = False
    """External system has requested coordination."""
    
    priority_inversion_detected: bool = False
    """Higher-priority event detected."""
    
    subsystem_response_arrived: bool = False
    """Awaiting subsystem response arrived."""
    
    timeout_elapsed: bool = False
    """Timeout reference has elapsed."""
    
    context_change: bool = False
    """Context has changed significantly."""
    
    # Priority threshold
    priority_threshold: int = 50
    """Minimum priority for activation."""


# =============================================================================
# EXECUTIVE SLEEP CONDITIONS - Semantic sleep conditions (not runtime states)
# =============================================================================


@dataclass(frozen=True)
class ExecutiveSleepConditions:
    """
    Semantic sleep condition specification.
    
    These define WHEN Executive should suspend coordination,
    NOT HOW suspension is implemented (no timers, sleeps, etc.).
    """
    
    # Sleep triggers (semantic descriptions)
    no_active_goals: bool = False
    """No active goals require coordination."""
    
    all_subsystems_synchronized: bool = False
    """All coordinated subsystems are in sync."""
    
    idle_threshold_reached: bool = False
    """Idle threshold has been reached."""
    
    # Cooldown period (arbitrary units, not time)
    cooldown_remaining: int = 0
    """Remaining cooldown before next potential activation."""


# =============================================================================
# EXECUTIVE SUSPENSION KINDS - Semantic suspension states
# =============================================================================


class ExecutiveSuspensionKind(Enum):
    """
    Kinds of executive suspension.
    
    These are semantic suspension descriptions:
        TEMPORARY_WAIT: Waiting for external conditions
        COORDINATION_IN_PROGRESS: Currently coordinating
        IDLE_MODE: Not currently needed
        PRIORITY_DEACTIVATION: Lower priority than current activity
    
    These are NOT:
        • Process states
        • Thread sleep states
        • Scheduler suspensions
        • Runtime suspension flags
    """
    
    TEMPORARY_WAIT = "temporary_wait"
    COORDINATION_IN_PROGRESS = "coordination_in_progress"
    IDLE_MODE = "idle_mode"
    PRIORITY_DEACTIVATION = "priority_deactivation"


# =============================================================================
# EXECUTIVE RESUMPTION KINDS - Semantic resumption states
# =============================================================================


class ExecutiveResumptionKind(Enum):
    """
    Kinds of executive resumption.
    
    These are semantic resumption descriptions:
        EXTERNAL_TRIGGER: Triggered by external event
        TIMEOUT_EXPIRED: Timeout reference has elapsed
        PRIORITY_INVERSION: Higher priority event occurred
        CONTEXT_UPDATE: Context changed requiring coordination
    
    These are NOT:
        • Process wakeups
        • Thread awakenings
        • Scheduler decisions
        • Runtime state transitions
    """
    
    EXTERNAL_TRIGGER = "external_trigger"
    TIMEOUT_EXPIRED = "timeout_expired"
    PRIORITY_INVERSION = "priority_inversion"
    CONTEXT_UPDATE = "context_update"


# =============================================================================
# EXECUTIVE INTERRUPTION KINDS - Semantic interruption states
# =============================================================================


@dataclass(frozen=True)
class ExecutiveInterruptionKind(Enum):
    """
    Kinds of executive interruption.
    
    These are semantic interruption descriptions:
        PRIORITY_PREEMPTION: Higher-priority event preempts current activity
        RESOURCE_CONFLICT: Resource conflict requires interruption
        ERROR_CONDITION: Error condition requires intervention
        EXTERNAL_REQUEST: External request requires attention
    
    These are NOT:
        • Process interrupts
        • Thread preemption
        • Scheduler decisions
        • Runtime interrupt flags
    """
    
    PRIORITY_PREEMPTION = "priority_preemption"
    RESOURCE_CONFLICT = "resource_conflict"
    ERROR_CONDITION = "error_condition"
    EXTERNAL_REQUEST = "external_request"


# =============================================================================
# EXECUTIVE CANCELLATION KINDS - Semantic cancellation states
# =============================================================================


class ExecutiveCancellationKind(Enum):
    """
    Kinds of executive cancellation.
    
    These are semantic cancellation descriptions:
        USER_REQUEST: User explicitly cancelled
        TIMEOUT_EXPIRED: Operation timed out
        RESOURCE_EXHAUSTED: Resources exhausted
        ERROR_RECOVERY: Error recovery requires cancellation
    
    These are NOT:
        • Process terminations
        • Thread cancellations
        • Scheduler decisions
        • Runtime cancellation flags
    """
    
    USER_REQUEST = "user_request"
    TIMEOUT_EXPIRED = "timeout_expired"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    ERROR_RECOVERY = "error_recovery"


# =============================================================================
# EXECUTIVE PREEMPTION KINDS - Semantic preemption states
# =============================================================================


@dataclass(frozen=True)
class ExecutivePreemptionKind(Enum):
    """
    Kinds of executive preemption.
    
    These are semantic preemption descriptions:
        HIGH_PRIORITY_GOAL: Higher-priority goal requires immediate attention
        CRITICAL_EVENT: Critical event demands response
        RESOURCE_STARVATION: Other system needs resources
    
    These are NOT:
        • Process preemptions
        • Thread preemptions
        • Scheduler decisions
        • Runtime preemption flags
    """
    
    HIGH_PRIORITY_GOAL = "high_priority_goal"
    CRITICAL_EVENT = "critical_event"
    RESOURCE_STARVATION = "resource_starvation"


# =============================================================================
# EXECUTIVE SYNCHRONIZATION KINDS - Semantic synchronization points
# =============================================================================


@dataclass(frozen=True)
class ExecutiveSynchronizationKind(Enum):
    """
    Kinds of executive synchronization.
    
    These are semantic synchronization descriptions:
        COORDINATION_COMPLETE: All coordination completed successfully
        SUBSYSTEM_RESPONSE_RECEIVED: Received response from subsystem
        STATE_COMMITTED: State has been committed
        BARRIER_REACHED: Coordination barrier reached
    
    These are NOT:
        • Mutex locks
        • Semaphore releases
        • Barrier waits
        • Runtime synchronization primitives
    """
    
    COORDINATION_COMPLETE = "coordination_complete"
    SUBSYSTEM_RESPONSE_RECEIVED = "subsystem_response_received"
    STATE_COMMITTED = "state_committed"
    BARRIER_REACHED = "barrier_reached"


# =============================================================================
# EXECUTIVE EVENT PARTICIPATION - How Executive participates in events
# =============================================================================


@dataclass(frozen=True)
class ExecutiveEventParticipation:
    """
    Semantic event participation record.
    
    This describes HOW Executive participates in event handling,
    NOT HOW events are implemented (no callbacks, async handlers, etc.).
    """
    
    event_id: str = field(default_factory=lambda: f"event_{id({})}")
    """Unique identifier for this event."""
    
    event_kind: str
    """Kind of event (e.g., 'goal_update', 'error_report')."""
    
    subscription_type: str = "direct"
    """Type of subscription to this event kind."""
    
    priority_handling: Literal["immediate", "queued", "deferred"] = "queued"
    """Priority handling for this event type."""
    
    acknowledged: bool = False
    """Has this event been acknowledged by Executive?"""
    
    response_required: bool = False
    """Does this event require an executive response?"""


# =============================================================================
# EXECUTIVE RUNTIME TRANSITIONS - Semantic state transitions (not runtime)
# =============================================================================


@dataclass(frozen=True)
class ExecutiveRuntimeTransition:
    """
    Semantic runtime transition record.
    
    This describes STATE CHANGES in Executive participation,
    NOT HOW these changes are implemented (no thread state, etc.).
    """
    
    from_state: str
    """State before transition."""
    
    to_state: str
    """State after transition."""
    
    transition_kind: str = "coordination"
    """Kind of transition."""
    
    trigger: Optional[str] = None
    """Trigger for this transition."""
    
    timestamp_utc: float = 0.0
    """Timestamp of transition (semantic, not real-time)."""


# =============================================================================
# EXECUTIVE EXECUTION BOUNDARIES - Semantic execution boundaries
# =============================================================================


@dataclass(frozen=True)
class ExecutiveExecutionBoundary:
    """
    Semantic execution boundary record.
    
    This defines WHERE Executive's semantic coordination ends
    and subsystem implementation begins (no runtime details).
    """
    
    boundary_id: str = field(default_factory=lambda: f"boundary_{id({})}")
    """Unique identifier for this boundary."""
    
    boundary_kind: Literal[
        "coordination_boundary",
        "implementation_boundary",
        "ownership_boundary"
    ] = "coordination_boundary"
    
    subsystem_name: str
    """Name of the subsystem at this boundary."""
    
    responsibility_transfer: bool = False
    """Does responsibility transfer across this boundary?"""
    
    decision_point: bool = True
    """Is this a point where Executive makes decisions?"""


# =============================================================================
# EXECUTIVE FAILURE PARTICIPATION - Semantic failure handling
# =============================================================================


@dataclass(frozen=True)
class ExecutiveFailureParticipation:
    """
    Semantic failure participation record.
    
    This describes HOW Executive participates in failure scenarios,
    NOT HOW failures are detected or handled (no error handlers, etc.).
    """
    
    failure_id: str = field(default_factory=lambda: f"failure_{id({})}")
    """Unique identifier for this failure."""
    
    failure_kind: Literal[
        "coordination_timeout",
        "subsystem_error",
        "state_inconsistency",
        "resource_exhaustion"
    ]
    
    detection_confidence: float = 0.5
    """Confidence in failure detection (0.0 to 1.0)."""
    
    escalation_required: bool = False
    """Does this require escalation?"""
    
    recovery_requested: bool = False
    """Has recovery been requested?"""


# =============================================================================
# EXECUTIVE RECOVERY PARTICIPATION - Semantic recovery states
# =============================================================================


class ExecutiveRecoveryParticipationKind(Enum):
    """
    Kinds of executive recovery participation.
    
    These are semantic recovery descriptions:
        ERROR_DETECTION: Detected error condition
        RECOVERY_REQUESTED: Recovery has been requested
        STATE_RESTORATION: Restoring to stable state
        COORDINATION_RESTART: Restarting coordination after failure
    
    These are NOT:
        • Process recovery
        • Thread restarts
        • Error handler invocations
        • Runtime recovery mechanisms
    """
    
    ERROR_DETECTION = "error_detection"
    RECOVERY_REQUESTED = "recovery_requested"
    STATE_RESTORATION = "state_restoration"
    COORDINATION_RESTART = "coordination_restart"


# =============================================================================
# EXECUTIVE IDLE PARTICIPATION - Semantic idle states
# =============================================================================


@dataclass(frozen=True)
class ExecutiveIdleParticipation:
    """
    Semantic idle participation record.
    
    This describes HOW Executive participates during idle periods,
    NOT HOW idle is implemented (no timers, sleep, etc.).
    """
    
    idle_kind: Literal[
        "waiting_for_request",
        "background_maintenance",
        "resource_conservation",
        "priority_deactivation"
    ]
    
    duration_reference: Optional[float] = None
    """Duration reference for idle period (arbitrary units)."""
    
    maintenance_tasks: Tuple[str, ...] = ()
    """Tasks that may be performed during idle."""
    
    wake_triggers: Tuple[str, ...] = ()
    """Triggers that will end idle state."""


# =============================================================================
# EXECUTIVE SHUTDOWN PARTICIPATION - Semantic shutdown states
# =============================================================================


@dataclass(frozen=True)
class ExecutiveShutdownParticipation:
    """
    Semantic shutdown participation record.
    
    This describes HOW Executive participates in shutdown,
    NOT HOW shutdown is implemented (no termination handlers, etc.).
    """
    
    shutdown_kind: Literal[
        "graceful_shutdown",
        "emergency_shutdown",
        "resource_cleanup",
        "state_persistence"
    ]
    
    cleanup_tasks: Tuple[str, ...] = ()
    """Tasks to perform during shutdown."""
    
    state_save_required: bool = True
    """Should state be saved before shutdown?"""
    
    coordinated_termination: bool = False
    """Should termination be coordinated with subsystems?"""


# =============================================================================
# EXECUTIVE LOOP PARTICICIPATION - Semantic loop participation (no runtime)
# =============================================================================


@dataclass(frozen=True)
class ExecutiveLoopParticipation:
    """
    Semantic loop participation record.
    
    This describes HOW Executive participates in execution loops,
    NOT HOW loops are implemented (no threads, coroutines, etc.).
    """
    
    loop_kind: Literal[
        "reasoning_loop",
        "agent_loop",
        "executive_loop",
        "planning_loop",
        "monitoring_loop",
        "learning_loop",
        "recovery_loop",
        "idle_loop"
    ]
    
    entry_conditions: Tuple[str, ...] = ()
    """Conditions that must be true to enter this loop."""
    
    exit_conditions: Tuple[str, ...] = ()
    """Conditions that cause exit from this loop."""
    
    iteration_count: int = 0
    """Number of iterations completed in this loop."""
    
    ownership_description: str = "external_runtime"
    """Description of who owns the loop implementation."""


# =============================================================================
# EXECUTIVE STATE PARTICIPATION - Semantic state transitions (not runtime)
# =============================================================================


@dataclass(frozen=True)
class ExecutiveStateParticipation:
    """
    Semantic state participation record.
    
    This describes EXECUTIVE STATE CHANGES during participation,
    NOT HOW these changes are implemented (no thread states, etc.).
    """
    
    from_state: str
    """State before transition."""
    
    to_state: str
    """State after transition."""
    
    participation_context: str = ""
    """Context of participation that triggered this state change."""
    
    timestamp_utc: float = 0.0
    """Timestamp (semantic, not real-time)."""
    
    state_change_reason: str = ""
    """Reason for the state change."""


# =============================================================================
# COORDINATION BARRIERS - Semantic coordination barriers (not runtime)
# =============================================================================


@dataclass(frozen=True)
class CoordinationBarrier:
    """
    Semantic coordination barrier.
    
    This defines POINTS WHERE Executive waits for subsystem responses,
    NOT HOW waiting is implemented (no mutexes, semaphores, etc.).
    """
    
    barrier_id: str = field(default_factory=lambda: f"barrier_{id({})}")
    """Unique identifier for this barrier."""
    
    barrier_kind: Literal[
        "subsystem_response",
        "state_consistency",
        "coordination_complete",
        "resource_available"
    ]
    
    waiting_for: Tuple[str, ...] = ()
    """What Executive is waiting for."""
    
    timeout_reference: Optional[float] = None
    """Timeout reference (arbitrary units)."""
    
    synchronization_point: bool = True
    """Is this a synchronization point?"""


# =============================================================================
# VISIBILITY GUARANTEES - Semantic visibility guarantees (not runtime)
# =============================================================================


@dataclass(frozen=True)
class VisibilityGuarantee:
    """
    Semantic visibility guarantee.
    
    This defines WHAT is visible when during coordination,
    NOT HOW visibility is implemented (no memory barriers, etc.).
    """
    
    visibility_kind: Literal[
        "state_visible",
        "request_processed",
        "response_available",
        "decision_made"
    ]
    
    guaranteed: bool = True
    """Is this guarantee always maintained?"""
    
    consistency_level: Literal["strong", "eventual", "none"] = "strong"
    """Consistency level of visibility."""
    
    ordering_guaranteed: bool = True
    """Are events ordered correctly?"""


# =============================================================================
# ORDERING GUARANTEES - Semantic ordering guarantees (not runtime)
# =============================================================================


@dataclass(frozen=True)
class OrderingGuarantee:
    """
    Semantic ordering guarantee.
    
    This defines HOW events are ordered during coordination,
    NOT HOW ordering is implemented (no locks, barriers, etc.).
    """
    
    guarantee_kind: Literal[
        "causal_ordering",
        "priority_ordering",
        "temporal_ordering"
    ]
    
    guaranteed: bool = True
    """Is this guarantee always maintained?"""
    
    implementation_neutral: bool = True
    """This guarantee holds regardless of runtime implementation."""
    
    subsystem_respected: bool = True
    """Do subsystems respect this ordering?"""


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Activation kinds
    "ExecutiveActivationKind",
    
    # Invocation kinds
    "ExecutiveInvocationKind",
    
    # Participation kinds
    "ExecutiveParticipationKind",
    
    # Cycle participation
    "ExecutiveCycleParticipation",
    
    # Scheduling participation
    "ExecutiveSchedulingParticipation",
    
    # Wake conditions
    "ExecutiveWakeConditions",
    
    # Sleep conditions
    "ExecutiveSleepConditions",
    
    # Suspension kinds
    "ExecutiveSuspensionKind",
    
    # Resumption kinds
    "ExecutiveResumptionKind",
    
    # Interruption kinds
    "ExecutiveInterruptionKind",
    
    # Cancellation kinds
    "ExecutiveCancellationKind",
    
    # Preemption kinds
    "ExecutivePreemptionKind",
    
    # Synchronization kinds
    "ExecutiveSynchronizationKind",
    
    # Event participation
    "ExecutiveEventParticipation",
    
    # Runtime transitions
    "ExecutiveRuntimeTransition",
    
    # Execution boundaries
    "ExecutiveExecutionBoundary",
    
    # Failure participation
    "ExecutiveFailureParticipation",
    
    # Recovery kinds
    "ExecutiveRecoveryParticipationKind",
    
    # Idle participation
    "ExecutiveIdleParticipation",
    
    # Shutdown participation
    "ExecutiveShutdownParticipation",
    
    # Loop participation
    "ExecutiveLoopParticipation",
    
    # State participation
    "ExecutiveStateParticipation",
    
    # Coordination barriers
    "CoordinationBarrier",
    
    # Visibility guarantees
    "VisibilityGuarantee",
    
    # Ordering guarantees
    "OrderingGuarantee",
]