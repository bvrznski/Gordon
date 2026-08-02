# Tree: Capability Map Structure
# ================================

from ...__tree__ import Node


def get_structure() -> dict:
    """Return the capability map structure."""
    from ...__tree__ import architecture
    for child in architecture.children:
        if child.name == "capability_map":
            return child.to_dict()
    return {}


__all__ = ["Node", "get_structure"]