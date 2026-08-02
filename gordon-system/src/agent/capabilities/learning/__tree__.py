# Tree: Learning Structure
# ===========================

from ...__tree__ import Node


def get_structure() -> dict:
    """Return the learning structure."""
    from ...__tree__ import capabilities
    for child in capabilities.children:
        if child.name == "learning":
            return child.to_dict()
    return {}


__all__ = ["Node", "get_structure"]