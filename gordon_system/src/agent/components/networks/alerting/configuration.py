# Alerting Network Configuration
# ==============================

"""
Immutable configuration for the AlertingNetwork.

Configuration is organized into nested value objects rather than one flat bag.
This phase creates the structure; later phases populate computational fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProjectionConfig:
    """
    Configuration for input projection and normalization.
    
    These settings control how raw signal evidence is transformed into
    canonical alerting projections.
    """
    
    # Normalization bounds
    min_intensity: float = 0.0
    max_intensity: float = 1.0
    
    # Change detection thresholds
    minimum_delta_for_change: float = 0.1
    
    # Onset/offset sensitivity
    onset_rising_threshold: float = 0.3
    offset_falling_threshold: float = 0.3


@dataclass(frozen=True)
class TemporalDetectionConfig:
    """
    Configuration for temporal signal change detection.
    
    These parameters control how sudden changes, novelty, and deviation are
    detected from sequential signals.
    """
    
    # Baseline computation
    baseline_window_size: int = 10
    
    # Change sensitivity
    minimum_significant_delta: float = 0.15
    
    # Predictive error handling
    prediction_error_weight: float = 1.0


@dataclass(frozen=True)
class NoveltyConfig:
    """
    Configuration for novelty detection.
    
    How deviations from recent baseline are interpreted as novelty.
    """
    
    # Deviation thresholds
    minor_deviation_threshold: float = 0.2
    major_deviation_threshold: float = 0.4
    
    # Expiration of learned patterns
    pattern_expiry_time_seconds: float = 300.0


@dataclass(frozen=True)
class UrgencyConfig:
    """
    Configuration for urgency estimation.
    
    How time-sensitive demand is assessed from signal characteristics.
    """
    
    # Rate-of-change sensitivity
    rapid_change_threshold: float = 0.5
    
    # Decay rate for urgency
    urgency_half_life_seconds: float = 10.0
    
    # Maximum urgency contribution to overall score
    max_urgency_contribution: float = 0.3


@dataclass(frozen=True)
class PredictionErrorConfig:
    """
    Configuration for prediction error handling.
    
    How prediction errors from predictive networks influence alert demand.
    """
    
    # Prediction error scaling
    error_scale_factor: float = 1.5
    
    # Error decay rate
    prediction_error_decay_rate: float = 0.9


@dataclass(frozen=True)
class RelevanceConfig:
    """
    Configuration for relevance assessment.
    
    How context and external hints influence demand estimation.
    """
    
    # Context hint weights
    focus_strength_weight: float = 0.2
    task_criticality_weight: float = 0.3
    
    # Modulation bounds
    max_context_modulation: float = 0.25


@dataclass(frozen=True)
class HabituationConfig:
    """
    Configuration for habituation state.
    
    How response attenuation occurs with repeated exposure to the same signal.
    """
    
    # Decay rate for habituation
    decay_rate: float = 0.95
    
    # Saturation level
    max_habituation: float = 1.0
    
    # Recovery time (seconds)
    recovery_time_seconds: float = 60.0


@dataclass(frozen=True)
class RefractoryConfig:
    """
    Configuration for refractory state.
    
    How the network resists immediate re-alerting after a recent alert.
    """
    
    # Refractory period duration
    refractory_period_seconds: float = 2.0
    
    # Attenuation during refractory
    attenuation_factor: float = 0.5


@dataclass(frozen=True)
class DemandCompositionConfig:
    """
    Configuration for combining features into a demand score.
    
    This determines how raw feature estimates become an overall assessment.
    """
    
    # Feature weights (normalized internally)
    intensity_weight: float = 0.2
    novelty_weight: float = 0.15
    prediction_error_weight: float = 0.15
    urgency_weight: float = 0.2
    contrast_weight: float = 0.1
    
    # State-based attenuation weights
    habituation_weight: float = 0.1
    refractory_weight: float = 0.1


@dataclass(frozen=True)
class ConfidenceConfig:
    """
    Configuration for confidence estimation.
    
    How the network estimates its own assessment confidence.
    """
    
    # Minimum evidence requirements
    min_evidence_for_high_confidence: int = 2
    
    # Uncertainty penalties
    uncertainty_penalty_per_missing_feature: float = 0.05


@dataclass(frozen=True)
class ClassificationConfig:
    """
    Configuration for alert level classification.
    
    Threshold boundaries between NEGLIGIBLE, LOW, MODERATE, HIGH, CRITICAL.
    """
    
    # Level thresholds (demand_score -> AlertingLevel)
    low_threshold: float = 0.1
    moderate_threshold: float = 0.3
    high_threshold: float = 0.5
    critical_threshold: float = 0.8


@dataclass(frozen=True)
class CapacityConfig:
    """
    Configuration for state capacity limits.
    
    Ensures bounded memory and prevents unbounded growth.
    """
    
    # Signal history limit (bounded)
    max_signal_history: int = 100
    
    # Baseline window size
    baseline_window_size: int = 50


@dataclass(frozen=True)
class DiagnosticsConfig:
    """
    Configuration for diagnostic and observability output.
    
    What to record for debugging, testing, and monitoring.
    """
    
    # Record level
    enable_feature_recording: bool = False
    enable_modulation_recording: bool = True
    enable_state_transitions: bool = True


@dataclass(frozen=True)
class AlertingNetworkConfig:
    """
    Immutable configuration for AlertingNetwork.
    
    Organized as nested value objects. All fields have sensible defaults.
    The network rejects any configuration that fails validation.
    
    This is the main configuration entry point for users of AlertingNetwork.
    """
    
    projection: ProjectionConfig = field(default_factory=ProjectionConfig)
    temporal_detection: TemporalDetectionConfig = field(
        default_factory=TemporalDetectionConfig
    )
    novelty: NoveltyConfig = field(default_factory=NoveltyConfig)
    urgency: UrgencyConfig = field(default_factory=UrgencyConfig)
    prediction_error: PredictionErrorConfig = field(
        default_factory=PredictionErrorConfig
    )
    relevance: RelevanceConfig = field(default_factory=RelevanceConfig)
    habituation: HabituationConfig = field(default_factory=HabituationConfig)
    refractory: RefractoryConfig = field(default_factory=RefractoryConfig)
    demand_composition: DemandCompositionConfig = field(
        default_factory=DemandCompositionConfig
    )
    confidence: ConfidenceConfig = field(default_factory=ConfidenceConfig)
    classification: ClassificationConfig = field(
        default_factory=ClassificationConfig
    )
    capacity: CapacityConfig = field(default_factory=CapacityConfig)
    diagnostics: DiagnosticsConfig = field(default_factory=DiagnosticsConfig)