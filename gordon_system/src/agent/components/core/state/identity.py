# Core State Identity Extensions - Phase 3.15.2
# ==============================================

"""
Canonical typed identities for Gordon Core state aggregates.

This module extends Phase 3.15.1 foundation with strongly-typed,
deterministic identity hierarchies for all state aggregate classifications.

IDENTITY HIERARCHY:
    StateTypeId      - Type classification (e.g., "lifecycle", "execution")
    AggregateId      - Aggregate identifier within a domain
    RuntimeId        - Runtime instance identifier
    BootSessionId    - Boot session identifier (restart detection)
    OwnerId          - Mutation owner identity
    AuthorityId      - Authority grant identifier
    VersionId        - Version identifier
    GenerationId     - Generation epoch identifier
    SnapshotId       - Snapshot capture identifier
    ViewId           - View/projection identifier
    ValidationId     - Validation result identifier
    TransitionId     - State transition identifier
    OperationId      - Operation request identifier
"""

# =============================================================================
# IMPORTS - Import-time purity maintained
# =============================================================================

from dataclasses import dataclass, field
from typing import (
    NewType,
    Optional,
    TypeVar,
    Generic,
    Tuple,
)
from enum import Enum, auto
import uuid
import time as _time_module

# =============================================================================
# STATE TYPE IDENTITY
# =============================================================================


class StateTypeId(str, Enum):
    """
    Canonical state type identifiers.
    
    TYPES:
        CORE        - Core infrastructure state
        LIFECYCLE   - Lifecycle state machine
        EXECUTION   - Execution flow state
        RUNTIME     - Runtime management state
        COMPONENT   - Component instance state
        SERVICE     - Service state
        STREAM      - Stream processing state
        RESOURCE    - Resource allocation state
        THREAD      - Thread execution state
        TRANSACTION - Transaction context state
        PERSISTENCE - Persistence operation state
    
    INVARIANTS:
        TYPE-001: Every state aggregate has exactly one type
        TYPE-002: Type is immutable and deterministic
        TYPE-003: Types are repository-wide consistent
    """
    
    # Core types
    CORE = "core"
    LIFECYCLE = "lifecycle"
    EXECUTION = "execution"
    
    # Runtime types
    RUNTIME = "runtime"
    COMPONENT = "component"
    SERVICE = "service"
    
    # Processing types
    STREAM = "stream"
    THREAD = "thread"
    
    # Resource types
    RESOURCE = "resource"
    TRANSACTION = "transaction"
    
    # Operational types
    PERSISTENCE = "persistence"
    
    @classmethod
    def from_string(cls, value: str) -> "StateTypeId":
        """Parse a string into a StateTypeId."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid StateTypeId: {value}")


# =============================================================================
# AGGREGATE IDENTITY
# =============================================================================


@dataclass(frozen=True, order=True, eq=True)
class AggregateId:
    """
    Canonical unique identifier for a state aggregate.
    
    An aggregate is the root of a state cluster with consistency boundaries.
    
    INVARIANTS:
        AGG-001: Every state aggregate has exactly one aggregate ID
        AGG-002: Aggregate ID is immutable once created
        AGG-003: No two aggregates share the same ID
        AGG-004: Aggregate IDs are globally unique within their type
    """
    
    value: str = field(default_factory=lambda: f"agg_{uuid.uuid4().hex[:24]}")
    type_id: StateTypeId = field(default=StateTypeId.CORE)
    namespace: Optional[str] = None  # e.g., "application", "runtime"
    
    @classmethod
    def generate(
        cls,
        type_id: StateTypeId = StateTypeId.CORE,
        namespace: Optional[str] = None,
        suffix: Optional[str] = None,
    ) -> "AggregateId":
        """Generate a new aggregate ID."""
        value = f"agg_{uuid.uuid4().hex[:20]}"
        if namespace:
            value = f"{namespace}_{value}"
        if suffix:
            value = f"{value}_{suffix}"
        return cls(value=value, type_id=type_id, namespace=namespace)
    
    def to_string(self) -> str:
        """Convert to string representation."""
        result = self.value
        if self.namespace:
            result = f"{self.namespace}:{result}"
        return result
    
    @classmethod
    def from_string(cls, value: str) -> "AggregateId":
        """Parse a string into an AggregateId."""
        namespace = None
        actual_value = value
        
        if ":" in value:
            parts = value.split(":", 1)
            namespace = parts[0]
            actual_value = parts[1]
        
        return cls(value=actual_value, namespace=namespace)
    
    def matches_type(self, type_id: StateTypeId) -> bool:
        """Check if this aggregate ID matches the given type."""
        return self.type_id == type_id
    
    def matches_namespace(self, namespace: str) -> bool:
        """Check if this aggregate ID matches the given namespace."""
        return self.namespace == namespace


# =============================================================================
# RUNTIME IDENTITY
# =============================================================================


@dataclass(frozen=True, order=True, eq=True)
class RuntimeId:
    """
    Canonical identifier for a runtime instance.
    
    Runtime isolation ensures Runtime A cannot access/modify Runtime B state.
    
    INVARIANTS:
        RT-001: Every runtime instance has exactly one runtime ID
        RT-002: Runtime IDs are globally unique across processes
        RT-003: Runtime ID is immutable once assigned
        RT-004: Runtime A cannot claim to be Runtime B
    """
    
    value: str = field(default_factory=lambda: f"rt_{uuid.uuid4().hex[:20]}")
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def generate(cls) -> "RuntimeId":
        """Generate a new runtime ID."""
        return cls()
    
    def is_runtime(self, other_value: str) -> bool:
        """Check if this runtime ID matches the given value."""
        return self.value == other_value


# =============================================================================
# BOOT SESSION IDENTITY
# =============================================================================


@dataclass(frozen=True, order=True, eq=True)
class BootSessionId:
    """
    Canonical identifier for a boot session.
    
    Boot sessions enable restart detection and state invalidation.
    
    INVARIANTS:
        BS-001: Every boot session has exactly one ID
        BS-002: Session IDs are unique per process lifetime
        BS-003: Old sessions are invalidated on restart
    """
    
    value: str = field(default_factory=lambda: f"bs_{uuid.uuid4().hex[:20]}")
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def generate(cls) -> "BootSessionId":
        """Generate a new boot session ID."""
        return cls()
    
    def is_session(self, other_value: str) -> bool:
        """Check if this session ID matches the given value."""
        return self.value == other_value


# =============================================================================
# OWNER IDENTITY
# =============================================================================


@dataclass(frozen=True, order=True, eq=True)
class OwnerId:
    """
    Canonical identifier for a state owner.
    
    The owner is the only entity with mutation authority.
    
    INVARIANTS:
        OWN-001: Every mutable state has exactly one owner
        OWN-002: Owner IDs are globally unique within scope
        OWN-003: Owner identity cannot be forged
    """
    
    value: str = field(default_factory=lambda: f"owner_{uuid.uuid4().hex[:20]}")
    kind: Optional[str] = None  # e.g., "lifecycle", "execution"
    
    @classmethod
    def for_kind(cls, kind: str) -> "OwnerId":
        """Create an owner ID for a specific kind."""
        return cls(value=f"owner_{kind}_{uuid.uuid4().hex[:16]}".replace("-", "_"), kind=kind)
    
    def is_owner(self, other_value: str) -> bool:
        """Check if this owner ID matches the given value."""
        return self.value == other_value
    
    def matches_kind(self, kind: str) -> bool:
        """Check if this owner matches the given kind."""
        return self.kind == kind


# =============================================================================
# AUTHORITY IDENTITY
# =============================================================================


@dataclass(frozen=True, order=True, eq=True)
class AuthorityId:
    """
    Canonical identifier for an authority grant.
    
    Authorities may be delegated or transferred with evidence.
    
    INVARIANTS:
        AUTH-001: Every authority has exactly one ID
        AUTH-002: Authority IDs are globally unique
        AUTH-003: Authority grants are traceable via this ID
    """
    
    value: str = field(default_factory=lambda: f"auth_{uuid.uuid4().hex[:20]}")
    granted_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def generate(cls) -> "AuthorityId":
        """Generate a new authority ID."""
        return cls()
    
    def is_authority(self, other_value: str) -> bool:
        """Check if this authority ID matches the given value."""
        return self.value == other_value


# =============================================================================
# VERSION IDENTITY
# =============================================================================


@dataclass(frozen=True, order=True, eq=True)
class VersionId:
    """
    Canonical identifier for a state version.
    
    Versions track evolution within a generation.
    
    INVARIANTS:
        VER-001: Every version has exactly one ID
        VER-002: Version IDs are deterministic from sequence number
        VER-003: Versions form a partial order
    """
    
    value: str = field(default_factory=lambda: f"ver_{uuid.uuid4().hex[:20]}")
    sequence: int = 0
    
    @classmethod
    def generate(cls, sequence: int = 0) -> "VersionId":
        """Generate a new version ID with the given sequence."""
        value = f"ver_seq{sequence}_{uuid.uuid4().hex[:16]}"
        return cls(value=value.replace("-", "_"), sequence=sequence)
    
    def is_version(self, other_value: str) -> bool:
        """Check if this version ID matches the given value."""
        return self.value == other_value
    
    def matches_sequence(self, sequence: int) -> bool:
        """Check if this version has the given sequence number."""
        return self.sequence == sequence


# =============================================================================
# GENERATION IDENTITY
# =============================================================================


@dataclass(frozen=True, order=True, eq=True)
class GenerationId:
    """
    Canonical identifier for a generation (epoch).
    
    Generations change on restart, migration, or other epoch events.
    
    INVARIANTS:
        GEN-001: Every generation has exactly one ID
        GEN-002: Generation IDs are monotonically increasing
        GEN-003: Stale generations are rejected
    """
    
    value: str = field(default_factory=lambda: f"gen_{uuid.uuid4().hex[:20]}")
    epoch: int = 0
    
    @classmethod
    def generate(cls, epoch: int = 0) -> "GenerationId":
        """Generate a new generation ID with the given epoch."""
        value = f"gen_e{epoch}_{uuid.uuid4().hex[:16]}"
        return cls(value=value.replace("-", "_"), epoch=epoch)
    
    def is_generation(self, other_value: str) -> bool:
        """Check if this generation ID matches the given value."""
        return self.value == other_value
    
    def matches_epoch(self, epoch: int) -> bool:
        """Check if this generation has the given epoch number."""
        return self.epoch == epoch
    
    def is_stale(self, current_epoch: int) -> bool:
        """Check if this generation is stale (older than current)."""
        return self.epoch < current_epoch


# =============================================================================
# SNAPSHOT IDENTITY
# =============================================================================


@dataclass(frozen=True, order=True, eq=True)
class SnapshotId:
    """
    Canonical identifier for a state snapshot.
    
    Snapshots are immutable observations at specific versions.
    
    INVARIANTS:
        SNAP-001: Every snapshot has exactly one ID
        SNAP-002: Snapshot IDs are globally unique
        SNAP-003: Snapshots are never mutated
    """
    
    value: str = field(default_factory=lambda: f"snap_{uuid.uuid4().hex[:20]}")
    captured_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def generate(cls) -> "SnapshotId":
        """Generate a new snapshot ID."""
        return cls()
    
    def is_snapshot(self, other_value: str) -> bool:
        """Check if this snapshot ID matches the given value."""
        return self.value == other_value


# =============================================================================
# VIEW IDENTITY
# =============================================================================


@dataclass(frozen=True, order=True, eq=True)
class ViewId:
    """
    Canonical identifier for a state view/projection.
    
    Views are filtered/derived representations of state.
    
    INVARIANTS:
        VIEW-001: Every view has exactly one ID
        VIEW-002: View IDs are globally unique
        VIEW-003: Views are immutable once created
    """
    
    value: str = field(default_factory=lambda: f"view_{uuid.uuid4().hex[:20]}")
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def generate(cls) -> "ViewId":
        """Generate a new view ID."""
        return cls()
    
    def is_view(self, other_value: str) -> bool:
        """Check if this view ID matches the given value."""
        return self.value == other_value


# =============================================================================
# VALIDATION IDENTITY
# =============================================================================


@dataclass(frozen=True, order=True, eq=True)
class ValidationId:
    """
    Canonical identifier for a validation result.
    
    Validations produce structured findings.
    
    INVARIANTS:
        VAL-001: Every validation has exactly one ID
        VAL-002: Validation IDs are globally unique
        VAL-003: Results are deterministic from input
    """
    
    value: str = field(default_factory=lambda: f"val_{uuid.uuid4().hex[:20]}")
    validated_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def generate(cls) -> "ValidationId":
        """Generate a new validation ID."""
        return cls()
    
    def is_validation(self, other_value: str) -> bool:
        """Check if this validation ID matches the given value."""
        return self.value == other_value


# =============================================================================
# TRANSITION IDENTITY
# =============================================================================


@dataclass(frozen=True, order=True, eq=True)
class TransitionId:
    """
    Canonical identifier for a state transition.
    
    Transitions represent valid state machine changes.
    
    INVARIANTS:
        TRA-001: Every transition has exactly one ID
        TRA-002: Transition IDs are globally unique
        TRA-003: Transitions have well-defined pre/post conditions
    """
    
    value: str = field(default_factory=lambda: f"tra_{uuid.uuid4().hex[:20]}")
    occurred_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def generate(cls) -> "TransitionId":
        """Generate a new transition ID."""
        return cls()
    
    def is_transition(self, other_value: str) -> bool:
        """Check if this transition ID matches the given value."""
        return self.value == other_value


# =============================================================================
# OPERATION IDENTITY
# =============================================================================


@dataclass(frozen=True, order=True, eq=True)
class OperationId:
    """
    Canonical identifier for a state operation.
    
    Operations are requests to mutate state.
    
    INVARIANTS:
        OP-001: Every operation has exactly one ID
        OP-002: Operation IDs are globally unique
        OP-003: Operations may be retried with same ID (idempotent)
    """
    
    value: str = field(default_factory=lambda: f"op_{uuid.uuid4().hex[:20]}")
    requested_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def generate(cls) -> "OperationId":
        """Generate a new operation ID."""
        return cls()
    
    @classmethod
    def for_idempotency(cls, idempotency_key: str) -> "OperationId":
        """Create an operation ID from an idempotency key."""
        value = f"op_{uuid.uuid5(uuid.NAMESPACE_DNS, idempotency_key).hex[:20]}"
        return cls(value=value)
    
    def is_operation(self, other_value: str) -> bool:
        """Check if this operation ID matches the given value."""
        return self.value == other_value


# =============================================================================
# SCOPE IDENTITY
# =============================================================================


class ScopeId(str, Enum):
    """
    Canonical scope identifiers for state visibility boundaries.
    
    SCOPES:
        PROCESS      - Process-wide scope
        APPLICATION  - Application-level scope
        RUNTIME      - Runtime-specific scope
        BOOT_SESSION - Boot session scope
        SUBSYSTEM    - Subsystem-scoped state
        COMPONENT    - Component-scoped state
        SERVICE      - Service-scoped state
        REQUEST      - Request-scoped state
        TRANSACTION  - Transaction-scoped state
        STREAM       - Stream-scoped state
        RESOURCE     - Resource-specific scope
        LOCAL        - Local-only scope
        PERSISTENT   - Persisted state scope
        DISTRIBUTED  - Distributed system scope
    
    INVARIANTS:
        SCOPE-001: Every state has exactly one primary scope
        SCOPE-002: Scope defines visibility and isolation boundaries
        SCOPE-003: Scopes may inherit from parent scopes
    """
    
    PROCESS = "process"
    APPLICATION = "application"
    RUNTIME = "runtime"
    BOOT_SESSION = "boot_session"
    SUBSYSTEM = "subsystem"
    COMPONENT = "component"
    SERVICE = "service"
    REQUEST = "request"
    TRANSACTION = "transaction"
    STREAM = "stream"
    RESOURCE = "resource"
    LOCAL = "local"
    PERSISTENT = "persistent"
    DISTRIBUTED = "distributed"
    
    @classmethod
    def from_string(cls, value: str) -> "ScopeId":
        """Parse a string into a ScopeId."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid ScopeId: {value}")
    
    HIERARCHY = {
        ScopeId.PROCESS: [ScopeId.APPLICATION, ScopeId.RUNTIME],
        ScopeId.APPLICATION: [ScopeId.SUBSYSTEM, ScopeId.REQUEST],
        ScopeId.SUBSYSTEM: [ScopeId.COMPONENT],
        ScopeId.COMPONENT: [ScopeId.SERVICE],
        ScopeId.REQUEST: [ScopeId.TRANSACTION],
        ScopeId.RUNTIME: [ScopeId.BOOT_SESSION],
    }
    
    def is_ancestor_of(self, other: "ScopeId") -> bool:
        """
        Check if this scope is an ancestor of the other.
        
        Hierarchy (parent -> child):
            PROCESS > APPLICATION > RUNTIME > BOOT_SESSION
            APPLICATION > SUBSYSTEM > COMPONENT > SERVICE
            REQUEST > TRANSACTION
            
        Returns True if self is in the inheritance path to other.
        """
        hierarchy = ScopeId.HIERARCHY
        
        if other not in hierarchy.get(self, []):
            return False
        return True
    
    def is_descendant_of(self, other: "ScopeId") -> bool:
        """Check if this scope descends from the other."""
        return other.is_ancestor_of(self)
    
    def inherits_from(self, parent_scope: "ScopeId") -> bool:
        """Check if this scope can inherit properties from parent."""
        return self == parent_scope or self.is_descendant_of(parent_scope)


# =============================================================================
# PUBLIC API
# =============================================================================


__all__ = [
    # Type IDs
    "StateTypeId",
    
    # Identity classes
    "AggregateId",
    "RuntimeId",
    "BootSessionId",
    "OwnerId",
    "AuthorityId",
    "VersionId",
    "GenerationId",
    "SnapshotId",
    "ViewId",
    "ValidationId",
    "TransitionId",
    "OperationId",
    
    # Scope IDs
    "ScopeId",
]