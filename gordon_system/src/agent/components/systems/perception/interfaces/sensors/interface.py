# Sensors Interface Implementation - Phase 5.2.5
# ==============================================

"""
Sensors Interface: The inbound interface for sensor evidence acquisition.

Package:
    perception/interfaces/sensors/

The Sensors Interface connects acquisition adapters and sensing infrastructure
to Perception Modalities. It is an inbound Interface that does not expose
Perception to cognition.

LAW-001: The Sensors Interface shall admit acquired evidence into the owning Modality only.
LAW-002: The Sensors Interface shall preserve sensor and adapter identity.
LAW-003: The Sensors Interface shall preserve calibration, permission and sandbox context.
LAW-004: The Sensors Interface shall preserve acquisition ordering and dropped-sample metadata.
LAW-005: The Sensors Interface shall not perform percept construction or semantic classification.
LAW-006: Sensor failure shall never fabricate replacement evidence.
LAW-007: Sensor sessions and publications shall remain inspectable.
LAW-008: Sensor communication shall remain deterministic for equivalent source streams.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from collections import deque
import uuid

from ..shared import (
    InterfaceKind,
    InterfaceStatus,
    InterfaceHealth,
    PerceptionInterfaceContract,
    RequestResult,
)


# =============================================================================
# SENSOR DESCRIPTOR
# =============================================================================


@dataclass(frozen=True)
class SensorKind:
    """Kinds of sensors."""
    
    VISION = "vision"
    AUDIO = "audio" 
    TEXT = "text"
    ACCELEROMETER = "accelerometer"
    GYROSCOPE = "gyroscope"
    MAGNETOMETER = "magnetometer"
    PRESSURE = "pressure"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    LIGHT = "light"
    PROXIMITY = "proximity"
    GPS = "gps"
    
    # Digital sensors
    KEYBOARD = "keyboard"
    MOUSE = "mouse"
    TOUCH = "touch"
    SHELL_COMMAND = "shell_command"
    FILESYSTEM_ACCESS = "filesystem_access"
    CLIPBOARD_ACCESS = "clipboard_access"
    NETWORK_ACTIVITY = "network_activity"
    KERNEL_EVENT = "kernel_event"


@dataclass(frozen=True)
class PerceptionSensorDescriptor:
    """
    Descriptor for a sensor available to the Sensors Interface.
    
    Fields:
        sensor_identity: Unique identifier for this sensor
        sensor_kind: The kind of sensor (see SensorKind)
        adapter_identity: Identity of the adapter providing access
        supported_modalities: Modalities this sensor can provide
        supported_signal_kinds: Signal kinds this sensor produces
        supported_observation_kinds: Observation kinds this sensor produces
        sampling_capabilities: Supported sampling rates and configurations
        calibration_requirements: Calibration requirements
        permission_requirements: Permission requirements for access
        platform_requirements: Platform-specific requirements
        sandbox_requirements: Sandbox restrictions if any
        availability: Current availability status
        health: Health status
        revision: Interface specification revision
        
    SENSOR-DESCRIPTOR-LAW-001: Every sensor shall expose one discoverable Descriptor.
    SENSOR-DESCRIPTOR-LAW-002: Descriptors shall declare supported Modalities and Signal kinds.
    SENSOR-DESCRIPTOR-LAW-003: Descriptors shall declare calibration, permission, platform and sandbox requirements.
    SENSOR-DESCRIPTOR-LAW-004: Descriptors shall distinguish capability from availability.
    SENSOR-DESCRIPTOR-LAW-005: Descriptors shall preserve adapter identity and revision.
    SENSOR-DESCRIPTOR-LAW-006: Descriptors shall not activate sensors.
    SENSOR-DESCRIPTOR-LAW-007: Descriptor history shall remain inspectable.
    SENSOR-DESCRIPTOR-LAW-008: Descriptor publication shall remain deterministic.
    """
    
    sensor_identity: str
    sensor_kind: str  # Must be one of SensorKind
    
    adapter_identity: str = "default_adapter"
    
    supported_modalities: Set[str] = field(default_factory=set)
    """Modalities this sensor can provide (vision, audio, etc.)"""
    
    supported_signal_kinds: Set[str] = field(default_factory=set)
    """Signal kinds this sensor produces (raw, preprocessed, etc.)"""
    
    supported_observation_kinds: Set[str] = field(default_factory=set)
    """Observation kinds this sensor produces (image, spectrogram, text, etc.)"""
    
    sampling_capabilities: Dict[str, Any] = field(default_factory=dict)
    """Supported sampling rates and configurations"""
    
    calibration_requirements: Dict[str, Any] = field(default_factory=dict)
    """Calibration requirements"""
    
    permission_requirements: Set[str] = field(default_factory=set)
    """Permissions required for access"""
    
    platform_requirements: Dict[str, Any] = field(default_factory=dict)
    """Platform-specific requirements (OS version, hardware, etc.)"""
    
    sandbox_requirements: Dict[str, Any] = field(default_factory=dict)
    """Sandbox restrictions if any (file system access limits, etc.)"""
    
    availability: bool = True
    health_status: str = InterfaceStatus.ACTIVE
    
    revision: int = 1
    
    @classmethod
    def create_vision_sensor(
        cls,
        sensor_id: str,
        adapter_id: str = "camera_adapter",
        **kwargs
    ) -> "PerceptionSensorDescriptor":
        """Create a vision sensor descriptor."""
        return cls(
            sensor_identity=sensor_id,
            sensor_kind=SensorKind.VISION,
            adapter_identity=adapter_id,
            supported_modalities={"vision"},
            supported_signal_kinds={"raw_image", "preprocessed", "features"},
            supported_observation_kinds={"image", "video", "frame"},
        )
    
    @classmethod
    def create_audio_sensor(
        cls,
        sensor_id: str,
        adapter_id: str = "audio_adapter",
        **kwargs
    ) -> "PerceptionSensorDescriptor":
        """Create an audio sensor descriptor."""
        return cls(
            sensor_identity=sensor_id,
            sensor_kind=SensorKind.AUDIO,
            adapter_identity=adapter_id,
            supported_modalities={"audio"},
            supported_signal_kinds={"raw_audio", "preprocessed", "spectrogram"},
            supported_observation_kinds={"audio_sample", "spectrogram", "mfcc"},
        )
    
    @classmethod
    def create_keyboard_sensor(
        cls,
        sensor_id: str,
        adapter_id: str = "keyboard_adapter",
        **kwargs
    ) -> "PerceptionSensorDescriptor":
        """Create a keyboard/digital input sensor descriptor."""
        return cls(
            sensor_identity=sensor_id,
            sensor_kind=SensorKind.KEYBOARD,
            adapter_identity=adapter_id,
            supported_modalities={"digital"},
            supported_signal_kinds={"key_event", "key_press", "key_release"},
            supported_observation_kinds={"keystroke", "input_event"},
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "sensor_identity": self.sensor_identity,
            "sensor_kind": self.sensor_kind,
            "adapter_identity": self.adapter_identity,
            "supported_modalities": list(self.supported_modalities),
            "supported_signal_kinds": list(self.supported_signal_kinds),
            "supported_observation_kinds": list(self.supported_observation_kinds),
            "sampling_capabilities": dict(self.sampling_capabilities),
            "calibration_requirements": dict(self.calibration_requirements),
            "permission_requirements": list(self.permission_requirements),
            "platform_requirements": dict(self.platform_requirements),
            "sandbox_requirements": dict(self.sandbox_requirements),
            "availability": self.availability,
            "health_status": self.health_status,
            "revision": self.revision,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptionSensorDescriptor":
        """Create descriptor from dictionary."""
        return cls(
            sensor_identity=data.get("sensor_identity", ""),
            sensor_kind=data.get("sensor_kind", ""),
            adapter_identity=data.get("adapter_identity", "default_adapter"),
            supported_modalities=set(data.get("supported_modalities", [])),
            supported_signal_kinds=set(data.get("supported_signal_kinds", [])),
            supported_observation_kinds=set(data.get("supported_observation_kinds", [])),
            sampling_capabilities=dict(data.get("sampling_capabilities", {})),
            calibration_requirements=dict(data.get("calibration_requirements", {})),
            permission_requirements=set(data.get("permission_requirements", [])),
            platform_requirements=dict(data.get("platform_requirements", {})),
            sandbox_requirements=dict(data.get("sandbox_requirements", {})),
            availability=data.get("availability", True),
            health_status=data.get("health_status", InterfaceStatus.ACTIVE),
            revision=int(data.get("revision", 1)),
        )


# =============================================================================
# ACQUISITION REQUEST
# =============================================================================


@dataclass(frozen=True)
class SensorAcquisitionRequest:
    """
    Request for sensor acquisition.
    
    Fields:
        request_identity: Unique identifier for this request
        sensor_reference: Reference to the target sensor
        requested_modality: Modality to acquire (vision, audio, etc.)
        requested_signal_kinds: Signal kinds desired
        sampling_configuration: Sampling configuration request
        quality_requirements: Quality requirements
        temporal_constraints: Time-based constraints
        spatial_constraints: Space-based constraints  
        permission_context: Permission context for this acquisition
        sandbox_context: Sandbox restrictions to respect
        calibration_reference: Calibration reference to use
        provenance: Request origin tracking
        
    SENSOR-ACQUISITION-LAW-001: Acquisition shall require validated configuration and authority.
    SENSOR-ACQUISITION-LAW-002: Effective sampling configuration shall remain explicit.
    SENSOR-ACQUISITION-LAW-003: Acquisition shall preserve calibration state.
    SENSOR-ACQUISITION-LAW-004: Acquisition shall preserve source quality and uncertainty.
    SENSOR-ACQUISITION-LAW-005: Acquisition shall report sample loss, disconnection and overflow.
    SENSOR-ACQUISITION-LAW-006: Acquisition failure shall not publish valid-looking evidence.
    SENSOR-ACQUISITION-LAW-007: Acquisition history shall remain inspectable.
    SENSOR-ACQUISITION-LAW-008: Acquisition behavior shall remain deterministic for equivalent source input.
    """
    
    request_identity: str
    sensor_reference: str
    
    requested_modality: Optional[str] = None
    requested_signal_kinds: Set[str] = field(default_factory=set)
    
    sampling_configuration: Dict[str, Any] = field(default_factory=dict)
    quality_requirements: Dict[str, Any] = field(default_factory=dict)
    
    temporal_constraints: Dict[str, Any] = field(default_factory=dict)
    spatial_constraints: Dict[str, Any] = field(default_factory=dict)
    
    permission_context: Dict[str, Any] = field(default_factory=dict)
    sandbox_context: Dict[str, Any] = field(default_factory=dict)
    calibration_reference: Optional[str] = None
    
    provenance: Dict[str, Any] = field(default_factory=lambda: {"timestamp": _time.time()})
    
    @classmethod
    def create(
        cls,
        sensor_id: str,
        modality: str,
        consumer_id: str,
        **kwargs
    ) -> "SensorAcquisitionRequest":
        """Create an acquisition request."""
        return cls(
            request_identity=f"acquisition:{uuid.uuid4().hex[:16]}",
            sensor_reference=sensor_id,
            requested_modality=modality,
            sampling_configuration=kwargs.get("sampling_config", {}),
            quality_requirements=kwargs.get("quality_requirements", {}),
            permission_context={"consumer": consumer_id},
        )
    
    def is_valid(self) -> bool:
        """Validate the acquisition request."""
        if not self.request_identity or len(self.request_identity) == 0:
            return False
        if not self.sensor_reference or len(self.sensor_reference) == 0:
            return False
        
        # Sampling configuration must have required fields
        if "sample_rate" in self.sampling_configuration:
            sample_rate = self.sampling_configuration["sample_rate"]
            if not isinstance(sample_rate, (int, float)) or sample_rate <= 0:
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "request_identity": self.request_identity,
            "sensor_reference": self.sensor_reference,
            "requested_modality": self.requested_modality,
            "requested_signal_kinds": list(self.requested_signal_kinds),
            "sampling_configuration": dict(self.sampling_configuration),
            "quality_requirements": dict(self.quality_requirements),
            "temporal_constraints": dict(self.temporal_constraints),
            "spatial_constraints": dict(self.spatial_constraints),
            "permission_context": dict(self.permission_context),
            "sandbox_context": dict(self.sandbox_context),
            "calibration_reference": self.calibration_reference,
            "provenance": dict(self.provenance),
        }


# =============================================================================
# ACQUISITION RESPONSE
# =============================================================================


@dataclass(frozen=True)
class SensorAcquisitionResponse:
    """
    Response to a sensor acquisition request.
    
    Fields:
        request_reference: Reference to the originating request
        acquisition_session: Unique identifier for this acquisition session
        effective_capabilities: What was actually available during acquisition
        effective_sampling_config: Sampling configuration that was used
        effective_permission_scope: Permissions that were granted
        effective_sandbox_scope: Sandbox restrictions that applied
        calibration_state: Calibration status of the sensor
        limitations: Any constraints that limited the acquisition
        status: Overall acquisition status
        
    SENSOR-ACQUISITION-LAW-001 through 008 apply to this response.
    """
    
    request_reference: str
    
    # Acquisition session
    acquisition_session: str = field(default_factory=lambda: f"session:{uuid.uuid4().hex[:16]}")
    
    # Effective capabilities (may differ from requested)
    effective_capabilities: Dict[str, Any] = field(default_factory=dict)
    
    # Effective sampling configuration  
    effective_sampling_config: Dict[str, Any] = field(default_factory=dict)
    
    # Permission and sandbox scope
    effective_permission_scope: Dict[str, Any] = field(default_factory=dict)
    effective_sandbox_scope: Dict[str, Any] = field(default_factory=dict)
    
    # Calibration state
    calibration_state: str = "unknown"
    calibration_reference: Optional[str] = None
    
    # Limitations that applied
    limitations: Set[str] = field(default_factory=set)
    
    # Status (SUCCESS, PARTIAL, FAILED, etc.)
    status: str = InterfaceStatus.ACTIVE  # ACTIVE = success in acquisition context
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_success(
        cls,
        request_ref: str,
        capabilities: Dict[str, Any],
        sampling_config: Dict[str, Any],
        **kwargs
    ) -> "SensorAcquisitionResponse":
        """Create a successful acquisition response."""
        return cls(
            request_reference=request_ref,
            effective_capabilities=dict(capabilities),
            effective_sampling_config=dict(sampling_config),
            calibration_state=kwargs.get("calibration_state", "calibrated"),
        )
    
    @classmethod
    def create_partial(
        cls,
        request_ref: str,
        capabilities: Dict[str, Any],
        limitations: List[str],
        **kwargs
    ) -> "SensorAcquisitionResponse":
        """Create a partial acquisition response."""
        return cls(
            request_reference=request_ref,
            effective_capabilities=dict(capabilities),
            limitations=set(limitations),
            status=InterfaceStatus.DEGRADED,
        )
    
    @classmethod
    def create_failed(
        cls,
        request_ref: str,
        failure_kind: str,
        **kwargs
    ) -> "SensorAcquisitionResponse":
        """Create a failed acquisition response."""
        return cls(
            request_reference=request_ref,
            status=InterfaceStatus.UNAVAILABLE,
            diagnostics={
                "failure_kind": failure_kind,
                "timestamp": _time.time(),
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "request_reference": self.request_reference,
            "acquisition_session": self.acquisition_session,
            "effective_capabilities": dict(self.effective_capabilities),
            "effective_sampling_config": dict(self.effective_sampling_config),
            "effective_permission_scope": dict(self.effective_permission_scope),
            "effective_sandbox_scope": dict(self.effective_sandbox_scope),
            "calibration_state": self.calibration_state,
            "calibration_reference": self.calibration_reference,
            "limitations": list(self.limitations),
            "status": self.status,
            "diagnostics": dict(self.diagnostics),
        }


# =============================================================================
# SENSOR EVIDENCE PUBLICATION
# =============================================================================


@dataclass(frozen=True)
class SensorEvidencePublication:
    """
    Publication of sensor evidence to a Modality.
    
    Fields:
        publication_identity: Unique identifier for this publication
        acquisition_session: The session that generated this evidence
        source_sensor: The sensor that produced the evidence
        source_adapter: The adapter providing access to the sensor
        observation: Processed observation data
        signal: Raw signal data (if included)
        acquisition_time: When the evidence was acquired
        sequence: Sequence number for ordering within session
        quality: Quality metrics of the evidence
        dropped_sample_metadata: Metadata about any samples that were dropped
        confidence: Confidence in the evidence (0.0-1.0)
        uncertainty: Uncertainty about the evidence (0.0-1.0)
        
    SENSOR-LAW-005 through 008 apply to this publication.
    """
    
    publication_identity: str = field(default_factory=lambda: f"pub:{uuid.uuid4().hex[:16]}")
    
    acquisition_session: str
    source_sensor: str
    source_adapter: str
    
    observation: Dict[str, Any]
    signal: Optional[Dict[str, Any]] = None  # May be omitted to save space
    
    acquisition_time: float = field(default_factory=_time.time)
    sequence: int = 0
    
    quality: Dict[str, Any] = field(default_factory=dict)
    dropped_sample_metadata: Optional[Dict[str, Any]] = None
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    @classmethod
    def create(
        cls,
        session_id: str,
        sensor_id: str,
        adapter_id: str,
        observation: Dict[str, Any],
        **kwargs
    ) -> "SensorEvidencePublication":
        """Create an evidence publication."""
        return cls(
            acquisition_session=session_id,
            source_sensor=sensor_id,
            source_adapter=adapter_id,
            observation=dict(observation),
            sequence=kwargs.get("sequence", 0),
            confidence=kwargs.get("confidence", 1.0),
            uncertainty=kwargs.get("uncertainty", 0.0),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "publication_identity": self.publication_identity,
            "acquisition_session": self.acquisition_session,
            "source_sensor": self.source_sensor,
            "source_adapter": self.source_adapter,
            "observation": dict(self.observation),
            "signal": dict(self.signal) if self.signal else None,
            "acquisition_time": self.acquisition_time,
            "sequence": self.sequence,
            "quality": dict(self.quality),
            "dropped_sample_metadata": self.dropped_sample_metadata,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


# =============================================================================
# SENSORS INTERFACE
# =============================================================================


class SensorsInterface:
    """
    Implementation of the Sensors Interface.
    
    This interface handles sensor discovery, acquisition requests, and evidence
    publication to Modalities.
    
    The interface maintains:
        - Available sensors (descriptors)
        - Active acquisition sessions  
        - Session history for inspection
        
    INTERFACE-LAW-001 through 008 apply to all interface operations.
    SENSOR-LAW-001 through 008 are specific to this interface.
    """
    
    def __init__(self, provider_id: str):
        self.provider_identity = provider_id
        self._contract = PerceptionInterfaceContract.create_sensors_contract(provider_id)
        
        # Sensor registry
        self._sensors: Dict[str, PerceptionSensorDescriptor] = {}
        self._sensor_history: deque = deque(maxlen=1000)  # Track last 1000 sensor events
        
        # Active sessions
        self._active_sessions: Dict[str, SensorAcquisitionResponse] = {}
        
        # Health tracking
        self._health = InterfaceHealth()
        self._session_counter = 0
    
    @property
    def contract(self) -> PerceptionInterfaceContract:
        """Get the interface contract."""
        return self._contract
    
    @property
    def health(self) -> InterfaceHealth:
        """Get the current interface health."""
        return self._health
    
    # -------------------------------------------------------------------------
    # Discovery operations
    # -------------------------------------------------------------------------
    
    def discover_sensors(self) -> List[PerceptionSensorDescriptor]:
        """
        Discover available sensors.
        
        Returns a list of all registered sensor descriptors.
        """
        return list(self._sensors.values())
    
    def get_sensor_descriptor(self, sensor_id: str) -> Optional[PerceptionSensorDescriptor]:
        """Get the descriptor for a specific sensor."""
        return self._sensors.get(sensor_id)
    
    # -------------------------------------------------------------------------
    # Sensor registration (for adapters to use)
    # -------------------------------------------------------------------------
    
    def register_sensor(self, descriptor: PerceptionSensorDescriptor) -> bool:
        """
        Register a new sensor with the interface.
        
        Returns True if registration succeeded.
        """
        self._sensors[descriptor.sensor_identity] = descriptor
        self._sensor_history.append({
            "event": "sensor_registered",
            "timestamp": _time.time(),
            "sensor_id": descriptor.sensor_identity,
        })
        return True
    
    def unregister_sensor(self, sensor_id: str) -> bool:
        """
        Unregister a sensor from the interface.
        
        Returns True if unregistration succeeded.
        """
        if sensor_id in self._sensors:
            del self._sensors[sensor_id]
            self._sensor_history.append({
                "event": "sensor_unregistered",
                "timestamp": _time.time(),
                "sensor_id": sensor_id,
            })
            return True
        return False
    
    # -------------------------------------------------------------------------
    # Acquisition operations  
    # -------------------------------------------------------------------------
    
    def start_acquisition(self, request: SensorAcquisitionRequest) -> Tuple[bool, SensorAcquisitionResponse]:
        """
        Start a sensor acquisition session.
        
        Returns:
            Tuple of (success, response)
            
        SENSOR-ACQUISITION-LAW-001: Acquisition shall require validated configuration and authority.
        SENSOR-ACQUISITION-LAW-006: Acquisition failure shall not publish valid-looking evidence.
        """
        # Validate the request
        if not request.is_valid:
            return False, SensorAcquisitionResponse.create_failed(
                request_ref=request.request_identity,
                failure_kind="invalid_request",
            )
        
        # Check sensor availability
        if request.sensor_reference not in self._sensors:
            return False, SensorAcquisitionResponse.create_failed(
                request_reference=request.request_identity,
                failure_kind="sensor_not_found",
            )
        
        # Generate session ID and response
        self._session_counter += 1
        session_id = f"session:{self.provider_identity}:{self._session_counter}"
        
        response = SensorAcquisitionResponse.create_success(
            request_reference=request.request_identity,
            capabilities={
                "modality": request.requested_modality,
                "sampling_rate": 60.0,  # Example default
            },
            sampling_config={"sample_rate": 60.0},
        )
        
        self._active_sessions[session_id] = response
        
        return True, response
    
    def get_session_response(self, session_id: str) -> Optional[SensorAcquisitionResponse]:
        """Get the response for an active session."""
        return self._active_sessions.get(session_id)
    
    def end_acquisition(self, session_id: str) -> bool:
        """
        End an acquisition session.
        
        Returns True if the session was ended.
        """
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
            return True
        return False
    
    # -------------------------------------------------------------------------
    # Evidence publication (for adapters to use)
    # -------------------------------------------------------------------------
    
    def publish_evidence(self, evidence: SensorEvidencePublication) -> Tuple[bool, str]:
        """
        Publish sensor evidence to the owning Modality.
        
        Returns:
            Tuple of (success, modality_name)
            
        SENSOR-LAW-001: The Sensors Interface shall admit acquired evidence into the owning Modality only.
        SENSOR-LAW-002: The Sensors Interface shall preserve sensor and adapter identity.
        """
        # Validate the evidence
        if not evidence.publication_identity or len(evidence.publication_identity) == 0:
            return False, "invalid_publication"
        
        # Track in history for inspection
        self._sensor_history.append({
            "event": "evidence_published",
            "timestamp": _time.time(),
            "publication_id": evidence.publication_identity,
            "session_id": evidence.acquisition_session,
            "source_sensor": evidence.source_sensor,
        })
        
        # Return the target modality (based on sensor kind)
        descriptor = self._sensors.get(evidence.source_sensor)
        if descriptor:
            modalities = list(descriptor.supported_modalities)
            return True, modalities[0] if modalities else "unknown"
        
        return True, "unknown"  # Default modality
    
    # -------------------------------------------------------------------------
    # Health and diagnostics
    # -------------------------------------------------------------------------
    
    def get_health(self) -> InterfaceHealth:
        """
        Get the current health status of the interface.
        
        Returns a snapshot of health metrics at this moment.
        """
        return InterfaceHealth(
            availability=1.0 if len(self._sensors) > 0 else 0.0,
            latency_ms=0.0,
            throughput_rps=float(len(self._sensor_history)) / max(1.0, _time.time() - 60),  # Last minute
            compatibility_health=InterfaceStatus.ACTIVE,
            authorization_health=InterfaceStatus.ACTIVE,
            subscription_health=InterfaceStatus.ACTIVE,
            publication_health=InterfaceStatus.ACTIVE,
            failure_rate=0.0,
        )
    
    def get_session_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the session and event history for inspection.
        
        This provides visibility into interface operations for debugging
        and audit purposes.
        """
        return list(self._sensor_history)[-limit:]
    
    def get_active_sessions(self) -> Dict[str, SensorAcquisitionResponse]:
        """Get all currently active acquisition sessions."""
        return dict(self._active_sessions)


__all__ = [
    # Descriptors
    "SensorKind",
    "PerceptionSensorDescriptor",
    
    # Acquisition
    "SensorAcquisitionRequest", 
    "SensorAcquisitionResponse",
    
    # Publication  
    "SensorEvidencePublication",
    
    # Interface implementation
    "SensorsInterface",
]