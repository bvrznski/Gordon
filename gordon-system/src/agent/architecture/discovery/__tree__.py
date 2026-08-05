# Tree: Architecture Discovery Layer Structure
# =============================================

"""
Package Contract:

This file defines the structural contract for the architecture discovery layer.
It specifies allowed and required children, ownership boundaries,
and architectural invariants.

No executable code - only declarations.

Architectural Invariants:
1. Package must exist at gordon.system.src.agent.architecture.discovery
2. Must have exactly the standard discovery components
3. No runtime implementation may appear in this layer (only models)
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


# Architecture discovery layer structure
inventory = Node("inventory")
package_manager = Node("package_manager")
module_manager = Node("module_manager")
authority_manager = Node("authority_manager")
dependency_manager = Node("dependency_manager")
import_graph = Node("import_graph")
topology_manager = Node("topology_manager")
report_manager = Node("report_manager")
metrics_manager = Node("metrics_manager")

discovery_tree = Node("discovery")
discovery_tree.add_child(inventory)
discovery_tree.add_child(package_manager)
discovery_tree.add_child(module_manager)
discovery_tree.add_child(authority_manager)
discovery_tree.add_child(dependency_manager)
discovery_tree.add_child(import_graph)
discovery_tree.add_child(topology_manager)
discovery_tree.add_child(report_manager)
discovery_tree.add_child(metrics_manager)


def get_structure() -> Dict[str, object]:
    """Return the architecture structure as a dictionary."""
    return discovery_tree.to_dict()


# Contract properties for validation
package_path = "gordon.system.src.agent.architecture.discovery"
parent_package = "gordon.system.src.agent.architecture"
allowed_children = [
    "inventory",
    "package_manager", 
    "module_manager",
    "authority_manager",
    "dependency_manager",
    "import_graph",
    "topology_manager",
    "report_manager",
    "metrics_manager",
]
required_children = allowed_children.copy()
required_files = ["__init__.py", "__meta__.py", "__tree__.py"]
forbidden_children = []
ownership_boundary = "gordon.system.src.agent.architecture.discovery.*"
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
    "inventory", "package_manager", "module_manager",
    "authority_manager", "dependency_manager", "import_graph",
    "topology_manager", "report_manager", "metrics_manager",
    "discovery_tree", "get_structure", "get_contract",
    # Contract properties
    "package_path", "parent_package",
    "allowed_children", "required_children",
    "required_files", "forbidden_children",
    "ownership_boundary", "dependency_direction",
    "runtime_activation_policy"
]