# Meta: Motivation Module
# =========================

"""
Architectural Identity:
- Canonical Name: Motivation
- Architectural Layer: 1 (Capabilities Layer)
- Semantic Owner: Capabilities Team
- Parent: gordon.system.src.agent.capabilities
- Status: Defined
- Maturity: Alpha

Purpose:
The motivation module provides driving forces and goal-oriented behavior.
It enables the agent to pursue objectives with purpose.

Public API Intention:
This package exposes only architectural definitions:
  - Tree structures (via __tree__.py)
  - Metadata declarations (via this file)

Documentation Reference:
See docs/agent/architecture/capability-map.md for complete specifications.
"""

name = "Motivation"
description = "Driving forces and goal-oriented behavior"
version = "0.0.1"

canonical_name = "gordon.system.src.agent.capabilities.motivation"
layer = 1
semantic_owner = "Capabilities Team"
parent_package = "gordon.system.src.agent.capabilities"

children_modules = []
allowed_dependencies = ["gordon.system.src.agent.architecture.*"]
forbidden_dependencies = ["g Gordon.system.src.agent.components.*", "gordon.system.src.agent.systems.*"]

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