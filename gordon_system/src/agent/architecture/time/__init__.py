# Canonical Temporal Architecture for Gordon Core - Phase 3.16
# =============================================================

"""
Canonical Temporal Architecture Package

Time is one of the fundamental architectural dimensions of the Gordon runtime.

Every subsystem depends upon time, either directly or indirectly.

This package establishes ONE unified architecture governing:
    * time
    * clocks
    * temporal identity
    * scheduling
    * timers
    * deadlines
    * retries
    * backoff
    * heartbeats
    * wakeups
    * synchronization
    * simulation
    * temporal persistence
    * temporal diagnostics

Architectural Principles:
-------------------------
Time is a Core concern.

Separate completely:
    * Wall Time      - Physical time from hardware clock (OS-specific)
    * Monotonic Time - Non-decreasing clock for measuring duration
    * Runtime Time   - Time relative to runtime startup
    * Boot Time      - Time since system boot
    * Logical Time   - Abstract time for coordination (e.g., Lamport timestamps)
    * Scheduler Time - Time as seen by the scheduler
    * Event Time     - Time associated with events in event streams
    * Stream Time    - Time within stream processing contexts
    * Transaction Time - Time within transaction boundaries
    * Simulation Time - Virtual time for deterministic testing/simulation
    * Agent Time     - Temporal perspective of an agent
    * Prediction Time - Future time for forecasting/planning
    * Decision Time  - Time at which a decision is made

These concepts shall NEVER be interchangeable.

Package Structure:
------------------
time/
├── __init__.py              # Package exports and documentation
├── foundations.py           # Temporal foundations, invariants, terminology
├── types/                   # Temporal type definitions
│   ├── instant.py           # Instant (point in time)
│   ├── duration.py          # Duration (time interval)
│   ├── timestamp.py         # Timestamp (instant with metadata)
│   ├── interval.py          # Interval (start+end instants)
│   ├── deadline.py          # Deadline (absolute point by which action must complete)
│   ├── timeout.py           # Timeout (duration limit for operation)
│   ├── epoch.py             # Epoch (reference time point)
│   ├── tick.py              # Tick (smallest temporal unit in simulation)
│   ├── frame.py             # Frame (temporal resolution unit)
│   ├── cycle.py             # Cycle (recurring event pattern)
│   ├── heartbeat.py         # Heartbeat (periodic signal)
│   ├── lease.py             # Lease (time-limited resource access)
│   ├── recurrence.py        # Recurrence (repeating schedule)
│   ├── schedule.py          # Schedule (temporal ordering of events)
│   ├── time_window.py       # Time window (bounded temporal context)
│   └── identifier.py        # Temporal identifiers
├── clocks/                  # Clock implementations and providers
│   ├── __init__.py          # Clock package exports
│   ├── provider.py          # Clock provider interface
│   ├── wall_clock.py        # Wall clock (real-world time)
│   ├── monotonic_clock.py   # Monotonic clock (non-decreasing)
│   ├── runtime_clock.py     # Runtime-local clock
│   ├── boot_clock.py        # Boot-time-based clock
│   ├── logical_clock.py     # Logical clock (distributed ordering)
│   ├── virtual_clock.py     # Virtual/simulated clock
│   └── injected_clock.py    # Injected time for testing
├── core/                    # Core temporal infrastructure
│   ├── __init__.py          # Core package exports
│   ├── timer.py             # Timer implementation
│   ├── deadline_manager.py  # Deadline tracking and enforcement
│   ├── timeout_policy.py    # Timeout handling policies
│   └── backoff.py           # Exponential backoff implementations
├── scheduler/               # Canonical scheduler
│   ├── __init__.py          # Scheduler package exports
│   ├── scheduler.py         # Main scheduler interface
│   ├── job.py               # Scheduled job definition
│   ├── trigger.py           # Trigger types (immediate, delayed, recurring)
│   ├── priority_queue.py    # Priority-based scheduling queue
│   └── admission.py         # Admission control for scheduled work
├── events/                  # Temporal events and wakeups
│   ├── __init__.py          # Events package exports
│   ├── wakeup.py            # Wakeup events (delayed execution)
│   ├── alarm.py             # Alarm events (deadline reached)
│   └── timer_event.py       # Timer expiration events
├── coordination/            # Temporal coordination & synchronization
│   ├── __init__.py          # Coordination package exports
│   ├── barrier.py           # Time-based barriers
│   ├── latch.py             # Time-based latches
│   └── fence.py             # Temporal memory fences
├── persistence/             # Time persistence & restoration
│   ├── __init__.py          # Persistence package exports
│   ├── checkpoint.py        # Temporal checkpoints
│   ├── snapshot.py          # Snapshot of temporal state
│   └── restoration.py       # Restoration from checkpoints
├── simulation/              # Virtual time & simulation
│   ├── __init__.py          # Simulation package exports
│   ├── virtual_time.py      # Virtual time provider
│   ├── simulator.py         # Time simulator controller
│   └── replay.py            # Replay from recorded events
├── distributed/             # Distributed temporal contracts (architecture only)
│   ├── __init__.py          # Distributed package exports
│   ├── clock_coordination.py  # Clock synchronization protocol
│   ├── logical_clocks.py      # Logical clock implementations
│   └── timestamps.py          # Distributed timestamp generation
└── observability/           # Temporal observability & diagnostics
    ├── __init__.py          # Observability package exports
    ├── timer_diagnostics.py   # Timer diagnostics
    ├── scheduler_diagnostics.py  # Scheduler diagnostics
    ├── latency_metrics.py     # Latency tracking metrics
    └── temporal_tracing.py    # Tracing of temporal operations

INVARIANTS (Canonical Model):
-----------------------------
TM-INV-001: Time is absolute and unidirectional
TM-INV-002: No subsystem reads OS clocks directly - all time access goes through canonical clocks
TM-INV-003: All temporal values are immutable for thread safety
TM-INV-004: Temporal operations are deterministic under same inputs
TM-INV-005: Clock skew is detected and reported, not silently corrected
TM-INV-006: Deadlines are hard constraints, never soft suggestions
TM-INV-007: Timers cannot be restarted (create new timer instead)
TM-INV-008: Simulation time is completely independent of wall time

ARCHITECTURAL BOUNDARIES:
-------------------------
Canonical Time Subsystems OWN:
    - All temporal type definitions
    - All clock implementations and providers
    - Timer lifecycle management
    - Deadline enforcement
    - Scheduler implementation
    - Temporal event generation
    - Time persistence infrastructure
    - Simulation infrastructure

Canonical Time Subsystems DO NOT OWN:
    - Business logic timing (subsystems decide WHEN to do work)
    - Runtime scheduling (Core owns WHEN code executes)
    - Thread lifecycle (Threads own their execution model)
    - Application-specific semantics (only temporal mechanics)

MIGRATION REQUIREMENTS:
-----------------------
All existing implementations of timers, schedulers, deadlines, retries,
timeouts, and related functionality MUST be migrated to canonical time.

Subsystems shall NOT implement their own temporal models.
"""

# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

from .types.instant import Instant
from .types.duration import Duration
from .types.timestamp import Timestamp
from .types.interval import Interval
from .types.deadline import Deadline
from .types.timeout import Timeout
from .types.epoch import Epoch
from .types.tick import Tick
from .types.frame import Frame
from .types.cycle import Cycle
from .types.heartbeat import Heartbeat
from .types.lease import Lease
from .types.recurrence import Recurrence
from .types.schedule import Schedule
from .types.time_window import TimeWindow
from .types.identifier import TemporalId

# Clock providers and implementations
from .clocks.provider import (
    ClockProvider,
    WallClockProvider,
    MonotonicClockProvider,
    RuntimeClockProvider,
)

# Core temporal components
from .core.timer import Timer, TimerHandle
from .core.deadline_manager import DeadlineManager
from .core.timeout_policy import TimeoutPolicy, TimeoutStrategy

# Scheduler
from .scheduler.scheduler import Scheduler
from .scheduler.job import ScheduledJob, JobId
from .scheduler.trigger import (
    Trigger,
    ImmediateTrigger,
    DelayedTrigger,
    RecurringTrigger,
)

# Temporal events and wakeups
from .events.wakeup import Wakeup, WakeupHandle

# Canonical model exports
from .foundations import (
    TemporalInvariants,
    TimeSource,
    ClockType,
    TemporalContext,
)

__all__ = [
    # Types
    "Instant",
    "Duration",
    "Timestamp",
    "Interval",
    "Deadline",
    "Timeout",
    "Epoch",
    "Tick",
    "Frame",
    "Cycle",
    "Heartbeat",
    "Lease",
    "Recurrence",
    "Schedule",
    "TimeWindow",
    "TemporalId",
    
    # Clocks
    "ClockProvider",
    "WallClockProvider",
    "MonotonicClockProvider",
    "RuntimeClockProvider",
    
    # Core
    "Timer",
    "TimerHandle",
    "DeadlineManager",
    "TimeoutPolicy",
    "TimeoutStrategy",
    
    # Scheduler
    "Scheduler",
    "ScheduledJob",
    "JobId",
    "Trigger",
    "ImmediateTrigger",
    "DelayedTrigger",
    "RecurringTrigger",
    
    # Events
    "Wakeup",
    "WakeupHandle",
    
    # Foundations
    "TemporalInvariants",
    "TimeSource",
    "ClockType",
    "TemporalContext",
]