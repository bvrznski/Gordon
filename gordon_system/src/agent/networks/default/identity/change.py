# Identity Change Assessment Model
# ================================

"""
Immutable identity change assessment model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IdentityChangeAssessment:
    """
    Immutable representation of an identity change assessment.
    
    PROPERTIES:
        • kind: What changed (IdentityChangeAssessmentKind.*)
        • previous_state: State before the change
        • current_state: Current state after the change
        • timestamp_utc: When the change occurred
        • evidence: Evidence supporting the change
        • confidence: Confidence in assessment (0.0 to 1.0)
    """
    
    kind: str = ""
    """What changed (IdentityChangeAssessmentKind.*)."""
    
    previous_state: str = ""
    """State before the change."""
    
    current_state: str = ""
    """Current state after the change."""
    
    timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    """When the change occurred."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting the change."""
    
    confidence: float = 1.0
    """Confidence in assessment (0.0 to 1.0)."""