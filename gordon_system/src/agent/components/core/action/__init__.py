# Action Runtime Infrastructure
# ===============================

"""
Canonical action execution runtime for Gordon Phase 3.7.26.

This module provides:

- Action request contracts (normalized work requests)
- Tool contracts (bounded operations)
- Effector contracts (side-effecting operations)
- Execution runtime (canonical dispatcher and invoker)
- Result contracts (structured outcomes)

Architecture:
    Goal / external request
        ↓
    Planning / decision authority (owns "what to do")
        ↓
    Action proposal
        ↓
    Authorization & policy evaluation (Phase 3.7.20+)
        ↓
    Validated action request
        ↓
    Tool/Effector selection
        ↓
    Execution runtime (THIS MODULE)
        ↓
    External side effect
        ↓
    Structured execution result
        ↓
    Observation / evaluation / memory

The Action Runtime does NOT:
    - Decide which action to take
    - Own planning or reasoning
    - Determine authorization policy
    - Interpret observations

It only executes validated actions deterministically.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Generic
from enum import Enum, auto
import uuid
import time

# Note: Core owns its own execution primitives.
# These types are defined in this module, not imported from execution:
#   - ActionId, InvocationId, ToolId, EffectorId (identifiers)
#   - ActionState, ExecutionStatus (execution states)
#   - TaskId is re-exported from core.execution for compatibility
#   - Priority is re-exported from core.execution for compatibility

from ..execution import (
    TaskId,
    Priority,
)

T = TypeVar("T")

# =============================================================================
# ACTION IDENTIFIERS
# =============================================================================


@dataclass(frozen=True)
class ActionId:
    """Unique identifier for an action."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "ActionId":
        """Generate a new unique action ID."""
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, ActionId):
            return self.value == other.value
        return False


@dataclass(frozen=True)
class InvocationId:
    """Unique identifier for a single invocation attempt."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "InvocationId":
        """Generate a new unique invocation ID."""
        return cls(value=f"{uuid.uuid4()}_{int(time.monotonic_ns())}")
    
    def __str__(self) -> str:
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ToolId:
    """Identifier for a tool."""
    
    value: str
    
    @classmethod
    def from_name(cls, name: str) -> "ToolId":
        """Create a ToolId from a name string."""
        return cls(value=name.lower().replace(" ", "_"))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class EffectorId:
    """Identifier for an effector."""
    
    value: str
    
    @classmethod
    def from_name(cls, name: str) -> "EffectorId":
        """Create an EffectorId from a name string."""
        return cls(value=name.lower().replace(" ", "_"))
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# ACTION STATES
# =============================================================================


class ActionState(Enum):
    """
    Action lifecycle states.
    
    States:
        CREATED → VALIDATING → REJECTED (if validation fails)
                ↓
            ADMITTED → QUEUED → RUNNING → [SUCCEEDED|FAILED]
                                              ↓
                                          CANCELLING → CANCELLED
    """
    
    # Initial state
    CREATED = "created"               # Action created but not yet validated
    
    # Validation states
    VALIDATING = "validating"         # Currently being validated
    REJECTED = "rejected"             # Validation failed (terminal)
    
    # Admission states
    ADMITTED = "admitted"             # Passed validation, admitted to queue
    QUEUED = "queued"                 # Waiting in execution queue
    
    # Execution states
    RUNNING = "running"               # Currently executing
    SUCCEEDED = "succeeded"           # Execution completed successfully
    FAILED = "failed"                 # Execution failed (terminal)
    
    # Cancellation states
    CANCELLING = "cancelling"         # Cancellation in progress
    CANCELLED = "cancelled"           # Cancellation complete (terminal)


# =============================================================================
# ACTION REQUEST CONTRACT
# =============================================================================


@dataclass(frozen=True)
class ActionRequest(Generic[T]):
    """
    Normalized action request for execution.
    
    This is the canonical contract that must be satisfied by all actions
    before they can be executed. It does NOT contain raw model output or
    unvalidated dictionaries.
    
    All fields are required unless marked as Optional with sensible defaults.
    """
    
    # Identity (required first)
    action_id: ActionId
    invocation_id: InvocationId
    
    # Tool/effector selection
    tool_id: Optional[ToolId] = None
    effector_id: Optional[EffectorId] = None
    operation: str = ""  # e.g., "read", "write", "delete"
    
    # Arguments (validated by schema before execution)
    arguments: Dict[str, Any] = field(default_factory=dict)
    
    # Context metadata
    originating_request_id: Optional[str] = None
    actor_id: Optional[str] = None  # Principal making the request
    authorization_context: Dict[str, Any] = field(default_factory=dict)
    
    # Execution parameters
    deadline_seconds: Optional[float] = None  # Total time limit
    priority: Priority = Priority.NORMAL
    timeout_seconds: Optional[float] = None  # Per-invocation timeout
    
    # Idempotency and retry control
    idempotency_key: Optional[str] = None
    max_attempts: int = 1
    retry_delay_seconds: float = 0.0
    
    # Resource requirements
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    
    # Expected result type (for validation)
    expected_result_type: str = "any"  # e.g., "string", "boolean", "file"
    
    # Risk classification
    risk_level: str = "low"  # low, medium, high, critical
    
    # Provenance
    created_at: float = field(default_factory=time.monotonic)
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolContract:
    """
    Contract defining a tool's capabilities and behavior.
    
    Tools are bounded operations that may or may not have side effects.
    """
    
    # Identity
    tool_id: ToolId
    name: str
    
    # Operation specification
    supported_operations: Tuple[str, ...]
    
    # Input schema (for validation)
    input_schema: Dict[str, Any]
    
    # Output schema (for result validation)
    output_schema: Dict[str, Any]
    
    # Behavior
    side_effect_class: str = "none"  # none, read, write, mutate
    is_idempotent: bool = False
    
    # Execution parameters
    timeout_seconds: float = 60.0
    concurrency_class: str = "concurrent"  # concurrent, serialized, isolated
    
    # Resource requirements
    cpu_required: Optional[float] = None  # millicores
    memory_required: Optional[int] = None  # bytes
    
    # Failure behavior
    failure_classification: str = "retryable"  # retryable, non_retryable


@dataclass(frozen=True)
class EffectorContract:
    """
    Contract defining an effector's side-effecting capabilities.
    
    Effectors cause external or embodied side effects in systems.
    They require stricter guarantees than pure tools.
    """
    
    # Identity
    effector_id: EffectorId
    name: str
    
    # Target domain (what system it affects)
    target_domain: str  # e.g., "filesystem", "network", "process"
    
    # Side effect classification
    side_effect_class: str  # read, write, mutate, delete, external
    reversibility: str = "unknown"  # reversible, partially_reversible, irreversible
    
    # Authorization requirements
    required_capability: Optional[str] = None
    required_permission: Optional[str] = None
    
    # Idempotency
    is_idempotent: bool = False
    
    # Execution parameters
    timeout_seconds: float = 60.0
    cancellation_policy: str = "cooperative"  # cooperative, forceful, none
    
    # Rollback support
    supports_rollback: bool = False
    rollback_operation: Optional[str] = None
    
    # Dry-run support
    supports_dry_run: bool = False


# =============================================================================
# EXECUTION RESULT CONTRACT
# =============================================================================


class ExecutionStatus(Enum):
    """Execution status categories."""
    
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


@dataclass(frozen=True)
class ExecutionResult(Generic[T]):
    """
    Normalized result of an action execution.
    
    This is the output contract - NOT the raw subprocess handle, SDK response,
    or privileged internal object. All results pass through this contract.
    """
    
    # Identity (required first)
    action_id: ActionId
    invocation_id: InvocationId
    
    # Execution status
    status: ExecutionStatus
    
    # Value or error (exclusive - only one set)
    value: Optional[T] = None
    error: Optional[str] = None
    
    # Timing
    started_at: float = field(default_factory=time.monotonic)
    completed_at: Optional[float] = None
    duration_seconds: Optional[float] = None
    
    # Side effect reporting (for effectors)
    side_effects_reported: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Retry information
    attempt_number: int = 1
    is_retry: bool = False
    
    # Warnings
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    
    # Resource usage
    cpu_seconds: Optional[float] = None
    memory_bytes: Optional[int] = None
    
    def mark_completed(self) -> "ExecutionResult[T]":
        """Mark result as completed (for mutable construction)."""
        if self.completed_at is None:
            return ExecutionResult(
                action_id=self.action_id,
                invocation_id=self.invocation_id,
                status=ExecutionStatus.SUCCEEDED,
                value=self.value,
                started_at=self.started_at,
                completed_at=time.monotonic(),
                duration_seconds=time.monotonic() - self.started_at,
                side_effects_reported=self.side_effects_reported,
                attempt_number=self.attempt_number,
                is_retry=self.is_retry,
                warnings=self.warnings,
            )
        return self
    
    def mark_failed(self, error: str) -> "ExecutionResult[T]":
        """Mark result as failed."""
        return ExecutionResult(
            action_id=self.action_id,
            invocation_id=self.invocation_id,
            status=ExecutionStatus.FAILED,
            error=error,
            started_at=self.started_at,
            completed_at=time.monotonic(),
            duration_seconds=time.monotonic() - self.started_at if self.started_at else 0.0,
        )
    
    def mark_cancelled(self, reason: str = "cancelled") -> "ExecutionResult[T]":
        """Mark result as cancelled."""
        return ExecutionResult(
            action_id=self.action_id,
            invocation_id=self.invocation_id,
            status=ExecutionStatus.CANCELLED,
            error=reason,
            started_at=self.started_at,
            completed_at=time.monotonic(),
        )


# =============================================================================
# ACTION EXECUTOR (CANONICAL AUTHORITY)
# =============================================================================


class ActionExecutor:
    """
    Canonical action execution authority for Phase 3.7.26.
    
    This is the single source of truth for executing actions in Gordon.
    It coordinates:
        - Validation
        - Admission control  
        - Dispatch to tool/effector
        - Timeout management
        - Cancellation propagation
        - Result normalization
        - Resource cleanup
    
    Invariants:
        1. Exactly one canonical executor per runtime
        2. All privileged actions pass through this authority
        3. Model output cannot bypass validation
        4. Results always use the ExecutionResult contract
        5. Side effects are reported truthfully
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # Tool/effector registries
        self._tools: Dict[ToolId, ToolContract] = {}
        self._effectors: Dict[EffectorId, EffectorContract] = {}
        
        # Execution tracking
        self._active_invocations: Dict[InvocationId, Any] = {}
        self._cancelled_invocations: set = set()
        
        # State
        self._is_running = True
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID."""
        return self._runtime_id
    
    # -------------------------------------------------------------------------
    # Tool/effector registration
    # -------------------------------------------------------------------------
    
    async def register_tool(self, contract: ToolContract) -> None:
        """Register a tool with the executor."""
        with self._lock:
            if contract.tool_id in self._tools:
                raise ValueError(f"Tool {contract.tool_id} already registered")
            self._tools[contract.tool_id] = contract
    
    async def unregister_tool(self, tool_id: ToolId) -> bool:
        """Unregister a tool. Returns True if registered."""
        with self._lock:
            if tool_id in self._tools:
                del self._tools[tool_id]
                return True
            return False
    
    async def register_effector(self, contract: EffectorContract) -> None:
        """Register an effector with the executor."""
        with self._lock:
            if contract.effector_id in self._effectors:
                raise ValueError(f"Effector {contract.effector_id} already registered")
            self._effectors[contract.effector_id] = contract
    
    async def unregister_effector(self, effector_id: EffectorId) -> bool:
        """Unregister an effector. Returns True if registered."""
        with self._lock:
            if effector_id in self._effectors:
                del self._effectors[effector_id]
                return True
            return False
    
    # -------------------------------------------------------------------------
    # Action execution
    # -------------------------------------------------------------------------
    
    async def execute(self, request: ActionRequest[T]) -> ExecutionResult[T]:
        """
        Execute an action.
        
        This is the canonical entry point for all privileged operations.
        It validates, admits, dispatches, and returns results.
        
        Args:
            request: The validated action request to execute
            
        Returns:
            Normalized execution result
            
        Raises:
            ValueError: If request is malformed
            RuntimeError: If executor is not running
        """
        if not self._is_running:
            raise RuntimeError("Executor is not running")
        
        # Validate required fields
        if request.action_id is None:
            raise ValueError("action_id is required")
        
        if request.invocation_id is None:
            raise ValueError("invocation_id is required")
        
        # Check tool/effector exists
        tool_or_effector = request.tool_id or request.effector_id
        if not tool_or_effector:
            raise ValueError("tool_id or effector_id must be specified")
        
        # Create invocation record
        invocation_id = request.invocation_id
        self._active_invocations[invocation_id] = {
            "request": request,
            "started_at": time.monotonic(),
        }
        
        try:
            # Dispatch to tool/effector implementation
            if request.tool_id and request.tool_id in self._tools:
                result = await self._execute_tool(request)
            elif request.effector_id and request.effector_id in self._effectors:
                result = await self._execute_effector(request)
            else:
                raise ValueError(f"Unknown tool/effector: {tool_or_effector}")
            
            return result
            
        finally:
            # Cleanup
            with self._lock:
                if invocation_id in self._active_invocations:
                    del self._active_invocations[invocation_id]
    
    async def _execute_tool(self, request: ActionRequest[T]) -> ExecutionResult[T]:
        """Execute a tool (no or minimal side effects)."""
        contract = self._tools.get(request.tool_id)
        
        if not contract:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error=f"Tool {request.tool_id} not registered",
            )
        
        # Execute with timeout
        try:
            import asyncio
            
            if request.timeout_seconds:
                result = await asyncio.wait_for(
                    self._invoke_tool_contract(request, contract),
                    timeout=request.timeout_seconds
                )
            else:
                result = await self._invoke_tool_contract(request, contract)
            
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.SUCCEEDED,
                value=result,
            )
            
        except asyncio.TimeoutError:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.TIMED_OUT,
                error=f"Tool execution exceeded {request.timeout_seconds}s timeout",
            )
    
    async def _execute_effector(self, request: ActionRequest[T]) -> ExecutionResult[T]:
        """Execute an effector (side-effecting operation)."""
        contract = self._effectors.get(request.effector_id)
        
        if not contract:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error=f"Effector {request.effector_id} not registered",
            )
        
        # Execute with timeout
        try:
            import asyncio
            
            if request.timeout_seconds:
                result = await asyncio.wait_for(
                    self._invoke_effector_contract(request, contract),
                    timeout=request.timeout_seconds
                )
            else:
                result = await self._invoke_effector_contract(request, contract)
            
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.SUCCEEDED,
                value=result,
                side_effects_reported=self._extract_side_effects(result),
            )
            
        except asyncio.TimeoutError:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.TIMED_OUT,
                error=f"Effector execution exceeded {request.timeout_seconds}s timeout",
            )
    
    async def _invoke_tool_contract(self, request: ActionRequest[T], contract: ToolContract) -> Any:
        """Invoke a tool implementation (stub for subclasses)."""
        # This would be implemented by concrete executor
        return None
    
    async def _invoke_effector_contract(self, request: ActionRequest[T], contract: EffectorContract) -> Any:
        """Invoke an effector implementation (stub for subclasses)."""
        # This would be implemented by concrete executor
        return None
    
    def _extract_side_effects(self, result: Any) -> Tuple[Dict[str, Any], ...]:
        """Extract side effects from a result."""
        if isinstance(result, dict):
            effects = result.get("side_effects", [])
            if isinstance(effects, list):
                return tuple(effects)
        return ()
    
    # -------------------------------------------------------------------------
    # Cancellation
    # -------------------------------------------------------------------------
    
    async def cancel(self, invocation_id: InvocationId) -> bool:
        """Cancel a running or queued invocation."""
        with self._lock:
            self._cancelled_invocations.add(invocation_id.value)
            
            if invocation_id in self._active_invocations:
                # Signal cancellation to the running operation
                return True
            return False
    
    def is_cancelled(self, invocation_id: InvocationId) -> bool:
        """Check if an invocation has been cancelled."""
        return invocation_id.value in self._cancelled_invocations
    
    # -------------------------------------------------------------------------
    # Status and monitoring
    # -------------------------------------------------------------------------
    
    def get_state_snapshot(self) -> Dict[str, Any]:
        """Get current executor state (for diagnostics)."""
        with self._lock:
            return {
                "runtime_id": self._runtime_id,
                "is_running": self._is_running,
                "tool_count": len(self._tools),
                "effector_count": len(self._effectors),
                "active_invocations": len(self._active_invocations),
                "cancelled_invocations": len(self._cancelled_invocations),
                "registered_tools": [str(k) for k in self._tools.keys()],
                "registered_effectors": [str(k) for k in self._effectors.keys()],
            }
    
    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """Initiate graceful shutdown."""
        import asyncio
        
        with self._lock:
            self._is_running = False
            
            # Cancel all active invocations
            for invocation_id in list(self._active_invocations.keys()):
                self._cancelled_invocations.add(invocation_id.value)
            
            # Wait for pending operations to complete (with timeout)
            try:
                await asyncio.wait_for(
                    self._wait_for_idle(),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                pass  # Force shutdown after timeout
    
    async def _wait_for_idle(self) -> None:
        """Wait for all invocations to complete."""
        import asyncio
        
        while True:
            with self._lock:
                if not self._active_invocations:
                    break
            await asyncio.sleep(0.1)
    
    # -------------------------------------------------------------------------
    # Utility methods
    # -------------------------------------------------------------------------
    
    def get_tool_contract(self, tool_id: ToolId) -> Optional[ToolContract]:
        """Get the contract for a registered tool."""
        return self._tools.get(tool_id)
    
    def get_effector_contract(self, effector_id: EffectorId) -> Optional[EffectorContract]:
        """Get the contract for a registered effector."""
        return self._effectors.get(effector_id)


# =============================================================================
# DEFAULT EXECUTOR IMPLEMENTATION
# =============================================================================


class DefaultActionExecutor(ActionExecutor):
    """
    Default implementation of ActionExecutor.
    
    Provides reference implementations for common tool and effector types.
    """
    
    def __init__(self, runtime_id: str):
        super().__init__(runtime_id)
        
        # Tool dispatch map (operation -> implementation)
        self._tool_handlers: Dict[str, Callable[[ActionRequest], Any]] = {}
        
        # Effector dispatch map
        self._effector_handlers: Dict[str, Callable[[ActionRequest], Any]] = {}
    
    def register_tool_handler(self, operation: str, handler: Callable[[ActionRequest], Any]) -> None:
        """Register a handler for a specific tool operation."""
        self._tool_handlers[operation] = handler
    
    def register_effector_handler(self, operation: str, handler: Callable[[ActionRequest], Any]) -> None:
        """Register a handler for a specific effector operation."""
        self._effector_handlers[operation] = handler
    
    async def _invoke_tool_contract(self, request: ActionRequest[T], contract: ToolContract) -> Any:
        """Invoke a tool by operation name."""
        handler = self._tool_handlers.get(request.operation)
        
        if not handler:
            raise ValueError(f"Unknown operation for tool {request.tool_id}: {request.operation}")
        
        return handler(request)
    
    async def _invoke_effector_contract(self, request: ActionRequest[T], contract: EffectorContract) -> Any:
        """Invoke an effector by operation name."""
        handler = self._effector_handlers.get(request.operation)
        
        if not handler:
            raise ValueError(f"Unknown operation for effector {request.effector_id}: {request.operation}")
        
        return handler(request)


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

from .registry import (
    RegistrationState,
    RegistryEntry,
    ActionRegistry,
)

__all__ = [
    # Identifiers
    "ActionId",
    "InvocationId",
    "ToolId",
    "EffectorId",
    
    # States and contracts
    "ActionState",
    "ActionRequest",
    "ToolContract",
    "EffectorContract",
    "ExecutionResult",
    "ExecutionStatus",
    
    # Executor
    "ActionExecutor",
    "DefaultActionExecutor",
    
    # Registry (imported separately to avoid circular imports)
    "RegistrationState",
    "RegistryEntry",
    "ActionRegistry",
]
