# Workspace Admission Decision Models
# ====================================

"""
Admission decision models for workspace candidates.

ARCHITECTURAL PRINCIPLES:
    - All dataclasses are frozen (deeply immutable)
    - No runtime dependencies
    - Bounded by explicit limits
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# WORKSPACE ADMISSION DECISION KINDS
# =============================================================================

from ..enums import WorkspaceAdmissionDecisionKind as DecisionKind


# =============================================================================
# WORKSPACE ADMISSION DECISION
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceAdmissionDecision:
    """
    Immutable admission decision from external workspace authority.
    
    The decision comes from external authority. The Default Network must never
    fabricate acceptance.
    
    PROPERTIES:
        • decision_id: Unique identifier for this decision
        • proposal_id: ID of the proposal being decided on
        • candidate_id: ID of the candidate being evaluated
        • candidate_revision: Revision being evaluated
        • kind: Decision kind (accept, reject, defer, etc.)
        • accepted_audience: Accepted audience recommendations
        • accepted_access: Accepted access classification
        • accepted_lifetime: Accepted lifetime classification
        • constraints: Any constraints on the accepted content
        • reasons: Human-readable explanation
        • decided_at_utc: When decision was made (ISO format string)
        • authority: External authority that made the decision
    """
    
    decision_id: str
    """Unique identifier for this decision."""
    
    proposal_id: str
    """ID of the proposal being decided on."""
    
    candidate_id: str
    """ID of the candidate being evaluated."""
    
    candidate_revision: int = 1
    """Revision being evaluated."""
    
    kind: str  # DecisionKind.*
    """Decision kind (accept, reject, defer, etc.)."""
    
    accepted_audience_recommendation: Tuple[str, ...] = field(default_factory=tuple)
    """Accepted audience recommendations (if accepted)."""
    
    accepted_access_classification: Optional[str] = None
    """Accepted access classification (if accepted)."""
    
    accepted_disclosure_classification: Optional[str] = None
    """Accepted disclosure classification (if accepted)."""
    
    accepted_lifetime: Optional[str] = None
    """Accepted lifetime classification (if accepted)."""
    
    constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Constraints on the accepted content."""
    
    reasons: Tuple[str, ...] = field(default_factory=tuple)
    """Human-readable explanation(s)."""
    
    decided_at_utc: str = ""
    """When decision was made (ISO format string)."""
    
    authority: str = "external_workspace"
    """External authority that made the decision."""
    
    provenance: str = "canonical"
    """Provenance reference."""
    
    @classmethod
    def accept(
        cls,
        proposal_id: str,
        candidate_id: str,
        revision: int = 1,
        audience_recommendations: Tuple[str, ...] = (),
        constraints: Tuple[str, ...] = (),
        reason: str = "",
    ) -> WorkspaceAdmissionDecision:
        """
        Create an acceptance decision.
        
        Args:
            proposal_id: ID of the accepted proposal
            candidate_id: ID of the accepted candidate
            revision: Revision being accepted
            audience_recommendations: Accepted audience recommendations
            constraints: Any constraints on the content
            reason: Explanation for acceptance
            
        Returns:
            New WorkspaceAdmissionDecision instance (kind=ACCEPT)
        """
        return cls(
            decision_id=f"admission_decision_{proposal_id}",
            proposal_id=proposal_id,
            candidate_id=candidate_id,
            candidate_revision=revision,
            kind="accept",
            accepted_audience_recommendation=audience_recommendations,
            constraints=constraints,
            reasons=(reason or "Candidate meets workspace criteria",),
        )
    
    @classmethod
    def reject(
        cls,
        proposal_id: str,
        candidate_id: str,
        revision: int = 1,
        reason: str = "",
    ) -> WorkspaceAdmissionDecision:
        """
        Create a rejection decision.
        
        Args:
            proposal_id: ID of the rejected proposal
            candidate_id: ID of the rejected candidate
            revision: Revision being evaluated
            reason: Explanation for rejection
            
        Returns:
            New WorkspaceAdmissionDecision instance (kind=REJECT)
        """
        return cls(
            decision_id=f"admission_decision_{proposal_id}",
            proposal_id=proposal_id,
            candidate_id=candidate_id,
            candidate_revision=revision,
            kind="reject",
            reasons=(reason or "Candidate does not meet workspace criteria",),
        )
    
    @classmethod
    def defer(
        cls,
        proposal_id: str,
        candidate_id: str,
        revision: int = 1,
        reason: str = "",
    ) -> WorkspaceAdmissionDecision:
        """
        Create a deferral decision.
        
        Args:
            proposal_id: ID of the deferred proposal
            candidate_id: ID of the deferred candidate
            revision: Revision being evaluated
            reason: Explanation for deferral
            
        Returns:
            New WorkspaceAdmissionDecision instance (kind=DEFER)
        """
        return cls(
            decision_id=f"admission_decision_{proposal_id}",
            proposal_id=proposal_id,
            candidate_id=candidate_id,
            candidate_revision=revision,
            kind="defer",
            reasons=(reason or "Workspace capacity unavailable at this time",),
        )
    
    @classmethod
    def request_revision(
        cls,
        proposal_id: str,
        candidate_id: str,
        revision: int = 1,
        requested_changes: Tuple[str, ...] = (),
        reason: str = "",
    ) -> WorkspaceAdmissionDecision:
        """
        Create a revision request decision.
        
        Args:
            proposal_id: ID of the proposal needing revision
            candidate_id: ID of the candidate needing revision
            revision: Current revision
            requested_changes: Description of requested changes
            reason: Explanation for revision request
            
        Returns:
            New WorkspaceAdmissionDecision instance (kind=REQUEST_REVISION)
        """
        return cls(
            decision_id=f"admission_decision_{proposal_id}",
            proposal_id=proposal_id,
            candidate_id=candidate_id,
            candidate_revision=revision,
            kind="request_revision",
            reasons=(reason or "Revision required before admission",),
            constraints=requested_changes,
        )


# =============================================================================
# WORKSPACE ADMISSION ACCEPTANCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceAdmissionAcceptance:
    """
    Immutable acceptance record from external workspace authority.
    
    Acceptance distinguishes:
        - candidate admitted (workspace availability)
        - candidate broadcast (delivery to consumers)
        - candidate consumed (downstream processing)
    
    PROPERTIES:
        • acceptance_id: Unique identifier for this acceptance
        • candidate_id: ID of the accepted candidate
        • candidate_revision: Revision being accepted
        • workspace_item_id: Workspace item ID (if applicable)
        • active_lifetime: Active lifetime in workspace
        • access_scope: Accepted access scope
        • audience_scope: Accepted audience scope
        • workspace_revision: Workspace state revision
        • limitations: Any limitations on the accepted content
    """
    
    acceptance_id: str
    """Unique identifier for this acceptance."""
    
    candidate_id: str
    """ID of the accepted candidate."""
    
    candidate_revision: int = 1
    """Revision being accepted."""
    
    workspace_item_id: Optional[str] = None
    """Workspace item ID (if applicable)."""
    
    active_lifetime: str = "transient"
    """Active lifetime in workspace."""
    
    access_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Accepted access scope."""
    
    audience_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Accepted audience scope."""
    
    workspace_revision: int = 1
    """Workspace state revision after acceptance."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Limitations on the accepted content."""
    
    admitted_at_utc: str = ""
    """When candidate was admitted (ISO format string)."""
    
    authority: str = "external_workspace"
    """Authority that made the admission decision."""
    
    @classmethod
    def admit(
        cls,
        candidate_id: str,
        revision: int = 1,
        workspace_item_id: Optional[str] = None,
        lifetime: str = "transient",
    ) -> WorkspaceAdmissionAcceptance:
        """
        Create an acceptance record for a candidate.
        
        Args:
            candidate_id: ID of the accepted candidate
            revision: Revision being accepted
            workspace_item_id: Workspace item ID (if assigned)
            lifetime: Active lifetime classification
            
        Returns:
            New WorkspaceAdmissionAcceptance instance
        """
        return cls(
            acceptance_id=f"acceptance_{candidate_id}",
            candidate_id=candidate_id,
            candidate_revision=revision,
            workspace_item_id=workspace_item_id,
            active_lifetime=lifetime,
            admitted_at_utc="",
        )


# =============================================================================
# WORKSPACE ADMISSION REJECTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceAdmissionRejection:
    """
    Immutable rejection record from external workspace authority.
    
    Rejection does not mutate or invalidate the source product automatically.
    
    PROPERTIES:
        • rejection_id: Unique identifier for this rejection
        • candidate_id: ID of the rejected candidate
        • candidate_revision: Revision being rejected
        • reason: Rejection reason (from RejectionReason.*)
        • workspace_item_id: Workspace item ID if already admitted
        • workspace_revision: Workspace state revision
    """
    
    rejection_id: str
    """Unique identifier for this rejection."""
    
    candidate_id: str
    """ID of the rejected candidate."""
    
    candidate_revision: int = 1
    """Revision being rejected."""
    
    reason: str
    """Rejection reason (from RejectionReason.*)."""
    
    workspace_item_id: Optional[str] = None
    """Workspace item ID if already admitted."""
    
    workspace_revision: int = 1
    """Workspace state revision after rejection."""
    
    rejected_at_utc: str = ""
    """When rejection occurred (ISO format string)."""
    
    authority: str = "external_workspace"
    """Authority that made the rejection decision."""
    
    @classmethod
    def insufficient_value(
        cls,
        candidate_id: str,
        revision: int = 1,
    ) -> WorkspaceAdmissionRejection:
        """
        Create a rejection for insufficient value.
        
        Args:
            candidate_id: ID of the rejected candidate
            revision: Revision being rejected
            
        Returns:
            New WorkspaceAdmissionRejection instance (reason=INSUFFICIENT_VALUE)
        """
        return cls(
            rejection_id=f"rejection_{candidate_id}",
            candidate_id=candidate_id,
            candidate_revision=revision,
            reason="insufficient_value",
            workspace_revision=1,
            rejected_at_utc="",
        )
    
    @classmethod
    def duplicate(
        cls,
        candidate_id: str,
        revision: int = 1,
        existing_item_id: Optional[str] = None,
    ) -> WorkspaceAdmissionRejection:
        """
        Create a rejection for duplicate content.
        
        Args:
            candidate_id: ID of the rejected candidate
            revision: Revision being rejected
            existing_item_id: Existing workspace item if duplicate
            
        Returns:
            New WorkspaceAdmissionRejection instance (reason=DUPLICATE)
        """
        return cls(
            rejection_id=f"rejection_{candidate_id}",
            candidate_id=candidate_id,
            candidate_revision=revision,
            reason="duplicate",
            workspace_item_id=existing_item_id,
            workspace_revision=1,
            rejected_at_utc="",
        )


# =============================================================================
# WORKSPACE ADMISSION DEFERRAL
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceAdmissionDeferral:
    """
    Immutable deferral record from external workspace authority.
    
    Deferral does not create polling. External system supplies reevaluation events.
    
    PROPERTIES:
        • deferral_id: Unique identifier for this deferral
        • candidate_id: ID of the deferred candidate
        • candidate_revision: Revision being deferred
        • reason: Deferral reason (from DeferralReason.*)
        • reevaluated_at_utc: When reevaluation will occur (optional)
        • workspace_item_id: Workspace item ID if already admitted
    """
    
    deferral_id: str
    """Unique identifier for this deferral."""
    
    candidate_id: str
    """ID of the deferred candidate."""
    
    candidate_revision: int = 1
    """Revision being deferred."""
    
    reason: str
    """Deferral reason (from DeferralReason.*)."""
    
    reevaluated_at_utc: Optional[str] = None
    """When reevaluation will occur (ISO format string, if known)."""
    
    workspace_item_id: Optional[str] = None
    """Workspace item ID if already admitted."""
    
    deferred_at_utc: str = ""
    """When deferral occurred (ISO format string)."""
    
    authority: str = "external_workspace"
    """Authority that made the deferral decision."""
    
    @classmethod
    def capacity_deferral(
        cls,
        candidate_id: str,
        revision: int = 1,
    ) -> WorkspaceAdmissionDeferral:
        """
        Create a deferral for capacity unavailable.
        
        Args:
            candidate_id: ID of the deferred candidate
            revision: Revision being deferred
            
        Returns:
            New WorkspaceAdmissionDeferral instance (reason=CAPACITY_UNAVAILABLE)
        """
        return cls(
            deferral_id=f"deferral_{candidate_id}",
            candidate_id=candidate_id,
            candidate_revision=revision,
            reason="capacity_unavailable",
            deferred_at_utc="",
        )
    
    @classmethod
    def waiting_for_evidence(
        cls,
        candidate_id: str,
        revision: int = 1,
    ) -> WorkspaceAdmissionDeferral:
        """
        Create a deferral for waiting on evidence.
        
        Args:
            candidate_id: ID of the deferred candidate
            revision: Revision being deferred
            
        Returns:
            New WorkspaceAdmissionDeferral instance (reason=WAITING_FOR_EVIDENCE)
        """
        return cls(
            deferral_id=f"deferral_{candidate_id}",
            candidate_id=candidate_id,
            candidate_revision=revision,
            reason="waiting_for_evidence",
            reevaluated_at_utc=None,
            deferred_at_utc="",
        )


# =============================================================================
# ADMISSION REASONS
# =============================================================================

class RejectionReason:
    """Rejection reason kinds."""
    
    INSUFFICIENT_VALUE = "insufficient_value"
    INSUFFICIENT_RELEVANCE = "insufficient_relevance"
    INSUFFICIENT_CONFIDENCE = "insufficient_confidence"
    DUPLICATE = "duplicate"
    CONFLICT = "conflict"
    CAPACITY = "capacity"
    STALE = "stale"
    INVALID = "invalid"
    UNSUPPORTED_KIND = "unsupported_kind"
    POLICY = "policy"
    PRIVACY = "privacy"
    SECURITY = "security"
    DISCLOSURE = "disclosure"
    AUDIENCE_MISMATCH = "audience_mismatch"
    MISSING_EVIDENCE = "missing_evidence"
    MISSING_PROVENANCE = "missing_provenance"
    UNKNOWN = "unknown"


class DeferralReason:
    """Deferral reason kinds."""
    
    CAPACITY_UNAVAILABLE = "capacity_unavailable"
    RELEVANT_CONTENT_ACTIVE = "relevant_content_active"
    WAITING_FOR_EVIDENCE = "waiting_for_evidence"
    WAITING_FOR_REVISION = "waiting_for_revision"
    WAITING_FOR_AUTHORITY = "waiting_for_authority"
    NOT_YET_TIMELY = "not_yet_timely"
    AUDIENCE_UNAVAILABLE = "audience_unavailable"
    UNKNOWN = "unknown"


class AdmissionReason:
    """Admission decision reasons."""
    
    MEETS_CRITERIA = "meets_criteria"
    HIGH_VALUE = "high_value"
    RELEVANT_TO_ACTIVE_WORK = "relevant_to_active_work"
    RESOLVES_CONFLICT = "resolves_conflict"
    SUPPORTS_OBJECTIVE = "supports_objective"
    UNKNOWN = "unknown"