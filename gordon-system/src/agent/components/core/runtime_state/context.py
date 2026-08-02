# Core Runtime Context
# =====================

"""
Core runtime context transport.

Provides:
- Domain-neutral runtime context with explicit facilities
- Immutable context objects
- Thread-safe access
- Versioned derived contexts

Runtime Context answers:
"Which runtime am I operating within, and which domain-neutral facilities
have been explicitly made available to me?"
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Any,
    TypeVar,
    Generic,
    Iterator,
)
from enum import Enum
import threading
import time

from ..types import RuntimeId, EntityId
from .registry import RegistryReader


class ContextScope(Enum):
    """
    Context scoping modes.
    
    Defines the lifetime and visibility of context instances.
    """
    PROCESS = "process"  # Process-wide (not recommended)
    RUNTIME = "runtime"  # Per-runtime instance
    COMPONENT = "component"  # Per-component scope
    OPERATION = "operation"  # Per-operation scope
    REQUEST = "request"  # Per-request scope


@dataclass(frozen=True)
class ContextEntry:
    """
    A context entry containing a value with metadata.
    
    Note: This is for internal representation only. The actual context
    uses typed accessors rather than generic dictionary access.
    """
    
    key: str
    value: Any
    owner: Optional[str] = None
    created_at: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class ContextSnapshot:
    """
    Immutable snapshot of context state.
    
    Provides safe exposure to read-only consumers without exposing
    mutable backing collections.
    """
    
    entries: Dict[str, Any]
    owners: Dict[str, str]
    created_at: Dict[str, float]


@dataclass(frozen=True)
class RuntimeContext:
    """
    Immutable runtime context with explicit facilities.
    
    Provides domain-neutral runtime context that can carry references to:
    - Runtime identity
    - Configuration (read-only view)
    - Registry query interface
    - State snapshot provider
    - Cancellation signal
    - Shutdown signal
    
    This is NOT a general-purpose mutable bag. It should not be used as:
    - A global service locator
    - A replacement for dependency injection
    - A container for capability-owned state
    
    Usage:
        # Build with explicit fields
        ctx = RuntimeContext(
            runtime_id=runtime_id,
            registry_reader=registry_reader,
            state_snapshot=state_snapshot
        )
        
        # Get a derived context (e.g., with additional values)
        derived_ctx = ctx.with_entries(extra={"key": value})
    """
    
    # Required fields - always present
    runtime_id: RuntimeId
    
    # Optional facilities (None if not provided)
    registry_reader: Optional[RegistryReader] = None
    state_snapshot: Any = None  # RuntimeStateSnapshot from state module
    cancellation_signal: Any = None  # CancellationSignal from signals module
    shutdown_signal: Any = None  # ShutdownSignal from signals module
    
    # Additional typed fields for runtime-provided facilities
    _extra_entries: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a context entry by key.
        
        Args:
            key: The entry's registered key
            
        Returns:
            The context value, or None if not found
        """
        return self._extra_entries.get(key)
    
    def contains(self, key: str) -> bool:
        """Check if a key exists in the context."""
        return key in self._extra_entries
    
    def with_entries(self, extra: Dict[str, Any]) -> "RuntimeContext":
        """
        Create a derived context with additional entries.
        
        Args:
            extra: Additional key-value pairs to add
            
        Returns:
            New RuntimeContext with merged entries
        """
        new_extra = dict(self._extra_entries)
        new_extra.update(extra)
        
        return RuntimeContext(
            runtime_id=self.runtime_id,
            registry_reader=self.registry_reader,
            state_snapshot=self.state_snapshot,
            cancellation_signal=self.cancellation_signal,
            shutdown_signal=self.shutdown_signal,
            _extra_entries=new_extra
        )
    
    def snapshot(self) -> ContextSnapshot:
        """Create an immutable snapshot of context entries."""
        return ContextSnapshot(
            entries=dict(self._extra_entries),
            owners={},  # No ownership tracking in this context
            created_at={}  # No timestamp tracking in this context
        )
    
    @property
    def keys(self) -> tuple:
        """Return all context keys as an immutable tuple."""
        return tuple(self._extra_entries.keys())


class ContextBuilder:
    """
    Builder for constructing runtime contexts.
    
    Usage:
        ctx = (
            RuntimeContextBuilder()
            .set_runtime_id(runtime_id)
            .set_registry_reader(registry_reader)
            .set_state_snapshot(state_snapshot)
            .build()
        )
    """
    
    def __init__(self) -> None:
        self._runtime_id: Optional[RuntimeId] = None
        self._registry_reader: Optional[RegistryReader] = None
        self._state_snapshot: Any = None
        self._cancellation_signal: Any = None
        self._shutdown_signal: Any = None
        self._extra: Dict[str, Any] = {}
    
    def set_runtime_id(self, runtime_id: RuntimeId) -> "ContextBuilder":
        """Set the runtime identifier."""
        self._runtime_id = runtime_id
        return self
    
    def set_registry_reader(self, reader: RegistryReader) -> "ContextBuilder":
        """Set the registry query interface."""
        self._registry_reader = reader
        return self
    
    def set_state_snapshot(self, snapshot: Any) -> "ContextBuilder":
        """Set the state snapshot provider."""
        self._state_snapshot = snapshot
        return self
    
    def set_cancellation_signal(self, signal: Any) -> "ContextBuilder":
        """Set the cancellation signal."""
        self._cancellation_signal = signal
        return self
    
    def set_shutdown_signal(self, signal: Any) -> "ContextBuilder":
        """Set the shutdown signal."""
        self._shutdown_signal = signal
        return self
    
    def add_entry(self, key: str, value: Any) -> "ContextBuilder":
        """Add an extra context entry."""
        self._extra[key] = value
        return self
    
    def build(self) -> RuntimeContext:
        """
        Build and return the runtime context.
        
        Raises:
            ValueError: If required fields are missing (runtime_id)
        """
        if self._runtime_id is None:
            raise ValueError("RuntimeContext requires runtime_id")
        
        return RuntimeContext(
            runtime_id=self._runtime_id,
            registry_reader=self._registry_reader,
            state_snapshot=self._state_snapshot,
            cancellation_signal=self._cancellation_signal,
            shutdown_signal=self._shutdown_signal,
            _extra_entries=dict(self._extra)
        )


# Thread-local storage for async-safe context propagation
class ContextLocal:
    """
    Thread-local (and async-task-local) context accessor.
    
    Provides per-context isolation without process-wide state.
    
    Usage:
        ctx_local = ContextLocal()
        
        # Set current context
        with ctx_local.use(context):
            value = ctx_local.get("some_key")
    """
    
    def __init__(self) -> None:
        self._local = threading.local()
    
    @property
    def _context_stack(self) -> List[RuntimeContext]:
        """Get or create the context stack for this thread/task."""
        if not hasattr(self._local, "_stack"):
            self._local._stack: List[RuntimeContext] = []
        return self._local._stack
    
    def get_context(self) -> Optional[RuntimeContext]:
        """Get the current context on this thread/task."""
        if self._context_stack:
            return self._context_stack[-1]
        return None
    
    def use(self, context: RuntimeContext):
        """
        Context manager to temporarily set the context.
        
        Args:
            context: The context to make current
        """
        class _ContextManager:
            def __init__(self, local: ContextLocal, ctx: RuntimeContext):
                self._local = local
                self._ctx = ctx
            
            def __enter__(self) -> "ContextLocal":
                self._local._context_stack.append(self._ctx)
                return self._local
            
            def __exit__(self, exc_type, exc_val, exc_tb) -> None:
                self._local._context_stack.pop()
        
        return _ContextManager(self, context)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the current context.
        
        Args:
            key: The entry's registered key
            
        Returns:
            The context value, or None if not found or no context
        """
        ctx = self.get_context()
        if ctx is None:
            return None
        return ctx.get(key)


__all__ = [
    "ContextScope",
    "ContextEntry",
    "ContextSnapshot",
    "RuntimeContext",
    "ContextBuilder",
    "ContextLocal",
]