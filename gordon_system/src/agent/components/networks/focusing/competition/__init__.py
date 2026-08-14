# Competition Resolution Subsystem
# ================================
#
# Phase 4.2.4: Canonical computational implementation of goal-directed competition,
# distractor suppression, and candidate refinement.
#
# This subsystem determines how competing FocusCandidates influence one another.
# It does NOT decide the final behavioral focus - only computes interaction.
# ================================================

"""
Competition Resolution and Suppression Model for Phase 4.2.4.

This module implements Gordon's canonical competition and suppression model:

ARCHITECTURAL RESPONSIBILITY:
    This subsystem owns:
        • Pairwise competition analysis between candidates
        • Conflict detection (resource, goal, context, temporal)
        • Compatibility estimation (can candidates coexist?)
        • Suppression recommendations (which should be suppressed?)
        • Dominance analysis (which is most influential?)
        • Competition matrix computation (pairwise relationships)
        • Explainability of all competition assessments
        • Confidence estimation for competition conclusions

    This subsystem NEVER owns:
        • Attention allocation
        • Winner selection
        • Behavioral decisions
        • Policy creation
        • Execution control

INPUTS:
    FocusCandidate: The candidates being assessed
    PriorityAssessment: Already computed priorities (external)
    ContextProjection: Current execution context (external)
    ActiveObjectives: Current objectives (external)

OUTPUTS (immutable recommendations):
    CompetitionAssessment: Overall competition summary
    CompetitionMatrix: Pairwise relationships
    SuppressionAssessment: Suppression recommendations
    CompetitionExplanation: Rationale for all conclusions
    CompetitionConfidence: Reliability scores

All computations are deterministic, explainable, and stateless.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)
from datetime import datetime
import math

# Import existing models
from gordon_system.src.agent.components.networks.focusing.models import FocusCandidate


# =============================================================================
# PUBLIC EXPORTS - Phase 4.2.4 computational models and algorithms
# =============================================================================

__all__ = [
    # Relationship types
    "CompetitionRelationship",
    
    # Competition descriptors (immutable data)
    "CompetitionDescriptor",
    "CompetitionContribution",
    "CompetitionEvidence",
    "CompetitionBreakdown",
    "CompetitionExplanation",
    "CompetitionConfidence",
    "SuppressionDescriptor",
    "SuppressionContribution",
    "SuppressionEvidence",
    "SuppressionSummary",
    
    # Assessment outputs
    "CompetitionAssessment",
    "SuppressionAssessment",
    "DominanceAssessment",
    "CompatibilityAssessment",
    "ConflictAssessment",
    
    # Matrix representation
    "CompetitionMatrix",
    
    # State classes (for persistence)
    "CompetitionState",
    "SuppressionState",
    "CompetitionHistory",
    "CompetitionSnapshots",
    
    # Diagnostic data
    "CompetitionDiagnostics",
    
    # Algorithm estimators
    "CompetitionAnalyzer",
    "ConflictDetector",
    "CompatibilityEstimator",
    "SuppressionEstimator",
    "DominanceAnalyzer",
]


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    """Clamp a value to the specified range."""
    return max(min_value, min(max_value, value))


def normalize(
    value: float,
    min_val: float,
    max_val: float,
    clamp_result: bool = True
) -> float:
    """
    Normalize a value from [min_val, max_val] to [0.0, 1.0].
    
    If the range is zero (all values equal), returns 0.5.
    """
    if max_val == min_val:
        return 0.5
    
    normalized = (value - min_val) / (max_val - min_val)
    
    if clamp_result:
        return clamp(normalized)
    
    return normalized


# =============================================================================
# COMPETITION RELATIONSHIP TYPES
# =============================================================================

class CompetitionRelationship:
    """
    Type of relationship between two competing candidates.
    
    Each relationship describes how candidates influence each other
    computationally (not behaviorally).
    """
    
    INDEPENDENT = "independent"
    """Candidates do not interact. Neither affects the other."""
    
    COMPATIBLE = "compatible"
    """Candidates can coexist and support each other."""
    
    SUPPORTIVE = "supportive"
    """One candidate supports or enables the other."""
    
    COMPETITIVE = "competitive"
    """Candidates compete for resources but can both be maintained."""
    
    MUTUALLY_EXCLUSIVE = "mutually_exclusive"
    """Only one candidate can be active at a time."""
    
    HIERARCHICAL = "hierarchical"
    """One candidate is dominant over the other (parent-child)."""
    
    BLOCKING = "blocking"
    """One candidate prevents the other from being valid."""


# =============================================================================
# COMPETITION DESCRIPTORS - Immutable data structures
# =============================================================================

@dataclass(frozen=True)
class CompetitionContribution:
    """
    A single computational contribution to a competition assessment.
    """
    
    source: str
    """Where this contribution came from (e.g., 'resource_overlap', 'goal_conflict')."""
    
    weight: float
    """Weight of this contribution in the overall assessment."""
    
    raw_value: float
    """Raw contribution score (0.0 to 1.0)."""
    
    effect_direction: str = "competitive"
    """Direction of effect: 'competitive', 'compatible', 'supportive'."""
    
    def contribution_score(self) -> float:
        """Calculate weighted contribution."""
        return self.raw_value * self.weight
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "source": self.source,
            "weight": self.weight,
            "raw_value": self.raw_value,
            "effect_direction": self.effect_direction,
            "contribution_score": self.contribution_score(),
        }


@dataclass(frozen=True)
class CompetitionEvidence:
    """
    Raw evidence components for a competition assessment.
    
    Contains all computational factors without aggregation or normalization.
    """
    
    # Pairwise relationship scores
    resource_overlap: float = 0.5
    """How much candidates share resources."""
    
    goal_conflict: float = 0.5
    """Degree of goal conflict between candidates."""
    
    context_compatibility: float = 0.5
    """Whether contexts are compatible for coexistence."""
    
    temporal_overlap: float = 0.5
    """Temporal alignment/overlap."""
    
    priority_ratio: float = 0.5
    """Ratio of priorities (higher = more dominant)."""
    
    # Evidence details
    contributing_factors: Tuple[CompetitionContribution, ...] = field(default_factory=tuple)
    """Detailed breakdown of factors."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "resource_overlap": self.resource_overlap,
            "goal_conflict": self.goal_conflict,
            "context_compatibility": self.context_compatibility,
            "temporal_overlap": self.temporal_overlap,
            "priority_ratio": self.priority_ratio,
            "contributing_factors": [c.to_dict() for c in self.contributing_factors],
        }


@dataclass(frozen=True)
class CompetitionDescriptor:
    """
    Describes competition characteristics without computing them.
    
    Contains only the relationship data, not algorithms.
    """
    
    relationship_type: str = CompetitionRelationship.COMPATIBLE
    """Type of competitive relationship."""
    
    competition_strength: float = 0.0
    """Strength of competition (0.0 to 1.0)."""
    
    compatibility_score: float = 1.0
    """Compatibility for coexistence (0.0 to 1.0)."""
    
    resource_conflict: float = 0.0
    """Resource conflict level."""
    
    goal_conflict: float = 0.0
    """Goal conflict level."""
    
    dominance_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting dominance relationships."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "relationship_type": self.relationship_type,
            "competition_strength": self.competition_strength,
            "compatibility_score": self.compatibility_score,
            "resource_conflict": self.resource_conflict,
            "goal_conflict": self.goal_conflict,
            "dominance_evidence": list(self.dominance_evidence),
        }


# =============================================================================
# COMPETITION MATRIX
# =============================================================================

@dataclass(frozen=True)
class CompetitionMatrixEntry:
    """
    A single entry in the competition matrix.
    
    Represents pairwise relationship between two candidates.
    """
    
    source_id: str
    """ID of first candidate."""
    
    target_id: str
    """ID of second candidate."""
    
    competition_strength: float = 0.0
    """How strongly they compete (0.0 to 1.0)."""
    
    compatibility_score: float = 1.0
    """Can they coexist? (0.0 to 1.0)."""
    
    relationship_type: str = CompetitionRelationship.COMPATIBLE
    """Type of relationship."""
    
    resource_overlap: float = 0.0
    """Shared resources."""
    
    goal_conflict: float = 0.0
    """Goal alignment conflict."""
    
    priority_ratio: float = 1.0
    """Priority ratio (source/target)."""
    
    dominance_direction: str = "neutral"
    """Dominance: 'source', 'target', or 'neutral'."""
    
    explanation: Optional[str] = None
    """Human-readable rationale for this relationship."""
    
    def is_symmetric(self) -> bool:
        """
        Check if this relationship is symmetric (mutual).
        
        Returns True for relationships like INDEPENDENT, COMPATIBLE.
        Returns False for directional relationships like HIERARCHICAL, BLOCKING.
        """
        asymmetric_types = {
            CompetitionRelationship.HIERARCHICAL,
            CompetitionRelationship.BLOCKING,
            "supportive",
            "dominated_by_source",
            "dominated_by_target",
        }
        return self.relationship_type not in asymmetric_types
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "competition_strength": self.competition_strength,
            "compatibility_score": self.compatibility_score,
            "relationship_type": self.relationship_type,
            "resource_overlap": self.resource_overlap,
            "goal_conflict": self.goal_conflict,
            "priority_ratio": self.priority_ratio,
            "dominance_direction": self.dominance_direction,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class CompetitionMatrix:
    """
    Immutable matrix representing pairwise competition relationships.
    
    Supports efficient lookup and analysis of candidate interactions
    without modifying any state.
    """
    
    # Matrix data
    entries: Tuple[CompetitionMatrixEntry, ...] = field(default_factory=tuple)
    """All pairwise relationship entries."""
    
    candidates_seen: Tuple[str, ...] = field(default_factory=tuple)
    """All candidate IDs seen in this matrix."""
    
    # Configuration
    max_entries: int = 1000
    
    @classmethod
    def create_empty(cls) -> "CompetitionMatrix":
        """Create an empty competition matrix."""
        return cls()
    
    def add_entry(self, entry: CompetitionMatrixEntry) -> "CompetitionMatrix":
        """
        Add a new entry to the matrix.
        
        Args:
            entry: The pairwise relationship to add
            
        Returns:
            New matrix with the entry added
        """
        # Check if we already have an entry for this pair
        existing_entries = tuple(
            e for e in self.entries
            if not (
                (e.source_id == entry.source_id and e.target_id == entry.target_id) or
                (e.source_id == entry.target_id and e.target_id == entry.source_id)
            )
        )
        
        new_entries = existing_entries + (entry,)
        
        # Trim if needed (keep most recent/strongest)
        if len(new_entries) > self.max_entries:
            new_entries = new_entries[-self.max_entries:]
        
        return dataclass_replace(self, entries=new_entries)
    
    def get_entry(
        self,
        source_id: str,
        target_id: str
    ) -> Optional[CompetitionMatrixEntry]:
        """
        Get the entry for a specific candidate pair.
        
        Checks both (source, target) and (target, source) since some
        relationships are symmetric.
        """
        for entry in self.entries:
            if (
                (entry.source_id == source_id and entry.target_id == target_id) or
                (entry.source_id == target_id and entry.target_id == source_id)
            ):
                return entry
        
        # If no entry found, they're independent by default
        return CompetitionMatrixEntry(
            source_id=source_id,
            target_id=target_id,
            competition_strength=0.0,
            compatibility_score=1.0,
            relationship_type=CompetitionRelationship.INDEPENDENT,
        )
    
    def get_competitors(self, candidate_id: str) -> Tuple[str, ...]:
        """
        Get all candidates that compete with the given candidate.
        
        Returns IDs of candidates where competition_strength > 0.
        """
        competitors = []
        for entry in self.entries:
            if (
                entry.competition_strength > 0.1 and
                candidate_id in (entry.source_id, entry.target_id)
            ):
                other = (
                    entry.target_id
                    if entry.source_id == candidate_id else
                    entry.source_id
                )
                competitors.append(other)
        
        return tuple(competitors)
    
    def get_dominant_candidates(self, threshold: float = 0.7) -> Tuple[str, ...]:
        """
        Get candidates with high dominance scores.
        
        A dominant candidate has many relationships where it's in the
        dominant position (priority_ratio > threshold).
        """
        dominance_count: Dict[str, int] = {}
        total_competitive = len(self.entries)
        
        for entry in self.entries:
            if entry.competition_strength > 0.1:
                # Count dominance
                if entry.dominance_direction == "source":
                    dominance_count[entry.source_id] = (
                        dominance_count.get(entry.source_id, 0) + 1
                    )
                elif entry.dominance_direction == "target":
                    dominance_count[entry.target_id] = (
                        dominance_count.get(entry.target_id, 0) + 1
                    )
        
        # Find candidates with significant dominance
        min_dominant_ratio = 0.3
        return tuple(
            candidate_id for candidate_id, count in dominance_count.items()
            if count / max(total_competitive, 1) >= min_dominant_ratio
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "entry_count": len(self.entries),
            "candidates_seen": list(self.candidates_seen),
            "entries": [e.to_dict() for e in self.entries],
        }


# =============================================================================
# SUPPRESSION DESCRIPTORS
# =============================================================================

@dataclass(frozen=True)
class SuppressionContribution:
    """
    A single computational contribution to a suppression recommendation.
    """
    
    source: str
    """Source of this suppression factor."""
    
    weight: float = 1.0
    """Weight of this factor."""
    
    raw_value: float = 0.5
    """Raw suppression strength (0.0 to 1.0)."""
    
    suppression_type: str = "temporary"
    """Type: 'temporary', 'partial', or 'full'."""
    
    def contribution_score(self) -> float:
        """Calculate weighted contribution."""
        return self.raw_value * self.weight
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "source": self.source,
            "weight": self.weight,
            "raw_value": self.raw_value,
            "suppression_type": self.suppression_type,
            "contribution_score": self.contribution_score(),
        }


@dataclass(frozen=True)
class SuppressionEvidence:
    """
    Raw evidence components for a suppression assessment.
    """
    
    resource_pressure: float = 0.0
    """How much resources this candidate consumes."""
    
    interference_score: float = 0.0
    """Degree to which this interferes with others."""
    
    priority_ratio: float = 0.5
    """Priority ratio compared to competitors."""
    
    historical_suppression_count: int = 0
    """Past suppression events for this candidate."""
    
    contributing_factors: Tuple[SuppressionContribution, ...] = field(default_factory=tuple)
    """Detailed breakdown."""
    
    def total_suppression_score(self) -> float:
        """Compute overall suppression score (0.0 to 1.0)."""
        base_score = (
            self.resource_pressure * 0.3 +
            self.interference_score * 0.4 +
            max(0, 1 - self.priority_ratio) * 0.3
        )
        
        # Add historical factor
        if self.historical_suppression_count > 0:
            base_score += min(0.2, self.historical_suppression_count * 0.05)
        
        return clamp(base_score)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "resource_pressure": self.resource_pressure,
            "interference_score": self.interference_score,
            "priority_ratio": self.priority_ratio,
            "historical_suppression_count": self.historical_suppression_count,
            "total_suppression_score": self.total_suppression_score(),
            "contributing_factors": [c.to_dict() for c in self.contributing_factors],
        }


@dataclass(frozen=True)
class SuppressionDescriptor:
    """
    Describes suppression characteristics without computing them.
    """
    
    should_suppress: bool = False
    """Recommendation to suppress this candidate."""
    
    suppression_strength: float = 0.0
    """Strength of suppression recommendation (0.0 to 1.0)."""
    
    suppression_type: str = "none"
    """Type: 'none', 'temporary', 'partial', or 'full'."""
    
    duration_recommendation_seconds: int = 0
    """Recommended suppression duration."""
    
    suppresses_candidates: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of candidates this suppresses."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "should_suppress": self.should_suppress,
            "suppression_strength": self.suppression_strength,
            "suppression_type": self.suppression_type,
            "duration_recommendation_seconds": self.duration_recommendation_seconds,
            "suppresses_candidates": list(self.suppresses_candidates),
        }


# =============================================================================
# COMPETITION ASSESSMENT OUTPUTS
# =============================================================================

@dataclass(frozen=True)
class CompetitionBreakdown:
    """
    Detailed breakdown of how competition was computed.
    """
    
    # Aggregated values
    overall_competition_strength: float = 0.0
    """Total competition strength across all candidates."""
    
    total_pairs_analyzed: int = 0
    """Number of candidate pairs examined."""
    
    competitive_pairs: int = 0
    """Pairs with significant competition."""
    
    compatible_pairs: int = 0
    """Pairs that can coexist."""
    
    # Component breakdown
    components: Tuple[CompetitionContribution, ...] = field(default_factory=tuple)
    """Individual factors contributing to assessment."""
    
    def contribution_percentages(self) -> Dict[str, float]:
        """Calculate percentage contribution of each component."""
        if not self.components:
            return {}
        
        total_weighted = sum(c.contribution_score() for c in self.components)
        if total_weighted == 0:
            return {c.source: 0.0 for c in self.components}
        
        return {
            c.source: (c.contribution_score() / total_weighted) * 100
            for c in self.components
        }
    
    def dominant_factors(self, threshold: float = 10.0) -> Tuple[str, ...]:
        """Get factors with significant contributions."""
        percentages = self.contribution_percentages()
        return tuple(
            name for name, pct in percentages.items() if pct >= threshold
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "overall_competition_strength": self.overall_competition_strength,
            "total_pairs_analyzed": self.total_pairs_analyzed,
            "competitive_pairs": self.competitive_pairs,
            "compatible_pairs": self.compatible_pairs,
            "components": [c.to_dict() for c in self.components],
            "contribution_percentages": self.contribution_percentages(),
            "dominant_factors": self.dominant_factors(),
        }


@dataclass(frozen=True)
class CompetitionConfidence:
    """
    Confidence assessment for a competition calculation.
    """
    
    score: float = 0.5
    """Overall confidence in the assessment."""
    
    # Confidence factors
    input_completeness_score: float = 0.5
    """Quality/quantity of input data."""
    
    relationship_consistency_score: float = 0.5
    """Consistency of detected relationships."""
    
    historical_stability_score: float = 0.5
    """Stability of competition patterns over time."""
    
    computation_stability_score: float = 0.5
    """Algorithm stability and determinism."""
    
    # Metadata
    confidence_factors: Tuple[str, ...] = field(default_factory=tuple)
    """Human-readable factors that increased confidence."""
    
    uncertainty_sources: Tuple[str, ...] = field(default_factory=tuple)
    """Identified sources of uncertainty."""
    
    @classmethod
    def low_confidence(cls) -> "CompetitionConfidence":
        """Create a low-confidence assessment."""
        return cls(
            score=0.3,
            input_completeness_score=0.4,
            relationship_consistency_score=0.3,
            historical_stability_score=0.2,
            computation_stability_score=0.6,
        )
    
    @classmethod
    def high_confidence(cls) -> "CompetitionConfidence":
        """Create a high-confidence assessment."""
        return cls(
            score=0.85,
            input_completeness_score=0.9,
            relationship_consistency_score=0.85,
            historical_stability_score=0.8,
            computation_stability_score=0.9,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "score": self.score,
            "input_completeness_score": self.input_completeness_score,
            "relationship_consistency_score": self.relationship_consistency_score,
            "historical_stability_score": self.historical_stability_score,
            "computation_stability_score": self.computation_stability_score,
            "confidence_factors": list(self.confidence_factors),
            "uncertainty_sources": list(self.uncertainty_sources),
        }


@dataclass(frozen=True)
class CompetitionExplanation:
    """
    Human-readable explanation of a competition assessment.
    """
    
    # Assessment identification
    assessment_id: str
    
    candidate_ids: Tuple[str, ...]
    """All candidates involved in this assessment."""
    
    timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    
    # Core findings
    primary_competition_patterns: Tuple[str, ...] = field(default_factory=tuple)
    """Main competition patterns detected."""
    
    compatibility_summary: str = ""
    """Summary of coexistence potential."""
    
    suppression_recommendations: Tuple[str, ...] = field(default_factory=tuple)
    """Suppression recommendations."""
    
    # Component breakdown
    contribution_summary: Dict[str, float] = field(default_factory=dict)
    """Component names to normalized contributions."""
    
    dominant_factors: Tuple[str, ...] = field(default_factory=tuple)
    """Most influential factors."""
    
    confidence_assessment: CompetitionConfidence = field(
        default_factory=CompetitionConfidence.low_confidence
    )
    
    def summary(self) -> str:
        """Generate a concise natural-language summary."""
        confidence_str = f"confidence: {self.confidence_assessment.score:.2f}"
        
        if self.dominant_factors:
            factors = ", ".join(
                f"{f} ({self.contribution_summary.get(f, 0):.0f}%)"
                for f in self.dominant_factors[:3]
            )
            return (
                f"Competition analysis with {confidence_str}. "
                f"Driven by: {factors}."
            )
        
        return (
            f"Competition analysis with {confidence_str}. "
            "No dominant factors identified."
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "assessment_id": self.assessment_id,
            "candidate_ids": list(self.candidate_ids),
            "timestamp_utc": self.timestamp_utc.isoformat(),
            "primary_competition_patterns": list(self.primary_competition_patterns),
            "compatibility_summary": self.compatibility_summary,
            "suppression_recommendations": list(self.suppression_recommendations),
            "contribution_summary": self.contribution_summary,
            "dominant_factors": list(self.dominant_factors),
            "confidence_assessment": self.confidence_assessment.to_dict(),
        }


@dataclass(frozen=True)
class CompetitionAssessment:
    """
    Complete competition assessment for a set of candidates.
    
    This is the primary output of Phase 4.2.4 - comprehensive evaluation
    containing all computational evidence and explanations.
    """
    
    # Identification
    assessment_id: str
    
    candidate_ids: Tuple[str, ...]
    """All candidates assessed."""
    
    timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    
    # Core assessments
    competition_matrix: CompetitionMatrix
    """Pairwise relationship matrix."""
    
    overall_competition_strength: float = 0.0
    """Total strength of competition across all candidates."""
    
    compatibility_score: float = 1.0
    """Overall coexistence potential (0.0 to 1.0)."""
    
    # Detailed breakdowns
    breakdown: CompetitionBreakdown
    """How competition was computed."""
    
    confidence: CompetitionConfidence
    """Assessment reliability score."""
    
    explanation: CompetitionExplanation
    """Human-readable rationale."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to serializable dictionary."""
        return {
            "assessment_id": self.assessment_id,
            "candidate_ids": list(self.candidate_ids),
            "timestamp_utc": self.timestamp_utc.isoformat(),
            "overall_competition_strength": self.overall_competition_strength,
            "compatibility_score": self.compatibility_score,
            "competition_matrix": self.competition_matrix.to_dict(),
            "breakdown": self.breakdown.to_dict(),
            "confidence": self.confidence.to_dict(),
            "explanation": self.explanation.to_dict(),
        }


# =============================================================================
# SUPPRESSION ASSESSMENT
# =============================================================================

@dataclass(frozen=True)
class SuppressionSummary:
    """
    High-level summary of suppression recommendations.
    """
    
    total_candidates_assessed: int = 0
    """Total candidates evaluated."""
    
    should_suppress_count: int = 0
    """Candidates recommended for suppression."""
    
    suppressions_by_strength: Dict[str, int] = field(default_factory=dict)
    """Count by strength level."""
    
    primary_suppression_reasons: Tuple[str, ...] = field(default_factory=tuple)
    """Top suppression reasons."""
    
    total_duration_recommendation_seconds: int = 0
    """Total recommended suppression time."""
    
    timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def compute(
        cls,
        suppressions: Sequence[SuppressionDescriptor],
    ) -> "SuppressionSummary":
        """Compute summary from a sequence of suppression descriptors."""
        if not suppressions:
            return cls()
        
        should_suppress_count = sum(1 for s in suppressions if s.should_suppress)
        
        strength_counts: Dict[str, int] = {}
        reasons: Dict[str, int] = {}
        total_duration = 0
        
        for sup in suppressions:
            if sup.should_suppress:
                strength = sup.suppression_type
                strength_counts[strength] = strength_counts.get(strength, 0) + 1
                
                if strength == "full":
                    reasons["resource_conflict"] = reasons.get("resource_conflict", 0) + 1
                elif strength == "partial":
                    reasons["goal_conflict"] = reasons.get("goal_conflict", 0) + 1
                
                total_duration += sup.duration_recommendation_seconds
        
        return cls(
            total_candidates_assessed=len(suppressions),
            should_suppress_count=should_suppress_count,
            suppressions_by_strength=strength_counts,
            primary_suppression_reasons=tuple(reasons.keys()),
            total_duration_recommendation_seconds=total_duration,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "total_candidates_assessed": self.total_candidates_assessed,
            "should_suppress_count": self.should_suppress_count,
            "suppressions_by_strength": self.suppressions_by_strength,
            "primary_suppression_reasons": list(self.primary_suppression_reasons),
            "total_duration_recommendation_seconds": self.total_duration_recommendation_seconds,
            "timestamp_utc": self.timestamp_utc.isoformat(),
        }


@dataclass(frozen=True)
class SuppressionAssessment:
    """
    Complete suppression assessment for a set of candidates.
    """
    
    # Identification
    assessment_id: str
    
    candidate_ids: Tuple[str, ...]
    
    timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    
    # Suppressions per candidate
    suppressions: Tuple[SuppressionDescriptor, ...] = field(default_factory=tuple)
    """Per-candidate suppression recommendations."""
    
    # Aggregate assessment
    summary: SuppressionSummary
    
    confidence: CompetitionConfidence = field(
        default_factory=CompetitionConfidence.low_confidence
    )
    
    explanation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "assessment_id": self.assessment_id,
            "candidate_ids": list(self.candidate_ids),
            "timestamp_utc": self.timestamp_utc.isoformat(),
            "suppressions": [s.to_dict() for s in self.suppressions],
            "summary": self.summary.to_dict(),
            "confidence": self.confidence.to_dict(),
        }


# =============================================================================
# DOMINANCE ASSESSMENT
# =============================================================================

@dataclass(frozen=True)
class DominanceAssessment:
    """
    Assessment of dominance relationships among candidates.
    
    Dominance represents computational influence, NOT executive authority.
    """
    
    # Candidate classification
    dominant_candidates: Tuple[str, ...] = field(default_factory=tuple)
    """Candidates with primary influence."""
    
    secondary_candidates: Tuple[str, ...] = field(default_factory=tuple)
    """Candidates with moderate influence."""
    
    supporting_candidates: Tuple[str, ...] = field(default_factory=tuple)
    """Candidates that support others."""
    
    background_candidates: Tuple[str, ...] = field(default_factory=tuple)
    """Low-influence candidates."""
    
    deferred_candidates: Tuple[str, ...] = field(default_factory=tuple)
    """Candidates recommended for deferral."""
    
    # Quantitative measures
    dominance_scores: Dict[str, float] = field(default_factory=dict)
    """Numerical dominance scores per candidate."""
    
    influence_graph: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """Dominance edges (from -> to)."""
    
    def is_dominated_by(self, candidate_id: str, by_candidate_id: str) -> bool:
        """Check if candidate is dominated by another."""
        return (
            candidate_id in self.deferred_candidates and
            by_candidate_id in self.dominant_candidates
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "dominant_candidates": list(self.dominant_candidates),
            "secondary_candidates": list(self.secondary_candidates),
            "supporting_candidates": list(self.supporting_candidates),
            "background_candidates": list(self.background_candidates),
            "deferred_candidates": list(self.deferred_candidates),
            "dominance_scores": self.dominance_scores,
            "influence_graph": [list(edge) for edge in self.influence_graph],
        }


# =============================================================================
# COMPATIBILITY ASSESSMENT
# =============================================================================

@dataclass(frozen=True)
class CompatibilityAssessment:
    """
    Assessment of whether candidates can coexist.
    
    Coexistence is computational, not behavioral.
    """
    
    # Pairwise compatibility
    compatible_pairs: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """Pairs that can coexist."""
    
    incompatible_pairs: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """Pairs that cannot coexist."""
    
    overall_compatibility_score: float = 1.0
    """Global compatibility score (0.0 to 1.0)."""
    
    # Compatibility matrix
    compatibility_matrix: Tuple[Tuple[str, str, float], ...] = field(default_factory=tuple)
    """(source, target, score) tuples."""
    
    coexistence_recommendation: str = "maintain_all"
    """
    Recommendation:
        • 'maintain_all': All can coexist
        • 'select_subset': Must select a subset
        • 'full_suppression_needed': Suppression required for all but one
    """
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "compatible_pairs": [list(p) for p in self.compatible_pairs],
            "incompatible_pairs": [list(p) for p in self.incompatible_pairs],
            "overall_compatibility_score": self.overall_compatibility_score,
            "compatibility_matrix": [
                list(triple) for triple in self.compatibility_matrix
            ],
            "coexistence_recommendation": self.coexistence_recommendation,
        }


# =============================================================================
# CONFLICT ASSESSMENT
# =============================================================================

@dataclass(frozen=True)
class ConflictAssessment:
    """
    Assessment of conflicts among candidates.
    
    Reports evidence, does NOT resolve behavior.
    """
    
    # Conflict types
    resource_conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """Candidates in resource conflict."""
    
    goal_conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """Candidates with conflicting goals."""
    
    context_conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """Candidates in contextual conflict."""
    
    temporal_conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """Candidates with temporal misalignment."""
    
    focus_conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """Candidates competing for same focus."""
    
    policy_conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """Policy constraint violations."""
    
    # Conflict metrics
    total_conflict_count: int = 0
    total_unique_candidates_involved: int = 0
    
    # Evidence details
    evidence_per_conflict_type: Dict[str, List[str]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "resource_conflicts": list(self.resource_conflicts),
            "goal_conflicts": list(self.goal_conflicts),
            "context_conflicts": list(self.context_conflicts),
            "temporal_conflicts": list(self.temporal_conflicts),
            "focus_conflicts": list(self.focus_conflicts),
            "policy_conflicts": list(self.policy_conflicts),
            "total_conflict_count": self.total_conflict_count,
            "total_unique_candidates_involved": self.total_unique_candidates_involved,
            "evidence_per_conflict_type": {
                k: list(v) for k, v in self.evidence_per_conflict_type.items()
            },
        }


# =============================================================================
# COMPETITION DIAGNOSTICS
# =============================================================================

@dataclass(frozen=True)
class CompetitionDiagnostics:
    """
    Diagnostic and tracing information for competition computation.
    
    Read-only diagnostics for debugging and monitoring.
    """
    
    # Timing
    pairwise_competition_duration_ms: float = 0.0
    """Duration of pairwise analysis."""
    
    conflict_detection_duration_ms: float = 0.0
    """Duration of conflict detection."""
    
    compatibility_analysis_duration_ms: float = 0.0
    """Duration of compatibility estimation."""
    
    suppression_estimation_duration_ms: float = 0.0
    """Duration of suppression recommendation."""
    
    dominance_analysis_duration_ms: float = 0.0
    """Duration of dominance analysis."""
    
    total_computation_time_ms: float = 0.0
    
    # Computation traces
    pairwise_analysis_traces: Tuple[str, ...] = field(default_factory=tuple)
    """Trace log entries for pairwise analysis."""
    
    suppression_traces: Tuple[str, ...] = field(default_factory=tuple)
    """Trace log entries for suppression."""
    
    dominance_traces: Tuple[str, ...] = field(default_factory=tuple)
    """Trace log entries for dominance."""
    
    # Statistics
    candidates_analyzed: int = 0
    pairs_analyzed: int = 0
    conflicts_detected: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "pairwise_competition_duration_ms": self.pairwise_competition_duration_ms,
            "conflict_detection_duration_ms": self.conflict_detection_duration_ms,
            "compatibility_analysis_duration_ms": self.compatibility_analysis_duration_ms,
            "suppression_estimation_duration_ms": self.suppression_estimation_duration_ms,
            "dominance_analysis_duration_ms": self.dominance_analysis_duration_ms,
            "total_computation_time_ms": self.total_computation_time_ms,
            "candidates_analyzed": self.candidates_analyzed,
            "pairs_analyzed": self.pairs_analyzed,
            "conflicts_detected": self.conflicts_detected,
        }


# =============================================================================
# COMPETITION STATE (for persistence)
# =============================================================================

@dataclass(frozen=True)
class CompetitionHistory:
    """
    Bounded history of competition assessments.
    
    Maintains recent assessments for continuity estimation
    and historical influence computation.
    """
    
    max_entries: int = 100
    
    _entries: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def create(cls, max_entries: int = 100) -> "CompetitionHistory":
        """Create a new history instance."""
        return cls(max_entries=max_entries)
    
    def append(self, entry: Dict[str, Any]) -> "CompetitionHistory":
        """Add a new assessment to history."""
        new_entries = self._entries + (entry,)
        
        if len(new_entries) > self.max_entries:
            new_entries = new_entries[-self.max_entries:]
        
        return dataclass_replace(self, _entries=new_entries)
    
    def get_latest(self, count: int = 1) -> Tuple[Dict[str, Any], ...]:
        """Get the most recent entries."""
        if not self._entries:
            return tuple()
        return self._entries[-count:]
    
    def continuity_score(self) -> float:
        """Estimate competition pattern continuity."""
        if len(self._entries) < 2:
            return 0.5
        
        # Simple variance-based continuity
        scores = [e.get("overall_competition_strength", 0.5) for e in self._entries]
        avg = sum(scores) / len(scores)
        variance = sum((s - avg) ** 2 for s in scores) / len(scores)
        
        return clamp(1.0 / (1.0 + variance))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "max_entries": self.max_entries,
            "entry_count": len(self._entries),
            "continuity_score": self.continuity_score(),
        }


@dataclass(frozen=True)
class CompetitionSnapshots:
    """
    Immutable snapshots of competition state at specific points.
    
    Used for replay, diagnostics, and auditing.
    """
    
    max_snapshots: int = 50
    _snapshots: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def create(cls, max_snapshots: int = 50) -> "CompetitionSnapshots":
        """Create a new snapshot container."""
        return cls(max_snapshots=max_snapshots)
    
    def capture(
        self,
        timestamp_utc: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Capture current state as an immutable snapshot."""
        if timestamp_utc is None:
            from datetime import datetime
            timestamp_utc = datetime.utcnow()
        
        snapshot = {
            "timestamp_utc": timestamp_utc.isoformat(),
            "metadata": metadata or {},
            "state_id": f"snapshot_{len(self._snapshots)}",
        }
        
        new_snapshots = self._snapshots + (snapshot,)
        if len(new_snapshots) > self.max_snapshots:
            new_snapshots = new_snapshots[-self.max_snapshots:]
        
        return snapshot
    
    def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get the most recent snapshot."""
        if not self._snapshots:
            return None
        return self._snapshots[-1]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "max_snapshots": self.max_snapshots,
            "snapshot_count": len(self._snapshots),
        }


@dataclass(frozen=True)
class SuppressionState:
    """
    Persistent state for suppression computation subsystem.
    
    Maintains historical information and configuration while
    remaining immutable between assessment cycles.
    """
    
    history: CompetitionHistory = field(default_factory=CompetitionHistory.create)
    snapshots: CompetitionSnapshots = field(default_factory=CompetitionSnapshots.create)
    
    default_suppression_threshold: float = 0.7
    
    state_id: str = field(default_factory=lambda: f"suppression_state_{id(object())}")
    
    def update_history(
        self,
        assessment_result: Dict[str, Any],
    ) -> "SuppressionState":
        """Update history with a new suppression assessment."""
        return dataclass_replace(
            self,
            history=self.history.append(assessment_result),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "state_id": self.state_id,
            "history": self.history.to_dict(),
            "snapshots": self.snapshots.to_dict(),
            "default_suppression_threshold": self.default_suppression_threshold,
        }


@dataclass(frozen=True)
class CompetitionState:
    """
    Persistent state for the competition computation subsystem.
    
    Maintains historical information and configuration while
    remaining immutable between assessment cycles.
    """
    
    history: CompetitionHistory = field(default_factory=CompetitionHistory.create)
    snapshots: CompetitionSnapshots = field(default_factory=CompetitionSnapshots.create)
    
    # Configuration (immutable once set)
    default_competition_threshold: float = 0.5
    default_compatibility_threshold: float = 0.7
    
    state_id: str = field(default_factory=lambda: f"competition_state_{id(object())}")
    
    def update_history(
        self,
        assessment_result: Dict[str, Any],
    ) -> "CompetitionState":
        """Update history with a new competition assessment."""
        return dataclass_replace(
            self,
            history=self.history.append(assessment_result),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "state_id": self.state_id,
            "history": self.history.to_dict(),
            "snapshots": self.snapshots.to_dict(),
            "default_competition_threshold": self.default_competition_threshold,
            "default_compatibility_threshold": self.default_compatibility_threshold,
        }


# =============================================================================
# COMPUTATIONAL ESTIMATORS (ALGORITHMS)
# =============================================================================

def dataclass_replace(obj: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass instance.
    
    This is needed because frozen dataclasses don't allow direct assignment.
    The standard library's dataclasses.replace doesn't work with deeply nested
    frozen structures as well as this custom implementation.
    """
    if hasattr(obj, "__dataclass_fields__"):
        # Get current field values
        current = {field: getattr(obj, field) for field in obj.__dataclass_fields__}
        
        # Update with new values
        current.update(kwargs)
        
        # Create new instance
        return type(obj)(**current)
    
    raise TypeError(f"Cannot replace fields on non-dataclass: {type(obj)}")


# =============================================================================
# PAIRWISE COMPETITION ANALYZER
# =============================================================================

@dataclass
class CompetitionAnalyzer:
    """
    Analyzes pairwise competition relationships between candidates.
    
    For each pair of candidates, determines:
        • Whether they are independent, compatible, or competing
        • The strength and type of their relationship
        • Which is dominant (if applicable)
    
    NO BEHAVIOR IS IMPLEMENTED. This only computes relationships.
    """
    
    # Configuration
    competition_threshold: float = 0.5
    
    def analyze_pair(
        self,
        candidate_a: FocusCandidate,
        candidate_b: FocusCandidate,
    ) -> CompetitionMatrixEntry:
        """
        Analyze the relationship between two candidates.
        
        Args:
            candidate_a: First candidate
            candidate_b: Second candidate
            
        Returns:
            Matrix entry describing their relationship
        """
        # Compute pairwise metrics
        resource_overlap = self._compute_resource_overlap(
            candidate_a, candidate_b
        )
        
        goal_conflict = self._compute_goal_conflict(candidate_a, candidate_b)
        
        context_compatibility = self._compute_context_compatibility(
            candidate_a, candidate_b
        )
        
        temporal_overlap = self._compute_temporal_overlap(candidate_a, candidate_b)
        
        # Determine relationship type based on metrics
        competition_strength = (
            resource_overlap * 0.3 +
            goal_conflict * 0.4 +
            (1 - context_compatibility) * 0.2 +
            temporal_overlap * 0.1
        )
        
        compatibility_score = (
            context_compatibility * 0.5 +
            (1 - competition_strength) * 0.5
        )
        
        # Determine relationship type
        if competition_strength < self.competition_threshold:
            if compatibility_score > 0.8:
                relationship_type = CompetitionRelationship.COMPATIBLE
            else:
                relationship_type = CompetitionRelationship.INDEPENDENT
        elif goal_conflict > 0.7 and context_compatibility < 0.3:
            relationship_type = CompetitionRelationship.MUTUALLY_EXCLUSIVE
        elif goal_conflict > 0.5 or resource_overlap > 0.6:
            relationship_type = CompetitionRelationship.COMPETITIVE
        else:
            relationship_type = CompetitionRelationship.COMPETITIVE
        
        # Determine dominance direction
        dominance_direction = "neutral"
        
        if hasattr(candidate_a, 'priority_descriptor') and candidate_a.priority_descriptor:
            priority_a = candidate_a.priority_descriptor.base_priority
        else:
            priority_a = 0.5
            
        if hasattr(candidate_b, 'priority_descriptor') and candidate_b.priority_descriptor:
            priority_b = candidate_b.priority_descriptor.base_priority
        else:
            priority_b = 0.5
        
        if priority_a > priority_b * 1.2:
            dominance_direction = "source"
        elif priority_b > priority_a * 1.2:
            dominance_direction = "target"
        
        # Generate explanation
        explanation_parts = []
        if resource_overlap > 0.5:
            explanation_parts.append("high resource overlap")
        if goal_conflict > 0.5:
            explanation_parts.append("goal conflict detected")
        if context_compatibility < 0.5:
            explanation_parts.append("context incompatibility")
        
        if explanation_parts:
            explanation = f"Relationship: {relationship_type}. " + ", ".join(explanation_parts)
        else:
            explanation = f"Candidates are {relationship_type}"
        
        return CompetitionMatrixEntry(
            source_id=candidate_a.target.target_id.value,
            target_id=candidate_b.target.target_id.value,
            competition_strength=clamp(competition_strength),
            compatibility_score=clamp(compatibility_score),
            relationship_type=relationship_type,
            resource_overlap=clamp(resource_overlap),
            goal_conflict=clamp(goal_conflict),
            priority_ratio=priority_a / max(priority_b, 0.01) if priority_b > 0 else 1.0,
            dominance_direction=dominance_direction,
            explanation=explanation,
        )
    
    def _compute_resource_overlap(
        self,
        candidate_a: FocusCandidate,
        candidate_b: FocusCandidate,
    ) -> float:
        """Compute resource overlap between two candidates."""
        # For now, use a simple heuristic based on semantic categories
        if candidate_a.target.semantic_category == candidate_b.target.semantic_category:
            return 0.8
        elif candidate_a.target.semantic_category.startswith(
            candidate_b.target.semantic_category[:4]
        ):
            return 0.5
        else:
            return 0.2
    
    def _compute_goal_conflict(
        self,
        candidate_a: FocusCandidate,
        candidate_b: FocusCandidate,
    ) -> float:
        """Compute goal conflict between two candidates."""
        # Simple heuristic: different semantic categories suggest some conflict
        if candidate_a.target.semantic_category != candidate_b.target.semantic_category:
            return 0.5
        else:
            return 0.2
    
    def _compute_context_compatibility(
        self,
        candidate_a: FocusCandidate,
        candidate_b: FocusCandidate,
    ) -> float:
        """Compute context compatibility between two candidates."""
        # Assume compatible unless categories are very different
        if candidate_a.target.semantic_category == candidate_b.target.semantic_category:
            return 1.0
        elif len(set(candidate_a.target.semantic_category) & 
                 set(candidate_b.target.semantic_category)) > 3:
            return 0.7
        else:
            return 0.5
    
    def _compute_temporal_overlap(
        self,
        candidate_a: FocusCandidate,
        candidate_b: FocusCandidate,
    ) -> float:
        """Compute temporal overlap between two candidates."""
        # Simple heuristic based on evaluation timestamps
        if hasattr(candidate_a, 'evaluation_timestamp_utc') and hasattr(candidate_b, 'evaluation_timestamp_utc'):
            return 0.8
        else:
            return 0.5
    
    def analyze_all(
        self,
        candidates: Sequence[FocusCandidate],
    ) -> Tuple[CompetitionMatrixEntry, ...]:
        """
        Analyze all pairwise relationships in a set of candidates.
        
        Args:
            candidates: List of candidates to analyze
            
        Returns:
            Tuple of all pairwise matrix entries
        """
        if len(candidates) < 2:
            return tuple()
        
        results = []
        for i, candidate_a in enumerate(candidates):
            for candidate_b in candidates[i + 1:]:
                entry = self.analyze_pair(candidate_a, candidate_b)
                results.append(entry)
        
        return tuple(results)


# =============================================================================
# CONFLICT DETECTOR
# =============================================================================

@dataclass
class ConflictDetector:
    """
    Detects conflicts among candidates.
    
    Reports evidence of resource, goal, context, temporal, and policy
    conflicts. Does NOT resolve conflicts - only identifies them.
    """
    
    resource_conflict_threshold: float = 0.6
    goal_conflict_threshold: float = 0.5
    
    def detect_all(
        self,
        candidates: Sequence[FocusCandidate],
        context_projection: Optional[Dict[str, Any]] = None,
    ) -> ConflictAssessment:
        """
        Detect all conflicts among the given candidates.
        
        Args:
            candidates: Candidates to analyze
            context_projection: Current execution context (optional)
            
        Returns:
            Conflict assessment with evidence of all detected conflicts
        """
        # Collect all conflict types
        resource_conflicts = []
        goal_conflicts = []
        context_conflicts = []
        temporal_conflicts = []
        focus_conflicts = []
        policy_conflicts = []
        
        candidates_seen = set()
        
        for i, candidate_a in enumerate(candidates):
            for candidate_b in candidates[i + 1:]:
                # Check resource conflict
                if self._detect_resource_conflict(candidate_a, candidate_b):
                    resource_conflicts.extend([
                        candidate_a.target.target_id.value,
                        candidate_b.target.target_id.value
                    ])
                
                # Check goal conflict
                if self._detect_goal_conflict(candidate_a, candidate_b):
                    goal_conflicts.extend([
                        candidate_a.target.target_id.value,
                        candidate_b.target.target_id.value
                    ])
                
                # Check context conflict
                if self._detect_context_conflict(candidate_a, candidate_b):
                    context_conflicts.extend([
                        candidate_a.target.target_id.value,
                        candidate_b.target.target_id.value
                    ])
                
                candidates_seen.update([
                    candidate_a.target.target_id.value,
                    candidate_b.target.target_id.value
                ])
        
        return ConflictAssessment(
            resource_conflicts=tuple(resource_conflicts),
            goal_conflicts=tuple(goal_conflicts),
            context_conflicts=tuple(context_conflicts),
            temporal_conflicts=tuple(temporal_conflicts),
            focus_conflicts=tuple(focus_conflicts),
            policy_conflicts=tuple(policy_conflicts),
            total_conflict_count=(
                len(set(resource_conflicts)) +
                len(set(goal_conflicts)) +
                len(set(context_conflicts))
            ),
            total_unique_candidates_involved=len(candidates_seen),
            evidence_per_conflict_type={
                "resource": resource_conflicts,
                "goal": goal_conflicts,
                "context": context_conflicts,
            },
        )
    
    def _detect_resource_conflict(
        self,
        candidate_a: FocusCandidate,
        candidate_b: FocusCandidate,
    ) -> bool:
        """Check if candidates have a resource conflict."""
        # Simple heuristic
        return (
            candidate_a.target.semantic_category == 
            candidate_b.target.semantic_category and
            hasattr(candidate_a, 'priority_descriptor') and
            hasattr(candidate_b, 'priority_descriptor')
        )
    
    def _detect_goal_conflict(
        self,
        candidate_a: FocusCandidate,
        candidate_b: FocusCandidate,
    ) -> bool:
        """Check if candidates have a goal conflict."""
        return (
            candidate_a.target.semantic_category != 
            candidate_b.target.semantic_category
        )
    
    def _detect_context_conflict(
        self,
        candidate_a: FocusCandidate,
        candidate_b: FocusCandidate,
    ) -> bool:
        """Check if candidates have a context conflict."""
        # Simplified for now
        return False


# =============================================================================
# COMPATIBILITY ESTIMATOR
# =============================================================================

@dataclass
class CompatibilityEstimator:
    """
    Estimates whether candidates can coexist computationally.
    
    Coexistence is about computational compatibility, not behavioral decisions.
    """
    
    compatibility_threshold: float = 0.7
    
    def estimate_all(
        self,
        candidates: Sequence[FocusCandidate],
    ) -> Tuple[Tuple[str, str], ...]:
        """
        Estimate pairwise compatibility among all candidates.
        
        Args:
            candidates: Candidates to analyze
            
        Returns:
            Tuple of compatible pairs (source_id, target_id)
        """
        if len(candidates) < 2:
            return tuple()
        
        compatible_pairs = []
        
        for i, candidate_a in enumerate(candidates):
            for candidate_b in candidates[i + 1:]:
                compatibility = self._estimate_compatibility(candidate_a, candidate_b)
                
                if compatibility >= self.compatibility_threshold:
                    compatible_pairs.append((
                        candidate_a.target.target_id.value,
                        candidate_b.target.target_id.value
                    ))
        
        return tuple(compatible_pairs)
    
    def _estimate_compatibility(
        self,
        candidate_a: FocusCandidate,
        candidate_b: FocusCandidate,
    ) -> float:
        """Estimate compatibility between two candidates."""
        # Base score from semantic categories
        if candidate_a.target.semantic_category == candidate_b.target.semantic_category:
            base_score = 0.8
        else:
            base_score = 0.5
        
        # Adjust for priority alignment
        try:
            priority_a = (
                candidate_a.priority_descriptor.base_priority
                if hasattr(candidate_a, 'priority_descriptor') and 
                   candidate_a.priority_descriptor else 0.5
            )
            priority_b = (
                candidate_b.priority_descriptor.base_priority
                if hasattr(candidate_b, 'priority_descriptor') and 
                   candidate_b.priority_descriptor else 0.5
            )
            
            # Higher priority candidates are more compatible with similar ones
            priority_diff = abs(priority_a - priority_b)
            priority_adjustment = 1.0 - (priority_diff * 0.3)
        except:
            priority_adjustment = 1.0
        
        return clamp(base_score * priority_adjustment)


# =============================================================================
# SUPPRESSION ESTIMATOR
# =============================================================================

@dataclass
class SuppressionEstimator:
    """
    Estimates suppression recommendations for candidates.
    
    Recommends which candidates should be suppressed, with what strength,
    and for how long. Does NOT perform suppression.
    """
    
    suppression_threshold: float = 0.7
    
    def estimate_all(
        self,
        candidates: Sequence[FocusCandidate],
        competition_matrix: Optional[CompetitionMatrix] = None,
        active_objectives: Optional[Sequence[str]] = None,
    ) -> Tuple[SuppressionDescriptor, ...]:
        """
        Estimate suppression recommendations for all candidates.
        
        Args:
            candidates: Candidates to analyze
            competition_matrix: Pre-computed competition relationships (optional)
            active_objectives: Current objectives for context (optional)
            
        Returns:
            Tuple of suppression descriptors (one per candidate)
        """
        if not candidates:
            return tuple()
        
        suppressions = []
        
        for candidate in candidates:
            descriptor = self._estimate_suppression(
                candidate,
                competition_matrix,
                active_objectives or [],
            )
            suppressions.append(descriptor)
        
        return tuple(suppressions)
    
    def _estimate_suppression(
        self,
        candidate: FocusCandidate,
        competition_matrix: Optional[CompetitionMatrix],
        active_objectives: Sequence[str],
    ) -> SuppressionDescriptor:
        """Estimate suppression for a single candidate."""
        # Base score from priority
        base_priority = (
            candidate.priority_descriptor.base_priority
            if hasattr(candidate, 'priority_descriptor') and 
               candidate.priority_descriptor else 0.5
        )
        
        # Compute interference score
        interference_score = self._compute_interference_score(
            candidate,
            competition_matrix,
            active_objectives,
        )
        
        # Resource pressure from priority (inverted - high priority = high resource)
        resource_pressure = base_priority
        
        # Total suppression score
        suppression_score = (
            resource_pressure * 0.3 +
            interference_score * 0.7
        )
        
        # Determine recommendation
        should_suppress = suppression_score >= self.suppression_threshold
        
        if should_suppress:
            if suppression_score > 0.9:
                suppression_type = "full"
                duration_seconds = 3600  # 1 hour
            elif suppression_score > 0.8:
                suppression_type = "partial"
                duration_seconds = 600  # 10 minutes
            else:
                suppression_type = "temporary"
                duration_seconds = 300  # 5 minutes
        else:
            suppression_type = "none"
            duration_seconds = 0
        
        return SuppressionDescriptor(
            should_suppress=should_suppress,
            suppression_strength=clamp(suppression_score),
            suppression_type=suppression_type,
            duration_recommendation_seconds=duration_seconds,
            suppresses_candidates=tuple(),  # This candidate doesn't suppress others
        )
    
    def _compute_interference_score(
        self,
        candidate: FocusCandidate,
        competition_matrix: Optional[CompetitionMatrix],
        active_objectives: Sequence[str],
    ) -> float:
        """Compute how much this candidate interferes with others."""
        if not competition_matrix:
            return 0.3
        
        # Count competing relationships
        competitors = competition_matrix.get_competitors(
            candidate.target.target_id.value
        )
        
        # Interference is proportional to number of competitors
        interference = min(1.0, len(competitors) * 0.2)
        
        return interference


# =============================================================================
# DOMINANCE ANALYZER
# =============================================================================

@dataclass
class DominanceAnalyzer:
    """
    Analyzes dominance relationships among candidates.
    
    Determines which candidates have computational influence over others.
    Dominance is NOT executive authority - it's a computational relationship.
    """
    
    dominance_threshold: float = 0.7
    
    def analyze_all(
        self,
        candidates: Sequence[FocusCandidate],
        competition_matrix: Optional[CompetitionMatrix] = None,
    ) -> DominanceAssessment:
        """
        Analyze dominance relationships among all candidates.
        
        Args:
            candidates: Candidates to analyze
            competition_matrix: Pre-computed competition matrix (optional)
            
        Returns:
            Dominance assessment with classifications and scores
        """
        if not candidates:
            return DominanceAssessment()
        
        # Compute dominance scores for each candidate
        dominance_scores = {}
        
        for candidate in candidates:
            score = self._compute_dominance_score(
                candidate,
                competition_matrix,
            )
            dominance_scores[candidate.target.target_id.value] = score
        
        # Classify candidates based on scores
        sorted_candidates = sorted(
            candidates,
            key=lambda c: dominance_scores.get(c.target.target_id.value, 0.5),
            reverse=True,
        )
        
        n = len(sorted_candidates)
        if n == 0:
            return DominanceAssessment()
        
        # Calculate classification boundaries
        dominant_threshold = (
            sorted_candidates[int(n * 0.7)].target.target_id.value 
            if n >= 3 else None
        )
        secondary_threshold = (
            sorted_candidates[int(n * 0.9)].target.target_id.value 
            if n >= 5 else None
        )
        
        dominant = []
        secondary = []
        supporting = []
        background = []
        deferred = []
        
        for candidate in sorted_candidates:
            score = dominance_scores.get(candidate.target.target_id.value, 0.5)
            
            if score > self.dominance_threshold:
                dominant.append(candidate.target.target_id.value)
            elif score > 0.6:
                secondary.append(candidate.target.target_id.value)
            elif score > 0.4:
                supporting.append(candidate.target.target_id.value)
            elif score > 0.2:
                background.append(candidate.target.target_id.value)
            else:
                deferred.append(candidate.target.target_id.value)
        
        # Build influence graph (dominant -> suppressed)
        influence_graph = []
        for candidate in sorted_candidates:
            score = dominance_scores.get(candidate.target.target_id.value, 0.5)
            if score > self.dominance_threshold:
                # Find candidates this dominates
                for other_candidate in sorted_candidates:
                    other_score = dominance_scores.get(
                        other_candidate.target.target_id.value, 0.5
                    )
                    if (
                        candidate != other_candidate and
                        score > other_score * 1.2
                    ):
                        influence_graph.append((
                            candidate.target.target_id.value,
                            other_candidate.target.target_id.value,
                        ))
        
        return DominanceAssessment(
            dominant_candidates=tuple(dominant),
            secondary_candidates=tuple(secondary),
            supporting_candidates=tuple(supporting),
            background_candidates=tuple(background),
            deferred_candidates=tuple(deferred),
            dominance_scores=dominance_scores,
            influence_graph=tuple(influence_graph),
        )
    
    def _compute_dominance_score(
        self,
        candidate: FocusCandidate,
        competition_matrix: Optional[CompetitionMatrix],
    ) -> float:
        """Compute a numerical dominance score for a candidate."""
        # Base from priority
        base_priority = (
            candidate.priority_descriptor.base_priority
            if hasattr(candidate, 'priority_descriptor') and 
               candidate.priority_descriptor else 0.5
        )
        
        score = base_priority * 0.6
        
        # Add influence from competition matrix
        if competition_matrix:
            competitors = competition_matrix.get_competitors(
                candidate.target.target_id.value
            )
            
            # More dominant if fewer competitors (less competition)
            if len(competitors) < 2:
                score += 0.1
            
            # Check dominance direction in matrix entries
            for entry in competition_matrix.entries:
                if (
                    entry.dominance_direction == "source" and
                    entry.source_id == candidate.target.target_id.value
                ):
                    score += 0.15
                elif (
                    entry.dominance_direction == "target" and
                    entry.target_id == candidate.target.target_id.value
                ):
                    score -= 0.1
        
        return clamp(score)


# =============================================================================
# COMPETITION CONFIDENCE ESTIMATOR
# =============================================================================

@dataclass
class CompetitionConfidenceEstimator:
    """
    Estimates confidence in competition assessments.
    
    Confidence depends on data quality, consistency, and historical patterns.
    """
    
    def estimate_all(
        self,
        candidates: Sequence[FocusCandidate],
        competition_matrix: Optional[CompetitionMatrix] = None,
        history: Optional[CompetitionHistory] = None,
    ) -> CompetitionConfidence:
        """
        Estimate confidence in the overall assessment.
        
        Args:
            candidates: Candidates assessed
            competition_matrix: Computed matrix (optional)
            history: Historical assessments (optional)
            
        Returns:
            Confidence assessment with detailed factors
        """
        # Input completeness score
        input_completeness = 0.5
        
        if candidates:
            # Check how many have priority descriptors
            with_priority = sum(
                1 for c in candidates 
                if hasattr(c, 'priority_descriptor') and c.priority_descriptor
            )
            input_completeness = clamp(with_priority / len(candidates))
        
        # Relationship consistency score
        relationship_consistency = 0.5
        
        if competition_matrix:
            entries = competition_matrix.entries
            
            # Check for consistent relationship types
            if entries:
                unique_types = set(e.relationship_type for e in entries)
                
                # More consistent if fewer relationship types (simpler structure)
                consistency_score = max(0.3, 1.0 - len(unique_types) * 0.1)
                relationship_consistency = clamp(consistency_score)
        
        # Historical stability score
        historical_stability = 0.5
        
        if history:
            continuity = history.continuity_score()
            historical_stability = continuity
        
        # Computation stability (always high for deterministic algorithms)
        computation_stability = 0.9
        
        # Overall confidence
        overall_confidence = (
            input_completeness * 0.25 +
            relationship_consistency * 0.30 +
            historical_stability * 0.25 +
            computation_stability * 0.20
        )
        
        return CompetitionConfidence(
            score=overall_confidence,
            input_completeness_score=input_completeness,
            relationship_consistency_score=relationship_consistency,
            historical_stability_score=historical_stability,
            computation_stability_score=computation_stability,
            confidence_factors=(
                "Deterministic computation",
                "Frozen dataclass outputs",
            ),
            uncertainty_sources=(
                f"Input completeness: {input_completeness:.2f}",
            ) if input_completeness < 0.8 else (),
        )


# =============================================================================
# PUBLIC API SUMMARY
# =============================================================================

"""
Phase 4.2.4 Competition and Suppression Model - Complete

This module provides the canonical implementation of:

1. COMPETITION ANALYSIS:
   • CompetitionAnalyzer: Pairwise relationship analysis
   • ConflictDetector: Resource, goal, context conflict detection
   • CompetitionMatrix: Immutable pairwise relationship storage

2. SUPPRESSION MODEL:
   • SuppressionEstimator: suppression recommendations
   • SuppressionAssessment: Complete suppression evaluation

3. DOMINANCE ANALYSIS:
   • DominanceAnalyzer: Candidate influence estimation
   • DominanceAssessment: Classification and scores

4. COMPATIBILITY ESTIMATION:
   • CompatibilityEstimator: Coexistence potential assessment

5. CONFIDENCE & EXPLAINABILITY:
   • CompetitionConfidenceEstimator: Assessment reliability
   • Comprehensive explanation generation

ALL OUTPUTS ARE IMMUTABLE (frozen dataclasses).
NO BEHAVIOR IS IMPLEMENTED - only computational assessments.
"""