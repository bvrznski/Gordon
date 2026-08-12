# Tree: Perception Structure
# =============================

"""
Package Contract:
- Package must exist at g Gordon.system.src.agent.systems.perception
- No direct children (leaf node)
- No runtime implementation may appear in this layer
- All contracts are repair-safe
"""

from typing import Dict, List


class Node:
    """Node in the perception tree structure."""
    
    def __init__(self, name: str):
        self.name = name
        self.children: List["Node"] = []
    
    def add_child(self, child: "Node") -> None:
        self.children.append(child)
    
    def to_dict(self) -> Dict[str, object]:
        return {"name": self.name, "children": [child.to_dict() for child in self.children]}


perception_tree = Node("perception")


def get_structure() -> Dict[str, object]:
    return perception_tree.to_dict()


package_path = "gordon.system.src.agent.systems.perception"
parent_package = "g Gordon.system.src.agent.systems"
allowed_children = []
required_children = []
required_files = ["__init__.py", "__meta__.py", "__tree__.py"]
forbidden_children = []
ownership_boundary = "gordon.system.src.agent.systems.perception.*"
dependency_direction = "downward"
runtime_activation_policy = "never"


def get_contract() -> Dict[str, object]:
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


__all__ = ["Node", "perception_tree", "get_structure", "get_contract", "package_path",
           "parent_package", "allowed_children", "required_children", "required_files",
           "forbidden_children", "ownership_boundary", "dependency_direction",
           "runtime_activation_policy"]