# Gordon Cognitive Architecture - Phase 4.5.5
# Action Evaluation Confidence and Uncertainty
# ============================================

"""
Confidence and Uncertainty assessment types for Action Evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple


# =============================================================================
# CONFIDENCE LEVEL ENUMERATION
# =============================================================================

class ConfidenceLevel(Enum):
    """
    Levels of confidence in an evaluation assessment.
    
    PROPERTIES:
        • HIGH: Assessment is reliable, evidence is strong
        • MEDIUM: Assessment has reasonable support
        • LOW: Assessment lacks sufficient evidence
        • UNKNOWN: Insufficient information to assess confidence
    """
    
    HIGH = "high"
    """Assessment is reliable, evidence is strong."""
    
    MEDIUM = "medium"
    """Assessment has reasonable support."""
    
    LOW = "low"
    """Assessment lacks sufficient evidence."""
    
    UNKNOWN = "unknown"
    """Insufficient information to assess confidence."""


# =============================================================================
# UNCERTAINTY LEVEL ENUMERATION
# =============================================================================

class UncertaintyLevel(Enum):
    """
    Levels of uncertainty in an evaluation assessment.
    
    PROPERTIES:
        • LOW: Input information is clear, assumptions are well-established
        • MEDIUM: Some ambiguity or unknowns exist
        • HIGH: Significant uncertainty about inputs or assumptions
        • UNKNOWN: Insufficient information to assess uncertainty
    """
    
    LOW = "low"
    """Input information is clear, assumptions are well-established."""
    
    MEDIUM = "medium"
    """Some ambiguity or unknowns exist."""
    
    HIGH = "high"
    """Significant uncertainty about inputs or assumptions."""
    
    UNKNOWN = "unknown"
    """Insufficient information to assess uncertainty."""


# =============================================================================
# CONFIDENCE ASSESSMENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class ConfidenceAssessment:
    """
    Assessment of confidence in evaluation results.
    
    CONFIDENCE is NOT the same as correctness. A high-confidence assessment
    may still be wrong if the evidence was misleading. Confidence measures
    the reliability of the assessment process given available evidence.
    
    PROPERTIES:
        • overall_confidence: Overall confidence level (0.0 to 1.0)
        • evidence_quality: Quality of evidence supporting assessment
        • model_confidence: Confidence in evaluation models/algorithms
        • data_sufficiency: Whether sufficient data was available
        • consistency: Consistency of results across assessments
    """
    
    overall_confidence: float = 0.5
    """Overall confidence level (0.0 to 1.0)."""
    
    evidence_quality: float = 0.5
    """Quality of evidence supporting assessment (0.0 to 1.0)."""
    
    model_confidence: float = 0.8
    """Confidence in evaluation models/algorithms (0.0 to 1.0)."""
    
    data_sufficiency: float = 0.5
    """Whether sufficient data was available (0.0 to 1.0)."""
    
    consistency: float = 0.7
    """Consistency of results across assessments (0.0 to 1.0)."""
    
    @classmethod
    def high_confidence(cls) -> ConfidenceAssessment:
        """Create a high confidence assessment."""
        return cls(
            overall_confidence=0.85,
            evidence_quality=0.9,
            model_confidence=0.95,
            data_sufficiency=0.85,
            consistency=0.9,
        )
    
    @classmethod
    def medium_confidence(cls) -> ConfidenceAssessment:
        """Create a medium confidence assessment."""
        return cls(
            overall_confidence=0.6,
            evidence_quality=0.7,
            model_confidence=0.85,
            data_sufficiency=0.6,
            consistency=0.7,
        )
    
    @classmethod
    def low_confidence(cls) -> ConfidenceAssessment:
        """Create a low confidence assessment."""
        return cls(
            overall_confidence=0.3,
            evidence_quality=0.4,
            model_confidence=0.85,
            data_sufficiency=0.2,
            consistency=0.5,
        )


# =============================================================================
# UNCERTAINTY ASSESSMENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class UncertaintyAssessment:
    """
    Assessment of uncertainty in evaluation inputs and assumptions.
    
    UNCERTAINTY is about the input data and assumptions, not about correctness.
    High uncertainty means we don't know enough to make a confident assessment.
    
    PROPERTIES:
        • overall_uncertainty: Overall uncertainty level (0.0 to 1.0)
        • epistemic_uncertainty: Uncertainty due to lack of knowledge
        • environmental_uncertainty: Uncertainty about environment/state
        • model_uncertainty: Uncertainty about evaluation models
        • incomplete_evidence: Degree to which evidence is incomplete
    """
    
    overall_uncertainty: float = 0.5
    """Overall uncertainty level (0.0 to 1.0)."""
    
    epistemic_uncertainty: float = 0.4
    """Uncertainty due to lack of knowledge (0.0 to 1.0)."""
    
    environmental_uncertainty: float = 0.3
    """Uncertainty about environment/state (0.0 to 1.0)."""
    
    model_uncertainty: float = 0.2
    """Uncertainty about evaluation models (0.0 to 1.0)."""
    
    incomplete_evidence: float = 0.5
    """Degree to which evidence is incomplete (0.0 to 1.0)."""
    
    @classmethod
    def low_uncertainty(cls) -> UncertaintyAssessment:
        """Create a low uncertainty assessment."""
        return cls(
            overall_uncertainty=0.2,
            epistemic_uncertainty=0.15,
            environmental_uncertainty=0.1,
            model_uncertainty=0.15,
            incomplete_evidence=0.2,
        )
    
    @classmethod
    def medium_uncertainty(cls) -> UncertaintyAssessment:
        """Create a medium uncertainty assessment."""
        return cls(
            overall_uncertainty=0.5,
            epistemic_uncertainty=0.4,
            environmental_uncertainty=0.35,
            model_uncertainty=0.25,
            incomplete_evidence=0.5,
        )
    
    @classmethod
    def high_uncertainty(cls) -> UncertaintyAssessment:
        """Create a high uncertainty assessment."""
        return cls(
            overall_uncertainty=0.8,
            epistemic_uncertainty=0.7,
            environmental_uncertainty=0.6,
            model_uncertainty=0.5,
            incomplete_evidence=0.9,
        )


# =============================================================================
# EVIDENCE QUALITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class EvidenceQuality:
    """
    Assessment of evidence quality supporting an evaluation.
    
    PROPERTIES:
        • overall_quality: Overall evidence quality (0.0 to 1.0)
        • source_reliability: Reliability of information sources
        • timeliness: How current the evidence is
        • completeness: How complete the evidence is
        • verifiability: How easily evidence can be verified
    """
    
    overall_quality: float = 0.5
    """Overall evidence quality (0.0 to 1.0)."""
    
    source_reliability: float = 0.5
    """Reliability of information sources (0.0 to 1.0)."""
    
    timeliness: float = 0.5
    """How current the evidence is (0.0 to 1.0)."""
    
    completeness: float = 0.5
    """How complete the evidence is (0.0 to 1.0)."""
    
    verifiability: float = 0.5
    """How easily evidence can be verified (0.0 to 1.0)."""
    
    @classmethod
    def high_quality(cls) -> EvidenceQuality:
        """Create a high quality evidence assessment."""
        return cls(
            overall_quality=0.9,
            source_reliability=0.95,
            timeliness=0.85,
            completeness=0.9,
            verifiability=0.95,
        )
    
    @classmethod
    def low_quality(cls) -> EvidenceQuality:
        """Create a low quality evidence assessment."""
        return cls(
            overall_quality=0.3,
            source_reliability=0.4,
            timeliness=0.2,
            completeness=0.3,
            verifiability=0.35,
        )