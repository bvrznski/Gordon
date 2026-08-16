# Meta: Evolution Module
# ========================

"""
Architectural Identity:
- Canonical Name: Evolution
- Architectural Layer: 1 (Capabilities Layer)
- Semantic Owner: Capabilities Team
- Parent: gordon.system.src.agent.capabilities
- Status: Defined
- Maturity: Alpha

Purpose:
The evolution module provides adaptive learning and system improvement.
It enables the agent to learn from experience and improve over time.

Public API Intention:
This package exposes only architectural definitions:
  - Tree structures (via __tree__.py)
  - Metadata declarations (via this file)

Documentation Reference:
See docs/agent/architecture/capability-map.md for complete specifications.
"""

name = "Evolution"
description = "Adaptive learning and system improvement"
version = "0.0.1"

canonical_name = "gordon.system.src.agent.capabilities.evolution"
layer = 1
semantic_owner = "Capabilities Team"
parent_package = "gordon.system.src.agent.capabilities"

children_modules = []
allowed_dependencies = ["gordon.system.src.agent.architecture.*", "gordon.system.src.agent.systems.memory"]
forbidden_dependencies = ["gordon.system.src.agent.components.*", "gordon.system.src.agent.systems.perception"]

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