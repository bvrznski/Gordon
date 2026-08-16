# Perception Confidence - Phase 5.2 Canonical Belief Measure
# ===========================================================

"""
Perception Confidence: Explicit belief in entity reliability.

Every PerceptualEntity possesses:
    - confidence (0.0-1.0 belief in reliability)
    - uncertainty (completely independent measure)

Confidence Laws:
    CONFIDENCE-LAW-001: Every entity exposes confidence explicitly
    CONFIDENCE-LAW-002: Every entity exposes uncertainty explicitly
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
    Basis for confidence in an entity.
    
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
# PERCEPTION CONFIDENCE - Belief in reliability
# =============================================================================


@dataclass(frozen=True)
class PerceptionConfidence:
    """
    Confidence level for a perceptual entity.
    
    Confidence represents the belief that this entity is reliable and 
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
    def low(cls) -> "PerceptionConfidence":
        """Create a low confidence (0.0-0.3)."""
        return cls(confidence=0.2)
    
    @classmethod
    def moderate(cls) -> "PerceptionConfidence":
        """Create a moderate confidence (0.4-0.7)."""
        return cls(confidence=0.55)
    
    @classmethod
    def high(cls) -> "PerceptionConfidence":
        """Create a high confidence (0.8-1.0)."""
        return cls(confidence=0.9)
    
    @classmethod
    def with_basis(
        cls,
        confidence: float,
        basis: ConfidenceBasis = ConfidenceBasis.EVIDENCE,
    ) -> "PerceptionConfidence":
        """
        Create a confidence level with specified basis.
        
        Args:
            confidence: 0.0-1.0
            basis: What supports this confidence?
            
        Returns:
            New PerceptionConfidence
        """
        return cls(
            confidence=confidence,
            confidence_basis=basis,
        )
    
    @classmethod
    def update_confidence(cls, instance: "PerceptionConfidence", new_value: float) -> "PerceptionConfidence":
        """
        Update confidence to a new value.
        
        Args:
            instance: The confidence to update
            new_value: 0.0-1.0
            
        Returns:
            New PerceptionConfidence with updated value
        """
        return dataclass_replace(
            instance,
            confidence=new_value,
            confidence_revision=time.time(),
        )


# =============================================================================
# PERCEPTION UNCERTAINTY - Known limitations
# =============================================================================


@dataclass(frozen=True)
class PerceptionUncertainty:
    """
    Uncertainty record for a perceptual entity.
    
    Uncertainty measures what we DON'T know, which is completely independent
    from confidence (which measures what we think we DO know).
    
    Fields:
        uncertainty:       0.0-1.0 known limitations
        
        # Uncertainty sources
        sensor_noise:      Noise in the sensing mechanism
        ambient_conditions:Environmental factors affecting perception
        signal_quality:    Quality of the acquired signal
        algorithm_limitations: Known limits of processing algorithms
        
        # Revision tracking
        uncertainty_revision: When was this uncertainty recorded?
    """
    
    uncertainty: float                    # 0.0 to 1.0 known limitations
    
    sensor_noise: float = 0.0            # Noise in the sensing mechanism
    ambient_conditions: str = "normal"   # Environmental factors
    signal_quality: float = 1.0          # Signal quality (1.0 = perfect)
    algorithm_limitations: Tuple[str, ...] = field(default_factory=tuple)  # Known algorithm limits
    
    uncertainty_revision: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Validate uncertainty value."""
        if not 0.0 <= self.uncertainty <= 1.0:
            raise ValueError(f"Uncertainty must be 0.0-1.0, got {self.uncertainty}")
    
    @property
    def effective_uncertainty(self) -> float:
        """
        Calculate the effective uncertainty considering all sources.
        
        This combines sensor noise and other uncertainty sources into
        a single measure.
        """
        base = self.uncertainty
        
        # Add sensor noise contribution (scaled)
        noise_contrib = self.sensor_noise * 0.3
        
        # Add signal quality penalty (inverse quality contributes to uncertainty)
        quality_penalty = (1.0 - self.signal_quality) * 0.3
        
        total = min(1.0, base + noise_contrib + quality_penalty)
        
        return total
    
    @classmethod
    def low(cls) -> "PerceptionUncertainty":
        """Create low uncertainty (minimal known limitations)."""
        return cls(
            uncertainty=0.1,
            sensor_noise=0.02,
            signal_quality=0.98,
        )
    
    @classmethod
    def moderate(cls) -> "PerceptionUncertainty":
        """Create moderate uncertainty."""
        return cls(
            uncertainty=0.35,
            sensor_noise=0.1,
            signal_quality=0.85,
        )
    
    @classmethod
    def high(cls) -> "PerceptionUncertainty":
        """Create high uncertainty (significant known limitations)."""
        return cls(
            uncertainty=0.65,
            sensor_noise=0.25,
            signal_quality=0.6,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace_confidence(instance: PerceptionConfidence, **kwargs) -> PerceptionConfidence:
    """Replace fields in a frozen confidence dataclass."""
    return PerceptionConfidence(
        confidence=kwargs.get("confidence", instance.confidence),
        confidence_basis=kwargs.get("confidence_basis", instance.confidence_basis),
        confidence_revision=kwargs.get("confidence_revision", instance.confidence_revision),
    )


def dataclass_replace_uncertainty(instance: PerceptionUncertainty, **kwargs) -> PerceptionUncertainty:
    """Replace fields in a frozen uncertainty dataclass."""
    return PerceptionUncertainty(
        uncertainty=kwargs.get("uncertainty", instance.uncertainty),
        sensor_noise=kwargs.get("sensor_noise", instance.sensor_noise),
        ambient_conditions=kwargs.get("ambient_conditions", instance.ambient_conditions),
        signal_quality=kwargs.get("signal_quality", instance.signal_quality),
        algorithm_limitations=kwargs.get("algorithm_limitations", instance.algorithm_limitations),
        uncertainty_revision=kwargs.get("uncertainty_revision", instance.uncertainty_revision),
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


def normalize_uncertainty(value: float) -> float:
    """
    Normalize a value to the 0.0-1.0 uncertainty range.
    
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
    "ConfidenceBasis",
    "PerceptionConfidence",
    "PerceptionUncertainty",
    "dataclass_replace_confidence",
    "dataclass_replace_uncertainty",
    "normalize_confidence",
    "normalize_uncertainty",
]
