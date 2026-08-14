# Timer Implementation - Phase 3.16
# ==================================

"""
Canonical Timer Implementation for Gordon Core.

TIMERS:
-------
A Timer represents a scheduled execution at some future time. It is NOT
a while-true loop, event loop, or runtime dispatcher.

Timer Lifecycle:
    CREATED → SCHEDULED → RUNNING → [COMPLETED | EXPIRED]
                            ↓
                         CANCELLED

INVARIANTS:
----------
TM-TMR-001: Timers are created with a callback and delay
TM-TMR-002: A timer can only be started once
TM-TMR-003: Started timers must have their callbacks invoked or cancelled
TM-TMR-004: Timer identity is immutable after creation
TM-TMR-005: Timers cannot be restarted (create new timer instead)
"""

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional, Any
import uuid


class TimerState(Enum):
    """States in the timer lifecycle."""
    CREATED = "created"          # Just created, not scheduled yet
    SCHEDULED = "scheduled"      # Scheduled but callback not invoked
    RUNNING = "running"          # Callback invocation started
    COMPLETED = "completed"      # Callback completed successfully
    EXPIRED = "expired"          # Timer expired (deadline passed)
    CANCELLED = "cancelled"      # Timer was cancelled before execution


@dataclass(frozen=True)
class TimerHandle:
    """
    Immutable handle to a timer for cancellation and status queries.
    
    The handle is created when the timer is scheduled and can be used
    to cancel the timer or check its status.
    """
    timer_id: str
    state: TimerState
    
    def is_active(self) -> bool:
        """Check if timer is still active (not completed, expired, or cancelled)."""
        return self.state not in (
            TimerState.COMPLETED,
            TimerState.EXPIRED,
            TimerState.CANCELLED,
        )
    
    def is_cancelled(self) -> bool:
        """Check if timer was cancelled."""
        return self.state == TimerState.CANCELLED


@dataclass
class Timer:
    """
    Canonical timer implementation.
    
    A timer schedules a callback to be invoked after a duration has elapsed.
    It does NOT execute the callback - it merely schedules it for execution.
    
    Usage:
        timer = Timer(
            callback=handle_timeout,
            delay=Duration.from_seconds(5.0),
            name="my_timer"
        )
        
        handle = scheduler.schedule(timer)
        
        # Later...
        if handle.is_active():
            # Timer is still running
            pass
    """
    
    # Callback to invoke when timer expires
    callback: Callable[["Timer", Optional[Any]], None]
    
    # Duration after which to invoke the callback
    delay: "Duration"
    
    # Optional context passed to callback
    context: Any = field(default=None)
    
    # Timer metadata
    name: str = ""
    created_at_ns: int = field(default_factory=lambda: int(time.monotonic_ns()))
    
    # Internal state (not part of frozen identity)
    _state: TimerState = field(init=False, default=TimerState.CREATED)
    _timer_id: str = field(init=False, default_factory=lambda: str(uuid.uuid4()))
    _scheduled_at_ns: Optional[int] = field(init=False, default=None)
    
    def __post_init__(self) -> None:
        """Validate timer configuration."""
        if self.delay.is_zero() or self.delay.is_negative():
            raise ValueError("Timer delay must be positive")
    
    @property
    def timer_id(self) -> str:
        """Get the unique timer identifier."""
        return self._timer_id
    
    @property
    def state(self) -> TimerState:
        """Get current timer state."""
        return self._state
    
    def schedule(self, scheduled_at_ns: Optional[int] = None) -> TimerHandle:
        """
        Schedule this timer for execution.
        
        Args:
            scheduled_at_ns: When the timer was scheduled (for simulation)
            
        Returns:
            TimerHandle for cancellation/status queries
            
        INVARIANT: TM-TMR-002
        """
        if self._state != TimerState.CREATED:
            raise RuntimeError(f"Timer already {self._state.value}, cannot reschedule")
        
        self._scheduled_at_ns = scheduled_at_ns or int(time.monotonic_ns())
        self._state = TimerState.SCHEDULED
        
        return TimerHandle(timer_id=self._timer_id, state=self._state)
    
    def start(self) -> None:
        """
        Mark timer as running (callback invocation started).
        
        INVARIANT: TM-TMR-003
        """
        if self._state != TimerState.SCHEDULED:
            raise RuntimeError(f"Timer must be scheduled before starting, current state: {self._state.value}")
        
        self._state = TimerState.RUNNING
    
    def complete(self) -> None:
        """Mark timer as completed."""
        self._state = TimerState.COMPLETED
    
    def expire(self) -> None:
        """
        Mark timer as expired (deadline passed).
        
        INVARIANT: TM-TMR-003
        """
        self._state = TimerState.EXPIRED
    
    def cancel(self) -> None:
        """
        Cancel the timer.
        
        After cancellation, the timer cannot be used again.
        This does NOT prevent the callback from being invoked if already running.
        
        INVARIANT: TM-TMR-004
        """
        if self._state == TimerState.RUNNING:
            # Cannot cancel a running timer
            return
        self._state = TimerState.CANCELLED
    
    def elapsed(self, now_ns: Optional[int] = None) -> "Duration":
        """
        Calculate how long this timer has been active.
        
        Args:
            now_ns: Current time in nanoseconds
            
        Returns:
            Duration since scheduling (or creation if not scheduled)
        """
        now = now_ns or int(time.monotonic_ns())
        
        start_ns = self._scheduled_at_ns or self.created_at_ns
        elapsed_ns = now - start_ns
        
        from ..foundations import Duration
        return Duration.from_nanoseconds(elapsed_ns)
    
    def remaining(self, deadline_ns: Optional[int] = None) -> "Duration":
        """
        Calculate remaining time until timer expires.
        
        Args:
            deadline_ns: When the timer should expire
            
        Returns:
            Duration from now to deadline (negative if already expired)
        """
        from ..foundations import Duration
        
        now = int(time.monotonic_ns())
        deadline = deadline_ns or (self._scheduled_at_ns or self.created_at_ns) + self.delay.to_nanoseconds()
        
        remaining_ns = deadline - now
        return Duration.from_nanoseconds(remaining_ns)
    
    def is_expired(self, now_ns: Optional[int] = None) -> bool:
        """
        Check if this timer has expired.
        
        Args:
            now_ns: Current time in nanoseconds
            
        Returns:
            True if current time >= deadline
        """
        return self.remaining(now_ns).is_negative()
    
    def is_pending(self) -> bool:
        """Check if timer is pending execution."""
        return self._state == TimerState.SCHEDULED
    
    def as_handle(self) -> TimerHandle:
        """Get current state as a handle."""
        return TimerHandle(timer_id=self._timer_id, state=self._state)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "Timer",
    "TimerHandle",
    "TimerState",
]