# Identity Integration Continuation Model
# =======================================

"""
Immutable identity integration continuation model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class IdentityIntegrationContinuation:
    """
    Immutable representation of an identity integration continuation recommendation.
    
    Continuations are advisory recommendations about what to do next,
    not executable commands or runtime actions.
    
    PROPERTIES:
        • kind: Continuation type (IdentityIntegrationContinuationKind.*)
        • reason: Why this continuation is recommended
        • expected_outcome: What is expected if continued
        • confidence: Confidence in recommendation (0.0 to 1.0)
        • required_resources: Resources needed to continue
    """
    
    kind: str = ""
    """Continuation type (IdentityIntegrationContinuationKind.*)."""
    
    reason: str = ""
    """Why this continuation is recommended."""
    
    expected_outcome: str = ""
    """What is expected if continued."""
    
    confidence: float = 1.0
    """Confidence in recommendation (0.0 to 1.0)."""
    
    required_resources: Tuple[str, ...] = field(default_factory=tuple)
    """Resources needed to continue."""