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
from typing import (
    TypeVar,
    Generic,
    Optional,
    Any,
    Dict,
    List,
    Set,
    Callable,
    Tuple,
)
from enum import Enum, auto
import uuid
import time
import threading

# Import activation types from the same module (they will be defined later but we need them now for type hints)
# We'll use string annotations to avoid forward-reference issues

# Import GordonRuntimeError for exceptions
try:
    from ..exceptions import RuntimeError as GordonRuntimeError
except ImportError:
    # Fallback: define our own if not available
    class GordonRuntimeError(RuntimeError):
        """Gordon runtime error base class."""
        pass


# =============================================================================
# RUNTIME STATE ENUM (must be defined before other types that reference it)
# =============================================================================


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
    
    # Pre-activation states (for activation lifecycle)
    ASSEMBLED = "assembled"  # Fully assembled but inactive
    
    # Activation states (runtime-level view)
    ACTIVATING = "activating"  # Currently activating infrastructure
    ACTIVE = "active"          # Infrastructure started, ready for evaluation


# =============================================================================
# STATE GUARD SYSTEM
# =============================================================================


class GuardResult(Enum):
    """Result of guard evaluation."""
    PASSED = "passed"
    FAILED = "failed"


@dataclass(frozen=True)
class GuardEvaluation:
    """Result of evaluating a single guard."""
    guard_name: str
    result: GuardResult
    reason: Optional[str] = None


class StateGuard:
    """
    Protocol for state transition guards.
    
    Guards are evaluated BEFORE a state transition is committed.
    They can block transitions based on external conditions like:
        - Readiness of subsystems
        - Admission availability  
        - Resource availability
    """
    
    @property
    def name(self) -> str:
        """Unique identifier for this guard."""
        raise NotImplementedError
    
    def evaluate(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> GuardEvaluation:
        """
        Evaluate if the transition should be allowed.
        
        Args:
            from_state: Source state
            to_state: Target state
            
        Returns:
            GuardEvaluation with result and optional reason
        """
        raise NotImplementedError
    
    def requires_guard(self, from_state: RuntimeState, to_state: RuntimeState) -> bool:
        """Check if this guard is relevant for the given transition."""
        return True


class ResourceGuard(StateGuard):
    """Guard that checks if sufficient resources are available."""
    
    def __init__(self, resources_available_fn: Optional[Callable[[], bool]] = None):
        self._resources_available = resources_available_fn or (lambda: True)
    
    @property
    def name(self) -> str:
        return "resource_guard"
    
    def evaluate(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> GuardEvaluation:
        if not self._resources_available():
            return GuardEvaluation(
                guard_name=self.name,
                result=GuardResult.FAILED,
                reason="Resources not available for transition"
            )
        return GuardEvaluation(
            guard_name=self.name,
            result=GuardResult.PASSED
        )
    
    def requires_guard(self, from_state: RuntimeState, to_state: RuntimeState) -> bool:
        # Check resources when transitioning to operational states
        return to_state in (
            RuntimeState.RUNNING,
            RuntimeState.STARTING,
        )


class ReadinessGuard(StateGuard):
    """Guard that checks if subsystem is ready for the target state."""
    
    def __init__(self, readiness_ready_fn: Callable[[], bool]):
        self._readiness_ready = readiness_ready_fn
    
    @property
    def name(self) -> str:
        return "readiness_guard"
    
    def evaluate(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> GuardEvaluation:
        if not self._readiness_ready():
            return GuardEvaluation(
                guard_name=self.name,
                result=GuardResult.FAILED,
                reason="Readiness check failed"
            )
        return GuardEvaluation(
            guard_name=self.name,
            result=GuardResult.PASSED
        )
    
    def requires_guard(self, from_state: RuntimeState, to_state: RuntimeState) -> bool:
        return to_state in (RuntimeState.STARTING, RuntimeState.RUNNING)


class GuardManager:
    """Manages multiple state guards."""
    
    def __init__(self):
        self._guards: List[StateGuard] = []
        self._lock = threading.RLock()
    
    def register_guard(self, guard: StateGuard) -> None:
        """Register a guard to be evaluated during transitions."""
        with self._lock:
            if not any(g.name == guard.name for g in self._guards):
                self._guards.append(guard)
    
    def unregister_guard(self, name: str) -> bool:
        """Unregister a guard by name."""
        with self._lock:
            for i, g in enumerate(self._guards):
                if g.name == name:
                    del self._guards[i]
                    return True
            return False
    
    def evaluate_guards(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> List[GuardEvaluation]:
        """
        Evaluate all relevant guards for a transition.
        
        Args:
            from_state: Source state
            to_state: Target state
            
        Returns:
            List of guard evaluations (only guards that require evaluation are included)
        """
        with self._lock:
            results: List[GuardEvaluation] = []
            
            for guard in self._guards:
                if guard.requires_guard(from_state, to_state):
                    result = guard.evaluate(from_state, to_state)
                    results.append(result)
            
            return results
    
    def are_guards_satisfied(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> bool:
        """Check if all relevant guards pass for a transition."""
        evaluations = self.evaluate_guards(from_state, to_state)
        return all(e.result == GuardResult.PASSED for e in evaluations)


# Re-export core types for convenience (EntityId is imported, not redefined)
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
    
    Guard Integration:
        The store includes a guard_manager property that can be used to register
        guards which are evaluated BEFORE transitions are applied. Guards can
        block transitions based on external conditions (readiness, admission,
        resources).
    """
    
    def __init__(self, initial_state: RuntimeState = RuntimeState.INITIAL) -> None:
        self._state = RuntimeStateSnapshot(
            state=initial_state,
            registry_revision=0,
            timestamp=time.monotonic(),
            runtime_id=str(uuid.uuid4())
        )
        self._version = 0
        # Initialize guard manager lazily to avoid circular import issues
        self._guard_manager: Optional[GuardManager] = None
    
    @property
    def state(self) -> RuntimeStateSnapshot:
        """Get current state snapshot (immutable view)."""
        return self._state
    
    @property
    def version(self) -> int:
        """Get current state version."""
        return self._version
    
    @property
    def guard_manager(self) -> GuardManager:
        """Get the guard manager for this store."""
        if self._guard_manager is None:
            self._guard_manager = GuardManager()
        return self._guard_manager
    
    def transition(
        self,
        transition: RuntimeStateTransition,
        expected_version: Optional[int] = None
    ) -> bool:
        """
        Apply a state transition.
        
        Guards (if registered) are evaluated BEFORE the transition is applied.
        If any guard returns FAILED, the transition is blocked.
        
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
        
        # Evaluate guards (if any registered)
        if self._guard_manager is not None:
            if not self._guard_manager.are_guards_satisfied(
                transition.from_state, transition.to_state
            ):
                return False  # Guard blocked the transition
        
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
    
    def create_transition(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
        reason: Optional[str] = None,
        timestamp: Optional[float] = None
    ) -> RuntimeStateTransition:
        """
        Create a new state transition object.
        
        This is a convenience method for creating transitions without having
        to manually construct the full RuntimeStateTransition object.
        
        Args:
            from_state: Source state
            to_state: Target state
            reason: Optional description of why the transition occurs
            timestamp: Optional timestamp (uses current time if not provided)
            
        Returns:
            A new RuntimeStateTransition ready for application
        """
        return RuntimeStateTransition(
            from_state=from_state,
            to_state=to_state,
            timestamp=time.monotonic() if timestamp is None else timestamp,
            registry_revision=self._version + 1,
            runtime_id=self.state.runtime_id,
            reason=reason
        )


# =============================================================================
# RUNTIME STATE TRUTH (CANONICAL OBSERVATION AGGREGATOR)
# =============================================================================


class RuntimeStateTruth:
    """
    Canonical aggregation of runtime state observations.
    
    This is NOT the source of truth for runtime state. Instead, it:
        - Aggregates observations from various sources
        - Provides a unified view of runtime health and status
        - Tracks versioned snapshots of aggregated state
    
    Invariants:
        1. RuntimeStateStore owns the true runtime state
        2. RuntimeTruth aggregates observations only
        3. Truth is immutable per version (new versions create new state)
        4. No direct mutation capability from outside observers
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._lock = threading.RLock()
        
        # Version tracking
        self._version = 0
        
        # Observation data (aggregated, not authoritative)
        self._observed_state: Optional[RuntimeState] = None
        self._health_status: Dict[str, str] = {}
        self._integrity_status: Dict[str, str] = {}
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this truth serves."""
        return self._runtime_id
    
    @property
    def version(self) -> int:
        """Get current truth version."""
        with self._lock:
            return self._version
    
    def update_from_state_store(self, store: RuntimeStateStore) -> None:
        """
        Update observed state from a runtime state store.
        
        This allows the truth aggregator to track what the authoritative
        state store reports without becoming the source of truth.
        """
        with self._lock:
            snapshot = store.get_snapshot()
            
            # Record as observation
            self._observed_state = snapshot.state
            self._version += 1
    
    def update_health(
        self, entity_id: str, status: str
    ) -> None:
        """Update health observation for an entity."""
        with self._lock:
            self._health_status[entity_id] = status
            self._version += 1
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get aggregated health status summary."""
        with self._lock:
            return {
                "overall": self._compute_overall_health(),
                "details": dict(self._health_status),
            }
    
    def _compute_overall_health(self) -> str:
        """Compute overall health from all observations."""
        if not self._health_status:
            return "unknown"
        
        statuses = list(self._health_status.values())
        
        # Priority: failed > unhealthy > degraded > healthy
        for status in ("failed", "unhealthy", "degraded"):
            if status in statuses:
                return status
        
        return "healthy"


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

# =============================================================================
# PHASE 3.7.11-R: Runtime Truth Publication System
# =============================================================================

from .runtime_truth import (
    RuntimeTruth,
    RuntimeTruthVersion,
    RuntimeTruthSnapshot,
)

# =============================================================================
# PHASE 3.7.8-I: Runtime State Machine (NEW)
# =============================================================================

from .statemachine import (
    CanonicalRuntimeState,
    RuntimeTransitionId,
    RuntimeVersion,
    RuntimeSnapshot,
    RuntimeTransitionRequest,
    RuntimeTransitionResult,
    RuntimeTransitionFailure,
    RuntimeHistoryEntry,
    RuntimeInvariantResult,
    
    # Drift detection (Phase 3.7.8-R remediation)
    StateDriftRule,
    StateDriftFinding,
    StateDriftSnapshot,
    StateDriftDetector,
    
    TransitionValidator,
    GuardEvaluator,
    ResourcesAvailableGuard,
    ReadinessSatisfiedGuard,
    AdmissionPermittedGuard,
    SchedulerAvailableGuard,
    ExecutorAvailableGuard,
    IntegrityValidGuard,
    HealthAcceptableGuard,
    ShutdownAbsentGuard,
    RuntimeStateMachine,
    StateMachineConfig,
    StateMachineEventPublisher,
    InvariantValidator,
)

# =============================================================================
# LIFECYCLE STATE MACHINE TYPES (for activation coordination)
# =============================================================================

# Note: EntityId is imported from ..types above

class ActivationState(Enum):
    """Runtime activation lifecycle states."""
    
    # Pre-activation states
    CONSTRUCTED = "constructed"
    ASSEMBLED = "assembled"  # Fully assembled but inactive
    
    # Activation states
    ACTIVATING = "activating"  # Currently activating
    ACTIVE = "active"          # Infrastructure started, ready for evaluation
    
    # Post-activation states
    QUIESCING = "quiescing"
    STOPPING = "stopping"
    STOPPED = "stopped"
    
    # Error states
    FAILED = "failed"
    PARTIALLY_ACTIVATED = "partially_activated"  # Partial success state


class ActivationTransactionState(Enum):
    """States of an activation transaction."""
    
    REQUESTED = "requested"
    VALIDATING = "validating"
    PLANNING = "planning"
    GRAPH_VERIFIED = "graph_verified"
    PLAN_COMMITTED = "plan_committed"
    ACTIVATING = "activating"
    VERIFYING = "verifying"
    COMMITTING = "committing"
    COMPLETED = "completed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class ActivationRequest:
    """
    Immutable request to activate a runtime.
    
    Args:
        activation_id: Unique activation transaction ID
        runtime_id: Runtime instance ID
        boot_session_id: Boot session ID (optional)
        requested_mode: Requested mode (default, recovery, test)
        expected_source_state: Expected source lifecycle state
        deadline: Absolute time deadline for activation
        cancellation_requested: Whether cancellation has been requested
    """
    
    activation_id: str
    runtime_id: str
    boot_session_id: Optional[str] = None
    requested_mode: str = "default"
    expected_source_state: ActivationState = ActivationState.ASSEMBLED
    deadline: float = field(default_factory=lambda: time.monotonic() + 30.0)
    cancellation_requested: bool = False
    
    @classmethod
    def create(cls, runtime_id: str) -> "ActivationRequest":
        """Create a new activation request with generated ID."""
        return cls(
            activation_id=str(uuid.uuid4()),
            runtime_id=runtime_id,
        )
    
    def is_expired(self) -> bool:
        """Check if request has passed its deadline."""
        return time.monotonic() > self.deadline


@dataclass(frozen=True)
class ActivationContext:
    """
    Context for a single activation attempt.
    
    This is the runtime context passed to activation components.
    """
    
    activation_id: str
    runtime_id: str
    boot_session_id: Optional[str]
    mode: str
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ActivationFailure:
    """
    Immutable failure record during activation.
    
    Preserves primary cause and collects secondary failures.
    """
    
    step_id: int
    entity_id: EntityId
    failed_transition: str
    primary_cause: Exception
    timestamp: float = field(default_factory=time.monotonic)
    secondary_failures: List[Tuple[str, Exception]] = field(default_factory=list)


@dataclass(frozen=True)
class ActivationResult:
    """
    Immutable result of an activation attempt.
    """
    
    activation_id: str
    runtime_id: str
    status: "ActivationStatus"
    source_state: ActivationState
    final_state: ActivationState
    activated_entity_ids: Tuple[EntityId, ...] = field(default_factory=tuple)
    rolled_back_entity_ids: Tuple[EntityId, ...] = field(default_factory=tuple)
    active_resource_ids: Tuple[str, ...] = field(default_factory=tuple)
    failed_entity_id: Optional[EntityId] = None
    primary_failure: Optional[ActivationFailure] = None
    rollback_failures: List[ActivationFailure] = field(default_factory=list)
    readiness_status: str = "unevaluated"
    admission_status: str = "closed"
    elapsed_time_seconds: float = 0.0
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success(self) -> bool:
        return self.status == ActivationStatus.COMPLETED
    
    @classmethod
    def success_result(
        cls,
        activation_id: str,
        runtime_id: str,
        activated_entities: List[EntityId],
        active_resources: List[str]
    ) -> "ActivationResult":
        return cls(
            activation_id=activation_id,
            runtime_id=runtime_id,
            status=ActivationStatus.COMPLETED,
            source_state=ActivationState.ASSEMBLED,
            final_state=ActivationState.ACTIVE,
            activated_entity_ids=tuple(activated_entities),
            active_resource_ids=tuple(active_resources),
            readiness_status="unevaluated",
            admission_status="closed"
        )
    
    @classmethod
    def failure_result(
        cls,
        activation_id: str,
        runtime_id: str,
        failed_entity: EntityId,
        primary_failure: ActivationFailure,
        activated_before_failure: List[EntityId],
        rolled_back_entities: List[EntityId]
    ) -> "ActivationResult":
        return cls(
            activation_id=activation_id,
            runtime_id=runtime_id,
            status=ActivationStatus.PARTIAL_FAILURE,
            source_state=ActivationState.ASSEMBLED,
            final_state=ActivationState.FAILED,
            activated_entity_ids=tuple(activated_before_failure),
            rolled_back_entity_ids=tuple(rolled_back_entities),
            failed_entity_id=failed_entity,
            primary_failure=primary_failure,
            readiness_status="unevaluated",
            admission_status="closed"
        )


class ActivationStatus(Enum):
    """Status of an activation attempt."""
    
    REQUESTED = "requested"
    VALIDATING = "validating"
    PLANNING = "planning"
    ACTIVATING = "activating"
    VERIFYING = "verifying"
    COMMITTING = "committing"
    COMPLETED = "completed"
    IDEMPOTENT_SUCCESS = "idempotent_success"
    PARTIAL_FAILURE = "partial_failure"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class ActivationConcurrencyConfig:
    """Configuration for parallel activation."""
    
    max_parallel: int = 4
    layer_timeout_multiplier: float = 1.5
    
    @classmethod
    def default(cls) -> "ActivationConcurrencyConfig":
        return cls()
    
    @classmethod
    def strict(cls) -> "ActivationConcurrencyConfig":
        return cls(max_parallel=1)


@dataclass(frozen=True)
class ActivationTimeoutConfig:
    """Configuration for timeouts during activation."""
    
    default_timeout: float = 30.0
    layer_timeout: Optional[float] = None
    component_timeout_multiplier: float = 2.0
    
    def get_component_timeout(self, base_timeout: Optional[float] = None) -> float:
        base = base_timeout or self.default_timeout
        return base * self.component_timeout_multiplier


@dataclass(frozen=True)
class ActivationConfig:
    """Immutable configuration for activation."""
    
    concurrency: ActivationConcurrencyConfig = field(default_factory=ActivationConcurrencyConfig.default)
    timeouts: ActivationTimeoutConfig = field(default_factory=ActivationTimeoutConfig)
    verify_activation: bool = True
    rollback_enabled: bool = True
    events_enabled: bool = True
    
    @classmethod
    def default(cls) -> "ActivationConfig":
        return cls()


@dataclass(frozen=True)
class RuntimeLifecycleCoordinatorSnapshot:
    """Immutable snapshot of lifecycle coordinator state."""
    
    runtime_id: str
    entity_count: int
    has_active_transaction: bool
    transaction_state: Optional[str]
    transaction_id: Optional[str]
    event_count: int
    activated_entity_ids: List[str]
    rolled_back_entity_ids: List[str]


@dataclass(frozen=True)
class ActivationTransaction:
    """
    Represents one activation attempt as a transaction-like object.
    """
    
    transaction_id: str
    runtime_id: str
    activation_request: ActivationRequest
    state: ActivationTransactionState
    
    # Tracking
    activated_entities: Set[EntityId] = field(default_factory=set)
    rolled_back_entities: Set[EntityId] = field(default_factory=set)
    active_resources: List[Tuple[str, EntityId]] = field(default_factory=list)
    
    # Failures
    primary_failure: Optional[ActivationFailure] = None
    secondary_failures: List[ActivationFailure] = field(default_factory=list)
    
    # Timing
    start_time: float = field(default_factory=time.monotonic)
    end_time: Optional[float] = None
    
    def to_snapshot(self) -> "RuntimeLifecycleCoordinatorSnapshot":
        return RuntimeLifecycleCoordinatorSnapshot(
            runtime_id=self.runtime_id,
            entity_count=0,
            has_active_transaction=True,
            transaction_state=self.state.value,
            transaction_id=self.transaction_id,
            event_count=0,
            activated_entity_ids=[str(eid) for eid in self.activated_entities],
            rolled_back_entity_ids=[str(eid) for eid in self.rolled_back_entities]
        )


# =============================================================================
# RUNTIME ACTIVATION CONTROLLER (CANONICAL AUTHORITY)
# =============================================================================


class ActivationPreconditionError(GordonRuntimeError):
    """Raised when activation preconditions are not met."""
    
    def __init__(
        self,
        message: str,
        runtime_id: Optional[str] = None,
        precondition_name: Optional[str] = None
    ) -> None:
        super().__init__(message)
        self.runtime_id = runtime_id
        self.precondition_name = precondition_name


class ActivationAuthorityError(GordonRuntimeError):
    """Raised when activation authority is violated."""
    
    def __init__(
        self,
        message: str,
        runtime_id: Optional[str] = None,
        authority_type: Optional[str] = None
    ) -> None:
        super().__init__(message)
        self.runtime_id = runtime_id
        self.authority_type = authority_type


class ActivationConcurrencyError(GordonRuntimeError):
    """Raised when concurrent activation is detected."""
    
    def __init__(
        self,
        message: str,
        runtime_id: Optional[str] = None,
        existing_transaction_id: Optional[str] = None
    ) -> None:
        super().__init__(message)
        self.runtime_id = runtime_id
        self.existing_transaction_id = existing_transaction_id


@dataclass(frozen=True)
class ActivationPreconditionResult:
    """Result of activation precondition validation."""
    
    passed: bool
    failed_preconditions: List[str] = field(default_factory=list)
    message: Optional[str] = None
    
    @classmethod
    def success(cls) -> "ActivationPreconditionResult":
        return cls(passed=True)
    
    @classmethod
    def failure(
        cls,
        preconditions: List[str],
        message: Optional[str] = None
    ) -> "ActivationPreconditionResult":
        return cls(passed=False, failed_preconditions=preconditions, message=message)


@dataclass(frozen=True)
class RuntimeActivationSnapshot:
    """Immutable snapshot of runtime activation state."""
    
    runtime_id: str
    boot_session_id: str
    is_activated: bool
    source_state: str  # ActivationState name
    final_state: Optional[str] = None  # ActivationState name if completed
    transaction_id: Optional[str] = None
    activated_entity_ids: List[str] = field(default_factory=list)
    rolled_back_entity_ids: List[str] = field(default_factory=list)
    primary_failure: Optional[str] = None


class RuntimeActivationController:
    """
    Canonical runtime-wide activation facade.
    
    This is the SINGLE canonical authority for runtime activation requests.
    It coordinates with the lifecycle coordinator and state store to ensure
    proper activation sequencing.
    
    Responsibilities:
        - Accept activation requests
        - Validate activation preconditions
        - Coordinate with RuntimeLifecycleCoordinator
        - Record activation transactions in RuntimeStateStore
        - Publish activation events
        - Provide immutable snapshots
    
    Does NOT:
        - Activate individual components directly (delegates to coordinator)
        - Mutate lifecycle state outside the coordinator
        - Open admission or set readiness
        - Execute normal tasks
    """
    
    def __init__(
        self,
        runtime_id: str,
        boot_session_id: str,
        state_store: RuntimeStateStore,
        lifecycle_coordinator: Optional["RuntimeLifecycleCoordinator"] = None,
        config: Optional[ActivationConfig] = None
    ) -> None:
        import threading
        
        self._runtime_id = runtime_id
        self._boot_session_id = boot_session_id
        self._state_store = state_store
        self._lifecycle_coordinator = lifecycle_coordinator
        self._config = config or ActivationConfig()
        
        # Transaction state
        self._lock = threading.Lock()
        self._current_transaction: Optional[ActivationTransaction] = None
        
        # Activation history (bounded)
        self._activation_history: List[RuntimeActivationSnapshot] = []
        self._max_history_size = 10
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID."""
        return self._runtime_id
    
    @property
    def is_activated(self) -> bool:
        """
        Check if runtime is currently activated.
        
        Returns True only if activation has completed successfully and
        the runtime is in ACTIVE state (not failing).
        """
        with self._lock:
            if self._current_transaction:
                return self._current_transaction.state == ActivationTransactionState.COMPLETED
            # Fall back to state store check
            current_state = self._state_store.state.state
            return current_state == RuntimeState.RUNNING
    
    def _validate_preconditions(
        self,
        request: ActivationRequest
    ) -> ActivationPreconditionResult:
        """
        Validate all activation preconditions.
        
        Returns:
            ActivationPreconditionResult indicating success or failure with details
        """
        failed = []
        
        # Check 1: Runtime exists and is valid
        if not self._runtime_id:
            failed.append("invalid_runtime_id")
        
        # Check 2: Runtime composition is complete (would use state_store in real impl)
        current_state = self._state_store.state.state
        if current_state not in (
            RuntimeState.ASSEMBLED,
            RuntimeState.READY,
            RuntimeState.STARTING
        ):
            failed.append("runtime_not_assembled_or_ready")
        
        # Check 3: No shutdown has begun
        if current_state in (RuntimeState.STOPPING, RuntimeState.STOPPED, RuntimeState.FAILED):
            failed.append("shutdown_already_started")
        
        # Check 4: No activation already active (checked at transaction level)
        with self._lock:
            if self._current_transaction and self._current_transaction.state in (
                ActivationTransactionState.ACTIVATING,
                ActivationTransactionState.ROLLING_BACK
            ):
                failed.append("activation_already_in_progress")
        
        # Check 5: Source state matches expected
        if current_state.name.lower().replace("_", "_") != request.expected_source_state.value:
            if not (current_state == RuntimeState.STARTING and 
                    request.expected_source_state == ActivationState.ASSEMBLED):
                failed.append("invalid_source_state")
        
        # Check 6: Readiness is false or unevaluated
        # Readiness is evaluated separately - don't block activation on it
        
        # Check 7: Admission is closed (checked at runtime level)
        # This would be checked via admission_authority in real impl
        
        if failed:
            return ActivationPreconditionResult.failure(failed, "Preconditions not met")
        return ActivationPreconditionResult.success()
    
    async def request_activation(
        self,
        request: Optional[ActivationRequest] = None
    ) -> Tuple[bool, RuntimeActivationSnapshot]:
        """
        Request runtime activation.
        
        This is the canonical entry point for activation. It:
        1. Validates preconditions
        2. Checks for concurrent activation attempts
        3. Delegates to lifecycle coordinator if available
        4. Records transaction in state store
        5. Returns immutable result
        
        Args:
            request: Optional activation request (creates default if not provided)
            
        Returns:
            Tuple of (success, snapshot) where snapshot contains full result info
            
        Raises:
            ActivationPreconditionError: If preconditions fail
            ActivationConcurrencyError: If concurrent activation detected
            RuntimeError: On activation failure
        """
        # Create default request if none provided
        if request is None:
            request = ActivationRequest.create(self._runtime_id)
        
        with self._lock:
            # Check for existing active transaction (concurrent activation check)
            if self._current_transaction and self._current_transaction.state in (
                ActivationTransactionState.ACTIVATING,
                ActivationTransactionState.ROLLING_BACK
            ):
                raise ActivationConcurrencyError(
                    f"Activation already in progress: {self._current_transaction.transaction_id}",
                    runtime_id=self._runtime_id,
                    existing_transaction_id=self._current_transaction.transaction_id
                )
            
            # Check for idempotent re-activation of active runtime
            if self.is_activated:
                return True, RuntimeActivationSnapshot(
                    runtime_id=self._runtime_id,
                    boot_session_id=self._boot_session_id,
                    is_activated=True,
                    source_state="active",
                    final_state="active",
                    transaction_id=request.activation_id,
                    activated_entity_ids=[],
                    rolled_back_entity_ids=[]
                )
            
            # Create new transaction
            self._current_transaction = ActivationTransaction(
                transaction_id=request.activation_id,
                runtime_id=self._runtime_id,
                activation_request=request,
                state=ActivationTransactionState.REQUESTED
            )
        
        try:
            # Validate preconditions
            precond_result = self._validate_preconditions(request)
            if not precond_result.passed:
                raise ActivationPreconditionError(
                    f"Activation preconditions failed: {precond_result.message}",
                    runtime_id=self._runtime_id,
                    precondition_name=";".join(precond_result.failed_preconditions)
                )
            
            # Transition to VALIDATING
            with self._lock:
                if self._current_transaction:
                    self._current_transaction.state = ActivationTransactionState.VALIDATING
            
            # If lifecycle coordinator is available, delegate to it
            if self._lifecycle_coordinator:
                try:
                    transaction, result = await self._lifecycle_coordinator.request_activation(request)
                    
                    with self._lock:
                        if transaction.state == ActivationTransactionState.COMPLETED:
                            # Update state store
                            transition = RuntimeStateTransition(
                                from_state=self._state_store.state.state,
                                to_state=RuntimeState.RUNNING,
                                timestamp=time.monotonic(),
                                registry_revision=self._state_store.version + 1,
                                runtime_id=self._runtime_id,
                                reason="activation_complete"
                            )
                            self._state_store.transition(transition)
                            
                            snapshot = RuntimeActivationSnapshot(
                                runtime_id=self._runtime_id,
                                boot_session_id=self._boot_session_id,
                                is_activated=True,
                                source_state=request.expected_source_state.value,
                                final_state= ActivationState.ACTIVE.value,
                                transaction_id=request.activation_id,
                                activated_entity_ids=list(transaction.activated_entities),
                                rolled_back_entity_ids=[]
                            )
                            
                            # Add to history
                            self._add_to_history(snapshot)
                            
                            return True, snapshot
                        else:
                            # Handle failure - rollback if needed
                            raise RuntimeError(
                                f"Activation failed: {result.primary_failure}"
                                if result and result.primary_failure
                                else "Activation failed"
                            )
                except Exception as e:
                    # Record failure in transaction
                    with self._lock:
                        if self._current_transaction:
                            self._current_transaction.state = ActivationTransactionState.FAILED
                            self._current_transaction.primary_failure = ActivationFailure(
                                step_id=-1,
                                entity_id=EntityId(self._runtime_id),
                                failed_transition="activation_failed",
                                primary_cause=e
                            )
                    
                    # Transition state store to FAILED
                    transition = RuntimeStateTransition(
                        from_state=self._state_store.state.state,
                        to_state=RuntimeState.FAILED,
                        timestamp=time.monotonic(),
                        registry_revision=self._state_store.version + 1,
                        runtime_id=self._runtime_id,
                        reason=str(e)
                    )
                    self._state_store.transition(transition)
                    
                    # Create failure snapshot
                    snapshot = RuntimeActivationSnapshot(
                        runtime_id=self._runtime_id,
                        boot_session_id=self._boot_session_id,
                        is_activated=False,
                        source_state=request.expected_source_state.value,
                        final_state=ActivationState.FAILED.value,
                        transaction_id=request.activation_id,
                        primary_failure=str(e)
                    )
                    
                    self._add_to_history(snapshot)
                    
                    return False, snapshot
            else:
                # No lifecycle coordinator - perform basic activation
                # This is a simplified path for direct component activation
                
                # Update state store to RUNNING
                transition = RuntimeStateTransition(
                    from_state=self._state_store.state.state,
                    to_state=RuntimeState.RUNNING,
                    timestamp=time.monotonic(),
                    registry_revision=self._state_store.version + 1,
                    runtime_id=self._runtime_id,
                    reason="activation_complete"
                )
                
                if not self._state_store.transition(transition):
                    raise RuntimeError("Failed to transition state store to RUNNING")
                
                with self._lock:
                    if self._current_transaction:
                        self._current_transaction.state = ActivationTransactionState.COMPLETED
                
                snapshot = RuntimeActivationSnapshot(
                    runtime_id=self._runtime_id,
                    boot_session_id=self._boot_session_id,
                    is_activated=True,
                    source_state=request.expected_source_state.value,
                    final_state=ActivationState.ACTIVE.value,
                    transaction_id=request.activation_id
                )
                
                self._add_to_history(snapshot)
                
                return True, snapshot
                
        except Exception as e:
            # Ensure we're in FAILED state
            with self._lock:
                if self._current_transaction:
                    self._current_transaction.state = ActivationTransactionState.FAILED
            
            raise
    
    def _add_to_history(self, snapshot: RuntimeActivationSnapshot) -> None:
        """Add a snapshot to the activation history (bounded)."""
        with self._lock:
            self._activation_history.append(snapshot)
            if len(self._activation_history) > self._max_history_size:
                # Remove oldest entries
                self._activation_history = self._activation_history[-self._max_history_size:]
    
    def get_snapshot(self) -> RuntimeActivationSnapshot:
        """
        Get an immutable snapshot of the current activation state.
        
        Returns the latest snapshot, which reflects either:
            - Current transaction state (if active)
            - Last completed activation (if inactive)
        """
        with self._lock:
            # Return most recent history entry if available
            if self._activation_history:
                return self._activation_history[-1]
            
            # Otherwise construct from current state
            current_state = self._state_store.state.state
            
            return RuntimeActivationSnapshot(
                runtime_id=self._runtime_id,
                boot_session_id=self._boot_session_id,
                is_activated=current_state == RuntimeState.RUNNING,
                source_state=current_state.value if hasattr(current_state, 'value') else str(current_state)
            )
    
    def get_activation_history(self) -> List[RuntimeActivationSnapshot]:
        """Get bounded history of activation snapshots (oldest first)."""
        with self._lock:
            return list(self._activation_history)


__all__ = [
    # Runtime Truth Publication System (Phase 3.7.11-R)
    "RuntimeTruth",
    "RuntimeTruthVersion", 
    "RuntimeTruthSnapshot",
    
    # State enumeration (original + canonical)
    "RuntimeState",
    "CanonicalRuntimeState",
    
    # Guard system (including Phase 3.7.8 guards)
    "GuardResult",
    "GuardEvaluation",
    "StateGuard",
    "ResourceGuard",
    "ReadinessGuard",
    "GuardManager",
    "ResourcesAvailableGuard",
    "ReadinessSatisfiedGuard",
    "AdmissionPermittedGuard",
    "SchedulerAvailableGuard",
    "ExecutorAvailableGuard",
    "IntegrityValidGuard",
    "HealthAcceptableGuard",
    "ShutdownAbsentGuard",
    
    # Snapshot and transition types
    "RuntimeStateSnapshot",
    "RuntimeStateTransition",
    
    # Store and truth
    "RuntimeStateStore",
    "RuntimeStateTruth",
    
    # Activation lifecycle state machine types
    "ActivationState",
    "ActivationTransactionState",
    "ActivationRequest",
    "ActivationContext",
    "ActivationFailure",
    "ActivationResult",
    "ActivationStatus",
    "ActivationConcurrencyConfig",
    "ActivationTimeoutConfig",
    "ActivationConfig",
    "RuntimeLifecycleCoordinatorSnapshot",
    "ActivationTransaction",
    
    # Runtime Activation Controller (canonical authority)
    "RuntimeActivationController",
    "ActivationPreconditionError",
    "ActivationAuthorityError",
    "ActivationConcurrencyError",
    "ActivationPreconditionResult",
    "RuntimeActivationSnapshot",
    
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
    
    # State Machine (Phase 3.7.8-I)
    "RuntimeTransitionId",
    "RuntimeVersion",
    "RuntimeSnapshot",
    "RuntimeTransitionRequest",
    "RuntimeTransitionResult",
    "RuntimeTransitionFailure",
    "RuntimeHistoryEntry",
    "RuntimeInvariantResult",
    "TransitionValidator",
    "GuardEvaluator",
    "RuntimeStateMachine",
    "StateMachineConfig",
    "StateMachineEventPublisher",
    "InvariantValidator",
]
