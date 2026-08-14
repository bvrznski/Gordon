# Feature Extractors for Alerting Network Phase 4.1.3
# =====================================================

"""
Feature extraction analyzers that transform raw AlertingSignals into structured features.

Architecture:
    - Each analyzer performs exactly one type of analysis
    - All analyzers are independently replaceable
    - No behavioral decisions or attention demand estimation
    - Pure deterministic feature extraction using bounded state (Phase 4.1.2)
    
Feature Families:
    - Change Detection: absolute change, relative change, rate of change, acceleration
    - Onset Detection: appearance, activation, emergence
    - Offset Detection: termination, disappearance, cessation
    - Contrast Detection: local contrast, background contrast, context contrast
    - Temporal Stability: variance, oscillation, consistency, drift
    - Frequency Analysis: event frequency, periodicity, burstiness
    - Prediction Error: expected signal vs observed signal deviation
    - Novelty: deviation from baseline, history, recent context
    - Urgency Indicators: rapid escalation, critical thresholds, time-sensitive transitions

Usage:
    Each analyzer has a static analyze() method that takes:
        - Signal: The AlertingSignal to analyze
        - Baseline: Optional AlertingBaseline for comparison
        - TemporalState: Optional TemporalState for rolling statistics
    
    Returns:
        Feature values (normalized 0.0-1.0 where applicable) with metadata
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


# =============================================================================
# Analyzer Base Interface
# =============================================================================


class FeatureAnalyzer:
    """Base class for all feature analyzers."""
    
    def analyze(self) -> dict:
        """
        Analyze a signal and return feature values.
        
        Returns:
            Dictionary of feature_name: value pairs
        """
        raise NotImplementedError


# =============================================================================
# Change Detection Analyzer
# =============================================================================

class ChangeDetector(FeatureAnalyzer):
    """
    Detects and quantifies changes in signal intensity over time.
    
    Measures:
        - absolute_change: |current - previous|
        - relative_change: (current - previous) / baseline
        - rate_of_change: absolute_change / time_delta
        - acceleration: change_in_rate / time_delta
    """
    
    def __init__(
        self,
        current_value: float,
        previous_value: Optional[float] = None,
        baseline_value: Optional[float] = None,
        time_delta_seconds: Optional[float] = None,
    ):
        """
        Initialize change detector.
        
        Args:
            current_value: Current signal value (0.0 to 1.0)
            previous_value: Previous signal value, or None if unavailable
            baseline_value: Expected baseline value for comparison
            time_delta_seconds: Time elapsed since last measurement
        """
        self.current_value = max(0.0, min(1.0, current_value))
        self.previous_value = previous_value
        self.baseline_value = baseline_value
        self.time_delta_seconds = time_delta_seconds
    
    def analyze(self) -> dict:
        """Perform change detection analysis."""
        result = {
            "absolute_change": 0.0,
            "relative_change": 0.0,
            "rate_of_change": 0.0,
            "acceleration": 0.0,
        }
        
        # Absolute change
        if self.previous_value is not None:
            result["absolute_change"] = abs(self.current_value - self.previous_value)
            
            # Relative change
            baseline = self.baseline_value if self.baseline_value is not None else 1.0
            result["relative_change"] = (
                abs(self.current_value - self.previous_value) / max(0.01, baseline)
            )
            
            # Rate of change (per second)
            if self.time_delta_seconds and self.time_delta_seconds > 0:
                result["rate_of_change"] = (
                    result["absolute_change"] / self.time_delta_seconds
                )
        
        return result


# =============================================================================
# Onset Detection Analyzer
# =============================================================================

class OnsetDetector(FeatureAnalyzer):
    """
    Detects signal onset events (appearance, activation, emergence).
    
    Measures:
        - onset_appearance: Evidence of sudden appearance from zero/low state
        - onset_activation: Evidence of activation event
        - onset_emergence: Evidence of emerging from background
    """
    
    def __init__(
        self,
        current_value: float,
        previous_value: Optional[float] = None,
        baseline_value: Optional[float] = None,
        threshold: float = 0.3,  # Threshold for significant change
    ):
        """
        Initialize onset detector.
        
        Args:
            current_value: Current signal value (0.0 to 1.0)
            previous_value: Previous signal value, or None if unavailable
            baseline_value: Expected baseline before onset
            threshold: Minimum relative change to qualify as onset
        """
        self.current_value = max(0.0, min(1.0, current_value))
        self.previous_value = previous_value
        self.baseline_value = baseline_value
        self.threshold = threshold
    
    def analyze(self) -> dict:
        """Perform onset detection analysis."""
        result = {
            "onset_appearance": 0.0,
            "onset_activation": 0.0,
            "onset_emergence": 0.0,
        }
        
        if self.previous_value is None:
            # First observation - assume potential appearance
            result["onset_appearance"] = min(1.0, self.current_value)
            return result
        
        # Absolute change from previous
        delta = self.current_value - self.previous_value
        
        # Appearance: significant increase from low state
        if delta > 0 and self.previous_value < 0.2:
            result["onset_appearance"] = min(1.0, delta / max(0.01, self.threshold))
        
        # Activation: transition from zero/negligible to active
        if self.previous_value < 0.1 and self.current_value > 0.3:
            result["onset_activation"] = 1.0
        
        # Emergence: rising from baseline context
        if self.baseline_value is not None:
            emergence_delta = self.current_value - self.baseline_value
            if emergence_delta > 0:
                result["onset_emergence"] = min(
                    1.0, emergence_delta / max(0.01, self.threshold)
                )
        
        return result


# =============================================================================
# Offset Detection Analyzer
# =============================================================================

class OffsetDetector(FeatureAnalyzer):
    """
    Detects signal offset events (termination, disappearance, cessation).
    
    Measures:
        - offset_termination: Evidence of termination event
        - offset_disappearance: Evidence of signal disappearing
        - offset_cessation: Evidence of cessation from active state
    """
    
    def __init__(
        self,
        current_value: float,
        previous_value: Optional[float] = None,
        baseline_value: Optional[float] = None,
        threshold: float = 0.3,
    ):
        """Initialize offset detector."""
        self.current_value = max(0.0, min(1.0, current_value))
        self.previous_value = previous_value
        self.baseline_value = baseline_value
        self.threshold = threshold
    
    def analyze(self) -> dict:
        """Perform offset detection analysis."""
        result = {
            "offset_termination": 0.0,
            "offset_disappearance": 0.0,
            "offset_cessation": 0.0,
        }
        
        if self.previous_value is None:
            return result
        
        delta = self.current_value - self.previous_value
        
        # Termination: significant decrease
        if delta < 0 and abs(delta) > self.threshold:
            result["offset_termination"] = min(1.0, abs(delta) / max(0.01, self.threshold))
        
        # Disappearance: falling to near-zero from active state
        if self.previous_value > 0.3 and self.current_value < 0.1:
            result["offset_disappearance"] = 1.0
        
        # Cessation: falling from active state toward baseline
        if self.baseline_value is not None:
            cessation_delta = self.current_value - self.baseline_value
            if cessation_delta < 0 and abs(cessation_delta) > self.threshold:
                result["offset_cessation"] = min(
                    1.0, abs(cessation_delta) / max(0.01, self.threshold)
                )
        
        return result


# =============================================================================
# Contrast Detection Analyzer
# =============================================================================

class ContrastAnalyzer(FeatureAnalyzer):
    """
    Detects contrast between signal and background/context.
    
    Measures:
        - local_contrast: Signal strength relative to nearby context
        - background_contrast: Signal vs estimated background level
        - context_contrast: Signal vs surrounding temporal context
    """
    
    def __init__(
        self,
        current_value: float,
        background_value: Optional[float] = None,
        recent_values: Tuple[float, ...] = (),
        min_background: float = 0.1,
    ):
        """Initialize contrast analyzer."""
        self.current_value = max(0.0, min(1.0, current_value))
        self.background_value = background_value
        self.recent_values = recent_values
        self.min_background = min_background
    
    def analyze(self) -> dict:
        """Perform contrast detection analysis."""
        result = {
            "local_contrast": 0.0,
            "background_contrast": 0.0,
            "context_contrast": 0.0,
        }
        
        # Local contrast: raw signal strength
        result["local_contrast"] = self.current_value
        
        # Background contrast
        if self.background_value is not None:
            bg = max(self.min_background, self.background_value)
            diff = abs(self.current_value - bg)
            result["background_contrast"] = min(1.0, diff / max(0.01, bg))
        
        # Context contrast: compare to recent mean
        if self.recent_values:
            recent_mean = sum(self.recent_values) / len(self.recent_values)
            diff = abs(self.current_value - recent_mean)
            result["context_contrast"] = min(1.0, diff / max(0.01, recent_mean))
        
        return result


# =============================================================================
# Temporal Stability Analyzer
# =============================================================================

class TemporalStabilityAnalyzer(FeatureAnalyzer):
    """
    Analyzes temporal stability characteristics of the signal.
    
    Measures:
        - variance: Signal variance over recent window
        - oscillation: Oscillation pattern strength (0.0 to 1.0)
        - consistency: Consistency with expected behavior
        - drift: Gradual directional shift
    """
    
    def __init__(
        self,
        recent_values: Tuple[float, ...] = (),
        baseline_mean: Optional[float] = None,
        window_size: int = 5,
    ):
        """Initialize temporal stability analyzer."""
        self.recent_values = recent_values
        self.baseline_mean = baseline_mean
        self.window_size = window_size
    
    def analyze(self) -> dict:
        """Perform temporal stability analysis."""
        result = {
            "variance": 0.0,
            "oscillation": 0.0,
            "consistency": 1.0,
            "drift": 0.0,
        }
        
        values = list(self.recent_values)
        
        if len(values) < 2:
            return result
        
        # Variance calculation
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / max(1, len(values) - 1)
        result["variance"] = min(1.0, variance * 4)  # Scale to [0, 1]
        
        # Oscillation: count zero-crossings
        if len(values) >= 3:
            crossings = sum(
                1 for i in range(len(values) - 1)
                if (values[i] - mean) * (values[i + 1] - mean) < 0
            )
            result["oscillation"] = min(1.0, crossings / max(1, len(values) - 2))
        
        # Consistency: how close recent values are to baseline
        if self.baseline_mean is not None:
            deviations = [abs(v - self.baseline_mean) for v in values]
            avg_deviation = sum(deviations) / len(deviations)
            result["consistency"] = max(0.0, 1.0 - avg_deviation * 2)
        
        # Drift: directional bias in recent trend
        if len(values) >= 3:
            # Simple linear trend estimation
            n = len(values)
            x_mean = (n - 1) / 2
            slope_num = sum((i - x_mean) * values[i] for i in range(n))
            slope_denom = sum((i - x_mean) ** 2 for i in range(n))
            if slope_denom > 0:
                slope = slope_num / slope_denom
                result["drift"] = min(1.0, abs(slope) * 10)
        
        return result


# =============================================================================
# Frequency Analysis Analyzer
# =============================================================================

class FrequencyAnalyzer(FeatureAnalyzer):
    """
    Analyzes frequency characteristics of signal events.
    
    Measures:
        - event_frequency: Events per unit time
        - periodicity: Regularity of pattern (0.0 to 1.0)
        - burstiness: Clustered event density
    """
    
    def __init__(
        self,
        recent_events: Tuple[datetime, ...] = (),
        window_seconds: float = 60.0,
        min_interval: float = 0.1,
    ):
        """Initialize frequency analyzer."""
        self.recent_events = recent_events
        self.window_seconds = window_seconds
        self.min_interval = min_interval
    
    def analyze(self) -> dict:
        """Perform frequency analysis."""
        result = {
            "event_frequency": 0.0,
            "periodicity": 0.0,
            "burstiness": 0.0,
        }
        
        if not self.recent_events:
            return result
        
        # Sort events chronologically
        sorted_events = sorted(self.recent_events)
        n = len(sorted_events)
        
        # Event frequency (events per second)
        if n >= 2:
            first, last = sorted_events[0], sorted_events[-1]
            elapsed = max(0.01, (last - first).total_seconds())
            result["event_frequency"] = min(1.0, n / max(self.window_seconds, elapsed))
        
        # Periodicity: compute intervals and check regularity
        if n >= 3:
            intervals = [
                (sorted_events[i + 1] - sorted_events[i]).total_seconds()
                for i in range(n - 1)
            ]
            
            mean_interval = sum(intervals) / len(intervals)
            if mean_interval > 0:
                variance = sum((i - mean_interval) ** 2 for i in intervals) / n
                std_dev = variance ** 0.5
                
                # Regularity = inverse of coefficient of variation
                cv = std_dev / mean_interval if mean_interval > 0 else float('inf')
                result["periodicity"] = max(0.0, min(1.0, 1.0 - min(cv, 1.0)))
        
        # Burstiness: ratio of events in short intervals to total
        burst_intervals = [i for i in intervals if i < self.min_interval]
        if n > 1:
            result["burstiness"] = min(1.0, len(burst_intervals) / max(1, n - 1))
        
        return result


# =============================================================================
# Prediction Error Analyzer
# =============================================================================

class PredictionErrorAnalyzer(FeatureAnalyzer):
    """
    Computes prediction error between expected and observed signals.
    
    Compares:
        - Expected signal value (from baseline/model)
        - Observed signal value
        
    Produces:
        - prediction_error_estimate: Deviation normalized to [0.0, 1.0]
    """
    
    def __init__(
        self,
        expected_value: Optional[float] = None,
        observed_value: float = 0.0,
        expected_variance: float = 0.1,
    ):
        """Initialize prediction error analyzer."""
        self.expected_value = expected_value
        self.observed_value = max(0.0, min(1.0, observed_value))
        self.expected_variance = max(0.01, expected_variance)
    
    def analyze(self) -> dict:
        """Perform prediction error analysis."""
        result = {
            "prediction_error_estimate": 0.0,
        }
        
        if self.expected_value is None:
            return result
        
        # Compute z-score normalized to [0, 1]
        difference = abs(self.observed_value - self.expected_value)
        z_score = difference / max(0.01, self.expected_variance ** 0.5)
        
        # Normalize to [0, 1] using sigmoid-like scaling
        result["prediction_error_estimate"] = min(1.0, z_score / 3.0)
        
        return result


# =============================================================================
# Novelty Analyzer
# =============================================================================

class NoveltyAnalyzer(FeatureAnalyzer):
    """
    Measures deviation from historical patterns.
    
    Novelty is descriptive - not behavioral.
    
    Measures deviation from:
        - baseline: Expected values
        - history: Recent signal patterns  
        - recent context: Short-term temporal context
    """
    
    def __init__(
        self,
        current_value: float,
        baseline_mean: Optional[float] = None,
        historical_mean: Optional[float] = None,
        recent_context_mean: Optional[float] = None,
        baseline_std: Optional[float] = None,
    ):
        """Initialize novelty analyzer."""
        self.current_value = max(0.0, min(1.0, current_value))
        self.baseline_mean = baseline_mean
        self.historical_mean = historical_mean
        self.recent_context_mean = recent_context_mean
        self.baseline_std = baseline_std or 0.1
    
    def analyze(self) -> dict:
        """Perform novelty analysis."""
        result = {
            "baseline_deviation": 0.0,
            "history_deviation": 0.0,
            "recent_context_deviation": 0.0,
        }
        
        # Normalize current value
        norm_current = self.current_value
        
        # Baseline deviation
        if self.baseline_mean is not None:
            z = abs(norm_current - self.baseline_mean) / max(0.01, self.baseline_std)
            result["baseline_deviation"] = min(1.0, z / 3.0)
        
        # History deviation
        if self.historical_mean is not None:
            diff = abs(norm_current - self.historical_mean)
            result["history_deviation"] = min(1.0, diff * 2)
        
        # Recent context deviation
        if self.recent_context_mean is not None:
            diff = abs(norm_current - self.recent_context_mean)
            result["recent_context_deviation"] = min(1.0, diff * 2)
        
        return result


# =============================================================================
# Urgency Indicator Analyzer
# =============================================================================

class UrgencyIndicatorAnalyzer:
    """
    Computes urgency cues from signal characteristics.
    
    Examples:
        - rapid_escalation: Fast intensity increase
        - critical_threshold: Crossing important thresholds
        - time_sensitive_transition: Urgent timing patterns
    """
    
    def __init__(
        self,
        current_value: float,
        previous_value: Optional[float] = None,
        rate_of_change: float = 0.0,
        threshold_critical: float = 0.8,
        threshold_escalation: float = 0.5,
    ):
        """Initialize urgency indicator analyzer."""
        self.current_value = max(0.0, min(1.0, current_value))
        self.previous_value = previous_value
        self.rate_of_change = rate_of_change
        self.threshold_critical = threshold_critical
        self.threshold_escalation = threshold_escalation
    
    def analyze(self) -> dict:
        """Perform urgency indicator analysis."""
        result = {
            "rapid_escalation": 0.0,
            "critical_threshold": 0.0,
            "time_sensitive_transition": 0.0,
        }
        
        # Rapid escalation: fast increase
        if self.previous_value is not None:
            delta = self.current_value - self.previous_value
            if delta > 0 and self.rate_of_change > self.threshold_escalation:
                result["rapid_escalation"] = min(1.0, delta * self.rate_of_change)
        
        # Critical threshold crossing
        if self.current_value >= self.threshold_critical:
            result["critical_threshold"] = 1.0
        
        # Time-sensitive transition
        if self.previous_value is not None and self.rate_of_change > 0:
            time_to_critical = (self.threshold_critical - self.current_value) / max(0.01, self.rate_of_change)
            result["time_sensitive_transition"] = min(1.0, 1.0 / max(1.0, time_to_critical))
        
        return result


# =============================================================================
# Context Projection Analyzer
# =============================================================================

class ContextProjectionAnalyzer:
    """
    Projects external context values into the feature space.
    
    These are NOT computed - they are inputs from higher layers.
    
    Examples:
        - task_criticality: From Executive/Workspace
        - focus_strength: From FocusingNetwork
        - resource_pressure: From ResourceMonitor
    """
    
    def __init__(
        self,
        task_criticality: Optional[float] = None,
        focus_strength: Optional[float] = None,
        resource_pressure: Optional[float] = None,
    ):
        """Initialize context projection analyzer."""
        self.task_criticality = (
            None if task_criticality is None else max(0.0, min(1.0, task_criticality))
        )
        self.focus_strength = (
            None if focus_strength is None else max(0.0, min(1.0, focus_strength))
        )
        self.resource_pressure = (
            None if resource_pressure is None else max(0.0, min(1.0, resource_pressure))
        )
    
    def analyze(self) -> dict:
        """Project context values into feature space."""
        result = {
            "task_criticality_projection": self.task_criticality,
            "focus_strength_projection": self.focus_strength,
            "resource_pressure_projection": self.resource_pressure,
        }
        
        return result


# =============================================================================
# Feature Aggregator
# =============================================================================

class FeatureAggregator:
    """
    Combines features from all analyzers into a single vector.
    
    Produces: AlertingFeatureVector with normalized features,
              provenance tracking, and validity flags.
    """
    
    def __init__(
        self,
        vector_id: str,
        signal_id: Optional[str] = None,
        extraction_timestamp: Optional[datetime] = None,
    ):
        """Initialize aggregator."""
        self.vector_id = vector_id
        self.signal_id = signal_id
        self.extraction_timestamp = extraction_timestamp or datetime.utcnow()
    
    def aggregate(
        self,
        change_features: dict,
        onset_features: dict,
        offset_features: dict,
        contrast_features: dict,
        temporal_features: dict,
        frequency_features: dict,
        prediction_features: dict,
        novelty_features: dict,
        urgency_features: dict,
        context_features: dict,
    ) -> "AlertingFeatureVector":
        """
        Aggregate all feature dictionaries into a vector.
        
        Args:
            change_features: From ChangeDetector
            onset_features: From OnsetDetector
            offset_features: From OffsetDetector
            contrast_features: From ContrastAnalyzer
            temporal_features: From TemporalStabilityAnalyzer
            frequency_features: From FrequencyAnalyzer
            prediction_features: From PredictionErrorAnalyzer
            novelty_features: From NoveltyAnalyzer
            urgency_features: From UrgencyIndicatorAnalyzer
            context_features: From ContextProjectionAnalyzer
            
        Returns:
            AlertingFeatureVector with all features combined
        """
        from .vector import AlertingFeatureVector
        
        # Build confidence and validity maps
        confidence_map = {}
        validity_map = {}
        
        def add_feature(name: str, value: float, valid: bool = True) -> None:
            """Add a feature to the maps."""
            confidence_map[name] = 0.9 if valid else 0.0
            validity_map[name] = valid
        
        # Add change detection features
        for name in ["absolute_change", "relative_change", "rate_of_change", "acceleration"]:
            val = change_features.get(name, 0.0)
            add_feature(name, val, valid=val >= 0)
        
        # Add onset features
        for name in ["onset_appearance", "onset_activation", "onset_emergence"]:
            val = onset_features.get(name, 0.0)
            add_feature(name, val, valid=True)
        
        # Add offset features
        for name in ["offset_termination", "offset_disappearance", "offset_cessation"]:
            val = offset_features.get(name, 0.0)
            add_feature(name, val, valid=True)
        
        # Add contrast features
        for name in ["local_contrast", "background_contrast", "context_contrast"]:
            val = contrast_features.get(name, 0.0)
            add_feature(name, val, valid=True)
        
        # Add temporal stability features
        for name in ["variance", "oscillation", "consistency", "drift"]:
            val = temporal_features.get(name, 0.0)
            add_feature(name, val, valid=True)
        
        # Add frequency features
        for name in ["event_frequency", "periodicity", "burstiness"]:
            val = frequency_features.get(name, 0.0)
            add_feature(name, val, valid=True)
        
        # Add prediction error
        name = "prediction_error_estimate"
        val = prediction_features.get(name, 0.0)
        add_feature(name, val, valid=prediction_features.get("expected_value") is not None)
        
        # Add novelty features
        for name in ["baseline_deviation", "history_deviation", "recent_context_deviation"]:
            val = novelty_features.get(name, 0.0)
            add_feature(name, val, valid=True)
        
        # Add urgency features
        for name in ["rapid_escalation", "critical_threshold", "time_sensitive_transition"]:
            val = urgency_features.get(name, 0.0)
            if name == "critical_threshold: float = None":
                name = "critical_threshold"
            add_feature(name, val, valid=True)
        
        # Add context projections (may be None)
        for name in ["task_criticality_projection", "focus_strength_projection", "resource_pressure_projection"]:
            val = context_features.get(name)
            if val is not None:
                add_feature(name, val, valid=True)
            else:
                confidence_map[name] = 0.0
                validity_map[name] = False
        
        return AlertingFeatureVector(
            vector_id=self.vector_id,
            # Change detection features
            absolute_change=change_features.get("absolute_change", 0.0),
            relative_change=change_features.get("relative_change", 0.0),
            rate_of_change=change_features.get("rate_of_change", 0.0),
            acceleration=change_features.get("acceleration", 0.0),
            # Onset detection features
            onset_appearance=onset_features.get("onset_appearance", 0.0),
            onset_activation=onset_features.get("onset_activation", 0.0),
            onset_emergence=onset_features.get("onset_emergence", 0.0),
            # Offset detection features
            offset_termination=offset_features.get("offset_termination", 0.0),
            offset_disappearance=offset_features.get("offset_disappearance", 0.0),
            offset_cessation=offset_features.get("offset_cessation", 0.0),
            # Contrast detection features
            local_contrast=contrast_features.get("local_contrast", 0.0),
            background_contrast=contrast_features.get("background_contrast", 0.0),
            context_contrast=contrast_features.get("context_contrast", 0.0),
            # Temporal stability features
            variance=temporal_features.get("variance", 0.0),
            oscillation=temporal_features.get("oscillation", 0.0),
            consistency=temporal_features.get("consistency", 0.0),
            drift=temporal_features.get("drift", 0.0),
            # Frequency analysis features
            event_frequency=frequency_features.get("event_frequency", 0.0),
            periodicity=frequency_features.get("periodicity", 0.0),
            burstiness=frequency_features.get("burstiness", 0.0),
            # Prediction error feature
            prediction_error_estimate=prediction_features.get(
                "prediction_error_estimate", 0.0
            ),
            # Novelty features
            baseline_deviation=novelty_features.get("baseline_deviation", 0.0),
            history_deviation=novelty_features.get("history_deviation", 0.0),
            recent_context_deviation=novelty_features.get(
                "recent_context_deviation", 0.0
            ),
            # Urgency indicator features
            rapid_escalation=urgency_features.get("rapid_escalation", 0.0),
            critical_threshold=urgency_features.get("critical_threshold: float = None", 0.0) or urgency_features.get("critical_threshold", 0.0),
            time_sensitive_transition=urgency_features.get(
                "time_sensitive_transition", 0.0
            ),
            # Context projection features (may be None)
            task_criticality_projection=context_features.get("task_criticality_projection"),
            focus_strength_projection=context_features.get("focus_strength_projection"),
            resource_pressure_projection=context_features.get("resource_pressure_projection"),
            # Metadata
            features_confidence=confidence_map,
            validity_flags=validity_map,
            extraction_timestamp=self.extraction_timestamp,
            signal_id_reference=self.signal_id,
        )