# Executive Demand Package - Phase 4.4.5
# ========================================

"""
Executive Demand Assessment and Management Module.

This module provides the semantic architecture for assessing executive demand:
the amount, persistence, specificity, and type of control that may be required
to maintain, restore, redirect, suspend, or safely terminate coherent cognitive
progression.
"""

from __future__ import annotations

# =============================================================================
# DEMAND ASSESSMENT TYPES
# =============================================================================

# Demand assessment (main assessment)
from gordon_system.src.agent.networks.executive.demand.assessment import (
    ExecutiveDemandAssessment,
    ExecutiveDemandAssessmentId,
)

# Demand levels and profiles
from gordon_system.src.agent.networks.executive.demand.level import (
    ExecutiveDemandLevel,
)

from gordon_system.src.agent.networks.executive.demand.profile import (
    ExecutiveDemandProfile,
)

from gordon_system.src.agent.networks.executive.demand.target import (
    ExecutiveDemandTarget,
)

# =============================================================================
# DEMAND COMPONENTS
# =============================================================================

# Demand component types
from gordon_system.src.agent.networks.executive.demand.uncertainty import (
    ExecutiveUncertaintyDemand,
)

from gordon_system.src.agent.networks.executive.demand.evidence_gap import (
    ExecutiveEvidenceGap,
    ExecutiveEvidenceGapDemand,
)

from gordon_system.src.agent.networks.executive.demand.decision import (
    ExecutiveDecisionDemand,
)

from gordon_system.src.agent.networks.executive.demand.switching import (
    ExecutiveSwitchingDemand,
)

from gordon_system.src.agent.networks.executive.demand.inhibition import (
    ExecutiveInhibitionDemand,
)

from gordon_system.src.agent.networks.executive.demand.monitoring import (
    ExecutiveMonitoringDemand,
)

from gordon_system.src.agent.networks.executive.demand.recovery import (
    ExecutiveRecoveryDemand,
)

from gordon_system.src.agent.networks.executive.demand.effort import (
    ExecutiveEffortDemand,
)

# =============================================================================
# CONTROL ASSESSMENT TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.demand.insufficiency import (
    ControlInsufficiencyAssessment,
)

from gordon_system.src.agent.networks.executive.demand.saturation import (
    ControlSaturationAssessment,
)

from gordon_system.src.agent.networks.executive.demand.overload import (
    ExecutiveOverloadAssessment,
)

# =============================================================================
# DEMAND METRICS
# =============================================================================

from gordon_system.src.agent.networks.executive.demand.urgency import (
    ExecutiveDemandUrgency,
)

from gordon_system.src.agent.networks.executive.demand.persistence import (
    ExecutiveDemandPersistence,
)

from gordon_system.src.agent.networks.executive.demand.recommendation import (
    ExecutiveDemandRecommendation,
)

# =============================================================================
# EXPORTS - Canonical public API
# =============================================================================

__all__: tuple[str, ...] = (
    # Main assessment types
    "ExecutiveDemandAssessment",
    "ExecutiveDemandAssessmentId",
    
    # Level and profile types
    "ExecutiveDemandLevel",
    "ExecutiveDemandProfile",
    
    # Target types
    "ExecutiveDemandTarget",
    
    # Component types
    "ExecutiveUncertaintyDemand",
    "ExecutiveEvidenceGap",
    "ExecutiveEvidenceGapDemand",
    "ExecutiveDecisionDemand",
    "ExecutiveSwitchingDemand",
    "ExecutiveInhibitionDemand",
    "ExecutiveMonitoringDemand",
    "ExecutiveRecoveryDemand",
    "ExecutiveEffortDemand",
    
    # Control assessment types
    "ControlInsufficiencyAssessment",
    "ControlSaturationAssessment",
    "ExecutiveOverloadAssessment",
    
    # Metrics
    "ExecutiveDemandUrgency",
    "ExecutiveDemandPersistence",
    "ExecutiveDemandRecommendation",
)