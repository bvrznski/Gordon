# Salience Network Integration Module

"""
Integration layer for the Salience Network.

This module provides repository-level integration contracts that govern
how the Salience Network interacts with other subsystems.
"""

from __future__ import annotations

# Repository Registry (Phase 4.8.1)
from ._registry import (
    SalienceRepositoryRegistry,
    SalienceArchitectureLayer,
    SalienceDependencyGraph,
    SalienceOwnershipGraph,
)

__all__ = [
    # Repository Integration
    "SalienceRepositoryRegistry",
    "SalienceArchitectureLayer",
    "SalienceDependencyGraph",
    "SalienceOwnershipGraph",
]