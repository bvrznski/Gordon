# Identity Aspect Model
# =====================

"""
Immutable identity aspect model for representing identity components.

An identity aspect represents a component of Gordon's self-identity including
roles, values, commitments, capabilities, and limitations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IdentityAspect:
    """
    Immutable representation of an identity aspect.
    
    PROPERTIES:
        • aspect_id: Unique identifier for this aspect
        • category: What kind of aspect (IdentityAspectCategory.*)
        • semantic_descriptor: Human-readable description
        • source_owner: Who owns this aspect's authority
        • authority: How authoritative this aspect is
        • factuality: Factuality classification of the aspect
        • confidence: Confidence in this aspect (0.0 to 1.0)
        • effective_from_utc: When this aspect became active
        • effective_to_utc: When this aspect ended (if applicable)
        • supporting_evidence: Evidence supporting this aspect
        • opposing_evidence: Evidence contradicting this aspect
        • revision_id: Identity revision that includes this aspect
        • provenance: Where this aspect came from
    """
    
    aspect_id: str
    """Unique identifier for this identity aspect."""
    
    category: str  # IdentityAspectCategory.*
    """What kind of aspect (IdentityAspectCategory.*)."""
    
    semantic_descriptor: str = ""
    """Human-readable description of the aspect."""
    
    source_owner: str = "identity_authority"
    """Owner of the source system (Identity, Memory, etc.)."""
    
    authority: str = "identity_authority"
    """Authority level that validated this aspect (AuthorityLevel.*)."""
    
    factuality: str = "accepted"
    """Factuality classification of the aspect (FactualityClassification.*)."""
    
    confidence: float = 1.0
    """Confidence in this aspect (0.0 to 1.0)."""
    
    effective_from_utc: datetime = field(default_factory=datetime.utcnow)
    """When this aspect became active."""
    
    effective_to_utc: Optional[datetime] = None
    """When this aspect ended (if applicable)."""
    
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence IDs that support this aspect."""
    
    opposing_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence IDs that contradict this aspect."""
    
    revision_id: str = ""
    """Identity revision ID that includes this aspect."""
    
    provenance: str = "canonical"
    """Provenance reference for the aspect."""