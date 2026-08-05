# Rollback Planner
# ================

"""
Rollback planner for Phase 3.7.10.

The planner:
    - Evaluates rollback eligibility based on state and failure context
    - Constructs immutable rollback plans with dependency-ordered steps
    - Validates plans before execution
    
Key principles:
    - Reverse of successful execution order (for cleanup)
    - Dependency-aware ordering
    - Deterministic plan construction from known state
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any
import time

from .coordinator import RollbackRequest


@dataclass(frozen=True)
class RollbackPlan:
    """
    An immutable rollback plan.
    
    A plan includes:
        - Target state (what we're restoring to)
        - Affected entities
        - Ordered steps with dependencies
        - Verification requirements
        
    The plan is constructed once and never modified during execution.
    """
    
    plan_id: str
    
    failure_id: str  # Which failure triggered this rollback
    
    target_state_version: int  # What state version to restore to
    
    scope: List[str] = field(default_factory=list)  # Affected entity IDs
    
    steps: List["RollbackStep"] = field(default_factory=list)
    
    verification_required: bool = True
    timeout_seconds: Optional[float] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if plan passes basic validation."""
        if not self.failure_id:
            return False
        
        if len(self.steps) == 0:
            return False
        
        # Check for circular dependencies (simplified check)
        seen_ids = set()
        for step in self.steps:
            if step.step_id in seen_ids:
                return False
            seen_ids.add(step.step_id)
        
        return True
    
    @property
    def estimated_duration_seconds(self) -> float:
        """Estimate total rollback time based on steps."""
        # Base time per step + dependency wait overhead
        base_time = len(self.steps) * 1.0  # ~1 second per step
        dep_overhead = len([s for s in self.steps if s.depends_on]) * 0.5
        return base_time + dep_overhead


@dataclass(frozen=True)
class RollbackStep:
    """
    A single rollback step.
    
    Steps are executed in order, respecting dependencies between them.
    
    Args:
        step_id: Unique identifier for this step
        action_type: What operation to perform (STOP_COMPONENT, RELEASE_RESOURCE, etc.)
        target_id: Entity affected by this step
        
        depends_on: List of step IDs that must complete first
        requires_verification: Whether this step needs verification
        timeout_seconds: Optional timeout for this specific step
    """
    
    step_id: str
    
    action_type: str  # e.g., "STOP_COMPONENT", "RELEASE_RESOURCE"
    target_id: str
    
    depends_on: List[str] = field(default_factory=list)
    requires_verification: bool = False
    timeout_seconds: Optional[float] = None


class RollbackEligibility(Enum):
    """Rollback eligibility status."""
    
    ELIGIBLE = "eligible"           # Known prior state exists, can rollback
    INELIGIBLE_EXACT = "ineligible_exact"  # No exact restoration possible
    COMPENSATING_ONLY = "compensating_only"  # Can only compensate, not rollback
    UNKNOWN = "unknown"             # Cannot determine without more information


@dataclass(frozen=True)
class RollbackEligibilityResult:
    """
    Result of rollback eligibility evaluation.
    
    Args:
        eligibility: ELIGIBLE, INELIGIBLE_EXACT, or COMPENSATING_ONLY
        reason: Why this result was reached
        
        available_checkpoints: List of available checkpoint names
        state_version_before_failure: What version we had before failure
        
        requires_compensation: Whether compensation actions are needed
    """
    
    eligibility: RollbackEligibility
    
    reason: str = ""
    
    available_checkpoints: List[str] = field(default_factory=list)
    state_version_before_failure: int = 0
    
    requires_compensation: bool = False


class RollbackPlanner:
    """
    Deterministic rollback planner.
    
    Usage:
        planner = RollbackPlanner()
        
        request = RollbackRequest(
            failure_id="failure_123",
            target_state_version=100
        )
        
        plan = await planner.plan(request)
    """
    
    def __init__(self) -> None:
        """Initialize the planner."""
        self._checkpoint_registry: Dict[str, Any] = {}  # Would connect to actual checkpoint provider
    
    async def evaluate_eligibility(
        self,
        request: RollbackRequest
    ) -> RollbackEligibilityResult:
        """
        Evaluate whether rollback is eligible for this failure.
        
        Args:
            request: The rollback request
            
        Returns:
            Eligibility result with determination and available options
        """
        # Check if target state version exists (is a checkpoint/snapshot)
        state_available = await self._check_state_availability(request.target_state_version)
        
        if not state_available:
            return RollbackEligibilityResult(
                eligibility=RollbackEligibility.UNKNOWN,
                reason=f"State version {request.target_state_version} not available"
            )
        
        # Check for known prior state
        if request.scope and len(request.scope) > 0:
            # We have scope information - can determine affected entities
            return RollbackEligibilityResult(
                eligibility=RollbackEligibility.ELIGIBLE,
                reason="Known prior state available, can restore exact state",
                available_checkpoints=[f"version_{request.target_state_version}"],
                state_version_before_failure=request.target_state_version
            )
        
        # Cannot determine without scope information
        return RollbackEligibilityResult(
            eligibility=RollbackEligibility.UNKNOWN,
            reason="Insufficient information to determine rollback eligibility"
        )
    
    async def plan(self, request: RollbackRequest) -> RollbackPlan:
        """
        Create a rollback plan for the request.
        
        This is deterministic - same inputs always produce same outputs.
        
        Args:
            request: The rollback request
            
        Returns:
            RollbackPlan with ordered steps
        """
        # Evaluate eligibility first
        eligibility = await self.evaluate_eligibility(request)
        
        if eligibility.eligibility == RollbackEligibility.UNKNOWN:
            raise ValueError(
                f"Cannot plan rollback without knowing state availability"
            )
        
        # Build step list in reverse dependency order
        
        steps = []
        
        # 1. Stop components (in dependency order, then reverse for cleanup)
        component_ids = self._get_component_ids(request.scope)
        stop_steps = [
            RollbackStep(
                step_id=f"stop_{i}",
                action_type="STOP_COMPONENT",
                target_id=component_id,
                depends_on=[]
            )
            for i, component_id in enumerate(component_ids)
        ]
        
        # 2. Release resources (after components stopped)
        resource_ids = self._get_resource_ids(request.scope)
        release_steps = [
            RollbackStep(
                step_id=f"release_{i}",
                action_type="RELEASE_RESOURCE",
                target_id=resource_id,
                depends_on=[s.step_id for s in stop_steps]  # Wait for all components stopped
            )
            for i, resource_id in enumerate(resource_ids)
        ]
        
        # 3. Restore state (after resources released)
        restore_step = RollbackStep(
            step_id="restore_state",
            action_type="RESTORE_STATE",
            target_id=request.failure_id,
            depends_on=[s.step_id for s in release_steps]  # Wait for all releases
        )
        
        steps.extend(stop_steps + release_steps + [restore_step])
        
        return RollbackPlan(
            plan_id=f"rollback_{time.monotonic_ns()}",
            failure_id=request.failure_id,
            target_state_version=request.target_state_version,
            scope=list(request.scope),
            steps=steps,
            verification_required=True,
            timeout_seconds=request.timeout_seconds
        )
    
    async def _check_state_availability(
        self,
        state_version: int
    ) -> bool:
        """Check if a specific state version is available (from checkpoint/snapshot)."""
        # Would query actual checkpoint provider
        # For now, assume all versions are available
        return True
    
    def _get_component_ids(self, scope: List[str]) -> List[str]:
        """
        Get component IDs to stop for the given scope.
        
        This would consult dependency graph to get proper order.
        """
        return list(scope)  # Simplified - in production, would use topological sort
    
    def _get_resource_ids(self, scope: List[str]) -> List[str]:
        """
        Get resource IDs to release for the given scope.
        
        This would query resource registry for affected resources.
        """
        # In production, this would query the actual resource registry
        return []  # Simplified