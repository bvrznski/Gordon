# Tree: Gordon Agent Structure
# =============================

"""
Package Contract:

This file defines the structural contract for the Gordon agent package.
It specifies allowed and required children, ownership boundaries,
and architectural invariants.

No executable code - only declarations.

Architectural Invariants:
1. Package must exist at gordon.system.src.agent
2. Must have exactly four direct children: architecture, capabilities, components, systems
3. No runtime implementation may appear in this layer
4. All contracts are repair-safe (can be regenerated without data loss)
"""

from typing import Dict, List


class Node:
    """Node in the package tree structure."""
    
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


# Architecture Layer (Layer 0)
architecture = Node("architecture")
architecture.add_child(Node("capability_map"))
architecture.add_child(Node("dependency_graph"))
architecture.add_child(Node("ownership"))
architecture.add_child(Node("topology"))

# Capabilities Layer (Layer 1)
capabilities = Node("capabilities")
capabilities.add_child(Node("action"))
capabilities.add_child(Node("agency"))
capabilities.add_child(Node("cognition"))
capabilities.add_child(Node("creativity"))
capabilities.add_child(Node("evolution"))
capabilities.add_child(Node("knowledge"))
capabilities.add_child(Node("learning"))
capabilities.add_child(Node("motivation"))
capabilities.add_child(Node("personality"))

# Components Layer (Layer 2)
components = Node("components")
core = Node("core")
core.add_child(Node("engine"))
core.add_child(Node("executor"))
core.add_child(Node("manager"))
components.add_child(core)

# Systems Layer (Layer 3)
systems = Node("systems")
systems.add_child(Node("memory"))
systems.add_child(Node("perception"))

# Root tree
tree = Node("agent")
tree.add_child(architecture)
tree.add_child(capabilities)
tree.add_child(components)
tree.add_child(systems)


def get_structure() -> Dict[str, object]:
    """Return the complete package structure as a dictionary."""
    return tree.to_dict()


# Contract properties for validation
package_path = "gordon.system.src.agent"
parent_package = None  # Root package
allowed_children = [
    "architecture", "capabilities", "components", "systems"
]
required_children = allowed_children.copy()
required_files = ["__init__.py", "__meta__.py", "__tree__.py"]
forbidden_children = []  # No forbidden children for root
ownership_boundary = "gordon.system.src.agent.*"
dependency_direction = "downward"  # May depend on nothing above
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
    "architecture", "capabilities", "components", "systems", "tree",
    "get_structure", "get_contract",
    # Contract properties
    "package_path", "parent_package",
    "allowed_children", "required_children",
    "required_files", "forbidden_children",
    "ownership_boundary", "dependency_direction",
    "runtime_activation_policy"
]