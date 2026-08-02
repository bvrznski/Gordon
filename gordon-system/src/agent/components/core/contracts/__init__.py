# Core Runtime Contracts
# =======================

"""
Core runtime contracts define foundational protocols for runtime entities.

This module provides structural interfaces without implementation.
Implementations are provided by concrete packages that depend on Core.
"""

from typing import Protocol, Any, Optional
from enum import Enum
import abc


class LifecycleState(Enum):
    """Possible lifecycle states for a runtime entity."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class LifecycleEntity(Protocol):
    """Protocol for lifecycle-managed entities."""
    
    @property
    def state(self) -> LifecycleState:
        """Return current lifecycle state."""
        ...
    
    async def initialize(self) -> None:
        """Initialize the entity (transition to INITIALIZING)."""
        ...
    
    async def start(self) -> None:
        """Start the entity (transition to STARTING, then RUNNING)."""
        ...
    
    async def stop(self) -> None:
        """Stop the entity (transition to STOPPING, then STOPPED)."""
        ...
    
    async def shutdown(self) -> None:
        """Shutdown the entity permanently."""
        ...


class Component(Protocol):
    """Protocol for Core components."""
    
    @property
    def name(self) -> str:
        """Return component identifier."""
        ...
    
    @property
    def description(self) -> Optional[str]:
        """Return component description."""
        ...
    
    async def start(self) -> None:
        """Start the component."""
        ...
    
    async def stop(self) -> None:
        """Stop the component."""
        ...


class Service(Protocol):
    """Protocol for runtime services."""
    
    @property
    def service_id(self) -> str:
        """Return service identifier."""
        ...
    
    async def start(self) -> None:
        """Start the service."""
        ...
    
    async def stop(self) -> None:
        """Stop the service."""
        ...


class RegistryEntry(Protocol):
    """Protocol for registry entries."""
    
    @property
    def key(self) -> str:
        """Return unique registry key."""
        ...
    
    @property
    def value(self) -> Any:
        """Return registry value."""
        ...


class ExecutableUnit(Protocol):
    """Protocol for executable units."""
    
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the unit with given arguments."""
        ...
    
    @property
    def name(self) -> str:
        """Return execution unit name."""
        ...


class SchedulableUnit(Protocol):
    """Protocol for schedulable units."""
    
    @property
    def priority(self) -> int:
        """Return scheduling priority (lower = higher priority)."""
        ...
    
    async def run(self) -> None:
        """Execute the schedulable unit."""
        ...


class StateOwner(Protocol):
    """Protocol for state owner entities."""
    
    @property
    def state_version(self) -> int:
        """Return current state version."""
        ...
    
    def get_state_snapshot(self) -> dict:
        """Return immutable state snapshot."""
        ...


class HealthReportingEntity(Protocol):
    """Protocol for health-reporting entities."""
    
    async def get_health_report(self) -> dict:
        """Return health status report."""
        ...
    
    @property
    def is_healthy(self) -> bool:
        """Return whether entity is healthy."""
        ...


__all__ = [
    "LifecycleState",
    "LifecycleEntity",
    "Component",
    "Service",
    "RegistryEntry",
    "ExecutableUnit",
    "SchedulableUnit",
    "StateOwner",
    "HealthReportingEntity",
]