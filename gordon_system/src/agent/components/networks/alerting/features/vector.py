# Alerting Feature Vector
# =======================

"""
Aggregated feature vector for alerting evidence.

This module provides AlertingFeatureVector, the canonical output of Phase 4.1.3.
It aggregates features from all analyzers with metadata about extraction provenance,
confidence, and validity flags.

Key properties:
    - Immutable (frozen dataclass)
    - Normalized features
    - Extraction provenance tracking
    - Confidence scores per feature
    - Validity flags for each feature
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any
from datetime import datetime


# =============================================================================
# AlertingFeatureVector: Aggregated Features with Metadata
# =============================================================================

@dataclass(frozen=True, slots=True)
class AlertingFeatureVector:
    """
    Aggregated feature vector from all analyzers.
    
    This is the canonical output of Phase 4.1.3 - transforming raw signals into
    structured evidence for downstream processing.
    
    Features are normalized to [0.0, 1.0] ranges where applicable.
    
    Structure:
        - Feature values: Normalized scalar measurements from all analyzers
        - Confidence scores: Per-feature confidence estimates
        - Validity flags: Whether each feature passed validation
        - Provenance: Tracking metadata for the extraction process
        - Timestamps: When features were computed
    
    The vector is NOT:
        - A behavioral decision
        - An attention demand score
        - A classification or recommendation
    
    It is purely descriptive: a structured representation of extracted evidence.
    """
    
    # Vector identity (for tracking across signals)
    vector_id: str
    
    # Feature values (all normalized to [0.0, 1.0] where applicable)
    # Change detection features
    absolute_change: float = 0.0
    relative_change: float = 0.0
    rate_of_change: float = 0.0
    acceleration: float = 0.0
    
    # Onset detection features
    onset_appearance: float = 0.0
    onset_activation: float = 0.0
    onset_emergence: float = 0.0
    
    # Offset detection features
    offset_termination: float = 0.0
    offset_disappearance: float = 0.0
    offset_cessation: float = 0.0
    
    # Contrast detection features
    local_contrast: float = 0.0
    background_contrast: float = 0.0
    context_contrast: float = 0.0
    
    # Temporal stability features
    variance: float = 0.0
    oscillation: float = 0.0
    consistency: float = 0.0
    drift: float = 0.0
    
    # Frequency analysis features
    event_frequency: float = 0.0
    periodicity: float = 0.0
    burstiness: float = 0.0
    
    # Prediction error features
    prediction_error_estimate: float = 0.0
    
    # Novelty features
    baseline_deviation: float = 0.0
    history_deviation: float = 0.0
    recent_context_deviation: float = 0.0
    
    # Urgency indicator features
    rapid_escalation: float = 0.0
    critical_threshold: float = 0.0
    time_sensitive_transition: float = 0.0
    
    # Context projection features (input values, not computed)
    task_criticality_projection: Optional[float] = None  # From external context
    focus_strength_projection: Optional[float] = None   # From external context
    resource_pressure_projection: Optional[float] = None  # From external context
    
    # Metadata - extraction provenance
    features_confidence: Dict[str, float] = field(default_factory=dict)
    validity_flags: Dict[str, bool] = field(default_factory=dict)
    extraction_timestamp: Optional[datetime] = None
    signal_id_reference: Optional[str] = None
    
    @property
    def feature_names(self) -> Tuple[str, ...]:
        """Return all feature names in the vector."""
        return (
            "absolute_change", "relative_change", "rate_of_change", "acceleration",
            "onset_appearance", "onset_activation", "onset_emergence",
            "offset_termination", "offset_disappearance", "offset_cessation",
            "local_contrast", "background_contrast", "context_contrast",
            "variance", "oscillation", "consistency", "drift",
            "event_frequency", "periodicity", "burstiness",
            "prediction_error_estimate",
            "baseline_deviation", "history_deviation", "recent_context_deviation",
            "rapid_escalation", "critical_threshold", "time_sensitive_transition",
            "task_criticality_projection", "focus_strength_projection", 
            "resource_pressure_projection"
        )
    
    @property
    def valid_feature_count(self) -> int:
        """Return count of features with validity=True."""
        return sum(1 for v in self.validity_flags.values() if v)
    
    @property
    def average_confidence(self) -> float:
        """Return average confidence across all features."""
        if not self.features_confidence:
            return 0.0
        return sum(self.features_confidence.values()) / len(self.features_confidence)
    
    def get_feature_value(self, name: str) -> Optional[float]:
        """
        Get feature value by name.
        
        Args:
            name: Feature name
            
        Returns:
            Feature value or None if not found
        """
        return getattr(self, name, None)
    
    def is_valid(self, name: str) -> bool:
        """
        Check if a feature is valid.
        
        Args:
            name: Feature name
            
        Returns:
            True if feature has validity flag set to True
        """
        return self.validity_flags.get(name, False)


# =============================================================================
# Validation Functions
# =============================================================================

def validate_feature_vector(vector: AlertingFeatureVector) -> Tuple[bool, list]:
    """
    Validate an AlertingFeatureVector.
    
    Checks:
        - All feature values are within valid ranges
        - Confidence scores are in [0.0, 1.0]
        - Validity flags are boolean
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Feature value range validation
    for name in vector.feature_names:
        if name == "vector_id":
            continue
            
        value = getattr(vector, name, None)
        
        # Skip optional context projections that can be None
        if name.endswith("_projection") and value is None:
            continue
            
        # Check numeric range [0.0, 1.0]
        if isinstance(value, (int, float)):
            if not (0.0 <= value <= 1.0):
                errors.append(f"{name} must be in [0.0, 1.0], got {value}")
    
    # Confidence score validation
    for name, confidence in vector.features_confidence.items():
        if not (0.0 <= confidence <= 1.0):
            errors.append(f"confidence({name}) must be in [0.0, 1.0], got {confidence}")
    
    return len(errors) == 0, errors