# Identity Claim Model
# ====================

"""
Immutable identity claim model for representing identity assertions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IdentityClaim:
    """
    Immutable representation of an identity claim.
    
    PROPERTIES:
        • claim_id: Unique identifier for this claim
        • proposition: The statement being claimed
        • subject: Who or what the claim is about
        • authority: Authority level that validated this claim (AuthorityLevel.*)
        • factuality: Factuality classification (FactualityClassification.*)
        • supporting_evidence: Evidence IDs supporting this claim
        • opposing_evidence: Evidence IDs contradicting this claim
        • confidence: Confidence in this claim (0.0 to 1.0)
        • validation_status: Validation status (valid, disputed, unsupported)
        • temporal_scope: Temporal bounds of applicability
        • provenance: Where this claim came from
    """
    
    claim_id: str
    """Unique identifier for this identity claim."""
    
    proposition: str = ""
    """The statement being claimed about identity."""
    
    subject: str = ""
    """Who or what the claim is about."""
    
    authority: str = "identity_authority"
    """Authority level that validated this claim (AuthorityLevel.*)."""
    
    factuality: str = "accepted"
    """Factuality classification (FactualityClassification.*)."""
    
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence IDs supporting this claim."""
    
    opposing_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence IDs contradicting this claim."""
    
    confidence: float = 1.0
    """Confidence in this claim (0.0 to 1.0)."""
    
    validation_status: str = "valid"
    """Validation status (valid, disputed, unsupported)."""
    
    temporal_scope_from_utc: datetime = field(default_factory=datetime.utcnow)
    """Start of temporal scope."""
    
    temporal_scope_to_utc: Optional[datetime] = None
    """End of temporal scope (if applicable)."""
    
    provenance: str = "canonical"
    """Where this claim came from."""