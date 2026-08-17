"""Inter-Layer Mapping - Phase 6.8 Part 2 Section 10.

This module is the canonical location for the InterLayerMapping contract.
The class is defined in ``layer.py`` and re-exported here so that both
import paths work:

    from ...shared.mapping import InterLayerMapping
    from ...shared.layer    import InterLayerMapping

Per LAYER-LAW-003: Inter-layer mappings shall remain explicit.
Mappings preserve semantic identity.
"""

from __future__ import annotations

from .layer import InterLayerMapping

__all__ = [
    "InterLayerMapping",
]