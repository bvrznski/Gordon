# Tree: Architecture Layer Structure
# ===================================

"""
Package Contract:

This file defines the structural contract for the architecture layer.
It specifies allowed and required children, ownership boundaries,
and architectural invariants.

No executable code - only declarations.

Architectural Invariants:
1. Package must exist at gordon.system.src.agent.architecture
2. Must have exactly nine direct children: inventory, topology, ownership, dependencies, boundaries, invariants, migration, certification, manifests
3. No runtime implementation may appear in this layer
4. All contracts are repair-safe (can be regenerated without data loss)
5. Architecture is descriptive and normative - it does not execute, schedule, or mutate runtime state
"""

from typing import Dict, List


class Node:
    """Node in the architecture tree structure."""
    
    def __init__(self, name: str):
        self.name = name
        self.children: List["Node"] = []
    
    def add_child(self, child: "Node") -> None:
        """Add a child node to this parent."""
        self.children.append(child)
    
    def to_dict(self) -> Dict[str, object]:
        """Return the tree as a dictionary for serialization."""
        return {
            "name": self.name,
            "children": [child.to_dict() for child in self.children],
        }


# =============================================================================
# CANONICAL ARCHITECTURE DOMAINS
# =============================================================================

inventory = Node("inventory")
topology = Node("topology")
ownership = Node("ownership")
dependencies = Node("dependencies")
boundaries = Node("boundaries")
invariants = Node("invariants")
migration = Node("migration")
certification = Node("certification")
manifests = Node("manifests")

architecture_tree = Node("architecture")
architecture_tree.add_child(inventory)
architecture_tree.add_child(topology)
architecture_tree.add_child(ownership)
architecture_tree.add_child(dependencies)
architecture_tree.add_child(boundaries)
architecture_tree.add_child(invariants)
architecture_tree.add_child(migration)
architecture_tree.add_child(certification)
architecture_tree.add_child(manifests)


def get_structure() -> Dict[str, object]:
    """Return the architecture structure as a dictionary."""
    return architecture_tree.to_dict()


# =============================================================================
# CONTRACT PROPERTIES FOR VALIDATION
# =============================================================================

package_path = "gordon.system.src.agent.architecture"
parent_package = "gordon.system.src.agent"
allowed_children = [
    "inventory",
    "topology", 
    "ownership",
    "dependencies",
    "boundaries",
    "invariants",
    "migration",
    "certification",
    "manifests",
]
required_children = allowed_children.copy()
required_files = ["__init__.py", "__meta__.py", "__tree__.py"]
forbidden_children = [
    # Runtime mechanisms must not appear in architecture layer
    "execution",
    "runtime",
    "scheduler",
    "synchronizer",
    "coordinator",
    "executor",
    "engine",
]

ownership_boundary = "gordon.system.src.agent.architecture.*"
dependency_direction = "downward"  # May depend on nothing above (descriptive only)
runtime_activation_policy = "never"


def get_contract() -> Dict[str, object]:
    """Return the complete package contract as a dictionary."""
    return {
        "package_path": package_path,
        "parent_package": parent_package,
        "allowed_children": allowed_children,
        "required_children": required_children,
        "required_files": required_files,
        "forbidden_children": forbidden_children,
        "ownership_boundary": ownership_boundary,
        "dependency_direction": dependency_direction,
        "runtime_activation_policy": runtime_activation_policy,
    }


__all__ = [
    "Node",
    # Canonical children
    "inventory", "topology", "ownership", "dependencies",
    "boundaries", "invariants", "migration", "certification", "manifests",
    "architecture_tree", "get_structure", "get_contract",
    # Contract properties
    "package_path", "parent_package",
    "allowed_children", "required_children",
    "required_files", "forbidden_children",
    "ownership_boundary", "dependency_direction",
    "runtime_activation_policy"
]