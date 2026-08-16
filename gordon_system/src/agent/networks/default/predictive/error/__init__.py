# Canonical Prediction Error Network Phase 4.9.3
# ==============================================
"""
Prediction Error Processing Engine - The comparator architecture.

PHASE 4.9.3: PREDICTION ERROR PROCESSING ENGINE
-----------------------------------------------
This module provides the complete prediction error processing pipeline:

    - Comparator Registry: Maps semantic types to comparison algorithms
    - Comparators: Pure, deterministic comparison implementations
    - Residual Builder: Constructs immutable mismatch representations  
    - Hierarchy Processor: Builds hierarchical residual graphs
    - Aggregation Engine: Groups and aggregates residuals across timescales
    - Error Landscape Builder: Constructs aggregate error state
    - PredictionErrorProcessor: Single orchestrator for all comparisons

ARCHITECTURAL PRINCIPLES:
------------------------
    * Pure functions only (no side effects)
    * Deterministic ordering (stable output regardless of thread scheduling)
    * Immutable outputs (frozen dataclasses throughout)
    * Stateless comparators (no internal state between calls)
    * No interpretation (only computation, no belief revision)

NO BELIEF REVISION
NO PRECISION ESTIMATION  
NO ACTIVE INFERENCE
NO ACTION EXECUTION

Those belong to subsequent phases.

IMPORT STRUCTURE:
----------------
The processor entry point is:

    from gordon_system.src.agent.networks.default.predictive.error import (
        PredictionErrorProcessor,
    )

Usage:

    processor = PredictionErrorProcessor()
    result = processor.process(request)

OUTPUT:
------
PredictionErrorState - Immutable aggregate state containing all prediction errors.
"""

from __future__ import annotations

# Core processing components
from gordon_system.src.agent.networks.default.predictive.error.processor import (
    PredictionErrorProcessor,
)

# Input types
from gordon_system.src.agent.networks.default.predictive.error.request import (
    PredictionComparisonRequest,
    ObservationProjection,
    PredictionReference,
    ComparisonProvenance,
)

# Output types
from gordon_system.src.agent.networks.default.predictive.error.result import (
    PredictionErrorState,
    PredictionComparisonResult,
    PredictionError,
    Mismatch,
    Residual,
    HierarchicalPredictionError,
    ErrorMagnitude,
    ErrorDirection,
    ErrorConfidence,
    ErrorUncertainty,
    PredictionErrorTrace,
    TemporalMismatch,
    SpatialMismatch,
    CausalMismatch,
    StructuralMismatch,
    LatentMismatch,
    MultimodalMismatch,
)

# Enum types
from gordon_system.src.agent.networks.default.predictive.error.enums import (
    MismatchKind,
    ErrorMagnitude as ErrorMagnitudeEnum,
    ErrorDirection as ErrorDirectionEnum,
    ComparisonStrategy,
    LatentMetric,
    TraceCode,
    FindingsCode,
    LimitationsKind,
    ConfidenceLevel,
    UncertaintyLevel,
    CrossLevelRelationKind,
    Modality,
    ErrorHierarchyLevel,
    TimespanKind,
)

__all__ = [
    # Processors
    "PredictionErrorProcessor",
    
    # Request types
    "PredictionComparisonRequest",
    "ObservationProjection", 
    "PredictionReference",
    "ComparisonProvenance",
    
    # Result types
    "PredictionErrorState",
    "PredictionComparisonResult",
    "PredictionError",
    "Mismatch",
    "Residual",
    "HierarchicalPredictionError",
    "ErrorMagnitude",
    "ErrorDirection",
    "ErrorConfidence", 
    "ErrorUncertainty",
    "PredictionErrorTrace",
    "TemporalMismatch",
    "SpatialMismatch",
    "CausalMismatch",
    "StructuralMismatch",
    "LatentMismatch",
    "MultimodalMismatch",
    
    # Enum types
    "MismatchKind",
    "ErrorMagnitudeEnum",
    "ErrorDirectionEnum", 
    "ComparisonStrategy",
    "LatentMetric",
    "TraceCode",
    "FindingsCode",
    "LimitationsKind",
    "ConfidenceLevel",
    "UncertaintyLevel",
    "CrossLevelRelationKind",
    "Modality",
    "ErrorHierarchyLevel",
    "TimespanKind",
]

__version__ = "4.9.3"
__phase__ = "4.9.3"
__name__ = "prediction_error_processing"