# Perception Projection - Percept Module
# =======================================

"""
Percept Projection: Exposes selected Percepts or Fused Percepts.

A Percept Projection exposes selected Percepts or Fused Percepts.
It may expose artifact identity, percept kind, source Modalities,
observed properties, temporal extent, spatial extent, confidence,
uncertainty, conflicts, alternatives, limitations, and provenance.

A Percept Projection shall not assign canonical environmental entity identity.
"""

from .projection import (
    PerceptProjection,
    PerceptProjectionBuilder,
)

__all__ = [
    "PerceptProjection",
    "PerceptProjectionBuilder",
]