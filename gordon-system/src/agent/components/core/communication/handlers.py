# Core Handler Infrastructure
# ===========================

"""
Handler protocols and registries for processing messages.

Handlers are responsible for:
- Processing specific communication contracts (commands, queries, events)
- Returning typed results or failing cleanly
- Supporting both sync and async execution
- Lifecycle-aware registration/deregistration
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Protocol
from enum import Enum
import time
import asyncio


class HandlerResultType(Enum):
    """Types of handler results."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class HandlerId:
    """Unique identifier for a handler."""
    value: str
    
    @classmethod
    def generate(cls) -> "HandlerId":
        import uuid
        return cls(value=f"handler_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class HandlerMetadata:
    """Metadata about a handler's capabilities."""
    handler_type: str  # e.g., "command", "query", "event"
    
    accepted_contract: str  # e.g., "task.execute", "state.get"
    
    sync_execution: bool = False
    async_execution: bool = True
    
    idempotent: bool = False
    result_type: Optional[str] = None
    
    concurrency_policy: str = "bounded_parallel"  # serial, parallel, reentrant
    max_concurrent: int = 10
    
    timeout_seconds: Optional[float] = None


@dataclass(frozen=True)
class HandlerResult:
    """Result of handler execution."""
    
    success: bool
    result_type: HandlerResultType = HandlerResultType.SUCCESS
    
    payload: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    
    # Timing
    start_time_utc: float = field(default_factory=time.time)
    end_time_utc: float = field(default_factory=time.time)
    
    handler_id: Optional[HandlerId] = None
    
    @classmethod
    def success(
        cls,
        payload: Optional[Dict[str, Any]] = None,
        handler_id: Optional[HandlerId] = None,
    ) -> "HandlerResult":
        return cls(
            success=True,
            result_type=HandlerResultType.SUCCESS,
            payload=dict(payload or {}),
            handler_id=handler_id,
        )
    
    @classmethod
    def failure(
        cls,
        error_message: str,
        error_type: Optional[str] = None,
        handler_id: Optional[HandlerId] = None,
    ) -> "HandlerResult":
        return cls(
            success=False,
            result_type=HandlerResultType.FAILURE,
            error_message=error_message,
            error_type=error_type,
            handler_id=handler_id,
        )
    
    @classmethod
    def cancelled(cls, handler_id: Optional[HandlerId] = None) -> "HandlerResult":
        return cls(
            success=False,
            result_type=HandlerResultType.CANCELLED,
            error_message="Handler was cancelled",
            handler_id=handler_id,
        )
    
    @property
    def duration_seconds(self) -> float:
        return self.end_time_utc - self.start_time_utc


# =============================================================================
# HANDLER PROTOCOLS (typed by contract type)
# =============================================================================

class CommandHandler(Protocol):
    """Protocol for command handlers."""
    
    async def __call__(self, payload: Dict[str, Any]) -> HandlerResult:
        """Process a command and return result."""
        ...


class QueryHandler(Protocol):
    """Protocol for query handlers."""
    
    async def __call__(self, payload: Dict[str, Any]) -> HandlerResult:
        """Process a query and return result."""
        ...


class EventHandler(Protocol):
    """Protocol for event handlers (subscribers)."""
    
    async def __call__(self, payload: Dict[str, Any]) -> None:
        """Process an event. No return value expected."""
        ...


# =============================================================================
# HANDLER REGISTRY
# =============================================================================

class HandlerRegistry:
    """
    Registry for handlers with lifecycle support.
    
    Handlers can be registered, unregistered, and managed through this
    central registry. The registry handles:
    - Type safety (separate storage per contract type)
    - Lifecycle ownership tracking
    - Concurrency control
    """
    
    def __init__(self):
        self._lock = None
        
        # handler_id -> (metadata, handler_callable)
        self._handlers: Dict[str, tuple] = {}
        
        # contract_type -> list of handler_ids
        self._contract_index: Dict[str, List[str]] = {}
    
    def _get_lock(self):
        import threading
        if self._lock is None:
            self._lock = threading.RLock()
        return self._lock
    
    def register(
        self,
        contract_type: str,
        handler: Any,
        metadata: Optional[HandlerMetadata] = None,
        handler_id: Optional[str] = None,
        lifecycle_owner: Optional[str] = None,
    ) -> HandlerId:
        """
        Register a handler for a specific contract type.
        
        Args:
            contract_type: The contract to handle (e.g., "task.execute")
            handler: Async callable that processes the contract
            metadata: Optional handler metadata
            handler_id: Optional unique identifier for this handler
            lifecycle_owner: Owner responsible for cleanup on shutdown
            
        Returns:
            Handler ID (generated or provided)
            
        Raises:
            DuplicateHandlerError: If already registered for this contract
        """
        lock = self._get_lock()
        with lock:
            if handler_id is None:
                handler_id = HandlerId.generate().value
            
            if contract_type in self._contract_index:
                existing_ids = self._contract_index[contract_type]
                if handler_id in existing_ids:
                    raise DuplicateHandlerError(
                        f"Handler {handler_id} already registered for {contract_type}"
                    )
            
            # Store metadata
            meta = metadata or HandlerMetadata(
                handler_type=self._determine_handler_type(handler),
                accepted_contract=contract_type,
            )
            
            self._handlers[handler_id] = (meta, handler, lifecycle_owner)
            
            if contract_type not in self._contract_index:
                self._contract_index[contract_type] = []
            self._contract_index[contract_type].append(handler_id)
            
            return HandlerId(value=handler_id)
    
    def unregister(self, handler_id: str) -> bool:
        """Remove a registered handler."""
        lock = self._get_lock()
        with lock:
            if handler_id not in self._handlers:
                return False
            
            meta, _, _ = self._handlers[handler_id]
            
            # Remove from index
            contract_type = meta.accepted_contract
            if contract_type in self._contract_index:
                try:
                    self._contract_index[contract_type].remove(handler_id)
                    if not self._contract_index[contract_type]:
                        del self._contract_index[contract_type]
                except ValueError:
                    pass
            
            # Remove handler
            del self._handlers[handler_id]
            return True
    
    def get_handlers(
        self,
        contract_type: str,
    ) -> List[tuple]:
        """
        Get all handlers for a contract type.
        
        Returns list of (metadata, handler, lifecycle_owner) tuples.
        """
        lock = self._get_lock()
        with lock:
            handler_ids = self._contract_index.get(contract_type, [])
            return [
                self._handlers[hid]
                for hid in handler_ids
                if hid in self._handlers
            ]
    
    def has_handlers(self, contract_type: str) -> bool:
        """Check if handlers are registered for this contract."""
        return len(self.get_handlers(contract_type)) > 0
    
    def get_all_handlers(self) -> Dict[str, tuple]:
        """Get all registered handlers."""
        lock = self._get_lock()
        with lock:
            return dict(self._handlers)
    
    def cleanup_orphans(
        self,
        active_owners: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Remove handlers without active lifecycle owners.
        
        Used during shutdown to clean up orphaned handlers.
        """
        lock = self._get_lock()
        with lock:
            active = set(active_owners or [])
            
            orphaned = [
                hid
                for hid, (_, _, owner) in list(self._handlers.items())
                if owner and owner not in active
            ]
            
            for hid in orphaned:
                self.unregister(hid)
            
            return orphaned
    
    def _determine_handler_type(self, handler: Any) -> str:
        """Determine the handler type from its signature or context."""
        # Check if it's an async function
        if asyncio.iscoroutinefunction(handler):
            return "async"
        elif callable(handler):
            return "sync"
        return "unknown"


class DuplicateHandlerError(Exception):
    """Raised when attempting to register a duplicate handler."""
    pass


# =============================================================================
# HANDLER CHAIN (for middleware)
# =============================================================================

class HandlerChain:
    """
    Chain of handlers for sequential processing.
    
    Each handler in the chain can:
    - Process the message
    - Short-circuit with an error
    - Pass to next handler
    
    Used for middleware patterns where cross-cutting concerns need to
    be applied before or after main handler execution.
    """
    
    def __init__(self):
        self._lock = None
        self._handlers: List[Callable[[Any], Any]] = []
    
    def _get_lock(self):
        import threading
        if self._lock is None:
            self._lock = threading.RLock()
        return self._lock
    
    def prepend(self, handler: Callable[[Any], Any]) -> None:
        """Add handler to the front of the chain."""
        lock = self._get_lock()
        with lock:
            self._handlers.insert(0, handler)
    
    def append(self, handler: Callable[[Any], Any]) -> None:
        """Add handler to the end of the chain."""
        lock = self._get_lock()
        with lock:
            self._handlers.append(handler)
    
    async def execute(self, message: Any) -> Any:
        """
        Execute all handlers in sequence.
        
        Args:
            message: The message to process
            
        Returns:
            The result after all handlers have processed it
            
        Raises:
            HandlerError: If any handler fails
        """
        lock = self._get_lock()
        with lock:
            handlers = list(self._handlers)
        
        result = message
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(result)
                else:
                    # For sync handlers, run in executor or directly
                    result = handler(result)
            except Exception as e:
                raise HandlerChainError(
                    f"Handler {handler} failed: {e}",
                    handler=handler,
                    message=result if result != message else None,
                )
        
        return result
    
    def get_handler_count(self) -> int:
        """Get the number of handlers in the chain."""
        lock = self._get_lock()
        with lock:
            return len(self._handlers)


class HandlerChainError(Exception):
    """Raised when a handler in the chain fails."""
    
    def __init__(
        self,
        message: str,
        handler: Optional[Callable] = None,
        message_state: Optional[Any] = None,
    ):
        super().__init__(message)
        self.handler = handler
        self.message_state = message_state


# =============================================================================
# BUILT-IN HANDLERS (for testing/defaults)
# =============================================================================

class LoggingHandler:
    """Simple handler that logs messages."""
    
    def __init__(self, prefix: str = ""):
        self._prefix = prefix
    
    async def __call__(self, payload: Dict[str, Any]) -> HandlerResult:
        # In real impl, would use logger
        print(f"{self._prefix}Handler received: {payload}")
        return HandlerResult.success(payload={"logged": True})


class FailingHandler:
    """Handler that always fails (for testing error handling)."""
    
    def __init__(self, error_message: str = "Intentional failure"):
        self._error = error_message
    
    async def __call__(self, payload: Dict[str, Any]) -> HandlerResult:
        return HandlerResult.failure(self._error)


class DelayedHandler:
    """Handler with configurable delay (for testing)."""
    
    def __init__(self, delay_seconds: float = 1.0):
        self.delay = delay_seconds
    
    async def __call__(self, payload: Dict[str, Any]) -> HandlerResult:
        import asyncio
        await asyncio.sleep(self.delay)
        return HandlerResult.success(payload={"delayed": True})


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Types
    "HandlerResultType",
    
    # Identities
    "HandlerId",
    
    # Metadata
    "HandlerMetadata",
    
    # Results
    "HandlerResult",
    
    # Protocols
    "CommandHandler",
    "QueryHandler",
    "EventHandler",
    
    # Registry
    "HandlerRegistry",
    "DuplicateHandlerError",
    
    # Chain
    "HandlerChain",
    "HandlerChainError",
    
    # Test helpers
    "LoggingHandler",
    "FailingHandler",
    "DelayedHandler",
]