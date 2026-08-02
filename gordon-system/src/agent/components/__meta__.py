# Meta: Components Layer
# ======================

"""
Architectural Identity:
- Canonical Name: Components
- Architectural Layer: 2 (Components Layer)
- Semantic Owner: Components Team
- Parent: gordon.system.src.agent
- Status: Defined
- Maturity: Alpha

Purpose:
The components layer provides building blocks and infrastructure for the Gordon agent.
It includes core execution, task management, and coordination components.

Public API Intention:
This package exposes only architectural definitions:
  - Tree structures (via __tree__.py)
  - Metadata declarations (via this file)

Documentation Reference:
See docs/agent/architecture/ for complete specifications.
"""

name = "Components"
description = "Building blocks and infrastructure for Gordon agent"
version = "0.0.1"

modules = [
    "core",
]

canonical_name = "gordon.system.src.agent.components"
layer = 2
semantic_owner = "Components Team"
parent_package = "gordon.system.src.agent"

children_modules = ["core"]
allowed_dependencies = ["gordon.system.src.agent.architecture.*", "gordon.system.src.agent.systems.*"]
forbidden_dependencies = ["gordon.system.src.agent.capabilities.*"]

runtime_activation = False
activation_policy = "never"

invariant: str = """
- No executable code allowed
- No runtime state
- Only declarations and definitions
- Purely declarative metadata
"""

__all__ = ["name", "description", "version", "modules", "canonical_name", "layer",
           "semantic_owner", "parent_package", "children_modules",
           "allowed_dependencies", "forbidden_dependencies", "runtime_activation",
           "activation_policy", "invariant"]