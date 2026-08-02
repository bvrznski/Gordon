# Core Runtime Assembly
# =====================

"""
Core runtime assembly and entry contract.

Provides:
- Runtime builder pattern for deterministic construction
- Runtime instance with startup/shutdown lifecycle
- Async context manager support
- Build validation
"""

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, TypeVar, Generic

from ..types import EntityId, Timestamp
from ..exceptions import ConfigurationError, StartupError


T = TypeVar("T")


@dataclass(frozen=True)
class BuildResult:
    """
    Result of runtime build.
    
    Args:
        success: Whether the build succeeded
        errors: List of validation/build errors
        warnings: List of non-blocking warnings
    """
    
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class StartupResult:
    """
    Result of runtime startup.
    
    Args:
        success: Whether startup succeeded
        services_started: List of successfully started service IDs
        failed_services: List of failed service info
        partial_success: Whether some services started before failure
    """
    
    success: bool
    services_started: List[str] = field(default_factory=list)
    failed_services: Dict[str, str] = field(default_factory=dict)  # service_id -> error
    partial_success: bool = False


@dataclass(frozen=True)
class ShutdownResult:
    """
    Result of runtime shutdown.
    
    Args:
        success: Whether shutdown succeeded
        services_stopped: List of successfully stopped service IDs
        failed_services: List of failed service info
    """
    
    success: bool
    services_stopped: List[str] = field(default_factory=list)
    failed_services: Dict[str, str] = field(default_factory=dict)


class RuntimeBuilder:
    """
    Builder for constructing runtime instances deterministically.
    
    Provides:
    - Step-by-step assembly
    - Validation before building
    - Configurable options
    
    Usage:
        builder = RuntimeBuilder()
        runtime = await builder.build()
    """
    
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {}
        self._services: List[Any] = []
        self._registries: Dict[str, Any] = {}
        self._validated = False
    
    @classmethod
    def create(cls) -> "RuntimeBuilder":
        """Create a new builder instance."""
        return cls()
    
    def set_config(self, key: str, value: Any) -> "RuntimeBuilder":
        """Set configuration value."""
        self._config[key] = value
        return self
    
    def add_service(self, service: Any) -> "RuntimeBuilder":
        """Add a service to the runtime."""
        self._services.append(service)
        return self
    
    def add_registry(self, name: str, registry: Any) -> "RuntimeBuilder":
        """Add a registry to the runtime."""
        self._registries[name] = registry
        return self
    
    async def validate(self) -> BuildResult:
        """
        Validate the build configuration.
        
        Returns:
            BuildResult with validation status
        """
        errors: List[str] = []
        
        # Check required config
        if not self._config.get("kernel_name"):
            errors.append("Missing required config: kernel_name")
        
        return BuildResult(
            success=len(errors) == 0,
            errors=errors
        )
    
    async def build(self) -> "RuntimeInstance":
        """
        Build and return a runtime instance.
        
        Returns:
            A configured RuntimeInstance ready for startup
            
        Raises:
            ConfigurationError: If validation fails
        """
        validation = await self.validate()
        
        if not validation.success:
            raise ConfigurationError(
                "Runtime build failed validation",
                config_key="runtime.build"
            )
        
        return RuntimeInstance(
            config=self._config,
            services=list(self._services),
            registries=dict(self._registries)
        )


class RuntimeInstance:
    """
    Core runtime instance with full lifecycle management.
    
    Usage as context manager:
        async with RuntimeBuilder().build() as runtime:
            # Runtime is running
            pass
        # Runtime has stopped
    
    Usage manually:
        runtime = await builder.build()
        await runtime.startup()
        try:
            # Use runtime
            pass
        finally:
            await runtime.shutdown()
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        services: List[Any],
        registries: Dict[str, Any]
    ) -> None:
        import uuid
        self._config = dict(config)
        self._services = list(services)
        self._registries = dict(registries)
        
        # State
        self._is_running = False
        self._started_services: List[str] = []
        self._stopped_services: List[str] = []
        self._start_time: Optional[float] = None
        self._stop_time: Optional[float] = None
        
        # Entities
        self._entity_id = EntityId(str(uuid.uuid4()))
    
    @property
    def entity_id(self) -> EntityId:
        """Get runtime instance ID."""
        return self._entity_id
    
    @property
    def is_running(self) -> bool:
        """Check if runtime is running."""
        return self._is_running
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get runtime configuration (read-only view)."""
        return dict(self._config)
    
    async def startup(self) -> StartupResult:
        """
        Start the runtime and all registered services.
        
        Returns:
            StartupResult with details of what started
            
        Raises:
            StartupError: If critical services fail to start
        """
        import asyncio
        
        if self._is_running:
            return StartupResult(success=True, services_started=self._started_services)
        
        errors: Dict[str, str] = {}
        partial_success = False
        
        # Start each service in order
        for i, service in enumerate(self._services):
            service_id = getattr(service, "service_id", f"service_{i}")
            
            try:
                if hasattr(service, "start") and asyncio.iscoroutinefunction(service.start):
                    await service.start()
                elif hasattr(service, "start"):
                    # Sync start - wrap in async
                    pass
                
                self._started_services.append(service_id)
                
            except Exception as e:
                errors[service_id] = str(e)
                partial_success = True
                
                if not self._config.get("allow_partial_startup", False):
                    # Rollback already started services
                    await self._rollback_startups()
                    raise StartupError(
                        f"Failed to start service '{service_id}'",
                        failed_component=service_id,
                        cause=e,
                        partial_success=partial_success
                    )
        
        self._is_running = True
        self._start_time = Timestamp.now().value
        
        return StartupResult(
            success=len(errors) == 0,
            services_started=self._started_services.copy(),
            failed_services=dict(errors),
            partial_success=partial_success and len(self._started_services) > 0
        )
    
    async def shutdown(self) -> ShutdownResult:
        """
        Stop the runtime and all services in reverse order.
        
        Returns:
            ShutdownResult with details of what stopped
        """
        import asyncio
        
        if not self._is_running:
            return ShutdownResult(success=True, services_stopped=self._stopped_services)
        
        errors: Dict[str, str] = {}
        
        # Stop services in reverse order
        for service_id in reversed(self._started_services):
            try:
                # Find the actual service object by ID
                service = self.get_service(service_id)
                
                if service is not None and hasattr(service, "stop"):
                    if asyncio.iscoroutinefunction(service.stop):
                        await service.stop()
                    else:
                        service.stop()
                
                self._stopped_services.append(str(service_id))
                
            except Exception as e:
                errors[str(service_id)] = str(e)
        
        self._is_running = False
        self._stop_time = Timestamp.now().value
        
        return ShutdownResult(
            success=len(errors) == 0,
            services_stopped=self._stopped_services.copy(),
            failed_services=dict(errors)
        )
    
    async def _rollback_startups(self) -> None:
        """Rollback all started services."""
        for service_id in reversed(self._started_services):
            try:
                # Stop the service
                if hasattr(service_id, "stop"):
                    await service_id.stop()
            except Exception:
                pass  # Ignore rollback errors
    
    async def __aenter__(self) -> "RuntimeInstance":
        """Async context manager entry."""
        result = await self.startup()
        
        if not result.success and not self._config.get("allow_partial_startup", False):
            raise StartupError(
                "Runtime startup failed",
                partial_success=result.partial_success
            )
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.shutdown()
    
    def get_service(self, service_id: str) -> Optional[Any]:
        """Get a registered service by ID."""
        for service in self._services:
            if hasattr(service, "service_id") and service.service_id == service_id:
                return service
        return None
    
    async def get_health_report(self) -> Dict[str, Any]:
        """Get runtime health status."""
        import time
        
        return {
            "entity_id": str(self.entity_id),
            "is_running": self._is_running,
            "services_started": len(self._started_services),
            "services_stopped": len(self._stopped_services),
            "uptime_seconds": (
                Timestamp.now().value - self._start_time
                if self._start_time else 0.0
            ),
            "config": {k: v for k, v in self._config.items() if not isinstance(v, (dict, list))}
        }


__all__ = [
    "BuildResult",
    "StartupResult",
    "ShutdownResult",
    "RuntimeBuilder",
    "RuntimeInstance",
]
