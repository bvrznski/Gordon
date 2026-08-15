# Identity Integration Purpose Model
# ==================================

"""
Immutable identity integration purpose model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class IdentityIntegrationPurpose:
    """
    Immutable representation of an identity integration purpose.
    
    Purposes determine what kind of identity integration is being performed
    and affect which projections are needed, source types allowed, and
    completion rules applied.
    
    PROPERTIES:
        • purpose_id: Unique identifier for this purpose
        • kind: What kind of integration (IdentityIntegrationPurposeKind.*)
        • description: Human-readable description of the purpose
        • required_projections: What projections are required
        • valid_source_types: Which source types are allowed
        • minimum_confidence: Minimum confidence threshold
    """
    
    purpose_id: str = ""
    """Unique identifier for this identity integration purpose."""
    
    kind: str = "general_identity_integration"
    """What kind of integration (IdentityIntegrationPurposeKind.*)."""
    
    description: str = ""
    """Human-readable description of the purpose."""
    
    required_projections: Tuple[str, ...] = field(default_factory=tuple)
    """What projections are required for this purpose."""
    
    valid_source_types: Tuple[str, ...] = field(default_factory=tuple)
    """Which source types are allowed for this purpose."""
    
    minimum_confidence: float = 0.5
    """Minimum confidence threshold (0.0 to 1.0)."""