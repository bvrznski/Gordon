# Motivational Projection Network - Phase 4.10.6
# ================================================
#
# The Motivational Reward Integration Engine transforms semantic reward into
# motivational projections without creating or modifying actual drives.
#
# ARCHITECTURE:
#
#     Reward Network
#            ↓
#     MultiDomainRewardState
#            ↓
#     MotivationalProjectionEngine
#            ↓
#     MotivationalProjectionState
#            ↓
#     Motivation System (separate subsystem)
#
# This subsystem implements PROJECTION only. It never owns motivation.

"""
Motivational Projection Network (Phase 4.10.6)

The Motivational Reward Integration Engine transforms semantic reward into
motivational projections without creating or modifying actual drives.

This is one of Gordon's most important architectural boundaries - the separation
between evaluation (Reward Network) and motivation (separate system).
"""

from .projection import DriveProjection, ProjectionType
from .tension import MotivationalTension, TensionType
from .synergy import MotivationalSynergy, SynergyType
from .graph import ProjectionGraph, GraphEdgeType
from .hierarchy import ProjectionHierarchy
from .temporal import TemporalProjection
from .field import MotivationalRewardField
from .state import MotivationalProjectionState
from .engine import MotivationalProjectionEngine
from .validation import MotivationalProjectionValidator

__all__ = [
    # Core models
    "DriveProjection",
    "ProjectionType",
    "MotivationalTension",
    "TensionType",
    "MotivationalSynergy",
    "SynergyType",
    "ProjectionGraph",
    "GraphEdgeType",
    "ProjectionHierarchy",
    "TemporalProjection",
    # Aggregate structures
    "MotivationalRewardField",
    "MotivationalProjectionState",
    # Engine and validation
    "MotivationalProjectionEngine",
    "MotivationalProjectionValidator",
]