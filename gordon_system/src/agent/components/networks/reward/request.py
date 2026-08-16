# Reward Network - Request Model
# ===============================

"""
Reward evaluation request model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class RewardEvaluationRequest:
    """
    Request to evaluate outcomes and compute reward estimates.
    
    INPUT CONTRACT (Phase 4.10.1 - Part 2):
        • identity: Request identifier
        • outcomes: Outcomes to evaluate
        • belief_state: Current belief state (projection from Predictive Network)
        • world_model: Current world model state
        • goal_projection: Projected goals
        • motivation_projection: Motivational context
        • prediction_error_projection: Prediction errors
        • precision_projection: Precision estimates
        • context_projection: Contextual information
        • reward_policy: Policy reference for evaluation rules
        • semantic_time: Time context for evaluation
        • provenance: Request provenance
        
    All inputs remain immutable. The request does not modify any system state.
    """
    
    # Identity and provenance
    identity: str
    """Request identifier."""
    
    provenance: Optional[str] = None
    """Provenance reference for this request."""
    
    # Outcomes to evaluate (required)
    outcomes: Tuple[dict, ...] = field(default_factory=tuple)
    """Outcomes to evaluate."""
    
    # Context projections from other networks (optional)
    belief_state: Optional[dict] = None
    """Current belief state (from Predictive Network)."""
    
    world_model: Optional[dict] = None
    """Current world model state."""
    
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
    reward_policy: Optional[str] = None
    """Policy reference for evaluation rules."""
    
    semantic_time: str = "immediate"
    """Time context for evaluation (timescale)."""