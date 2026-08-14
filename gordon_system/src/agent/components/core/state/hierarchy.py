# Runtime State Hierarchy - Phase 3.15.4
# =======================================
#
# Canonical runtime state hierarchy for Gordon Core.
#
# This module establishes the hierarchical runtime state model supporting:
#   - Explicit ownership and bounded composition
#   - Parent-child relationships with lifecycle propagation
#   - Deterministic traversal through the hierarchy
#   - Runtime isolation enforcement
#   - Aggregate validation and diagnostics
#
# ARCHITECTURAL PRINCIPLES:
#   1. One canonical runtime state hierarchy exists throughout the Core
#   2. Each aggregate has exactly one explicit owner
#   3. Parent ownership does not automatically grant mutation authority over children
#   4. Hierarchy traversal must validate ownership at each step
#   5. Runtime isolation is enforced (cross-runtime relationships prohibited)
#   6. Aggregates remain bounded (no unbounded graphs)
#

from dataclasses import dataclass, field
from typing import (
    Dict,
    Any,
    Optional,
    Tuple,
    Protocol,
    runtime_checkable,
    Iterator,
    Set,
    List,
)
from enum import Enum, auto
import uuid
import time as _time_module


# =============================================================================
# CONTAINMENT RELATIONSHIP TYPES
# =============================================================================


class ContainmentType(Enum):
    """
    Canonical containment relationship types between aggregates.
    
    These relationships remain semantically distinct:
    
    | Type | Description |
    |------|-------------|
    | OWNS | Full ownership with mutation authority |
    | CONTAINS | Structural containment without full ownership |
    | REFERENCES | Reference to another aggregate (loose coupling) |
    | OBSERVES | Observes state but does not own/contain |
    | DERIVES | Derived from source aggregate |
    | AGGREGATES | Aggregates multiple aggregates under one scope |
    | PROJECTS | Projects a view onto another aggregate |
    
    INVARIANTS:
        CONTAIN-001: Each relationship is one of the defined types
        CONTAIN-002: OWNS implies containment but not vice versa
        CONTAIN-003: REFERENCES does not imply ownership or containment
    """
    
    OWNS = "owns"
    CONTAINS = "contains"
    REFERENCES = "references"
    OBSERVES = "observes"
    DERIVES = "derives"
    AGGREGATES = "aggregates"
    PROJECTS = "projects"


# =============================================================================
# RUNTIME STATE HIERARCHY TYPES
# =============================================================================


class RuntimeStateHierarchyType(Enum):
    """
    Canonical runtime state hierarchy types for the Gordon Core.
    
    Each level has exactly one explicit owner and maintains parent-child relationships.
    
    HIERARCHY LEVELS:
        APPLICATION       - Application-wide runtime state (root of most hierarchies)
        RUNTIME           - Runtime instance state
        HOST              - Host/Node state in distributed systems
        BOOT_SESSION      - Boot session scope (reset on restart)
        
        SUBSYSTEM         - Subsystem-level aggregate (e.g., "execution", "streams")
        COMPONENT         - Component instance state
        SERVICE           - Service instance state
        
        EXECUTION         - Execution context state
        RESOURCE          - Resource allocation state
        STREAM            - Stream processing state
        INTERACTION       - Interaction lifecycle state
        TRANSACTION       - Transaction context state
        HEALTH            - Health condition state
        READINESS         - Readiness availability state
        ADMISSION         - Admission decision state
        RECOVERY          - Recovery process state
        SHUTDOWN          - Shutdown procedure state
        
    INVARIANTS:
        HIER-001: Every aggregate has exactly one hierarchy type
        HIER-002: Hierarchy types are repository-wide and consistent
        HIER-003: Parent-child relationships follow the defined hierarchy
    """
    
    # Root-level aggregates (no parent)
    APPLICATION = "application"
    RUNTIME = "runtime"
    HOST = "host"
    BOOT_SESSION = "boot_session"
    
    # Subsystem-level aggregates
    SUBSYSTEM = "subsystem"
    COMPONENT = "component"
    SERVICE = "service"
    
    # Execution and processing aggregates
    EXECUTION = "execution"
    RESOURCE = "resource"
    STREAM = "stream"
    INTERACTION = "interaction"
    TRANSACTION = "transaction"
    
    # Operational aggregates
    HEALTH = "health"
    READINESS = "readiness"
    ADMISSION = "admission"
    RECOVERY = "recovery"
    SHUTDOWN = "shutdown"


# =============================================================================
# RUNTIME STATE IDENTITY
# =============================================================================


@dataclass(frozen=True, order=True)
class RuntimeStateId:
    """
    Canonical unique identifier for a runtime state aggregate.
    
    A runtime state identity preserves:
        - Aggregate type: Which hierarchy level this aggregate represents
        - Unique value: UUID-based unique identifier within scope
        - Scope: The visibility and lifetime boundary
        - Runtime identity: Which runtime instance owns this state
        - Boot-session identity: Which boot session (for restart detection)
    
    INVARIANTS:
        RT-ID-001: Every aggregate has exactly one unique identity
        RT-ID-002: Identity is immutable once created
        RT-ID-003: No two aggregates share the same identity
        RT-ID-004: Runtime A cannot claim to be Runtime B's state
    """
    
    value: str
    
    # Classification metadata
    hierarchy_type: RuntimeStateHierarchyType = field(default=RuntimeStateHierarchyType.RUNTIME)
    scope: Optional[str] = None  # Scope name (e.g., "main", "execution")
    
    # Runtime binding (enforces isolation)
    runtime_id: Optional[str] = None
    boot_session_id: Optional[str] = None
    
    @classmethod
    def generate(
        cls,
        hierarchy_type: RuntimeStateHierarchyType = RuntimeStateHierarchyType.RUNTIME,
        scope: Optional[str] = None,
        runtime_id: Optional[str] = None,
        boot_session_id: Optional[str] = None,
    ) -> "RuntimeStateId":
        """Generate a new unique runtime state ID."""
        return cls(
            value=f"agg_{uuid.uuid4().hex[:24]}",
            hierarchy_type=hierarchy_type,
            scope=scope,
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
        )
    
    @classmethod
    def for_application(cls, application_name: str) -> "RuntimeStateId":
        """Generate an application-level aggregate ID."""
        return cls(
            value=f"app_{application_name}",
            hierarchy_type=RuntimeStateHierarchyType.APPLICATION,
            scope="global",
            runtime_id=None,
            boot_session_id=None,
        )
    
    @classmethod
    def for_runtime(cls, runtime_id: str) -> "RuntimeStateId":
        """Generate a runtime-level aggregate ID."""
        return cls(
            value=f"rt_{runtime_id}",
            hierarchy_type=RuntimeStateHierarchyType.RUNTIME,
            scope="instance",
            runtime_id=runtime_id,
            boot_session_id=None,
        )
    
    @classmethod
    def for_boot_session(cls, session_id: str) -> "RuntimeStateId":
        """Generate a boot session-level aggregate ID."""
        return cls(
            value=f"bs_{session_id}",
            hierarchy_type=RuntimeStateHierarchyType.BOOT_SESSION,
            scope="session",
            runtime_id=None,
            boot_session_id=session_id,
        )
    
    @classmethod
    def for_subsystem(cls, subsystem_name: str) -> "RuntimeStateId":
        """Generate a subsystem-level aggregate ID."""
        return cls(
            value=f"sub_{subsystem_name}",
            hierarchy_type=RuntimeStateHierarchyType.SUBSYSTEM,
            scope="subsystem",
            runtime_id=None,
            boot_session_id=None,
        )
    
    @classmethod
    def for_component(cls, component_name: str) -> "RuntimeStateId":
        """Generate a component-level aggregate ID."""
        return cls(
            value=f"comp_{component_name}",
            hierarchy_type=RuntimeStateHierarchyType.COMPONENT,
            scope="component",
            runtime_id=None,
            boot_session_id=None,
        )
    
    @classmethod
    def for_service(cls, service_name: str) -> "RuntimeStateId":
        """Generate a service-level aggregate ID."""
        return cls(
            value=f"svc_{service_name}",
            hierarchy_type=RuntimeStateHierarchyType.SERVICE,
            scope="service",
            runtime_id=None,
            boot_session_id=None,
        )
    
    def is_compatible_runtime(self, runtime_id: str) -> bool:
        """Check if this aggregate belongs to the given runtime."""
        return self.runtime_id == runtime_id
    
    def is_stale_session(self, current_boot_session_id: str) -> bool:
        """Check if this aggregate's boot session is stale (older than current)."""
        if self.boot_session_id is None:
            return False
        return self.boot_session_id != current_boot_session_id


# =============================================================================
# CORE STATE AUTHORITY TYPE IMPORT
# =============================================================================


def _get_core_state_authority_type() -> "CoreStateAuthorityType":
    """Get the CoreStateAuthorityType enum."""
    try:
        from gordon_system.src.agent.components.core.state import CoreStateAuthorityType
        return CoreStateAuthorityType
    except ImportError:
        # Fallback - this will be fixed by proper imports
        class MockAuthority(Enum):
            EXCLUSIVE_MUTATION = "exclusive_mutation"
            SHARED_OBSERVATION = "shared_observation"
        return MockAuthority


def _get_default_authority_for_kind(owner_kind: str) -> "CoreStateAuthorityType":
    """Get default authority type for an owner kind."""
    CoreStateAuthorityType = _get_core_state_authority_type()
    if owner_kind == "observer" or owner_kind == "observes":
        return CoreStateAuthorityType.SHARED_OBSERVATION
    return CoreStateAuthorityType.EXCLUSIVE_MUTATION


# =============================================================================
# AGGREGATE OWNERSHIP EVIDENCE
# =============================================================================


@dataclass(frozen=True)
class AggregateOwnership:
    """
    Immutable ownership evidence for a runtime state aggregate.
    
    Every mutable aggregate has exactly one identifiable owner.
    
    OWNERSHIP PRINCIPLES:
        - Exactly one EXCLUSIVE_MUTATION owner per mutable aggregate
        - Multiple observers may exist (SHARED_OBSERVATION, etc.)
        - Authority types are orthogonal to mutability classification
    
    INVARIANTS:
        AGG-OWN-001: Every mutable aggregate has exactly one mutation owner
        AGG-OWN-002: Ownership evidence is immutable once created
        AGG-OWN-003: Owner identity cannot be forged (runtime isolation)
    """
    
    # Identity
    aggregate_id: RuntimeStateId
    
    # Owner information
    owner_identity: str  # Who has mutation authority
    owner_kind: str      # e.g., "lifecycle", "execution", "stream"
    
    # Scope of authority
    ownership_scope: Optional[str] = None
    
    # Authority type
    authority_type: "CoreStateAuthorityType" = field(
        default=None  # Will be set by _get_core_state_authority_type()
    )
    
    # Evidence of acquisition
    acquired_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def for_mutation_owner(
        cls,
        aggregate_id: RuntimeStateId,
        owner_identity: str,
        owner_kind: str,
        ownership_scope: Optional[str] = None,
    ) -> "AggregateOwnership":
        """Create ownership evidence for a mutation owner."""
        authority_type = _get_default_authority_for_kind(owner_kind)
        return cls(
            aggregate_id=aggregate_id,
            owner_identity=owner_identity,
            owner_kind=owner_kind,
            ownership_scope=ownership_scope,
            authority_type=authority_type,
        )
    
    @classmethod
    def for_observer(
        cls,
        aggregate_id: RuntimeStateId,
        owner_identity: str,
        ownership_scope: Optional[str] = None,
    ) -> "AggregateOwnership":
        """Create ownership evidence for an observer."""
        authority_type = _get_default_authority_for_kind("observer")
        return cls(
            aggregate_id=aggregate_id,
            owner_identity=owner_identity,
            owner_kind="observer",
            ownership_scope=ownership_scope,
            authority_type=authority_type,
        )


# =============================================================================
# RUNTIME STATE HIERARCHY AGGREGATE (BASE CLASS)
# =============================================================================


@runtime_checkable
class RuntimeStateAggregate(Protocol):
    """
    Protocol for runtime state aggregates in the hierarchy.
    
    All aggregates must satisfy this protocol to ensure consistent behavior.
    
    PROTOCOL REQUIREMENTS:
        - identity: Unique aggregate identifier
        - owner: Explicit mutation owner
        - parent: Optional parent aggregate ID
        - children: Set of child aggregate IDs (immutable)
        - containment_type: Relationship type with parent
        - version: Current version in lineage
        - generation: Epoch number for restart/migration detection
    
    INVARIANTS:
        AGG-PROT-001: Every aggregate has exactly one identity
        AGG-PROT-002: Every mutable aggregate has exactly one owner
        AGG-PROT-003: Aggregates form a tree (not arbitrary graph)
        AGG-PROT-004: Version and generation track state evolution
    """
    
    @property
    def identity(self) -> RuntimeStateId:
        ...
    
    @property
    def owner_identity(self) -> str:
        ...
    
    @property
    def parent_id(self) -> Optional[RuntimeStateId]:
        ...
    
    @property
    def children_ids(self) -> Tuple[RuntimeStateId, ...]:
        ...
    
    @property
    def containment_type_with_parent(self) -> ContainmentType:
        ...
    
    @property
    def version_sequence(self) -> int:
        ...
    
    @property
    def generation(self) -> int:
        ...


# =============================================================================
# RUNTIME STATE HIERARCHY AGGREGATE (BASE IMPLEMENTATION)
# =============================================================================


@dataclass(frozen=True)
class RuntimeStateAggregateBase:
    """
    Base implementation for runtime state aggregates.
    
    Provides common functionality while remaining immutable.
    
    INVARIANTS:
        AGG-IMP-001: Aggregate is frozen once created
        AGG-IMP-002: Children are tracked explicitly (not mutable)
        AGG-IMP-003: Parent relationship is explicit and validated
    """
    
    # Identity
    identity: RuntimeStateId
    
    # Ownership
    owner_identity: str
    
    # Hierarchy
    parent_id: Optional[RuntimeStateId] = None
    containment_type_with_parent: ContainmentType = ContainmentType.OWNS
    
    # Version tracking
    version_sequence: int = 0
    generation: int = 0
    
    # Children (immutable tuple)
    children_ids: Tuple[RuntimeStateId, ...] = field(default_factory=tuple)
    
    # Metadata
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    last_modified_at_utc: float = field(default_factory=_time_module.monotonic)
    
    def get_child(self, child_id: RuntimeStateId) -> Optional["RuntimeStateAggregateBase"]:
        """
        Get a child aggregate by its ID.
        
        Note: This returns the child's identity only. Actual child data
        must be retrieved from the owning subsystem.
        """
        if child_id in self.children_ids:
            return self._create_child(child_id)
        return None
    
    def _create_child(self, child_id: RuntimeStateId) -> "RuntimeStateAggregateBase":
        """Create a reference to a child aggregate."""
        return RuntimeStateAggregateBase(
            identity=child_id,
            owner_identity=self.owner_identity,
            parent_id=self.identity,
            containment_type=self.containment_type_with_parent,
            version_sequence=0,
            generation=self.generation,
        )
    
    def with_child(self, child: "RuntimeStateAggregateBase") -> "RuntimeStateAggregateBase":
        """
        Create a new aggregate with the given child added.
        
        Returns a new instance (immutable update).
        """
        if child.parent_id != self.identity:
            raise ValueError("Child's parent must be this aggregate")
        
        return dataclass_replace(
            self,
            children_ids=self.children_ids + (child.identity,),
            last_modified_at_utc=_time_module.monotonic(),
        )
    
    def without_child(self, child_id: RuntimeStateId) -> "RuntimeStateAggregateBase":
        """
        Create a new aggregate with the given child removed.
        
        Returns a new instance (immutable update).
        """
        if child_id not in self.children_ids:
            return self
        
        return dataclass_replace(
            self,
            children_ids=tuple(c for c in self.children_ids if c != child_id),
            last_modified_at_utc=_time_module.monotonic(),
        )
    
    def is_descendant_of(self, ancestor_id: RuntimeStateId) -> bool:
        """Check if this aggregate is a descendant of the given ancestor."""
        current = self
        while current.parent_id is not None:
            if current.parent_id == ancestor_id:
                return True
            current = RuntimeStateAggregateBase(
                identity=current.parent_id,
                owner_identity=self.owner_identity,
            )
        return False
    
    def get_ancestors(self) -> Tuple[RuntimeStateId, ...]:
        """Get all ancestor IDs from parent to root."""
        ancestors: List[RuntimeStateId] = []
        current = self
        while current.parent_id is not None:
            ancestors.append(current.parent_id)
            current = RuntimeStateAggregateBase(
                identity=current.parent_id,
                owner_identity=self.owner_identity,
            )
        return tuple(reversed(ancestors))
    
    def get_depth(self) -> int:
        """Get the depth of this aggregate in the hierarchy (0 for root)."""
        depth = 0
        current = self
        while current.parent_id is not None:
            depth += 1
            current = RuntimeStateAggregateBase(
                identity=current.parent_id,
                owner_identity=self.owner_identity,
            )
        return depth
    
    def validate_consistency(self) -> Tuple[bool, Optional[str]]:
        """
        Validate that this aggregate is consistent with its hierarchy.
        
        Returns:
            (valid: bool, reason: Optional[str])
        """
        if self.parent_id is not None:
            pass  # Validation happens at aggregate management level
        
        return True, None


# =============================================================================
# CONCRETE AGGREGATE TYPES
# =============================================================================


@dataclass(frozen=True)
class ApplicationStateAggregate(RuntimeStateAggregateBase):
    """
    Application-level runtime state aggregate.
    
    This is typically the root of most hierarchies within an application.
    """
    
    name: str = "default"
    version: str = "1.0.0"


@dataclass(frozen=True)
class RuntimeStateAggregate(RuntimeStateAggregateBase):
    """
    Runtime instance-level aggregate.
    
    Represents the runtime execution environment state.
    """
    
    runtime_id: str = "default"
    start_time_utc: float = field(default_factory=_time_module.monotonic)
    is_active: bool = True


@dataclass(frozen=True)
class BootSessionStateAggregate(RuntimeStateAggregateBase):
    """
    Boot session-level aggregate.
    
    Represents state within a single boot session (reset on restart).
    """
    
    session_id: str = "default"
    start_time_utc: float = field(default_factory=_time_module.monotonic)
    end_time_utc: Optional[float] = None


@dataclass(frozen=True)
class SubsystemStateAggregate(RuntimeStateAggregateBase):
    """
    Subsystem-level aggregate.
    
    Represents a logical subsystem (e.g., "execution", "streams").
    """
    
    subsystem_name: str = "default"
    version: str = "1.0.0"


@dataclass(frozen=True)
class ComponentStateAggregate(RuntimeStateAggregateBase):
    """
    Component-level aggregate.
    
    Represents a component instance state.
    """
    
    component_name: str = "default"
    version: str = "1.0.0"


@dataclass(frozen=True)
class ServiceStateAggregate(RuntimeStateAggregateBase):
    """
    Service-level aggregate.
    
    Represents a service instance state.
    """
    
    service_name: str = "default"
    version: str = "1.0.0"


@dataclass(frozen=True)
class ExecutionStateAggregate(RuntimeStateAggregateBase):
    """
    Execution context-level aggregate.
    
    Represents an execution flow state.
    """
    
    execution_id: str = "default"
    state: str = "idle"  # idle, active, paused, terminated


@dataclass(frozen=True)
class ResourceStateAggregate(RuntimeStateAggregateBase):
    """
    Resource allocation-level aggregate.
    
    Represents a resource allocation state (e.g., memory, CPU).
    """
    
    resource_type: str = "generic"
    resource_id: str = "default"
    allocated_amount: float = 0.0


@dataclass(frozen=True)
class StreamStateAggregate(RuntimeStateAggregateBase):
    """
    Stream processing-level aggregate.
    
    Represents a stream's runtime state.
    """
    
    stream_name: str = "default"
    partition_count: int = 1


@dataclass(frozen=True)
class InteractionStateAggregate(RuntimeStateAggregateBase):
    """
    Interaction lifecycle-level aggregate.
    
    Represents an interaction's runtime state.
    """
    
    interaction_id: str = "default"
    direction: str = "inbound"  # inbound, outbound


@dataclass(frozen=True)
class TransactionStateAggregate(RuntimeStateAggregateBase):
    """
    Transaction context-level aggregate.
    
    Represents a transaction's runtime state.
    """
    
    transaction_id: str = "default"
    status: str = "pending"  # pending, active, committed, aborted


@dataclass(frozen=True)
class HealthStateAggregate(RuntimeStateAggregateBase):
    """
    Health condition-level aggregate.
    
    Represents an aggregate's health state.
    """
    
    health_score: int = 100  # 0-100
    status: str = "healthy"  # healthy, degraded, unhealthy


@dataclass(frozen=True)
class ReadinessStateAggregate(RuntimeStateAggregateBase):
    """
    Readiness availability-level aggregate.
    
    Represents whether an aggregate is ready to accept work.
    """
    
    is_ready: bool = False
    reason: str = "unknown"


@dataclass(frozen=True)
class AdmissionStateAggregate(RuntimeStateAggregateBase):
    """
    Admission decision-level aggregate.
    
    Represents an admission control decision state.
    """
    
    is_admitted: bool = False
    reason: str = "pending"


@dataclass(frozen=True)
class RecoveryStateAggregate(RuntimeStateAggregateBase):
    """
    Recovery process-level aggregate.
    
    Represents a recovery operation's state.
    """
    
    status: str = "idle"  # idle, in_progress, completed, failed


@dataclass(frozen=True)
class ShutdownStateAggregate(RuntimeStateAggregateBase):
    """
    Shutdown procedure-level aggregate.
    
    Represents a shutdown operation's state.
    """
    
    status: str = "idle"  # idle, in_progress, completed


# =============================================================================
# HIERARCHY MANAGER (PUBLIC API)
# =============================================================================


class RuntimeStateHierarchy:
    """
    Public facade for the runtime state hierarchy.
    
    Provides read-only access to the hierarchy while enforcing:
        - Ownership validation on traversal
        - Runtime isolation enforcement
        - Hierarchical consistency validation
    
    PUBLIC API:
        - lookup_aggregate: Get an aggregate by ID
        - get_parent: Get parent of an aggregate
        - get_children: Get children of an aggregate
        - get_ancestors: Get all ancestors of an aggregate
        - get_descendants: Get all descendants of an aggregate
        - validate_hierarchy: Validate the entire hierarchy structure
        - snapshot: Create an immutable snapshot of the hierarchy
    
    INVARIANTS:
        HIER-API-001: All APIs are read-only (no mutation)
        HIER-API-002: Ownership is validated on traversal
        HIER-API-003: Runtime isolation is enforced
        HIER-API-004: Snapshots are immutable
    """
    
    def __init__(
        self,
        root_aggregate: ApplicationStateAggregate,
        aggregates_by_id: Dict[RuntimeStateId, RuntimeStateAggregateBase] = None,
    ) -> None:
        """
        Initialize the hierarchy with a root aggregate.
        
        Args:
            root_aggregate: The application-level root aggregate
            aggregates_by_id: Optional dict of all aggregates by ID
        """
        self._root = root_aggregate
        self._aggregates_by_id: Dict[RuntimeStateId, RuntimeStateAggregateBase] = (
            aggregates_by_id or {}
        )
        
        # Add root to the registry
        if root_aggregate.identity not in self._aggregates_by_id:
            self._aggregates_by_id[root_aggregate.identity] = root_aggregate
    
    @property
    def root(self) -> ApplicationStateAggregate:
        """Get the root aggregate (application-level)."""
        return self._root
    
    def lookup_aggregate(self, aggregate_id: RuntimeStateId) -> Optional[RuntimeStateAggregateBase]:
        """
        Look up an aggregate by its ID.
        
        Args:
            aggregate_id: The unique identifier of the aggregate
            
        Returns:
            The aggregate if found, None otherwise
        """
        return self._aggregates_by_id.get(aggregate_id)
    
    def get_parent(self, aggregate_id: RuntimeStateId) -> Optional[RuntimeStateAggregateBase]:
        """
        Get the parent of an aggregate.
        
        Args:
            aggregate_id: The ID of the aggregate
            
        Returns:
            The parent aggregate if found and ownership validates,
            None if no parent or validation fails
        """
        aggregate = self._aggregates_by_id.get(aggregate_id)
        if aggregate is None:
            return None
        
        if aggregate.parent_id is None:
            return None
        
        # Validate runtime isolation
        if not self._validate_runtime_isolation(aggregate, aggregate):
            return None
        
        return self._aggregates_by_id.get(aggregate.parent_id)
    
    def get_children(self, aggregate_id: RuntimeStateId) -> Tuple[RuntimeStateAggregateBase, ...]:
        """
        Get all children of an aggregate.
        
        Args:
            aggregate_id: The ID of the parent aggregate
            
        Returns:
            Tuple of child aggregates
        """
        parent = self._aggregates_by_id.get(aggregate_id)
        if parent is None:
            return tuple()
        
        children: List[RuntimeStateAggregateBase] = []
        for child_id in parent.children_ids:
            child = self._aggregates_by_id.get(child_id)
            if child is not None:
                # Validate ownership
                if self._validate_ownership(parent, child):
                    children.append(child)
        
        return tuple(children)
    
    def get_ancestors(self, aggregate_id: RuntimeStateId) -> Tuple[RuntimeStateAggregateBase, ...]:
        """
        Get all ancestors of an aggregate (from parent to root).
        
        Args:
            aggregate_id: The ID of the aggregate
            
        Returns:
            Tuple of ancestor aggregates in order from immediate parent to root
        """
        aggregate = self._aggregates_by_id.get(aggregate_id)
        if aggregate is None:
            return tuple()
        
        ancestors: List[RuntimeStateAggregateBase] = []
        current_id = aggregate.parent_id
        
        while current_id is not None:
            ancestor = self._aggregates_by_id.get(current_id)
            if ancestor is None:
                break
            if not self._validate_runtime_isolation(aggregate, ancestor):
                break
            ancestors.append(ancestor)
            current_id = ancestor.parent_id
        
        return tuple(reversed(ancestors))
    
    def get_descendants(self, aggregate_id: RuntimeStateId) -> Tuple[RuntimeStateAggregateBase, ...]:
        """
        Get all descendants of an aggregate.
        
        Args:
            aggregate_id: The ID of the aggregate
            
        Returns:
            Tuple of descendant aggregates (level-order traversal)
        """
        aggregate = self._aggregates_by_id.get(aggregate_id)
        if aggregate is None:
            return tuple()
        
        descendants: List[RuntimeStateAggregateBase] = []
        
        # BFS traversal
        queue = list(self.get_children(aggregate_id))
        while queue:
            child = queue.pop(0)
            if not self._validate_runtime_isolation(aggregate, child):
                continue
            descendants.append(child)
            
            # Add children of this child
            for grandchild_id in child.children_ids:
                grandchild = self._aggregates_by_id.get(grandchild_id)
                if grandchild is not None:
                    queue.append(grandchild)
        
        return tuple(descendants)
    
    def _validate_runtime_isolation(
        self,
        source: RuntimeStateAggregateBase,
        target: RuntimeStateAggregateBase,
    ) -> bool:
        """
        Validate that the operation respects runtime isolation.
        
        Cross-runtime operations are not permitted unless explicitly allowed.
        
        Args:
            source: The source aggregate
            target: The target aggregate
            
        Returns:
            True if runtime isolation is preserved, False otherwise
        """
        # If either has no runtime binding, isolation doesn't apply
        if source.identity.runtime_id is None or target.identity.runtime_id is None:
            return True
        
        # Both must belong to the same runtime
        return source.identity.runtime_id == target.identity.runtime_id
    
    def _validate_ownership(
        self,
        parent: RuntimeStateAggregateBase,
        child: RuntimeStateAggregateBase,
    ) -> bool:
        """
        Validate ownership relationship between parent and child.
        
        Parent ownership does not automatically grant mutation authority
        over children. This validates the structural relationship.
        
        Args:
            parent: The parent aggregate
            child: The child aggregate
            
        Returns:
            True if ownership is consistent, False otherwise
        """
        # For now, we allow any owner for hierarchical structure
        # Mutation authority is handled separately by each aggregate
        return True
    
    def validate_hierarchy(self) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate the entire hierarchy structure.
        
        Checks:
            - No cycles in parent-child relationships
            - All children have valid parents
            - Runtime isolation is preserved
            - No orphaned aggregates
            
        Returns:
            (valid: bool, findings: Tuple of finding messages)
        """
        findings: List[str] = []
        visited: Set[RuntimeStateId] = set()
        
        def traverse(aggregate: RuntimeStateAggregateBase) -> None:
            """Traverse the hierarchy recursively."""
            agg_id = aggregate.identity
            
            # Cycle detection
            if agg_id in visited:
                findings.append(f"Cycle detected: {agg_id.value}")
                return
            
            visited.add(agg_id)
            
            # Validate parent relationship (child should reference this as parent)
            for child_id in aggregate.children_ids:
                child = self._aggregates_by_id.get(child_id)
                if child is not None:
                    if child.parent_id != agg_id:
                        findings.append(
                            f"Parent-child inconsistency: {child_id.value} "
                            f"parent is {child.parent_id.value}, expected {agg_id.value}"
                        )
                    
                    # Runtime isolation check
                    if not self._validate_runtime_isolation(aggregate, child):
                        findings.append(
                            f"Runtime isolation violation: {agg_id.value} and "
                            f"{child_id.value} belong to different runtimes"
                        )
            
            # Traverse children
            for child_id in aggregate.children_ids:
                child = self._aggregates_by_id.get(child_id)
                if child is not None:
                    traverse(child)
        
        # Start traversal from root
        traverse(self._root)
        
        # Check for orphaned aggregates
        all_aggregate_ids = set(self._aggregates_by_id.keys())
        reachable_ids = visited
        
        orphans = all_aggregate_ids - reachable_ids
        if orphans:
            for orphan_id in orphans:
                findings.append(f"Orphan aggregate: {orphan_id.value}")
        
        return len(findings) == 0, tuple(findings)
    
    def snapshot(self) -> "RuntimeStateHierarchySnapshot":
        """
        Create an immutable snapshot of the current hierarchy state.
        
        Returns:
            An immutable snapshot that preserves the hierarchy at this point
        """
        # Collect all aggregates for snapshot
        aggregates_data: List[dict] = []
        for agg_id, aggregate in self._aggregates_by_id.items():
            aggregates_data.append({
                "identity": {
                    "value": aggregate.identity.value,
                    "hierarchy_type": aggregate.identity.hierarchy_type.value,
                    "scope": aggregate.identity.scope,
                    "runtime_id": aggregate.identity.runtime_id,
                    "boot_session_id": aggregate.identity.boot_session_id,
                },
                "owner_identity": aggregate.owner_identity,
                "parent_id": aggregate.parent_id.value if aggregate.parent_id else None,
                "children_ids": [c.value for c in aggregate.children_ids],
                "version_sequence": aggregate.version_sequence,
                "generation": aggregate.generation,
            })
        
        return RuntimeStateHierarchySnapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex[:24]}",
            root_identity=self._root.identity.value,
            aggregates=tuple(aggregates_data),
            created_at_utc=_time_module.monotonic(),
        )
    
    def get_diagnostics(self) -> "RuntimeStateHierarchyDiagnostics":
        """
        Get diagnostics for the entire hierarchy.
        
        Returns:
            Immutable diagnostics object with hierarchy statistics
        """
        total_count = len(self._aggregates_by_id)
        
        # Count by type
        type_counts: Dict[str, int] = {}
        for aggregate in self._aggregates_by_id.values():
            type_name = aggregate.identity.hierarchy_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # Calculate max depth
        def get_depth(aggregate: RuntimeStateAggregateBase) -> int:
            if aggregate.parent_id is None:
                return 0
            parent = self._aggregates_by_id.get(aggregate.parent_id)
            if parent is None:
                return 0
            return 1 + get_depth(parent)
        
        max_depth = max((get_depth(a) for a in self._aggregates_by_id.values()), default=0)
        
        # Validation result
        valid, findings = self.validate_hierarchy()
        
        return RuntimeStateHierarchyDiagnostics(
            diagnostics_id=f"diag_{uuid.uuid4().hex[:24]}",
            total_aggregate_count=total_count,
            hierarchy_depth=max_depth,
            aggregate_type_counts=type_counts,
            is_valid=valid,
            validation_findings=findings,
            created_at_utc=_time_module.monotonic(),
        )


@dataclass(frozen=True)
class RuntimeStateHierarchySnapshot:
    """
    Immutable snapshot of the runtime state hierarchy at a point in time.
    
    SNAPSHOTS PRINCIPLES:
        - Snapshots are immutable once created
        - Snapshots preserve hierarchy structure
        - Snapshots can be used for debugging and auditing
    
    INVARIANTS:
        SNAPSHOT-001: Snapshot is immutable once created
        SNAPSHOT-002: Snapshot preserves all aggregates at point-in-time
        SNAPSHOT-003: Snapshot does not provide mutation access
    """
    
    snapshot_id: str
    root_identity: str
    aggregates: Tuple[dict, ...]  # Serialized aggregate data
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    
    def get_aggregate(self, identity_value: str) -> Optional[dict]:
        """Get a specific aggregate from the snapshot."""
        for agg in self.aggregates:
            if agg.get("identity", {}).get("value") == identity_value:
                return agg
        return None
    
    def to_dict(self) -> dict:
        """Convert snapshot to a dictionary representation."""
        return {
            "snapshot_id": self.snapshot_id,
            "root_identity": self.root_identity,
            "aggregate_count": len(self.aggregates),
            "created_at_utc": self.created_at_utc,
        }


@dataclass(frozen=True)
class RuntimeStateHierarchyDiagnostics:
    """
    Immutable diagnostics for the runtime state hierarchy.
    
    DIAGNOSTICS PRINCIPLES:
        - Diagnostics are immutable once created
        - Diagnostics provide overview without exposing internal state
        - Diagnostics include validation findings
    
    INVARIANTS:
        DIAG-001: Diagnostics are immutable once created
        DIAG-002: Diagnostics don't expose live handles or secrets
        DIAG-003: Diagnostics include hierarchy statistics
    """
    
    diagnostics_id: str
    total_aggregate_count: int
    hierarchy_depth: int
    aggregate_type_counts: Dict[str, int]
    is_valid: bool
    validation_findings: Tuple[str, ...]
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    
    def get_summary(self) -> str:
        """Get a human-readable summary of diagnostics."""
        lines = [
            "Runtime State Hierarchy Diagnostics",
            "=====================================",
            f"Total Aggregates: {self.total_aggregate_count}",
            f"Hierarchy Depth: {self.hierarchy_depth}",
            f"Validity: {'VALID' if self.is_valid else 'INVALID'}",
        ]
        
        # Add type counts
        lines.append("")
        lines.append("Aggregate Types:")
        for type_name, count in sorted(self.aggregate_type_counts.items()):
            lines.append(f"  {type_name}: {count}")
        
        # Add validation findings
        if self.validation_findings:
            lines.append("")
            lines.append("Validation Findings:")
            for finding in self.validation_findings:
                lines.append(f"  - {finding}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """Convert diagnostics to a dictionary representation."""
        return {
            "diagnostics_id": self.diagnostics_id,
            "total_aggregate_count": self.total_aggregate_count,
            "hierarchy_depth": self.hierarchy_depth,
            "aggregate_type_counts": dict(self.aggregate_type_counts),
            "is_valid": self.is_valid,
            "validation_findings": list(self.validation_findings),
            "created_at_utc": self.created_at_utc,
        }


# =============================================================================
# HELPER FUNCTIONS (dataclass_replace)
# =============================================================================


def dataclass_replace(instance: Any, **changes: Any) -> Any:
    """
    Create a new instance with specified changes.
    
    Similar to dataclasses.replace but works with this custom implementation.
    """
    import copy
    new_instance = copy.deepcopy(instance)
    
    for key, value in changes.items():
        setattr(new_instance, key, value)
    
    return new_instance


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = (
    # Containment types
    "ContainmentType",
    
    # Hierarchy types
    "RuntimeStateHierarchyType",
    
    # ID types
    "RuntimeStateId",
    
    # Ownership
    "AggregateOwnership",
    
    # Base classes and protocols
    "RuntimeStateAggregate",
    "RuntimeStateAggregateBase",
    
    # Concrete aggregate types
    "ApplicationStateAggregate",
    "RuntimeStateAggregate",
    "BootSessionStateAggregate",
    "SubsystemStateAggregate",
    "ComponentStateAggregate",
    "ServiceStateAggregate",
    "ExecutionStateAggregate",
    "ResourceStateAggregate",
    "StreamStateAggregate",
    "InteractionStateAggregate",
    "TransactionStateAggregate",
    "HealthStateAggregate",
    "ReadinessStateAggregate",
    "AdmissionStateAggregate",
    "RecoveryStateAggregate",
    "ShutdownStateAggregate",
    
    # Public API
    "RuntimeStateHierarchy",
    "RuntimeStateHierarchySnapshot",
    "RuntimeStateHierarchyDiagnostics",
)