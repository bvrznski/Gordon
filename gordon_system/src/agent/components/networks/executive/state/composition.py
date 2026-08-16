# Executive State Composition Types
# ==================================

"""
Composition types for executive state evaluation.

These provide bounded classifications for confidence, completeness,
consistency, and coherence assessments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# STATE CONFIDENCE CLASSIFICATION
# =============================================================================


@dataclass(frozen=True)
class ExecutiveStateConfidence:
    """
    Classification of executive state confidence.
    
    Confidence reflects how well the state represents reality based on
    available evidence and authority decisions.
    """
    
    overall_confidence: float = 0.5
    """Overall confidence score (0.0 to 1.0)."""
    
    class Classification:
        UNKNOWN = "unknown"
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        VERY_HIGH = "very_high"
    
    classification: str = Classification.UNKNOWN
    """Human-readable confidence class."""
    
    context_confidence: float = 0.5
    """Confidence derived from the context assessment."""
    
    active_task_set_confidence: float = 1.0
    """Confidence in the active task set definition."""
    
    goal_state_confidence: float = 1.0
    """Confidence in the current goal state."""
    
    strategy_confidence: float = 1.0
    """Confidence in the current strategy."""
    
    authority_decisions_valid: bool = True
    """Whether accepted authority decisions appear valid."""
    
    stale_context: bool = False
    """Whether context may be stale."""
    
    provenance_quality: str = "unknown"
    """Quality of the evidence trail."""
    
    @classmethod
    def from_scores(cls, base_confidence: float) -> ExecutiveStateConfidence:
        """Create confidence classification from a numeric score."""
        if base_confidence >= 0.8:
            return cls(overall_confidence=base_confidence, classification=cls.Classification.HIGH)
        elif base_confidence >= 0.5:
            return cls(overall_confidence=base_confidence, classification=cls.Classification.MEDIUM)
        elif base_confidence > 0.2:
            return cls(overall_confidence=base_confidence, classification=cls.Classification.LOW)
        else:
            return cls(overall_confidence=base_confidence, classification=cls.Classification.UNKNOWN)


# =============================================================================
# STATE COMPLETENESS CLASSIFICATION
# =============================================================================


@dataclass(frozen=True)
class ExecutiveStateCompleteness:
    """
    Classification of executive state completeness.
    
    Completeness reflects whether the state contains sufficient information
    for its current purpose and mode.
    """
    
    class Status:
        COMPLETE = "complete"
        """All required information is present."""
        
        SUFFICIENT = "sufficient"
        """Sufficient information for the current mode."""
        
        PARTIAL = "partial"
        """Some information missing but workable."""
        
        WAITING = "waiting"
        """Waiting for external results before completion."""
        
        INSUFFICIENT = "insufficient"
        """Missing critical information."""
        
        INVALID = "invalid"
        """State is invalid or corrupted."""
    
    status: str = Status.WAITING
    """Completeness classification."""
    
    missing_required_items: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of required items that are missing."""
    
    optional_items_missing: int = 0
    """Count of optional items that could be added."""
    
    completeness_score: float = 0.5
    """Numeric completeness score (0.0 to 1.0)."""
    
    mode_appropriate: bool = True
    """Whether the incompleteness is acceptable for current mode."""
    
    @classmethod
    def complete(cls) -> ExecutiveStateCompleteness:
        """Create a complete status."""
        return cls(status=cls.Status.COMPLETE, completeness_score=1.0)
    
    @classmethod
    def sufficient(cls) -> ExecutiveStateCompleteness:
        """Create a sufficient status."""
        return cls(status=cls.Status.SUFFICIENT, completeness_score=0.8)


# =============================================================================
# STATE CONSISTENCY CLASSIFICATION
# =============================================================================


@dataclass(frozen=True)
class ExecutiveStateConsistency:
    """
    Classification of executive state consistency.
    
    Consistency checks for logical contradictions within the state itself.
    """
    
    class Status:
        CONSISTENT = "consistent"
        """No inconsistencies detected."""
        
        INCONSISTENT = "inconsistent"
        """Inconsistencies were detected."""
        
        UNKNOWN = "unknown"
        """Consistency could not be determined."""
    
    status: str = Status.CONSISTENT
    """Consistency classification."""
    
    detected_inconsistencies: Tuple[str, ...] = field(default_factory=tuple)
    """IDs or descriptions of detected inconsistencies."""
    
    consistency_score: float = 1.0
    """Numeric consistency score (0.0 to 1.0)."""
    
    @classmethod
    def consistent(cls) -> ExecutiveStateConsistency:
        """Create a consistent status."""
        return cls(status=cls.Status.CONSISTENT, consistency_score=1.0)
    
    @classmethod
    def inconsistent(cls, inconsistencies: Tuple[str, ...] = ()) -> ExecutiveStateConsistency:
        """Create an inconsistent status."""
        return cls(status=cls.Status.INCONSISTENT, detected_inconsistencies=inconsistencies, consistency_score=0.0)


# =============================================================================
# STATE COHERENCE CLASSIFICATION
# =============================================================================


@dataclass(frozen=True)
class ExecutiveStateCoherence:
    """
    Classification of executive state coherence.
    
    Coherence assesses whether the state forms a meaningful organization,
    beyond just logical consistency.
    """
    
    class Status:
        COHERENT = "coherent"
        """State forms a coherent whole."""
        
        WEAKLY_COHERENT = "weakly_coherent"
        """State is consistent but fragmented."""
        
        INCOHERENT = "incoherent"
        """State lacks meaningful organization."""
        
        UNKNOWN = "unknown"
        """Coherence could not be determined."""
    
    status: str = Status.COHERENT
    """Coherence classification."""
    
    goal_alignment: float = 1.0
    """How well goals align with each other."""
    
    task_set_alignment: float = 1.0
    """How well tasks align with goals."""
    
    strategy_alignment: float = 1.0
    """How well strategy supports goals and tasks."""
    
    control_alignment: float = 1.0
    """How well control allocation matches demand."""
    
    temporal_continuity: bool = True
    """Whether state shows temporal continuity."""
    
    @classmethod
    def coherent(cls) -> ExecutiveStateCoherence:
        """Create a coherent status."""
        return cls(status=cls.Status.COHERENT)
    
    @classmethod
    def weakly_coherent(cls) -> ExecutiveStateCoherence:
        """Create a weakly coherent status."""
        return cls(status=cls.Status.WEAKLY_COHERENT)


# =============================================================================
# CONTEXT CONFIDENCE CLASSIFICATION
# =============================================================================


@dataclass(frozen=True)
class ExecutiveContextConfidence:
    """
    Classification of executive context confidence.
    
    Context confidence assesses how well the context represents the external
    world for the current assessment purpose.
    """
    
    overall_confidence: float = 0.5
    """Overall confidence score (0.0 to 1.0)."""
    
    class Classification:
        UNKNOWN = "unknown"
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        VERY_HIGH = "very_high"
    
    classification: str = Classification.UNKNOWN
    """Human-readable confidence class."""
    
    source_confidence_avg: float = 0.5
    """Average confidence from source projections."""
    
    source_authority_score: float = 1.0
    """Authority score of sources."""
    
    projection_completeness: float = 1.0
    """Completeness of projections."""
    
    revision_consistency: bool = True
    """Whether revisions are consistent."""
    
    temporal_validity: bool = True
    """Whether context is temporally valid."""
    
    source_agreement: float = 1.0
    """Degree of agreement between sources."""
    
    @classmethod
    def from_score(cls, score: float) -> ExecutiveContextConfidence:
        """Create confidence classification from a numeric score."""
        if score >= 0.8:
            return cls(overall_confidence=score, classification=cls.Classification.HIGH)
        elif score >= 0.5:
            return cls(overall_confidence=score, classification=cls.Classification.MEDIUM)
        else:
            return cls(overall_confidence=score, classification=cls.Classification.LOW)


# =============================================================================
# CONTEXT COMPLETENESS CLASSIFICATION
# =============================================================================


@dataclass(frozen=True)
class ExecutiveContextCompleteness:
    """
    Classification of executive context completeness.
    
    Context completeness is purpose-relative - what's complete for one
    assessment may be insufficient for another.
    """
    
    class Status:
        COMPLETE = "complete"
        """All required projections for this purpose are present."""
        
        SUFFICIENT = "sufficient"
        """Sufficient for current purposes despite some gaps."""
        
        PARTIAL = "partial"
        """Some required projections missing but workable."""
        
        INSUFFICIENT = "insufficient"
        """Missing critical required projections."""
    
    status: str = Status.PARTIAL
    """Completeness classification."""
    
    purpose_relative: bool = True
    """Whether completeness is evaluated relative to purpose."""
    
    required_missing_count: int = 0
    """Number of required projections that are missing."""
    
    optional_missing_count: int = 0
    """Number of optional projections that could be added."""
    
    completeness_score: float = 0.5
    """Numeric completeness score (0.0 to 1.0)."""
    
    @classmethod
    def complete(cls) -> ExecutiveContextCompleteness:
        """Create a complete status."""
        return cls(status=cls.Status.COMPLETE, completeness_score=1.0)
    
    @classmethod
    def sufficient(cls) -> ExecutiveContextCompleteness:
        """Create a sufficient status."""
        return cls(status=cls.Status.SUFFICIENT, completeness_score=0.8)


# =============================================================================
# CONTEXT FRESHNESS CLASSIFICATION
# =============================================================================


@dataclass(frozen=True)
class ExecutiveContextFreshness:
    """
    Classification of executive context freshness.
    
    Freshness considers both age and whether the information is up-to-date
    for its purpose.
    """
    
    class Status:
        FRESH = "fresh"
        """Recent and likely still valid."""
        
        STALE = "stale"
        """Age may affect validity."""
        
        EXPIRED = "expired"
        """Definitely no longer valid."""
    
    status: str = Status.FRESH
    """Freshness classification."""
    
    average_age_seconds: float = 0.0
    """Average age of projections in seconds."""
    
    max_validity_seconds: float = 60.0
    """Maximum validity period for this context (seconds)."""
    
    stale_projection_count: int = 0
    """Number of projections that may be stale."""
    
    expired_projection_count: int = 0
    """Number of projections that are definitely expired."""
    
    revision_lag: int = 0
    """How many revisions behind the latest sources are."""
    
    freshness_score: float = 1.0
    """Numeric freshness score (0.0 to 1.0)."""
    
    @classmethod
    def fresh(cls) -> ExecutiveContextFreshness:
        """Create a fresh status."""
        return cls(status=cls.Status.FRESH, freshness_score=1.0)
    
    @classmethod
    def stale(cls) -> ExecutiveContextFreshness:
        """Create a stale status."""
        return cls(status=cls.Status.STALE, freshness_score=0.5)


# =============================================================================
# CONTEXT CONSISTENCY CLASSIFICATION
# =============================================================================


@dataclass(frozen=True)
class ExecutiveContextConsistency:
    """
    Classification of executive context consistency.
    
    Checks for contradictions between different projections in the context.
    """
    
    class Status:
        CONSISTENT = "consistent"
        """No inconsistencies detected."""
        
        CONFLICTED = "conflicted"
        """Conflicts were detected."""
    
    status: str = Status.CONSISTENT
    """Consistency classification."""
    
    detected_conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """IDs or descriptions of detected conflicts."""
    
    conflict_resolution_needed: bool = False
    """Whether explicit resolution is required."""
    
    @classmethod
    def consistent(cls) -> ExecutiveContextConsistency:
        """Create a consistent status."""
        return cls(status=cls.Status.CONSISTENT)
    
    @classmethod
    def conflicted(cls, conflicts: Tuple[str, ...] = ()) -> ExecutiveContextConsistency:
        """Create a conflicted status."""
        return cls(status=cls.Status.CONFLICTED, detected_conflicts=conflicts)


# =============================================================================
# CONTEXT VALIDITY CLASSIFICATION
# =============================================================================


@dataclass(frozen=True)
class ExecutiveContextValidity:
    """
    Classification of executive context validity.
    
    Validity assesses whether the context can be used for its intended purpose.
    """
    
    class Status:
        VALID = "valid"
        """Valid for current purposes."""
        
        VALID_WITH_LIMITATIONS = "valid_with_limitations"
        """Valid but with known limitations."""
        
        STALE = "stale"
        """May no longer be valid."""
        
        INCOMPLETE = "incomplete"
        """Missing required elements."""
        
        CONFLICTED = "conflicted"
        """Contains conflicting information."""
        
        EXPIRED = "expired"
        """Definitely no longer valid."""
        
        INVALID = "invalid"
        """Cannot be used for any purpose."""
    
    status: str = Status.VALID
    """Validity classification."""
    
    validity_reasons: Tuple[str, ...] = field(default_factory=tuple)
    """Reasoning behind the validity classification."""
    
    required_projections_missing: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of missing required projections."""
    
    confidence_score: float = 1.0
    """Numeric validity score (0.0 to 1.0)."""
    
    @classmethod
    def valid(cls) -> ExecutiveContextValidity:
        """Create a valid status."""
        return cls(status=cls.Status.VALID, confidence_score=1.0)
    
    @classmethod
    def invalid(cls, reasons: Tuple[str, ...] = ()) -> ExecutiveContextValidity:
        """Create an invalid status."""
        return cls(status=cls.Status.INVALID, validity_reasons=reasons, confidence_score=0.0)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveStateConfidence",
    "ExecutiveStateCompleteness",
    "ExecutiveStateConsistency",
    "ExecutiveStateCoherence",
    "ExecutiveContextConfidence",
    "ExecutiveContextCompleteness",
    "ExecutiveContextFreshness",
    "ExecutiveContextConsistency",
    "ExecutiveContextValidity",
)