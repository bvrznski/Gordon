# Value Integration Module for Phase 4.10.3
# ==================================================================================================

"""
Value integration computes overall semantic value from benefits, costs,
constraints, confidence, and uncertainty.

Unlike learning systems, this module only produces semantic valuation - it never
modifies policies or performs adaptation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# VALUE INTEGRATION RESULT
# =============================================================================

@dataclass(frozen=True)
class ValueIntegrationResult:
    """
    Result of value integration operation.
    
    Integrates benefits, costs, constraints, confidence, and uncertainty into
    a comprehensive semantic value assessment.
    
    PROPERTIES:
        • total_value: Integrated net value
        • benefit_component: Sum of all benefits
        • cost_component: Sum of all costs
        • constraint_adjustment: Penalty from constraints
        • confidence_component: Value adjustment from confidence
        • uncertainty_penalty: Penalty from uncertainty
    
    INVARIANTS:
        • All components remain inspectable (never collapsed)
        • Trace is preserved for provenance
        • Results are immutable
    """
    
    total_value: float
    """Net integrated value."""
    
    benefit_component: float = 0.0
    """Sum of all benefit contributions."""
    
    cost_component: float = 0.0
    """Sum of all cost contributions."""
    
    constraint_adjustment: float = 0.0
    """Adjustment from constraints."""
    
    confidence_component: float = 1.0
    """Value adjustment from confidence level."""
    
    uncertainty_penalty: float = 0.0
    """Penalty applied for uncertainty."""
    
    evidence_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to all contributing evidence."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Processing trace for provenance."""
    
    @property
    def net_value(self) -> float:
        """Return the net integrated value."""
        return self.total_value
    
    @classmethod
    def zero(cls) -> ValueIntegrationResult:
        """Create a zero-value integration result."""
        return cls(
            total_value=0.0,
            benefit_component=0.0,
            cost_component=0.0,
            constraint_adjustment=0.0,
            confidence_component=1.0,
            uncertainty_penalty=0.0,
        )


# =============================================================================
# VALUE INTEGRATION POLICY
# =============================================================================

@dataclass(frozen=True)
class ValueIntegrationPolicy:
    """
    Policy for value integration operations.
    
    Specifies how benefits, costs, constraints, confidence, and uncertainty
    are combined into overall semantic value.
    
    PROPERTIES:
        • benefit_weight: Weight for benefit component
        • cost_weight: Weight for cost component (typically > 0)
        • constraint_penalty: Penalty factor for unmet constraints
        • confidence_scaling: How much confidence affects final value
        • uncertainty_scaling: How much uncertainty reduces final value
    
    INVARIANTS:
        • Policy is immutable
        • Weights must be non-negative
    """
    
    benefit_weight: float = 1.0
    """Weight for benefit component (>= 0)."""
    
    cost_weight: float = 1.0
    """Weight for cost component (>= 0)."""
    
    constraint_penalty: float = 0.5
    """Penalty factor for unmet constraints (>= 0)."""
    
    confidence_scaling: float = 1.0
    """How much confidence scales final value (>= 0)."""
    
    uncertainty_scaling: float = 1.0
    """How much uncertainty reduces final value (>= 0)."""
    
    def __post_init__(self):
        if self.benefit_weight < 0:
            raise ValueError("benefit_weight must be non-negative")
        if self.cost_weight < 0:
            raise ValueError("cost_weight must be non-negative")


# =============================================================================
# VALUE INTEGRATOR
# =============================================================================

@dataclass(frozen=True)
class ValueIntegrator:
    """
    Integrates benefits, costs, constraints, confidence, and uncertainty.
    
    Computes overall semantic value by combining all valuation factors while
    preserving their individual contributions for traceability.
    
    VALUE INTEGRATION PROCESS:
        1. Aggregate benefit components
        2. Aggregate cost components  
        3. Apply constraint adjustments
        4. Scale by confidence
        5. Apply uncertainty penalty
    
    NOT RESPONSIBLE FOR:
        • Modifying system state
        • Learning or policy updates
        • Making executive decisions
    """
    
    policy: ValueIntegrationPolicy = field(default_factory=ValueIntegrationPolicy)
    
    def integrate(
        self,
        benefit_value: float,
        cost_value: float,
        constraint_adjustment: float = 0.0,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
        evidence_refs: Tuple[str, ...] = tuple(),
    ) -> ValueIntegrationResult:
        """
        Integrate all value components into net semantic value.
        
        Args:
            benefit_value: Total benefit contribution
            cost_value: Total cost contribution  
            constraint_adjustment: Penalty from unmet constraints
            confidence: Confidence level in valuation (0.0 to 1.0)
            uncertainty: Uncertainty about valuation (0.0 to 1.0)
            evidence_refs: References to contributing evidence
            
        Returns:
            ValueIntegrationResult with all components preserved
        """
        trace: Tuple[str, ...] = ("VALUE_INTEGRATION_START",)
        
        # Apply weights
        weighted_benefit = benefit_value * self.policy.benefit_weight
        weighted_cost = cost_value * self.policy.cost_weight
        
        trace += ("WEIGHTED_COMPONENTS",)
        
        # Compute net before adjustments
        net_before_adjustments = weighted_benefit - weighted_cost
        
        # Apply constraint adjustment (always negative or zero)
        adjusted_value = net_before_adjustments + constraint_adjustment
        
        trace += ("CONSTRAINT_ADJUSTMENT_APPLIED",)
        
        # Apply confidence scaling
        confidence_factor = self._compute_confidence_factor(confidence)
        confident_value = adjusted_value * confidence_factor
        
        trace += ("CONFIDENCE_SCALING_APPLIED",)
        
        # Apply uncertainty penalty (reduces value magnitude)
        uncertainty_penalty = self._compute_uncertainty_penalty(uncertainty)
        final_value = confident_value - uncertainty_penalty
        
        trace += ("UNCERTAINTY_PENALTY_APPLIED", "VALUE_INTEGRATION_COMPLETE")
        
        return ValueIntegrationResult(
            total_value=final_value,
            benefit_component=weighted_benefit,
            cost_component=weighted_cost,
            constraint_adjustment=constraint_adjustment,
            confidence_component=confidence_factor,
            uncertainty_penalty=uncertainty_penalty,
            evidence_refs=evidence_refs,
            trace=trace,
        )
    
    def _compute_confidence_factor(self, confidence: float) -> float:
        """Compute scaling factor from confidence level."""
        # High confidence = 1.0, low confidence = less than 1.0
        return max(0.5, confidence)
    
    def _compute_uncertainty_penalty(self, uncertainty: float) -> float:
        """Compute penalty from uncertainty level."""
        # Higher uncertainty = larger penalty (reduces absolute value)
        if uncertainty <= 0:
            return 0.0
        
        # Penalty grows with uncertainty but is capped
        return uncertainty * 0.5


# =============================================================================
# MIXED VALUE REPRESENTATION
# =============================================================================

@dataclass(frozen=True)
class MixedValue:
    """
    Represents a value that has both positive and negative components.
    
    Unlike scalar values, mixed value preserves the dual nature of the valuation
    for downstream inspection and decision making.
    
    PROPERTIES:
        • positive_component: Positive contribution
        • negative_component: Negative contribution  
        • net_value: Net result (positive - negative)
        • ambiguity: Whether the valence is unclear
    
    INVARIANTS:
        • Both components are always preserved
        • Net value is computed, not stored
    """
    
    positive_component: float = 0.0
    """Positive contribution to value."""
    
    negative_component: float = 0.0
    """Negative contribution to value."""
    
    ambiguity: bool = False
    """Whether the overall valence is ambiguous."""
    
    @property
    def net_value(self) -> float:
        """Net value (positive - negative)."""
        return self.positive_component - self.negative_component
    
    @classmethod
    def from_values(cls, positive: float, negative: float) -> "MixedValue":
        """Create mixed value from positive and negative components."""
        return cls(positive_component=positive, negative_component=negative)
    
    @property
    def is_positive(self) -> bool:
        """Check if net value is positive."""
        return self.net_value > 0
    
    @property
    def is_negative(self) -> bool:
        """Check if net value is negative."""
        return self.net_value < 0
    
    @property
    def is_neutral(self) -> bool:
        """Check if net value is approximately zero."""
        return abs(self.net_value) < 0.01


@dataclass(frozen=True)
class CompositeValueIntegrationResult(ValueIntegrationResult):
    """
    Extended result that includes mixed value representation.
    
    Preserves both the scalar net value and detailed decomposition
    of positive/negative contributions.
    
    PROPERTIES:
        • Inherits all ValueIntegrationResult properties
        • mixed_value: Full mixed value representation
    
    NOT RESPONSIBLE FOR:
        • Modifying system state
        • Making decisions
    """
    
    mixed_value: MixedValue = field(default_factory=MixedValue)
    """Full mixed value representation with both components."""