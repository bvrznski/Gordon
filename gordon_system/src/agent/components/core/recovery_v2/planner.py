# Recovery Planner
# ================

"""
Recovery planner for Phase 3.7.10.

The planner:
    - Evaluates recovery eligibility based on failure classification
    - Constructs immutable recovery plans with ordered steps
    - Validates plans before execution
    
Plans may include:
    - Containment confirmation
    - Quiescence (stopping admission, canceling tasks)
    - State capture (for potential rollback)
    - Rollback actions (if eligible)
    - Resource reacquisition  
    - Component reconstruction/restart
    - Verification steps
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any
import time

# Import from failure module for type references
from ..failure.types import FailureKind

from .coordinator import RecoveryRequest


@dataclass(frozen=True)
class RecoveryPlan:
    """
    An immutable recovery plan.
    
    Args:
        plan_id: Unique identifier for this plan
        failure_id: Which failure triggered recovery
        
        target_state: What state we're recovering to (healthy, degraded, etc.)
        
        phases: Ordered list of recovery phases
        steps: All individual recovery steps
        dependencies: Step dependency graph
        
        verification_required: Whether independent verification is required
        timeout_seconds: Maximum time for recovery operation
    """
    
    plan_id: str
    
    failure_id: str  # Which failure triggered recovery
    
    target_state: "RecoveryTargetState" = None  # Default set below
    
    phases: List["RecoveryPhase"] = field(default_factory=list)
    steps: List["RecoveryStep"] = field(default_factory=list)
    
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    
    verification_required: bool = True
    timeout_seconds: Optional[float] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if plan passes basic validation."""
        if not self.failure_id:
            return False
        
        # Must have at least one step
        if len(self.steps) == 0:
            return False
        
        # All dependencies must reference existing steps
        all_step_ids = {s.step_id for s in self.steps}
        for deps in self.dependencies.values():
            for dep in deps:
                if dep not in all_step_ids:
                    return False
        
        return True
    
    @property
    def estimated_duration_seconds(self) -> float:
        """Estimate total recovery time."""
        # Base time per step + dependency wait overhead
        base_time = len(self.steps) * 2.0  # ~2 seconds per step
        dep_overhead = sum(len(deps) for deps in self.dependencies.values()) * 0.5
        return base_time + dep_overhead


@dataclass(frozen=True)
class RecoveryStep:
    """
    A single recovery step.
    
    Args:
        step_id: Unique identifier for this step
        action_type: What operation to perform
        target_id: Entity affected by this step
        
        depends_on: Step IDs that must complete first
        timeout_seconds: Optional timeout for this step
        requires_verification: Whether verification is needed
    """
    
    step_id: str
    
    action_type: str  # e.g., "QUIESCE", "CAPTURE_STATE", "RESTART_COMPONENT"
    target_id: str
    
    depends_on: List[str] = field(default_factory=list)
    timeout_seconds: Optional[float] = None
    requires_verification: bool = False


class RecoveryPhase(Enum):
    """Recovery phases in order."""
    
    CONTAINMENT = "containment"         # Confirm or establish containment
    QUIESCE = "quiesce"                 # Stop admission, cancel tasks
    CAPTURE_STATE = "capture_state"     # Capture current state for rollback
    ROLLBACK = "rollback"               # Rollback if eligible
    REACQUIRE_RESOURCES = "reacquire_resources"  # Get resources back
    RECONSTRUCT = "reconstruct"         # Build fresh component instances
    VERIFY = "verify"                   # Verify target state restored


@dataclass(frozen=True)
class RecoveryTargetState:
    """Target state for recovery."""
    
    target_state: str  # e.g., "healthy", "degraded"
    components_affected: List[str] = field(default_factory=list)
    degraded_components: List[str] = field(default_factory=list)


class RecoveryEligibility(Enum):
    """Recovery eligibility status."""
    
    ELIGIBLE = "eligible"           # Can attempt recovery
    INELIGIBLE_TRANSIENT = "ineligible_transient"  # Will recover naturally
    INELIGIBLE_PERMANENT = "ineligible_permanent"  # Cannot recover, needs fix
    UNKNOWN = "unknown"             # Need more information


@dataclass(frozen=True)
class RecoveryEligibilityResult:
    """
    Result of recovery eligibility evaluation.
    
    Args:
        eligibility: ELIGIBLE or INELIGIBLE
        reason: Why this result was reached
        
        suggested_policy: Which recovery policy to use
        estimated_budget_remaining: How much budget is left
    """
    
    eligibility: RecoveryEligibility
    reason: str = ""
    
    suggested_policy: Optional[str] = None
    estimated_budget_remaining: int = 0


class RecoveryPlanner:
    """
    Deterministic recovery planner.
    
    Usage:
        planner = RecoveryPlanner()
        
        request = RecoveryRequest(
            failure_id="failure_123",
            classification_result=classification
        )
        
        plan = await planner.plan(request)
    """
    
    def __init__(self) -> None:
        """Initialize the planner."""
        self._phase_order: List[RecoveryPhase] = [
            RecoveryPhase.CONTAINMENT,
            RecoveryPhase.QUIESCE,
            RecoveryPhase.CAPTURE_STATE,
            RecoveryPhase.ROLLBACK,
            RecoveryPhase.REACQUIRE_RESOURCES,
            RecoveryPhase.RECONSTRUCT,
            RecoveryPhase.VERIFY
        ]
    
    async def evaluate_eligibility(
        self,
        request: RecoveryRequest
    ) -> RecoveryEligibilityResult:
        """
        Evaluate whether recovery is eligible for this failure.
        
        Args:
            request: The recovery request
            
        Returns:
            Eligibility result with determination and suggested policy
        """
        classification = request.classification_result
        
        if classification is None:
            return RecoveryEligibilityResult(
                eligibility=RecoveryEligibility.UNKNOWN,
                reason="No classification available"
            )
        
        # Check for permanent failures
        if classification.kind in (FailureKind.FATAL, FailureKind.PANIC):
            return RecoveryEligibilityResult(
                eligibility=RecoveryEligibility.INELIGIBLE_PERMANENT,
                reason=f"Fatal failure: {classification.kind.value}"
            )
        
        # Check for programming/configuration issues
        if classification.kind in (FailureKind.PROGRAMMING, FailureKind.CONFIGURATION):
            return RecoveryEligibilityResult(
                eligibility=RecoveryEligibility.INELIGIBLE_PERMANENT,
                reason="Requires manual intervention"
            )
        
        # Check budget
        budget_remaining = request.budget_remaining or 3
        
        if budget_remaining <= 0:
            return RecoveryEligibilityResult(
                eligibility=RecoveryEligibility.INELIGIBLE_TRANSIENT,
                reason="Budget exhausted",
                estimated_budget_remaining=budget_remaining
            )
        
        # At least one recovery path available?
        has_retry = classification.retryability is True
        has_rollback = classification.rollback_eligibility is True
        
        if not has_retry and not has_rollback:
            return RecoveryEligibilityResult(
                eligibility=RecoveryEligibility.INELIGIBLE_TRANSIENT,
                reason="No recovery path available (no retry, no rollback)"
            )
        
        return RecoveryEligibilityResult(
            eligibility=RecoveryEligibility.ELIGIBLE,
            reason="Can attempt recovery",
            suggested_policy="RETRY" if has_retry else "ROLLBACK",
            estimated_budget_remaining=budget_remaining
        )
    
    async def plan(self, request: RecoveryRequest) -> RecoveryPlan:
        """
        Create a recovery plan for the request.
        
        Args:
            request: The recovery request
            
        Returns:
            RecoveryPlan with ordered steps
        """
        # Evaluate eligibility first
        eligibility = await self.evaluate_eligibility(request)
        
        if eligibility.eligibility != RecoveryEligibility.ELIGIBLE:
            raise ValueError(
                f"Recovery not eligible: {eligibility.reason}"
            )
        
        # Build plan phases in order
        steps = []
        dependencies: Dict[str, List[str]] = {}
        step_id_counter = 0
        
        def make_step(action_type: str, target_id: str) -> RecoveryStep:
            nonlocal step_id_counter
            step = RecoveryStep(
                step_id=f"step_{step_id_counter}",
                action_type=action_type,
                target_id=target_id
            )
            step_id_counter += 1
            return step
        
        # Phase 1: Containment (if needed)
        if request.classification_result and request.classification_result.containment_requirement:
            containment_step = make_step("VERIFY_CONTAINMENT", request.failure_id)
            steps.append(containment_step)
        
        # Phase 2: Quiesce
        quiesce_step = make_step("QUIESCE_ADMISSION", "runtime")
        steps.append(quiesce_step)
        
        # Phase 3: Capture state (for rollback if needed later)
        capture_step = make_step("CAPTURE_STATE", request.failure_id)
        steps.append(capture_step)
        dependencies[capture_step.step_id] = [quiesce_step.step_id]
        
        # Phase 4-6: Recovery actions based on classification
        classification = request.classification_result
        
        if classification and classification.rollback_eligibility is True:
            rollback_step = make_step("ROLLBACK", request.failure_id)
            steps.append(rollback_step)
            dependencies[rollback_step.step_id] = [capture_step.step_id]
            
            reacquire_step = make_step("REACQUIRE_RESOURCES", request.failure_id)
            steps.append(reacquire_step)
            dependencies[reacquire_step.step_id] = [rollback_step.step_id]
            
            verify_step = make_step("VERIFY_RESTORED_STATE", request.failure_id)
            steps.append(verify_step)
            dependencies[verify_step.step_id] = [reacquire_step.step_id]
        elif classification and classification.retryability is True:
            retry_steps = []
            for i in range(min(3, request.budget_remaining or 3)):
                retry_step = make_step("RETRY_OPERATION", f"operation_{i}")
                steps.append(retry_step)
                
                if retry_steps:
                    dependencies[retry_step.step_id] = [retry_steps[-1].step_id]
                else:
                    dependencies[retry_step.step_id] = [quiesce_step.step_id]
                
                retry_steps.append(retry_step)
            
            verify_step = make_step("VERIFY_RESTORED_STATE", request.failure_id)
            steps.append(verify_step)
            if retry_steps:
                dependencies[verify_step.step_id] = [retry_steps[-1].step_id]
        else:
            # Fallback: degraded recovery
            degrade_step = make_step("ENTER_DEGRADED_MODE", "runtime")
            steps.append(degrade_step)
        
        return RecoveryPlan(
            plan_id=f"recovery_{time.monotonic_ns()}",
            failure_id=request.failure_id,
            target_state=RecoveryTargetState(target_state="healthy"),
            phases=self._phase_order,
            steps=steps,
            dependencies=dependencies,
            verification_required=True
        )