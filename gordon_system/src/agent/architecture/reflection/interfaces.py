"""Reflection Infrastructure Interfaces - Phase 3.12.7.
================================================================================

Canonical interfaces for Reflection, Metadata & Discovery Architecture.

These interfaces define the contract for passive architectural introspection:

- IReflectionService       - Main reflection API entry point
- IMetadataRepository    - Metadata storage and retrieval  
- IDiscoveryService      - Component discovery without instantiation
- IOwnershipInspector    - Ownership graph inspection
- IDependencyInspector   - Dependency graph analysis
- ITopologyInspector     - Topology structure inspection

All interfaces are read-only. They never modify state.
"""

from abc import ABC, abstractmethod
from typing import (
    Any, Dict, List, Optional, Set, Tuple, Protocol, runtime_checkable
)
from dataclasses import dataclass
from pathlib import Path
import time


# =============================================================================
# REFLECTION ARCHITECTURE INTERFACES
# =============================================================================


@runtime_checkable
class IReflectionService(Protocol):
    """
    Main reflection service interface.
    
    This is the primary entry point for architectural introspection.
    All reflection operations flow through this service.
    
    Reflection is PASSIVE - it never modifies anything.
    """
    
    @abstractmethod
    def get_inventory(self) -> Any:
        """Get complete architecture inventory."""
        ...
    
    @abstractmethod  
    def inspect_package(self, package_name: str) -> Optional[Any]:
        """Inspect a specific package's metadata."""
        ...
    
    @abstractmethod
    def inspect_module(self, module_path: str) -> Optional[Any]:
        """Inspect a specific module's metadata."""
        ...
    
    @abstractmethod
    def get_dependencies(self, entity_id: str) -> Tuple[str, ...]:
        """Get dependencies of an entity (read-only analysis)."""
        ...
    
    @abstractmethod
    def get_dependents(self, entity_id: str) -> Tuple[str, ...]:
        """Get entities that depend on the given entity."""
        ...
    
    @abstractmethod
    def discover_owners(self) -> Dict[str, str]:
        """
        Discover ownership information.
        
        Returns mapping of entity_id -> owner_name
        """
        ...
    
    @abstractmethod
    def get_topology(self) -> Any:
        """Get runtime topology graph (read-only snapshot)."""
        ...


@runtime_checkable  
class IMetadataRepository(Protocol):
    """
    Repository for immutable metadata storage.
    
    Metadata is captured at a point in time and never modified.
    """
    
    @abstractmethod
    def get_metadata(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for an entity."""
        ...
    
    @abstractmethod
    def find_by_type(self, type_name: str) -> Tuple[str, ...]:
        """Find all entities of a given type."""
        ...
    
    @abstractmethod
    def find_by_category(self, category: str) -> Tuple[str, ...]:
        """Find all entities in a category."""
        ...
    
    @abstractmethod
    def list_all_entities(self) -> Tuple[str, ...]:
        """List all known entity IDs (read-only)."""
        ...
    
    @abstractmethod
    def get_version(self, entity_id: str) -> Optional[str]:
        """Get version of an entity's metadata."""
        ...


@runtime_checkable
class IDiscoveryService(Protocol):
    """
    Service for discovering components without instantiation.
    
    Discovery is deterministic and repository-driven.
    It NEVER instantiates classes or modifies runtime state.
    """
    
    @abstractmethod
    def discover_packages(self) -> Tuple[Any, ...]:
        """Discover all packages in the repository."""
        ...
    
    @abstractmethod
    def discover_modules(self) -> Tuple[Any, ...]:
        """Discover all modules."""
        ...
    
    @abstractmethod  
    def discover_runtime_authorities(self) -> Tuple[Any, ...]:
        """Discover runtime authority components."""
        ...
    
    @abstractmethod
    def locate_entity(self, entity_id: str) -> Optional[str]:
        """
        Locate an entity's source location.
        
        Returns path to the entity definition (file:line format or similar).
        """
        ...
    
    @abstractmethod
    def find_by_name_pattern(self, pattern: str) -> Tuple[str, ...]:
        """Find entities matching a name pattern."""
        ...


@runtime_checkable
class IOwnershipInspector(Protocol):
    """
    Inspector for ownership relationships.
    
    Determines who owns what in the architecture.
    Ownership is immutable and canonical.
    """
    
    @abstractmethod
    def get_owner(self, entity_id: str) -> Optional[str]:
        """Get the owner of an entity."""
        ...
    
    @abstractmethod
    def get_entities_by_owner(self, owner: str) -> Tuple[str, ...]:
        """Get all entities owned by a specific owner."""
        ...
    
    @abstractmethod
    def get_ownership_graph(self) -> Any:
        """
        Get ownership relationship graph.
        
        Returns graph representation of ownership relationships.
        """
        ...
    
    @abstractmethod
    def verify_ownership_matrix(self) -> Tuple[bool, List[str]]:
        """Verify ownership consistency. Returns (is_valid, issues)."""
        ...


@runtime_checkable
class IDependencyInspector(Protocol):
    """
    Inspector for dependency relationships.
    
    Analyzes dependencies without validating them.
    Validation is the responsibility of Integrity.
    """
    
    @abstractmethod
    def get_dependencies(self, entity_id: str) -> Tuple[str, ...]:
        """Get entities that the given entity depends on."""
        ...
    
    @abstractmethod
    def get_dependents(self, entity_id: str) -> Tuple[str, ...]:
        """Get entities that depend on the given entity."""
        ...
    
    @abstractmethod
    def detect_cycles(self) -> Tuple[Tuple[str, ...], ...]:
        """
        Detect dependency cycles.
        
        Returns list of detected cycles (each cycle is a tuple of entity IDs).
        """
        ...
    
    @abstractmethod
    def topologically_sort(
        self,
        entities: Tuple[str, ...]
    ) -> Tuple[str, ...]:
        """
        Topologically sort entities by dependencies.
        
        Dependencies come first in the result.
        Raises ValueError if cycles exist.
        """
        ...
    
    @abstractmethod
    def get_dependency_graph(self) -> Any:
        """Get complete dependency graph."""
        ...


@runtime_checkable
class ITopologyInspector(Protocol):
    """
    Inspector for topology relationships.
    
    Visualizes and analyzes the architectural topology.
    Topology is descriptive, not prescriptive.
    """
    
    @abstractmethod
    def get_nodes(self) -> Tuple[Any, ...]:
        """Get all topology nodes."""
        ...
    
    @abstractmethod
    def get_edges(self) -> Tuple[Any, ...]:
        """Get all topology edges."""
        ...
    
    @abstractmethod
    def find_path(self, from_entity: str, to_entity: str) -> Optional[Tuple[str, ...]]:
        """
        Find a path between two entities.
        
        Returns list of entity IDs forming the path, or None if no path exists.
        """
        ...
    
    @abstractmethod
    def get_category_nodes(self, category: str) -> Tuple[Any, ...]:
        """Get all nodes in a specific category."""
        ...
    
    @abstractmethod
    def compute_metrics(self) -> Dict[str, Any]:
        """
        Compute topology metrics.
        
        Returns dictionary of computed metrics (e.g., centrality, connectivity).
        """
        ...


@runtime_checkable
class IArchitectureInventory(Protocol):
    """
    Interface for architecture inventory operations.
    
    Inventory summarizes what exists in the repository.
    """
    
    @abstractmethod
    def get_packages(self) -> Tuple[Any, ...]:
        """Get all package metadata."""
        ...
    
    @abstractmethod
    def get_modules(self) -> Tuple[Any, ...]:
        """Get all module metadata."""
        ...
    
    @abstractmethod
    def get_apis(self) -> Tuple[Any, ...]:
        """Get all public API items."""
        ...
    
    @abstractmethod
    def get_authorities(self) -> Tuple[Any, ...]:
        """Get all runtime authorities."""
        ...
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, int]:
        """Get inventory statistics (counts)."""
        ...