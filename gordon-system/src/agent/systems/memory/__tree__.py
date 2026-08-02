# Tree: Memory System Structure
# ===============================

from ..__tree__ import Node


def get_structure() -> dict:
    """Return the memory system structure."""
    from ..__tree__ import systems
    for child in systems.children:
        if child.name == "memory":
            return child.to_dict()
    return {}


__all__ = ["Node", "get_structure"]