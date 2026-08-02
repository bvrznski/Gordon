# Tree: Ownership Structure
# ===========================

from ...__tree__ import Node


def get_structure() -> dict:
    """Return the ownership structure."""
    from ...__tree__ import architecture
    for child in architecture.children:
        if child.name == "ownership":
            return child.to_dict()
    return {}


__all__ = ["Node", "get_structure"]