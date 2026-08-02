# Core Synchronization Primitives
# ================================
#
# NOTE: Cancellation types are provided by the execution module.
# This module provides concurrency primitives only.

"""
Core runtime synchronization and concurrency primitives.

Provides:
- Async-compatible locks and semaphores
- One-time execution guards
- Bounded resource access
- Guarded concurrent resource access

Cancellation tokens and sources are in the `execution` module to provide
single-authority semantics for cancellation.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, TypeVar, Generic
from contextlib import asynccontextmanager


T = TypeVar("T")


@dataclass(frozen=True)
class ShutdownSignal:
    """
    Signal for graceful shutdown coordination.
    
    Usage:
        signal = ShutdownSignal()
        
        # Check if shutdown requested
        if signal.is_shutdown_requested:
            await self.stop_gracefully()
        
        # Request shutdown
        signal.request_shutdown()
    """
    
    _shutdown_requested: bool = False
    
    @property
    def is_shutdown_requested(self) -> bool:
        """Check if shutdown has been requested."""
        import threading
        lock = threading.Lock()
        with lock:
            return self._shutdown_requested
    
    def request_shutdown(self) -> None:
        """Request graceful shutdown."""
        import threading
        lock = threading.Lock()
        with lock:
            self._shutdown_requested = True


class AsyncLock:
    """
    Async-compatible lock wrapper.
    
    Provides async/await semantics for synchronization.
    
    Usage:
        lock = AsyncLock()
        
        async with lock:
            # Critical section
            pass
    """
    
    def __init__(self) -> None:
        self._lock: Any = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Acquire the lock."""
        await self._lock.acquire()
        return True
    
    def release(self) -> None:
        """Release the lock."""
        try:
            self._lock.release()
        except RuntimeError:
            pass  # Lock was already released
    
    @asynccontextmanager
    async def __aenter__(self):
        await self._lock.acquire()
        try:
            yield
        finally:
            self._lock.release()
    
    def __enter__(self):
        raise RuntimeError("AsyncLock must be used with 'async with', not 'with'")
    
    def __exit__(self, *args):
        raise RuntimeError("AsyncLock must be used with 'async with', not 'with'")


class OnceGuard:
    """
    Guard to ensure an operation runs only once.
    
    Usage:
        once = OnceGuard()
        
        async with once.run():
            # This code runs exactly once
            pass
        
        # Subsequent calls will raise AlreadyStartedError
    """
    
    def __init__(self) -> None:
        self._started: bool = False
        self._lock: Any = asyncio.Lock()
    
    async def is_started(self) -> bool:
        """Check if operation has been started."""
        async with self._lock:
            return self._started
    
    @asynccontextmanager
    async def run(self):
        """
        Context manager ensuring single execution.
        
        Raises:
            RuntimeError: If called more than once
        """
        async with self._lock:
            if self._started:
                raise RuntimeError("OnceGuard operation already started")
            self._started = True
        
        try:
            yield
        finally:
            pass
    
    def reset(self) -> None:
        """Reset the guard to allow another execution."""
        import threading
        lock = threading.Lock()
        with lock:
            self._started = False


class BoundedSemaphore:
    """
    Async semaphore with bounded count.
    
    Usage:
        sem = BoundedSemaphore(3)
        
        async with sem:
            # Up to 3 concurrent entries
            pass
    """
    
    def __init__(self, max_count: int) -> None:
        if max_count <= 0:
            raise ValueError("max_count must be positive")
        self._max_count = max_count
        self._semaphore: Any = asyncio.Semaphore(max_count)
    
    @property
    def max_count(self) -> int:
        """Return the maximum count."""
        return self._max_count
    
    async def acquire(self) -> bool:
        """Acquire a semaphore slot."""
        await self._semaphore.acquire()
        return True
    
    def release(self) -> None:
        """Release a semaphore slot."""
        try:
            self._semaphore.release()
        except ValueError:
            pass  # Already at max count
    
    @asynccontextmanager
    async def __aenter__(self):
        await self._semaphore.acquire()
        try:
            yield
        finally:
            self._semaphore.release()
    
    def __enter__(self):
        raise RuntimeError("BoundedSemaphore must be used with 'async with', not 'with'")


class GuardedResource(Generic[T]):
    """
    Resource protected by a lock for safe concurrent access.
    
    Usage:
        resource = GuardedResource(initial_value=0)
        
        async with resource.access() as value:
            # Read and modify atomically
            return value + 1
    """
    
    def __init__(self, initial: T) -> None:
        self._value = initial
        self._lock: Any = asyncio.Lock()
    
    @property
    def lock(self) -> AsyncLock:
        """Return the underlying lock."""
        return AsyncLock()
    
    @asynccontextmanager
    async def access(self) -> Any:
        """
        Access resource with exclusive lock.
        
        Yields:
            The current value (for read-only use)
        """
        async with self._lock:
            yield self._value
    
    async def update(
        self,
        updater: Callable[[T], T]
    ) -> T:
        """
        Atomically update the resource value.
        
        Args:
            updater: Function that transforms current value to new value
            
        Returns:
            New value after update
        """
        async with self._lock:
            self._value = updater(self._value)
            return self._value
    
    async def get(self) -> T:
        """Get the current resource value."""
        async with self._lock:
            return self._value


__all__ = [
    # Shutdown signal (not duplicated - unique to this module)
    "ShutdownSignal",
    # Concurrency primitives
    "AsyncLock",
    "OnceGuard",
    "BoundedSemaphore",
    "GuardedResource",
]