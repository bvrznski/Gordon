# Salience Network Validation Module

"""
Validation layer for the Salience Network.

This module provides deterministic validation contracts without runtime behavior.
"""

from __future__ import annotations

# Validation Framework (Phase 4.8.1)
from ._framework import (
    SalienceValidator,
    SalienceValidationResult,
    SalienceValidationError,
    SalienceOwnershipInvariant,
    SalienceArchitectureInvariant,
)

__all__ = [
    # Validation Framework
    "SalienceValidator",
    "SalienceValidationResult",
    "SalienceValidationError",
    "SalienceOwnershipInvariant",
    "SalienceArchitectureInvariant",
]