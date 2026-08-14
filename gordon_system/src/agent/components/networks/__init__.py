# Networks Layer
# ==============

"""
Networks Layer for Gordon.

This package provides canonical contracts and implementations for signal
coordination networks. A Network answers:
    
    How should related signals, evidence, and computational contributions be
    combined into one structured coordination result?

Networks do NOT answer:

    What enduring objective should Gordon pursue?
    Which ExecutionThread should run next?
    Should the current Thread be interrupted?

That belongs to higher semantic layers (Execution, Executive, Arbitration).
"""

from gordon_system.src.agent.components.networks.alerting import (
    AlertingNetworkConfig,
    AlertingInput,
    AlertingContext,
    AlertingAssessment,
    AlertingFeatures,
    AlertingLevel,
    AlertingRecommendation,
    AlertingReason,
    AlertingNetworkStateSnapshot,
)

__all__ = [
    "AlertingNetworkConfig",
    "AlertingInput",
    "AlertingContext",
    "AlertingAssessment",
    "AlertingFeatures",
    "AlertingLevel",
    "AlertingRecommendation",
    "AlertingReason",
    "AlertingNetworkStateSnapshot",
]
