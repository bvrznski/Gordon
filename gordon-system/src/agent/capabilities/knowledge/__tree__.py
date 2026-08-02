# Tree: Knowledge Structure
# ============================

from ...__tree__ import Node


def get_structure() -> dict:
    """Return the knowledge structure."""
    from ...__tree__ import capabilities
    for child in capabilities.children:
        if child.name == "knowledge":
            return child.to_dict()
    return {}


__all__ = ["Node", "get_structure"]