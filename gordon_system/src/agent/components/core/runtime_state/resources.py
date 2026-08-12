# Core Resource Scope Abstraction
# ================================

"""
Runtime-scoped resource management.

Provides:
- Runtime-scoped resource tracking
- Explicit ownership
- Deterministic release
- Reverse-order cleanup where appropriate
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Any,
    Callable,
    Iterator,
)
from enum import Enum
import threading
import time


class ResourceState(Enum):
    """Resource state values."""
    ACQUIRED = "acquired"
    RELEASED = "released"
    FAILED_ACQUISITION = "failed_acquisition"
    FAILED_RELEASE = "failed_release"


@dataclass(frozen=True)
class ResourceHandle:
    """
    Handle for a runtime-scoped resource.
    
    Provides explicit ownership and tracking without exposing
    the actual resource (which remains owned by its original source).
    """
    
    resource_id: str  # Unique identifier
    owner_id: str  # ID of scope that owns this
    acquired_at: float = field(default_factory=time.monotonic)
    
    def is_active(self) -> bool:
        """Check if this handle represents an active resource."""
        return True  # Handles are never "inactive" - just tracking references


class ResourceAcquisition:
    """
    Record of a single resource acquisition.
    
    Used internally to track ownership and order.
    """
    
    def __init__(
        self,
        resource_id: str,
        owner_id: str,
        acquire_fn: Optional[Callable[[], Any]] = None,
        release_fn: Optional[Callable[[Any], None]] = None
    ) -> None:
        self.resource_id = resource_id
        self.owner_id = owner_id
        self.acquire_fn = acquire_fn
        self.release_fn = release_fn
        self.acquired_at = time.monotonic()
        self.state = ResourceState.ACQUIRED
        self.value: Optional[Any] = None
    
    def try_acquire(self) -> bool:
        """Try to acquire the resource."""
        if self.acquire_fn is not None and self.state == ResourceState.ACQUIRED:
            try:
                self.value = self.acquire_fn()
                return True
            except Exception:
                self.state = ResourceState.FAILED_ACQUISITION
                return False
        return False
    
    def try_release(self) -> bool:
        """Try to release the resource."""
        if self.release_fn is not None and self.value is not None:
            try:
                self.release_fn(self.value)
                self.state = ResourceState.RELEASED
                return True
            except Exception:
                self.state = ResourceState.FAILED_RELEASE
                return False
        self.state = ResourceState.RELEASED
        return True


class ResourceScope:
    """
    Runtime-scoped resource container.
    
    Provides:
    - Explicit ownership of runtime resources
    - Deterministic release order (reverse acquisition)
    - No duplicate release
    - Failure reporting
    
    Usage:
        # Create a scope
        scope = ResourceScope(scope_id="my_runtime")
        
        # Acquire resources with callbacks
        def acquire_db() -> DatabaseConnection:
            return db.connect()
        
        def release_db(conn: DatabaseConnection) -> None:
            conn.close()
        
        handle = scope.acquire(
            "database",
            acquire_fn=acquire_db,
            release_fn=release_db
        )
        
        # Scope cleanup releases all resources in reverse order
    """
    
    def __init__(self, scope_id: Optional[str] = None) -> None:
        self._lock = threading.Lock()
        self._scope_id = scope_id or f"resource_scope_{id(self)}"
        self._acquisitions: Dict[str, ResourceAcquisition] = {}
        self._order: List[str] = []  # Track acquisition order
    
    @property
    def scope_id(self) -> str:
        """Get the scope identifier."""
        return self._scope_id
    
    @property
    def active_count(self) -> int:
        """Get number of active (acquired) resources."""
        with self._lock:
            return len([a for a in self._acquisitions.values() if a.state == ResourceState.ACQUIRED])
    
    @property
    def is_empty(self) -> bool:
        """Check if scope has no tracked resources."""
        with self._lock:
            return len(self._acquisitions) == 0
    
    def acquire(
        self,
        resource_id: str,
        acquire_fn: Optional[Callable[[], Any]] = None,
        release_fn: Optional[Callable[[Any], None]] = None
    ) -> ResourceHandle:
        """
        Register a resource for tracking.
        
        Args:
            resource_id: Unique identifier for this resource
            acquire_fn: Optional callable to actually acquire the resource
            release_fn: Optional callable to release the resource
            
        Returns:
            A handle to track this resource
            
        Raises:
            ValueError: If resource_id already exists in scope
        """
        with self._lock:
            if resource_id in self._acquisitions:
                raise ValueError(f"Resource '{resource_id}' already acquired in scope")
            
            acquisition = ResourceAcquisition(
                resource_id=resource_id,
                owner_id=self._scope_id,
                acquire_fn=acquire_fn,
                release_fn=release_fn
            )
            
            # Try to acquire immediately if callback provided
            if acquisition.acquire_fn is not None:
                acquisition.try_acquire()
            
            self._acquisitions[resource_id] = acquisition
            self._order.append(resource_id)
            
            return ResourceHandle(
                resource_id=resource_id,
                owner_id=self._scope_id
            )
    
    def release(self, resource_id: str) -> bool:
        """
        Release a specific resource.
        
        Args:
            resource_id: The resource to release
            
        Returns:
            True if released successfully or already released
            
        Raises:
            KeyError: If resource not found in scope
        """
        with self._lock:
            if resource_id not in self._acquisitions:
                raise KeyError(f"Resource '{resource_id}' not in scope")
            
            acquisition = self._acquisitions[resource_id]
            return acquisition.try_release()
    
    def release_all(self) -> Dict[str, bool]:
        """
        Release all resources in reverse order.
        
        Returns:
            Mapping of resource_id -> success flag
        """
        results: Dict[str, bool] = {}
        
        with self._lock:
            # Reverse order for cleanup
            for resource_id in reversed(self._order):
                if resource_id in self._acquisitions:
                    acquisition = self._acquisitions[resource_id]
                    results[resource_id] = acquisition.try_release()
            
            return results
    
    def get_handle(self, resource_id: str) -> Optional[ResourceHandle]:
        """Get a handle for a tracked resource."""
        with self._lock:
            if resource_id in self._acquisitions:
                return ResourceHandle(
                    resource_id=resource_id,
                    owner_id=self._scope_id
                )
            return None
    
    def get_status(self, resource_id: str) -> Optional[ResourceState]:
        """Get the state of a tracked resource."""
        with self._lock:
            if resource_id in self._acquisitions:
                return self._acquisitions[resource_id].state
            return None
    
    def get_all_resources(self) -> Dict[str, ResourceHandle]:
        """Get all tracked resources as handles."""
        with self._lock:
            return {
                rid: ResourceHandle(resource_id=rid, owner_id=self._scope_id)
                for rid in self._order
            }
    
    def clear(self) -> None:
        """Clear all resources without releasing (use with caution)."""
        with self._lock:
            self._acquisitions.clear()
            self._order.clear()
    
    def __contains__(self, resource_id: str) -> bool:
        """Check if a resource is tracked in this scope."""
        with self._lock:
            return resource_id in self._acquisitions
    
    def __len__(self) -> int:
        """Return number of tracked resources."""
        with self._lock:
            return len(self._order)
    
    def __iter__(self) -> Iterator[str]:
        """Iterate over tracked resource IDs in acquisition order."""
        with self._lock:
            yield from list(self._order)


class ScopedResourceOwner:
    """
    Mixin for objects that own resources within a runtime scope.
    
    Provides automatic resource cleanup when the owner is shut down.
    """
    
    def __init__(self, scope_id: Optional[str] = None) -> None:
        self._resource_scope = ResourceScope(scope_id=scope_id)
    
    @property
    def resource_scope(self) -> ResourceScope:
        """Get the owned resource scope."""
        return self._resource_scope
    
    def acquire_resource(
        self,
        resource_id: str,
        acquire_fn: Optional[Callable[[], Any]] = None,
        release_fn: Optional[Callable[[Any], None]] = None
    ) -> ResourceHandle:
        """
        Acquire a resource within this owner's scope.
        
        Args:
            resource_id: Unique identifier for the resource
            acquire_fn: Callable to acquire the resource
            release_fn: Callable to release the resource
            
        Returns:
            A handle to track the resource
        """
        return self._resource_scope.acquire(
            resource_id=resource_id,
            acquire_fn=acquire_fn,
            release_fn=release_fn
        )
    
    def release_all_resources(self) -> Dict[str, bool]:
        """Release all resources in this owner's scope."""
        return self._resource_scope.release_all()


__all__ = [
    "ResourceState",
    "ResourceHandle",
    "ResourceAcquisition",
    "ResourceScope",
    "ScopedResourceOwner",
]