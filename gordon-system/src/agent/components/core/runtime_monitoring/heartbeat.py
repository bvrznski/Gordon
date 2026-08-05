# Core Runtime Heartbeat & Watchdog System
# =========================================

"""
Heartbeat supervision and watchdog monitoring for runtime integrity.

Provides:
- HeartbeatManager: Supervises heartbeat sources and detects loss
- Watchdog: Monitors progress and triggers alerts on anomalies
- WatchdogPolicy: Configurable watchdog behavior
- WatchdogEvent: Events from watchdog triggering
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable, Set
from enum import Enum, auto
import uuid
import time
import threading
import asyncio

# =============================================================================
# HEARTBEAT SOURCE
# =============================================================================


@dataclass(frozen=True)
class HeartbeatSource:
    """
    A registered heartbeat source.
    
    Sources emit heartbeats at regular intervals. Loss of heartbeats
    triggers health degradation alerts.
    """
    
    # Identifiers
    source_id: str          # Unique identifier for this source
    runtime_id: str         # Which runtime this belongs to
    
    # Configuration
    name: str               # Human-readable name
    expected_interval_seconds: float  # Expected heartbeat frequency
    max_missed: int = 3     # How many missed before declaring lost
    
    # State
    last_heartbeat_utc: float = field(default_factory=time.time)
    consecutive_missed: int = 0
    total_sent: int = 0
    
    @property
    def is_active(self) -> bool:
        """Check if this source is currently active."""
        return self.consecutive_missed < self.max_missed
    
    @property
    def time_since_heartbeat(self) -> float:
        """Time in seconds since last heartbeat."""
        return time.time() - self.last_heartbeat_utc
    
    def record_heartbeat(self) -> "HeartbeatSource":
        """Record a new heartbeat and reset counters."""
        return dataclass_replace(self, 
            last_heartbeat_utc=time.time(),
            consecutive_missed=0,
            total_sent=self.total_sent + 1
        )
    
    def increment_missed(self) -> "HeartbeatSource":
        """Increment missed counter."""
        return dataclass_replace(self, 
            consecutive_missed=self.consecutive_missed + 1
        )
    
    @classmethod
    def create(
        cls,
        source_id: str,
        runtime_id: str,
        name: str,
        expected_interval_seconds: float = 5.0,
        max_missed: int = 3
    ) -> "HeartbeatSource":
        """Create a new heartbeat source."""
        return cls(
            source_id=source_id,
            runtime_id=runtime_id,
            name=name,
            expected_interval_seconds=expected_interval_seconds,
            max_missed=max_missed,
            last_heartbeat_utc=time.time()
        )


# =============================================================================
# HEARTBEAT EVENT
# =============================================================================


class HeartbeatEvent(Enum):
    """Types of heartbeat events."""
    
    SENT = "sent"               # Heartbeat was sent
    RECEIVED = "received"       # Heartbeat was received and processed
    LOST = "lost"               # Heartbeat signal was lost
    RESTORED = "restored"       # Lost heartbeat was restored
    TIMEOUT_WARNING = "timeout_warning"  # Approaching timeout threshold


@dataclass(frozen=True)
class HeartbeatEventRecord:
    """
    A record of a heartbeat event.
    """
    
    # Identifiers
    event_id: str             # Unique identifier
    source_id: str            # Which source
    runtime_id: str           # Runtime instance
    
    # Event type
    event_type: HeartbeatEvent
    
    # Timestamps
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Context
    sequence_number: int = 0   # Heartbeat sequence for this source
    latency_ms: float = 0.0    # Processing latency


# =============================================================================
# HEARTBEAT MANAGER (CANONICAL AUTHORITY)
# =============================================================================


class HeartbeatManager:
    """
    Canonical authority for heartbeat supervision.
    
    This is THE ONE source of truth for heartbeat state. It owns:
    
    - Heartbeat registration
    - Heartbeat recording and validation
    - Loss detection
    - History tracking
    
    Invariants:
        1. Exactly one per runtime instance
        2. Runtime-scoped (not global)
        3. Never mutates subsystem state directly
        4. Events are immutable observables
    """
    
    def __init__(self, runtime_id: str):
        """
        Initialize the HeartbeatManager.
        
        Args:
            runtime_id: Unique identifier for this runtime instance
            
        Note: This creates a NEW manager. For singleton behavior,
        use create_heartbeat_manager() from runtime_monitoring/__init__.py
        """
        self._runtime_id = runtime_id
        
        # Core state
        self._lock = threading.RLock()
        self._sources: Dict[str, HeartbeatSource] = {}
        self._events: List[HeartbeatEventRecord] = []
        self._event_publisher: Optional[Callable[[HeartbeatEventRecord], None]] = None
        
        # Counters
        self._sequence_counters: Dict[str, int] = {}
        
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this manager serves."""
        return self._runtime_id
    
    @property
    def source_count(self) -> int:
        """Get total number of registered sources."""
        with self._lock:
            return len(self._sources)
    
    # -------------------------------------------------------------------------
    # Source Registration
    # -------------------------------------------------------------------------
    
    def register_source(
        self,
        name: str,
        expected_interval_seconds: float = 5.0,
        max_missed: int = 3
    ) -> HeartbeatSource:
        """
        Register a new heartbeat source.
        
        Args:
            name: Human-readable name for this source
            expected_interval_seconds: Expected heartbeat frequency
            max_missed: How many missed before declaring lost
            
        Returns:
            The created HeartbeatSource with source_id
        """
        with self._lock:
            source_id = f"heartbeat_{uuid.uuid4().hex[:12]}"
            
            source = HeartbeatSource.create(
                source_id=source_id,
                runtime_id=self._runtime_id,
                name=name,
                expected_interval_seconds=expected_interval_seconds,
                max_missed=max_missed
            )
            
            self._sources[source_id] = source
            self._sequence_counters[source_id] = 0
            
            return source
    
    def unregister_source(self, source_id: str) -> bool:
        """Remove a registered heartbeat source."""
        with self._lock:
            if source_id in self._sources:
                del self._sources[source_id]
                if source_id in self._sequence_counters:
                    del self._sequence_counters[source_id]
                return True
            return False
    
    # -------------------------------------------------------------------------
    # Heartbeat Operations
    # -------------------------------------------------------------------------
    
    def record_heartbeat(self, source_id: str) -> Optional[HeartbeatSource]:
        """
        Record a heartbeat from a source.
        
        Args:
            source_id: The registered source that sent the heartbeat
            
        Returns:
            Updated HeartbeatSource if found, None otherwise
        """
        with self._lock:
            source = self._sources.get(source_id)
            if source is None:
                return None
            
            # Increment sequence counter
            seq = self._sequence_counters.get(source_id, 0) + 1
            self._sequence_counters[source_id] = seq
            
            # Update source state
            new_source = source.record_heartbeat()
            self._sources[source_id] = new_source
            
            # Emit event
            event = HeartbeatEventRecord(
                event_id=f"hb_event_{uuid.uuid4().hex[:12]}",
                source_id=source_id,
                runtime_id=self._runtime_id,
                event_type=HeartbeatEvent.RECEIVED,
                sequence_number=seq
            )
            self._record_event(event)
            
            return new_source
    
    def record_lost_heartbeat(self, source_id: str) -> Optional[Tuple[HeartbeatSource, bool]]:
        """
        Record that a heartbeat was lost.
        
        Args:
            source_id: The registered source
            
        Returns:
            Tuple of (updated source, is_new_loss) if found, None otherwise
        """
        with self._lock:
            source = self._sources.get(source_id)
            if source is None:
                return None
            
            new_source = source.increment_missed()
            self._sources[source_id] = new_source
            
            # Check if this is a new loss (first missed beyond threshold)
            was_active = source.is_active
            is_new_loss = was_active and not new_source.is_active
            
            # Emit event
            event_type = (
                HeartbeatEvent.LOST if is_new_loss 
                else HeartbeatEvent.TIMEOUT_WARNING
            )
            
            event = HeartbeatEventRecord(
                event_id=f"hb_event_{uuid.uuid4().hex[:12]}",
                source_id=source_id,
                runtime_id=self._runtime_id,
                event_type=event_type,
                sequence_number=self._sequence_counters.get(source_id, 0)
            )
            self._record_event(event)
            
            return new_source, is_new_loss
    
    def restore_heartbeat(self, source_id: str) -> Optional[HeartbeatSource]:
        """
        Restore a heartbeat after it was lost.
        
        Args:
            source_id: The registered source
            
        Returns:
            Updated HeartbeatSource if found, None otherwise
        """
        with self._lock:
            source = self._sources.get(source_id)
            if source is None:
                return None
            
            # Check if this was a loss restoration
            was_lost = not source.is_active
            
            new_source = source.record_heartbeat()
            self._sources[source_id] = new_source
            
            if was_lost:
                event = HeartbeatEventRecord(
                    event_id=f"hb_event_{uuid.uuid4().hex[:12]}",
                    source_id=source_id,
                    runtime_id=self._runtime_id,
                    event_type=HeartbeatEvent.RESTORED
                )
                self._record_event(event)
            
            return new_source
    
    # -------------------------------------------------------------------------
    # Status Queries
    # -------------------------------------------------------------------------
    
    def get_source_status(self, source_id: str) -> Optional[HeartbeatSource]:
        """Get the current status of a heartbeat source."""
        with self._lock:
            return self._sources.get(source_id)
    
    def are_all_sources_active(self) -> bool:
        """Check if all registered sources are currently active."""
        with self._lock:
            return all(s.is_active for s in self._sources.values())
    
    def get_inactive_sources(self) -> List[HeartbeatSource]:
        """Get all sources that have lost their heartbeat signal."""
        with self._lock:
            return [s for s in self._sources.values() if not s.is_active]
    
    # -------------------------------------------------------------------------
    # Event History
    # -------------------------------------------------------------------------
    
    def _record_event(self, event: HeartbeatEventRecord) -> None:
        """Record a heartbeat event."""
        with self._lock:
            self._events.append(event)
            
            # Limit history size
            if len(self._events) > 1000:
                self._events = self._events[-1000:]
            
            # Notify publisher if configured
            if self._event_publisher:
                try:
                    self._event_publisher(event)
                except Exception:
                    pass  # Don't let publisher errors affect main flow
    
    def get_events(self, since_timestamp: Optional[float] = None) -> List[HeartbeatEventRecord]:
        """Get heartbeat events, optionally filtered by time."""
        with self._lock:
            if since_timestamp is None:
                return list(self._events)
            
            return [e for e in self._events if e.timestamp_utc >= since_timestamp]
    
    # -------------------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------------------
    
    def set_event_publisher(
        self,
        publisher: Optional[Callable[[HeartbeatEventRecord], None]]
    ) -> None:
        """Set the event publisher callback."""
        with self._lock:
            self._event_publisher = publisher


# =============================================================================
# WATCHDOG POLICY
# =============================================================================


class WatchdogPolicy(Enum):
    """
    Watchdog policy types.
    
    Policies determine how watchdogs respond to anomalies:
        - ALERT: Log and emit events only
        - WARN: Emit warning diagnostics
        - BLOCK: Block operations until resolved
        - TERMINATE: Terminate runtime on violation
    """
    
    ALERT = "alert"         # Log and emit events only
    WARN = "warn"           # Emit warning diagnostics
    BLOCK = "block"         # Block operations
    TERMINATE = "terminate" # Force termination


@dataclass(frozen=True)
class WatchdogConfig:
    """
    Configuration for a watchdog.
    """
    
    name: str                          # Watchdog name
    check_interval_seconds: float      # How often to run checks
    timeout_seconds: float             # Max time before triggering
    policy: WatchdogPolicy = WatchdogPolicy.ALERT
    description: str = ""              # Human-readable description
    
    @classmethod
    def create(
        cls,
        name: str,
        check_interval_seconds: float,
        timeout_seconds: float,
        policy: WatchdogPolicy = WatchdogPolicy.ALERT,
        description: str = ""
    ) -> "WatchdogConfig":
        """Create a new watchdog configuration."""
        return cls(
            name=name,
            check_interval_seconds=check_interval_seconds,
            timeout_seconds=timeout_seconds,
            policy=policy,
            description=description
        )


# =============================================================================
# WATCHDOG EVENT
# =============================================================================


class WatchdogEventType(Enum):
    """Types of watchdog events."""
    
    CHECK_STARTED = "check_started"
    CHECK_COMPLETED = "check_completed"
    TRIGGERED = "triggered"          # Anomaly detected
    CLEARED = "cleared"              # Previously triggered condition cleared
    CONFIG_CHANGED = "config_changed"


@dataclass(frozen=True)
class WatchdogEvent:
    """
    An event from watchdog operation.
    """
    
    # Identifiers
    event_id: str              # Unique identifier
    watchdog_name: str         # Which watchdog
    runtime_id: str            # Runtime instance
    
    # Event type
    event_type: WatchdogEventType
    
    # Timestamps
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Details
    details: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# WATCHDOG (PROGRESS MONITOR)
# =============================================================================


class Watchdog:
    """
    A progress monitoring watchdog.
    
    Watchdogs detect anomalies like stalled evaluators, dead heartbeats,
    or blocked operations. They are observational - they do NOT mutate state
    directly but may trigger events that subsystems handle.
    
    Usage:
        # Create a watchdog configuration
        config = WatchdogConfig.create(
            name="scheduler_watchdog",
            check_interval_seconds=10.0,
            timeout_seconds=30.0,
            policy=WatchdogPolicy.ALERT
        )
        
        # Create and start the watchdog
        watchdog = Watchdog(config)
        
        async def check_scheduler():
            return scheduler.is_active
        
        result = await watchdog.check("scheduler_health", check_scheduler)
        
        if not result:
            # Scheduler may be stuck - event was emitted
            pass
    """
    
    def __init__(
        self,
        config: WatchdogConfig,
        runtime_id: Optional[str] = None
    ):
        """
        Initialize a watchdog.
        
        Args:
            config: Watchdog configuration
            runtime_id: Runtime instance ID (optional)
        """
        self._config = config
        self._runtime_id = runtime_id or "default"
        self._lock = threading.RLock()
        
        # State
        self._last_check_utc: Optional[float] = None
        self._is_triggered: bool = False
        self._events: List[WatchdogEvent] = []
        
    @property
    def config(self) -> WatchdogConfig:
        """Get the watchdog configuration."""
        return self._config
    
    @property
    def is_triggered(self) -> bool:
        """Check if this watchdog has triggered (detected an anomaly)."""
        with self._lock:
            return self._is_triggered
    
    # -------------------------------------------------------------------------
    # Check Operations
    # -------------------------------------------------------------------------
    
    async def check(
        self,
        check_name: str,
        check_fn: Callable[[], Any],
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Execute a single watchdog check.
        
        Args:
            check_name: Human-readable name for this check
            check_fn: Async function to execute (should return truthy if OK)
            context: Additional context data
            
        Returns:
            True if check passed, False if anomaly detected
        """
        start_time = time.monotonic()
        
        # Emit started event
        self._emit_event(WatchdogEventType.CHECK_STARTED, {
            "check_name": check_name
        })
        
        try:
            result = await asyncio.to_thread(check_fn)
            
            duration = time.monotonic() - start_time
            
            if result:
                # Check passed
                self._is_triggered = False  # Clear any previous trigger
                
                # Emit completed event
                self._emit_event(WatchdogEventType.CHECK_COMPLETED, {
                    "check_name": check_name,
                    "duration_ms": duration * 1000,
                    "passed": True
                })
                
                return True
            
            else:
                # Check failed - anomaly detected
                was_triggered = self._is_triggered
                self._is_triggered = True
                
                # Emit triggered event with policy info
                self._emit_event(WatchdogEventType.TRIGGERED, {
                    "check_name": check_name,
                    "duration_ms": duration * 1000,
                    "policy": self._config.policy.value,
                    "details": context or {}
                })
                
                return False
                
        except Exception as e:
            # Check raised exception - anomaly detected
            was_triggered = self._is_triggered  
            self._is_triggered = True
            
            self._emit_event(WatchdogEventType.TRIGGERED, {
                "check_name": check_name,
                "duration_ms": (time.monotonic() - start_time) * 1000,
                "policy": self._config.policy.value,
                "error": f"{type(e).__name__}: {str(e)}",
                "details": context or {}
            })
            
            return False
    
    async def run_periodic_check(
        self,
        check_name: str,
        check_fn: Callable[[], Any],
        stop_event: Optional[asyncio.Event] = None
    ) -> None:
        """
        Run a periodic watchdog check loop.
        
        Args:
            check_name: Name of the check
            check_fn: Function to execute periodically  
            stop_event: Event to signal when to stop (optional)
        """
        while True:
            if stop_event and stop_event.is_set():
                break
            
            await self.check(check_name, check_fn)
            
            # Wait for next interval
            try:
                await asyncio.wait_for(
                    stop_event.wait() if stop_event else asyncio.sleep(0),
                    timeout=self._config.check_interval_seconds
                )
            except asyncio.TimeoutError:
                continue  # Normal timeout, continue loop
    
    # -------------------------------------------------------------------------
    # Event Management
    # -------------------------------------------------------------------------
    
    def _emit_event(self, event_type: WatchdogEventType, details: Dict[str, Any]) -> None:
        """Emit a watchdog event."""
        with self._lock:
            event = WatchdogEvent(
                event_id=f"watchdog_event_{uuid.uuid4().hex[:12]}",
                watchdog_name=self._config.name,
                runtime_id=self._runtime_id,
                event_type=event_type,
                timestamp_utc=time.time(),
                monotonic_time=time.monotonic(),
                details=details
            )
            
            self._events.append(event)
            
            # Limit history size
            if len(self._events) > 1000:
                self._events = self._events[-1000:]
    
    def get_events(self, since_timestamp: Optional[float] = None) -> List[WatchdogEvent]:
        """Get watchdog events, optionally filtered by time."""
        with self._lock:
            if since_timestamp is None:
                return list(self._events)
            
            return [e for e in self._events if e.timestamp_utc >= since_timestamp]
    
    def clear_triggered(self) -> bool:
        """
        Manually clear a triggered state.
        
        Returns True if state was cleared, False if already clear.
        """
        with self._lock:
            if not self._is_triggered:
                return False
            
            self._is_triggered = False
            self._emit_event(WatchdogEventType.CLEARED, {})
            return True


# =============================================================================
# WATCHDOG SYSTEM (COLLECTION OF WATCHDOGS)
# =============================================================================


class WatchdogSystem:
    """
    Collection of watchdogs for a runtime instance.
    
    Provides centralized management of multiple watchdogs with:
        - Registration and configuration
        - Status aggregation
        - Event aggregation
    """
    
    def __init__(self, runtime_id: str):
        """Initialize the watchdog system."""
        self._runtime_id = runtime_id
        self._lock = threading.RLock()
        
        # Watchdogs by name
        self._watchdogs: Dict[str, Watchdog] = {}
        
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this system serves."""
        return self._runtime_id
    
    # -------------------------------------------------------------------------
    # Watchdog Management
    # -------------------------------------------------------------------------
    
    def register_watchdog(self, watchdog: Watchdog) -> None:
        """Register a watchdog with the system."""
        with self._lock:
            self._watchdogs[watchdog.config.name] = watchdog
    
    def unregister_watchdog(self, name: str) -> bool:
        """Unregister a watchdog by name."""
        with self._lock:
            if name in self._watchdogs:
                del self._watchdogs[name]
                return True
            return False
    
    def get_watchdog(self, name: str) -> Optional[Watchdog]:
        """Get a watchdog by name."""
        with self._lock:
            return self._watchdogs.get(name)
    
    # -------------------------------------------------------------------------
    # Status Queries
    # -------------------------------------------------------------------------
    
    def any_triggered(self) -> bool:
        """Check if any watchdog is currently triggered."""
        with self._lock:
            return any(w.is_triggered for w in self._watchdogs.values())
    
    def get_triggered_watchdogs(self) -> List[Watchdog]:
        """Get all currently triggered watchdogs."""
        with self._lock:
            return [w for w in self._watchdogs.values() if w.is_triggered]
    
    def get_all_watchdogs_status(self) -> Dict[str, bool]:
        """Get trigger status of all watchdogs."""
        with self._lock:
            return {name: w.is_triggered for name, w in self._watchdogs.items()}
    
    # -------------------------------------------------------------------------
    # Event Aggregation
    # -------------------------------------------------------------------------
    
    def get_events(
        self,
        since_timestamp: Optional[float] = None
    ) -> List[WatchdogEvent]:
        """Get all watchdog events."""
        with self._lock:
            all_events: List[WatchdogEvent] = []
            
            for watchdog in self._watchdogs.values():
                events = watchdog.get_events(since_timestamp=since_timestamp)
                all_events.extend(events)
            
            # Sort by timestamp
            all_events.sort(key=lambda e: e.timestamp_utc)
            
            return all_events


# =============================================================================
# WATCHDOG POLICY HANDLER (DECORATOR/HELPER)
# =============================================================================

class WatchdogPolicyHandler:
    """
    Helper for handling watchdog policy responses.
    
    This class determines what action to take based on the policy
    and current state.
    """
    
    @staticmethod
    def should_block(policy: WatchdogPolicy, is_triggered: bool) -> bool:
        """Determine if operations should be blocked."""
        return (
            policy in (WatchdogPolicy.BLOCK, WatchdogPolicy.TERMINATE)
            and is_triggered
        )
    
    @staticmethod
    def should_terminate(policy: WatchdogPolicy, is_triggered: bool) -> bool:
        """Determine if runtime should be terminated."""
        return policy == WatchdogPolicy.TERMINATE and is_triggered
    
    @staticmethod
    def should_log(policy: WatchdogPolicy, is_triggered: bool) -> bool:
        """Determine if event should be logged."""
        # Always log for alert, warn, block; terminate implies logging
        return True  # All policies should log


# =============================================================================
# DATACLASS REPLACE HELPER
# =============================================================================

def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    import dataclasses
    if hasattr(obj, '__dataclass_fields__'):
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Heartbeat models
    "HeartbeatSource",
    "HeartbeatEvent",
    "HeartbeatEventRecord",
    
    # Watchdog models
    "WatchdogPolicy",
    "WatchdogConfig",
    "WatchdogEventType", 
    "WatchdogEvent",
    
    # Authorities
    "HeartbeatManager",
    "Watchdog",
    "WatchdogSystem",
    
    # Helpers
    "WatchdogPolicyHandler",
]