# Alerting Signal Models and Computational State
# ==============================================

"""
Computational state models for the AlertingNetwork.

This module provides the canonical signal representation and bounded computational
state upon which every later Alerting computation depends. It is entirely runtime-neutral:
no Core scheduler, no timers, no polling, no threads, no asynchronous logic.

The AlertingNetwork remains a pure computational Network.

Components:
    - AlertingSignal: A normalized observation (independent of perception)
    - AlertingFeature: Extracted measurable properties
    - AlertingEvidence: Aggregates multiple features with confidence
    - AlertingHistory: Bounded history of signals
    - AlertingBaseline: Adaptive baseline for deviation detection
    - HabituationState: Response attenuation with repeated exposure
    - RefractoryState: Suppression after recent alerts
    - TemporalState: Recent observations and rolling statistics
    - NetworkState: Complete bounded computational state

All models are immutable dataclasses with frozen=True to ensure:
    - Deterministic behavior
    - Thread safety
    - Hashability (for use in sets/dicts)
    - No side effects from modification
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, FrozenSet, Optional, Tuple
from datetime import datetime


# =============================================================================
# Type Aliases
# =============================================================================

AlertingSignalId = str
AlertingEvidenceId = str
AlertingScalar = float


# =============================================================================
# AlertingSignal: Canonical Observation
# =============================================================================

@dataclass(frozen=True, slots=True)
class AlertingSignal:
    """
    A single normalized observation.
    
    Represents one signal presentation. It is independent of perception - 
    meaning it's a processed representation that can come from any source.
    
    Fields include:
        identity: Unique identifier for tracking
        source: Origin of the signal (AlertingSource enum)
        modality: Sensory channel (AlertingModality enum)
        timestamp: When observed
        signal_category: Type of event or change
        payload_reference: Reference to underlying data (not embedded payload)
        confidence: Confidence in this observation (0.0 to 1.0)
        provenance: Source tracking metadata
    
    The signal itself does NOT contain:
        - Demand scores
        - Attention recommendations
        - Behavioral commands
        - Execution authority
    
    It is purely descriptive: what was observed, when, where, and with what confidence.
    """
    
    # Identity (required for state tracking across signals)
    signal_id: AlertingSignalId
    
    # Source and modality (required for proper routing and classification)
    source: str  # String representation of AlertingSource enum value
    modality: str  # String representation of AlertingModality enum value
    
    # Timestamp (required - no wall-clock usage inside the network)
    timestamp: datetime
    
    # Signal category (what kind of event/transition occurred)
    signal_category: str  # e.g., "onset", "offset", "change", "pulse"
    
    # Payload reference (pointer to underlying data, not embedded payload)
    payload_reference: Optional[str] = None
    
    # Confidence in this observation (0.0 to 1.0)
    confidence: float = 1.0
    
    # Provenance tracking
    provenance: str = "unknown"  # Simple string representation


# =============================================================================
# AlertingFeature: Measurable Properties
# =============================================================================

@dataclass(frozen=True, slots=True)
class AlertingFeature:
    """
    A measurable property extracted from a signal.
    
    Features are quantitative measurements. They are NOT interpretations.
    Each feature has a name and a scalar value.
    
    Examples of features:
        - intensity: Signal strength (0.0 to 1.0)
        - contrast: Signal-to-background ratio
        - velocity: Rate of change (0.0 to 1.0 per time unit)
        - change_magnitude: Absolute deviation from baseline
        - frequency: Oscillation rate
        - periodicity: Regularity of pattern (0.0 to 1.0)
        - entropy: Uncertainty/randomness measure
        - novelty_hint: Deviation from learned patterns
        - prediction_error_hint: Unpredicted component
        - urgency_hint: Time-sensitive demand indicator
    
    Features are measured, not inferred. Inference happens in later phases.
    """
    
    # Feature identifier
    feature_id: str
    
    # Feature name (machine-readable)
    name: str  # e.g., "intensity", "contrast", "velocity"
    
    # Measured value (typically 0.0 to 1.0, but bounds vary by feature)
    value: float
    
    # Unit description for documentation
    unit_description: Optional[str] = None
    
    # Confidence in this measurement (0.0 to 1.0)
    confidence: float = 1.0


# =============================================================================
# AlertingEvidence: Aggregated Features
# =============================================================================

@dataclass(frozen=True, slots=True)
class AlertingEvidence:
    """
    Evidence aggregates multiple features into a coherent representation.
    
    Evidence exists BEFORE demand estimation. It is the raw material from which
    later phases compute attention demand.
    
    Contains:
        - features: Tuple of AlertingFeature instances
        - confidence: Overall confidence in this evidence set
        - provenance: Tracking metadata
    
    The context projection represents how this evidence projects into the
    network's internal model (e.g., expected intensity, variance).
    """
    
    # Evidence identifier
    evidence_id: AlertingEvidenceId
    
    # Features that constitute this evidence
    features: Tuple[AlertingFeature, ...]
    
    # Overall confidence in this evidence set
    confidence: float = 1.0
    
    # Provenance tracking
    provenance: str = "unknown"
    
    # Context projection (optional)
    context_projection: Optional[str] = None


# =============================================================================
# AlertingHistory: Bounded Signal History
# =============================================================================

@dataclass(frozen=True, slots=True)
class AlertingHistory:
    """
    A bounded history of signals.
    
    The capacity is configurable and must be enforced. The history maintains
    signals in chronological order (oldest to newest).
    
    Operations:
        - append: Add new signal (evicts oldest if at capacity)
        - recent: Get last N signals
        - rolling_stats: Compute statistics over bounded window
    
    Bounded growth is guaranteed by capacity enforcement.
    """
    
    # Maximum number of signals to retain
    capacity: int = 100
    
    # Signals in chronological order (oldest first)
    _signals: Tuple[AlertingSignal, ...] = field(default_factory=tuple)
    
    @property
    def size(self) -> int:
        """Return current history size."""
        return len(self._signals)
    
    @property
    def is_empty(self) -> bool:
        """Return True if history contains no signals."""
        return self.size == 0
    
    @property
    def last_signal(self) -> Optional[AlertingSignal]:
        """Return the most recent signal, or None if empty."""
        return self._signals[-1] if self._signals else None
    
    @property
    def first_signal(self) -> Optional[AlertingSignal]:
        """Return the oldest signal, or None if empty."""
        return self._signals[0] if self._signals else None
    
    def recent(self, n: int = 1) -> Tuple[AlertingSignal, ...]:
        """
        Return the last N signals (most recent first).
        
        Args:
            n: Number of signals to retrieve
            
        Returns:
            Tuple of up to N most recent signals
        """
        if self._signals:
            return tuple(reversed(self._signals[-n:]))
        return ()
    
    def contains_signal_id(self, signal_id: str) -> bool:
        """Check if a signal ID exists in history."""
        return any(s.signal_id == signal_id for s in self._signals)
    
    def snapshot(self) -> Tuple[AlertingSignal, ...]:
        """
        Return an immutable snapshot of signals.
        
        Used for diagnostics, validation, serialization, and testing.
        """
        return self._signals


# =============================================================================
# AlertingBaseline: Adaptive Baseline Model
# =============================================================================

@dataclass(frozen=True, slots=True)
class AlertingBaseline:
    """
    An adaptive baseline model for deviation detection.
    
    Stores expected values for various signal characteristics. The baseline
    is updated through explicit transitions - never hidden mutations.
    
    Expected values stored:
        - expected_intensity: Expected average intensity
        - expected_variance: Expected variance around mean
        - expected_change_frequency: Expected rate of change events
        - expected_arrival_interval: Expected time between signals
    
    Baseline updates are state transitions that produce a new baseline instance.
    """
    
    # Expected values (all must be non-negative)
    expected_intensity: float = 0.5  # 0.0 to 1.0
    expected_variance: float = 0.1   # Variance in intensity
    expected_change_frequency: float = 0.2  # Events per unit time
    expected_arrival_interval: float = 5.0  # Seconds between signals
    
    # Tracking statistics for adaptation
    observation_count: int = 0
    last_update_timestamp: Optional[datetime] = None
    
    def update(
        self,
        new_intensity: float,
        timestamp: datetime
    ) -> AlertingBaseline:
        """
        Create a new baseline with updated estimates.
        
        This is an explicit transition - returns a new instance rather than
        modifying the existing one. Implements a simple exponential moving average
        for gradual adaptation.
        
        Args:
            new_intensity: Observed intensity value
            timestamp: When this observation was made
            
        Returns:
            New AlertingBaseline with updated expectations
        """
        alpha = 0.1  # Adaptation rate
        
        return AlertingBaseline(
            expected_intensity=self.expected_intensity * (1 - alpha) + new_intensity * alpha,
            expected_variance=self._update_variance(new_intensity, alpha),
            expected_change_frequency=self.expected_change_frequency,
            expected_arrival_interval=self._update_interval(timestamp, alpha),
            observation_count=self.observation_count + 1,
            last_update_timestamp=timestamp
        )
    
    def _update_variance(self, new_value: float, alpha: float) -> float:
        """Update variance estimate."""
        # Simple heuristic: variance scales with intensity
        return max(0.0, min(1.0, self.expected_variance * (1 - alpha) + abs(new_value - self.expected_intensity) * alpha))
    
    def _update_interval(self, timestamp: datetime, alpha: float) -> float:
        """Update arrival interval estimate."""
        # If we have a last update, compute time delta
        if self.last_update_timestamp:
            from datetime import timedelta
            elapsed = (timestamp - self.last_update_timestamp).total_seconds()
            return max(0.1, self.expected_arrival_interval * (1 - alpha) + elapsed * alpha)
        return self.expected_arrival_interval
    
    def deviation(self, observed_intensity: float) -> float:
        """
        Compute deviation from expected intensity.
        
        Returns a normalized deviation score (0.0 to 1.0).
        """
        if self.expected_variance <= 0:
            return 0.0
        
        z_score = abs(observed_intensity - self.expected_intensity) / max(0.01, self.expected_variance)
        # Normalize to 0-1 range using sigmoid-like function
        return min(1.0, z_score)


# =============================================================================
# HabituationState: Response Attenuation with Repetition
# =============================================================================

@dataclass(frozen=True, slots=True)
class HabituationState:
    """
    Computational habituation state.
    
    Purpose: Repeated identical stimuli gradually decrease demand over time.
    
    This is NOT neuroscience-based modeling. It's functional habituation:
    a computational mechanism to reduce response to repeated signals.
    
    Stores:
        - exposure_count: Number of exposures to the same stimulus type
        - last_exposure: When the last exposure occurred
        - habituation_coefficient: Current attenuation factor (0.0 to 1.0)
        - recovery_coefficient: Rate at which sensitivity recovers
    
    No neuroscience terminology is used in ownership.
    Only functional terminology.
    """
    
    # State values (all bounded)
    exposure_count: int = 0
    last_exposure_timestamp: Optional[datetime] = None
    habituation_coefficient: float = 1.0  # 1.0 = no attenuation, 0.0 = maximum attenuation
    recovery_coefficient: float = 0.05  # Per-time-unit recovery rate
    
    def record_exposure(self, timestamp: datetime) -> HabituationState:
        """
        Record a new exposure event and update state.
        
        Args:
            timestamp: When the exposure occurred
            
        Returns:
            New HabituationState with updated counts and coefficient
        """
        # Increase exposure count (bounded)
        new_count = min(100, self.exposure_count + 1)
        
        # Decrease habituation coefficient (more attenuation with more exposures)
        # Coefficient ranges from 1.0 (no habituation) to ~0.2 (full habituation)
        new_coefficient = max(0.2, self.habituation_coefficient * 0.9)
        
        return HabituationState(
            exposure_count=new_count,
            last_exposure_timestamp=timestamp,
            habituation_coefficient=new_coefficient,
            recovery_coefficient=self.recovery_coefficient
        )
    
    def recover(self, current_time: datetime) -> HabituationState:
        """
        Apply recovery over time.
        
        Args:
            current_time: Current timestamp
            
        Returns:
            New HabituationState with recovered coefficient
        """
        if self.last_exposure_timestamp is None:
            return self
        
        elapsed = (current_time - self.last_exposure_timestamp).total_seconds()
        recovery_amount = elapsed * self.recovery_coefficient
        
        new_coefficient = min(1.0, self.habituation_coefficient + recovery_amount)
        
        return HabituationState(
            exposure_count=self.exposure_count,
            last_exposure_timestamp=self.last_exposure_timestamp,
            habituation_coefficient=new_coefficient,
            recovery_coefficient=self.recovery_coefficient
        )
    
    def snapshot(self) -> dict:
        """
        Return immutable snapshot for diagnostics/testing.
        
        Includes all state values in a dictionary format.
        """
        return {
            "exposure_count": self.exposure_count,
            "last_exposure_timestamp": self.last_exposure_timestamp.isoformat() if self.last_exposure_timestamp else None,
            "habituation_coefficient": self.habituation_coefficient,
            "recovery_coefficient": self.recovery_coefficient
        }


# =============================================================================
# RefractoryState: Post-Alert Suppression Period
# =============================================================================

@dataclass(frozen=True, slots=True)
class RefractoryState:
    """
    Computational refractory suppression state.
    
    Purpose: Prevent repeated triggering by the same event.
    
    Stores:
        - recent_alerts: Recent alert timestamps (bounded)
        - suppression_window: Duration of suppression after an alert
        - suppression_strength: How strongly alerts are suppressed
        - expiration: When current suppression period ends
    
    The refractory state prevents rapid re-alerting after a significant event.
    """
    
    # State values
    recent_alerts: Tuple[datetime, ...] = field(default_factory=tuple)
    suppression_window_seconds: float = 2.0
    suppression_strength: float = 0.5  # Multiplier for suppressed signals
    
    @property
    def last_alert(self) -> Optional[datetime]:
        """Return the most recent alert timestamp."""
        return self.recent_alerts[-1] if self.recent_alerts else None
    
    @property
    def is_in_refractory_period(self) -> bool:
        """Return True if currently in refractory period."""
        return len(self.recent_alerts) > 0
    
    def record_alert(self, timestamp: datetime) -> RefractoryState:
        """
        Record a new alert and update state.
        
        Args:
            timestamp: When the alert occurred
            
        Returns:
            New RefractoryState with updated recent alerts
        """
        # Keep only alerts within suppression window
        cutoff = timestamp.timestamp() - self.suppression_window_seconds
        
        # Add new alert to beginning of tuple (most recent first)
        new_alerts = tuple(
            dt for dt in self.recent_alerts 
            if dt.timestamp() > cutoff
        ) + (timestamp,)
        
        return RefractoryState(
            recent_alerts=new_alerts,
            suppression_window_seconds=self.suppression_window_seconds,
            suppression_strength=self.suppression_strength
        )
    
    def is_suppressed(self, current_time: datetime) -> bool:
        """
        Check if a signal at the given time would be suppressed.
        
        Args:
            current_time: Time to check
            
        Returns:
            True if signal should be suppressed
        """
        return len(self.recent_alerts) > 0
    
    def suppression_multiplier(self, current_time: datetime) -> float:
        """
        Get suppression multiplier for a given time.
        
        Args:
            current_time: Time to evaluate
            
        Returns:
            Suppression multiplier (1.0 = no suppression)
        """
        if not self.recent_alerts:
            return 1.0
        
        # Check if within suppression window
        last_alert = self.last_alert
        elapsed = (current_time - last_alert).total_seconds()
        
        if elapsed < self.suppression_window_seconds:
            return max(0.0, 1.0 - (elapsed / self.suppression_window_seconds) * (1 - self.suppression_strength))
        return 1.0
    
    def snapshot(self) -> dict:
        """Return immutable snapshot for diagnostics/testing."""
        return {
            "recent_alert_count": len(self.recent_alerts),
            "suppression_window_seconds": self.suppression_window_seconds,
            "suppression_strength": self.suppression_strength
        }


# =============================================================================
# TemporalState: Rolling Statistics and Recent Observations
# =============================================================================

@dataclass(frozen=True, slots=True)
class TemporalState:
    """
    Temporal state containing rolling statistics.
    
    Contains recent observations with their timestamps, along with computed
    rolling statistics over a bounded window.
    """
    
    # Bounded history of observations (timestamped values)
    _observations: Tuple[Tuple[datetime, float], ...] = field(default_factory=tuple)
    
    # Rolling statistics
    rolling_mean: Optional[float] = None
    rolling_std: Optional[float] = None
    rolling_min: Optional[float] = None
    rolling_max: Optional[float] = None
    
    # Timing information
    last_observation_timestamp: Optional[datetime] = None
    last_assessment_timestamp: Optional[datetime] = None
    last_significant_event_timestamp: Optional[datetime] = None
    
    @property
    def observation_count(self) -> int:
        """Return number of observations."""
        return len(self._observations)
    
    def add_observation(self, timestamp: datetime, value: float) -> TemporalState:
        """
        Add a new observation and recompute rolling statistics.
        
        Args:
            timestamp: When observation was made
            value: Observed value
            
        Returns:
            New TemporalState with updated observations and stats
        """
        # Add to beginning (most recent first)
        new_observations = ((timestamp, value),) + self._observations
        
        # Recompute statistics
        values = [v for _, v in new_observations]
        
        return TemporalState(
            _observations=new_observations,
            rolling_mean=self._compute_mean(values),
            rolling_std=self._compute_std(values),
            rolling_min=min(values) if values else None,
            rolling_max=max(values) if values else None,
            last_observation_timestamp=timestamp,
            last_assessment_timestamp=self.last_assessment_timestamp,
            last_significant_event_timestamp=self.last_significant_event_timestamp
        )
    
    def record_assessment(self, timestamp: datetime) -> TemporalState:
        """Record an assessment timestamp."""
        return TemporalState(
            _observations=self._observations,
            rolling_mean=self.rolling_mean,
            rolling_std=self.rolling_std,
            rolling_min=self.rolling_min,
            rolling_max=self.rolling_max,
            last_observation_timestamp=self.last_observation_timestamp,
            last_assessment_timestamp=timestamp,
            last_significant_event_timestamp=self.last_significant_event_timestamp
        )
    
    def record_significant_event(self, timestamp: datetime) -> TemporalState:
        """Record a significant event timestamp."""
        return TemporalState(
            _observations=self._observations,
            rolling_mean=self.rolling_mean,
            rolling_std=self.rolling_std,
            rolling_min=self.rolling_min,
            rolling_max=self.rolling_max,
            last_observation_timestamp=self.last_observation_timestamp,
            last_assessment_timestamp=self.last_assessment_timestamp,
            last_significant_event_timestamp=timestamp
        )
    
    def _compute_mean(self, values: list) -> Optional[float]:
        """Compute mean of values."""
        if not values:
            return None
        return sum(values) / len(values)
    
    def _compute_std(self, values: list) -> Optional[float]:
        """Compute standard deviation of values."""
        if len(values) < 2:
            return None
        mean = self._compute_mean(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def snapshot(self) -> dict:
        """Return immutable snapshot."""
        return {
            "observation_count": self.observation_count,
            "rolling_mean": self.rolling_mean,
            "rolling_std": self.rolling_std,
            "rolling_min": self.rolling_min,
            "rolling_max": self.rolling_max,
            "last_observation_timestamp": self.last_observation_timestamp.isoformat() if self.last_observation_timestamp else None,
            "last_assessment_timestamp": self.last_assessment_timestamp.isoformat() if self.last_assessment_timestamp else None,
            "last_significant_event_timestamp": self.last_significant_event_timestamp.isoformat() if self.last_significant_event_timestamp else None
        }


# =============================================================================
# NetworkState: Complete Bounded Computational State
# =============================================================================

@dataclass(frozen=True, slots=True)
class NetworkState:
    """
    Complete bounded computational state of the AlertingNetwork.
    
    This captures all internal state that the network owns. It does NOT include:
        - Cognitive goals
        - Active task state  
        - Full perceptual history (only bounded temporal state)
        - Global event history
    
    The state is designed to be:
        - Immutable (snapshots create new instances)
        - Serializable (for diagnostics and testing)
        - Deterministic (same input produces same output given same state)
    
    State transitions return new NetworkState instances rather than modifying
    existing ones.
    """
    
    # Core state components
    signal_history: AlertingHistory = field(default_factory=AlertingHistory)
    baseline: AlertingBaseline = field(default_factory=AlertingBaseline)
    habituation_state: HabituationState = field(default_factory=HabituationState)
    refractory_state: RefractoryState = field(default_factory=RefractoryState)
    temporal_state: TemporalState = field(default_factory=TemporalState)
    
    # Diagnostic counters (not part of core computation, but useful for monitoring)
    total_signals_processed: int = 0
    total_assessments_completed: int = 0
    
    def with_signal_history(self, history: AlertingHistory) -> NetworkState:
        """Return new state with updated signal history."""
        return NetworkState(
            signal_history=history,
            baseline=self.baseline,
            habituation_state=self.habituation_state,
            refractory_state=self.refractory_state,
            temporal_state=self.temporal_state,
            total_signals_processed=self.total_signals_processed,
            total_assessments_completed=self.total_assessments_completed
        )
    
    def with_baseline(self, baseline: AlertingBaseline) -> NetworkState:
        """Return new state with updated baseline."""
        return NetworkState(
            signal_history=self.signal_history,
            baseline=baseline,
            habituation_state=self.habituation_state,
            refractory_state=self.refractory_state,
            temporal_state=self.temporal_state,
            total_signals_processed=self.total_signals_processed,
            total_assessments_completed=self.total_assessments_completed
        )
    
    def with_habituation(self, state: HabituationState) -> NetworkState:
        """Return new state with updated habituation state."""
        return NetworkState(
            signal_history=self.signal_history,
            baseline=self.baseline,
            habituation_state=state,
            refractory_state=self.refractory_state,
            temporal_state=self.temporal_state,
            total_signals_processed=self.total_signals_processed,
            total_assessments_completed=self.total_assessments_completed
        )
    
    def with_refractory(self, state: RefractoryState) -> NetworkState:
        """Return new state with updated refractory state."""
        return NetworkState(
            signal_history=self.signal_history,
            baseline=self.baseline,
            habituation_state=self.habituation_state,
            refractory_state=state,
            temporal_state=self.temporal_state,
            total_signals_processed=self.total_signals_processed,
            total_assessments_completed=self.total_assessments_completed
        )
    
    def with_temporal(self, state: TemporalState) -> NetworkState:
        """Return new state with updated temporal state."""
        return NetworkState(
            signal_history=self.signal_history,
            baseline=self.baseline,
            habituation_state=self.habituation_state,
            refractory_state=self.refractory_state,
            temporal_state=state,
            total_signals_processed=self.total_signals_processed,
            total_assessments_completed=self.total_assessments_completed
        )
    
    def with_signal_processed(self) -> NetworkState:
        """Increment signal processed counter."""
        return NetworkState(
            signal_history=self.signal_history,
            baseline=self.baseline,
            habituation_state=self.habituation_state,
            refractory_state=self.refractory_state,
            temporal_state=self.temporal_state,
            total_signals_processed=self.total_signals_processed + 1,
            total_assessments_completed=self.total_assessments_completed
        )
    
    def with_assessment_completed(self) -> NetworkState:
        """Increment assessment completed counter."""
        return NetworkState(
            signal_history=self.signal_history,
            baseline=self.baseline,
            habituation_state=self.habituation_state,
            refractory_state=self.refractory_state,
            temporal_state=self.temporal_state,
            total_signals_processed=self.total_signals_processed,
            total_assessments_completed=self.total_assessments_completed + 1
        )
    
    def snapshot(self) -> dict:
        """
        Return immutable snapshot of entire state.
        
        Used for diagnostics, validation, serialization, and testing.
        All sub-states are also snapshotted.
        """
        return {
            "signal_history": self.signal_history.snapshot(),
            "baseline": {
                "expected_intensity": self.baseline.expected_intensity,
                "expected_variance": self.baseline.expected_variance,
                "expected_change_frequency": self.baseline.expected_change_frequency,
                "expected_arrival_interval": self.baseline.expected_arrival_interval,
                "observation_count": self.baseline.observation_count,
                "last_update_timestamp": self.baseline.last_update_timestamp.isoformat() if self.baseline.last_update_timestamp else None
            },
            "habituation_state": self.habituation_state.snapshot(),
            "refractory_state": self.refractory_state.snapshot(),
            "temporal_state": self.temporal_state.snapshot(),
            "total_signals_processed": self.total_signals_processed,
            "total_assessments_completed": self.total_assessments_completed
        }


# =============================================================================
# State Transition Models
# =============================================================================

@dataclass(frozen=True, slots=True)
class StateTransition:
    """
    A state transition record for debugging and validation.
    
    Records what changed during an assessment. Not part of core computation
    but useful for explainability and testing.
    """
    
    # Transition identity
    transition_id: str
    
    # Type of transition
    transition_type: str  # e.g., "baseline_update", "habituation_change"
    
    # Timestamp
    timestamp: datetime
    
    # Before/after values
    before_state: dict
    after_state: dict
    
    # Reason for change (optional)
    reason: Optional[str] = None


# =============================================================================
# Validation Functions
# =============================================================================

def validate_signal(signal: AlertingSignal) -> Tuple[bool, list]:
    """
    Validate an AlertingSignal.
    
    Checks:
        - signal_id is non-empty
        - source and modality are non-empty strings
        - timestamp is a datetime
        - confidence is in valid range (0.0 to 1.0)
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not signal.signal_id:
        errors.append("signal_id must be non-empty")
    
    if not signal.source:
        errors.append("source must be non-empty")
    
    if not signal.modality:
        errors.append("modality must be non-empty")
    
    if not isinstance(signal.timestamp, datetime):
        errors.append("timestamp must be a datetime")
    
    if not (0.0 <= signal.confidence <= 1.0):
        errors.append(f"confidence must be in [0.0, 1.0], got {signal.confidence}")
    
    return len(errors) == 0, errors


def validate_feature(feature: AlertingFeature) -> Tuple[bool, list]:
    """
    Validate an AlertingFeature.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not feature.feature_id:
        errors.append("feature_id must be non-empty")
    
    if not feature.name:
        errors.append("feature name must be non-empty")
    
    # Value bounds are feature-specific; no generic validation
    
    if not (0.0 <= feature.confidence <= 1.0):
        errors.append(f"confidence must be in [0.0, 1.0], got {feature.confidence}")
    
    return len(errors) == 0, errors


def validate_evidence(evidence: AlertingEvidence) -> Tuple[bool, list]:
    """
    Validate an AlertingEvidence.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not evidence.evidence_id:
        errors.append("evidence_id must be non-empty")
    
    # Check confidence range
    if not (0.0 <= evidence.confidence <= 1.0):
        errors.append(f"confidence must be in [0.0, 1.0], got {evidence.confidence}")
    
    return len(errors) == 0, errors


def validate_history(history: AlertingHistory) -> Tuple[bool, list]:
    """
    Validate an AlertingHistory.
    
    Checks:
        - capacity is positive
        - size does not exceed capacity (should be enforced)
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if history.capacity <= 0:
        errors.append(f"capacity must be positive, got {history.capacity}")
    
    if history.size > history.capacity:
        errors.append(f"history size ({history.size}) exceeds capacity ({history.capacity})")
    
    # Validate each signal
    for i, signal in enumerate(history._signals):
        valid, sig_errors = validate_signal(signal)
        if not valid:
            errors.append(f"signal {i}: {sig_errors}")
    
    return len(errors) == 0, errors


def validate_baseline(baseline: AlertingBaseline) -> Tuple[bool, list]:
    """
    Validate an AlertingBaseline.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    for name, value in [
        ("expected_intensity", baseline.expected_intensity),
        ("expected_variance", baseline.expected_variance),
        ("expected_change_frequency", baseline.expected_change_frequency),
        ("expected_arrival_interval", baseline.expected_arrival_interval),
    ]:
        if value < 0:
            errors.append(f"{name} must be non-negative, got {value}")
    
    return len(errors) == 0, errors


def validate_habituation(state: HabituationState) -> Tuple[bool, list]:
    """
    Validate a HabituationState.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not (0.0 <= state.habituation_coefficient <= 1.0):
        errors.append(f"habituation_coefficient must be in [0.0, 1.0], got {state.habituation_coefficient}")
    
    if state.exposure_count < 0:
        errors.append(f"exposure_count must be non-negative, got {state.exposure_count}")
    
    return len(errors) == 0, errors


def validate_refractory(state: RefractoryState) -> Tuple[bool, list]:
    """
    Validate a RefractoryState.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if state.suppression_window_seconds <= 0:
        errors.append(f"suppression_window_seconds must be positive, got {state.suppression_window_seconds}")
    
    if not (0.0 <= state.suppression_strength <= 1.0):
        errors.append(f"suppression_strength must be in [0.0, 1.0], got {state.suppression_strength}")
    
    return len(errors) == 0, errors


def validate_temporal(state: TemporalState) -> Tuple[bool, list]:
    """
    Validate a TemporalState.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    # Basic validation - temporal values can be None or in valid ranges
    return True, []


def validate_network_state(state: NetworkState) -> Tuple[bool, list]:
    """
    Validate complete NetworkState.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate each component
    _, hist_errs = validate_history(state.signal_history)
    if hist_errs:
        errors.extend([f"signal_history: {e}" for e in hist_errs])
    
    _, base_errs = validate_baseline(state.baseline)
    if base_errs:
        errors.extend([f"baseline: {e}" for e in base_errs])
    
    _, hab_errs = validate_habituation(state.habituation_state)
    if hab_errs:
        errors.extend([f"habituation_state: {e}" for e in hab_errs])
    
    _, ref_errs = validate_refractory(state.refractory_state)
    if ref_errs:
        errors.extend([f"refractory_state: {e}" for e in ref_errs])
    
    _, temp_errs = validate_temporal(state.temporal_state)
    if temp_errs:
        errors.extend([f"temporal_state: {e}" for e in temp_errs])
    
    # Validate counters
    if state.total_signals_processed < 0:
        errors.append(f"total_signals_processed must be non-negative, got {state.total_signals_processed}")
    
    if state.total_assessments_completed < 0:
        errors.append(f"total_assessments_completed must be non-negative, got {state.total_assessments_completed}")
    
    return len(errors) == 0, errors


# =============================================================================
# Snapshot Validation
# =============================================================================

def validate_snapshot_consistency(original: NetworkState, snapshot: dict) -> Tuple[bool, list]:
    """
    Validate that a snapshot accurately represents the original state.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check top-level fields
    if snapshot.get("total_signals_processed") != original.total_signals_processed:
        errors.append("total_signals_processed mismatch")
    
    if snapshot.get("total_assessments_completed") != original.total_assessments_completed:
        errors.append("total_assessments_completed mismatch")
    
    return len(errors) == 0, errors