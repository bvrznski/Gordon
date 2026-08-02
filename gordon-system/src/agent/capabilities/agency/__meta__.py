# Meta: Agency Module
# =====================

"""
Architectural Identity:
- Canonical Name: Agency
- Architectural Layer: 1 (Capabilities Layer)
- Semantic Owner: Capabilities Team
- Parent: gordon.system.src.agent.capabilities
- Status: Defined
- Maturity: Alpha

Purpose:
The agency module provides self-directed action and autonomy. It enables the agent
to make decisions independently and act with intentionality.

Public API Intention:
This package exposes only architectural definitions:
  - Tree structures (via __tree__.py)
  - Metadata declarations (via this file)

Documentation Reference:
See docs/agent/architecture/capability-map.md for complete specifications.
"""

name = "Agency"
description = "Self-directed action and autonomy"
version = "0.0.1"

# Architectural properties
canonical_name = "gordon.system.src.agent.capabilities.agency"
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