# Canonical Predictive State Types
# ==================================
"""
State types for the Predictive Processing Network Phase 4.9.1.

This module provides immutable state types including:
    - BeliefProjection: Immutable projection of current beliefs
    - WorldModelProjection: Immutable world model projection
    - HierarchicalPrediction: Aggregate hierarchical prediction structure

PHASE BOUNDARY:
    This module defines state types ONLY. No mutation, no computation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..enums import PredictionLevel, PredictionTimescale, PredictionStatus
    from ..content import ConfidenceEstimate, PredictiveUncertainty

# =============================================================================
# BELIEF PROJECTION (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class BeliefProjection:
    """
    Immutable projection of current belief state.
    
    Fields:
        identity:           Belief state identity
        levels:             Hierarchical belief projections
        global_confidence:  Global confidence estimate
        global_uncertainty: Global uncertainty estimate
        authority:          External authority reference
        revision:           Belief state revision
        provenance:         Provenance tracking
        
    Rules:
        - BeliefProjection is input to prediction, not the authoritative mutable store
        - No mutation methods allowed
        - Hierarchical organization preserved
        - Authority and revision from external source maintained
    """
    identity: str
    levels: tuple[dict[str, object], ...] = field(default_factory=tuple)
    global_confidence: ConfidenceEstimate | None = None
    global_uncertainty: PredictiveUncertainty | None = None
    authority: str | None = None
    revision: int = 1
    provenance: dict[str, str] | None = None


# =============================================================================
# WORLD MODEL PROJECTION (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorldModelProjection:
    """
    Immutable world model projection.
    
    Fields:
        identity:           Model identity
        priors:             Prior expectations
        causal_relations:   Causal relationship projections
        structural_expectations: Structural expectations
        temporal_patterns:  Temporal pattern projections
        latent_patterns:    Latent pattern references
        model_uncertainty:  Uncertainty in the world model itself
        authority:          External authority reference
        revision:           Model revision
        provenance:         Provenance tracking
        
    Rules:
        - WorldModelProjection is input to prediction, not mutable world model
        - No pattern store ownership (Memory owns persistence)
        - Authority and revision from external source maintained
        - Revision tracked for staleness detection
    """
    identity: str
    priors: tuple[dict[str, object], ...] = field(default_factory=tuple)
    causal_relations: tuple[dict[str, object], ...] = field(default_factory=tuple)
    structural_expectations: tuple[dict[str, object], ...] = field(default_factory=tuple)
    temporal_patterns: tuple[dict[str, object], ...] = field(default_factory=tuple)
    latent_patterns: tuple[dict[str, object], ...] = field(default_factory=tuple)
    model_uncertainty: PredictiveUncertainty | None = None
    authority: str | None = None
    revision: int = 1
    provenance: dict[str, str] | None = None


# =============================================================================
# PREDICTION LEVEL PROJECTION (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictionLevelProjection:
    """
    Immutable projection of a single hierarchy level.
    
    Fields:
        level:              Level identity
        predictions:        Predictions at this level
        confidence:         Confidence for this level
        uncertainty:        Uncertainty for this level
        parent_level:       Parent level reference (if any)
        child_levels:       Child level references
        constraints:        Cross-level constraints
        provenance:         Provenance tracking
        
    Rules:
        - Level projections are immutable snapshots
        - No mutable collections inside
        - Parent-child relations explicit, not inferred from list position
    """
    level: str  # PredictionLevel or string code
    predictions: tuple[dict[str, object], ...] = field(default_factory=tuple)
    confidence: ConfidenceEstimate | None = None
    uncertainty: PredictiveUncertainty | None = None
    parent_level: str | None = None
    child_levels: tuple[str, ...] = field(default_factory=tuple)
    constraints: tuple[dict[str, object], ...] = field(default_factory=tuple)
    provenance: dict[str, str] | None = None


# =============================================================================
# HIERARCHICAL PREDICTION (AGGREGATE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class HierarchicalPrediction:
    """
    Immutable hierarchical prediction aggregate.
    
    Fields:
        identity:           Aggregate identity
        levels:             Level projections in hierarchy
        global_confidence:  Overall confidence estimate
        global_uncertainty: Overall uncertainty estimate
        timescale:          Prediction timescale
        cross_level_relations: Typed relations between levels
        provenance:         Provenance tracking
        revision:           Revision number
        
    Rules:
        - Single canonical hierarchical aggregate exists
        - Hierarchy is acyclic and explicitly typed
        - Global confidence references level-specific confidences
        - No mutable history inside
    """
    identity: str
    levels: tuple[PredictionLevelProjection, ...] = field(default_factory=tuple)
    global_confidence: ConfidenceEstimate | None = None
    global_uncertainty: PredictiveUncertainty | None = None
    timescale: str  # PredictionTimescale or string code
    cross_level_relations: tuple[dict[str, object], ...] = field(default_factory=tuple)
    provenance: dict[str, str] | None = None
    revision: int = 1


# =============================================================================
# CONTEXTUAL FORECAST (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ContextualForecast:
    """
    Immutable contextual forecast.
    
    Fields:
        identity:           Forecast identity
        subject:            Subject being forecast
        predicted_state:    Predicted future state
        horizon:            Temporal horizon
        source_context:     Source context projection reference
        anticipated_context: Anticipated future context (optional)
        confidence:         Forecast confidence
        uncertainty:        Forecast uncertainty
        assumptions:        Material assumptions for this forecast
        provenance:         Provenance tracking
        
    Rules:
        - Forecasts are distinct from basic predictions
        - Horizon is typed semantic value, not wall-clock
        - No scheduling of future evaluation (that's a later phase)
    """
    identity: str
    subject: str  # PredictiveSubjectReference or string code
    predicted_state: dict[str, object]
    horizon: str  # PredictionHorizon or string code
    source_context: str | None = None
    anticipated_context: dict[str, object] | None = None
    confidence: ConfidenceEstimate | None = None
    uncertainty: PredictiveUncertainty | None = None
    assumptions: tuple[dict[str, object], ...] = field(default_factory=tuple)
    provenance: dict[str, str] | None = None


# =============================================================================
# LATENT STATE PROJECTION (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class LatentStateProjection:
    """
    Immutable latent state projection.
    
    Fields:
        identity:           Latent state identity
        embedding:          Latent vector (immutable tuple)
        level:              Hierarchy level of this projection
        timescale:          Timescale of prediction
        confidence:         Confidence in latent representation
        uncertainty:        Uncertainty about latent values
        encoder_reference:  Encoder/model reference
        latent_schema:      Schema reference for validation
        provenance:         Provenance tracking
        
    Rules:
        - Latent vectors are immutable (tuples, not mutable lists)
        - Schema compatibility must be validated
        - No NaN or infinity in embeddings
    """
    identity: str
    embedding: tuple[float, ...]  # Immutable tuple of floats
    level: str  # PredictionLevel or string code
    timescale: str  # PredictionTimescale or string code
    confidence: ConfidenceEstimate | None = None
    uncertainty: PredictiveUncertainty | None = None
    encoder_reference: str | None = None
    latent_schema: str | None = None
    provenance: dict[str, str] | None = None
    
    def __post_init__(self) -> None:
        # Validate embedding values if present
        import math
        for value in self.embedding:
            if math.isnan(value) or math.isinf(value):
                raise ValueError("Latent embeddings cannot contain NaN or infinity")


# =============================================================================
# LATENT TRAJECTORY (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class LatentTrajectory:
    """
    Immutable latent trajectory.
    
    Fields:
        identity:           Trajectory identity
        start_state:        Starting latent state
        projected_states:   Intermediate states in projection
        end_state:          Terminal predicted state
        horizon:            Temporal horizon of trajectory
        confidence:         Overall trajectory confidence
        uncertainty:        Overall trajectory uncertainty  
        transition_model:   Model used for projection
        provenance:         Provenance tracking
        
    Rules:
        - Trajectory states are immutable snapshots
        - Horizon is typed semantic value, not wall-clock duration
        - No internal history mutation (that's a later phase)
    """
    identity: str
    start_state: LatentStateProjection
    projected_states: tuple[LatentStateProjection, ...] = field(default_factory=tuple)
    end_state: LatentStateProjection | None = None
    horizon: str  # PredictionHorizon or string code
    confidence: ConfidenceEstimate | None = None
    uncertainty: PredictiveUncertainty | None = None
    transition_model: str | None = None
    provenance: dict[str, str] | None = None


__all__: list[str] = [
    "BeliefProjection",
    "WorldModelProjection",
    "PredictionLevelProjection",
    "HierarchicalPrediction",
    "ContextualForecast",
    "LatentStateProjection",
    "LatentTrajectory",
]
