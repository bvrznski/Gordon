# Workspace Integration Contracts Subpackage
# ==========================================

"""
Protocol definitions for workspace integration external interfaces.

ARCHITECTURAL PRINCIPLES:
    - All contracts are Protocol types (no runtime implementation)
    - No runtime dependencies
    - Bounded by explicit limits
"""

from __future__ import annotations


# =============================================================================
# WORKSPACE CONTRACTS
# =============================================================================

class WorkspaceAdmissionContract:
    """
    Protocol for external workspace admission authority.
    
    The Default Network depends only on this contract, never concrete implementations.
    """
    
    def evaluate_candidate(
        self,
        proposal_id: str,
        candidate_id: str,
        revision: int = 1,
        audience_recommendations: tuple[str, ...] = (),
        access_classification: str = "internal_general",
        disclosure_classification: str = "internal_only",
        lifetime: str = "transient",
    ) -> dict:
        """
        Evaluate a candidate submission proposal.
        
        Args:
            proposal_id: ID of the proposal
            candidate_id: ID of the candidate being evaluated
            revision: Revision of the candidate
            audience_recommendations: Requested audience recommendations
            access_classification: Requested access classification
            disclosure_classification: Requested disclosure classification
            lifetime: Requested lifetime classification
            
        Returns:
            Admission decision dictionary with keys:
                - decision_kind: accept/reject/defer/request_revision/etc.
                - constraints: Any constraints on accepted content
                - reasons: Human-readable explanation(s)
        """
        raise NotImplementedError


class WorkspaceFeedbackContract:
    """
    Protocol for external workspace feedback projection.
    
    Used to project all feedback received about a workspace integration episode.
    """
    
    def project_feedback(
        self,
        request_id: str,
    ) -> dict:
        """
        Project all feedback for an integration episode.
        
        Args:
            request_id: ID of the integration request
            
        Returns:
            Feedback projection dictionary with keys:
                - admission_decisions: All admission decisions
                - broadcast_results: All broadcast results
                - consumption_feedback: All consumption feedback
                - expiration_feedback: All expiration feedback
                - eviction_feedback: All eviction feedback
                - unresolved_revision_requests: Unresolved revision requests
        """
        raise NotImplementedError


# =============================================================================
# ADMISSION AUTHORITY CONTRACT
# =============================================================================

class AdmissionAuthorityContract:
    """
    Protocol for admission authority operations.
    
    Defines the interface for external authorities that make admission decisions.
    """
    
    def admit_candidate(
        self,
        proposal_id: str,
        candidate_id: str,
        revision: int = 1,
        audience_recommendations: tuple[str, ...] = (),
        access_classification: str = "internal_general",
        lifetime: str = "transient",
    ) -> dict:
        """Admit a candidate to the workspace."""
        raise NotImplementedError
    
    def reject_candidate(
        self,
        proposal_id: str,
        candidate_id: str,
        revision: int = 1,
    ) -> dict:
        """Reject a candidate from admission."""
        raise NotImplementedError
    
    def defer_admission(
        self,
        proposal_id: str,
        candidate_id: str,
        revision: int = 1,
    ) -> dict:
        """Defer admission of a candidate for later evaluation."""
        raise NotImplementedError


# =============================================================================
# FEEDBACK CONTRACT
# =============================================================================

class FeedbackContract:
    """
    Protocol for workspace feedback collection.
    
    Defines the interface for collecting feedback on workspace items.
    """
    
    def get_broadcast_result(
        self,
        broadcast_id: str,
    ) -> dict:
        """Get result of a specific broadcast."""
        raise NotImplementedError
    
    def get_consumption_feedback(
        self,
        item_id: str,
        consumer_category: str,
    ) -> dict:
        """Get consumption feedback for an item from a consumer."""
        raise NotImplementedError
    
    def get_eviction_feedback(
        self,
        item_id: str,
    ) -> dict:
        """Get eviction feedback for an item."""
        raise NotImplementedError


# =============================================================================
# CONSUMER PROJECTION CONTRACT
# =============================================================================

class ConsumerProjectionContract:
    """
    Protocol for consumer projections.
    
    Defines the interface for projecting which consumers may receive workspace items.
    """
    
    def get_consumer_categories(self) -> tuple[str, ...]:
        """Get all available consumer categories."""
        raise NotImplementedError
    
    def can_consume(
        self,
        consumer_category: str,
        access_classification: str,
        disclosure_classification: str,
    ) -> bool:
        """Check if a consumer category can consume an item with given classifications."""
        raise NotImplementedError


# =============================================================================
# ATTENTION ASSESSMENT CONTRACT
# =============================================================================

class AttentionAssessmentContract:
    """
    Protocol for attention assessment.
    
    Defines the interface for external attention systems that assess candidate
    attention requirements.
    """
    
    def assess_candidate_attention(
        self,
        candidate_id: str,
        relevance_to_objectives: float = 0.5,
        urgency: float = 0.0,
        importance: float = 0.5,
    ) -> dict:
        """Assess attention requirements for a candidate."""
        raise NotImplementedError


# =============================================================================
# EXECUTIVE REVIEW CONTRACT
# =============================================================================

class ExecutiveReviewContract:
    """
    Protocol for Executive review.
    
    Defines the interface for External Executive authority that makes strategic
    decisions about candidates requiring review.
    """
    
    def request_executive_review(
        self,
        candidate_id: str,
        revision: int = 1,
        rationale: str = "",
    ) -> dict:
        """Request Executive review of a candidate."""
        raise NotImplementedError
    
    def evaluate_executive_candidate(
        self,
        candidate_id: str,
        revision: int = 1,
    ) -> dict:
        """Evaluate an Executive review candidate."""
        raise NotImplementedError


# =============================================================================
# CONTEXT PROVIDER CONTRACT
# =============================================================================

class ContextProviderContract:
    """
    Protocol for context projection provider.
    
    Defines the interface for obtaining InternalContext projections needed for
    workspace integration.
    """
    
    def get_context_projection(
        self,
        context_id: str,
        revision: int = 1,
    ) -> dict:
        """Get a specific context projection."""
        raise NotImplementedError


# =============================================================================
# VALIDATION CONTRACT
# =============================================================================

class ValidationContract:
    """
    Protocol for workspace integration validation.
    
    Defines the interface for validating workspace integration requests and
    candidates against architectural constraints.
    """
    
    def validate_request(
        self,
        request_id: str,
        purpose_kind: str,
        subject_kind: str,
        scope: dict,
        context_id: str,
    ) -> tuple[bool, list[str]]:
        """Validate a workspace integration request."""
        raise NotImplementedError
    
    def validate_candidate(
        self,
        candidate_id: str,
        kind: str,
        purpose: str,
        content: dict,
        origin: dict,
    ) -> tuple[bool, list[str]]:
        """Validate a workspace candidate structure."""
        raise NotImplementedError