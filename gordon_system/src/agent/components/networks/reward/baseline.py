# Reward Network - Adaptive Reward Baseline Model (Phase 4.10.4)
# ================================================================

"""
Adaptive reward baseline model for temporal reward interpretation.

An AdaptiveRewardBaseline represents a reference point against which reward
estimates are interpreted, evolving over time as expectations shift through
repeated experience and context changes.

BASELINE TYPES:
    • expected_reward: Expected value given current conditions
    • expected_effort: Expected resource expenditure
    • expected_quality: Expected outcome quality (0.0 to 1.0)
    • expected_latency: Expected completion time

BASELINE LAWS:
    BASELINE-LAW-001: Exactly one AdaptiveRewardBaseline exists for each semantic domain.
    BASELINE-LAW-002: Baselines remain immutable.
    BASELINE-LAW-003: Baseline revisions preserve lineage.
    BASELINE-LAW-004: Baseline adaptation preserves provenance.
    BASELINE-LAW-005: Baseline adaptation shall never modify historical baselines.
    BASELINE-LAW-006: Baselines remain distinct from Reward Estimates.
    BASELINE-LAW-007: Baselines remain distinct from Motivation.
    BASELINE-LAW-008: Baseline adaptation remains deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class AdaptiveRewardBaseline:
    """
    Semantic baseline for reward interpretation that adapts over time.
    
    A baseline provides a reference point against which reward estimates can be
    meaningfully compared. As expectations evolve through repeated experience,
    the same reward value may represent different levels of surprise or
    significance relative to the current baseline.
    
    CRITICAL DISTINCTION:
        • Reward Estimates: Absolute semantic valuation
        • Adaptive Baselines: Relative reference for interpreting that value
        
    For example, receiving +10 reward every day initially represents exceptional
    performance. Months later, the same +10 may be interpreted as normal because
    the baseline has shifted. The actual reward estimate remains unchanged.
    
    PROPERTIES:
        • baseline_id: Unique identifier for this baseline
        • domain: Semantic domain this baseline applies to
        • current_value: Current baseline reference point
        • adaptation_history: Record of past values and when they changed
        • adaptation_rate: Speed of baseline adjustment
        • confidence: Confidence in the baseline value
        • uncertainty: Uncertainty about the baseline
        
    NOT RESPONSIBLE FOR:
        • Computing reward estimates (that belongs to RewardEvaluation)
        • Modifying reward estimates from evaluation results
        • Learning policies from adaptation
        • Making executive decisions based on baseline shifts
    
    The baseline is a descriptive temporal model. It answers "What do we expect?"
    not "How should I learn?" or "What should I do?"
    """
    
    # Identity and reference (no defaults first)
    baseline_id: str
    """Unique identifier for this baseline."""
    
    domain: str  # BaselineDomain.*
    """Semantic domain this baseline applies to."""
    
    current_value: float = 0.0
    """Current baseline reference point."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Adaptation tracking (always preserved)
    adaptation_history: Tuple[Tuple[str, float], ...] = field(default_factory=tuple)
    """History of (timestamp_or_event, value) pairs showing evolution."""
    
    initial_value: float = 0.0
    """Original baseline value when first established."""
    
    # Adaptation dynamics
    adaptation_rate: float = 0.1
    """Rate of baseline adjustment (0.0=static, 1.0=fully adaptive)."""
    
    last_adaptation_event: Optional[str] = None
    """Description of what triggered the last adaptation."""
    
    # Semantic evaluation fields
    confidence: float = 1.0
    """Confidence in the current baseline value."""
    
    uncertainty: float = 0.0
    """Uncertainty about the baseline value."""
    
    # Context and provenance
    context_signature: Tuple[str, ...] = field(default_factory=tuple)
    """Context features this baseline applies to."""
    
    provenance: Optional[str] = None
    """Provenance reference for this baseline construction."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from baseline analysis."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Analysis trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.baseline_id}@v{self.revision}"
    
    @property
    def history_length(self) -> int:
        """Get count of historical adaptation events."""
        return len(self.adaptation_history)
    
    @property
    def has_adapted(self) -> bool:
        """Check if baseline has adapted from its initial value."""
        return self.current_value != self.initial_value
    
    # Factory methods for common baseline types
    @classmethod
    def create_reward_baseline(
        cls,
        baseline_id: str,
        domain: str = "reward",
        expected_value: float = 0.0,
        confidence: float = 1.0,
    ) -> AdaptiveRewardBaseline:
        """Create a reward expectation baseline."""
        return cls(
            baseline_id=baseline_id,
            domain=domain,
            current_value=expected_value,
            initial_value=expected_value,
            adaptation_history=tuple(),
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    @classmethod
    def create_effort_baseline(
        cls,
        baseline_id: str,
        expected_effort: float = 0.5,
        confidence: float = 0.8,
    ) -> AdaptiveRewardBaseline:
        """Create an effort expectation baseline."""
        return cls(
            baseline_id=baseline_id,
            domain="effort",
            current_value=expected_effort,
            initial_value=expected_effort,
            adaptation_history=tuple(),
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    @classmethod
    def create_quality_baseline(
        cls,
        baseline_id: str,
        expected_quality: float = 0.8,
        confidence: float = 0.9,
    ) -> AdaptiveRewardBaseline:
        """Create a quality expectation baseline."""
        return cls(
            baseline_id=baseline_id,
            domain="quality",
            current_value=expected_quality,
            initial_value=expected_quality,
            adaptation_history=tuple(),
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    # Adaptation methods (return new immutable instances)
    def adapt_to_new_value(
        self,
        new_value: float,
        event_description: str,
    ) -> AdaptiveRewardBaseline:
        """
        Create a new baseline instance with adapted value.
        
        This method does not modify the current instance. It creates a new
        version with the updated value and records the adaptation in history.
        
        Args:
            new_value: The new baseline reference point
            event_description: What triggered this adaptation
            
        Returns:
            New AdaptiveRewardBaseline instance with adapted value
        """
        # Build new history with current state prepended
        new_history = (
            (event_description, self.current_value),
        ) + self.adaptation_history
        
        return AdaptiveRewardBaseline(
            baseline_id=self.baseline_id,
            domain=self.domain,
            current_value=new_value,
            revision=self.revision + 1,
            adaptation_history=new_history,
            initial_value=self.initial_value,
            adaptation_rate=self.adaptation_rate,
            last_adaptation_event=event_description,
            confidence=self.confidence * 0.95,  # slight confidence reduction due to shift
            uncertainty=1.0 - (self.confidence * 0.95),
            context_signature=self.context_signature,
            provenance=self.provenance,
        )
    
    def adjust_rate(self, new_rate: float) -> AdaptiveRewardBaseline:
        """
        Create a new baseline instance with adjusted adaptation rate.
        
        Args:
            new_rate: New adaptation rate (0.0 to 1.0)
            
        Returns:
            New AdaptiveRewardBaseline instance with updated rate
        """
        return AdaptiveRewardBaseline(
            baseline_id=self.baseline_id,
            domain=self.domain,
            current_value=self.current_value,
            revision=self.revision + 1,
            adaptation_history=self.adaptation_history,
            initial_value=self.initial_value,
            adaptation_rate=new_rate,
            last_adaptation_event=self.last_adaptation_event,
            confidence=self.confidence,
            uncertainty=self.uncertainty,
            context_signature=self.context_signature,
            provenance=self.provenance,
        )
    
    def apply_offset(self, offset: float) -> AdaptiveRewardBaseline:
        """
        Create a new baseline instance with value adjusted by offset.
        
        Args:
            offset: Value to add to current baseline
            
        Returns:
            New AdaptiveRewardBaseline instance with offset value
        """
        return self.adapt_to_new_value(
            new_value=self.current_value + offset,
            event_description=f"offset_adjustment_{offset:+.3f}",
        )
    
    @property
    def is_static(self) -> bool:
        """Check if baseline has zero adaptation rate (never changes)."""
        return self.adaptation_rate == 0.0
    
    @property
    def is_fully_adaptive(self) -> bool:
        """Check if baseline has maximum adaptation rate."""
        return self.adaptation_rate >= 1.0


@dataclass(frozen=True)
class BaselineDomain:
    """
    Semantic domain specification for baselines.
    
    Defines the semantic categories for which baselines can be established.
    Each domain represents a different aspect of reward interpretation.
    """
    
    # Canonical domain identifiers
    REWARD: str = "reward"
    """General reward expectation baseline."""
    
    EFFORT: str = "effort"
    """Expected resource expenditure baseline."""
    
    QUALITY: str = "quality"
    """Expected outcome quality baseline."""
    
    LATENCY: str = "latency"
    """Expected completion time baseline."""
    
    COMPLEXITY: str = "complexity"
    """Expected task complexity baseline."""
    
    UNCERTAINTY: str = "uncertainty"
    """Expected uncertainty level baseline."""
    
    @classmethod
    def all_domains(cls) -> Tuple[str, ...]:
        """Return all canonical domain identifiers."""
        return (
            cls.REWARD,
            cls.EFFORT,
            cls.QUALITY,
            cls.LATENCY,
            cls.COMPLEXITY,
            cls.UNCERTAINTY,
        )