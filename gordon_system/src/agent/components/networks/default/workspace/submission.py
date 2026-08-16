# Workspace Submission and Revision Proposals
# ============================================

"""
Submission, revision, and withdrawal proposals for workspace candidates.

ARCHITECTURAL PRINCIPLES:
    - All dataclasses are frozen (deeply immutable)
    - No runtime dependencies
    - Bounded by explicit limits
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# WORKSPACE SUBMISSION PROPOSAL
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceSubmissionProposal:
    """
    Immutable proposal to submit a workspace candidate for admission.
    
    The proposal contains all information the external authority needs to
    evaluate admission. It does not perform actual submission or broadcast.
    
    PROPERTIES:
        • proposal_id: Unique identifier for this proposal
        • candidate: The candidate being proposed
        • target_workspace_category: Target workspace (if applicable)
        • requested_audience: Requested audience recommendation
        • requested_access: Requested access classification
        • requested_lifetime: Requested lifetime
        • admission_rationale: Rationale for admission
        • source_references: Source product references used
        • idempotency_key: For deduplication of identical proposals
    """
    
    proposal_id: str
    """Unique identifier for this proposal."""
    
    candidate_id: str
    """ID of the candidate being proposed."""
    
    candidate_revision: int = 1
    """Revision of the candidate being proposed."""
    
    target_workspace_category: Optional[str] = None
    """Target workspace category (if applicable)."""
    
    requested_audience_recommendation: Tuple[str, ...] = field(default_factory=tuple)
    """Requested audience recommendations."""
    
    requested_access_classification: str = "internal_general"
    """Requested access classification."""
    
    requested_disclosure_classification: str = "internal_only"
    """Requested disclosure classification."""
    
    requested_lifetime: str = "transient"
    """Requested lifetime classification."""
    
    admission_rationale: str = ""
    """Rationale for admission."""
    
    source_references: Tuple[str, ...] = field(default_factory=tuple)
    """Source product reference IDs used to create this candidate."""
    
    idempotency_key: str = ""
    """Key for deduplicating identical proposals."""
    
    correlation_id: str = ""
    """Correlation ID for tracing."""
    
    causation_id: Optional[str] = None
    """Causation ID if from another event."""
    
    provenance: str = "canonical"
    """Provenance reference."""
    
    @classmethod
    def for_candidate(
        cls,
        candidate_id: str,
        revision: int = 1,
        idempotency_key: Optional[str] = None,
        correlation_id: str = "",
    ) -> WorkspaceSubmissionProposal:
        """
        Create a submission proposal for a candidate.
        
        Args:
            candidate_id: ID of the candidate to propose
            revision: Revision of the candidate
            idempotency_key: Key for deduplication (generated if None)
            correlation_id: Correlation ID for tracing
            
        Returns:
            New WorkspaceSubmissionProposal instance
        """
        return cls(
            proposal_id=f"proposal_{candidate_id}",
            candidate_id=candidate_id,
            candidate_revision=revision,
            idempotency_key=idempotency_key or f"{candidate_id}:r{revision}",
            correlation_id=correlation_id,
            provenance="canonical",
        )


# =============================================================================
# WORKSPACE CANDIDATE REVISION PROPOSAL
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateRevisionProposal:
    """
    Immutable proposal to revise an existing workspace candidate.
    
    A revision preserves the base candidate while producing a new revision.
    
    PROPERTIES:
        • proposal_id: Unique identifier for this proposal
        • base_candidate_id: ID of the candidate being revised
        • base_revision: Revision being revised
        • changes: What is changing in this revision
        • new_evidence: New evidence supporting the revision
        • reason: Why this revision is needed
    """
    
    proposal_id: str
    """Unique identifier for this proposal."""
    
    base_candidate_id: str
    """ID of the candidate being revised."""
    
    base_revision: int = 1
    """Revision being revised."""
    
    changes: Tuple[str, ...] = field(default_factory=tuple)
    """Description of changed fields."""
    
    new_evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """New evidence reference IDs."""
    
    reason: str = ""
    """Why this revision is needed."""
    
    provenance: str = "canonical"
    """Provenance reference."""
    
    @classmethod
    def refine_content(
        cls,
        candidate_id: str,
        revision: int,
        new_semantic_claims: Tuple[str, ...],
        reason: str = "",
    ) -> WorkspaceCandidateRevisionProposal:
        """
        Create a revision proposal to refine content.
        
        Args:
            candidate_id: ID of the candidate to revise
            revision: Current revision
            new_semantic_claims: Updated semantic claims
            reason: Why revision is needed
            
        Returns:
            New WorkspaceCandidateRevisionProposal instance
        """
        return cls(
            proposal_id=f"revision_{candidate_id}:r{revision}",
            base_candidate_id=candidate_id,
            base_revision=revision,
            changes=("semantic_claims",),
            reason=reason or "Refined semantic content",
        )
    
    @classmethod
    def add_evidence(
        cls,
        candidate_id: str,
        revision: int,
        new_evidence_references: Tuple[str, ...],
        reason: str = "",
    ) -> WorkspaceCandidateRevisionProposal:
        """
        Create a revision proposal to add evidence.
        
        Args:
            candidate_id: ID of the candidate to revise
            revision: Current revision
            new_evidence_references: New evidence reference IDs
            reason: Why revision is needed
            
        Returns:
            New WorkspaceCandidateRevisionProposal instance
        """
        return cls(
            proposal_id=f"revision_{candidate_id}:r{revision}",
            base_candidate_id=candidate_id,
            base_revision=revision,
            changes=("evidence",),
            new_evidence_references=new_evidence_references,
            reason=reason or "Added supporting evidence",
        )


# =============================================================================
# WORKSPACE CANDIDATE REVISION REQUEST
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateRevisionRequest:
    """
    Immutable request from external authority for candidate revision.
    
    The external authority may request specific changes to improve the
    candidate's chances of admission.
    
    PROPERTIES:
        • request_id: Unique identifier for this request
        • candidate_id: ID of the candidate needing revision
        • requested_changes: What should be changed
        • reason: Why revision is requested
        • deadline: When revision must be completed (optional)
    """
    
    request_id: str
    """Unique identifier for this request."""
    
    candidate_id: str
    """ID of the candidate needing revision."""
    
    requested_changes: Tuple[str, ...] = field(default_factory=tuple)
    """Description of requested changes."""
    
    reason: str = ""
    """Why revision is requested."""
    
    deadline_utc: Optional[str] = None
    """When revision must be completed (ISO format string)."""
    
    provenance: str = "canonical"
    """Provenance reference."""
    
    @classmethod
    def for_narrower_scope(
        cls,
        candidate_id: str,
        reason: str = "",
    ) -> WorkspaceCandidateRevisionRequest:
        """
        Create a revision request for narrower scope.
        
        Args:
            candidate_id: ID of the candidate needing revision
            reason: Why revision is requested
            
        Returns:
            New WorkspaceCandidateRevisionRequest instance
        """
        return cls(
            request_id=f"revision_request_{candidate_id}",
            candidate_id=candidate_id,
            requested_changes=("narrower_scope",),
            reason=reason or "Scope too broad",
        )
    
    @classmethod
    def for_more_evidence(
        cls,
        candidate_id: str,
        reason: str = "",
    ) -> WorkspaceCandidateRevisionRequest:
        """
        Create a revision request for more evidence.
        
        Args:
            candidate_id: ID of the candidate needing revision
            reason: Why revision is requested
            
        Returns:
            New WorkspaceCandidateRevisionRequest instance
        """
        return cls(
            request_id=f"revision_request_{candidate_id}",
            candidate_id=candidate_id,
            requested_changes=("more_evidence",),
            reason=reason or "Insufficient supporting evidence",
        )


# =============================================================================
# WORKSPACE CANDIDATE WITHDRAWAL PROPOSAL
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateWithdrawalProposal:
    """
    Immutable proposal to withdraw an existing workspace candidate.
    
    A withdrawal proposal does not remove content. External authority decides.
    
    PROPERTIES:
        • proposal_id: Unique identifier for this proposal
        • candidate_id: ID of the candidate to withdraw
        • revision: Revision being withdrawn
        • reason: Why withdrawal is proposed
        • provenance: Origin tracking
    """
    
    proposal_id: str
    """Unique identifier for this proposal."""
    
    candidate_id: str
    """ID of the candidate to withdraw."""
    
    revision: int = 1
    """Revision being withdrawn."""
    
    reason: str = ""
    """Why withdrawal is proposed."""
    
    provenance: str = "canonical"
    """Provenance reference."""
    
    @classmethod
    def for_source_invalidated(
        cls,
        candidate_id: str,
        revision: int = 1,
    ) -> WorkspaceCandidateWithdrawalProposal:
        """
        Create a withdrawal proposal when source is invalidated.
        
        Args:
            candidate_id: ID of the candidate to withdraw
            revision: Revision being withdrawn
            
        Returns:
            New WorkspaceCandidateWithdrawalProposal instance
        """
        return cls(
            proposal_id=f"withdrawal_{candidate_id}:r{revision}",
            candidate_id=candidate_id,
            revision=revision,
            reason="Source product invalidated",
        )
    
    @classmethod
    def for_confidence_collapsed(
        cls,
        candidate_id: str,
        revision: int = 1,
        previous_confidence: float = 0.8,
    ) -> WorkspaceCandidateWithdrawalProposal:
        """
        Create a withdrawal proposal when confidence collapses.
        
        Args:
            candidate_id: ID of the candidate to withdraw
            revision: Revision being withdrawn
            previous_confidence: Previous confidence level
            
        Returns:
            New WorkspaceCandidateWithdrawalProposal instance
        """
        return cls(
            proposal_id=f"withdrawal_{candidate_id}:r{revision}",
            candidate_id=candidate_id,
            revision=revision,
            reason=f"Confidence collapsed from {previous_confidence:.2f} to near zero",
        )