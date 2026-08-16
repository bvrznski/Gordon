# Meta: Memory Module
# ====================

"""
Architectural Identity:
- Canonical Name: Memory
- Architectural Layer: 3 (Systems Layer)
- Semantic Owner: Systems Team
- Parent: g Gordon.system.src.agent.systems
- Status: Defined
- Maturity: Alpha

Purpose:
The memory module provides persistent storage for agent experiences and knowledge.
It enables the agent to remember past interactions.

Public API Intention:
This package exposes only architectural definitions:
  - Tree structures (via __tree__.py)
  - Metadata declarations (via this file)

Documentation Reference:
See docs/agent/architecture/ for complete specifications.
"""

name = "Memory"
description = "Persistent storage for agent experiences and knowledge"
version = "0.0.1"

canonical_name = "gordon.system.src.agent.systems.memory"
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