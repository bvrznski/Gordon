# Gordon Core - Communication Domains & Endpoints (Phase 3.21.2)
# ===============================================================
#
# Canonical endpoint architecture supporting all runtime entities
#
# Every architectural entity shall communicate through endpoints.
# Endpoints provide identity, ownership, visibility, authority,
# and communication policy for each participating entity.

"""
Canonical Communication Domains & Endpoints for Gordon Phase 3.21.2

ENDPOINT TYPES:
---------------
Every endpoint shall possess:
    - identity: Unique identifier across the runtime
    - ownership: Entity responsible for this endpoint
    - visibility: Which other endpoints can see this one
    - authority: What operations this endpoint can perform
    - communication policy: How messages are handled

Supported Endpoint Types:
    - RuntimeEndpoint: The entire runtime instance
    - ComponentEndpoint: Individual components within runtime
    - ServiceEndpoint: Services providing cross-component functionality
    - CapabilityEndpoint: Capabilities that provide specific behaviors
    - ModuleEndpoint: Modules containing related components
    - StreamEndpoint: Streams for ordered message transport
    - SchedulerEndpoint: Schedulers for time-based execution
    - ExecutionEndpoint: Execution engines for work processing
    - RecoveryEndpoint: Recovery systems for fault tolerance
    - DiagnosticEndpoint: Diagnostics for observability
    - ExternalEndpoint: External system connections
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, FrozenSet, Callable, Awaitable
from enum import Enum, auto
import time
import uuid


# =============================================================================
# ENDPOINT IDENTITY
# =============================================================================

@dataclass(frozen=True)
class EndpointId:
    """
    Unique identifier for an endpoint.
    
    Identity invariant: No two endpoints share the same ID across the runtime.
    """
    
    value: str
    
    @classmethod
    def generate(cls) -> "EndpointId":
        """Generate a new unique endpoint ID."""
        return cls(value=f"ep_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# ENDPOINT OWNERSHIP MODEL
# =============================================================================

class EndpointOwnershipType(Enum):
    """
    Types of ownership for endpoints.
    
    Invariants:
        - OWN-EP-001: Every endpoint has exactly one owner type
        - OWN-EP-002: Ownership cannot be transferred without explicit action
    """
    
    RUNTIME = "runtime"         # Owned by the runtime itself
    COMPONENT = "component"     # Owned by a specific component
    SERVICE = "service"         # Owned by a service (cross-component)
    CAPABILITY = "capability"   # Owned by a capability provider
    MODULE = "module"           # Owned by a module (grouping)
    SYSTEM = "system"           # System-level infrastructure
    EXTERNAL = "external"       # External system connection


@dataclass(frozen=True)
class EndpointOwnership:
    """
    Immutable record of endpoint ownership.
    
    Args:
        owner_type: Category of the owner
        owner_id: Identifier of the owning entity
        created_at_utc: When this endpoint was created
        created_by: Who/what created it (runtime, user, system)
    """
    
    owner_type: EndpointOwnershipType
    owner_id: str
    created_at_utc: float = field(default_factory=time.time)
    created_by: str = "runtime"


# =============================================================================
# ENDPOINT VISIBILITY MODEL
# =============================================================================

class VisibilityScope(Enum):
    """
    Canonical visibility scopes for endpoints.
    
    Invariants:
        - VIS-EP-001: Endpoints can only see what they have visibility into
        - VIS-EP-002: Visibility is preserved throughout message lifecycle
    """
    
    PRIVATE = "private"         # Only visible to self (no external communication)
    LOCAL = "local"             # Visible within current component/module
    COMPONENT = "component"     # Visible to other components in same runtime
    SERVICE = "service"         # Visible to services in cluster
    RUNTIME = "runtime"         # Visible across entire runtime instance
    GLOBAL = "global"           # System-wide visibility


@dataclass(frozen=True)
class EndpointVisibility:
    """
    Immutable record of endpoint visibility.
    
    Args:
        scope: The visibility scope level
        allowed_recipients: List of endpoint IDs this can communicate with
                            (empty tuple = unrestricted within scope)
        disallowed_recipients: Explicitly forbidden recipients
    """
    
    scope: VisibilityScope
    allowed_recipients: Tuple[str, ...] = field(default_factory=tuple)
    disallowed_recipients: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# ENDPOINT AUTHORITY MODEL
# =============================================================================

class EndpointAuthority(Enum):
    """
    Canonical authority levels for endpoints.
    
    Invariants:
        - AUT-EP-001: Authority determines what operations are permitted
        - AUT-EP-002: Authority cannot be elevated without explicit grant
    """
    
    NONE = "none"               # No communication authority
    READ_ONLY = "read-only"     # Can receive but not send
    SEND_ONLY = "send-only"     # Can send but not receive
    FULL = "full"               # Can both send and receive
    
    # Special authorities
    BROADCAST = "broadcast"     # Can broadcast to all endpoints
    MONITOR = "monitor"         # Can observe all communication


@dataclass(frozen=True)
class EndpointAuthorityRecord:
    """
    Immutable record of endpoint authority.
    
    Args:
        communication_authority: Basic send/receive authority
        special_authorities: Set of special authority flags
        policies_applied: List of policy names applied to this endpoint
    """
    
    communication_authority: EndpointAuthority = EndpointAuthority.FULL
    special_authorities: FrozenSet[EndpointAuthority] = field(default_factory=frozenset)
    policies_applied: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# COMMUNICATION POLICY MODEL
# =============================================================================

class DeliveryPolicy(Enum):
    """
    Canonical delivery policy types.
    
    Invariants:
        - DLV-EP-001: Policy determines how messages are delivered
        - DLV-EP-002: Policy is evaluated before message processing
    """
    
    IMMEDIATE = "immediate"     # Deliver immediately, no buffering
    BUFFERED = "buffered"       # Buffer and deliver when ready
    DEFERRED = "deferred"       # Defer delivery until explicit request
    BATCHED = "batched"         # Batch messages for efficiency


@dataclass(frozen=True)
class EndpointPolicy:
    """
    Immutable communication policy for an endpoint.
    
    Args:
        delivery_policy: How messages are delivered to this endpoint
        rate_limit_per_second: Maximum messages per second (0 = unlimited)
        max_queue_size: Maximum queued messages before backpressure
        timeout_seconds: Message timeout for this endpoint
        dead_letter_enabled: Whether dead-letter queue is enabled
    """
    
    delivery_policy: DeliveryPolicy = DeliveryPolicy.BUFFERED
    rate_limit_per_second: int = 0  # 0 = unlimited
    max_queue_size: int = 10000     # Default queue size
    timeout_seconds: float = 30.0   # Default message timeout
    dead_letter_enabled: bool = True


# =============================================================================
# ENDPOINT TYPE ENUMERATION
# =============================================================================

class EndpointType(Enum):
    """
    Canonical endpoint types in the Gordon architecture.
    
    Every endpoint shall belong to exactly one type.
    """
    
    # Runtime-level endpoints
    RUNTIME = "runtime"         # The entire runtime instance
    
    # Component-level endpoints
    COMPONENT = "component"     # Individual components
    
    # Service-level endpoints
    SERVICE = "service"         # Services providing cross-component functionality
    
    # Capability-level endpoints
    CAPABILITY = "capability"   # Capabilities providing specific behaviors
    
    # Module-level endpoints
    MODULE = "module"           # Modules containing related components
    
    # Infrastructure endpoints
    STREAM = "stream"           # Streams for ordered message transport
    SCHEDULER = "scheduler"     # Schedulers for time-based execution
    EXECUTION = "execution"     # Execution engines for work processing
    RECOVERY = "recovery"       # Recovery systems for fault tolerance
    DIAGNOSTIC = "diagnostic"   # Diagnostics for observability
    
    # External endpoints
    EXTERNAL = "external"       # External system connections


# =============================================================================
# ENDPOINT DESCRIPTOR
# =============================================================================

@dataclass(frozen=True, slots=True)
class EndpointDescriptor:
    """
    Immutable descriptor for an endpoint.
    
    This is the single source of truth for endpoint metadata.
    
    Args:
        endpoint_id: Unique identifier
        endpoint_type: The category of this endpoint
        name: Human-readable name (optional)
        description: Human-readable description (optional)
        
        # Ownership
        ownership: Who owns this endpoint
        
        # Visibility
        visibility: What other endpoints can see this one
        
        # Authority
        authority: What operations this endpoint can perform
        
        # Policy
        policy: How messages are handled for this endpoint
        
        # Context
        runtime_id: ID of the runtime this endpoint belongs to
        component_id: Optional component containing this endpoint
        metadata: Free-form metadata dictionary
    """
    
    # Identity
    endpoint_id: str
    endpoint_type: EndpointType
    
    # Naming
    name: Optional[str] = None
    description: Optional[str] = None
    
    # Ownership
    ownership: EndpointOwnership = field(default_factory=EndpointOwnership)
    
    # Visibility
    visibility: EndpointVisibility = field(default_factory=lambda: EndpointVisibility(scope=VisibilityScope.RUNTIME))
    
    # Authority
    authority: EndpointAuthorityRecord = field(default_factory=EndpointAuthorityRecord)
    
    # Policy
    policy: EndpointPolicy = field(default_factory=EndpointPolicy)
    
    # Context
    runtime_id: str = ""
    component_id: Optional[str] = None
    
    # Metadata (free-form, for extensibility)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_runtime(cls, runtime_id: str) -> "EndpointDescriptor":
        """Create a runtime-level endpoint descriptor."""
        return cls(
            endpoint_id=f"runtime_{runtime_id}",
            endpoint_type=EndpointType.RUNTIME,
            name=f"Runtime-{runtime_id}",
            ownership=EndpointOwnership(
                owner_type=EndpointOwnershipType.RUNTIME,
                owner_id=runtime_id,
            ),
            visibility=EndpointVisibility(scope=VisibilityScope.GLOBAL),
            authority=EndpointAuthorityRecord(
                communication_authority=EndpointAuthority.FULL,
                special_authorities=frozenset([EndpointAuthority.BROADCAST]),
            ),
        )
    
    @classmethod
    def create_component(
        cls,
        runtime_id: str,
        component_id: str,
        name: Optional[str] = None,
    ) -> "EndpointDescriptor":
        """Create a component-level endpoint descriptor."""
        return cls(
            endpoint_id=f"comp_{component_id}",
            endpoint_type=EndpointType.COMPONENT,
            name=name or f"Component-{component_id}",
            runtime_id=runtime_id,
            component_id=component_id,
            ownership=EndpointOwnership(
                owner_type=EndpointOwnershipType.COMPONENT,
                owner_id=component_id,
            ),
            visibility=EndpointVisibility(scope=VisibilityScope.RUNTIME),
        )
    
    @classmethod
    def create_service(
        cls,
        runtime_id: str,
        service_id: str,
        name: Optional[str] = None,
    ) -> "EndpointDescriptor":
        """Create a service-level endpoint descriptor."""
        return cls(
            endpoint_id=f"svc_{service_id}",
            endpoint_type=EndpointType.SERVICE,
            name=name or f"Service-{service_id}",
            runtime_id=runtime_id,
            ownership=EndpointOwnership(
                owner_type=EndpointOwnershipType.SERVICE,
                owner_id=service_id,
            ),
            visibility=EndpointVisibility(scope=VisibilityScope.SERVICE),
            authority=EndpointAuthorityRecord(
                communication_authority=EndpointAuthority.FULL,
            ),
        )
    
    @classmethod
    def create_capability(
        cls,
        runtime_id: str,
        capability_id: str,
        name: Optional[str] = None,
    ) -> "EndpointDescriptor":
        """Create a capability-level endpoint descriptor."""
        return cls(
            endpoint_id=f"cap_{capability_id}",
            endpoint_type=EndpointType.CAPABILITY,
            name=name or f"Capability-{capability_id}",
            runtime_id=runtime_id,
            ownership=EndpointOwnership(
                owner_type=EndpointOwnershipType.CAPABILITY,
                owner_id=capability_id,
            ),
            visibility=EndpointVisibility(scope=VisibilityScope.RUNTIME),
        )
    
    @classmethod
    def create_stream(cls, stream_id: str, runtime_id: str) -> "EndpointDescriptor":
        """Create a stream endpoint descriptor."""
        return cls(
            endpoint_id=f"str_{stream_id}",
            endpoint_type=EndpointType.STREAM,
            name=f"Stream-{stream_id}",
            runtime_id=runtime_id,
            ownership=EndpointOwnership(
                owner_type=EndpointOwnershipType.SYSTEM,
                owner_id="system",
            ),
            visibility=EndpointVisibility(scope=VisibilityScope.RUNTIME),
        )
    
    @classmethod
    def create_external(cls, external_id: str) -> "EndpointDescriptor":
        """Create an external endpoint descriptor."""
        return cls(
            endpoint_id=f"ext_{external_id}",
            endpoint_type=EndpointType.EXTERNAL,
            name=f"External-{external_id}",
            ownership=EndpointOwnership(
                owner_type=EndpointOwnershipType.EXTERNAL,
                owner_id=external_id,
            ),
            visibility=EndpointVisibility(scope=VisibilityScope.RUNTIME),
            authority=EndpointAuthorityRecord(
                communication_authority=EndpointAuthority.SEND_ONLY,
            ),
        )
    
    def can_communicate_with(self, target_endpoint: "EndpointDescriptor") -> bool:
        """
        Check if this endpoint can communicate with the target.
        
        Rules:
            1. Sender visibility must include receiver
            2. Receiver authority must allow receiving
            3. No disallowed recipient list matches
        """
        # Check if receiver is in allowed list (if not empty = unrestricted)
        if self.visibility.allowed_recipients and target_endpoint.endpoint_id not in self.visibility.allowed_recipients:
            return False
        
        # Check if receiver is in disallowed list
        if target_endpoint.endpoint_id in self.visibility.disallowed_recipients:
            return False
        
        # Check sender has send authority
        if self.authority.communication_authority not in (
            EndpointAuthority.FULL,
            EndpointAuthority.SEND_ONLY,
        ):
            return False
        
        # Check receiver accepts messages (has receive authority)
        if target_endpoint.authority.communication_authority not in (
            EndpointAuthority.FULL,
            EndpointAuthority.READ_ONLY,
        ):
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert endpoint descriptor to dictionary for serialization."""
        return {
            "endpoint_id": self.endpoint_id,
            "endpoint_type": self.endpoint_type.value,
            "name": self.name,
            "runtime_id": self.runtime_id,
            "component_id": self.component_id,
        }


# =============================================================================
# ENDPOINT REGISTRY
# =============================================================================

@dataclass(slots=True)
class EndpointRegistry:
    """
    Registry for endpoint descriptors.
    
    This is a runtime-level registry of all endpoints.
    
    Note: This class is mutable (for registry operations) but contains
    immutable descriptors. Use with caution in concurrent contexts.
    """
    
    _endpoints: Dict[str, EndpointDescriptor] = field(default_factory=dict)
    _lock: Optional[Any] = None  # Will be lazily initialized
    
    def _get_lock(self):
        """Lazy initialization of lock for thread safety."""
        if self._lock is None:
            import threading
            self._lock = threading.RLock()
        return self._lock
    
    def register(self, endpoint: EndpointDescriptor) -> bool:
        """
        Register an endpoint descriptor.
        
        Args:
            endpoint: The endpoint to register
            
        Returns:
            True if registered successfully
            
        Raises:
            ValueError: If endpoint_id already exists
        """
        lock = self._get_lock()
        with lock:
            if endpoint.endpoint_id in self._endpoints:
                raise ValueError(
                    f"Endpoint {endpoint.endpoint_id} already registered"
                )
            self._endpoints[endpoint.endpoint_id] = endpoint
            return True
    
    def unregister(self, endpoint_id: str) -> bool:
        """Unregister an endpoint by ID."""
        lock = self._get_lock()
        with lock:
            if endpoint_id in self._endpoints:
                del self._endpoints[endpoint_id]
                return True
            return False
    
    def get_endpoint(self, endpoint_id: str) -> Optional[EndpointDescriptor]:
        """Get an endpoint descriptor by ID."""
        return self._endpoints.get(endpoint_id)
    
    def get_endpoints_by_type(self, endpoint_type: EndpointType) -> Tuple[EndpointDescriptor, ...]:
        """Get all endpoints of a specific type."""
        lock = self._get_lock()
        with lock:
            return tuple(
                ep for ep in self._endpoints.values()
                if ep.endpoint_type == endpoint_type
            )
    
    def get_endpoints_by_component(self, component_id: str) -> Tuple[EndpointDescriptor, ...]:
        """Get all endpoints belonging to a specific component."""
        lock = self._get_lock()
        with lock:
            return tuple(
                ep for ep in self._endpoints.values()
                if ep.component_id == component_id
            )
    
    def get_all_endpoints(self) -> Tuple[EndpointDescriptor, ...]:
        """Get all registered endpoints."""
        lock = self._get_lock()
        with lock:
            return tuple(self._endpoints.values())
    
    def count_by_type(self) -> Dict[str, int]:
        """Count endpoints by type."""
        lock = self._get_lock()
        with lock:
            counts: Dict[str, int] = {}
            for ep in self._endpoints.values():
                ep_type = ep.endpoint_type.value
                counts[ep_type] = counts.get(ep_type, 0) + 1
            return counts


# =============================================================================
# ENDPOINT ROUTING KEY
# =============================================================================

@dataclass(frozen=True)
class EndpointRoutingKey:
    """
    Immutable routing key for endpoint addressing.
    
    Used for determining where messages should be routed.
    
    Args:
        runtime_id: Runtime where message should be delivered
        endpoint_type: Type of target endpoint
        endpoint_id: Specific endpoint ID (if known)
        wildcard_pattern: Wildcard pattern for matching multiple endpoints
    """
    
    runtime_id: str
    endpoint_type: Optional[EndpointType] = None
    endpoint_id: Optional[str] = None
    wildcard_pattern: Optional[str] = None
    
    def matches(self, endpoint: EndpointDescriptor) -> bool:
        """Check if this routing key matches the given endpoint."""
        # Runtime must match
        if self.runtime_id and endpoint.runtime_id != self.runtime_id:
            return False
        
        # Type filter (if specified)
        if self.endpoint_type and endpoint.endpoint_type != self.endpoint_type:
            return False
        
        # Specific ID filter (if specified)
        if self.endpoint_id and endpoint.endpoint_id != self.endpoint_id:
            return False
        
        # Wildcard pattern matching
        if self.wildcard_pattern:
            import fnmatch
            name = endpoint.name or ""
            if not fnmatch.fnmatch(name, self.wildcard_pattern):
                return False
        
        return True


# =============================================================================
# ENDPOINT PROTOCOLS (for message bus integration)
# =============================================================================

class IEndpointSender:
    """
    Protocol for sending messages from an endpoint.
    
    This protocol is implemented by endpoints that can send messages.
    """
    
    @property
    def sender_id(self) -> str:
        """Get the unique ID of this sender."""
        ...
    
    async def send(
        self,
        target_endpoint: EndpointDescriptor,
        message_body: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send a message to another endpoint.
        
        Args:
            target_endpoint: The recipient endpoint descriptor
            message_body: The message content
            metadata: Optional additional metadata
            
        Returns:
            True if sent (delivery not guaranteed)
        """
        ...
    
    async def broadcast(
        self,
        message_body: Any,
        recipients_filter: Optional[Callable[[EndpointDescriptor], bool]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Broadcast a message to multiple endpoints.
        
        Args:
            message_body: The message content
            recipients_filter: Optional filter function for target selection
            metadata: Optional additional metadata
            
        Returns:
            Number of endpoints that received the message
        """
        ...


class IEndpointReceiver:
    """
    Protocol for receiving messages at an endpoint.
    
    This protocol is implemented by endpoints that can receive messages.
    """
    
    @property
    def receiver_id(self) -> str:
        """Get the unique ID of this receiver."""
        ...
    
    async def receive(
        self,
        message_body: Any,
        sender_endpoint: EndpointDescriptor,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Receive a message from another endpoint.
        
        Args:
            message_body: The received message content
            sender_endpoint: The sender's endpoint descriptor
            metadata: Additional metadata about the transmission
            
        Returns:
            True if message was processed successfully
        """
        ...


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Identity
    "EndpointId",
    
    # Ownership
    "EndpointOwnershipType",
    "EndpointOwnership",
    
    # Visibility
    "VisibilityScope",
    "EndpointVisibility",
    
    # Authority
    "EndpointAuthority",
    "EndpointAuthorityRecord",
    
    # Policy
    "DeliveryPolicy",
    "EndpointPolicy",
    
    # Types
    "EndpointType",
    
    # Descriptors
    "EndpointDescriptor",
    
    # Registry
    "EndpointRegistry",
    
    # Routing
    "EndpointRoutingKey",
    
    # Protocols
    "IEndpointSender",
    "IEndpointReceiver",
]