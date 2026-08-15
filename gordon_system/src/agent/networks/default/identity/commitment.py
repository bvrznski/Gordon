# Identity Commitment Projection Model
# =====================================

"""
Immutable identity commitment projection model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IdentityCommitmentProjection:
    """
    Immutable representation of an identity commitment projection.
    
    PROPERTIES:
        • commitment_id: Unique identifier for this commitment
        • owner: Who owns the commitment
        • beneficiary: Who benefits from the commitment
        • content: What is committed
        • source_authority: Authority that validated this commitment
        • status: Current status (active, completed, cancelled)
        • creation_context: How the commitment was created
        • completion_condition: When the commitment is complete
        • expiration_condition: When the commitment expires
        • confidence: Confidence in this commitment (0.0 to 1.0)
        • effective_from_utc: When this commitment became active
        • provenance: Where this commitment came from
    """
    
    commitment_id: str
    """Unique identifier for this identity commitment."""
    
    owner: str = ""
    """Who owns the commitment."""
    
    beneficiary: str = ""
    """Who benefits from the commitment."""
    
    content: str = ""
    """What is committed (description of the obligation)."""
    
    source_authority: str = "identity_authority"
    """Authority that validated this commitment (AuthorityLevel.*)."""
    
    status: str = "active"
    """Current status (active, completed, cancelled, expired)."""
    
    creation_context: str = ""
    """How the commitment was created."""
    
    completion_condition: str = ""
    """When the commitment is considered complete."""
    
    expiration_condition: str = ""
    """When the commitment expires."""
    
    confidence: float = 1.0
    """Confidence in this commitment (0.0 to 1.0)."""
    
    effective_from_utc: datetime = field(default_factory=datetime.utcnow)
    """When this commitment became active."""
    
    provenance: str = "canonical"
    """Provenance reference for the commitment."""