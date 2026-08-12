# Meta: Architecture Layer
# ========================

"""
Architectural Identity:
- Canonical Name: Architecture
- Architectural Layer: 0 (Architecture Layer)
- Semantic Owner: Architecture Team
- Parent: gordon.system.src.agent
- Status: Defined
- Maturity: Alpha

Purpose:
The architecture layer provides structural definitions for the entire system.
It defines how components relate to each other, who owns what, and how
dependencies are organized. This is pure declarative information with no
runtime implementation.

Public API Intention:
This package exposes only architectural definitions:
  - Tree structures (via __tree__.py)
  - Metadata declarations (via this file)

Documentation Reference:
See docs/agent/architecture/ for complete specifications.
"""

name = "Architecture"
description = "Structural patterns and organization for Gordon agent"
version = "0.0.1"

modules = [
    "capability_map",
    "dependency_graph",
    "ownership",
    "topology",
]

# Architectural properties
canonical_name = "gordon.system.src.agent.architecture"
layer = 0  # Architecture Layer
semantic_owner = "Architecture Team"
parent_package = "gordon.system.src.agent"

children_modules = [
    "capability_map", "dependency_graph", "ownership", "topology"
]

allowed_dependencies = []
forbidden_dependencies = ["capabilities.*", "components.*", "systems.*"]

runtime_activation = False
activation_policy = "never"

# Package invariants
invariant: str = """
- No executable code allowed
- No runtime state
- Only declarations and definitions
- Purely declarative metadata
"""

__all__ = [
    "name", "description", "version",
    "modules", "canonical_name", "layer",
    "semantic_owner", "parent_package",
    "children_modules", "allowed_dependencies",
    "forbidden_dependencies", "runtime_activation",
    "activation_policy", "invariant"
]