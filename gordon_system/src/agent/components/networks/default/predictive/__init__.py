# Predictive Processing Network - Canonical Implementation
# ==========================================================
"""
Phase 4.9.1: Predictive Generation Only

The Predictive Processing Network generates expectations about future states.

It does NOT:
    - Compute prediction errors (Phase 4.9.2)
    - Update beliefs (Phase 4.9.5)
    - Perform active inference (Phase 4.9.6)
    - Allocate attention or execute actions

Canonical Output:
    Immutable predictions, forecasts, counterfactual projections,
    and Predictive Network State.

Package Structure:
    enums/          - Enum types (PredictionLevel, PredictionTimescale, etc.)
    __base__.py     - Identity, revision, provenance, serialization
    content/        - Confidence, Uncertainty, Assumptions, Constraints
    state/          - BeliefProjection, WorldModelProjection, HierarchicalPrediction
    generation/     - Prediction, Request, Result, Policy

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
        PredictionLevel,
        PredictionTimescale,
        PredictionModality,
        ConfidenceLevel,
        UncertaintyLevel,
        PredictionStatus,
        PredictiveHypothesisStatus,
        CrossLevelRelationKind,
        PredictionSourceKind,
        PredictiveAssumptionKind,
        PredictiveConstraintKind,
        CounterfactualModificationKind,
        PredictionFindingCode,
        PredictionLimitationKind,
        ValidationStrictness,
        PredictiveTraceCode,
        SemanticTimeKind,
        LatentSchemaKind,
    )

    # Base types (identity, revision, provenance)
    from .__base__ import (
        SemanticIdentity,
        RequestIdentity,
        PredictionIdentity,
        BeliefIdentity,
        WorldModelIdentity,
        HypothesisIdentity,
        ScenarioIdentity,
        LatentStateIdentity,
        LatentTrajectoryIdentity,
        ForecastIdentity,
        Revision,
        SchemaVersion,
        PredictionProvenance,
        BeliefProvenance,
        WorldModelProvenance,
        CounterfactualProvenance,
        StateIdentity,
        PolicyIdentity,
        GenerativeModelIdentity,
        PredictiveSubjectReference,
        SerializationEnvelope,
    )

    # Content types
    from .content import (
        ConfidenceEstimate,
        PredictiveUncertainty,
        PredictiveAssumption,
        PredictiveConstraint,
        PredictionSourceReference,
    )

    # State types
    from .state import (
        BeliefProjection,
        WorldModelProjection,
        PredictionLevelProjection,
        HierarchicalPrediction,
        ContextualForecast,
        LatentStateProjection,
        LatentTrajectory,
    )

    # Generation types
    from .generation import (
        Prediction,
        PredictionRequest,
        PredictionGenerationRequest,
        PredictionGenerationResult,
        PredictionPolicy,
    )


# =============================================================================
# CANONICAL EXPORTS (Phase 4.9.1)
# =============================================================================

__all__: list[str] = [
    # Enums
    "PredictionLevel",
    "PredictionTimescale", 
    "PredictionModality",
    "ConfidenceLevel",
    "UncertaintyLevel",
    "PredictionStatus",
    "PredictiveHypothesisStatus",
    "CrossLevelRelationKind",
    "PredictionSourceKind",
    "PredictiveAssumptionKind",
    "PredictiveConstraintKind",
    "CounterfactualModificationKind",
    "PredictionFindingCode",
    "PredictionLimitationKind",
    "ValidationStrictness",
    "PredictiveTraceCode",
    "SemanticTimeKind",
    "LatentSchemaKind",
    # Base types
    "SemanticIdentity",
    "RequestIdentity",
    "PredictionIdentity", 
    "BeliefIdentity",
    "WorldModelIdentity",
    "HypothesisIdentity",
    "ScenarioIdentity",
    "LatentStateIdentity",
    "LatentTrajectoryIdentity",
    "ForecastIdentity",
    "Revision",
    "SchemaVersion",
    "PredictionProvenance",
    "BeliefProvenance",
    "WorldModelProvenance",
    "CounterfactualProvenance",
    "StateIdentity",
    "PolicyIdentity",
    "GenerativeModelIdentity",
    "PredictiveSubjectReference",
    "SerializationEnvelope",
    # Content types
    "ConfidenceEstimate",
    "PredictiveUncertainty",
    "PredictiveAssumption",
    "PredictiveConstraint",
    "PredictionSourceReference",
    # State types
    "BeliefProjection", 
    "WorldModelProjection",
    "PredictionLevelProjection",
    "HierarchicalPrediction",
    "ContextualForecast",
    "LatentStateProjection",
    "LatentTrajectory",
    # Generation types
    "Prediction",
    "PredictionRequest",
    "PredictionGenerationRequest",
    "PredictionGenerationResult",
    "PredictionPolicy",
]


# =============================================================================
# PHASE CONSTANTS
# =============================================================================

PHASE_VERSION: str = "4.9.1"
PHASE_STATUS: str = "DEVELOPMENT"

CANONICAL_PREDICTIVE_SCHEMA: str = "gordon.predictive.state.v1"
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
Predictive Processing Network - Phase 4.9.1

The Predictive Processing Network (PPN) generates expectations about the world.

Core Principle:
    Intelligence is predictive, not reactive.
    
    PPN continuously proposes: "What should exist?"
    before perception determines: "What actually exists?"

This Phase (4.9.1):
    - Constructs hierarchical predictions
    - Maintains belief states and projections  
    - Generates expectations from world model
    - Estimates prediction confidence and uncertainty

NOT in this Phase:
    - Prediction error computation
    - Belief revision
    - Active inference
    - Attention allocation
    - Action execution

For complete documentation, see: docs/agent/architecture/predictive-network/
"""
