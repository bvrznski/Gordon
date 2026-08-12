# Core Temporal System
# =====================
"""
Core runtime temporal ordering and scheduling.

Provides:
- Time-based event ordering
- Temporal constraints for operations
- Timestamp management with monotonic/wall-clock

Phase 3.7: Runtime third-stage expansion - Temporal subsystem.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time


# =============================================================================
# Time Type
# =============================================================================

class TimeType(Enum):
    """
    Types of timestamps in the runtime system.
    
    - WALL_CLOCK: UTC wall-clock time (absolute)
    - MONOTONIC: Monotonic time for duration calculations
    - LOGICAL: Logical timestamp from Lamport clock
    - VECTOR: Vector timestamp for causality tracking
    """
    
    WALL_CLOCK = "wall_clock"
    MONOTONIC = "monotonic"
    LOGICAL = "logical"
    VECTOR = "vector"


@dataclass(frozen=True)
class Timestamp:
    """
    A timestamp with type information.
    
    Usage:
        ts = Timestamp(
            value=time.time(),
            time_type=TimeType.WALL_CLOCK
        )
        
        # Compare timestamps of same type
        if ts1 < ts2:
            pass
    """
    
    value: float  # The timestamp value
    
    time_type: TimeType = TimeType.MONOTONIC
    
    @property
    def is_wall_clock(self) -> bool:
        """Check if this is a wall-clock timestamp."""
        return self.time_type == TimeType.WALL_CLOCK
    
    @property
    def is_monotonic(self) -> bool:
        """Check if this is a monotonic timestamp."""
        return self.time_type == TimeType.MONOTONIC
    
    def to_wall_clock(self) -> "Timestamp":
        """Convert to wall-clock time (if possible)."""
        if self.is_wall_clock:
            return self
        # For non-wall-clock, we can't convert accurately
        # Just return a new wall-clock timestamp at current time
        return Timestamp(value=time.time(), time_type=TimeType.WALL_CLOCK)
    
    def to_monotonic(self) -> "Timestamp":
        """Convert to monotonic time."""
        if self.is_monotonic:
            return self
        # Can't accurately convert from other types
        return Timestamp(value=time.monotonic(), time_type=TimeType.MONOTONIC)
    
    def elapsed_since(self, other: "Timestamp") -> float:
        """
        Calculate time elapsed since another timestamp.
        
        Requires same time type for accurate calculation.
        """
        if self.time_type != other.time_type:
            raise ValueError(
                f"Cannot compare timestamps of different types: "
                f"{self.time_type} vs {other.time_type}"
            )
        return self.value - other.value
    
    def __lt__(self, other: "Timestamp") -> bool:
        """Check if this timestamp is earlier than another."""
        if self.time_type != other.time_type:
            raise ValueError("Cannot compare timestamps of different types")
        return self.value < other.value
    
    def __le__(self, other: "Timestamp") -> bool:
        return self.value <= other.value
    
    def __gt__(self, other: "Timestamp") -> bool:
        return self.value > other.value
    
    def __ge__(self, other: "Timestamp") -> bool:
        return self.value >= other.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Timestamp):
            return False
        if self.time_type != other.time_type:
            return False
        return self.value == other.value
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "value": self.value,
            "time_type": self.time_type.value if hasattr(self.time_type, 'value') else str(self.time_type)
        }


# =============================================================================
# Temporal Order
# =============================================================================

class TemporalOrder:
    """
    Maintains temporal ordering of events.
    
    Provides:
        - Event timestamping and ordering
        - Interval tracking
        - Rate limiting with time windows
    
    Usage:
        order = TemporalOrder()
        
        # Record events
        event_id_1 = order.record_event("event_type_1")
        event_id_2 = order.record_event("event_type_2")
        
        # Get events in temporal order
        events = order.get_events_in_order()
    """
    
    def __init__(self) -> None:
        self._events: Dict[str, Tuple[float, str]] = {}  # id -> (timestamp, type)
        self._timestamps: List[Tuple[float, str]] = []  # Sorted by time
        self._lock = __import__("threading").Lock()
    
    def record_event(self, event_type: str) -> str:
        """
        Record an event with a timestamp.
        
        Args:
            event_type: Type/classification of the event
            
        Returns:
            Event ID
        """
        import uuid
        
        timestamp = time.monotonic()
        event_id = f"evt_{uuid.uuid4().hex[:8]}"
        
        with self._lock:
            self._events[event_id] = (timestamp, event_type)
            
            # Insert in sorted order
            inserted = False
            for i, (ts, _) in enumerate(self._timestamps):
                if timestamp < ts:
                    self._timestamps.insert(i, (timestamp, event_id))
                    inserted = True
                    break
            
            if not inserted:
                self._timestamps.append((timestamp, event_id))
        
        return event_id
    
    def record_event_with_time(self, event_type: str, timestamp: float) -> str:
        """
        Record an event with a specific timestamp.
        
        Useful for replay or backdating events.
        """
        import uuid
        
        event_id = f"evt_{uuid.uuid4().hex[:8]}"
        
        with self._lock:
            self._events[event_id] = (timestamp, event_type)
            
            # Insert in sorted order
            inserted = False
            for i, (ts, _) in enumerate(self._timestamps):
                if timestamp < ts:
                    self._timestamps.insert(i, (timestamp, event_id))
                    inserted = True
                    break
            
            if not inserted:
                self._timestamps.append((timestamp, event_id))
        
        return event_id
    
    def get_events_in_order(self) -> List[Tuple[str, str, float]]:
        """
        Get events in temporal order.
        
        Returns list of (event_id, event_type, timestamp).
        """
        with self._lock:
            result = []
            for ts, event_id in self._timestamps:
                if event_id in self._events:
                    _, event_type = self._events[event_id]
                    result.append((event_id, event_type, ts))
            return result
    
    def get_events_in_window(
        self,
        window_seconds: float,
        reference_time: Optional[float] = None
    ) -> List[Tuple[str, str, float]]:
        """
        Get events within a time window.
        
        Args:
            window_seconds: How far back to look
            reference_time: Reference timestamp (now if not provided)
            
        Returns:
            Events in the time window, newest first
        """
        with self._lock:
            ref = reference_time or time.monotonic()
            cutoff = ref - window_seconds
            
            result = []
            for ts, event_id in reversed(self._timestamps):
                if ts >= cutoff:
                    _, event_type = self._events.get(event_id, (ts, "unknown"))
                    result.append((event_id, event_type, ts))
                else:
                    break
            
            return result
    
    @property
    def event_count(self) -> int:
        """Return number of recorded events."""
        with self._lock:
            return len(self._events)
    
    def clear(self) -> None:
        """Clear all recorded events."""
        with self._lock:
            self._events.clear()
            self._timestamps.clear()


# =============================================================================
# Rate Limiter
# =============================================================================

@dataclass(frozen=True)
class RateLimitConfig:
    """
    Configuration for rate limiting.
    
    Usage:
        config = RateLimitConfig(
            max_calls=10,
            window_seconds=60.0  # Per minute
        )
        
        limiter = RateLimiter(config)
        
        if limiter.can_call():
            make_api_call()
            limiter.record_call()
    """
    
    max_calls: int = 10
    window_seconds: float = 60.0
    burst_size: int = 0  # Additional burst capacity
    
    @property
    def effective_limit(self) -> int:
        """Return total allowed calls including burst."""
        return self.max_calls + self.burst_size


class RateLimiter:
    """
    Rate limiter based on time windows.
    
    Usage:
        limiter = RateLimiter(RateLimitConfig(max_calls=10, window_seconds=60))
        
        if limiter.can_call():
            do_operation()
            limiter.record_call()
    """
    
    def __init__(self, config: RateLimitConfig) -> None:
        self._config = config
        self._calls: List[float] = []  # Timestamps of calls
        self._lock = __import__("threading").Lock()
    
    @property
    def config(self) -> RateLimitConfig:
        """Return current configuration."""
        return self._config
    
    def _clean_old_calls(self, now: float) -> None:
        """Remove calls outside the window."""
        cutoff = now - self._config.window_seconds
        self._calls = [ts for ts in self._calls if ts > cutoff]
    
    def can_call(self) -> bool:
        """
        Check if a call is allowed under rate limits.
        
        Returns True if call would be allowed, False if limited.
        """
        with self._lock:
            now = time.monotonic()
            self._clean_old_calls(now)
            
            return len(self._calls) < self._config.effective_limit
    
    def record_call(self) -> bool:
        """
        Record a call for rate limiting purposes.
        
        Returns True if call was recorded, False if limited.
        """
        with self._lock:
            now = time.monotonic()
            
            if not self.can_call():
                return False
            
            self._calls.append(now)
            return True
    
    def get_remaining_calls(self) -> int:
        """Return number of calls remaining in current window."""
        with self._lock:
            self._clean_old_calls(time.monotonic())
            return max(0, self._config.effective_limit - len(self._calls))
    
    @property
    def call_count(self) -> int:
        """Return number of calls recorded in current window."""
        with self._lock:
            return len(self._calls)
    
    def reset(self) -> None:
        """Reset rate limit state."""
        with self._lock:
            self._calls.clear()


__all__ = [
    # Timestamp types
    "TimeType",
    "Timestamp",
    
    # Ordering
    "TemporalOrder",
    
    # Rate limiting
    "RateLimitConfig",
    "RateLimiter",
]