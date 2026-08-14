# Alerting Network Models and Contracts
# ======================================

"""
Data models for alerting assessment.

All models are immutable dataclasses with frozen=True to ensure:
- Deterministic behavior
- Thread safety
- Hashability (for use in sets/dicts)
- No side effects from modification
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Optional, Tuple, Any
from datetime import datetime

# Import enums
from .enums import (
    AlertingModality,
    AlertingSource,
    AlertingLevel,
    AlertingRecommendation,
    AlertingReasonCategory,
    AlertingStateTransition,
)


# Type aliases for clarity
AlertingSignalId = str
AlertingAssessmentId = str
AlertingScalar = float


@dataclass(frozen=True, slots=True)
class AlertingContext:
    """
    Optional context that may modulate alert demand.
    
    This represents state owned by higher layers (Executive, Workspace, etc.).
    The AlertingNetwork consumes this but does NOT own or modify it.
    """
    
    # Current cognitive state
    current_focus_strength: Optional[float] = None  # 0.0 to 1.0
    current_task_criticality: Optional[float] = None  # 0.0 to 1.0
    current_cognitive_load: Optional[float] = None  # 0.0 to 1.0
    
    # Signal relevance
    signal_relevance: Optional[float] = None  # 0.0 to 1.0
    safety_relevance: Optional[float] = None  # 0.0 to 1.0
    
    # External hints (owned by other systems)
    external_priority_hint: Optional[float] = None  # 0.0 to 1.0
    internal_priority_hint: Optional[float] = None  # 0.0 to 1.0
    
    # Recent alert pressure
    recent_alert_pressure: Optional[float] = None  # 0.0 to 1.0


@dataclass(frozen=True, slots=True)
class AlertingInput:
    """
    A single signal presented for alert-demand assessment.
    
    This is the canonical input contract for the AlertingNetwork.
    All fields must be provided or explicitly set to None (for optionals).
    
    Requirements:
        - Immutable
        - Validated (see validation module)
        - Bounded (no arbitrary growth)
        - Serialization-ready
        - No live objects, callbacks, or service handles
    """
    
    # Identity (required for tracking state)
    signal_id: AlertingSignalId
    
    # Source and modality (required for proper routing and classification)
    source: AlertingSource
    modality: AlertingModality
    
    # Timestamp (required - no wall-clock usage inside the network)
    timestamp: datetime  # Use Python's datetime; injected by caller
    
    # Primary signal features
    intensity: Optional[float] = None  # 0.0 to 1.0, or None for absence
    
    previous_intensity: Optional[float] = None  # Previous known value
    
    background_intensity: Optional[float] = None  # Baseline context level
    
    # Event flags
    onset: Optional[bool] = None
    offset: Optional[bool] = None
    change_detected: Optional[bool] = None
    
    # External hints (provided by other systems)
    novelty_hint: Optional[float] = None  # 0.0 to 1.0, or None if not available
    
    urgency_hint: Optional[float] = None  # 0.0 to 1.0, or None if not available
    
    prediction_error: Optional[float] = None  # 0.0 to 1.0, or None
    
    biological_relevance_hint: Optional[float] = None  # 0.0 to 1.0, or None
    
    # Optional context (owned by caller)
    context: Optional[AlertingContext] = None
    
    # Additional attributes for extensibility
    # Keys must be strings; values must be scalars
    attributes: Mapping[str, AlertingScalar] = field(default_factory=dict)
    
    # Provenance tracking
    provenance: Optional[AlertingProvenance] = None


@dataclass(frozen=True, slots=True)
class AlertingFeatures:
    """
    Computed features from a signal assessment.
    
    This is part of the output contract. Each feature must have:
        - Clear meaning documented
        - Expected range (usually 0.0 to 1.0)
        - Missing-data behavior defined
    
    Features are NOT authoritative on their own. They contribute to the final
    demand score but don't command behavior.
    """
    
    # Intensity and change features
    intensity: float  # The signal's intensity (0.0 to 1.0)
    delta_intensity: float  # Absolute change from previous
    normalized_change: float  # Change relative to baseline
    
    onset_strength: float  # Evidence of sudden onset
    offset_strength: float  # Evidence of sudden offset
    
    # Temporal and novelty features
    novelty: float  # Deviation from recent baseline
    prediction_error: float  # Externally supplied prediction error
    urgency: float  # Time-sensitive demand (0.0 to 1.0)
    
    # Contrast and salience
    contrast: float  # Signal-to-background ratio
    biological_relevance: float  # Biological significance evidence
    
    # State-based attenuation
    pattern_violation: float  # Violated expected pattern
    unexpected_onset: float  # Onset without prior warning
    unexpected_offset: float  # Offset without warning
    
    habituation: float  # Reduced response due to repetition (0.0 to 1.0)
    refractory_attenuation: float  # Attenuation from recent alerts (0.0 to 1.0)


@dataclass(frozen=True, slots=True)
class AlertingModulation:
    """
    Modulation factors applied during assessment.
    
    These show how context and state modified the base score.
    The final score is computed as:
        
        base_score + positive_modulation - negative_modulation = final_score
    
    All values are clamped to [0.0, 1.0].
    """
    
    # Modulation components
    positive_modulation: float  # Factors that increase demand
    negative_modulation: float  # Factors that decrease demand
    
    # Context effects
    focus_modulation: float  # Effect of current focus strength
    task_criticality_modulation: float  # Effect of task criticality
    cognitive_load_modulation: float  # Effect of cognitive load
    
    # State-based modulation
    habituation_modulation: float  # Attenuation from habituation
    refractory_modulation: float  # Attenuation from refractory period


@dataclass(frozen=True, slots=True)
class AlertingReason:
    """
    A single reason contributing to an assessment.
    
    Each reason must be based on actual computed evidence, not fixed text.
    The network returns a tuple of reasons to explain its decision.
    """
    
    # Reason identity
    code: str  # Machine-readable code (e.g., "SUDDEN_INTENSITY_CHANGE")
    
    category: AlertingReasonCategory  # Categorical classification
    
    # Human-readable explanation
    description: str  # Brief natural-language summary
    
    # Evidence contribution
    contribution: float  # How much this reason affected the score (0.0 to 1.0)
    
    confidence: float  # Confidence in this reason's applicability (0.0 to 1.0)
    
    # Evidence reference (for debugging/audit)
    evidence_reference: str  # e.g., "intensity_delta > threshold"


@dataclass(frozen=True, slots=True)
class AlertingProvenance:
    """
    Provenance tracking for assessment.
    
    Records where data came from without embedding implementation details.
    """
    
    # Input source
    input_source: Optional[AlertingSource] = None  # Source of the original signal
    
    # Processing metadata
    processed_at: Optional[datetime] = None  # When assessment was computed
    
    # Configuration version (for reproducibility)
    config_version: Optional[str] = None  # e.g., "1.0.0"
    
    # Deterministic trace
    seed_hash: Optional[int] = None  # For deterministic testing
    
    # Optional caller reference
    caller_id: Optional[str] = None


@dataclass(frozen=True, slots=True)
class AlertingStateTransitionRecord:
    """
    Record of state changes during assessment.
    
    Used for explainability and debugging. Not part of the core output but
    available through snapshot_state() or detailed logs.
    """
    
    signal_id: AlertingSignalId
    
    transition: AlertingStateTransition
    
    timestamp: datetime
    
    # Before/after values (if applicable)
    old_value: Optional[float] = None
    new_value: Optional[float] = None
    
    reason: Optional[str] = None


@dataclass(frozen=True, slots=True)
class AlertingAssessment:
    """
    Canonical assessment output from the AlertingNetwork.
    
    This is an immutable record of the network's analysis. It does NOT command
    behavior - consumers decide what to do with it.
    
    Structure:
        - Assessment identity (for tracing)
        - Signal identity and metadata
        - Core scores (demand, confidence)
        - Classification (level, recommendation)
        - Computed features for explainability
        - Modulation evidence (how context/state affected the score)
        - Reasons for the assessment
        - Provenance tracking
    
    The assessment must never contain:
        - Thread commands
    
    The assessment must never contain:
        - Thread commands
        - Loop decisions
        - Executive authority
        - Action requests
        - Process-control commands
    """
    
    # Assessment identity
    assessment_id: AlertingAssessmentId
    signal_id: AlertingSignalId  # Reference to input
    
    # Signal metadata (copy from input)
    source: AlertingSource
    modality: AlertingModality
    timestamp: datetime  # Original signal timestamp
    
    # Core assessment values
    demand_score: float  # Overall attention demand (0.0 to 1.0)
    confidence: float  # Confidence in the assessment (0.0 to 1.0)
    
    # Classification
    level: AlertingLevel
    recommendation: AlertingRecommendation
    
    # Features for explainability
    features: AlertingFeatures
    
    # Modulation evidence
    modulation: AlertingModulation
    
    # Reasons for the assessment
    reasons: Tuple[AlertingReason, ...]
    
    # State transitions (optional)
    state_transition: Optional[AlertingStateTransition] = None
    
    # Provenance
    provenance: AlertingProvenance