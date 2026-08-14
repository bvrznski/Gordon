# Gordon Core - Cross-Runtime Communication (Phase 3.21.12)
# ===========================================================
#
# Canonical contracts for distributed execution communication
#
# Defines contracts for runtime-to-runtime messaging, cluster communication,
# remote services, federation, and gateway protocols.

"""
Canonical Cross-Runtime Communication for Gordon Phase 3.21.12

CROSS-RUNTIME ARCHITECTURE:
---------------------------
Runtime-to-Runtime: Direct messaging between separate runtimes
Cluster Communication: Multiple runtimes acting as a coordinated cluster
Remote Services: Calling services in remote runtime contexts
Federation: Distributed coordination across multiple systems
Gateway Communication: Protocol translation between different environments
Distributed Events: Event propagation across runtime boundaries

RUNTIME ADDRESSING:
-------------------
- RuntimeAddress: Unique identifier for a runtime instance
- ClusterIdentity: Identity of a cluster of runtimes
- RemoteEndpoint: Reference to endpoint in remote runtime
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple
from enum import Enum, auto
import time
import uuid


# =============================================================================
# RUNTIME ADDRESS
# =============================================================================

@dataclass(frozen=True)
class RuntimeAddress:
    """
    Immutable address for a remote runtime.
    
    Args:
        runtime_id: Unique identifier of the target runtime
        cluster_id: Optional cluster containing this runtime
        region: Geographic or logical region
        network_address: Network location (IP/hostname + port)
    """
    
    runtime_id: str
    cluster_id: Optional[str] = None
    region: str = "local"
    network_address: str = "localhost:0"


# =============================================================================
# CLUSTER IDENTITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class ClusterIdentity:
    """
    Immutable identity for a runtime cluster.
    
    Args:
        cluster_id: Unique identifier for the cluster
        leader_runtime_id: Current leader/runtime coordinator
        member_runtimes: All runtimes in the cluster
        creation_timestamp_utc: When cluster was formed
    """
    
    cluster_id: str
    leader_runtime_id: Optional[str] = None
    member_runtimes: Tuple[str, ...] = field(default_factory=tuple)
    creation_timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# FEDERATION MESSAGE
# =============================================================================

class FederationMessageKind(Enum):
    """
    Canonical federation message types.
    """
    
    # Discovery messages
    DISCOVER_PEERS = "discover_peers"
    PEER_ADVERTISED = "peer_advertised"
    LEADER_ELECT = "leader_elect"
    LEADER_DECLARED = "leader_declared"
    
    # Synchronization messages
    STATE_SYNC_REQUEST = "state_sync_request"
    STATE_SYNC_RESPONSE = "state_sync_response"
    HEARTBEAT = "heartbeat"
    
    # Event messages
    DISTRIBUTED_EVENT = "distributed_event"
    EVENT_ACKNOWLEDGEMENT = "event_acknowledgement"


@dataclass(frozen=True, slots=True)
class FederationMessage:
    """
    Immutable message for federation communication.
    
    Args:
        message_kind: Type of federation message
        correlation_id: For linking related messages
        source_runtime_id: Where this originated
        target_runtimes: Intended recipients
        
        # Content
        payload: Message-specific data
        
        # Timing
        timestamp_utc: When created
        expiry_utc: When it expires
    """
    
    message_kind: FederationMessageKind
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    source_runtime_id: str = ""
    target_runtimes: Tuple[str, ...] = field(default_factory=tuple)
    
    payload: Dict[str, Any] = field(default_factory=dict)
    
    timestamp_utc: float = field(default_factory=time.time)
    expiry_utc: Optional[float] = None


# =============================================================================
# GATEWAY PROTOCOL
# =============================================================================

class GatewayProtocol(Enum):
    """
    Canonical gateway protocol types.
    """
    
    REST_HTTP = "rest_http"           # HTTP/REST over network
    GRPC = "grpc"                     # gRPC for high-performance
    WEBSOCKET = "websocket"           # WebSockets for streaming
    MQTT = "mqtt"                     # MQTT for IoT scenarios


@dataclass(frozen=True)
class GatewayProtocolConfig:
    """
    Immutable gateway protocol configuration.
    
    Args:
        protocol: The protocol to use
        endpoint_url: Gateway endpoint URL
        authentication_type: Type of auth (none, api_key, oauth, etc.)
        timeout_seconds: Request timeout
        retry_policy: Retry configuration
    """
    
    protocol: GatewayProtocol = GatewayProtocol.GRPC
    endpoint_url: str = ""
    authentication_type: str = "none"
    timeout_seconds: float = 30.0
    retry_policy: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# REMOTE ENDPOINT REFERENCE
# =============================================================================

@dataclass(frozen=True)
class RemoteEndpointReference:
    """
    Immutable reference to an endpoint in a remote runtime.
    
    Args:
        runtime_address: Address of the remote runtime
        endpoint_id: ID of the endpoint within that runtime
        endpoint_type: Type of the endpoint
        protocol_config: How to connect to it
    """
    
    runtime_address: RuntimeAddress
    endpoint_id: str
    endpoint_type: str = "unknown"
    protocol_config: GatewayProtocolConfig = field(
        default_factory=GatewayProtocolConfig
    )
    
    def __str__(self) -> str:
        return f"{self.endpoint_id}@{self.runtime_address.runtime_id}"


# =============================================================================
# REMOTE MESSAGE
# =============================================================================

@dataclass(frozen=True, slots=True)
class RemoteMessage:
    """
    Immutable message for remote delivery.
    
    Args:
        local_message: The original message being sent
        remote_endpoint: Where it should be delivered
        protocol: How to transport it
        timestamp_utc: When prepared for remote delivery
        
        # Reliability
        expected_response: Whether response is expected
        correlation_chain: For distributed tracing
    """
    
    local_message: Dict[str, Any]
    remote_endpoint: RemoteEndpointReference
    
    protocol: GatewayProtocol = GatewayProtocol.GRPC
    timestamp_utc: float = field(default_factory=time.time)
    
    expected_response: bool = False
    correlation_chain: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# DISTRIBUTED TRACING CONTEXT
# =============================================================================

@dataclass(frozen=True, slots=True)
class DistributedTraceContext:
    """
    Immutable context for distributed tracing across runtime boundaries.
    
    Args:
        trace_id: Global trace identifier
        span_id: Current operation span
        parent_span_id: Parent operation span
        
        # Propagation
        is_remote: Whether this context came from remote
        sampled: Whether this trace should be recorded
        
        # Timestamps (for latency calculation)
        start_timestamp_utc: When trace began
    """
    
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    
    is_remote: bool = False
    sampled: bool = True
    
    start_timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# CLUSTER STATE
# =============================================================================

@dataclass(slots=True)
class ClusterState:
    """
    Mutable state for cluster membership and coordination.
    
    Tracks active members, leader, and health status.
    """
    
    _cluster_id: str = ""
    _leader_runtime_id: Optional[str] = None
    _member_runtimes: Dict[str, Tuple[float, bool]] = field(
        default_factory=dict
    )  # runtime_id -> (last_heartbeat_utc, is_healthy)
    
    def register_member(self, runtime_id: str) -> None:
        """Register a new cluster member."""
        self._member_runtimes[runtime_id] = (time.time(), True)
    
    def unregister_member(self, runtime_id: str) -> bool:
        """Remove a member from the cluster."""
        if runtime_id in self._member_runtimes:
            del self._member_runtimes[runtime_id]
            return True
        return False
    
    def update_heartbeat(self, runtime_id: str) -> None:
        """Update heartbeat timestamp for a member."""
        if runtime_id in self._member_runtimes:
            current = self._member_runtimes[runtime_id]
            self._member_runtimes[runtime_id] = (time.time(), current[1])
    
    def mark_healthy(self, runtime_id: str) -> None:
        """Mark a member as healthy."""
        if runtime_id in self._member_runtimes:
            current = self._member_runtimes[runtime_id]
            self._member_runtimes[runtime_id] = (current[0], True)
    
    def mark_unhealthy(self, runtime_id: str) -> None:
        """Mark a member as unhealthy."""
        if runtime_id in self._member_runtimes:
            current = self._member_runtimes[runtime_id]
            self._member_runtimes[runtime_id] = (current[0], False)
    
    def get_healthy_members(self) -> Tuple[str, ...]:
        """Get list of healthy member runtime IDs."""
        return tuple(
            rid for rid, (_, healthy) in self._member_runtimes.items()
            if healthy
        )
    
    def is_leader(self, runtime_id: str) -> bool:
        """Check if a runtime is the current leader."""
        return self._leader_runtime_id == runtime_id


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Runtime addressing
    "RuntimeAddress",
    
    # Cluster identity
    "ClusterIdentity",
    
    # Federation messages
    "FederationMessageKind",
    "FederationMessage",
    
    # Gateway protocols
    "GatewayProtocol",
    "GatewayProtocolConfig",
    
    # Remote endpoints
    "RemoteEndpointReference",
    "RemoteMessage",
    
    # Distributed tracing
    "DistributedTraceContext",
    
    # Cluster state
    "ClusterState",
]