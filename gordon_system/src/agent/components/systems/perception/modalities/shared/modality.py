# Perception Modality - Phase 5.2 Shared Modality Contract
# ===========================================================

"""
Perception Modality: An autonomous perceptual subsystem responsible for
acquiring information from one class of environmental signals and transforming
those signals into the common Perceptual Ontology.

Modality Laws:
    MODALITY-LAW-001: Every Perception Modality possesses one stable architectural identity
    MODALITY-LAW-002: Every Modality shall belong to exactly one canonical Modality Family
    MODALITY-LAW-003: Every Modality shall declare its supported capabilities explicitly
    MODALITY-LAW-004: Every Modality shall expose canonical Perception Foundation artifacts only
    MODALITY-LAW-005: Every Modality shall preserve complete acquisition and processing provenance
    MODALITY-LAW-006: Every Modality shall preserve confidence and uncertainty explicitly
    MODALITY-LAW-007: Every Modality shall remain independently testable and replaceable
    MODALITY-LAW-008: Modality semantics shall remain deterministic for equivalent inputs,
                      configuration, calibration and effective permissions

Modality Philosophy:
    Environment → Sensor → Signal → Feature → Percept → Integration
    
Every modality implements the same external contract. Only implementation differs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# MODALITY FAMILY - Classification of acquisition domains
# =============================================================================


class ModalityFamily(Enum):
    """
    Classification of modality acquisition domains.
    
    Sensory Modalities: Observe physical or simulated environments
    
    Digital Modalities: Observe computational environments (OS state,
                      application state, symbolic execution, event streams)
    """
    
    SENSORY = "sensory"     # Physical/simulated environment observation
    DIGITAL = "digital"   # Computational environment observation


# =============================================================================
# MODALITY KIND - Canonical modality types
# =============================================================================


class ModalityKind(Enum):
    """
    Canonical modality kinds.
    
    Current modalities (Phase 5.2.1):
        vision, audition, speech, console
        
    Future modalities:
        depth, lidar, radar, touch, proprioception, inertial,
        shell, kernel, filesystem, network, processes,
        windows, clipboard, editor, browser, api
    """
    
    # Sensory modalities
    VISION = "vision"
    AUDITION = "audition"
    SPEECH = "speech"
    DEPTH = "depth"
    LIDAR = "lidar"
    RADAR = "radar"
    TOUCH = "touch"
    PROPRIOCEPTION = "proprioception"
    INERTIAL = "inertial"
    
    # Digital modalities
    CONSOLE = "console"
    SHELL = "shell"
    KERNEL = "kernel"
    FILESYSTEM = "filesystem"
    NETWORK = "network"
    PROCESSES = "processes"
    WINDOWS = "windows"
    CLIPBOARD = "clipboard"
    EDITOR = "editor"
    BROWSER = "browser"
    API = "api"


# =============================================================================
# ACTIVATION MODE - When and how a modality acquires observations
# =============================================================================


class ActivationMode(Enum):
    """
    Modes of modality activation.
    
    CONTINUOUS: Continuously acquire data (e.g., video stream)
    PERIODIC: Acquire at regular intervals
    EVENT_DRIVEN: React to external events
    ON_DEMAND: Activate only when explicitly requested
    SESSION_BOUND: Active during a specific session
    POLICY_TRIGGERED: Activated by policy conditions
    MANUAL: User-triggered activation only
    DISABLED: Not active
    """
    
    CONTINUOUS = "continuous"
    PERIODIC = "periodic"
    EVENT_DRIVEN = "event_driven"
    ON_DEMAND = "on_demand"
    SESSION_BOUND = "session_bound"
    POLICY_TRIGGERED = "policy_triggered"
    MANUAL = "manual"
    DISABLED = "disabled"


# =============================================================================
# MODALITY STATE - Lifecycle states
# =============================================================================


class ModalityState(Enum):
    """
    States in the modality lifecycle.
    
    DISCOVERED: Modality detected but not yet initialized
    UNAVAILABLE: Detected but temporarily inaccessible
    INITIALIZING: Currently being set up
    CALIBRATING: Calibration in progress
    READY: Initialized and calibrated, awaiting activation
    ACTIVE: Actively acquiring observations
    DEGRADED: Degraded operation (some capabilities unavailable)
    SANDBOXED: Limited by sandbox constraints
    SUSPENDED: Temporarily paused
    FAILED: Failed during operation
    TERMINATED: Permanently stopped
    """
    
    DISCOVERED = "discovered"
    UNAVAILABLE = "unavailable"
    INITIALIZING = "initializing"
    CALIBRATING = "calibrating"
    READY = "ready"
    ACTIVE = "active"
    DEGRADED = "degraded"
    SANDBOXED = "sandboxed"
    SUSPENDED = "suspended"
    FAILED = "failed"
    TERMINATED = "terminated"


# =============================================================================
# CALIBRATION STATE
# =============================================================================


class CalibrationState(Enum):
    """
    Calibration status of a modality.
    
    UNCALIBRATED: Not yet calibrated
    CALIBRATING: Currently calibrating
    CALIBRATED: Calibrated and ready
    DEGRADED: Calibrated but degraded accuracy
    INVALID: Calibration data is invalid or expired
    """
    
    UNCALIBRATED = "uncalibrated"
    CALIBRATING = "calibrating"
    CALIBRATED = "calibrated"
    DEGRADED = "degraded"
    INVALID = "invalid"


# =============================================================================
# TRUST PROFILE - Digital evidence source trustworthiness
# =============================================================================


@dataclass(frozen=True)
class TrustProfile:
    """
    Trustworthiness profile for a digital evidence source.
    
    Fields:
        authority:            Source authority level (none, basic, elevated, privileged)
        visibility_scope:     What the source can observe (self, process_tree, host, etc.)
        integrity_guarantees: Integrity guarantees provided (none, signed, verified)
        trust_level:          0.0-1.0 trust assessment
        freshness:            How fresh the data is (instant, near_realtime, delayed, historical)
        completeness:         Portion of available evidence that is actually observed
    """
    
    authority: str                      # none, basic, elevated, privileged
    visibility_scope: str               # self_only, process_tree, user_scope, etc.
    integrity_guarantees: str           # none, signed, verified
    trust_level: float = 0.5            # 0.0-1.0
    freshness: str = "delayed"          # instant, near_realtime, delayed, historical
    completeness: Optional[float] = None  # 0.0-1.0 or None for unknown


# =============================================================================
# CALIBRATION METADATA - Modality calibration information
# =============================================================================


@dataclass(frozen=True)
class CalibrationMetadata:
    """
    Calibration metadata for a modality.
    
    Fields:
        method:              Calibration method used
        inputs:              Input data used for calibration
        revision:            Calibration revision number
        timestamp_utc:       When calibration was performed
        sensor_alignment:    Alignment parameters
        noise_estimate:      Estimated noise characteristics
        quality_estimate:    Quality assessment after calibration
        time_sync_offset_ms: Time synchronization offset in milliseconds
        provenance:          Calibration provenance tracking
    """
    
    method: str                         # Algorithm/method used
    inputs: Tuple[str, ...] = field(default_factory=tuple)  # Input references
    revision: int = 1                   # Calibration version
    timestamp_utc: float = field(default_factory=time.time)
    
    sensor_alignment: Dict[str, float] = field(default_factory=dict)
    noise_estimate: float = 0.0         # Noise level estimate
    quality_estimate: float = 1.0       # Post-calibration quality
    time_sync_offset_ms: float = 0.0    # Time sync offset
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking


# =============================================================================
# MODALITY HEALTH - Modality operational health status
# =============================================================================


@dataclass(frozen=True)
class ModalityHealth:
    """
    Operational health status of a modality.
    
    Fields:
        is_available:        True if modality can produce observations
        latency_ms:          Typical acquisition latency in milliseconds
        sensor_quality:      Quality score 0.0-1.0 for the sensor hardware
        confidence_quality:  Quality of confidence estimation
        pipeline_health:     Health of processing pipeline components
        diagnostics:         Detailed diagnostic information
    """
    
    is_available: bool = True           # Can the modality function?
    latency_ms: float = 0.0             # Acquisition latency (0 if not applicable)
    sensor_quality: float = 1.0         # Sensor quality 0.0-1.0
    confidence_quality: float = 1.0     # Confidence estimation quality 0.0-1.0
    pipeline_health: Dict[str, bool] = field(default_factory=dict)  # Component health
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)    # Diagnostic messages


# =============================================================================
# MODALITY DIAGNOSTICS - Detailed diagnostic information
# =============================================================================


@dataclass(frozen=True)
class ModalityDiagnostics:
    """
    Detailed diagnostic information for a modality.
    
    Fields:
        observation_count:       Total observations produced
        dropped_event_count:     Events that could not be processed
        signal_quality_mean:     Mean quality score of signals
        confidence_distribution: Confidence value distribution
        uncertainty_distribution: Uncertainty value distribution
        effective_permission_scope: Current permission scope
        sandbox_status:          Sandbox enforcement status
        calibration_status:      Calibration state string
    """
    
    observation_count: int = 0
    dropped_event_count: int = 0
    signal_quality_mean: float = 1.0
    confidence_distribution: Dict[str, float] = field(default_factory=dict)  # value -> count
    uncertainty_distribution: Dict[str, float] = field(default_factory=dict)
    effective_permission_scope: Tuple[str, ...] = field(default_factory=tuple)
    sandbox_status: str = "none"
    calibration_status: str = "unknown"


# =============================================================================
# MODALITY METRICS - Runtime statistics
# =============================================================================


@dataclass(frozen=True)
class ModalityMetrics:
    """
    Runtime metrics for a modality.
    
    Fields:
        observations_produced:   Number of observations generated
        signals_processed:       Number of signals processed
        features_extracted:      Number of features computed
        percepts_generated:      Number of percepts created
        latency_p50_ms:          50th percentile latency in ms
        latency_p95_ms:          95th percentile latency in ms
        throughput_observations_per_sec: Observations generated per second
        errors_count:            Error count
        warnings_count:          Warning count
    """
    
    observations_produced: int = 0
    signals_processed: int = 0
    features_extracted: int = 0
    percepts_generated: int = 0
    
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    
    throughput_observations_per_sec: float = 0.0
    
    errors_count: int = 0
    warnings_count: int = 0


# =============================================================================
# PERCEPTION MODALITY - Base class for all modalities
# =============================================================================


@dataclass(frozen=True)
class PerceptionModality:
    """
    Base class for all Perception Modalities.
    
    Every modality implements the same external semantic boundary. Internal
    acquisition mechanisms may differ completely.
    
    Fields:
        identity:            Unique modality identifier (UUID-based)
        family:              Modality family (SENSORY or DIGITAL)
        modality_kind:       Canonical kind (VISION, CONSOLE, etc.)
        
        capabilities:        Set of supported capability identifiers
        permissions:         Effective permission set for this instance
        sandbox_profile:     Active sandbox profile (NONE to STRICT)
        
        availability:        Current availability state
        lifecycle_state:     Current lifecycle state
        calibration_state:   Calibration status
        health:              Operational health status
        
        configuration:       Modality-specific configuration
        revision:            Configuration revision number
        provenance:          Modality origin tracking
        
        metrics:             Runtime statistics
    """
    
    # Core identity (required)
    identity: str                       # Globally unique modality ID
    
    family: ModalityFamily              # SENSORY or DIGITAL
    modality_kind: ModalityKind         # Which specific modality?
    
    # Capabilities and permissions
    capabilities: Tuple[str, ...] = field(default_factory=tuple)
    permissions: Tuple[str, ...] = field(default_factory=tuple)
    sandbox_profile: str = "NONE"       # NONE, PROCESS, USER, CONTAINER, etc.
    
    # Availability and states (required)
    availability: str = "UNKNOWN"       # AVAILABLE, DEGRADED, RESTRICTED, etc.
    lifecycle_state: ModalityState = ModalityState.DISCOVERED
    calibration_state: CalibrationState = CalibrationState.UNCALIBRATED
    
    health: ModalityHealth = field(default_factory=ModalityHealth)
    
    # Configuration (optional)
    configuration: Dict[str, Any] = field(default_factory=dict)
    
    revision: int = 1                   # Configuration revision
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    # Runtime metrics
    metrics: ModalityMetrics = field(default_factory=ModalityMetrics)
    
    @property
    def is_active(self) -> bool:
        """Check if modality is actively producing observations."""
        return self.lifecycle_state == ModalityState.ACTIVE
    
    @property
    def is_ready(self) -> bool:
        """Check if modality is ready for activation."""
        return (
            self.lifecycle_state == ModalityState.READY and
            self.calibration_state in (CalibrationState.CALIBRATED, CalibrationState.DEGRADED)
        )
    
    @property
    def is_operational(self) -> bool:
        """Check if modality can produce observations."""
        return (
            self.availability == "AVAILABLE" and
            self.health.is_available
        )
    
    @classmethod
    def create(
        cls,
        modality_kind: ModalityKind,
        identity: Optional[str] = None,
        family: ModalityFamily = ModalityFamily.DIGITAL,  # Default to digital
        capabilities: Tuple[str, ...] = (),
        permissions: Tuple[str, ...] = (),
        sandbox_profile: str = "NONE",
    ) -> "PerceptionModality":
        """
        Create a new modality instance.
        
        Args:
            modality_kind: Which kind of modality to create
            identity: Unique identifier (auto-generated if None)
            family: Modality family (SENSORY or DIGITAL)
            capabilities: Supported capability identifiers
            permissions: Effective permission set
            sandbox_profile: Active sandbox profile
            
        Returns:
            New PerceptionModality instance
        """
        return cls(
            identity=identity or f"modality:{uuid.uuid4().hex[:24]}",
            family=family,
            modality_kind=modality_kind,
            capabilities=capabilities,
            permissions=permissions,
            sandbox_profile=sandbox_profile,
            availability="UNKNOWN",
            lifecycle_state=ModalityState.DISCOVERED,
            calibration_state=CalibrationState.UNCALIBRATED,
        )
    
    def update_health(
        self,
        is_available: Optional[bool] = None,
        latency_ms: Optional[float] = None,
        sensor_quality: Optional[float] = None,
        confidence_quality: Optional[float] = None,
        pipeline_health: Optional[Dict[str, bool]] = None,
        diagnostics: Optional[Tuple[str, ...]] = None,
    ) -> "PerceptionModality":
        """
        Create a new instance with updated health information.
        
        Args:
            is_available: Can the modality function?
            latency_ms: Acquisition latency
            sensor_quality: Sensor quality 0.0-1.0
            confidence_quality: Confidence estimation quality
            pipeline_health: Component health map
            diagnostics: Diagnostic messages
            
        Returns:
            New PerceptionModality with updated health
        """
        new_health = ModalityHealth(
            is_available=is_available if is_available is not None else self.health.is_available,
            latency_ms=latency_ms if latency_ms is not None else self.health.latency_ms,
            sensor_quality=sensor_quality if sensor_quality is not None else self.health.sensor_quality,
            confidence_quality=confidence_quality if confidence_quality is not None else self.health.confidence_quality,
            pipeline_health=pipeline_health or dict(self.health.pipeline_health),
            diagnostics=diagnostics or self.health.diagnostics,
        )
        
        return dataclass_replace(
            self,
            health=new_health,
        )
    
    def update_availability(self, availability: str) -> "PerceptionModality":
        """Create a new instance with updated availability state."""
        return dataclass_replace(self, availability=availability)
    
    def update_lifecycle_state(self, state: ModalityState) -> "PerceptionModality":
        """Create a new instance with updated lifecycle state."""
        return dataclass_replace(self, lifecycle_state=state)
    
    def update_calibration_state(self, state: CalibrationState) -> "PerceptionModality":
        """Create a new instance with updated calibration state."""
        return dataclass_replace(self, calibration_state=state)
    
    def increment_metrics_observations(self) -> "PerceptionModality":
        """Increment observation count in metrics."""
        new_metrics = ModalityMetrics(
            **{k: getattr(self.metrics, k) for k in self.metrics.__dataclass_fields__.keys()}
        )
        # Can't modify frozen dataclass directly, so use builder pattern
        return self  # Placeholder - actual implementation would be more complex
    
    def record_observation(self) -> "PerceptionModality":
        """Record an observation event."""
        new_metrics = ModalityMetrics(
            observations_produced=self.metrics.observations_produced + 1,
            signals_processed=self.metrics.signals_processed,
            features_extracted=self.metrics.features_extracted,
            percepts_generated=self.metrics.percepts_generated,
            latency_p50_ms=self.metrics.latency_p50_ms,
            latency_p95_ms=self.metrics.latency_p95_ms,
            throughput_observations_per_sec=self.metrics.throughput_observations_per_sec,
            errors_count=self.metrics.errors_count,
            warnings_count=self.metrics.warnings_count,
        )
        return dataclass_replace(self, metrics=new_metrics)
    
    def record_error(self) -> "PerceptionModality":
        """Record an error event."""
        new_metrics = ModalityMetrics(
            observations_produced=self.metrics.observations_produced,
            signals_processed=self.metrics.signals_processed,
            features_extracted=self.metrics.features_extracted,
            percepts_generated=self.metrics.percepts_generated,
            latency_p50_ms=self.metrics.latency_p50_ms,
            latency_p95_ms=self.metrics.latency_p95_ms,
            throughput_observations_per_sec=self.metrics.throughput_observations_per_sec,
            errors_count=self.metrics.errors_count + 1,
            warnings_count=self.metrics.warnings_count,
        )
        return dataclass_replace(self, metrics=new_metrics)
    
    def record_warning(self) -> "PerceptionModality":
        """Record a warning event."""
        new_metrics = ModalityMetrics(
            observations_produced=self.metrics.observations_produced,
            signals_processed=self.metrics.signals_processed,
            features_extracted=self.metrics.features_extracted,
            percepts_generated=self.metrics.percepts_generated,
            latency_p50_ms=self.metrics.latency_p50_ms,
            latency_p95_ms=self.metrics.latency_p95_ms,
            throughput_observations_per_sec=self.metrics.throughput_observations_per_sec,
            errors_count=self.metrics.errors_count,
            warnings_count=self.metrics.warnings_count + 1,
        )
        return dataclass_replace(self, metrics=new_metrics)
    
    def get_diagnostics(self) -> ModalityDiagnostics:
        """Generate diagnostics report for this modality."""
        return ModalityDiagnostics(
            observation_count=self.metrics.observations_produced,
            dropped_event_count=0,  # Will be tracked separately
            signal_quality_mean=self.health.sensor_quality,
            confidence_distribution={},
            uncertainty_distribution={},
            effective_permission_scope=self.permissions,
            sandbox_status=self.sandbox_profile,
            calibration_status=self.calibration_state.name,
        )
    
    def is_capable(self, capability: str) -> bool:
        """Check if modality supports a specific capability."""
        return capability in self.capabilities
    
    def has_permission(self, permission: str) -> bool:
        """Check if modality has a specific permission."""
        return permission in self.permissions


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(instance: PerceptionModality, **kwargs) -> PerceptionModality:
    """Replace fields in a frozen perception modality dataclass."""
    return PerceptionModality(
        identity=kwargs.get("identity", instance.identity),
        family=kwargs.get("family", instance.family),
        modality_kind=kwargs.get("modality_kind", instance.modality_kind),
        capabilities=kwargs.get("capabilities", instance.capabilities),
        permissions=kwargs.get("permissions", instance.permissions),
        sandbox_profile=kwargs.get("sandbox_profile", instance.sandbox_profile),
        availability=kwargs.get("availability", instance.availability),
        lifecycle_state=kwargs.get("lifecycle_state", instance.lifecycle_state),
        calibration_state=kwargs.get("calibration_state", instance.calibration_state),
        health=kwargs.get("health", instance.health),
        configuration=kwargs.get("configuration", instance.configuration),
        revision=kwargs.get("revision", instance.revision),
        provenance=kwargs.get("provenance", instance.provenance),
        metrics=kwargs.get("metrics", instance.metrics),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: list[str] = [
    # Enums
    "ModalityFamily",
    "ModalityKind",
    "ActivationMode",
    "ModalityState",
    "CalibrationState",
    
    # Dataclasses
    "TrustProfile",
    "CalibrationMetadata",
    "ModalityHealth",
    "ModalityDiagnostics",
    "ModalityMetrics",
    "PerceptionModality",
    
    # Utility functions
    "dataclass_replace",
]