# Spatial Binding - Phase 5.2.3
# =============================

"""
Spatial Binding: Organizes perceptual artifacts into coherent spatial structures.

Spatial Binding answers:
    Which perceptual artifacts occupy, compose or refer to the same spatial,
    topological or hierarchical structure?
"""

from gordon_system.src.agent.components.systems.perception.integration.spatial_binding.request import SpatialBindingRequest
from gordon_system.src.agent.components.systems.perception.integration.spatial_binding.result import SpatialBindingResult
from gordon_system.src.agent.components.systems.perception.integration.spatial_binding.binding import (
    SpatialBinding,
    SpatialRelation,
)

__all__ = [
    "SpatialBindingRequest",
    "SpatialBindingResult",
    "SpatialBinding",
    "SpatialRelation",
]