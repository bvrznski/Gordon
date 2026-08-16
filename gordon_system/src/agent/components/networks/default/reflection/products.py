# Reflective Products Models
# ===========================

"""
Immutable models for reflective products (insights, patterns, etc.).

ARCHITECTURAL PRINCIPLES:
    - Products are bounded semantic results
    - Insights are distinguished from hypotheses
    - Products reference supporting evidence or record insufficient support
    - No runtime dependencies
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# PRODUCT KINDS (re-exported for convenience)
# =============================================================================

# Re-exports from enums for easy import
from .enums import ReflectiveProductKind as ProductKind

INSIGHT = "insight"
PATTERN = "pattern"
ASSUMPTION = "assumption"
CONTRADICTION = "contradiction"
CAUSE_HYPOTHESIS = "cause_hypothesis"
CONSEQUENCE_ANALYSIS = "consequence_analysis"
LESSON = "lesson"
CORRECTION_PROPOSAL = "correction_proposal"
IMPROVEMENT_PROPOSAL = "improvement_proposal"
QUESTION = "question"
UNCERTAINTY = "uncertainty"
KNOWLEDGE_GAP = "knowledge_gap"
SUCCESS_FACTOR = "success_factor"
FAILURE_FACTOR = "failure_factor"
RISK = "risk"
FOLLOW_UP_TOPIC = "follow_up_topic"
NO_MEANINGFUL_RESULT = "no_meaningful_result"


# =============================================================================
# INSIGHT VALIDATION STATUS
# =============================================================================

class InsightValidationStatus:
    """
    Status of an insight's validation.
    
    Insights must be validated before being considered reliable.
    """
    
    PENDING_VALIDATION = "pending_validation"
    """Insight generated, awaiting validation."""
    
    VALIDATED = "validated"
    """Insight has been validated against evidence."""
    
    REJECTED = "rejected"
    """Insight was rejected after validation."""
    
    PARTIALLY_VALIDATED = "partially_validated"
    """Some aspects validated, others pending."""
    
    HYPOTHESIS = "hypothesis"
    """Not yet validated - still a hypothesis."""


# =============================================================================
# REFLECTIVE PRODUCT
# =============================================================================

@dataclass(frozen=True, slots=True)
class ReflectiveProduct:
    """
    Immutable semantic result generated through reflection.
    
    A ReflectiveProduct is the primary output of reflection. Products
    should be compatible with InternalThought but remain distinct from
    runtime execution commands.
    
    PROPERTIES:
        • product_id: Unique identifier
        • kind: What type of product (ReflectiveProductKind.*)
        • semantic_content: The core concept (bounded representation)
        • subject_reference: What this is about
        • supporting_evidence: Evidence IDs that support this
        • opposing_evidence: Evidence IDs that contradict this
        • confidence: Quality assessment (0.0 to 1.0)
        • novelty: Uniqueness measure (0.0 to 1.0)
        • importance: Decision-making value (0.0 to 1.0)
        • expected_utility: Potential utility (0.0 to 1.0)
        • validation_status: Validated or still hypothesis
        • limitations: Known limitations of this product
        
    BOUNDEDNESS:
        Products must be bounded and compatible with InternalThought.
    
    NOT RESPONSIBLE FOR:
        - Mutating source data
        - Scheduling execution
        - Allocating resources
    """
    
    product_id: str
    """Unique identifier for this product."""
    
    kind: str  # ReflectiveProductKind.*
    """The canonical kind of this product."""
    
    semantic_content: str
    """Core semantic concept (bounded representation)."""
    
    subject_reference: Optional[str] = None
    """Reference to what this is about."""
    
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence IDs that support this product."""
    
    opposing_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence IDs that contradict this product."""
    
    confidence: float = 0.5
    """Confidence in this product (0.0 to 1.0)."""
    
    novelty: float = 0.0
    """Novelty measure (0.0 = not novel, 1.0 = completely novel)."""
    
    importance: float = 0.5
    """Importance for decision-making (0.0 to 1.0)."""
    
    expected_utility: float = 0.0
    """Expected utility if acted upon (0.0 to 1.0)."""
    
    validation_status: str = InsightValidationStatus.PENDING_VALIDATION
    """Current validation status."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this product."""
    
    provenance: Optional[str] = None
    """Provenance reference (how this product was generated)."""
    
    @classmethod
    def insight(
        cls,
        product_id: str,
        semantic_content: str,
        supporting_evidence: Tuple[str, ...],
        confidence: float = 0.8,
        novelty: float = 0.3,
    ) -> ReflectiveProduct:
        """Create an insight product."""
        return cls(
            product_id=product_id,
            kind=INSIGHT,
            semantic_content=semantic_content,
            supporting_evidence=supporting_evidence,
            confidence=confidence,
            novelty=novelty,
            validation_status=InsightValidationStatus.VALIDATED,
        )
    
    @classmethod
    def pattern(
        cls,
        product_id: str,
        semantic_content: str,
        evidence_count: int,
        confidence: float = 0.7,
        exceptions: Tuple[str, ...] = (),
    ) -> ReflectiveProduct:
        """Create a pattern product."""
        return cls(
            product_id=product_id,
            kind=PATTERN,
            semantic_content=semantic_content,
            supporting_evidence=tuple(f"evidence_{i}" for i in range(evidence_count)),
            confidence=confidence,
            novelty=0.5,
        )
    
    @classmethod
    def hypothesis(
        cls,
        product_id: str,
        semantic_content: str,
        evidence_references: Tuple[str, ...],
        confidence: float = 0.4,
    ) -> ReflectiveProduct:
        """Create a hypothesis (unvalidated insight)."""
        return cls(
            product_id=product_id,
            kind=CAUSE_HYPOTHESIS,
            semantic_content=semantic_content,
            supporting_evidence=evidence_references,
            confidence=confidence,
            validation_status=InsightValidationStatus.HYPOTHESIS,
        )
    
    @classmethod
    def correction_proposal(
        cls,
        product_id: str,
        problem_summary: str,
        proposed_correction: str,
        expected_utility: float = 0.7,
    ) -> ReflectiveProduct:
        """Create a correction proposal."""
        return cls(
            product_id=product_id,
            kind=CORRECTION_PROPOSAL,
            semantic_content=f"Problem: {problem_summary}. Correction: {proposed_correction}",
            expected_utility=expected_utility,
            novelty=0.2,
        )
    
    @classmethod
    def follow_up_topic(
        cls,
        product_id: str,
        topic_description: str,
        rationale: str,
    ) -> ReflectiveProduct:
        """Create a follow-up recommendation."""
        return cls(
            product_id=product_id,
            kind=FOLLOW_UP_TOPIC,
            semantic_content=f"Topic: {topic_description}. Rationale: {rationale}",
            expected_utility=0.5,
        )
    
    @classmethod
    def no_meaningful_result(cls, product_id: str) -> ReflectiveProduct:
        """Create a no-meaningful-result product."""
        return cls(
            product_id=product_id,
            kind=NO_MEANINGFUL_RESULT,
            semantic_content="Reflection completed without meaningful products.",
            confidence=1.0,
            novelty=0.0,
        )
    
    def is_validated(self) -> bool:
        """Check if this product has been validated."""
        return self.validation_status == InsightValidationStatus.VALIDATED
    
    def is_hypothesis(self) -> bool:
        """Check if this product is still a hypothesis (unvalidated)."""
        return self.validation_status in {
            InsightValidationStatus.HYPOTHESIS,
            InsightValidationStatus.PENDING_VALIDATION,
        }
    
    def has_sufficient_support(self, min_confidence: float = 0.5) -> bool:
        """Check if this product has sufficient supporting evidence."""
        return (
            len(self.supporting_evidence) > 0 and
            self.confidence >= min_confidence
        )


# =============================================================================
# INSIGHT STRUCTURE
# =============================================================================

@dataclass(frozen=True, slots=True)
class InsightStructure:
    """
    Structured representation of an insight.
    
    An insight is more than just a product - it has internal structure
    that enables evaluation and follow-up.
    
    PROPERTIES:
        • claim: The main assertion
        • evidence_summary: Summary of supporting evidence
        • confidence: Confidence in the claim
        • limitations: Known constraints on applicability
        • novelty: How novel is this insight
        • expected_utility: Potential value if acted upon
        
    BOUNDEDNESS:
        Each component must be bounded.
    """
    
    claim: str
    """The main assertion or interpretation."""
    
    evidence_summary: Tuple[str, ...] = field(default_factory=tuple)
    """Summaries of supporting evidence items."""
    
    confidence: float = 0.5
    """Confidence in the insight (0.0 to 1.0)."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations on applicability."""
    
    novelty: float = 0.0
    """Novelty measure (0.0 to 1.0)."""
    
    expected_utility: float = 0.0
    """Expected utility if acted upon (0.0 to 1.0)."""
    
    @classmethod
    def new(
        cls,
        claim: str,
        evidence_summaries: Tuple[str, ...],
        confidence: float = 0.5,
    ) -> InsightStructure:
        """Create a new insight structure."""
        return cls(
            claim=claim,
            evidence_summary=evidence_summaries,
            confidence=confidence,
        )
    
    def to_product(self, product_id: str) -> ReflectiveProduct:
        """Convert this insight structure to a reflective product."""
        return ReflectiveProduct(
            product_id=product_id,
            kind=INSIGHT,
            semantic_content=self.claim,
            supporting_evidence=self.evidence_summary,
            confidence=self.confidence,
            novelty=self.novelty,
            expected_utility=self.expected_utility,
            validation_status=(
                InsightValidationStatus.VALIDATED
                if self.confidence >= 0.7 else
                InsightValidationStatus.PARTIALLY_VALIDATED
            ),
        )


# =============================================================================
# PATTERN STRUCTURE
# =============================================================================

@dataclass(frozen=True, slots=True)
class PatternStructure:
    """
    Structured representation of a pattern.
    
    A pattern describes a recurring or structurally similar relation
    across evidence items.
    
    PROPERTIES:
        • pattern_description: The pattern itself
        • participating_observations: Which observations participate
        • recurrence_count: How often observed
        • temporal_extent: Time range of observations
        • confidence: Confidence in the pattern
        • exceptions: Known exceptions to the pattern
        
    BOUNDEDNESS:
        All components must be bounded.
    """
    
    pattern_description: str
    """Description of the recurring relation."""
    
    participating_observations: Tuple[str, ...] = field(default_factory=tuple)
    """References to observations exhibiting this pattern."""
    
    recurrence_count: int = 0
    """Number of times observed."""
    
    temporal_extent_start_utc: Optional[str] = None
    """Start of observation period (ISO string)."""
    
    temporal_extent_end_utc: Optional[str] = None
    """End of observation period (ISO string)."""
    
    confidence: float = 0.5
    """Confidence in the pattern (0.0 to 1.0)."""
    
    exceptions: Tuple[str, ...] = field(default_factory=tuple)
    """Known exceptions or edge cases."""
    
    possible_explanations: Tuple[str, ...] = field(default_factory=tuple)
    """Proposed explanations for this pattern."""
    
    @classmethod
    def new(
        cls,
        pattern_description: str,
        observation_refs: Tuple[str, ...],
        recurrence_count: int = 1,
        confidence: float = 0.5,
    ) -> PatternStructure:
        """Create a new pattern structure."""
        return cls(
            pattern_description=pattern_description,
            participating_observations=observation_refs,
            recurrence_count=recurrence_count,
            confidence=confidence,
        )


# =============================================================================
# ASSUMPTION STRUCTURE
# =============================================================================

@dataclass(frozen=True, slots=True)
class AssumptionStructure:
    """
    Structured representation of an assumption.
    
    An assumption represents a proposition that influenced activity
    but was not explicitly validated.
    
    PROPERTIES:
        • assumption_content: The assumed proposition
        • origin: How this assumption arose (explicit or inferred)
        • supporting_evidence: Evidence that supports the assumption
        • contradicting_evidence: Evidence against the assumption
        • consequence: Impact of the assumption on outcomes
        
    BOUNDEDNESS:
        All components must be bounded.
    """
    
    assumption_content: str
    """The assumed proposition."""
    
    origin: str = "inferred"
    """How this arose: 'explicit' or 'inferred'"""
    
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence that supports this assumption."""
    
    contradicting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence that contradicts this assumption."""
    
    consequence: str = ""
    """Impact of this assumption on outcomes."""
    
    confidence: float = 0.5
    """Confidence in the assumption (0.0 to 1.0)."""
    
    validation_status: str = InsightValidationStatus.PENDING_VALIDATION
    
    @classmethod
    def new(
        cls,
        assumption_content: str,
        origin: str = "inferred",
        confidence: float = 0.5,
    ) -> AssumptionStructure:
        """Create a new assumption structure."""
        return cls(
            assumption_content=assumption_content,
            origin=origin,
            confidence=confidence,
        )