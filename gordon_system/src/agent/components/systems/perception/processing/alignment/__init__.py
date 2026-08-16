# Perception Alignment - Phase 5.2.2
# ==================================

"""
Alignment: Maps perceptual evidence into compatible reference systems.

Alignment prepares evidence for multimodal integration by establishing
compatible temporal, spatial, and semantic relationships.
"""

from __future__ import annotations

from .temporal import TemporalAlignment
from .spatial import SpatialAlignment
from .identity import PerceptualIdentityAlignment
from .schema import PerceptualSchemaAlignment

__all__ = [
    "TemporalAlignment",
    "SpatialAlignment", 
    "PerceptualIdentityAlignment",
    "PerceptualSchemaAlignment",
]