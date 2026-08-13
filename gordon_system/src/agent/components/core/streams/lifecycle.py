# Stream Lifecycle Infrastructure - Phase 3.11.3
# ===============================================

"""
Canonical stream lifecycle state machine and ownership architecture.

This module provides the canonical lifecycle infrastructure for semantic streams.
Streams exist parallel to execution hierarchy without owning any aspect of it.

Ownership Model:
    SemanticOwner     - Defines stream purpose, domain semantics, validation rules
    InfrastructureOwn - Core owns generic transport, storage interface, cursors
    RuntimeOwner      - Scoped runtime instance owns active stream state
    LifecycleAuth     - Singular authority commits lifecycle transitions
    CommitAuthority   - Canonical position allocator (may overlap with RuntimeOwner)

Stream Lifecycle Axis:
    DECLARED → REGISTERED → INITIALIZING → READY → ACTIVE → [PAUSED/DRAINING/DEGRADED] → CLOSED
    
    FAILED: Terminal failure state (may recover if policy permits)
    
Active State Transitions:
    ACTIVE ↔ PAUSED   - Temporarily suspends admission
    ACTIVE → DRAINING - Graceful shutdown, allows in-flight completion
    ACTIVE → DEGRADED - Operational under limitations
    ACTIVE → CLOSING  - Permanent shutdown
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, FrozenSet
from enum import Enum
import time

# =============================================================================
# STREAM LIFECYCLE STATE ENUMERATION
# =============================================================================


class StreamLifecycleState(Enum):
    """
    Canonical stream lifecycle states.
    
    State Flow:
        DECLARED → REGISTERED → INITIALIZING → READY → ACTIVATING → ACTIVE
            ↓             ↓              ↓          ↓          ↓      ↘
        [CLOSED]     [FAILED]      [FAILED]  [FAILED]  [DRAINING]  DRAINED
                                                         ↓           ↓
                                                       [DEGRADED]──┘
            ↑                    ↑               ↑         ↑
        FAILED                RECOVERING    RESUMING   PAUSED
    
    Ownership:
        - SemanticOwner owns policy and meaning (not runtime state)
        - InfrastructureOwner owns generic machinery
        - RuntimeOwner owns active instance state
        - LifecycleAuthority commits transitions
    """
    
    # Initial states - infrastructure preparation
    DECLARED = "declared"           # Metadata exists, no runtime created
    REGISTERED = "registered"       # Registry accepted descriptor
    
    # Initialization states
    INITIALIZING = "initializing"   # Runtime structures prepared
    READY = "ready"                 # All dependencies ready
    
    # Activation states
    ACTIVATING = "activating"       # Opening generation, binding authorities
    ACTIVE = "active"               # Normal operation, admits commits
    
    # Temporary suspension states
    PAUSING = "pausing"             # Suspending admission
    PAUSED = "paused"               # Suspended, may resume later
    RESUMING = "resuming"           # Resuming from paused state
    
    # Shutdown states
    DRAINING = "draining"           # Allowing in-flight completion
    DRAINED = "drained"             # In-flight work complete
    CLOSING = "closing"             # Final shutdown
    CLOSED = "closed"               # Terminal (permanently ended)
    
    # Error/recovery states
    DEGRADING = "degrading"         # Entering degraded mode
    DEGRADED = "degraded"           # Operational under limitations
    RECOVERING = "recovering"       # Restoring from failure
    FAILING = "failing"             # Failed, cannot continue safely
    FAILED = "failed"               # Terminal failure state


# =============================================================================
# LIFECYCLE TRANSITION GRAPH
# =============================================================================


class StreamLifecycleTransitionGraph:
    """
    Stream lifecycle state transition graph.
    
    Defines all valid transitions between lifecycle states and the rules
    governing each transition. Only one authority (per stream instance)
    may commit transitions.
    """
    
    def __init__(self) -> None:
        self._transitions: Dict[Tuple[StreamLifecycleState, StreamLifecycleState], str] = {
            # Initialization path
            (StreamLifecycleState.DECLARED, StreamLifecycleState.REGISTERED): "Registry accepted descriptor",
            (StreamLifecycleState.REGISTERED, StreamLifecycleState.INITIALIZING): "Runtime initialization started",
            (StreamLifecycleState.INITIALIZING, StreamLifecycleState.READY): "Dependencies validated and ready",
            
            # Activation path
            (StreamLifecycleState.READY, StreamLifecycleState.ACTIVATING): "Activation requested",
            (StreamLifecycleState.ACTIVATING, StreamLifecycleState.ACTIVE): "Generation opened, authorities bound",
            
            # Normal operations
            (StreamLifecycleState.ACTIVE, StreamLifecycleState.PAUSING): "Pause requested",
            (StreamLifecycleState.ACTIVE, StreamLifecycleState.DRAINING): "Shutdown requested",
            (StreamLifecycleState.ACTIVE, StreamLifecycleState.DEGRADING): "Degradation detected",
            
            # Pause/resume cycle
            (StreamLifecycleState.PAUSING, StreamLifecycleState.PAUSED): "Paused successfully",
            (StreamLifecycleState.PAUSED, StreamLifecycleState.RESUMING): "Resume requested",
            (StreamLifecycleState.RESUMING, StreamLifecycleState.ACTIVE): "Resumed successfully",
            
            # Draining paths
            (StreamLifecycleState.DRAINING, StreamLifecycleState.DRAINED): "In-flight work completed",
            (StreamLifecycleState.DRAINED, StreamLifecycleState.CLOSING): "Drain complete, closing",
            (StreamLifecycleState.DRAINED, StreamLifecycleState.RESUMING): "Resume from drained state",
            
            # Degradation paths
            (StreamLifecycleState.DEGRADING, StreamLifecycleState.DEGRADED): "Degraded mode entered",
            (StreamLifecycleState.DEGRADED, StreamLifecycleState.RECOVERING): "Recovery initiated",
            
            # Recovery path
            (StreamLifecycleState.RECOVERING, StreamLifecycleState.ACTIVE): "Recovered successfully",
            (StreamLifecycleState.RECOVERING, StreamLifecycleState.PAUSED): "Recovered but paused",
            (StreamLifecycleState.RECOVERING, StreamLifecycleState.DEGRADED): "Recovered in degraded state",
            
            # Close paths
            (StreamLifecycleState.CLOSING, StreamLifecycleState.CLOSED): "Shutdown complete",
            
            # Failed transitions
            (StreamLifecycleState.DECLARED, StreamLifecycleState.FAILED): "Initialization failure",
            (StreamLifecycleState.REGISTERED, StreamLifecycleState.FAILED): "Registration validation failed",
            (StreamLifecycleState.INITIALIZING, StreamLifecycleState.FAILED): "Runtime initialization failed",
            (StreamLifecycleState.READY, StreamLifecycleState.FAILED): "Dependencies unavailable",
            (StreamLifecycleState.ACTIVATING, StreamLifecycleState.FAILED): "Generation open failed",
            (StreamLifecycleState.PAUSED, StreamLifecycleState.FAILED): "Paused state corruption detected",
            (StreamLifecycleState.DRAINING, StreamLifecycleState.FAILED): "Drain timeout or error",
            (StreamLifecycleState.CLOSING, StreamLifecycleState.FAILED): "Shutdown incomplete",
            
            # Failed recovery paths
            (StreamLifecycleState.FAILED, StreamLifecycleState.RECOVERING): "Recovery requested",
        }
    
    def get_transition_reason(self, from_state: StreamLifecycleState, to_state: StreamLifecycleState) -> Optional[str]:
        """Get the reason description for a valid transition."""
        return self._transitions.get((from_state, to_state))
    
    def is_valid_transition(self, from_state: StreamLifecycleState, to_state: StreamLifecycleState) -> bool:
        """Check if a transition is valid according to the graph."""
        return (from_state, to_state) in self._transitions
    
    def get_allowed_transitions(self, state: StreamLifecycleState) -> Tuple[StreamLifecycleState, ...]:
        """Get all states that can be reached from given state."""
        return tuple(
            to for (f, to) in self._transitions.keys()
            if f == state
        )
    
    def get_all_states(self) -> FrozenSet[StreamLifecycleState]:
        """Get all valid lifecycle states."""
        return frozenset(StreamLifecycleState)


# =============================================================================
# LIFECYCLE TRANSITION CONTRACT
# =============================================================================


@dataclass(frozen=True)
class StreamLifecycleTransition:
    """
    Immutable contract for a lifecycle state transition.
    
    Every transition must be committed by the canonical lifecycle authority.
    The transition record is immutable and preserves provenance.
    """
    
    # Identity
    stream_id: str                   # Which stream?
    runtime_instance_id: str         # Which instance (for scoped ownership)
    
    # State information
    previous_state: StreamLifecycleState
    requested_state: StreamLifecycleState  # What was requested
    committed_state: StreamLifecycleState   # What actually became current
    
    # Transition metadata
    transition_id: str               # Unique ID for this transition
    triggered_at_utc: float          # When transition was triggered
    committed_at_utc: float = field(default_factory=time.time)  # When committed
    
    # Authority information
    requested_by: Optional[str] = None    # Who requested?
    authority_id: Optional[str] = None     # Who committed it?
    
    # Context
    generation_before: Optional[str] = None   # Active generation before
    generation_after: Optional[str] = None    # Active generation after
    
    admission_before: bool = True      # Was admission open before?
    admission_after: bool = True       # Is admission open after?
    
    degradation_state_before: str = "healthy"  # Before
    degradation_state_after: str = "healthy"   # After
    
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: Optional[Dict[str, str]] = None  # For audit trail
    
    @classmethod
    def from_request(
        cls,
        stream_id: str,
        runtime_instance_id: str,
        previous_state: StreamLifecycleState,
        requested_state: StreamLifecycleState,
        transition_id: Optional[str] = None,
        requested_by: Optional[str] = None,
        authority_id: Optional[str] = None,
    ) -> "StreamLifecycleTransition":
        """Create a new lifecycle transition from a request."""
        return cls(
            stream_id=stream_id,
            runtime_instance_id=runtime_instance_id,
            previous_state=previous_state,
            requested_state=requested_state,
            committed_state=requested_state,  # By default, what was requested
            transition_id=transition_id or f"t-{time.monotonic_ns()}-{hash(requested_by or '') % 1000:04d}",
            triggered_at_utc=time.time(),
            requested_by=requested_by,
            authority_id=authority_id,
        )
    
    def with_committed_state(self, state: StreamLifecycleState) -> "StreamLifecycleTransition":
        """Create new transition with different committed state."""
        return dataclass_replace(self, committed_state=state)
    
    def with_generation(self, gen_before: Optional[str], gen_after: Optional[str]) -> "StreamLifecycleTransition":
        """Update generation information."""
        return dataclass_replace(
            self,
            generation_before=gen_before,
            generation_after=gen_after
        )
    
    def with_admission(self, before: bool, after: bool) -> "StreamLifecycleTransition":
        """Update admission state."""
        return dataclass_replace(
            self,
            admission_before=before,
            admission_after=after
        )
    
    def with_degradation(self, before: str, after: str) -> "StreamLifecycleTransition":
        """Update degradation state."""
        return dataclass_replace(
            self,
            degradation_state_before=before,
            degradation_state_after=after
        )


@dataclass(frozen=True)
class StreamLifecycleSnapshot:
    """
    Immutable snapshot of current stream lifecycle state.
    
    Used for persistence, recovery, and read-only inspection. Contains only
    bounded metadata - no live objects, locks, or service instances.
    """
    
    # Identity
    stream_id: str
    runtime_instance_id: str
    
    # Current state
    lifecycle_state: StreamLifecycleState
    active_generation_id: Optional[str] = None  # generation_id.value or None
    
    # Last transition reference
    last_transition_id: Optional[str] = None
    
    # Configuration context
    configuration_generation: int = 1
    ownership_version: int = 1
    
    # Operational status
    admission_status: str = "open"       # open, paused, draining, closed
    degradation_state: str = "healthy"   # healthy, degraded, recovering
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def from_transition(
        cls,
        stream_id: str,
        runtime_instance_id: str,
        transition: StreamLifecycleTransition
    ) -> "StreamLifecycleSnapshot":
        """Create a snapshot from the result of a lifecycle transition."""
        return cls(
            stream_id=stream_id,
            runtime_instance_id=runtime_instance_id,
            lifecycle_state=transition.committed_state,
            active_generation_id=transition.generation_after,
            last_transition_id=transition.transition_id,
            configuration_generation=1,  # Will be updated by config authority
            ownership_version=1,         # Will be updated on ownership changes
            admission_status="open" if transition.admission_after else "closed",
            degradation_state=transition.degradation_state_after,
        )


# =============================================================================
# OWNERSHIP MODEL - Roles and Descriptors
# =============================================================================


class OwnershipRole(Enum):
    """
    Semantic ownership roles for streams.
    
    These roles may be held by the same subsystem where appropriate but
    remain semantically distinct. The model prevents collapse into a single
    generic owner field.
    """
    
    # Primary ownership roles
    SEMANTIC_OWNER = "semantic_owner"           # Defines stream purpose, semantics, validation rules
    INFRASTRUCTURE_OWNER = "infrastructure_owner"  # Core owns generic transport/storage infrastructure
    RUNTIME_OWNER = "runtime_owner"             # Scoped runtime instance owns active state
    
    # Authority roles
    LIFECYCLE_AUTHORITY = "lifecycle_authority"     # Commits lifecycle transitions (singular per stream)
    COMMIT_AUTHORITY = "commit_authority"           # Allocates canonical positions (may overlap with runtime owner)
    
    # Administrative roles
    CONFIGURATION_AUTHORITY = "configuration_authority"  # May configure stream parameters
    ADMINISTRATIVE_AUTHORITY = "administrative_authority"  # May perform administrative operations
    
    # Domain interaction roles
    PRODUCER_AUTHORITY = "producer_authority"     # May publish records when authorized
    CONSUMER_AUTHORITY = "consumer_authority"     # May consume records when authorized
    OBSERVER_AUTHORITY = "observer_authority"     # Passive inspection only
    RECOVERY_AUTHORITY = "recovery_authority"     # May trigger recovery


@dataclass(frozen=True)
class OwnershipDescriptor:
    """
    Immutable descriptor for stream ownership configuration.
    
    Contains all ownership information without live objects, locks, or callbacks.
    This is what gets persisted and restored across restarts.
    """
    
    # Identity
    stream_id: str
    
    # Ownership roles (stable identifiers, not instances)
    semantic_owner_id: Optional[str] = None
    infrastructure_owner_id: str = "core"  # Core owns generic infrastructure
    runtime_owner_id: Optional[str] = None
    
    # Authority bindings
    lifecycle_authority_id: Optional[str] = None
    commit_authority_id: Optional[str] = None
    
    configuration_authority_id: Optional[str] = None
    administrative_authority_id: Optional[str] = None
    recovery_authority_id: Optional[str] = None
    
    # Domain interaction authorities
    producer_authority_id: Optional[str] = None
    consumer_authority_id: Optional[str] = None
    observer_authority_id: Optional[str] = None
    
    # Scope and versioning
    scope: str = "global"  # global, user, session, agent, tenant, etc.
    ownership_version: int = 1
    
    # Temporal bounds
    effective_from_utc: float = field(default_factory=time.time)
    effective_until_utc: Optional[float] = None
    
    # Provenance (for audit)
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_runtime_context(
        cls,
        stream_id: str,
        runtime_instance_id: str,
        semantic_owner: Optional[str] = None,
    ) -> "OwnershipDescriptor":
        """Create ownership descriptor from runtime context."""
        return cls(
            stream_id=stream_id,
            infrastructure_owner_id="core",
            runtime_owner_id=runtime_instance_id,
            scope=cls._infer_scope(runtime_instance_id),
            semantic_owner_id=semantic_owner,
        )
    
    @staticmethod
    def _infer_scope(instance_id: str) -> str:
        """Infer scope from instance ID (simple heuristic)."""
        if "user:" in instance_id or "session:" in instance_id:
            return "user"
        if "agent:" in instance_id:
            return "agent"
        if "tenant:" in instance_id:
            return "tenant"
        return "global"
    
    def is_compatible_with(self, other: "OwnershipDescriptor") -> bool:
        """Check if two ownership descriptors are compatible for integration."""
        # Same stream ID required
        if self.stream_id != other.stream_id:
            return False
        
        # Scope must match (unless both are global)
        if self.scope != other.scope and self.scope != "global" and other.scope != "global":
            return False
        
        # Ownership version must be compatible
        return abs(self.ownership_version - other.ownership_version) <= 1
    
    def with_runtime_owner(self, new_owner: str) -> "OwnershipDescriptor":
        """Return descriptor with updated runtime owner."""
        return dataclass_replace(
            self,
            runtime_owner_id=new_owner,
            ownership_version=self.ownership_version + 1
        )
    
    def is_expired(self, at_utc: Optional[float] = None) -> bool:
        """Check if this descriptor has expired."""
        at = at_utc or time.time()
        return self.effective_until_utc is not None and at > self.effective_until_utc


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Simple dataclass replace implementation for frozen dataclasses."""
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


def validate_ownership_descriptor(descriptor: OwnershipDescriptor) -> Tuple[bool, Optional[str]]:
    """
    Validate ownership descriptor structure.
    
    Returns:
        (is_valid, error_message) tuple
    """
    if not descriptor.stream_id:
        return False, "stream_id is required"
    
    # Core infrastructure owner must be set
    if not descriptor.infrastructure_owner_id:
        return False, "infrastructure_owner_id must be set"
    
    # If runtime_owner is set, authority bindings are allowed
    # (runtime owner may hold multiple roles)
    
    return True, None


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # State enumeration
    "StreamLifecycleState",
    
    # Transition graph
    "StreamLifecycleTransitionGraph",
    
    # Contracts
    "StreamLifecycleTransition",
    "StreamLifecycleSnapshot",
    
    # Ownership model
    "OwnershipRole",
    "OwnershipDescriptor",
    "validate_ownership_descriptor",
    "dataclass_replace",
]