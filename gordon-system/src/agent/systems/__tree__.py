# Tree: Systems Layer Structure
# ==============================

from ..__tree__ import Node


def get_structure() -> dict:
    """Return the systems structure as a dictionary."""
    from ..__tree__ import systems
    return systems.to_dict()


__all__ = ["Node", "get_structure"]