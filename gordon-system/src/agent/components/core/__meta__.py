# Meta: Core Components Module
# =============================

"""
Architectural Identity:
- Canonical Name: Core
- Architectural Layer: 2 (Components Layer)
- Semantic Owner: Components Team
- Parent: g Gordon.system.src.agent.components
- Status: Defined
- Maturity: Alpha

Purpose:
The core module provides essential agent infrastructure components.
It includes execution, task management, and coordination.

Public API Intention:
This package exposes only architectural definitions:
  - Tree structures (via __tree__.py)
  - Metadata declarations (via this file)

Documentation Reference:
See docs/agent/architecture/ for complete specifications.
"""

name = "Core"
description = "Essential agent infrastructure components"
version = "0.0.1"

modules = [
    "engine",
    "executor",
    "manager",
]

canonical_name = "gordon.system.src.agent.components.core"
layer = 2
semantic_owner = "Components Team"
parent_package = "gordon.system.src.agent.components"

children_modules = ["engine", "executor", "manager"]
allowed_dependencies = ["g Gordon.system.src.agent.architecture.*", "g Gordon.system.src.agent.systems.*"]
forbidden_dependencies = ["g Gordon.system.src.agent.capabilities.*"]

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