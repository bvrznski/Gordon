# Perception Projection - Snapshot Module
# =======================================

"""
Snapshot Projection: Captures one immutable perceptual view at a specific revision.

A Snapshot Projection captures one immutable perceptual view at a specific semantic
revision. Snapshots remain stable even when Perception continues evolving.
"""

from .projection import PerceptionSnapshotProjection

__all__ = ["PerceptionSnapshotProjection"]