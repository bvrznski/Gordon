# Provenance Module for Internal Context
# ======================================

"""
Provenance models for internal context assembly.

Provenance tracks the origin and transformation history of context items
without copying full source payloads.
"""

from __future__ import annotations

from .provenance import InternalContextProvenance, ProjectionProvenance

__all__ = [
    "InternalContextProvenance",
    "ProjectionProvenance",
]