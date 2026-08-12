# Plugin Abstraction Layer - Phase 3.8.8.1
# ===========================================
"""
Canonical plugin abstractions and contracts.

Defines the core type system for plugins, extensions, and capabilities.
"""

from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Callable,
    TypeVar,
    Generic,
)
from enum import Enum, auto
import uuid
import time
from abc import ABC, abstractmethod
from typing import Set

# Import core exceptions
try:
    from ..exceptions import CoreError
except ImportError:
    class CoreError(Exception):
        pass


T = TypeVar("T")


# =============================================================================
# EXCEPTIONS (Plugin-specific)
# =============================================================================


class PluginError(CoreError):
    """Base exception for all plugin-related errors."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        plugin_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.plugin_id = plugin_id


class PluginLoadError(PluginError):
    """Raised when plugin loading fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        plugin_id: Optional[str] = None,
        phase: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, plugin_id=plugin_id, cause=cause)
        self.phase = phase


class PluginUnloadError(PluginError):
    """Raised when plugin unloading fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        plugin_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, plugin_id=plugin_id, cause=cause)


class LifecycleTransitionError(PluginError):
    """Raised when lifecycle transition is invalid."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        plugin_id: Optional[str] = None,
        from_state: Optional[PluginState] = None,
        to_state: Optional[PluginState] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, plugin_id=plugin_id, cause=cause)
        self.from_state = from_state
        self.to_state = to_state


class DuplicateRegistrationError(PluginError):
    """Raised when attempting to register a duplicate plugin."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        plugin_id: Optional[str] = None,
        existing_plugin: Optional["RegistrationRecord"] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, plugin_id=plugin_id, cause=cause)
        self.existing_plugin = existing_plugin


class MissingDependencyError(PluginError):
    """Raised when a required dependency is not available."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        plugin_id: Optional[str] = None,
        missing_dependency: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, plugin_id=plugin_id, cause=cause)
        self.missing_dependency = missing_dependency


class CircularDependencyError(MissingDependencyError):
    """Raised when a circular dependency is detected."""


class CompatibilityError(PluginError):
    """Raised when compatibility validation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        plugin_id: Optional[str] = None,
        required_version: Optional[str] = None,
        actual_version: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, plugin_id=plugin_id, cause=cause)
        self.required_version = required_version
        self.actual_version = actual_version


class CapabilityError(PluginError):
    """Raised when capability validation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        capability_id: Optional[str] = None,
        plugin_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, plugin_id=plugin_id, cause=cause)
        self.capability_id = capability_id


class ExtensionPointError(PluginError):
    """Raised when extension point operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        extension_point_id: Optional[str] = None,
        plugin_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, plugin_id=plugin_id, cause=cause)
        self.extension_point_id = extension_point_id




# =============================================================================
# PLUGIN STATE MACHINE
# =============================================================================


class PluginState(Enum):
    """
    States of the plugin lifecycle.
    
    State transitions:
        CREATED -> DISCOVERED -> REGISTERED -> LOADED -> INITIALIZED -> ACTIVE
                                                           |-> SUSPENDED (optional)
        ACTIVE -> UNLOADING -> UNLOADED
        Any state -> FAILED (on error)
    """
    
    # Pre-discovery states
    CREATED = "created"               # Plugin object instantiated
    DISCOVERED = "discovered"         # Manifest parsed, metadata available
    
    # Registration states
    REGISTERED = "registered"         # Registered with plugin registry
    VALIDATED = "validated"           # Dependencies validated
    
    # Loading states
    LOADED = "loaded"                 # Code loaded into runtime
    INITIALIZED = "initialized"       # Plugin initialized (setup completed)
    
    # Active states
    ACTIVE = "active"                 # Fully operational
    SUSPENDED = "suspended"           # Temporarily paused
    
    # Unloading states
    UNLOADING = "unloading"           # Currently being unloaded
    UNLOADED = "unloaded"             # Code removed from runtime
    
    # Error states
    FAILED = "failed"                 # Permanent failure (requires restart)
    INVALID = "invalid"               # Manifest validation failed


# =============================================================================
# PLUGIN MANIFEST
# =============================================================================


@dataclass(frozen=True)
class PluginVersion:
    """
    Immutable plugin semantic version.
    
    Follows semver 2.0.0 specification:
        MAJOR.MINOR.PATCH
    
    Example: "1.2.3" -> major=1, minor=2, patch=3
    """
    
    major: int
    minor: int = 0
    patch: int = 0
    pre_release: Optional[str] = None
    build_metadata: Optional[str] = None
    
    @classmethod
    def parse(cls, version_str: str) -> "PluginVersion":
        """Parse a semver string into a PluginVersion."""
        # Remove leading 'v' if present
        version = version_str.lstrip("v")
        
        # Split by '-'
        parts = version.split("-")
        base_version = parts[0]
        pre_release = parts[1] if len(parts) > 1 else None
        
        # Split base version by '.'
        version_parts = base_version.split(".")
        major = int(version_parts[0]) if len(version_parts) > 0 else 0
        minor = int(version_parts[1]) if len(version_parts) > 1 else 0
        patch = int(version_parts[2]) if len(version_parts) > 2 else 0
        
        return cls(
            major=major,
            minor=minor,
            patch=patch,
            pre_release=pre_release,
            build_metadata=None,  # Build metadata not parsed for simplicity
        )
    
    def __str__(self) -> str:
        """Return string representation."""
        result = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            result += f"-{self.pre_release}"
        return result
    
    def compare_to(self, other: "PluginVersion") -> int:
        """
        Compare versions (-1=self < other, 0=equal, 1=self > other).
        
        Implements semver precedence rules.
        """
        # Compare major
        if self.major != other.major:
            return -1 if self.major < other.major else 1
        
        # Compare minor
        if self.minor != other.minor:
            return -1 if self.minor < other.minor else 1
        
        # Compare patch
        if self.patch != other.patch:
            return -1 if self.patch < other.patch else 1
        
        # Both have no pre-release: equal
        if not self.pre_release and not other.pre_release:
            return 0
        
        # This has no pre-release but other does: this is greater
        if not self.pre_release and other.pre_release:
            return 1
        
        # Other has no pre-release but this does: other is greater
        if self.pre_release and not other.pre_release:
            return -1
        
        # Both have pre-release: compare lexicographically
        if self.pre_release < other.pre_release:
            return -1
        elif self.pre_release > other.pre_release:
            return 1
        
        return 0
    
    def is_compatible_with(self, other: "PluginVersion") -> bool:
        """
        Check if versions are compatible (same major version).
        
        Compatible versions can coexist and share extension contracts.
        """
        return self.major == other.major


@dataclass(frozen=True)
class PluginIdentifier:
    """Immutable identifier for a plugin."""
    
    namespace: str  # e.g., "com.company"
    name: str       # e.g., "feature-xyz"
    uuid: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    
    @classmethod
    def from_string(cls, plugin_str: str) -> "PluginIdentifier":
        """Parse 'namespace/name' string into identifier."""
        parts = plugin_str.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid plugin identifier format: {plugin_str}")
        return cls(namespace=parts[0], name=parts[1])
    
    def __str__(self) -> str:
        """Return 'namespace/name' string."""
        return f"{self.namespace}/{self.name}"
    
    @property
    def full_id(self) -> str:
        """Return fully qualified identifier with UUID."""
        return f"{self}@{self.uuid}"


@dataclass(frozen=True)
class PluginManifest:
    """
    Immutable plugin manifest - the canonical contract between plugin and core.
    
    This is the authoritative source for all plugin metadata.
    """
    
    # Identity
    id: PluginIdentifier
    version: PluginVersion
    
    # Metadata
    name: str                         # User-friendly display name
    description: str                  # Long-form description
    vendor: Optional[str] = None      # Publisher information
    url: Optional[str] = None         # Project homepage
    
    # Dependencies (what this plugin requires)
    required_capabilities: List[str] = field(default_factory=list)
    optional_capabilities: List[str] = field(default_factory=list)
    
    # Extension points this plugin contributes to
    extension_points: List[str] = field(default_factory=list)
    
    # Lifecycle configuration
    auto_load: bool = False           # Should load on startup?
    dependencies_mandatory: bool = True  # Fail if deps unmet?
    
    # Metadata timestamps
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        namespace: str,
        name: str,
        version: str,
        display_name: str,
        description: str,
    ) -> "PluginManifest":
        """Create a new plugin manifest with auto-generated IDs."""
        return cls(
            id=PluginIdentifier.from_string(f"{namespace}/{name}"),
            version=PluginVersion.parse(version),
            name=display_name,
            description=description,
        )
    
    @property
    def full_version(self) -> str:
        """Return full version string including pre-release."""
        return str(self.version)
    
    @property
    def requires_core_compatible(self) -> bool:
        """
        Check if plugin requires core compatibility validation.
        
        Plugins with major version < 2 typically require stricter compatibility.
        """
        return self.version.major < 2


@dataclass(frozen=True)
class PluginDescriptor:
    """
    Descriptor for a loaded plugin - includes runtime state.
    
    Created after manifest parsing, before actual code loading.
    """
    
    # Static metadata (from manifest)
    manifest: PluginManifest
    
    # Runtime state
    load_order: Optional[int] = None  # Position in startup sequence
    is_loaded: bool = False           # Has code been loaded?
    initialization_state: str = "pending"  # pending/initialized/failed
    
    # Discovery metadata
    source_path: Optional[str] = None   # Where was it discovered from?
    discovery_timestamp: float = field(default_factory=time.time)
    
    @classmethod
    def from_manifest(cls, manifest: PluginManifest) -> "PluginDescriptor":
        """Create descriptor from manifest."""
        return cls(manifest=manifest)


# =============================================================================
# PLUGIN CONTEXT
# =============================================================================


@dataclass
class PluginContext:
    """
    Execution context for a plugin.
    
    Provides access to core services and runtime information while maintaining
    isolation boundaries.
    """
    
    # Identity
    plugin_id: str
    plugin_version: str
    
    # Runtime environment
    runtime_id: str
    boot_session_id: str
    
    # Configuration
    configuration: Dict[str, Any] = field(default_factory=dict)
    
    # Service access (read-only interfaces to core services)
    _services: Dict[str, Any] = field(default_factory=dict)
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get a service by name."""
        return self._services.get(service_name)
    
    def has_service(self, service_name: str) -> bool:
        """Check if a service is available."""
        return service_name in self._services
    
    def add_service(self, service_name: str, service: Any) -> None:
        """Register a service with this context."""
        self._services[service_name] = service


# =============================================================================
# EXTENSION POINTS AND EXTENSIONS
# =============================================================================


class ExtensionPoint(ABC):
    """
    Abstract base for extension points.
    
    Extension points define the contract between core and plugins.
    Plugins implement these interfaces to extend core functionality.
    """
    
    @property
    @abstractmethod
    def extension_point_id(self) -> str:
        """Unique identifier for this extension point type."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Extension point API version."""
        pass


@dataclass(frozen=True)
class ExtensionDescriptor:
    """
    Descriptor for an extension implementation.
    
    Created when a plugin registers an extension with an extension point.
    """
    
    extension_id: str
    extension_point_id: str
    plugin_id: str
    
    # Extension metadata
    name: str
    description: Optional[str] = None
    
    # Priority ordering (higher = executed first)
    priority: int = 0
    
    # Enablement state
    enabled: bool = True
    
    @property
    def is_active(self) -> bool:
        """Check if extension is active."""
        return self.enabled


class Extension(Generic[T], ABC):
    """
    Base class for extensions.
    
    Plugins extend core by inheriting from appropriate Extension types.
    """
    
    @abstractmethod
    def get_extension_descriptor(self) -> ExtensionDescriptor:
        """Get the descriptor for this extension."""
        pass
    
    @property
    @abstractmethod
    def is_ready(self) -> bool:
        """Check if extension is ready to be used."""
        pass


# =============================================================================
# CAPABILITIES
# =============================================================================


@dataclass(frozen=True)
class CapabilityId:
    """Unique identifier for a capability."""
    
    domain: str  # e.g., "llm", "embeddings", "persistence"
    name: str    # e.g., "chat_completion", "text_generation"
    
    @classmethod
    def from_string(cls, cap_str: str) -> "CapabilityId":
        """Parse 'domain:name' string."""
        parts = cap_str.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid capability identifier: {cap_str}")
        return cls(domain=parts[0], name=parts[1])
    
    def __str__(self) -> str:
        """Return 'domain:name' string."""
        return f"{self.domain}:{self.name}"


@dataclass(frozen=True)
class CapabilityMetadata:
    """Metadata about a capability."""
    
    version: str
    description: Optional[str] = None
    deprecated_since: Optional[str] = None
    removed_in: Optional[str] = None
    
    @property
    def is_deprecated(self) -> bool:
        """Check if capability is deprecated."""
        return self.deprecated_since is not None
    
    @property
    def is_removed(self) -> bool:
        """Check if capability is removed."""
        return self.removed_in is not None


@dataclass(frozen=True)
class CapabilityDeclaration:
    """
    Declaration of capabilities provided by a plugin.
    
    This is the contract - what the plugin claims to support.
    """
    
    # Standard capabilities
    chat_completion: bool = False
    text_generation: bool = False
    embeddings: bool = False
    vision: bool = False
    
    # Additional capability flags
    streaming: bool = False
    tool_calling: bool = False
    structured_output: bool = False
    
    # Custom capabilities (free-form)
    custom: Dict[str, Any] = field(default_factory=dict)
    
    def has_capability(self, capability_id: CapabilityId) -> bool:
        """Check if this declaration includes a specific capability."""
        if capability_id.domain == "llm" and capability_id.name == "chat_completion":
            return self.chat_completion
        if capability_id.domain == "llm" and capability_id.name == "text_generation":
            return self.text_generation
        if capability_id.domain == "embeddings" and capability_id.name == "embeddings":
            return self.embeddings
        if capability_id.domain == "vision" and capability_id.name == "vision":
            return self.vision
        
        # Check custom capabilities
        return capability_id.name in self.custom
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert declaration to dictionary."""
        result = {
            "chat_completion": self.chat_completion,
            "text_generation": self.text_generation,
            "embeddings": self.embeddings,
            "vision": self.vision,
            "streaming": self.streaming,
            "tool_calling": self.tool_calling,
            "structured_output": self.structured_output,
            "streaming": self.streaming,
        }
        result.update(self.custom)
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CapabilityDeclaration":
        """Create declaration from dictionary."""
        return cls(
            chat_completion=data.get("chat_completion", False),
            text_generation=data.get("text_generation", False),
            embeddings=data.get("embeddings", False),
            vision=data.get("vision", False),
            streaming=data.get("streaming", False),
            tool_calling=data.get("tool_calling", False),
            structured_output=data.get("structured_output", False),
            custom={k: v for k, v in data.items() 
                    if k not in ["chat_completion", "text_generation", 
                               "embeddings", "vision", "streaming",
                               "tool_calling", "structured_output"]},
        )


# =============================================================================
# CAPABILITY CLASS
# =============================================================================


@dataclass(frozen=True)
class Capability:
    """
    A capability offered by a plugin.
    
    Capabilities are the fundamental unit of plugin functionality that can be
    discovered, queried, and negotiated between plugins and core.
    """
    
    # Identity
    id: CapabilityId
    
    # Version info
    version: PluginVersion
    
    # Metadata
    name: str
    description: Optional[str] = None
    
    # Provider information
    provider_id: Optional[str] = None
    priority: int = 0  # Higher = preferred (for capability negotiation)
    
    # Lifecycle state
    enabled: bool = True
    available: bool = True
    
    @property
    def full_name(self) -> str:
        """Return fully qualified capability name."""
        return f"{self.id.domain}:{self.id.name}@{str(self.version)}"
    
    def is_compatible_with(self, required_version: PluginVersion) -> bool:
        """
        Check if this capability satisfies a version requirement.
        
        A capability is compatible if:
        - Major versions match (breaking changes require new major version)
        - Capability version >= required version
        """
        if self.version.major != required_version.major:
            return False
        return self.version.compare_to(required_version) >= 0
    
    def to_descriptor(self) -> "CapabilityDescriptor":
        """Convert capability to descriptor."""
        return CapabilityDescriptor(
            id=self.id,
            version=str(self.version),
            name=self.name,
            description=self.description,
            provider_id=self.provider_id,
            priority=self.priority,
            enabled=self.enabled,
            available=self.available,
        )


@dataclass(frozen=True)
class CapabilityDescriptor:
    """
    Descriptor for a capability - simplified view for registration.
    
    Used when registering capabilities without exposing full plugin context.
    """
    
    id: CapabilityId
    version: str
    name: str
    description: Optional[str] = None
    
    provider_id: Optional[str] = None
    priority: int = 0
    
    enabled: bool = True
    available: bool = True


# =============================================================================
# PLUGIN BASE CLASS
# =============================================================================


class Plugin(ABC):
    """
    Abstract base class for all plugins.
    
    Plugins implement this interface to integrate with the core plugin system.
    Each plugin must provide a manifest and can optionally implement lifecycle hooks.
    
    Lifecycle Methods:
        - initialize(context): Called once after loading, before activation
        - activate(): Called when plugin becomes active
        - suspend(): Called when plugin is temporarily suspended
        - resume(): Called when plugin resumes from suspension
        - deactivate(): Called when plugin is deactivated
        - unload(): Called when plugin code is being unloaded
    
    State Machine:
        CREATED -> DISCOVERED -> REGISTERED -> LOADED -> INITIALIZED
            -> ACTIVE <-> SUSPENDED
            -> UNLOADING -> UNLOADED
    """
    
    def __init__(self, context: PluginContext):
        self._context = context
        self._state = PluginState.CREATED
    
    @property
    @abstractmethod
    def manifest(self) -> PluginManifest:
        """Get the plugin manifest."""
        pass
    
    @property
    def state(self) -> PluginState:
        """Get current plugin state."""
        return self._state
    
    @property
    def context(self) -> PluginContext:
        """Get the plugin context."""
        return self._context
    
    # -------------------------------------------------------------------------
    # Lifecycle Methods (can be overridden by plugins)
    # -------------------------------------------------------------------------
    
    async def initialize(self, context: PluginContext) -> None:
        """
        Initialize the plugin after loading.
        
        Called once, immediately after code is loaded but before activation.
        Use this for setup that must happen before the plugin becomes active.
        
        Args:
            context: The plugin execution context
            
        Raises:
            PluginError: If initialization fails
        """
        pass
    
    async def activate(self) -> None:
        """
        Activate the plugin - make it operational.
        
        Called when the plugin transitions to ACTIVE state.
        This is where plugins should start their main functionality.
        """
        self._state = PluginState.ACTIVE
    
    async def suspend(self) -> None:
        """
        Suspend the plugin temporarily.
        
        The plugin should pause its operations but keep state in memory.
        It can be resumed later with resume().
        """
        self._state = PluginState.SUSPENDED
    
    async def resume(self) -> None:
        """Resume from suspension."""
        if self._state == PluginState.SUSPENDED:
            self._state = PluginState.ACTIVE
    
    async def deactivate(self) -> None:
        """
        Deactivate the plugin.
        
        Called before unload. Plugins should stop all operations and release
        any resources that don't need to persist across reloads.
        """
        if self._state == PluginState.SUSPENDED:
            self._state = PluginState.ACTIVE  # Resume first
        elif self._state != PluginState.ACTIVE:
            return
        self._state = PluginState.UNLOADING
    
    async def unload(self) -> None:
        """Clean up and prepare for unloading."""
        self._state = PluginState.UNLOADED
    
    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------
    
    def get_capability(self, capability_name: str) -> Optional[Capability]:
        """
        Get a capability by name.
        
        Plugins should override this to expose their capabilities.
        Default implementation returns None (no capabilities).
        
        Args:
            capability_name: Name of the capability
            
        Returns:
            Capability if available, None otherwise
        """
        return None
    
    def get_capabilities(self) -> List[Capability]:
        """
        Get all capabilities provided by this plugin.
        
        Plugins should override to expose their capabilities.
        Default implementation returns empty list.
        
        Returns:
            List of capability objects
        """
        return []
    
    # -------------------------------------------------------------------------
    # State Queries
    # -------------------------------------------------------------------------
    
    def is_initialized(self) -> bool:
        """Check if plugin has been initialized."""
        return self._state in (
            PluginState.INITIALIZED,
            PluginState.ACTIVE,
            PluginState.SUSPENDED,
        )
    
    def is_active(self) -> bool:
        """Check if plugin is active."""
        return self._state == PluginState.ACTIVE
    
    def is_suspended(self) -> bool:
        """Check if plugin is suspended."""
        return self._state == PluginState.SUSPENDED


# =============================================================================
# EXTENSION IMPLEMENTATION BASE
# =============================================================================


class ExtensionImpl(Extension[T]):
    """
    Base implementation of an extension.
    
    Plugins extending core functionality should inherit from this class and
    implement the required abstract methods.
    
    Args:
        extension_id: Unique identifier for this extension
        extension_point_id: The extension point being implemented
        plugin_id: ID of the plugin providing this extension
    """
    
    def __init__(
        self,
        extension_id: str,
        extension_point_id: str,
        plugin_id: str,
    ):
        self._extension_id = extension_id
        self._extension_point_id = extension_point_id
        self._plugin_id = plugin_id
    
    @property
    def is_ready(self) -> bool:
        """Check if extension is ready to be used."""
        return True
    
    def get_extension_descriptor(self) -> ExtensionDescriptor:
        """Get the descriptor for this extension."""
        return ExtensionDescriptor(
            extension_id=self._extension_id,
            extension_point_id=self._extension_point_id,
            plugin_id=self._plugin_id,
            name=self.__class__.__name__,
            description=None,
            priority=0,
            enabled=True,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_plugin_context(
    runtime_id: str,
    boot_session_id: str,
) -> PluginContext:
    """
    Create a default plugin context.
    
    Args:
        runtime_id: The running runtime ID
        boot_session_id: The current boot session ID
        
    Returns:
        A new PluginContext instance
    """
    return PluginContext(
        plugin_id="core",
        plugin_version="3.8.8",
        runtime_id=runtime_id,
        boot_session_id=boot_session_id,
    )


def validate_manifest(manifest: PluginManifest) -> bool:
    """
    Validate a plugin manifest.
    
    Checks that all required fields are present and valid.
    
    Args:
        manifest: The manifest to validate
        
    Returns:
        True if valid, raises exception otherwise
    """
    # Check required fields
    if not manifest.id or not str(manifest.id):
        raise ValueError("Plugin must have a valid identifier")
    
    if not manifest.version:
        raise ValueError("Plugin must have a version")
    
    if not manifest.name:
        raise ValueError("Plugin must have a name")
    
    if not manifest.description:
        raise ValueError("Plugin must have a description")
    
    # Validate version format
    try:
        str(manifest.version)
    except Exception as e:
        raise ValueError(f"Invalid version format: {e}")
    
    return True


__all__ = [
    # State machine
    "PluginState",
    
    # Manifest types
    "PluginVersion",
    "PluginIdentifier",
    "PluginManifest",
    "PluginDescriptor",
    
    # Context and runtime
    "PluginContext",
    
    # Extension system
    "ExtensionPoint",
    "ExtensionDescriptor",
    "Extension",
    
    # Capabilities
    "CapabilityId",
    "CapabilityMetadata",
    "CapabilityDeclaration",
    "Capability",
    "CapabilityDescriptor",
    
    # Plugin base class
    "Plugin",
    "ExtensionImpl",
    
    # Exceptions
    "PluginError",
    "PluginLoadError",
    "PluginUnloadError",
    "LifecycleTransitionError",
    "DuplicateRegistrationError",
    "MissingDependencyError",
    "CircularDependencyError",
    "CompatibilityError",
    "CapabilityError",
    "ExtensionPointError",
    
    # Utilities
    "create_plugin_context",
    "validate_manifest",
]
