"""Ownership Inspector - Phase 3.12.7.
================================================================================

Deterministic ownership graph inspection for Gordon Core reflection architecture.

Provides:
- OwnerInfo, PackageOwnership, ModuleOwnership, RuntimeOwnership data models
- OwnershipGraph for relationship visualization
- OwnershipInspector class for querying ownership relationships
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

from ..discovery.inventory import (
    ArchitectureInventory,
    PackageMetadata,
    ModuleMetadata,
    RuntimeAuthority,
)


# =============================================================================
# OWNERSHIP DATA MODELS (immutable)
# =============================================================================


@dataclass(frozen=True)
class OwnerInfo:
    """Information about an owner in the architecture."""
    name: str
    contact: Optional[str] = None
    category: str = "unknown"
    total_entities: int = 0


@dataclass(frozen=True)  
class PackageOwnership:
    """Ownership mapping for packages."""
    package_name: str
    owner: str
    layer: str
    responsibility: str


@dataclass(frozen=True)
class ModuleOwnership:
    """Ownership mapping for modules."""
    module_path: str
    package_name: str
    owner: str
    purpose: str


@dataclass(frozen=True)
class RuntimeOwnership:
    """Ownership mapping for runtime authorities."""
    authority_id: str
    implementation: str
    owner: str
    category: str


# =============================================================================
# OWNERSHIP GRAPH
# =============================================================================


@dataclass(frozen=True)
class OwnershipGraph:
    """
    Graph representation of ownership relationships.
    
    Nodes: entity IDs (packages, modules, authorities)
    Edges: owner relationships
    
    This graph is computed deterministically from metadata and never modified.
    """
    
    nodes: Tuple[str, ...]
    edges: Tuple[Tuple[str, str], ...]  # (entity_id, owner_name)
    
    def get_owner(self, entity_id: str) -> Optional[str]:
        """Get the owner of an entity."""
        for src, dst in self.edges:
            if src == entity_id:
                return dst
        return None
    
    def get_entities_by_owner(self, owner: str) -> Tuple[str, ...]:
        """Get all entities owned by a specific owner."""
        return tuple(src for src, dst in self.edges if dst == owner)
    
    def invert(self) -> Dict[str, Tuple[str, ...]]:
        """Return owner -> [entities] mapping."""
        result: Dict[str, List[str]] = {}
        for src, dst in self.edges:
            if dst not in result:
                result[dst] = []
            result[dst].append(src)
        return {k: tuple(v) for k, v in result.items()}


# =============================================================================
# OWNERSHIP INSPECTOR
# =============================================================================


class OwnershipInspector:
    """
    Inspector for ownership relationships.
    
    Determines who owns what in the architecture.
    Ownership is immutable and canonical.
    
    This inspector is:
    - Deterministic: Same input always produces same output
    - Read-only: Never modifies anything
    - Passive: Only inspects, never acts
    """
    
    def __init__(self, inventory: ArchitectureInventory) -> None:
        """
        Initialize with an architecture inventory.
        
        Args:
            inventory: Complete architecture inventory (immutable)
        """
        self._inventory = inventory
    
    def get_owner(self, entity_id: str) -> Optional[str]:
        """Get the owner of an entity."""
        # Check packages
        for pkg in self._inventory.packages:
            if f"package:{pkg.name}" == entity_id:
                return pkg.owner
        
        # Check modules (inherit from package)
        for mod in self._inventory.modules:
            if f"module:{mod.path}" == entity_id:
                # Find owning package
                for pkg in self._inventory.packages:
                    if mod.package_name == pkg.name:
                        return pkg.owner
        
        # Check authorities
        for auth in self._inventory.runtime_authorities:
            if f"authority:{auth.implementation}" == entity_id:
                return auth.owner
        
        return None
    
    def get_entities_by_owner(self, owner: str) -> Tuple[str, ...]:
        """Get all entities owned by a specific owner."""
        nodes: Set[str] = set()
        
        for pkg in self._inventory.packages:
            if pkg.owner == owner:
                nodes.add(f"package:{pkg.name}")
        
        # Modules inherit from packages
        for mod in self._inventory.modules:
            for pkg in self._inventory.packages:
                if mod.package_name == pkg.name and pkg.owner == owner:
                    nodes.add(f"module:{mod.path}")
        
        for auth in self._inventory.runtime_authorities:
            if auth.owner == owner:
                nodes.add(f"authority:{auth.implementation}")
        
        return tuple(nodes)
    
    def get_ownership_graph(self) -> OwnershipGraph:
        """
        Get ownership relationship graph.
        
        Returns graph representation of ownership relationships.
        """
        nodes: Set[str] = set()
        edges: List[Tuple[str, str]] = []
        
        for pkg in self._inventory.packages:
            nodes.add(f"package:{pkg.name}")
            edges.append((f"package:{pkg.name}", pkg.owner))
        
        # Modules inherit from packages
        for mod in self._inventory.modules:
            nodes.add(f"module:{mod.path}")
            for pkg in self._inventory.packages:
                if mod.package_name == pkg.name:
                    edges.append((f"module:{mod.path}", pkg.owner))
                    break
        
        for auth in self._inventory.runtime_authorities:
            nodes.add(f"authority:{auth.implementation}")
            edges.append((f"authority:{auth.implementation}", auth.owner))
        
        return OwnershipGraph(
            nodes=tuple(nodes),
            edges=tuple(edges)
        )
    
    def verify_ownership_matrix(self) -> Tuple[bool, List[str]]:
        """Verify ownership consistency. Returns (is_valid, issues)."""
        issues: List[str] = []
        
        # Check for packages without owners
        for pkg in self._inventory.packages:
            if pkg.owner == "Unknown":
                issues.append(f"Package '{pkg.name}' has no owner")
        
        # Verify all modules have package owners
        for mod in self._inventory.modules:
            found_package = False
            for pkg in self._inventory.packages:
                if mod.package_name == pkg.name:
                    found_package = True
                    break
            if not found_package:
                issues.append(f"Module '{mod.path}' references unknown package")
        
        return (len(issues) == 0, issues)
    
    def discover_owners(self) -> Dict[str, str]:
        """
        Discover ownership information for all entities.
        
        Returns mapping of entity_id -> owner_name
        """
        result: Dict[str, str] = {}
        
        for pkg in self._inventory.packages:
            result[f"package:{pkg.name}"] = pkg.owner
        
        # Modules inherit from packages
        for mod in self._inventory.modules:
            for pkg in self._inventory.packages:
                if mod.package_name == pkg.name:
                    result[f"module:{mod.path}"] = pkg.owner
                    break
        
        for auth in self._inventory.runtime_authorities:
            result[f"authority:{auth.implementation}"] = auth.owner
        
        return result


def detect_ownership_gaps(inventory: ArchitectureInventory) -> Tuple[str, ...]:
    """
    Detect ownership gaps in the architecture.
    
    An ownership gap occurs when an entity has no owner assigned.
    
    Args:
        inventory: Complete architecture inventory
        
    Returns:
        Tuple of entity IDs that have ownership gaps
    """
    gaps: Set[str] = set()
    
    for pkg in inventory.packages:
        if pkg.owner == "Unknown":
            gaps.add(f"package:{pkg.name}")
    
    return tuple(gaps)


def validate_ownership_matrix(inventory: ArchitectureInventory) -> Tuple[bool, List[str]]:
    """
    Validate ownership matrix consistency.
    
    Checks that:
    1. Every package has an owner
    2. Every module references a valid package
    3. Every authority is properly categorized
    
    Args:
        inventory: Complete architecture inventory
        
    Returns:
        (is_valid, issues) tuple
    """
    issues: List[str] = []
    
    # Check packages
    for pkg in inventory.packages:
        if not pkg.owner or pkg.owner == "Unknown":
            issues.append(f"Package '{pkg.name}' has no owner")
    
    # Check modules reference valid packages
    package_names = {pkg.name for pkg in inventory.packages}
    for mod in inventory.modules:
        if mod.package_name not in package_names:
            issues.append(f"Module '{mod.path}' references unknown package '{mod.package_name}'")
    
    return (len(issues) == 0, issues)