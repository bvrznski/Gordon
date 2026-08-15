# Default Network - Workspace Integration Package
# ================================================

"""
Workspace Integration layer for the Default Network.

This package implements runtime-neutral coordination of workspace candidates -
semantic proposals that may deserve evaluation for admission to a shared
cognitive workspace.

ARCHITECTURAL PRINCIPLES:
    1. Workspace Integration is distinct from workspace ownership
    2. All contracts are deeply immutable
    3. No runtime references in domain models
    4. All bounds are explicit and bounded
    5. State transitions are semantic records, not runtime actions

ARCHITECTURAL BOUNDARIES:
    • Does NOT own or mutate shared workspace state
    • Does NOT perform direct broadcast
    • Does NOT invoke Executive, Alerting, or Focusing
    • Does NOT schedule execution or allocate resources
    • Does NOT own runtime progression (ExecutionLoop does that)

ARCHITECTURAL INVARIANTS:
    DEFAULT-WS-INV-001: The Default Network does not own the shared workspace
    DEFAULT-WS-INV-002: Every Workspace Integration belongs to exactly one InternalEpisode
    DEFAULT-WS-INV-003: Every Workspace Integration has explicit purpose, subject, scope
    DEFAULT-WS-INV-004: Every Workspace Integration binds to one InternalContext revision
    DEFAULT-WS-INV-005: Every candidate preserves source ownership, factuality, provenance
    DEFAULT-WS-INV-006: A workspace candidate is distinct from admitted workspace content
    DEFAULT-WS-INV-007: Admission is distinct from broadcast
    DEFAULT-WS-INV-008: Broadcast is distinct from consumption
"""

from __future__ import annotations

# =============================================================================
# CORE MODELS
# =============================================================================

from .request import (
    WorkspaceIntegrationRequest,
    WorkspaceIntegrationRequestId,
)

from .purpose import (
    WorkspaceIntegrationPurpose,
    WorkspaceIntegrationPurposeKind,
)

from .subject import (
    WorkspaceIntegrationSubject,
    WorkspaceIntegrationSubjectKind,
)

from .scope import (
    WorkspaceIntegrationScope,
)

# =============================================================================
# SOURCE PRODUCT REFERENCE
# =============================================================================

from .source_product import (
    WorkspaceSourceProductReference,
    WorkspaceSourceProductKind,
)

# =============================================================================
# CANDIDATE MODELS
# =============================================================================

from .candidate import (
    WorkspaceCandidate,
    WorkspaceCandidateId,
    WorkspaceCandidateRevision,
)

from .content import (
    WorkspaceCandidateContent,
)

from .origin import (
    WorkspaceCandidateOrigin,
)

# =============================================================================
# CANDIDATE KINDS AND PURPOSES
# =============================================================================

from .enums import (
    WorkspaceCandidateKind,
    WorkspaceCandidatePurpose,
)

# =============================================================================
# ASSESSMENT MODELS
# =============================================================================

from .value import (
    WorkspaceCandidateValue,
)

from .relevance import (
    WorkspaceCandidateRelevance,
)

from .urgency import (
    WorkspaceCandidateUrgency,
)

from .importance import (
    WorkspaceCandidateImportance,
)

from .novelty import (
    WorkspaceCandidateNovelty,
)

from .confidence import (
    WorkspaceCandidateConfidence,
)

from .risk import (
    WorkspaceCandidateRisk,
)

# =============================================================================
# AUDIENCE, ACCESS, DISCLOSURE, LIFETIME
# =============================================================================

from .audience import (
    WorkspaceAudienceRecommendation,
)

from .access import (
    WorkspaceAccessClassification,
)

from .disclosure import (
    WorkspaceDisclosureClassification,
)

from .lifetime import (
    WorkspaceCandidateLifetime,
    WorkspacePersistenceRecommendation,
)

# =============================================================================
# DUPLICATE AND CONFLICT MODELS
# =============================================================================

from .duplicate import (
    WorkspaceCandidateDuplicateAssessment,
    DuplicateAssessmentKind,
)

from .conflict import (
    WorkspaceCandidateConflict,
    ConflictKind,
)

# =============================================================================
# COMPETITION AND CAPACITY
# =============================================================================

from .competition import (
    WorkspaceCompetitionProjection,
)

from .capacity import (
    WorkspaceCapacityCost,
)

# =============================================================================
# SUBMISSION, REVISION, WITHDRAWAL PROPOSALS
# =============================================================================

from .submission import (
    WorkspaceSubmissionProposal,
)

from .revision import (
    WorkspaceCandidateRevisionProposal,
    WorkspaceCandidateRevisionRequest,
)

from .withdrawal import (
    WorkspaceCandidateWithdrawalProposal,
)

# =============================================================================
# ADMISSION CONTRACTS
# =============================================================================

from .admission.decision import (
    WorkspaceAdmissionDecision,
    WorkspaceAdmissionDecisionKind,
)

from .admission.acceptance import (
    WorkspaceAdmissionAcceptance,
)

from .admission.rejection import (
    WorkspaceAdmissionRejection,
    RejectionReason,
)

from .admission.deferral import (
    WorkspaceAdmissionDeferral,
    DeferralReason,
)

from .admission.reason import (
    AdmissionReason,
)

# =============================================================================
# FEEDBACK CONTRACTS
# =============================================================================

from .feedback.broadcast import (
    WorkspaceBroadcastResult,
)

from .feedback.consumption import (
    WorkspaceConsumptionFeedback,
)

from .feedback.expiration import (
    WorkspaceExpirationFeedback,
)

from .feedback.eviction import (
    WorkspaceEvictionFeedback,
)

from .feedback.projection import (
    WorkspaceFeedbackProjection,
)

# =============================================================================
# PERFORMANCE ASSESSMENT
# =============================================================================

from .performance import (
    WorkspaceCandidatePerformanceAssessment,
)

# =============================================================================
# EPISODE, PLAN, OUTCOME, CONTINUATION
# =============================================================================

from .episode import (
    WorkspaceIntegrationEpisode,
)

from .plan import (
    WorkspaceIntegrationPlan,
    WorkspaceCoordinationStepKind,
    WorkspacePlanStep,
)

from .product import (
    WorkspaceIntegrationProduct,
    WorkspaceIntegrationProductKind,
)

from .outcome import (
    WorkspaceIntegrationOutcome,
    WorkspaceIntegrationOutcomeKind,
)

from .continuation import (
    WorkspaceIntegrationContinuation,
)

# =============================================================================
# STATE AND HISTORY
# =============================================================================

from .state.model import (
    WorkspaceIntegrationState,
)

from .state.snapshot import (
    WorkspaceIntegrationSnapshot,
)

from .state.transition import (
    WorkspaceIntegrationTransitionRecord,
)

from .state.history import (
    WorkspaceIntegrationHistory,
)

# =============================================================================
# CONFIGURATION
# =============================================================================

from .configuration import (
    WorkspaceIntegrationConfig,
)

# =============================================================================
# VALIDATION
# =============================================================================

from .validation.request import (
    validate_workspace_request,
)

from .validation.scope import (
    validate_scope_bounds,
)

from .validation.candidate import (
    validate_candidate_structure,
)

from .validation.admission import (
    validate_admission_decision,
)

from .validation.architecture import (
    verify_architectural_boundaries,
)

# =============================================================================
# EXCEPTIONS
# =============================================================================

from .exceptions import (
    WorkspaceIntegrationError,
    InvalidWorkspaceRequest,
    InvalidWorkspacePurpose,
    InvalidWorkspaceSubject,
    InvalidWorkspaceScope,
    InvalidWorkspaceCandidate,
    InvalidWorkspaceContent,
    InvalidWorkspaceOrigin,
    InvalidWorkspaceAssessment,
    InvalidWorkspaceAudience,
    InvalidWorkspaceAccessClassification,
    InvalidWorkspaceDisclosureClassification,
    InvalidWorkspaceLifetime,
    WorkspaceRecurrenceLimitExceeded,
    WorkspaceCapacityExceeded,
    WorkspaceInvariantViolation,
)

# =============================================================================
# CONTRACTS
# =============================================================================

from .contracts.workspace import (
    WorkspaceAdmissionContract,
    WorkspaceFeedbackContract,
)

from .contracts.admission import (
    AdmissionAuthorityContract,
)

from .contracts.feedback import (
    FeedbackContract,
)

from .contracts.consumer import (
    ConsumerProjectionContract,
)

from .contracts.attention import (
    AttentionAssessmentContract,
)

from .contracts.executive import (
    ExecutiveReviewContract,
)

from .contracts.provider import (
    ContextProviderContract,
)

from .contracts.validation import (
    ValidationContract,
)

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Core models
    "WorkspaceIntegrationRequest",
    "WorkspaceIntegrationRequestId",
    "WorkspaceIntegrationPurpose",
    "WorkspaceIntegrationSubject",
    "WorkspaceIntegrationScope",
    
    # Source product reference
    "WorkspaceSourceProductReference",
    "WorkspaceSourceProductKind",
    
    # Candidate models
    "WorkspaceCandidate",
    "WorkspaceCandidateId",
    "WorkspaceCandidateRevision",
    "WorkspaceCandidateContent",
    "WorkspaceCandidateOrigin",
    
    # Enums
    "WorkspaceCandidateKind",
    "WorkspaceCandidatePurpose",
    "WorkspaceIntegrationPurposeKind",
    "WorkspaceIntegrationSubjectKind",
    
    # Assessment models
    "WorkspaceCandidateValue",
    "WorkspaceCandidateRelevance",
    "WorkspaceCandidateUrgency",
    "WorkspaceCandidateImportance",
    "WorkspaceCandidateNovelty",
    "WorkspaceCandidateConfidence",
    "WorkspaceCandidateRisk",
    
    # Audience, Access, Disclosure, Lifetime
    "WorkspaceAudienceRecommendation",
    "WorkspaceAccessClassification",
    "WorkspaceDisclosureClassification",
    "WorkspaceCandidateLifetime",
    "WorkspacePersistenceRecommendation",
    
    # Duplicate and conflict
    "WorkspaceCandidateDuplicateAssessment",
    "DuplicateAssessmentKind",
    "WorkspaceCandidateConflict",
    "ConflictKind",
    
    # Competition and capacity
    "WorkspaceCompetitionProjection",
    "WorkspaceCapacityCost",
    
    # Proposals
    "WorkspaceSubmissionProposal",
    "WorkspaceCandidateRevisionProposal",
    "WorkspaceCandidateRevisionRequest",
    "WorkspaceCandidateWithdrawalProposal",
    
    # Admission contracts
    "WorkspaceAdmissionDecision",
    "WorkspaceAdmissionDecisionKind",
    "WorkspaceAdmissionAcceptance",
    "WorkspaceAdmissionRejection",
    "RejectionReason",
    "WorkspaceAdmissionDeferral",
    "DeferralReason",
    "AdmissionReason",
    
    # Feedback contracts
    "WorkspaceBroadcastResult",
    "WorkspaceConsumptionFeedback",
    "WorkspaceExpirationFeedback",
    "WorkspaceEvictionFeedback",
    "WorkspaceFeedbackProjection",
    
    # Performance assessment
    "WorkspaceCandidatePerformanceAssessment",
    
    # Episode, Plan, Outcome, Continuation
    "WorkspaceIntegrationEpisode",
    "WorkspaceIntegrationPlan",
    "WorkspaceCoordinationStepKind",
    "WorkspacePlanStep",
    "WorkspaceIntegrationProduct",
    "WorkspaceIntegrationProductKind",
    "WorkspaceIntegrationOutcome",
    "WorkspaceIntegrationOutcomeKind",
    "WorkspaceIntegrationContinuation",
    
    # State and history
    "WorkspaceIntegrationState",
    "WorkspaceIntegrationSnapshot",
    "WorkspaceIntegrationTransitionRecord",
    "WorkspaceIntegrationHistory",
    
    # Configuration
    "WorkspaceIntegrationConfig",
    
    # Validation
    "validate_workspace_request",
    "validate_scope_bounds",
    "validate_candidate_structure",
    "validate_admission_decision",
    "verify_architectural_boundaries",
    
    # Exceptions
    "WorkspaceIntegrationError",
    "InvalidWorkspaceRequest",
    "InvalidWorkspacePurpose",
    "InvalidWorkspaceSubject",
    "InvalidWorkspaceScope",
    "InvalidWorkspaceCandidate",
    "InvalidWorkspaceContent",
    "InvalidWorkspaceOrigin",
    "InvalidWorkspaceAssessment",
    "InvalidWorkspaceAudience",
    "InvalidWorkspaceAccessClassification",
    "InvalidWorkspaceDisclosureClassification",
    "InvalidWorkspaceLifetime",
    "WorkspaceRecurrenceLimitExceeded",
    "WorkspaceCapacityExceeded",
    "WorkspaceInvariantViolation",
    
    # Contracts
    "WorkspaceAdmissionContract",
    "WorkspaceFeedbackContract",
    "AdmissionAuthorityContract",
    "FeedbackContract",
    "ConsumerProjectionContract",
    "AttentionAssessmentContract",
    "ExecutiveReviewContract",
    "ContextProviderContract",
    "ValidationContract",
]