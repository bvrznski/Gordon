# Memory Integration Validation
# =============================

"""
Validation layer for memory integration.

ARCHITECTURAL PRINCIPLES:
    - Validates structure and content of memory integration components
    - Ensures architectural boundaries are respected
"""

from __future__ import annotations


__all__ = [
    "ArchitectureValidationError",
    "DefaultMemInvariant",
]