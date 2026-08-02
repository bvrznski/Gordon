# Meta: Executor Module
# ======================

"""
Architectural Identity:
- Canonical Name: Executor
- Architectural Layer: 2 (Components Layer)
- Semantic Owner: Components Team
- Parent: g Gordon.system.src.agent.components.core
- Status: Defined
- Maturity: Alpha

Purpose:
The executor module executes tasks and workflows.
It manages task execution and result handling.

Public API Intention:
This package exposes only architectural definitions:
  - Tree structures (via __tree__.py)
  - Metadata declarations (via this file)

Documentation Reference:
See docs/agent/architecture/ for complete specifications.
"""

name = "Executor"
description = "Executes tasks and workflows"
version = "0.0.1"

canonical_name = "gordon.system.src.agent.components.core.executor"
layer = 2
semantic_owner = "Components Team"
parent_package = "gordon.system.src.agent.components.core"

children_modules = []
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

__all__ = ["name", "description", "version", "canonical_name", "layer",
           "semantic_owner", "parent_package", "children_modules",
           "allowed_dependencies", "forbidden_dependencies", "runtime_activation",
           "activation_policy", "invariant"]