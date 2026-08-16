# Reflection Contracts Package
# ===========================

"""
Contracts for capability invocation boundaries.

This package defines the interface between reflection coordination
and external capability owners without containing implementation details.
"""

from __future__ import annotations


# Re-export main contracts for convenience
from .capability import (
    ReflectionCapabilityRequest,
    ReflectionCapabilityResult,
)

__all__ = [
    "ReflectionCapabilityRequest",
    "ReflectionCapabilityResult",
]