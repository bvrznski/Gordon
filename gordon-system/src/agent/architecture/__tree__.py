# Tree: Architecture Layer Structure
# ===================================

from ..__tree__ import Node


def get_structure() -> dict:
    """Return the architecture structure as a dictionary."""
    from ..__tree__ import architecture
    return architecture.to_dict()


__all__ = ["Node", "get_structure"]