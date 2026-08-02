# Tree: Dependency Graph Structure
# ==================================

from ...__tree__ import Node


def get_structure() -> dict:
    """Return the dependency graph structure."""
    from ...__tree__ import architecture
    for child in architecture.children:
        if child.name == "dependency_graph":
            return child.to_dict()
    return {}


__all__ = ["Node", "get_structure"]