"""Reflection Infrastructure - Core Architecture Phase 3.12.7.
================================================================================

Canonical Reflection, Metadata & Discovery Architecture for Gordon Core.

ARCHITECTURAL PRINCIPLES:
- Reflection is passive - it observes but never modifies
- Metadata is immutable - once captured, it cannot change  
- Discovery determines location without instantiation
- Registries organize and index - they don't create

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

# Core versions and metadata
__version__ = "1.0.0"
__phase__ = "3.12.7"

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
    DependencyAnalysis,
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
    "DependencyAnalysis",
    "DependencyInspector",
    "topologically_sort_dependencies",
    
    # Discovery
    "DiscoveryResult",
    "DiscoverySession", 
    "DiscoveryService",
    "discover_packages",
    "discover_modules",
    "discover_runtime_authorities",
]