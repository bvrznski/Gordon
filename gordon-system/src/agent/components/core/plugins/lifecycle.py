# Plugin Lifecycle Manager - Phase 3.8.8.2
# ==========================================
"""
Canonical lifecycle manager for plugins.

Provides:
- State machine transitions with validation
- Lifecycle event generation
- Synchronous and async state transitions
- Health tracking during lifecycle

State Transitions (valid):
    CREATED -> DISCOVERED -> REGISTERED -> LOADED -> INITIALIZED
        -> ACTIVE <-> SUSPENDED
        -> UNLOADING -> UNLOADED
    
    Any state -> FAILED (on error)
"""

from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Callable,
    Awaitable,
)
from enum import Enum, auto
import asyncio
import time

# Import from abstraction module
try:
    from .abstraction import (
        PluginState,
        PluginError,
        LifecycleTransitionError,
    )
except ImportError:
    class PluginState(Enum):
        CREATED = "created"
        DISCOVERED = "discovered"
        REGISTERED = "registered"
        LOADED = "loaded"
        INITIALIZED = "initialized"
        ACTIVE = "active"
        SUSPENDED = "suspended"
        UNLOADING = "unloading"
        UNLOADED = "unloaded"
    
    class PluginError(Exception):
        pass
    
    class LifecycleTransitionError(PluginError):
        pass


class LifecycleEventType(Enum):
    """Types of lifecycle events."""
    
    DISCOVERED = "discovered"
    REGISTERED = "registered"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    ACTIVATED = "activated"
    SUSPENDED = "suspended"
    RESUMED = "resumed"
    DEACTIVATED = "deactivated"
    UNLOADED = "unloaded"
    FAILED = "failed"


@dataclass(frozen=True)
class LifecycleEvent:
    """An event in the plugin lifecycle."""
    
    event_type: LifecycleEventType
    timestamp: float  # Unix timestamp
    plugin_id: str
    from_state: Optional[PluginState]
    to_state: Optional[PluginState]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> float:
        """Get duration since event (for monitoring)."""
        return time.monotonic() - self.timestamp


@dataclass(frozen=True)
class PluginHealthReport:
    """Health report for a plugin at a point in time."""
    
    plugin_id: str
    state: PluginState
    health_status: str  # healthy, degraded, failed
    last_state_change: float
    initialization_time_ms: Optional[float] = None
    activation_latency_ms: Optional[float] = None


# =============================================================================
# VALIDATION RULES
# =============================================================================

# Valid transitions: from_state -> set of valid to_states
_VALID_TRANSITIONS: Dict[PluginState, List[PluginState]] = {
    PluginState.CREATED: [PluginState.DISCOVERED],
    PluginState.DISCOVERED: [PluginState.REGISTERED],
    PluginState.REGISTERED: [PluginState.LOADED],
    PluginState.LOADED: [PluginState.INITIALIZED],
    PluginState.INITIALIZED: [PluginState.ACTIVE, PluginState.FAILED],
    PluginState.ACTIVE: [PluginState.SUSPENDED, PluginState.UNLOADING, PluginState.FAILED],
    PluginState.SUSPENDED: [PluginState.ACTIVE, PluginState.UNLOADING, PluginState.FAILED],
    PluginState.UNLOADING: [PluginState.UNLOADED, PluginState.FAILED],
    PluginState.UNLOADED: [PluginState.CREATED],  # Can restart
    PluginState.FAILED: [],  # Terminal state - requires manual recovery
}

# States where plugins can be active (running)
_ACTIVE_STATES = {
    PluginState.ACTIVE,
}


class LifecycleManager:
    """
    Manages plugin lifecycle state transitions.
    
    Responsibilities:
        - Validate and execute state transitions
        - Generate lifecycle events
        - Track health during transitions
        - Maintain transition history
    
    Thread Safety:
        All operations are async and use internal locking.
    """
    
    def __init__(self, max_history: int = 100):
        """
        Initialize the lifecycle manager.
        
        Args:
            max_history: Maximum number of state change events to keep
        """
        self._lock = asyncio.Lock()
        
        # State storage
        self._plugin_states: Dict[str, PluginState] = {}
        
        # Transition history (for debugging/audit)
        self._state_history: Dict[str, List[tuple]] = {}
        self._max_history = max_history
        
        # Health tracking
        self._health_reports: Dict[str, PluginHealthReport] = {}
        
        # Timing for latency tracking
        self._transition_start_times: Dict[str, float] = {}
    
    async def get_state(self, plugin_id: str) -> Optional[PluginState]:
        """
        Get the current state of a plugin.
        
        Args:
            plugin_id: The plugin identifier
            
        Returns:
            Current state, or None if not tracked
        """
        async with self._lock:
            return self._plugin_states.get(plugin_id)
    
    async def transition(
        self,
        plugin_id: str,
        to_state: PluginState,
    ) -> bool:
        """
        Attempt to transition a plugin to a new state.
        
        Args:
            plugin_id: The plugin identifier
            to_state: Target state
            
        Returns:
            True if transition succeeded, False otherwise
            
        Raises:
            LifecycleTransitionError: If transition is invalid
        """
        async with self._lock:
            from_state = self._plugin_states.get(plugin_id)
            
            # Initialize state if not tracked yet
            if from_state is None:
                from_state = PluginState.CREATED
            
            # Check for valid transition
            valid_targets = _VALID_TRANSITIONS.get(from_state, [])
            
            if to_state not in valid_targets:
                raise LifecycleTransitionError(
                    f"Invalid transition: {from_state.value} -> {to_state.value}",
                    plugin_id=plugin_id,
                    from_state=from_state,
                    to_state=to_state,
                )
            
            # Record the transition
            self._plugin_states[plugin_id] = to_state
            
            # Update history
            if plugin_id not in self._state_history:
                self._state_history[plugin_id] = []
            
            self._state_history[plugin_id].append((from_state, to_state, time.monotonic()))
            
            # Trim history if needed
            if len(self._state_history[plugin_id]) > self._max_history:
                self._state_history[plugin_id] = (
                    self._state_history[plugin_id][-self._max_history:]
                )
            
            return True
    
    async def force_state(
        self,
        plugin_id: str,
        state: PluginState,
    ) -> None:
        """
        Force a plugin into a specific state (bypass validation).
        
        Use this for error recovery or testing scenarios.
        
        Args:
            plugin_id: The plugin identifier
            state: State to force
        """
        async with self._lock:
            self._plugin_states[plugin_id] = state
    
    async def record_health_report(
        self,
        plugin_id: str,
        health_status: str,
        initialization_time_ms: Optional[float] = None,
        activation_latency_ms: Optional[float] = None,
    ) -> PluginHealthReport:
        """
        Record a health report for a plugin.
        
        Args:
            plugin_id: The plugin identifier
            health_status: Status string (healthy, degraded, failed)
            initialization_time_ms: Time to initialize (optional)
            activation_latency_ms: Time from initialized to active (optional)
            
        Returns:
            The recorded health report
        """
        async with self._lock:
            state = self._plugin_states.get(plugin_id, PluginState.CREATED)
            
            # Get last state change time from history
            last_change = time.monotonic()
            if plugin_id in self._state_history and self._state_history[plugin_id]:
                last_change = self._state_history[plugin_id][-1][2]
            
            report = PluginHealthReport(
                plugin_id=plugin_id,
                state=state,
                health_status=health_status,
                last_state_change=last_change,
                initialization_time_ms=initialization_time_ms,
                activation_latency_ms=activation_latency_ms,
            )
            
            self._health_reports[plugin_id] = report
            return report
    
    async def get_health_report(self, plugin_id: str) -> Optional[PluginHealthReport]:
        """Get the health report for a plugin."""
        async with self._lock:
            return self._health_reports.get(plugin_id)
    
    async def get_all_states(self) -> Dict[str, PluginState]:
        """Get states of all tracked plugins."""
        async with self._lock:
            return dict(self._plugin_states)
    
    async def get_state_history(
        self,
        plugin_id: str,
    ) -> List[tuple]:
        """
        Get the complete state transition history for a plugin.
        
        Returns:
            List of (from_state, to_state, timestamp) tuples
        """
        async with self._lock:
            return list(self._state_history.get(plugin_id, []))
    
    def is_active(self, state: PluginState) -> bool:
        """Check if a state represents an active plugin."""
        return state in _ACTIVE_STATES
    
    def can_transition(self, from_state: PluginState, to_state: PluginState) -> bool:
        """Check if a transition is valid without executing it."""
        valid_targets = _VALID_TRANSITIONS.get(from_state, [])
        return to_state in valid_targets
    
    async def reset(self) -> None:
        """Reset all state tracking (useful for testing)."""
        async with self._lock:
            self._plugin_states.clear()
            self._state_history.clear()
            self._health_reports.clear()


# =============================================================================
# ASYNC LIFECYCLE OPERATIONS
# =============================================================================


class LifecycleHooks:
    """
    Container for lifecycle hook callbacks.
    
    Plugins can register callbacks that are called during state transitions.
    """
    
    def __init__(self):
        """Initialize hooks container."""
        self._on_discovered: List[Callable[[str], Awaitable[None]]] = []
        self._on_registered: List[Callable[[str], Awaitable[None]]] = []
        self._on_loaded: List[Callable[[str], Awaitable[None]]] = []
        self._on_initialized: List[Callable[[str], Awaitable[None]]] = []
        self._on_activated: List[Callable[[str], Awaitable[None]]] = []
        self._on_suspended: List[Callable[[str], Awaitable[None]]] = []
        self._on_resumed: List[Callable[[str], Awaitable[None]]] = []
        self._on_deactivated: List[Callable[[str], Awaitable[None]]] = []
        self._on_unloaded: List[Callable[[str], Awaitable[None]]] = []
    
    def on_discovered(self, func: Callable[[str], Awaitable[None]]) -> None:
        """Register callback for discovered state."""
        self._on_discovered.append(func)
    
    def on_registered(self, func: Callable[[str], Awaitable[None]]) -> None:
        """Register callback for registered state."""
        self._on_registered.append(func)
    
    def on_loaded(self, func: Callable[[str], Awaitable[None]]) -> None:
        """Register callback for loaded state."""
        self._on_loaded.append(func)
    
    def on_initialized(self, func: Callable[[str], Awaitable[None]]) -> None:
        """Register callback for initialized state."""
        self._on_initialized.append(func)
    
    async def fire_discovered(self, plugin_id: str) -> None:
        """Fire discovered hook."""
        await asyncio.gather(*[h(plugin_id) for h in self._on_discovered])
    
    async def fire_registered(self, plugin_id: str) -> None:
        """Fire registered hook."""
        await asyncio.gather(*[h(plugin_id) for h in self._on_registered])
    
    async def fire_loaded(self, plugin_id: str) -> None:
        """Fire loaded hook."""
        await asyncio.gather(*[h(plugin_id) for h in self._on_loaded])
    
    async def fire_initialized(self, plugin_id: str) -> None:
        """Fire initialized hook."""
        await asyncio.gather(*[h(plugin_id) for h in self._on_initialized])
    
    async def fire_activated(self, plugin_id: str) -> None:
        """Fire activated hook."""
        await asyncio.gather(*[h(plugin_id) for h in self._on_activated])
    
    async def fire_suspended(self, plugin_id: str) -> None:
        """Fire suspended hook."""
        await asyncio.gather(*[h(plugin_id) for h in self._on_suspended])
    
    async def fire_resumed(self, plugin_id: str) -> None:
        """Fire resumed hook."""
        await asyncio.gather(*[h(plugin_id) for h in self._on_resumed])
    
    async def fire_deactivated(self, plugin_id: str) -> None:
        """Fire deactivated hook."""
        await asyncio.gather(*[h(plugin_id) for h in self._on_deactivated])
    
    async def fire_unloaded(self, plugin_id: str) -> None:
        """Fire unloaded hook."""
        await asyncio.gather(*[h(plugin_id) for h in self._on_unloaded])


__all__ = [
    # Enums
    "LifecycleEventType",
    
    # Data classes
    "LifecycleEvent",
    "PluginHealthReport",
    
    # Main class
    "LifecycleManager",
    
    # Hooks container
    "LifecycleHooks",
]