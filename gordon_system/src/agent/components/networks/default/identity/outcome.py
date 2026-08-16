# Identity Integration Outcome Model
# ===================================

"""
Immutable identity integration outcome model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class IdentityIntegrationOutcome:
    """
    Immutable representation of an identity integration episode outcome.
    
    Outcomes represent the final result of an identity integration episode.
    
    PROPERTIES:
        • outcome_id: Unique identifier for this outcome
        • kind: Outcome type (IdentityIntegrationOutcomeKind.*)
        • subject: What was integrated
        • identity_revision: Revision at time of completion
        • accepted_products: Products that were accepted
        • rejected_products: Products that were rejected
        • unresolved_products: Products that remain unresolved
        • revision_proposals: Revision proposals generated
        • confidence: Confidence in outcome (0.0 to 1.0)
        • completeness: How complete the outcome is (0.0 to 1.0)
        • limitations: Known limitations of this outcome
    """
    
    outcome_id: str
    """Unique identifier for this identity integration outcome."""
    
    kind: str = ""
    """Outcome type (IdentityIntegrationOutcomeKind.*)."""
    
    subject: str = ""
    """What was integrated."""
    
    identity_revision: str = ""
    """Revision at time of completion."""
    
    accepted_products: Tuple[str, ...] = field(default_factory=tuple)
    """Product IDs that were accepted."""
    
    rejected_products: Tuple[str, ...] = field(default_factory=tuple)
    """Product IDs that were rejected."""
    
    unresolved_products: Tuple[str, ...] = field(default_factory=tuple)
    """Product IDs that remain unresolved."""
    
    revision_proposals: Tuple[str, ...] = field(default_factory=tuple)
    """Revision proposals generated."""
    
    confidence: float = 1.0
    """Confidence in outcome (0.0 to 1.0)."""
    
    completeness: float = 1.0
    """How complete the outcome is (0.0 to 1.0)."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this outcome."""