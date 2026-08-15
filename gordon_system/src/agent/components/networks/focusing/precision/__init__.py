# Precision Allocation and Computational Resource Budgeting
# =========================================================
#
# Phase 4.2.5: Canonical computational implementation of attentional precision
# estimation, computational bandwidth recommendation, and resource budgeting.
#
# This phase estimates how computational resources SHOULD be distributed among
# FocusTargets - but does NOT allocate runtime resources, schedule execution,
# or own any behavioral policy.

"""
Precision Allocation and Computational Resource Budgeting for Phase 4.2.5.

This module implements Gordon's canonical precision allocation model:

ARCHITECTURAL RESPONSIBILITY:
    This subsystem owns:
        • Precision estimation (focus sharpness, discrimination, ambiguity)
        • Uncertainty analysis (representation, context, priority uncertainty)
        • Bandwidth estimation (recommended computational bandwidth)
        • Resource demand estimation (processing effort, iterations, memory)
        • Budget recommendation (computational budget, relative allocation)
        • Allocation recommendations (percentage, effort, reservation)
        • Confidence estimation for all assessments
        • Explainability of all recommendations
    
    This subsystem NEVER owns:
        • Runtime resource allocation
        • CPU scheduling
        • GPU scheduling
        • Memory management
        • Behavior
        • Planning
        • Execution

INPUTS:
    FocusCandidate: The target under assessment (external projection)
    PriorityAssessment: Already computed priorities (external)
    CompetitionAssessment: Competition analysis results (external)
    SuppressionAssessment: Suppression recommendations (external)
    ContextProjection: Current execution context (external)
    PolicyConstraints: Policy guidance (external)
    ResourceConstraints: Resource limits (external)
    HistoricalPrecisionState: Previous precision values (external)

OUTPUTS (immutable recommendations):
    PrecisionAssessment: Complete precision evaluation
    BandwidthAssessment: Recommended bandwidth allocation
    BudgetAssessment: Recommended budget allocation
    AllocationRecommendation: Recommended resource distribution
    PrecisionConfidence: Assessment reliability score
    PrecisionExplanation: Human-readable rationale

All computations are deterministic, explainable, and stateless.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)
from datetime import datetime
import math


# =============================================================================
# PUBLIC EXPORTS - Phase 4.2.5 computational models and algorithms
# =============================================================================

__all__ = [
    # Estimators (algorithms)
    "PrecisionEstimator",
    "UncertaintyEstimator",
    "BandwidthEstimator",
    "ResourceDemandEstimator",
    "BudgetEstimator",
    "AllocationRecommender",
    "PrecisionConfidenceEstimator",
    
    # Immutable assessment outputs
    "PrecisionAssessment",
    "BandwidthAssessment",
    "BudgetAssessment",
    "AllocationRecommendation",
    "PrecisionExplanation",
    "PrecisionSummary",
    "ResourceDemandEstimate",
    
    # State (for persistence)
    "PrecisionState",
    "AllocationState",
    "BandwidthState",
    "BudgetHistory",
    "PrecisionSnapshots",
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
# PRECISION DESCRIPTORS - Immutable data structures
# =============================================================================


@dataclass(frozen=True)
class PrecisionDescriptor:
    """
    Describes precision characteristics without computing them.
    
    Contains only the estimated values, not algorithms.
    """
    
    focus_sharpness: float  # 0.0 to 1.0 - How narrowly focused
    required_discrimination: float  # 0.0 to 1.0 - Needed discrimination level
    expected_uncertainty: float  # 0.0 to 1.0 - Expected ambiguity level
    computational_resolution: int = 100  # Units of computational resolution needed
    processing_depth: int = 3  # Number of reasoning layers
    
    bandwidth_preference: str = "moderate"  # coarse, moderate, fine, ultra_fine
    uncertainty_tolerance: float = 0.5  # 0.0 to 1.0 - How much uncertainty is acceptable
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "focus_sharpness": self.focus_sharpness,
            "required_discrimination": self.required_discrimination,
            "expected_uncertainty": self.expected_uncertainty,
            "computational_resolution": self.computational_resolution,
            "processing_depth": self.processing_depth,
            "bandwidth_preference": self.bandwidth_preference,
            "uncertainty_tolerance": self.uncertainty_tolerance,
        }


@dataclass(frozen=True)
class PrecisionContribution:
    """
    A single contribution to a precision assessment.
    """
    
    source: str  # Where this came from
    weight: float = 1.0  # Weight of this contribution
    raw_value: float = 0.5  # Raw score (0.0 to 1.0)
    effect: str = "positive"  # positive, negative, neutral
    
    def contribution_score(self) -> float:
        """Calculate weighted contribution."""
        if self.effect == "negative":
            return -self.raw_value * self.weight
        return self.raw_value * self.weight
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "source": self.source,
            "weight": self.weight,
            "raw_value": self.raw_value,
            "effect": self.effect,
            "contribution_score": self.contribution_score(),
        }


@dataclass(frozen=True)
class PrecisionEvidence:
    """
    Raw evidence components for a precision assessment.
    
    Contains all computational factors without aggregation.
    """
    
    focus_sharpness_estimate: float = 0.5
    discrimination_requirement: float = 0.5
    context_uncertainty: float = 0.5
    representation_uncertainty: float = 0.5
    
    # Component details for explainability
    components: Tuple[PrecisionContribution, ...] = field(default_factory=tuple)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "focus_sharpness_estimate": self.focus_sharpness_estimate,
            "discrimination_requirement": self.discrimination_requirement,
            "context_uncertainty": self.context_uncertainty,
            "representation_uncertainty": self.representation_uncertainty,
            "components": [c.to_dict() for c in self.components],
        }


# =============================================================================
# BANDWIDTH DESCRIPTORS
# =============================================================================


class BandwidthLevel:
    """
    Bandwidth classification levels.
    
    Each level describes recommended computational bandwidth allocation.
    """
    
    COARSE = "coarse"  # Broad, diffuse attention (equivalent to minimal)
    MINIMAL = "minimal"  # Bare minimum resources
    LOW = "low"  # Reduced allocation
    MODERATE = "moderate"  # Standard allocation
    HIGH = "high"  # Elevated allocation
    FINE = "fine"  # Narrow, focused attention (equivalent to fine)
    ULTRA_FINE = "ultra_fine"  # Maximum precision
    MAXIMUM = "maximum"  # Maximum resources available


@dataclass(frozen=True)
class BandwidthDescriptor:
    """
    Describes bandwidth characteristics without computing them.
    """
    
    recommended_level: str = BandwidthLevel.MODERATE
    """Recommended bandwidth level."""
    
    minimum_bandwidth: float = 0.1
    """Minimum required bandwidth (0.0 to 1.0)."""
    
    optimal_bandwidth: float = 0.5
    """Optimal bandwidth recommendation (0.0 to 1.0)."""
    
    maximum_bandwidth: float = 1.0
    """Maximum allowed bandwidth (0.0 to 1.0)."""
    
    adaptive_mode: bool = True
    """Whether bandwidth can adapt dynamically."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "recommended_level": self.recommended_level,
            "minimum_bandwidth": self.minimum_bandwidth,
            "optimal_bandwidth": self.optimal_bandwidth,
            "maximum_bandwidth": self.maximum_bandwidth,
            "adaptive_mode": self.adaptive_mode,
        }


@dataclass(frozen=True)
class BandwidthContribution:
    """
    A single contribution to bandwidth assessment.
    """
    
    source: str
    weight: float = 1.0
    raw_value: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "source": self.source,
            "weight": self.weight,
            "raw_value": self.raw_value,
            "weighted_score": self.weight * self.raw_value,
        }


@dataclass(frozen=True)
class BandwidthRecommendation:
    """
    Bandwidth recommendation with rationale.
    """
    
    recommended_bandwidth: float  # 0.0 to 1.0
    confidence: float = 0.5
    justification: str = ""
    adaptive_strategy: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "recommended_bandwidth": self.recommended_bandwidth,
            "confidence": self.confidence,
            "justification": self.justification,
            "adaptive_strategy": self.adaptive_strategy,
        }


# =============================================================================
# RESOURCE DESCRIPTORS
# =============================================================================


@dataclass(frozen=True)
class ResourceDemandDescriptor:
    """
    Describes resource demands without computing them.
    """
    
    estimated_processing_effort: float = 0.5  # 0.0 to 1.0
    expected_iterations: int = 10
    memory_pressure_estimate: float = 0.3  # 0.0 to 1.0
    reasoning_complexity: str = "moderate"  # simple, moderate, complex
    
    context_size_estimate: int = 100
    """Estimated tokens or data points needed."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "estimated_processing_effort": self.estimated_processing_effort,
            "expected_iterations": self.expected_iterations,
            "memory_pressure_estimate": self.memory_pressure_estimate,
            "reasoning_complexity": self.reasoning_complexity,
            "context_size_estimate": self.context_size_estimate,
        }


@dataclass(frozen=True)
class BudgetDescriptor:
    """
    Describes budget characteristics without computing them.
    """
    
    recommended_budget: float = 0.5  # 0.0 to 1.0
    reserved_budget: float = 0.1  # Reserved for dynamic needs
    fair_share_estimate: float = 0.2  # Expected proportional allocation
    
    budget_confidence: float = 0.5
    allocation_constraints: Tuple[str, ...] = field(default_factory=tuple)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "recommended_budget": self.recommended_budget,
            "reserved_budget": self.reserved_budget,
            "fair_share_estimate": self.fair_share_estimate,
            "budget_confidence": self.budget_confidence,
            "allocation_constraints": list(self.allocation_constraints),
        }


@dataclass(frozen=True)
class AllocationContribution:
    """
    A single contribution to allocation recommendation.
    """
    
    source: str
    weight: float = 1.0
    raw_value: float = 0.5
    allocation_percentage: float = 0.2
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "source": self.source,
            "weight": self.weight,
            "raw_value": self.raw_value,
            "allocation_percentage": self.allocation_percentage,
            "weighted_allocation": self.weight * self.allocation_percentage,
        }


# =============================================================================
# IMMUTABLE ASSESSMENT OUTPUTS
# =============================================================================


@dataclass(frozen=True)
class PrecisionAssessment:
    """
    Complete precision assessment for a single focus candidate.
    
    This is the primary output of Phase 4.2.5 - comprehensive evaluation
    containing all computational evidence and explanations.
    """
    
    # Required fields (no defaults) must come first
    target_id: str = ""
    """ID of the focus target being assessed."""
    
    timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    """When this assessment was generated."""
    
    # Primary outputs - these have defaults now to ensure proper order
    focus_sharpness: float = 0.5  # 0.0 to 1.0 - How narrowly focused
    precision_bandwidth: BandwidthLevel = BandwidthLevel.MODERATE
    
    # Detailed assessments - optional with defaults
    uncertainty_analysis: "UncertaintyAnalysis" = field(default_factory=lambda: UncertaintyAnalysis())
    bandwidth_assessment: "BandwidthAssessment" = field(default_factory=lambda: BandwidthAssessment(recommended_level="moderate"))
    resource_demand: "ResourceDemandDescriptor" = field(default_factory=ResourceDemandDescriptor)
    budget_allocation: "BudgetDescriptor" = field(default_factory=BudgetDescriptor)
    
    # Validation
    is_finite: bool = True
    """Whether all computed values are finite (not NaN/inf)."""
    
    is_normalized: bool = True
    """Whether all values are within [0.0, 1.0] bounds."""
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert assessment to serializable dictionary.
        This is the canonical export format for diagnostics and storage.
        """
        return {
            "target_id": self.target_id,
            "timestamp_utc": self.timestamp_utc.isoformat(),
            "focus_sharpness": self.focus_sharpness,
            "precision_bandwidth": self.precision_bandwidth,
            "uncertainty_analysis": self.uncertainty_analysis.to_dict(),
            "bandwidth_assessment": self.bandwidth_assessment.to_dict(),
            "resource_demand": self.resource_demand.to_dict(),
            "budget_allocation": self.budget_allocation.to_dict(),
            "is_finite": self.is_finite,
            "is_normalized": self.is_normalized,
        }


@dataclass(frozen=True)
class UncertaintyAnalysis:
    """
    Analysis of uncertainty factors in precision estimation.
    """
    
    representation_uncertainty: float = 0.5
    """Uncertainty in target representation."""
    
    context_uncertainty: float = 0.5
    """Uncertainty in current context."""
    
    priority_uncertainty: float = 0.5
    """Uncertainty in priority estimation."""
    
    competition_uncertainty: float = 0.5
    """Uncertainty from competition analysis."""
    
    prediction_uncertainty: float = 0.5
    """Uncertainty in future state predictions."""
    
    # Combined assessment
    total_uncertainty_score: Optional[float] = None
    
    def total(self) -> float:
        """Compute combined uncertainty score."""
        if self.total_uncertainty_score is not None:
            return self.total_uncertainty_score
        
        # Weighted average of uncertainty sources
        weights = {
            "representation": 0.25,
            "context": 0.20,
            "priority": 0.20,
            "competition": 0.20,
            "prediction": 0.15,
        }
        
        total = (
            self.representation_uncertainty * weights["representation"] +
            self.context_uncertainty * weights["context"] +
            self.priority_uncertainty * weights["priority"] +
            self.competition_uncertainty * weights["competition"] +
            self.prediction_uncertainty * weights["prediction"]
        )
        
        return clamp(total)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "representation_uncertainty": self.representation_uncertainty,
            "context_uncertainty": self.context_uncertainty,
            "priority_uncertainty": self.priority_uncertainty,
            "competition_uncertainty": self.competition_uncertainty,
            "prediction_uncertainty": self.prediction_uncertainty,
            "total_uncertainty_score": self.total(),
        }


@dataclass(frozen=True)
class BandwidthAssessment:
    """
    Assessment of bandwidth allocation recommendation.
    """
    
    recommended_level: str = "moderate"
    minimum_bandwidth: float = 0.1
    optimal_bandwidth: float = 0.5
    maximum_bandwidth: float = 1.0
    
    confidence: float = 0.5
    justification: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "recommended_level": self.recommended_level,
            "minimum_bandwidth": self.minimum_bandwidth,
            "optimal_bandwidth": self.optimal_bandwidth,
            "maximum_bandwidth": self.maximum_bandwidth,
            "confidence": self.confidence,
            "justification": self.justification,
        }


@dataclass(frozen=True)
class ResourceDemandEstimate:
    """
    Estimate of computational resource requirements.
    """
    
    estimated_processing_effort: float = 0.5
    expected_iterations: int = 10
    memory_pressure_estimate: float = 0.3
    reasoning_complexity: str = "moderate"
    context_size_estimate: int = 100
    
    estimated_memory_mb: Optional[float] = None
    """Estimated memory usage in MB."""
    
    estimated_time_seconds: Optional[float] = None
    """Estimated execution time in seconds."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "estimated_processing_effort": self.estimated_processing_effort,
            "expected_iterations": self.expected_iterations,
            "memory_pressure_estimate": self.memory_pressure_estimate,
            "reasoning_complexity": self.reasoning_complexity,
            "context_size_estimate": self.context_size_estimate,
            "estimated_memory_mb": self.estimated_memory_mb,
            "estimated_time_seconds": self.estimated_time_seconds,
        }


@dataclass(frozen=True)
class BudgetAssessment:
    """
    Assessment of budget allocation recommendation.
    """
    
    recommended_budget: float = 0.5  # 0.0 to 1.0
    reserved_budget: float = 0.1
    fair_share_estimate: float = 0.2
    
    confidence: float = 0.5
    constraints_applied: Tuple[str, ...] = field(default_factory=tuple)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "recommended_budget": self.recommended_budget,
            "reserved_budget": self.reserved_budget,
            "fair_share_estimate": self.fair_share_estimate,
            "confidence": self.confidence,
            "constraints_applied": list(self.constraints_applied),
        }


@dataclass(frozen=True)
class AllocationRecommendation:
    """
    Recommendation for resource allocation distribution.
    """
    
    recommended_allocation_percentage: float  # 0.0 to 1.0
    recommended_effort: float = 0.5  # Normalized effort (0.0 to 1.0)
    recommended_computational_priority: int = 50  # Relative priority rank
    
    recommended_reservation: float = 0.2  # Reserved for dynamic needs
    confidence: float = 0.5
    
    justification: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "recommended_allocation_percentage": self.recommended_allocation_percentage,
            "recommended_effort": self.recommended_effort,
            "recommended_computational_priority": self.recommended_computational_priority,
            "recommended_reservation": self.recommended_reservation,
            "confidence": self.confidence,
            "justification": self.justification,
        }


@dataclass(frozen=True)
class PrecisionConfidence:
    """
    Confidence assessment for precision estimation.
    """
    
    score: float = 0.5
    """Overall confidence in the precision estimate."""
    
    # Confidence factors
    input_completeness_score: float = 0.5
    priority_stability_score: float = 0.5
    competition_consistency_score: float = 0.5
    
    resource_knowledge_score: float = 0.5
    historical_stability_score: float = 0.5
    
    # Metadata
    confidence_factors: Tuple[str, ...] = field(default_factory=tuple)
    """Human-readable factors that increased confidence."""
    
    uncertainty_sources: Tuple[str, ...] = field(default_factory=tuple)
    """Identified sources of uncertainty."""
    
    @classmethod
    def low_confidence(cls) -> "PrecisionConfidence":
        """Create a low-confidence assessment (default fallback)."""
        return cls(
            score=0.3,
            input_completeness_score=0.4,
            priority_stability_score=0.3,
            competition_consistency_score=0.3,
            resource_knowledge_score=0.5,
            historical_stability_score=0.4,
        )
    
    @classmethod
    def high_confidence(cls) -> "PrecisionConfidence":
        """Create a high-confidence assessment."""
        return cls(
            score=0.85,
            input_completeness_score=0.9,
            priority_stability_score=0.85,
            competition_consistency_score=0.8,
            resource_knowledge_score=0.85,
            historical_stability_score=0.9,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "score": self.score,
            "input_completeness_score": self.input_completeness_score,
            "priority_stability_score": self.priority_stability_score,
            "competition_consistency_score": self.competition_consistency_score,
            "resource_knowledge_score": self.resource_knowledge_score,
            "historical_stability_score": self.historical_stability_score,
            "confidence_factors": list(self.confidence_factors),
            "uncertainty_sources": list(self.uncertainty_sources),
        }


@dataclass(frozen=True)
class PrecisionExplanation:
    """
    Human-readable explanation of a precision assessment.
    
    Contains the rationale for why this candidate received
    its precision and bandwidth values.
    """
    
    # Core assessment
    target_id: str
    """ID of the focus target being assessed."""
    
    final_focus_sharpness: float
    """The computed focus sharpness (0.0 to 1.0)."""
    
    final_bandwidth_level: str
    """The recommended bandwidth level."""
    
    # Explanation sections
    precision_justification: str
    """Why this precision level was selected."""
    
    uncertainty_justification: str
    """How uncertainty affects the recommendation."""
    
    bandwidth_justification: str
    """Why this bandwidth is recommended."""
    
    resource_justification: str
    """Resource demand rationale."""
    
    budget_justification: str
    """Budget allocation rationale."""
    
    # Component breakdown
    contribution_summary: Dict[str, float]
    """Component names to their normalized contributions."""
    
    dominant_factors: Tuple[str, ...]
    """Most influential factors in the final assessment."""
    
    confidence_assessment: PrecisionConfidence
    
    timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    """When this explanation was generated."""
    
    def summary(self) -> str:
        """
        Generate a concise natural-language summary.
        
        Example:
            "Focus sharpness 0.75 (confidence: 0.89). 
             Primarily driven by context_uncertainty (40%) and 
             discrimination_requirement (35%). Recommended bandwidth: moderate."
        """
        confidence_str = f"confidence: {self.confidence_assessment.score:.2f}"
        
        if self.dominant_factors:
            factors = ", ".join(
                f"{f} ({self.contribution_summary.get(f, 0):.0f}%)"
                for f in self.dominant_factors[:3]
            )
            return (
                f"Focus sharpness {self.final_focus_sharpness:.2f} "
                f"({confidence_str}). "
                f"Bandwidth: {self.final_bandwidth_level}. "
                f"Driven by: {factors}."
            )
        
        return (
            f"Focus sharpness {self.final_focus_sharpness:.2f} "
            f"({confidence_str}). "
            f"No dominant factors identified."
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "target_id": self.target_id,
            "final_focus_sharpness": self.final_focus_sharpness,
            "final_bandwidth_level": self.final_bandwidth_level,
            "precision_justification": self.precision_justification,
            "uncertainty_justification": self.uncertainty_justification,
            "bandwidth_justification": self.bandwidth_justification,
            "resource_justification": self.resource_justification,
            "budget_justification": self.budget_justification,
            "contribution_summary": self.contribution_summary,
            "dominant_factors": list(self.dominant_factors),
            "confidence_assessment": self.confidence_assessment.to_dict(),
            "timestamp_utc": self.timestamp_utc.isoformat(),
        }


@dataclass(frozen=True)
class PrecisionSummary:
    """
    High-level summary of precision assessments for multiple candidates.
    
    Used for reporting and diagnostics without exposing full details.
    """
    
    candidate_count: int
    """Number of candidates assessed."""
    
    average_focus_sharpness: float
    """Mean focus sharpness across all candidates."""
    
    max_focus_sharpness: float
    """Highest focus sharpness among candidates."""
    
    min_focus_sharpness: float
    """Lowest focus sharpness among candidates."""
    
    bandwidth_distribution: Dict[str, int]
    """Count of candidates per bandwidth level."""
    
    timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    """When this summary was generated."""
    
    @classmethod
    def compute(
        cls,
        assessments: Sequence[PrecisionAssessment],
    ) -> "PrecisionSummary":
        """
        Compute summary from a sequence of precision assessments.
        
        Args:
            assessments: List or tuple of PrecisionAssessment instances
            
        Returns:
            PrecisionSummary with computed statistics
        """
        if not assessments:
            return cls(
                candidate_count=0,
                average_focus_sharpness=0.0,
                max_focus_sharpness=0.0,
                min_focus_sharpness=0.0,
                bandwidth_distribution={},
            )
        
        sharpness_values = [a.focus_sharpness for a in assessments]
        n = len(sharpness_values)
        avg = sum(sharpness_values) / n
        
        # Count bandwidth distribution
        bandwidth_counts: Dict[str, int] = {}
        for a in assessments:
            level = a.precision_bandwidth
            bandwidth_counts[level] = bandwidth_counts.get(level, 0) + 1
        
        return cls(
            candidate_count=n,
            average_focus_sharpness=avg,
            max_focus_sharpness=max(sharpness_values),
            min_focus_sharpness=min(sharpness_values),
            bandwidth_distribution=bandwidth_counts,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "candidate_count": self.candidate_count,
            "average_focus_sharpness": self.average_focus_sharpness,
            "max_focus_sharpness": self.max_focus_sharpness,
            "min_focus_sharpness": self.min_focus_sharpness,
            "bandwidth_distribution": self.bandwidth_distribution,
            "timestamp_utc": self.timestamp_utc.isoformat(),
        }


# =============================================================================
# STATE CLASSES - For persistence across assessment cycles
# =============================================================================


@dataclass(frozen=True)
class PrecisionHistory:
    """
    Bounded history of precision assessments.
    
    Maintains recent precision values for continuity estimation
    and historical influence computation.
    """
    
    # Configuration
    max_entries: int = 100
    
    # Historical entries (chronological, newest at end)
    _entries: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def create(cls, max_entries: int = 100) -> "PrecisionHistory":
        """Create a new history instance."""
        return cls(max_entries=max_entries)
    
    def append(self, entry: Dict[str, Any]) -> "PrecisionHistory":
        """
        Add a new precision assessment to history.
        
        Maintains bounded capacity by removing oldest entries if needed.
        """
        new_entries = self._entries + (entry,)
        
        # Trim to max length (keep newest)
        if len(new_entries) > self.max_entries:
            new_entries = new_entries[-self.max_entries:]
        
        return dataclass_replace(self, _entries=new_entries)
    
    def get_latest(self, count: int = 1) -> Tuple[Dict[str, Any], ...]:
        """Get the most recent entries."""
        if not self._entries:
            return tuple()
        return self._entries[-count:]
    
    def get_precision_history(self) -> Tuple[float, ...]:
        """Extract just the focus sharpness values from history."""
        return tuple(
            entry.get("focus_sharpness", 0.5)
            for entry in self._entries
        )
    
    def continuity_score(self) -> float:
        """
        Estimate focus continuity from historical patterns.
        
        Higher score indicates more stable, continuous precision.
        """
        precisions = self.get_precision_history()
        
        if len(precisions) < 2:
            return 0.5
        
        # Compute variance (lower = more stable/continuous)
        avg = sum(precisions) / len(precisions)
        variance = sum((p - avg) ** 2 for p in precisions) / len(precisions)
        
        # Convert to continuity score (inverse relationship)
        # Variance of 0 → score 1.0, variance > 1.0 → score approaches 0
        continuity = 1.0 / (1.0 + variance)
        
        return clamp(continuity)
    
    def trend_direction(self) -> str:
        """
        Determine historical precision trend direction.
        
        Returns: 'increasing', 'decreasing', or 'stable'
        """
        precisions = self.get_precision_history()
        
        if len(precisions) < 2:
            return "unknown"
        
        # Simple linear trend detection
        n = len(precisions)
        first_half_avg = sum(precisions[:n//2]) / (n//2)
        second_half_avg = sum(precisions[n//2:]) / (n - n//2)
        
        diff = second_half_avg - first_half_avg
        
        if diff > 0.1:
            return "increasing"
        elif diff < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "max_entries": self.max_entries,
            "entry_count": len(self._entries),
            "continuity_score": self.continuity_score(),
            "trend_direction": self.trend_direction(),
            "latest_precisions": list(self.get_precision_history()[-10:]),
        }


@dataclass(frozen=True)
class PrecisionSnapshots:
    """
    Immutable snapshots of precision state at specific points in time.
    
    Used for replay, diagnostics, and auditing without modifying live state.
    """
    
    # Configuration
    max_snapshots: int = 50
    
    # Snapshots (chronological, newest at end)
    _snapshots: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def create(cls, max_snapshots: int = 50) -> "PrecisionSnapshots":
        """Create a new snapshot container."""
        return cls(max_snapshots=max_snapshots)
    
    def capture(
        self,
        timestamp_utc: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Capture current state as an immutable snapshot.
        
        Args:
            timestamp_utc: When to record (defaults to now)
            metadata: Additional context for the snapshot
            
        Returns:
            The captured snapshot dictionary
        """
        if timestamp_utc is None:
            timestamp_utc = datetime.utcnow()
        
        snapshot = {
            "timestamp_utc": timestamp_utc.isoformat(),
            "metadata": metadata or {},
            "state_id": f"snapshot_{len(self._snapshots)}",
        }
        
        # Add to snapshots (maintaining bounded capacity)
        new_snapshots = self._snapshots + (snapshot,)
        if len(new_snapshots) > self.max_snapshots:
            new_snapshots = new_snapshots[-self.max_snapshots:]
        
        return snapshot
    
    def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get the most recent snapshot, if any."""
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
class PrecisionState:
    """
    Persistent state for the precision computation subsystem.
    
    Maintains historical information and configuration while
    remaining immutable between assessment cycles.
    """
    
    # History tracking
    history: PrecisionHistory = field(default_factory=PrecisionHistory.create)
    
    # Snapshots
    snapshots: PrecisionSnapshots = field(default_factory=PrecisionSnapshots.create)
    
    # Configuration (immutable once set)
    default_weight_sharpness: float = 0.35
    default_weight_discrimination: float = 0.25
    default_weight_uncertainty: float = 0.15
    default_weight_priority_influence: float = 0.15
    default_weight_context_fit: float = 0.10
    
    # Metadata
    state_id: str = field(default_factory=lambda: f"precision_state_{id(object())}")
    
    def update_history(
        self,
        assessment_result: Dict[str, Any],
    ) -> "PrecisionState":
        """
        Update history with a new precision assessment result.
        
        Args:
            assessment_result: Result dictionary from PrecisionAssessment
            
        Returns:
            New PrecisionState with updated history
        """
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
            "weights": {
                "sharpness": self.default_weight_sharpness,
                "discrimination": self.default_weight_discrimination,
                "uncertainty": self.default_weight_uncertainty,
                "priority_influence": self.default_weight_priority_influence,
                "context_fit": self.default_weight_context_fit,
            },
        }


@dataclass(frozen=True)
class AllocationHistory:
    """
    Bounded history of allocation recommendations.
    
    Maintains recent allocation values for continuity estimation
    and historical influence computation.
    """
    
    max_entries: int = 100
    _entries: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def create(cls, max_entries: int = 100) -> "AllocationHistory":
        """Create a new history instance."""
        return cls(max_entries=max_entries)
    
    def append(self, entry: Dict[str, Any]) -> "AllocationHistory":
        """Add a new allocation recommendation to history."""
        new_entries = self._entries + (entry,)
        
        if len(new_entries) > self.max_entries:
            new_entries = new_entries[-self.max_entries:]
        
        return dataclass_replace(self, _entries=new_entries)
    
    def get_latest(self, count: int = 1) -> Tuple[Dict[str, Any], ...]:
        """Get the most recent entries."""
        if not self._entries:
            return tuple()
        return self._entries[-count:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "max_entries": self.max_entries,
            "entry_count": len(self._entries),
        }


@dataclass(frozen=True)
class AllocationState:
    """
    Persistent state for allocation recommendations.
    
    Maintains historical information and configuration while
    remaining immutable between assessment cycles.
    """
    
    history: AllocationHistory = field(default_factory=AllocationHistory.create)
    
    # Configuration
    default_allocation_weight_precision: float = 0.40
    default_allocation_weight_priority: float = 0.35
    default_allocation_weight_uncertainty: float = 0.15
    default_allocation_weight_context: float = 0.10
    
    state_id: str = field(default_factory=lambda: f"allocation_state_{id(object())}")
    
    def update_history(
        self,
        allocation_result: Dict[str, Any],
    ) -> "AllocationState":
        """Update history with a new allocation recommendation."""
        return dataclass_replace(
            self,
            history=self.history.append(allocation_result),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "state_id": self.state_id,
            "history": self.history.to_dict(),
            "weights": {
                "precision": self.default_allocation_weight_precision,
                "priority": self.default_allocation_weight_priority,
                "uncertainty": self.default_allocation_weight_uncertainty,
                "context": self.default_allocation_weight_context,
            },
        }


@dataclass(frozen=True)
class BandwidthHistory:
    """
    Bounded history of bandwidth assessments.
    """
    
    max_entries: int = 100
    _entries: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def create(cls, max_entries: int = 100) -> "BandwidthHistory":
        """Create a new history instance."""
        return cls(max_entries=max_entries)
    
    def append(self, entry: Dict[str, Any]) -> "BandwidthHistory":
        """Add a new bandwidth assessment to history."""
        new_entries = self._entries + (entry,)
        
        if len(new_entries) > self.max_entries:
            new_entries = new_entries[-self.max_entries:]
        
        return dataclass_replace(self, _entries=new_entries)
    
    def get_latest(self, count: int = 1) -> Tuple[Dict[str, Any], ...]:
        """Get the most recent entries."""
        if not self._entries:
            return tuple()
        return self._entries[-count:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "max_entries": self.max_entries,
            "entry_count": len(self._entries),
        }


@dataclass(frozen=True)
class BandwidthState:
    """
    Persistent state for bandwidth assessments.
    """
    
    history: BandwidthHistory = field(default_factory=BandwidthHistory.create)
    
    # Configuration
    default_bandwidth_weight_precision: float = 0.40
    default_bandwidth_weight_uncertainty: float = 0.30
    default_bandwidth_weight_context: float = 0.20
    default_bandwidth_weight_priority: float = 0.10
    
    state_id: str = field(default_factory=lambda: f"bandwidth_state_{id(object())}")
    
    def update_history(
        self,
        bandwidth_result: Dict[str, Any],
    ) -> "BandwidthState":
        """Update history with a new bandwidth assessment."""
        return dataclass_replace(
            self,
            history=self.history.append(bandwidth_result),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "state_id": self.state_id,
            "history": self.history.to_dict(),
            "weights": {
                "precision": self.default_bandwidth_weight_precision,
                "uncertainty": self.default_bandwidth_weight_uncertainty,
                "context": self.default_bandwidth_weight_context,
                "priority": self.default_bandwidth_weight_priority,
            },
        }


@dataclass(frozen=True)
class BudgetHistory:
    """
    Bounded history of budget assessments.
    
    Maintains recent budget values for continuity estimation
    and historical influence computation.
    """
    
    max_entries: int = 100
    _entries: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def create(cls, max_entries: int = 100) -> "BudgetHistory":
        """Create a new history instance."""
        return cls(max_entries=max_entries)
    
    def append(self, entry: Dict[str, Any]) -> "BudgetHistory":
        """Add a new budget assessment to history."""
        new_entries = self._entries + (entry,)
        
        if len(new_entries) > self.max_entries:
            new_entries = new_entries[-self.max_entries:]
        
        return dataclass_replace(self, _entries=new_entries)
    
    def get_latest(self, count: int = 1) -> Tuple[Dict[str, Any], ...]:
        """Get the most recent entries."""
        if not self._entries:
            return tuple()
        return self._entries[-count:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "max_entries": self.max_entries,
            "entry_count": len(self._entries),
        }


# =============================================================================
# COMPUTATIONAL ESTIMATORS (ALGORITHMS)
# =============================================================================


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass instance.
    
    This is needed because frozen dataclasses don't allow direct assignment.
    Uses __dict__ manipulation for stateless algorithms.
    """
    # For frozen dataclasses, we need to use a different approach
    if hasattr(obj, "__dataclass_fields__"):
        # Create new instance with updated fields
        init_values = {}
        for field_name in obj.__dataclass_fields__.keys():
            if field_name in kwargs:
                init_values[field_name] = kwargs[field_name]
            else:
                init_values[field_name] = getattr(obj, field_name)
        return type(obj)(**init_values)
    else:
        # Fallback: create a copy with updated values
        new_obj = obj.__class__.__new__(obj.__class__)
        for k, v in vars(obj).items():
            setattr(new_obj, k, v)
        for k, v in kwargs.items():
            setattr(new_obj, k, v)
        return new_obj


# =============================================================================
# PRECISION ESTIMATOR
# =============================================================================


class PrecisionEstimator:
    """
    Computes focus sharpness and precision estimates for focus targets.
    
    This estimator determines how narrowly a target should be focused,
    what discrimination level is required, and how much computational
    resolution is needed.
    
    Input: FocusCandidate (external projection)
    Output: Focus sharpness estimate, bandwidth preference, processing depth
    
    NO runtime resource allocation. NO scheduling. NO execution.
    """
    
    def __init__(
        self,
        weight_sharpness: float = 0.35,
        weight_discrimination: float = 0.25,
        weight_uncertainty: float = 0.15,
        weight_priority_influence: float = 0.15,
        weight_context_fit: float = 0.10,
    ):
        """
        Initialize the precision estimator.
        
        Args:
            weight_sharpness: Weight for focus sharpness computation
            weight_discrimination: Weight for discrimination requirement
            weight_uncertainty: Weight for uncertainty penalty
            weight_priority_influence: Weight from priority estimation
            weight_context_fit: Weight for context fit
        """
        total_weight = (
            weight_sharpness +
            weight_discrimination +
            weight_uncertainty +
            weight_priority_influence +
            weight_context_fit
        )
        
        # Normalize weights to sum to 1.0
        if abs(total_weight - 1.0) > 0.01:
            weight_sharpness /= total_weight
            weight_discrimination /= total_weight
            weight_uncertainty /= total_weight
            weight_priority_influence /= total_weight
            weight_context_fit /= total_weight
        
        self.weight_sharpness = weight_sharpness
        self.weight_discrimination = weight_discrimination
        self.weight_uncertainty = weight_uncertainty
        self.weight_priority_influence = weight_priority_influence
        self.weight_context_fit = weight_context_fit
    
    def estimate_precision(
        self,
        focus_target_id: str,
        context_projection: Dict[str, Any],
        priority_assessment: Optional[Dict[str, Any]] = None,
        competition_assessment: Optional[Dict[str, Any]] = None,
        historical_state: Optional[Dict[str, Any]] = None,
    ) -> "PrecisionEstimationResult":
        """
        Estimate precision for a focus target.
        
        Args:
            focus_target_id: ID of the target to assess
            context_projection: Current execution context (external)
            priority_assessment: Priority assessment from Phase 4.2.3 (optional)
            competition_assessment: Competition analysis from Phase 4.2.4 (optional)
            historical_state: Previous precision values (optional)
            
        Returns:
            PrecisionEstimationResult with all estimated values
        """
        # Extract values from context
        context_uncertainty = self._extract_context_uncertainty(context_projection)
        priority_influence = self._extract_priority_influence(priority_assessment)
        
        # Compute base sharpness from discrimination and uncertainty
        base_sharpness = self._compute_base_sharpness(
            context_uncertainty, historical_state
        )
        
        # Apply priority modulation
        final_sharpness = base_sharpness * (1.0 - self.weight_uncertainty) + (
            priority_influence * self.weight_priority_influence
        )
        
        # Clamp to [0.0, 1.0]
        final_sharpness = clamp(final_sharpness)
        
        # Determine bandwidth preference from sharpness
        if final_sharpness < 0.3:
            bandwidth_preference = BandwidthLevel.COARSE
        elif final_sharpness < 0.6:
            bandwidth_preference = BandwidthLevel.MODERATE
        elif final_sharpness < 0.85:
            bandwidth_preference = BandwidthLevel.FINE
        else:
            bandwidth_preference = BandwidthLevel.ULTRA_FINE
        
        # Estimate processing depth from context complexity
        processing_depth = self._estimate_processing_depth(context_projection)
        
        # Determine computational resolution based on sharpness and depth
        computational_resolution = int(
            50 + (final_sharpness * 100) + (processing_depth * 25)
        )
        computational_resolution = clamp(computational_resolution, 25, 300)
        
        # Compute uncertainty penalty for precision estimation
        estimated_uncertainty = self._estimate_estimation_uncertainty(
            context_projection,
            priority_assessment,
            historical_state,
        )
        
        return PrecisionEstimationResult(
            focus_sharpness=final_sharpness,
            required_discrimination=self.weight_discrimination * 100,
            expected_uncertainty=estimated_uncertainty,
            computational_resolution=int(computational_resolution),
            processing_depth=processing_depth,
            bandwidth_preference=bandwidth_preference,
        )
    
    def _extract_context_uncertainty(self, context: Dict[str, Any]) -> float:
        """Extract uncertainty from context projection."""
        return clamp(context.get("uncertainty_score", 0.5))
    
    def _extract_priority_influence(self, assessment: Optional[Dict[str, Any]]) -> float:
        """Extract priority influence score."""
        if not assessment:
            return 0.5
        return clamp(assessment.get("priority_score", 0.5))
    
    def _compute_base_sharpness(
        self,
        context_uncertainty: float,
        historical_state: Optional[Dict[str, Any]],
    ) -> float:
        """
        Compute base sharpness from context and history.
        
        Lower uncertainty → higher sharpness (finer focus).
        Historical stability → more reliable sharpness estimate.
        """
        # Base sharpness from context uncertainty
        # High uncertainty → lower sharpness (broader focus needed)
        base_from_uncertainty = 1.0 - context_uncertainty
        
        # If we have historical data, increase confidence
        if historical_state and historical_state.get("continuity_score", 0) > 0.7:
            base_from_uncertainty = clamp(base_from_uncertainty + 0.1)
        
        return clamp(base_from_uncertainty)
    
    def _estimate_processing_depth(self, context: Dict[str, Any]) -> int:
        """Estimate processing depth based on context complexity."""
        # Higher complexity → more reasoning layers needed
        complexity_score = context.get("complexity_score", 0.5)
        
        if complexity_score < 0.25:
            return 1  # Simple processing
        elif complexity_score < 0.5:
            return 2  # Moderate processing
        elif complexity_score < 0.75:
            return 3  # Complex processing
        else:
            return 4  # Very complex processing
    
    def _estimate_estimation_uncertainty(
        self,
        context: Dict[str, Any],
        priority_assessment: Optional[Dict[str, Any]],
        historical_state: Optional[Dict[str, Any]],
    ) -> float:
        """
        Estimate uncertainty in the precision estimation itself.
        
        Higher values mean more uncertainty about the precision estimate.
        """
        # Base uncertainty from context
        base_uncertainty = context.get("uncertainty_score", 0.5) * 0.4
        
        # Add priority uncertainty component
        if priority_assessment and "uncertainty" in priority_assessment:
            base_uncertainty += priority_assessment["uncertainty"] * 0.3
        
        # Reduce if we have historical continuity
        if historical_state and historical_state.get("continuity_score", 0) > 0.7:
            base_uncertainty *= 0.5
        
        return clamp(base_uncertainty)


@dataclass(frozen=True)
class PrecisionEstimationResult:
    """
    Result of a precision estimation.
    
    Contains all estimated values without aggregation or normalization.
    This is the foundational data that gets processed into assessments.
    """
    
    focus_sharpness: float  # 0.0 to 1.0
    required_discrimination: float = 50.0  # Units of discrimination needed
    expected_uncertainty: float = 0.5  # 0.0 to 1.0
    
    computational_resolution: int = 100
    """Units of computational resolution needed."""
    
    processing_depth: int = 3
    """Number of reasoning layers needed."""
    
    bandwidth_preference: str = BandwidthLevel.MODERATE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "focus_sharpness": self.focus_sharpness,
            "required_discrimination": self.required_discrimination,
            "expected_uncertainty": self.expected_uncertainty,
            "computational_resolution": self.computational_resolution,
            "processing_depth": self.processing_depth,
            "bandwidth_preference": self.bandwidth_preference,
        }


# =============================================================================
# UNCERTAINTY ESTIMATOR
# =============================================================================


class UncertaintyEstimator:
    """
    Estimates uncertainty factors in precision allocation.
    
    Computes:
        • Representation uncertainty (how well is the target represented?)
        • Context uncertainty (how stable is the current context?)
        • Priority uncertainty (how certain are priority estimates?)
        • Competition uncertainty (how uncertain are competition relationships?)
        • Prediction uncertainty (how certain are future state predictions?)
    
    Input: FocusCandidate, ContextProjection, PriorityAssessment, etc.
    Output: UncertaintyAnalysis with individual and total scores
    """
    
    def __init__(
        self,
        weight_representation: float = 0.25,
        weight_context: float = 0.20,
        weight_priority: float = 0.20,
        weight_competition: float = 0.20,
        weight_prediction: float = 0.15,
    ):
        """
        Initialize the uncertainty estimator.
        
        Args:
            weight_representation: Weight for representation uncertainty
            weight_context: Weight for context uncertainty
            weight_priority: Weight for priority uncertainty
            weight_competition: Weight for competition uncertainty
            weight_prediction: Weight for prediction uncertainty
        """
        total = (
            weight_representation +
            weight_context +
            weight_priority +
            weight_competition +
            weight_prediction
        )
        
        # Normalize weights
        if abs(total - 1.0) > 0.01:
            weight_representation /= total
            weight_context /= total
            weight_priority /= total
            weight_competition /= total
            weight_prediction /= total
        
        self.weight_representation = weight_representation
        self.weight_context = weight_context
        self.weight_priority = weight_priority
        self.weight_competition = weight_competition
        self.weight_prediction = weight_prediction
    
    def estimate_all(
        self,
        focus_target_id: str,
        context_projection: Dict[str, Any],
        priority_assessment: Optional[Dict[str, Any]] = None,
        competition_assessment: Optional[Dict[str, Any]] = None,
        historical_state: Optional[Dict[str, Any]] = None,
    ) -> UncertaintyAnalysis:
        """
        Estimate all uncertainty factors for a focus target.
        
        Args:
            focus_target_id: ID of the target being assessed
            context_projection: Current execution context (external)
            priority_assessment: Priority assessment from Phase 4.2.3 (optional)
            competition_assessment: Competition analysis from Phase 4.2.4 (optional)
            historical_state: Previous uncertainty values (optional)
            
        Returns:
            UncertaintyAnalysis with all uncertainty scores
        """
        # Estimate each uncertainty factor
        
        # Representation uncertainty - how well is the target represented?
        representation_uncertainty = self._estimate_representation_uncertainty(
            context_projection,
            focus_target_id,
        )
        
        # Context uncertainty - how stable is the current context?
        context_uncertainty = self._estimate_context_uncertainty(context_projection)
        
        # Priority uncertainty - how certain are priority estimates?
        priority_uncertainty = self._estimate_priority_uncertainty(
            priority_assessment,
            historical_state,
        )
        
        # Competition uncertainty - how uncertain are competition relationships?
        competition_uncertainty = self._estimate_competition_uncertainty(
            competition_assessment,
            context_projection,
        )
        
        # Prediction uncertainty - how certain are future state predictions?
        prediction_uncertainty = self._estimate_prediction_uncertainty(
            context_projection,
            historical_state,
        )
        
        # Compute total uncertainty (weighted average)
        total_uncertainty = (
            representation_uncertainty * self.weight_representation +
            context_uncertainty * self.weight_context +
            priority_uncertainty * self.weight_priority +
            competition_uncertainty * self.weight_competition +
            prediction_uncertainty * self.weight_prediction
        )
        
        return UncertaintyAnalysis(
            representation_uncertainty=representation_uncertainty,
            context_uncertainty=context_uncertainty,
            priority_uncertainty=priority_uncertainty,
            competition_uncertainty=competition_uncertainty,
            prediction_uncertainty=prediction_uncertainty,
            total_uncertainty_score=total_uncertainty,
        )
    
    def _estimate_representation_uncertainty(
        self,
        context: Dict[str, Any],
        target_id: str,
    ) -> float:
        """Estimate how well the target is represented in context."""
        # Use context clarity score (inverted = higher uncertainty when unclear)
        clarity_score = context.get("context_clarity", 0.7)
        
        # If target has been in context for a while, representation is more stable
        if "target_duration" in context:
            duration = context["target_duration"]
            if duration > 5:  # Target has been present for a while
                clarity_score = min(1.0, clarity_score + 0.2)
        
        return clamp(1.0 - clarity_score)
    
    def _estimate_context_uncertainty(self, context: Dict[str, Any]) -> float:
        """Estimate uncertainty in the current context."""
        # Higher context change rate → higher uncertainty
        change_rate = context.get("context_change_rate", 0.3)
        
        return clamp(change_rate)
    
    def _estimate_priority_uncertainty(
        self,
        assessment: Optional[Dict[str, Any]],
        historical_state: Optional[Dict[str, Any]],
    ) -> float:
        """Estimate uncertainty in priority estimates."""
        if not assessment:
            return 0.5  # Default uncertainty without assessment
        
        # Use the assessment's uncertainty if available
        if "uncertainty" in assessment:
            return clamp(assessment["uncertainty"])
        
        # Otherwise, estimate from priority stability
        stability = assessment.get("stability", 0.7)
        return clamp(1.0 - stability)
    
    def _estimate_competition_uncertainty(
        self,
        competition: Optional[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> float:
        """Estimate uncertainty in competition relationships."""
        if not competition:
            return 0.5  # Default uncertainty without competition data
        
        # Use competition matrix consistency
        matrix_consistency = competition.get("matrix_consistency", 0.7)
        
        # Add context volatility component
        context_volatility = context.get("context_volatility", 0.3)
        
        combined = (matrix_consistency * 0.6 + context_volatility * 0.4)
        
        return clamp(1.0 - combined)
    
    def _estimate_prediction_uncertainty(
        self,
        context: Dict[str, Any],
        historical_state: Optional[Dict[str, Any]],
    ) -> float:
        """Estimate uncertainty in future state predictions."""
        # Use prediction confidence from context
        prediction_confidence = context.get("prediction_confidence", 0.6)
        
        # Reduce if we have stable history
        if historical_state and historical_state.get("continuity_score", 0) > 0.7:
            prediction_confidence = min(1.0, prediction_confidence + 0.2)
        
        return clamp(1.0 - prediction_confidence)


# =============================================================================
# BANDWIDTH ESTIMATOR
# =============================================================================


class BandwidthEstimator:
    """
    Estimates recommended computational bandwidth allocation.
    
    Determines how much computational bandwidth a target deserves,
    from minimal to maximum allocation.
    
    Input: FocusCandidate, PrecisionEstimationResult, ContextProjection
    Output: BandwidthAssessment with recommended level and parameters
    
    BANDWIDTH IS ADVISORY. It NEVER reserves runtime resources.
    """
    
    def __init__(
        self,
        weight_sharpness: float = 0.40,
        weight_uncertainty: float = 0.30,
        weight_context_fit: float = 0.20,
        weight_priority_influence: float = 0.10,
    ):
        """
        Initialize the bandwidth estimator.
        
        Args:
            weight_sharpness: Weight for focus sharpness
            weight_uncertainty: Weight for uncertainty (higher uncertainty → lower bandwidth)
            weight_context_fit: Weight for context fit
            weight_priority_influence: Weight for priority influence
        """
        total = (
            weight_sharpness +
            weight_uncertainty +
            weight_context_fit +
            weight_priority_influence
        )
        
        # Normalize weights
        if abs(total - 1.0) > 0.01:
            weight_sharpness /= total
            weight_uncertainty /= total
            weight_context_fit /= total
            weight_priority_influence /= total
        
        self.weight_sharpness = weight_sharpness
        self.weight_uncertainty = weight_uncertainty
        self.weight_context_fit = weight_context_fit
        self.weight_priority_influence = weight_priority_influence
    
    def estimate_bandwidth(
        self,
        focus_target_id: str,
        precision_result: PrecisionEstimationResult,
        context_projection: Dict[str, Any],
        priority_assessment: Optional[Dict[str, Any]] = None,
    ) -> BandwidthAssessment:
        """
        Estimate recommended bandwidth for a focus target.
        
        Args:
            focus_target_id: ID of the target being assessed
            precision_result: Precision estimation from PrecisionEstimator
            context_projection: Current execution context (external)
            priority_assessment: Priority assessment from Phase 4.2.3 (optional)
            
        Returns:
            BandwidthAssessment with recommended bandwidth parameters
        """
        # Extract values
        sharpness = precision_result.focus_sharpness
        uncertainty = precision_result.expected_uncertainty
        
        # Get priority influence
        priority_influence = self._extract_priority_influence(priority_assessment)
        
        # Get context fit score
        context_fit = context_projection.get("context_fit", 0.5)
        
        # Compute bandwidth score (normalized to [0.0, 1.0])
        bandwidth_score = (
            sharpness * self.weight_sharpness +
            (1.0 - uncertainty) * self.weight_uncertainty +  # Lower uncertainty → higher bandwidth
            context_fit * self.weight_context_fit +
            priority_influence * self.weight_priority_influence
        )
        
        # Clamp to [0.0, 1.0]
        bandwidth_score = clamp(bandwidth_score)
        
        # Map score to bandwidth level
        if bandwidth_score < 0.2:
            bandwidth_level = BandwidthLevel.MINIMAL
            minimum_bw = 0.05
            optimal_bw = 0.15
            maximum_bw = 0.3
        elif bandwidth_score < 0.4:
            bandwidth_level = BandwidthLevel.LOW
            minimum_bw = 0.1
            optimal_bw = 0.25
            maximum_bw = 0.45
        elif bandwidth_score < 0.7:
            bandwidth_level = BandwidthLevel.MODERATE
            minimum_bw = 0.2
            optimal_bw = 0.45
            maximum_bw = 0.7
        elif bandwidth_score < 0.85:
            bandwidth_level = BandwidthLevel.HIGH
            minimum_bw = 0.4
            optimal_bw = 0.65
            maximum_bw = 0.9
        else:
            bandwidth_level = BandwidthLevel.MAXIMUM
            minimum_bw = 0.6
            optimal_bw = 0.8
            maximum_bw = 1.0
        
        # Determine if adaptive mode is appropriate
        context_stability = context_projection.get("context_stability", 0.7)
        adaptive_mode = context_stability < 0.6
        
        return BandwidthAssessment(
            recommended_level=bandwidth_level,
            minimum_bandwidth=minimum_bw,
            optimal_bandwidth=optimal_bw,
            maximum_bandwidth=maximum_bw,
            confidence=self._compute_confidence(precision_result, priority_assessment),
            justification=self._generate_justification(
                bandwidth_score,
                sharpness,
                uncertainty,
                context_fit,
                priority_influence,
            ),
        )
    
    def _extract_priority_influence(self, assessment: Optional[Dict[str, Any]]) -> float:
        """Extract priority influence score."""
        if not assessment:
            return 0.5
        return clamp(assessment.get("priority_score", 0.5))
    
    def _compute_confidence(
        self,
        precision_result: PrecisionEstimationResult,
        priority_assessment: Optional[Dict[str, Any]],
    ) -> float:
        """Compute confidence in the bandwidth recommendation."""
        # Base confidence from precision estimation quality
        base_confidence = 0.5
        
        if precision_result.focus_sharpness > 0.8:
            base_confidence += 0.2
        elif precision_result.focus_sharpness < 0.3:
            base_confidence -= 0.1
        
        # Add priority assessment confidence
        if priority_assessment and "confidence" in priority_assessment:
            base_confidence += priority_assessment["confidence"] * 0.2
        
        return clamp(base_confidence)
    
    def _generate_justification(
        self,
        bandwidth_score: float,
        sharpness: float,
        uncertainty: float,
        context_fit: float,
        priority_influence: float,
    ) -> str:
        """Generate human-readable justification for bandwidth recommendation."""
        parts = []
        
        if sharpness >= 0.7:
            parts.append(f"high focus sharpness ({sharpness:.2f})")
        elif sharpness < 0.3:
            parts.append(f"low focus sharpness ({sharpness:.2f})")
        
        if uncertainty < 0.3:
            parts.append(f"low uncertainty ({uncertainty:.2f})")
        elif uncertainty > 0.7:
            parts.append(f"high uncertainty ({uncertainty:.2f})")
        
        if context_fit >= 0.6:
            parts.append(f"good context fit ({context_fit:.2f})")
        
        if priority_influence >= 0.6:
            parts.append(f"strong priority influence ({priority_influence:.2f})")
        
        justification = "Bandwidth recommendation based on: "
        if parts:
            justification += ", ".join(parts) + "."
        else:
            justification += "balanced factors."
        
        return justification


# =============================================================================
# RESOURCE DEMAND ESTIMATOR
# =============================================================================


class ResourceDemandEstimator:
    """
    Estimates computational resource requirements for focus targets.
    
    Computes:
        • Processing effort (how much CPU/GPU processing needed?)
        • Expected iterations (how many reasoning steps?)
        • Memory pressure (how much memory required?)
        • Reasoning complexity (simple, moderate, complex, very complex)
        • Context size estimate (tokens/data points needed)
    
    Input: FocusCandidate, PrecisionEstimationResult, ContextProjection
    Output: ResourceDemandEstimate with all requirements
    
    NO runtime resource allocation. Only estimation.
    """
    
    def __init__(
        self,
        weight_sharpness: float = 0.30,
        weight_uncertainty: float = 0.25,
        weight_processing_depth: float = 0.20,
        weight_context_size: float = 0.15,
        weight_complexity: float = 0.10,
    ):
        """
        Initialize the resource demand estimator.
        
        Args:
            weight_sharpness: Weight for focus sharpness
            weight_uncertainty: Weight for uncertainty (higher → more resources)
            weight_processing_depth: Weight for reasoning depth
            weight_context_size: Weight for context size requirements
            weight_complexity: Weight for processing complexity
        """
        total = (
            weight_sharpness +
            weight_uncertainty +
            weight_processing_depth +
            weight_context_size +
            weight_complexity
        )
        
        # Normalize weights
        if abs(total - 1.0) > 0.01:
            weight_sharpness /= total
            weight_uncertainty /= total
            weight_processing_depth /= total
            weight_context_size /= total
            weight_complexity /= total
        
        self.weight_sharpness = weight_sharpness
        self.weight_uncertainty = weight_uncertainty
        self.weight_processing_depth = weight_processing_depth
        self.weight_context_size = weight_context_size
        self.weight_complexity = weight_complexity
    
    def estimate_resources(
        self,
        focus_target_id: str,
        precision_result: PrecisionEstimationResult,
        context_projection: Dict[str, Any],
    ) -> ResourceDemandEstimate:
        """
        Estimate resource requirements for a focus target.
        
        Args:
            focus_target_id: ID of the target being assessed
            precision_result: Precision estimation from PrecisionEstimator
            context_projection: Current execution context (external)
            
        Returns:
            ResourceDemandEstimate with all resource requirements
        """
        sharpness = precision_result.focus_sharpness
        uncertainty = precision_result.expected_uncertainty
        processing_depth = precision_result.processing_depth
        
        # Get context factors
        context_complexity = context_projection.get("complexity_score", 0.5)
        estimated_context_size = context_projection.get("context_size", 100)
        
        # Compute processing effort (higher with sharpness, uncertainty, depth)
        base_processing_effort = (
            sharpness * self.weight_sharpness +
            uncertainty * self.weight_uncertainty +
            (processing_depth / 5) * self.weight_processing_depth +
            context_complexity * 0.2
        )
        
        estimated_processing_effort = clamp(base_processing_effort)
        
        # Compute expected iterations based on processing depth and complexity
        base_iterations = (
            processing_depth *
            max(1, int(context_complexity * 10))
        )
        
        # Scale iterations by sharpness (finer focus → more iterations needed)
        iteration_factor = 5 + int(sharpness * 15)
        expected_iterations = max(1, base_iterations * iteration_factor // 20)
        
        # Compute memory pressure
        memory_base = estimated_context_size / 1000.0
        memory_from_uncertainty = uncertainty * 0.3
        memory_from_sharpness = sharpness * 0.2
        
        memory_pressure_estimate = clamp(
            memory_base + memory_from_uncertainty + memory_from_sharpness
        )
        
        # Determine reasoning complexity level
        if processing_depth <= 2 and context_complexity < 0.4:
            reasoning_complexity = "simple"
        elif processing_depth <= 3 and context_complexity < 0.6:
            reasoning_complexity = "moderate"
        elif processing_depth <= 4 and context_complexity < 0.8:
            reasoning_complexity = "complex"
        else:
            reasoning_complexity = "very_complex"
        
        # Estimate memory in MB (rough estimation)
        estimated_memory_mb = (
            memory_pressure_estimate * 512 +  # Base: ~512MB for high pressure
            estimated_context_size * 0.5  # Context: ~0.5MB per 100 tokens
        )
        
        # Estimate time in seconds (rough estimation)
        estimated_time_seconds = (
            expected_iterations * 0.01 +  # 10ms per iteration
            estimated_memory_mb * 0.002  # 2ms per MB memory pressure
        )
        
        return ResourceDemandEstimate(
            estimated_processing_effort=estimated_processing_effort,
            expected_iterations=expected_iterations,
            memory_pressure_estimate=memory_pressure_estimate,
            reasoning_complexity=reasoning_complexity,
            context_size_estimate=estimated_context_size,
            estimated_memory_mb=min(estimated_memory_mb, 8192),  # Cap at 8GB
            estimated_time_seconds=min(estimated_time_seconds, 60.0),  # Cap at 60s
        )


# =============================================================================
# BUDGET ESTIMATOR
# =============================================================================


class BudgetEstimator:
    """
    Recommends computational budget allocation.
    
    Computes:
        • Recommended computational budget (normalized, 0.0 to 1.0)
        • Relative allocation percentage
        • Fair-share estimate
        • Reserved importance
    
    Input: FocusCandidate, PrecisionAssessment, BandwidthAssessment, ContextProjection
    Output: BudgetAssessment with recommended budget parameters
    
    BUDGETS ARE RECOMMENDATIONS ONLY. No runtime allocation.
    """
    
    def __init__(
        self,
        weight_precision: float = 0.35,
        weight_bandwidth: float = 0.25,
        weight_context_fit: float = 0.20,
        weight_priority_influence: float = 0.15,
        weight_uncertainty_penalty: float = 0.05,
    ):
        """
        Initialize the budget estimator.
        
        Args:
            weight_precision: Weight for precision estimation
            weight_bandwidth: Weight for bandwidth recommendation
            weight_context_fit: Weight for context fit
            weight_priority_influence: Weight for priority influence
            weight_uncertainty_penalty: Penalty factor for uncertainty
        """
        total = (
            weight_precision +
            weight_bandwidth +
            weight_context_fit +
            weight_priority_influence +
            weight_uncertainty_penalty
        )
        
        # Normalize weights
        if abs(total - 1.0) > 0.01:
            weight_precision /= total
            weight_bandwidth /= total
            weight_context_fit /= total
            weight_priority_influence /= total
            weight_uncertainty_penalty = min(
                0.2, weight_uncertainty_penalty / total
            )
        
        self.weight_precision = weight_precision
        self.weight_bandwidth = weight_bandwidth
        self.weight_context_fit = weight_context_fit
        self.weight_priority_influence = weight_priority_influence
        self.weight_uncertainty_penalty = weight_uncertainty_penalty
    
    def estimate_budget(
        self,
        focus_target_id: str,
        precision_assessment: PrecisionAssessment,
        bandwidth_assessment: BandwidthAssessment,
        context_projection: Dict[str, Any],
    ) -> BudgetAssessment:
        """
        Estimate recommended budget for a focus target.
        
        Args:
            focus_target_id: ID of the target being assessed
            precision_assessment: Precision assessment from this phase
            bandwidth_assessment: Bandwidth assessment from this phase
            context_projection: Current execution context (external)
            
        Returns:
            BudgetAssessment with recommended budget parameters
        """
        # Extract values
        focus_sharpness = precision_assessment.focus_sharpness
        uncertainty_score = precision_assessment.uncertainty_analysis.total()
        
        optimal_bandwidth = bandwidth_assessment.optimal_bandwidth
        context_fit = context_projection.get("context_fit", 0.5)
        
        priority_influence = self._extract_priority_influence(
            context_projection.get("priority_assessment")
        )
        
        # Get constraints from context
        constraints = tuple(context_projection.get("budget_constraints", []))
        
        # Compute base budget score
        base_budget = (
            focus_sharpness * self.weight_precision +
            optimal_bandwidth * self.weight_bandwidth +
            context_fit * self.weight_context_fit +
            priority_influence * self.weight_priority_influence -
            uncertainty_score * self.weight_uncertainty_penalty
        )
        
        # Clamp to [0.0, 1.0]
        recommended_budget = clamp(base_budget)
        
        # Compute fair share estimate (normalized against total budget pool)
        # Assume a pool of 5 targets for estimation
        budget_pool_size = context_projection.get("budget_pool_size", 5)
        fair_share_estimate = recommended_budget / max(budget_pool_size, 1)
        
        return BudgetAssessment(
            recommended_budget=recommended_budget,
            reserved_budget=0.1,  # Always reserve 10% for dynamic needs
            fair_share_estimate=fair_share_estimate,
            confidence=self._compute_confidence(precision_assessment),
            constraints_applied=constraints,
        )
    
    def _extract_priority_influence(self, assessment: Optional[Dict[str, Any]]) -> float:
        """Extract priority influence score."""
        if not assessment:
            return 0.5
        return clamp(assessment.get("priority_score", 0.5))
    
    def _compute_confidence(self, precision_assessment: PrecisionAssessment) -> float:
        """Compute confidence in the budget recommendation."""
        # Base confidence from precision estimation quality
        base_confidence = 0.5
        
        if precision_assessment.focus_sharpness > 0.7:
            base_confidence += 0.15
        elif precision_assessment.focus_sharpness < 0.3:
            base_confidence -= 0.1
        
        # Add uncertainty penalty
        total_uncertainty = precision_assessment.uncertainty_analysis.total()
        if total_uncertainty > 0.7:
            base_confidence -= 0.2
        elif total_uncertainty < 0.3:
            base_confidence += 0.15
        
        return clamp(base_confidence)


# =============================================================================
# ALLOCATION RECOMMENDER
# =============================================================================


class AllocationRecommender:
    """
    Recommends resource allocation distribution.
    
    Computes:
        • Recommended allocation percentage (0.0 to 1.0)
        • Recommended effort (normalized, 0.0 to 1.0)
        • Recommended computational priority rank
    
    Input: FocusCandidate, PrecisionAssessment, BudgetAssessment, ContextProjection
    Output: AllocationRecommendation with all allocation parameters
    
    NO runtime allocation. Only recommendations.
    """
    
    def __init__(
        self,
        weight_precision_allocation: float = 0.40,
        weight_priority_allocation: float = 0.35,
        weight_uncertainty_penalty: float = 0.15,
        weight_context_fit: float = 0.10,
    ):
        """
        Initialize the allocation recommender.
        
        Args:
            weight_precision_allocation: Weight for precision-based allocation
            weight_priority_allocation: Weight for priority-based allocation
            weight_uncertainty_penalty: Penalty factor for uncertainty
            weight_context_fit: Weight for context fit
        """
        total = (
            weight_precision_allocation +
            weight_priority_allocation +
            weight_uncertainty_penalty +
            weight_context_fit
        )
        
        # Normalize weights
        if abs(total - 1.0) > 0.01:
            weight_precision_allocation /= total
            weight_priority_allocation /= total
            weight_uncertainty_penalty = min(
                0.2, weight_uncertainty_penalty / total
            )
            weight_context_fit /= total
        
        self.weight_precision_allocation = weight_precision_allocation
        self.weight_priority_allocation = weight_priority_allocation
        self.weight_uncertainty_penalty = weight_uncertainty_penalty
        self.weight_context_fit = weight_context_fit
    
    def recommend_allocation(
        self,
        focus_target_id: str,
        precision_assessment: PrecisionAssessment,
        budget_assessment: BudgetAssessment,
        context_projection: Dict[str, Any],
    ) -> AllocationRecommendation:
        """
        Recommend resource allocation for a focus target.
        
        Args:
            focus_target_id: ID of the target being assessed
            precision_assessment: Precision assessment from this phase
            budget_assessment: Budget assessment from this phase
            context_projection: Current execution context (external)
            
        Returns:
            AllocationRecommendation with allocation parameters
        """
        # Extract values
        recommended_budget = budget_assessment.recommended_budget
        
        total_uncertainty = precision_assessment.uncertainty_analysis.total()
        context_fit = context_projection.get("context_fit", 0.5)
        
        priority_influence = self._extract_priority_influence(
            context_projection.get("priority_assessment")
        )
        
        # Compute allocation percentage
        allocation_percentage = (
            recommended_budget * self.weight_precision_allocation +
            priority_influence * self.weight_priority_allocation +
            context_fit * self.weight_context_fit -
            total_uncertainty * self.weight_uncertainty_penalty
        )
        
        # Clamp to [0.0, 1.0]
        allocation_percentage = clamp(allocation_percentage)
        
        # Compute recommended effort (based on resource demand)
        resource_demand = precision_assessment.resource_demand
        estimated_effort = (
            resource_demand.estimated_processing_effort * 0.5 +
            resource_demand.expected_iterations / 100 * 0.3 +
            resource_demand.memory_pressure_estimate * 0.2
        )
        
        # Clamp effort to [0.0, 1.0]
        recommended_effort = clamp(estimated_effort)
        
        # Compute computational priority rank (lower is higher priority)
        base_priority = int((1.0 - allocation_percentage) * 100)
        priority_adjustment = int(total_uncertainty * 20)
        recommended_computational_priority = max(1, base_priority + priority_adjustment)
        
        # Determine reservation percentage
        recommended_reservation = budget_assessment.reserved_budget
        
        return AllocationRecommendation(
            recommended_allocation_percentage=allocation_percentage,
            recommended_effort=recommended_effort,
            recommended_computational_priority=recommended_computational_priority,
            recommended_reservation=recommended_reservation,
            confidence=budget_assessment.confidence * 0.8,  # Slightly lower than budget
            justification=self._generate_justification(
                allocation_percentage,
                precision_assessment,
                context_projection,
            ),
        )
    
    def _extract_priority_influence(self, assessment: Optional[Dict[str, Any]]) -> float:
        """Extract priority influence score."""
        if not assessment:
            return 0.5
        return clamp(assessment.get("priority_score", 0.5))
    
    def _generate_justification(
        self,
        allocation_percentage: float,
        precision_assessment: PrecisionAssessment,
        context_projection: Dict[str, Any],
    ) -> str:
        """Generate human-readable justification for allocation recommendation."""
        parts = []
        
        if allocation_percentage >= 0.7:
            parts.append(f"high allocation ({allocation_percentage:.1%})")
        elif allocation_percentage <= 0.2:
            parts.append(f"low allocation ({allocation_percentage:.1%})")
        
        # Add factors
        sharpness = precision_assessment.focus_sharpness
        uncertainty = precision_assessment.uncertainty_analysis.total()
        context_fit = context_projection.get("context_fit", 0.5)
        
        if sharpness >= 0.7:
            parts.append(f"high focus sharpness ({sharpness:.2f})")
        elif sharpness < 0.3:
            parts.append(f"low focus sharpness ({sharpness:.2f})")
        
        if uncertainty < 0.3:
            parts.append(f"low uncertainty ({uncertainty:.2f})")
        
        if context_fit >= 0.6:
            parts.append(f"good context fit ({context_fit:.2f})")
        
        justification = "Allocation recommendation based on: "
        if parts:
            justification += ", ".join(parts) + "."
        else:
            justification += "balanced factors."
        
        return justification


# =============================================================================
# CONFIDENCE ESTIMATOR
# =============================================================================


class PrecisionConfidenceEstimator:
    """
    Estimates confidence in precision assessments.
    
    Confidence depends upon:
        • Input completeness (all required inputs available?)
        • Priority stability (consistent priorities over time?)
        • Competition consistency (stable competition relationships?)
        • Resource knowledge (do we understand resource requirements?)
        • Historical stability (stable patterns in history?)
    
    Input: FocusCandidate, PrecisionAssessment, ContextProjection
    Output: PrecisionConfidence with scores for each factor
    
    NO runtime allocation. Only confidence estimation.
    """
    
    def __init__(
        self,
        weight_input_completeness: float = 0.25,
        weight_priority_stability: float = 0.20,
        weight_competition_consistency: float = 0.20,
        weight_resource_knowledge: float = 0.15,
        weight_historical_stability: float = 0.20,
    ):
        """
        Initialize the confidence estimator.
        
        Args:
            weight_input_completeness: Weight for input completeness
            weight_priority_stability: Weight for priority stability
            weight_competition_consistency: Weight for competition consistency
            weight_resource_knowledge: Weight for resource knowledge
            weight_historical_stability: Weight for historical stability
        """
        total = (
            weight_input_completeness +
            weight_priority_stability +
            weight_competition_consistency +
            weight_resource_knowledge +
            weight_historical_stability
        )
        
        # Normalize weights
        if abs(total - 1.0) > 0.01:
            weight_input_completeness /= total
            weight_priority_stability /= total
            weight_competition_consistency /= total
            weight_resource_knowledge /= total
            weight_historical_stability /= total
        
        self.weight_input_completeness = weight_input_completeness
        self.weight_priority_stability = weight_priority_stability
        self.weight_competition_consistency = weight_competition_consistency
        self.weight_resource_knowledge = weight_resource_knowledge
        self.weight_historical_stability = weight_historical_stability
    
    def estimate_confidence(
        self,
        focus_target_id: str,
        precision_assessment: PrecisionAssessment,
        context_projection: Dict[str, Any],
        historical_state: Optional[Dict[str, Any]] = None,
    ) -> PrecisionConfidence:
        """
        Estimate confidence in a precision assessment.
        
        Args:
            focus_target_id: ID of the target being assessed
            precision_assessment: Precision assessment from this phase
            context_projection: Current execution context (external)
            historical_state: Previous state for stability comparison
            
        Returns:
            PrecisionConfidence with all confidence scores
        """
        # Estimate each confidence factor
        
        # Input completeness - are all required inputs available?
        input_completeness = self._estimate_input_completeness(
            precision_assessment,
            context_projection,
        )
        
        # Priority stability - are priorities consistent over time?
        priority_stability = self._estimate_priority_stability(
            historical_state,
            precision_assessment,
        )
        
        # Competition consistency - are relationships stable?
        competition_consistency = self._estimate_competition_consistency(
            context_projection,
        )
        
        # Resource knowledge - do we understand resource requirements?
        resource_knowledge = self._estimate_resource_knowledge(
            precision_assessment,
        )
        
        # Historical stability - are patterns stable over time?
        historical_stability = self._estimate_historical_stability(
            historical_state,
        )
        
        # Compute total confidence (weighted average)
        total_confidence = (
            input_completeness * self.weight_input_completeness +
            priority_stability * self.weight_priority_stability +
            competition_consistency * self.weight_competition_consistency +
            resource_knowledge * self.weight_resource_knowledge +
            historical_stability * self.weight_historical_stability
        )
        
        # Identify confidence factors and uncertainty sources for explainability
        confidence_factors = []
        uncertainty_sources = []
        
        if input_completeness > 0.8:
            confidence_factors.append("complete_input_data")
        else:
            uncertainty_sources.append("incomplete_inputs")
        
        if priority_stability > 0.7:
            confidence_factors.append("stable_priority_history")
        elif priority_stability < 0.3:
            uncertainty_sources.append("unstable_priority_patterns")
        
        if competition_consistency > 0.8:
            confidence_factors.append("consistent_competition_analysis")
        else:
            uncertainty_sources.append("inconsistent_competition_relationships")
        
        if resource_knowledge > 0.7:
            confidence_factors.append("clear_resource_requirements")
        
        if historical_stability > 0.7:
            confidence_factors.append("stable_historical_patterns")
        elif historical_stability < 0.3:
            uncertainty_sources.append("unstable_historical_patterns")
        
        return PrecisionConfidence(
            score=total_confidence,
            input_completeness_score=input_completeness,
            priority_stability_score=priority_stability,
            competition_consistency_score=competition_consistency,
            resource_knowledge_score=resource_knowledge,
            historical_stability_score=historical_stability,
            confidence_factors=tuple(confidence_factors),
            uncertainty_sources=tuple(uncertainty_sources),
        )
    
    def _estimate_input_completeness(
        self,
        precision_assessment: PrecisionAssessment,
        context_projection: Dict[str, Any],
    ) -> float:
        """Estimate completeness of input data."""
        # Check which components are present
        present_components = 0
        total_components = 5  # sharpness, uncertainty, bandwidth, resources, budget
        
        if precision_assessment.focus_sharpness >= 0:
            present_components += 1
        
        if precision_assessment.uncertainty_analysis.total() >= 0:
            present_components += 1
        
        if precision_assessment.bandwidth_assessment.confidence >= 0:
            present_components += 1
        
        if precision_assessment.resource_demand.estimated_processing_effort >= 0:
            present_components += 1
        
        if precision_assessment.budget_allocation.recommended_budget >= 0:
            present_components += 1
        
        return present_components / total_components
    
    def _estimate_priority_stability(
        self,
        historical_state: Optional[Dict[str, Any]],
        current_assessment: PrecisionAssessment,
    ) -> float:
        """Estimate stability of priority over time."""
        if not historical_state or "history" not in historical_state:
            return 0.5  # Default without history
        
        history = historical_state["history"]
        if not history.get("continuity_score"):
            return 0.5
        
        continuity = history.get("continuity_score", 0.5)
        
        # Also consider current assessment uncertainty
        current_uncertainty = current_assessment.uncertainty_analysis.total()
        stability_from_uncertainty = 1.0 - current_uncertainty
        
        # Combine factors
        return clamp((continuity + stability_from_uncertainty) / 2)
    
    def _estimate_competition_consistency(
        self,
        context_projection: Dict[str, Any],
    ) -> float:
        """Estimate consistency of competition relationships."""
        # Use matrix consistency from context if available
        return clamp(context_projection.get("competition_consistency", 0.7))
    
    def _estimate_resource_knowledge(self, precision_assessment: PrecisionAssessment) -> float:
        """Estimate knowledge about resource requirements."""
        # Higher confidence when resource estimates are well-defined
        resource_demand = precision_assessment.resource_demand
        
        base_confidence = 0.5
        
        if resource_demand.expected_iterations > 0:
            base_confidence += 0.1
        if resource_demand.estimated_memory_mb is not None:
            base_confidence += 0.1
        if resource_demand.estimated_time_seconds is not None:
            base_confidence += 0.1
        if resource_demand.context_size_estimate > 0:
            base_confidence += 0.1
        
        return clamp(base_confidence)
    
    def _estimate_historical_stability(
        self,
        historical_state: Optional[Dict[str, Any]],
    ) -> float:
        """Estimate stability of historical patterns."""
        if not historical_state or "history" not in historical_state:
            return 0.5  # Default without history
        
        continuity = historical_state.get("continuity_score", 0.5)
        
        # Check trend consistency
        trend_direction = historical_state.get("trend_direction", "unknown")
        
        if trend_direction == "stable":
            return clamp(continuity + 0.2)
        elif trend_direction == "increasing" or trend_direction == "decreasing":
            return clamp(continuity - 0.1)
        else:
            return continuity


# =============================================================================
# EXPLAINABILITY
# =============================================================================


class PrecisionExplanationGenerator:
    """
    Generates human-readable explanations for precision assessments.
    
    Every assessment shall explain:
        • Why precision is recommended
        • Why bandwidth changed
        • Why additional effort is justified
        • Uncertainty contribution
        • Resource contribution
        • Confidence rationale
    
    Input: FocusCandidate, PrecisionAssessment, ContextProjection
    Output: PrecisionExplanation with all explanation components
    """
    
    def generate(
        self,
        focus_target_id: str,
        precision_assessment: PrecisionAssessment,
        context_projection: Dict[str, Any],
    ) -> PrecisionExplanation:
        """
        Generate a complete explanation for a precision assessment.
        
        Args:
            focus_target_id: ID of the target being assessed
            precision_assessment: The assessment to explain
            context_projection: Current execution context (external)
            
        Returns:
            PrecisionExplanation with all explanation components
        """
        sharpness = precision_assessment.focus_sharpness
        uncertainty = precision_assessment.uncertainty_analysis.total()
        
        bandwidth_level = precision_assessment.precision_bandwidth
        recommended_budget = precision_assessment.budget_allocation.recommended_budget
        
        # Generate each justification section
        precision_justification = self._generate_precision_justification(
            sharpness,
            uncertainty,
            context_projection,
        )
        
        uncertainty_justification = self._generate_uncertainty_justification(
            precision_assessment.uncertainty_analysis,
        )
        
        bandwidth_justification = self._generate_bandwidth_justification(
            bandwidth_level,
            precision_assessment.bandwidth_assessment.justification,
        )
        
        resource_justification = self._generate_resource_justification(
            precision_assessment.resource_demand,
        )
        
        budget_justification = self._generate_budget_justification(
            recommended_budget,
            precision_assessment.budget_allocation.confidence,
        )
        
        # Extract dominant factors from contributions
        contribution_summary: Dict[str, float] = {}
        dominant_factors = []
        
        if sharpness >= 0.6:
            contribution_summary["focus_sharpness"] = sharpness * 100
            dominant_factors.append("sharpness")
        
        if uncertainty < 0.4:
            contribution_summary["low_uncertainty"] = (1 - uncertainty) * 100
            dominant_factors.append("low_uncertainty")
        
        if bandwidth_level in (BandwidthLevel.FINE, BandwidthLevel.ULTRA_FINE):
            contribution_summary["high_precision_bandwidth"] = 0.8 * 100
            dominant_factors.append("precision_bandwidth")
        
        if recommended_budget >= 0.6:
            contribution_summary["high_allocation"] = recommended_budget * 100
            dominant_factors.append("allocation")
        
        # Compute summary percentages (normalize to sum ~100)
        total_contribution = sum(contribution_summary.values()) or 100
        for k in contribution_summary:
            contribution_summary[k] = (
                contribution_summary[k] / total_contribution * 100
            )
        
        return PrecisionExplanation(
            target_id=focus_target_id,
            final_focus_sharpness=sharpness,
            final_bandwidth_level=bandwidth_level,
            precision_justification=precision_justification,
            uncertainty_justification=uncertainty_justification,
            bandwidth_justification=bandwidth_justification,
            resource_justification=resource_justification,
            budget_justification=budget_justification,
            contribution_summary=contribution_summary,
            dominant_factors=tuple(dominant_factors[:3]),  # Top 3 factors
            confidence_assessment=precision_assessment.uncertainty_analysis,
        )
    
    def _generate_precision_justification(
        self,
        sharpness: float,
        uncertainty: float,
        context_projection: Dict[str, Any],
    ) -> str:
        """Generate explanation for precision recommendation."""
        if sharpness >= 0.7:
            reason = "high focus sharpness indicates clear target definition"
        elif sharpness >= 0.4:
            reason = "moderate focus sharpness suggests reasonable clarity"
        else:
            reason = "low focus sharpness indicates need for broader attention"
        
        # Add uncertainty context
        if uncertainty < 0.3:
            uncertainty_reason = f" with low uncertainty ({uncertainty:.2f})"
        elif uncertainty > 0.7:
            uncertainty_reason = f" with high uncertainty ({uncertainty:.2f}) - consider verifying inputs"
        else:
            uncertainty_reason = f" with moderate uncertainty ({uncertainty:.2f})"
        
        context_fit = context_projection.get("context_fit", "unknown")
        
        return (
            f"{reason}{uncertainty_reason}. "
            f"Context fit score: {context_fit}."
        )
    
    def _generate_uncertainty_justification(
        self,
        uncertainty_analysis: UncertaintyAnalysis,
    ) -> str:
        """Generate explanation for uncertainty analysis."""
        total = uncertainty_analysis.total()
        
        if total < 0.3:
            return "Low overall uncertainty across all factors. Representations are clear, context is stable, and predictions are reliable."
        elif total > 0.7:
            return (
                f"High overall uncertainty ({total:.2f}). "
                f"Consider: representation uncertainty ({uncertainty_analysis.representation_uncertainty:.2f}), "
                f"context uncertainty ({uncertainty_analysis.context_uncertainty:.2f})"
            )
        else:
            return (
                f"Moderate overall uncertainty ({total:.2f}). "
                f"Uncertainty distributed across: context, representation, and prediction factors."
            )
    
    def _generate_bandwidth_justification(
        self,
        bandwidth_level: str,
        base_justification: str,
    ) -> str:
        """Generate explanation for bandwidth recommendation."""
        level_descriptions = {
            BandwidthLevel.MINIMAL: "minimal computational allocation - basic processing only",
            BandwidthLevel.LOW: "reduced bandwidth allocation - essential processing only",
            BandwidthLevel.MODERATE: "standard bandwidth allocation - balanced resource usage",
            BandwidthLevel.HIGH: "elevated bandwidth allocation - comprehensive processing",
            BandwidthLevel.MAXIMUM: "maximum bandwidth allocation - full computational resources",
        }
        
        return (
            f"Bandwidth level: {bandwidth_level} ({level_descriptions.get(bandwidth_level, 'unknown')}). "
            f"Based on: {base_justification}"
        )
    
    def _generate_resource_justification(
        self,
        resource_demand: ResourceDemandEstimate,
    ) -> str:
        """Generate explanation for resource requirements."""
        return (
            f"Processing effort: {resource_demand.estimated_processing_effort:.2f}. "
            f"Iterations: {resource_demand.expected_iterations}. "
            f"Memory pressure: {resource_demand.memory_pressure_estimate:.2f}. "
            f"Reasoning complexity: {resource_demand.reasoning_complexity}."
        )
    
    def _generate_budget_justification(
        self,
        recommended_budget: float,
        confidence: float,
    ) -> str:
        """Generate explanation for budget recommendation."""
        if recommended_budget >= 0.7:
            budget_reason = "high allocation requested - target requires substantial resources"
        elif recommended_budget >= 0.4:
            budget_reason = "moderate allocation - balanced resource requirements"
        else:
            budget_reason = f"low allocation ({recommended_budget:.1%}) - minimal resources needed"
        
        confidence_str = f"confidence: {confidence:.2f}"
        
        return f"{budget_reason}. {confidence_str}."