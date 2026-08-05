# Core Federation System
# ======================
"""
Core runtime entity federation and coordination.

Provides:
- Multi-runtime entity discovery and communication
- Cross-runtime dependencies
- Federated state synchronization

Phase 3.7: Runtime third-stage expansion - Federation subsystem.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import time


# =============================================================================
# Runtime Identity
# =============================================================================

@dataclass(frozen=True)
class RuntimeIdentity:
    """
    Unique identifier for a runtime instance in a federation.
    
    Usage:
        identity = RuntimeIdentity(
            cluster_id="prod-cluster",
            runtime_id=runtime_uuid,
            role="primary"
        )
        
        # Check equality
        if identity == other_identity:
            pass
    """
    
    cluster_id: str  # Cluster or environment identifier
    
    runtime_id: str  # Unique runtime instance ID
    
    role: str = "standalone"  # primary, secondary, observer, etc.
    
    @property
    def is_primary(self) -> bool:
        """Check if this runtime has primary role."""
        return self.role in ("primary", "leader")
    
    @property
    def is_secondary(self) -> bool:
        """Check if this runtime has secondary role."""
        return self.role == "secondary"
    
    @property
    def is_observer(self) -> bool:
        """Check if this runtime is observer-only."""
        return self.role == "observer"
    
    def to_string(self) -> str:
        """Return string representation."""
        return f"{self.cluster_id}/{self.runtime_id}@{self.role}"
    
    @classmethod
    def from_string(cls, s: str) -> "RuntimeIdentity":
        """Parse RuntimeIdentity from string."""
        parts = s.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid runtime identity format: {s}")
        
        cluster_id = parts[0]
        rest = parts[1].split("@")
        
        if len(rest) == 2:
            return cls(
                cluster_id=cluster_id,
                runtime_id=rest[0],
                role=rest[1]
            )
        
        return cls(cluster_id=cluster_id, runtime_id=rest[0])
    
    def __str__(self) -> str:
        return self.to_string()


# =============================================================================
# Federated Entity
# =============================================================================

class FederationStatus(Enum):
    """
    Status of an entity in a federated context.
    
    - LOCAL: Entity exists only in local runtime
    - FEDERATED: Entity synchronized across runtimes
    - REMOTE: Entity exists in remote runtime
    - HYBRID: Entity has components in multiple runtimes
    """
    
    LOCAL = "local"
    FEDERATED = "federated"
    REMOTE = "remote"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class FederatedEntity:
    """
    An entity that may exist across federated runtimes.
    
    Usage:
        fed_entity = FederatedEntity(
            local_id=entity_id,
            global_id=federation_id,
            status=FederationStatus.FEDERATED
        )
        
        # Access remote copies if available
        remote_copy = fed_entity.get_remote_copy(runtime_id)
    """
    
    local_id: str  # Local identifier
    
    global_id: str  # Federation-wide unique ID
    
    status: FederationStatus = FederationStatus.LOCAL
    
    # Runtime locations
    local_runtime: Optional[RuntimeIdentity] = None
    remote_runtimes: List[RuntimeIdentity] = field(default_factory=list)
    
    # Synchronization state
    last_sync_at: Optional[float] = None
    sync_version: int = 0
    
    @property
    def is_federated(self) -> bool:
        """Check if entity exists across multiple runtimes."""
        return self.status in (FederationStatus.FEDERATED, FederationStatus.HYBRID)
    
    @property
    def has_remote_copies(self) -> bool:
        """Check if entity has remote runtime copies."""
        return len(self.remote_runtimes) > 0
    
    def add_remote_runtime(self, runtime: RuntimeIdentity) -> "FederatedEntity":
        """Return copy with added remote runtime."""
        new_remotes = list(self.remote_runtimes)
        if runtime not in new_remotes:
            new_remotes.append(runtime)
        
        return FederatedEntity(
            local_id=self.local_id,
            global_id=self.global_id,
            status=(
                FederationStatus.HYBRID
                if self.status == FederationStatus.LOCAL else
                FederationStatus.FEDERATED
            ),
            local_runtime=self.local_runtime,
            remote_runtimes=new_remotes,
            last_sync_at=time.time() if new_remotes else self.last_sync_at,
            sync_version=self.sync_version + 1
        )
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "local_id": self.local_id,
            "global_id": self.global_id,
            "status": self.status.value if hasattr(self.status, 'value') else str(self.status),
            "local_runtime": str(self.local_runtime) if self.local_runtime else None,
            "remote_count": len(self.remote_runtimes)
        }


# =============================================================================
# Federation Connection
# =============================================================================

@dataclass(frozen=True)
class FederationConnection:
    """
    Connection between federated runtimes.
    
    Usage:
        connection = FederationConnection(
            local_runtime=local_identity,
            remote_runtime=remote_identity,
            latency_ms=10.5
        )
        
        # Check if connection is healthy
        if connection.is_healthy:
            send_federated_message(connection)
    """
    
    local_runtime: RuntimeIdentity
    remote_runtime: RuntimeIdentity
    
    created_at: float = field(default_factory=time.time)
    
    last_ping_at: Optional[float] = None
    latency_ms: float = 0.0
    
    message_count: int = 0
    error_count: int = 0
    
    @property
    def is_healthy(self) -> bool:
        """Check if connection appears healthy."""
        # Consider unhealthy if too many errors or no recent ping
        return self.error_count < 10 and (
            self.last_ping_at is None or
            time.time() - self.last_ping_at < 300.0  # 5 minute threshold
        )
    
    def record_message(self, success: bool = True) -> "FederationConnection":
        """Return copy with updated message count."""
        return FederationConnection(
            local_runtime=self.local_runtime,
            remote_runtime=self.remote_runtime,
            created_at=self.created_at,
            last_ping_at=time.time() if success else self.last_ping_at,
            latency_ms=(
                (self.latency_ms + time.time() - self.created_at) / 2
                if success else self.latency_ms
            ),
            message_count=self.message_count + 1,
            error_count=self.error_count + (0 if success else 1)
        )


# =============================================================================
# Federation Manager
# =============================================================================

class FederationManager:
    """
    Manages federated runtime connections and entities.
    
    Provides:
        - Runtime discovery and connection management
        - Entity federation across runtimes
        - State synchronization coordination
    
    Usage:
        manager = FederationManager(local_runtime_id)
        
        # Add remote runtime connection
        manager.add_remote_runtime(remote_identity, endpoint="http://...")
        
        # Federate an entity
        fed_entity = manager.federate_entity(
            local_entity_id,
            target_runtimes=[remote1, remote2]
        )
        
        # Get all federated entities
        entities = manager.get_federated_entities()
    """
    
    def __init__(self, local_runtime_id: str) -> None:
        self.local_identity = RuntimeIdentity(
            cluster_id="local",
            runtime_id=local_runtime_id,
            role="primary"
        )
        
        self._runtimes: Dict[str, RuntimeIdentity] = {}
        self._connections: Dict[str, FederationConnection] = {}
        self._entities: Dict[str, FederatedEntity] = {}
        self._lock = __import__("threading").Lock()
    
    def add_remote_runtime(
        self,
        runtime_identity: RuntimeIdentity,
        endpoint: Optional[str] = None
    ) -> None:
        """Register a remote runtime."""
        with self._lock:
            self._runtimes[runtime_identity.runtime_id] = runtime_identity
            
            # Create connection record
            self._connections[runtime_identity.runtime_id] = FederationConnection(
                local_runtime=self.local_identity,
                remote_runtime=runtime_identity
            )
    
    def federate_entity(
        self,
        local_entity_id: str,
        target_runtimes: Optional[List[str]] = None,
        global_id: Optional[str] = None
    ) -> FederatedEntity:
        """
        Federate an entity to other runtimes.
        
        Args:
            local_entity_id: Local entity identifier
            target_runtimes: List of runtime IDs to federate to (all if None)
            global_id: Federation-wide unique ID
            
        Returns:
            The created FederatedEntity
        """
        import uuid
        
        with self._lock:
            fed_id = global_id or f"fed_{uuid.uuid4().hex[:8]}"
            
            # Determine target runtimes
            targets = (
                list(self._runtimes.keys()) if target_runtimes is None
                else [rt for rt in target_runtimes if rt in self._runtimes]
            )
            
            remote_runtimes = [
                self._runtimes[rt_id] for rt_id in targets
            ]
            
            entity = FederatedEntity(
                local_id=local_entity_id,
                global_id=fed_id,
                status=FederationStatus.FEDERATED if remote_runtimes else FederationStatus.LOCAL,
                local_runtime=self.local_identity,
                remote_runtimes=remote_runtimes,
                sync_version=1
            )
            
            self._entities[fed_id] = entity
            
            return entity
    
    def get_federated_entity(self, global_id: str) -> Optional[FederatedEntity]:
        """Get a federated entity by its global ID."""
        with self._lock:
            return self._entities.get(global_id)
    
    def get_local_entities(self) -> Dict[str, FederatedEntity]:
        """
        Get all entities local to this runtime.
        
        Returns dict of local_id -> FederatedEntity
        """
        with self._lock:
            return {
                e.local_id: e for e in self._entities.values()
                if e.status in (FederationStatus.LOCAL, FederationStatus.HYBRID)
            }
    
    def get_federated_entities(self) -> List[FederatedEntity]:
        """Get all federated entities."""
        with self._lock:
            return [
                e for e in self._entities.values()
                if e.status in (FederationStatus.FEDERATED, FederationStatus.HYBRID)
            ]
    
    def update_connection(
        self,
        runtime_id: str,
        success: bool = True
    ) -> None:
        """Update connection state after message exchange."""
        with self._lock:
            if runtime_id in self._connections:
                conn = self._connections[runtime_id]
                self._connections[runtime_id] = conn.record_message(success)
    
    def get_connection(self, runtime_id: str) -> Optional[FederationConnection]:
        """Get connection to a remote runtime."""
        with self._lock:
            return self._connections.get(runtime_id)
    
    @property
    def remote_runtime_count(self) -> int:
        """Return number of registered remote runtimes."""
        with self._lock:
            return len(self._runtimes)
    
    @property
    def federated_entity_count(self) -> int:
        """Return number of federated entities."""
        with self._lock:
            return len([e for e in self._entities.values() if e.is_federated])


__all__ = [
    # Runtime identity
    "RuntimeIdentity",
    
    # Federation status
    "FederationStatus",
    
    # Entities and connections
    "FederatedEntity",
    "FederationConnection",
    
    # Manager
    "FederationManager",
]