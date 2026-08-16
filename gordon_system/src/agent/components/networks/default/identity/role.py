# Identity Role Model
# ===================

"""
Immutable identity role model for representing roles in Gordon's identity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IdentityRole:
    """
    Immutable representation of an identity role.
    
    PROPERTIES:
        • role_id: Unique identifier for this role
        • kind: What kind of role (IdentityRoleKind.*)
        • definition: Human-readable definition
        • scope: Scope or boundaries of the role
        • source_authority: Who validated this role
        • responsibilities: Responsibilities associated with the role
        • commitments: Commitments made by this role
        • constraints: Constraints on this role
        • activation_conditions: When this role becomes active
        • deactivation_conditions: When this role ends
        • confidence: Confidence in this role (0.0 to 1.0)
        • effective_from_utc: When this role became active
        • effective_to_utc: When this role ended (if applicable)
        • provenance: Where this role came from
    """
    
    role_id: str
    """Unique identifier for this identity role."""
    
    kind: str  # IdentityRoleKind.*
    """What kind of role (IdentityRoleKind.*)."""
    
    definition: str = ""
    """Human-readable definition of the role."""
    
    scope: str = ""
    """Scope or boundaries of the role."""
    
    source_authority: str = "identity_authority"
    """Authority that validated this role (AuthorityLevel.*)."""
    
    responsibilities: Tuple[str, ...] = field(default_factory=tuple)
    """Responsibilities associated with this role."""
    
    commitments: Tuple[str, ...] = field(default_factory=tuple)
    """Commitments made by this role."""
    
    constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Constraints on this role."""
    
    activation_conditions: str = ""
    """When this role becomes active."""
    
    deactivation_conditions: str = ""
    """When this role ends."""
    
    confidence: float = 1.0
    """Confidence in this role (0.0 to 1.0)."""
    
    effective_from_utc: datetime = field(default_factory=datetime.utcnow)
    """When this role became active."""
    
    effective_to_utc: Optional[datetime] = None
    """When this role ended (if applicable)."""
    
    provenance: str = "canonical"
    """Provenance reference for the role."""