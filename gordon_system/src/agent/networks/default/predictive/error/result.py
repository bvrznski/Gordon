# Canonical Prediction Error Result Types
# =======================================
"""
Result types for Prediction Error Network Phase 4.9.2.

This module provides:
    - PredictionComparisonResult: Immutable result from comparison
    - PredictionErrorState: Aggregate state of all errors

PHASE BOUNDARY:
    This is pure semantic infrastructure with NO runtime dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# PREDICTION COMPARISON RESULT (IMMUTABLE OUTPUT)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictionComparisonResult:
    """
    Immutable result from prediction comparison.
    
    Fields:
        request_identity:       Source request identity
        prediction_error:       Computed error representation
        findings:               Any additional findings during comparison
        limitations:            Known limitations on the result
        trace:                  Structural trace of comparison process
        provenance:             Result provenance
        
    Rules:
        - No raw dictionaries as output
        - Immutable result structure
        - Status indicates completeness without implying correctness
    """
    request_identity: str  # RequestIdentity or string code
    prediction_error: PredictionError | None = None
    findings: tuple[str, ...] = field(default_factory=tuple)  # FindingsCode codes
    limitations: tuple[str, ...] = field(default_factory=tuple)  # LimitationsKind codes
    trace: dict[str, Any] | None = None  # Trace codes and timestamps
    provenance: str | None = None  # ComparisonProvenance or reference


# =============================================================================
# PREDICTION ERROR STATE (AGGREGATE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictionErrorState:
    """
    Immutable aggregate state of all prediction errors.
    
    Fields:
        errors:                 All computed errors
        hierarchy:              Hierarchical error structure
        timescales:             Timescale-specific error breakdown
        confidence:             Overall confidence in error representation
        uncertainty:            Overall uncertainty decomposition
        findings:               Aggregate findings across all errors
        limitations:            Aggregate limitations across all errors
        trace:                  Structural trace of state construction
        provenance:             State provenance
        
    Rules:
        - Exactly one canonical PredictionErrorState exists
        - Immutable aggregate
        - No belief updates included
    """
    errors: tuple[PredictionError, ...] = field(default_factory=tuple)
    hierarchy: dict[str, Any] | None = None  # HierarchicalPredictionError
    timescales: dict[str, tuple[PredictionError, ...]] = field(
        default_factory=dict
    )  # TimespanKind -> errors
    confidence: str | None = None  # ErrorConfidence or reference
    uncertainty: dict[str, Any] | None = None  # UncertaintyDecomposition
    findings: tuple[str, ...] = field(default_factory=tuple)
    limitations: tuple[str, ...] = field(default_factory=tuple)
    trace: dict[str, Any] | None = None
    provenance: str | None = None


# =============================================================================
# CANONICAL PREDICTION ERROR MODEL (RESULT COMPONENT)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictionError:
    """
    Canonical immutable prediction error model.
    
    Fields:
        identity:               Error identity
        prediction_reference:   Reference to compared prediction
        observation_reference:  Reference to observed state
        mismatch:               Mismatch representation
        magnitude:              Error magnitude level
        direction:              Semantic direction of error
        confidence:             Confidence in mismatch existence
        uncertainty:            Uncertainty decomposition
        provenance:             Error provenance
        revision:               Error version
        
    Rules:
        - Exactly one canonical PredictionError model exists
        - Deeply immutable with frozen dataclass
        - No comparison mutations
    """
    identity: str  # PredictionErrorIdentity or string code
    prediction_reference: str  # PredictionReference
    observation_reference: str  # ObservationReference
    mismatch: Mismatch | None = None
    magnitude: str  # ErrorMagnitude or string code
    direction: str  # ErrorDirection or string code
    confidence: str | None = None  # ErrorConfidence or reference
    uncertainty: dict[str, Any] | None = None  # UncertaintyDecomposition
    provenance: str | None = None  # ErrorProvenance or reference
    revision: int = 1


# =============================================================================
# MISMATCH MODEL (SEMANTIC DISAGREEMENT)
# =============================================================================

@dataclass(frozen=True, slots=True)
class Mismatch:
    """
    Canonical mismatch representation.
    
    Fields:
        kind:                   Primary mismatch kind
        expected_value:         Expected value/state
        observed_value:         Observed value/state  
        semantic_difference:    Human-readable difference description
        confidence:             Confidence in mismatch classification
        uncertainty:            Uncertainty about the mismatch
        
    Rules:
        - Exactly one primary mismatch kind
        - Mismatch kind is independent from magnitude
        - No arbitrary payloads (structured data only)
    """
    kind: str  # MismatchKind or string code
    expected_value: Any | None = None
    observed_value: Any | None = None
    semantic_difference: str | None = None
    confidence: str | None = None  # ErrorConfidence or reference
    uncertainty: dict[str, Any] | None = None


# =============================================================================
# RESIDUAL MODEL (DIFFERENCE REPRESENTATION)
# =============================================================================

@dataclass(frozen=True, slots=True)
class Residual:
    """
    Canonical residual representation.
    
    Fields:
        expected:               Expected value/state
        observed:               Observed value/state
        difference:             Numerical or semantic difference
        representation:         How the difference is represented
        metric:                 Comparison metric used
        
    Rules:
        - Represents semantic difference only
        - No interpretation encoded
        - Immutable residual structure
    """
    expected: Any | None = None
    observed: Any | None = None
    difference: float | str | None = None
    representation: str | None = None  # ValueKind or string code
    metric: str | None = None  # LatentMetric or comparison type


# =============================================================================
# HIERARCHICAL PREDICTION ERROR (LEVEL-SPECIFIC)
# =============================================================================

@dataclass(frozen=True, slots=True)
class HierarchicalPredictionError:
    """
    Hierarchical error representation.
    
    Fields:
        level:                  Hierarchy level
        prediction_errors:      Errors at this level
        confidence:             Confidence at this level
        uncertainty:            Uncertainty decomposition
        cross_level_relations:  Relations to other levels
        
    Rules:
        - Errors preserve originating Prediction Level
        - Hierarchy remains explicit
    """
    level: str  # ErrorHierarchyLevel or string code
    prediction_errors: tuple[PredictionError, ...] = field(default_factory=tuple)
    confidence: str | None = None  # ErrorConfidence or reference
    uncertainty: dict[str, Any] | None = None
    cross_level_relations: tuple[dict[str, Any], ...] = field(default_factory=tuple)  # CrossLevelRelationKind


# =============================================================================
# ERROR MAGNITUDE (ALREADY IN enums.py)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ErrorMagnitude:
    """
    Error magnitude representation.
    
    Fields:
        level:                  Magnitude level enum value
        numeric_value:          Optional numeric equivalent
        context:                Context-specific interpretation
        
    Rules:
        - Magnitude is independent from mismatch kind
        - Magnitude does not imply importance
    """
    level: str  # ErrorMagnitude or string code
    numeric_value: float | None = None
    context: dict[str, Any] | None = None


# =============================================================================
# ERROR DIRECTION (ALREADY IN enums.py)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ErrorDirection:
    """
    Error direction representation.
    
    Fields:
        kind:                   Direction kind enum value
        magnitude:              Associated magnitude
        semantic_description:   Human-readable description
        
    Rules:
        - Direction is typed, not inferred from magnitude
    """
    kind: str  # ErrorDirection or string code
    magnitude: float | None = None
    semantic_description: str | None = None


# =============================================================================
# ERROR CONFIDENCE (ALREADY IN enums.py)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ErrorConfidence:
    """
    Error confidence representation.
    
    Fields:
        level:                  Confidence level enum value
        components:             Decomposed confidence sources
        calibration:            Calibration information
        
    Rules:
        - Error confidence differs from prediction confidence
        - Confidence is bounded
    """
    level: str  # ErrorConfidence or string code
    components: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    calibration: float | None = None


# =============================================================================
# ERROR UNCERTAINTY (ALREADY IN enums.py)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ErrorUncertainty:
    """
    Error uncertainty representation.
    
    Fields:
        decomposition:          Uncertainty decomposition
        comparison_uncertainty: Comparison-specific uncertainty
        prediction_uncertainty: Prediction-related uncertainty  
        observation_uncertainty: Observation-related uncertainty
        
    Rules:
        - Uncertainty is decomposed into components
        - Unknown uncertainty distinct from low uncertainty
    """
    decomposition: dict[str, float] = field(default_factory=dict)
    comparison_uncertainty: float | None = None
    prediction_uncertainty: float | None = None
    observation_uncertainty: float | None = None


# =============================================================================
# PREDICTION ERROR TRACE (ALREADY IN enums.py - TraceCode)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictionErrorTrace:
    """
    Immutable structural trace of error construction.
    
    Fields:
        events:                 Ordered sequence of trace codes
        timestamps:             Timestamps for each event
        metadata:               Additional context
        
    Rules:
        - Trace contains stable codes, not hidden reasoning text
    """
    events: tuple[str, ...] = field(default_factory=tuple)  # TraceCode codes
    timestamps: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


# =============================================================================
# TEMPORAL MISMATCH (DOMAIN-SPECIFIC)
# =============================================================================

@dataclass(frozen=True, slots=True)
class TemporalMismatch:
    """
    Temporal mismatch representation.
    
    Fields:
        expected_time:          Expected time reference
        observed_time:          Observed time reference
        temporal_offset:        Time difference
        sequence_mismatch:      Whether order is wrong
        
    Rules:
        - Temporal mismatch distinct from causal mismatch
    """
    expected_time: str | None = None
    observed_time: str | None = None
    temporal_offset: float | None = None
    sequence_mismatch: bool = False


# =============================================================================
# SPATIAL MISMATCH (DOMAIN-SPECIFIC)
# =============================================================================

@dataclass(frozen=True, slots=True)
class SpatialMismatch:
    """
    Spatial mismatch representation.
    
    Fields:
        expected_location:      Expected location
        observed_location:      Observed location
        spatial_offset:         Location difference
        topology_mismatch:      Whether topology differs
        
    Rules:
        - Wrong location, wrong geometry represented
    """
    expected_location: tuple[float, float] | None = None
    observed_location: tuple[float, float] | None = None
    spatial_offset: float | None = None
    topology_mismatch: bool = False


# =============================================================================
# CAUSAL MISMATCH (DOMAIN-SPECIFIC)
# =============================================================================

@dataclass(frozen=True, slots=True)
class CausalMismatch:
    """
    Causal mismatch representation.
    
    Fields:
        expected_cause:         Expected cause
        observed_cause:         Observed cause
        causal_relationship:    Changed relationship
        
    Rules:
        - Causal distinct from temporal mismatch
    """
    expected_cause: str | None = None
    observed_cause: str | None = None
    causal_relationship: str | None = None


# =============================================================================
# STRUCTURAL MISMATCH (DOMAIN-SPECIFIC)
# =============================================================================

@dataclass(frozen=True, slots=True)
class StructuralMismatch:
    """
    Structural mismatch representation.
    
    Fields:
        expected_structure:     Expected structure
        observed_structure:     Observed structure
        structural_difference:  Detailed difference description
        
    Rules:
        - Graph/hierarchy/topology mismatch
        - Not scalar disagreement
    """
    expected_structure: dict[str, Any] | None = None
    observed_structure: dict[str, Any] | None = None
    structural_difference: str | None = None


# =============================================================================
# LATENT MISMATCH (DOMAIN-SPECIFIC)
# =============================================================================

@dataclass(frozen=True, slots=True)
class LatentMismatch:
    """
    Latent mismatch representation.
    
    Fields:
        expected_latent:        Expected latent projection
        observed_latent:        Observed latent projection
        distance:               Distance metric result
        metric:                 Metric used for comparison
        
    Rules:
        - Latent comparison requires compatible schemas
        - No encoder training in Phase 4.9.2
    """
    expected_latent: tuple[float, ...] | None = None
    observed_latent: tuple[float, ...] | None = None
    distance: float | None = None
    metric: str | None = None  # LatentMetric or string code


# =============================================================================
# MULTIMODAL MISMATCH (DOMAIN-SPECIFIC)
# =============================================================================

@dataclass(frozen=True, slots=True)
class MultimodalMismatch:
    """
    Multimodal mismatch representation.
    
    Fields:
        modalities:             Modalities involved
        modality_disagreements: Per-modality disagreements
        
    Rules:
        - Modalities remain explicit
        - Agreement does not imply certainty
    """
    modalities: tuple[str, ...] = field(default_factory=tuple)
    modality_disagreements: tuple[dict[str, Any], ...] = field(default_factory=tuple)
