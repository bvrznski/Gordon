# Meta: Action Module
# ====================

"""
Architectural Identity:
- Canonical Name: Action
- Architectural Layer: 1 (Capabilities Layer)
- Semantic Owner: Capabilities Team
- Parent: gordon.system.src.agent.capabilities
- Status: Defined
- Maturity: Alpha

Purpose:
The action module executes physical and digital actions. It provides the interface
between intelligent decision-making and observable behavior in the environment.

Public API Intention:
This package exposes only architectural definitions:
  - Tree structures (via __tree__.py)
  - Metadata declarations (via this file)

Documentation Reference:
See docs/agent/architecture/capability-map.md for complete specifications.
"""

name = "Action"
description = "Executes physical and digital actions"
version = "0.0.1"

# Architectural properties
canonical_name = "gordon.system.src.agent.capabilities.action"
layer = 1
semantic_owner = "Capabilities Team"
parent_package = "gordon.system.src.agent.capabilities"

children_modules = []

allowed_dependencies = [
    "gordon.system.src.agent.architecture.*",
]
forbidden_dependencies = [
    "gordon.system.src.agent.components.*",
    "gordon.system.src.agent.systems.*",
]

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
    "canonical_name", "layer",
    "semantic_owner", "parent_package",
    "children_modules", "allowed_dependencies",
    "forbidden_dependencies", "runtime_activation",
    "activation_policy", "invariant"
]