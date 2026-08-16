# Realized Reward Estimator for Phase 4.10.3
# ==================================================================================================

"""
Realized reward estimator computes actual experienced value.

Unlike expected reward which reflects predicted future value, realized reward
represents the actual value experienced from outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class RealizedRewardEstimate:
    """
    Actual experienced reward value.
    
    Represents the real value experienced from an outcome or action,
    computed directly from evidence of what actually occurred.
    
    REALIZED REWARD LAWS:
        REALIZED-LAW-001: Realized Reward is explicitly represented
        REALIZED-LAW-002: Realized Reward preserves provenance
        REALIZED-LAW-003: Realized Reward remains immutable
        REALIZED-LAW-004: Realized Reward remains distinguishable from Expected Reward
    
    PROPERTIES:
        • realized_value: Actual experienced value
        • time_of_occurrence: When this was realized
        • outcome_ref: Reference to the outcome that produced it
        • confidence: Confidence in the measurement
    
    NOT RESPONSIBLE FOR:
        • Updating policies or learning
        • Making executive decisions
        • Modifying system state
    """
    
    realized_value: float
    """Actual experienced reward value."""
    
    time_of_occurrence: str = "immediate"
    """When this was realized (semantic time)."""
    
    outcome_ref: Tuple[str, ...] = field(default_factory=tuple)
    """References to outcomes that produced this reward."""
    
    confidence: float = 1.0
    """Confidence in the measurement (0.0 to 1.0)."""
    
    uncertainty: float = 0.0
    """Uncertainty about the measurement (0.0 to 1.0)."""
    
    evidence_ref: Tuple[str, ...] = field(default_factory=tuple)
    """References to evidence supporting this estimate."""
    
    @classmethod
    def zero(cls) -> RealizedRewardEstimate:
        """Create a zero-value realized reward estimate."""
        return cls(realized_value=0.0)
    
    @property
    def net_value(self) -> float:
        """Return the net realized value."""
        return self.realized_value


@dataclass(frozen=True)
class MultiTimescaleRealizedReward:
    """
    Realized reward across multiple timescales.
    
    Preserves realized values at different temporal horizons without
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
    """Realized reward for current moment."""
    
    short_term: float = 0.0
    """Realized reward for short-term future."""
    
    medium_term: float = 0.0
    """Realized reward for medium-term future."""
    
    long_term: float = 0.0
    """Realized reward for long-term future."""
    
    @property
    def total(self) -> float:
        """Compute sum across all timescales."""
        return self.immediate + self.short_term + self.medium_term + self.long_term
    
    @classmethod
    def from_estimates(
        cls,
        immediate: RealizedRewardEstimate,
        short_term: Optional[RealizedRewardEstimate] = None,
        medium_term: Optional[RealizedRewardEstimate] = None,
        long_term: Optional[RealizedRewardEstimate] = None,
    ) -> MultiTimescaleRealizedReward:
        """Create from individual time-scale estimates."""
        return cls(
            immediate=immediate.realized_value if immediate else 0.0,
            short_term=short_term.realized_value if short_term else 0.0,
            medium_term=medium_term.realized_value if medium_term else 0.0,
            long_term=long_term.realized_value if long_term else 0.0,
        )


@dataclass(frozen=True)
class RealizedRewardEstimator:
    """
    Estimator for realized reward values.
    
    Computes actual experienced reward from evidence of what occurred.
    Realized reward is separate from expected (predicted) reward.
    
    REALIZED REWARD ESTIMATION PROCESS:
        1. Extract outcome evidence
        2. Compute benefit and cost from actual outcomes
        3. Combine into realized reward estimate
    
    NOT RESPONSIBLE FOR:
        • Modifying system state
        • Learning or policy updates
        • Making executive decisions
    """
    
    def estimate(
        self,
        evidence_state: dict,
    ) -> RealizedRewardEstimate:
        """
        Estimate realized reward from evidence of actual outcomes.
        
        Args:
            evidence_state: RewardEvidenceState as dictionary
            
        Returns:
            RealizedRewardEstimate with actual value and metadata
        """
        trace: Tuple[str, ...] = ("REALIZED_REWARD_ESTIMATION_START",)
        
        evidences = evidence_state.get("evidences", ())
        
        # Compute realized value from direct evidence
        positive_sum = 0.0
        negative_sum = 0.0
        
        for evidence in evidences:
            if isinstance(evidence, dict):
                relationship = evidence.get("relationship", "unknown")
                confidence = evidence.get("confidence", 0.5)
                
                # Supports reward = positive realized value
                if relationship == "supports_reward":
                    positive_sum += confidence
                # Supports punishment = negative realized value
                elif relationship == "supports_punishment":
                    negative_sum += confidence
        
        realized_value = positive_sum - negative_sum
        
        trace += ("REALIZED_VALUE_COMPUTED",)
        
        # Compute average confidence and uncertainty
        avg_confidence = self._compute_avg_confidence(evidences)
        avg_uncertainty = self._compute_avg_uncertainty(evidences)
        
        trace += ("REALIZED_REWARD_ESTIMATION_COMPLETE",)
        
        return RealizedRewardEstimate(
            realized_value=realized_value,
            time_of_occurrence="immediate",
            outcome_ref=tuple(),
            confidence=avg_confidence,
            uncertainty=avg_uncertainty,
            evidence_ref=tuple(str(e.get("evidence_id", "")) for e in evidences if isinstance(e, dict)),
        )
    
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


@dataclass(frozen=True)
class RealizedRewardAggregator:
    """
    Aggregates multiple realized reward estimates.
    
    Combines realized rewards from different sources while preserving
    their individual identities and contributions.
    
    PROPERTIES:
        • total_value: Sum of all realized values
        • individual_estimates: All contributing estimates
    
    NOT RESPONSIBLE FOR:
        • Modifying system state
        • Making executive decisions
    """
    
    individual_estimates: Tuple[RealizedRewardEstimate, ...]
    """All contributing realized reward estimates."""
    
    @property
    def total_value(self) -> float:
        """Sum of all realized values."""
        return sum(e.realized_value for e in self.individual_estimates)
    
    @property
    def avg_confidence(self) -> float:
        """Average confidence across all estimates."""
        if not self.individual_estimates:
            return 0.5
        return sum(e.confidence for e in self.individual_estimates) / len(self.individual_estimates)
    
    @classmethod
    def aggregate(cls, *estimates: RealizedRewardEstimate) -> "RealizedRewardAggregator":
        """Create aggregator from estimates."""
        return cls(individual_estimates=estimates)