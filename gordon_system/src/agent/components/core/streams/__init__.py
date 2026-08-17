# Stream Infrastructure
# ====================

"""
Stream infrastructure package.

This module provides canonical stream types, exceptions, and utility functions
for all Core stream operations. Every other streams submodule may import from
this module but shall never define these types again.

Stream ownership model:
    - Streams own their content and semantics
    - Core owns the transport mechanism (registry, storage interface, backpressure)
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, FrozenSet
import uuid


class StreamKind(Enum):
    """
    Categories of stream types.
    
    Defines the fundamental kinds of streams in the system:
        - EVENT: Event streams for notifications and changes
        - COMMAND: Command streams for actions and requests
        - DATA: Data streams for persistent information
        - CONTROL: Control streams for system management
        - OBSERVATION: Observation streams for sensory input and perception
    """
    
    EVENT = "event"              # Event/notification stream
    COMMAND = "command"          # Command/request stream
    DATA = "data"                # Data/persistence stream
    CONTROL = "control"          # Control/management stream
    OBSERVATION = "observation"  # Observation/perception stream

# Re-export canonical types from existing modules to provide unified API
# The canonical definitions exist in:
#   - lifecycle.py: StreamLifecycleState and StreamLifecycleTransitionGraph
#   - security.py: IdentityId, StreamId, StreamRecordId, etc.
#
# Phase 3.14.6 Interaction Contracts (imported after stream infrastructure)
from agent.architecture.interaction.taxonomy import (
    Interaction,
    Request,
    Response,
    Command,
    Event,
    Signal,
    Notification,
    Proposal,
    Observation,
    Query,
    Publication as TaxonomyPublication,
    Subscription as TaxonomySubscription,
    Checkpoint,
    Heartbeat,
    Synchronization,
    Transaction,
    Recovery,
    InteractionCategory,
    InteractionId,
    InteractionCorrelation,
    InteractionTrait,
)

from agent.architecture.interaction.semantics import (
    RequestState,
    ResponseState,
    CommandState,
    Outcome,
    DiagnosticMetadata,
)

# =============================================================================
# IDENTITY TYPES (re-exported from security.py for convenience)
# =============================================================================

# Identity types are defined in security.py with richer semantics
# This package provides the canonical import point

# =============================================================================
# LIFECYCLE TYPES (imported from lifecycle.py - canonical source)
# =============================================================================


class StreamLifecycleState(Enum):
    """
    Stream lifecycle states.
    
    State Flow:
        DECLARED → REGISTERED → INITIALIZING → READY → ACTIVATING → ACTIVE
            ↓             ↓              ↓          ↓          ↓      ↘
        [CLOSED]     [FAILED]      [FAILED]  [FAILED]  [DRAINING]  DRAINED
                                                          ↓           ↓
                                                        [DEGRADED]──┘
        
        Active transitions:
            ACTIVE ↔ PAUSED   - Temporarily suspends admission
            ACTIVE → DRAINING - Graceful shutdown, allows in-flight completion
            ACTIVE → DEGRADED - Operational under limitations
        
        Failed recovery paths:
            Any state → FAILED (error detected)
            FAILED → RECOVERING (recovery initiated)
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


class StreamLifecycleTransitionGraph:
    """
    Stream lifecycle state transition graph.
    
    Defines all valid transitions between lifecycle states and the rules
    governing each transition. Only one authority (per stream instance)
    may commit transitions.
    """
    
    def __init__(self) -> None:
        # Build the complete transition map
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
    timestamp: float = field(default_factory=lambda: 0.0)  # When did it occur?
    
    # Authority tracking
    requesting_authority: Optional[str] = None  # Who requested it?
    committing_authority: Optional[str] = None  # Who committed it?
    
    # Validation
    validation_result: str = "valid"      # pre-validation, post-validation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transition record to dictionary for serialization."""
        return {
            "stream_id": self.stream_id,
            "runtime_instance_id": self.runtime_instance_id,
            "previous_state": self.previous_state.value,
            "requested_state": self.requested_state.value,
            "committed_state": self.committed_state.value,
            "transition_id": self.transition_id,
            "timestamp": self.timestamp,
            "requesting_authority": self.requesting_authority,
            "committing_authority": self.committing_authority,
            "validation_result": self.validation_result,
        }


@dataclass(frozen=True)
class StreamLifecycleSnapshot:
    """
    Immutable snapshot of stream lifecycle state.
    
    Used for persistence and recovery.
    """
    
    stream_id: str
    state: StreamLifecycleState
    
    # Operational information
    generation_count: int = 0
    record_count: int = 0
    last_activity_timestamp: float = field(default_factory=lambda: 0.0)


# =============================================================================
# IDENTITY TYPES
# =============================================================================


class IdentityType(Enum):
    """Categories of identity for routing and validation."""
    
    SYSTEM = "system"      # System-level identities
    NETWORK = "network"    # Network-related identities  
    USER = "user"          # Human user identities
    SERVICE = "service"    # Service-to-service identities


class IdentityCategory(Enum):
    """Security classification for identity scope."""
    
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"


@dataclass(frozen=True)
class IdentityId:
    """Unique identifier for an identity."""
    
    value: str
    category: IdentityCategory = IdentityCategory.INTERNAL
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Identity ID cannot be empty")
    
    @classmethod
    def generate(cls, prefix: str = "", category: IdentityCategory = IdentityCategory.INTERNAL) -> "IdentityId":
        """Generate a new random identity ID."""
        unique_id = str(uuid.uuid4())[:12]
        return cls(value=f"{prefix}{unique_id}", category=category)


@dataclass(frozen=True)
class StreamId:
    """
    Unique identifier for a stream.
    
    Format: domain/name/scope
    Example: user/events/session-abc123
    
    Ownership:
        - Streams own their semantic meaning (domain)
        - Core owns the transport mechanism (name, scope)
    """
    
    domain: str       # Semantic owner domain
    name: str         # Stream type/semantic purpose
    scope: str = ""   # Isolation scope (empty for global)
    
    def __post_init__(self):
        if not self.domain:
            raise ValueError("Stream domain cannot be empty")
        if not self.name:
            raise ValueError("Stream name cannot be empty")
    
    @classmethod
    def from_string(cls, value: str) -> "StreamId":
        """Parse a stream ID string into components."""
        parts = value.split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid stream ID format: {value}")
        
        domain = parts[0]
        name = parts[1]
        scope = parts[2] if len(parts) > 2 else ""
        
        return cls(domain=domain, name=name, scope=scope)
    
    def to_string(self) -> str:
        """Convert stream ID to string format."""
        if self.scope:
            return f"{self.domain}/{self.name}/{self.scope}"
        return f"{self.domain}/{self.name}"
    
    def matches(self, other: "StreamId") -> bool:
        """Check if two stream IDs match (ignoring scope)."""
        return self.domain == other.domain and self.name == other.name


@dataclass(frozen=True)
class StreamRecordId:
    """
    Unique identifier for a record within a stream.
    
    Format: generation:sequence
    Example: gen-001:seq-42
    """
    
    generation_id: str
    sequence_number: int
    
    def __post_init__(self):
        if not self.generation_id:
            raise ValueError("Generation ID cannot be empty")
        if self.sequence_number < 0:
            raise ValueError("Sequence number must be non-negative")


@dataclass(frozen=True)
class StreamGenerationId:
    """Identifier for a stream generation."""
    
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Generation ID cannot be empty")


@dataclass(frozen=True)
class StreamCursor:
    """
    Position cursor for reading streams.
    
    Cursor tracks progress through a stream and supports multiple
    navigation modes (from_start, from_end, from_position).
    """
    
    position: str              # Position marker (checkpoint ID, timestamp, etc.)
    mode: str = "from_start"   # Navigation mode
    
    VALID_MODES = {"from_start", "from_end", "from_position"}
    
    def __post_init__(self):
        if self.mode not in self.VALID_MODES:
            raise ValueError(f"Invalid cursor mode: {self.mode}")


@dataclass(frozen=True)
class StreamCheckpoint:
    """
    Checkpoint for stream recovery.
    
    Contains all state needed to resume stream operations from a known
    consistent point.
    """
    
    stream_id: str
    generation_id: Optional[str] = None
    position: Optional[str] = None
    timestamp: float = 0.0


@dataclass(frozen=True)
class StreamPosition:
    """
    Absolute position in a stream.
    
    Combines generation and sequence number for precise positioning.
    """
    
    generation_id: str
    sequence_number: int
    
    def __post_init__(self):
        if not self.generation_id:
            raise ValueError("Generation ID cannot be empty")
        if self.sequence_number < 0:
            raise ValueError("Sequence number must be non-negative")


# =============================================================================
# EXCEPTIONS
# =============================================================================


class StreamError(Exception):
    """Base exception for stream operations."""
    pass


class StreamNotFoundError(StreamError, KeyError):
    """Raised when a stream cannot be found."""
    
    def __init__(self, stream_id: str):
        self.stream_id = stream_id
        super().__init__(f"Stream not found: {stream_id}")


class StreamClosedError(StreamError):
    """Raised when attempting operation on closed stream."""
    
    def __init__(self, stream_id: str):
        self.stream_id = stream_id
        super().__init__(f"Stream is closed: {stream_id}")


class StreamPausedError(StreamError):
    """Raised when stream is paused and cannot accept operations."""
    
    def __init__(self, stream_id: str):
        self.stream_id = stream_id
        super().__init__(f"Stream is paused: {stream_id}")


class CapacityExceededError(StreamError):
    """Raised when stream capacity limits are exceeded."""
    
    def __init__(self, stream_id: str, dimension: str, limit: int):
        self.stream_id = stream_id
        self.dimension = dimension
        self.limit = limit
        super().__init__(
            f"Capacity exceeded for {stream_id}: {dimension} limit is {limit}"
        )


class StreamGenerationClosedError(StreamError):
    """Raised when attempting to write to a closed generation."""
    
    def __init__(self, stream_id: str, generation_id: str):
        self.stream_id = stream_id
        self.generation_id = generation_id
        super().__init__(
            f"Generation {generation_id} is closed: {stream_id}"
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def validate_stream_id(stream_id: StreamId) -> Tuple[bool, Optional[str]]:
    """
    Validate a stream ID.
    
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(stream_id, StreamId):
        return False, "stream_id must be a StreamId instance"
    
    if not stream_id.domain or not stream_id.name:
        return False, "Stream domain and name cannot be empty"
    
    # Check for reserved characters
    reserved_chars = {" ", "/", "*", "?", "\"", "<", ">", "|"}
    for char in reserved_chars:
        if char in stream_id.to_string():
            return False, f"Stream ID contains invalid character: {char}"
    
    return True, None


def validate_stream_lifecycle_transition(
    graph: StreamLifecycleTransitionGraph,
    from_state: StreamLifecycleState,
    to_state: StreamLifecycleState
) -> Tuple[bool, Optional[str]]:
    """
    Validate a lifecycle transition using the provided graph.
    
    Returns:
        (is_valid, error_message)
    """
    if not graph.is_valid_transition(from_state, to_state):
        allowed = graph.get_allowed_transitions(from_state)
        return False, (
            f"Invalid transition: {from_state.value} -> {to_state.value}. "
            f"Allowed: {[s.value for s in allowed]}"
        )
    
    return True, None


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass.
    
    This is a compatibility implementation that works with frozen dataclasses
    by creating a new instance with the modified values.
    """
    if hasattr(obj, "__dataclass_fields__"):
        # Dataclass - create new instance
        field_dict = {f.name: getattr(obj, f.name) for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    
    raise TypeError(f"Cannot replace fields on non-dataclass object: {type(obj)}")


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Identity types
    "IdentityType", "IdentityCategory",
    "IdentityId", "StreamId", "StreamRecordId", "StreamGenerationId",
    
    # Position and checkpoint types
    "StreamCursor", "StreamCheckpoint", "StreamPosition",
    
    # Lifecycle types (canonical)
    "StreamLifecycleState", "StreamLifecycleTransitionGraph",
    "StreamLifecycleTransition", "StreamLifecycleSnapshot",
    
    # Interaction contracts (Phase 3.14.6)
    "StreamTransportRole",
    "StreamTransportConstraint",
    "PublicationContract",
    "SubscriptionContract",
    "RoutingContract",
    "OrderingType",
    "OrderingGuarantees",
    "ReplayContract",
    "IsolationRules",
    "OwnershipPreservation",
    "AuthorityPreservation",
    "StreamObservabilityMetadata",
    "StreamFailureType",
    "StreamTransportFailure",
    "InteractionStreamRecord",
    
    # StreamKind (new)
    "StreamKind",
    
    # Exceptions
    "StreamError", "StreamNotFoundError", "StreamClosedError",
    "StreamPausedError", "CapacityExceededError", 
    "StreamGenerationClosedError",
    
    # Utility functions
    "validate_stream_id", "validate_stream_lifecycle_transition",
    "dataclass_replace",
]
