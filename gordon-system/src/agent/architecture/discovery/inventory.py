"""Architecture Inventory Models.

Defines immutable, deterministic data structures for representing
discovered architecture metadata.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import time


# =============================================================================
# ENUMERATIONS
# =============================================================================


class PackageCategory(Enum):
    """Categories of packages in the Gordon Core system."""
    
    # Architectural layers
    CORE = "core"
    KERNEL = "kernel"
    RUNTIME = "runtime"
    EXECUTION = "execution"
    INFRASTRUCTURE = "infrastructure"
    OBSERVABILITY = "observability"
    RECOVERY = "recovery"
    COMPATIBILITY = "compatibility"
    TESTING = "testing"
    LEGACY = "legacy"
    
    # Unknown / unclassified
    UNKNOWN = "unknown"


class APIType(Enum):
    """Types of public API items."""
    
    CLASS = "class"
    FUNCTION = "function"
    PROTOCOL = "protocol"
    CONSTANT = "constant"
    DATACLASS = "dataclass"
    ENUM = "enum"
    ABC = "abstract_base_class"
    SERVICE = "service"
    REGISTRY = "registry"
    SCHEDULER = "scheduler"
    BUILDER = "builder"
    FACTORY = "factory"


class LifecycleParticipation(Enum):
    """How a module participates in the lifecycle."""
    
    NONE = "none"
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    FULL_LIFECYCLE = "full_lifecycle"


# =============================================================================
# CORE INVENTORY MODELS
# =============================================================================


@dataclass(frozen=True)
class PackageMetadata:
    """
    Metadata about a package in the architecture.
    
    This is the authoritative source of package information,
    including ownership, purpose, and architectural classification.
    """
    
    # Identity (required - no defaults)
    name: str
    path: str
    
    # Architectural classification (required - no defaults)
    category: PackageCategory
    layer: str  # e.g., "Phase 0", "Phase 1", "Phase 2"
    
    # Ownership (optional with defaults)
    owner: str = "Unknown"  # Team or individual responsible
    contact: Optional[str] = None
    
    # Purpose (optional with defaults)
    description: str = ""
    purpose: str = ""  # Detailed description of what this package does
    responsibility: str = ""  # What this package is responsible for
    
    # Public facade
    public_api: Tuple[str, ...] = field(default_factory=tuple)
    
    # Dependencies (package-level)
    dependencies: Set[str] = field(default_factory=set)
    optional_dependencies: Set[str] = field(default_factory=set)
    
    # Lifecycle participation
    lifecycle_participation: LifecycleParticipation = LifecycleParticipation.NONE
    
    # Version and stability
    version: str = "1.0.0"
    stability: str = "stable"  # stable, beta, experimental
    
    # Metadata
    extension_points: List[str] = field(default_factory=list)
    compatibility_notes: Optional[str] = None
    deprecated: bool = False
    deprecation_reason: Optional[str] = None


@dataclass(frozen=True)
class ModuleMetadata:
    """
    Metadata about a module within a package.
    
    Captures responsibility, imports, exports, and runtime participation.
    """
    
    # Identity
    name: str
    path: str
    package_name: str
    
    # Ownership
    owner: Optional[str] = None
    
    # Responsibility
    purpose: str = ""
    responsibility: str = ""
    
    # Imports (module-level)
    imports: Set[str] = field(default_factory=set)
    external_imports: Set[str] = field(default_factory=set)
    internal_imports: Set[str] = field(default_factory=set)
    
    # Exports
    exports: Tuple[str, ...] = field(default_factory=tuple)
    public_api: Tuple[str, ...] = field(default_factory=tuple)
    private_api: Tuple[str, ...] = field(default_factory=tuple)
    
    # API inventory
    classes: Set[str] = field(default_factory=set)
    functions: Set[str] = field(default_factory=set)
    protocols: Set[str] = field(default_factory=set)
    dataclasses: Set[str] = field(default_factory=set)
    enums: Set[str] = field(default_factory=set)
    
    # Runtime participation
    mutable_globals: Set[str] = field(default_factory=set)
    singletons: Set[str] = field(default_factory=set)
    
    # Lifecycle participation
    lifecycle_participation: LifecycleParticipation = LifecycleParticipation.NONE
    
    # Health, recovery, startup, shutdown participation
    health_participation: bool = False
    recovery_participation: bool = False
    startup_participation: bool = False
    shutdown_participation: bool = False


@dataclass(frozen=True)
class APIItem:
    """
    A single public API item discovered in a module.
    
    Represents classes, functions, protocols, and other exported symbols.
    """
    
    # Identity
    name: str
    type_: APIType
    
    # Defining package
    defining_package: str
    
    # Metadata
    owner: Optional[str] = None
    version: str = "1.0.0"
    deprecated: bool = False
    deprecation_reason: Optional[str] = None
    
    # Documentation
    description: Optional[str] = None
    parameters: List[Tuple[str, Optional[str]]] = field(default_factory=list)
    
    # Usage tracking (consumers)
    consumers: Set[str] = field(default_factory=set)


@dataclass(frozen=True)
class RuntimeAuthority:
    """
    A canonical runtime authority discovered in the system.
    
    Authorities are single points of responsibility for specific aspects
    of runtime behavior.
    """
    
    # Identity
    name: str
    category: str  # e.g., "Runtime", "Execution", "Recovery"
    
    # Implementation details
    implementation: str  # Fully qualified class name
    owner: str
    
    # Public interface
    public_interface: Tuple[str, ...] = field(default_factory=tuple)
    
    # Dependencies
    dependencies: Set[str] = field(default_factory=set)
    optional_dependencies: Set[str] = field(default_factory=set)
    
    # Runtime scope
    scope: str = "runtime"  # runtime, operation, request, singleton
    
    # Metadata
    description: Optional[str] = None
    stability: str = "stable"
    version: str = "1.0.0"


@dataclass(frozen=True)
class DependencyEdge:
    """
    A dependency relationship between two entities.
    
    Represents both compile-time and runtime dependencies.
    """
    
    from_entity: str  # The dependent entity
    to_entity: str    # The dependency target
    
    type_: str = "runtime"  # runtime, construction, activation, shutdown, optional
    required: bool = True


@dataclass(frozen=True)
class DependencyGraph:
    """
    A complete dependency graph for a module or package.
    
    Supports topological sorting and cycle detection.
    """
    
    edges: Tuple[DependencyEdge, ...]
    
    @property
    def vertices(self) -> Set[str]:
        """Get all unique vertices in the graph."""
        result: Set[str] = set()
        for edge in self.edges:
            result.add(edge.from_entity)
            result.add(edge.to_entity)
        return result
    
    def get_dependencies(self, entity: str) -> List[str]:
        """Get entities that the given entity depends on."""
        return [e.to_entity for e in self.edges if e.from_entity == entity]
    
    def get_dependents(self, entity: str) -> List[str]:
        """Get entities that depend on the given entity."""
        return [e.from_entity for e in self.edges if e.to_entity == entity]


@dataclass(frozen=True)
class ImportEdge:
    """
    An import relationship between modules.
    
    Captures both direct and transitive imports.
    """
    
    from_module: str  # The importing module
    to_module: str    # The imported module
    
    type_: str = "direct"  # direct, transitive, runtime
    optional: bool = False


@dataclass(frozen=True)
class TopologyNode:
    """
    A node in the runtime topology graph.
    
    Represents entities like kernels, services, schedulers, etc.
    """
    
    id: str
    name: str
    category: str  # e.g., "Kernel", "Service", "Scheduler"
    type_: str     # e.g., "class", "instance"
    
    # Metadata
    owner: Optional[str] = None
    version: str = "1.0.0"
    
    # Runtime properties
    scope: str = "runtime"  # runtime, operation, request
    lifecycle_state: str = "unknown"  # created, initialized, running, stopped


@dataclass(frozen=True)
class TopologyEdge:
    """
    An edge in the runtime topology graph.
    
    Represents relationships like dependency, communication, ownership.
    """
    
    from_node: str
    to_node: str
    
    type_: str = "dependency"  # dependency, communication, ownership


@dataclass(frozen=True)
class EntryPoint:
    """
    An entry point in the system.
    
    Represents executable code paths that start execution.
    """
    
    name: str
    path: str  # Module path + function/method name
    
    type_: str = "executable"  # executable, daemon, cli, builder, startup_path, shutdown_path
    
    # Metadata
    owner: Optional[str] = None
    description: Optional[str] = None


@dataclass(frozen=True)
class BackgroundExecution:
    """
    Information about background execution in the system.
    
    Captures threads, async tasks, schedulers, timers, etc.
    """
    
    name: str
    location: str  # Module path where it's defined
    
    type_: str = "thread"  # thread, async_task, scheduler, timer, poller, worker, idle_loop
    
    owner: Optional[str] = None
    lifecycle_participation: LifecycleParticipation = LifecycleParticipation.NONE


# =============================================================================
# MAIN INVENTORY CONTAINER
# =============================================================================


@dataclass(frozen=True)
class ArchitectureInventory:
    """
    Complete architecture inventory of the system.
    
    This is the immutable, deterministic result of discovery operations.
    All metadata is captured at a specific point in time and never modified.
    """
    
    # Discovery metadata (required - no defaults)
    repository_path: str
    discovered_at: float  # monotonic timestamp
    
    # Required tuples (no defaults) - must come before optional fields
    packages: Tuple[PackageMetadata, ...]
    
    # Modules (flattened view)
    modules: Tuple[ModuleMetadata, ...]
    
    # API inventory
    public_apis: Tuple[APIItem, ...]
    
    # Runtime authorities
    runtime_authorities: Tuple[RuntimeAuthority, ...]
    
    # Dependency graphs
    package_dependencies: DependencyGraph
    runtime_dependencies: DependencyGraph
    
    # Import graph
    import_graph_edges: Tuple[ImportEdge, ...]
    
    # Topology
    topology_nodes: Tuple[TopologyNode, ...]
    topology_edges: Tuple[TopologyEdge, ...]
    
    # Entry points and background execution
    entry_points: Tuple[EntryPoint, ...]
    background_execution: Tuple[BackgroundExecution, ...]
    
    # Version and metadata (optional with defaults)
    version: str = "1.0.0"
    
    # Metrics summary (counts)
    total_packages: int = 0
    total_modules: int = 0
    total_classes: int = 0
    total_functions: int = 0
    total_protocols: int = 0
    total_dataclasses: int = 0
    total_enums: int = 0
    total_authorities: int = 0
    
    def get_package(self, name: str) -> Optional[PackageMetadata]:
        """Get package metadata by name."""
        for pkg in self.packages:
            if pkg.name == name:
                return pkg
        return None
    
    def get_module(self, path: str) -> Optional[ModuleMetadata]:
        """Get module metadata by path."""
        for mod in self.modules:
            if mod.path == path:
                return mod
        return None
    
    def filter_packages_by_category(self, category: PackageCategory) -> Tuple[PackageMetadata, ...]:
        """Filter packages by category."""
        return tuple(p for p in self.packages if p.category == category)
    
    def filter_modules_by_package(self, package_name: str) -> Tuple[ModuleMetadata, ...]:
        """Filter modules by package name."""
        return tuple(m for m in self.modules if m.package_name == package_name)