# Identity Gap Model
# ===================

"""
Immutable identity gap model for representing gaps in identity evidence or representation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class IdentityGap:
    """
    Immutable representation of an identity gap.
    
    A gap represents a missing element in the identity structure that should
    be present but lacks sufficient evidence or definition.
    
    PROPERTIES:
        • gap_id: Unique identifier for this gap
        • category: Gap type (IdentityGapKind.*)
        • expected_component: What component is missing
        • reason_for_gap: Why this gap exists
        • potential_sources: Where this information might be found
        • confidence: Confidence in gap assessment (0.0 to 1.0)
    """
    
    gap_id: str
    """Unique identifier for this identity gap."""
    
    category: str = ""
    """Gap type (IdentityGapKind.*)."""
    
    expected_component: str = ""
    """What component or information is missing."""
    
    reason_for_gap: str = ""
    """Why this gap exists (if known)."""
    
    potential_sources: Tuple[str, ...] = field(default_factory=tuple)
    """Where this missing information might be found."""
    
    confidence: float = 1.0
    """Confidence in gap assessment (0.0 to 1.0)."""