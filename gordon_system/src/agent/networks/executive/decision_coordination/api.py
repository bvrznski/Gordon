# Gordon Executive Decision Coordination API - Phase 4.4.10C Part 4
# ==================================================================

"""
Public API for Executive Decision Coordination.

This module provides the stable public interface for the coordination subsystem.
All exports are immutable, runtime-neutral, and preserve subsystem ownership.

PUBLIC API:
===========

Core Types (from __init__.py):
    - ExecutiveDecisionCoordinationRequestId
    - ExecutiveDecisionProjectionId
    - ExecutiveDecisionCoordinationResponseId
    - ExecutiveDecisionCoordinationOutcomeId
    - ExecutiveDecisionStateId
    - ExecutiveDecisionHistoryEntryId
    - ExecutiveDecisionTransitionId
    - ExecutiveDecisionContinuationId
    - ActionSelectionRequestId
    - ActionSelectionOutcomeId
    - SelectedActionReferenceId
    - ExecutiveExecutionReadinessProjectionId

Enums (from __init__.py):
    - ExecutiveDecisionCoordinationSubjectKind
    - ExecutiveDecisionCoordinationTargetKind
    - ExecutiveDecisionCoordinationPurpose
    - ExecutiveDecisionCoordinationKind
    - ExecutiveDecisionCoordinationRequirementKind

Contract Types (from coordination.py):
    - ExecutiveDecisionCoordinationSubject
    - ExecutiveDecisionCoordinationTarget
    - ExecutiveDecisionCoordinationRequirement
    - ExecutiveDecisionCoordinationConstraint
    - ExecutiveDecisionCoordinationDependency
    - ExecutiveDecisionProjection
    - ExecutiveDecisionCoordinationRequest
    - ExecutiveDecisionCoordinationResponse
    - ExecutiveDecisionCoordinationOutcome
    - ActionSelectionRequest (TERMINAL EXECUTIVE PRODUCT)
    - ActionSelectionOutcome (externally owned)

State Types (from state.py):
    - ExecutiveDecisionState
    - ExecutiveDecisionHistoryEntry
    - ExecutiveDecisionLineage
    - ExecutiveDecisionDelta
    - ExecutiveDecisionTransition
    - ExecutiveDecisionContinuation

VALIDATION PIPELINE:
==================

Every public artifact must pass validation before use.

Validation order:
1. Identity validation (unique, non-empty)
2. Revision validation (positive integer)
3. Schema validation (matches expected version)
4. Ownership validation (no ownership transfer implied)
5. Authority validation (required authority present)
6. Policy validation (policy constraints satisfied)
7. Security validation (security constraints satisfied)
8. Boundedness validation (collections bounded)
9. Privacy validation (privacy scope respected)
10. Provenance validation (provenance trail complete)
11. Invariant validation (all invariants hold)
12. Serialization validation (can be serialized deterministically)

IMPLEMENTATION NOTES:
====================

- All types are frozen dataclasses
- No mutable state exposed in public API
- No runtime primitives (threads, coroutines, schedulers, etc.)
- No subsystem references (only references to external systems)
- All collections are bounded tuples
"""

# Re-export core types from __init__.py
from .__init__ import (
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
    ExecutiveDecisionCoordinationSubjectKind,
    ExecutiveDecisionCoordinationTargetKind,
    ExecutiveDecisionCoordinationPurpose,
    ExecutiveDecisionCoordinationKind,
    ExecutiveDecisionCoordinationRequirementKind,
)

# Re-export coordination contract types
from .coordination import (
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
    ActionSelectionRequest,
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

# Re-export state types
from .state import (
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


def create_coordination_request(
    purpose: ExecutiveDecisionCoordinationPurpose,
    subject: ExecutiveDecisionCoordinationSubject,
    targets: tuple[ExecutiveDecisionCoordinationTarget, ...],
) -> ExecutiveDecisionCoordinationRequest:
    """
    Create a coordination request with required validation.
    
    This is a convenience constructor that validates the request structure
    before returning it. It does not invoke any downstream systems.
    
    Args:
        purpose: The overall purpose of this coordination
        subject: What is being coordinated (decision, revision, etc.)
        targets: Subsystems that should participate in coordination
        
    Returns:
        A validated ExecutiveDecisionCoordinationRequest
        
    Raises:
        ValueError: If validation fails
    """
    # Validate at least one target
    if not targets:
        raise ValueError("At least one target must be specified")
    
    return ExecutiveDecisionCoordinationRequest(
        purpose=purpose,
        subject=subject,
        targets=targets,
    )


def create_action_selection_request_from_decision(
    decision_identity: str,
    decision_revision_ref: int,
    decision_commitment_reference: Optional[str] = None,
) -> ActionSelectionRequest:
    """
    Create an Action Selection Request from a Decision Commitment.
    
    This is the TERMINAL Executive-owned product. It represents the canonical
    boundary where Executive decision-making yields to Action Selection
    capability.
    
    Args:
        decision_identity: The Decision Identity
        decision_revision_ref: The revision number being coordinated
        decision_commitment_reference: Reference to accepted commitment (if any)
        
    Returns:
        A validated ActionSelectionRequest
        
    Note: This does NOT select an action. It only requests that Action Selection
          consider the decision when selecting actions.
    """
    return ActionSelectionRequest(
        request_id=ActionSelectionRequestId.generate(),
        revision=1,
        schema_version="1.0.0",
        decision_identity=decision_identity,
        decision_revision_ref=decision_revision_ref,
        decision_commitment_reference=decision_commitment_reference,
        subject="EXECUTIVE_DECISION",
        purpose="ADVANCE_DECISION",
    )


def create_coordination_response(
    originating_request_ref: str,
    decision_identity: Optional[str],
    kind: Literal[
        "ACCEPTED", "ACCEPTED_WITH_CONDITIONS", "PARTIALLY_ACCEPTED",
        "PRODUCT_RETURNED", "MULTIPLE_PRODUCTS_RETURNED",
        "CONFLICT_IDENTIFIED", "MISSING_CONTEXT", "MISSING_AUTHORITY",
        "MISSING_EVIDENCE", "POLICY_REVIEW_REQUIRED", "SECURITY_REVIEW_REQUIRED",
        "STALE_REQUEST", "STALE_DECISION_REVISION", "UNSUPPORTED_REQUEST",
        "REJECTED", "DEFERRED", "EXPIRED", "FAILED"
    ] = "ACCEPTED",
    returned_products: tuple[ReturnedProduct, ...] = (),
) -> ExecutiveDecisionCoordinationResponse:
    """
    Create a coordination response from a target subsystem.
    
    This is the canonical response format for downstream systems to
    coordinate with the executive decision process.
    
    Args:
        originating_request_ref: Reference to the originating request
        decision_identity: The Decision Identity being coordinated
        kind: Response kind (acceptance, rejection, product returned, etc.)
        returned_products: Products returned by target subsystem
        
    Returns:
        A validated ExecutiveDecisionCoordinationResponse
    """
    return ExecutiveDecisionCoordinationResponse(
        response_id=ExecutiveDecisionCoordinationResponseId.generate(),
        revision=1,
        originating_request_ref=originating_request_ref,
        decision_identity=decision_identity,
        kind=kind,
        returned_products=returned_products,
    )