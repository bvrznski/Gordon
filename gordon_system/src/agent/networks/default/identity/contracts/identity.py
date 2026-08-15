# Identity Capability Contract
# ============================

"""
Protocol for the Identity Capability contract interface.
"""

from __future__ import annotations

from typing import Protocol, Tuple
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IdentityProjectionRequest:
    """
    Request for an identity projection from Identity Capability.
    
    PROPERTIES:
        • request_id: Unique identifier for this request
        • episode_id: Episode making the request (if any)
        • plan_step_id: Plan step making the request (if any)
        • requested_aspects: Which aspects to include
        • temporal_scope: Temporal bounds for projections
        • authority_constraints: What authority levels are acceptable
        • factuality_constraints: What factuality levels are acceptable
        • expected_schema: Expected output schema
        • confidence_threshold: Minimum confidence threshold
        • privacy_constraints: Privacy classification constraints
        • correlation_id: Correlation ID for traceability
        • causation_id: Causation ID for traceability
    """
    
    request_id: str = ""
    """Unique identifier for this request."""
    
    episode_id: str = ""
    """Episode making the request (if any)."""
    
    plan_step_id: str = ""
    """Plan step making the request (if any)."""
    
    requested_aspects: Tuple[str, ...] = ()
    """Which aspects to include in projection."""
    
    temporal_scope_from_utc: str = ""
    """Temporal bounds for projections (start)."""
    
    temporal_scope_to_utc: str = ""
    """Temporal bounds for projections (end)."""
    
    authority_constraints: Tuple[str, ...] = ()
    """What authority levels are acceptable."""
    
    factuality_constraints: Tuple[str, ...] = ()
    """What factuality levels are acceptable."""
    
    expected_schema: str = ""
    """Expected output schema."""
    
    confidence_threshold: float = 0.5
    """Minimum confidence threshold."""
    
    privacy_constraints: str = ""
    """Privacy classification constraints."""
    
    correlation_id: str = ""
    """Correlation ID for traceability."""
    
    causation_id: str = ""
    """Causation ID for traceability."""


@dataclass(frozen=True, slots=True)
class IdentityProjectionResult:
    """
    Result of an identity projection request.
    
    PROPERTIES:
        • result_id: Unique identifier for this result
        • originating_request_id: Request that produced this result
        • episode_id: Episode associated with result
        • status: Status of the operation
        • identity_projection_reference: Reference to the projection
        • identity_aspects: Extracted identity aspects
        • claims: Identity claims extracted
        • continuity_assessment: Continuity assessment
        • confidence: Confidence in projection
        • completeness: Completeness of projection
        • limitations: Known limitations
        • failure_reason: Reason for failure (if failed)
        • provenance: Provenance tracking
    """
    
    result_id: str = ""
    """Unique identifier for this result."""
    
    originating_request_id: str = ""
    """Request that produced this result."""
    
    episode_id: str = ""
    """Episode associated with result."""
    
    status: str = "success"
    """Status of the operation (success, failure, pending)."""
    
    identity_projection_reference: str = ""
    """Reference to the projection."""
    
    identity_aspects: Tuple[str, ...] = ()
    """Extracted identity aspects."""
    
    claims: Tuple[str, ...] = ()
    """Identity claims extracted."""
    
    continuity_assessment: str = ""
    """Continuity assessment."""
    
    confidence: float = 1.0
    """Confidence in projection (0.0 to 1.0)."""
    
    completeness: float = 1.0
    """Completeness of projection (0.0 to 1.0)."""
    
    limitations: Tuple[str, ...] = ()
    """Known limitations."""
    
    failure_reason: str = ""
    """Reason for failure (if failed)."""
    
    provenance: str = "canonical"
    """Provenance tracking."""


@dataclass(frozen=True, slots=True)
class IdentityRevisionProposal:
    """
    Immutable identity revision proposal.
    
    PROPERTIES:
        • proposal_id: Unique identifier for this proposal
        • identity_revision_base: Base revision being revised
        • proposed_changes: What changes are proposed
        • preserved_aspects: Aspects to preserve
        • invalidated_claims: Claims that become invalid
        • supporting_evidence: Evidence supporting change
        • opposing_evidence: Evidence contradicting change
        • authority_required: Who must approve
        • confidence: Confidence in proposal (0.0 to 1.0)
        • risk: Estimated risk level (0.0 to 1.0)
    """
    
    proposal_id: str = ""
    """Unique identifier for this proposal."""
    
    identity_revision_base: str = ""
    """Base revision being revised."""
    
    proposed_changes: Tuple[str, ...] = ()
    """Changes being proposed."""
    
    preserved_aspects: Tuple[str, ...] = ()
    """Aspects to preserve from current revision."""
    
    invalidated_claims: Tuple[str, ...] = ()
    """Claims that become invalid after change."""
    
    supporting_evidence: Tuple[str, ...] = ()
    """Evidence supporting this proposal."""
    
    opposing_evidence: Tuple[str, ...] = ()
    """Evidence contradicting this proposal."""
    
    authority_required: str = "identity_authority"
    """Who must approve this change."""
    
    confidence: float = 1.0
    """Confidence in proposal (0.0 to 1.0)."""
    
    risk: float = 0.5
    """Estimated risk level of change (0.0 to 1.0)."""


@dataclass(frozen=True, slots=True)
class IdentityRevisionEvaluation:
    """
    Evaluation result for an identity revision proposal.
    
    PROPERTIES:
        • evaluation_id: Unique identifier for this evaluation
        • originating_proposal_id: Proposal being evaluated
        • episode_id: Episode making the request (if any)
        • status: Status of the evaluation
        • decision: Decision made (accept, reject, defer, modify)
        • modified_changes: Modified changes (if modified)
        • required_authority: Required authority for change
        • confidence: Confidence in evaluation (0.0 to 1.0)
        • limitations: Known limitations
        • provenance: Provenance tracking
    """
    
    evaluation_id: str = ""
    """Unique identifier for this evaluation."""
    
    originating_proposal_id: str = ""
    """Proposal being evaluated."""
    
    episode_id: str = ""
    """Episode making the request (if any)."""
    
    status: str = "completed"
    """Status of the evaluation (completed, pending, failed)."""
    
    decision: str = "accept"
    """Decision made (accept, reject, defer, modify)."""
    
    modified_changes: Tuple[str, ...] = ()
    """Modified changes (if modified)."""
    
    required_authority: str = ""
    """Required authority for change."""
    
    confidence: float = 1.0
    """Confidence in evaluation (0.0 to 1.0)."""
    
    limitations: Tuple[str, ...] = ()
    """Known limitations."""
    
    provenance: str = "canonical"
    """Provenance tracking."""


class IdentityCapabilityContract(Protocol):
    """
    Protocol for the Identity Capability contract interface.
    
    The Default Network depends only on contracts.
    It must not import concrete Identity implementation.
    It must not invoke mutation operations directly.
    """
    
    def project(
        self,
        request: IdentityProjectionRequest,
    ) -> IdentityProjectionResult:
        """
        Project current identity state as specified by the request.
        
        Args:
            request: The projection request with constraints
            
        Returns:
            IdentityProjectionResult with projected identity information
        """
        ...
    
    def evaluate_revision(
        self,
        proposal: IdentityRevisionProposal,
    ) -> IdentityRevisionEvaluation:
        """
        Evaluate a revision proposal.
        
        Args:
            proposal: The revision proposal to evaluate
            
        Returns:
            IdentityRevisionEvaluation with the evaluation result
        """
        ...