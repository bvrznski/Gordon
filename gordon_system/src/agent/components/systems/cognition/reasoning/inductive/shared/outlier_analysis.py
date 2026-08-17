# Induction Outlier Analysis - Phase 7.2
# =======================================

"""
Canonical Outlier Analysis Contract.

Outlier analysis evaluates observations that violate discovered patterns.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class Outlier:
    """
    An outlier - an observation that violates discovered patterns.
    
    Outliers may indicate:
        - New phenomena not yet understood
        - Measurement or sensor errors
        - Exceptions to the rule
        - Model failures
    
    Outliers remain first-class artifacts and are never silently discarded.
    """
    
    # Identity
    outlier_identity: str                 # Unique identifier for this outlier
    
    # Supporting observation (reference)
    supporting_observation: str           # ID of the anomalous observation
    
    # Deviation measures
    deviation_measure: float = 0.0        # How much does it deviate?
    z_score: float = 0.0                  # Standard deviations from mean
    residual: float = 0.0                 # Difference from predicted value
    
    # Explanation candidates (possible reasons)
    explanation_candidates: Tuple[str, ...] = ()  # Possible explanations
    
    # Outlier characteristics
    is_extreme_outlier: bool = False      # Extreme deviation?
    is_moderate_outlier: bool = False     # Moderate deviation?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    detected_by_pattern: Optional[str] = None  # Which pattern was violated?
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def severity(self) -> float:
        """
        Calculate outlier severity based on deviation and other factors.
        
        Higher values indicate more significant outliers.
        """
        base_severity = self.deviation_measure
        
        # Extreme outliers get additional weight
        if self.is_extreme_outlier:
            base_severity *= 1.5
        
        return max(0.0, min(1.0, base_severity))
    
    def has_explanation(self) -> bool:
        """Check if this outlier has at least one explanation candidate."""
        return len(self.explanation_candidates) > 0


@dataclass(frozen=True)
class OutlierAnalysis:
    """
    Analysis of outliers in an observation set.
    
    An analysis records:
        - Analyzed outliers (all detected outliers)
        - Explanations for each
        - Recommendations based on findings
        - Provenance tracking
    
    Outliers remain first-class artifacts in the analysis.
    """
    
    # Identity
    analysis_identity: str                # Unique identifier for this analysis
    
    # Analyzed outliers
    analyzed_outliers: Tuple[Outlier, ...]
    
    # Explanation summary
    explanations_found: int = 0           # How many outliers have explanations?
    most_likely_explanation: Optional[str] = None  # Best overall explanation
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()  # Actions to consider
    action_required: bool = False         # Does this require immediate attention?
    
    # Outlier statistics
    total_outliers_detected: int = 0      # Total outliers found
    outlier_rate: float = 0.0             # Percentage of observations that are outliers
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    analysis_method: str = "default"
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def outlier_count(self) -> int:
        """Number of outliers analyzed."""
        return len(self.analyzed_outliers)
    
    @property
    def has_significant_outliers(self) -> bool:
        """Check if significant outliers were found."""
        return self.total_outliers_detected > 0


@dataclass(frozen=True)
class OutlierCandidate:
    """
    A candidate outlier awaiting analysis.
    
    This is a preliminary identification that may or may not
    be confirmed as a true outlier after detailed analysis.
    """
    
    # Identity
    candidate_identity: str               # Unique identifier
    
    # Observation details
    observation_id: str                   # ID of the suspicious observation
    observation_value: Any                # The value itself
    
    # Initial deviation
    initial_deviation: float = 0.0        # First-pass deviation estimate
    
    # Classification (may change after analysis)
    is_outlier: bool = False              # Is it confirmed as outlier?
    outlier_confidence: float = 0.5       # Confidence in outlier classification
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    detection_method: str = "default"
    provenance: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class OutlierReport:
    """
    Comprehensive report on outliers in a dataset.
    
    Provides high-level summary of outlier characteristics and implications.
    """
    
    report_id: str
    
    # Summary statistics
    total_observations_analyzed: int = 0
    outliers_found: int = 0
    outlier_percentage: float = 0.0
    
    # Outlier types found
    extreme_outliers: int = 0             # Very severe deviations
    moderate_outliers: int = 0            # Moderate deviations
    potential_errors: int = 0             # Likely measurement errors
    
    # Analysis results
    primary_cause: Optional[str] = None   # Main explanation for outliers
    secondary_causes: Tuple[str, ...] = ()  # Additional explanations
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()
    data_quality_score: float = 1.0       # Overall data quality (affected by outliers)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    analysis_method: str = "default"


__all__ = [
    "Outlier",
    "OutlierAnalysis",
    "OutlierCandidate",
    "OutlierReport",
]