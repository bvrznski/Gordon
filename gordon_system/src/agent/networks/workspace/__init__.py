# Gordon Workspace Network
# =========================
#
# Canonical implementation of the Workspace Network subsystem (Phase 4.6).
#
# ARCHITECTURAL PURPOSE:
# ----------------------
# The Workspace Network coordinates bounded global cognitive availability through
# Candidate admission, evaluation, competitive arbitration, selection, activation,
# broadcast, and distribution.
#
# PRIMARY FUNCTION:
# -----------------
# Determine which currently relevant cognitive content becomes globally available
# to eligible consumer systems under what conditions and with what scope.
#
# ARCHITECTURAL BOUNDARIES:
# -------------------------
# The Workspace Network coordinates but does NOT own:
#
#   - Perception (sensory input processing)
#   - Reasoning (logical inference, deduction, induction)
#   - Memory (long-term storage and retrieval)
#   - Working Memory (active maintenance of bounded content)
#   - Planning (temporal sequencing and strategy formation)
#   - Imagination (creative generation without constraint)
#   - Motivation (goal-driven energy and direction)
#   - Decisions (Action Selection and commitment)
#   - Actions (execution and physical manifestation)
#   - Execution (runtime execution infrastructure)
#   - Persistent Domain State (durable state storage)
#
# The Workspace Network DOES own:
#
#   - Workspace Content projections
#   - Workspace Candidates (admission, evaluation, competition)
#   - Broadcast selection and activation
#   - Global broadcast semantics
#   - Target eligibility and distribution coordination
#   - State transitions through Deltas and Transitions
#   - History, Lineage, Delta, Transition, Continuation records
#
# ARCHITECTURAL INVARIANTS:
# -------------------------
# WS-INV-001: Submitted content remains owned by its source system.
# WS-INV-002: Workspace Content is a projection, not replacement for source artifact.
# WS-INV-003: Candidate admission is distinct from evaluation.
# WS-INV-004: Evaluation is distinct from competition.
# WS-INV-005: Competition is distinct from Broadcast selection.
# WS-INV-006: Selection is distinct from activation.
# WS-INV-007: Activation is distinct from runtime delivery.
# WS-INV-008: Workspace broadcast is a semantic artifact, not a transport message.
# WS-INV-009: Core owns runtime communication and scheduling.
# WS-INV-010: Working Memory remains externally owned.
# WS-INV-011: Target capabilities remain externally owned.
# WS-INV-012: Executive modulation does not automatically determine the winner.
# WS-INV-013: Policy and Security restrictions cannot be reduced to score penalties.
# WS-INV-014: Every Workspace State change occurs through a typed Delta and validated Transition.
# WS-INV-015: Semantic artifacts acquire neither current time nor random identity internally.
# WS-INV-016: Equivalent semantic inputs produce equivalent semantic outputs.
# WS-INV-017: All public semantic collections are bounded and deeply immutable.
# WS-INV-018: Replay performs no external delivery.
# WS-INV-019: Package import performs no runtime work.
#
# ARCHITECTURAL PRINCIPLES:
# -------------------------
# 1. Canonical definitions only (no duplicates)
# 2. Deeply immutable artifacts (frozen dataclasses)
# 3. External time providers (never use datetime.now, time.time internally)
# 4. External identity providers (never generate UUIDs internally)
# 5. Explicit boundedness on all collections
# 6. Typed State changes via Delta and Transition
# 7. Semantic-time preservation throughout lifecycle
# 8. Runtime-neutral contracts (no runtime dependencies in semantics)
# 9. Deterministic outputs for equivalent inputs
# 10. Import safety (no side effects at import time)

from __future__ import annotations

# =============================================================================
# CANONICAL SEMANTICS (Phase 4.6.2)
# =============================================================================

from .semantics.content import (
    WorkspaceContent,
    WorkspaceContentIdentity,
    WorkspaceContentRevision,
    WorkspaceContentReference,
    WorkspaceContentKind,
    WorkspaceContentContext,
    WorkspaceContentScope,
    WorkspaceContentValidity,
    WorkspaceContentFreshness,
    WorkspaceContentVisibility,
    WorkspaceContentProvenance,
)

from .semantics.candidate import (
    WorkspaceCandidate,
    WorkspaceCandidateIdentity,
    WorkspaceCandidateRevision,
    WorkspaceCandidateReference,
    WorkspaceAdmissionRequest,
    WorkspaceAdmissionDecision,
    WorkspaceAdmissionValidation,
    WorkspaceEligibility,
    WorkspaceCandidateState,
    WorkspaceCandidateStatus,
    WorkspaceCandidateValidity,
    WorkspaceCandidatePool,
)

# =============================================================================
# COMPETITION AND SELECTION (Phase 4.6.5)
# =============================================================================

from .competition import (
    # Identity types
    WorkspaceCompetitionIdentity,
    WorkspaceCompetitionRevision,
    WorkspaceCompetitionReference,
    
    # Competition purpose
    WorkspaceCompetitionPurpose,
    
    # Core request/context/scope
    WorkspaceCompetitionRequest,
    WorkspaceCompetitionContext,
    WorkspaceCompetitionScope,
    
    # Competition candidate
    WorkspaceCompetitionCandidate,
    
    # Frontier
    WorkspaceFrontierIdentity,
    WorkspaceFrontierRevision,
    WorkspaceFrontierSnapshot,
    WorkspaceCompetitionFrontier,
    
    # Winner
    WorkspaceWinnerIdentity,
    WorkspaceWinnerRevision,
    WorkspaceWinnerReference,
    WorkspaceWinner,
    
    # Coalition
    WorkspaceCoalitionIdentity,
    WorkspaceCoalitionRevision,
    WorkspaceCoalitionMemberRef,
    WorkspaceCoalition,
    
    # Compatibility and conflict
    WorkspaceCompatibilityKind,
    WorkspaceConflictKind,
    
    # Selection outcome
    WorkspaceSelectionOutcomeIdentity,
    WorkspaceSelectionOutcomeRevision,
    WorkspaceSelectionReason,
    WorkspaceSelectionEvidence,
    WorkspaceSelectionJustification,
    WorkspaceSelectionOutcome,
    
    # History
    CompetitionHistoryEntry,
    CompetitionHistory,
    
    # Lineage
    LineageNode,
    LineageRelation,
    CompetitionLineage,
    
    # Invalidation and continuation
    CompetitionInvalidation,
    CompetitionContinuation,
)

# =============================================================================
# BROADCAST CONSTRUCTION (Phase 4.6.6)
# =============================================================================

from .broadcast import (
    # Identity types
    WorkspaceBroadcastIdentity,
    WorkspaceBroadcastRevision,
    WorkspaceBroadcastReference,
    WorkspaceBroadcastPayloadIdentity,
    WorkspaceBroadcastPayloadReference,
    
    # Request and context
    WorkspaceBroadcastRequest,
    WorkspaceBroadcastContext,
    WorkspaceBroadcastScope,
    
    # Payload types
    WorkspaceBroadcastPayloadKind,
    WorkspaceBroadcastPayload,
    WorkspaceBroadcastProjection,
    
    # Audience, visibility, availability
    WorkspaceBroadcastAudience,
    WorkspaceBroadcastVisibility,
    WorkspaceBroadcastAvailability,
    
    # Evidence and justification
    WorkspaceBroadcastEvidence,
    WorkspaceBroadcastJustification,
    
    # Confidence and uncertainty
    WorkspaceBroadcastConfidence,
    WorkspaceBroadcastUncertainty,
    
    # History, lineage, invalidation, continuation
    WorkspaceBroadcastHistoryEntry,
    WorkspaceBroadcastHistory,
    WorkspaceLineageNode,
    WorkspaceLineageRelation,
    WorkspaceBroadcastLineage,
    WorkspaceBroadcastInvalidationKind,
    WorkspaceBroadcastInvalidation,
    WorkspaceBroadcastContinuationKind,
    WorkspaceBroadcastContinuation,
    
    # Main artifact
    WorkspaceBroadcast,
)

# =============================================================================
# BROADCAST DISTRIBUTION (Phase 4.6.7)
# =============================================================================

from .distribution import (
    # Distribution identities and references
    WorkspaceBroadcastDistributionIdentity,
    WorkspaceBroadcastDistributionRevision,
    WorkspaceBroadcastDistributionReference,
    
    # Distribution Request
    WorkspaceBroadcastDistributionPurpose,
    WorkspaceBroadcastDistributionScope,
    WorkspaceDistributionAuthorityRequirement,
    WorkspaceDistributionAuthority,
    WorkspaceBroadcastDistributionRequest,
    
    # Target semantics
    WorkspaceBroadcastTargetKind,
    WorkspaceBroadcastTargetEligibilityStatus,
    WorkspaceBroadcastTargetAvailabilityStatus,
    WorkspaceBroadcastTargetEligibility,
    WorkspaceBroadcastTargetAvailability,
    WorkspaceBroadcastTargetCapabilityProjection,
    
    # Disclosure policy
    WorkspaceDistributionDisclosureLevel,
    WorkspaceDistributionFieldRule,
    WorkspaceDistributionDisclosurePolicy,
    
    # Projections
    WorkspaceBroadcastTargetProjectionKind,
    WorkspaceBroadcastTargetProjectionIdentity,
    WorkspaceBroadcastTargetProjectionReference,
    WorkspaceBroadcastTargetProjection,
    
    # Working Memory projections
    WorkspaceWorkingMemoryProjection,
    WorkspaceWorkingMemoryAdmissionProjection,
    WorkspaceWorkingMemoryAcknowledgement,
    
    # Memory encoding projections
    WorkspaceMemoryEncodingEligibilityProjection,
    WorkspaceMemoryEncodingAcknowledgement,
    
    # Network-specific projections (Executive, Decision, etc.)
    WorkspaceExecutiveBroadcastProjection,
    WorkspaceExecutiveBroadcastAcknowledgement,
    WorkspaceDecisionBroadcastProjection,
    WorkspaceDecisionBroadcastAcknowledgement,
    WorkspaceAttentionBroadcastProjection,
    WorkspaceAttentionBroadcastAcknowledgement,
    WorkspaceAlertingBroadcastProjection,
    WorkspaceAlertingBroadcastAcknowledgement,
    WorkspaceFocusingBroadcastProjection,
    WorkspaceFocusingBroadcastAcknowledgement,
    WorkspaceDefaultNetworkBroadcastProjection,
    WorkspaceDefaultNetworkBroadcastAcknowledgement,
    WorkspaceMotivationBroadcastProjection,
    WorkspaceMotivationBroadcastAcknowledgement,
    WorkspaceReasoningBroadcastProjection,
    WorkspaceReasoningBroadcastAcknowledgement,
    WorkspacePlanningBroadcastProjection,
    WorkspacePlanningBroadcastAcknowledgement,
    WorkspacePerceptionBroadcastProjection,
    WorkspacePerceptionBroadcastAcknowledgement,
    WorkspaceLearningBroadcastProjection,
    WorkspaceLearningBroadcastAcknowledgement,
    WorkspacePredictionBroadcastProjection,
    WorkspacePredictionBroadcastAcknowledgement,
    WorkspaceWorldModelBroadcastProjection,
    WorkspaceWorldModelBroadcastAcknowledgement,
    WorkspaceMonitoringBroadcastProjection,
    WorkspaceMonitoringBroadcastAcknowledgement,
    WorkspaceRecoveryBroadcastProjection,
    WorkspaceRecoveryBroadcastAcknowledgement,
    
    # Delivery Projections
    WorkspaceDistributionRequirement,
    WorkspaceDistributionRequirementKind,
    WorkspaceDistributionConstraint,
    WorkspaceDistributionConstraintKind,
    WorkspaceBroadcastDeliveryProjectionIdentity,
    WorkspaceBroadcastDeliveryProjectionReference,
    WorkspaceBroadcastDeliveryProjection,
    
    # Acknowledgements
    WorkspaceAcknowledgementPolicy,
    WorkspaceBroadcastAcknowledgementKind,
    WorkspaceBroadcastAcknowledgementIdentity,
    WorkspaceBroadcastAcknowledgementReference,
    WorkspaceBroadcastAcknowledgement,
    
    # Rejections and deferrals
    WorkspaceBroadcastDistributionRejection,
    WorkspaceBroadcastDistributionRejectionReason,
    WorkspaceBroadcastDistributionDeferral,
    
    # Partial delivery
    WorkspaceBroadcastPartialDelivery,
    
    # Duplicate handling
    WorkspaceBroadcastDuplicateDeliveryAssessment,
    
    # Stale target handling
    WorkspaceBroadcastStaleTargetAssessment,
    WorkspaceBroadcastStaleTargetReason,
    
    # Conflicts
    WorkspaceBroadcastDeliveryConflict,
    WorkspaceBroadcastDeliveryConflictKind,
    
    # Correlation and causation
    WorkspaceDistributionCorrelationId,
    WorkspaceDistributionCorrelationReference,
    WorkspaceDistributionCorrelationContext,
    WorkspaceDistributionCausationReference,
    WorkspaceDistributionCausationRelation,
    
    # Dispositions and outcomes
    WorkspaceBroadcastDistributionDisposition,
    WorkspaceBroadcastDistributionOutcomeIdentity,
    WorkspaceBroadcastDistributionOutcomeReference,
    WorkspaceBroadcastDistributionOutcome,
    WorkspaceBroadcastDistributionCompleteness,
    WorkspaceBroadcastDistributionValidity,
    
    # Bounds
    WorkspaceDistributionFanOutBounds,
    WorkspaceDistributionFanInBounds,
    
    # Target ordering
    WorkspaceDistributionTargetOrder,
    
    # History and lineage
    WorkspaceBroadcastDistributionHistoryEntry,
    WorkspaceBroadcastDistributionHistory,
    WorkspaceBroadcastDistributionLineageRelation,
    WorkspaceBroadcastDistributionLineage,
    
    # Invalidation and continuation
    WorkspaceBroadcastDistributionInvalidation,
    WorkspaceBroadcastDistributionInvalidationReason,
    WorkspaceBroadcastDistributionContinuation,
    WorkspaceBroadcastDistributionContinuationKind,
    
    # State integration
    WorkspaceDistributionStateDeltaProposal,
    
    # Validation
    WorkspaceBroadcastDistributionValidationResult,
    
    # Privacy and provenance
    WorkspacePrivacy,
    WorkspaceDistributionProvenance,
    
    # Architectural laws
    ARCHITECTURAL_LAWS,
)

# =============================================================================
# PUBLIC API (Phase 4.6.x - Complete Workspace Semantics)
# =============================================================================

__all__ = [
    # Canonical semantics
    "WorkspaceContent",
    "WorkspaceContentIdentity",
    "WorkspaceContentRevision",
    "WorkspaceContentReference",
    "WorkspaceContentKind",
    "WorkspaceContentContext",
    "WorkspaceContentScope",
    "WorkspaceContentValidity",
    "WorkspaceContentFreshness",
    "WorkspaceContentVisibility",
    "WorkspaceContentProvenance",
    
    # Candidate semantics (for admission pipeline reference)
    "WorkspaceCandidate",
    "WorkspaceCandidateIdentity",
    "WorkspaceCandidateRevision",
    "WorkspaceCandidateReference",
    "WorkspaceAdmissionRequest",
    "WorkspaceAdmissionDecision",
    "WorkspaceAdmissionValidation",
    "WorkspaceEligibility",
    "WorkspaceCandidateState",
    "WorkspaceCandidateStatus",
    "WorkspaceCandidateValidity",
    "WorkspaceCandidatePool",
    
    # Competition and Selection (Phase 4.6.5)
    "WorkspaceCompetitionIdentity",
    "WorkspaceCompetitionRevision",
    "WorkspaceCompetitionReference",
    "WorkspaceCompetitionPurpose",
    "WorkspaceCompetitionRequest",
    "WorkspaceCompetitionContext",
    "WorkspaceCompetitionScope",
    "WorkspaceCompetitionCandidate",
    "WorkspaceFrontierIdentity",
    "WorkspaceFrontierRevision",
    "WorkspaceFrontierSnapshot",
    "WorkspaceCompetitionFrontier",
    "WorkspaceWinnerIdentity",
    "WorkspaceWinnerRevision",
    "WorkspaceWinnerReference",
    "WorkspaceWinner",
    "WorkspaceCoalitionIdentity",
    "WorkspaceCoalitionRevision",
    "WorkspaceCoalitionMemberRef",
    "WorkspaceCoalition",
    "WorkspaceCompatibilityKind",
    "WorkspaceConflictKind",
    "WorkspaceSelectionOutcomeIdentity",
    "WorkspaceSelectionOutcomeRevision",
    "WorkspaceSelectionReason",
    "WorkspaceSelectionEvidence",
    "WorkspaceSelectionJustification",
    "WorkspaceSelectionOutcome",
    "CompetitionHistoryEntry",
    "CompetitionHistory",
    "LineageNode",
    "LineageRelation",
    "CompetitionLineage",
    "CompetitionInvalidation",
    "CompetitionContinuation",
    
    # Broadcast Construction (Phase 4.6.6)
    "WorkspaceBroadcastIdentity",
    "WorkspaceBroadcastRevision",
    "WorkspaceBroadcastReference",
    "WorkspaceBroadcastPayloadIdentity",
    "WorkspaceBroadcastPayloadReference",
    "WorkspaceBroadcastRequest",
    "WorkspaceBroadcastContext",
    "WorkspaceBroadcastScope",
    "WorkspaceBroadcastPayloadKind",
    "WorkspaceBroadcastPayload",
    "WorkspaceBroadcastProjection",
    "WorkspaceBroadcastAudience",
    "WorkspaceBroadcastVisibility",
    "WorkspaceBroadcastAvailability",
    "WorkspaceBroadcastEvidence",
    "WorkspaceBroadcastJustification",
    "WorkspaceBroadcastConfidence",
    "WorkspaceBroadcastUncertainty",
    "WorkspaceBroadcastHistoryEntry",
    "WorkspaceBroadcastHistory",
    "WorkspaceLineageNode",
    "WorkspaceLineageRelation",
    "WorkspaceBroadcastLineage",
    "WorkspaceBroadcastInvalidationKind",
    "WorkspaceBroadcastInvalidation",
    "WorkspaceBroadcastContinuationKind",
    "WorkspaceBroadcastContinuation",
    "WorkspaceBroadcast",
    
    # Distribution identities and references (Phase 4.6.7)
    "WorkspaceBroadcastDistributionIdentity",
    "WorkspaceBroadcastDistributionRevision",
    "WorkspaceBroadcastDistributionReference",
    
    # Distribution Request
    "WorkspaceBroadcastDistributionPurpose",
    "WorkspaceBroadcastDistributionScope",
    "WorkspaceDistributionAuthorityRequirement",
    "WorkspaceDistributionAuthority",
    "WorkspaceBroadcastDistributionRequest",
    
    # Target semantics
    "WorkspaceBroadcastTargetKind",
    "WorkspaceBroadcastTargetEligibilityStatus",
    "WorkspaceBroadcastTargetAvailabilityStatus",
    "WorkspaceBroadcastTargetEligibility",
    "WorkspaceBroadcastTargetAvailability",
    "WorkspaceBroadcastTargetCapabilityProjection",
    
    # Disclosure policy
    "WorkspaceDistributionDisclosureLevel",
    "WorkspaceDistributionFieldRule",
    "WorkspaceDistributionDisclosurePolicy",
    
    # Projections
    "WorkspaceBroadcastTargetProjectionKind",
    "WorkspaceBroadcastTargetProjectionIdentity",
    "WorkspaceBroadcastTargetProjectionReference",
    "WorkspaceBroadcastTargetProjection",
    
    # Working Memory projections
    "WorkspaceWorkingMemoryProjection",
    "WorkspaceWorkingMemoryAdmissionProjection",
    "WorkspaceWorkingMemoryAcknowledgement",
    
    # Memory encoding projections
    "WorkspaceMemoryEncodingEligibilityProjection",
    "WorkspaceMemoryEncodingAcknowledgement",
    
    # Network-specific projections (Executive, Decision, etc.)
    "WorkspaceExecutiveBroadcastProjection",
    "WorkspaceExecutiveBroadcastAcknowledgement",
    "WorkspaceDecisionBroadcastProjection",
    "WorkspaceDecisionBroadcastAcknowledgement",
    "WorkspaceAttentionBroadcastProjection",
    "WorkspaceAttentionBroadcastAcknowledgement",
    "WorkspaceAlertingBroadcastProjection",
    "WorkspaceAlertingBroadcastAcknowledgement",
    "WorkspaceFocusingBroadcastProjection",
    "WorkspaceFocusingBroadcastAcknowledgement",
    "WorkspaceDefaultNetworkBroadcastProjection",
    "WorkspaceDefaultNetworkBroadcastAcknowledgement",
    "WorkspaceMotivationBroadcastProjection",
    "WorkspaceMotivationBroadcastAcknowledgement",
    "WorkspaceReasoningBroadcastProjection",
    "WorkspaceReasoningBroadcastAcknowledgement",
    "WorkspacePlanningBroadcastProjection",
    "WorkspacePlanningBroadcastAcknowledgement",
    "WorkspacePerceptionBroadcastProjection",
    "WorkspacePerceptionBroadcastAcknowledgement",
    "WorkspaceLearningBroadcastProjection",
    "WorkspaceLearningBroadcastAcknowledgement",
    "WorkspacePredictionBroadcastProjection",
    "WorkspacePredictionBroadcastAcknowledgement",
    "WorkspaceWorldModelBroadcastProjection",
    "WorkspaceWorldModelBroadcastAcknowledgement",
    "WorkspaceMonitoringBroadcastProjection",
    "WorkspaceMonitoringBroadcastAcknowledgement",
    "WorkspaceRecoveryBroadcastProjection",
    "WorkspaceRecoveryBroadcastAcknowledgement",
    
    # Delivery Projections
    "WorkspaceDistributionRequirement",
    "WorkspaceDistributionRequirementKind",
    "WorkspaceDistributionConstraint",
    "WorkspaceDistributionConstraintKind",
    "WorkspaceBroadcastDeliveryProjectionIdentity",
    "WorkspaceBroadcastDeliveryProjectionReference",
    "WorkspaceBroadcastDeliveryProjection",
    
    # Acknowledgements
    "WorkspaceAcknowledgementPolicy",
    "WorkspaceBroadcastAcknowledgementKind",
    "WorkspaceBroadcastAcknowledgementIdentity",
    "WorkspaceBroadcastAcknowledgementReference",
    "WorkspaceBroadcastAcknowledgement",
    
    # Rejections and deferrals
    "WorkspaceBroadcastDistributionRejection",
    "WorkspaceBroadcastDistributionRejectionReason",
    "WorkspaceBroadcastDistributionDeferral",
    
    # Partial delivery
    "WorkspaceBroadcastPartialDelivery",
    
    # Duplicate handling
    "WorkspaceBroadcastDuplicateDeliveryAssessment",
    
    # Stale target handling
    "WorkspaceBroadcastStaleTargetAssessment",
    "WorkspaceBroadcastStaleTargetReason",
    
    # Conflicts
    "WorkspaceBroadcastDeliveryConflict",
    "WorkspaceBroadcastDeliveryConflictKind",
    
    # Correlation and causation
    "WorkspaceDistributionCorrelationId",
    "WorkspaceDistributionCorrelationReference",
    "WorkspaceDistributionCorrelationContext",
    "WorkspaceDistributionCausationReference",
    "WorkspaceDistributionCausationRelation",
    
    # Dispositions and outcomes
    "WorkspaceBroadcastDistributionDisposition",
    "WorkspaceBroadcastDistributionOutcomeIdentity",
    "WorkspaceBroadcastDistributionOutcomeReference",
    "WorkspaceBroadcastDistributionOutcome",
    "WorkspaceBroadcastDistributionCompleteness",
    "WorkspaceBroadcastDistributionValidity",
    
    # Bounds
    "WorkspaceDistributionFanOutBounds",
    "WorkspaceDistributionFanInBounds",
    
    # Target ordering
    "WorkspaceDistributionTargetOrder",
    
    # History and lineage
    "WorkspaceBroadcastDistributionHistoryEntry",
    "WorkspaceBroadcastDistributionHistory",
    "WorkspaceBroadcastDistributionLineageRelation",
    "WorkspaceBroadcastDistributionLineage",
    
    # Invalidation and continuation
    "WorkspaceBroadcastDistributionInvalidation",
    "WorkspaceBroadcastDistributionInvalidationReason",
    "WorkspaceBroadcastDistributionContinuation",
    "WorkspaceBroadcastDistributionContinuationKind",
    
    # State integration
    "WorkspaceDistributionStateDeltaProposal",
    
    # Validation
    "WorkspaceBroadcastDistributionValidationResult",
    
    # Privacy and provenance
    "WorkspacePrivacy",
    "WorkspaceDistributionProvenance",
    
    # Architectural laws
    "ARCHITECTURAL_LAWS",
]
