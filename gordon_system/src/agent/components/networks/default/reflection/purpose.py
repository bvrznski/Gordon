# Reflection Purpose Models
# =========================

"""
Immutable models for reflection purposes.

ARCHITECTURAL PRINCIPLES:
    - Purposes define the goal of reflection
    - Each purpose has associated rules and constraints
    - No runtime dependencies in domain objects
"""

from __future__ import annotations

from dataclasses import dataclass, field


# =============================================================================
# REFLECTION PURPOSE KINDS
# =============================================================================

class ReflectionPurposeKind:
    """
    Canonical kinds of reflection purposes.
    
    Each kind defines the expected behavior, evidence requirements,
    and completion rules for that type of reflection.
    """
    
    EXPERIENCE_REVIEW = "experience_review"
    """Review experience to extract lessons."""
    
    OUTCOME_REVIEW = "outcome_review"
    """Evaluate an outcome against criteria."""
    
    FAILURE_REVIEW = "failure_review"
    """Analyze a failure to identify root causes."""
    
    SUCCESS_REVIEW = "success_review"
    """Analyze success factors."""
    
    ASSUMPTION_REVIEW = "assumption_review"
    """Identify and evaluate assumptions."""
    
    PATTERN_DISCOVERY = "pattern_discovery"
    """Discover patterns across evidence."""
    
    CONTRADICTION_ANALYSIS = "contradiction_analysis"
    """Analyze contradictions between evidence sources."""
    
    INSIGHT_GENERATION = "insight_generation"
    """Generate insights from prior activity."""
    
    DECISION_REVIEW = "decision_review"
    """Review decisions and their outcomes."""
    
    PLAN_REVIEW = "plan_review"
    """Review plans against actual execution."""
    
    BEHAVIOR_REVIEW = "behavior_review"
    """Review behavioral patterns."""
    
    SELF_EVALUATION = "self_evaluation"
    """Self-evaluation of reflection process."""
    
    IDENTITY_REVIEW = "identity_review"
    """Review identity state and consistency."""
    
    NARRATIVE_REVIEW = "narrative_review"
    """Review narrative coherence."""
    
    MEMORY_INTEGRATION_REVIEW = "memory_integration_review"
    """Review memory integration quality."""
    
    POLICY_REVIEW = "policy_review"
    """Review policy effectiveness."""
    
    ARCHITECTURE_REVIEW = "architecture_review"
    """Review system architecture and design."""
    
    GENERAL_REFLECTION = "general_reflection"
    """General-purpose reflection."""
    
    @classmethod
    def all_kinds(cls) -> tuple[str, ...]:
        """Return all purpose kinds."""
        return (
            cls.EXPERIENCE_REVIEW,
            cls.OUTCOME_REVIEW,
            cls.FAILURE_REVIEW,
            cls.SUCCESS_REVIEW,
            cls.ASSUMPTION_REVIEW,
            cls.PATTERN_DISCOVERY,
            cls.CONTRADICTION_ANALYSIS,
            cls.INSIGHT_GENERATION,
            cls.DECISION_REVIEW,
            cls.PLAN_REVIEW,
            cls.BEHAVIOR_REVIEW,
            cls.SELF_EVALUATION,
            cls.IDENTITY_REVIEW,
            cls.NARRATIVE_REVIEW,
            cls.MEMORY_INTEGRATION_REVIEW,
            cls.POLICY_REVIEW,
            cls.ARCHITECTURE_REVIEW,
            cls.GENERAL_REFLECTION,
        )


# =============================================================================
# REFLECTION PURPOSE
# =============================================================================

@dataclass(frozen=True, slots=True)
class ReflectionPurpose:
    """
    Immutable purpose definition for a reflection.
    
    The purpose defines what the reflection is trying to achieve,
    its expected evidence, allowed products, and completion rules.
    """
    
    kind: str  # ReflectionPurposeKind.*
    """The canonical kind of this purpose."""
    
    description: str = ""
    """Human-readable description of this purpose."""
    
    expected_context: tuple[str, ...] = field(default_factory=tuple)
    """Expected context elements for this purpose."""
    
    allowed_products: tuple[str, ...] = field(default_factory=tuple)
    """Product kinds this purpose may produce."""
    
    completion_rules: tuple[str, ...] = field(default_factory=tuple)
    """Rules for determining when this purpose is complete."""
    
    recursion_limit: int = 3
    """Maximum recursion depth allowed."""
    
    required_confidence: float = 0.5
    """Minimum confidence threshold."""
    
    allows_follow_up_proposals: bool = True
    """Whether follow-up proposals are allowed."""
    
    @classmethod
    def outcome_review(cls) -> ReflectionPurpose:
        """Create an outcome review purpose."""
        return cls(
            kind=ReflectionPurposeKind.OUTCOME_REVIEW,
            description="Review an outcome to identify success factors, failure causes, and lessons",
            expected_context=("objective", "plan", "decisions", "outcomes"),
            allowed_products=(
                "success_factor",
                "failure_factor",
                "lesson",
                "correction_proposal",
                "improvement_proposal",
                "question",
            ),
            completion_rules=(
                "outcome_evidence_validated",
                "success_failure_factors_recorded",
                "unresolved_uncertainty_reported",
            ),
        )
    
    @classmethod
    def assumption_review(cls) -> ReflectionPurpose:
        """Create an assumption review purpose."""
        return cls(
            kind=ReflectionPurposeKind.ASSUMPTION_REVIEW,
            description="Identify and evaluate assumptions that influenced activity",
            expected_context=("decisions", "plans", "outcomes"),
            allowed_products=(
                "assumption",
                "supporting_evidence",
                "contradicting_evidence",
                "consequence_analysis",
            ),
            completion_rules=(
                "material_assumptions_identified",
                "evidence_attached",
                "validation_status_assigned",
            ),
        )
    
    @classmethod
    def pattern_discovery(cls) -> ReflectionPurpose:
        """Create a pattern discovery purpose."""
        return cls(
            kind=ReflectionPurposeKind.PATTERN_DISCOVERY,
            description="Discover patterns across evidence",
            expected_context=("activity_history", "outcomes"),
            allowed_products=(
                "pattern",
                "evidence_reference",
                "exception",
            ),
            completion_rules=(
                "candidate_patterns_produced",
                "evidence_and_exceptions_recorded",
                "confidence_assigned",
            ),
        )
    
    @classmethod
    def insight_generation(cls) -> ReflectionPurpose:
        """Create an insight generation purpose."""
        return cls(
            kind=ReflectionPurposeKind.INSIGHT_GENERATION,
            description="Generate insights from prior activity",
            expected_context=("thoughts", "decisions", "outcomes"),
            allowed_products=(
                "insight",
                "evidence_reference",
                "novelty_assessment",
                "limitations",
            ),
            completion_rules=(
                "at_least_one_insight_candidate_evaluated",
                "accepted_and_rejected_distinguished",
                "limitations_recorded",
            ),
        )
    
    @classmethod
    def general(cls) -> ReflectionPurpose:
        """Create a general reflection purpose."""
        return cls(
            kind=ReflectionPurposeKind.GENERAL_REFLECTION,
            description="General-purpose reflection with no specific focus",
            expected_context=(),
            allowed_products=tuple(),  # All products allowed
            completion_rules=("meaningful_product_produced",),
        )