# Component, Service & Capability Identities - Phase 3.19.4
# ===========================================================

"""
Component, service, capability identity types.

Every Gordon component (package, module, class) must possess:
    - Component Identity (what the component is)
    - Service Identity (what services it provides)
    - Capability Identity (what capabilities it offers)

COMPONENT IDENTITY HIERARCHY:
    ComponentId             - The component itself
        └── ServiceId         - Services provided by component
            └── CapabilityId      - Specific capability within service
            
INVARIANTS:
    CMP-001: Each component has exactly one canonical identity
    CMP-002: Component identity is stable across restarts
    CMP-003: No two components share the same fully-qualified identity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import uuid


# =============================================================================
# COMPONENT IDENTITY
# =============================================================================


@dataclass(frozen=True)
class ComponentId:
    """
    Canonical identity for a Gordon component.
    
    Components include packages, modules, classes, and other architectural
    elements that are part of the Gordon system.
    
    INVARIANTS:
        CMP-001: Each component has exactly one canonical identity
        CMP-002: Component identity is stable across restarts
        CMP-003: No two components share the same fully-qualified identity
        
    PARAMETERS:
        name          - Component name (e.g., "state_manager", "event_dispatcher")
        module_path   - Full Python module path
        package       - Package containing this component
        version       - Component version within the application
    """
    
    name: str
    module_path: Optional[str] = None
    package: Optional[str] = None
    version: str = "1.0.0"
    
    @classmethod
    def from_fqname(cls, fqname: str) -> "ComponentId":
        """Create a ComponentId from a fully-qualified name."""
        parts = fqname.split(".")
        
        if len(parts) >= 2:
            module_path = ".".join(parts[:-1])
            name = parts[-1]
        else:
            module_path = None
            name = parts[0]
            
        return cls(
            name=name,
            module_path=module_path,
            package=None,
            version="1.0.0",
        )
    
    @property
    def fqname(self) -> str:
        """Get fully-qualified component name."""
        if self.module_path:
            return f"{self.module_path}.{self.name}"
        return self.name
    
    def to_string(self) -> str:
        """Serialize to canonical string representation."""
        parts = [self.fqname, self.version]
        return ":".join(parts)
    
    @classmethod
    def from_string(cls, value: str) -> "ComponentId":
        """Parse a string into ComponentId."""
        parts = value.split(":")
        
        if len(parts) >= 2:
            name_parts = parts[0].rsplit(".", 1)
            module_path = name_parts[0] if len(name_parts) > 1 else None
            name = name_parts[-1]
            version = parts[1]
        else:
            name = parts[0]
            module_path = None
            version = "1.0.0"
            
        return cls(
            name=name,
            module_path=module_path,
            version=version,
        )
    
    def __hash__(self) -> int:
        """Hash based on fully-qualified name."""
        return hash(self.fqname)


# =============================================================================
# SERVICE IDENTITY
# =============================================================================


@dataclass(frozen=True)
class ServiceId:
    """
    Canonical identity for a service provided by a component.
    
    Services are the interface contracts that components expose to other
    parts of the system.
    
    INVARIANTS:
        SV-001: Each service has exactly one canonical identity
        SV-002: Service identities are unique within their component scope
        SV-003: Service ID never changes during execution
        
    PARAMETERS:
        name          - Service name (e.g., "execution_manager", "state_accessor")
        component     - Component providing this service
        version       - Service contract version
    """
    
    name: str
    component: ComponentId
    version: str = "1.0.0"
    
    @classmethod
    def from_string(cls, value: str) -> "ServiceId":
        """Parse a string into ServiceId."""
        parts = value.split(":")
        
        if len(parts) >= 3:
            name = parts[0]
            component_name = parts[1]
            version = parts[2]
        elif len(parts) == 2:
            name = parts[0]
            component_name = ""
            version = parts[1]
        else:
            name = parts[0]
            component_name = ""
            version = "1.0.0"
            
        return cls(
            name=name,
            component=ComponentId(name=component_name),
            version=version,
        )
    
    @property
    def fqname(self) -> str:
        """Get fully-qualified service name."""
        if self.component.module_path:
            return f"{self.component.module_path}.{self.name}"
        return self.name
    
    def to_string(self) -> str:
        """Serialize to canonical string representation."""
        parts = [self.fqname, self.component.version, self.version]
        return ":".join(parts)


# =============================================================================
# CAPABILITY IDENTITY
# =============================================================================


@dataclass(frozen=True)
class CapabilityId:
    """
    Canonical identity for a specific capability within a service.
    
    Capabilities are the concrete implementations of services that provide
    actual functionality.
    
    INVARIANTS:
        CP-001: Each capability has exactly one canonical identity
        CP-002: Capability identities are unique within their service scope
        CP-003: Capability ID never changes during execution
        
    PARAMETERS:
        name          - Capability name
        service       - Service this capability implements
        version       - Capability implementation version
    """
    
    name: str
    service: ServiceId
    version: str = "1.0.0"
    
    @classmethod
    def from_string(cls, value: str) -> "CapabilityId":
        """Parse a string into CapabilityId."""
        parts = value.split(":")
        
        if len(parts) >= 3:
            name = parts[0]
            service_name = parts[1]
            version = parts[2] if len(parts) > 2 else "1.0.0"
        else:
            name = parts[0]
            service_name = ""
            version = "1.0.0"
            
        return cls(
            name=name,
            service=ServiceId(name=service_name, component=ComponentId(name="")),
            version=version,
        )
    
    @property
    def fqname(self) -> str:
        """Get fully-qualified capability name."""
        if self.service.component.module_path:
            return f"{self.service.component.module_path}.{self.name}"
        return self.name
    
    def to_string(self) -> str:
        """Serialize to canonical string representation."""
        parts = [self.fqname, self.version]
        return ":".join(parts)


# =============================================================================
# MODULE IDENTITY
# =============================================================================


@dataclass(frozen=True)
class ModuleId:
    """
    Canonical identity for a Python module.
    
    Modules are the fundamental organizational unit in Python and Gordon.
    
    INVARIANTS:
        MOD-001: Each module has exactly one canonical identity
        MOD-002: Module identities are based on import path
        MOD-003: Module ID is stable across restarts
        
    PARAMETERS:
        name          - Module name (e.g., "gordon.components.core.state")
        package       - Package containing the module
        file_path     - File system path to the module
    """
    
    name: str
    package: Optional[str] = None
    file_path: Optional[str] = None
    
    @classmethod
    def from_import_path(cls, import_path: str) -> "ModuleId":
        """Create a ModuleId from an import path."""
        return cls(name=import_path)
    
    @property
    def import_path(self) -> str:
        """Get the full import path for this module."""
        if self.package:
            return f"{self.package}.{self.name}"
        return self.name
    
    def to_string(self) -> str:
        """Serialize to canonical string representation."""
        return self.import_path


# =============================================================================
# PACKAGE IDENTITY  
# =============================================================================


@dataclass(frozen=True)
class PackageId:
    """
    Canonical identity for a Python package.
    
    Packages group related modules and components together.
    
    INVARIANTS:
        PKG-001: Each package has exactly one canonical identity
        PKG-002: Package identities are based on import path
        PKG-003: Package ID is stable across restarts
        
    PARAMETERS:
        name          - Package name (e.g., "gordon.components.core")
        version       - Package version
        directory     - File system directory containing the package
    """
    
    name: str
    version: str = "1.0.0"
    directory: Optional[str] = None
    
    @classmethod
    def from_import_path(cls, import_path: str) -> "PackageId":
        """Create a PackageId from an import path."""
        return cls(name=import_path)
    
    @property
    def import_path(self) -> str:
        """Get the full import path for this package."""
        return self.name
    
    def to_string(self) -> str:
        """Serialize to canonical string representation."""
        parts = [self.import_path, self.version]
        return ":".join(parts)


# =============================================================================
# REGISTRY OF COMPONENT IDENTITIES
# =============================================================================


class ComponentIdentityRegistry:
    """
    Registry for tracking component identities within Gordon.
    
    Provides utilities for finding components by identity and managing
    component registration.
    
    INVARIANTS:
        CIR-001: No duplicate fully-qualified component names
        CIR-002: Component identities are immutable once registered
        CIR-003: Registry maintains discovery information
        
    METHODS:
        register()          - Register a new component identity
        find_by_name()      - Look up component by name
        list_all()          - List all registered components
        unregister()        - Remove a component from registry
    """
    
    def __init__(self):
        self._registry: dict[str, ComponentId] = {}
        self._services: dict[str, ServiceId] = {}
        self._capabilities: dict[str, CapabilityId] = {}
    
    def register_component(self, component: ComponentId) -> bool:
        """Register a new component identity."""
        fqname = component.fqname
        if fqname in self._registry:
            return False
        self._registry[fqname] = component
        return True
    
    def register_service(self, service: ServiceId) -> bool:
        """Register a new service identity."""
        fqname = service.fqname
        if fqname in self._services:
            return False
        self._services[fqname] = service
        return True
    
    def register_capability(self, capability: CapabilityId) -> bool:
        """Register a new capability identity."""
        fqname = capability.fqname
        if fqname in self._capabilities:
            return False
        self._capabilities[fqname] = capability
        return True
    
    def find_component(self, name: str) -> Optional[ComponentId]:
        """Find a component by its fully-qualified name."""
        return self._registry.get(name)
    
    def find_service(self, name: str) -> Optional[ServiceId]:
        """Find a service by its fully-qualified name."""
        return self._services.get(name)
    
    def find_capability(self, name: str) -> Optional[CapabilityId]:
        """Find a capability by its fully-qualified name."""
        return self._capabilities.get(name)
    
    def list_all_components(self) -> list[ComponentId]:
        """List all registered components."""
        return list(self._registry.values())
    
    def list_services_for_component(
        self, 
        component: ComponentId,
    ) -> list[ServiceId]:
        """List all services provided by a component."""
        component_path = component.module_path or component.name
        return [
            s for s in self._services.values()
            if s.component.fqname.startswith(component_path)
        ]


__all__ = [
    "ComponentId",
    "ServiceId",
    "CapabilityId",
    "ModuleId", 
    "PackageId",
    "ComponentIdentityRegistry",
]