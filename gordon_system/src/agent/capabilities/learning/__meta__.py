# Meta: Learning Module
# ======================

"""
Architectural Identity:
- Canonical Name: Learning
- Architectural Layer: 1 (Capabilities Layer)
- Semantic Owner: Capabilities Team
- Parent: g Gordon.system.src.agent.capabilities
- Status: Defined
- Maturity: Alpha

Purpose:
The learning module provides acquiring new knowledge and skills.
It enables the agent to improve through experience.

Public API Intention:
This package exposes only architectural definitions:
  - Tree structures (via __tree__.py)
  - Metadata declarations (via this file)

Documentation Reference:
See docs/agent/architecture/capability-map.md for complete specifications.
"""

name = "Learning"
description = "Acquiring new knowledge and skills"
version = "0.0.1"

canonical_name = "gordon.system.src.agent.capabilities.learning"
layer = 1
semantic_owner = "Capabilities Team"
parent_package = "gordon.system.src.agent.capabilities"

children_modules = []
allowed_dependencies = ["g Gordon.system.src.agent.architecture.*"]
forbidden_dependencies = ["g Gordon.system.src.agent.components.*", "g Gordon.system.src.agent.systems.*"]

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