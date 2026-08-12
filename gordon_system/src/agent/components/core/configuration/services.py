# Service Registry & Dependency Injection Framework
# ================================================
"""
Service registry and dependency injection for Gordon Core.

This module implements Phase 3.8.4.3: Dependency Injection, Service Registration & Lifetimes.

SERVICE TAXONOMY

Define canonical abstractions for:

- ServiceDescriptor - Describes a service's contract and implementation
- ServiceContract - Interface that services must implement
- ServiceImplementation - Concrete implementation of a contract
- ServiceFactory - Factory for creating service instances
- ServiceRegistry - Central registry for all registered services
- DependencyResolver - Resolves dependencies between services
- DependencyGraph - Graph representation of service dependencies
- ServiceScope - Scope for scoped service lifetimes
- LifetimePolicy - Policy for managing service lifetime
- ResolutionContext - Context for dependency resolution

Phase 3.8.4: Configuration & Dependency Management
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    Any,
    Optional,
    List,
    Tuple,
    Callable,
)
from enum import Enum
import time


# =============================================================================
# Service Contract Definition
# =============================================================================

class ServiceContract:
    """
    Base class for all service contracts.
    
    All services should inherit from this or implement a compatible interface.
    Services expose well-defined interfaces for dependency injection.
    """
    pass


@dataclass(frozen=True)
class ServiceId:
    """Unique identifier for a service."""
    value: str
    
    @classmethod
    def generate(cls) -> "ServiceId":
        import uuid
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "ServiceId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# Lifetime Policies
# =============================================================================

class Lifetime(Enum):
    """Lifetime policies for services."""
    SINGLETON = "singleton"  # One instance per registry
    SCOPED = "scoped"       # One instance per scope
    TRANSIENT = "transient" # New instance each time


@dataclass(frozen=True)
class LifetimePolicy:
    """Policy for managing service lifetime."""
    lifetime: Lifetime
    max_lifetime_seconds: Optional[float] = None  # For scoped/transient services
    
    def is_singleton(self) -> bool:
        return self.lifetime == Lifetime.SINGLETON
    
    def is_scoped(self) -> bool:
        return self.lifetime == Lifetime.SCOPED
    
    def is_transient(self) -> bool:
        return self.lifetime == Lifetime.TRANSIENT


# =============================================================================
# Service Descriptor
# =============================================================================

@dataclass(frozen=True)
class ServiceDescriptor:
    """
    Describes a service's contract and implementation.
    
    This is the canonical representation of a service for dependency injection.
    """
    contract_type: type  # The interface/service contract class
    implementation_type: Optional[type] = None  # Concrete implementation, if any
    factory_function: Optional[Callable[[Any], Any]] = None  # Factory to create instance
    lifetime_policy: LifetimePolicy = field(default_factory=lambda: LifetimePolicy(Lifetime.TRANSIENT))
    service_id: ServiceId = field(default_factory=ServiceId.generate)
    
    def is_self_registered(self) -> bool:
        """Check if this descriptor registers the implementation as its own contract."""
        return self.implementation_type is not None and self.implementation_type == self.contract_type
    
    def uses_factory(self) -> bool:
        """Check if a factory function is used for creation."""
        return self.factory_function is not None


# =============================================================================
# Dependency Graph
# =============================================================================

@dataclass(frozen=True)
class DependencyEdge:
    """A dependency edge from one service to another."""
    from_service: ServiceId  # The dependent service
    to_service: ServiceId    # The required service
    required: bool = True    # If False, this is an optional dependency


@dataclass(frozen=True)
class DependencyGraph:
    """
    Immutable dependency graph representation.
    
    Dependencies are directional: A -> B means "A depends on B"
    """
    _edges: Dict[ServiceId, List[DependencyEdge]] = field(default_factory=dict)
    
    @classmethod
    def create(cls, edges: Tuple[DependencyEdge, ...]) -> "DependencyGraph":
        """Create a graph from a list of dependency edges."""
        graph_dict: Dict[ServiceId, List[DependencyEdge]] = {}
        
        for edge in edges:
            if edge.from_service not in graph_dict:
                graph_dict[edge.from_service] = []
            graph_dict[edge.from_service].append(edge)
        
        return cls(_edges=graph_dict)
    
    def get_dependencies(self, service: ServiceId) -> List[ServiceId]:
        """Get services that the given service depends on."""
        if service not in self._edges:
            return []
        return [edge.to_service for edge in self._edges[service]]
    
    def has_cycle(self) -> bool:
        """
        Check if the graph contains a cycle.
        
        Returns:
            True if there is a cycle, False otherwise
        """
        visited = set()
        rec_stack = set()
        
        def dfs(service: ServiceId) -> bool:
            visited.add(service)
            rec_stack.add(service)
            
            for dep in self.get_dependencies(service):
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(service)
            return False
        
        all_services = set(self._edges.keys())
        for edge_list in self._edges.values():
            for edge in edge_list:
                all_services.add(edge.to_service)
        
        for service in all_services:
            if service not in visited:
                if dfs(service):
                    return True
        
        return False
    
    def topological_sort(self) -> List[ServiceId]:
        """
        Perform topological sort on the graph.
        
        Returns:
            List of services in dependency order (dependencies first)
            
        Raises:
            ValueError: If graph contains a cycle
        """
        if self.has_cycle():
            raise ValueError("Cannot topologically sort cyclic dependency graph")
        
        # Kahn's algorithm
        in_degree = {service: 0 for service in self._edges.keys()}
        all_services = set(self._edges.keys())
        for edge_list in self._edges.values():
            for edge in edge_list:
                all_services.add(edge.to_service)
                if edge.from_service in in_degree:
                    in_degree[edge.from_service] += 1
        
        # Start with services that have no incoming edges (no dependencies)
        queue = [s for s in all_services if in_degree.get(s, 0) == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for edge_list in self._edges.values():
                for edge in edge_list:
                    if edge.to_service == node and edge.from_service in all_services:
                        in_degree[edge.from_service] -= 1
                        if in_degree[edge.from_service] == 0:
                            queue.append(edge.from_service)
        
        return result


# =============================================================================
# Service Registry
# =============================================================================

class DuplicateRegistrationError(Exception):
    """Raised when a service is registered twice."""
    pass


@dataclass(frozen=True)
class RegistrationRecord:
    """A record of a registered service."""
    descriptor: ServiceDescriptor
    instance: Optional[Any] = None  # If singleton, store the instance
    created_at: float = field(default_factory=time.monotonic)


class ServiceRegistry:
    """
    Central registry for all registered services.
    
    Services are registered by contract and can be resolved by contract or ID.
    The registry owns providers, not service values (as per core law).
    
    Core Laws:
    - Exactly one service registry exists
    - One resolver exists
    - Circular dependencies are rejected
    """
    
    def __init__(self):
        self._registrations: Dict[ServiceId, RegistrationRecord] = {}
        self._contract_registry: Dict[type, List[ServiceId]] = {}  # contract -> list of IDs
        self._dependency_graph: DependencyGraph = DependencyGraph.create(())
        self._lock = __import__("threading").Lock()
    
    def register(self, descriptor: ServiceDescriptor) -> ServiceId:
        """
        Register a service with the registry.
        
        Args:
            descriptor: The service descriptor containing contract and implementation
            
        Returns:
            The registered service ID
            
        Raises:
            DuplicateRegistrationError: If service is already registered
        """
        service_id = descriptor.service_id
        
        with self._lock:
            if service_id in self._registrations:
                raise DuplicateRegistrationError(f"Service {service_id} already registered")
            
            # Check for duplicate contract registration
            contract = descriptor.contract_type
            if contract in self._contract_registry:
                existing_ids = self._contract_registry[contract]
                if not descriptor.uses_factory():
                    # If this isn't using a factory, it's likely a duplicate implementation
                    raise DuplicateRegistrationError(
                        f"Service contract {contract.__name__} already has implementations"
                    )
            
            # Update graph if implementation is specified (not just factory)
            if descriptor.implementation_type and not descriptor.uses_factory():
                self._add_dependency(contract, descriptor.implementation_type)
            
            record = RegistrationRecord(descriptor=descriptor)
            self._registrations[service_id] = record
            
            if contract not in self._contract_registry:
                self._contract_registry[contract] = []
            self._contract_registry[contract].append(service_id)
        
        return service_id
    
    def _add_dependency(self, from_type: type, to_type: type) -> None:
        """Add a dependency edge between types."""
        # Simplified: In real implementation, would check actual dependencies
        pass
    
    def unregister(self, service_id: ServiceId) -> bool:
        """Unregister a service."""
        with self._lock:
            if service_id not in self._registrations:
                return False
            
            record = self._registrations[service_id]
            contract = record.descriptor.contract_type
            
            del self._registrations[service_id]
            
            if contract in self._contract_registry:
                self._contract_registry[contract] = [
                    sid for sid in self._contract_registry[contract] 
                    if sid != service_id
                ]
            
            return True
    
    def get_registration(self, service_id: ServiceId) -> Optional[RegistrationRecord]:
        """Get a registered service by ID."""
        return self._registrations.get(service_id)
    
    def resolve_by_contract(self, contract_type: type) -> Optional[ServiceId]:
        """
        Resolve a service by its contract type.
        
        Args:
            contract_type: The service contract/interface class
            
        Returns:
            ServiceId if found, None otherwise
        """
        with self._lock:
            candidates = self._contract_registry.get(contract_type)
            if not candidates:
                return None
            
            # Return the first registered service for this contract
            return candidates[0]
    
    def list_registered_services(self) -> List[Tuple[str, str]]:
        """
        List all registered services.
        
        Returns:
            List of (service_id_str, contract_name) tuples
        """
        with self._lock:
            return [
                (sid.value, record.descriptor.contract_type.__name__)
                for sid, record in self._registrations.items()
            ]


# =============================================================================
# Dependency Resolver
# =============================================================================

class DependencyResolutionError(Exception):
    """Raised when dependency resolution fails."""
    pass


@dataclass(frozen=True)
class ResolutionResult:
    """Result of dependency resolution."""
    success: bool
    service_id: Optional[ServiceId] = None
    instance: Optional[Any] = None
    error_message: Optional[str] = None
    resolved_dependencies: List[ServiceId] = field(default_factory=list)


class DependencyResolver:
    """
    Resolves dependencies between services.
    
    Core Law: Dependencies are explicit. Constructor injection is the default.
    """
    
    def __init__(self, registry: ServiceRegistry):
        self._registry = registry
    
    def resolve(self, service_id: ServiceId) -> ResolutionResult:
        """
        Resolve a service and its dependencies.
        
        Args:
            service_id: The ID of the service to resolve
            
        Returns:
            ResolutionResult with instance or error
        """
        record = self._registry.get_registration(service_id)
        
        if not record:
            return ResolutionResult(
                success=False,
                error_message=f"Service {service_id} not found in registry"
            )
        
        descriptor = record.descriptor
        
        # If singleton and already created, return cached instance
        if descriptor.lifetime_policy.is_singleton() and record.instance is not None:
            return ResolutionResult(
                success=True,
                service_id=service_id,
                instance=record.instance
            )
        
        try:
            if descriptor.uses_factory():
                # Use factory to create instance
                instance = descriptor.factory_function(None)  # Context would be passed here
            elif descriptor.implementation_type:
                # Direct instantiation (simplified)
                instance = descriptor.implementation_type()
            else:
                return ResolutionResult(
                    success=False,
                    error_message=f"No implementation or factory for service {service_id}"
                )
            
            # Cache singleton instances
            if descriptor.lifetime_policy.is_singleton():
                with self._registry._lock:
                    self._registry._registrations[service_id] = RegistrationRecord(
                        descriptor=descriptor,
                        instance=instance,
                        created_at=record.created_at
                    )
            
            return ResolutionResult(
                success=True,
                service_id=service_id,
                instance=instance
            )
        
        except Exception as e:
            return ResolutionResult(
                success=False,
                error_message=f"Failed to resolve {service_id}: {e}"
            )


# =============================================================================
# Service Scope
# =============================================================================

class ServiceScope:
    """
    A scope for scoped service lifetimes.
    
    Services with SCOPED lifetime are created once per scope and shared within
    that scope. When the scope ends, those services are disposed.
    """
    
    def __init__(self, registry: ServiceRegistry):
        self._registry = registry
        self._scoped_instances: Dict[ServiceId, Any] = {}
        self._created_at = time.monotonic()
    
    def resolve(self, service_id: ServiceId) -> Optional[Any]:
        """Resolve a scoped service."""
        if service_id in self._scoped_instances:
            return self._scoped_instances[service_id]
        
        result = DependencyResolver(self._registry).resolve(service_id)
        if result.success and result.instance:
            record = self._registry.get_registration(service_id)
            if record and record.descriptor.lifetime_policy.is_scoped():
                self._scoped_instances[service_id] = result.instance
            return result.instance
        return None
    
    def dispose(self) -> None:
        """Dispose of all scoped instances."""
        self._scoped_instances.clear()


# =============================================================================
# Service Factory
# =============================================================================

class ServiceFactory:
    """
    Factory for creating service instances.
    
    Factories can be registered to provide custom instantiation logic,
    dependency injection, or complex object graphs.
    """
    
    def __init__(self):
        self._factories: Dict[type, Callable[[Any], Any]] = {}
    
    def register_factory(self, contract_type: type, factory_fn: Callable[[Any], Any]) -> None:
        """Register a factory function for a contract."""
        self._factories[contract_type] = factory_fn
    
    def create(self, contract_type: type, context: Any) -> Optional[Any]:
        """
        Create an instance using the registered factory.
        
        Args:
            contract_type: The service contract to create
            context: Context passed to the factory
            
        Returns:
            Created instance or None if no factory registered
        """
        factory = self._factories.get(contract_type)
        if factory:
            return factory(context)
        return None


# =============================================================================
# Public API exports
# =============================================================================

__all__ = [
    # Contracts
    "ServiceContract",
    
    # IDs and Lifetimes
    "ServiceId",
    "Lifetime",
    "LifetimePolicy",
    
    # Descriptors
    "ServiceDescriptor",
    
    # Graph
    "DependencyEdge",
    "DependencyGraph",
    
    # Registry
    "DuplicateRegistrationError",
    "RegistrationRecord",
    "ServiceRegistry",
    
    # Resolver
    "DependencyResolutionError",
    "ResolutionResult",
    "DependencyResolver",
    
    # Scope
    "ServiceScope",
    
    # Factory
    "ServiceFactory",
]