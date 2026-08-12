# Core Runtime Types
# ====================

"""
Core runtime value types.

These are stable, immutable types used throughout Core for:
- Entity identifiers
- Lifecycle timestamps
- Execution identifiers
- Health states
"""

from dataclasses import dataclass, field
from typing import NewType, Tuple, Optional
import uuid


# Identifier types
EntityId = NewType("EntityId", str)
ComponentId = NewType("ComponentId", str)
ServiceId = NewType("ServiceId", str)
RuntimeId = NewType("RuntimeId", str)
DependencyKey = NewType("DependencyKey", str)
ExecutionId = NewType("ExecutionId", str)
SchedulingId = NewType("SchedulingId", str)


@dataclass(frozen=True)
class EntityIdentifier:
    """Unique identifier for a runtime entity."""
    
    value: EntityId
    
    @classmethod
    def generate(cls) -> "EntityIdentifier":
        """Generate a new unique entity identifier."""
        return cls(value=EntityId(str(uuid.uuid4())))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ComponentIdentifier:
    """Unique identifier for a component."""
    
    name: str
    version: str = "1.0.0"
    
    @classmethod
    def from_string(cls, s: str) -> "ComponentIdentifier":
        """Parse component identifier from string (format: name@version)."""
        if "@" in s:
            name, version = s.split("@", 1)
            return cls(name=name, version=version)
        return cls(name=s)
    
    def __str__(self) -> str:
        return f"{self.name}@{self.version}"


@dataclass(frozen=True)
class ServiceIdentifier:
    """Unique identifier for a service."""
    
    name: str
    component: ComponentIdentifier
    
    @classmethod
    def from_string(cls, s: str) -> "ServiceIdentifier":
        """Parse service identifier from string (format: component/name)."""
        component_name, name = s.split("/", 1)
        return cls(name=name, component=ComponentIdentifier.from_string(component_name))
    
    def __str__(self) -> str:
        return f"{self.component.name}/{self.name}"


# Lifecycle timestamps
@dataclass(frozen=True)
class Timestamp:
    """Monotonic timestamp for lifecycle events."""
    
    value: float  # monotonic time in seconds
    
    @classmethod
    def now(cls) -> "Timestamp":
        """Create a timestamp from current monotonic time."""
        import time
        return cls(value=time.monotonic())
    
    def elapsed_since(self, other: "Timestamp") -> float:
        """Return elapsed time since another timestamp."""
        return self.value - other.value


@dataclass(frozen=True)
class LifecycleEvent:
    """Record of a lifecycle transition event."""
    
    timestamp: Timestamp
    from_state: str
    to_state: str
    entity_id: EntityId
    cause: Optional[str] = None


# Health states
class HealthState:
    """Health state enumeration."""
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_value(cls, value: str) -> str:
        """Validate and return health state."""
        if value not in {cls.HEALTHY, cls.DEGRADED, cls.UNHEALTHY, cls.UNKNOWN}:
            raise ValueError(f"Invalid health state: {value}")
        return value


# Runtime phase values
class RuntimePhase:
    """Runtime execution phases."""
    
    BOOTSTRAP = "bootstrap"
    INITIALIZING = "initializing"
    STARTUP = "startup"
    RUNNING = "running"
    SHUTDOWN = "shutdown"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(frozen=True)
class ExecutionContext:
    """Context for execution operations."""
    
    execution_id: ExecutionId
    parent_execution_id: Optional[ExecutionId] = None
    timeout_seconds: Optional[float] = None
    priority: int = 0


@dataclass(frozen=True)
class SchedulingContext:
    """Context for scheduling operations."""
    
    scheduling_id: SchedulingId
    entity_id: EntityId
    delay_seconds: float = 0.0
    priority: int = 100


# Dependency graph types
@dataclass(frozen=True)
class DependencyEdge:
    """Edge in dependency graph (A depends on B)."""
    
    from_entity: EntityId
    to_entity: EntityId
    required: bool = True
    
    def reverse(self) -> "DependencyEdge":
        """Return reversed edge (B is depended upon by A)."""
        return DependencyEdge(
            from_entity=self.to_entity,
            to_entity=self.from_entity,
            required=self.required
        )


@dataclass(frozen=True)
class DependencyGraphSnapshot:
    """Immutable snapshot of dependency graph state."""
    
    edges: Tuple[DependencyEdge, ...]
    vertices: Tuple[EntityId, ...]
    
    def get_dependencies(self, entity_id: EntityId) -> Tuple[EntityId, ...]:
        """Get all entities that the given entity depends on."""
        return tuple(
            edge.to_entity for edge in self.edges
            if edge.from_entity == entity_id
        )
    
    def get_dependents(self, entity_id: EntityId) -> Tuple[EntityId, ...]:
        """Get all entities that depend on the given entity."""
        return tuple(
            edge.from_entity for edge in self.edges
            if edge.to_entity == entity_id
        )


__all__ = [
    # Identifier types
    "EntityId",
    "ComponentId",
    "ServiceId",
    "RuntimeId",
    "DependencyKey",
    "ExecutionId",
    "SchedulingId",
    # Data classes
    "EntityIdentifier",
    "ComponentIdentifier",
    "ServiceIdentifier",
    "Timestamp",
    "LifecycleEvent",
    # Health states
    "HealthState",
    # Runtime phases
    "RuntimePhase",
    # Context types
    "ExecutionContext",
    "SchedulingContext",
    # Graph types
    "DependencyEdge",
    "DependencyGraphSnapshot",
]