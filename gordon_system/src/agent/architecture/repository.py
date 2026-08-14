"""Repository - Canonical Repository Architecture for Gordon Core.

This module establishes the canonical Repository, Package & Modular Architecture
for the Gordon repository as defined in Phase 3.27.

PHILOSOPHY:
- Repository is a self-describing architectural system
- Every directory has explicit architecture and ownership
- Package boundaries are enforced through topology rules
- Module composition preserves architectural integrity

ARCHITECTURAL RESPONSIBILITIES:
- Define repository topology (where things live)
- Enforce package ownership and boundaries
- Validate dependency direction
- Verify architectural layering
- Track public vs internal APIs

Repository NEVER owns:
- Runtime behavior
- Semantic interpretation
- State management
- Execution scheduling

"""

__version__ = "1.0.0"
__phase__ = "3.27"

# =============================================================================
# ARCHITECTURAL ZONES
# =============================================================================

ARCHITECTURAL_ZONES = {
    # Primary implementation workspace
    "gordon_system": {
        "purpose": "Primary implementation workspace",
        "subzones": {
            "docs": {"purpose": "Documentation (public API)"},
            "src": {"purpose": "Source code implementation zone"},
            "tests": {"purpose": "Test implementations"}
        }
    },
    
    # Optional workspaces
    "gordon-environment": {"purpose": "Environment zone (optional)"},
    "gordon-improver": {"purpose": "Improver zone (optional)"},
    "gordon-legacy": {"purpose": "Legacy code zone (migrating)"},
    "gordon-modules": {"purpose": "Module zone (extensibility)"},
    "gordon-researcher": {"purpose": "Research zone (experimental)"},
    
    # Generated artifacts zones
    "observability": {"purpose": "Observability artifacts zone"},
    "recommendations": {"purpose": "Recommendations zone (generated)"},
    "reports": {"purpose": "Reports zone (generated)"},
    "validation": {"purpose": "Validation results zone"}
}

# =============================================================================
# ARCHITECTURAL LAYERS
# =============================================================================

ARCHITECTURAL_LAYERS = {
    # Layer 7: Foundation - Core primitives, types, utilities
    "foundation": {
        "priority": 7,
        "responsibility": "Core primitives, types, utilities",
        "packages": ["types", "errors", "utilities"]
    },
    
    # Layer 6: Core - Runtime infrastructure, lifecycle
    "core": {
        "priority": 6,
        "responsibility": "Runtime infrastructure, lifecycle",
        "packages": ["core", "runtime", "lifecycle"]
    },
    
    # Layer 5: Infrastructure - Platform services, storage, network
    "infrastructure": {
        "priority": 5,
        "responsibility": "Platform services, storage, network",
        "packages": []
    },
    
    # Layer 4: Runtime - Execution runtime, scheduling
    "runtime": {
        "priority": 4,
        "responsibility": "Execution runtime, scheduling",
        "packages": ["execution", "runtime"]
    },
    
    # Layer 3: Capability - Business capabilities, features
    "capability": {
        "priority": 3,
        "responsibility": "Business capabilities, features",
        "packages": ["capabilities"]
    },
    
    # Layer 2: Cognitive - Reasoning, planning, memory
    "cognitive": {
        "priority": 2,
        "responsibility": "Reasoning, planning, memory",
        "packages": ["cognition", "memory"]
    },
    
    # Layer 1: Application - High-level applications
    "application": {
        "priority": 1,
        "responsibility": "High-level applications",
        "packages": []
    }
}

# =============================================================================
# TOPOLOGY INVARIANTS
# =============================================================================

TOPOLOGY_INVARIIANTS = [
    # Every file in src/ belongs to exactly one package
    ("unique_package_ownership", 
     "Every file in src/ belongs to exactly one package"),
    
    # No cyclic dependencies between packages at same layer
    ("acyclic_dependencies",
     "No cyclic dependencies between packages at same layer"),
    
    # Dependencies only flow downward through architectural layers
    ("layered_dependencies",
     "Dependencies only flow downward through architectural layers"),
    
    # Public APIs are exported from package __init__.py
    ("explicit_public_api",
     "Public APIs are explicitly exported from package __init__.py"),
    
    # Internal APIs never leak across package boundaries
    ("private_internal_api",
     "Internal APIs never leak across package boundaries")
]

# =============================================================================
# PACKAGE CATEGORIES
# =============================================================================

PACKAGE_CATEGORIES = {
    "implementation": {
        "description": "Concrete functionality",
        "examples": ["state", "execution"],
        "rules": ["One primary responsibility per package"]
    },
    "interface": {
        "description": "Abstract contracts",
        "examples": ["interfaces", "communication"],
        "rules": ["Pure interface definitions, no implementations"]
    },
    "protocol": {
        "description": "Wire-level specifications",
        "examples": [],
        "rules": []
    },
    "model": {
        "description": "Data models and types",
        "examples": ["types", "models"],
        "rules": ["Immutable by default, serializable"]
    },
    "registry": {
        "description": "Entity registries",
        "examples": ["registry"],
        "rules": ["Singleton or registry patterns"]
    },
    "facade": {
        "description": "Simplified access layers",
        "examples": [],
        "rules": ["Delegates to implementations, minimal logic"]
    },
    "utility": {
        "description": "Shared utilities",
        "examples": ["utils", "helpers"],
        "rules": ["Stateless where possible"]
    },
    "adapter": {
        "description": "Integration adapters",
        "examples": [],
        "rules": ["Translate external interfaces to internal contracts"]
    }
}

# =============================================================================
# DEPENDENCY RULES
# =============================================================================

DEPENDENCY_RULES = [
    ("layered", 
     "Dependencies flow down through architectural layers"),
    ("explicit", 
     "All dependencies must be declared"),
    ("acyclic", 
     "No cycles within same layer"),
    ("minimal",
     "Only required dependencies")
]

# =============================================================================
# API RULES
# =============================================================================

PUBLIC_API_RULES = [
    ("explicit_exports", 
     "Only __all__ items are public"),
    ("version_stability",
     "Major version changes on breaking changes"),
    ("documentation_required",
     "Public APIs must be documented"),
    ("tests_required",
     "All public APIs must have tests")
]

INTERNAL_API_RULES = [
    ("private_by_default", 
     "Not in __all__, starts with _"),
    ("no_stability_guarantees",
     "Can change freely"),
    ("implementation_detail",
     "Hidden from users")
]

# =============================================================================
# PUBLISH API
# =============================================================================

__all__ = [
    # Zones
    "ARCHITECTURAL_ZONES",
    
    # Layers
    "ARCHITECTURAL_LAYERS",
    
    # Topology rules
    "TOPOLOGY_INVARIIANTS",
    
    # Package categories
    "PACKAGE_CATEGORIES",
    
    # Dependency rules
    "DEPENDENCY_RULES",
    
    # API rules
    "PUBLIC_API_RULES",
    "INTERNAL_API_RULES"
]