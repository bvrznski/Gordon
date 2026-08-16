# Prediction Error Network - Canonical Implementation
# =====================================================
"""
Phase 4.9.2: Prediction Error Representation

The Prediction Error layer compares predictions against observations.

It does NOT:
    - Revise beliefs (Phase 4.9.5)
    - Compute Precision weights (Phase 4.9.3)
    - Perform Active Inference (Phase 4.9.6)
    - Allocate attention or execute actions
    - Update the World Model

Canonical Output:
    Immutable PredictionError, PredictionErrorState, and comparison results.

Package Structure:
    enums/            - Mismatch kind enums
    __base__.py       - Identity, provenance, revision types
    request.py        - Comparison request (immutable input)
    result.py         - Comparison result (immutable output)
    policy.py         - Comparison policy configuration
    prediction_error.py  - Canonical Error model
    mismatch.py       - Mismatch representation
    residual.py       - Residual representation
    magnitude.py      - Error magnitude enum
    direction.py      - Error direction enum
    taxonomy.py       - Error taxonomy definitions
    hierarchy.py      - Hierarchical error handling
    temporal.py       - Temporal error handling
    spatial.py        - Spatial error handling  
    causal.py         - Causal error handling
    structural.py     - Structural error handling
    latent.py         - Latent comparison contracts
    multimodal.py     - Multimodal comparison
    confidence.py     - Error confidence estimation
    uncertainty.py    - Error uncertainty decomposition
    trace.py          - Structural trace codes
    state.py          - PredictionErrorState aggregate
    validation.py     - Validation functions

Import Rules:
    All imports must be from canonical modules.
    No runtime dependencies allowed in semantic layer.
    Deep immutability enforced through frozen dataclasses.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Enums (type definitions)
    from .enums import (
        MismatchKind,
        ErrorMagnitude,
        ErrorDirection,
        ComparisonStrategy,
        LatentMetric,
        ConfidenceLevel,
        UncertaintyLevel,
        TraceCode,
        FindingsCode,
        LimitationsKind,
    )

    # Base types
    from .__base__ import (
        SemanticIdentity,
        RequestIdentity,
        PredictionErrorIdentity,
        ObservationReference,
        ErrorProvenance,
        Revision,
        SchemaVersion,
        SerializationEnvelope,
    )

    # Comparison request and result
    from .request import (
        PredictionComparisonRequest,
        ObservationProjection,
    )
    
    from .result import (
        PredictionComparisonResult,
        PredictionErrorState,
    )

    # Policy
    from .policy import (
        ComparisonPolicy,
        ValueComparisonStrategy,
        CategoricalComparisonStrategy,
        StructuredComparisonStrategy,
    )

    # Error models
    from .prediction_error import (
        PredictionError,
        Mismatch,
        Residual,
    )

    # Components
    from .magnitude import ErrorMagnitude
    from .direction import ErrorDirection
    from .taxonomy import ErrorTaxonomy
    from .hierarchy import HierarchicalPredictionError, CrossLevelRelationKind

    # Domain-specific errors
    from .temporal import TemporalMismatch, TemporalResidual
    from .spatial import SpatialMismatch, SpatialResidual
    from .causal import CausalMismatch, CausalResidual
    from .structural import StructuralMismatch, StructuralResidual
    from .latent import LatentMismatch, LatentResidual, LatentComparisonContract
    from .multimodal import MultimodalMismatch, MultimodalResidual

    # Confidence and uncertainty
    from .confidence import ErrorConfidence, ErrorConfidenceDecomposition
    from .uncertainty import ErrorUncertainty, UncertaintyDecomposition

    # Trace and state
    from .trace import PredictionErrorTrace
    from .state import PredictionErrorState


# =============================================================================
# CANONICAL EXPORTS (Phase 4.9.2)
# =============================================================================

__all__: list[str] = [
    # Enums
    "MismatchKind",
    "ErrorMagnitude", 
    "ErrorDirection",
    "ComparisonStrategy",
    "LatentMetric",
    "ConfidenceLevel",
    "UncertaintyLevel",
    "TraceCode",
    "FindingsCode",
    "LimitationsKind",
    # Base types
    "SemanticIdentity",
    "RequestIdentity",
    "PredictionErrorIdentity",
    "ObservationReference",
    "ErrorProvenance",
    "Revision",
    "SchemaVersion",
    "SerializationEnvelope",
    # Request and Result
    "PredictionComparisonRequest",
    "ObservationProjection",
    "PredictionComparisonResult",
    "PredictionErrorState",
    # Policy
    "ComparisonPolicy",
    "ValueComparisonStrategy",
    "CategoricalComparisonStrategy", 
    "StructuredComparisonStrategy",
    # Error models
    "PredictionError",
    "Mismatch",
    "Residual",
    # Components
    "ErrorMagnitude",
    "ErrorDirection",
    "ErrorTaxonomy",
    "HierarchicalPredictionError",
    "CrossLevelRelationKind",
    # Domain-specific
    "TemporalMismatch", 
    "TemporalResidual",
    "SpatialMismatch",
    "SpatialResidual",
    "CausalMismatch",
    "CausalResidual",
    "StructuralMismatch",
    "StructuralResidual",
    "LatentMismatch",
    "LatentResidual",
    "LatentComparisonContract",
    "MultimodalMismatch",
    "MultimodalResidual",
    # Confidence and uncertainty
    "ErrorConfidence",
    "ErrorConfidenceDecomposition",
    "ErrorUncertainty", 
    "UncertaintyDecomposition",
    # Trace and state
    "PredictionErrorTrace",
    "PredictionErrorState",
]


# =============================================================================
# PHASE CONSTANTS
# =============================================================================

PHASE_VERSION: str = "4.9.2"
PHASE_STATUS: str = "DEVELOPMENT"

CANONICAL_ERROR_SCHEMA: str = "gordon.prediction_error.state.v1"
DEFAULT_HIERARCHY_LEVELS: tuple[str, ...] = ("sensory", "contextual", "abstract")
DEFAULT_TIMESTEPSCALES: tuple[str, ...] = (
    "immediate",
    "short_term", 
    "medium_term",
    "long_term",
)


# =============================================================================
# MODULE DOCUMENTATION
# =============================================================================

__doc__ = """
Prediction Error Network - Phase 4.9.2

The Prediction Error layer compares predictions against observations.

Core Principle:
    Intelligence is predictive, not reactive.
    
    PPN compares: What was expected? vs What actually occurred?
    
This Phase (4.9.2):
    - Represents prediction errors
    - Classifies mismatch types  
    - Preserves hierarchical structure
    - Maintains traceability
    
NOT in this Phase:
    - Belief revision
    - Precision weighting
    - Active inference
    - Attention allocation
    - Action execution

For complete documentation, see: docs/agent/architecture/predictive-network/
"""