# Cross-Modal Correlation - Phase 5.2 Evidence Grouping
# ======================================================

"""
CrossModalCorrelation: A grouping of perceptual evidence that originates from
multiple modalities but refers to the same underlying occurrence.

Correlation groups evidence without establishing causation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# CORRELATION TYPE - How evidences are correlated
# =============================================================================


class CorrelationType(Enum):
    """
    Types of correlation between perceptual evidence.
    
    TEMPORAL: Evidence from different modalities at similar times
    SPATIAL: Evidence from overlapping regions
    CAUSAL: One event appears to cause another (correlational only)
    SEMANTIC: Similar semantic interpretation across modalities
    STRUCTURAL: Same underlying structure detected by multiple modalities
    """
    
    TEMPORAL = "temporal"               # Time-aligned evidence
    SPATIAL = "spatial"                 # Region-overlapping evidence
    CAUSAL = "causal"                   # Cause-effect relationship (correlational)
    SEMANTIC = "semantic"               # Similar interpretation
    STRUCTURAL = "structural"           # Same underlying structure


# =============================================================================
# CORRELATION CANDIDATE - Evidence candidates for correlation
# =============================================================================


@dataclass(frozen=True)
class CorrelationCandidate:
    """
    A single observation that may participate in a correlation.
    
    Fields:
        modality_identity:   Which modality produced this evidence
        
        observation_id:      The observation's identifier
        
        timestamp_utc:       When observed
        
        confidence:          Modality's confidence in the observation
    """
    
    # Core identity (required)
    modality_identity: str              # Source modality
    
    observation_id: str                 # Observation reference
    
    timestamp_utc: float = 0.0          # When observed
    
    confidence: float = 1.0             # Modality's confidence


# =============================================================================
# CROSS-MODAL CORRELATION - Grouped evidence from multiple modalities
# =============================================================================


@dataclass(frozen=True)
class CrossModalCorrelation:
    """
    A grouping of perceptual evidence from multiple modalities.
    
    Correlation groups evidence. It does not establish causation.
    
    Fields:
        correlation_identity:  Unique identifier for this correlation
        
        participating_observations: References to correlated observations
        
        participating_modalities: Which modalities contributed
        
        correlation_type:        Type of correlation (temporal, spatial, etc.)
        
        temporal_alignment_ms:   Time alignment in milliseconds
        confidence:              Confidence in the correlation 0.0-1.0
        uncertainty:             Known limitations on the correlation
        
        provenance:              Correlation tracking
    """
    
    # Core identity (required)
    correlation_identity: str           # Globally unique identifier
    
    # Evidence participation
    participating_observations: Tuple[CorrelationCandidate, ...] = field(default_factory=tuple)
    
    participating_modalities: Tuple[str, ...] = field(default_factory=tuple)
    
    # Correlation type
    correlation_type: str = "temporal"  # CorrelationType value
    
    # Alignment metrics
    temporal_alignment_ms: float = 0.0  # Time alignment precision
    
    # Quality
    confidence: float = 1.0             # Confidence in correlation 0.0-1.0
    uncertainty: float = 0.0            # Known limitations
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    @property
    def is_temporally_aligned(self) -> bool:
        """Check if observations are temporally aligned."""
        return self.temporal_alignment_ms < 100.0  # Within 100ms
    
    @classmethod
    def create(
        cls,
        observations: Tuple[CorrelationCandidate, ...],
        correlation_type: str = "temporal",
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "CrossModalCorrelation":
        """
        Create a new cross-modal correlation.
        
        Args:
            observations: Observations to correlate
            correlation_type: Type of correlation
            confidence: Confidence in correlation
            uncertainty: Known limitations
            
        Returns:
            New CrossModalCorrelation instance
        """
        modalities = tuple(set(o.modality_identity for o in observations))
        
        return cls(
            correlation_identity=f"corr:{time.time_ns()}",
            participating_observations=observations,
            participating_modalities=modalities,
            correlation_type=correlation_type,
            confidence=confidence,
            uncertainty=uncertainty,
        )


# =============================================================================
# CORRELATOR - Interface for cross-modal correlation
# =============================================================================


class Correlator:
    """
    Interface for correlating evidence across modalities.
    
    Implementations handle:
        - Temporal alignment of observations
        - Spatial overlap detection
        - Semantic similarity matching
        - Confidence aggregation
    """
    
    def correlate_observations(
        self,
        modality_identities: Tuple[str, ...],
        observation_ids: Tuple[str, ...],
        correlation_types: Optional[Tuple[str, ...]] = None,
    ) -> Tuple[CrossModalCorrelation, ...]:
        """
        Attempt to correlate observations across modalities.
        
        Args:
            modality_identities: Modalities to check
            observation_ids: Observations to correlate
            correlation_types: Types of correlation to attempt
            
        Returns:
            Tuple of correlations (may be empty)
        """
        raise NotImplementedError
    
    def get_correlation_candidates(
        self,
        reference_modality: str,
        reference_timestamp_utc: float,
        time_window_ms: float = 100.0,
    ) -> Tuple[CorrelationCandidate, ...]:
        """
        Get candidate observations that may correlate with a reference.
        
        Args:
            reference_modality: Reference modality
            reference_timestamp_utc: Reference timestamp
            time_window_ms: Time window in milliseconds
            
        Returns:
            Candidates within the time window
        """
        raise NotImplementedError


# =============================================================================
# EXPORTS
# =============================================================================

__all__: list[str] = [
    # Enums
    "CorrelationType",
    
    # Dataclasses
    "CorrelationCandidate",
    "CrossModalCorrelation",
    
    # Classes
    "Correlator",
]