# Temporal Types Package - Phase 3.16
# ====================================

"""
Temporal Type Definitions for Gordon Core.

All temporal values are immutable dataclasses to ensure thread safety
and deterministic behavior.

TYPES:
------
Instant       - Point in time (nanoseconds since epoch)
Duration      - Time interval between two instants
Timestamp     - Instant with metadata (source, sequence, etc.)
Interval      - Start and end instants
Deadline      - Absolute point by which action must complete
Timeout       - Duration limit for an operation
Epoch         - Reference point in time
Tick          - Smallest temporal unit in simulation
Frame         - Temporal resolution unit
Cycle         - Recurring event pattern
Heartbeat     - Periodic signal
Lease         - Time-limited resource access
Recurrence    - Repeating schedule
Schedule      - Temporal ordering of events
TimeWindow    - Bounded temporal context
TemporalId    - Unique identifier for temporal objects

All types support:
    - Deterministic serialization (to_serializable/from_serializable)
    - Comparison operations (<, <=, ==, >=, >)
    - Hashing for use in sets and dicts
    - Immutable modification via builder methods
"""

from ..foundations import Instant, Duration

# Import additional types as they are implemented
# from .timestamp import Timestamp
# from .interval import Interval
# from .deadline import Deadline
# from .timeout import Timeout
# etc.

__all__ = [
    "Instant",
    "Duration",
]