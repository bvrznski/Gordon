# Canonical Predictive Generation Types
# ======================================
"""
Generation types for the Predictive Processing Network Phase 4.9.1.

This module provides:
    - Prediction: Atomic prediction model with all required fields
    - PredictionRequest: Immutable request for prediction generation
    - PredictionGenerationResult: Result from generative model
    - PredictionPolicy: Configuration for prediction behavior

PHASE BOUNDARY:
    This module defines generation types ONLY. No computation, no learning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..enums import (
        PredictionLevel,
        PredictionTimescale,
        PredictionModality,
        ConfidenceLevel,
        UncertaintyLevel,
        PredictionStatus,
    )
    from ..content import ConfidenceEstimate, PredictiveUncertainty

# =============================================================================
# PREDICTION (ATOMIC MODEL)
# =============================================================================

@dataclass(frozen=True, slots=True)
class Prediction:
    """
    Immutable atomic prediction model.
    
    Fields:
        identity:           Prediction identity
        subject:            Subject being predicted (PredictiveSubjectReference or string)
        level:              Hierarchy level of this prediction
        timescale:          Timescale of the prediction
        modality:           Semantic domain/modality
        expected_state:     Expected future state
        confidence:         Confidence estimate for this prediction
        uncertainty:        Uncertainty estimate for this prediction  
        assumptions:        Material assumptions underlying this prediction
        constraints:        Applied constraints
        source:             Source reference (PredictionSourceReference or string)
        authority:          Authority over the predicted subject
        provenance:         Provenance tracking
        revision:           Prediction revision number
        
    Rules:
        - One canonical atomic Prediction model exists
        - No error fields, Action directives, learning signals
        - Deeply immutable with frozen dataclass
    """
    identity: str
    subject: str  # PredictiveSubjectReference or string code
    level: str  # PredictionLevel or string code
    timescale: str  # PredictionTimescale or string code
    modality: str  # PredictionModality or string code
    expected_state: dict[str, object]
    confidence: ConfidenceEstimate | None = None
    uncertainty: PredictiveUncertainty | None = None
    assumptions: tuple[dict[str, object], ...] = field(default_factory=tuple)
    constraints: tuple[dict[str, object], ...] = field(default_factory=tuple)
    source: str  # PredictionSourceReference or string code
    authority: str | None = None
    provenance: dict[str, str] | None = None
    revision: int = 1


# =============================================================================
# PREDICTION REQUEST (IMMUTABLE INPUT)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictionRequest:
    """
    Immutable prediction request.
    
    Fields:
        identity:           Request identity
        subject:            Subject to predict
        context:            Context projections for prediction
        belief_projection:  Belief state projection
        world_model_projection: World model projection
        requested_levels:   Requested hierarchy levels
        requested_timescales: Requested timescales
        modalities:         Requested modalities
        policy:             Prediction policy configuration
        semantic_time:      External semantic time reference (optional)
        provenance:         Request provenance
        
    Rules:
        - All inputs are immutable
        - No runtime references in request
        - Semantic time supplied externally, not acquired internally
    """
    identity: str
    subject: str  # PredictiveSubjectReference or string code
    context: tuple[dict[str, object], ...] = field(default_factory=tuple)
    belief_projection: dict[str, object] | None = None  # BeliefProjection or simplified
    world_model_projection: dict[str, object] | None = None  # WorldModelProjection or simplified
    requested_levels: tuple[str, ...] = field(default_factory=tuple)  # PredictionLevel codes
    requested_timescales: tuple[str, ...] = field(default_factory=tuple)  # PredictionTimescale codes
    modalities: tuple[str, ...] = field(default_factory=tuple)  # PredictionModality codes
    policy: dict[str, object] | None = None  # PredictionPolicy or simplified
    semantic_time: str | None = None  # External semantic time reference
    provenance: dict[str, str] | None = None


# =============================================================================
# PREDICTION GENERATION REQUEST (IMMUTABLE INPUT TO GENERATOR)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictionGenerationRequest:
    """
    Immutable request for the generative model.
    
    Fields:
        request_identity:   Source request identity
        subject:            Subject to predict
        context:            Context projections
        belief_projection:  Belief projection input
        world_model_projection: World model projection input
        levels:             Levels to generate predictions for
        timescales:         Timescales to consider
        modalities:         Modalities to cover
        constraints:        Additional constraints
        policy:             Policy configuration
        semantic_time:      External semantic time reference
        
    Rules:
        - Distinct from runtime or transport requests
        - Immutable only, no callbacks
    """
    request_identity: str
    subject: str  # PredictiveSubjectReference or string code
    context: tuple[dict[str, object], ...] = field(default_factory=tuple)
    belief_projection: dict[str, object] | None = None
    world_model_projection: dict[str, object] | None = None
    levels: tuple[str, ...] = field(default_factory=tuple)  # PredictionLevel codes
    timescales: tuple[str, ...] = field(default_factory=tuple)  # PredictionTimescale codes
    modalities: tuple[str, ...] = field(default_factory=tuple)  # PredictionModality codes
    constraints: tuple[dict[str, object], ...] = field(default_factory=tuple)
    policy: dict[str, object] | None = None
    semantic_time: str | None = None


# =============================================================================
# PREDICTION GENERATION RESULT (IMMUTABLE OUTPUT FROM GENERATOR)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictionGenerationResult:
    """
    Immutable result from generative model.
    
    Fields:
        request_identity:   Source request identity
        predictions:        Generated atomic predictions
        hierarchical_prediction: Hierarchical prediction aggregate
        forecasts:          Contextual forecasts
        latent_predictions: Latent state projections
        counterfactuals:    Counterfactual predictions
        confidence:         Overall confidence estimate
        uncertainty:        Overall uncertainty estimate
        findings:           Generation findings (validation issues, etc.)
        limitations:        Known limitations on predictions
        trace:              Structural trace of generation process
        status:             Final prediction status
        
    Rules:
        - No raw dictionaries as output
        - Immutable result structure
        - Status indicates completeness without implying correctness
    """
    request_identity: str
    predictions: tuple[Prediction, ...] = field(default_factory=tuple)
    hierarchical_prediction: dict[str, object] | None = None  # HierarchicalPrediction or simplified
    forecasts: tuple[dict[str, object], ...] = field(default_factory=tuple)  # ContextualForecast
    latent_predictions: tuple[dict[str, object], ...] = field(default_factory=tuple)  # LatentStateProjection
    counterfactuals: tuple[dict[str, object], ...] = field(default_factory=tuple)  # CounterfactualPrediction
    confidence: ConfidenceEstimate | None = None
    uncertainty: PredictiveUncertainty | None = None
    findings: tuple[dict[str, object], ...] = field(default_factory=tuple)
    limitations: tuple[dict[str, object], ...] = field(default_factory=tuple)
    trace: dict[str, object] | None = None
    status: str  # PredictionStatus or string code


# =============================================================================
# PREDICTION POLICY (IMMUTABLE CONFIGURATION)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictionPolicy:
    """
    Immutable prediction policy configuration.
    
    Fields:
        enabled_levels:         Which hierarchy levels are enabled
        supported_timescales:   Which timescales are supported
        supported_modalities:   Which modalities are supported
        hypothesis_limit:       Maximum number of hypotheses to generate
        counterfactual_limit:   Maximum counterfactual scenarios
        latent_prediction_enabled: Whether latent predictions are enabled
        counterfactual_prediction_enabled: Whether counterfactuals are enabled
        confidence_policy:      Confidence policy configuration
        uncertainty_policy:     Uncertainty policy configuration
        hierarchy_policy:       Hierarchy structure rules
        unknown_input_policy:   How to handle unknown inputs
        strictness:             Validation strictness level
        
    Rules:
        - Policy is immutable (frozen dataclass)
        - No callbacks, no model instances, no service references
    """
    enabled_levels: tuple[str, ...] = field(default_factory=tuple)  # PredictionLevel codes
    supported_timescales: tuple[str, ...] = field(default_factory=tuple)  # PredictionTimescale codes
    supported_modalities: tuple[str, ...] = field(default_factory=tuple)  # PredictionModality codes
    hypothesis_limit: int = 10
    counterfactual_limit: int = 5
    latent_prediction_enabled: bool = False
    counterfactual_prediction_enabled: bool = False
    confidence_policy: str | None = None
    uncertainty_policy: str | None = None
    hierarchy_policy: str | None = None
    unknown_input_policy: str = "reject"
    strictness: str = "normal"  # ValidationStrictness or string code


__all__ = [
    "Prediction",
    "PredictionRequest",
    "PredictionGenerationRequest",
    "PredictionGenerationResult",
    "PredictionPolicy",
]