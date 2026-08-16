# Canonical Prediction Error Request Types
# ========================================
"""
Request types for Prediction Error Network Phase 4.9.2.

This module provides:
    - PredictionComparisonRequest: Immutable request for prediction comparison
    - ObservationProjection: External observation reference

PHASE BOUNDARY:
    This is pure semantic infrastructure with NO runtime dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# OBSERVATION PROJECTION (EXTERNAL SUPPLY)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ObservationProjection:
    """
    External observation projection for comparison with predictions.
    
    Rules:
        - Observation authority is external (not owned by error layer)
        - No ownership transfer via reference
        - Authority and revision preserved from source
    
    Fields:
        identity:           Semantic identity of observation
        modality:           Semantic domain/modality
        observed_state:     Observed state representation
        timestamp_ref:      External semantic time reference (optional)
        authority:          External authority reference
        provenance:         Observation provenance
    """
    identity: str  # SemanticIdentity or string code
    modality: str  # e.g., "vision", "audio", "language"
    observed_state: dict[str, Any]
    timestamp_ref: str | None = None  # External semantic time reference
    authority: str | None = None
    provenance: dict[str, str] | None = None


# =============================================================================
# PREDICTION COMPARISON REQUEST (IMMUTABLE INPUT)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictionComparisonRequest:
    """
    Immutable request for prediction comparison.
    
    Fields:
        identity:               Request identity
        prediction:             Prediction to compare against observation
        observation:            Observation projection for comparison
        policy:                 Comparison policy configuration
        semantic_time:          External semantic time reference (optional)
        provenance:             Request provenance
    
    Rules:
        - All inputs are immutable
        - No runtime references in request
        - Semantic time supplied externally, not acquired internally
    """
    identity: str  # RequestIdentity or string code
    prediction: dict[str, Any]  # Prediction or simplified reference
    observation: ObservationProjection | None = None
    policy: str | None = None  # ComparisonPolicy reference
    semantic_time: str | None = None  # External semantic time reference
    provenance: dict[str, str] | None = None


# =============================================================================
# PREDICTION REFERENCE (FOR ERROR MODEL)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictionReference:
    """
    Reference to a prediction for use in error representation.
    
    Fields:
        identity:           Prediction identity
        subject_identity:   Subject being predicted
        level:              Hierarchy level of prediction
        timescale:          Timescale horizon
        modality:           Semantic domain
        authority:          Authority over the prediction
    """
    identity: str  # PredictionIdentity or string code
    subject_identity: str  # SemanticIdentity or string code
    level: str  # ErrorHierarchyLevel or string code
    timescale: str  # TimespanKind or string code
    modality: str  # Modality or string code
    authority: str | None = None


# =============================================================================
# COMPARISON PROVENANCE (ERROR LAYER)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ComparisonProvenance:
    """
    Provenance for comparison results.
    
    Fields:
        request_identity:       Source comparison request identity
        prediction_reference:   Prediction reference used
        observation_identity:   Observation reference used
        policy_reference:       Policy applied during comparison
        trace_codes:            Trace events that occurred
        comparison_timestamp_ref: Semantic time of comparison (optional)
    """
    request_identity: str
    prediction_reference: str
    observation_identity: str
    policy_reference: str | None = None
    trace_codes: tuple[str, ...] = field(default_factory=tuple)
    comparison_timestamp_ref: str | None = None