# Salience Network Serialization Module

"""
Serialization layer for the Salience Network.

This module provides deterministic serialization contracts without runtime behavior.
"""

from __future__ import annotations

# Serialization Framework (Phase 4.8.1)
from ._framework import (
    SalienceSerializer,
    SalienceDeserializer,
    SalienceSchemaVersion,
    SalienceRevision,
)

__all__ = [
    # Serialization Framework
    "SalienceSerializer",
    "SalienceDeserializer",
    "SalienceSchemaVersion",
    "SalienceRevision",
]