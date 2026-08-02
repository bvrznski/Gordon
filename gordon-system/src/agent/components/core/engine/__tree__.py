# Tree: Engine Structure
# ========================

from ....__tree__ import Node


def get_structure() -> dict:
    """Return the engine structure."""
    from ....__tree__ import core
    for child in core.children:
        if child.name == "engine":
            return child.to_dict()
    return {}


__all__ = ["Node", "get_structure"]