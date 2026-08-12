# Test Doubles - Testing Infrastructure
# ==========================================
"""
Test Doubles subpackage providing mocks, fakes, stubs, spies, simulators, and emulators.

This module follows the test doubles taxonomy:
- Real Implementation (preferred)
- Fakes (working but simplified implementations)
- Stubs (provide answers to questions, no behavior)
- Spies (record interactions for verification)
- Mocks (pre-programmed expectations, verify interactions)
- Simulators (emulate external systems)
- Emulators (full system replication)
"""

from .mocks import (
    Mock,
    MockConfig,
    MockExpectation,
    MockResult,
)

from .fakes import (
    Fake,
    FakeConfig,
    InMemoryRepository,
    FakeClock,
    FakeScheduler,
    FakeNetwork,
)

from .stubs import (
    Stub,
    StubConfig,
    StubResult,
)

from .simulators import (
    Simulator,
    SimulationConfig,
)

from .emulators import (
    Emulator,
    EmulationSession,
    EmulationState,
)

__all__ = [
    # Mocks - verify interactions
    "Mock",
    "MockConfig",
    "MockExpectation",
    "MockResult",
    
    # Fakes - working simplified implementations
    "Fake",
    "FakeConfig",
    "InMemoryRepository",
    "FakeClock",
    "FakeScheduler",
    "FakeNetwork",
    
    # Stubs - provide answers, no behavior
    "Stub",
    "StubConfig",
    "StubResult",
    
    # Simulators - external system emulation
    "Simulator",
    "SimulationConfig",
    
    # Emulators - full system replication
    "Emulator",
    "EmulationSession",
    "EmulationState",
]
