# Expected Reward Estimator for Phase 4.10.3
# ==================================================================================================

"""
Expected reward estimator computes predicted future value.

Unlike realized reward which reflects actual experienced value, expected reward
represents the predicted future value based on current evidence and projections.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional

from .base import IntegrationResult


@dataclass(frozen=True)
class ExpectedRewardEstimate:
    """
    Estimated future reward value.
    
    Represents the predicted value of a future outcome or action,
    computed from current evidence and projections.
    
    EXPECTED REWARD LAWS:
        EXPECTED-LAW-001: Expected Reward is explicitly represented
        EXPECTED-LAW-002: Expected Reward remains independent from Realized Reward
        EXPECTED-LAW-003: Expected Reward preserves uncertainty
        EXPECTED-LAW-004: Expected Reward preserves confidence
    
    PROPERTIES:
        • expected_value: Predicted reward value
        • time_horizon: Temporal scope of the expectation
        • confidence: Confidence in the prediction
        • uncertainty: Uncertainty about the prediction
    
    NOT RESPONSIBLE FOR:
        • Updating policies or learning
        • Making executive decisions
        • Modifying system state
    """
    
    expected_value: float
    """Predicted reward value."""
    
    time_horizon: str = "immediate"
    """Temporal scope (immediate, short_term, medium_term, long_term)."""
    
    confidence: float = 0.5
    """Confidence in the prediction (0.0 to 1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty about the prediction (0.0 to 1.0)."""
    
    evidence_ref: Tuple[str, ...] = field(default_factory=tuple)
    """References to evidence supporting this estimate."""
    
    projection_id: Optional[str] = None
    """ID of the projection that generated this expectation."""
    
    @classmethod
    def zero(cls) -> ExpectedRewardEstimate:
        """Create a zero-value expected reward estimate."""
        return cls(expected_value=0.0)
    
    @property
    def net_value(self) -> float:
        """Return the net expected value."""
        return self.expected_value


@dataclass(frozen=True)
class ExpectedRewardContext:
    """
    Context for expected reward estimation.
    
    Contains world model state, goal projections, and other contextual
    information needed to estimate expected future rewards.
    
    PROPERTIES:
        • world_model: Current world model state
        • goal_projection: Projected goals
        • motivation_projection: Motivational context
        • prediction_errors: Prediction error signals
    
    NOT RESPONSIBLE FOR:
        • Modifying any state
        • Making decisions
    """
    
    world_model: Optional[dict] = None
    """Current world model state."""
    
    goal_projection: Optional[dict] = None
    """Projected goals."""
    
    motivation_projection: Optional[dict] = None
    """Motivational context."""
    
    prediction_errors: Optional[dict] = None
    """Prediction error signals."""


@dataclass(frozen=True)
class ExpectedRewardEstimator:
    """
    Estimator for expected future reward values.
    
    Computes predicted reward based on current evidence, world model state,
    and projections. Expected reward is separate from realized reward.
    
    EXPECTED REWARD ESTIMATION PROCESS:
        1. Extract context from evidence state
        2. Project future states using world model
        3. Estimate benefit and cost for projected outcomes
        4. Combine into expected reward estimate
    
    NOT RESPONSIBLE FOR:
        • Modifying system state
        • Learning or policy updates
        • Making executive decisions
    """
    
    def estimate(
        self,
        evidence_state: dict,
        context: Optional[ExpectedRewardContext] = None,
    ) -> ExpectedRewardEstimate:
        """
        Estimate expected future reward from current evidence and context.
        
        Args:
            evidence_state: RewardEvidenceState as dictionary
            context: Context for expectation (optional)
            
        Returns:
            ExpectedRewardEstimate with predicted value and metadata
        """
        trace: Tuple[str, ...] = ("EXPECTED_REWARD_ESTIMATION_START",)
        
        # Extract context from evidence state if not provided
        world_model = (
            context.world_model 
            if context and context.world_model 
            else evidence_state.get("world_model")
        )
        goal_projection = (
            context.goal_projection 
            if context and context.goal_projection 
            else evidence_state.get("goal_projection")
        )
        
        # Estimate based on evidence relationships
        evidences = evidence_state.get("evidences", ())
        
        positive_evidence = []
        negative_evidence = []
        
        for evidence in evidences:
            if isinstance(evidence, dict):
                relationship = evidence.get("relationship", "unknown")
                
                if relationship == "supports_reward":
                    positive_evidence.append(evidence)
                elif relationship == "supports_punishment":
                    negative_evidence.append(evidence)
        
        # Compute expected value
        base_expected_value = self._compute_base_value(
            positive_evidence,
            negative_evidence,
        )
        
        trace += ("EXPECTED_VALUE_COMPUTED",)
        
        # Adjust by confidence and uncertainty
        avg_confidence = self._compute_avg_confidence(evidences)
        avg_uncertainty = self._compute_avg_uncertainty(evidences)
        
        # Time horizon based on evidence timescales
        time_horizon = self._determine_time_horizon(evidences)
        
        trace += ("EXPECTED_REWARD_ESTIMATION_COMPLETE",)
        
        return ExpectedRewardEstimate(
            expected_value=base_expected_value,
            time_horizon=time_horizon,
            confidence=avg_confidence,
            uncertainty=avg_uncertainty,
            evidence_ref=tuple(str(e.get("evidence_id", "")) for e in evidences if isinstance(e, dict)),
            projection_id=context.projection_id if context else None,
        )
    
    def _compute_base_value(
        self,
        positive_evidence: list,
        negative_evidence: list,
    ) -> float:
        """Compute base expected value from evidence counts and quality."""
        # Weight by confidence
        pos_sum = sum(e.get("confidence", 0.5) for e in positive_evidence)
        neg_sum = sum(e.get("confidence", 0.5) for e in negative_evidence)
        
        if not positive_evidence and not negative_evidence:
            return 0.0
        
        # Normalize to [-1, 1] range
        total = pos_sum + neg_sum
        if total == 0:
            return 0.0
        
        return (pos_sum - neg_sum) / total
    
    def _compute_avg_confidence(self, evidences: Tuple[dict, ...]) -> float:
        """Compute average confidence from evidence."""
        if not evidences:
            return 0.5
        
        return sum(e.get("confidence", 0.5) for e in evidences) / len(evidences)
    
    def _compute_avg_uncertainty(self, evidences: Tuple[dict, ...]) -> float:
        """Compute average uncertainty from evidence."""
        if not evidences:
            return 0.5
        
        return sum(e.get("uncertainty", 0.0) for e in evidences) / len(evidences)
    
    def _determine_time_horizon(self, evidences: Tuple[dict, ...]) -> str:
        """Determine time horizon from evidence timescales."""
        if not evidences:
            return "immediate"
        
        # Simple heuristic: check most common timescale
        timescales = [e.get("timescale", "immediate") for e in evidences]
        if any(ts == "long_term" for ts in timescales):
            return "long_term"
        elif any(ts == "medium_term" for ts in timescales):
            return "medium_term"
        elif any(ts == "short_term" for ts in timescales):
            return "short_term"
        else:
            return "immediate"


@dataclass(frozen=True)
class MultiTimescaleExpectedReward:
    """
    Expected reward across multiple timescales.
    
    Preserves expected values at different temporal horizons without
    collapsing them into a single scalar value.
    
    TIMESCALES:
        • immediate: Current moment (0-5 seconds)
        • short_term: Near future (seconds to minutes)
        • medium_term: Intermediate horizon (minutes to hours)
        • long_term: Extended horizon (hours to days)
    
    INVARIANTS:
        • Timescales remain separate and inspectable
        • No collapse of temporal dimensions
    """
    
    immediate: float = 0.0
    """Expected reward for current moment."""
    
    short_term: float = 0.0
    """Expected reward for short-term future."""
    
    medium_term: float = 0.0
    """Expected reward for medium-term future."""
    
    long_term: float = 0.0
    """Expected reward for long-term future."""
    
    @property
    def total(self) -> float:
        """Compute sum across all timescales."""
        return self.immediate + self.short_term + self.medium_term + self.long_term
    
    @classmethod
    def from_estimates(
        cls,
        immediate: ExpectedRewardEstimate,
        short_term: Optional[ExpectedRewardEstimate] = None,
        medium_term: Optional[ExpectedRewardEstimate] = None,
        long_term: Optional[ExpectedRewardEstimate] = None,
    ) -> MultiTimescaleExpectedReward:
        """Create from individual time-scale estimates."""
        return cls(
            immediate=immediate.expected_value if immediate else 0.0,
            short_term=short_term.expected_value if short_term else 0.0,
            medium_term=medium_term.expected_value if medium_term else 0.0,
            long_term=long_term.expected_value if long_term else 0.0,
        )