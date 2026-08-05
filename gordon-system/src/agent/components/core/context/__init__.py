# Core Runtime Context
# ====================

"""
Core runtime context representation.

Provides explicit runtime context that can carry controlled references to:
- runtime identity
- configuration
- registries
- scheduler
- state infrastructure
- observability
- lifecycle controller
- shutdown signal
"""

import warnings
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, TypeVar, Generic

from ..types import RuntimeId, Timestamp


T = TypeVar("T")


@dataclass(frozen=True)
class ContextEntry(Generic[T]):
    """A context entry containing a value with metadata."""
    
    key: str
    value: T
    owner: Optional[str] = None  # Owner identifier for debugging
    created_at: float = field(default_factory=lambda: Timestamp.now().value)


class RuntimeContext:
    """
    Thread-safe runtime context container.
    
    Provides:
    - Controlled entry registration
    - Type-hinted retrieval
    - Immutable snapshots
    - Explicit ownership tracking
    
    Usage:
        ctx = RuntimeContext()
        ctx.register("config", config_obj, owner="configuration")
        config = ctx.get("config")
    """
    
    def __init__(self) -> None:
        self._lock: Any = None  # Will be imported lazily
        self._entries: Dict[str, Any] = {}
        self._owners: Dict[str, str] = {}
        self._created_at: Dict[str, float] = {}
        import threading
        self._lock = threading.Lock()
    
    def register(self, key: str, value: Any, owner: Optional[str] = None) -> None:
        """
        Register a context entry.
        
        Args:
            key: Unique identifier for the entry
            value: The context value
            owner: Optional owner identifier
            
        Raises:
            ValueError: If key already exists
        """
        with self._lock:
            if key in self._entries:
                raise ValueError(f"Context key '{key}' is already registered")
            import time
            self._entries[key] = value
            self._owners[key] = owner or "anonymous"
            self._created_at[key] = time.monotonic()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a context entry by key.
        
        .. deprecated::
           Use `get_typed()` for type-safe access. This method provides arbitrary
           access without type validation and may be removed in future versions.
        
        Args:
            key: The entry's registered key
            
        Returns:
            The context value, or None if not found
        """
        warnings.warn(
            "Context.get() is deprecated. Use Context.get_typed() for type-safe access.",
            DeprecationWarning,
            stacklevel=2
        )
        with self._lock:
            return self._entries.get(key)
    
    def get_typed(self, key: str, expected_type: type[T]) -> T:
        """
        Get a context entry by key with type validation.
        
        This method provides type-safe retrieval of context entries.
        Unlike `get()` which returns Optional[Any], this method validates
        that the stored value is of the expected type.
        
        Args:
            key: The entry's registered key
            expected_type: The expected type of the value
            
        Returns:
            The context value, validated to be of expected_type
            
        Raises:
            KeyError: If key not found in context
            TypeError: If value is not of expected_type
        """
        with self._lock:
            if key not in self._entries:
                raise KeyError(f"Context key '{key}' not found")
            value = self._entries[key]
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"Context entry '{key}' is {type(value).__name__}, "
                    f"expected {expected_type.__name__}"
                )
            return value
    
    def get_or_raise(self, key: str) -> Any:
        """Get a context entry, raising KeyError if not found."""
        value = self.get(key)
        if value is None:
            raise KeyError(f"Context key '{key}' not found")
        return value
    
    def contains(self, key: str) -> bool:
        """Check if a key exists in the context."""
        with self._lock:
            return key in self._entries
    
    def deregister(self, key: str) -> Optional[Any]:
        """
        Remove an entry from the context.
        
        Args:
            key: The entry's registered key
            
        Returns:
            The removed value, or None if not found
        """
        with self._lock:
            if key in self._entries:
                value = self._entries.pop(key)
                self._owners.pop(key, None)
                self._created_at.pop(key, None)
                return value
            return None
    
    def get_owner(self, key: str) -> Optional[str]:
        """Get the owner of a context entry."""
        with self._lock:
            return self._owners.get(key)
    
    def keys(self) -> tuple:
        """Return all context keys as an immutable tuple."""
        with self._lock:
            return tuple(self._entries.keys())
    
    def snapshot(self) -> "ContextSnapshot":
        """Create an immutable snapshot of the context."""
        with self._lock:
            entries_copy = dict(self._entries)
            owners_copy = dict(self._owners)
            created_at_copy = dict(self._created_at)
        
        return ContextSnapshot(
            entries=entries_copy,
            owners=owners_copy,
            created_at=created_at_copy
        )
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator."""
        with self._lock:
            return key in self._entries
    
    def __len__(self) -> int:
        """Return number of context entries."""
        with self._lock:
            return len(self._entries)


@dataclass(frozen=True)
class ContextSnapshot:
    """Immutable snapshot of runtime context state."""
    
    entries: Dict[str, Any]
    owners: Dict[str, str]
    created_at: Dict[str, float]
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the snapshot."""
        return self.entries.get(key)
    
    def get_typed(self, key: str, expected_type: type[T]) -> T:
        """
        Get a context entry by key with type validation.
        
        Args:
            key: The entry's registered key
            expected_type: The expected type of the value
            
        Returns:
            The context value, validated to be of expected_type
            
        Raises:
            KeyError: If key not found in snapshot
            TypeError: If value is not of expected_type
        """
        if key not in self.entries:
            raise KeyError(f"Context key '{key}' not found in snapshot")
        value = self.entries[key]
        if not isinstance(value, expected_type):
            raise TypeError(
                f"Context entry '{key}' is {type(value).__name__}, "
                f"expected {expected_type.__name__}"
            )
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """Return as dictionary (note: owners and timestamps are not included)."""
        return dict(self.entries)


@dataclass(frozen=True)
class RuntimeContextBuilder:
    """Builder for constructing runtime contexts."""
    
    _config: Optional[Any] = None
    _registries: Dict[str, Any] = field(default_factory=dict)
    _scheduler: Optional[Any] = None
    _state: Optional[Any] = None
    _observability: Optional[Any] = None
    _lifecycle_controller: Optional[Any] = None
    
    def set_config(self, config: Any) -> "RuntimeContextBuilder":
        self._config = config
        return self
    
    def add_registry(self, name: str, registry: Any) -> "RuntimeContextBuilder":
        self._registries[name] = registry
        return self
    
    def set_scheduler(self, scheduler: Any) -> "RuntimeContextBuilder":
        self._scheduler = scheduler
        return self
    
    def set_state(self, state: Any) -> "RuntimeContextBuilder":
        self._state = state
        return self
    
    def set_observability(self, observability: Any) -> "RuntimeContextBuilder":
        self._observability = observability
        return self
    
    def set_lifecycle_controller(self, controller: Any) -> "RuntimeContextBuilder":
        self._lifecycle_controller = controller
        return self
    
    def build(self) -> RuntimeContext:
        """Build and return the runtime context."""
        ctx = RuntimeContext()
        
        if self._config is not None:
            ctx.register("config", self._config, owner="configuration")
        
        for name, registry in self._registries.items():
            ctx.register(f"registry.{name}", registry, owner=name)
        
        if self._scheduler is not None:
            ctx.register("scheduler", self._scheduler, owner="scheduling")
        
        if self._state is not None:
            ctx.register("state", self._state, owner="state")
        
        if self._observability is not None:
            ctx.register("observability", self._observability, owner="observability")
        
        if self._lifecycle_controller is not None:
            ctx.register("lifecycle_controller", self._lifecycle_controller, owner="lifecycle")
        
        return ctx


__all__ = [
    "ContextEntry",
    "RuntimeContext",
    "ContextSnapshot",
    "RuntimeContextBuilder",
]
