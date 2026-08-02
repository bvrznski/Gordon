# Tree: Topology Structure
# ==========================

from ...__tree__ import Node


def get_structure() -> dict:
    """Return the topology structure."""
    from ...__tree__ import architecture
    for child in architecture.children:
        if child.name == "topology":
            return child.to_dict()
    return {}


__all__ = ["Node", "get_structure"]