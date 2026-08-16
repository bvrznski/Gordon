# Workspace Feedback Contracts Subpackage
# =======================================

"""
Feedback contract models for workspace candidates.

ARCHITECTURAL PRINCIPLES:
    - All dataclasses are frozen (deeply immutable)
    - No runtime dependencies
    - Bounded by explicit limits
"""

from __future__ import annotations

# =============================================================================
# FEEDBACK MODELS
# =============================================================================

from .broadcast import (
    WorkspaceBroadcastResult,
)

from .consumption import (
    WorkspaceConsumptionFeedback,
)

from .expiration import (
    WorkspaceExpirationFeedback,
)

from .eviction import (
    WorkspaceEvictionFeedback,
)

from .projection import (
    WorkspaceFeedbackProjection,
)


__all__ = [
    # Broadcast result
    "WorkspaceBroadcastResult",
    
    # Consumption feedback
    "WorkspaceConsumptionFeedback",
    
    # Expiration feedback
    "WorkspaceExpirationFeedback",
    
    # Eviction feedback
    "WorkspaceEvictionFeedback",
    
    # Feedback projection
    "WorkspaceFeedbackProjection",
]