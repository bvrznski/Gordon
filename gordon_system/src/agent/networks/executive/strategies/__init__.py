# Executive Strategy Package
# ==========================

"""
Executive Strategy - The authoritative, bounded, revisioned semantic representation
of strategy coordination for the Executive Network.

This package provides:
- Canonical immutable strategy definitions
- Assessment and proposal structures
- Runtime-neutral coordinate semantics
"""

from gordon_system.src.agent.networks.executive.strategies.model import (
    ExecutiveStrategy,
    ExecutiveStrategyId,
    ExecutiveStrategyRevision,
    ExecutiveStrategySubject,
    ExecutiveStrategyScope,
)

from gordon_system.src.agent.networks.executive.strategies.purpose import (
    ExecutiveStrategyPurpose,
)

from gordon_system.src.agent.networks.executive.strategies.kind import (
    ExecutiveStrategyKind,
)

from gordon_system.src.agent.networks.executive.strategies.status import (
    ExecutiveStrategyStatus,
)

from gordon_system.src.agent.networks.executive.strategies.activation import (
    ExecutiveStrategyActivationState,
)

from gordon_system.src.agent.networks.executive.strategies.principle import (
    ExecutiveStrategyPrinciple,
)

from gordon_system.src.agent.networks.executive.strategies.assumption import (
    ExecutiveStrategyAssumption,
)

from gordon_system.src.agent.networks.executive.strategies.precondition import (
    ExecutiveStrategyPrecondition,
)

from gordon_system.src.agent.networks.executive.strategies.constraint import (
    ExecutiveStrategyConstraintReference,
)

from gordon_system.src.agent.networks.executive.strategies.dependency import (
    ExecutiveStrategyDependency,
)

from gordon_system.src.agent.networks.executive.strategies.evidence import (
    ExecutiveStrategyEvidenceRequirement,
)

from gordon_system.src.agent.networks.executive.strategies.monitoring import (
    ExecutiveStrategyMonitoringRequirement,
)

from gordon_system.src.agent.networks.executive.strategies.performance import (
    ExecutiveStrategyPerformanceCriteria,
)

from gordon_system.src.agent.networks.executive.strategies.completion import (
    ExecutiveStrategyCompletionCriteria,
)

from gordon_system.src.agent.networks.executive.strategies.failure import (
    ExecutiveStrategyFailureCriteria,
    ExecutiveStrategyFailureAssessment,
)

from gordon_system.src.agent.networks.executive.strategies.abandonment import (
    ExecutiveStrategyAbandonmentCriteria,
    ExecutiveStrategyAbandonmentProposal,
)

from gordon_system.src.agent.networks.executive.strategies.fallback import (
    ExecutiveStrategyFallback,
)

from gordon_system.src.agent.networks.executive.strategies.recovery import (
    ExecutiveStrategyRecoveryConditions,
    ExecutiveStrategyRecoveryAssessment,
    ExecutiveStrategyRecoveryProposal,
)

from gordon_system.src.agent.networks.executive.strategies.alternative import (
    ExecutiveStrategyAlternative,
)

from gordon_system.src.agent.networks.executive.strategies.applicability import (
    ExecutiveStrategyApplicabilityAssessment,
)

from gordon_system.src.agent.networks.executive.strategies.eligibility import (
    ExecutiveStrategyEligibilityAssessment,
)

from gordon_system.src.agent.networks.executive.strategies.readiness import (
    ExecutiveStrategyReadinessAssessment,
)

from gordon_system.src.agent.networks.executive.strategies.feasibility import (
    ExecutiveStrategyFeasibilityAssessment,
)

from gordon_system.src.agent.networks.executive.strategies.adequacy import (
    ExecutiveStrategyAdequacyAssessment,
)

from gordon_system.src.agent.networks.executive.strategies.risk import (
    ExecutiveStrategyRiskAssessment,
)

from gordon_system.src.agent.networks.executive.strategies.cost import (
    ExecutiveStrategyCostAssessment,
)

from gordon_system.src.agent.networks.executive.strategies.benefit import (
    ExecutiveStrategyBenefitAssessment,
)

from gordon_system.src.agent.networks.executive.strategies.reversibility import (
    ExecutiveStrategyReversibility,
)

from gordon_system.src.agent.networks.executive.strategies.adaptability import (
    ExecutiveStrategyAdaptability,
)

from gordon_system.src.agent.networks.executive.strategies.persistence import (
    ExecutiveStrategyPersistence,
)

from gordon_system.src.agent.networks.executive.strategies.drift import (
    ExecutiveStrategyDriftAssessment,
)

from gordon_system.src.agent.networks.executive.strategies.hierarchy import (
    ExecutiveStrategyHierarchy,
)

from gordon_system.src.agent.networks.executive.strategies.composition import (
    ExecutiveStrategyComposition,
)

from gordon_system.src.agent.networks.executive.strategies.decomposition import (
    ExecutiveStrategyDecomposition,
)

from gordon_system.src.agent.networks.executive.strategies.competition import (
    ExecutiveStrategyCompetition,
)

from gordon_system.src.agent.networks.executive.strategies.conflict import (
    ExecutiveStrategyConflict,
)

from gordon_system.src.agent.networks.executive.strategies.interference import (
    ExecutiveStrategyInterferenceAssessment,
)

from gordon_system.src.agent.networks.executive.strategies.comparison import (
    ExecutiveStrategyComparison,
    ExecutiveStrategyRelation,
)

from gordon_system.src.agent.networks.executive.strategies.selection import (
    ExecutiveStrategySelectionRecommendation,
)

from gordon_system.src.agent.networks.executive.strategies.commitment import (
    ExecutiveStrategyCommitmentAssessment,
    ExecutiveStrategyCommitmentProposal,
)

from gordon_system.src.agent.networks.executive.strategies.activation_proposal import (
    ExecutiveStrategyActivationProposal,
)

from gordon_system.src.agent.networks.executive.strategies.maintenance import (
    ExecutiveStrategyMaintenanceAssessment,
    ExecutiveStrategyMaintenanceProposal,
)

from gordon_system.src.agent.networks.executive.strategies.revision_proposal import (
    ExecutiveStrategyRevisionAssessment,
    ExecutiveStrategyRevisionProposal,
)

from gordon_system.src.agent.networks.executive.strategies.suspension import (
    ExecutiveStrategySuspensionAssessment,
    ExecutiveStrategySuspensionProposal,
)

from gordon_system.src.agent.networks.executive.strategies.restoration import (
    ExecutiveStrategyRestorationAssessment,
    ExecutiveStrategyRestorationProposal,
)

from gordon_system.src.agent.networks.executive.strategies.replacement import (
    ExecutiveStrategyReplacementAssessment,
    ExecutiveStrategyReplacementProposal,
)

from gordon_system.src.agent.networks.executive.strategies.termination import (
    ExecutiveStrategyTerminationAssessment,
    ExecutiveStrategyTerminationProposal,
)

from gordon_system.src.agent.networks.executive.strategies.outcome import (
    ExecutiveStrategyOutcomeAssessment,
)

__all__ = (
    # Core types
    "ExecutiveStrategy",
    "ExecutiveStrategyId",
    "ExecutiveStrategyRevision",
    "ExecutiveStrategySubject",
    "ExecutiveStrategyScope",
)