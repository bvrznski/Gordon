# Core Runtime State Infrastructure
# ================================

"""
Core runtime state infrastructure for Gordon agent.

Provides:
- Canonical entity registries with explicit registration semantics
- Domain-neutral runtime context transport
- Immutable, versioned runtime state snapshots
- Shutdown and cancellation signaling
- Runtime-scoped resource management
- Thread-safe operations with deterministic ordering

This package implements Phase 3.2 substrate for domain-neutral Core infrastructure.
"""

from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, Any, Dict, List, Set
from enum import Enum, auto
import uuid
import time

# Re-export core types for convenience
from ..types import (
    EntityId,
    ComponentId,
    ServiceId,
    RuntimeId,
    Timestamp,
)


class RegistrationStatus(Enum):
    """Registration status values."""
    PENDING = "pending"
    IDEMPOTENT = "idempotent"  # Already registered with same descriptor
    REGISTERED = "registered"
    REPLACED = "replaced"
    DEPRECATED = "deprecated"
    REMOVED = "removed"
    REJECTED_DUPLICATE = "rejected_duplicate"
    REJECTED_CONFLICT = "rejected_conflict"


@dataclass(frozen=True)
class RegistrationDescriptor:
    """
    A registration descriptor for runtime entities.
    
    Provides:
    - Canonical entity identifier
    - Entity category for indexing
    - Implementation reference (factory or class)
    - Exposed protocols/interfaces
    - Lifecycle capability
    - Dependency declarations
    - Scope annotation
    - Registration metadata
    
    Descriptors are immutable and hashable by canonical identifier.
    """
    
    # Canonical identification
    entity_id: EntityId
    category: str  # e.g., "component", "service", "provider"
    
    # Implementation information
    implementation: Any  # Class, factory, or reference to implementation
    name: Optional[str] = None  # Human-readable name
    
    # Protocol/interface exposure
    protocols: List[str] = field(default_factory=list)  # Type aliases for interfaces
    interface: Optional[Any] = None  # Protocol class if any
    
    # Lifecycle and scope
    lifecycle_required: bool = True
    scope: str = "runtime"  # runtime, operation, request
    
    # Dependency declarations (from Phase 3.1)
    dependencies: List[EntityId] = field(default_factory=list)
    optional_dependencies: List[EntityId] = field(default_factory=list)
    
    # Metadata
    version: str = "1.0.0"
    source_package: Optional[str] = None
    source_location: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    deprecated: bool = False
    replacement_for: Optional[EntityId] = None
    
    # Status tracking
    status: RegistrationStatus = RegistrationStatus.PENDING
    registered_at: float = field(default_factory=lambda: Timestamp.now().value)


@dataclass(frozen=True)
class RegistrationResult:
    """
    Result of a registration operation.
    
    Provides structured outcome information without ambiguous booleans.
    """
    
    status: RegistrationStatus
    descriptor: Optional[RegistrationDescriptor] = None
    reason: Optional[str] = None
    registry_revision: int = 0
    
    @property
    def success(self) -> bool:
        """Check if registration succeeded."""
        return self.status in (RegistrationStatus.REGISTERED, RegistrationStatus.IDEMPOTENT)
    
    @property
    def idempotent(self) -> bool:
        """Check if this was an idempotent registration."""
        return self.status == RegistrationStatus.IDEMPOTENT
    
    @property
    def rejected(self) -> bool:
        """Check if registration was rejected."""
        return self.status in (
            RegistrationStatus.REJECTED_DUPLICATE,
            RegistrationStatus.REJECTED_CONFLICT
        )


class RegistryRevision:
    """
    Immutable registry revision tracker.
    
    Provides versioning for registry snapshots and binding resolution.
    """
    
    def __init__(self, initial_value: int = 0) -> None:
        self._value = initial_value
    
    @property
    def value(self) -> int:
        """Get current revision number."""
        return self._value
    
    def next(self) -> "RegistryRevision":
        """Return a new revision with incremented value."""
        return RegistryRevision(self._value + 1)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RegistryRevision):
            return False
        return self._value == other.value
    
    def __hash__(self) -> int:
        return hash(self._value)
    
    def __repr__(self) -> str:
        return f"RegistryRevision({self._value})"


class RuntimeState(Enum):
    """
    Runtime state values for Core infrastructure.
    
    These are domain-neutral runtime states, not capability semantics.
    """
    
    # Construction phases
    INITIAL = "initial"
    BUILDING = "building"
    VALIDATING = "validating"
    READY = "ready"
    
    # Runtime phases
    STARTING = "starting"
    RUNNING = "running"
    
    # Shutdown phases
    STOPPING = "stopping"
    STOPPED = "stopped"
    
    # Error states
    FAILED = "failed"
    TERMINATED = "terminated"


@dataclass(frozen=True)
class RuntimeStateSnapshot:
    """
    Immutable snapshot of runtime state.
    
    Provides:
    - Current runtime state
    - Registry revision at time of capture
    - Timestamp
    - Optional diagnostic information
    
    Snapshots are valid for inspection but cannot be modified.
    """
    
    state: RuntimeState
    registry_revision: int
    timestamp: float  # monotonic
    diagnostic_info: Dict[str, Any] = field(default_factory=dict)
    runtime_id: str = ""
    
    def transition_to(self, new_state: RuntimeState) -> "RuntimeStateTransition":
        """
        Create a state transition to the new state.
        
        Args:
            new_state: Target state
            
        Returns:
            A transition record ready for application
        """
        return RuntimeStateTransition(
            from_state=self.state,
            to_state=new_state,
            timestamp=time.monotonic(),
            registry_revision=self.registry_revision + 1,
            runtime_id=self.runtime_id
        )


@dataclass(frozen=True)
class RuntimeStateTransition:
    """
    A state transition command.
    
    Provides explicit, inspectable state changes with version validation.
    """
    
    from_state: RuntimeState
    to_state: RuntimeState
    timestamp: float  # monotonic
    registry_revision: int
    runtime_id: str
    reason: Optional[str] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if this transition is logically valid."""
        return self.from_state != self.to_state


class RuntimeStateStore:
    """
    Authoritative store for Core runtime state.
    
    Provides:
    - Single authoritative source of truth for runtime state
    - Immutable snapshots with versioning
    - Explicit transition operations only
    - Version validation to prevent lost updates
    
    This is the ONE authority for runtime state, not distributed across modules.
    """
    
    def __init__(self, initial_state: RuntimeState = RuntimeState.INITIAL) -> None:
        self._state = RuntimeStateSnapshot(
            state=initial_state,
            registry_revision=0,
            timestamp=time.monotonic(),
            runtime_id=str(uuid.uuid4())
        )
        self._version = 0
    
    @property
    def state(self) -> RuntimeStateSnapshot:
        """Get current state snapshot (immutable view)."""
        return self._state
    
    @property
    def version(self) -> int:
        """Get current state version."""
        return self._version
    
    def transition(
        self,
        transition: RuntimeStateTransition,
        expected_version: Optional[int] = None
    ) -> bool:
        """
        Apply a state transition.
        
        Args:
            transition: The transition to apply
            expected_version: If provided, validate against current version
            
        Returns:
            True if transition applied successfully, False otherwise
            
        Raises:
            ValueError: If transition is invalid or version doesn't match
        """
        # Validate transition
        if not transition.is_valid:
            raise ValueError(f"Invalid state transition: {transition.from_state} -> {transition.to_state}")
        
        # Check expected version for optimistic locking
        if expected_version is not None and expected_version != self._version:
            return False
        
        # Apply transition (creates new snapshot)
        self._state = RuntimeStateSnapshot(
            state=transition.to_state,
            registry_revision=transition.registry_revision,
            timestamp=transition.timestamp,
            runtime_id=transition.runtime_id
        )
        self._version += 1
        
        return True
    
    def get_snapshot(self) -> RuntimeStateSnapshot:
        """Get an immutable snapshot of current state."""
        return self._state


# Re-export from other modules
from .registry import (
    RegistryPhase,
    RegistrySnapshot,
    DuplicateRegistrationError,
    ConflictingRegistrationError,
    RegistrySealedError,
    UnknownEntityError,
    RegistryWriter,
    RegistryReader,
    Registry,
)

from .context import (
    ContextScope,
    ContextEntry,
    ContextSnapshot,
    RuntimeContext,
    ContextBuilder,
    ContextLocal,
)

from .signals import (
    SignalType,
    SignalOrigin,
    SignalState,
    CancellationRequestedError,
    ShutdownRequestedError,
    CancellationSignal,
    ShutdownSignal,
    CombinedSignal,
)

from .resources import (
    ResourceState,
    ResourceHandle,
    ResourceAcquisition,
    ResourceScope,
    ScopedResourceOwner,
)


__all__ = [
    # From main __init__.py
    "RegistrationDescriptor",
    "RegistrationResult",
    "RegistrationStatus",
    "RegistryRevision",
    "RuntimeState",
    "RuntimeStateSnapshot",
    "RuntimeStateTransition",
    "RuntimeStateStore",
    
    # From registry.py
    "RegistryPhase",
    "RegistrySnapshot",
    "DuplicateRegistrationError",
    "ConflictingRegistrationError",
    "RegistrySealedError",
    "UnknownEntityError",
    "RegistryWriter",
    "RegistryReader",
    "Registry",
    
    # From context.py
    "ContextScope",
    "ContextEntry",
    "ContextSnapshot",
    "RuntimeContext",
    "ContextBuilder",
    "ContextLocal",
    
    # From signals.py
    "SignalType",
    "SignalOrigin",
    "SignalState",
    "CancellationRequestedError",
    "ShutdownRequestedError",
    "CancellationSignal",
    "ShutdownSignal",
    "CombinedSignal",
    
    # From resources.py
    "ResourceState",
    "ResourceHandle",
    "ResourceAcquisition",
    "ResourceScope",
    "ScopedResourceOwner",
]