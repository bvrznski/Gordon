"""Package - Canonical Package Architecture for Gordon Core.

This module defines the canonical package architecture rules, patterns,
and validation as defined in Phase 3.27.

PHILOSOPHY:
- One package = one owner
- One package = one primary responsibility  
- Clear boundaries between packages
- Explicit public and internal contracts

PACKAGE RESPONSIBILITIES:
- Define package ownership (team or individual)
- Specify architectural layer membership
- Document dependencies on other packages
- Export public APIs from __init__.py
- Manage versioning when distributed

Package NEVER owns:
- Runtime behavior
- Semantic interpretation
- State management
- Execution scheduling

"""

__version__ = "1.0.0"
__phase__ = "3.27"

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


class PackageCategory(Enum):
    """Package category types."""
    IMPLEMENTATION = "implementation"  # Concrete functionality
    INTERFACE = "interface"           # Abstract contracts
    PROTOCOL = "protocol"             # Wire-level specifications
    MODEL = "model"                   # Data models and types
    REGISTRY = "registry"             # Entity registries
    FACADE = "facade"                 # Simplified access layers
    UTILITY = "utility"               # Shared utilities
    ADAPTER = "adapter"               # Integration adapters


class PackageStatus(Enum):
    """Package lifecycle status."""
    PROPOSED = "proposed"
    DEVELOPMENT = "development"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    REMOVED = "removed"


@dataclass
class PackageMetadata:
    """Metadata for a canonical package."""
    
    name: str                           # Package name (directory)
    owner: str                          # Owner (team or individual email)
    layer: str                          # Architectural layer (foundation, core, etc.)
    category: PackageCategory           # Package category
    version: str = "1.0.0"              # Semantic version
    
    dependencies: List[str] = field(default_factory=list)  # Direct package dependencies
    public_api: List[str] = field(default_factory=list)    # Public API exports from __init__.py
    internal_api: List[str] = field(default_factory=list)  # Internal API (starts with _)
    
    status: PackageStatus = PackageStatus.DEVELOPMENT
    documentation_url: Optional[str] = None
    created_at: Optional[str] = None
    last_updated: Optional[str] = None


@dataclass 
class PackageArchitecture:
    """Architectural definition for a package."""
    
    path: str                           # Filesystem path to package
    metadata: PackageMetadata           # Package metadata
    
    # Architecture rules
    rules: Dict[str, Any] = field(default_factory=lambda: {
        "max_modules": 50,              # Maximum modules per package
        "max_depth": 3,                 # Maximum nesting depth
        "max_dependencies": 15          # Maximum dependencies
    })


class PackageValidator:
    """Validates package architecture against canonical rules."""
    
    @staticmethod
    def validate_package_ownership(metadata: PackageMetadata) -> bool:
        """Verify package has exactly one owner."""
        return bool(metadata.owner)
    
    @staticmethod
    def validate_layer_membership(metadata: PackageMetadata, layers: Dict[str, Any]) -> bool:
        """Verify package is in a valid architectural layer."""
        return metadata.layer in layers
    
    @staticmethod
    def validate_dependencies_acyclic(
        packages: Dict[str, PackageArchitecture]
    ) -> tuple[bool, List[List[str]]]:
        """
        Verify no cyclic dependencies exist.
        
        Returns:
            Tuple of (is_acyclic, list_of_cycles)
        """
        # Implementation would check dependency graph for cycles
        return True, []
    
    @staticmethod
    def validate_layering(
        packages: Dict[str, PackageArchitecture],
        layer_order: List[str]
    ) -> tuple[bool, List[tuple[str, str]]]:
        """
        Verify dependencies flow correctly through layers.
        
        Higher layer (lower number) can depend on lower layer (higher number).
        Lower layer cannot depend on higher layer.
        
        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        # Implementation would check dependency direction
        return True, []


class PackageBuilder:
    """Builds package architectures from filesystem."""
    
    @staticmethod
    def discover_packages(root_path: str) -> Dict[str, PackageArchitecture]:
        """Discover all packages under root path."""
        packages = {}
        
        # Implementation would scan directory structure
        # and build PackageArchitecture instances
        
        return packages
    
    @staticmethod
    def validate_all(packages: Dict[str, PackageArchitecture]) -> dict:
        """Validate all packages against canonical rules."""
        results = {
            "total": len(packages),
            "valid": 0,
            "invalid": 0,
            "errors": []
        }
        
        for name, pkg in packages.items():
            is_valid = True
            errors = []
            
            # Validate ownership
            if not PackageValidator.validate_package_ownership(pkg.metadata):
                is_valid = False
                errors.append("Package has no owner")
            
            # Validate layer membership
            # ... additional validations
            
            if is_valid:
                results["valid"] += 1
            else:
                results["invalid"] += 1
                results["errors"].extend(errors)
        
        return results


# =============================================================================
# PUBLISH API
# =============================================================================

__all__ = [
    "PackageCategory",
    "PackageStatus",
    "PackageMetadata",
    "PackageArchitecture",
    "PackageValidator",
    "PackageBuilder"
]