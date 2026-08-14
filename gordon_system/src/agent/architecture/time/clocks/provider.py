# Clock Providers - Phase 3.16
# ============================

"""
Canonical Clock Provider Implementations.

All time access in Gordon Core goes through ClockProvider implementations.
No subsystem shall read OS clocks directly.

IMPLEMENTATIONS:
----------------
WallClockProvider: Real-world time from os.time()
MonotonicClockProvider: Non-decreasing time for measurements
RuntimeClockProvider: Time since runtime startup
BootClockProvider: Time since system boot (Linux-specific)
VirtualClockProvider: Simulated time for testing

USAGE EXAMPLES:
---------------
# Get current wall time
provider = WallClockProvider()
instant = provider.get_instant()

# Measure duration with monotonic clock
monotonic = MonotonicClockProvider()
start = monotonic.get_time()
# ... work ...
duration_ms = (monotonic.get_time() - start) * 1000

# Use in simulation mode for deterministic tests
from time.clocks import VirtualClockProvider
from architecture.time.types.duration import Duration

provider = VirtualClockProvider(start_time=0.0)
context = TemporalContext(provider, simulation_mode=True)

# Advance time by 10 seconds
provider.advance(Duration.from_seconds(10))
"""

import os
import time
from typing import Optional

from ..foundations import (
    ClockProvider as BaseClockProvider,
    Instant,
    Duration,
    ClockType,
    TimeSource,
)


class WallClockProvider(BaseClockProvider):
    """
    Wall clock provider using OS real-time clock.
    
    This provides real-world time from the system's hardware clock.
    Note: This may jump due to NTP corrections or manual adjustments.
    
    Use for:
        - External timestamps
        - User-facing times
        - Logging with wall-clock context
        
    DON'T use for:
        - Duration measurements (use MonotonicClockProvider)
        - Timeout calculations (use MonotonicClockProvider)
    """
    
    def __init__(self):
        self._clock_type = ClockType.REAL_WALL
    
    @property
    def clock_type(self) -> ClockType:
        return self._clock_type
    
    def get_time(self) -> float:
        """Get current time as Unix timestamp in seconds."""
        return time.time()
    
    def get_instant(self) -> Instant:
        """Get current time as an Instant object."""
        return Instant.from_seconds(time.time(), TimeSource.WALL)
    
    def get_duration(self, start_time: float, end_time: float) -> Duration:
        """
        Calculate duration between two timestamps.
        
        Args:
            start_time: Start timestamp in seconds
            end_time: End timestamp in seconds
            
        Returns:
            Duration representing the interval
        """
        return Duration.from_seconds(end_time - start_time, TimeSource.WALL)
    
    def sleep(self, duration: float) -> None:
        """Sleep for specified duration using wall clock."""
        time.sleep(duration)
    
    def is_simulated(self) -> bool:
        """Check if in simulation mode (always False for real clocks)."""
        return False


class MonotonicClockProvider(BaseClockProvider):
    """
    Monotonic clock provider for duration measurements.
    
    This provides a non-decreasing clock that is guaranteed to never
    go backward, even if system time is adjusted. It's the recommended
    clock for all internal timing operations.
    
    Use for:
        - Duration calculations
        - Timeout measurements
        - Scheduling decisions
        - Performance benchmarking
        
    DON'T use for:
        - User-facing times (not human-readable)
        - External timestamps
    """
    
    def __init__(self):
        self._clock_type = ClockType.MONOTONIC
    
    @property
    def clock_type(self) -> ClockType:
        return self._clock_type
    
    def get_time(self) -> float:
        """Get monotonic time in seconds."""
        return time.monotonic()
    
    def get_instant(self) -> Instant:
        """
        Get current monotonic time as an Instant.
        
        Note: The instant is relative to some arbitrary epoch.
        Use only for duration calculations, not absolute timestamps.
        """
        # Convert to nanoseconds and back for compatibility
        ns = int(time.monotonic_ns())
        return Instant.from_nanoseconds(ns, TimeSource.MONOTONIC)
    
    def get_duration(self, start_time: float, end_time: float) -> Duration:
        """
        Calculate duration between two monotonic timestamps.
        
        Args:
            start_time: Start timestamp in seconds
            end_time: End timestamp in seconds
            
        Returns:
            Duration representing the interval
        """
        return Duration.from_seconds(end_time - start_time, TimeSource.MONOTONIC)
    
    def sleep(self, duration: float) -> None:
        """Sleep for specified duration using monotonic clock."""
        time.sleep(duration)
    
    def is_simulated(self) -> bool:
        """Check if in simulation mode (always False for real clocks)."""
        return False


class RuntimeClockProvider(BaseClockProvider):
    """
    Runtime-local clock provider.
    
    This provides time relative to when the runtime started. It's reset
    on every runtime restart, making it useful for tracking runtime
    lifecycle events.
    
    The epoch is: runtime startup time
    
    Use for:
        - Runtime uptime calculations
        - Runtime-specific timeouts
        - Lifecycle monitoring
        
    DON'T use for:
        - Cross-runtime comparisons
        - External timestamps
    """
    
    _RUNTIME_START_TIME = None  # Set once at first access
    
    def __init__(self):
        self._clock_type = ClockType.RUNTIME
        if RuntimeClockProvider._RUNTIME_START_TIME is None:
            RuntimeClockProvider._RUNTIME_START_TIME = time.monotonic()
    
    @property
    def clock_type(self) -> ClockType:
        return self._clock_type
    
    def get_time(self) -> float:
        """Get runtime uptime in seconds."""
        if RuntimeClockProvider._RUNTIME_START_TIME is None:
            RuntimeClockProvider._RUNTIME_START_TIME = time.monotonic()
        return time.monotonic() - RuntimeClockProvider._RUNTIME_START_TIME
    
    def get_instant(self) -> Instant:
        """
        Get current runtime time as an Instant.
        
        The instant represents runtime uptime in nanoseconds.
        """
        if RuntimeClockProvider._RUNTIME_START_TIME is None:
            RuntimeClockProvider._RUNTIME_START_TIME = time.monotonic()
        
        runtime_ns = int((time.monotonic() - RuntimeClockProvider._RUNTIME_START_TIME) * 1_000_000_000)
        return Instant.from_nanoseconds(runtime_ns, TimeSource.RUNTIME)
    
    def get_duration(self, start_time: float, end_time: float) -> Duration:
        """
        Calculate duration between two runtime timestamps.
        
        Args:
            start_time: Start timestamp in seconds (runtime uptime)
            end_time: End timestamp in seconds (runtime uptime)
            
        Returns:
            Duration representing the interval
        """
        return Duration.from_seconds(end_time - start_time, TimeSource.RUNTIME)
    
    def sleep(self, duration: float) -> None:
        """Sleep for specified duration using monotonic clock."""
        time.sleep(duration)
    
    def is_simulated(self) -> bool:
        """Check if in simulation mode (always False for real clocks)."""
        return False


class BootClockProvider(BaseClockProvider):
    """
    System boot-time clock provider.
    
    This provides time since system boot. On Linux, this uses the
    monotonic clock which starts at 0 on boot. On other systems,
    it falls back to a similar approach.
    
    The epoch is: system boot time
    
    Use for:
        - System uptime monitoring
        - Boot-based scheduling
        - Hardware lifecycle tracking
        
    DON'T use for:
        - Cross-system comparisons
        - External timestamps
    """
    
    def __init__(self):
        self._clock_type = ClockType.BOOT
    
    @property
    def clock_type(self) -> ClockType:
        return self._clock_type
    
    def get_time(self) -> float:
        """Get system uptime in seconds."""
        # On Linux, monotonic starts at 0 on boot
        # This is the closest we can get to boot time without platform APIs
        return time.monotonic()
    
    def get_instant(self) -> Instant:
        """
        Get current boot time as an Instant.
        
        The instant represents boot uptime in nanoseconds.
        """
        ns = int(time.monotonic_ns())
        return Instant.from_nanoseconds(ns, TimeSource.BOOT)
    
    def get_duration(self, start_time: float, end_time: float) -> Duration:
        """
        Calculate duration between two boot timestamps.
        
        Args:
            start_time: Start timestamp in seconds
            end_time: End timestamp in seconds
            
        Returns:
            Duration representing the interval
        """
        return Duration.from_seconds(end_time - start_time, TimeSource.BOOT)
    
    def sleep(self, duration: float) -> None:
        """Sleep for specified duration using monotonic clock."""
        time.sleep(duration)
    
    def is_simulated(self) -> bool:
        """Check if in simulation mode (always False for real clocks)."""
        return False


class VirtualClockProvider(BaseClockProvider):
    """
    Virtual/simulated clock provider for deterministic testing.
    
    This provider allows explicit control over time progression,
    enabling deterministic tests and simulations. Time can be:
        - Advanced manually
        - Set to specific values
        - Frozen in place
    
    Use for:
        - Unit tests needing deterministic timing
        - Simulations
        - Replay of recorded events
        - Future prediction scenarios
        
    DON'T use for:
        - Production code (should use real clocks)
        - Real-time operations
    """
    
    def __init__(self, start_time: float = 0.0):
        self._clock_type = ClockType.VIRTUAL_MANUAL
        self._current_time_ns = int(start_time * 1_000_000_000)
        self._is_frozen = False
    
    @property
    def clock_type(self) -> ClockType:
        return self._clock_type
    
    def get_time(self) -> float:
        """Get current virtual time in seconds."""
        if self._is_frozen:
            return self._current_time_ns / 1_000_000_000.0
        # Virtual clock doesn't advance on its own
        return self._current_time_ns / 1_000_000_000.0
    
    def get_instant(self) -> Instant:
        """Get current virtual time as an Instant."""
        if self._is_frozen:
            return Instant.from_nanoseconds(self._current_time_ns, TimeSource.SIMULATION)
        return Instant.from_nanoseconds(self._current_time_ns, TimeSource.SIMULATION)
    
    def get_duration(self, start_time: float, end_time: float) -> Duration:
        """
        Calculate duration between two virtual timestamps.
        
        Args:
            start_time: Start timestamp in seconds
            end_time: End timestamp in seconds
            
        Returns:
            Duration representing the interval
        """
        return Duration.from_seconds(end_time - start_time, TimeSource.SIMULATION)
    
    def sleep(self, duration: float) -> None:
        """
        Sleep for specified duration by advancing virtual time.
        
        In simulation mode, sleep doesn't actually block - it just
        advances the virtual clock.
        
        Args:
            duration: Duration to advance in seconds
        """
        self._current_time_ns += int(duration * 1_000_000_000)
    
    def is_simulated(self) -> bool:
        """Check if in simulation mode."""
        return True
    
    # Control methods for virtual clock
    def set_time(self, time_seconds: float) -> None:
        """
        Set the current virtual time.
        
        Args:
            time_seconds: New time in seconds since epoch
        """
        self._current_time_ns = int(time_seconds * 1_000_000_000)
    
    def advance(self, duration: Duration) -> None:
        """
        Advance virtual time by a duration.
        
        Args:
            duration: Amount to advance
        """
        self._current_time_ns += duration.to_nanoseconds()
    
    def freeze(self) -> None:
        """Freeze virtual time (prevent auto-advancement)."""
        self._is_frozen = True
    
    def unfreeze(self) -> None:
        """Unfreeze virtual time."""
        self._is_frozen = False


__all__ = [
    "WallClockProvider",
    "MonotonicClockProvider",
    "RuntimeClockProvider",
    "BootClockProvider",
    "VirtualClockProvider",
]