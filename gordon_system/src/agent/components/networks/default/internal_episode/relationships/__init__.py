# Relationships Module Package
# ===========================

"""
Relationships package for internal episode parent-child coordination.

Provides models for episode derivation, delegation, and relationship tracking.
"""

from __future__ import annotations

from .parent_child import (
    InternalEpisodeRelationship,
)
from .derivation import (
    DerivationKind,
)

__all__ = [
    "InternalEpisodeRelationship",
    "DerivationKind",
]