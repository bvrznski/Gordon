# Canonical Prediction Error Enums
# ================================
"""
Defines immutable enum types for the Prediction Error Network.

PHASE 4.9.2: Error Representation Only
--------------------------------------
This module defines enum types used throughout the error layer.
All enums are frozen dataclasses with explicit string values.

NO runtime logic, NO mutation, NO external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Final


# =============================================================================
# MISMATCH KINDS (ERROR TAXONOMY)
# =============================================================================

class MismatchKind(Enum):
    """
    Canonical mismatch kinds representing semantic disagreement.
    
    VALUES:
        VALUE:          Scalar value disagreement
        CATEGORY:       Semantic classification disagreement
        STRUCTURE:      Graph/hierarchy/topology mismatch
        TEMPORAL:       Time ordering or sequence mismatch
        SPATIAL:        Location or geometry mismatch
        CAUSAL:         Cause-effect relationship mismatch
        RELATIONAL:     Relationship type mismatch
        SEQUENCE:       Order of events mismatch
        PRESENCE:       Unexpected entity presence
        ABSENCE:        Expected entity missing
        LATENT:         Latent state projection disagreement
        MULTIMODAL:     Agreement across modalities
        UNKNOWN:        Mismatch kind unknown
        
    Rules:
        - Each mismatch has exactly one primary kind
        - Mismatch kinds are typed (not strings)
        - Mismatch kind is independent from magnitude
    """
    VALUE = "value"
    CATEGORY = "category"
    STRUCTURE = "structure"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    CAUSAL = "causal"
    RELATIONAL = "relational"
    SEQUENCE = "sequence"
    PRESENCE = "presence"
    ABSENCE = "absence"
    LATENT = "latent"
    MULTIMODAL = "multimodal"
    UNKNOWN = "unknown"


# =============================================================================
# ERROR MAGNITUDE (SEPARATE FROM KIND)
# =============================================================================

class ErrorMagnitude(Enum):
    """
    Canonical error magnitude levels.
    
    VALUES:
        NONE:           No mismatch detected
        VERY_SMALL:     Negligible deviation
        SMALL:          Minor deviation, likely acceptable
        MODERATE:       Noticeable deviation
        LARGE:          Significant deviation
        SEVERE:         Major deviation requiring attention
        UNKNOWN:        Magnitude unknown
        
    Rules:
        - Magnitude is independent from mismatch kind
        - Magnitude does not imply importance
        - Zero mismatch remains representable as NONE
    """
    NONE = "none"
    VERY_SMALL = "very_small"
    SMALL = "small"
    MODERATE = "moderate"
    LARGE = "large"
    SEVERE = "severe"
    UNKNOWN = "unknown"


# =============================================================================
# ERROR DIRECTION (SEMANTIC)
# =============================================================================

class ErrorDirection(Enum):
    """
    Canonical error direction representing semantic nature of mismatch.
    
    VALUES:
        EXPECTED_BUT_MISSING:       Expected entity not present
        UNEXPECTED_PRESENT:         Unwanted entity observed
        LOWER_THAN_EXPECTED:        Observed value below expectation
        HIGHER_THAN_EXPECTED:       Observed value above expectation
        SHIFTED:                    Temporal or spatial shift
        MISCLASSIFIED:              Wrong category assignment
        REORDERED:                  Sequence order incorrect
        STRUCTURALLY_MISMATCHED:    Structure differs from expectation
        UNKNOWN:                    Direction unknown
        
    Rules:
        - Direction is typed, not inferred from magnitude
        - Presence and absence remain distinct
        - Misclassification remains distinct from displacement
    """
    EXPECTED_BUT_MISSING = "expected_but_missing"
    UNEXPECTED_PRESENT = "unexpected_present"
    LOWER_THAN_EXPECTED = "lower_than_expected"
    HIGHER_THAN_EXPECTED = "higher_than_expected"
    SHIFTED = "shifted"
    MISCLASSIFIED = "misclassified"
    REORDERED = "reordered"
    STRUCTURALLY_MISMATCHED = "structurally_mismatched"
    UNKNOWN = "unknown"


# =============================================================================
# COMPARISON STRATEGIES
# =============================================================================

class ComparisonStrategy(Enum):
    """
    Canonical comparison strategies.
    
    VALUES:
        VALUE:            Scalar value comparison with tolerance
        CATEGORICAL:      Category/classification matching
        STRUCTURED:       Complex structure comparison (graph/tree)
        DISTRIBUTION:     Distribution-based comparison
        LATENT:           Latent space distance comparison
        MULTIMODAL:       Cross-modality alignment check
        
    Rules:
        - Strategy selection is deterministic based on schema
        - No runtime discovery of strategies
    """
    VALUE = "value"
    CATEGORICAL = "categorical"
    STRUCTURED = "structured"
    DISTRIBUTION = "distribution"
    LATENT = "latent"
    MULTIMODAL = "multimodal"


# =============================================================================
# LATENT COMPARE METRICS
# =============================================================================

class LatentMetric(Enum):
    """
    Canonical latent space comparison metrics.
    
    VALUES:
        COSINE:       Cosine similarity/distance
        EUCLIDEAN:    Euclidean distance
        MANHATTAN:    Manhattan distance  
        DOT_PRODUCT:  Dot product (unnormalized)
        
    Rules:
        - Metric identity is preserved during comparison
        - No training occurs in Phase 4.9.2
    """
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    DOT_PRODUCT = "dot_product"


# =============================================================================
# COMPARISON TRACE CODES (STRUCTURAL)
# =============================================================================

class TraceCode(Enum):
    """
    Canonical trace codes for structural provenance.
    
    VALUES:
        REQUEST_VALIDATED:      Request passed validation
        PREDICTION_LOADED:      Prediction referenced successfully  
        OBSERVATION_LOADED:     Observation loaded successfully
        STRATEGY_SELECTED:      Comparison strategy determined
        COMPARISON_COMPLETED:   Comparison executed
        MISMATCH_CLASSIFIED:    Mismatch type identified
        MAGNITUDE_ESTIMATED:    Magnitude level assigned
        ERROR_CREATED:          PredictionError constructed
        STATE_CONSTRUCTED:      PredictionErrorState constructed
        
    Rules:
        - Trace contains stable codes, not hidden reasoning text
    """
    REQUEST_VALIDATED = "request_validated"
    PREDICTION_LOADED = "prediction_loaded"
    OBSERVATION_LOADED = "observation_loaded"
    STRATEGY_SELECTED = "strategy_selected"
    COMPARISON_COMPLETED = "comparison_completed"
    MISMATCH_CLASSIFIED = "mismatch_classified"
    MAGNITUDE_ESTIMATED = "magnitude_estimated"
    ERROR_CREATED = "error_created"
    STATE_CONSTRUCTED = "state_constructed"


# =============================================================================
# FINDINGS CODES
# =============================================================================

class FindingsCode(Enum):
    """
    Canonical comparison findings.
    
    VALUES:
        INVALID_PREDICTION:         Prediction failed validation
        INVALID_OBSERVATION:        Observation failed validation
        MISSING_OBSERVATION:        No observation provided
        INVALID_POLICY:             Policy configuration invalid
        UNSUPPORTED_COMPARISON:     Comparison not supported for type
        UNKNOWN_VALUE_KIND:         Cannot determine value kind
        LATENT_SCHEMA_MISMATCH:     Latent schemas incompatible
        MODALITY_MISMATCH:          Modality combination invalid
        INVALID_HIERARCHY:          Hierarchy structure invalid
        
    Rules:
        - Findings are deterministically ordered and typed
    """
    INVALID_PREDICTION = "invalid_prediction"
    INVALID_OBSERVATION = "invalid_observation"
    MISSING_OBSERVATION = "missing_observation"
    INVALID_POLICY = "invalid_policy"
    UNSUPPORTED_COMPARISON = "unsupported_comparison"
    UNKNOWN_VALUE_KIND = "unknown_value_kind"
    LATENT_SCHEMA_MISMATCH = "latent_schema_mismatch"
    MODALITY_MISMATCH = "modality_mismatch"
    INVALID_HIERARCHY = "invalid_hierarchy"


# =============================================================================
# LIMITATIONS KIND
# =============================================================================

class LimitationsKind(Enum):
    """
    Canonical comparison limitations.
    
    VALUES:
        INSUFFICIENT_OBSERVATION:   Observation insufficient for comparison
        UNSUPPORTED_MODALITY:       Modality not supported by comparator
        UNKNOWN_SCHEMA:             Schema unknown or unrecognized  
        HIGH_UNCERTAINTY:           High uncertainty degrades confidence
        LATENT_MODEL_UNAVAILABLE:   Latent model unavailable
        UNKNOWN_HORIZON:            Temporal horizon unknown
        
    Rules:
        - Limitations describe constraints, not errors
    """
    INSUFFICIENT_OBSERVATION = "insufficient_observation"
    UNSUPPORTED_MODALITY = "unsupported_modality"
    UNKNOWN_SCHEMA = "unknown_schema"
    HIGH_UNCERTAINTY = "high_uncertainty"
    LATENT_MODEL_UNAVAILABLE = "latent_model_unavailable"
    UNKNOWN_HORIZON = "unknown_horizon"


# =============================================================================
# CONFIDENCE LEVELS (ERROR-SPECIFIC)
# =============================================================================

class ConfidenceLevel(Enum):
    """
    Canonical confidence levels for error representation.
    
    VALUES:
        UNKNOWN:        No basis for assessment
        VERY_LOW:       Minimal support for mismatch claim
        LOW:            Limited support, high uncertainty  
        MODERATE:       Reasonable support with some doubts
        HIGH:           Strong support, relatively stable
        VERY_HIGH:      Very strong support, expected reliability
        
    Rules:
        - Error confidence differs from prediction confidence
        - Error confidence is independent from uncertainty
    """
    UNKNOWN = "unknown"
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


# =============================================================================
# UNCERTAINTY LEVELS (ERROR-SPECIFIC)
# =============================================================================

class UncertaintyLevel(Enum):
    """
    Canonical uncertainty levels for error representation.
    
    VALUES:
        UNKNOWN:        Basis unknown
        LOW:            Relatively stable comparison result
        MODERATE:       Some ambiguity in mismatch type
        HIGH:           Significant uncertainty about mismatch
        EXTREME:        Very high ambiguity
        
    Rules:
        - Error uncertainty differs from prediction uncertainty
        - Uncertainty is decomposed into components
    """
    UNKNOWN = "unknown"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


# =============================================================================
# CROSS-LEVEL RELATION KINDS
# =============================================================================

class CrossLevelRelationKind(Enum):
    """
    Canonical cross-level error relationships.
    
    VALUES:
        SUPPORTS:           Higher level supports lower level predictions
        CONTRADICTS:        Levels have conflicting predictions
        PROPAGATES:         Error propagates between levels
        CONSTRAINTS:        One level constrains another's errors
        EXPLAINS:           One level explains another's error
        REFINES:            Lower level refines higher level error
        
    Rules:
        - Cross-level relations must be typed explicitly
    """
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    PROPAGATES = "propagates"
    CONSTRAINTS = "constrains"
    EXPLAINS = "explains"
    REFINES = "refines"


# =============================================================================
# MODALITY TYPES
# =============================================================================

class Modality(Enum):
    """
    Canonical modality types for mismatch representation.
    
    VALUES:
        VISION:         Visual perception data
        AUDIO:          Audio/speech data
        LANGUAGE:       Language/text data
        MEMORY:         Memory projection data
        LATENT:         Latent space representation
        WORLD_MODEL:    World model state
        
    Rules:
        - Modality is preserved in mismatch representation
    """
    VISION = "vision"
    AUDIO = "audio"
    LANGUAGE = "language"
    MEMORY = "memory"
    LATENT = "latent"
    WORLD_MODEL = "world_model"


# =============================================================================
# HIERARCHY LEVELS (ERROR)
# =============================================================================

class ErrorHierarchyLevel(Enum):
    """
    Canonical error hierarchy levels.
    
    VALUES:
        SENSORY:        Sensory mismatch
        CONTEXTUAL:     Contextual mismatch
        ABSTRACT:       Abstract conceptual mismatch
        
    Rules:
        - Errors preserve their originating hierarchy level
    """
    SENSORY = "sensory"
    CONTEXTUAL = "contextual"
    ABSTRACT = "abstract"


# =============================================================================
# TIMESPAN KINDS (TEMPORAL)
# =============================================================================

class TimespanKind(Enum):
    """
    Canonical temporal timespans for error representation.
    
    VALUES:
        IMMEDIATE:      Next few moments
        SHORT_TERM:     Seconds to minutes
        MEDIUM_TERM:    Minutes to hours
        LONG_TERM:      Hours to days
        OPEN_HORIZON:   Uncertain time frame
        
    Rules:
        - Timespan is semantic, not wall-clock
    """
    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"
    OPEN_HORIZON = "open_horizon"


# =============================================================================
# UTILITY CONSTANTS
# =============================================================================

DEFAULT_MISMATCH_KINDS: Final[tuple[MismatchKind, ...]] = (
    MismatchKind.VALUE,
    MismatchKind.CATEGORY,
    MismatchKind.STRUCTURE,
    MismatchKind.TEMPORAL,
    MismatchKind.SPATIAL,
    MismatchKind.CAUSAL,
)

DEFAULT_ERROR_MAGNITUDES: Final[tuple[ErrorMagnitude, ...]] = (
    ErrorMagnitude.NONE,
    ErrorMagnitude.VERY_SMALL,
    ErrorMagnitude.SMALL,
    ErrorMagnitude.MODERATE,
    ErrorMagnitude.LARGE,
    ErrorMagnitude.SEVERE,
)