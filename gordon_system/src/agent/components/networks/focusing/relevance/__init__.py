# Relevance Module - Focusing Network
# ====================================

"""
Relevance-related computations for the FocusingNetwork.

This module handles:
    - Goal-directed relevance estimation
    - Priority aggregation
    - Competition analysis
    - Suppression recommendations

Note: This module delegates to specialized submodules.
"""

from gordon_system.src.agent.components.networks.focusing.relevance.estimators import (
    GoalRelevanceEstimator,
    ContextRelevanceEstimator,
    PolicyModulator,
)

from gordon_system.src.agent.components.networks.focusing.relevance.competition import (
    CompetitionAnalyzer,
    ConflictDetector,
    CompatibilityEstimator,
    SuppressionEstimator,
    DominanceAnalyzer,
)

__all__ = [
    "GoalRelevanceEstimator",
    "ContextRelevanceEstimator", 
    "PolicyModulator",
    "CompetitionAnalyzer",
    "ConflictDetector",
    "CompatibilityEstimator",
    "SuppressionEstimator",
    "DominanceAnalyzer",
]