# Tree: Systems Layer Structure
# ==============================

"""
Package Contract:
- Package must exist at g Gordon.system.src.agent.systems
- Must have exactly two direct children: memory, perception
- No runtime implementation may appear in this layer
- All contracts are repair-safe
"""

from typing import Dict, List


class Node:
    """Node in the systems tree structure."""
    
    def __init__(self, name: str):
        self.name = name
        self.children: List["Node"] = []
    
    def add_child(self, child: "Node") -> None:
        self.children.append(child)
    
    def to_dict(self) -> Dict[str, object]:
        return {"name": self.name, "children": [child.to_dict() for child in self.children]}


memory = Node("memory")
perception = Node("perception")

systems_tree = Node("systems")
systems_tree.add_child(memory)
systems_tree.add_child(perception)


def get_structure() -> Dict[str, object]:
    return systems_tree.to_dict()


package_path = "gordon.system.src.agent.systems"
parent_package = "g Gordon.system.src.agent"
allowed_children = ["memory", "perception"]
required_children = allowed_children.copy()
required_files = ["__init__.py", "__meta__.py", "__tree__.py"]
forbidden_children = []
ownership_boundary = "g Gordon.system.src.agent.systems.*"
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


__all__ = ["Node", "memory", "perception", "systems_tree", "get_structure", "get_contract",
           "package_path", "parent_package", "allowed_children", "required_children",
           "required_files", "forbidden_children", "ownership_boundary",
           "dependency_direction", "runtime_activation_policy"]