# Core Kernel - Control Plane
# ===========================

"""
Core runtime control plane.

The kernel coordinates runtime infrastructure without containing cognition
or capability semantics. It provides:

- Runtime identity ownership
- Runtime context coordination  
- Bootstrap orchestration
- Lifecycle management
- Dependency resolution
- Service startup/shutdown ordering
"""

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable

from ..types import EntityId, RuntimeId, Timestamp
from ..exceptions import StartupError, ShutdownError

# Phase 3.7.21: Data Governance integration
try:
    from ..data_governance import (
        DataGovernanceManager,
        InformationRecord,
        OwnerIdentity,
        ClassificationLevel,
        LifecycleState,
    )
except ImportError:
    # Data governance not available - set up stub types
    class DataGovernanceManager:
        pass
    
    InformationRecord = None
    OwnerIdentity = None
    ClassificationLevel = None
    LifecycleState = None

# Re-export builder components
from .builder import (
    ConstructionStage,
    ConstructionStatus,
    KernelConstructionId,
    ConstructionInputSnapshot,
    ConstructionStageRecord,
    KernelConstructionResult,
    KernelConstructionSnapshot,
    KernelConstructionReceipt,
    KernelBuilderState,
    KernelConstructionRequest,
    KernelConstructionContext,
    KernelBuilder,
    KernelConstructionPlan,
    dataclass_replace as _dataclass_replace,
)


@dataclass(frozen=True)
class KernelConfig:
    """
    Kernel configuration.
    
    Args:
        name: Kernel instance name
        version: Kernel version string
        allow_partial_startup: Whether to proceed with partial service startup
    """
    
    name: str = "core-kernel"
    version: str = "1.0.0"
    allow_partial_startup: bool = False


@dataclass(frozen=True)
class ServiceInfo:
    """Information about a registered service."""
    
    service_id: str
    name: str
    dependencies: List[str]
    startup_order: int
    shutdown_order: int


@dataclass()
class KernelState:
    """Kernel state representation."""
    
    is_running: bool = False
    services_started: int = 0
    services_stopped: int = 0
    start_time: Optional[float] = None
    stop_time: Optional[float] = None


@dataclass(frozen=True)
class KernelGovernanceConfig:
    """
    Kernel governance configuration.
    
    Args:
        data_governance_manager: Canonical DataGovernanceManager instance
        govern_all_information: Whether to automatically govern all information
        default_classification: Default classification level for new information
    """
    
    data_governance_manager: Optional[DataGovernanceManager] = None
    govern_all_information: bool = True
    default_classification: ClassificationLevel = ClassificationLevel.INTERNAL if hasattr(ClassificationLevel, 'INTERNAL') else None

class ServiceAdapter:
    """
    Adapter for integrating services with the kernel.
    
    Provides lifecycle hooks and dependency coordination.
    """
    
    def __init__(self, service_id: str, name: str) -> None:
        self.service_id = service_id
        self.name = name
        self._dependencies: List[str] = []
        self._startup_order = 1000
        self._shutdown_order = 1000
    
    def depends_on(self, *service_ids: str) -> "ServiceAdapter":
        """Declare dependencies on other services."""
        self._dependencies.extend(service_ids)
        return self
    
    def set_startup_order(self, order: int) -> "ServiceAdapter":
        """Set startup priority (lower = starts earlier)."""
        self._startup_order = order
        return self
    
    def set_shutdown_order(self, order: int) -> "ServiceAdapter":
        """Set shutdown priority (higher = stops later)."""
        self._shutdown_order = order
        return self
    
    def get_dependencies(self) -> List[str]:
        """Get service dependencies."""
        return list(self._dependencies)
    
    @property
    def startup_order(self) -> int:
        return self._startup_order
    
    @property
    def shutdown_order(self) -> int:
        return self._shutdown_order


class Kernel:
    """
    Core kernel - coordinates runtime infrastructure.
    
    The kernel:
    - Owns the runtime context
    - Coordinates bootstrap and shutdown sequences
    - Resolves dependencies between services
    - Exposes runtime health
    
    The kernel does NOT:
    - Contain cognition
    - Own capability semantics
    - Choose goals or plan actions
    - Interpret observations
    """
    
    def __init__(
        self,
        config: Optional[KernelConfig] = None,
        governance_config: Optional[KernelGovernanceConfig] = None,
    ) -> None:
        import uuid
        self._config = config or KernelConfig()
        self._entity_id = EntityId(str(uuid.uuid4()))
        
        # Service management
        self._services: Dict[str, ServiceAdapter] = {}
        self._service_instances: Dict[str, Any] = {}
        
        # Phase 3.7.21: Governance integration
        self._governance_config = governance_config or KernelGovernanceConfig()
        self._data_governance_mgr: Optional[DataGovernanceManager] = None
        
        if self._governance_config.data_governance_manager is not None:
            self._data_governance_mgr = self._governance_config.data_governance_manager
        elif self._governance_config.govern_all_information:
            # Create default governance manager
            try:
                from ..data_governance import DataGovernanceManager
                self._data_governance_mgr = DataGovernanceManager()
            except ImportError:
                pass
        
        # State
        self._state = KernelState()
        self._lock = asyncio.Lock()
    
    @property
    def entity_id(self) -> EntityId:
        """Get kernel's unique identifier."""
        return self._entity_id
    
    @property
    def name(self) -> str:
        """Get kernel name."""
        return self._config.name
    
    @property
    def version(self) -> str:
        """Get kernel version."""
        return self._config.version
    
    @property
    def is_running(self) -> bool:
        """Check if kernel is running."""
        return self._state.is_running
    
    async def register_service(
        self,
        service_id: str,
        adapter: ServiceAdapter
    ) -> None:
        """
        Register a service with the kernel.
        
        This does NOT start the service. Registration just makes it available
        for the startup sequence.
        
        Args:
            service_id: Unique identifier for this service instance
            adapter: The service adapter providing lifecycle hooks
        """
        async with self._lock:
            if service_id in self._services:
                from ..exceptions import RegistrationError
                raise RegistrationError(f"Service '{service_id}' already registered")
            
            self._services[service_id] = adapter
    
    def unregister_service(self, service_id: str) -> bool:
        """
        Unregister a service.
        
        Args:
            service_id: The service to unregister
            
        Returns:
            True if unregistered, False if not found
        """
        if service_id in self._services:
            del self._services[service_id]
            return True
        return False
    
    async def resolve_service_order(self) -> List[str]:
        """
        Resolve the startup/shutdown order for all services.
        
        Returns:
            List of service IDs in startup order (dependencies first)
        """
        if not self._services:
            return []
        
        # Build dependency graph
        from ..dependency import DependencyGraph, Dependency
        
        dependencies = []
        for sid, adapter in self._services.items():
            for dep_id in adapter.get_dependencies():
                dependencies.append(Dependency(
                    from_entity=sid,
                    to_entity=dep_id,
                    required=True
                ))
        
        # Create graph and get topological order
        graph = DependencyGraph.create(dependencies)
        
        try:
            return graph.topological_sort()
        except ValueError as e:
            cycle = graph.find_cycle()
            from ..exceptions import DependencyError
            raise DependencyError(
                f"Dependency cycle detected: {cycle}",
                cycle_path=cycle
            )
    
    async def start_all_services(self) -> None:
        """
        Start all registered services in dependency order.
        
        Raises:
            StartupError: If any service fails to start (and partial startup not allowed)
        """
        import asyncio
        
        # Resolve startup order
        order = await self.resolve_service_order()
        
        errors: List[str] = []
        
        async with self._lock:
            for service_id in order:
                if service_id not in self._services:
                    continue
                
                adapter = self._services[service_id]
                
                try:
                    # Create and start the service instance
                    await self._instantiate_and_start_service(service_id, adapter)
                    
                except Exception as e:
                    errors.append(f"{service_id}: {e}")
                    
                    if not self._config.allow_partial_startup:
                        # Rollback already-started services
                        await self._rollback_startups(order, service_id)
                        raise StartupError(
                            f"Failed to start service '{service_id}'",
                            failed_component=service_id,
                            cause=e
                        )
            
            self._state.is_running = True
            self._state.start_time = Timestamp.now().value
    
    async def stop_all_services(self) -> None:
        """
        Stop all services in reverse dependency order.
        
        Raises:
            ShutdownError: If any service fails to stop
        """
        import asyncio
        
        # Resolve startup order, then reverse for shutdown
        order = await self.resolve_service_order()
        shutdown_order = list(reversed(order))
        
        errors: List[str] = []
        
        async with self._lock:
            for service_id in shutdown_order:
                if service_id not in self._services:
                    continue
                
                try:
                    await self._stop_service(service_id)
                    
                except Exception as e:
                    errors.append(f"{service_id}: {e}")
            
            self._state.is_running = False
            self._state.stop_time = Timestamp.now().value
            
            if errors and not self._config.allow_partial_startup:
                raise ShutdownError(
                    f"Failed to stop services: {'; '.join(errors)}",
                    failed_service=errors[0].split(":")[0] if errors else None
                )
    
    async def _instantiate_and_start_service(self, service_id: str, adapter: ServiceAdapter) -> None:
        """Instantiate and start a single service."""
        # This would typically instantiate the actual service
        # For now, we just mark it as ready
        self._service_instances[service_id] = f"instance-of-{adapter.name}"
    
    async def _stop_service(self, service_id: str) -> None:
        """Stop a single service."""
        if service_id in self._service_instances:
            del self._service_instances[service_id]
    
    async def _rollback_startups(
        self,
        order: List[str],
        failed_at: str
    ) -> None:
        """Stop all services that were started before the failure."""
        # Find position of failed service and stop everything before it (in reverse)
        try:
            idx = order.index(failed_at)
            rollback_order = list(reversed(order[:idx]))
            
            for sid in rollback_order:
                if sid in self._service_instances:
                    del self._service_instances[sid]
                    
        except ValueError:
            pass  # Service not found in order
    
    @property
    def data_governance_manager(self) -> Optional[DataGovernanceManager]:
        """Get the kernel's DataGovernanceManager instance."""
        return self._data_governance_mgr
    
    async def get_health_report(self) -> Dict[str, Any]:
        """
        Get kernel health status.
        
        Returns:
            Health report dictionary
        """
        import time
        
        return {
            "name": self.name,
            "version": self.version,
            "entity_id": str(self.entity_id),
            "is_running": self._state.is_running,
            "services_registered": len(self._services),
            "services_started": len(self._service_instances),
            "governance_manager_present": self._data_governance_mgr is not None,
            "uptime_seconds": (
                Timestamp.now().value - self._state.start_time
                if self._state.start_time else 0.0
            )
        }
    
    async def __aenter__(self) -> "Kernel":
        """Async context manager entry."""
        await self.start_all_services()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.stop_all_services()
    
    async def govern_information(
        self,
        information_id: str,
        content_hash: str,
        owner: OwnerIdentity,
        classification: Optional[ClassificationLevel] = None,
        lifecycle_state: LifecycleState = LifecycleState.CREATED,
    ) -> Optional[InformationRecord]:
        """
        Govern a piece of information through the kernel's governance manager.
        
        Args:
            information_id: Unique identifier for the information
            content_hash: Hash of the content (integrity guarantee)
            owner: Owner identity
            classification: Classification level (auto-assigned if None)
            lifecycle_state: Initial lifecycle state
            
        Returns:
            InformationRecord with full governance context, or None if
            data_governance is not available
        """
        if self._data_governance_mgr is None:
            return None
        
        try:
            record = await self._data_governance_mgr.govern(
                information_id=information_id,
                content_hash=content_hash,
                owner=owner,
                classification=classification,
                lifecycle_state=lifecycle_state,
            )
            return record
        except Exception:
            return None


__all__ = [
    # Kernel types (existing)
    "KernelConfig",
    "ServiceInfo",
    "KernelState",
    "ServiceAdapter",
    "Kernel",
    "KernelGovernanceConfig",
    
    # Builder components (new)
    "ConstructionStage",
    "ConstructionStatus",
    "KernelConstructionId",
    "ConstructionInputSnapshot",
    "ConstructionStageRecord",
    "KernelConstructionResult",
    "KernelConstructionSnapshot",
    "KernelConstructionReceipt",
    "KernelBuilderState",
    "KernelConstructionRequest",
    "KernelConstructionContext",
    "KernelBuilder",
    "KernelConstructionPlan",
]

# Phase 3.7.21 exports
if DataGovernanceManager is not None:
    __all__.extend([
        "DataGovernanceManager",
        "InformationRecord",
        "OwnerIdentity",
        "ClassificationLevel",
        "LifecycleState",
    ])
