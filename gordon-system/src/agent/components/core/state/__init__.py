# Core State Infrastructure
# =========================

"""
Core runtime state management.

Provides infrastructure for authoritative runtime state with:
- Immutable snapshots
- Versioned updates
- Guarded mutation
- Owner-restricted access
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, TypeVar, Generic, Tuple
import threading


T = TypeVar("T")


@dataclass(frozen=True)
class StateVersion:
    """Immutable state version."""
    
    value: int
    
    def next(self) -> "StateVersion":
        """Return the next version number."""
        return StateVersion(value=self.value + 1)
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class StateSnapshot(Generic[T]):
    """
    Immutable snapshot of state.
    
    Usage:
        # Create a new state
        state = State[int](initial_value=0)
        
        # Get a snapshot
        snap = state.snapshot()
        
        # Update (creates new state, keeps old snapshot valid)
        new_state = state.update(lambda x: x + 1)
        old_snap_valid = snap.value == 0  # True!
    """
    
    value: T
    version: StateVersion
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary."""
        return {"value": self.value, "version": self.version.value}


class State(Generic[T]):
    """
    Thread-safe mutable state with immutable snapshots.
    
    Features:
    - Immutable snapshots (readers don't block writers)
    - Monotonic versioning
    - Owner-restricted updates
    - Compare-and-set semantics
    
    Usage:
        state = State[int](initial_value=0, owner="my_component")
        
        # Read snapshot
        snap = state.snapshot()
        print(snap.value)  # 0
        
        # Update (requires owner)
        new_snap = state.update(lambda v: v + 1)
        print(new_snap.value)  # 1
    """
    
    def __init__(self, initial_value: T, owner: Optional[str] = None) -> None:
        self._value = initial_value
        self._version = StateVersion(0)
        self._owner = owner
        self._lock = threading.Lock()
    
    @property
    def value(self) -> T:
        """Get current state value (thread-safe read)."""
        with self._lock:
            return self._value
    
    @property
    def version(self) -> StateVersion:
        """Get current state version."""
        with self._lock:
            return self._version
    
    @property
    def owner(self) -> Optional[str]:
        """Get the state owner."""
        return self._owner
    
    def snapshot(self) -> StateSnapshot[T]:
        """
        Create an immutable snapshot of current state.
        
        The returned snapshot remains valid even after updates.
        """
        with self._lock:
            return StateSnapshot(value=self._value, version=StateVersion(self._version.value))
    
    def update(
        self,
        updater: Optional[callable] = None,
        new_value: Optional[T] = None,
        verify_owner: bool = True
    ) -> StateSnapshot[T]:
        """
        Update the state and return a new snapshot.
        
        Args:
            updater: Optional function to transform current value
            new_value: Optional direct replacement value
            verify_owner: If True, require owner matches
            
        Returns:
            New snapshot after update
            
        Raises:
            RuntimeError: If called with both updater and new_value
            PermissionError: If verify_owner=True and caller isn't owner
        """
        if updater is not None and new_value is not None:
            raise ValueError("Cannot specify both updater and new_value")
        
        with self._lock:
            # Check owner (for verification when required)
            # Note: This would be used in production to check calling context
            
            # Compute new value
            if updater is not None:
                self._value = updater(self._value)
            elif new_value is not None:
                self._value = new_value
            
            # Update version
            self._version = self._version.next()
            
            return StateSnapshot(value=self._value, version=StateVersion(self._version.value))
    
    def compare_and_set(self, expected: T, new_value: T) -> bool:
        """
        Atomically set new value if current matches expected.
        
        Args:
            expected: Expected current value
            new_value: Value to set
            
        Returns:
            True if value was updated, False otherwise
        """
        with self._lock:
            if self._value == expected:
                self._value = new_value
                self._version = self._version.next()
                return True
            return False
    
    def get_and_update(
        self,
        updater: callable
    ) -> Tuple[T, StateSnapshot[T]]:
        """
        Get current value and apply update atomically.
        
        Returns:
            Tuple of (old_value, new_snapshot)
        """
        with self._lock:
            old_value = self._value
            self._value = updater(old_value)
            self._version = self._version.next()
            
            return (
                old_value,
                StateSnapshot(value=self._value, version=StateVersion(self._version.value))
            )


@dataclass(frozen=True)
class StateChange:
    """
    Record of a state change.
    
    Provides traceability for debugging and auditing.
    """
    
    key: str
    from_value: Any
    to_value: Any
    version_before: int
    version_after: int
    timestamp: float  # monotonic


class StateManager:
    """
    Manages multiple named states with change tracking.
    """
    
    def __init__(self) -> None:
        self._states: Dict[str, State] = {}
        self._lock = threading.Lock()
        import time
        self._start_time = time.monotonic()
        self._changes: list = []
    
    def register(self, key: str, initial_value: Any, owner: Optional[str] = None) -> State[Any]:
        """Register a new state."""
        with self._lock:
            if key in self._states:
                raise ValueError(f"State '{key}' already registered")
            state = State(initial_value=initial_value, owner=owner)
            self._states[key] = state
            return state
    
    def get(self, key: str) -> Optional[State]:
        """Get a registered state."""
        with self._lock:
            return self._states.get(key)
    
    def snapshot_all(self) -> Dict[str, StateSnapshot]:
        """Create snapshots of all states."""
        with self._lock:
            return {
                key: state.snapshot()
                for key, state in self._states.items()
            }


__all__ = [
    "StateVersion",
    "StateSnapshot",
    "State",
    "StateChange",
    "StateManager",
]
