# Clocks Package - Phase 3.16
# ============================

"""
Canonical Clock Subsystem for Gordon Core.

Clocks are the only source of time in Gordon Core. No subsystem shall
read OS clocks directly.

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

Virtual Clock: Simulated time for testing
    - Used for: Deterministic tests, simulations
    - Properties: Manipulable, can be paused/resumed/fast-forwarded

INJECTING TIME:
---------------
Time injection is a powerful testing feature. In test contexts:
1. Create an InjectedClockProvider with known start time
2. Use it in TemporalContext with simulation_mode=True
3. Control time progression explicitly
4. All temporal operations use injected time

Example:
    from src.agent.architecture.time import (
        InjectedClockProvider,
        TemporalContext,
        Instant,
        Duration
    )
    
    # Create injected clock starting at epoch 0
    provider = InjectedClockProvider(start_time=0.0)
    context = TemporalContext(provider=provider, simulation_mode=True)
    
    # Time is now controlled - advance it for testing
    provider.advance(Duration.from_seconds(10))
"""

from .provider import (
    ClockProvider,
    WallClockProvider,
    MonotonicClockProvider,
    RuntimeClockProvider,
    BootClockProvider,
)

__all__ = [
    "ClockProvider",
    "WallClockProvider",
    "MonotonicClockProvider",
    "RuntimeClockProvider",
    "BootClockProvider",
]