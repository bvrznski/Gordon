# Identity Evidence Model
# =======================

"""
Immutable identity evidence model for representing evidence supporting or 
contradicting identity claims.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IdentityEvidence:
    """
    Immutable representation of identity evidence.
    
    PROPERTIES:
        • evidence_id: Unique identifier for this evidence
        • source_owner: Who owns the source system (Identity, Memory, etc.)
        • source_revision: Source revision at capture time
        • authority: Authority level that validated this evidence (AuthorityLevel.*)
        • factuality: Factuality classification (FactualityClassification.*)
        • captured_at_utc: When this evidence was captured
        • relevance: Relevance to identity integration (0.0 to 1.0)
        • category: Evidence category (IdentityEvidenceCategory.*)
        • supporting_claims: Claim IDs this evidence supports
        • opposing_claims: Claim IDs this evidence contradicts
    """
    
    evidence_id: str
    """Unique identifier for this identity evidence."""
    
    source_owner: str = ""
    """Owner of the source system (Identity, Memory, etc.)."""
    
    source_revision: int = 1
    """Source revision number at capture time."""
    
    authority: str = "identity_authority"
    """Authority level that validated this evidence (AuthorityLevel.*)."""
    
    factuality: str = "recorded"
    """Factuality classification (FactualityClassification.*)."""
    
    captured_at_utc: datetime = field(default_factory=datetime.utcnow)
    """When this evidence was captured."""
    
    relevance: float = 1.0
    """Relevance to identity integration (0.0 to 1.0)."""
    
    category: str = "recorded"
    """Evidence category (IdentityEvidenceCategory.*)."""
    
    supporting_claims: Tuple[str, ...] = field(default_factory=tuple)
    """Claim IDs this evidence supports."""
    
    opposing_claims: Tuple[str, ...] = field(default_factory=tuple)
    """Claim IDs this evidence contradicts."""