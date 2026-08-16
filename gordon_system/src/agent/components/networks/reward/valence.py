# Reward Network - Valence Estimator
# ====================================

"""
Valence estimator for reward evaluation.

Valence represents the qualitative direction of a reward estimate (positive,
negative, neutral, mixed, or unknown). Valence is independent from magnitude.

VALENCE LAWS:
    VALENCE-LAW-001: Every RewardEstimate possesses explicit Valence.
    VALENCE-LAW-002: Valence remains independent from magnitude.
    VALENCE-LAW-003: Valence remains independent from confidence.
    VALENCE-LAW-004: Valence remains independent from uncertainty.
    VALENCE-LAW-005: Mixed valence remains representable.
    VALENCE-LAW-006: Unknown valence remains representable.
    VALENCE-LAW-007: Valence estimates preserve provenance.
    VALENCE-LAW-008: Valence estimation remains deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class Valence:
    """
    Qualitative direction of a reward estimate.
    
    Valence represents the semantic direction of benefit/cost evaluation
    without implying any specific magnitude or certainty.
    
    VALENCE KINDS:
        • positive: Outcome is beneficial
        • negative: Outcome is costly  
        • neutral: Outcome has no clear valence
        • mixed: Outcome has both positive and negative aspects
        • unknown: Valence cannot be determined from available information
        
    VALIENCE INVARIANTS:
        • Valence is always explicit (never inferred)
        • Valence is independent of magnitude
        • Valence is independent of confidence
        • Valence is independent of uncertainty
    """
    
    kind: str  # ValenceKind.*
    """The valence direction."""
    
    @property
    def is_positive(self) -> bool:
        """Check if this is positive valence."""
        return self.kind == "positive"
    
    @property
    def is_negative(self) -> bool:
        """Check if this is negative valence."""
        return self.kind == "negative"
    
    @property
    def is_neutral(self) -> bool:
        """Check if this is neutral valence."""
        return self.kind == "neutral"
    
    @property
    def is_mixed(self) -> bool:
        """Check if this is mixed valence."""
        return self.kind == "mixed"
    
    @property
    def is_unknown(self) -> bool:
        """Check if this is unknown valence."""
        return self.kind == "unknown"


@dataclass(frozen=True)
class ValenceEstimate:
    """
    Complete valence assessment for a reward evaluation.
    
    Aggregates valence from multiple sources while preserving their
    individual contributions and evidence.
    
    PROPERTIES:
        • primary_valence: The dominant valence direction
        • contributing_valences: Individual source valences
        • confidence: Confidence in the valence assignment
        
    NOT RESPONSIBLE FOR:
        • Making executive decisions based on valence
        • Modifying outcomes or beliefs
        • Updating reward policies
    """
    
    primary_valence: Valence
    """The dominant valence direction."""
    
    contributing_valences: Tuple[Valence, ...] = field(default_factory=tuple)
    """Individual source valences (for traceability)."""
    
    confidence: float = 1.0
    """Confidence in the valence assignment."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this valence assignment."""
    
    provenance: Optional[str] = None
    """Provenance reference for this estimation method."""
    
    @property
    def is_determined(self) -> bool:
        """Check if valence was determined (not unknown)."""
        return self.primary_valence.kind != "unknown"