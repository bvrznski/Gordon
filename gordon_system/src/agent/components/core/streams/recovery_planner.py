# Stream Recovery Planner - Phase 3.11.7
# =========================================

"""
Recovery planning infrastructure for Gordon's Semantic Stream subsystem.

This module implements the recovery planner that evaluates failure conditions
and determines appropriate recovery actions based on:

    - Stream lifecycle state
    - Checkpoint availability and validity
    - Replay availability
    - Persistence health
    - Ownership constraints
    - Authorization context
    - Integrity requirements
    - Capacity limits
    - Retry policies

Recovery Planning Process:
    
    1. Failure Detection → 2. Failure Classification → 3. Context Analysis
       ↓                      ↓                        ↓
    4. Constraint Evaluation → 5. Decision Generation → 6. Plan Creation
    
Planning Decisions:
    RESUME          - Resume from validated checkpoint without replay
    REPLAY          - Replay from checkpoint to restore cursor position
    RESTORE         - Restore stream state from validated checkpoint
    RESTART_GEN     - Restart generation from scratch (new generation)
    DEGRADE         - Enter degraded operation mode with limitations
    ABORT           - Terminate recovery attempt gracefully
    ESCALATE        - Escalate to higher authority for decision

Constraints:
    - Recovery must respect lifecycle state machine transitions
    - Checkpoints must be validated before restoration
    - Replay never recreates committed history
    - Ownership and authorization are always preserved
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum, auto
import time


# =============================================================================
# RECOVERY DECISIONS (Canonical)
# =============================================================================

class RecoveryDecision(Enum):
    """
    Canonical recovery decision types.
    
    Each decision defines:
        - What action to take
        - Expected outcome
        - Resource requirements
        - Lifecycle impact
    
    Decisions are ordered by aggressiveness of intervention.
    """
    
    # Non-intrusive decisions (minimal state change)
    RESUME = "resume"
    """Resume from validated checkpoint without replay. Fastest recovery."""
    
    REPLAY = "replay"
    """Replay from checkpoint to restore cursor position."""
    
    RESTORE = "restore"
    """Restore stream state from validated checkpoint."""
    
    # Moderate intervention decisions
    RESTART_GEN = "restart_generation"
    """Restart generation from scratch (new generation)."""
    
    DEGRADE = "degrade"
    """Enter degraded operation mode with limitations."""
    
    ABORT = "abort"
    """Terminate recovery attempt gracefully."""
    
    ESCALATE = "escalate"
    """Escalate to higher authority for decision."""


# =============================================================================
# RECOVERY CONSTRAINTS (Planning Parameters)
# =============================================================================

@dataclass(frozen=True)
class RecoveryConstraints:
    """
    Constraints that affect recovery planning.
    
    These are the boundaries within which recovery must operate.
    """
    
    # Lifecycle constraints
    lifecycle_state: str = "active"
    """Current stream lifecycle state."""
    
    allow_generation_rollover: bool = False
    """Can create new generation for recovery?"""
    
    # Checkpoint constraints
    checkpoint_validation_required: bool = True
    """Must checkpoints be validated before restore?"""
    
    checkpoint_version_compatible: bool = True
    """Check version compatibility?"""
    
    # Authorization constraints
    authorization_required: bool = True
    """Require explicit authorization for recovery operations."""
    
    scope_isolation_mandatory: bool = True
    """Enforce scope isolation strictly?"""
    
    # Capacity constraints
    max_replay_records: Optional[int] = 10000
    """Maximum records in replay operation."""
    
    max_restore_time_seconds: float = 60.0
    """Maximum allowed time for restoration."""
    
    # Integrity constraints
    integrity_validation_required: bool = True
    """Must integrity be revalidated after recovery?"""
    
    security_audit_required: bool = True
    """Must all recovery actions be audited?"""
    
    # Retry constraints
    max_retry_attempts: int = 3
    """Maximum retry attempts per operation."""
    
    # Timing constraints
    recovery_deadline_utc: Optional[float] = None
    """Absolute deadline by which recovery must complete."""


# =============================================================================
# RECOVERY PLANNER INPUT (Context for Planning)
# =============================================================================

@dataclass(frozen=True)
class RecoveryPlanningContext:
    """
    Context provided to the recovery planner.
    
    This contains all information needed to make a deterministic
    recovery decision.
    """
    
    # Failure context
    failure: Any  # StreamFailureDescriptor reference
    
    # Stream state
    stream_id: Optional[str] = None
    """Stream identifier."""
    
    current_generation_id: Optional[int] = None
    """Current generation number."""
    
    last_checkpoint_id: Optional[str] = None
    """Most recent valid checkpoint (if any)."""
    
    cursor_position: Optional[int] = None
    """Current cursor position before failure."""
    
    lifecycle_state: str = "active"
    """Current lifecycle state."""
    
    # Availability indicators
    checkpoint_available: bool = False
    """Is a valid checkpoint available?"""
    
    replay_available: bool = True
    """Can replay historical records?"""
    
    persistence_healthy: bool = True
    """Is persistence layer operational?"""
    
    # Ownership context
    owner_id: Optional[str] = None
    """Stream owner identifier."""
    
    authorization_context: Optional[Dict[str, Any]] = None
    """Authorization context for recovery operations."""
    
    # Policy references
    retry_policy_id: Optional[str] = None
    """Which retry policy to apply?"""
    
    # Timing
    failure_timestamp_utc: float = field(default_factory=time.time)
    when_planning_started: float = field(default_factory=time.time)


# =============================================================================
# RECOVERY PLANNING OUTPUT (The Plan)
# =============================================================================

class RecoveryPlanStatus(Enum):
    """
    Status of a recovery plan.
    """
    
    PENDING = "pending"           # Plan created, not yet executed
    VALIDATED = "validated"       # Plan validated for execution
    EXECUTING = "executing"       # Plan is currently executing
    COMPLETED = "completed"       # Plan completed successfully
    FAILED = "failed"             # Plan execution failed
    INVALIDATED = "invalidated"   # Plan no longer valid (lifecycle changed)


@dataclass(frozen=True)
class RecoveryPlan:
    """
    Immutable recovery plan.
    
    A recovery plan is the output of planning and the input to execution.
    It contains:
        - Decision made
        - Steps to execute
        - Validation requirements
        - Rollback options
    
    Design principles:
        - Immutable for thread safety
        - Deterministic from context
        - Self-documenting (every field explains its purpose)
    """
    
    # Identity and metadata
    plan_id: str  # Unique identifier
    planning_timestamp_utc: float
    
    # Decision
    decision: RecoveryDecision
    """The recovery decision made by the planner."""
    
    reason: str
    """Human-readable explanation for the decision."""
    
    # Context captured at planning time
    stream_id: Optional[str] = None
    generation_id: Optional[int] = None
    failure_id: Optional[str] = None
    
    # Execution parameters
    start_position: Optional[int] = None
    """Where to start recovery (cursor position or checkpoint)."""
    
    target_state: str = "active"
    """Desired lifecycle state after recovery."""
    
    max_duration_seconds: float = 60.0
    """Maximum allowed duration for recovery."""
    
    # Constraints applied
    validate_checkpoints: bool = True
    """Should checkpoints be validated?"""
    
    require_integrity_verification: bool = True
    """Should integrity be verified after recovery?"""
    
    # Step sequence (ordered)
    steps: Tuple[str, ...] = field(default_factory=tuple)
    """Ordered list of recovery steps to execute."""
    
    # Status tracking
    status: RecoveryPlanStatus = RecoveryPlanStatus.PENDING
    
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Result (after execution)
    success: bool = False
    error_message: str = ""
    
    def is_terminal(self) -> bool:
        """Check if plan reached a terminal state."""
        return self.status in (
            RecoveryPlanStatus.COMPLETED,
            RecoveryPlanStatus.FAILED,
            RecoveryPlanStatus.INVALIDATED,
        )
    
    @classmethod
    def for_resume(
        cls,
        stream_id: str,
        checkpoint_id: str,
        cursor_position: int,
        reason: str = "Resuming from validated checkpoint",
    ) -> "RecoveryPlan":
        """Create a RESUME plan."""
        return cls(
            plan_id=f"plan:{time.monotonic_ns()}:{__import__('uuid').uuid4().hex[:8]}",
            planning_timestamp_utc=time.time(),
            decision=RecoveryDecision.RESUME,
            reason=reason,
            stream_id=stream_id,
            start_position=cursor_position,
            target_state="active",
            steps=("validate_checkpoint", "restore_cursor", "resume_delivery"),
        )
    
    @classmethod
    def for_replay(
        cls,
        stream_id: str,
        checkpoint_id: str,
        cursor_position: int,
        max_records: Optional[int] = None,
        reason: str = "Replaying from checkpoint to restore cursor position",
    ) -> "RecoveryPlan":
        """Create a REPLAY plan."""
        steps = ["validate_checkpoint", "replay_history"]
        if max_records:
            steps.append(f"limit_replay_to_{max_records}_records")
        steps.extend(["restore_cursor", "resume_delivery"])
        
        return cls(
            plan_id=f"plan:{time.monotonic_ns()}:{__import__('uuid').uuid4().hex[:8]}",
            planning_timestamp_utc=time.time(),
            decision=RecoveryDecision.REPLAY,
            reason=reason,
            stream_id=stream_id,
            start_position=cursor_position,
            target_state="active",
            steps=tuple(steps),
        )
    
    @classmethod
    def for_restart_generation(
        cls,
        stream_id: str,
        new_generation_number: int,
        reason: str = "Restarting generation due to unrecoverable failure",
    ) -> "RecoveryPlan":
        """Create a RESTART_GENERATION plan."""
        return cls(
            plan_id=f"plan:{time.monotonic_ns()}:{__import__('uuid').uuid4().hex[:8]}",
            planning_timestamp_utc=time.time(),
            decision=RecoveryDecision.RESTART_GEN,
            reason=reason,
            stream_id=stream_id,
            start_position=None,  # New generation starts at position 0
            target_state="active",
            steps=("close_generation", "create_new_generation", "open_generation"),
        )
    
    @classmethod
    def for_degrade(
        cls,
        stream_id: str,
        degraded_mode: str = "read_only",
        reason: str = "Entering degraded mode due to recoverable failure",
    ) -> "RecoveryPlan":
        """Create a DEGRADE plan."""
        return cls(
            plan_id=f"plan:{time.monotonic_ns()}:{__import__('uuid').uuid4().hex[:8]}",
            planning_timestamp_utc=time.time(),
            decision=RecoveryDecision.DEGRADE,
            reason=reason,
            stream_id=stream_id,
            target_state="degraded",
            steps=("validate_degradation_safe", "enter_degraded_mode"),
        )
    
    @classmethod
    def for_abort(
        cls,
        stream_id: str,
        reason: str = "Aborting recovery due to unrecoverable failure",
    ) -> "RecoveryPlan":
        """Create an ABORT plan."""
        return cls(
            plan_id=f"plan:{time.monotonic_ns()}:{__import__('uuid').uuid4().hex[:8]}",
            planning_timestamp_utc=time.time(),
            decision=RecoveryDecision.ABORT,
            reason=reason,
            stream_id=stream_id,
            target_state="draining",  # Graceful shutdown
            steps=("validate_abort_safe", "abort_recovery"),
        )
    
    @classmethod
    def for_escalate(
        cls,
        stream_id: str,
        reason: str = "Escalating recovery decision to higher authority",
    ) -> "RecoveryPlan":
        """Create an ESCALATE plan."""
        return cls(
            plan_id=f"plan:{time.monotonic_ns()}:{__import__('uuid').uuid4().hex[:8]}",
            planning_timestamp_utc=time.time(),
            decision=RecoveryDecision.ESCALATE,
            reason=reason,
            stream_id=stream_id,
            target_state="active",  # Stay in current state
            steps=("gather_additional_context", "escalate_to_authority"),
        )


# =============================================================================
# RECOVERY PLANNER (The Decision Engine)
# =============================================================================

class RecoveryPlanner:
    """
    Canonical recovery planner for stream failures.
    
    The planner evaluates failure context and constraints to determine
    the appropriate recovery action. Planning is deterministic - given
    the same inputs, it always produces the same output.
    
    Planning Algorithm:
        
        1. If failure is terminal → ABORT
        2. If checkpoint unavailable and replay unavailable → ESCALATE
        3. If lifecycle state allows resume → RESUME (fastest)
        4. If replay available and position known → REPLAY
        5. If generation integrity questionable → RESTORE + RESTART_GEN
        6. If capacity exceeded and can be relieved → DEGRADE
        7. Otherwise → ESCALATE
    """
    
    def __init__(
        self,
        constraints: Optional[RecoveryConstraints] = None,
    ):
        """
        Initialize the recovery planner.
        
        Args:
            constraints: Recovery constraints to apply during planning.
                        If None, uses defaults.
        """
        self._constraints = constraints or RecoveryConstraints()
    
    @property
    def constraints(self) -> RecoveryConstraints:
        """Get current constraints."""
        return self._constraints
    
    def plan_recovery(
        self,
        context: RecoveryPlanningContext,
    ) -> RecoveryPlan:
        """
        Plan recovery for a failure.
        
        This is the main planning function. It evaluates all factors
        and returns a deterministic recovery plan.
        
        Args:
            context: Context containing failure state, stream info,
                    and availability indicators.
                    
        Returns:
            A RecoveryPlan with the decision and execution parameters.
        """
        # Step 1: Check for terminal conditions
        if self._is_terminal_condition(context):
            return self._plan_abort(context, "Terminal failure condition detected")
        
        # Step 2: Check checkpoint availability and validity
        if not context.checkpoint_available:
            if not context.replay_available:
                return self._plan_escalate(
                    context,
                    "No recovery anchors available (no checkpoint + no replay)"
                )
            # Can use replay from earliest position
            return self._plan_replay_from_earliest(context)
        
        # Step 3: Check if we can resume from checkpoint
        if self._can_resume_from_checkpoint(context):
            return self._plan_resume(context)
        
        # Step 4: Plan replay recovery
        if context.replay_available:
            return self._plan_replay_from_checkpoint(context)
        
        # Step 5: Consider generation restart
        if self._can_restart_generation(context):
            return self._plan_restart_generation(context)
        
        # Step 6: Check if degradation is appropriate
        if self._can_degrade(context):
            return self._plan_degrade(context)
        
        # Step 7: Escalate as last resort
        return self._plan_escalate(
            context,
            "Cannot determine safe recovery action from available information"
        )
    
    def _is_terminal_condition(self, context: RecoveryPlanningContext) -> bool:
        """Check if the failure is terminal."""
        failure = getattr(context, 'failure', None)
        if not failure:
            return False
        
        # Check failure properties
        if hasattr(failure, 'terminal') and getattr(failure, 'terminal', False):
            return True
        
        # Check severity
        severity = getattr(failure, 'severity', None)
        if severity in ('fatal', 'FATAL'):
            return True
        
        return False
    
    def _can_resume_from_checkpoint(self, context: RecoveryPlanningContext) -> bool:
        """Check if resume from checkpoint is appropriate."""
        if not context.checkpoint_available:
            return False
        
        # Resume is only valid for certain failure types
        # (non-corruption, non-integrity failures)
        return (
            self._constraints.lifecycle_state in ("active", "paused") and
            context.cursor_position is not None and
            context.persistence_healthy
        )
    
    def _can_restart_generation(self, context: RecoveryPlanningContext) -> bool:
        """Check if generation restart is appropriate."""
        return (
            self._constraints.allow_generation_rollover and
            context.lifecycle_state in ("active", "degraded")
        )
    
    def _can_degrade(self, context: RecoveryPlanningContext) -> bool:
        """Check if degradation is appropriate."""
        # Can degrade if failure is recoverable but not immediately
        return (
            self._constraints.max_replay_records is None or  # No hard limit
            context.cursor_position is None  # Position unknown, can't replay
        )
    
    def _plan_abort(self, context: RecoveryPlanningContext, reason: str) -> RecoveryPlan:
        """Create an ABORT plan."""
        return RecoveryPlan.for_abort(context.stream_id or "unknown", reason)
    
    def _plan_resume(self, context: RecoveryPlanningContext) -> RecoveryPlan:
        """Create a RESUME plan."""
        return RecoveryPlan.for_resume(
            stream_id=context.stream_id or "unknown",
            checkpoint_id=context.last_checkpoint_id or "unknown",
            cursor_position=context.cursor_position or 0,
            reason="Resuming from validated checkpoint after non-corruptive failure",
        )
    
    def _plan_replay_from_checkpoint(self, context: RecoveryPlanningContext) -> RecoveryPlan:
        """Create a REPLAY plan from checkpoint."""
        return RecoveryPlan.for_replay(
            stream_id=context.stream_id or "unknown",
            checkpoint_id=context.last_checkpoint_id or "unknown",
            cursor_position=context.cursor_position or 0,
            reason="Replaying from checkpoint after corruption/integrity failure",
        )
    
    def _plan_replay_from_earliest(self, context: RecoveryPlanningContext) -> RecoveryPlan:
        """Create a REPLAY plan from earliest available position."""
        return RecoveryPlan.for_replay(
            stream_id=context.stream_id or "unknown",
            checkpoint_id="earliest_available",
            cursor_position=0,
            reason="Replaying from earliest position due to missing checkpoint",
        )
    
    def _plan_restart_generation(self, context: RecoveryPlanningContext) -> RecoveryPlan:
        """Create a RESTART_GENERATION plan."""
        new_gen = (context.current_generation_id or 1) + 1
        return RecoveryPlan.for_restart_generation(
            stream_id=context.stream_id or "unknown",
            new_generation_number=new_gen,
            reason="Restarting generation due to integrity concerns",
        )
    
    def _plan_degrade(self, context: RecoveryPlanningContext) -> RecoveryPlan:
        """Create a DEGRADE plan."""
        return RecoveryPlan.for_degrade(
            stream_id=context.stream_id or "unknown",
            degraded_mode="read_only",
            reason="Entering degraded mode due to recoverable failure with no immediate recovery path",
        )
    
    def _plan_escalate(self, context: RecoveryPlanningContext, reason: str) -> RecoveryPlan:
        """Create an ESCALATE plan."""
        return RecoveryPlan.for_escalate(context.stream_id or "unknown", reason)