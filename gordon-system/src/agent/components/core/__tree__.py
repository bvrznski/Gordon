# Tree: Core Components Structure
# =================================

"""
Package Contract:
- Package must exist at g Gordon.system.src.agent.components.core
- Must have exactly three direct children: engine, executor, manager
- No runtime implementation may appear in this layer
- All contracts are repair-safe
"""

from typing import Dict, List


class Node:
    """Node in the core components tree structure."""
    
    def __init__(self, name: str):
        self.name = name
        self.children: List["Node"] = []
    
    def add_child(self, child: "Node") -> None:
        self.children.append(child)
    
    def to_dict(self) -> Dict[str, object]:
        return {"name": self.name, "children": [child.to_dict() for child in self.children]}


engine = Node("engine")
executor = Node("executor")
manager = Node("manager")

core_tree = Node("core")
core_tree.add_child(engine)
core_tree.add_child(executor)
core_tree.add_child(manager)


def get_structure() -> Dict[str, object]:
    return core_tree.to_dict()


package_path = "gordon.system.src.agent.components.core"
parent_package = "gordon.system.src.agent.components"
allowed_children = ["engine", "executor", "manager"]
required_children = allowed_children.copy()
required_files = ["__init__.py", "__meta__.py", "__tree__.py"]
forbidden_children = []
ownership_boundary = "g Gordon.system.src.agent.components.core.*"
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


__all__ = ["Node", "engine", "executor", "manager", "core_tree", "get_structure", "get_contract",
           "package_path", "parent_package", "allowed_children", "required_children",
           "required_files", "forbidden_children", "ownership_boundary",
           "dependency_direction", "runtime_activation_policy"]