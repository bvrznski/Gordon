# Priority Estimation Subsystem
# ================================
#
# Phase 4.2.3: Canonical goal-directed relevance estimation and priority aggregation.
#
# This subsystem computes:
#   • Relevance estimates (goal alignment, context fit)
#   • Priority assessments (computational importance)
#   • Historical influence (persistence, continuity)
#   • Policy modulation (constraints, preferences)
#
# This phase NEVER decides what the agent focuses on.
# It only computes evidence and recommendations.
# ================================================

"""
Goal-Directed Relevance Estimation and Priority Aggregation System.

This module implements Phase 4.2.3 of Gordon's Focusing Network: canonical
computational algorithms for estimating goal-directed attentional relevance
and priority values.

ARCHITECTURAL RESPONSIBILITY:
    This subsystem owns:
        • Goal relevance estimation (alignment with objectives)
        • Context evaluation (situational fit)
        • Policy modulation (constraint adherence)
        • Historical influence (persistence, continuity)
        • Priority aggregation (weighted combination)
        • Priority normalization (bounded scaling)
        • Confidence estimation (assessment reliability)
        • Explainability (rationale generation)

    This subsystem NEVER owns:
        • Attention allocation
        • Competition resolution
        • Suppression logic
        • Decision making
        • Policy creation

INPUTS (projections only):
    FocusCandidate: The target under assessment
    ActiveObjectives: Current objectives (external projection)
    ContextProjection: Current execution context (external)
    WorkingMemoryProjection: Relevant memory state (external)
    HistoricalPriorityState: Previous priority values (external)

OUTPUTS (immutable recommendations):
    PriorityAssessment: Complete priority evaluation
    RelevanceAssessment: Goal and context relevance scores
    PriorityEvidence: Raw scoring components
    PriorityExplanation: Human-readable rationale
    PriorityConfidence: Assessment reliability score
    PriorityVector: Normalized priority representation

No behavioral policy is implemented.
No attention is allocated.
No execution decisions are made.

All computations are deterministic, explainable, and stateless.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)
from datetime import datetime
import math


# =============================================================================
# PUBLIC EXPORTS - Phase 4.2.3 computational models and algorithms
# =============================================================================

__all__ = [
    # Estimators (algorithms)
    "GoalRelevanceEstimator",
    "ContextRelevanceEstimator",
    "PolicyModulator",
    "HistoricalPriorityModel",
    "PriorityAggregator",
    "PriorityNormalizer",
    "PriorityConfidenceEstimator",
    
    # Immutable assessment outputs
    "PriorityAssessment",
    "RelevanceAssessment",
    "PriorityEvidence",
    "PriorityComponent",
    "PriorityContribution",
    "PriorityVector",
    "PriorityBreakdown",
    "PriorityConfidence",
    "PriorityExplanation",
    "PrioritySummary",
    
    # State (for persistence)
    "PriorityState",
    "PriorityHistory",
    "PrioritySnapshots",
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
# IMMUTABLE OUTPUT TYPES
# =============================================================================


@dataclass(frozen=True)
class PriorityComponent:
    """
    A single component of a priority assessment.
    
    Each component represents one computational factor that contributed
    to the final priority estimate.
    """
    
    name: str
    """Identifier for this component (e.g., 'goal_alignment', 'context_fit')."""
    
    raw_value: float
    """Raw component score before weighting (0.0 to 1.0)."""
    
    weight: float
    """Weight applied to this component during aggregation."""
    
    contribution: float
    """Final contribution: raw_value * weight."""
    
    source: str = "unknown"
    """Source of this component (e.g., 'goal_system', 'memory_context')."""
    
    timestamp_utc: Optional[datetime] = None
    """When this component was computed."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "name": self.name,
            "raw_value": self.raw_value,
            "weight": self.weight,
            "contribution": self.contribution,
            "source": self.source,
            "timestamp_utc": (
                self.timestamp_utc.isoformat()
                if self.timestamp_utc else None
            ),
        }


@dataclass(frozen=True)
class PriorityEvidence:
    """
    Raw evidence components for a priority assessment.
    
    Contains all computational factors without aggregation or normalization.
    This is the foundational data that gets processed into assessments.
    """
    
    goal_relevance_score: float
    """Alignment with active objectives (0.0 to 1.0)."""
    
    context_relevance_score: float
    """Fit to current situational context (0.0 to 1.0)."""
    
    policy_conformance_score: float
    """Adherence to policy constraints (0.0 to 1.0)."""
    
    historical_priority: float
    """Previous priority value for continuity estimation."""
    
    expected_progress: Optional[float] = None
    """Expected computational progress from this focus."""
    
    resource_cost: Optional[float] = None
    """Estimated resource cost (lower is better)."""
    
    uncertainty_score: Optional[float] = None
    """Uncertainty in the assessment (0.0 to 1.0, higher is more uncertain)."""
    
    # Component details for explainability
    components: Tuple[PriorityComponent, ...] = field(default_factory=tuple)
    
    def total_weight(self) -> float:
        """Calculate sum of all component weights."""
        return sum(c.weight for c in self.components)
    
    def normalized_evidence(self) -> Dict[str, float]:
        """
        Convert evidence to normalized dictionary representation.
        
        All values are scaled to [0.0, 1.0] range.
        """
        return {
            "goal_relevance_score": clamp(self.goal_relevance_score),
            "context_relevance_score": clamp(self.context_relevance_score),
            "policy_conformance_score": clamp(self.policy_conformance_score),
            "historical_priority": clamp(self.historical_priority),
            "expected_progress": (
                clamp(self.expected_progress) if self.expected_progress is not None
                else 0.5
            ),
            "resource_cost": (
                # Invert resource cost (lower cost = higher score)
                1.0 - clamp(self.resource_cost) if self.resource_cost is not None
                else 0.5
            ),
            "uncertainty_score": (
                clamp(self.uncertainty_score) if self.uncertainty_score is not None
                else 0.5
            ),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "goal_relevance_score": self.goal_relevance_score,
            "context_relevance_score": self.context_relevance_score,
            "policy_conformance_score": self.policy_conformance_score,
            "historical_priority": self.historical_priority,
            "expected_progress": self.expected_progress,
            "resource_cost": self.resource_cost,
            "uncertainty_score": self.uncertainty_score,
            "components": [c.to_dict() for c in self.components],
        }


@dataclass(frozen=True)
class RelevanceAssessment:
    """
    Goal and context relevance assessment for a focus candidate.
    
    Contains scores without priority aggregation.
    This is the foundation upon which priority is built.
    """
    
    goal_relevance: float
    """Alignment with active objectives (0.0 to 1.0)."""
    
    task_relevance: float
    """Alignment with current tasks (0.0 to 1.0)."""
    
    context_relevance: float
    """Fit to current situational context (0.0 to 1.0)."""
    
    recency_score: float
    """How recently this target was relevant (0.0 to 1.0)."""
    
    expected_utility: Optional[float] = None
    """Expected computational utility if focused."""
    
    def quality_score(self) -> float:
        """
        Compute combined relevance quality.
        
        Higher scores indicate better overall relevance fit.
        """
        # Weighted combination of relevance dimensions
        weights = {
            "goal": 0.4,
            "task": 0.3,
            "context": 0.2,
            "recency": 0.1,
        }
        
        score = (
            self.goal_relevance * weights["goal"] +
            self.task_relevance * weights["task"] +
            self.context_relevance * weights["context"] +
            self.recency_score * weights["recency"]
        )
        
        return clamp(score)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "goal_relevance": self.goal_relevance,
            "task_relevance": self.task_relevance,
            "context_relevance": self.context_relevance,
            "recency_score": self.recency_score,
            "expected_utility": self.expected_utility,
            "quality_score": self.quality_score(),
        }


@dataclass(frozen=True)
class PriorityVector:
    """
    Normalized priority representation for comparison and storage.
    
    Contains the final computed priority values after normalization
    and aggregation. This is the output format used by other subsystems.
    """
    
    normalized_priority: float
    """Final normalized priority value (0.0 to 1.0)."""
    
    goal_weighted_priority: float
    """Priority emphasizing goal alignment."""
    
    context_weighted_priority: float
    """Priority emphasizing context fit."""
    
    historical_weighted_priority: float
    """Priority emphasizing historical continuity."""
    
    # Normalization metadata
    min_input_priority: float = 0.0
    max_input_priority: float = 1.0
    normalization_method: str = "min_max"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "normalized_priority": self.normalized_priority,
            "goal_weighted_priority": self.goal_weighted_priority,
            "context_weighted_priority": self.context_weighted_priority,
            "historical_weighted_priority": self.historical_weighted_priority,
            "min_input_priority": self.min_input_priority,
            "max_input_priority": self.max_input_priority,
            "normalization_method": self.normalization_method,
        }


@dataclass(frozen=True)
class PriorityBreakdown:
    """
    Detailed breakdown of how priority was computed.
    
    Contains all components with their individual contributions
    and the aggregation rationale. This enables explainability.
    """
    
    # Aggregated values
    total_priority: float
    """Final aggregated priority before normalization."""
    
    weighted_sum: float
    """Sum of (component_score * component_weight)."""
    
    weight_total: float
    """Sum of all weights."""
    
    # Component contributions (ordered by contribution)
    component_contributions: Tuple[PriorityComponent, ...]
    
    # Normalization details
    original_min: Optional[float] = None
    original_max: Optional[float] = None
    
    normalized_min: float = 0.0
    normalized_max: float = 1.0
    
    def contribution_percentages(self) -> Dict[str, float]:
        """
        Calculate percentage contribution of each component.
        
        Returns dictionary mapping component names to their percentage
        contribution (all values sum to ~1.0).
        """
        if self.weighted_sum == 0:
            return {c.name: 0.0 for c in self.component_contributions}
        
        return {
            c.name: (
                (c.contribution / self.weighted_sum) * 100.0
                if self.weighted_sum > 0 else 0.0
            )
            for c in self.component_contributions
        }
    
    def dominant_components(self, threshold: float = 10.0) -> Tuple[str, ...]:
        """
        Get components with significant contributions.
        
        Components contributing at least 'threshold' percent of total.
        """
        percentages = self.contribution_percentages()
        return tuple(
            name for name, pct in percentages.items() if pct >= threshold
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "total_priority": self.total_priority,
            "weighted_sum": self.weighted_sum,
            "weight_total": self.weight_total,
            "component_contributions": [
                c.to_dict() for c in self.component_contributions
            ],
            "contribution_percentages": self.contribution_percentages(),
            "dominant_components": self.dominant_components(),
        }


@dataclass(frozen=True)
class PriorityConfidence:
    """
    Confidence assessment for a priority estimation.
    
    Measures the reliability of the computed priority value.
    Higher confidence means more data/less uncertainty went into the estimate.
    """
    
    score: float
    """Confidence in the priority estimate (0.0 to 1.0)."""
    
    # Confidence factors
    input_completeness_score: float
    """How complete were the inputs?"""
    
    context_quality_score: float
    """Quality of contextual information."""
    
    historical_consistency_score: float
    """Consistency with historical priority patterns."""
    
    computation_stability_score: float
    """Stability of the aggregation algorithm."""
    
    # Metadata
    confidence_factors: Tuple[str, ...] = field(default_factory=tuple)
    """Human-readable factors that influenced confidence."""
    
    uncertainty_sources: Tuple[str, ...] = field(default_factory=tuple)
    """Identified sources of uncertainty."""
    
    @classmethod
    def low_confidence(cls) -> "PriorityConfidence":
        """Create a low-confidence assessment (default fallback)."""
        return cls(
            score=0.3,
            input_completeness_score=0.5,
            context_quality_score=0.4,
            historical_consistency_score=0.3,
            computation_stability_score=0.6,
        )
    
    @classmethod
    def high_confidence(cls) -> "PriorityConfidence":
        """Create a high-confidence assessment."""
        return cls(
            score=0.85,
            input_completeness_score=0.9,
            context_quality_score=0.85,
            historical_consistency_score=0.8,
            computation_stability_score=0.9,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "score": self.score,
            "input_completeness_score": self.input_completeness_score,
            "context_quality_score": self.context_quality_score,
            "historical_consistency_score": self.historical_consistency_score,
            "computation_stability_score": self.computation_stability_score,
            "confidence_factors": list(self.confidence_factors),
            "uncertainty_sources": list(self.uncertainty_sources),
        }


@dataclass(frozen=True)
class PriorityExplanation:
    """
    Human-readable explanation of a priority assessment.
    
    Contains the rationale for why this candidate received
    its priority value, including which factors were most important.
    """
    
    # Core assessment
    target_id: str
    """ID of the focus target being assessed."""
    
    final_priority: float
    """The computed priority (0.0 to 1.0)."""
    
    # Explanation sections
    goal_alignment_rationale: str
    """Why this aligns with active objectives."""
    
    context_fit_rationale: str
    """Why this fits the current situation."""
    
    policy_compliance_rationale: str
    """How this respects constraints."""
    
    historical_continuity_rationale: str
    """How this maintains focus continuity."""
    
    # Component breakdown
    contribution_summary: Dict[str, float]
    """Component names to their normalized contributions."""
    
    dominant_factors: Tuple[str, ...]
    """Most influential factors in the final priority."""
    
    confidence_assessment: PriorityConfidence
    
    timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    """When this explanation was generated."""
    
    def summary(self) -> str:
        """
        Generate a concise natural-language summary.
        
        Example:
            "Priority 0.82 (confidence: 0.91). Primarily driven by 
             goal_alignment (45%) and context_fit (30%)."
        """
        confidence_str = f"confidence: {self.confidence_assessment.score:.2f}"
        
        if self.dominant_factors:
            factors = ", ".join(
                f"{f} ({self.contribution_summary.get(f, 0):.0f}%)"
                for f in self.dominant_factors[:3]
            )
            return (
                f"Priority {self.final_priority:.2f} "
                f"({confidence_str}). "
                f"Driven by: {factors}."
            )
        
        return (
            f"Priority {self.final_priority:.2f} "
            f"({confidence_str}). "
            "No dominant factors identified."
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "target_id": self.target_id,
            "final_priority": self.final_priority,
            "goal_alignment_rationale": self.goal_alignment_rationale,
            "context_fit_rationale": self.context_fit_rationale,
            "policy_compliance_rationale": self.policy_compliance_rationale,
            "historical_continuity_rationale": self.historical_continuity_rationale,
            "contribution_summary": self.contribution_summary,
            "dominant_factors": list(self.dominant_factors),
            "confidence_assessment": self.confidence_assessment.to_dict(),
            "timestamp_utc": self.timestamp_utc.isoformat(),
        }


@dataclass(frozen=True)
class PrioritySummary:
    """
    High-level summary of priority assessments for multiple candidates.
    
    Used for reporting and diagnostics without exposing full details.
    """
    
    candidate_count: int
    """Number of candidates assessed."""
    
    average_priority: float
    """Mean priority across all candidates."""
    
    max_priority: float
    """Highest priority among candidates."""
    
    min_priority: float
    """Lowest priority among candidates."""
    
    priority_variance: float
    """Variance in priorities (higher = more spread out)."""
    
    high_priority_count: int
    """Candidates with priority >= 0.7."""
    
    low_priority_count: int
    """Candidates with priority <= 0.3."""
    
    timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    """When this summary was generated."""
    
    @classmethod
    def compute(
        cls,
        priorities: Sequence[float],
    ) -> "PrioritySummary":
        """
        Compute summary from a sequence of priority values.
        
        Args:
            priorities: List or tuple of priority scores (0.0 to 1.0)
            
        Returns:
            PrioritySummary with computed statistics
        """
        if not priorities:
            return cls(
                candidate_count=0,
                average_priority=0.0,
                max_priority=0.0,
                min_priority=0.0,
                priority_variance=0.0,
                high_priority_count=0,
                low_priority_count=0,
            )
        
        n = len(priorities)
        avg = sum(priorities) / n
        
        # Variance calculation
        variance = sum((p - avg) ** 2 for p in priorities) / n if n > 1 else 0.0
        
        # Count high/low priority candidates
        high_count = sum(1 for p in priorities if p >= 0.7)
        low_count = sum(1 for p in priorities if p <= 0.3)
        
        return cls(
            candidate_count=n,
            average_priority=avg,
            max_priority=max(priorities),
            min_priority=min(priorities),
            priority_variance=variance,
            high_priority_count=high_count,
            low_priority_count=low_count,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "candidate_count": self.candidate_count,
            "average_priority": self.average_priority,
            "max_priority": self.max_priority,
            "min_priority": self.min_priority,
            "priority_variance": self.priority_variance,
            "high_priority_count": self.high_priority_count,
            "low_priority_count": self.low_priority_count,
            "timestamp_utc": self.timestamp_utc.isoformat(),
        }


@dataclass(frozen=True)
class PriorityAssessment:
    """
    Complete priority assessment for a single focus candidate.
    
    This is the primary output of Phase 4.2.3 - a comprehensive
    evaluation containing all computational evidence and explanations.
    
    NO DECISIONS ARE MADE IN THIS CLASS. It only computes and explains.
    """
    
    # Core identification
    target_id: str
    """ID of the focus target being assessed."""
    
    candidate_id: str
    """ID of this assessment cycle's candidate."""
    
    timestamp_utc: datetime
    """When this assessment was generated."""
    
    # Primary output
    priority: float
    """Final normalized priority (0.0 to 1.0)."""
    
    # Detailed assessments
    relevance_assessment: RelevanceAssessment
    """Goal and context relevance breakdown."""
    
    priority_evidence: PriorityEvidence
    """Raw scoring components."""
    
    priority_vector: PriorityVector
    """Normalized priority representation."""
    
    priority_breakdown: PriorityBreakdown
    """Detailed computation explanation."""
    
    confidence: PriorityConfidence
    """Assessment reliability score."""
    
    explanation: PriorityExplanation
    """Human-readable rationale."""
    
    # Validation
    is_finite: bool = True
    """Whether all computed values are finite (not NaN/inf)."""
    
    is_normalized: bool = True
    """Whether priority is within [0.0, 1.0] bounds."""
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert assessment to serializable dictionary.
        
        This is the canonical export format for diagnostics and storage.
        """
        return {
            "target_id": self.target_id,
            "candidate_id": self.candidate_id,
            "timestamp_utc": self.timestamp_utc.isoformat(),
            
            # Primary output
            "priority": self.priority,
            
            # Detailed assessments
            "relevance_assessment": self.relevance_assessment.to_dict(),
            "priority_evidence": self.priority_evidence.to_dict(),
            "priority_vector": self.priority_vector.to_dict(),
            "priority_breakdown": self.priority_breakdown.to_dict(),
            "confidence": self.confidence.to_dict(),
            "explanation": self.explanation.to_dict(),
            
            # Validation
            "is_finite": self.is_finite,
            "is_normalized": self.is_normalized,
        }


# =============================================================================
# STATE CLASSES - For persistence across assessment cycles
# =============================================================================


@dataclass(frozen=True)
class PriorityHistory:
    """
    Bounded history of priority assessments.
    
    Maintains recent priority values for continuity estimation
    and historical influence computation.
    """
    
    # Configuration
    max_entries: int = 100
    
    # Historical entries (chronological, newest at end)
    _entries: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def create(cls, max_entries: int = 100) -> "PriorityHistory":
        """Create a new history instance."""
        return cls(max_entries=max_entries)
    
    def append(self, entry: Dict[str, Any]) -> "PriorityHistory":
        """
        Add a new priority assessment to history.
        
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
    
    def get_priority_history(self) -> Tuple[float, ...]:
        """Extract just the priority values from history."""
        return tuple(
            entry.get("priority", 0.5)
            for entry in self._entries
        )
    
    def continuity_score(self) -> float:
        """
        Estimate focus continuity from historical patterns.
        
        Higher score indicates more stable, continuous priority.
        """
        priorities = self.get_priority_history()
        
        if len(priorities) < 2:
            return 0.5
        
        # Compute variance (lower = more stable/continuous)
        avg = sum(priorities) / len(priorities)
        variance = sum((p - avg) ** 2 for p in priorities) / len(priorities)
        
        # Convert to continuity score (inverse relationship)
        # Variance of 0 → score 1.0, variance > 1.0 → score approaches 0
        continuity = 1.0 / (1.0 + variance)
        
        return clamp(continuity)
    
    def trend_direction(self) -> str:
        """
        Determine historical priority trend direction.
        
        Returns: 'increasing', 'decreasing', 'stable', or 'unknown'
        """
        priorities = self.get_priority_history()
        
        if len(priorities) < 2:
            return "unknown"
        
        # Simple linear trend detection
        n = len(priorities)
        first_half_avg = sum(priorities[:n//2]) / (n//2)
        second_half_avg = sum(priorities[n//2:]) / (n - n//2)
        
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
            "latest_priorities": list(self.get_priority_history()[-10:]),
        }


@dataclass(frozen=True)
class PrioritySnapshots:
    """
    Immutable snapshots of priority state at specific points in time.
    
    Used for replay, diagnostics, and auditing without modifying live state.
    """
    
    # Configuration
    max_snapshots: int = 50
    
    # Snapshots (chronological, newest at end)
    _snapshots: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def create(cls, max_snapshots: int = 50) -> "PrioritySnapshots":
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
class PriorityState:
    """
    Persistent state for the priority computation subsystem.
    
    Maintains historical information and configuration while
    remaining immutable between assessment cycles.
    """
    
    # History tracking
    history: PriorityHistory = field(default_factory=PriorityHistory.create)
    
    # Snapshots
    snapshots: PrioritySnapshots = field(default_factory=PrioritySnapshots.create)
    
    # Configuration (immutable once set)
    default_weight_goal_relevance: float = 0.35
    default_weight_context_relevance: float = 0.25
    default_weight_policy_conformance: float = 0.15
    default_weight_historical_priority: float = 0.15
    default_weight_uncertainty_penalty: float = 0.10
    
    # Metadata
    state_id: str = field(default_factory=lambda: f"priority_state_{id(object())}")
    
    def update_history(
        self,
        assessment_result: Dict[str, Any],
    ) -> "PriorityState":
        """
        Update history with a new priority assessment result.
        
        Args:
            assessment_result: Result dictionary from PriorityAssessment
            
        Returns:
            New PriorityState with updated history
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
                "goal_relevance": self.default_weight_goal_relevance,
                "context_relevance": self.default_weight_context_relevance,
                "policy_conformance": self.default_weight_policy_conformance,
                "historical_priority": self.default_weight_historical_priority,
                "uncertainty_penalty": self.default_weight_uncertainty_penalty,
            },
        }


# =============================================================================
# COMPUTATIONAL ESTIMATORS (ALGORITHMS)
# =============================================================================


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass instance.
    
    Creates a new copy with specified fields updated while maintaining
    immutability guarantees.
    """
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {
            f.name: getattr(obj, f.name)
            for f in obj.__dataclass_fields__.values()
        }
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError(f"Object {obj} is not a dataclass")


# -----------------------------------------------------------------------------
# GOAL RELEVANCE ESTIMATOR
# -----------------------------------------------------------------------------


class GoalRelevanceEstimator:
    """
    Estimate how strongly a candidate contributes to active objectives.
    
    This estimator computes goal alignment scores based on:
        • Objective similarity
        • Expected contribution
        • Progress toward goals
        • Dependency satisfaction
    
    NO BEHAVIOR IS IMPLEMENTED. This only estimates relevance.
    """
    
    def __init__(
        self,
        weight_goal_alignment: float = 1.0,
    ):
        """
        Initialize the goal relevance estimator.
        
        Args:
            weight_goal_alignment: Weight for goal alignment in aggregation
        """
        self.weight_goal_alignment = weight_goal_alignment
    
    def estimate(
        self,
        candidate_target_id: str,
        active_objectives: Sequence[str],
        context_projection: Mapping[str, Any],
    ) -> float:
        """
        Estimate goal relevance for a candidate.
        
        Args:
            candidate_target_id: ID of the candidate to assess
            active_objectives: List of currently active objective strings
            context_projection: Current execution context as mapping
            
        Returns:
            Goal relevance score (0.0 to 1.0)
            
        NOTE: This is a computational estimation, NOT decision making.
        """
        # Default: no objectives = neutral relevance
        if not active_objectives:
            return 0.5
        
        # Get candidate metadata from context (if available)
        candidate_metadata = self._get_candidate_metadata(
            candidate_target_id,
            context_projection,
        )
        
        # Estimate based on available signals
        # These are placeholder heuristics - actual implementation would use
        # domain-specific semantic analysis
        
        signal_scores = []
        
        # Signal 1: Objective overlap (if metadata contains objective references)
        if "objectives" in candidate_metadata:
            obj_overlap = self._compute_objective_overlap(
                set(active_objectives),
                set(candidate_metadata["objectives"]),
            )
            signal_scores.append(obj_overlap)
        
        # Signal 2: Task dependency (if task info is present)
        if "task_dependencies" in candidate_metadata:
            dep_score = self._estimate_dependency_satisfaction(
                candidate_metadata["task_dependencies"],
                context_projection,
            )
            signal_scores.append(dep_score)
        
        # Signal 3: Expected progress
        expected_progress = candidate_metadata.get("expected_progress")
        if expected_progress is not None:
            # Normalize to [0, 1] range assuming progress is measured in some unit
            normalized_progress = normalize(float(expected_progress), 0.0, 100.0)
            signal_scores.append(normalized_progress)
        
        # Signal 4: Constraint satisfaction
        constraint_score = self._estimate_constraint_satisfaction(
            candidate_metadata.get("constraints", []),
            context_projection,
        )
        signal_scores.append(constraint_score)
        
        if not signal_scores:
            return 0.5  # No signals = neutral
        
        # Average of signals
        base_score = sum(signal_scores) / len(signal_scores)
        
        # Apply weight (in aggregation, this will be combined with other weights)
        weighted_score = base_score * self.weight_goal_alignment
        
        return clamp(weighted_score)
    
    def _get_candidate_metadata(
        self,
        candidate_id: str,
        context: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """Extract metadata for a candidate from context."""
        # Context structure depends on external systems
        # This is a placeholder implementation
        
        # Look for candidate metadata in common locations
        if "candidates" in context:
            candidates = context["candidates"]
            if isinstance(candidates, dict):
                return candidates.get(candidate_id, {}).get("metadata", {})
        
        if "candidate_metadata" in context:
            return context["candidate_metadata"].get(candidate_id, {})
        
        return {}
    
    def _compute_objective_overlap(
        self,
        active_objectives: set,
        candidate_objectives: set,
    ) -> float:
        """Compute overlap between active objectives and candidate's objectives."""
        if not active_objectives or not candidate_objectives:
            return 0.5
        
        intersection = len(active_objectives & candidate_objectives)
        union = len(active_objectives | candidate_objectives)
        
        # Jaccard similarity
        return intersection / union if union > 0 else 0.0
    
    def _estimate_dependency_satisfaction(
        self,
        dependencies: Sequence[str],
        context: Mapping[str, Any],
    ) -> float:
        """Estimate how well current context satisfies candidate dependencies."""
        # Placeholder: check if dependencies are mentioned in context
        if not dependencies:
            return 1.0
        
        context_str = str(context).lower()
        
        satisfied_deps = sum(
            1 for dep in dependencies
            if any(word in context_str for word in dep.lower().split())
        )
        
        return satisfied_deps / len(dependencies) if dependencies else 1.0
    
    def _estimate_constraint_satisfaction(
        self,
        constraints: Sequence[str],
        context: Mapping[str, Any],
    ) -> float:
        """Estimate how well current context satisfies constraints."""
        if not constraints:
            return 1.0
        
        # Check for constraint satisfaction signals in context
        context_str = str(context).lower()
        
        satisfied = sum(
            1 for c in constraints
            if any(signal in context_str for signal in ["compliant", "allowed", "permitted"])
        )
        
        return clamp(satisfied / len(constraints)) if constraints else 1.0
    
    def estimate_full(
        self,
        candidate_target_id: str,
        active_objectives: Sequence[str],
        context_projection: Mapping[str, Any],
        historical_priorities: Optional[Sequence[float]] = None,
    ) -> Tuple[float, PriorityComponent]:
        """
        Full goal relevance estimation with contribution tracking.
        
        Returns:
            Tuple of (score, component) where component captures the evidence
        """
        score = self.estimate(
            candidate_target_id,
            active_objectives,
            context_projection,
        )
        
        component = PriorityComponent(
            name="goal_relevance",
            raw_value=score,
            weight=self.weight_goal_alignment,
            contribution=score * self.weight_goal_alignment,
            source="goal_system",
            timestamp_utc=datetime.utcnow(),
        )
        
        return score, component


# -----------------------------------------------------------------------------
# CONTEXT RELEVANCE ESTIMATOR
# -----------------------------------------------------------------------------


class ContextRelevanceEstimator:
    """
    Estimate how well a candidate fits the current situational context.
    
    This estimator evaluates:
        • Current conversation/state
        • Task progress
        • Environmental conditions
        • Memory availability
    
    NO BEHAVIOR IS IMPLEMENTED. This only estimates fit.
    """
    
    def __init__(
        self,
        weight_current_context: float = 0.4,
        weight_task_progress: float = 0.3,
        weight_memory_context: float = 0.2,
        weight_environmental_fit: float = 0.1,
    ):
        """
        Initialize the context relevance estimator.
        
        Args:
            weight_current_context: Weight for current situational context
            weight_task_progress: Weight for task progress alignment
            weight_memory_context: Weight for memory-based context
            weight_environmental_fit: Weight for environmental conditions
        """
        self.weight_current_context = weight_current_context
        self.weight_task_progress = weight_task_progress
        self.weight_memory_context = weight_memory_context
        self.weight_environmental_fit = weight_environmental_fit
    
    def estimate(
        self,
        candidate_target_id: str,
        current_context: Mapping[str, Any],
    ) -> float:
        """
        Estimate context relevance for a candidate.
        
        Args:
            candidate_target_id: ID of the candidate to assess
            current_context: Current execution context mapping
            
        Returns:
            Context relevance score (0.0 to 1.0)
        """
        # Extract context components
        conversation_state = self._get_conversation_state(current_context)
        task_state = self._get_task_state(current_context)
        memory_state = self._get_memory_state(current_context)
        environmental_state = self._get_environmental_state(current_context)
        
        # Compute individual scores
        context_score = self._estimate_conversation_fit(
            candidate_target_id,
            conversation_state,
        )
        
        progress_score = self._estimate_task_progress_alignment(
            candidate_target_id,
            task_state,
        )
        
        memory_score = self._estimate_memory_relevance(
            candidate_target_id,
            memory_state,
        )
        
        environment_score = self._estimate_environmental_fit(
            candidate_target_id,
            environmental_state,
        )
        
        # Weighted combination
        score = (
            context_score * self.weight_current_context +
            progress_score * self.weight_task_progress +
            memory_score * self.weight_memory_context +
            environment_score * self.weight_environmental_fit
        )
        
        return clamp(score)
    
    def _get_conversation_state(
        self,
        context: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """Extract conversation state from context."""
        if "conversation" in context:
            return context["conversation"]
        if "current_topic" in context or "active_discussion" in context:
            return {
                "topic": context.get("current_topic", ""),
                "participants": context.get("participants", []),
            }
        return {}
    
    def _get_task_state(
        self,
        context: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """Extract task state from context."""
        if "tasks" in context:
            return context["tasks"]
        if "current_task" in context or "active_tasks" in context:
            return {
                "current": context.get("current_task"),
                "completed": context.get("completed_tasks", []),
                "pending": context.get("pending_tasks", []),
            }
        return {}
    
    def _get_memory_state(
        self,
        context: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """Extract memory state from context."""
        if "memory" in context:
            return context["memory"]
        if "relevant_memories" in context or "working_memory" in context:
            return {
                "recent": context.get("recent_memories", []),
                "active": context.get("working_memory", {}),
            }
        return {}
    
    def _get_environmental_state(
        self,
        context: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """Extract environmental state from context."""
        if "environment" in context:
            return context["environment"]
        return {}
    
    def _estimate_conversation_fit(
        self,
        candidate_id: str,
        conversation_state: Mapping[str, Any],
    ) -> float:
        """Estimate how well candidate fits current conversation."""
        # Placeholder implementation
        if not conversation_state:
            return 0.5
        
        # Check for mention in current topic
        topic = conversation_state.get("topic", "")
        if candidate_id.lower() in str(topic).lower():
            return 1.0
        
        return 0.3
    
    def _estimate_task_progress_alignment(
        self,
        candidate_id: str,
        task_state: Mapping[str, Any],
    ) -> float:
        """Estimate how well candidate aligns with current task progress."""
        # Placeholder implementation
        if not task_state:
            return 0.5
        
        # Check if candidate is referenced in current/pending tasks
        current_task = task_state.get("current", "")
        pending = task_state.get("pending", [])
        
        if any(candidate_id.lower() in str(item).lower() for item in [current_task] + list(pending)):
            return 0.8
        
        return 0.4
    
    def _estimate_memory_relevance(
        self,
        candidate_id: str,
        memory_state: Mapping[str, Any],
    ) -> float:
        """Estimate relevance based on working memory activation."""
        # Placeholder implementation
        if not memory_state:
            return 0.5
        
        recent = memory_state.get("recent", [])
        
        if any(candidate_id.lower() in str(mem).lower() for mem in recent):
            return 0.9
        
        return 0.4
    
    def _estimate_environmental_fit(
        self,
        candidate_id: str,
        environmental_state: Mapping[str, Any],
    ) -> float:
        """Estimate fit with current environmental conditions."""
        # Placeholder implementation
        if not environmental_state:
            return 0.5
        
        # Check for environmental constraints that might affect relevance
        constraints = environmental_state.get("constraints", [])
        
        if any(c.lower() in ["blocked", "infeasible"] for c in constraints):
            return 0.2
        
        return 0.7
    
    def estimate_full(
        self,
        candidate_target_id: str,
        current_context: Mapping[str, Any],
    ) -> Tuple[float, PriorityComponent]:
        """
        Full context relevance estimation with contribution tracking.
        
        Returns:
            Tuple of (score, component) where component captures the evidence
        """
        score = self.estimate(candidate_target_id, current_context)
        
        component = PriorityComponent(
            name="context_relevance",
            raw_value=score,
            weight=(
                self.weight_current_context +
                self.weight_task_progress +
                self.weight_memory_context +
                self.weight_environmental_fit
            ),
            contribution=score * (
                self.weight_current_context +
                self.weight_task_progress +
                self.weight_memory_context +
                self.weight_environmental_fit
            ),
            source="context_projections",
            timestamp_utc=datetime.utcnow(),
        )
        
        return score, component


# -----------------------------------------------------------------------------
# POLICY MODULATOR
# -----------------------------------------------------------------------------


class PolicyModulator:
    """
    Apply policy constraints to priority estimates.
    
    This modulator adjusts scores based on:
        • User preferences
        • System policies
        • Safety constraints
        • Organizational rules
    
    Policy NEVER creates priority - it only modulates existing evidence.
    """
    
    def __init__(
        self,
        default_modulation_factor: float = 1.0,
    ):
        """
        Initialize the policy modulator.
        
        Args:
            default_modulation_factor: Base factor for policy adjustments
        """
        self.default_modulation_factor = default_modulation_factor
    
    def modulate(
        self,
        base_priority: float,
        policy_constraints: Sequence[str],
        user_preferences: Optional[Mapping[str, Any]] = None,
        resource_limits: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[float, PriorityComponent]:
        """
        Apply policy modulation to a priority estimate.
        
        Args:
            base_priority: The base priority score (0.0 to 1.0)
            policy_constraints: List of active policy constraint strings
            user_preferences: Optional user preference mapping
            resource_limits: Optional resource constraint mapping
            
        Returns:
            Tuple of (modulated_priority, component) where component captures evidence
        """
        # Start with base priority
        adjusted = base_priority
        
        modulation_factors = []
        
        # Check each policy constraint
        for constraint in policy_constraints:
            factor = self._compute_constraint_factor(constraint)
            modulation_factors.append(factor)
            if factor < 1.0:
                adjusted *= factor
        
        # Apply user preferences (if present)
        if user_preferences:
            pref_factor = self._compute_preference_factor(user_preferences)
            modulation_factors.append(pref_factor)
            adjusted *= pref_factor
        
        # Apply resource limits (if present)
        if resource_limits:
            resource_factor = self._compute_resource_factor(resource_limits)
            modulation_factors.append(resource_factor)
            adjusted *= resource_factor
        
        component = PriorityComponent(
            name="policy_modulation",
            raw_value=base_priority,
            weight=self.default_modulation_factor,
            contribution=adjusted * self.default_modulation_factor,
            source="policy_system",
            timestamp_utc=datetime.utcnow(),
        )
        
        return clamp(adjusted), component
    
    def _compute_constraint_factor(self, constraint: str) -> float:
        """Compute adjustment factor for a policy constraint."""
        # Placeholder implementation
        constraint_lower = constraint.lower()
        
        if "blocked" in constraint_lower or "denied" in constraint_lower:
            return 0.1  # Strong reduction
        
        if "restricted" in constraint_lower or "limited" in constraint_lower:
            return 0.5  # Moderate reduction
        
        if "required" in constraint_lower or "must" in constraint_lower:
            return 1.2  # Slight boost for required items
        
        return 1.0  # No effect
    
    def _compute_preference_factor(
        self,
        preferences: Mapping[str, Any],
    ) -> float:
        """Compute adjustment factor based on user preferences."""
        # Placeholder implementation
        if not preferences:
            return 1.0
        
        # Check for preference-based boosts
        if "priority_boost" in preferences:
            boost = preferences["priority_boost"]
            return clamp(1.0 + boost)
        
        return 1.0
    
    def _compute_resource_factor(
        self,
        resource_limits: Mapping[str, Any],
    ) -> float:
        """Compute adjustment factor based on resource availability."""
        # Placeholder implementation
        if not resource_limits:
            return 1.0
        
        available = resource_limits.get("available", 1.0)
        required = resource_limits.get("required", 0.5)
        
        ratio = available / max(required, 0.01)
        
        # Higher ratio = more resources available = higher factor
        return clamp(ratio)


# -----------------------------------------------------------------------------
# HISTORICAL PRIORITY MODEL
# -----------------------------------------------------------------------------


class HistoricalPriorityModel:
    """
    Estimate priority based on historical patterns and continuity.
    
    This model uses past assessments to inform current estimates:
        • Priority persistence (maintain focus)
        • Transition history (when to shift)
        • Historical importance (long-term significance)
    
    Historical data provides stability, preventing oscillation.
    """
    
    def __init__(
        self,
        weight_continuity: float = 0.6,
        weight_history_strength: float = 0.3,
        weight_transition_bias: float = 0.1,
    ):
        """
        Initialize the historical priority model.
        
        Args:
            weight_continuity: Weight for maintaining current focus
            weight_history_strength: Weight for historical importance
            weight_transition_bias: Weight for transition-related factors
        """
        self.weight_continuity = weight_continuity
        self.weight_history_strength = weight_history_strength
        self.weight_transition_bias = weight_transition_bias
    
    def estimate(
        self,
        candidate_target_id: str,
        historical_priorities: Sequence[float],
        recent_transitions: Optional[Sequence[Dict[str, Any]]] = None,
    ) -> Tuple[float, PriorityComponent]:
        """
        Estimate priority from historical patterns.
        
        Args:
            candidate_target_id: ID of the candidate
            historical_priorities: Previous priority values (newest first)
            recent_transitions: Optional transition history
            
        Returns:
            Tuple of (historical_priority_score, component)
        """
        if not historical_priorities:
            return 0.5, PriorityComponent(
                name="historical_priority",
                raw_value=0.5,
                weight=self.weight_continuity,
                contribution=0.5 * self.weight_continuity,
                source="none",
                timestamp_utc=datetime.utcnow(),
            )
        
        # Compute continuity score (how stable is this target's priority?)
        continuity = self._compute_continuity(historical_priorities)
        
        # Compute historical strength (average of recent values)
        recent_history = historical_priorities[:10]  # Last 10 assessments
        history_strength = sum(recent_history) / len(recent_history)
        
        # Check transition patterns
        transition_bias = self._estimate_transition_bias(
            candidate_target_id,
            recent_transitions or [],
            historical_priorities,
        )
        
        # Weighted combination
        score = (
            continuity * self.weight_continuity +
            history_strength * self.weight_history_strength +
            (1.0 - transition_bias) * self.weight_transition_bias  # Lower bias = higher score
        )
        
        component = PriorityComponent(
            name="historical_priority",
            raw_value=score,
            weight=(
                self.weight_continuity +
                self.weight_history_strength +
                self.weight_transition_bias
            ),
            contribution=score * (
                self.weight_continuity +
                self.weight_history_strength +
                self.weight_transition_bias
            ),
            source="priority_history",
            timestamp_utc=datetime.utcnow(),
        )
        
        return clamp(score), component
    
    def _compute_continuity(self, history: Sequence[float]) -> float:
        """
        Compute focus continuity from historical priorities.
        
        Higher score = more stable/continuous priority pattern.
        """
        if len(history) < 2:
            return 0.5
        
        # Compute variance (lower = more continuous)
        avg = sum(history) / len(history)
        variance = sum((h - avg) ** 2 for h in history) / len(history)
        
        # Convert to continuity score
        continuity = 1.0 / (1.0 + variance)
        
        return clamp(continuity)
    
    def _estimate_transition_bias(
        self,
        candidate_id: str,
        transitions: Sequence[Dict[str, Any]],
        historical_priorities: Sequence[float],
    ) -> float:
        """
        Estimate transition-related bias for a candidate.
        
        Returns a bias factor where higher = more likely to be selected
        due to recent transition patterns.
        """
        if not transitions:
            return 0.5
        
        # Count recent transitions involving this candidate
        relevant_transitions = sum(
            1 for t in transitions
            if candidate_id in str(t.get("affected_targets", []))
        )
        
        # Check direction of last transition
        last_transition = transitions[-1] if transitions else {}
        is_last_transition = (
            last_transition.get("destination_target") == candidate_id
        )
        
        # Compute bias based on patterns
        bias_score = 0.5
        
        # Boost if recently transitioning to this target
        if is_last_transition:
            bias_score += 0.2
        
        # Boost if frequently involved in transitions
        if relevant_transitions > len(transitions) / 2:
            bias_score += 0.15
        
        return clamp(bias_score)
    
    def get_continuity_from_history(
        self,
        history: PriorityHistory,
    ) -> float:
        """
        Get continuity score directly from PriorityHistory.
        
        Args:
            history: The historical priority data
            
        Returns:
            Continuity score (0.0 to 1.0)
        """
        return history.continuity_score()


# -----------------------------------------------------------------------------
# PRIORITY AGGREGATOR
# -----------------------------------------------------------------------------


class PriorityAggregator:
    """
    Aggregate all relevance and priority components into a final estimate.
    
    This aggregator combines:
        • Goal relevance scores
        • Context relevance scores
        • Policy modulation effects
        • Historical influence
    
    The aggregation is deterministic and replaceable.
    No competition or suppression logic is implemented here.
    """
    
    def __init__(
        self,
        weight_goal_relevance: float = 0.35,
        weight_context_relevance: float = 0.25,
        weight_policy_modulation: float = 0.15,
        weight_historical_priority: float = 0.15,
        weight_uncertainty_penalty: float = 0.10,
    ):
        """
        Initialize the priority aggregator.
        
        Args:
            weight_goal_relevance: Weight for goal alignment
            weight_context_relevance: Weight for situational fit
            weight_policy_modulation: Weight for policy adjustments
            weight_historical_priority: Weight for historical patterns
            weight_uncertainty_penalty: Penalty for uncertain assessments
        """
        self.weight_goal_relevance = weight_goal_relevance
        self.weight_context_relevance = weight_context_relevance
        self.weight_policy_modulation = weight_policy_modulation
        self.weight_historical_priority = weight_historical_priority
        self.weight_uncertainty_penalty = weight_uncertainty_penalty
        
        # Validate weights sum to ~1.0
        total_weight = (
            weight_goal_relevance +
            weight_context_relevance +
            weight_policy_modulation +
            weight_historical_priority +
            weight_uncertainty_penalty
        )
        
        if abs(total_weight - 1.0) > 0.01:
            # Normalize weights to sum to 1.0
            self.weight_goal_relevance /= total_weight
            self.weight_context_relevance /= total_weight
            self.weight_policy_modulation /= total_weight
            self.weight_historical_priority /= total_weight
            self.weight_uncertainty_penalty /= total_weight
    
    def aggregate(
        self,
        goal_relevance_score: float,
        context_relevance_score: float,
        policy_conformance_score: float,
        historical_priority_score: float,
        uncertainty_score: Optional[float] = None,
    ) -> Tuple[float, PriorityEvidence]:
        """
        Aggregate all relevance scores into a priority estimate.
        
        Args:
            goal_relevance_score: Goal alignment (0.0 to 1.0)
            context_relevance_score: Context fit (0.0 to 1.0)
            policy_conformance_score: Policy adherence (0.0 to 1.0)
            historical_priority_score: Historical influence (0.0 to 1.0)
            uncertainty_score: Optional assessment uncertainty (0.0 to 1.0, higher = more uncertain)
            
        Returns:
            Tuple of (priority_estimate, evidence) where evidence captures all components
        """
        # Base scores (weighted sum)
        weighted_scores = {
            "goal_relevance": goal_relevance_score * self.weight_goal_relevance,
            "context_relevance": context_relevance_score * self.weight_context_relevance,
            "policy_conformance": policy_conformance_score * self.weight_policy_modulation,
            "historical_priority": historical_priority_score * self.weight_historical_priority,
        }
        
        total_weighted = sum(weighted_scores.values())
        
        # Apply uncertainty penalty (reduces priority for uncertain assessments)
        if uncertainty_score is not None:
            uncertainty_factor = 1.0 - (uncertainty_score * self.weight_uncertainty_penalty)
            total_weighted *= clamp(uncertainty_factor)
        
        # Create component records
        components = tuple(
            PriorityComponent(
                name=name,
                raw_value=base_score / weight if weight > 0 else 0.5,
                weight=weight,
                contribution=value,
                source="priority_aggregation",
                timestamp_utc=datetime.utcnow(),
            )
            for name, (base_score, weight, value) in [
                ("goal_relevance", (goal_relevance_score, self.weight_goal_relevance, weighted_scores["goal_relevance"])),
                ("context_relevance", (context_relevance_score, self.weight_context_relevance, weighted_scores["context_relevance"])),
                ("policy_conformance", (policy_conformance_score, self.weight_policy_modulation, weighted_scores["policy_conformance"])),
                ("historical_priority", (historical_priority_score, self.weight_historical_priority, weighted_scores["historical_priority"])),
            ]
        )
        
        if uncertainty_score is not None:
            components += (
                PriorityComponent(
                    name="uncertainty_penalty",
                    raw_value=1.0 - uncertainty_score,
                    weight=self.weight_uncertainty_penalty,
                    contribution=total_weighted * self.weight_uncertainty_penalty / max(self.weight_uncertainty_penalty, 0.001),
                    source="priority_aggregation",
                    timestamp_utc=datetime.utcnow(),
                ),
            )
        
        evidence = PriorityEvidence(
            goal_relevance_score=goal_relevance_score,
            context_relevance_score=context_relevance_score,
            policy_conformance_score=policy_conformance_score,
            historical_priority=historical_priority_score,
            expected_progress=None,
            resource_cost=None,
            uncertainty_score=uncertainty_score,
            components=components,
        )
        
        return clamp(total_weighted), evidence
    
    def aggregate_from_components(
        self,
        goal_relevance: PriorityComponent,
        context_relevance: PriorityComponent,
        policy_modulation: PriorityComponent,
        historical_priority: PriorityComponent,
        uncertainty_component: Optional[PriorityComponent] = None,
    ) -> Tuple[float, PriorityEvidence]:
        """
        Aggregate from pre-computed component records.
        
        This method accepts already-processed component evidence rather than
        raw scores, useful for replay or when components were computed separately.
        
        Args:
            goal_relevance: Goal relevance component
            context_relevance: Context relevance component
            policy_modulation: Policy modulation component
            historical_priority: Historical priority component
            uncertainty_component: Optional uncertainty penalty component
            
        Returns:
            Tuple of (priority, evidence)
        """
        # Extract raw values from components
        goal_score = goal_relevance.raw_value
        context_score = context_relevance.raw_value
        policy_score = policy_modulation.raw_value
        historical_score = historical_priority.raw_value
        
        # Aggregate
        priority, evidence = self.aggregate(
            goal_relevance_score=goal_score,
            context_relevance_score=context_score,
            policy_conformance_score=policy_score,
            historical_priority_score=historical_score,
        )
        
        return priority, evidence
    
    def get_weighted_breakdown(
        self,
        scores: Dict[str, float],
    ) -> PriorityBreakdown:
        """
        Get detailed breakdown of weighted aggregation.
        
        Args:
            scores: Dictionary mapping component names to raw scores
            
        Returns:
            PriorityBreakdown with all contribution details
        """
        # Compute weighted contributions
        contributions = []
        
        for name, score in scores.items():
            weight = getattr(self, f"weight_{name.replace('.', '_')}", 0.0)
            contribution = score * weight
            
            contributions.append(
                PriorityComponent(
                    name=name,
                    raw_value=score,
                    weight=weight,
                    contribution=contribution,
                    source="aggregation",
                    timestamp_utc=datetime.utcnow(),
                )
            )
        
        total_priority = sum(c.contribution for c in contributions)
        weighted_sum = total_priority
        weight_total = sum(c.weight for c in contributions)
        
        return PriorityBreakdown(
            total_priority=total_priority,
            weighted_sum=weighted_sum,
            weight_total=weight_total,
            component_contributions=tuple(contributions),
        )


# -----------------------------------------------------------------------------
# PRIORITY NORMALIZER
# -----------------------------------------------------------------------------


class PriorityNormalizer:
    """
    Normalize priority values to bounded, comparable range.
    
    Normalization ensures:
        • Values stay in [0.0, 1.0] range
        • Stable comparisons across assessments
        • Monotonic ordering preserved
        • Consistent scaling
    
    Normalization NEVER alters relative ordering unexpectedly.
    """
    
    def __init__(
        self,
        output_min: float = 0.0,
        output_max: float = 1.0,
        input_min: Optional[float] = None,
        input_max: Optional[float] = None,
    ):
        """
        Initialize the priority normalizer.
        
        Args:
            output_min: Minimum value of normalized range
            output_max: Maximum value of normalized range
            input_min: Expected minimum of input values (auto-detect if None)
            input_max: Expected maximum of input values (auto-detect if None)
        """
        self.output_min = output_min
        self.output_max = output_max
        self.input_min = input_min
        self.input_max = input_max
    
    def normalize(
        self,
        priority: float,
        reference_range: Optional[Tuple[float, float]] = None,
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Normalize a priority value to the output range.
        
        Args:
            priority: The priority value to normalize
            reference_range: Optional (min, max) for reference-based normalization
            
        Returns:
            Tuple of (normalized_value, metadata)
        """
        # Determine input range
        if reference_range is not None:
            input_min, input_max = reference_range
        elif self.input_min is not None and self.input_max is not None:
            input_min, input_max = self.input_min, self.input_max
        else:
            # Default range if no reference available
            input_min, input_max = 0.0, 1.0
        
        # Handle edge case: zero range
        if input_max == input_min:
            normalized = (self.output_min + self.output_max) / 2.0
            return normalized, {
                "method": "edge_case",
                "input_range": (input_min, input_max),
                "normalized_value": normalized,
                "reason": "Zero input range - returning midpoint",
            }
        
        # Normalize to [0, 1] first
        unit_normalized = (priority - input_min) / (input_max - input_min)
        
        # Scale to output range
        final_normalized = (
            self.output_min +
            unit_normalized * (self.output_max - self.output_min)
        )
        
        return clamp(final_normalized), {
            "method": "min_max",
            "original_value": priority,
            "input_range": (input_min, input_max),
            "output_range": (self.output_min, self.output_max),
            "unit_normalization": unit_normalized,
            "final_value": final_normalized,
        }
    
    def normalize_batch(
        self,
        priorities: Sequence[float],
        reference_range: Optional[Tuple[float, float]] = None,
    ) -> Tuple[List[float], Dict[str, Any]]:
        """
        Normalize multiple priority values.
        
        Args:
            priorities: List of priority values to normalize
            reference_range: Optional (min, max) for reference-based normalization
            
        Returns:
            Tuple of (normalized_list, metadata)
        """
        if not priorities:
            return [], {"method": "empty_batch", "count": 0}
        
        # Compute global range if not provided
        if reference_range is None:
            input_min = min(priorities)
            input_max = max(priorities)
            reference_range = (input_min, input_max)
        
        normalized = []
        for p in priorities:
            n, _ = self.normalize(p, reference_range)
            normalized.append(n)
        
        return normalized, {
            "method": "batch_min_max",
            "count": len(priorities),
            "global_input_range": reference_range,
            "output_range": (self.output_min, self.output_max),
        }
    
    def to_vector(
        self,
        priority: float,
        reference_range: Optional[Tuple[float, float]] = None,
    ) -> PriorityVector:
        """
        Convert a priority value to a normalized priority vector.
        
        The PriorityVector format is used for storage and comparison
        across assessment cycles.
        
        Args:
            priority: The priority value to convert
            reference_range: Optional (min, max) for normalization
            
        Returns:
            PriorityVector with normalized values and metadata
        """
        if reference_range is None:
            input_min = self.input_min if self.input_min is not None else 0.0
            input_max = self.input_max if self.input_max is not None else 1.0
        else:
            input_min, input_max = reference_range
        
        normalized_value, metadata = self.normalize(priority, reference_range)
        
        return PriorityVector(
            normalized_priority=normalized_value,
            goal_weighted_priority=normalized_value * 0.8,  # Placeholder
            context_weighted_priority=normalized_value * 0.9,  # Placeholder
            historical_weighted_priority=normalized_value * 0.7,  # Placeholder
            min_input_priority=input_min,
            max_input_priority=input_max,
            normalization_method="min_max",
        )


# -----------------------------------------------------------------------------
# PRIORITY CONFIDENCE ESTIMATOR
# -----------------------------------------------------------------------------


class PriorityConfidenceEstimator:
    """
    Estimate confidence in priority assessments.
    
    Confidence measures the reliability of computed priorities:
        • Input completeness: Were all relevant factors available?
        • Context quality: How clear was the situational context?
        • Historical consistency: Do results match historical patterns?
        • Computation stability: Is the algorithm behaving predictably?
    
    Confidence is SEPARATE from priority - a high-priority item
    can have low confidence (insufficient data).
    """
    
    def __init__(
        self,
        weight_input_completeness: float = 0.3,
        weight_context_quality: float = 0.25,
        weight_historical_consistency: float = 0.25,
        weight_computation_stability: float = 0.2,
    ):
        """
        Initialize the confidence estimator.
        
        Args:
            weight_input_completeness: Weight for input availability
            weight_context_quality: Weight for context clarity
            weight_historical_consistency: Weight for pattern match
            weight_computation_stability: Weight for algorithm stability
        """
        self.weight_input_completeness = weight_input_completeness
        self.weight_context_quality = weight_context_quality
        self.weight_historical_consistency = weight_historical_consistency
        self.weight_computation_stability = weight_computation_stability
        
        # Validate weights sum to 1.0
        total_weight = (
            weight_input_completeness +
            weight_context_quality +
            weight_historical_consistency +
            weight_computation_stability
        )
        
        if abs(total_weight - 1.0) > 0.01:
            self.weight_input_completeness /= total_weight
            self.weight_context_quality /= total_weight
            self.weight_historical_consistency /= total_weight
            self.weight_computation_stability /= total_weight
    
    def estimate(
        self,
        input_data: Mapping[str, Any],
        context_projection: Mapping[str, Any],
        historical_priorities: Optional[Sequence[float]] = None,
    ) -> PriorityConfidence:
        """
        Estimate confidence in a priority assessment.
        
        Args:
            input_data: Available input data for the assessment
            context_projection: Context projection used in estimation
            historical_priorities: Historical priority values (for consistency check)
            
        Returns:
            PriorityConfidence with score and breakdown
        """
        # Compute individual confidence factors
        
        # 1. Input completeness
        input_completeness = self._estimate_input_completeness(input_data)
        
        # 2. Context quality
        context_quality = self._estimate_context_quality(context_projection)
        
        # 3. Historical consistency (if history available)
        if historical_priorities:
            historical_consistency = self._estimate_historical_consistency(
                historical_priorities,
                input_data.get("computed_priority", 0.5),
            )
        else:
            historical_consistency = 0.5  # No history = neutral
        
        # 4. Computation stability
        computation_stability = self._estimate_computation_stability(input_data)
        
        # Weighted combination
        confidence_score = (
            input_completeness * self.weight_input_completeness +
            context_quality * self.weight_context_quality +
            historical_consistency * self.weight_historical_consistency +
            computation_stability * self.weight_computation_stability
        )
        
        # Identify factors and uncertainty sources
        confidence_factors = []
        uncertainty_sources = []
        
        if input_completeness < 0.7:
            uncertainty_sources.append("incomplete_inputs")
        else:
            confidence_factors.append("complete_inputs")
        
        if context_quality < 0.7:
            uncertainty_sources.append("unclear_context")
        else:
            confidence_factors.append("clear_context")
        
        if historical_consistency < 0.7:
            uncertainty_sources.append("historical_inconsistency")
        else:
            confidence_factors.append("historical_consistency")
        
        if computation_stability < 0.8:
            uncertainty_sources.append("computation_instability")
        else:
            confidence_factors.append("stable_computation")
        
        return PriorityConfidence(
            score=clamp(confidence_score),
            input_completeness_score=input_completeness,
            context_quality_score=context_quality,
            historical_consistency_score=historical_consistency,
            computation_stability_score=computation_stability,
            confidence_factors=tuple(confidence_factors),
            uncertainty_sources=tuple(uncertainty_sources),
        )
    
    def _estimate_input_completeness(
        self,
        input_data: Mapping[str, Any],
    ) -> float:
        """Estimate completeness of input data."""
        # Required inputs for priority estimation
        required_fields = [
            "goal_relevance",
            "context_relevance",
            "policy_conformance",
            "historical_priority",
        ]
        
        present_fields = sum(
            1 for field in required_fields
            if field in input_data and input_data[field] is not None
        )
        
        return present_fields / len(required_fields) if required_fields else 0.5
    
    def _estimate_context_quality(
        self,
        context: Mapping[str, Any],
    ) -> float:
        """Estimate quality of contextual information."""
        # Check for key contextual signals
        context_signals = [
            "active_objectives",
            "current_task",
            "recent_memories",
            "environmental_state",
        ]
        
        present_signals = sum(
            1 for signal in context_signals
            if signal in context and context[signal]
        )
        
        # Bonus for well-structured context
        bonus = 0.0
        if isinstance(context, dict) and len(context) > 5:
            bonus = 0.1
        
        return clamp((present_signals / len(context_signals)) + bonus)
    
    def _estimate_historical_consistency(
        self,
        historical_priorities: Sequence[float],
        current_priority: float,
    ) -> float:
        """Estimate how consistent current priority is with history."""
        if not historical_priorities:
            return 0.5
        
        # Compute statistics
        avg = sum(historical_priorities) / len(historical_priorities)
        variance = sum((h - avg) ** 2 for h in historical_priorities) / len(historical_priorities)
        
        # How far is current from average (normalized by variance)
        if variance > 0:
            deviation = abs(current_priority - avg) / math.sqrt(variance)
        else:
            deviation = 0.0
        
        # Convert to consistency score (lower deviation = higher consistency)
        consistency = 1.0 / (1.0 + deviation)
        
        return clamp(consistency)
    
    def _estimate_computation_stability(
        self,
        input_data: Mapping[str, Any],
    ) -> float:
        """Estimate stability of computation algorithm."""
        # Check for signs of instability
        instability_factors = 0
        
        # Check for NaN/inf values
        for value in input_data.values():
            if isinstance(value, (int, float)):
                if math.isnan(value) or math.isinf(value):
                    instability_factors += 1
        
        # Check for extreme values that might indicate computation issues
        for value in input_data.values():
            if isinstance(value, (int, float)) and (value < 0.0 or value > 1.0):
                if not (0.0 <= value <= 1.05):  # Small tolerance
                    instability_factors += 0.5
        
        # Base stability score
        base_stability = 1.0 - (instability_factors * 0.2)
        
        return clamp(base_stability)


# -----------------------------------------------------------------------------
# FULL ESTIMATION PIPELINE
# -----------------------------------------------------------------------------


class PriorityEstimationPipeline:
    """
    Complete priority estimation pipeline.
    
    This class orchestrates all the computational steps from input
    to final assessment with explanations.
    """
    
    def __init__(
        self,
        goal_relevance_estimator: Optional[GoalRelevanceEstimator] = None,
        context_relevance_estimator: Optional[ContextRelevanceEstimator] = None,
        policy_modulator: Optional[PolicyModulator] = None,
        historical_priority_model: Optional[HistoricalPriorityModel] = None,
        priority_aggregator: Optional[PriorityAggregator] = None,
        priority_normalizer: Optional[PriorityNormalizer] = None,
        confidence_estimator: Optional[PriorityConfidenceEstimator] = None,
    ):
        """
        Initialize the priority estimation pipeline.
        
        Args:
            goal_relevance_estimator: Estimator for goal alignment
            context_relevance_estimator: Estimator for situational fit
            policy_modulator: Policy constraint modulator
            historical_priority_model: Historical pattern analyzer
            priority_aggregator: Component aggregator
            priority_normalizer: Output normalizer
            confidence_estimator: Confidence assessor
        """
        self.goal_relevance_estimator = goal_relevance_estimator or GoalRelevanceEstimator()
        self.context_relevance_estimator = context_relevance_estimator or ContextRelevanceEstimator()
        self.policy_modulator = policy_modulator or PolicyModulator()
        self.historical_priority_model = historical_priority_model or HistoricalPriorityModel()
        
        # Initialize aggregator with weights that sum to 1.0
        self.priority_aggregator = priority_aggregator or PriorityAggregator(
            weight_goal_relevance=0.35,
            weight_context_relevance=0.25,
            weight_policy_modulation=0.15,
            weight_historical_priority=0.15,
            weight_uncertainty_penalty=0.10,
        )
        
        self.priority_normalizer = priority_normalizer or PriorityNormalizer()
        self.confidence_estimator = confidence_estimator or PriorityConfidenceEstimator()
    
    def estimate(
        self,
        candidate_target_id: str,
        active_objectives: Sequence[str],
        context_projection: Mapping[str, Any],
        historical_priorities: Optional[Sequence[float]] = None,
        policy_constraints: Optional[Sequence[str]] = None,
        user_preferences: Optional[Mapping[str, Any]] = None,
    ) -> PriorityAssessment:
        """
        Run the full priority estimation pipeline.
        
        This implements the canonical pipeline described in Phase 4.2.3:
            FocusCandidate
                ↓
            Goal Relevance Estimation
                ↓
            Context Evaluation
                ↓
            Policy Evaluation
                ↓
            Historical Influence
                ↓
            Priority Aggregation
                ↓
            Priority Normalization
                ↓
            Confidence Estimation
                ↓
            Priority Assessment
        
        Args:
            candidate_target_id: ID of the candidate to assess
            active_objectives: List of active objective strings
            context_projection: Current execution context
            historical_priorities: Historical priority values (newest first)
            policy_constraints: Active policy constraint strings
            user_preferences: Optional user preference mapping
            
        Returns:
            PriorityAssessment with complete evaluation and explanation
        """
        timestamp = datetime.utcnow()
        
        # Step 1: Goal Relevance Estimation
        goal_relevance_score, goal_component = self.goal_relevance_estimator.estimate_full(
            candidate_target_id,
            active_objectives,
            context_projection,
        )
        
        # Step 2: Context Relevance Estimation
        context_relevance_score, context_component = self.context_relevance_estimator.estimate_full(
            candidate_target_id,
            context_projection,
        )
        
        # Step 3 & 4: Policy and Historical (run in parallel conceptually)
        policy_conformance_score, policy_component = self.policy_modulator.modulate(
            base_priority=0.5,  # Base for policy component
            policy_constraints=policy_constraints or [],
            user_preferences=user_preferences,
        )
        
        historical_priority_score, historical_component = self.historical_priority_model.estimate(
            candidate_target_id,
            historical_priorities or [],
        )
        
        # Step 5: Aggregate
        aggregated_priority, evidence = self.priority_aggregator.aggregate(
            goal_relevance_score=goal_relevance_score,
            context_relevance_score=context_relevance_score,
            policy_conformance_score=policy_conformance_score,
            historical_priority_score=historical_priority_score,
        )
        
        # Add components to evidence
        all_components = (
            (goal_component, context_component, policy_component, historical_component)
        )
        evidence = dataclass_replace(evidence, components=all_components)
        
        # Step 6: Normalize
        normalized_priority, normalization_metadata = self.priority_normalizer.normalize(
            aggregated_priority,
        )
        
        priority_vector = self.priority_normalizer.to_vector(normalized_priority)
        
        # Step 7: Compute confidence
        confidence = self.confidence_estimator.estimate(
            input_data={
                "goal_relevance": goal_relevance_score,
                "context_relevance": context_relevance_score,
                "policy_conformance": policy_conformance_score,
                "historical_priority": historical_priority_score,
                "computed_priority": normalized_priority,
            },
            context_projection=context_projection,
            historical_priorities=historical_priorities or [],
        )
        
        # Step 8: Generate explanation
        breakdown = self.priority_aggregator.get_weighted_breakdown({
            "goal_relevance": goal_relevance_score,
            "context_relevance": context_relevance_score,
            "policy_conformance": policy_conformance_score,
            "historical_priority": historical_priority_score,
        })
        
        # Generate rationale strings
        goal_rationale = self._generate_goal_alignment_rationale(
            candidate_target_id,
            active_objectives,
            goal_relevance_score,
        )
        
        context_rationale = self._generate_context_fit_rationale(
            candidate_target_id,
            context_projection,
            context_relevance_score,
        )
        
        policy_rationale = self._generate_policy_compliance_rationale(
            policy_constraints or [],
            policy_conformance_score,
        )
        
        historical_rationale = self._generate_historical_continuity_rationale(
            candidate_target_id,
            historical_priorities or [],
            historical_priority_score,
        )
        
        explanation = PriorityExplanation(
            target_id=candidate_target_id,
            final_priority=normalized_priority,
            goal_alignment_rationale=goal_rationale,
            context_fit_rationale=context_rationale,
            policy_compliance_rationale=policy_rationale,
            historical_continuity_rationale=historical_rationale,
            contribution_summary=breakdown.contribution_percentages(),
            dominant_factors=breakdown.dominant_components(threshold=5.0),
            confidence_assessment=confidence,
        )
        
        # Step 9: Create relevance assessment
        relevance = RelevanceAssessment(
            goal_relevance=goal_relevance_score,
            task_relevance=context_relevance_score,  # Use context as task proxy
            context_relevance=context_relevance_score,
            recency_score=0.7,  # Placeholder for recency
        )
        
        # Step 10: Build final assessment
        assessment = PriorityAssessment(
            target_id=candidate_target_id,
            candidate_id=f"assessment_{timestamp.timestamp():.0f}",
            timestamp_utc=timestamp,
            priority=normalized_priority,
            relevance_assessment=relevance,
            priority_evidence=evidence,
            priority_vector=priority_vector,
            priority_breakdown=breakdown,
            confidence=confidence,
            explanation=explanation,
            is_finite=True,
            is_normalized=(0.0 <= normalized_priority <= 1.0),
        )
        
        return assessment
    
    def _generate_goal_alignment_rationale(
        self,
        candidate_id: str,
        active_objectives: Sequence[str],
        score: float,
    ) -> str:
        """Generate goal alignment explanation."""
        if not active_objectives:
            return "No active objectives defined; relevance computed from available signals."
        
        objective_str = ", ".join(active_objectives[:3])
        
        if score >= 0.7:
            return (
                f"Strong alignment with active objectives [{objective_str}]. "
                f"Expected to contribute meaningfully to goal completion."
            )
        elif score >= 0.4:
            return (
                f"Moderate alignment with active objectives [{objective_str}]. "
                f"Some contribution expected but secondary to other priorities."
            )
        else:
            return (
                f"Weak alignment with active objectives [{objective_str}]. "
                f"May not significantly advance current goals."
            )
    
    def _generate_context_fit_rationale(
        self,
        candidate_id: str,
        context: Mapping[str, Any],
        score: float,
    ) -> str:
        """Generate context fit explanation."""
        if score >= 0.7:
            return (
                f"Good fit to current situational context. "
                f"Resources and conditions appear favorable for this focus."
            )
        elif score >= 0.4:
            return (
                f"Moderate fit to current situational context. "
                f"Some contextual alignment present but not optimal."
            )
        else:
            return (
                f"Poor fit to current situational context. "
                f"Contextual conditions may not support sustained focus."
            )
    
    def _generate_policy_compliance_rationale(
        self,
        constraints: Sequence[str],
        score: float,
    ) -> str:
        """Generate policy compliance explanation."""
        if not constraints:
            return "No active policy constraints to evaluate."
        
        constraint_str = ", ".join(constraints[:3])
        
        if score >= 0.8:
            return (
                f"Good compliance with active constraints [{constraint_str}]. "
                f"No significant policy conflicts detected."
            )
        elif score >= 0.5:
            return (
                f"Moderate compliance with active constraints [{constraint_str}]. "
                f"Some constraint alignment present but may require attention."
            )
        else:
            return (
                f"Potential policy constraint violations detected [{constraint_str}]. "
                f"Review required before sustained focus allocation."
            )
    
    def _generate_historical_continuity_rationale(
        self,
        candidate_id: str,
        historical_priorities: Sequence[float],
        score: float,
    ) -> str:
        """Generate historical continuity explanation."""
        if not historical_priorities:
            return "No historical priority data available for continuity assessment."
        
        avg = sum(historical_priorities) / len(historical_priorities)
        variance = sum((h - avg) ** 2 for h in historical_priorities) / len(historical_priorities)
        
        continuity = 1.0 / (1.0 + variance)
        
        if continuity >= 0.7:
            return (
                f"Strong focus continuity maintained. "
                f"Historical pattern shows stable priority ({avg:.2f} avg, {continuity:.2f} continuous)."
            )
        elif continuity >= 0.4:
            return (
                f"Moderate focus continuity. "
                f"Some historical priority variation detected ({avg:.2f} avg)."
            )
        else:
            return (
                f"Unstable historical pattern detected. "
                f"Historical priority varies significantly from current estimate."
            )


# =============================================================================
# END OF PHASE 4.2.3 IMPLEMENTATION
# =============================================================================