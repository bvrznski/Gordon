# Core Recovery Architecture
# ==========================

"""
Recovery coordination for runtime failures.

This module provides:
- Recovery policy contracts
- Recovery plan construction and validation
- Bounded recovery execution
- Budget tracking and loop prevention
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum, auto
import time


# Re-export FailureCategory from failures module for recovery plan defaults
try:
    from .failures import FailureCategory
except ImportError:
    class FailureCategory(Enum):
        EXECUTION = "execution"
        DEPENDENCY = "dependency"
        RESOURCE = "resource"
        LIFECYCLE = "lifecycle"
        CONFIGURATION = "configuration"


# =============================================================================
# Recovery Policy Types
# =============================================================================

class RecoveryAction(Enum):
    """
    Generic recovery actions Core may invoke.
    
    These are domain-neutral actions that work with existing authorities:
        - NO_ACTION: No action needed (already handled)
        - RETRY_OPERATION: Retry the failed operation
        - CANCEL_TASK: Cancel a specific task
        - CANCEL_SCOPE: Cancel an entire scope
        - RELEASE_RESOURCE: Release a resource
        - REINITIALIZE_ENTITY: Reinitialize an entity
        - RESTART_ENTITY: Restart an entity through lifecycle
        - REBIND_DEPENDENCY: Rebind a dependency
        - MARK_DEGRADED: Mark subject as degraded
        - ISOLATE_ENTITY: Isolate from other entities
        - STOP_ENTITY: Stop the entity
        - REQUEST_RUNTIME_SHUTDOWN: Request runtime shutdown
        - REQUIRE_PROCESS_RESTART: Require process restart
        - ESCALATE: Escalate to higher authority
    """
    
    NO_ACTION = "no_action"
    RETRY_OPERATION = "retry_operation"
    CANCEL_TASK = "cancel_task"
    CANCEL_SCOPE = "cancel_scope"
    RELEASE_RESOURCE = "release_resource"
    REINITIALIZE_ENTITY = "reinitialize_entity"
    RESTART_ENTITY = "restart_entity"
    REBIND_DEPENDENCY = "rebind_dependency"
    MARK_DEGRADED = "mark_degraded"
    ISOLATE_ENTITY = "isolate_entity"
    STOP_ENTITY = "stop_entity"
    REQUEST_RUNTIME_SHUTDOWN = "request_runtime_shutdown"
    REQUIRE_PROCESS_RESTART = "require_process_restart"
    ESCALATE = "escalate"


class RecoveryPolicy(Enum):
    """
    Recovery policy templates.
    
    Defines high-level recovery behavior:
        - NO_OP: Do not recover (may still record and escalate)
        - IMMEDIATE_RETRY: Try again right away
        - EXPONENTIAL_BACKOFF: Wait with exponential backoff
        - RESTART: Stop and restart the entity
        - ISOLATE: Isolate from system while degraded
    """
    
    NO_OP = "no_op"                # No automatic recovery
    IMMEDIATE_RETRY = "immediate_retry"
    FIXED_BACKOFF = "fixed_backoff"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    RESTART = "restart"
    ISOLATE = "isolate"


# =============================================================================
# Recovery Policy Contract
# =============================================================================

class RecoveryPolicyEvaluator:
    """
    Contract for recovery policy evaluation.
    
    Policies decide:
        - Whether recovery is permitted
        - Which generic action is allowed
        - Attempt limits
        - Backoff strategy
        - Degradation behavior
        - Escalation threshold
    
    Usage:
        class MyRecoveryPolicy(RecoveryPolicyEvaluator):
            def evaluate(self, failure: FailureRecord) -> RecoveryDecision:
                if failure.category == FailureCategory.CONFIGURATION:
                    return RecoveryDecision(
                        permit_recovery=False,
                        action=RecoveryAction.ESCALATE
                    )
                return RecoveryDecision(
                    permit_recovery=True,
                    action=RecoveryAction.RETRY_OPERATION
                )
        
        policy = MyRecoveryPolicy()
        decision = policy.evaluate(failure)
    """
    
    async def evaluate(self, failure: "FailureRecord") -> "RecoveryDecision":
        """
        Evaluate recovery for a failure.
        
        Args:
            failure: The failure record to evaluate
            
        Returns:
            RecoveryDecision with permit flag and action
        """
        raise NotImplementedError


@dataclass(frozen=True)
class RecoveryDecision:
    """
    Result of policy evaluation.
    
    Args:
        permit_recovery: Whether recovery is allowed
        action: Which generic recovery action to use
        max_attempts: Maximum attempts allowed
        backoff_seconds: Base backoff time if using backoff
        escalation_threshold: When to escalate (attempt count)
        degradation_on_failure: Whether to mark degraded on failure
    """
    
    permit_recovery: bool = False
    action: RecoveryAction = RecoveryAction.ESCALATE
    
    max_attempts: int = 3
    backoff_seconds: float = 0.0  # 0 = immediate retry
    
    escalation_threshold: int = 5
    degradation_on_failure: bool = True


# =============================================================================
# Recovery Plan
# =============================================================================

@dataclass(frozen=True)
class RecoveryPlan:
    """
    A recovery plan for a specific failure.
    
    A plan is inspectable before execution and includes:
        - Target subject
        - Ordered actions to take
        - Required authorities
        - Timeout and cancellation behavior
        - Compensation/rollback actions
        - Post-recovery verification
    
    Usage:
        plan = RecoveryPlan(
            recovery_id=recovery_id,
            failure=failure,
            target_subject=entity_id,
            preconditions=[],
            actions=[
                RecoveryAction.RELEASE_RESOURCE,
                RecoveryAction.CANCEL_TASK,
                RecoveryAction.RESTART_ENTITY
            ],
            post_recovery_checks=["integrity", "health"],
            timeout_seconds=30.0
        )
        
        # Can inspect before executing
        if plan.is_safe:
            await execute_plan(plan)
    """
    
    recovery_id: str  # Unique identifier for this recovery attempt
    
    failure: "FailureRecord"  # The triggering failure
    target_subject: str  # Entity being recovered
    
    # Recovery strategy
    policy: RecoveryPolicy = RecoveryPolicy.IMMEDIATE_RETRY
    
    # Actions to execute in order
    actions: List[RecoveryAction] = field(default_factory=list)
    
    # Context requirements
    preconditions: List["Precondition"] = field(default_factory=list)
    required_authorities: List[str] = field(default_factory=list)  # e.g., "lifecycle", "scheduling"
    
    # Timing and limits
    timeout_seconds: float = 60.0
    max_attempts: int = 3
    backoff_seconds: float = 1.0
    
    # Compensation
    rollback_actions: List[RecoveryAction] = field(default_factory=list)
    
    # Verification
    post_recovery_checks: List[str] = field(default_factory=list)  # Check names
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    
    # Escalation
    escalation_condition: Optional[str] = None  # When to escalate (e.g., "timeout_exceeded")
    
    @property
    def is_safe(self) -> bool:
        """Check if plan passes basic safety checks."""
        # Check for invalid action sequences
        if not self.actions:
            return False
        
        # No duplicate consecutive actions unless intentional
        for i in range(1, len(self.actions)):
            if self.actions[i] == self.actions[i-1]:
                return False
        
        return True
    
    @property
    def duration_estimate_seconds(self) -> float:
        """Estimate total recovery time."""
        base_duration = len(self.actions) * 2.0  # ~2 seconds per action
        backoff_time = (self.max_attempts - 1) * self.backoff_seconds if self.backoff_seconds > 0 else 0
        return base_duration + backoff_time
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to a JSON-serializable dictionary."""
        return {
            "recovery_id": self.recovery_id,
            "target_subject": self.target_subject,
            "policy": self.policy.value if hasattr(self.policy, 'value') else str(self.policy),
            "action_count": len(self.actions),
            "actions": [a.value if hasattr(a, 'value') else str(a) for a in self.actions],
            "timeout_seconds": self.timeout_seconds,
            "max_attempts": self.max_attempts,
            "backoff_seconds": self.backoff_seconds,
            "post_recovery_checks": self.post_recovery_checks,
            "escalation_condition": self.escalation_condition
        }
    
    @classmethod
    def create(
        cls,
        failure: "FailureRecord",
        target_subject: str,
        actions: Optional[List[RecoveryAction]] = None,
        policy: RecoveryPolicy = RecoveryPolicy.IMMEDIATE_RETRY,
        timeout_seconds: float = 60.0,
        max_attempts: int = 3,
        backoff_seconds: float = 1.0,
        **kwargs
    ) -> "RecoveryPlan":
        """
        Create a new recovery plan.
        
        Args:
            failure: The triggering failure
            target_subject: Entity to recover
            actions: Recovery actions to take (defaults based on category)
            policy: Recovery policy template
            timeout_seconds: Maximum time for recovery
            max_attempts: Maximum retry attempts
            backoff_seconds: Base backoff between retries
            **kwargs: Additional RecoveryPlan parameters
            
        Returns:
            A new RecoveryPlan instance
        """
        if actions is None:
            # Default actions based on failure category
            actions = cls._default_actions_for_category(failure.category)
        
        return cls(
            recovery_id=f"recovery_{time.monotonic_ns()}",
            failure=failure,
            target_subject=target_subject,
            policy=policy,
            actions=actions,
            timeout_seconds=timeout_seconds,
            max_attempts=max_attempts,
            backoff_seconds=backoff_seconds,
            **kwargs
        )
    
    @staticmethod
    def _default_actions_for_category(category: "FailureCategory") -> List[RecoveryAction]:
        """Get default recovery actions for a failure category."""
        defaults = {
            FailureCategory.EXECUTION: [
                RecoveryAction.CANCEL_TASK,
                RecoveryAction.RETRY_OPERATION
            ],
            FailureCategory.DEPENDENCY: [
                RecoveryAction.REBIND_DEPENDENCY,
                RecoveryAction.ISOLATE_ENTITY
            ],
            FailureCategory.RESOURCE: [
                RecoveryAction.RELEASE_RESOURCE,
                RecoveryAction.REINITIALIZE_ENTITY
            ],
            FailureCategory.LIFECYCLE: [
                RecoveryAction.STOP_ENTITY,
                RecoveryAction.RESTART_ENTITY
            ],
            FailureCategory.CONFIGURATION: [
                RecoveryAction.ESCALATE
            ],
        }
        
        return defaults.get(category, [RecoveryAction.RETRY_OPERATION])


@dataclass(frozen=True)
class Precondition:
    """
    A condition that must be true before recovery can proceed.
    
    Usage:
        precondition = Precondition(
            name="entity_stopped",
            check=lambda state: state == LifecycleState.STOPPED
        )
        
        plan = RecoveryPlan(
            preconditions=[precondition],
            ...
        )
    """
    
    name: str  # Unique identifier for this precondition
    description: str  # Human-readable description
    
    # Check function - returns (passed: bool, reason: Optional[str])
    check: Callable[[Any], tuple]  # state -> (bool, optional reason)
    
    is_blocking: bool = True  # If true, blocks recovery if not met


# =============================================================================
# Recovery Budget
# =============================================================================

@dataclass
class RecoveryBudget:
    """
    Track and limit recovery attempts.
    
    Prevents:
        - Endless restart loops
        - Repeated reinitialization loops
        - Failure-recovery-failure oscillation
    
    Usage:
        budget = RecoveryBudget(
            subject=entity_id,
            allowed_attempts=3,
            window_seconds=60.0  # Per minute window
        )
        
        if budget.can_attempt():
            await attempt_recovery()
            budget.consume_attempt()
    """
    
    budget_id: str  # Unique identifier
    
    subject: str  # Entity this budget applies to
    
    allowed_attempts: int = 3
    consumed_attempts: int = 0
    
    window_seconds: float = 60.0  # Time window for counting attempts
    
    first_attempt_at: Optional[float] = None
    latest_attempt_at: Optional[float] = None
    
    cooldown_until: float = 0.0  # When next attempt is allowed (backoff)
    
    @property
    def remaining_attempts(self) -> int:
        """Calculate remaining attempts."""
        return max(0, self.allowed_attempts - self.consumed_attempts)
    
    @property
    def exhausted(self) -> bool:
        """Check if budget is exhausted."""
        return self.remaining_attempts <= 0
    
    def can_attempt(self, now: Optional[float] = None) -> bool:
        """
        Check if an attempt is allowed.
        
        Args:
            now: Current time (uses monotonic time if not provided)
            
        Returns:
            True if attempt is permitted
        """
        current_time = now or time.monotonic()
        
        # Check cooldown
        if current_time < self.cooldown_until:
            return False
        
        # Check budget exhaustion
        if self.exhausted:
            return False
        
        # Clean old attempts outside the window
        window_start = current_time - self.window_seconds
        if self.first_attempt_at is not None and self.first_attempt_at < window_start:
            # Reset window (simplified - would need more sophisticated tracking in production)
            self.consumed_attempts = 0
            self.first_attempt_at = current_time
        
        return True
    
    def consume_attempt(self, now: Optional[float] = None) -> None:
        """
        Record that an attempt was made.
        
        Args:
            now: Current time
        """
        current_time = now or time.monotonic()
        
        self.consumed_attempts += 1
        
        if self.first_attempt_at is None:
            self.first_attempt_at = current_time
        
        self.latest_attempt_at = current_time
    
    def set_cooldown(self, seconds: float, now: Optional[float] = None) -> None:
        """
        Set cooldown before next attempt.
        
        Args:
            seconds: Cooldown duration
            now: Current time
        """
        current_time = now or time.monotonic()
        self.cooldown_until = current_time + seconds
    
    def reset(self) -> None:
        """Reset budget state."""
        self.consumed_attempts = 0
        self.first_attempt_at = None
        self.latest_attempt_at = None
        self.cooldown_until = 0.0


# =============================================================================
# Recovery Result
# =============================================================================

class RecoveryResult(Enum):
    """
    Outcome of a recovery attempt.
    
    Usage:
        result = await execute_recovery(plan)
        
        if result == RecoveryResult.SUCCESS:
            # Recovery successful, verify state
            pass
        
        elif result == RecoveryResult.PARTIAL:
            # Some actions succeeded, some failed
            # May need escalation
            pass
        
        elif result == RecoveryResult.FAILURE:
            # All recovery attempts exhausted
            # Escalate or mark as degraded
            pass
    """
    
    SUCCESS = "success"       # Recovery completed successfully
    PARTIAL = "partial"      # Some success, some failure (may need escalation)
    FAILURE = "failure"      # All recovery attempts failed
    CANCELLED = "cancelled"  # Recovery was cancelled
    TIMEOUT = "timeout"      # Recovery exceeded timeout
    SKIPPED = "skipped"      # Recovery skipped due to policy or state


@dataclass(frozen=True)
class RecoveryExecutionResult:
    """
    Result of recovery execution.
    
    Args:
        result: Overall outcome (SUCCESS, PARTIAL, FAILURE, etc.)
        plan: The plan that was executed
        actions_executed: How many actions were actually executed
        actions_succeeded: How many succeeded
        actions_failed: How many failed
        
        primary_failure_preserved: Whether primary failure is still intact
        secondary_failures: Any failures that occurred during recovery
        
        post_verification_passed: Whether post-recovery checks passed
    """
    
    result: RecoveryResult
    
    plan: Optional[RecoveryPlan] = None
    failure_record: Optional["FailureRecord"] = None  # Original failure
    
    actions_executed: int = 0
    actions_succeeded: int = 0
    actions_failed: int = 0
    
    primary_failure_preserved: bool = True
    secondary_failures: List["FailureRecord"] = field(default_factory=list)
    
    post_verification_passed: bool = False
    
    @property
    def success(self) -> bool:
        """Check if recovery succeeded."""
        return self.result == RecoveryResult.SUCCESS and self.post_verification_passed
    
    @property
    def requires_escalation(self) -> bool:
        """Check if failure should be escalated."""
        # Escalate if:
        # - Not all actions succeeded AND some failed
        # - Or post verification failed
        # - Or primary failure was lost
        
        failure_ratio = (self.actions_failed / self.actions_executed) if self.actions_executed > 0 else 0
        
        return (
            not self.post_verification_passed or
            not self.primary_failure_preserved or
            (failure_ratio > 0 and self.result == RecoveryResult.PARTIAL)
        )


# =============================================================================
# Recovery Coordinator Contract
# =============================================================================

class RecoveryCoordinator:
    """
    Contract for recovery coordination.
    
    The coordinator:
        - Accepts classified failures
        - Consults recovery policy
        - Checks budgets
        - Constructs recovery plan
        - Validates plan safety
        - Invokes existing authority hooks (not creating new ones)
        - Tracks progress and handles cancellation/timeout
        - Runs post-recovery verification
    
    MUST NOT:
        - Invent domain-specific repair operations
        - Create duplicate lifecycle, state, or scheduling authority
        - Make autonomous decisions about capability semantics
    
    Usage:
        class MyRecoveryCoordinator(RecoveryCoordinator):
            async def handle_failure(self, failure: FailureRecord) -> RecoveryExecutionResult:
                # 1. Evaluate policy
                decision = self.policy.evaluate(failure)
                
                if not decision.permit_recovery:
                    return RecoveryExecutionResult(
                        result=RecoveryResult.SKIPPED,
                        failure_record=failure
                    )
                
                # 2. Check budget
                budget = self.get_budget(failure.source_entity_id)
                if not budget.can_attempt():
                    return RecoveryExecutionResult(
                        result=RecoveryResult.FAILURE,
                        failure_record=failure
                    )
                
                # 3. Create and execute plan
                plan = RecoveryPlan.create(failure, failure.source_entity_id)
                
                return await self.execute_plan(plan)
        
        coordinator = MyRecoveryCoordinator(policy=my_policy)
    """
    
    def __init__(self) -> None:
        self._budgets: Dict[str, RecoveryBudget] = {}
        self._active_recoveries: Dict[str, RecoveryPlan] = {}
    
    async def handle_failure(self, failure: "FailureRecord") -> RecoveryExecutionResult:
        """
        Handle a new failure.
        
        This is the main entry point for recovery coordination.
        
        Args:
            failure: The failure to recover from
            
        Returns:
            Result of the recovery attempt
        """
        raise NotImplementedError
    
    async def execute_plan(self, plan: RecoveryPlan) -> RecoveryExecutionResult:
        """
        Execute a recovery plan.
        
        Args:
            plan: The plan to execute
            
        Returns:
            Execution result with outcome and metrics
        """
        raise NotImplementedError
    
    def get_budget(self, subject: str) -> RecoveryBudget:
        """Get or create budget for a subject."""
        if subject not in self._budgets:
            self._budgets[subject] = RecoveryBudget(
                budget_id=f"budget_{subject}_{time.monotonic_ns()}",
                subject=subject
            )
        return self._budgets[subject]
    
    def record_active_recovery(self, recovery_id: str, plan: RecoveryPlan) -> None:
        """Track an active recovery."""
        self._active_recoveries[recovery_id] = plan
    
    def remove_active_recovery(self, recovery_id: str) -> Optional[RecoveryPlan]:
        """Remove and return a completed recovery."""
        return self._active_recoveries.pop(recovery_id, None)


__all__ = [
    # Recovery actions
    "RecoveryAction",
    
    # Policies
    "RecoveryPolicy",
    "RecoveryPolicyEvaluator",
    "RecoveryDecision",
    
    # Plans
    "RecoveryPlan",
    "Precondition",
    
    # Budgets and loop prevention
    "RecoveryBudget",
    
    # Results
    "RecoveryResult",
    "RecoveryExecutionResult",
    
    # Coordination
    "RecoveryCoordinator",
]