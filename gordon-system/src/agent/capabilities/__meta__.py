# Meta: Capabilities Layer
# =========================

"""
Architectural Identity:
- Canonical Name: Capabilities
- Architectural Layer: 1 (Capabilities Layer)
- Semantic Owner: Capabilities Team
- Parent: gordon.system.src.agent
- Status: Defined
- Maturity: Alpha

Purpose:
The capabilities layer provides intelligent behaviors and actions for the Gordon agent.
Each capability is an independent, self-contained unit of intelligence.

Public API Intention:
This package exposes only architectural definitions:
  - Tree structures (via __tree__.py)
  - Metadata declarations (via this file)

Documentation Reference:
See docs/agent/architecture/capability-map.md for complete specifications.
"""

name = "Capabilities"
description = "Intelligent behaviors and actions for Gordon agent"
version = "0.0.1"

modules = [
    "action",
    "agency",
    "cognition",
    "creativity",
    "evolution",
    "knowledge",
    "learning",
    "motivation",
    "personality",
]

# Architectural properties
canonical_name = "gordon.system.src.agent.capabilities"
layer = 1  # Capabilities Layer
semantic_owner = "Capabilities Team"
parent_package = "gordon.system.src.agent"

children_modules = [
    "action", "agency", "cognition", "creativity",
    "evolution", "knowledge", "learning", "motivation", "personality"
]

allowed_dependencies = ["gordon.system.src.agent.architecture.*"]
forbidden_dependencies = ["gordon.system.src.agent.components.*", "gordon.system.src.agent.systems.*"]

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