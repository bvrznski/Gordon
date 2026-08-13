"""Discovery Service - Phase 3.12.7.
================================================================================

Deterministic component discovery for Gordon Core reflection architecture.

Provides:
- DiscoveryResult - Single discovery result
- DiscoverySession - Session state management
- DiscoveryService - Main discovery orchestrator
- discover_packages, discover_modules, discover_runtime_authorities - Top-level functions
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

from ..discovery.inventory import (
    PackageMetadata,
    ModuleMetadata,
    RuntimeAuthority,
)
from ..discovery.package_manager import PackageDiscoveryManager
from ..discovery.module_manager import ModuleDiscoveryManager


# =============================================================================
# DISCOVERY DATA MODELS (immutable)
# =============================================================================


@dataclass(frozen=True)
class DiscoveryResult:
    """Single discovery result."""
    entity_id: str
    location: str  # file path or module path
    category: str  # package, module, authority, etc.
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class DiscoverySession:
    """
    Session state for discovery operations.
    
    Tracks progress and results of a discovery run.
    """
    session_id: str
    repository_path: Path
    started_at_utc: float
    results: Tuple[DiscoveryResult, ...]
    errors: Tuple[str, ...]


# =============================================================================
# DISCOVERY SERVICE
# =============================================================================


class DiscoveryService:
    """
    Service for discovering components without instantiation.
    
    Discovery is deterministic and repository-driven.
    It NEVER instantiates classes or modifies runtime state.
    
    This service is:
    - Deterministic: Same input always produces same output
    - Read-only: Never modifies anything
    - Passive: Only discovers, never acts
    """
    
    def __init__(
        self,
        repository_path: str = ".",
        package_manager: Optional[PackageDiscoveryManager] = None,
        module_manager: Optional[ModuleDiscoveryManager] = None,
    ) -> None:
        """
        Initialize the discovery service.
        
        Args:
            repository_path: Path to the repository root
            package_manager: Package discovery manager (created if not provided)
            module_manager: Module discovery manager (created if not provided)
        """
        self._repository_path = Path(repository_path).resolve()
        self._package_manager = package_manager or PackageDiscoveryManager()
        self._module_manager = module_manager or ModuleDiscoveryManager()
    
    def discover_packages(self) -> Tuple[PackageMetadata, ...]:
        """Discover all packages in the repository."""
        return self._package_manager.discover_packages(
            str(self._repository_path),
            include_tests=False
        )
    
    def discover_modules(self) -> Tuple[ModuleMetadata, ...]:
        """Discover all modules."""
        packages = self.discover_packages()
        return self._module_manager.discover_modules(
            str(self._repository_path),
            packages
        )
    
    def discover_runtime_authorities(self) -> Tuple[RuntimeAuthority, ...]:
        """
        Discover runtime authority components.
        
        Runtime authorities are components that own specific runtime concerns:
        - Scheduling
        - Resource management  
        - Context management
        - State management
        
        Returns tuple of discovered authorities (immutable).
        """
        modules = self.discover_modules()
        authorities: List[RuntimeAuthority] = []
        
        for mod in modules:
            # Identify authority patterns by name and module location
            if "authority" in mod.name.lower():
                authorities.append(RuntimeAuthority(
                    name=mod.name,
                    category="Runtime",
                    implementation=f"{mod.package_name}.{mod.name}",
                    owner="Core Team"
                ))
            elif "scheduler" in mod.path:
                authorities.append(RuntimeAuthority(
                    name=mod.name,
                    category="Scheduling",
                    implementation=f"{mod.package_name}.{mod.name}",
                    owner="Core Team"
                ))
            elif "state" in mod.path and "runtime_state" not in mod.path:
                authorities.append(RuntimeAuthority(
                    name=mod.name,
                    category="State Management",
                    implementation=f"{mod.package_name}.{mod.name}",
                    owner="Core Team"
                ))
        
        return tuple(authorities)
    
    def locate_entity(self, entity_id: str) -> Optional[str]:
        """
        Locate an entity's source location.
        
        Returns path to the entity definition (file:line format or similar).
        """
        # Check packages
        packages = self.discover_packages()
        for pkg in packages:
            if f"package:{pkg.name}" == entity_id:
                return f"{self._repository_path}/{pkg.path}/__init__.py"
        
        # Check modules
        modules = self.discover_modules()
        for mod in modules:
            if f"module:{mod.path}" == entity_id:
                return f"{self._repository_path}/{mod.package_name}/{mod.name}.py"
        
        return None
    
    def find_by_category(self, category: str) -> Tuple[str, ...]:
        """Find entities in a specific category."""
        packages = self.discover_packages()
        modules = self.discover_modules()
        authorities = self.discover_runtime_authorities()
        
        results: Set[str] = set()
        
        for pkg in packages:
            if pkg.category.value == category.lower():
                results.add(f"package:{pkg.name}")
        
        return tuple(results)


# =============================================================================
# TOP-LEVEL DISCOVERY FUNCTIONS
# =============================================================================


def discover_packages(repository_path: str) -> Tuple[PackageMetadata, ...]:
    """
    Discover all packages in a repository.
    
    Args:
        repository_path: Path to the repository root
        
    Returns:
        Tuple of package metadata (immutable)
    """
    manager = PackageDiscoveryManager()
    return manager.discover_packages(repository_path, include_tests=False)


def discover_modules(repository_path: str) -> Tuple[ModuleMetadata, ...]:
    """
    Discover all modules in a repository.
    
    Args:
        repository_path: Path to the repository root
        
    Returns:
        Tuple of module metadata (immutable)
    """
    packages = discover_packages(repository_path)
    manager = ModuleDiscoveryManager()
    return manager.discover_modules(repository_path, packages)


def discover_runtime_authorities(
    repository_path: str
) -> Tuple[RuntimeAuthority, ...]:
    """
    Discover runtime authorities in a repository.
    
    Runtime authorities are components that own specific runtime concerns.
    
    Args:
        repository_path: Path to the repository root
        
    Returns:
        Tuple of authority metadata (immutable)
    """
    discovery = DiscoveryService(repository_path)
    return discovery.discover_runtime_authorities()