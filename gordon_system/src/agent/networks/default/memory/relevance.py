# Memory Relevance Models
# ========================

"""
Immutable relevance models for memory records.

ARCHITECTURAL PRINCIPLES:
    - Frozen dataclasses (deeply immutable)
    - Semantic only, no implementation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# MEMORY RELEVANCE ASSESSMENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryRelevanceAssessment:
    """
    Immutable relevance assessment for a memory record or integration episode.
    
    Relevance determines how well memory content relates to current needs.
    
    PROPERTIES:
        • purpose_relevance: How relevant is this to the memory integration purpose?
        • subject_overlap: Does this share subjects with the current context?
        • objective_relevance: Supports or contradicts current objectives?
        • episode_relevance: Related to the current InternalEpisode?
        • thought_relevance: Related to the current thoughts?
        • temporal_relevance: Temporal proximity to current time?
        • causal_relevance: Causally related to current situation?
        • narrative_relevance: Fits into narrative coherence?
        • identity_relevance: Relevant to identity representation?
        • predictive_relevance: Useful for predictions?
        • source_confidence: Confidence in the relevance assessment itself
        • overall_score: Combined relevance score (0.0 to 1.0)
        
    IS NOT:
        - Importance (relevance ≠ importance)
        - Truth (relevant memories can be false)
        - Retrieval rank (though related)
    """
    
    # Contribution factors
    purpose_relevance: float = 0.5
    """How relevant is this to the memory integration purpose?"""
    
    subject_overlap: float = 0.5
    """Does this share subjects with the current context?"""
    
    objective_relevance: float = 0.5
    """Supports or contradicts current objectives?"""
    
    episode_relevance: float = 0.5
    """Related to the current InternalEpisode?"""
    
    thought_relevance: float = 0.5
    """Related to the current thoughts?"""
    
    temporal_relevance: float = 0.5
    """Temporal proximity to current time?"""
    
    causal_relevance: float = 0.5
    """Causally related to current situation?"""
    
    narrative_relevance: float = 0.5
    """Fits into narrative coherence?"""
    
    identity_relevance: float = 0.5
    """Relevant to identity representation?"""
    
    predictive_relevance: float = 0.5
    """Useful for predictions?"""
    
    # Quality assessment
    source_confidence: float = 0.5
    """Confidence in the relevance assessment itself."""
    
    # Overall score (derived)
    overall_score: float = 0.5
    """Combined relevance score (0.0 to 1.0)."""
    
    @classmethod
    def new(
        cls,
        purpose_relevance: float = 0.5,
        subject_overlap: float = 0.5,
        objective_relevance: float = 0.5,
        episode_relevance: float = 0.5,
        thought_relevance: float = 0.5,
        temporal_relevance: float = 0.5,
        causal_relevance: float = 0.5,
        narrative_relevance: float = 0.5,
        identity_relevance: float = 0.5,
        predictive_relevance: float = 0.5,
    ) -> MemoryRelevanceAssessment:
        """Create a new relevance assessment."""
        # Calculate overall score as weighted average
        overall = (
            purpose_relevance * 0.2 +
            subject_overlap * 0.15 +
            objective_relevance * 0.15 +
            episode_relevance * 0.1 +
            thought_relevance * 0.1 +
            temporal_relevance * 0.1 +
            causal_relevance * 0.05 +
            narrative_relevance * 0.05 +
            identity_relevance * 0.05 +
            predictive_relevance * 0.05
        )
        
        return cls(
            purpose_relevance=purpose_relevance,
            subject_overlap=subject_overlap,
            objective_relevance=objective_relevance,
            episode_relevance=episode_relevance,
            thought_relevance=thought_relevance,
            temporal_relevance=temporal_relevance,
            causal_relevance=causal_relevance,
            narrative_relevance=narrative_relevance,
            identity_relevance=identity_relevance,
            predictive_relevance=predictive_relevance,
            overall_score=min(1.0, max(0.0, overall)),
        )
    
    def is_highly_relevant(self) -> bool:
        """Check if this memory is highly relevant."""
        return self.overall_score >= 0.7
    
    def is_low_relevance(self) -> bool:
        """Check if this memory has low relevance."""
        return self.overall_score <= 0.2


# =============================================================================
# MEMORY FRESHNESS ASSESSMENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryFreshnessAssessment:
    """
    Immutable freshness assessment for a memory record.
    
    Freshness is purpose-relative - old memory may remain valid.
    
    PROPERTIES:
        • record_age_seconds: How old is the record?
        • source_update_age_seconds: When was the source last updated?
        • revision_lag_seconds: Time since last revision?
        • supersession_status: Has this been superseded?
        • context_applicability: Still applicable to current context?
        • freshness_classification: Classification of freshness
        • confidence: Confidence in freshness assessment
        • provenance: Provenance reference
        
    IS NOT:
        - Staleness indicator (old ≠ stale)
        - Independent of content validity
    """
    
    # Age metrics
    record_age_seconds: float = 0.0
    """How old is the record?"""
    
    source_update_age_seconds: float = 0.0
    """When was the source last updated?"""
    
    revision_lag_seconds: float = 0.0
    """Time since last revision?"""
    
    # Status
    supersession_status: str = "not_superseded"
    """Has this been superseded?"""
    
    context_applicability: str = "unknown"
    """Still applicable to current context?"""
    
    # Assessment
    freshness_classification: str = "unknown"
    """Classification of freshness."""
    
    confidence: float = 0.5
    """Confidence in freshness assessment (0.0 to 1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def from_record_age(
        cls,
        record_age_seconds: float,
        context_applicability: str = "unknown",
    ) -> MemoryFreshnessAssessment:
        """Create a freshness assessment based on record age."""
        # Determine classification based on age
        if record_age_seconds < 3600:  # 1 hour
            classification = "very_fresh"
        elif record_age_seconds < 86400:  # 1 day
            classification = "fresh"
        elif record_age_seconds < 604800:  # 1 week
            classification = "moderate"
        else:
            classification = "old"
        
        return cls(
            record_age_seconds=record_age_seconds,
            context_applicability=context_applicability,
            freshness_classification=classification,
            confidence=0.7 if context_applicability == "applicable" else 0.5,
        )
    
    def is_fresh(self) -> bool:
        """Check if this memory is fresh."""
        return self.freshness_classification in {"very_fresh", "fresh"}
    
    def is_stale(self) -> bool:
        """Check if this memory may be stale (old and not applicable)."""
        return (
            self.freshness_classification == "old"
            and self.context_applicability == "not_applicable"
        )