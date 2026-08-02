# Tree: Core Components Structure
# =================================

from ..__tree__ import Node


def get_structure() -> dict:
    """Return the core components structure."""
    from ..__tree__ import components
    for child in components.children:
        if child.name == "core":
            return child.to_dict()
    return {}


__all__ = ["Node", "get_structure"]