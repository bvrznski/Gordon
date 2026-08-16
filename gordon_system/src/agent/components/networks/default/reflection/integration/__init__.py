# Reflection Integration Package
# ==============================

"""
Integration helpers for reflection coordination.

This package provides integration points between reflection coordination
and external systems (memory, narrative, identity, workspace).

ARCHITECTURAL PRINCIPLES:
    • These are integration HINTS, not implementations
    • No runtime dependencies in this package
    • All integrations are advisory (never automatic)
"""

from __future__ import annotations


# Integration proposal types - re-export from outcome.py for convenience
from ..outcome import (
    ProposalKind,
)

__all__ = [
    "ProposalKind",
]