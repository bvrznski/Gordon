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
2. Must have exactly four direct children: capability_map, dependency_graph, ownership, topology
3. No runtime implementation may appear in this layer
4. All contracts are repair-safe (can be regenerated without data loss)
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


# Architecture layer structure
capability_map = Node("capability_map")
dependency_graph = Node("dependency_graph")
ownership = Node("ownership")
topology = Node("topology")

architecture_tree = Node("architecture")
architecture_tree.add_child(capability_map)
architecture_tree.add_child(dependency_graph)
architecture_tree.add_child(ownership)
architecture_tree.add_child(topology)


def get_structure() -> Dict[str, object]:
    """Return the architecture structure as a dictionary."""
    return architecture_tree.to_dict()


# Contract properties for validation
package_path = "gordon.system.src.agent.architecture"
parent_package = "gordon.system.src.agent"
allowed_children = ["capability_map", "dependency_graph", "ownership", "topology"]
required_children = allowed_children.copy()
required_files = ["__init__.py", "__meta__.py", "__tree__.py"]
forbidden_children = []
ownership_boundary = "gordon.system.src.agent.architecture.*"
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
    "capability_map", "dependency_graph", "ownership", "topology",
    "architecture_tree", "get_structure", "get_contract",
    # Contract properties
    "package_path", "parent_package",
    "allowed_children", "required_children",
    "required_files", "forbidden_children",
    "ownership_boundary", "dependency_direction",
    "runtime_activation_policy"
]