# Meta: Perception Module
# ========================

"""
Architectural Identity:
- Canonical Name: Perception
- Architectural Layer: 3 (Systems Layer)
- Semantic Owner: Systems Team
- Parent: g Gordon.system.src.agent.systems
- Status: Defined
- Maturity: Alpha

Purpose:
The perception module processes and interprets environmental inputs.
It enables the agent to sense and understand its environment.

Public API Intention:
This package exposes only architectural definitions:
  - Tree structures (via __tree__.py)
  - Metadata declarations (via this file)

Documentation Reference:
See docs/agent/architecture/ for complete specifications.
"""

name = "Perception"
description = "Processes and interprets environmental inputs"
version = "0.0.1"

canonical_name = "gordon.system.src.agent.systems.perception"
layer = 3
semantic_owner = "Systems Team"
parent_package = "g Gordon.system.src.agent.systems"

children_modules = []
allowed_dependencies = ["g Gordon.system.src.agent.architecture.*"]
forbidden_dependencies = ["g Gordon.system.src.agent.capabilities.*", "g Gordon.system.src.agent.components.*"]

runtime_activation = False
activation_policy = "never"

invariant: str = """
- No executable code allowed
- No runtime state
- Only declarations and definitions
- Purely declarative metadata
"""

__all__ = ["name", "description", "version", "canonical_name", "layer",
           "semantic_owner", "parent_package", "children_modules",
           "allowed_dependencies", "forbidden_dependencies", "runtime_activation",
           "activation_policy", "invariant"]