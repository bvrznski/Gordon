# Core Component Interface
# ========================

"""
Core component interface - the base contract for all runtime entities.

This is NOT an abstract base class for code reuse. It is a BEHAVIORAL
contract that defines what makes something a "component" in the Gordon runtime.

ARCHITECTURAL PRINCIPLES:
- Every runtime entity MUST conform to this contract
- Components are lifecycle-managed
- Components have identity and state
- Components can be discovered, registered, and managed
"""

from typing import Protocol, Optional, Dict, Any
from dataclasses import dataclass
import uuid


@dataclass(frozen=True)
class ComponentId:
    """
    Unique identifier for a component within the runtime.
    
    Component IDs are immutable and globally unique within a runtime instance.
    They follow the pattern: "component-type.instance-number"
    """
    
    value: str
    
    @classmethod
    def generate(cls, prefix: str = "component") -> "ComponentId":
        """Generate a new component ID with the given prefix."""
        return cls(value=f"{prefix}_{uuid.uuid4().hex[:12]}")
    
    @classmethod
    def from_parts(cls, component_type: str, instance_id: int) -> "ComponentId":
        """Create a component ID from type and instance number."""
        return cls(value=f"{component_type}.{instance_id}")
    
    @property
    def component_type(self) -> str:
        """Extract the component type from the ID."""
        if "." in self.value:
            return self.value.split(".")[0]
        return self.value
    
    @property
    def instance_id(self) -> Optional[int]:
        """Extract the instance number from the ID, or None if not numeric."""
        if "." in self.value:
            try:
                return int(self.value.split(".")[1])
            except ValueError:
                return None
        return None


@dataclass(frozen=True)
class ComponentMetadata:
    """
    Immutable metadata about a component.
    
    This is the canonical source of truth for component information,
    not embedded in the component implementation itself.
    """
    
    component_id: str
    component_type: str  # e.g., "service", "daemon", "task"
    
    # Component properties
    version: str = "1.0.0"
    description: str = ""
    tags: Dict[str, str] = None  # type: ignore
    
    # Lifecycle state (for registry/querying)
    is_enabled: bool = True
    is_running: bool = False
    
    # Configuration reference (optional - can point to config source)
    config_path: Optional[str] = None


# =============================================================================
# CORE COMPONENT INTERFACES
# =============================================================================

class IComponent(Protocol):
    """
    Base interface for all runtime components.
    
    Every entity in the Gordon runtime MUST implement this interface.
    This is not an abstract base class - it's a behavioral contract.
    
    INVARIANTS:
        1. All components have a unique ID within the runtime
        2. Components can report their metadata
        3. Components can be enabled/disabled dynamically
    """
    
    @property
    def component_id(self) -> ComponentId:
        """Get the unique identifier for this component."""
        ...
    
    @property
    def metadata(self) -> ComponentMetadata:
        """Get immutable metadata about this component."""
        ...
    
    def is_enabled(self) -> bool:
        """Check if this component is enabled (can receive events, etc.)."""
        ...
    
    def enable(self) -> None:
        """Enable this component to receive events and process requests."""
        ...
    
    def disable(self) -> None:
        """
        Disable this component.
        
        After disabling:
            - Component stops processing new events
            - Existing operations may continue to completion
            - Component can be re-enabled later
        """
        ...


class ILifecycleComponent(IComponent, Protocol):
    """
    Interface for components that have lifecycle management.
    
    Components implementing this interface support full startup/shutdown
    semantics through their lifecycle controller.
    """
    
    @property
    def lifecycle_state(self) -> str:
        """Get the current lifecycle state (created, running, stopped, etc.)."""
        ...
    
    async def initialize(self) -> None:
        """
        Initialize component resources and dependencies.
        
        This is called once during startup before start().
        """
        ...
    
    async def start(self) -> None:
        """
        Start component operation.
        
        After calling start():
            - Component begins processing events
            - Background tasks are started
            - Component becomes available to other components
        """
        ...
    
    async def stop(self) -> None:
        """
        Stop component operation gracefully.
        
        After calling stop():
            - Component stops accepting new work
            - Existing operations complete or timeout
            - Resources are released
        """
        ...
    
    async def shutdown(self) -> None:
        """
        Force shutdown regardless of current state.
        
        Used during application termination to ensure cleanup.
        This should NOT be called by other components.
        """
        ...


class IManagedComponent(ILifecycleComponent, Protocol):
    """
    Interface for components that are managed by the runtime framework.
    
    Managed components:
        - Are registered with the component registry
        - Follow framework lifecycle conventions
        - Can be discovered and introspected
    """
    
    @property
    def manager_id(self) -> Optional[str]:
        """Get the ID of the manager responsible for this component."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on this component.
        
        Returns:
            Dictionary with health status information:
                - status: "healthy", "degraded", or "failed"
                - details: Additional context-specific information
                - timestamp: When the check was performed
        """
        ...
    
    async def diagnostics(self) -> Dict[str, Any]:
        """
        Get diagnostic information about this component.
        
        Returns:
            Dictionary with diagnostic data suitable for debugging.
        """
        ...


class IComponentFactory(Protocol):
    """
    Factory interface for creating components.
    
    Factories are responsible for:
        - Creating component instances
        - Injecting dependencies
        - Registering with the system
    
    This is NOT a factory pattern implementation - it's a contract for
    how components can be constructed in the runtime.
    """
    
    async def create_component(self, component_id: ComponentId) -> IComponent:
        """
        Create and return a new component instance.
        
        Args:
            component_id: The unique ID to assign to this component
            
        Returns:
            A newly created component ready for initialization
            
        Raises:
            ComponentCreationError: If component creation fails
        """
        ...
    
    async def destroy_component(self, component: IComponent) -> None:
        """
        Clean up and remove a component.
        
        Args:
            component: The component to destroy
        """
        ...


class ComponentCreationError(Exception):
    """Raised when component creation fails."""
    pass


__all__ = [
    "ComponentId",
    "ComponentMetadata",
    "IComponent",
    "ILifecycleComponent",
    "IManagedComponent",
    "IComponentFactory",
    "ComponentCreationError",
]