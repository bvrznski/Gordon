# Meta: Gordon Agent Core
# =========================

"""
Architectural Identity:
- Canonical Name: Gordon Agent
- Architectural Layer: Root (Layer -1)
- Semantic Owner: System Owner
- Parent: None (root package)
- Status: Defined
- Maturity: Alpha

Purpose:
The root agent package serves as the canonical entry point and namespace
for all Gordon system components. It defines the structural foundation upon
which all other layers are built.

Public API Intention:
This package exposes only architectural definitions, not runtime implementations.
It provides:
  - Package structure tree (via __tree__.py)
  - Metadata declarations (via this file)

Documentation Reference:
See docs/agent/architecture/ for complete architectural specifications.
"""

name = "Gordon Agent"
description = "Core intelligent agent framework for the Gordon system"
version = "0.0.1"

packages = [
    "gordon.system.src.agent.architecture",
    "gordon.system.src.agent.capabilities",
    "gordon.system.src.agent.components",
    "gordon.system.src.agent.systems",
]

# Architectural properties
canonical_name = "gordon.system.src.agent"
layer = -1  # Root layer, above all other layers
semantic_owner = "System Owner"
parent_package = None

# Package hierarchy
children_packages = [
    "architecture",
    "capabilities",
    "components",
    "systems",
]

# Dependency direction (which layers this package may depend on)
allowed_dependencies = []
forbidden_dependencies = []

# Runtime activation policy
runtime_activation = False  # No runtime in architecture layer
activation_policy = "never"

__all__ = [
    "name", "description", "version",
    "packages", "canonical_name", "layer",
    "semantic_owner", "parent_package",
    "children_packages", "allowed_dependencies",
    "forbidden_dependencies", "runtime_activation", "activation_policy"
]