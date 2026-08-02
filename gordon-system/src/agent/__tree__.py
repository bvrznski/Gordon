# Tree: Gordon Agent Structure
# =============================

from typing import Dict, List


class Node:
    """Node in the package tree structure."""
    def __init__(self, name: str):
        self.name = name
        self.children: List["Node"] = []
    
    def add_child(self, child: "Node") -> None:
        self.children.append(child)
    
    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "children": [child.to_dict() for child in self.children],
        }


# Architecture Layer
architecture = Node("architecture")
architecture.add_child(Node("capability_map"))
architecture.add_child(Node("dependency_graph"))
architecture.add_child(Node("ownership"))
architecture.add_child(Node("topology"))

# Capability Layer (memory and perception removed - moved to systems)
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

# Component Layer
components = Node("components")
core = Node("core")
core.add_child(Node("engine"))
core.add_child(Node("executor"))
core.add_child(Node("manager"))
components.add_child(core)

# Systems Layer (memory and perception moved here)
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


__all__ = ["Node", "architecture", "capabilities", "components", "systems", "tree", "get_structure"]