# Executive Conflicts Package - Phase 4.4.5
# ===========================================

"""
Executive Conflict Monitoring and Semantic Conflict Architecture.

This is Phase 4.4.5: Conflict Monitoring and Executive Demand.
"""

from __future__ import annotations

# =============================================================================
# CANONICAL CONFLICT TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.conflicts.model import (
    ExecutiveConflict,
    ExecutiveConflictId,
    ExecutiveConflictRevision,
    ExecutiveConflictSchemaVersion,
)

from gordon_system.src.agent.networks.executive.conflicts.subject import (
    ExecutiveConflictSubject,
    ExecutiveConflictSubjectKind,
)

from gordon_system.src.agent.networks.executive.conflicts.source import (
    ExecutiveConflictSourceReference,
    ExecutiveConflictSourceCategory,
)

from gordon_system.src.agent.networks.executive.conflicts.kind import (
    ExecutiveConflictKind,
)

from gordon_system.src.agent.networks.executive.conflicts.dimension import (
    ExecutiveConflictDimension,
)

from gordon_system.src.agent.networks.executive.conflicts.status import (
    ExecutiveConflictStatus,
)

from gordon_system.src.agent.networks.executive.conflicts.scope import (
    ExecutiveConflictScope,
)

from gordon_system.src.agent.networks.executive.conflicts.evidence import (
    ExecutiveConflictEvidence,
    ExecutiveConflictEvidenceKind,
)

from gordon_system.src.agent.networks.executive.conflicts.relation import (
    ExecutiveConflictRelation,
    ExecutiveConflictRelationKind,
)

from gordon_system.src.agent.networks.executive.conflicts.severity import (
    ExecutiveConflictSeverity,
    ExecutiveConflictSeverityClass,
)

from gordon_system.src.agent.networks.executive.conflicts.persistence import (
    ExecutiveConflictPersistence,
    ExecutiveConflictPersistenceClass,
)

from gordon_system.src.agent.networks.executive.conflicts.recurrence import (
    ExecutiveConflictRecurrence,
    ExecutiveConflictRecurrenceClass,
)

from gordon_system.src.agent.networks.executive.conflicts.propagation import (
    ExecutiveConflictPropagation,
    ExecutiveConflictPropagationTarget,
)

# =============================================================================
# ASSESSMENT TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.conflicts.interference import (
    ExecutiveInterferenceAssessment,
    ExecutiveInterferenceClass,
)

from gordon_system.src.agent.networks.executive.conflicts.ambiguity import (
    ExecutiveAmbiguityAssessment,
    ExecutiveAmbiguityClass,
)

# =============================================================================
# DEMAND COMPONENT TYPES
# =============================================================================

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

from gordon_system.src.agent.networks.executive.conflicts.duplicate import (
    ExecutiveConflictDuplicateAssessment,
)

from gordon_system.src.agent.networks.executive.conflicts.aggregate import (
    ExecutiveConflictAggregate,
)

from gordon_system.src.agent.networks.executive.conflicts.decomposition import (
    ExecutiveConflictDecomposition,
)

# =============================================================================
# TENSION, GAP, AND DEMAND TYPES (demand package)
# =============================================================================

# =============================================================================
# DEMAND TYPES
# =============================================================================

# =============================================================================
# DEMAND COMPONENTS
# =============================================================================

# =============================================================================
# CONTROL ASSESSMENT TYPES
# =============================================================================

# =============================================================================
# MONITORING REQUEST TYPES (Phase 4.4.5 monitoring module)
# =============================================================================

from gordon_system.src.agent.networks.executive.demand.assessment import (
    ExecutiveDemandAssessment,
    ExecutiveDemandAssessmentId,
)

from gordon_system.src.agent.networks.executive.demand.level import (
    ExecutiveDemandLevel,
)

from gordon_system.src.agent.networks.executive.demand.profile import (
    ExecutiveDemandProfile,
)

from gordon_system.src.agent.networks.executive.demand.target import (
    ExecutiveDemandTarget,
)

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

from gordon_system.src.agent.networks.executive.demand.insufficiency import (
    ControlInsufficiencyAssessment,
)

from gordon_system.src.agent.networks.executive.demand.saturation import (
    ControlSaturationAssessment,
)

from gordon_system.src.agent.networks.executive.demand.overload import (
    ExecutiveOverloadAssessment,
)

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
    # Conflict core types
    "ExecutiveConflict",
    "ExecutiveConflictId",
    "ExecutiveConflictRevision",
    "ExecutiveConflictSchemaVersion",
    
    # Subject and source types
    "ExecutiveConflictSubject",
    "ExecutiveConflictSubjectKind",
    "ExecutiveConflictSourceReference",
    "ExecutiveConflictSourceCategory",
    
    # Classification types (enums)
    "ExecutiveConflictKind",
    "ExecutiveConflictDimension",
    "ExecutiveConflictStatus",
    
    # Scope model
    "ExecutiveConflictScope",
    
    # Evidence and relation types
    "ExecutiveConflictEvidence",
    "ExecutiveConflictEvidenceKind",
    "ExecutiveConflictRelation",
    "ExecutiveConflictRelationKind",
    
    # Assessment types
    "ExecutiveConflictSeverity",
    "ExecutiveConflictSeverityClass",
    "ExecutiveConflictPersistence",
    "ExecutiveConflictPersistenceClass",
    "ExecutiveConflictRecurrence",
    "ExecutiveConflictRecurrenceClass",
    "ExecutiveConflictPropagation",
    "ExecutiveConflictPropagationTarget",
    "ExecutiveInterferenceAssessment",
    "ExecutiveInterferenceClass",
    "ExecutiveAmbiguityAssessment",
    "ExecutiveAmbiguityClass",
    "ExecutiveConflictDuplicateAssessment",
    "ExecutiveConflictAggregate",
    "ExecutiveConflictDecomposition",
    
    # Demand types
    "ExecutiveDemandAssessment",
    "ExecutiveDemandAssessmentId",
    "ExecutiveDemandLevel",
    "ExecutiveDemandProfile",
    "ExecutiveDemandTarget",
    "ExecutiveDemandUrgency",
    "ExecutiveDemandPersistence",
    "ExecutiveDemandRecommendation",
    
    # Demand components
    "ExecutiveUncertaintyDemand",
    "ExecutiveEvidenceGap",
    "ExecutiveEvidenceGapDemand",
    "ExecutiveDecisionDemand",
    "ExecutiveSwitchingDemand",
    "ExecutiveInhibitionDemand",
    "ExecutiveMonitoringDemand",
    "ExecutiveRecoveryDemand",
    "ExecutiveEffortDemand",
    
    # Control assessment
    "ControlInsufficiencyAssessment",
    "ControlSaturationAssessment",
    "ExecutiveOverloadAssessment",
)
