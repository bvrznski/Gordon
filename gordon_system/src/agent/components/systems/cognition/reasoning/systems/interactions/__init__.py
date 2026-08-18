# Interactions Module - Phase 7.38
# =================================

"""
Interaction management for Systems Reasoning.

Interaction management evaluates:
    - information exchange
    - resource exchange
    - control dependencies
    - synchronization
    - communication
    - coupling

Interactions remain explicit.
"""

from .manager import InteractionManager, InteractionNetwork

__all__ = [
    "InteractionManager",
    "InteractionNetwork",
]