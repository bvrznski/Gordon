# Development Tool Registry
# =========================
"""
Tool registry provides centralized registration and discovery of development tools.

This module implements the canonical tool registry that maintains a single source
of truth for all registered development tools, their versions, and capabilities.

ARCHITECTURAL PRINCIPLES:
- Single authoritative tool registry
- Tools are registered by name with unique identifiers
- Version constraints can be specified
- Capabilities are explicitly documented
- Registry is immutable by default (changes require explicit updates)
"""
from typing import (
    Protocol,
    Dict,
    List,
    Optional,
    Any,
    TypeVar,
    Generic,
    Callable,
    Iterable,
)
from dataclasses import dataclass, field
from enum import Enum
import threading


T = TypeVar("T")


@dataclass(frozen=True)
class ToolEntry:
    """Immutable entry in the tool registry."""
    name: str
    version: str
    category: str
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    configuration_schema: Optional[Dict[str, Any]] = None
    documentation_url: Optional[str] = None
    
    def matches_version(self, constraint: str) -> bool:
        """Check if this entry's version matches a constraint."""
        # Parse constraint (simple format: major.minor.patch)
        if not constraint:
            return True
        
        parts = constraint.split(".")
        self_parts = self.version.split(".")
        
        for i in range(min(len(parts), len(self_parts))):
            try:
                if int(parts[i]) != int(self_parts[i]):
                    return False
            except ValueError:
                # Non-numeric part, skip
                continue
        
        return True


class RegistryState(Enum):
    """Possible states of the tool registry."""
    INITIAL = "initial"
    LOADED = "loaded"
    FROZEN = "frozen"
    SHUTDOWN = "shutdown"


# =============================================================================
# TOOL REGISTRY IMPLEMENTATION
# =============================================================================

class ToolRegistry:
    """
    Centralized registry for development tools.
    
    This class provides thread-safe registration, discovery, and management
    of development tools in the Gordon system.
    
    Usage:
        >>> registry = ToolRegistry()
        >>> registry.register("my-tool", "1.0.0", "build")
        True
        >>> tool = registry.get("my-tool")
    """
    
    def __init__(self) -> None:
        """Initialize an empty tool registry."""
        self._tools: Dict[str, ToolEntry] = {}
        self._state: RegistryState = RegistryState.INITIAL
        self._lock = threading.RLock()
    
    @property
    def state(self) -> RegistryState:
        """Get the current state of the registry."""
        return self._state
    
    @property
    def tool_names(self) -> List[str]:
        """Get list of all registered tool names."""
        with self._lock:
            return list(self._tools.keys())
    
    @property
    def tool_count(self) -> int:
        """Get the total number of registered tools."""
        with self._lock:
            return len(self._tools)
    
    def register(
        self,
        name: str,
        version: str,
        category: str = "general",
        description: str = "",
        capabilities: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        configuration_schema: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Register a tool in the registry.
        
        Args:
            name: Unique identifier for the tool
            version: Semantic version string
            category: Tool category (build, test, lint, etc.)
            description: Human-readable description
            capabilities: List of supported capabilities
            dependencies: List of required tools
            configuration_schema: Optional JSON schema for validation
            
        Returns:
            True if registration succeeded, False if already exists
        """
        with self._lock:
            if self._state == RegistryState.FROZEN:
                raise RuntimeError("Registry is frozen - no modifications allowed")
            
            if name in self._tools:
                return False
            
            self._tools[name] = ToolEntry(
                name=name,
                version=version,
                category=category,
                description=description,
                capabilities=capabilities or [],
                dependencies=dependencies or [],
                configuration_schema=configuration_schema,
            )
            
            return True
    
    def get(self, name: str) -> Optional[ToolEntry]:
        """Get a registered tool entry by name."""
        with self._lock:
            return self._tools.get(name)
    
    def list_by_category(self, category: str) -> List[ToolEntry]:
        """List all tools in a specific category."""
        with self._lock:
            return [
                entry for entry in self._tools.values()
                if entry.category == category
            ]
    
    def find_by_capability(self, capability: str) -> List[ToolEntry]:
        """Find all tools that support a specific capability."""
        with self._lock:
            return [
                entry for entry in self._tools.values()
                if capability in entry.capabilities
            ]
    
    def validate_dependencies(self, tool_name: str) -> bool:
        """
        Validate that all dependencies of a tool are registered.
        
        Args:
            tool_name: Name of the tool to validate
            
        Returns:
            True if all dependencies are satisfied
        """
        with self._lock:
            entry = self._tools.get(tool_name)
            if not entry:
                return False
            
            for dep in entry.dependencies:
                if dep not in self._tools:
                    return False
            
            return True
    
    def freeze(self) -> None:
        """Freeze the registry - no further modifications allowed."""
        with self._lock:
            self._state = RegistryState.FROZEN
    
    def unfreeze(self) -> None:
        """Unfreeze the registry - allow modifications again."""
        with self._lock:
            if self._state == RegistryState.SHUTDOWN:
                raise RuntimeError("Registry has been shutdown")
            self._state = RegistryState.LOADED
    
    def shutdown(self) -> Dict[str, Any]:
        """
        Shutdown the registry and return summary statistics.
        
        Returns:
            Dictionary with shutdown information
        """
        with self._lock:
            self._state = RegistryState.SHUTDOWN
            return {
                "tools_count": len(self._tools),
                "categories": list(set(e.category for e in self._tools.values())),
                "total_capabilities": sum(len(e.capabilities) for e in self._tools.values()),
            }


# =============================================================================
# BUILDER PATTERN FOR TOOL REGISTRATION
# =============================================================================

class ToolRegistryBuilder:
    """
    Builder pattern for constructing tool registry configurations.
    
    Usage:
        >>> builder = ToolRegistryBuilder()
        >>> builder.add_tool("my-tool", "1.0.0").build()
    """
    
    def __init__(self) -> None:
        """Initialize a new builder."""
        self._config: Dict[str, Any] = {}
    
    def add_tool(
        self,
        name: str,
        version: str,
        category: str = "general",
        description: str = "",
        capabilities: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        configuration_schema: Optional[Dict[str, Any]] = None,
    ) -> "ToolRegistryBuilder":
        """Add a tool configuration."""
        if name not in self._config:
            self._config[name] = {
                "version": version,
                "category": category,
                "description": description,
                "capabilities": capabilities or [],
                "dependencies": dependencies or [],
                "configuration_schema": configuration_schema,
            }
        return self
    
    def from_dict(self, config: Dict[str, Any]) -> "ToolRegistryBuilder":
        """Load configuration from a dictionary."""
        for name, data in config.items():
            self.add_tool(
                name=name,
                version=data.get("version", "0.0.0"),
                category=data.get("category", "general"),
                description=data.get("description", ""),
                capabilities=data.get("capabilities", []),
                dependencies=data.get("dependencies", []),
                configuration_schema=data.get("configuration_schema"),
            )
        return self
    
    def build(self) -> ToolRegistry:
        """Build and return a configured registry."""
        registry = ToolRegistry()
        
        for name, data in self._config.items():
            registry.register(
                name=name,
                version=data["version"],
                category=data["category"],
                description=data["description"],
                capabilities=data.get("capabilities", []),
                dependencies=data.get("dependencies", []),
                configuration_schema=data.get("configuration_schema"),
            )
        
        return registry


# =============================================================================
# CONVENIENCE EXPORTS
# =============================================================================

__all__ = [
    "ToolEntry",
    "RegistryState",
    "ToolRegistry",
    "ToolRegistryBuilder",
]