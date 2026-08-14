# Alerting Network Pipeline Implementation - Phase 4.1.5
# =======================================================

"""
Production-quality AlertingNetwork implementation.

This module provides the complete computational pipeline that transforms signals
into advisory attention-demand assessments. It is:

    - Runtime-neutral: No dependency on Core scheduler, timers, or async logic
    - Deterministic: Same inputs produce same outputs given same state
    - Stateful but bounded: Internal state is explicitly managed and limited
    - Thread-safe: No global mutable state, instances are independent

Pipeline Structure:
    
    Input: AlertingInput
    
    ↓ SignalNormalizer (Phase 4.1.5)
        Normalize intensity, background, novelty hints to canonical ranges
    
    ↓ FeatureExtractor (Phase 4.1.3 - features/vector.py, features/analyzers.py)
        Extract change, onset, offset, contrast, temporal, frequency, novelty features
    
    ↓ TemporalAnalyzer (Phase 4.1.5)
        Compute rolling statistics over bounded history window
    
    ↓ BaselineEstimator (Phase 4.1.5)
        Update baseline expectations for deviation detection
    
    ↓ DemandEstimator (Phase 4.1.4 - demand_estimator.py)
        Combine features into demand score with state-based modulation
    
    ↓ ContextModulator (Phase 4.1.5)
        Apply context-based modulation (focus, task criticality, resource pressure)
    
    ↓ HabituationModel (Phase 4.1.2/4.1.5 - states.py)
        Attenuate response due to repeated exposure
    
    ↓ RefractorySuppressionModel (Phase 4.1.5)
        Suppress immediate re-alerts after significant event
    
    ↓ ConfidenceEstimator (Phase 4.1.5)
        Estimate confidence in the assessment based on evidence quality
    
    ↓ AssessmentBuilder (Phase 4.1.1/4.1.2 - models.py)
        Assemble complete AlertingAssessment record
    
    Output: AlertingAssessment

No hidden execution paths.
No implicit state mutation.
Explicit state transitions only.

Public Interface:

    network = AlertingNetwork(config)
    
    assessment = network.assess(
        signals=signals,
        context=context,
        state=state,
    )
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any
from datetime import datetime

# Core imports (Phase 4.1.1 - models)
from gordon_system.src.agent.components.networks.alerting.models import (
    AlertingInput,
    AlertingContext,
    AlertingAssessment,
    AlertingFeatures,
    AlertingModulation,
    AlertingReason,
    AlertingProvenance,
    AlertingNetworkStateSnapshot,
)

# State models (Phase 4.1.2)
from gordon_system.src.agent.components.networks.alerting.states import (
    HabituationState,
    RefractoryState,
    TemporalState,
    NetworkState,
    AlertingBaseline,
)

# Configuration (Phase 4.1.1)
from gordon_system.src.agent.components.networks.alerting.configuration import (
    AlertingNetworkConfig,
)

# Feature extraction (Phase 4.1.3)
from gordon_system.src.agent.components.networks.alerting.features.vector import AlertingFeatureVector
from gordon_system.src.agent.components.networks.alerting.features.analyzers import (
    FeatureAggregator,
    ChangeDetector,
    OnsetDetector,
    OffsetDetector,
    ContrastAnalyzer,
    TemporalStabilityAnalyzer,
    FrequencyAnalyzer,
    PredictionErrorAnalyzer,
    NoveltyAnalyzer,
    UrgencyIndicatorAnalyzer,
)

# Demand estimation (Phase 4.1.4)
from gordon_system.src.agent.components.networks.alerting.demand_estimator import (
    AlertingDemandEstimator,
    EvidenceSummary,
    ModulationSummary,
)

# Constants
from gordon_system.src.agent.components.networks.alerting.constants import (
    MIN_INTENSITY,
    MAX_INTENSITY,
    FEATURE_MIN,
    FEATURE_MAX,
)

# Enums
from gordon_system.src.agent.components.networks.alerting.enums import (
    AlertingLevel,
    AlertingRecommendation,
    AlertingReasonCategory,
)


# =============================================================================
# Signal Normalizer (Phase 4.1.5)
# =============================================================================

class SignalNormalizer:
    """
    Normalize input signals to canonical ranges.
    
    Transforms raw signal values into the [0.0, 1.0] range expected by
    downstream components. No computation decisions - just standardization.
    """

    def __init__(self, config: AlertingNetworkConfig):
        self.config = config

    def normalize(self, input_signal: AlertingInput) -> Dict[str, float]:
        """
        Normalize signal values to canonical ranges.

        Args:
            input_signal: Raw input from caller

        Returns:
            Dictionary of normalized feature-ready values
        """
        result: Dict[str, float] = {}

        # Intensity normalization [0.0, 1.0]
        intensity = input_signal.intensity
        if intensity is not None:
            result["normalized_intensity"] = max(0.0, min(1.0, intensity))
        else:
            result["normalized_intensity"] = 0.0

        # Previous intensity normalization
        prev_intensity = input_signal.previous_intensity
        if prev_intensity is not None:
            result["normalized_prev_intensity"] = max(0.0, min(1.0, prev_intensity))
        else:
            result["normalized_prev_intensity"] = 0.0

        # Background normalization [0.0, 1.0]
        bg = input_signal.background_intensity
        if bg is not None and bg > 0:
            result["normalized_background"] = max(0.01, min(1.0, bg))
        else:
            result["normalized_background"] = 0.5  # Default neutral background

        # Novelty hint normalization [0.0, 1.0]
        novelty = input_signal.novelty_hint
        if novelty is not None:
            result["normalized_novelty"] = max(0.0, min(1.0, novelty))
        else:
            result["normalized_novelty"] = 0.0

        # Urgency hint normalization [0.0, 1.0]
        urgency = input_signal.urgency_hint
        if urgency is not None:
            result["normalized_urgency"] = max(0.0, min(1.0, urgency))
        else:
            result["normalized_urgency"] = 0.0

        # Prediction error normalization [0.0, 1.0]
        pred_error = input_signal.prediction_error
        if pred_error is not None:
            result["normalized_prediction_error"] = max(0.0, min(1.0, pred_error))
        else:
            result["normalized_prediction_error"] = 0.3  # Default uncertainty

        return result


# =============================================================================
# Temporal Analyzer (Phase 4.1.5)
# =============================================================================

class TemporalAnalyzer:
    """
    Analyze temporal characteristics of signal history.
    
    Computes rolling statistics over bounded window for deviation detection
    and pattern analysis.
    """

    def __init__(self, config: AlertingNetworkConfig):
        self.config = config
        self.window_size = config.temporal_detection.baseline_window_size

    def analyze(
        self,
        recent_values: Tuple[float, ...],
        current_timestamp: datetime,
        previous_state: Optional[TemporalState] = None,
    ) -> Tuple[TemporalState, Dict[str, float]]:
        """
        Analyze temporal patterns in recent signals.

        Args:
            recent_values: Recent signal values (chronological order)
            current_timestamp: When current signal was observed
            previous_state: Previous temporal state for continuity

        Returns:
            Tuple of (new_temporal_state, stats_dict)
        """
        # Get bounded history window
        if len(recent_values) > self.window_size:
            values = recent_values[-self.window_size:]
        else:
            values = recent_values

        # Compute rolling statistics
        if len(values) >= 2:
            mean_val = sum(values) / len(values)
            variance = sum((v - mean_val) ** 2 for v in values) / max(1, len(values) - 1)
            std_val = math.sqrt(variance)

            min_val = min(values)
            max_val = max(values)
        else:
            mean_val = values[0] if values else 0.5
            variance = 0.0
            std_val = 0.1
            min_val = mean_val
            max_val = mean_val

        # Create or update temporal state
        new_state = TemporalState(
            _observations=tuple((current_timestamp, v) for v in values),
            rolling_mean=mean_val,
            rolling_std=std_val,
            rolling_min=min_val,
            rolling_max=max_val,
            last_observation_timestamp=current_timestamp,
            last_assessment_timestamp=getattr(previous_state, "last_assessment_timestamp", current_timestamp)
            if previous_state else current_timestamp,
            last_significant_event_timestamp=getattr(previous_state, "last_significant_event_timestamp", None)
            if previous_state else None,
        )

        stats = {
            "rolling_mean": mean_val,
            "rolling_std": std_val,
            "rolling_min": min_val,
            "rolling_max": max_val,
            "observation_count": len(values),
        }

        return new_state, stats


# =============================================================================
# Baseline Estimator (Phase 4.1.5)
# =============================================================================

class BaselineEstimator:
    """
    Estimate and update baseline expectations for deviation detection.
    
    Maintains adaptive baseline that shifts gradually with new observations.
    """

    def __init__(self, config: AlertingNetworkConfig):
        self.config = config
        self.alpha = 0.1  # Adaptation rate (exponential moving average)

    def estimate(
        self,
        current_intensity: float,
        previous_baseline: Optional[AlertingBaseline] = None,
        timestamp: Optional[datetime] = None,
    ) -> Tuple[AlertingBaseline, Dict[str, float]]:
        """
        Estimate new baseline from current observation.

        Args:
            current_intensity: Current signal intensity
            previous_baseline: Previous baseline state
            timestamp: When observation occurred

        Returns:
            Tuple of (new_baseline, stats_dict)
        """
        if previous_baseline is None:
            # Initialize baseline with reasonable defaults
            baseline = AlertingBaseline(
                expected_intensity=current_intensity,
                expected_variance=0.1,
                expected_change_frequency=0.2,
                expected_arrival_interval=5.0,
                observation_count=1,
                last_update_timestamp=timestamp or datetime.utcnow(),
            )
        else:
            # Update existing baseline using exponential moving average
            baseline = previous_baseline.update(current_intensity, timestamp or datetime.utcnow())

        stats = {
            "expected_intensity": baseline.expected_intensity,
            "expected_variance": baseline.expected_variance,
            "deviation": baseline.deviation(current_intensity),
        }

        return baseline, stats


# =============================================================================
# Habituation Model (Phase 4.1.5)
# =============================================================================

class HabituationModel:
    """
    Track and compute habituation state.
    
    Repeated exposure to the same stimulus gradually decreases demand over time.
    This is functional habituation, not neuroscience-based modeling.
    """

    def __init__(self, config: AlertingNetworkConfig):
        self.config = config
        self.decay_rate = config.habituation.decay_rate

    def update(
        self,
        current_state: HabituationState,
        timestamp: datetime,
    ) -> Tuple[HabituationState, float]:
        """
        Update habituation state after observation.

        Args:
            current_state: Current habituation state
            timestamp: When observation occurred

        Returns:
            Tuple of (new_state, attenuation_factor)
        """
        # Record new exposure
        new_state = current_state.record_exposure(timestamp)

        # Apply recovery over time since last exposure
        if current_state.last_exposure_timestamp is not None:
            elapsed = (timestamp - current_state.last_exposure_timestamp).total_seconds()
            recovered = current_state.recover(timestamp)
            
            if hasattr(recovered, 'habituation_coefficient'):
                new_state = HabituationState(
                    exposure_count=new_state.exposure_count,
                    last_exposure_timestamp=timestamp,
                    habituation_coefficient=recovered.habituation_coefficient,
                    recovery_coefficient=new_state.recovery_coefficient,
                )

        # Compute attenuation factor (0.0 to 1.0, where 1.0 = no attenuation)
        attenuation = new_state.habituation_coefficient

        return new_state, attenuation


# =============================================================================
# Refractory Suppression Model (Phase 4.1.5)
# =============================================================================

class RefractorySuppressionModel:
    """
    Implement refractory suppression for immediate re-alerts.
    
    After a significant event, subsequent immediate events are suppressed
    to prevent rapid repeated triggering by the same source.
    """

    def __init__(self, config: AlertingNetworkConfig):
        self.config = config
        self.window_seconds = config.refractory.refractory_period_seconds

    def check_suppression(
        self,
        current_state: RefractoryState,
        timestamp: datetime,
        demand_score: float,
    ) -> Tuple[RefractoryState, float, bool]:
        """
        Check if signal should be suppressed by refractory period.

        Args:
            current_state: Current refractory state
            timestamp: When signal was observed
            demand_score: Computed demand score before suppression

        Returns:
            Tuple of (new_state, suppression_multiplier, is_suppressed)
        """
        # Record new alert event
        new_state = current_state.record_alert(timestamp)

        # Check if within suppression window
        if new_state.is_in_refractory_period:
            multiplier = new_state.suppression_multiplier(timestamp)
            is_suppressed = multiplier < 1.0
        else:
            multiplier = 1.0
            is_suppressed = False

        return new_state, multiplier, is_suppressed


# =============================================================================
# Context Modulator (Phase 4.1.5)
# =============================================================================

class ContextModulator:
    """
    Apply context-based modulation to demand estimate.
    
    Adjusts demand based on external context such as focus strength,
    task criticality, and resource pressure.
    """

    def __init__(self, config: AlertingNetworkConfig):
        self.config = config
        self.focus_weight = config.relevance.focus_strength_weight
        self.task_crit_weight = config.relevance.task_criticality_weight

    def modulate(
        self,
        base_demand: float,
        context: Optional[AlertingContext],
    ) -> Tuple[float, Dict[str, float], Tuple[str, ...]]:
        """
        Apply contextual modulation to demand.

        Args:
            base_demand: Demand score before context modulation
            context: External context for modulation

        Returns:
            Tuple of (modulated_demand, modulation_factors, evidence)
        """
        if context is None:
            return base_demand, {}, ()

        evidence = []
        total_modulation = 0.0

        # Focus strength modulation
        focus_strength = getattr(context, "focus_strength_projection", None)
        if focus_strength is not None:
            # Low focus = higher demand (signal needs attention)
            # High focus = lower demand (focus already allocated)
            mod = (1.0 - focus_strength) * self.focus_weight * base_demand
            total_modulation += mod
            evidence.append(f"focus_mod={mod:.3f}")

        # Task criticality modulation
        task_crit = getattr(context, "task_criticality_projection", None)
        if task_crit is not None:
            # High task criticality increases demand for relevant signals
            mod = task_crit * self.task_crit_weight * base_demand
            total_modulation += mod
            evidence.append(f"task_crit_mod={mod:.3f}")

        # Resource pressure modulation
        res_pressure = getattr(context, "resource_pressure_projection", None)
        if res_pressure is not None:
            mod = res_pressure * 0.1 * base_demand
            total_modulation += mod
            evidence.append(f"res_pressure_mod={mod:.3f}")

        # Apply modulation and clamp
        new_demand = base_demand + total_modulation
        new_demand = max(0.0, min(1.0, new_demand))

        factors = {
            "total_modulation": total_modulation,
            "new_demand": new_demand,
        }

        return new_demand, factors, tuple(evidence)


# =============================================================================
# Confidence Estimator (Phase 4.1.5)
# =============================================================================

class ConfidenceEstimator:
    """
    Estimate confidence in the demand assessment.
    
    Based on feature completeness, consistency, and evidence quality.
    """

    def __init__(self, config: AlertingNetworkConfig):
        self.config = config
        self.min_features_for_high_conf = config.confidence.min_evidence_for_high_confidence

    def estimate(
        self,
        features: AlertingFeatureVector,
        feature_count: int,
        evidence_summary: EvidenceSummary,
    ) -> float:
        """
        Estimate confidence in the demand assessment.

        Args:
            features: Extracted feature vector
            feature_count: Number of valid features
            evidence_summary: Summary of contributing features

        Returns:
            Confidence score [0.0, 1.0]
        """
        # Base confidence from feature completeness
        total_features = len(features.feature_names)
        completeness_ratio = feature_count / max(1, total_features)
        base_confidence = completeness_ratio * 0.7

        # Bonus for good evidence quality
        avg_evidence_conf = evidence_summary.average_confidence if hasattr(evidence_summary, 'average_confidence') else 0.5
        confidence_bonus = avg_evidence_conf * 0.2

        # Small penalty for high uncertainty (low feature count)
        if feature_count < self.min_features_for_high_conf:
            uncertainty_penalty = (self.min_features_for_high_conf - feature_count) / self.min_features_for_high_conf * 0.1
        else:
            uncertainty_penalty = 0.0

        confidence = base_confidence + confidence_bonus - uncertainty_penalty
        return max(0.0, min(1.0, confidence))


# =============================================================================
# Assessment Builder (Phase 4.1.5)
# =============================================================================

class AssessmentBuilder:
    """
    Assemble complete AlertingAssessment from computed components.
    
    Final step in the pipeline - combines all results into output record.
    """

    def __init__(self, config: AlertingNetworkConfig):
        self.config = config

    def build(
        self,
        assessment_id: str,
        signal_id: str,
        source: Any,
        modality: Any,
        timestamp: datetime,
        demand_score: float,
        confidence: float,
        features: AlertingFeatures,
        modulation: AlertingModulation,
        reasons: Tuple[AlertingReason, ...],
    ) -> AlertingAssessment:
        """
        Build final assessment record.

        Args:
            assessment_id: Unique identifier for this assessment
            signal_id: Reference to input signal
            source: Signal source
            modality: Signal modality
            timestamp: When signal was observed
            demand_score: Computed attention demand
            confidence: Confidence in the assessment
            features: Computed feature values
            modulation: Modulation evidence
            reasons: List of reasons for the assessment

        Returns:
            Complete AlertingAssessment record
        """
        # Classify level from demand score
        if demand_score < self.config.classification.low_threshold:
            level = AlertingLevel.NEGLIGIBLE
        elif demand_score < self.config.classification.moderate_threshold:
            level = AlertingLevel.LOW
        elif demand_score < self.config.classification.high_threshold:
            level = AlertingLevel.MODERATE
        elif demand_score < self.config.classification.critical_threshold:
            level = AlertingLevel.HIGH
        else:
            level = AlertingLevel.CRITICAL

        # Generate recommendation based on level and confidence
        if level in (AlertingLevel.HIGH, AlertingLevel.CRITICAL):
            recommendation = AlertingRecommendation.REQUEST_URGENT_ATTENTION
        elif level == AlertingLevel.MODERATE:
            recommendation = AlertingRecommendation.REQUEST_ATTENTION
        elif level == AlertingLevel.LOW:
            recommendation = AlertingRecommendation.OBSERVE
        else:
            recommendation = AlertingRecommendation.IGNORE

        provenance = AlertingProvenance(
            input_source=source if hasattr(source, 'value') else source,
            processed_at=timestamp,
            config_version="4.1.5",
            seed_hash=None,
            caller_id=None,
        )

        return AlertingAssessment(
            assessment_id=assessment_id,
            signal_id=signal_id,
            source=source if hasattr(source, 'value') else source,
            modality=modality if hasattr(modality, 'value') else modality,
            timestamp=timestamp,
            demand_score=demand_score,
            confidence=confidence,
            level=level,
            recommendation=recommendation,
            features=features,
            modulation=modulation,
            reasons=reasons,
            state_transition=None,
            provenance=provenance,
        )


# =============================================================================
# AlertingNetwork - Main Pipeline Entry Point (Phase 4.1.5)
# =============================================================================

class AlertingNetwork:
    """
    Complete AlertingNetwork pipeline implementation.

    This is the canonical entry point for assessing exogenous attention demand.
    It implements the full computational pipeline:

        Input → Normalizer → Extractor → Analyzer → Estimator → 
        Modulator → Habituation → Refractory → Confidence → Assessment

    Public API:
        assess() - Main assessment method
        snapshot_state() - Get current internal state
        reset() - Reset to clean state

    No side effects.
    Deterministic behavior.
    Bounded state management.
    """

    def __init__(self, config: Optional[AlertingNetworkConfig] = None):
        """
        Initialize the AlertingNetwork.

        Args:
            config: Configuration (uses defaults if None)
        """
        self.config = config or AlertingNetworkConfig()

        # Initialize pipeline components
        self._normalizer = SignalNormalizer(self.config)
        self._temporal_analyzer = TemporalAnalyzer(self.config)
        self._baseline_estimator = BaselineEstimator(self.config)
        self._habituation_model = HabituationModel(self.config)
        self._refractory_model = RefractorySuppressionModel(self.config)
        self._context_modulator = ContextModulator(self.config)
        self._confidence_estimator = ConfidenceEstimator(self.config)

        # Demand estimator is Phase 4.1.4 implementation
        self._demand_estimator = AlertingDemandEstimator(
            config=self.config,
        )

        # Assessment builder
        self._builder = AssessmentBuilder(self.config)

        # Internal state (Phase 4.1.2)
        self._signal_history: Tuple[AlertingInput, ...] = ()
        self._baseline: Optional[AlertingBaseline] = None
        self._habituation_state: HabituationState = HabituationState()
        self._refractory_state: RefractoryState = RefractoryState()
        self._temporal_state: TemporalState = TemporalState()

        # Counters for diagnostics
        self._total_assessments = 0

    def assess(
        self,
        alerting_input: AlertingInput,
        context: Optional[AlertingContext] = None,
        state_override: Optional[Dict[str, Any]] = None,
    ) -> AlertingAssessment:
        """
        Assess exogenous attention demand for a signal.

        Pipeline execution:
            1. Signal normalization
            2. Feature extraction
            3. Temporal analysis
            4. Baseline estimation
            5. Demand computation with state-based modulation
            6. Context modulation
            7. Habituation attenuation
            8. Refractory suppression
            9. Confidence estimation
            10. Assessment assembly

        Args:
            alerting_input: Signal to assess
            context: Optional external context for modulation
            state_override: Optional state overrides for testing/debugging

        Returns:
            Complete AlertingAssessment record

        Note:
            This method is pure - it does not mutate the input signal or
            context. It only updates internal network state.
        """
        timestamp = alerting_input.timestamp
        signal_id = alerting_input.signal_id

        # 1. Normalize signal to canonical ranges
        normalized = self._normalizer.normalize(alerting_input)

        # 2. Extract features using analyzers
        feature_vector, extracted_features = self._extract_features(
            normalized,
            timestamp,
            signal_id,
        )

        # 3. Temporal analysis
        recent_values = tuple(
            getattr(feature_vector, name, 0.0)
            for name in ["absolute_change", "relative_change", "rate_of_change"]
            if hasattr(feature_vector, name)
        )
        self._temporal_state, temporal_stats = self._temporal_analyzer.analyze(
            recent_values,
            timestamp,
            self._temporal_state,
        )

        # 4. Baseline estimation
        current_intensity = normalized.get("normalized_intensity", 0.5)
        self._baseline, baseline_stats = self._baseline_estimator.estimate(
            current_intensity,
            self._baseline,
            timestamp,
        )

        # 5. Compute demand with state-based modulation (Phase 4.1.4)
        base_demand, confidence, evidence_summary, modulation_summary = (
            self._demand_estimator.compute_demand(
                feature_vector,
                context,
                self._habituation_state,
                self._refractory_state,
            )
        )

        # 6. Apply context modulation
        contextual_demand, context_factors, context_evidence = self._context_modulator.modulate(
            base_demand,
            context,
        )

        # 7. Apply habituation attenuation
        new_habituation, habituation_attenuation = self._habituation_model.update(
            self._habituation_state,
            timestamp,
        )
        habituated_demand = contextual_demand * habituation_attenuation

        # 8. Apply refractory suppression
        new_refractory, refractory_multiplier, is_suppressed = self._refractory_model.check_suppression(
            self._refractory_state,
            timestamp,
            habituated_demand,
        )
        final_demand = habituated_demand * refractory_multiplier

        # 9. Estimate confidence
        feature_count = sum(
            1 for name in feature_vector.feature_names
            if getattr(feature_vector, name, None) is not None and feature_vector.is_valid(name)
        )
        confidence = self._confidence_estimator.estimate(
            feature_vector,
            feature_count,
            evidence_summary,
        )

        # 10. Build final assessment
        assessment_features = AlertingFeatures(
            intensity=current_intensity,
            delta_intensity=feature_vector.absolute_change,
            normalized_change=feature_vector.relative_change,
            onset_strength=feature_vector.onset_appearance,
            offset_strength=feature_vector.offset_termination,
            novelty=feature_vector.baseline_deviation,
            prediction_error=feature_vector.prediction_error_estimate,
            urgency=final_demand * 0.8,
            contrast=feature_vector.local_contrast,
            biological_relevance=0.3,
            pattern_violation=feature_vector.oscillation,
            unexpected_onset=float(alerting_input.onset or False),
            unexpected_offset=float(alerting_input.offset or False),
            habituation=max(0.0, 1.0 - habituation_attenuation),
            refractory_attenuation=max(0.0, 1.0 - refractory_multiplier),
        )

        assessment_modulation = AlertingModulation(
            positive_modulation=context_factors.get("total_modulation", 0.0) if context_factors else 0.0,
            negative_modulation=habituation_attenuation + (1 - refractory_multiplier),
            focus_modulation=context_factors.get("focus_modulation", 0.0) if context_factors else 0.0,
            task_criticality_modulation=context_factors.get("task_crit_modulation", 0.0) if context_factors else 0.0,
            cognitive_load_modulation=0.0,
            habituation_modulation=habituation_attenuation,
            refractory_modulation=1 - refractory_multiplier,
        )

        reasons = tuple(
            AlertingReason(
                code="BASELINE_ASSESSMENT",
                category=AlertingReasonCategory.PREDICTION_ERROR
                if not context_evidence else AlertingReasonCategory.CONTEXTUAL_RELEVANCE,
                description=f"Assessment based on signal characteristics with demand={final_demand:.3f}",
                contribution=1.0,
                confidence=confidence,
                evidence_reference=f"demand_score={final_demand:.3f}",
            ),
        )

        assessment = self._builder.build(
            assessment_id=f"assessment_{signal_id}",
            signal_id=signal_id,
            source=alerting_input.source,
            modality=alerting_input.modality,
            timestamp=timestamp,
            demand_score=max(0.0, min(1.0, final_demand)),
            confidence=max(0.0, min(1.0, confidence)),
            features=assessment_features,
            modulation=assessment_modulation,
            reasons=reasons,
        )

        # Update internal state for next assessment
        self._signal_history = self._signal_history + (alerting_input,)
        self._baseline = baseline_stats.get("updated_baseline", self._baseline)
        self._habituation_state = new_habituation
        self._refractory_state = new_refractory
        self._total_assessments += 1

        return assessment

    def _extract_features(
        self,
        normalized: Dict[str, float],
        timestamp: datetime,
        signal_id: str,
    ) -> Tuple[AlertingFeatureVector, Dict[str, Any]]:
        """
        Extract features from normalized signal values.

        Args:
            normalized: Normalized signal values
            timestamp: When observation occurred
            signal_id: Reference to input signal

        Returns:
            Tuple of (feature_vector, extracted_features_dict)
        """
        # Use feature aggregators to extract features
        aggregator = FeatureAggregator(
            vector_id=signal_id,
            extraction_timestamp=timestamp,
        )

        # Extract change features
        current_val = normalized.get("normalized_intensity", 0.5)
        prev_val = normalized.get("normalized_prev_intensity", 0.0)

        change_detector = ChangeDetector(
            current_value=current_val,
            previous_value=prev_val if prev_val > 0 else None,
            baseline_value=0.5,
        )
        change_features = change_detector.analyze()

        # Extract onset features
        onset_detector = OnsetDetector(
            current_value=current_val,
            previous_value=prev_val if prev_val > 0 else None,
            threshold=0.3,
        )
        onset_features = onset_detector.analyze()

        # Extract offset features
        offset_detector = OffsetDetector(
            current_value=current_val,
            previous_value=prev_val if prev_val > 0 else None,
            threshold=0.3,
        )
        offset_features = offset_detector.analyze()

        # Extract contrast features
        background_val = normalized.get("normalized_background", 0.5)
        contrast_analyzer = ContrastAnalyzer(
            current_value=current_val,
            background_value=background_val if background_val > 0 else None,
            recent_values=(prev_val,) if prev_val > 0 else (),
        )
        contrast_features = contrast_analyzer.analyze()

        # Extract temporal stability features
        temp_stability = TemporalStabilityAnalyzer(
            recent_values=(current_val, prev_val) if prev_val > 0 else (current_val,),
            baseline_mean=0.5,
            window_size=5,
        )
        temporal_features = temp_stability.analyze()

        # Extract frequency features
        freq_analyzer = FrequencyAnalyzer()
        frequency_features = freq_analyzer.analyze()

        # Extract prediction error
        pred_error = normalized.get("normalized_prediction_error", 0.3)
        pred_analyzer = PredictionErrorAnalyzer(
            expected_value=0.5,
            observed_value=current_val,
            expected_variance=0.1,
        )
        prediction_features = pred_analyzer.analyze()

        # Extract novelty features
        novelty_analyzer = NoveltyAnalyzer(
            current_value=current_val,
            baseline_mean=0.5,
            historical_mean=prev_val if prev_val > 0 else None,
            recent_context_mean=None,
            baseline_std=0.1,
        )
        novelty_features = novelty_analyzer.analyze()

        # Extract urgency features
        urgency_indicator = UrgencyIndicatorAnalyzer(
            current_value=current_val,
            previous_value=prev_val if prev_val > 0 else None,
            rate_of_change=change_features.get("rate_of_change", 0.0),
        )
        urgency_features = urgency_indicator.analyze()

        # Context projection (external)
        context_projection = {"task_criticality_projection": None, "focus_strength_projection": None}

        # Aggregate all features
        feature_vector = aggregator.aggregate(
            change_features=change_features,
            onset_features=onset_features,
            offset_features=offset_features,
            contrast_features=contrast_features,
            temporal_features=temporal_features,
            frequency_features=frequency_features,
            prediction_features=prediction_features,
            novelty_features=novelty_features,
            urgency_features=urgency_features,
            context_features=context_projection,
        )

        extracted = {
            "current_intensity": current_val,
            "prev_intensity": prev_val,
            "baseline_value": 0.5,
        }

        return feature_vector, extracted

    def snapshot_state(self) -> AlertingNetworkStateSnapshot:
        """
        Produce immutable snapshot of network's internal state.

        Returns:
            AlertingNetworkStateSnapshot with bounded computational state
        """
        # Compute recent baseline statistics from history
        if self._signal_history:
            intensities = tuple(
                getattr(s, "intensity", 0.5) for s in self._signal_history
            )
            recent_baseline_mean = sum(intensities) / len(intensities)
            variance = sum((i - recent_baseline_mean) ** 2 for i in intensities) / max(1, len(intensities) - 1)
            recent_baseline_std = math.sqrt(variance)
        else:
            recent_baseline_mean = None
            recent_baseline_std = None

        return AlertingNetworkStateSnapshot(
            recent_baseline_mean=recent_baseline_mean,
            recent_baseline_std=recent_baseline_std,
            recent_signals_count=len(self._signal_history),
            last_signal_timestamp=self._signal_history[-1].timestamp if self._signal_history else None,
            habituation_level=self._habituation_state.habituation_coefficient,
            refractory_remaining=max(0.0, 2.0 - (datetime.utcnow() - self._refractory_state.last_alert).total_seconds()
                                     if self._refractory_state.last_alert else 0.0),
            assessment_count=self._total_assessments,
            total_demand_score=0.0,  # Could track cumulative demand if needed
        )

    def reset(self, full_reset: bool = False) -> AlertingNetworkStateSnapshot:
        """
        Reset network to clean state.

        Args:
            full_reset: If True, reset all state including history

        Returns:
            Fresh state snapshot after reset
        """
        self._signal_history = () if full_reset else self._signal_history
        self._baseline = None if full_reset else self._baseline
        self._habituation_state = HabituationState() if full_reset else self._habituation_state
        self._refractory_state = RefractoryState() if full_reset else self._refractory_state
        self._temporal_state = TemporalState() if full_reset else self._temporal_state

        return self.snapshot_state()