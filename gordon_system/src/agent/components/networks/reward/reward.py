# Reward Network - Reward Estimate Model
# =======================================

"""
Reward estimate model for reward evaluation.

A RewardEstimate represents a complete assessment of the value of an outcome,
including magnitude, valence, benefits, costs, confidence, and uncertainty.

REWARD LAWS:
    REWARD-LAW-003: Every RewardEstimate references exactly one Outcome.
    REWARD-LAW-004: Reward estimates preserve semantic identity.
    REWARD-LAW-005: Reward estimates preserve provenance.
    REWARD-LAW-006: Reward estimates preserve revision history.
    REWARD-LAW-007: Reward estimates preserve contributing reward sources.
    REWARD-LAW-008: Reward estimates are immutable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


RewardEstimateId = str
"""Unique identifier for a reward estimate."""


ValenceKind = str
"""Type alias for valence kinds (positive/negative/neutral/mixed/unknown)."""


@dataclass(frozen=True)
class RewardSource:
    """
    A single contributor to the reward estimate.
    
    Each reward source is explicitly represented with its contribution
    and supporting evidence. Multiple sources may contribute to a single
    reward estimate.
    
    SOURCE KINDS:
        • goal_progress: Advancement toward strategic objectives
        • curiosity: Exploration of novel information  
        • novelty: Exposure to new experiences
        • competence: Skill acquisition or improvement
        • social_approval: Positive feedback from others
        • resource_acquisition: Gaining new resources
        • risk_reduction: Decreasing potential negative outcomes
        • efficiency_gain: Resource usage optimization
        • knowledge_gain: New understanding acquired
    """
    
    source_kind: str  # RewardSourceKind.*
    """The kind of reward source."""
    
    contribution_amount: float
    """Amount contributed to the estimate."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this contribution."""
    
    provenance: Optional[str] = None
    """Provenance reference for this source type."""


# =============================================================================
# REWARD ESTIMATE (Phase 4.10.1 - Part 2)
# =============================================================================

@dataclass(frozen=True, slots=True)
class RewardEstimate:
    """
    Complete reward assessment for an outcome.
    
    Every reward estimate is attached to exactly one Outcome and represents
    the net value assessment considering benefits, costs, valence, confidence,
    and uncertainty.
    
    PROPERTIES:
        • estimate_id: Unique identifier for this estimate
        • outcome_ref: Reference to the evaluated Outcome
        • magnitude: Net reward magnitude (benefits - costs)
        • valence: Qualitative direction (positive/negative/neutral/etc.)
        • benefit_estimate: Decomposed benefit assessment
        • cost_estimate: Decomposed cost assessment  
        • confidence: Confidence in the estimate
        • uncertainty: Uncertainty about the estimate
        • reward_sources: Explicit contributing sources
        
    PROPERTIES - MULTI-TIMESCALE:
        • immediate_reward: Reward value for immediate horizon
        • short_term_reward: Reward value for short-term (seconds-minutes)
        • medium_term_reward: Reward value for medium-term (minutes-hours)
        • long_term_reward: Reward value for long-term (hours-days)
        
    PROPERTIES - HIERARCHY:
        • action_outcome_reward: Reward at action level
        • task_outcome_reward: Reward at task level  
        • goal_outcome_reward: Reward at goal level
        • strategy_outcome_reward: Reward at strategy level
        
    NOT RESPONSIBLE FOR:
        • Making executive decisions based on reward
        • Modifying outcomes, beliefs, or world model
        • Updating policies or performing learning
        • Selecting actions or generating plans
    """
    
    # Identity and reference (no defaults first)
    estimate_id: RewardEstimateId
    """Unique identifier for this reward estimate."""
    
    outcome_ref: str  # Outcome.canonical_identity
    """Reference to the evaluated Outcome."""
    
    magnitude: float
    """Net reward magnitude (benefits - costs)."""
    
    valence: str  # ValenceKind.*
    """Qualitative direction of the reward."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Fields with defaults (after no-default fields)
    benefit_estimate: float = 0.0
    """Total estimated benefits."""
    
    cost_estimate: float = 0.0
    """Total estimated costs."""
    
    confidence: str = "unknown"  # Confidence level indicator
    """Confidence in the estimate (high/medium/low/unknown)."""
    
    uncertainty: str = "unknown"
    """Uncertainty about the estimate (high/medium/low/unknown)."""
    
    reward_sources: Tuple[RewardSource, ...] = field(default_factory=tuple)
    """Explicitly contributing reward sources."""
    
    immediate_reward: float = 0.0
    short_term_reward: float = 0.0
    medium_term_reward: float = 0.0  
    long_term_reward: float = 0.0
    
    action_outcome_reward: float = 0.0
    task_outcome_reward: float = 0.0
    goal_outcome_reward: float = 0.0
    strategy_outcome_reward: float = 0.0
    
    provenance: Optional[str] = None
    """Provenance reference for this estimation method."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from evaluation."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this estimate."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Evaluation trace for provenance."""
    
    @classmethod
    def create(
        cls,
        estimate_id: str,
        outcome_ref: str,
        magnitude: float,
        valence: str,
        benefit_estimate: float = 0.0,
        cost_estimate: float = 0.0,
        confidence: str = "unknown",
        uncertainty: str = "unknown",
    ) -> RewardEstimate:
        """
        Create a new reward estimate.
        
        Args:
            estimate_id: Unique identifier for this estimate
            outcome_ref: Reference to the Outcome being evaluated
            magnitude: Net reward magnitude (benefits - costs)
            valence: Qualitative direction of reward
            benefit_estimate: Total estimated benefits
            cost_estimate: Total estimated costs
            confidence: Confidence level in the estimate
            uncertainty: Uncertainty about the estimate
            
        Returns:
            New RewardEstimate instance
        """
        return cls(
            estimate_id=estimate_id,
            outcome_ref=outcome_ref,
            revision=0,
            magnitude=magnitude,
            valence=valence,
            benefit_estimate=benefit_estimate,
            cost_estimate=cost_estimate,
            confidence=confidence,
            uncertainty=uncertainty,
        )
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.estimate_id}@v{self.revision}"
    
    @property
    def net_value(self) -> float:
        """Compute net value (benefits - costs)."""
        return self.benefit_estimate - self.cost_estimate
    
    @property  
    def is_positive(self) -> bool:
        """Check if this is a positive reward estimate."""
        return self.valence == "positive"
    
    @property
    def is_negative(self) -> bool:
        """Check if this is a negative reward estimate."""
        return self.valence == "negative"