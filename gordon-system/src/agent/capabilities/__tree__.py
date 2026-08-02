# Tree: Capabilities Layer Structure
# ====================================

from ..__tree__ import Node


def get_structure() -> dict:
    """Return the capabilities structure as a dictionary."""
    from ..__tree__ import capabilities
    return capabilities.to_dict()


__all__ = ["Node", "get_structure"]