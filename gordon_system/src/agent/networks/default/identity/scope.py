# Identity Integration Scope Model
# ================================

"""
Immutable identity integration scope model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class IdentityIntegrationScope:
    """
    Immutable representation of an identity integration scope.
    
    PROPERTIES:
        • scope_id: Unique identifier for this scope
        • max_identity_aspects: Maximum identity aspects to consider
        • max_roles: Maximum roles to consider
        • max_values: Maximum values to consider
        • max_commitments: Maximum commitments to consider
        • max_capabilities: Maximum capabilities to assess
        • max_limitations: Maximum limitations to record
        • max_source_references: Maximum source references allowed
        • temporal_range_from_utc: Start of temporal range (if any)
        • temporal_range_to_utc: End of temporal range (if any)
        • included_aspects: Which aspects are explicitly included
        • excluded_aspects: Which aspects are explicitly excluded
    """
    
    scope_id: str = ""
    """Unique identifier for this identity integration scope."""
    
    max_identity_aspects: int = 50
    """Maximum identity aspects to consider."""
    
    max_roles: int = 20
    """Maximum roles to consider."""
    
    max_values: int = 30
    """Maximum values to consider."""
    
    max_commitments: int = 25
    """Maximum commitments to consider."""
    
    max_capabilities: int = 15
    """Maximum capabilities to assess."""
    
    max_limitations: int = 15
    """Maximum limitations to record."""
    
    max_source_references: int = 100
    """Maximum source references allowed."""
    
    temporal_range_from_utc: str = ""
    """Start of temporal range (if any)."""
    
    temporal_range_to_utc: str = ""
    """End of temporal range (if any)."""
    
    included_aspects: Tuple[str, ...] = field(default_factory=tuple)
    """Which aspects are explicitly included."""
    
    excluded_aspects: Tuple[str, ...] = field(default_factory=tuple)
    """Which aspects are explicitly excluded."""