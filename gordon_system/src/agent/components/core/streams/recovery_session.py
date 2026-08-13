# Stream Recovery Session - Phase 3.11.7
# =========================================

"""
Recovery session infrastructure for Gordon's Semantic Stream subsystem.

A recovery session represents a single attempt to recover from failure.
It tracks the lifecycle of recovery execution, including:

    - Plan validation and approval
    - Step execution tracking
    - State transitions during recovery
    - Success/failure outcome
    - Observability events

Recovery Session Lifecycle:
    
    INITIATED → VALIDATING → EXECUTING → [COMPLETED | FAILED]
                  ↓                    ↓         ↑
                ABORTED              ROLLBACK  |
                                              |
                                          RETRY
    
Session Responsibilities:
    - Execute recovery plan steps
    - Track execution state
    - Emit observability events
    - Handle intermediate failures
    - Support rollback if needed

Constraints:
    - Session cannot outlive the stream lifecycle
    - No modification of committed history during session
    - Ownership constraints enforced throughout
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# SESSION STATE
# =============================================================================

class RecoverySessionState(Enum):
    """
    State of a recovery session.
    
    States:
        INITIATED      - Session created but not yet validated
        VALIDATING     - Validating plan and context
        EXECUTING      - Executing recovery steps
        COMPLETED      - All steps completed successfully
        FAILED         - Recovery failed, may retry or escalate
        ABORTED        - Session aborted (graceful termination)
        ROLLED_BACK    - Rollback executed after failure
    """
    
    INITIATED = "initiated"
    VALIDATING = "validating"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    ROLLED_BACK = "rolled_back"


# =============================================================================
# RECOVERY STEP RESULT
# =============================================================================

class RecoveryStepResult(Enum):
    """
    Result of a single recovery step.
    
    Steps may:
        - SUCCEED: Step completed successfully, proceed to next
        - FAIL_PERMANENTLY: Step failed unrecoverably, abort session
        - RETRYABLE_FAILURE: Step failed but can be retried
        - SKIP: Step skipped (conditional)
        - WAIT: Step requires external input before proceeding
    """
    
    SUCCEED = "succeed"
    FAIL_PERMANENTLY = "fail_permanently"
    RETRYABLE_FAILURE = "retryable_failure"
    SKIP = "skip"
    WAIT = "wait"


@dataclass(frozen=True)
class RecoveryStepExecution:
    """
    Result of executing a recovery step.
    """
    
    step_name: str
    """Name of the step that was executed."""
    
    result: RecoveryStepResult
    """Outcome of the step execution."""
    
    timestamp_utc: float = field(default_factory=time.time)
    
    error_message: str = ""
    """Error message if step failed."""
    
    metrics: Dict[str, Any] = field(default_factory=dict)
    """Metrics collected during step execution."""
    
    next_step: Optional[str] = None
    """Next step to execute (if any)."""
    
    rollback_available: bool = False
    """Can this failure be rolled back?"""
    
    @property
    def is_success(self) -> bool:
        return self.result == RecoveryStepResult.SUCCEED
    
    @property
    def is_terminal_failure(self) -> bool:
        return self.result in (
            RecoveryStepResult.FAIL_PERMANENTLY,
            RecoveryStepResult.ABORTED,
        )
    
    @property
    def can_retry(self) -> bool:
        return self.result == RecoveryStepResult.RETRYABLE_FAILURE


# =============================================================================
# RECOVERY SESSION (The Execution Context)
# =============================================================================

@dataclass(frozen=False)
class RecoverySession:
    """
    Mutable recovery session state.
    
    This is the runtime object that tracks a single recovery attempt.
    It's mutable to allow step execution and state updates, but
    produces immutable result artifacts.
    
    Thread safety: Session operations should be serialized by caller.
    """
    
    # Identity
    session_id: str  # Unique session identifier
    
    plan: Any  # RecoveryPlan reference
    
    # Execution context
    stream_id: Optional[str] = None
    generation_id: Optional[int] = None
    
    # Lifecycle state
    state: RecoverySessionState = RecoverySessionState.INITIATED
    
    created_at_utc: float = field(default_factory=time.time)
    
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Execution tracking
    current_step_index: int = 0
    steps_completed: List[str] = field(default_factory=list)
    steps_failed: List[Tuple[str, str]] = field(default_factory=list)  # (step_name, error)
    
    # Results
    step_results: List[RecoveryStepExecution] = field(default_factory=list)
    
    final_success: bool = False
    final_error_message: str = ""
    
    # Retry state
    retry_count: int = 0
    max_retries: int = 3
    
    # Observability
    events_emitted: List[str] = field(default_factory=list)  # Event IDs
    
    def is_terminal(self) -> bool:
        """Check if session reached a terminal state."""
        return self.state in (
            RecoverySessionState.COMPLETED,
            RecoverySessionState.FAILED,
            RecoverySessionState.ABORTED,
            RecoverySessionState.ROLLED_BACK,
        )
    
    def can_retry(self) -> bool:
        """Check if session can be retried."""
        return (
            self.retry_count < self.max_retries and
            not self.is_terminal() and
            any(r.can_retry for r in self.step_results)
        )
    
    def get_next_step(self) -> Optional[str]:
        """Get the next step to execute."""
        if self.current_step_index >= len(self.plan.steps):
            return None
        return self.plan.steps[self.current_step_index]
    
    def record_step_result(self, result: RecoveryStepExecution) -> None:
        """Record execution of a recovery step."""
        self.step_results.append(result)
        
        if result.is_success:
            self.steps_completed.append(result.step_name)
            self.current_step_index += 1
        elif result.is_terminal_failure:
            self.steps_failed.append((result.step_name, result.error_message))
        else:
            # Retryable or wait - don't advance index
            pass
    
    def to_result(self) -> "RecoveryResult":
        """Create an immutable RecoveryResult from this session."""
        return RecoveryResult(
            session_id=self.session_id,
            plan_id=self.plan.plan_id if self.plan else "",
            decision=self.plan.decision if self.plan else None,
            stream_id=self.stream_id or "unknown",
            generation_id=self.generation_id,
            state=self.state,
            success=self.final_success,
            error_message=self.final_error_message,
            steps_executed=len(self.step_results),
            steps_completed=len(self.steps_completed),
            steps_failed=len(self.steps_failed),
            retry_count=self.retry_count,
            created_at_utc=self.created_at_utc,
            started_at_utc=self.started_at_utc or self.created_at_utc,
            completed_at_utc=self.completed_at_utc or time.time(),
            step_results=tuple(self.step_results),
        )


@dataclass(frozen=True)
class RecoveryResult:
    """
    Immutable result of a recovery session.
    
    This is what gets returned to callers after recovery completes
    (successfully or not). It contains all relevant outcome information.
    """
    
    # Session identity
    session_id: str
    
    plan_id: str
    decision: Optional[Any] = None  # RecoveryDecision reference
    
    # Stream context
    stream_id: str
    generation_id: Optional[int] = None
    
    # Outcome
    state: RecoverySessionState
    success: bool
    error_message: str = ""
    
    # Execution details
    steps_executed: int = 0
    steps_completed: int = 0
    steps_failed: int = 0
    
    retry_count: int = 0
    
    # Timing
    created_at_utc: float = 0.0
    started_at_utc: float = 0.0
    completed_at_utc: float = 0.0
    
    # Step-by-step results
    step_results: Tuple[RecoveryStepExecution, ...] = field(default_factory=tuple)
    
    @property
    def duration_seconds(self) -> float:
        """Calculate total recovery duration."""
        return self.completed_at_utc - self.started_at_utc
    
    @classmethod
    def success_result(
        cls,
        session_id: str,
        plan_id: str,
        stream_id: str,
        generation_id: Optional[int] = None,
        steps_executed: int = 0,
    ) -> "RecoveryResult":
        """Create a successful result."""
        now = time.time()
        return cls(
            session_id=session_id,
            plan_id=plan_id,
            decision=None,  # Will be set by caller
            stream_id=stream_id,
            generation_id=generation_id,
            state=RecoverySessionState.COMPLETED,
            success=True,
            steps_executed=steps_executed,
            steps_completed=steps_executed,
            created_at_utc=now - 1.0,  # Approximate
            started_at_utc=now - 1.0,
            completed_at_utc=now,
        )
    
    @classmethod
    def failure_result(
        cls,
        session_id: str,
        plan_id: str,
        stream_id: str,
        error_message: str,
        generation_id: Optional[int] = None,
        steps_executed: int = 0,
        retry_count: int = 0,
    ) -> "RecoveryResult":
        """Create a failure result."""
        now = time.time()
        return cls(
            session_id=session_id,
            plan_id=plan_id,
            decision=None,
            stream_id=stream_id,
            generation_id=generation_id,
            state=RecoverySessionState.FAILED,
            success=False,
            error_message=error_message,
            steps_executed=steps_executed,
            retry_count=retry_count,
            created_at_utc=now - 1.0,
            started_at_utc=now - 1.0,
            completed_at_utc=now,
        )


# =============================================================================
# CONTINUITY COORDINATOR (Session Orchestrator)
# =============================================================================

class ContinuityCoordinator:
    """
    Coordinator for recovery sessions and continuity restoration.
    
    The coordinator doesn't own stream history but coordinates
    the restoration process, ensuring:
        
        - Checkpoint loading before replay
        - Cursor reconstruction after restoration
        - Lifecycle synchronization with recovery state
        - Integrity validation post-recovery
    
    Responsibilities:
        - Create and manage recovery sessions
        - Load checkpoints when needed
        - Validate integrity after recovery
        - Synchronize lifecycle transitions
        - Emit observability events
    
    Constraints:
        - Never modify committed history
        - Respect ownership boundaries
        - Enforce authorization for all operations
    """
    
    def __init__(self):
        """Initialize the continuity coordinator."""
        self._sessions: Dict[str, RecoverySession] = {}
        self._session_counter = 0
    
    def create_session(
        self,
        plan: Any,  # RecoveryPlan reference
        stream_id: Optional[str] = None,
        generation_id: Optional[int] = None,
    ) -> RecoverySession:
        """
        Create a new recovery session.
        
        Args:
            plan: The recovery plan to execute
            stream_id: Stream being recovered (optional, from plan)
            generation_id: Generation being recovered (optional, from plan)
            
        Returns:
            New RecoverySession in INITIATED state
        """
        self._session_counter += 1
        session_id = f"session:{time.monotonic_ns()}:{uuid.uuid4().hex[:8]}"
        
        session = RecoverySession(
            session_id=session_id,
            plan=plan,
            stream_id=stream_id or (plan.stream_id if hasattr(plan, 'stream_id') else None),
            generation_id=generation_id,
            state=RecoverySessionState.INITIATED,
        )
        
        self._sessions[session_id] = session
        return session
    
    def start_session(self, session: RecoverySession) -> bool:
        """
        Start a recovery session.
        
        Transitions session from INITIATED to VALIDATING.
        
        Args:
            session: Session to start
            
        Returns:
            True if started successfully, False otherwise
        """
        if session.state != RecoverySessionState.INITIATED:
            return False
        
        session.started_at_utc = time.time()
        session.state = RecoverySessionState.VALIDATING
        return True
    
    def execute_next_step(self, session: RecoverySession) -> Optional[RecoveryStepExecution]:
        """
        Execute the next step in a recovery session.
        
        Args:
            session: Session to advance
            
        Returns:
            Execution result for the step, or None if no steps remain
        """
        if session.state not in (RecoverySessionState.VALIDATING, RecoverySessionState.EXECUTING):
            return None
        
        next_step = session.get_next_step()
        if not next_step:
            # All steps completed
            session.final_success = True
            session.state = RecoverySessionState.COMPLETED
            session.completed_at_utc = time.time()
            return None
        
        # In a real implementation, this would execute the step logic
        # For now, we simulate successful execution
        result = RecoveryStepExecution(
            step_name=next_step,
            result=RecoveryStepResult.SUCCEED,
        )
        
        session.record_step_result(result)
        
        if session.state == RecoverySessionState.VALIDATING:
            session.state = RecoverySessionState.EXECUTING
        
        return result
    
    def validate_after_execution(self, session: RecoverySession) -> Tuple[bool, str]:
        """
        Validate recovery after all steps executed.
        
        Performs integrity checks and lifecycle synchronization.
        
        Args:
            session: Completed session to validate
            
        Returns:
            (is_valid, message) tuple
        """
        if not session.is_terminal():
            return False, "Session must be in terminal state to validate"
        
        # In real implementation, would verify:
        # - Checkpoint integrity
        # - Cursor position validity
        # - Lifecycle state consistency
        
        return True, "Validation passed"
    
    def get_session(self, session_id: str) -> Optional[RecoverySession]:
        """Get a session by ID."""
        return self._sessions.get(session_id)
    
    def remove_session(self, session_id: str) -> bool:
        """
        Remove a session from tracking.
        
        Returns True if session was found and removed.
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    @property
    def active_sessions(self) -> List[RecoverySession]:
        """Get all currently active (non-terminal) sessions."""
        return [
            s for s in self._sessions.values()
            if not s.is_terminal()
        ]
    
    def get_all_results(self) -> List[RecoveryResult]:
        """Get results for all completed sessions."""
        results = []
        for session in self._sessions.values():
            if session.state == RecoverySessionState.COMPLETED:
                results.append(session.to_result())
        return results