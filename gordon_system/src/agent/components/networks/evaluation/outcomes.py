# Gordon Cognitive Architecture - Phase 4.5.5
# Action Evaluation Expected Outcomes
# ===================================

"""
Expected Outcome Analysis type definitions.

This module defines types for analyzing expected outcomes of Action Candidates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# OUTCOME EFFECTIVENESS
# =============================================================================

@dataclass(frozen=True, slots=True)
class OutcomeEffectiveness:
    """
    Assessment of how effective an outcome is expected to be.
    
    PROPERTIES:
        - effectiveness_score: How effective the outcome will be (0.0 to 1.0)
        - intended_effect_coverage: Portion of intended effects achieved
        - side_effect_coverage: Unintended but accepted effects
        - quality_of_outcome: Overall quality assessment
    """
    
    effectiveness_score: float = 0.5
    """How effective the outcome will be (0.0 to 1.0)."""
    
    intended_effect_coverage: float = 0.5
    """Portion of intended effects achieved (0.0 to 1.0)."""
    
    side_effect_coverage: float = 0.2
    """Unintended but accepted effects (0.0 to 1.0)."""
    
    quality_of_outcome: float = 0.5
    """Overall quality assessment (0.0 to 1.0)."""
    
    @classmethod
    def high_effectiveness(cls) -> OutcomeEffectiveness:
        """Create a high effectiveness assessment."""
        return cls(
            effectiveness_score=0.9,
            intended_effect_coverage=0.95,
            side_effect_coverage=0.3,
            quality_of_outcome=0.85,
        )
    
    @classmethod
    def low_effectiveness(cls) -> OutcomeEffectiveness:
        """Create a low effectiveness assessment."""
        return cls(
            effectiveness_score=0.2,
            intended_effect_coverage=0.15,
            side_effect_coverage=0.6,
            quality_of_outcome=0.3,
        )


# =============================================================================
# OUTCOME SIDE EFFECTS
# =============================================================================

@dataclass(frozen=True, slots=True)
class OutcomeSideEffects:
    """
    Assessment of side effects from an Action.
    
    PROPERTIES:
        - positive_side_effects: Beneficial side effects (count or score)
        - negative_side_effects: Harmful side effects (count or score)
        - detectability: How likely side effects are to be detected
        - manageability: How manageable the side effects are
    """
    
    positive_side_effects: Tuple[str, ...] = field(default_factory=tuple)
    """Beneficial side effects."""
    
    negative_side_effects: Tuple[str, ...] = field(default_factory=tuple)
    """Harmful side effects."""
    
    detectability: float = 0.5
    """How likely side effects are to be detected (0.0 to 1.0)."""
    
    manageability: float = 0.5
    """How manageable the side effects are (0.0 to 1.0)."""
    
    @classmethod
    def minimal_side_effects(cls) -> OutcomeSideEffects:
        """Create an assessment with minimal side effects."""
        return cls(
            positive_side_effects=(),
            negative_side_effects=(),
            detectability=0.9,
            manageability=0.95,
        )
    
    @classmethod
    def significant_positive_side_effects(cls, effects: Tuple[str, ...]) -> OutcomeSideEffects:
        """Create an assessment with positive side effects."""
        return cls(
            positive_side_effects=effects,
            negative_side_effects=(),
            detectability=0.8,
            manageability=0.9,
        )


# =============================================================================
# EXPECTED OUTCOMES
# =============================================================================

@dataclass(frozen=True, slots=True)
class ExpectedOutcomes:
    """
    Summary of expected outcomes for an Action Candidate.
    
    PROPERTIES:
        - primary_effects: Primary intended effects
        - secondary_effects: Secondary intended effects
        - side_effects: Side effect assessment
        - effectiveness: Effectiveness assessment
        - persistence: How long effects last
        - reversibility: Can effects be reversed?
    """
    
    primary_effects: Tuple[str, ...] = field(default_factory=tuple)
    """Primary intended effects."""
    
    secondary_effects: Tuple[str, ...] = field(default_factory=tuple)
    """Secondary intended effects."""
    
    side_effects: OutcomeSideEffects = field(default_factory=OutcomeSideEffects)
    """Side effect assessment."""
    
    effectiveness: OutcomeEffectiveness = field(default_factory=OutcomeEffectiveness)
    """Effectiveness assessment."""
    
    persistence: str = "unknown"
    """How long effects last: 'temporary', 'persistent', 'permanent', 'unknown'."""
    
    reversibility: bool = False
    """Can effects be reversed?"""
    
    @classmethod
    def positive_outcomes(
        cls,
        primary_effects: Tuple[str, ...],
        secondary_effects: Tuple[str, ...] = (),
    ) -> ExpectedOutcomes:
        """Create expected outcomes with positive assessment."""
        return cls(
            primary_effects=primary_effects,
            secondary_effects=secondary_effects,
            side_effects=OutcomeSideEffects.minimal_side_effects(),
            effectiveness=OutcomeEffectiveness.high_effectiveness(),
            persistence="persistent",
            reversibility=False,
        )
    
    @classmethod
    def negative_outcomes(cls, effects: Tuple[str, ...]) -> ExpectedOutcomes:
        """Create expected outcomes with negative assessment."""
        return cls(
            primary_effects=effects,
            secondary_effects=(),
            side_effects=OutcomeSideEffects.minimal_side_effects(),
            effectiveness=OutcomeEffectiveness.low_effectiveness(),
            persistence="temporary",
            reversibility=True,
        )


# =============================================================================
# EXPECTED BENEFIT
# =============================================================================

@dataclass(frozen=True, slots=True)
class ExpectedBenefit:
    """
    Assessment of expected benefit from an Action.
    
    PROPERTIES:
        - overall_benefit: Total expected benefit score (0.0 to 1.0)
        - direct_benefit: Direct benefit to primary objectives
        - indirect_benefit: Indirect benefits to secondary concerns
        - long_term_value: Expected long-term value
    """
    
    overall_benefit: float = 0.5
    """Total expected benefit score (0.0 to 1.0)."""
    
    direct_benefit: float = 0.3
    """Direct benefit to primary objectives (0.0 to 1.0)."""
    
    indirect_benefit: float = 0.2
    """Indirect benefits to secondary concerns (0.0 to 1.0)."""
    
    long_term_value: float = 0.4
    """Expected long-term value (0.0 to 1.0)."""
    
    @classmethod
    def high_benefit(cls) -> ExpectedBenefit:
        """Create a high benefit assessment."""
        return cls(
            overall_benefit=0.9,
            direct_benefit=0.85,
            indirect_benefit=0.75,
            long_term_value=0.95,
        )
    
    @classmethod
    def low_benefit(cls) -> ExpectedBenefit:
        """Create a low benefit assessment."""
        return cls(
            overall_benefit=0.2,
            direct_benefit=0.1,
            indirect_benefit=0.3,
            long_term_value=0.25,
        )


# =============================================================================
# EXPECTED RISK
# =============================================================================

@dataclass(frozen=True, slots=True)
class ExpectedRisk:
    """
    Assessment of expected risk from an Action.
    
    PROPERTIES:
        - overall_risk: Total expected risk score (0.0 to 1.0)
        - failure_probability: Probability of failure (0.0 to 1.0)
        - impact_severity: Severity if failure occurs (0.0 to 1.0)
        - detectability: How detectable failures are (0.0 to 1.0)
    """
    
    overall_risk: float = 0.5
    """Total expected risk score (0.0 to 1.0)."""
    
    failure_probability: float = 0.3
    """Probability of failure (0.0 to 1.0)."""
    
    impact_severity: float = 0.6
    """Severity if failure occurs (0.0 to 1.0)."""
    
    detectability: float = 0.5
    """How detectable failures are (0.0 to 1.0)."""
    
    @classmethod
    def high_risk(cls) -> ExpectedRisk:
        """Create a high risk assessment."""
        return cls(
            overall_risk=0.8,
            failure_probability=0.6,
            impact_severity=0.9,
            detectability=0.3,
        )
    
    @classmethod
    def low_risk(cls) -> ExpectedRisk:
        """Create a low risk assessment."""
        return cls(
            overall_risk=0.2,
            failure_probability=0.1,
            impact_severity=0.3,
            detectability=0.9,
        )