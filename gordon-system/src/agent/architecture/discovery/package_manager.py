"""Package Discovery Manager.

Discovers and classifies packages in the repository.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

from .inventory import (
    ArchitectureInventory,
    PackageMetadata,
    PackageCategory,
    LifecycleParticipation,
)


# =============================================================================
# PACKAGE CLASSIFICATION RULES
# =============================================================================


@dataclass(frozen=True)
class ClassificationRule:
    """
    A rule for classifying a package.
    
    Rules are evaluated in order. The first matching rule determines
    the classification.
    """
    
    name: str
    match_paths: Tuple[str, ...]  # Paths that match this rule
    category: PackageCategory
    layer: str
    owner: str


# Default classification rules for Gordon Core
DEFAULT_CLASSIFICATION_RULES = (
    ClassificationRule(
        name="Architecture Layer (Phase 0)",
        match_paths=("architecture",),
        category=PackageCategory.INFRASTRUCTURE,
        layer="Phase 0",
        owner="Core Architecture Team"
    ),
    ClassificationRule(
        name="Kernel Layer (Phase 1)",
        match_paths=("kernel", "lifecycle"),
        category=PackageCategory.KERNEL,
        layer="Phase 1",
        owner="Runtime Core Team"
    ),
    ClassificationRule(
        name="Runtime Layer (Phase 2)",
        match_paths=(
            "bootstrap", "configuration", "context", "registry", "runtime",
            "state", "synchronization", "runtime_state", "scheduling"
        ),
        category=PackageCategory.RUNTIME,
        layer="Phase 2",
        owner="Runtime Core Team"
    ),
    ClassificationRule(
        name="Execution Layer (Phase 2)",
        match_paths=("execution", "executor", "engine", "manager"),
        category=PackageCategory.EXECUTION,
        layer="Phase 2",
        owner="Execution Team"
    ),
    ClassificationRule(
        name="Infrastructure Layer (Phase 2)",
        match_paths=(
            "dependency", "types", "exceptions", "contracts", "dependencies"
        ),
        category=PackageCategory.INFRASTRUCTURE,
        layer="Phase 2",
        owner="Core Infrastructure Team"
    ),
    ClassificationRule(
        name="Observability Layer (Phase 3)",
        match_paths=("observability", "health"),
        category=PackageCategory.OBSERVABILITY,
        layer="Phase 3",
        owner="Observability Team"
    ),
    ClassificationRule(
        name="Recovery Layer (Phase 3)",
        match_paths=("recovery", "integrity", "failures"),
        category=PackageCategory.RECOVERY,
        layer="Phase 3",
        owner="Recovery Team"
    ),
    ClassificationRule(
        name="Testing Layer",
        match_paths=("testing",),
        category=PackageCategory.TESTING,
        layer="N/A",
        owner="QA Team"
    ),
)


class PackageDiscoveryManager:
    """
    Discovers and classifies packages in the repository.
    
    This manager is:
    - Deterministic: Same input always produces same output
    - Repository-driven: Scans file system, not runtime state
    - Read-only: Never modifies source code or runtime state
    - Side-effect free: Importing this module does no scanning
    """
    
    def __init__(
        self,
        rules: Optional[Tuple[ClassificationRule, ...]] = None,
        exclude_paths: Optional[Tuple[str, ...]] = None
    ) -> None:
        """
        Initialize the package discovery manager.
        
        Args:
            rules: Classification rules to use (defaults to DEFAULT_CLASSIFICATION_RULES)
            exclude_paths: Paths to exclude from discovery (e.g., tests, __pycache__)
        """
        self._rules = rules or DEFAULT_CLASSIFICATION_RULES
        self._exclude_paths = exclude_paths or (
            "__pycache__", ".pytest_cache", "tests", "test_", "*.pyc"
        )
        
        # Cache for classification results
        self._classification_cache: Dict[str, Tuple[PackageCategory, str, str]] = {}
    
    def get_classification(
        self,
        package_path: str
    ) -> Tuple[PackageCategory, str, str]:
        """
        Classify a package path.
        
        Args:
            package_path: Relative path to the package
            
        Returns:
            Tuple of (category, layer, owner)
        """
        # Check cache first
        if package_path in self._classification_cache:
            return self._classification_cache[package_path]
        
        # Find matching rule
        for rule in self._rules:
            for match_path in rule.match_paths:
                if match_path in package_path or package_path.startswith(match_path):
                    result = (rule.category, rule.layer, rule.owner)
                    self._classification_cache[package_path] = result
                    return result
        
        # Default classification: unknown
        result = (PackageCategory.UNKNOWN, "Unknown", "Unknown")
        self._classification_cache[package_path] = result
        return result
    
    def is_excluded(self, path: str) -> bool:
        """Check if a path should be excluded from discovery."""
        for exclude in self._exclude_paths:
            if exclude in path:
                return True
        return False
    
    def discover_packages(
        self,
        repository_path: str,
        include_tests: bool = False
    ) -> Tuple[PackageMetadata, ...]:
        """
        Discover all packages in the repository.
        
        This is a deterministic, file-system-only scan. It does not:
        - Import any Python modules
        - Execute any code
        - Modify any files
        
        Args:
            repository_path: Path to the repository root
            include_tests: Whether to include test packages
            
        Returns:
            Tuple of PackageMetadata for all discovered packages
        """
        repo_path = Path(repository_path)
        packages: List[PackageMetadata] = []
        
        # Walk the directory tree looking for __init__.py files
        for init_file in repo_path.rglob("**/__init__.py"):
            # Get package path relative to repository root
            rel_path = init_file.relative_to(repo_path)
            parts = list(rel_path.parts[:-1])  # Remove __init__.py
            
            if not parts:
                continue  # Skip root __init__.py
            
            package_name = parts[-1]
            package_path = "/".join(parts)
            
            # Check exclusions
            if self.is_excluded(package_path):
                if not include_tests and "test" in package_path.lower():
                    continue
            
            # Classify the package
            category, layer, owner = self.get_classification(package_path)
            
            # Create package metadata
            packages.append(PackageMetadata(
                name=package_name,
                path=package_path,
                owner=owner,
                description=f"Gordon Core {category.value} package",
                purpose=f"Provides {package_name.replace('_', ' ')} functionality",
                responsibility=f"Manages {package_name.replace('_', ' ')} concerns",
                category=category,
                layer=layer,
                version="1.0.0",
                stability="stable"
            ))
        
        return tuple(packages)
    
    def discover_with_dependencies(
        self,
        repository_path: str
    ) -> ArchitectureInventory:
        """
        Discover packages and their dependencies.
        
        Args:
            repository_path: Path to the repository root
            
        Returns:
            Complete architecture inventory with package metadata
        """
        packages = self.discover_packages(repository_path)
        
        # Build dependency graph (placeholder - would require import analysis)
        from .inventory import DependencyGraph
        
        empty_graph = DependencyGraph(edges=())
        
        # Build module inventory (placeholder)
        modules: List[PackageMetadata] = []  # Will be populated by ModuleDiscoveryManager
        
        # Build full inventory
        return ArchitectureInventory(
            repository_path=repository_path,
            discovered_at=0.0,  # Will be set by caller
            version="1.0.0",
            packages=tuple(packages),
            modules=tuple(modules),
            public_apis=(),
            runtime_authorities=(),
            package_dependencies=empty_graph,
            runtime_dependencies=empty_graph,
            import_graph_edges=(),
            topology_nodes=(),
            topology_edges=(),
            entry_points=(),
            background_execution=(),
            total_packages=len(packages),
            total_modules=0,
            total_classes=0,
            total_functions=0,
            total_protocols=0,
            total_dataclasses=0,
            total_enums=0,
            total_authorities=0
        )