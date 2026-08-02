# Tree: Components Layer Structure
# ==================================

"""
Package Contract:
- Package must exist at g Gordon.system.src.agent.components
- Must have exactly one direct child: core
- No runtime implementation may appear in this layer
- All contracts are repair-safe
"""

from typing import Dict, List


class Node:
    """Node in the components tree structure."""
    
    def __init__(self, name: str):
        self.name = name
        self.children: List["Node"] = []
    
    def add_child(self, child: "Node") -> None:
        self.children.append(child)
    
    def to_dict(self) -> Dict[str, object]:
        return {"name": self.name, "children": [child.to_dict() for child in self.children]}


# Core components
core = Node("core")
core.add_child(Node("engine"))
core.add_child(Node("executor"))
core.add_child(Node("manager"))

components_tree = Node("components")
components_tree.add_child(core)


def get_structure() -> Dict[str, object]:
    return components_tree.to_dict()


package_path = "gordon.system.src.agent.components"
parent_package = "gordon.system.src.agent"
allowed_children = ["core"]
required_children = ["core"]
required_files = ["__init__.py", "__meta__.py", "__tree__.py"]
forbidden_children = []
ownership_boundary = "gordon.system.src.agent.components.*"
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


__all__ = ["Node", "core", "components_tree", "get_structure", "get_contract", "package_path",
           "parent_package", "allowed_children", "required_children", "required_files",
           "forbidden_children", "ownership_boundary", "dependency_direction",
           "runtime_activation_policy"]