# Identity Limitation Projection Model
# ====================================

"""
Immutable identity limitation projection model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IdentityLimitationProjection:
    """
    Immutable representation of an identity limitation projection.
    
    PROPERTIES:
        • limitation_id: Unique identifier for this limitation
        • description: Human-readable description
        • affected_scope: What is affected by this limitation
        • source: Where this limitation comes from
        • evidence: Evidence supporting the limitation
        • confidence: Confidence in this limitation (0.0 to 1.0)
        • temporal_validity: Temporal bounds of applicability
        • mitigation_proposal_references: Related mitigation proposals
        • provenance: Provenance tracking
    """
    
    limitation_id: str
    """Unique identifier for this identity limitation."""
    
    description: str = ""
    """Human-readable description of the limitation."""
    
    affected_scope: str = ""
    """What is affected by this limitation."""
    
    source: str = "identity_self_assessment"
    """Where this limitation comes from."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence IDs supporting the limitation."""
    
    confidence: float = 1.0
    """Confidence in this limitation (0.0 to 1.0)."""
    
    temporal_validity_from_utc: datetime = field(default_factory=datetime.utcnow)
    """When this limitation started being applicable."""
    
    temporal_validity_to_utc: Optional[datetime] = None
    """When this limitation may end (if applicable)."""
    
    mitigation_proposal_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to related mitigation proposals."""
    
    provenance: str = "canonical"
    """Provenance tracking reference."""