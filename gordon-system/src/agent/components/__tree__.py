# Tree: Components Layer Structure
# ==================================

from ..__tree__ import Node


def get_structure() -> dict:
    """Return the components structure as a dictionary."""
    from ..__tree__ import components
    return components.to_dict()


__all__ = ["Node", "get_structure"]