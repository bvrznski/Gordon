# Canonical Predictive Enums
# ==========================
"""
Defines immutable enum types for the Predictive Processing Network.

PHASE 4.9.1: Prediction Generation Only
---------------------------------------
This module defines enum types used throughout the predictive layer.
All enums are frozen dataclasses with explicit string values.

NO runtime logic, NO mutation, NO external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Final


# =============================================================================
# PREDICTION LEVELS (DEFAULT HIERARCHY)
# =============================================================================

class PredictionLevel(Enum):
    """
    Canonical prediction hierarchy levels.
    
    DEFAULT HIERARCHY:
        SENSORY:     Raw observation expectations
        CONTEXTUAL:  Contextual and situational expectations  
        ABSTRACT:    High-level conceptual and goal-related expectations
        
    Rules:
        - Higher levels constrain lower levels semantically
        - Lower levels refine higher level predictions
        - Cross-level relations must be typed explicitly
        - No implicit ordering defines hierarchy
    """
    SENSORY = "sensory"
    CONTEXTUAL = "contextual"
    ABSTRACT = "abstract"


# =============================================================================
# PREDICTION TIMESTEPSCALES (TEMPORAL HORIZONS)
# =============================================================================

class PredictionTimescale(Enum):
    """
    Canonical prediction temporal horizons.
    
    DEFAULT VALUES:
        IMMEDIATE:      Next few moments (0-5 seconds)
        SHORT_TERM:     Near future (seconds to minutes)
        MEDIUM_TERM:    Intermediate horizon (minutes to hours)
        LONG_TERM:      Extended horizon (hours to days)
        OPEN_HORIZON:   Uncertain or open-ended time frame
        UNKNOWN:        Temporal basis unspecified
        
    Note:
        Timescales are semantic categories, NOT wall-clock measurements.
        Semantic time must be supplied externally where required.
    """
    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"
    OPEN_HORIZON = "open_horizon"
    UNKNOWN = "unknown"


# =============================================================================
# PREDICTION MODALITIES (SEMANTIC DOMAINS)
# =============================================================================

class PredictionModality(Enum):
    """
    Canonical prediction semantic modalities/domains.
    
    VALUES:
        SENSOR:         Physical sensor readings
        CONTEXTUAL:     Situational and environmental context
        SEMANTIC:       Conceptual and abstract knowledge
        TEMPORAL:       Temporal patterns and sequences
        Causal:         Causal relationships and effects
        GOAL:           Goal-related expectations
        TASK:           Task-specific predictions
        SOCIAL:         Social and interactive expectations
        INTERNAL:       Internal state projections
    """
    SENSOR = "sensor"
    CONTEXTUAL = "contextual"
    SEMANTIC = "semantic"
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    GOAL = "goal"
    TASK = "task"
    SOCIAL = "social"
    INTERNAL = "internal"


# =============================================================================
# CONFIDENCE LEVELS (QUALITATIVE)
# =============================================================================

class ConfidenceLevel(Enum):
    """
    Canonical qualitative confidence levels.
    
    VALUES:
        UNKNOWN:        No basis for assessment
        VERY_LOW:       Minimal support for prediction
        LOW:            Limited support, high uncertainty
        MODERATE:       Reasonable support with some doubts
        HIGH:           Strong support, relatively stable
        VERY_HIGH:      Very strong support, expected reliability
        
    Note:
        Confidence is distinct from Precision and Uncertainty.
        High confidence may coexist with high uncertainty about a different dimension.
    """
    UNKNOWN = "unknown"
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


# =============================================================================
# UNCERTAINTY LEVELS (QUALITATIVE)
# =============================================================================

class UncertaintyLevel(Enum):
    """
    Canonical qualitative uncertainty levels.
    
    VALUES:
        UNKNOWN:        Basis for assessment unknown
        LOW:            Relatively stable expectations
        MODERATE:       Some ambiguity or variability
        HIGH:           Significant uncertainty
        EXTREME:        Very high ambiguity, low stability
        
    Note:
        Uncertainty is decomposed into model, observation, context components.
        High confidence in the presence of uncertainty is representable.
    """
    UNKNOWN = "unknown"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


# =============================================================================
# PREDICTION STATUS
# =============================================================================

class PredictionStatus(Enum):
    """
    Canonical prediction status values.
    
    VALUES:
        COMPLETE:       All predictions successfully generated
        PARTIAL:        Some predictions generated, others blocked
        PROVISIONAL:    Generated but pending validation
        DEGRADED:       Generated with degraded confidence
        UNDERDETERMINED:Insufficient basis for confident prediction
        UNSUPPORTED:    Subject or context not supported
        INVALID:        Request could not be processed
        REJECTED:       Explicitly rejected by policy
    """
    COMPLETE = "complete"
    PARTIAL = "partial"
    PROVISIONAL = "provisional"
    DEGRADED = "degraded"
    UNDERDETERMINED = "underdetermined"
    UNSUPPORTED = "unsupported"
    INVALID = "invalid"
    REJECTED = "rejected"


# =============================================================================
# PREDICTIVE HYPOTHESIS STATUS
# =============================================================================

class PredictiveHypothesisStatus(Enum):
    """
    Canonical hypothesis status values for generation-time semantics.
    
    VALUES:
        CANDIDATE:          Candidate for consideration
        SUPPORTED:          Supported by current projections
        WEAKLY_SUPPORTED:   Some support but with reservations
        CONFLICTED:         Conflicts with other hypotheses
        UNDERDETERMINED:    Insufficient evidence to determine
        REJECTED:           Explicitly rejected
        UNKNOWN:            Status unknown
        
    Note:
        Generation-time status does not imply observational confirmation.
    """
    CANDIDATE = "candidate"
    SUPPORTED = "supported"
    WEAKLY_SUPPORTED = "weakly_supported"
    CONFLICTED = "conflicted"
    UNDERDETERMINED = "underdetermined"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


# =============================================================================
# CROSS-LEVEL RELATION KINDS
# =============================================================================

class CrossLevelRelationKind(Enum):
    """
    Canonical cross-level relationship kinds.
    
    VALUES:
        CONSTRAINS:         Higher level constrains lower level predictions
        ABSTRACTS:          Higher level abstracts from lower level details
        REFINES:            Lower level refines higher level predictions
        SUPPORTS:           Levels mutually support each other
        CONFLICTS_WITH:     Levels have conflicting predictions
        PROJECTS_TO:        Level projects expectations to another
        EXPLAINS:           One level explains another's predictions
        DEPENDS_ON:         Level depends on another for context
        
    Note:
        Cross-level relations must be typed explicitly, not inferred from list position.
    """
    CONSTRAINS = "constrains"
    ABSTRACTS = "abstracts"
    REFINES = "refines"
    SUPPORTS = "supports"
    CONFLICTS_WITH = "conflicts_with"
    PROJECTS_TO = "projects_to"
    EXPLAINS = "explains"
    DEPENDS_ON = "depends_on"


# =============================================================================
# PREDICTION SOURCE KIND
# =============================================================================

class PredictionSourceKind(Enum):
    """
    Canonical prediction source kinds.
    
    VALUES:
        WORLD_MODEL:        Generated from world model projections
        BELIEF_STATE:       Derived from belief state projections
        MEMORY_PROJECTION:  Based on memory projections
        PERCEPTION_CONTEXT: Grounded in perception context
        GOAL_CONTEXT:       Influenced by goal projections
        TASK_CONTEXT:       Shaped by task context projections
        LATENT_MODEL:       Generated through latent representations
        COUNTERFACTUAL_MODEL: Counterfactual scenario predictions
        EXTERNAL_MODEL:     External model integration
        
    Note:
        Source identifies where predictive information came from.
        It does not transfer authority over the predicted entity.
    """
    WORLD_MODEL = "world_model"
    BELIEF_STATE = "belief_state"
    MEMORY_PROJECTION = "memory_projection"
    PERCEPTION_CONTEXT = "perception_context"
    GOAL_CONTEXT = "goal_context"
    TASK_CONTEXT = "task_context"
    LATENT_MODEL = "latent_model"
    COUNTERFACTUAL_MODEL = "counterfactual_model"
    EXTERNAL_MODEL = "external_model"


# =============================================================================
# PREDICTIVE ASSUMPTION KINDS
# =============================================================================

class PredictiveAssumptionKind(Enum):
    """
    Canonical predictive assumption kinds.
    
    VALUES:
        WORLD_STATE:        Assumptions about current world state
        CONTEXT:            Assumptions about context stability
        CAUSAL:             Assumptions about causal relationships
        TEMPORAL:           Assumptions about temporal continuity
        AGENT:              Assumptions about agent behavior
        SENSOR:             Assumptions about sensor reliability
        MODEL:              Assumptions about model applicability
        COUNTERFACTUAL:     Assumptions for counterfactual scenarios
        
    Note:
        Material assumptions must be explicit, not hidden in generic context.
    """
    WORLD_STATE = "world_state"
    CONTEXT = "context"
    CAUSAL = "causal"
    TEMPORAL = "temporal"
    AGENT = "agent"
    SENSOR = "sensor"
    MODEL = "model"
    COUNTERFACTUAL = "counterfactual"


# =============================================================================
# PREDICTIVE CONSTRAINT KINDS
# =============================================================================

class PredictiveConstraintKind(Enum):
    """
    Canonical predictive constraint kinds.
    
    VALUES:
        PHYSICAL:   Constraints from physical laws
        CAUSAL:     Constraints from causal relationships
        TEMPORAL:   Constraints from temporal ordering
        TASK:       Constraints from task requirements
        GOAL:       Constraints from goal objectives
        CONTEXT:    Constraints from current context
        RESOURCE:   Constraints from resource limitations
        MODALITY:   Constraints from modality boundaries
        HIERARCHICAL: Constraints from hierarchy structure
        POLICY:     Constraints from policy rules
        
    Note:
        Constraints are externally supplied or derived from projections.
    """
    PHYSICAL = "physical"
    CAUSAL = "causal"
    TEMPORAL = "temporal"
    TASK = "task"
    GOAL = "goal"
    CONTEXT = "context"
    RESOURCE = "resource"
    MODALITY = "modality"
    HIERARCHICAL = "hierarchical"
    POLICY = "policy"


# =============================================================================
# COUNTERFACTUAL MODIFICATION KINDS
# =============================================================================

class CounterfactualModificationKind(Enum):
    """
    Canonical counterfactual modification kinds.
    
    VALUES:
        REPLACE_VALUE:      Replace a specific value
        ADD_ENTITY:         Add a new entity to the scenario
        REMOVE_ENTITY:      Remove an existing entity from the scenario
        CHANGE_CONTEXT:     Modify context projections
        CHANGE_GOAL_PROJECTION:  Change goal expectations
        CHANGE_TASK_PROJECTION:  Change task expectations
        CHANGE_ACTION_ASSUMPTION: Modify action assumptions
        CHANGE_CAUSAL_ASSUMPTION: Modify causal relationships
        CHANGE_TEMPORAL_ASSUMPTION: Modify temporal expectations
        
    Note:
        Modifications must have explicit targets and operations.
        No arbitrary recursive dictionary mutation allowed.
    """
    REPLACE_VALUE = "replace_value"
    ADD_ENTITY = "add_entity"
    REMOVE_ENTITY = "remove_entity"
    CHANGE_CONTEXT = "change_context"
    CHANGE_GOAL_PROJECTION = "change_goal_projection"
    CHANGE_TASK_PROJECTION = "change_task_projection"
    CHANGE_ACTION_ASSUMPTION = "change_action_assumption"
    CHANGE_CAUSAL_ASSUMPTION = "change_causal_assumption"
    CHANGE_TEMPORAL_ASSUMPTION = "change_temporal_assumption"


# =============================================================================
# PREDICTION FINDING CODES
# =============================================================================

class PredictionFindingCode(Enum):
    """
    Canonical prediction finding codes.
    
    VALUES:
        INVALID_REQUEST:          Request structure invalid
        INVALID_SUBJECT:          Subject reference invalid
        INVALID_CONTEXT:          Context projection invalid
        MISSING_BELIEF_PROJECTION: Belief projection required but missing
        MISSING_WORLD_MODEL_PROJECTION: World model projection required but missing
        UNSUPPORTED_LEVEL:        Requested level not supported by generator
        UNSUPPORTED_TIMESCALE:    Requested timescale not supported
        UNSUPPORTED_MODALITY:     Requested modality not supported
        INCOMPATIBLE_LEVELS:      Requested levels are incompatible
        INCOMPATIBLE_TIMESCALES:  Requested timescales are incompatible
        INVALID_CONFIDENCE:       Confidence value invalid
        INVALID_UNCERTAINTY:      Uncertainty value invalid
        MISSING_PROVENANCE:       Provenance information missing
        CONFLICTING_ASSUMPTIONS:  Material assumptions conflict
        CONSTRAINT_VIOLATION:     Constraint not satisfied
        COUNTERFACTUAL_INVALID:   Counterfactual scenario invalid
        LATENT_SCHEMA_MISMATCH:   Latent schema incompatible
        MODEL_UNAVAILABLE:        Required model unavailable
        PREDICTION_UNDERDETERMINED: Insufficient basis for prediction
        
    Note:
        Findings are deterministically ordered and typed.
    """
    INVALID_REQUEST = "invalid_request"
    INVALID_SUBJECT = "invalid_subject"
    INVALID_CONTEXT = "invalid_context"
    MISSING_BELIEF_PROJECTION = "missing_belief_projection"
    MISSING_WORLD_MODEL_PROJECTION = "missing_world_model_projection"
    UNSUPPORTED_LEVEL = "unsupported_level"
    UNSUPPORTED_TIMESCALE = "unsupported_timescale"
    UNSUPPORTED_MODALITY = "unsupported_modality"
    INCOMPATIBLE_LEVELS = "incompatible_levels"
    INCOMPATIBLE_TIMESCALES = "incompatible_timescales"
    INVALID_CONFIDENCE = "invalid_confidence"
    INVALID_UNCERTAINTY = "invalid_uncertainty"
    MISSING_PROVENANCE = "missing_provenance"
    CONFLICTING_ASSUMPTIONS = "conflicting_assumptions"
    CONSTRAINT_VIOLATION = "constraint_violation"
    COUNTERFACTUAL_INVALID = "counterfactual_invalid"
    LATENT_SCHEMA_MISMATCH = "latent_schema_mismatch"
    MODEL_UNAVAILABLE = "model_unavailable"
    PREDICTION_UNDERDETERMINED = "prediction_undetermined"


# =============================================================================
# PREDICTION LIMITATION KINDS
# =============================================================================

class PredictionLimitationKind(Enum):
    """
    Canonical prediction limitation kinds.
    
    VALUES:
        INSUFFICIENT_CONTEXT:      Context information insufficient
        INSUFFICIENT_PRIORS:       World model priors insufficient
        LOW_MODEL_CONFIDENCE:      Model confidence too low
        HIGH_MODEL_UNCERTAINTY:    Model uncertainty too high
        HIGH_CONTEXT_UNCERTAINTY:  Context uncertainty too high
        HIGH_OBSERVATION_UNCERTAINTY: Observation uncertainty too high
        UNSUPPORTED_HORIZON:       Temporal horizon not supported
        UNSUPPORTED_MODALITY:      Semantic modality not supported
        LATENT_MODEL_UNAVAILABLE:  Latent model unavailable
        COUNTERFACTUAL_MODEL_UNAVAILABLE: Counterfactual model unavailable
        EXTERNAL_AUTHORITY_UNCERTAIN: External authority uncertain
        WORLD_MODEL_STALE:         World model projection stale
        
    Note:
        Limitations describe constraints on prediction quality, not errors.
    """
    INSUFFICIENT_CONTEXT = "insufficient_context"
    INSUFFICIENT_PRIORS = "insufficient_priors"
    LOW_MODEL_CONFIDENCE = "low_model_confidence"
    HIGH_MODEL_UNCERTAINTY = "high_model_uncertainty"
    HIGH_CONTEXT_UNCERTAINTY = "high_context_uncertainty"
    HIGH_OBSERVATION_UNCERTAINTY = "high_observation_uncertainty"
    UNSUPPORTED_HORIZON = "unsupported_horizon"
    UNSUPPORTED_MODALITY = "unsupported_modality"
    LATENT_MODEL_UNAVAILABLE = "latent_model_unavailable"
    COUNTERFACTUAL_MODEL_UNAVAILABLE = "counterfactual_model_unavailable"
    EXTERNAL_AUTHORITY_UNCERTAIN = "external_authority_uncertain"
    WORLD_MODEL_STALE = "world_model_stale"


# =============================================================================
# VALIDATION STRICTNESS
# =============================================================================

class ValidationStrictness(Enum):
    """
    Canonical validation strictness levels.
    
    VALUES:
        RELAXED:   Minimal validation, prefer permissive interpretation
        NORMAL:    Standard validation with typical checks
        STRICT:    Full validation, reject any ambiguity
        CANNONICAL: Strictest validation, enforce all constraints
        
    Note:
        Validation is deterministic and side-effect free.
    """
    RELAXED = "relaxed"
    NORMAL = "normal"
    STRICT = "strict"
    CANNONICAL = "canonical"


# =============================================================================
# TRACE CODES (STRUCTURAL PROVENANCE)
# =============================================================================

class PredictiveTraceCode(Enum):
    """
    Canonical predictive trace codes for structural provenance.
    
    VALUES:
        REQUEST_VALIDATED:          Request passed validation
        CONTEXT_CONSTRUCTED:        Predictive context constructed
        BELIEF_PROJECTED:           Belief projection applied
        WORLD_MODEL_PROJECTED:      World model projection applied
        HIERARCHY_SELECTED:         Hierarchy configuration selected
        TIMESCALE_SELECTED:         Timescale selection recorded
        MODALITY_SELECTED:          Modality selection recorded
        PREDICTION_GENERATED:       Prediction generated successfully
        LATENT_PROJECTION_GENERATED: Latent projection computed
        COUNTERFACTUAL_GENERATED:   Counterfactual scenario evaluated
        CONFIDENCE_ASSIGNED:        Confidence estimate assigned
        UNCERTAINTY_DECOMPOSED:     Uncertainty decomposition computed
        HIERARCHY_VALIDATED:        Hierarchy structure validated
        PREDICTIVE_STATE_CONSTRUCTED: Predictive state constructed
        
    Note:
        Trace contains stable codes, not hidden reasoning text.
    """
    REQUEST_VALIDATED = "request_validated"
    CONTEXT_CONSTRUCTED = "context_constructed"
    BELIEF_PROJECTED = "belief_projected"
    WORLD_MODEL_PROJECTED = "world_model_projected"
    HIERARCHY_SELECTED = "hierarchy_selected"
    TIMESCALE_SELECTED = "timescale_selected"
    MODALITY_SELECTED = "modality_selected"
    PREDICTION_GENERATED = "prediction_generated"
    LATENT_PROJECTION_GENERATED = "latent_projection_generated"
    COUNTERFACTUAL_GENERATED = "counterfactual_generated"
    CONFIDENCE_ASSIGNED = "confidence_assigned"
    UNCERTAINTY_DECOMPOSED = "uncertainty_decomposed"
    HIERARCHY_VALIDATED = "hierarchy_validated"
    PREDICTIVE_STATE_CONSTRUCTED = "predictive_state_constructed"


# =============================================================================
# SEMANTIC TIME KINDS (EXTERNAL SUPPLY)
# =============================================================================

class SemanticTimeKind(Enum):
    """
    Canonical semantic time reference kinds.
    
    VALUES:
        ABSOLUTE:     Absolute temporal reference point
        RELATIVE:     Relative to another event
        DURATION:     Temporal duration specification
        CYCLE_OFFSET: Offset within a repeating cycle
        EPISODE_OFFSET: Position within an episode
        
    Note:
        Semantic time is supplied externally, not generated internally.
        No wall-clock acquisition occurs in Phase 4.9.1.
    """
    ABSOLUTE = "absolute"
    RELATIVE = "relative"
    DURATION = "duration"
    CYCLE_OFFSET = "cycle_offset"
    EPISODE_OFFSET = "episode_offset"


# =============================================================================
# LATENT SCHEMA KINDS
# =============================================================================

class LatentSchemaKind(Enum):
    """
    Canonical latent schema kinds.
    
    VALUES:
        VECTOR:      Fixed-dimension vector embedding
        SPARSE:      Sparse representation with indices
        DISTRIBUTED: Distributed activation pattern
        PROJECTION:  Projected latent representation
        
    Note:
        Latent vectors are immutable and schema-bound.
        Schema compatibility must be validated explicitly.
    """
    VECTOR = "vector"
    SPARSE = "sparse"
    DISTRIBUTED = "distributed"
    PROJECTION = "projection"


# =============================================================================
# UTILITY CONSTANTS
# =============================================================================

DEFAULT_PREDICTION_LEVELS: Final[tuple[PredictionLevel, ...]] = (
    PredictionLevel.SENSORY,
    PredictionLevel.CONTEXTUAL,
    PredictionLevel.ABSTRACT,
)

DEFAULT_TIMESTEPSCALES: Final[tuple[PredictionTimescale, ...]] = (
    PredictionTimescale.IMMEDIATE,
    PredictionTimescale.SHORT_TERM,
    PredictionTimescale.MEDIUM_TERM,
    PredictionTimescale.LONG_TERM,
)