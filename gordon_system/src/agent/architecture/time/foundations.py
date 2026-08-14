# Temporal Foundations - Phase 3.16
# ==================================

"""
Temporal Foundations Module

This module establishes the canonical temporal model for Gordon Core.

TEMPORAL INVARIANTS (TM-INV):
-----------------------------
TM-INV-001: Time is absolute and unidirectional
    - Events occur in a total order
    - No backward time travel or temporal loops
    - Causality is preserved

TM-INV-002: All time access goes through canonical clocks
    - No direct OS clock access outside canonical time subsystem
    - All temporal reads use ClockProvider interface
    - OS-specific code isolated to clock provider implementations

TM-INV-003: Temporal values are immutable for thread safety
    - Instant, Duration, Timestamp are frozen dataclasses
    - Modifications return new instances (immutable builder pattern)
    - No mutable time-related state outside canonical modules

TM-INV-004: Temporal operations are deterministic under same inputs
    - Given same clock state, same results
    - Simulation mode ensures reproducibility
    - Deterministic random in backoff algorithms

TM-INV-005: Clock skew is detected and reported, not silently corrected
    - Wall clock monotonicity verified
    - Skew detection between clocks
    - Error handling for inconsistent time sources

TM-INV-006: Deadlines are hard constraints
    - Deadline expiry triggers immediate action (cancellation, failure)
    - Soft deadlines rejected at design time
    - Deadline enforcement is authoritative

TM-INV-007: Timers cannot be restarted
    - Timer lifecycle: created → scheduled → executed/failed → expired
    - Restart creates new timer instance
    - Timer identity is unique and immutable

TM-INV-008: Simulation time is independent of wall time
    - Virtual clock runs separately from real clock
    - Time manipulation only in simulation context
    - No leakage between simulation and real time

TEMPORAL TYPES AND RELATIONSHIPS:
---------------------------------
instant (point) + duration → instant (new point)
instant - instant → duration
duration + duration → duration
deadline = instant + duration

CLOCK TYPES:
------------
Wall Clock: Real-world time from hardware clock
    - Used for: External timestamps, logging, user-facing times
    - Properties: May jump (NTP corrections), may go backward slightly
    
Monotonic Clock: Non-decreasing clock for measurement
    - Used for: Duration calculations, timeouts, scheduling
    - Properties: Always moves forward at constant rate

Runtime Clock: Time since runtime startup
    - Used for: Runtime lifecycle management
    - Properties: Reset on restart, monotonic within session

Boot Clock: Time since system boot
    - Used for: System uptime tracking
    - Properties: Monotonic, reset on reboot

Logical Clock: Abstract time for coordination
    - Used for: Distributed ordering, event sequencing
    - Properties: May have gaps, not necessarily continuous

Virtual Clock: Simulated time for testing
    - Used for: Deterministic tests, simulations
    - Properties: Manipulable, can be paused/resumed/fast-forwarded

SCHEDULING MODEL:
-----------------
Schedule → Job → Trigger → Execution

- Schedule: Named collection of jobs
- Job: Unit of work with timing requirements
- Trigger: Condition that starts job execution
    * Immediate: Run now
    * Delayed: Run after duration
    * Recurring: Run periodically

TEMPORAL CONTEXT:
-----------------
Every temporal operation exists in a TemporalContext which defines:
    - Time source (which clock to use)
    - Simulation mode (if any)
    - Deadline enforcement strategy
    - Clock skew tolerance
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol, Optional, List, Dict, Any, TypeVar, Generic
import uuid


# =============================================================================
# Temporal Invariants (Documentation and Enforcement)
# =============================================================================


class TemporalInvariants:
    """
    Canonical temporal invariants for Gordon Core.
    
    These are the fundamental principles that govern all temporal operations.
    Every implementation MUST adhere to these invariants.
    """
    
    # Invariant identifiers
    TIME_UNIDIRECTIONAL = "TM-INV-001"
    CANONICAL_CLOCK_ACCESS = "TM-INV-002"
    IMMUTABLE_TEMPORAL_VALUES = "TM-INV-003"
    DETERMINISTIC_OPERATIONS = "TM-INV-004"
    CLOCK_SKEW_DETECTION = "TM-INV-005"
    HARD_DEADLINES = "TM-INV-006"
    NO_TIMER_RESTART = "TM-INV-007"
    INDEPENDENT_SIMULATION_TIME = "TM-INV-008"
    
    @classmethod
    def get_all(cls) -> Dict[str, str]:
        """Return all invariants with descriptions."""
        return {
            cls.TIME_UNIDIRECTIONAL: "Time is absolute and unidirectional",
            cls.CANONICAL_CLOCK_ACCESS: "All time access goes through canonical clocks",
            cls.IMMUTABLE_TEMPORAL_VALUES: "Temporal values are immutable for thread safety",
            cls.DETERMINISTIC_OPERATIONS: "Temporal operations are deterministic under same inputs",
            cls.CLOCK_SKEW_DETECTION: "Clock skew is detected and reported, not silently corrected",
            cls.HARD_DEADLINES: "Deadlines are hard constraints, never soft suggestions",
            cls.NO_TIMER_RESTART: "Timers cannot be restarted (create new timer instead)",
            cls.INDEPENDENT_SIMULATION_TIME: "Simulation time is completely independent of wall time",
        }
    
    @classmethod
    def validate_invariant(cls, invariant_id: str) -> bool:
        """
        Validate that an invariant exists.
        
        Args:
            invariant_id: The invariant identifier to validate
            
        Returns:
            True if the invariant is recognized
        """
        return invariant_id in cls.get_all()


# =============================================================================
# Time Source Types
# =============================================================================


class TimeSource(Enum):
    """
    Classification of time sources for temporal operations.
    
    Every temporal value must be tagged with its source so that
    downstream consumers can reason about its properties and constraints.
    """
    
    WALL = "wall"           # Real-world time from hardware clock
    MONOTONIC = "monotonic"  # Non-decreasing clock for duration measurement
    RUNTIME = "runtime"     # Time since runtime startup
    BOOT = "boot"           # Time since system boot
    LOGICAL = "logical"     # Abstract coordination time (Lamport, vector)
    SCHEDULER = "scheduler"  # Scheduler's view of time
    EVENT = "event"         # Time associated with events in streams
    STREAM = "stream"       # Time within stream processing context
    TRANSACTION = "transaction"  # Time within transaction boundaries
    SIMULATION = "simulation"  # Virtual/simulated time
    AGENT = "agent"         # Agent's temporal perspective
    PREDICTION = "prediction"  # Forecast/planning time
    DECISION = "decision"   # Time at which decision was made


class ClockType(Enum):
    """
    Types of clock implementations available.
    
    This distinguishes between different clock implementations that may
    be registered and used by the system.
    """
    
    REAL_WALL = "real_wall"
    MONOTONIC = "monotonic"
    RUNTIME = "runtime"
    BOOT = "boot"
    LOGICAL_LAMPORT = "logical_lamport"
    LOGICAL_VECTOR = "logical_vector"
    VIRTUAL_MANUAL = "virtual_manual"
    VIRTUAL_AUTO = "virtual_auto"
    INJECTED_TEST = "injected_test"


# =============================================================================
# Canonical Time Provider Interface
# =============================================================================


class ClockProvider(Protocol):
    """
    Protocol for canonical time providers.
    
    All time access in Gordon Core goes through clock providers.
    No subsystem shall read OS clocks directly.
    
    INVARIANTS:
        CP-INV-001: get_time() returns monotonically non-decreasing values
        CP-INV-002: All implementations must be thread-safe
        CP-INV-003: get_duration() measures elapsed wall-clock time
        CP-INV-004: get_instant() returns absolute time point
    """
    
    @property
    def clock_type(self) -> ClockType:
        """Return the type of this clock."""
        ...
    
    def get_time(self) -> float:
        """
        Get current time as a numeric timestamp.
        
        Returns:
            Time value in seconds (float)
            
        INVARIANT: CP-INV-001
        """
        ...
    
    def get_instant(self) -> "Instant":
        """
        Get current time as an Instant object.
        
        Returns:
            Instant representing current moment
            
        INVARIANT: CP-INV-004
        """
        ...
    
    def get_duration(self, start_time: float, end_time: float) -> "Duration":
        """
        Calculate duration between two timestamps.
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            
        Returns:
            Duration representing the time interval
            
        INVARIANT: CP-INV-003
        """
        ...
    
    def sleep(self, duration: float) -> None:
        """
        Sleep for specified duration.
        
        Args:
            duration: Duration to sleep in seconds
        """
        ...
    
    def is_simulated(self) -> bool:
        """Check if this clock is in simulation mode."""
        ...


# =============================================================================
# Instant - Point in Time
# =============================================================================


@dataclass(frozen=True)
class Instant:
    """
    Immutable representation of a point in time.
    
    An instant represents an absolute moment, independent of any particular
    calendar system or timezone. It is the foundation for all temporal
    calculations.
    
    INVARIANTS:
        INS-INV-001: Instants can be compared (earlier, same, later)
        INS-INV-002: Instant - Instant → Duration
        INS-INV-003: Instant + Duration → Instant
        INS-INV-004: Instant - Duration → Instant
        
    Thread Safety:
        Immutable dataclass ensures thread safety.
        
    Serialization:
        Stored as nanoseconds since Unix epoch for determinism.
    """
    
    # Nanoseconds since Unix epoch (1970-01-01 00:00:00 UTC)
    _nanoseconds: int
    
    # Time source tag for context
    source: TimeSource = field(default=TimeSource.WALL, kw_only=True)
    
    def __post_init__(self) -> None:
        """Validate instant after initialization."""
        if self._nanoseconds < 0:
            raise ValueError("Instant cannot be negative (before Unix epoch)")
    
    @classmethod
    def now(cls, provider: ClockProvider) -> Instant:
        """
        Create Instant from current time using a clock provider.
        
        Args:
            provider: Clock provider to read from
            
        Returns:
            Instant representing current moment
        """
        return provider.get_instant()
    
    @classmethod
    def from_seconds(cls, seconds: float, source: TimeSource = TimeSource.WALL) -> Instant:
        """Create instant from Unix timestamp in seconds."""
        nanoseconds = int(seconds * 1_000_000_000)
        return cls(_nanoseconds=nanoseconds, source=source)
    
    @classmethod
    def from_nanoseconds(cls, nanoseconds: int, source: TimeSource = TimeSource.WALL) -> Instant:
        """Create instant from nanoseconds since epoch."""
        return cls(_nanoseconds=nanoseconds, source=source)
    
    def to_seconds(self) -> float:
        """Convert to Unix timestamp in seconds."""
        return self._nanoseconds / 1_000_000_000.0
    
    def to_nanoseconds(self) -> int:
        """Get nanoseconds since epoch."""
        return self._nanoseconds
    
    def plus(self, duration: "Duration") -> Instant:
        """
        Add duration to this instant.
        
        Args:
            duration: Duration to add
            
        Returns:
            New instant at end of duration
        """
        return Instant(
            _nanoseconds=self._nanoseconds + duration.to_nanoseconds(),
            source=self.source,
        )
    
    def minus(self, duration: "Duration") -> Instant:
        """
        Subtract duration from this instant.
        
        Args:
            duration: Duration to subtract
            
        Returns:
            New instant at start of duration
        """
        return Instant(
            _nanoseconds=self._nanoseconds - duration.to_nanoseconds(),
            source=self.source,
        )
    
    def minus_instant(self, other: "Instant") -> "Duration":
        """
        Calculate duration between two instants.
        
        Args:
            other: The instant to subtract
            
        Returns:
            Duration from other to self
        """
        return Duration.from_nanoseconds(
            nanoseconds=self._nanoseconds - other.to_nanoseconds(),
            source=self.source,
        )
    
    def is_before(self, other: "Instant") -> bool:
        """Check if this instant is before another."""
        return self._nanoseconds < other.to_nanoseconds()
    
    def is_after(self, other: "Instant") -> bool:
        """Check if this instant is after another."""
        return self._nanoseconds > other.to_nanoseconds()
    
    def is_same_or_before(self, other: "Instant") -> bool:
        """Check if this instant is same or before another."""
        return self._nanoseconds <= other.to_nanoseconds()
    
    def is_same_or_after(self, other: "Instant") -> bool:
        """Check if this instant is same or after another."""
        return self._nanoseconds >= other.to_nanoseconds()
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Instant):
            return False
        return self._nanoseconds == other.to_nanoseconds()
    
    def __lt__(self, other: "Instant") -> bool:
        return self._nanoseconds < other.to_nanoseconds()
    
    def __le__(self, other: "Instant") -> bool:
        return self._nanoseconds <= other.to_nanoseconds()
    
    def __gt__(self, other: "Instant") -> bool:
        return self._nanoseconds > other.to_nanoseconds()
    
    def __ge__(self, other: "Instant") -> bool:
        return self._nanoseconds >= other.to_nanoseconds()
    
    def __hash__(self) -> int:
        return hash(self._nanoseconds)
    
    def __repr__(self) -> str:
        return f"Instant({self._nanoseconds}ns, source={self.source.value})"


# =============================================================================
# Duration - Time Interval
# =============================================================================


@dataclass(frozen=True)
class Duration:
    """
    Immutable representation of a time interval.
    
    A duration represents an amount of time, independent of when it occurs.
    Durations can be added to instants or other durations.
    
    INVARIANTS:
        DUR-INV-001: Duration + Duration → Duration
        DUR-INV-002: Instant + Duration → Instant
        DUR-INV-003: Duration is always non-negative
        DUR-INV-004: Duration - Duration → Duration
        
    Thread Safety:
        Immutable dataclass ensures thread safety.
    """
    
    # Nanoseconds in the duration
    _nanoseconds: int
    
    # Time source (for simulation context)
    source: TimeSource = field(default=TimeSource.MONOTONIC, kw_only=True)
    
    def __post_init__(self) -> None:
        """Validate duration after initialization."""
        if self._nanoseconds < 0:
            raise ValueError("Duration cannot be negative")
    
    @classmethod
    def zero(cls) -> "Duration":
        """Return zero-duration."""
        return Duration(_nanoseconds=0)
    
    @classmethod
    def from_seconds(cls, seconds: float, source: TimeSource = TimeSource.MONOTONIC) -> "Duration":
        """Create duration from seconds."""
        nanoseconds = int(seconds * 1_000_000_000)
        return cls(_nanoseconds=nanoseconds, source=source)
    
    @classmethod
    def from_millis(cls, millis: int, source: TimeSource = TimeSource.MONOTONIC) -> "Duration":
        """Create duration from milliseconds."""
        nanoseconds = millis * 1_000_000
        return cls(_nanoseconds=nanoseconds, source=source)
    
    @classmethod
    def from_micros(cls, micros: int, source: TimeSource = TimeSource.MONOTONIC) -> "Duration":
        """Create duration from microseconds."""
        nanoseconds = micros * 1_000
        return cls(_nanoseconds=nanoseconds, source=source)
    
    @classmethod
    def from_nanoseconds(cls, nanoseconds: int, source: TimeSource = TimeSource.MONOTONIC) -> "Duration":
        """Create duration from nanoseconds."""
        return cls(_nanoseconds=nanoseconds, source=source)
    
    def to_seconds(self) -> float:
        """Convert to seconds."""
        return self._nanoseconds / 1_000_000_000.0
    
    def to_millis(self) -> int:
        """Convert to milliseconds."""
        return self._nanoseconds // 1_000_000
    
    def to_micros(self) -> int:
        """Convert to microseconds."""
        return self._nanoseconds // 1_000
    
    def to_nanoseconds(self) -> int:
        """Get nanoseconds."""
        return self._nanoseconds
    
    def plus(self, other: "Duration") -> "Duration":
        """
        Add two durations.
        
        Args:
            other: Duration to add
            
        Returns:
            New duration with summed value
        """
        return Duration(
            _nanoseconds=self._nanoseconds + other.to_nanoseconds(),
            source=self.source,
        )
    
    def minus(self, other: "Duration") -> "Duration":
        """
        Subtract duration from this one.
        
        Args:
            other: Duration to subtract
            
        Returns:
            New duration with difference
        """
        result = self._nanoseconds - other.to_nanoseconds()
        if result < 0:
            raise ValueError("Resulting duration would be negative")
        return Duration(_nanoseconds=result, source=self.source)
    
    def times(self, factor: int) -> "Duration":
        """Multiply duration by integer factor."""
        return Duration(
            _nanoseconds=self._nanoseconds * factor,
            source=self.source,
        )
    
    def divided_by(self, divisor: int) -> "Duration":
        """Divide duration by integer."""
        if divisor == 0:
            raise ZeroDivisionError("Cannot divide duration by zero")
        return Duration(
            _nanoseconds=self._nanoseconds // divisor,
            source=self.source,
        )
    
    def is_zero(self) -> bool:
        """Check if this is a zero duration."""
        return self._nanoseconds == 0
    
    def is_positive(self) -> bool:
        """Check if this is a positive duration."""
        return self._nanoseconds > 0
    
    def is_negative(self) -> bool:
        """Check if this would be negative (should not happen after validation)."""
        return self._nanoseconds < 0
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Duration):
            return False
        return self._nanoseconds == other.to_nanoseconds()
    
    def __lt__(self, other: "Duration") -> bool:
        return self._nanoseconds < other.to_nanoseconds()
    
    def __le__(self, other: "Duration") -> bool:
        return self._nanoseconds <= other.to_nanoseconds()
    
    def __gt__(self, other: "Duration") -> bool:
        return self._nanoseconds > other.to_nanoseconds()
    
    def __ge__(self, other: "Duration") -> bool:
        return self._nanoseconds >= other.to_nanoseconds()
    
    def __hash__(self) -> int:
        return hash(self._nanoseconds)
    
    def __repr__(self) -> str:
        return f"Duration({self._nanoseconds}ns, source={self.source.value})"


# =============================================================================
# Temporal Context
# =============================================================================


class TemporalContext:
    """
    Context for temporal operations.
    
    Defines the temporal environment in which operations occur,
    including the clock source, simulation mode, and enforcement strategy.
    
    Every temporal operation should have an associated context that defines
    its temporal semantics.
    """
    
    def __init__(
        self,
        provider: Optional[ClockProvider] = None,
        simulation_mode: bool = False,
        deadline_enforcement: "DeadlineEnforcement" = None,
        clock_skew_tolerance: Duration = None,
    ):
        """
        Initialize temporal context.
        
        Args:
            provider: Clock provider to use (defaults to wall clock)
            simulation_mode: Whether time is simulated
            deadline_enforcement: How deadlines are enforced
            clock_skew_tolerance: Maximum acceptable clock skew
        """
        from .core.deadline_manager import DeadlineEnforcement
        
        self._provider = provider or WallClockProvider()
        self._simulation_mode = simulation_mode
        self._deadline_enforcement = deadline_enforcement or DeadlineEnforcement.STRICT
        self._clock_skew_tolerance = clock_skew_tolerance or Duration.from_millis(100)
    
    @property
    def provider(self) -> ClockProvider:
        """Get the clock provider for this context."""
        return self._provider
    
    @property
    def simulation_mode(self) -> bool:
        """Check if in simulation mode."""
        return self._simulation_mode
    
    @property
    def deadline_enforcement(self) -> "DeadlineEnforcement":
        """Get the deadline enforcement strategy."""
        return self._deadline_enforcement
    
    @property
    def clock_skew_tolerance(self) -> Duration:
        """Get maximum acceptable clock skew."""
        return self._clock_skew_tolerance
    
    def now(self) -> Instant:
        """Get current instant in this context."""
        return Instant.now(self._provider)
    
    def duration_since(self, start: Instant) -> Duration:
        """
        Calculate duration since given instant.
        
        Args:
            start: Start instant
            
        Returns:
            Duration from start to now
        """
        return self.now().minus_instant(start)
    
    def with_provider(self, provider: ClockProvider) -> "TemporalContext":
        """Create new context with different clock provider."""
        return TemporalContext(
            provider=provider,
            simulation_mode=self._simulation_mode,
            deadline_enforcement=self._deadline_enforcement,
            clock_skew_tolerance=self._clock_skew_tolerance,
        )
    
    def with_simulation(self, enabled: bool = True) -> "TemporalContext":
        """Create new context with simulation mode."""
        return TemporalContext(
            provider=self._provider,
            simulation_mode=enabled,
            deadline_enforcement=self._deadline_enforcement,
            clock_skew_tolerance=self._clock_skew_tolerance,
        )


# =============================================================================
# Deadline Enforcement Strategy
# =============================================================================


class DeadlineEnforcement(Enum):
    """
    Strategies for enforcing deadlines.
    
    Different contexts may require different enforcement behaviors:
        - STRICT: Deadline expiry causes immediate failure/cancellation
        - SOFT: Deadline expiry is advisory, work continues if possible
        - BEST_EFFORT: Try to meet deadline but don't fail on expiry
    """
    
    STRICT = "strict"
    SOFT = "soft"
    BEST_EFFORT = "best_effort"


# =============================================================================
# Utility Functions
# =============================================================================


def now_nanoseconds() -> int:
    """Get current time in nanoseconds (wall clock)."""
    return int(time.time() * 1_000_000_000)


def monotonic_nanoseconds() -> int:
    """
    Get monotonic time in nanoseconds.
    
    This is the recommended clock for measuring durations and timeouts
    because it never goes backward.
    """
    return int(time.monotonic_ns())


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Invariants
    "TemporalInvariants",
    
    # Time sources
    "TimeSource",
    "ClockType",
    
    # Provider interface
    "ClockProvider",
    
    # Core types
    "Instant",
    "Duration",
    
    # Context
    "TemporalContext",
    "DeadlineEnforcement",
    
    # Utilities
    "now_nanoseconds",
    "monotonic_nanoseconds",
]