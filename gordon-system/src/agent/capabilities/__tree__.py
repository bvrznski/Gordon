# Tree: Capabilities Layer Structure
# ====================================

"""
Package Contract:

This file defines the structural contract for the capabilities layer.
It specifies allowed and required children, ownership boundaries,
and architectural invariants.

No executable code - only declarations.

Architectural Invariants:
1. Package must exist at gordon.system.src.agent.capabilities
2. Must have exactly nine direct children (one for each capability)
3. No runtime implementation may appear in this layer
4. All contracts are repair-safe (can be regenerated without data loss)
"""

from typing import Dict, List


class Node:
    """Node in the capabilities tree structure."""
    
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


# Capabilities Layer Structure
action = Node("action")
agency = Node("agency")
cognition = Node("cognition")
creativity = Node("creativity")
evolution = Node("evolution")
knowledge = Node("knowledge")
learning = Node("learning")
motivation = Node("motivation")
personality = Node("personality")

capabilities_tree = Node("capabilities")
capabilities_tree.add_child(action)
capabilities_tree.add_child(agency)
capabilities_tree.add_child(cognition)
capabilities_tree.add_child(creativity)
capabilities_tree.add_child(evolution)
capabilities_tree.add_child(knowledge)
capabilities_tree.add_child(learning)
capabilities_tree.add_child(motivation)
capabilities_tree.add_child(personality)


def get_structure() -> Dict[str, object]:
    """Return the capabilities structure as a dictionary."""
    return capabilities_tree.to_dict()


# Contract properties for validation
package_path = "gordon.system.src.agent.capabilities"
parent_package = "gordon.system.src.agent"
allowed_children = [
    "action", "agency", "cognition", "creativity",
    "evolution", "knowledge", "learning", "motivation", "personality"
]
required_children = allowed_children.copy()
required_files = ["__init__.py", "__meta__.py", "__tree__.py"]
forbidden_children = []
ownership_boundary = "gordon.system.src.agent.capabilities.*"
dependency_direction = "downward"  # May depend on architecture layer
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
    "action", "agency", "cognition", "creativity",
    "evolution", "knowledge", "learning", "motivation", "personality",
    "capabilities_tree", "get_structure", "get_contract",
    # Contract properties
    "package_path", "parent_package",
    "allowed_children", "required_children",
    "required_files", "forbidden_children",
    "ownership_boundary", "dependency_direction",
    "runtime_activation_policy"
]