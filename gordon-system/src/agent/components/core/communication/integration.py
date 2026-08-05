# Core Communication Integration
# ==============================

"""
Integration between communication runtime and other Core systems.

This module provides hooks for:
- Lifecycle coordination (start/stop)
- Runtime assembly integration
- Signal propagation (cancellation, shutdown)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time


@dataclass(frozen=True)
class CommunicationLifecycleConfig:
    """Configuration for communication lifecycle integration."""
    
    startup_timeout_seconds: float = 5.0
    shutdown_drain_timeout_seconds: float = 30.0
    default_pending_request_timeout_seconds: float = 30.0
    max_dead_letter_capacity: int = 10000


class CommunicationLifecycleAdapter:
    """
    Adapter for integrating communication with Core lifecycle.
    
    Manages communication runtime during lifecycle transitions:
        CREATED -> INITIALIZING -> READY -> RUNNING -> STOPPING -> STOPPED
    
    During shutdown:
        1. Close admission (no new messages)
        2. Cancel pending requests
        3. Drain critical queues
        4. Stop workers
        5. Report unresolved communication
    """
    
    def __init__(
        self,
        transport: Any,  # LocalTransport or similar
        config: Optional[CommunicationLifecycleConfig] = None,
    ):
        self._transport = transport
        self._config = config or CommunicationLifecycleConfig()
        
        # State tracking
        self._state = "INIT"
        self._lock = __import__("threading").RLock()
        
        # Pending requests registry (for cleanup)
        self._pending_requests = None
    
    @property
    def state(self) -> str:
        """Get current lifecycle state."""
        with self._lock:
            return self._state
    
    async def initialize(self, runtime_id: str) -> None:
        """Initialize communication subsystem."""
        with self._lock:
            if self._state != "INIT":
                raise RuntimeError(
                    f"Cannot initialize: already in {self._state}"
                )
            
            self._state = "INITIALIZING"
        
        # Initialize transport
        try:
            # Create pending requests registry for cleanup tracking
            from .requests import PendingRequestRegistry
            
            self._pending_requests = PendingRequestRegistry(
                max_pending=10000,
                default_timeout_seconds=self._config.default_pending_request_timeout_seconds,
            )
            
            with self._lock:
                self._state = "READY"
                
        except Exception as e:
            with self._lock:
                self._state = "FAILED"
            raise
    
    async def start(self) -> None:
        """Start communication subsystem."""
        with self._lock:
            if self._state != "READY":
                raise RuntimeError(
                    f"Cannot start: not ready (current: {self._state})"
                )
            
            self._state = "RUNNING"
        
        # Start transport
        try:
            self._transport.start()
            
        except Exception as e:
            with self._lock:
                self._state = "FAILED"
            raise
    
    async def stop(self) -> None:
        """
        Stop communication subsystem gracefully.
        
        Shutdown sequence:
            1. Mark as stopping (reject new messages)
            2. Cancel pending requests
            3. Drain critical queues
            4. Stop workers
            5. Report unresolved
        """
        with self._lock:
            if self._state != "RUNNING":
                return  # Idempotent
            
            self._state = "STOPPING"
        
        try:
            # Cancel pending requests (with timeout)
            if self._pending_requests:
                expired = self._pending_requests.cleanup_expired()
                
                # Report any unresolved
                remaining = self._pending_requests.get_pending_count()
                if remaining > 0:
                    pass  # Log or report unresolved communication
            
            # Stop transport
            self._transport.stop()
            
        finally:
            with self._lock:
                self._state = "STOPPED"
    
    async def shutdown(self) -> None:
        """Force shutdown (non-graceful)."""
        # Just call stop for now
        await self.stop()
    
    def is_running(self) -> bool:
        """Check if communication is running."""
        with self._lock:
            return self._state == "RUNNING"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get integrated statistics from all subsystems."""
        transport_stats = self._transport.get_statistics()
        
        with self._lock:
            state = self._state
        
        return {
            **transport_stats,
            "lifecycle_state": state,
            "timestamp_utc": time.time(),
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall communication health."""
        transport_stats = self._transport.get_statistics()
        
        with self._lock:
            state = self._state
        
        # Determine health based on state and stats
        if state != "RUNNING":
            return {
                "status": "unhealthy",
                "reason": f"Lifecycle state: {state}",
            }
        
        # Check transport health
        queue_size = transport_stats.get("queue_size", 0)
        max_queue_size = self._config.shutdown_drain_timeout_seconds * 100
        
        if queue_size >= max_queue_size:
            return {
                "status": "degraded",
                "reason": f"Queue saturation: {queue_size}/{max_queue_size}",
            }
        
        return {
            "status": "healthy",
            **transport_stats,
        }


class SignalPropagationAdapter:
    """
    Adapter for propagating signals through communication.
    
    Converts cancellation/shutdown signals into communication events
    that can be handled by registered handlers.
    """
    
    def __init__(
        self,
        transport: Any,  # LocalTransport
        lifecycle_adapter: CommunicationLifecycleAdapter,
    ):
        self._transport = transport
        self._lifecycle = lifecycle_adapter
    
    async def propagate_cancellation(
        self,
        target_type: str,
        target_id: str,
        reason: Optional[str] = None,
    ) -> int:
        """
        Propagate cancellation signal via communication.
        
        Args:
            target_type: Type of target (e.g., "task", "handler")
            target_id: ID of the target
            reason: Reason for cancellation
            
        Returns:
            Number of handlers that received the signal
        """
        if not self._lifecycle.is_running():
            return 0
        
        # Create cancellation message
        from .local import DeliveryMode, DeliveryResult
        
        message = {
            "type": "signal.cancellation",
            "target_type": target_type,
            "target_id": target_id,
            "reason": reason or "",
            "timestamp_utc": time.time(),
        }
        
        result = self._transport.send(message)
        
        return 1 if result.success else 0
    
    async def propagate_shutdown(
        self,
        scope: str,
        reason: Optional[str] = None,
    ) -> int:
        """
        Propagate shutdown signal via communication.
        
        Args:
            scope: Shutdown scope (e.g., "runtime", "component")
            reason: Reason for shutdown
            
        Returns:
            Number of handlers that received the signal
        """
        if not self._lifecycle.is_running():
            return 0
        
        from .local import DeliveryMode, DeliveryResult
        
        message = {
            "type": "signal.shutdown",
            "scope": scope,
            "reason": reason or "",
            "timestamp_utc": time.time(),
        }
        
        result = self._transport.send(message)
        
        return 1 if result.success else 0


__all__ = [
    # Lifecycle
    "CommunicationLifecycleConfig",
    "CommunicationLifecycleAdapter",
    
    # Signal propagation
    "SignalPropagationAdapter",
]