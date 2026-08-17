# Perception Projection - Workspace Module
# =========================================

"""
Workspace Projection: Exposes a bounded perceptual view for Workspace Network.

A Workspace Projection exposes a bounded perceptual view suitable for admission
into the Workspace Network. It may include currently relevant Percepts, active
Scene fragment, active Events, recent changes, conflicts, ambiguity, missing
evidence, modality availability, confidence, uncertainty.

The Workspace Projection does not own Workspace state. It produces a candidate
Workspace-facing perceptual representation.
"""

from .projection import (
    WorkspacePerceptionProjection,
)

__all__ = [
    "WorkspacePerceptionProjection",
]