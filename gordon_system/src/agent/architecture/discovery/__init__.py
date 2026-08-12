"""Architecture Discovery Framework.

Provides deterministic, repository-driven architecture discovery capabilities for Gordon Core.
"""

# Version
__version__ = "1.0.0"

# Discovery framework exports
from .inventory import (
    ArchitectureInventory,
    PackageMetadata,
    ModuleMetadata,
    APIItem,
    PackageCategory,
    APIType,
    LifecycleParticipation,
)
from .package_manager import PackageDiscoveryManager
from .module_manager import ModuleDiscoveryManager
from .authority_manager import AuthorityDiscoveryManager, RuntimeAuthority
from .dependency_manager import DependencyDiscoveryManager, DependencyGraph
from .import_graph import ImportGraphManager, ImportEdge
from .topology_manager import RuntimeTopologyManager, TopologyNode, TopologyEdge
from .report_manager import ArchitectureReportManager
from .metrics_manager import MetricsManager

__all__ = [
    # Inventory
    "ArchitectureInventory",
    "PackageMetadata",
    "ModuleMetadata",
    "APIItem",
    "PackageCategory",
    "APIType",
    "LifecycleParticipation",
    
    # Managers
    "PackageDiscoveryManager",
    "ModuleDiscoveryManager",
    "AuthorityDiscoveryManager",
    "DependencyDiscoveryManager",
    "ImportGraphManager",
    "RuntimeTopologyManager",
    "ArchitectureReportManager",
    "MetricsManager",
    
    # Models
    "RuntimeAuthority",
    "DependencyGraph",
    "ImportEdge",
    "TopologyNode",
    "TopologyEdge",
]
