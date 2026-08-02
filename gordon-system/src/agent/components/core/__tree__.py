# Tree: Core Components Structure
# =================================

"""
Package Contract:
- Package must exist at g Gordon.system.src.agent.components.core
- Must have exactly 16 direct children: contracts, types, exceptions, lifecycle,
  registry, dependency, configuration, context, state, synchronization,
  execution, scheduling, observability, integrity, kernel, runtime
- Deferred children: testing (for test utilities)
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


# Core runtime foundation packages
contracts = Node("contracts")
types = Node("types")
exceptions = Node("exceptions")
lifecycle = Node("lifecycle")
registry = Node("registry")
dependency = Node("dependency")
configuration = Node("configuration")
context = Node("context")
state = Node("state")
synchronization = Node("synchronization")
execution = Node("execution")
scheduling = Node("scheduling")
observability = Node("observability")
integrity = Node("integrity")
kernel = Node("kernel")
runtime = Node("runtime")

# Testing utilities (deferred - test-only)
testing = Node("testing")

core_tree = Node("core")
core_tree.add_child(contracts)
core_tree.add_child(types)
core_tree.add_child(exceptions)
core_tree.add_child(lifecycle)
core_tree.add_child(registry)
core_tree.add_child(dependency)
core_tree.add_child(configuration)
core_tree.add_child(context)
core_tree.add_child(state)
core_tree.add_child(synchronization)
core_tree.add_child(execution)
core_tree.add_child(scheduling)
core_tree.add_child(observability)
core_tree.add_child(integrity)
core_tree.add_child(kernel)
core_tree.add_child(runtime)
core_tree.add_child(testing)


def get_structure() -> Dict[str, object]:
    return core_tree.to_dict()


package_path = "gordon.system.src.agent.components.core"
parent_package = "gordon.system.src.agent.components"
allowed_children = [
    "contracts", "types", "exceptions", "lifecycle", "registry",
    "dependency", "configuration", "context", "state", "synchronization",
    "execution", "scheduling", "observability", "integrity", "kernel",
    "runtime", "testing"
]
required_children = [
    "contracts", "types", "exceptions", "lifecycle", "registry",
    "dependency", "configuration", "context", "state", "synchronization",
    "execution", "scheduling", "observability", "integrity", "kernel",
    "runtime"
]
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


__all__ = [
    "Node", "contracts", "types", "exceptions", "lifecycle", "registry",
    "dependency", "configuration", "context", "state", "synchronization",
    "execution", "scheduling", "observability", "integrity", "kernel",
    "runtime", "testing", "core_tree", "get_structure", "get_contract",
    "package_path", "parent_package", "allowed_children", "required_children",
    "required_files", "forbidden_children", "ownership_boundary",
    "dependency_direction", "runtime_activation_policy"
]