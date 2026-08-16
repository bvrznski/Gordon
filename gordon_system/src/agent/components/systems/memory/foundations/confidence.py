# Memory Confidence - Phase 5.1 Canonical Belief Measure
# ========================================================

"""
Memory Confidence: Explicit belief in artifact reliability.

Every Memory Artifact possesses:
    - confidence (0.0-1.0 belief in reliability)
    - uncertainty (completely independent measure)

Confidence Laws:
    CONFIDENCE-LAW-001: Every artifact exposes confidence
    CONFIDENCE-LAW-002: Every artifact exposes uncertainty
    CONFIDENCE-LAW-003: Confidence is never computed as inverse of uncertainty
    CONFIDENCE-LAW-004: Uncertainty remains explicitly represented
    CONFIDENCE-LAW-005: Confidence revisions preserve lineage
    CONFIDENCE-LAW-006: Uncertainty provenance is explicit
    CONFIDENCE-LAW-007: Historical confidence estimates are inspectable
    CONFIDENCE-LAW-008: Confidence evaluation is deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum, auto
import time


# =============================================================================
# CONFIDENCE BASIS - What supports the confidence claim?
# =============================================================================


class ConfidenceBasis(Enum):
    """
    Basis for confidence in an artifact.
    
    These are NOT mutually exclusive:
        EVIDENCE:        Supported by direct evidence
        INFERENCE:       Derived through logical reasoning
        AUTHORITY:       Attributed to a trusted source
        CONSISTENCY:     Consistent with known facts
        REPEATEDLY_VERIFIED: Verified multiple times
        ESTIMATE:        Rough estimate without strong basis
    """
    
    EVIDENCE = "evidence"                   # Supported by evidence
    INFERENCE = "inference"                 # Derived through reasoning
    AUTHORITY = "authority"                 # Trusted source
    CONSISTENCY = "consistency"             # Consistent with known facts
    REPEATEDLY_VERIFIED = "repeatedly_verified"
    ESTIMATE = "estimate"                   # Rough estimate


# =============================================================================
# MEMORY CONFIDENCE - Belief in reliability
# =============================================================================


@dataclass(frozen=True)
class MemoryConfidence:
    """
    Confidence level for a memory artifact.
    
    Confidence represents the belief that this artifact is reliable and 
    accurate. It's completely independent from uncertainty (which measures
    what we don't know).
    
    Fields:
        confidence:         0.0-1.0 belief in reliability
        
        # Support basis
        confidence_basis:   Why do we believe this? (evidence, inference, etc.)
        
        # Revision tracking
        confidence_revision: When was this confidence set?
    """
    
    confidence: float                      # 0.0 to 1.0
    
    confidence_basis: ConfidenceBasis = ConfidenceBasis.EVIDENCE
    confidence_revision: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Validate confidence value."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")
    
    @classmethod
    def low(cls) -> "MemoryConfidence":
        """Create a low confidence (0.0-0.3)."""
        return cls(confidence=0.2)
    
    @classmethod
    def moderate(cls) -> "MemoryConfidence":
        """Create a moderate confidence (0.4-0.7)."""
        return cls(confidence=0.55)
    
    @classmethod
    def high(cls) -> "MemoryConfidence":
        """Create a high confidence (0.8-1.0)."""
        return cls(confidence=0.9)
    
    @classmethod
    def with_basis(
        cls,
        confidence: float,
        basis: ConfidenceBasis = ConfidenceBasis.EVIDENCE,
    ) -> "MemoryConfidence":
        """
        Create a confidence level with specified basis.
        
        Args:
            confidence: 0.0-1.0
            basis: What supports this confidence?
            
        Returns:
            New MemoryConfidence
        """
        return cls(
            confidence=confidence,
            confidence_basis=basis,
        )
    
    @classmethod
    def update_confidence(cls, instance: "MemoryConfidence", new_value: float) -> "MemoryConfidence":
        """
        Update confidence to a new value.
        
        Args:
            instance: The confidence to update
            new_value: 0.0-1.0
            
        Returns:
            New MemoryConfidence with updated value
        """
        return dataclass_replace(
            instance,
            confidence=new_value,
            confidence_revision=time.time(),
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(instance: MemoryConfidence, **kwargs) -> MemoryConfidence:
    """Replace fields in a frozen dataclass."""
    return MemoryConfidence(
        confidence=kwargs.get("confidence", instance.confidence),
        confidence_basis=kwargs.get("confidence_basis", instance.confidence_basis),
        confidence_revision=kwargs.get("confidence_revision", instance.confidence_revision),
    )


def normalize_confidence(value: float) -> float:
    """
    Normalize a value to the 0.0-1.0 range.
    
    Args:
        value: Any numeric value
        
    Returns:
        Clamped to 0.0-1.0
    """
    return max(0.0, min(1.0, float(value)))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MemoryConfidence",
    "ConfidenceBasis",
    "dataclass_replace",
    "normalize_confidence",
]