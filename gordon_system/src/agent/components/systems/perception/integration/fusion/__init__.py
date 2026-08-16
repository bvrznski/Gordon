# Fusion - Phase 5.2.3
# ====================

"""
Fusion: Constructs integrated perceptual artifacts from multiple evidence sources.

Fusion answers:
    Which compatible evidence should be combined to create a single coherent
    perceptual representation?
"""

from gordon_system.src.agent.components.systems.perception.integration.fusion.request import PerceptualFusionRequest
from gordon_system.src.agent.components.systems.perception.integration.fusion.result import PerceptualFusionResult
from gordon_system.src.agent.components.systems.perception.integration.fusion.strategy import FusionStrategy, FusionStrategyKind

__all__ = [
    "PerceptualFusionRequest",
    "PerceptualFusionResult",
    "FusionStrategy",
    "FusionStrategyKind",
]