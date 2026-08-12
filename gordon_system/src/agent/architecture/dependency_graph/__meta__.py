# Meta: Dependency Graph Module
# ==============================

"""
Architectural Identity:
- Canonical Name: Dependency Graph
- Architectural Layer: 0 (Architecture Layer)
- Semantic Owner: Architecture Team
- Parent: gordon.system.src.agent.architecture
- Status: Defined
- Maturity: Alpha

Purpose:
The dependency graph module manages dependencies between agent components and their resolution.
It defines the structure that connects capability definitions with runtime execution.

Public API Intention:
This package exposes only architectural definitions:
  - Tree structures (via __tree__.py)
  - Metadata declarations (via this file)

Documentation Reference:
See docs/agent/architecture/dependency-rules.md for complete specifications.
"""

name = "Dependency Graph"
description = "Manages dependencies between agent components and their resolution"
version = "0.0.1"

# Architectural properties
canonical_name = "gordon.system.src.agent.architecture.dependency_graph"
layer = 0
semantic_owner = "Architecture Team"
parent_package = "gordon.system.src.agent.architecture"

children_modules = []

allowed_dependencies = []
forbidden_dependencies = ["capabilities.*", "components.*", "systems.*"]

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