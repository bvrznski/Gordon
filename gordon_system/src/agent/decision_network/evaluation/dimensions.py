# Gordon Cognitive Architecture - Phase 4.5.5
# Action Evaluation Dimensions
# ============================

"""
Action Evaluation Dimension Result type definitions.

This module defines the per-dimension assessment types used in evaluation.
Each dimension is evaluated independently and produces its own result type.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# DIMENSION RESULT BASE TYPES
# =============================================================================

DimensionName = str
"""Identifier for an evaluation dimension."""


@dataclass(frozen=True, slots=True)
class DimensionResult:
    """
    Base class for dimension results.
    
    PROPERTIES:
        • dimension_name: Name of the evaluated dimension
        • score: Numerical score (0.0 to 1.0) where higher is better
        • confidence: Confidence in this assessment (0.0 to 1.0)
        • uncertainty: Uncertainty about this assessment (0.0 to 1.0)
    """
    
    dimension_name: DimensionName
    """Name of the evaluated dimension."""
    
    score: float = 0.5
    """Numerical score (0.0 to 1.0) where higher is better."""
    
    confidence: float = 0.5
    """Confidence in this assessment (0.0 to 1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty about this assessment (0.0 to 1.0)."""

    @classmethod
    def high(cls, dimension_name: DimensionName) -> DimensionResult:
        """Create a high-scoring result."""
        return cls(
            dimension_name=dimension_name,
            score=0.8,
            confidence=0.7,
            uncertainty=0.2,
        )
    
    @classmethod
    def medium(cls, dimension_name: DimensionName) -> DimensionResult:
        """Create a medium-scoring result."""
        return cls(
            dimension_name=dimension_name,
            score=0.5,
            confidence=0.5,
            uncertainty=0.4,
        )
    
    @classmethod
    def low(cls, dimension_name: DimensionName) -> DimensionResult:
        """Create a low-scoring result."""
        return cls(
            dimension_name=dimension_name,
            score=0.2,
            confidence=0.6,
            uncertainty=0.3,
        )


# =============================================================================
# FEASIBILITY DIMENSION
# =============================================================================

@dataclass(frozen=True, slots=True)
class FeasibilityResult(DimensionResult):
    """
    Result for the Feasibility dimension.
    
    Feasibility determines whether an Action is realistically performable.
    
    CONSIDERS:
        • Capability availability (do we have the tools?)
        • Prerequisite satisfaction (are preconditions met?)
        • Dependency completeness (are dependencies satisfied?)
        • Authority sufficiency (do we have permission?)
        • Resource availability (semantic: do we need them?)
        • Temporal validity (is timing right?)
        • Environmental assumptions (do assumptions hold?)
    
    PROPERTIES:
        • overall_feasibility: Overall feasibility score
        • capability_score: Capability availability assessment
        • prerequisite_score: Prerequisite satisfaction assessment
        • dependency_score: Dependency completeness assessment
        • authority_score: Authority sufficiency assessment
        • temporal_validity: Temporal validity score
    """
    
    overall_feasibility: float = 0.5
    """Overall feasibility score (0.0 to 1.0)."""
    
    capability_score: float = 0.5
    """Capability availability assessment (0.0 to 1.0)."""
    
    prerequisite_score: float = 0.5
    """Prerequisite satisfaction assessment (0.0 to 1.0)."""
    
    dependency_score: float = 0.5
    """Dependency completeness assessment (0.0 to 1.0)."""
    
    authority_score: float = 0.5
    """Authority sufficiency assessment (0.0 to 1.0)."""
    
    temporal_validity: float = 0.5
    """Temporal validity score (0.0 to 1.0)."""
    
    @classmethod
    def fully_feasible(cls) -> FeasibilityResult:
        """Create a fully feasible assessment."""
        return cls(
            dimension_name="feasibility",
            overall_feasibility=1.0,
            capability_score=1.0,
            prerequisite_score=1.0,
            dependency_score=1.0,
            authority_score=1.0,
            temporal_validity=1.0,
            confidence=0.9,
            uncertainty=0.1,
        )
    
    @classmethod
    def not_feasible(cls, reasons: Tuple[str, ...] = ()) -> FeasibilityResult:
        """Create a not feasible assessment."""
        return cls(
            dimension_name="feasibility",
            overall_feasibility=0.0,
            capability_score=0.0,
            prerequisite_score=0.0,
            dependency_score=0.0,
            authority_score=0.0,
            temporal_validity=0.0,
            confidence=0.8,
            uncertainty=0.2,
        )


# =============================================================================
# SUITABILITY DIMENSION
# =============================================================================

@dataclass(frozen=True, slots=True)
class SuitabilityResult(DimensionResult):
    """
    Result for the Suitability dimension.
    
    Suitability evaluates how appropriate an Action is for the current request.
    
    CONSIDERS:
        • Match to target purpose
        • Fit with context
        • Appropriateness of approach
    
    PROPERTIES:
        • overall_suitability: Overall suitability score
        • purpose_match: How well it matches the intended purpose
        • context_fit: How well it fits current context
        • approach_appropriateness: Assessment of the chosen approach
    """
    
    overall_suitability: float = 0.5
    """Overall suitability score (0.0 to 1.0)."""
    
    purpose_match: float = 0.5
    """How well it matches the intended purpose (0.0 to 1.0)."""
    
    context_fit: float = 0.5
    """How well it fits current context (0.0 to 1.0)."""
    
    approach_appropriateness: float = 0.5
    """Assessment of the chosen approach (0.0 to 1.0)."""
    
    @classmethod
    def highly_suitable(cls) -> SuitabilityResult:
        """Create a highly suitable assessment."""
        return cls(
            dimension_name="suitability",
            overall_suitability=1.0,
            purpose_match=1.0,
            context_fit=1.0,
            approach_appropriateness=1.0,
            confidence=0.85,
            uncertainty=0.15,
        )
    
    @classmethod
    def unsuitable(cls) -> SuitabilityResult:
        """Create an unsuitable assessment."""
        return cls(
            dimension_name="suitability",
            overall_suitability=0.0,
            purpose_match=0.0,
            context_fit=0.0,
            approach_appropriateness=0.0,
            confidence=0.9,
            uncertainty=0.1,
        )


# =============================================================================
# ADEQUACY DIMENSION
# =============================================================================

@dataclass(frozen=True, slots=True)
class AdequacyResult(DimensionResult):
    """
    Result for the Adequacy dimension.
    
    Adequacy determines whether an Action sufficiently satisfies the intended
    purpose. Partial adequacy is supported.
    
    CONSIDERS:
        • Completeness of effect coverage
        • Depth of solution
        • Coverage of requirements
    
    PROPERTIES:
        • overall_adequacy: Overall adequacy score
        • effect_coverage: How much of the desired effect is covered
        • requirement_satisfaction: Degree to which requirements are met
        • partial_adequacy: Whether this provides partial satisfaction
    """
    
    overall_adequacy: float = 0.5
    """Overall adequacy score (0.0 to 1.0)."""
    
    effect_coverage: float = 0.5
    """How much of the desired effect is covered (0.0 to 1.0)."""
    
    requirement_satisfaction: float = 0.5
    """Degree to which requirements are met (0.0 to 1.0)."""
    
    partial_adequacy: bool = False
    """Whether this provides partial satisfaction."""
    
    @classmethod
    def fully_adequate(cls) -> AdequacyResult:
        """Create a fully adequate assessment."""
        return cls(
            dimension_name="adequacy",
            overall_adequacy=1.0,
            effect_coverage=1.0,
            requirement_satisfaction=1.0,
            partial_adequacy=False,
            confidence=0.85,
            uncertainty=0.15,
        )
    
    @classmethod
    def partially_adequate(cls, coverage: float = 0.5) -> AdequacyResult:
        """Create a partially adequate assessment."""
        return cls(
            dimension_name="adequacy",
            overall_adequacy=coverage,
            effect_coverage=coverage,
            requirement_satisfaction=coverage,
            partial_adequacy=True,
            confidence=0.6,
            uncertainty=0.3,
        )
    
    @classmethod
    def inadequate(cls) -> AdequacyResult:
        """Create an inadequate assessment."""
        return cls(
            dimension_name="adequacy",
            overall_adequacy=0.0,
            effect_coverage=0.0,
            requirement_satisfaction=0.0,
            partial_adequacy=False,
            confidence=0.85,
            uncertainty=0.15,
        )


# =============================================================================
# COMPATIBILITY DIMENSION
# =============================================================================

@dataclass(frozen=True, slots=True)
class CompatibilityResult(DimensionResult):
    """
    Result for the Compatibility dimension.
    
    Compatibility evaluates compatibility with goals, strategies, plans,
    policies, security requirements, workspace state, etc.
    
    CONSIDERS:
        • Goal alignment
        • Strategy alignment
        • Plan compatibility
        • Commitment compatibility
        • Policy compliance
        • Security compliance
        • Workspace compatibility
        • Executive state compatibility
    
    PROPERTIES:
        • overall_compatibility: Overall compatibility score
        • goal_alignment: Alignment with active goals
        • strategy_alignment: Alignment with active strategies
        • plan_compatibility: Compatibility with current plan
        • policy_compliance: Policy compliance level
        • security_compliance: Security compliance level
    """
    
    overall_compatibility: float = 0.5
    """Overall compatibility score (0.0 to 1.0)."""
    
    goal_alignment: float = 0.5
    """Alignment with active goals (0.0 to 1.0)."""
    
    strategy_alignment: float = 0.5
    """Alignment with active strategies (0.0 to 1.0)."""
    
    plan_compatibility: float = 0.5
    """Compatibility with current plan (0.0 to 1.0)."""
    
    policy_compliance: float = 0.5
    """Policy compliance level (0.0 to 1.0)."""
    
    security_compliance: float = 0.5
    """Security compliance level (0.0 to 1.0)."""
    
    @classmethod
    def fully_compatible(cls) -> CompatibilityResult:
        """Create a fully compatible assessment."""
        return cls(
            dimension_name="compatibility",
            overall_compatibility=1.0,
            goal_alignment=1.0,
            strategy_alignment=1.0,
            plan_compatibility=1.0,
            policy_compliance=1.0,
            security_compliance=1.0,
            confidence=0.9,
            uncertainty=0.1,
        )
    
    @classmethod
    def incompatible(cls, conflicts: Tuple[str, ...] = ()) -> CompatibilityResult:
        """Create an incompatible assessment."""
        return cls(
            dimension_name="compatibility",
            overall_compatibility=0.0,
            goal_alignment=0.0,
            strategy_alignment=0.0,
            plan_compatibility=0.0,
            policy_compliance=0.0,
            security_compliance=0.0,
            confidence=0.85,
            uncertainty=0.15,
        )


# =============================================================================
# COMPLETENESS DIMENSION
# =============================================================================

@dataclass(frozen=True, slots=True)
class CompletenessResult(DimensionResult):
    """
    Result for the Completeness dimension.
    
    Completeness determines whether an Action is well-formed with sufficient
    information to be evaluated and potentially executed.
    
    CONSIDERS:
        • Evidence quality
        • Assumption coverage
        • Constraint specification
        • Precondition completeness
    
    PROPERTIES:
        • overall_completeness: Overall completeness score
        • evidence_quality: Quality of supporting evidence
        • assumption_coverage: Coverage of assumptions
        • constraint_specification: Specification of constraints
        • precondition_satisfaction: Precondition clarity
    """
    
    overall_completeness: float = 0.5
    """Overall completeness score (0.0 to 1.0)."""
    
    evidence_quality: float = 0.5
    """Quality of supporting evidence (0.0 to 1.0)."""
    
    assumption_coverage: float = 0.5
    """Coverage of assumptions (0.0 to 1.0)."""
    
    constraint_specification: float = 0.5
    """Specification of constraints (0.0 to 1.0)."""
    
    precondition_satisfaction: float = 0.5
    """Precondition clarity (0.0 to 1.0)."""
    
    @classmethod
    def complete(cls) -> CompletenessResult:
        """Create a complete assessment."""
        return cls(
            dimension_name="completeness",
            overall_completeness=1.0,
            evidence_quality=1.0,
            assumption_coverage=1.0,
            constraint_specification=1.0,
            precondition_satisfaction=1.0,
            confidence=0.95,
            uncertainty=0.05,
        )
    
    @classmethod
    def incomplete(cls, gaps: Tuple[str, ...] = ()) -> CompletenessResult:
        """Create an incomplete assessment."""
        return cls(
            dimension_name="completeness",
            overall_completeness=0.3,
            evidence_quality=0.3,
            assumption_coverage=0.3,
            constraint_specification=0.3,
            precondition_satisfaction=0.3,
            confidence=0.4,
            uncertainty=0.5,
        )


# =============================================================================
# RISK DIMENSION
# =============================================================================

@dataclass(frozen=True, slots=True)
class RiskResult(DimensionResult):
    """
    Result for the Risk dimension.
    
    Risk assesses what could go wrong with an Action.
    
    CONSIDERS:
        • Failure modes
        • Error scenarios
        • Adverse outcomes
    
    PROPERTIES:
        • overall_risk: Overall risk score (0.0 to 1.0, higher = more risk)
        • failure_probability: Estimated probability of failure
        • impact_severity: Severity if failure occurs
        • detectability: How detectable failures are
    """
    
    overall_risk: float = 0.5
    """Overall risk score (0.0 to 1.0, higher = more risk)."""
    
    failure_probability: float = 0.25
    """Estimated probability of failure (0.0 to 1.0)."""
    
    impact_severity: float = 0.5
    """Severity if failure occurs (0.0 to 1.0)."""
    
    detectability: float = 0.5
    """How detectable failures are (0.0 to 1.0, higher = more detectable)."""
    
    @classmethod
    def low_risk(cls) -> RiskResult:
        """Create a low risk assessment."""
        return cls(
            dimension_name="risk",
            overall_risk=0.2,
            failure_probability=0.1,
            impact_severity=0.3,
            detectability=0.9,
            confidence=0.75,
            uncertainty=0.25,
        )
    
    @classmethod
    def high_risk(cls) -> RiskResult:
        """Create a high risk assessment."""
        return cls(
            dimension_name="risk",
            overall_risk=0.8,
            failure_probability=0.6,
            impact_severity=0.9,
            detectability=0.3,
            confidence=0.65,
            uncertainty=0.35,
        )
    
    @classmethod
    def risk_free(cls) -> RiskResult:
        """Create a risk-free assessment."""
        return cls(
            dimension_name="risk",
            overall_risk=0.0,
            failure_probability=0.0,
            impact_severity=0.0,
            detectability=1.0,
            confidence=0.9,
            uncertainty=0.1,
        )


# =============================================================================
# BENEFIT DIMENSION
# =============================================================================

@dataclass(frozen=True, slots=True)
class BenefitResult(DimensionResult):
    """
    Result for the Benefit dimension.
    
    Benefit assesses positive outcomes from an Action.
    
    CONSIDERS:
        • Primary benefits
        • Secondary benefits
        • Long-term benefits
    
    PROPERTIES:
        • overall_benefit: Overall benefit score (0.0 to 1.0)
        • primary_benefit: Primary expected benefit
        • secondary_benefit: Secondary expected benefit
        • long_term_value: Long-term value assessment
    """
    
    overall_benefit: float = 0.5
    """Overall benefit score (0.0 to 1.0)."""
    
    primary_benefit: float = 0.5
    """Primary expected benefit (0.0 to 1.0)."""
    
    secondary_benefit: float = 0.25
    """Secondary expected benefit (0.0 to 1.0)."""
    
    long_term_value: float = 0.3
    """Long-term value assessment (0.0 to 1.0)."""
    
    @classmethod
    def high_benefit(cls) -> BenefitResult:
        """Create a high benefit assessment."""
        return cls(
            dimension_name="benefit",
            overall_benefit=0.9,
            primary_benefit=0.95,
            secondary_benefit=0.85,
            long_term_value=0.9,
            confidence=0.75,
            uncertainty=0.25,
        )
    
    @classmethod
    def no_benefit(cls) -> BenefitResult:
        """Create a no benefit assessment."""
        return cls(
            dimension_name="benefit",
            overall_benefit=0.0,
            primary_benefit=0.0,
            secondary_benefit=0.0,
            long_term_value=0.0,
            confidence=0.85,
            uncertainty=0.15,
        )


# =============================================================================
# EXPECTED UTILITY DIMENSION
# =============================================================================

@dataclass(frozen=True, slots=True)
class ExpectedUtilityResult(DimensionResult):
    """
    Result for the Expected Utility dimension.
    
    Expected utility is the net expected value considering benefits minus risks.
    
    CONSIDERS:
        • Expected benefit
        • Expected cost
        • Probability-weighted outcomes
    
    PROPERTIES:
        • overall_expected_utility: Overall expected utility score (-1.0 to 1.0)
        • expected_benefit: Expected positive value
        • expected_cost: Expected negative value (costs, risks)
        • probability_weighted_value: Probability-weighted outcome
    """
    
    overall_expected_utility: float = 0.0
    """Overall expected utility (-1.0 to 1.0, higher is better)."""
    
    expected_benefit: float = 0.5
    """Expected positive value (0.0 to 1.0)."""
    
    expected_cost: float = 0.25
    """Expected negative value, costs, risks (0.0 to 1.0)."""
    
    probability_weighted_value: float = 0.375
    """Probability-weighted outcome (-1.0 to 1.0)."""
    
    @classmethod
    def positive_utility(cls) -> ExpectedUtilityResult:
        """Create a positive expected utility assessment."""
        return cls(
            dimension_name="expected_utility",
            overall_expected_utility=0.5,
            expected_benefit=0.8,
            expected_cost=0.3,
            probability_weighted_value=0.5,
            confidence=0.7,
            uncertainty=0.3,
        )
    
    @classmethod
    def negative_utility(cls) -> ExpectedUtilityResult:
        """Create a negative expected utility assessment."""
        return cls(
            dimension_name="expected_utility",
            overall_expected_utility=-0.4,
            expected_benefit=0.2,
            expected_cost=0.7,
            probability_weighted_value=-0.35,
            confidence=0.65,
            uncertainty=0.35,
        )
    
    @classmethod
    def neutral_utility(cls) -> ExpectedUtilityResult:
        """Create a neutral expected utility assessment."""
        return cls(
            dimension_name="expected_utility",
            overall_expected_utility=0.0,
            expected_benefit=0.5,
            expected_cost=0.5,
            probability_weighted_value=0.0,
            confidence=0.6,
            uncertainty=0.4,
        )


# =============================================================================
# REVERSIBILITY DIMENSION
# =============================================================================

@dataclass(frozen=True, slots=True)
class ReversibilityResult(DimensionResult):
    """
    Result for the Reversibility dimension.
    
    Reversibility determines whether an Action can be reversed and at what cost.
    
    CONSIDERS:
        • Whether reversal is possible
        • Cost of reversal
        • Time to reversal
    
    PROPERTIES:
        • overall_reversibility: Overall reversibility score (0.0 to 1.0)
        • reversible: Whether the action is reversible
        • reversal_cost: Expected cost to reverse
        • time_to_reverse: Estimated time to reverse
    """
    
    overall_reversibility: float = 0.5
    """Overall reversibility score (0.0 to 1.0, higher = more reversible)."""
    
    reversible: bool = False
    """Whether the action is reversible."""
    
    reversal_cost: float = 0.5
    """Expected cost to reverse (0.0 to 1.0, lower = easier)."""
    
    time_to_reverse: float = 0.5
    """Estimated time to reverse (0.0 to 1.0, higher = faster)."""
    
    @classmethod
    def fully_reversible(cls) -> ReversibilityResult:
        """Create a fully reversible assessment."""
        return cls(
            dimension_name="reversibility",
            overall_reversibility=1.0,
            reversible=True,
            reversal_cost=0.1,
            time_to_reverse=0.9,
            confidence=0.85,
            uncertainty=0.15,
        )
    
    @classmethod
    def irreversible(cls) -> ReversibilityResult:
        """Create an irreversible assessment."""
        return cls(
            dimension_name="reversibility",
            overall_reversibility=0.0,
            reversible=False,
            reversal_cost=1.0,
            time_to_reverse=0.0,
            confidence=0.95,
            uncertainty=0.05,
        )
    
    @classmethod
    def partially_reversible(cls, cost: float = 0.5) -> ReversibilityResult:
        """Create a partially reversible assessment."""
        return cls(
            dimension_name="reversibility",
            overall_reversibility=0.5,
            reversible=True,
            reversal_cost=cost,
            time_to_reverse=0.5,
            confidence=0.7,
            uncertainty=0.3,
        )


# =============================================================================
# PERSISTENCE DIMENSION
# =============================================================================

@dataclass(frozen=True, slots=True)
class PersistenceResult(DimensionResult):
    """
    Result for the Persistence dimension.
    
    Persistence estimates how long expected effects persist after an Action.
    
    CONSIDERS:
        • Temporary vs persistent effects
        • Duration of effects
        • Decay rate
    
    PROPERTIES:
        • overall_persistence: Overall persistence score (0.0 to 1.0)
        • persistence_kind: Kind of persistence (temporary, persistent, permanent)
        • estimated_duration: Estimated duration of effects
        • decay_rate: Rate at which effects decay
    """
    
    overall_persistence: float = 0.5
    """Overall persistence score (0.0 to 1.0)."""
    
    persistence_kind: str = "unknown"
    """Kind of persistence: 'temporary', 'persistent', 'permanent', 'unknown'."""
    
    estimated_duration: float = 1.0
    """Estimated duration in abstract time units (0.0+)."""
    
    decay_rate: float = 0.5
    """Rate at which effects decay (0.0 to 1.0, higher = faster decay)."""
    
    @classmethod
    def permanent(cls) -> PersistenceResult:
        """Create a permanent persistence assessment."""
        return cls(
            dimension_name="persistence",
            overall_persistence=1.0,
            persistence_kind="permanent",
            estimated_duration=float("inf"),
            decay_rate=0.0,
            confidence=0.85,
            uncertainty=0.15,
        )
    
    @classmethod
    def temporary(cls) -> PersistenceResult:
        """Create a temporary persistence assessment."""
        return cls(
            dimension_name="persistence",
            overall_persistence=0.3,
            persistence_kind="temporary",
            estimated_duration=10.0,
            decay_rate=0.8,
            confidence=0.75,
            uncertainty=0.25,
        )
    
    @classmethod
    def persistent(cls) -> PersistenceResult:
        """Create a persistent (medium duration) assessment."""
        return cls(
            dimension_name="persistence",
            overall_persistence=0.6,
            persistence_kind="persistent",
            estimated_duration=100.0,
            decay_rate=0.3,
            confidence=0.7,
            uncertainty=0.3,
        )