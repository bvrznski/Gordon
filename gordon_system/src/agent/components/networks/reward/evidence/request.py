# Reward Network - Evidence Request Model
# ========================================

"""
Evidence request model for Phase 4.10.2.

Input contract for the reward evidence engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class RewardEvidenceRequest:
    """
    Request to extract and process reward evidence from outcomes.

    INPUT CONTRACT (Phase 4.10.2):
        • identity: Request identifier
        • outcomes: Outcomes to extract evidence from
        • world_model: Current world model state
        • belief_state: Current belief state projection
        • goal_projection: Projected goals
        • motivation_projection: Motivational context
        • prediction_error_projection: Prediction errors
        • precision_projection: Precision estimates
        • context_projection: Contextual information
        • evidence_policy: Policy reference for evidence extraction rules
        • semantic_time: Time context for evidence

    All inputs remain immutable. The request does not modify any system state.
    """

    # Identity and provenance
    identity: str
    """Request identifier."""

    provenance: Optional[str] = None
    """Provenance reference for this request."""

    # Outcomes to extract from (required)
    outcomes: Tuple[dict, ...] = field(default_factory=tuple)
    """Outcomes to extract evidence from."""

    # Context projections from other networks (optional)
    world_model: Optional[dict] = None
    """Current world model state."""

    belief_state: Optional[dict] = None
    """Current belief state (from Predictive Network)."""

    goal_projection: Optional[dict] = None
    """Projected goals."""

    motivation_projection: Optional[dict] = None
    """Motivational context."""

    prediction_error_projection: Optional[dict] = None
    """Prediction errors."""

    precision_projection: Optional[dict] = None
    """Precision estimates."""

    context_projection: Optional[dict] = None
    """Contextual information."""

    # Policy and time
    evidence_policy: Optional[str] = None
    """Policy reference for evidence extraction rules."""

    semantic_time: str = "immediate"
    """Time context for evidence processing."""