# Provider Lifecycle Integration - Kernel Adapter
# ================================================
"""
Provider lifecycle integration with Gordon's runtime infrastructure.

This module provides adapters to integrate providers with:
- Kernel lifecycle management
- State store registration
- Health monitoring

Key Design Decisions:
- Providers use the existing kernel lifecycle mechanisms
- Registration happens through the kernel's state store
- No separate provider lifecycle authority exists
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import asyncio

from .types import ProviderStatus, CapabilityDeclaration
from .exceptions import ProviderNotReadyError


@dataclass(frozen=True)
class ProviderLifecycleState:
    """
    Lifecycle state for a provider tracked by the runtime.
    
    This is distinct from ProviderStatus which tracks operational readiness.
    """
    initialized: bool = False
    started: bool = False
    ready_for_requests: bool = False
    
    @property
    def is_running(self) -> bool:
        """Check if provider is fully running."""
        return self.started and self.ready_for_requests


class ProviderLifecycleAdapter:
    """
    Adapter that integrates a provider with the kernel's lifecycle system.
    
    Usage:
        # Create adapter for a provider
        adapter = ProviderLifecycleAdapter(
            provider=my_llm_provider,
            health_check_interval=60.0
        )
        
        # Use with kernel
        await kernel.register_service("llm", adapter)
    """
    
    def __init__(
        self,
        provider_id: str,
        kind: str,
        capabilities: CapabilityDeclaration,
        status_callback=None,  # Optional callback for status updates
    ):
        """
        Initialize the lifecycle adapter.
        
        Args:
            provider_id: The provider's unique identifier
            kind: Provider kind (LLM, VLM, etc.)
            capabilities: Declared capabilities of this provider
            status_callback: Optional async function to call on status changes
        """
        self.provider_id = provider_id
        self.kind = kind
        self.capabilities = capabilities
        self._status_callback = status_callback
        
        # Internal state
        self._state = ProviderLifecycleState()
        self._lock = asyncio.Lock()
    
    @property
    def service_id(self) -> str:
        """Return the service ID for kernel registration."""
        return f"provider/{self.provider_id}"
    
    async def initialize(self) -> None:
        """
        Initialize the provider.
        
        Called by the kernel during startup sequence.
        """
        async with self._lock:
            if self._state.initialized:
                return
            
            # Transition to initializing
            await self._update_status(ProviderStatus.INITIALIZING)
            
            # In a real implementation, this would:
            # - Load configuration
            # - Create connections
            # - Initialize resources
            
            # Mark as initialized and ready for startup
            self._state.initialized = True
            self._state.started = False
            await self._update_status(ProviderStatus.READY)
    
    async def start(self) -> None:
        """
        Start the provider.
        
        Called by the kernel during startup sequence after all initializations.
        """
        async with self._lock:
            if not self._state.initialized:
                raise ProviderNotReadyError(
                    message=f"Provider '{self.provider_id}' must be initialized first",
                    provider_id=self.provider_id,
                    operation="start"
                )
            
            if self._state.started:
                return  # Already started
            
            await self._update_status(ProviderStatus.STARTING)
            
            # In a real implementation, this would:
            # - Start connections
            # - Begin accepting requests
            
            self._state.started = True
            self._state.ready_for_requests = True
            await self._update_status(ProviderStatus.RUNNING)
    
    async def stop(self) -> None:
        """
        Stop the provider gracefully.
        
        Called by the kernel during shutdown sequence.
        """
        async with self._lock:
            if not self._state.started:
                return  # Not started yet
            
            await self._update_status(ProviderStatus.STOPPING)
            
            # In a real implementation, this would:
            # - Wait for in-flight requests to complete
            # - Close connections gracefully
            
            self._state.ready_for_requests = False
            self._state.started = False
            await self._update_status(ProviderStatus.STOPPED)
    
    async def shutdown(self) -> None:
        """
        Force shutdown the provider.
        
        Called by the kernel during forced termination or error recovery.
        """
        async with self._lock:
            # In a real implementation, this would:
            # - Kill any remaining processes
            # - Release all resources immediately
            
            self._state.ready_for_requests = False
            self._state.started = False
            await self._update_status(ProviderStatus.FAILED)
    
    async def _update_status(self, new_status: ProviderStatus) -> None:
        """Update the provider's status and notify listeners."""
        # Store current state (in real implementation, this would be stored)
        
        # Notify callback if configured
        if self._status_callback is not None:
            try:
                await self._status_callback(self.provider_id, new_status)
            except Exception:
                pass  # Don't let callback failures affect lifecycle
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the provider.
        
        Returns:
            Health status dictionary with ready flag
        """
        async with self._lock:
            if not self._state.ready_for_requests:
                return {
                    "status": "unhealthy",
                    "ready": False,
                    "reason": "Provider is not ready for requests"
                }
            
            # In a real implementation, this would:
            # - Ping the provider endpoint
            # - Check resource availability
            # - Verify model is loaded
            
            return {
                "status": "healthy",
                "ready": True,
                "provider_id": self.provider_id,
                "kind": self.kind
            }
    
    @property
    def is_healthy(self) -> bool:
        """Check if provider is healthy."""
        # Simplified - in real implementation would check actual status
        return self._state.ready_for_requests
    
    async def get_health_report(self) -> Dict[str, Any]:
        """
        Get full health report for this provider.
        
        Returns:
            Complete health report including metadata
        """
        current_status = ProviderStatus.RUNNING if self._state.ready_for_requests else ProviderStatus.STOPPED
        
        return {
            "provider_id": self.provider_id,
            "kind": self.kind,
            "capabilities": {
                "chat_completion": self.capabilities.supports_chat_completion,
                "text_generation": self.capabilities.supports_text_generation,
                "embeddings": self.capabilities.supports_embeddings,
                "vision": self.capabilities.supports_vision,
                "streaming": self.capabilities.supports_streaming,
            },
            "status": current_status.value,
            "ready": self._state.ready_for_requests,
            "initialized": self._state.initialized,
            "started": self._state.started,
        }


__all__ = [
    "ProviderLifecycleState",
    "ProviderLifecycleAdapter",
]