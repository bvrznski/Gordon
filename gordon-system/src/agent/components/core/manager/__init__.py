# Core Manager Infrastructure
# ==========================
"""
Core runtime entity manager.

Provides:
- Entity collection and lifecycle management
- Resource pool management
- Dependency coordination
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, TypeVar, Generic, Callable
from enum import Enum
import time

T = TypeVar("T")


# =============================================================================
# Manager Status
# =============================================================================

class ManagerStatus(Enum):
    """
    Manager operational status.
    
    States:
        - PENDING: Created but not initialized
        - INITIALIZING: Setting up resources
        - READY: Ready to manage entities
        - RUNNING: Actively managing
        - STOPPING: Graceful shutdown in progress
        - STOPPED: Fully shut down
    """
    
    PENDING = "pending"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"


# =============================================================================
# Entity Management
# =============================================================================

@dataclass(frozen=True)
class ManagedEntity:
    """
    An entity managed by the manager.
    
    Contains lifecycle and state information.
    """
    
    entity_id: str
    entity_type: str  # e.g., "service", "task", "component"
    
    # Lifecycle
    status: ManagerStatus = ManagerStatus.PENDING
    created_at: float = field(default_factory=time.time)
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Dependencies (entity IDs this depends on)
    dependencies: List[str] = field(default_factory=list)
    
    @property
    def is_ready(self) -> bool:
        """Check if entity is ready for use."""
        return self.status == ManagerStatus.READY
    
    @property
    def is_active(self) -> bool:
        """Check if entity is actively managed."""
        return self.status in (ManagerStatus.RUNNING, ManagerStatus.READY)


class EntityCollection(Generic[T]):
    """
    Collection of managed entities.
    
    Provides:
        - Entity registration and lookup
        - Type-based filtering
        - Status management
    
    Usage:
        collection = EntityCollection[MyService]()
        
        service = MyService(id="svc_1")
        collection.add(service)
        
        # Get by ID
        retrieved = collection.get("svc_1")
        
        # Filter by status
        active = list(collection.filter_by_status(ManagerStatus.RUNNING))
    """
    
    def __init__(self) -> None:
        self._entities: Dict[str, ManagedEntity] = {}
        self._instances: Dict[str, Any] = {}  # entity_id -> instance
        self._lock = __import__("threading").Lock()
    
    @property
    def size(self) -> int:
        """Return number of managed entities."""
        with self._lock:
            return len(self._entities)
    
    def add(
        self,
        entity: T,
        entity_id: Optional[str] = None,
        entity_type: str = "unknown"
    ) -> ManagedEntity:
        """
        Add an entity to the collection.
        
        Args:
            entity: The entity instance
            entity_id: Unique identifier (auto-generated if not provided)
            entity_type: Type classification
            
        Returns:
            ManagedEntity record
        """
        import uuid
        
        with self._lock:
            eid = entity_id or f"entity_{uuid.uuid4().hex[:8]}"
            
            managed = ManagedEntity(
                entity_id=eid,
                entity_type=entity_type
            )
            
            self._entities[eid] = managed
            self._instances[eid] = entity
            
            return managed
    
    def get(self, entity_id: str) -> Optional[T]:
        """Get entity instance by ID."""
        with self._lock:
            return self._instances.get(entity_id)
    
    def remove(self, entity_id: str) -> bool:
        """Remove an entity from the collection."""
        with self._lock:
            if entity_id in self._entities:
                del self._entities[entity_id]
                del self._instances[entity_id]
                return True
            return False
    
    def get_all(self) -> List[T]:
        """Get all managed instances."""
        with self._lock:
            return list(self._instances.values())
    
    def filter_by_type(self, entity_type: str) -> List[T]:
        """Filter entities by type."""
        with self._lock:
            return [
                inst for eid, inst in self._instances.items()
                if self._entities.get(eid, ManagedEntity("", "")).entity_type == entity_type
            ]
    
    def filter_by_status(self, status: ManagerStatus) -> List[T]:
        """Filter entities by status."""
        with self._lock:
            return [
                inst for eid, inst in self._instances.items()
                if self._entities.get(eid, ManagedEntity("", "")).status == status
            ]
    
    def update_status(
        self,
        entity_id: str,
        new_status: ManagerStatus
    ) -> bool:
        """Update entity status."""
        with self._lock:
            if entity_id in self._entities:
                # Update the copy
                old = self._entities[entity_id]
                self._entities[entity_id] = ManagedEntity(
                    entity_id=old.entity_id,
                    entity_type=old.entity_type,
                    status=new_status,
                    created_at=old.created_at,
                    config=dict(old.config),
                    dependencies=list(old.dependencies)
                )
                return True
            return False
    
    def get_managed(self, entity_id: str) -> Optional[ManagedEntity]:
        """Get ManagedEntity record."""
        with self._lock:
            return self._entities.get(entity_id)


# =============================================================================
# Resource Pool
# =============================================================================

@dataclass(frozen=True)
class ResourcePoolConfig:
    """
    Configuration for a resource pool.
    
    Defines limits and behavior for pooled resources.
    """
    
    max_resources: int = 10
    min_resources: int = 1
    timeout_seconds: float = 30.0
    
    can_expand: bool = True
    expansion_step: int = 2


class ResourcePool:
    """
    Managed pool of reusable resources.
    
    Provides:
        - Resource acquisition and release
        - Pool resizing based on demand
        - Timeout for operations
    
    Usage:
        config = ResourcePoolConfig(max_resources=5)
        pool = ResourcePool(config)
        
        async with pool.acquire() as resource:
            # Use the resource
            pass
    """
    
    def __init__(self, config: Optional[ResourcePoolConfig] = None) -> None:
        self._config = config or ResourcePoolConfig()
        self._available: List[Any] = []
        self._in_use: Dict[str, Any] = {}
        self._lock = __import__("threading").Lock()
    
    @property
    def available_count(self) -> int:
        """Return count of available resources."""
        with self._lock:
            return len(self._available)
    
    @property
    def in_use_count(self) -> int:
        """Return count of in-use resources."""
        with self._lock:
            return len(self._in_use)
    
    @property
    def total_count(self) -> int:
        """Return total resource count (available + in use)."""
        with self._lock:
            return len(self._available) + len(self._in_use)
    
    async def acquire(
        self,
        resource_id: Optional[str] = None
    ) -> "ResourceAcquisition":
        """
        Acquire a resource from the pool.
        
        Args:
            resource_id: Optional custom ID for tracking
            
        Returns:
            Acquisition context manager
        """
        import asyncio
        
        async def do_acquire():
            with self._lock:
                if self._available:
                    # Reuse existing resource
                    return self._available.pop(0)
                
                # Create new if under limit
                if self.total_count < self._config.max_resources:
                    return self._create_resource()
                
                raise ResourcePoolExhausted(
                    f"Pool exhausted: {self.total_count}/{self._config.max_resources} in use"
                )
        
        resource = await do_acquire()
        
        rid = resource_id or f"res_{time.monotonic_ns()}"
        
        with self._lock:
            self._in_use[rid] = resource
        
        return ResourceAcquisition(self, rid)
    
    async def release(
        self,
        resource_id: str
    ) -> bool:
        """Release a resource back to the pool."""
        with self._lock:
            if resource_id in self._in_use:
                resource = self._in_use.pop(resource_id)
                # Reset and return to available pool
                await self._reset_resource(resource)
                self._available.append(resource)
                return True
            return False
    
    async def _create_resource(self) -> Any:
        """Create a new resource (override in subclasses)."""
        return {}
    
    async def _reset_resource(self, resource: Any) -> None:
        """Reset a resource for reuse (override in subclasses)."""
        pass
    
    def clear(self) -> None:
        """Clear all resources."""
        with self._lock:
            self._available.clear()
            self._in_use.clear()


class ResourceAcquisition:
    """Resource acquisition context manager."""
    
    def __init__(self, pool: ResourcePool, resource_id: str):
        self._pool = pool
        self._resource_id = resource_id
    
    async def __aenter__(self) -> Any:
        return self._pool.get_resource(self._resource_id)
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._pool.release(self._resource_id)


class ResourcePoolExhausted(Exception):
    """Raised when resource pool is exhausted."""
    pass


# =============================================================================
# Dependency Manager
# =============================================================================

@dataclass(frozen=True)
class DependencyEdge:
    """
    A dependency relationship between entities.
    
    entity_a depends on entity_b
    """
    
    from_entity: str  # Dependent
    to_entity: str    # Required


class DependencyGraph:
    """
    Manages dependencies between managed entities.
    
    Provides:
        - Dependency registration and lookup
        - Cycle detection
        - Topological ordering
    
    Usage:
        graph = DependencyGraph()
        
        graph.add_dependency("task_2", "task_1")  # task_2 depends on task_1
        
        # Get dependencies for a task
        deps = graph.get_dependencies("task_2")
    """
    
    def __init__(self) -> None:
        self._edges: Dict[str, List[str]] = {}  # entity -> [dependents]
        self._reverse: Dict[str, List[str]] = {}  # entity -> [dependencies]
        self._lock = __import__("threading").Lock()
    
    def add_dependency(self, from_entity: str, to_entity: str) -> None:
        """
        Add a dependency relationship.
        
        Args:
            from_entity: The dependent entity
            to_entity: The required entity
        """
        with self._lock:
            if from_entity not in self._edges:
                self._edges[from_entity] = []
            if to_entity not in self._reverse:
                self._reverse[to_entity] = []
            
            self._edges[from_entity].append(to_entity)
            self._reverse[to_entity].append(from_entity)
    
    def remove_dependency(self, from_entity: str, to_entity: str) -> bool:
        """Remove a dependency relationship."""
        with self._lock:
            if from_entity in self._edges and to_entity in self._edges[from_entity]:
                self._edges[from_entity].remove(to_entity)
                if to_entity in self._reverse:
                    self._reverse[to_entity].remove(from_entity)
                return True
            return False
    
    def get_dependencies(self, entity: str) -> List[str]:
        """Get entities that the given entity depends on."""
        with self._lock:
            return list(self._edges.get(entity, []))
    
    def get_dependents(self, entity: str) -> List[str]:
        """Get entities that depend on the given entity."""
        with self._lock:
            return list(self._reverse.get(entity, []))
    
    def has_cycle(self) -> bool:
        """
        Check if the dependency graph contains a cycle.
        
        Uses DFS to detect cycles.
        """
        visited = set()
        rec_stack = set()
        
        all_nodes = set(self._edges.keys()) | set(self._reverse.keys())
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self._edges.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in all_nodes:
            if node not in visited:
                if dfs(node):
                    return True
        
        return False
    
    def topological_order(self) -> List[str]:
        """
        Get entities in topological order (dependencies first).
        
        Raises:
            ValueError: If graph has a cycle
        """
        if self.has_cycle():
            raise ValueError("Cannot compute topological order with cycles")
        
        # Kahn's algorithm
        in_degree: Dict[str, int] = {}
        all_nodes = set(self._edges.keys()) | set(self._reverse.keys())
        
        for node in all_nodes:
            in_degree[node] = len(self._edges.get(node, []))
        
        # Start with nodes that have no dependencies (in_degree == 0)
        queue = [node for node in all_nodes if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # For each node that depends on this one
            for dependent in self._reverse.get(node, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        return result


# =============================================================================
# Manager Protocol
# =============================================================================

class EntityManagerProtocol(Generic[T]):
    """
    Protocol for entity managers.
    
    Usage:
        class MyManager(EntityManagerProtocol[MyEntity]):
            async def register(self, entity: T) -> str:
                pass
            
            async def get(self, entity_id: str) -> Optional[T]:
                pass
        
        manager = MyManager()
    """
    
    @property
    def status(self) -> ManagerStatus:
        """Return manager status."""
        raise NotImplementedError
    
    async def register(self, entity: T) -> ManagedEntity:
        """Register an entity with the manager."""
        raise NotImplementedError
    
    async def deregister(self, entity_id: str) -> bool:
        """Remove an entity from management."""
        raise NotImplementedError
    
    async def get(self, entity_id: str) -> Optional[T]:
        """Get a managed entity by ID."""
        raise NotImplementedError
    
    async def shutdown(self, timeout_seconds: float = 30.0) -> List[str]:
        """
        Initiate graceful shutdown.
        
        Returns list of deregistered entity IDs.
        """
        raise NotImplementedError


# =============================================================================
# Default Manager Implementation
# =============================================================================

class SimpleEntityManager:
    """
    Simple entity manager implementation.
    
    Provides basic entity registration, lookup, and lifecycle management.
    
    Usage:
        manager = SimpleEntityManager()
        
        entity = MyService(id="svc_1")
        managed = await manager.register(entity)
        
        retrieved = await manager.get("svc_1")
        
        cancelled = await manager.shutdown()
    """
    
    def __init__(self) -> None:
        self._status = ManagerStatus.PENDING
        self._collection: EntityCollection[Any] = EntityCollection()
        self._dependency_graph: DependencyGraph = DependencyGraph()
        self._lock = __import__("threading").Lock()
    
    @property
    def status(self) -> ManagerStatus:
        return self._status
    
    async def register(
        self,
        entity: Any,
        entity_type: str = "unknown"
    ) -> ManagedEntity:
        """Register an entity."""
        with self._lock:
            if self._status != ManagerStatus.RUNNING:
                raise ManagerNotReadyError("Manager is not running")
        
        managed = self._collection.add(entity, entity_type=entity_type)
        
        # Update status
        with self._lock:
            self._collection.update_status(managed.entity_id, ManagerStatus.READY)
        
        return managed
    
    async def deregister(self, entity_id: str) -> bool:
        """Remove an entity."""
        # Update status first
        with self._lock:
            if not self._collection.update_status(entity_id, ManagerStatus.STOPPING):
                return False
        
        result = self._collection.remove(entity_id)
        
        if result:
            with self._lock:
                self._dependency_graph.remove_dependency(entity_id, "")
        
        return True
    
    async def get(self, entity_id: str) -> Optional[Any]:
        """Get an entity by ID."""
        return self._collection.get(entity_id)
    
    async def shutdown(self, timeout_seconds: float = 30.0) -> List[str]:
        """Initiate graceful shutdown."""
        with self._lock:
            # Mark all entities as stopping
            for entity_id in list(self._collection._entities.keys()):
                self._collection.update_status(entity_id, ManagerStatus.STOPPING)
            
            self._status = ManagerStatus.STOPPED
        
        return list(self._collection._entities.keys())
    
    async def add_dependency(
        self,
        dependent_id: str,
        required_id: str
    ) -> None:
        """Add a dependency between entities."""
        with self._lock:
            if not self._collection.get(dependent_id):
                raise ManagerError(f"Unknown entity: {dependent_id}")
            if not self._collection.get(required_id):
                raise ManagerError(f"Unknown entity: {required_id}")
            
            self._dependency_graph.add_dependency(dependent_id, required_id)
    
    def get_dependencies(self, entity_id: str) -> List[str]:
        """Get dependencies for an entity."""
        return self._dependency_graph.get_dependencies(entity_id)


# =============================================================================
# Exception Types
# =============================================================================

class ManagerError(Exception):
    """Base exception for manager errors."""
    pass


class ManagerNotReadyError(ManagerError):
    """Raised when manager is not ready."""
    
    def __init__(self, message: str = "Manager is not ready"):
        super().__init__(message)


__all__ = [
    # Status
    "ManagerStatus",
    
    # Entity management
    "ManagedEntity",
    "EntityCollection",
    
    # Resource pool
    "ResourcePoolConfig",
    "ResourcePool",
    "ResourceAcquisition",
    "ResourcePoolExhausted",
    
    # Dependency management
    "DependencyEdge",
    "DependencyGraph",
    
    # Protocol
    "EntityManagerProtocol",
    
    # Implementation
    "SimpleEntityManager",
    
    # Exceptions
    "ManagerError",
    "ManagerNotReadyError",
]