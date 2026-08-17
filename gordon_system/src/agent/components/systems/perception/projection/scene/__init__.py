# Perception Projection - Scene Module
# ======================================

"""
Scene Projection: Exposes one or more perceptual Scenes.

A Scene Projection exposes one or more perceptual Scenes.
It may include participating Percepts, structural relations,
temporal extent, spatial reference frames, modality participation,
active Events, conflicts, ambiguity, missing evidence,
scene confidence, scene uncertainty.

A Scene Projection remains observational. It does not become a World Model.
"""

from .projection import (
    SceneProjection,
    ProjectedSceneStructure,
)

__all__ = [
    "SceneProjection",
    "ProjectedSceneStructure",
]