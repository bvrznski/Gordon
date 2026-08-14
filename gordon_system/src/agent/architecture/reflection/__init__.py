"""Reflection Infrastructure - Core Architecture Phase 3.23.
================================================================================

Canonical Reflection, Metadata & Introspection Architecture for Gordon Core.

PHILOSOPHY:
- Reflection describes what exists (not what happens)
- Metadata is structured, typed, and discoverable
- One canonical system for the entire repository
- No implementation details exposed in metadata

REFLECTION RESPONSIBILITIES:
- Architectural introspection (what exists?)
- Repository discovery (where is it located?)
- Metadata access (how is it described?)
- Ownership inspection (who owns it?)
- Dependency inspection (what does it depend on?)
- Topology inspection (how are things connected?)

Reflection NEVER owns:
- Execution scheduling
- Semantic interpretation  
- Runtime state modification
- Component instantiation

"""
__version__ = "1.0.0"
__phase__ = "3.23"

# =============================================================================
# INVENTORY MODELS - Import from discovery (canonical source)
# =============================================================================

from ..discovery.inventory import (
    # Core models  
    ArchitectureInventory,
    PackageMetadata,
    ModuleMetadata,
    APIItem,
    RuntimeAuthority,
    
    # Graph models
    DependencyEdge, 
    DependencyGraph,
    ImportEdge,
    TopologyNode,
    TopologyEdge,
    
    # Entry point models
    EntryPoint,
    BackgroundExecution,
    
    # Enumerations
    PackageCategory,
    APIType,
    LifecycleParticipation,
)

# =============================================================================
# OWNERSHIP INSPECTION - Own implementation
# =============================================================================

from .ownership import (
    OwnerInfo,
    PackageOwnership,
    ModuleOwnership, 
    RuntimeOwnership,
    OwnershipGraph,
    OwnershipInspector,
    detect_ownership_gaps,
    validate_ownership_matrix,
)

# =============================================================================
# TOPOLOGY INSPECTION - Own implementation  
# =============================================================================

from .topology import (
    TopologyPathFinder,
    TopologySummary,
    TopologyAnalysis,
    TopologyReport,
    TopologyInspector,
    compute_topology_metrics,
)

# =============================================================================
# DEPENDENCY INSPECTION - Own implementation
# =============================================================================

from .dependency_inspector import (
    CycleInfo,
    DependencyReport,
    DependencyInspector,
    topologically_sort_dependencies,
)

# =============================================================================
# DISCOVERY SERVICE - Own implementation  
# =============================================================================

from .discovery import (
    DiscoveryResult,
    DiscoverySession,
    DiscoveryService,
    discover_packages,
    discover_modules,
    discover_runtime_authorities,
)

# =============================================================================
# REGISTRY & MANIFEST - Phase 3.23
# =============================================================================

from .registry import (
    # Enumerations
    RegistryType,
    RegistryScope,
    
    # Entry models
    RegistryEntry,
    ManifestEntry,
    
    # Registry models
    EntityMetadataRegistry,
    CapabilityRegistry,
    
    # Audit models
    AuditRecord,
    AuditLog,
    
    # Builder
    RegistryBuilder,
    
    # Operations
    create_entity_metadata_registry_from_inventory,
    create_manifest,
)

# =============================================================================
# NEW PHASE 3.23 METADATA EXPORTS
# =============================================================================

from .metadata import (
    # Versioning & Provenance
    MetadataVersion,
    Provenance,
    
    # Identity metadata
    IdentityMetadata,
    OwnerMetadata,
    OwnershipMetadata,
    
    # Versioning & lifecycle
    VersionMetadata,
    LifecyclePhase,
    LifecycleMetadata,
    
    # Capability metadata
    CapabilityType,
    CapabilityMetadata,
    
    # Interface metadata
    InterfaceContract,
    InterfaceMetadata,
    
    # Dependency metadata
    DependencyType,
    DependencyMetadata,
    
    # Security metadata
    SecurityClassification,
    SecurityMetadata,
    
    # Configuration metadata
    ConfigOption,
    ConfigurationMetadata,
    
    # Execution metadata
    ExecutionMode,
    ExecutionMetadata,
    
    # Diagnostic metadata
    DiagnosticType,
    DiagnosticMetadata,
    
    # Documentation metadata
    DocumentationMetadata,
    
    # Complete metadata
    EntityMetadata,
    MetadataBuilder,
)

__all__ = [
    # Inventory models (canonical source: discovery module)
    "ArchitectureInventory",
    "PackageMetadata", 
    "ModuleMetadata",
    "APIItem",
    "RuntimeAuthority",
    "DependencyEdge",
    "DependencyGraph",
    "ImportEdge",
    "TopologyNode",
    "TopologyEdge",
    "EntryPoint",
    "BackgroundExecution",
    "PackageCategory",
    "APIType",
    "LifecycleParticipation",
    
    # Ownership
    "OwnerInfo",
    "PackageOwnership",
    "ModuleOwnership", 
    "RuntimeOwnership",
    "OwnershipGraph",
    "OwnershipInspector",
    "detect_ownership_gaps",
    "validate_ownership_matrix",
    
    # Topology
    "TopologyPathFinder",
    "TopologySummary",
    "TopologyAnalysis",
    "TopologyReport",
    "TopologyInspector",
    "compute_topology_metrics",
    
    # Dependency
    "CycleInfo", 
    "DependencyReport",
    "DependencyInspector",
    "topologically_sort_dependencies",
    
    # Discovery
    "DiscoveryResult",
    "DiscoverySession", 
    "DiscoveryService",
    "discover_packages",
    "discover_modules",
    "discover_runtime_authorities",
    
    # PHASE 3.23 REGISTRY & MANIFEST EXPORTS
    "RegistryType",
    "RegistryScope",
    "RegistryEntry",
    "ManifestEntry",
    "EntityMetadataRegistry",
    "CapabilityRegistry",
    "AuditRecord",
    "AuditLog",
    "RegistryBuilder",
    "create_entity_metadata_registry_from_inventory",
    "create_manifest",
    
    # PHASE 3.23 METADATA EXPORTS
    # Versioning & Provenance
    "MetadataVersion",
    "Provenance",
    # Identity metadata
    "IdentityMetadata",
    "OwnerMetadata",
    "OwnershipMetadata",
    # Versioning & lifecycle
    "VersionMetadata",
    "LifecyclePhase",
    "LifecycleMetadata",
    # Capability metadata
    "CapabilityType",
    "CapabilityMetadata",
    # Interface metadata
    "InterfaceContract",
    "InterfaceMetadata",
    # Dependency metadata
    "DependencyType",
    "DependencyMetadata",
    # Security metadata
    "SecurityClassification",
    "SecurityMetadata",
    # Configuration metadata
    "ConfigOption",
    "ConfigurationMetadata",
    # Execution metadata
    "ExecutionMode",
    "ExecutionMetadata",
    # Diagnostic metadata
    "DiagnosticType",
    "DiagnosticMetadata",
    # Documentation metadata
    "DocumentationMetadata",
    # Complete metadata
    "EntityMetadata",
    "MetadataBuilder",
]
