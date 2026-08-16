# Salience Network Assessment State
# ================================
#
# Canonical implementation of multi-dimensional salience assessment (Phase 4.8.4).
#

"""
Multi-dimensional salience assessment state.

The assessment represents semantic evaluation across all salience dimensions:
    - significance: Overall importance
    - relevance: Contextual alignment
    - novelty:新 information value
    - urgency: Temporal pressure
    - uncertainty: Semantic confidence
    - conflict: Contradictory evidence
    - prediction_error: Expectation violation

Assessment does NOT compute scores; it represents computed results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from .enums import SalienceLevel


@dataclass(frozen=True)
class SignificanceDescriptor:
    """
    Semantic descriptor for significance assessment.
    
    Significance answers: "How important is this in absolute terms?"
    """
    
    level: SalienceLevel = SalienceLevel.UNKNOWN
    """Canonical significance level."""
    
    basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for the significance judgment."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this assessment."""


@dataclass(frozen=True)
class RelevanceDescriptor:
    """
    Semantic descriptor for relevance assessment.
    
    Relevance answers: "How well does this align with current context?"
    """
    
    level: SalienceLevel = SalienceLevel.UNKNOWN
    """Canonical relevance level."""
    
    context_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Contexts to which this is relevant."""
    
    basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for the relevance judgment."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this assessment."""


@dataclass(frozen=True)
class NoveltyDescriptor:
    """
    Semantic descriptor for novelty assessment.
    
    Novelty answers: "How new or unexpected is this?"
    """
    
    level: SalienceLevel = SalienceLevel.UNKNOWN
    """Canonical novelty level."""
    
    expected_vs_actual: Tuple[str, ...] = field(default_factory=tuple)
    """Expected vs. actual semantic comparison."""
    
    basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for the novelty judgment."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this assessment."""


@dataclass(frozen=True)
class UrgencyDescriptor:
    """
    Semantic descriptor for urgency assessment.
    
    Urgency answers: "What temporal pressure does this carry?"
    """
    
    level: SalienceLevel = SalienceLevel.UNKNOWN
    """Canonical urgency level."""
    
    time_basis: Tuple[str, ...] = field(default_factory=tuple)
    """External time references if available."""
    
    consequences_if_delayed: Tuple[str, ...] = field(default_factory=tuple)
    """Consequences of not responding promptly."""
    
    basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for the urgency judgment."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this assessment."""


@dataclass(frozen=True)
class UncertaintyDescriptor:
    """
    Semantic descriptor for uncertainty assessment.
    
    Uncertainty describes unresolved semantic unknowns (distinct from confidence).
    """
    
    level: SalienceLevel = SalienceLevel.UNKNOWN
    """Canonical uncertainty level."""
    
    sources_of_uncertainty: Tuple[str, ...] = field(default_factory=tuple)
    """Identified sources of semantic uncertainty."""
    
    missing_information: Tuple[str, ...] = field(default_factory=tuple)
    """Identified gaps in available information."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this assessment."""


@dataclass(frozen=True)
class ConflictDescriptor:
    """
    Semantic descriptor for conflict assessment.
    
    Conflict answers: "Are there contradictory pieces of evidence?"
    """
    
    level: SalienceLevel = SalienceLevel.UNKNOWN
    """Canonical conflict level."""
    
    conflicting_evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of mutually contradictory evidence."""
    
    resolution_basis: str = field(default="")
    """Semantic basis for any resolved conflict."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this assessment."""


@dataclass(frozen=True)
class PredictionErrorDescriptor:
    """
    Semantic descriptor for prediction-error assessment.
    
    Prediction error answers: "How much does this deviate from expectations?"
    """
    
    level: SalienceLevel = SalienceLevel.UNKNOWN
    """Canonical prediction-error level."""
    
    expected_vs_observed: Tuple[str, ...] = field(default_factory=tuple)
    """Expected state vs. observed state comparison."""
    
    confidence_in_prediction: float = 0.5
    """Confidence in the original prediction (0-1)."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this assessment."""


@dataclass(frozen=True)
class MotivationalSalienceDescriptor:
    """
    Semantic descriptor for motivational significance.
    
    Motivational salience answers: "How strongly does this drive action?"
    
    This is external to the Salience Network in terms of authority.
    """
    
    level: SalienceLevel = SalienceLevel.UNKNOWN
    """Canonical motivational salience level."""
    
    motivation_id: str = field(default="")
    """Authority-referenced motivation source ID."""
    
    basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for the motivational assessment."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this assessment."""


@dataclass(frozen=True)
class ContextualSalienceDescriptor:
    """
    Semantic descriptor for contextual significance.
    
    Contextual salience answers: "How does context modify interpretation?"
    """
    
    level: SalienceLevel = SalienceLevel.UNKNOWN
    """Canonical contextual salience level."""
    
    context_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Contexts affecting this assessment."""
    
    basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for the contextual assessment."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this assessment."""


@dataclass(frozen=True)
class ConfidenceDescriptor:
    """
    Semantic descriptor for confidence in assessment.
    
    Confidence answers: "How strongly do we believe this assessment?"
    
    Distinct from uncertainty: one can be highly confident about uncertainty.
    """
    
    level: SalienceLevel = SalienceLevel.UNKNOWN
    """Canonical confidence level."""
    
    evidence_count: int = 0
    """Number of supporting evidence items."""
    
    uncertainty_basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for uncertainty level (if known)."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this assessment."""


@dataclass(frozen=True)
class SalienceAssessmentState:
    """
    Canonical multi-dimensional salience assessment.
    
    The aggregate assessment provides one coherent view without collapsing all
    dimensions into a single unexplained score.
    
    ARCHITECTURAL INVARIANTS:
        - SALIENCE-ASSESSMENT-INV-001: Assessment preserves ontology semantics
        - SALIENCE-ASSESSMENT-INV-002: UNKNOWN remains distinct from NEGLIGIBLE
        - SALIENCE-ASSESSMENT-INV-003: Assessment never computes, only represents
    
    ASSESSMENT LAWS:
        - SALIENCE-ASSESSMENT-LAW-001: Overall level may differ from dimension levels
        - SALIENCE-ASSESSMENT-LAW-002: Assessment preserves external authority
        - SALIENCE-ASSESSMENT-LAW-003: Assessment never represents runtime behavior
    """
    
    overall_level: SalienceLevel = SalienceLevel.UNKNOWN
    """Overall canonical salience level."""
    
    significance: SignificanceDescriptor = field(default_factory=SignificanceDescriptor)
    """Semantic significance assessment."""
    
    relevance: RelevanceDescriptor = field(default_factory=RelevanceDescriptor)
    """Contextual relevance assessment."""
    
    novelty: NoveltyDescriptor = field(default_factory=NoveltyDescriptor)
    """Newness and unexpectedness assessment."""
    
    urgency: UrgencyDescriptor = field(default_factory=UrgencyDescriptor)
    """Temporal pressure assessment."""
    
    uncertainty: UncertaintyDescriptor = field(default_factory=UncertaintyDescriptor)
    """Semantic uncertainty representation."""
    
    conflict: ConflictDescriptor = field(default_factory=ConflictDescriptor)
    """Evidence contradiction assessment."""
    
    prediction_error: PredictionErrorDescriptor = field(default_factory=PredictionErrorDescriptor)
    """Expectation deviation assessment."""
    
    confidence: ConfidenceDescriptor = field(default_factory=ConfidenceDescriptor)
    """Confidence in the assessment itself."""
    
    motivational_significance: MotivationalSalienceDescriptor | None = None
    """Motivationally-weighted significance (external authority)."""
    
    contextual_significance: ContextualSalienceDescriptor | None = None
    """Context-modified significance."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Aggregate assessment limitations."""