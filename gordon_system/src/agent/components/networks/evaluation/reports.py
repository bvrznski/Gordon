# Gordon Cognitive Architecture - Phase 4.5.5
# Action Evaluation Reports and Results
# =====================================

"""
Main evaluation report types including EvaluatedActionCandidatePool.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# EVALUATION DISPOSITION
# =============================================================================

@dataclass(frozen=True, slots=True)
class EvaluationDisposition:
    """
    Disposition of an evaluation - whether it succeeded and why.
    
    PROPERTIES:
        • disposition: Success/failure indicator
        • reason: Reason for the disposition
        • limitations: Known limitations of this evaluation
        • assumptions: Assumptions made during evaluation
    """
    
    disposition: str = "success"
    """Success/failure indicator."""
    
    reason: str = ""
    """Reason for the disposition."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this evaluation."""
    
    assumptions: Tuple[str, ...] = field(default_factory=tuple)
    """Assumptions made during evaluation."""
    
    @classmethod
    def success(cls) -> EvaluationDisposition:
        """Create a successful disposition."""
        return cls(
            disposition="success",
            reason="Evaluation completed successfully.",
        )
    
    @classmethod
    def partial(cls, reason: str = "") -> EvaluationDisposition:
        """Create a partial success disposition."""
        return cls(
            disposition="partial",
            reason=reason or "Evaluation completed with some limitations.",
        )


# =============================================================================
# ACTION EVALUATION REPORT
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionEvaluationReport:
    """
    Complete evaluation report for an Action Candidate.
    
    PROPERTIES:
        • candidate_id: ID of the evaluated action candidate
        • revision: Revision number of this evaluation
        • dimensions: Results from all dimension evaluations
        • conflicts: Conflict analysis results
        • interference: Interference analysis results
        • outcomes: Expected outcome analysis
        • confidence: Confidence assessment
        • uncertainty: Uncertainty assessment
        • recommendation: Recommendation about the action
        • dominance_analysis: Dominance relationships with other candidates
        • disposition: Evaluation success/failure status
        • provenance: Provenance information (who/when/why)
    """
    
    candidate_id: str
    """ID of the evaluated action candidate."""
    
    revision: int = 1
    """Revision number of this evaluation."""
    
    dimensions: Tuple[Tuple[str, float], ...] = field(default_factory=tuple)
    """Results from all dimension evaluations as (dimension_name, score) tuples."""
    
    conflicts: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """Conflict analysis results as (conflict_id, description) tuples."""
    
    interference: Tuple[Tuple[str, float], ...] = field(default_factory=tuple)
    """Interference analysis results as (candidate_id, strength) tuples."""
    
    outcomes: str = ""
    """Expected outcome analysis summary."""
    
    confidence: float = 0.5
    """Confidence assessment (0.0 to 1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty assessment (0.0 to 1.0)."""
    
    recommendation: str = ""
    """Recommendation about the action."""
    
    dominance_analysis: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """Dominance relationships as (winner_id, loser_id) tuples."""
    
    disposition: EvaluationDisposition = field(default_factory=EvaluationDisposition.success)
    """Evaluation success/failure status."""
    
    provenance: dict = field(default_factory=dict)
    """Provenance information (who/when/why)."""
    
    @classmethod
    def new(cls, candidate_id: str) -> ActionEvaluationReport:
        """Create a new evaluation report for a candidate."""
        return cls(
            candidate_id=candidate_id,
            revision=1,
        )


# =============================================================================
# EVALUATED ACTION CANDIDATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class EvaluatedActionCandidate:
    """
    An Action Candidate that has been evaluated.
    
    This is an immutable record containing both the original candidate
    and its evaluation results. The original candidate reference is preserved.
    
    PROPERTIES:
        • original_candidate_id: Reference to the original candidate ID
        • evaluation_report: Complete evaluation report
        • overall_score: Composite score from all dimensions
        • is_recommended: Whether this candidate receives a positive recommendation
    """
    
    original_candidate_id: str
    """Reference to the original candidate ID."""
    
    evaluation_report: ActionEvaluationReport = field(default_factory=ActionEvaluationReport)
    """Complete evaluation report."""
    
    overall_score: float = 0.5
    """Composite score from all dimensions (0.0 to 1.0)."""
    
    is_recommended: bool = False
    """Whether this candidate receives a positive recommendation."""
    
    @classmethod
    def new(cls, original_candidate_id: str) -> EvaluatedActionCandidate:
        """Create a new evaluated action candidate."""
        return cls(
            original_candidate_id=original_candidate_id,
            evaluation_report=ActionEvaluationReport.new(original_candidate_id),
        )


# =============================================================================
# EVALUATED ACTION CANDIDATE POOL
# =============================================================================

@dataclass(frozen=True, slots=True)
class EvaluatedActionCandidatePool:
    """
    A complete collection of evaluated Action Candidates.
    
    This is the terminal product of Phase 4.5.5 - a complete, immutable,
    auditable evaluation of every Action Candidate in the pool.
    
    NO ACTION IS SELECTED HERE.
    
    PROPERTIES:
        • original_pool_size: Size of the input candidate pool
        • evaluated_candidates: List of all evaluated candidates
        • pairwise_comparisons: All pairwise comparison results
        • dominance_relations: Dominance relationships between candidates
        • conflict_summary: Summary of conflicts detected
        • interference_summary: Summary of interferences detected
        • provenance: Provenance information for the entire evaluation
    """
    
    original_pool_size: int = 0
    """Size of the input candidate pool."""
    
    evaluated_candidates: Tuple[EvaluatedActionCandidate, ...] = field(default_factory=tuple)
    """List of all evaluated candidates."""
    
    pairwise_comparisons: Tuple[Tuple[str, str, float], ...] = field(default_factory=tuple)
    """All pairwise comparison results as (a_id, b_id, score) tuples."""
    
    dominance_relations: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """Dominance relationships between candidates."""
    
    conflict_summary: str = ""
    """Summary of conflicts detected."""
    
    interference_summary: str = ""
    """Summary of interferences detected."""
    
    provenance: dict = field(default_factory=dict)
    """Provenance information for the entire evaluation."""
    
    @classmethod
    def empty(cls) -> EvaluatedActionCandidatePool:
        """Create an empty evaluated candidate pool."""
        return cls(
            original_pool_size=0,
            evaluated_candidates=(),
            pairwise_comparisons=(),
            dominance_relations=(),
        )
    
    @classmethod
    def from_evaluations(
        cls,
        candidates: Tuple[EvaluatedActionCandidate, ...],
    ) -> EvaluatedActionCandidatePool:
        """Create a pool from a tuple of evaluated candidates."""
        return cls(
            original_pool_size=len(candidates),
            evaluated_candidates=candidates,
        )
    
    @classmethod
    def with_comparisons(
        cls,
        candidates: Tuple[EvaluatedActionCandidate, ...],
        comparisons: Tuple[Tuple[str, str, float], ...],
    ) -> EvaluatedActionCandidatePool:
        """Create a pool with pre-computed pairwise comparisons."""
        return cls(
            original_pool_size=len(candidates),
            evaluated_candidates=candidates,
            pairwise_comparisons=comparisons,
        )


# =============================================================================
# EVALUATION SUMMARY
# =============================================================================

@dataclass(frozen=True, slots=True)
class EvaluatedActionCandidatePoolSummary:
    """
    Summary statistics for an EvaluatedActionCandidatePool.
    
    PROPERTIES:
        • total_candidates: Total number of candidates in pool
        • candidates_by_recommendation: Count by recommendation status
        • average_confidence: Average confidence across all evaluations
        • average_uncertainty: Average uncertainty across all evaluations
        • total_conflicts: Number of conflicts detected
        • dominant_candidates: List of candidate IDs that dominate others
    """
    
    total_candidates: int = 0
    """Total number of candidates in pool."""
    
    candidates_by_recommendation: dict = field(default_factory=dict)
    """Count by recommendation status."""
    
    average_confidence: float = 0.5
    """Average confidence across all evaluations (0.0 to 1.0)."""
    
    average_uncertainty: float = 0.5
    """Average uncertainty across all evaluations (0.0 to 1.0)."""
    
    total_conflicts: int = 0
    """Number of conflicts detected."""
    
    dominant_candidates: Tuple[str, ...] = field(default_factory=tuple)
    """List of candidate IDs that dominate others."""