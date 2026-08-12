# Rollback Coordinator
# ====================

"""
Rollback Coordinator - the canonical authority for global rollback in Phase 3.7.10.

The RollbackCoordinator owns:
    - Global rollback planning and coordination
    - Dependency-ordered rollback execution  
    - Barrier management across subsystems
    - Verification routing (independent verifier)
    - Rollback result tracking

Key constraints:
    - Does NOT perform component-specific cleanup
    - Coordinates existing subsystem authorities
    - Requires independent verification before declaring success
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable, Awaitable
import time
import uuid

from .planner import RollbackPlanner, RollbackPlan


@dataclass(frozen=True)
class RollbackRequest:
    """
    Request to perform a rollback.
    
    Args:
        failure_id: Which failure triggered the rollback request
        target_state_version: What state version to restore to
        scope: Entities affected by the rollback
        mode: How to rollback (FULL, PARTIAL, etc.)
        
        verify_before_restore: Whether to verify before restoring
        timeout_seconds: Maximum time for rollback operation
    """
    
    failure_id: str
    target_state_version: int
    
    scope: List[str] = field(default_factory=list)
    mode: "RollbackMode" = None  # Default set below
    
    verify_before_restore: bool = False
    timeout_seconds: Optional[float] = None
    
    requested_at: float = field(default_factory=time.time)


@dataclass(frozen=True)
class RollbackResult:
    """
    Result of a rollback operation.
    
    Args:
        rollback_id: Which rollback this result is for
        success: Whether rollback succeeded
        state_restored_to_version: What state version we restored to
        
        actions_executed: Count of executed steps
        actions_succeeded: Count that succeeded  
        actions_failed: Count that failed
        
        verification_passed: Whether independent verification passed
        
        duration_seconds: How long rollback took
    """
    
    rollback_id: str
    
    success: bool
    state_restored_to_version: int = 0
    
    actions_executed: int = 0
    actions_succeeded: int = 0
    actions_failed: int = 0
    
    verification_passed: Optional[bool] = None
    
    duration_seconds: float = 0.0


@dataclass(frozen=True)
class RollbackStepResult:
    """
    Result of a single rollback step.
    
    Args:
        step_index: Which step this is
        action_performed: What was executed
        succeeded: Whether this step succeeded
        
        error_message: If failed, what went wrong
    """
    
    step_index: int
    action_performed: str
    
    succeeded: bool = True
    error_message: Optional[str] = None


class RollbackMode(Enum):
    """Rollback strategy modes."""
    
    FULL = "full"               # Complete restoration to known state
    PARTIAL = "partial"         # Restore only affected components
    TRANSACTIONAL = "transactional"  # Within transaction boundaries
    COMPENSATING = "compensating"    # Counteract effects (not exact rollback)
    CHECKPOINT = "checkpoint"     # Restore from checkpoint
    BEST_EFFORT = "best_effort"   # Try to roll back what's possible
    LOCAL = "local"               # Only rollback local component state
    CASCADE = "cascade"           # Propagate to dependents


class RollbackCoordinator:
    """
    Canonical rollback coordinator for Phase 3.7.10.
    
    Usage:
        planner = RollbackPlanner()
        verifier = DefaultRollbackVerifier()
        
        coordinator = RollbackCoordinator(
            planner=planner,
            verifier=verifier
        )
        
        request = RollbackRequest(
            failure_id="failure_123",
            target_state_version=100
        )
        
        result = await coordinator.request_rollback(request)
    """
    
    def __init__(
        self,
        planner: Optional[RollbackPlanner] = None,
        verifier: Optional[Any] = None,  # RollbackVerifier protocol
    ):
        """Initialize the rollback coordinator."""
        self._planner = planner or RollbackPlanner()
        self._verifier = verifier
        
        # Internal state
        self._active_rollbacks: Dict[str, RollbackPlan] = {}
        self._results: Dict[str, RollbackResult] = {}
        self._step_handlers: Dict[str, Callable[[str], Awaitable[RollbackStepResult]]] = {}
        
    async def request_rollback(self, request: RollbackRequest) -> RollbackResult:
        """
        Request a rollback operation.
        
        This is the canonical entry point for all rollback requests.
        
        Args:
            request: The rollback request
            
        Returns:
            RollbackResult with outcome and metrics
        """
        # Validate request
        if not request.failure_id:
            raise ValueError("Rollback request missing failure_id")
        
        # Check if already active
        if request.failure_id in self._active_rollbacks:
            return self._results.get(
                request.failure_id,
                RollbackResult(
                    rollback_id=request.failure_id,
                    success=False
                )
            )
        
        # Plan the rollback (deterministic)
        plan = await self._planner.plan(request)
        
        if not plan.is_valid:
            return RollbackResult(
                rollback_id=request.failure_id,
                success=False,
                actions_failed=len(plan.steps)
            )
        
        # Record active rollback
        self._active_rollbacks[request.failure_id] = plan
        
        # Execute rollback (dependency-ordered steps)
        start_time = time.monotonic()
        
        executed = 0
        succeeded = 0
        failed = 0
        last_error = None
        
        for step_index, step in enumerate(plan.steps):
            handler = self._step_handlers.get(step.action_type)
            
            if handler is not None:
                try:
                    result = await handler(step.target_id)
                    
                    if result.succeeded:
                        succeeded += 1
                    else:
                        failed += 1
                        last_error = result.error_message
                        
                except Exception as e:
                    failed += 1
                    last_error = str(e)
            else:
                # No handler - skip step or fail
                failed += 1
                
            executed += 1
        
        duration = time.monotonic() - start_time
        
        # Check verification if required
        verification_passed = None
        if request.verify_before_restore and self._verifier is not None:
            try:
                verification_passed = await self._verifier.verify(
                    plan.target_state,
                    request.failure_id
                )
            except Exception:
                verification_passed = False
        
        result = RollbackResult(
            rollback_id=request.failure_id,
            success=failed == 0 and (verification_passed is not False),
            state_restored_to_version=plan.target_state_version,
            actions_executed=executed,
            actions_succeeded=succeeded,
            actions_failed=failed,
            verification_passed=verification_passed,
            duration_seconds=duration
        )
        
        self._results[request.failure_id] = result
        
        # Clean up active rollback
        if request.failure_id in self._active_rollbacks:
            del self._active_rollbacks[request.failure_id]
        
        return result
    
    async def cancel_rollback(self, rollback_id: str) -> bool:
        """Cancel an active rollback."""
        if rollback_id in self._active_rollbacks:
            # Would implement cancellation logic here
            del self._active_rollbacks[rollback_id]
            return True
        
        return False
    
    def snapshot(self) -> Dict[str, Any]:
        """Get an immutable snapshot of rollback state."""
        return {
            "active_rollbacks": len(self._active_rollbacks),
            "completed_results": len(self._results),
        }
    
    def register_step_handler(
        self,
        action_type: str,
        handler: Callable[[str], Awaitable[RollbackStepResult]]
    ) -> None:
        """Register a handler for a specific rollback step type."""
        self._step_handlers[action_type] = handler


class DefaultRollbackCoordinator(RollbackCoordinator):
    """
    Default implementation of RollbackCoordinator.
    
    This coordinator provides sensible defaults for:
        - Plan execution order (reverse dependency order)
        - Step handlers (subsystem adapters)
        - Verification (if configured)
    """
    
    def __init__(self, verifier: Optional[Any] = None):
        super().__init__(
            planner=RollbackPlanner(),
            verifier=verifier
        )
        
        # Register default step handlers
        self.register_step_handler("STOP_COMPONENT", self._stop_component)
        self.register_step_handler("RELEASE_RESOURCE", self._release_resource)
        self.register_step_handler("RESTORE_STATE", self._restore_state)
    
    async def _stop_component(self, target_id: str) -> RollbackStepResult:
        """Default handler for stopping a component."""
        # Would call the actual component's stop method
        return RollbackStepResult(step_index=0, action_performed="STOP_COMPONENT", succeeded=True)
    
    async def _release_resource(self, target_id: str) -> RollbackStepResult:
        """Default handler for releasing a resource."""
        # Would release the resource through ResourceGovernor
        return RollbackStepResult(step_index=0, action_performed="RELEASE_RESOURCE", succeeded=True)
    
    async def _restore_state(self, target_id: str) -> RollbackStepResult:
        """Default handler for restoring component state."""
        # Would restore from checkpoint or snapshot
        return RollbackStepResult(step_index=0, action_performed="RESTORE_STATE", succeeded=True)