# Reflection State Package
# =======================

"""
Immutable models for reflection coordination state, transitions,
snapshots, and history.

ARCHITECTURAL PRINCIPLES:
    - State is bounded (no unbounded growth)
    - Transitions are semantic records, not runtime actions
    - Snapshots preserve full state at a point in time
    - History is bounded and observable but not persistent memory
"""

from __future__ import annotations

# Core state models
from .model import ReflectionCoordinationState
from .transition import ReflectionTransitionKind, ReflectionTransitionRecord
from .snapshot import ReflectionSnapshot
from .history import ReflectionHistory


__all__ = [
    "ReflectionCoordinationState",
    "ReflectionTransitionKind",
    "ReflectionTransitionRecord",
    "ReflectionSnapshot",
    "ReflectionHistory",
]