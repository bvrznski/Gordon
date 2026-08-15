# Identity Value Projection Model
# ===============================

"""
Immutable identity value projection model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IdentityValueProjection:
    """
    Immutable representation of an identity value projection.
    
    PROPERTIES:
        • value_id: Unique identifier for this value
        • semantic_definition: Human-readable definition
        • source_authority: Authority that validated this value
        • priority: Importance ranking (0.0 to 1.0)
        • application_scope: Where this value applies
        • associated_commitments: Commitments related to this value
        • conflicts: Conflicting values
        • confidence: Confidence in this value (0.0 to 1.0)
        • effective_from_utc: When this value became active
        • provenance: Where this value came from
    """
    
    value_id: str
    """Unique identifier for this identity value."""
    
    semantic_definition: str = ""
    """Human-readable definition of the value."""
    
    source_authority: str = "identity_authority"
    """Authority that validated this value (AuthorityLevel.*)."""
    
    priority: float = 0.5
    """Importance ranking (0.0 to 1.0)."""
    
    application_scope: str = ""
    """Where this value applies."""
    
    associated_commitments: Tuple[str, ...] = field(default_factory=tuple)
    """Commitments related to this value."""
    
    conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """Conflicting values."""
    
    confidence: float = 1.0
    """Confidence in this value (0.0 to 1.0)."""
    
    effective_from_utc: datetime = field(default_factory=datetime.utcnow)
    """When this value became active."""
    
    provenance: str = "canonical"
    """Provenance reference for the value."""