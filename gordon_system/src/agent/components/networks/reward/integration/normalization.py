# Reward Normalization Module for Phase 4.10.3
# ==================================================================================================

"""
Reward normalization converts reward values to canonical representations.

Normalization preserves semantic meaning while ensuring consistent representation
across the system. It never changes the underlying valuation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class NormalizationResult:
    """
    Result of reward normalization operation.
    
    PROPERTIES:
        • normalized_value: Value in canonical scale
        • original_value: Original pre-normalization value
        • scaling_factor: Factor applied during normalization
        • metadata: Additional information about normalization
    
    INVARIANTS:
        • Normalization is deterministic
        • Trace is preserved for provenance
    """
    
    normalized_value: float
    """Value in canonical scale."""
    
    original_value: float = 0.0
    """Original pre-normalization value."""
    
    scaling_factor: float = 1.0
    """Factor applied during normalization."""
    
    metadata: Tuple[str, ...] = field(default_factory=tuple)
    """Additional information about normalization."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Processing trace for provenance."""


@dataclass(frozen=True)
class NormalizationPolicy:
    """
    Policy for reward value normalization.
    
    Specifies how values are scaled to canonical representations while
    preserving their semantic meaning.
    
    PROPERTIES:
        • min_value: Minimum of canonical scale
        • max_value: Maximum of canonical scale
        • preserve_sign: Whether sign must be preserved
    
    INVARIANTS:
        • Policy is immutable
        • Min < Max
    """
    
    min_value: float = -1.0
    """Minimum of canonical scale."""
    
    max_value: float = 1.0
    """Maximum of canonical scale."""
    
    preserve_sign: bool = True
    """Whether sign must be preserved during normalization."""
    
    def __post_init__(self):
        if self.min_value >= self.max_value:
            raise ValueError("min_value must be less than max_value")


@dataclass(frozen=True)
class RewardNormalizer:
    """
    Normalizes reward values to canonical representation.
    
    Converts raw reward estimates to consistent scale while preserving
    semantic meaning and traceability.
    
    NOT RESPONSIBLE FOR:
        • Modifying system state
        • Making decisions
        • Learning or policy updates
    """
    
    policy: NormalizationPolicy = field(default_factory=NormalizationPolicy)
    
    def normalize(self, value: float) -> NormalizationResult:
        """
        Normalize a reward value to canonical scale.
        
        Args:
            value: Raw reward value to normalize
            
        Returns:
            NormalizationResult with normalized value and metadata
        """
        trace: Tuple[str, ...] = ("NORMALIZATION_START",)
        
        # Get policy bounds
        min_val = self.policy.min_value
        max_val = self.policy.max_value
        
        # Handle edge cases
        if value == 0:
            result = NormalizationResult(
                normalized_value=0.0,
                original_value=value,
                scaling_factor=1.0,
                trace=trace + ("ZERO_VALUE", "NORMALIZATION_COMPLETE"),
            )
            return result
        
        # Determine original range (assume [-inf, inf] for now)
        # In practice, this would use domain-specific knowledge
        original_min = -10.0  # Assumed minimum
        original_max = 10.0   # Assumed maximum
        
        trace += ("RANGE_DETERMINED",)
        
        # Apply normalization formula
        if original_max == original_min:
            scaling_factor = 1.0
            normalized = value
        else:
            # Linear mapping to canonical range
            t = (value - original_min) / (original_max - original_min)
            scaling_factor = (max_val - min_val) / (original_max - original_min)
            normalized = min_val + t * (max_val - min_val)
        
        trace += ("VALUE_NORMALIZED", "NORMALIZATION_COMPLETE")
        
        return NormalizationResult(
            normalized_value=normalized,
            original_value=value,
            scaling_factor=scaling_factor,
            metadata=(
                f"original_range:[{original_min},{original_max}]",
                f"canonical_range:[{min_val},{max_val}]",
            ),
            trace=trace,
        )
    
    def normalize_batch(self, values: Tuple[float, ...]) -> Tuple[NormalizationResult, ...]:
        """Normalize a batch of reward values."""
        return tuple(self.normalize(v) for v in values)
    
    def denormalize(self, normalized_value: float) -> NormalizationResult:
        """
        Denormalize a canonical value back to original scale.
        
        Args:
            normalized_value: Value in canonical scale
            
        Returns:
            NormalizationResult with denormalized value
        """
        trace: Tuple[str, ...] = ("DENORMALIZATION_START",)
        
        # Reverse the normalization formula
        min_val = self.policy.min_value
        max_val = self.policy.max_value
        
        original_min = -10.0  # Assumed minimum (must match normalize)
        original_max = 10.0   # Assumed maximum (must match normalize)
        
        if max_val == min_val:
            result = NormalizationResult(
                normalized_value=normalized_value,
                original_value=original_min,
                scaling_factor=1.0,
                trace=trace + ("DENORMALIZATION_COMPLETE",),
            )
            return result
        
        # Reverse mapping
        t = (normalized_value - min_val) / (max_val - min_val)
        denormalized = original_min + t * (original_max - original_min)
        
        trace += ("VALUE_DENORMALIZED", "DENORMALIZATION_COMPLETE")
        
        return NormalizationResult(
            normalized_value=normalized_value,
            original_value=denormalized,
            scaling_factor=(max_val - min_val) / (original_max - original_min),
            metadata=(
                f"canonical_range:[{min_val},{max_val}]",
                f"original_range:[{original_min},{original_max}]",
            ),
            trace=trace,
        )


@dataclass(frozen=True)
class RewardScale:
    """
    Represents a canonical reward scale.
    
    Defines the range and semantics of normalized reward values.
    
    PROPERTIES:
        • min_value: Minimum reward value (most negative)
        • max_value: Maximum reward value (most positive)
        • zero_point: Neutral point on the scale
    
    COMMON SCALES:
        • [-1, 1]: Standard bounded scale
        • [0, 1]: Non-negative scale
        • [-10, 10]: Extended range scale
    """
    
    min_value: float = -1.0
    """Minimum reward value."""
    
    max_value: float = 1.0
    """Maximum reward value."""
    
    zero_point: float = 0.0
    """Neutral point on the scale."""
    
    @property
    def range(self) -> float:
        """Size of the scale range."""
        return self.max_value - self.min_value
    
    @classmethod
    def standard(cls) -> "RewardScale":
        """Create standard [-1, 1] scale."""
        return cls(min_value=-1.0, max_value=1.0, zero_point=0.0)
    
    @classmethod
    def non_negative(cls) -> "RewardScale":
        """Create [0, 1] scale."""
        return cls(min_value=0.0, max_value=1.0, zero_point=0.5)