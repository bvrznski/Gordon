# Internal Context Confidence Model
# =================================

"""
Structured confidence assessment for internal context.

Confidence measures evidential quality, not truth. High confidence means
strong supporting evidence; low confidence means weak or conflicting evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class InternalContextConfidence:
    """
    Structured confidence assessment for internal context.
    
    Confidence measures evidential quality, not truth. High confidence means
    strong supporting evidence; low confidence means weak or conflicting evidence.
    
    CONFIDENCE LEVELS:
        • very_high (0.9+): Strong consensus with minimal uncertainty
        • high (0.75-0.9): Good evidence with minor uncertainty
        • medium (0.5-0.75): Mixed evidence, some uncertainty
        • low (0.25-0.5): Weak or conflicting evidence
        • very_low (< 0.25): Minimal supporting evidence
    
    PROPERTIES:
        • overall_confidence: Numerical score from 0.0 to 1.0
        • confidence_justification: List of reasons for the confidence level
        • source_reliability: Assessment of source quality
        • conflict_count: Number of conflicting pieces of evidence
    """
    
    overall_confidence: float = 0.5
    """Numerical confidence score from 0.0 to 1.0."""
    
    confidence_justification: Tuple[str, ...] = field(default_factory=tuple)
    """Reasons for the assigned confidence level."""
    
    source_reliability: float = 0.5
    """Assessment of source reliability (0.0 to 1.0)."""
    
    conflict_count: int = 0
    """Number of conflicting pieces of evidence found."""
    
    @classmethod
    def very_high(cls) -> InternalContextConfidence:
        """Create a very-high-confidence record."""
        return cls(
            overall_confidence=0.95,
            confidence_justification=("Strong consensus across sources",),
            source_reliability=0.95,
        )
    
    @classmethod
    def high(cls) -> InternalContextConfidence:
        """Create a high-confidence record."""
        return cls(
            overall_confidence=0.85,
            confidence_justification=("Strong evidence base",),
            source_reliability=0.9,
        )
    
    @classmethod
    def medium(cls) -> InternalContextConfidence:
        """Create a medium-confidence record."""
        return cls(
            overall_confidence=0.6,
            confidence_justification=("Mixed but reasonable evidence",),
            source_reliability=0.7,
        )
    
    @classmethod
    def low(cls) -> InternalContextConfidence:
        """Create a low-confidence record."""
        return cls(
            overall_confidence=0.35,
            confidence_justification=("Weak or conflicting evidence",),
            source_reliability=0.4,
            conflict_count=2,
        )
    
    @classmethod
    def very_low(cls) -> InternalContextConfidence:
        """Create a very-low-confidence record."""
        return cls(
            overall_confidence=0.15,
            confidence_justification=("Minimal supporting evidence",),
            source_reliability=0.2,
            conflict_count=5,
        )
    
    @classmethod
    def from_score(cls, score: float) -> InternalContextConfidence:
        """Create a confidence record from a numerical score."""
        if score >= 0.9:
            return cls.very_high()
        elif score >= 0.75:
            return cls.high()
        elif score >= 0.5:
            return cls.medium()
        elif score >= 0.25:
            return cls.low()
        else:
            return cls.very_low()
    
    def is_reliable(self) -> bool:
        """Check if confidence level is considered reliable (>= medium)."""
        return self.overall_confidence >= 0.5
    
    def to_normalized_score(self) -> float:
        """Return the confidence as a normalized score from 0.0 to 1.0."""
        return max(0.0, min(1.0, self.overall_confidence))