# Memory Integration State
# ========================

"""
State management for memory integration.

ARCHITECTURAL PRINCIPLES:
    - Frozen state (deeply immutable)
    - Bounded history only
"""

from __future__ import annotations


__all__ = [
    "MemoryIntegrationStateKind",
    "MemoryIntegrationState",
    "StateTransitionKind",
    "StateTransition",
    "StateSnapshot",
    "HistoryEntry",
]

from .model import (
    MemoryIntegrationState,
    MemoryIntegrationStateKind,
    StateTransition,
    StateTransitionKind,
    StateSnapshot,
    HistoryEntry,
)