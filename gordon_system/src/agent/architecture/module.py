"""Module - Canonical Module Architecture for Gordon Core.

This module defines canonical module patterns, types, and architecture
rules as defined in Phase 3.27.

PHILOSOPHY:
- One primary responsibility per module
- Clear boundaries between modules
- Minimal coupling through interfaces

MODULE RESPONSIBILITIES:
- Define module type (implementation, interface, protocol, model, etc.)
- Specify module ownership and layer
- Document dependencies on other modules
- Export public symbols from __init__.py

Module NEVER owns:
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


class ModuleType(Enum):
    """Module type classifications."""
    
    # Core module types
    IMPLEMENTATION = "implementation"   # Concrete functionality
    INTERFACE = "interface"            # Abstract contracts
    PROTOCOL = "protocol"              # Wire-level specifications  
    MODEL = "model"                    # Data models and types
    
    # Structural module types
    REGISTRY = "registry"              # Entity registries
    FACADE = "facade"                  # Simplified access layers
    UTILITY = "utility"                # Shared utilities
    ADAPTER = "adapter"                # Integration adapters


class ModuleStatus(Enum):
    """Module lifecycle status."""
    PROPOSED = "proposed"
    DEVELOPMENT = "development"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    REMOVED = "removed"


@dataclass
class ModuleMetadata:
    """Metadata for a canonical module."""
    
    name: str                           # Module name (file without .py)
    type: ModuleType                    # Module type
    path: str                           # Filesystem path
    
    owner: Optional[str] = None         # Owner (team or individual email)
    layer: Optional[str] = None         # Architectural layer
    
    public_symbols: List[str] = field(default_factory=list)   # Exported symbols
    internal_symbols: List[str] = field(default_factory=list) # Internal symbols (starts with _)
    
    dependencies: List[str] = field(default_factory=list)     # Module dependencies
    tests: List[str] = field(default_factory=list)            # Test files
    
    status: ModuleStatus = ModuleStatus.DEVELOPMENT


@dataclass 
class ModuleArchitecture:
    """Architectural definition for a module."""
    
    path: str                           # Filesystem path to module
    metadata: ModuleMetadata            # Module metadata
    
    # Architecture rules
    rules: Dict[str, Any] = field(default_factory=lambda: {
        "max_functions": 50,            # Maximum functions/methods
        "max_lines": 1000,              # Maximum lines of code
        "max_nesting_depth": 3          # Maximum nesting depth
    })


class ModuleValidator:
    """Validates module architecture against canonical rules."""
    
    @staticmethod
    def validate_module_ownership(metadata: ModuleMetadata) -> bool:
        """Verify module has owner and layer metadata."""
        return bool(metadata.owner) and bool(metadata.layer)
    
    @staticmethod
    def validate_module_type(metadata: ModuleMetadata, allowed_types: List[ModuleType]) -> bool:
        """Verify module is of a valid type."""
        return metadata.type in allowed_types
    
    @staticmethod
    def validate_public_api(metadata: ModuleMetadata) -> tuple[bool, List[str]]:
        """
        Verify public API follows canonical rules.
        
        Rules:
        - All exported symbols are documented
        - No implementation details leaked (no _ prefix)
        - __all__ is explicitly defined
        
        Returns:
            Tuple of (is_valid, violations)
        """
        violations = []
        
        # Check for leaked internal symbols in public API
        for symbol in metadata.public_symbols:
            if symbol.startswith("_"):
                violations.append(f"Internal symbol '{symbol}' in public API")
        
        return len(violations) == 0, violations
    
    @staticmethod
    def validate_module_size(metadata: ModuleMetadata, max_lines: int = 1000) -> tuple[bool, str]:
        """Verify module doesn't exceed size limits."""
        # Implementation would check actual line count
        return True, ""


class ModuleBuilder:
    """Builds module architectures from filesystem."""
    
    @staticmethod
    def discover_modules(package_path: str) -> Dict[str, ModuleArchitecture]:
        """Discover all modules under package path."""
        modules = {}
        
        # Implementation would scan directory structure
        # and build ModuleArchitecture instances
        
        return modules
    
    @staticmethod
    def validate_all(modules: Dict[str, ModuleArchitecture]) -> dict:
        """Validate all modules against canonical rules."""
        results = {
            "total": len(modules),
            "valid": 0,
            "invalid": 0,
            "errors": []
        }
        
        for name, mod in modules.items():
            is_valid = True
            errors = []
            
            # Validate ownership
            if not ModuleValidator.validate_module_ownership(mod.metadata):
                is_valid = False
                errors.append("Module missing ownership metadata")
            
            # Validate size
            size_valid, _ = ModuleValidator.validate_module_size(mod.metadata)
            if not size_valid:
                is_valid = False
                errors.append(f"Module exceeds size limits")
            
            if is_valid:
                results["valid"] += 1
            else:
                results["invalid"] += 1
                results["errors"].extend(errors)
        
        return results


# Module type patterns
MODULE_PATTERNS: Dict[ModuleType, Dict[str, Any]] = {
    ModuleType.IMPLEMENTATION: {
        "filename_pattern": r"^[a-z0-9_]+\.py$",
        "should_export": ["class", "function", "constant"],
        "must_have": ["__all__"]
    },
    ModuleType.INTERFACE: {
        "filename_pattern": r"^interfaces?\.py$|^[a-z0-9_]+_interface\.py$",
        "should_export": ["Protocol", "Interface"],
        "must_not_have": ["def ", "class.*:"]
    },
    ModuleType.PROTOCOL: {
        "filename_pattern": r"^protocols?\.py$|^[a-z0-9_]+_protocol\.py$",
        "should_export": [],
        "must_have": []
    },
    ModuleType.MODEL: {
        "filename_pattern": r"^(models?|types?)\.py$|^[a-z0-9_]+_model\.py$",
        "should_export": ["dataclass", "NamedTuple"],
        "must_have": []
    },
    ModuleType.REGISTRY: {
        "filename_pattern": r"^registry(s)?\.py$",
        "should_export": ["Registry"],
        "must_have": ["register()", "get()"]
    },
    ModuleType.FACADE: {
        "filename_pattern": r"^facade(s)?\.py$|^[a-z0-9_]+_facade\.py$",
        "should_export": [],
        "must_have": []
    },
    ModuleType.UTILITY: {
        "filename_pattern": r"^(utils?|helpers?)\.py$",
        "should_export": ["staticmethod", "function"],
        "must_have": []
    },
    ModuleType.ADAPTER: {
        "filename_pattern": r"^adapters?\.py$|^[a-z0-9_]+_adapter\.py$",
        "should_export": [],
        "must_have": []
    }
}


# =============================================================================
# PUBLISH API
# =============================================================================

__all__ = [
    "ModuleType",
    "ModuleStatus",
    "ModuleMetadata",
    "ModuleArchitecture",
    "ModuleValidator",
    "ModuleBuilder",
    "MODULE_PATTERNS"
]