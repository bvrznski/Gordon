# Gordon Executive Decision Coordination Index - Phase 4.4.10C Part 4
# ==================================================================

"""
Package index for decision coordination subsystem.

This module provides a single import point for all decision coordination artifacts.
"""

__version__ = "1.0.0"

from .__init__ import (
    # Identity types
    ExecutiveDecisionCoordinationRequestId,
    ExecutiveDecisionProjectionId,
    ExecutiveDecisionCoordinationResponseId,
    ExecutiveDecisionCoordinationOutcomeId,
    ExecutiveDecisionStateId,
    ExecutiveDecisionHistoryEntryId,
    ExecutiveDecisionTransitionId,
    ExecutiveDecisionContinuationId,
    ActionSelectionRequestId,
    ActionSelectionOutcomeId,
    SelectedActionReferenceId,
    ExecutiveExecutionReadinessProjectionId,
    # Enum types
    ExecutiveDecisionCoordinationSubjectKind,
    ExecutiveDecisionCoordinationTargetKind,
    ExecutiveDecisionCoordinationPurpose,
    ExecutiveDecisionCoordinationKind,
    ExecutiveDecisionCoordinationRequirementKind,
)

from .coordination import (
    # Contract types
    ExecutiveDecisionCoordinationSubject,
    ExecutiveDecisionCoordinationTarget,
    ExecutiveDecisionCoordinationRequirement,
    ExecutiveDecisionCoordinationConstraint,
    ExecutiveDecisionCoordinationDependency,
    ExecutiveDecisionProjection,
    AcceptanceCondition,
    CompletionCondition,
    ExecutiveDecisionCoordinationRequest,
    ProductReference,
    CompletionRequirements,
    ExecutiveDecisionCoordinationResponse,
    ReturnedProduct,
    ExecutiveDecisionCoordinationOutcome,
    OmissionSummary,
    DecisionContinuation,
    ActionSelectionRequest,  # TERMINAL EXECUTIVE PRODUCT
    ActionSelectionConstraint,
    ActionAuthorityRequirement,
    ActionPropertyPreference,
    ActionSelectionEvidenceRequirement,
    ActionSelectionReturnRequirements,
    ActionSelectionOutcome,
    AdmissibilityAssessment,
    FeasibilityAssessment,
    PolicyAssessment,
    SecurityAssessment,
    AuthorityAssessment,
    ReversibilityAssessment,
    ExpectedOutcomeAssessment,
    ActionDisposition,
    ExecutiveExecutionReadinessProjection,
    ExecutiveExecutionReadinessStatus,
    ExecutiveDecisionOutcomeIntegration,
    ExecutiveDecisionOutcomeRelation,
    ExecutiveDecisionPostSelectionAssessment,
    ExecutiveDecisionCoordinationCompletionAssessment,
)

from .state import (
    # State types
    ExecutiveDecisionStateId as DecisionStateId,
    ExecutiveDecisionState,
    ExecutiveDecisionStateSummary,
    ExecutiveDecisionHistoryEntry,
    ExecutiveDecisionLineage,
    ExecutiveDecisionDelta,
    ExecutiveDecisionTransition,
    ExecutiveDecisionContinuation,
    ExecutiveDecisionCoordinationPlan,
    CoordinationStage,
    ExecutiveDecisionDownstreamInvalidation,
    ExecutiveDecisionCoordinationReplayRecord,
    TargetResolution,
    ProjectionGeneration,
)

# Export the API convenience functions
from .api import (
    create_coordination_request,
    create_action_selection_request_from_decision,
    create_coordination_response,
)