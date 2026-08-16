# Identity Revision Proposal Model
# ================================

"""
Immutable identity revision proposal model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class IdentityRevisionProposal:
    """
    Immutable representation of an identity revision proposal.
    
    PROPERTIES:
        • proposal_id: Unique identifier for this proposal
        • identity_revision_base: The base revision being revised
        • proposed_changes: What changes are proposed
        • preserved_aspects: Aspects to preserve from current revision
        • invalidated_claims: Claims that become invalid after change
        • supporting_evidence: Evidence supporting the proposal
        • opposing_evidence: Evidence contradicting the proposal
        • authority_required: Who must approve this change
        • confidence: Confidence in proposal (0.0 to 1.0)
        • risk: Estimated risk level of change (0.0 to 1.0)
    """
    
    proposal_id: str
    """Unique identifier for this revision proposal."""
    
    identity_revision_base: str = ""
    """The base revision that would be revised."""
    
    proposed_changes: Tuple[str, ...] = field(default_factory=tuple)
    """Changes being proposed (revision operation references)."""
    
    preserved_aspects: Tuple[str, ...] = field(default_factory=tuple)
    """Aspects to preserve from current revision."""
    
    invalidated_claims: Tuple[str, ...] = field(default_factory=tuple)
    """Claims that become invalid after the change."""
    
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this proposal."""
    
    opposing_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence contradicting this proposal."""
    
    authority_required: str = "identity_authority"
    """Who must approve this change (AuthorityLevel.*)."""
    
    confidence: float = 1.0
    """Confidence in proposal (0.0 to 1.0)."""
    
    risk: float = 0.5
    """Estimated risk level of change (0.0 to 1.0)."""