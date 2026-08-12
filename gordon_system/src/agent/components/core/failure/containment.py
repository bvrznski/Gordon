# Failure Containment
# ===================

"""
Failure containment for Phase 3.7.10.

Containment prevents uncontrolled propagation of failures:
    - Isolates affected components from the rest of the system
    - Prevents cascade failures to dependent subsystems  
    - Preserves evidence for root cause analysis
    - Enables recovery in a safe, bounded scope

The containment authority is part of FailureCoordinator.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable, Awaitable
import time


# =============================================================================
# Containment Types
# =============================================================================

@dataclass(frozen=True)
class ContainmentRequest:
    """
    Request to contain a failure.
    
    Args:
        failure_id: Which failure to contain
        scope: Entities to isolate (entity IDs)
        actions: Specific containment actions to take
        timeout_seconds: How long containment should last
        priority: Containment priority (affects ordering)
    """
    
    failure_id: str
    scope: List[str]  # Affected entity IDs
    
    actions: List["ContainmentAction"] = field(default_factory=list)
    
    timeout_seconds: Optional[float] = None  # None = until manually released
    priority: int = 0  # Higher = more urgent
    
    requested_at: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ContainmentPlan:
    """
    A containment plan for a specific failure.
    
    Args:
        containment_id: Unique identifier for this containment operation
        failure_id: The failure being contained
        scope: Entities affected by the plan
        barrier_required: Whether to wait at containment boundary
        verification_required: Whether verification is needed before proceeding
        
        actions: Ordered list of containment actions to execute
    """
    
    containment_id: str
    
    failure_id: str
    scope: List[str]
    
    barrier_required: bool = True
    verification_required: bool = False
    
    actions: List["ContainmentAction"] = field(default_factory=list)


@dataclass(frozen=True)
class ContainmentAction:
    """
    A single containment action.
    
    Actions are executed in order as part of a containment plan.
    
    Types of containment actions:
        - STOP_ADMISSION: Prevent new work from being admitted
        - WITHDRAW_CAPABILITY: Remove capability publication
        - QUARANTINE_ENTITY: Isolate specific entity
        - CANCEL_TASKS: Cancel affected tasks
        - REVOKE_RESOURCE: Release resource lease
        - CLOSE_CONNECTION: Close network/database connections
        - FREEZE_QUEUE: Stop queue processing for affected partition
    """
    
    action_id: str
    
    action_type: "ContainmentActionType"
    
    target_id: Optional[str] = None  # Entity to act on (None = all in scope)
    
    # Action-specific parameters
    timeout_seconds: Optional[float] = None
    priority: int = 0
    
    # Verification requirements
    requires_verification: bool = False
    verification_predicate: Optional[Callable[[Any], bool]] = None


class ContainmentActionType(Enum):
    """Types of containment actions."""
    
    STOP_ADMISSION = "stop_admission"
    WITHDRAW_CAPABILITY = "withdraw_capability"
    QUARANTINE_ENTITY = "quarantine_entity"
    CANCEL_TASKS = "cancel_tasks"
    REVOKE_RESOURCE = "revoke_resource"
    CLOSE_CONNECTION = "close_connection"
    FREEZE_QUEUE = "freeze_queue"
    ISOLATE_GPU = "isolate_gpu"
    DISABLE_MODEL_ROUTING = "disable_model_routing"


@dataclass(frozen=True)
class ContainmentBarrier:
    """
    A barrier to synchronize containment completion.
    
    Barriers ensure all containment actions complete before proceeding
    to recovery operations.
    
    Args:
        barrier_id: Unique identifier
        expected_parties: How many entities must signal completion
        timeout_seconds: How long to wait
    """
    
    barrier_id: str
    
    expected_parties: int = 1
    completed_parties: List[str] = field(default_factory=list)
    
    timeout_seconds: Optional[float] = None


@dataclass(frozen=True)
class ContainmentResult:
    """
    Result of a containment operation.
    
    Args:
        containment_id: Which containment this is for
        success: Whether containment succeeded
        scope_affected: How many entities in scope were affected
        scope_total: Total entities in scope
        
        actions_executed: Count of executed actions
        actions_succeeded: Count that succeeded
        actions_failed: Count that failed
        
        verification_passed: Whether verification passed (if required)
        
        containment_duration_seconds: Time spent in containment
    """
    
    containment_id: str
    
    success: bool
    
    scope_affected: int = 0
    scope_total: int = 0
    
    actions_executed: int = 0
    actions_succeeded: int = 0
    actions_failed: int = 0
    
    verification_passed: Optional[bool] = None
    
    containment_duration_seconds: float = 0.0


@dataclass(frozen=True)
class ContainmentStatus:
    """
    Current status of containment for a failure.
    
    Args:
        failure_id: Which failure is being contained
        active_containments: List of active containment IDs
        containment_count: Total number of active containments
        total_scope_size: Total affected entities across all containments
        
        barrier_status: Status of any active barriers
        verification_status: Verification state (pending/required/failed/passed)
    """
    
    failure_id: str
    
    active_containments: List[str] = field(default_factory=list)
    containment_count: int = 0
    total_scope_size: int = 0
    
    barrier_status: Optional["ContainmentBarrier"] = None
    verification_status: Optional["VerificationStatus"] = None


class VerificationStatus(Enum):
    """Containment verification status."""
    
    NOT_REQUIRED = "not_required"
    PENDING = "pending"  # Waiting for verification
    REQUIRED = "required"  # Verification needed but not started
    FAILED = "failed"  # Verification failed
    PASSED = "passed"  # Verification succeeded


# =============================================================================
# Containment Coordinator Interface
# =============================================================================

class ContainmentCoordinator:
    """
    Interface for containment coordination.
    
    This is the authority responsible for:
        - Accepting containment requests
        - Building containment plans
        - Executing containment actions in order
        - Managing barriers and verification
    
    The coordinator does NOT perform subsystem-specific cleanup.
    It coordinates existing subsystem authorities to act on containment orders.
    """
    
    async def request_containment(
        self,
        failure_id: str,
        scope: List[str],
        timeout_seconds: Optional[float] = None
    ) -> ContainmentResult:
        """
        Request containment for a failure.
        
        Args:
            failure_id: ID of the failure to contain
            scope: Entity IDs to isolate
            timeout_seconds: How long to wait for containment
            
        Returns:
            ContainmentResult with outcome and metrics
        """
        raise NotImplementedError
    
    async def execute_containment_plan(
        self,
        plan: ContainmentPlan
    ) -> ContainmentResult:
        """
        Execute a containment plan.
        
        Args:
            plan: The plan to execute
            
        Returns:
            Result of the containment operation
        """
        raise NotImplementedError
    
    async def release_containment(self, failure_id: str) -> bool:
        """
        Release containment for a failure (after recovery).
        
        Args:
            failure_id: ID of the failure
            
        Returns:
            True if successfully released
        """
        raise NotImplementedError
    
    async def wait_for_barrier(
        self,
        barrier: ContainmentBarrier
    ) -> bool:
        """
        Wait for a containment barrier to be satisfied.
        
        Args:
            barrier: The barrier to wait on
            
        Returns:
            True if barrier was satisfied, False if timeout
        """
        raise NotImplementedError
    
    def get_containment_status(self, failure_id: str) -> ContainmentStatus:
        """Get current containment status for a failure."""
        raise NotImplementedError


# =============================================================================
# Default Containment Coordinator Implementation
# =============================================================================

class DefaultContainmentCoordinator(ContainmentCoordinator):
    """
    Default implementation of ContainmentCoordinator.
    
    This coordinator:
        - Maintains active containments per failure
        - Tracks scope and actions
        - Manages barriers with timeout support
        - Performs verification if required
        
    The coordinator delegates to subsystem-specific adapters for actual
    containment actions (not implementing them directly).
    """
    
    def __init__(self) -> None:
        self._containments: Dict[str, ContainmentStatus] = {}
        self._barriers: Dict[str, ContainmentBarrier] = {}
        self._action_handlers: Dict[ContainmentActionType, Callable[[str], Awaitable[bool]]] = {}
    
    def register_action_handler(
        self,
        action_type: ContainmentActionType,
        handler: Callable[[str], Awaitable[bool]]
    ) -> None:
        """Register a handler for a specific containment action type."""
        self._action_handlers[action_type] = handler
    
    async def request_containment(
        self,
        failure_id: str,
        scope: List[str],
        timeout_seconds: Optional[float] = None
    ) -> ContainmentResult:
        """
        Request containment for a failure.
        
        Creates or updates a containment status and executes actions.
        """
        # Check if already contained
        current_status = self._containments.get(failure_id)
        
        if current_status is not None:
            # Update existing containment scope
            existing_scope = set(current_status.scope_affected)
            new_scope = set(scope) - existing_scope
            
            if not new_scope:
                return ContainmentResult(
                    containment_id=failure_id,
                    success=True,
                    scope_affected=current_status.total_scope_size,
                    scope_total=current_status.total_scope_size
                )
            
            # Add new scope to containment
            scope = list(existing_scope | set(scope))
        
        # Build plan with default actions based on scope
        actions = [
            ContainmentAction(
                action_id=f"action_{i}",
                action_type=ContainmentActionType.QUARANTINE_ENTITY,
                target_id=entity_id,
                requires_verification=True
            )
            for i, entity_id in enumerate(scope[:10])  # Limit to first 10
        ]
        
        plan = ContainmentPlan(
            containment_id=failure_id,
            failure_id=failure_id,
            scope=list(scope),
            actions=actions,
            barrier_required=True,
            verification_required=True
        )
        
        return await self.execute_containment_plan(plan)
    
    async def execute_containment_plan(self, plan: ContainmentPlan) -> ContainmentResult:
        """Execute a containment plan with ordered actions."""
        start_time = time.monotonic()
        
        executed = 0
        succeeded = 0
        failed = 0
        
        for action in plan.actions:
            handler = self._action_handlers.get(action.action_type)
            
            if handler is None:
                # No handler registered - skip or fail based on requirement
                failed += 1
                continue
            
            try:
                target_id = action.target_id or "default"
                result = await handler(target_id)
                
                if result:
                    succeeded += 1
                else:
                    failed += 1
                    
            except Exception:
                failed += 1
                
            executed += 1
        
        # Check verification if required
        verification_passed = None
        if plan.verification_required:
            verification_passed = succeeded == len(plan.actions) and succeeded > 0
        
        duration = time.monotonic() - start_time
        
        return ContainmentResult(
            containment_id=plan.containment_id,
            success=failed == 0,
            scope_affected=succeeded,
            scope_total=len(plan.actions),
            actions_executed=executed,
            actions_succeeded=succeeded,
            actions_failed=failed,
            verification_passed=verification_passed,
            containment_duration_seconds=duration
        )
    
    async def release_containment(self, failure_id: str) -> bool:
        """Release containment for a failure."""
        if failure_id in self._containments:
            del self._containments[failure_id]
        
        # Clean up barrier if exists
        if failure_id in self._barriers:
            del self._barriers[failure_id]
        
        return True
    
    async def wait_for_barrier(self, barrier: ContainmentBarrier) -> bool:
        """Wait for a containment barrier with timeout."""
        # Simplified implementation - would use proper synchronization primitives
        expected = barrier.expected_parties
        
        if len(barrier.completed_parties) >= expected:
            return True
        
        # Check timeout
        if barrier.timeout_seconds is not None:
            import asyncio
            try:
                await asyncio.sleep(min(0.1, barrier.timeout_seconds))
            except asyncio.CancelledError:
                return False
            
            return len(barrier.completed_parties) >= expected
        
        # No timeout - wait indefinitely (would use proper synchronization)
        while len(barrier.completed_parties) < expected:
            import time
            time.sleep(0.01)
        
        return True
    
    def get_containment_status(self, failure_id: str) -> ContainmentStatus:
        """Get current containment status for a failure."""
        if failure_id in self._containments:
            return self._containments[failure_id]
        
        return ContainmentStatus(
            failure_id=failure_id,
            active_containments=[],
            containment_count=0,
            total_scope_size=0
        )