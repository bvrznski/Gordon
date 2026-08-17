# Knowledge-Perception Grounding - Observation Contract
# =======================================================

"""
Observation: The smallest externally grounded unit in the Knowledge-Perception Grounding layer.

This module defines observations as they are used in the grounding context.
An observation is raw evidence from the environment, without semantic interpretation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import uuid


# =============================================================================
# OBSERVATION SOURCES - Where does this observation come from?
# =============================================================================


class ObservationSourceKind(Enum):
    """
    Kinds of observation sources.
    
    CAMERA: Visual sensors (webcam, depth camera)
    MICROPHONE: Audio sensors
    SCREEN: Screen capture / visual display analysis
    CONSOLE: Terminal/console output
    SHELL: Shell command execution results
    KERNEL: Kernel events and system calls
    FILESYSTEM: File/directory changes
    NETWORK: Network activity
    ROBOTIC_SENSOR: Robotic platform sensors
    FUTURE_SENSOR: Future sensor modalities
    """
    
    CAMERA = "camera"
    MICROPHONE = "microphone"
    SCREEN = "screen"
    CONSOLE = "console"
    SHELL = "shell"
    KERNEL = "kernel"
    FILESYSTEM = "filesystem"
    NETWORK = "network"
    ROBOTIC_SENSOR = "robotic_sensor"
    FUTURE_SENSOR = "future_sensor"


# =============================================================================
# OBSERVATION TYPES - What kind of observation is this?
# =============================================================================


class ObservationType(Enum):
    """
    Types of observations (describing sensory content without semantic meaning).
    
    OBJECT: Visual object detection
    PERSON: Person-related observation
    SPEECH: Spoken language detected
    SOUND: Non-speech audio
    IMAGE: Static image
    VIDEO: Video stream segment
    TEXT: Textual content
    COMMAND: Command execution
    PROCESS: Process event (creation/termination)
    FILE: File system event
    DIRECTORY: Directory change
    NETWORK_EVENT: Network activity
    KERNEL_EVENT: Kernel-level event
    GUI_EVENT: GUI interaction
    UNKNOWN: Unspecified type
    """
    
    OBJECT = "object"
    PERSON = "person"
    SPEECH = "speech"
    SOUND = "sound"
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"
    COMMAND = "command"
    PROCESS = "process"
    FILE = "file"
    DIRECTORY = "directory"
    NETWORK_EVENT = "network_event"
    KERNEL_EVENT = "kernel_event"
    GUI_EVENT = "gui_event"
    UNKNOWN = "unknown"


# =============================================================================
# OBSERVATION - Canonical observation structure
# =============================================================================


@dataclass(frozen=True)
class Observation:
    """
    Raw evidence from a sensor interaction.
    
    Observations are the smallest externally grounded unit in the grounding layer.
    They represent sensory input without semantic interpretation.
    
    Fields:
        observation_identity:  Unique identifier for this observation
        
        modality:              Sensor modality (vision, audio, console, etc.)
        source_sensor:         Which sensor captured this
        timestamp_utc:         When the observation was acquired
        
        observation_payload:   Raw observation data
        confidence:            Sensor confidence in this observation
        uncertainty:           Known limitations
        
        provenance:            Complete origin tracking
    """
    
    # Identity (required)
    observation_identity: str
    
    # Acquisition context
    modality: str                  # vision, audio, console, shell, etc.
    source_sensor: str             # Sensor identifier
    timestamp_utc: float           # When acquired
    
    # Observation data
    observation_payload: bytes     # Raw sensor data
    confidence: float = 1.0       # Sensor confidence (0.0-1.0)
    uncertainty: float = 0.0      # Known limitations (independent measure)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate observation."""
        if not self.observation_identity:
            raise ValueError("observation_identity is required")
        if not self.timestamp_utc > 0:
            raise ValueError("timestamp_utc must be positive")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")
    
    @property
    def is_valid(self) -> bool:
        """Check if observation has minimal required data."""
        return (
            len(self.observation_identity) > 0 and
            self.timestamp_utc > 0.0 and
            len(self.modality) > 0 and
            len(self.source_sensor) > 0
        )
    
    @classmethod
    def from_payload(
        cls,
        payload: bytes,
        modality: str,
        source_sensor: str,
        timestamp_utc: Optional[float] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> "Observation":
        """
        Create an observation from raw payload data.
        
        Args:
            payload: Raw sensor output
            modality: Modality type (vision, audio, etc.)
            source_sensor: Which sensor captured this
            timestamp_utc: When it was captured (default: now)
            confidence: Sensor confidence 0.0-1.0
            uncertainty: Known limitations (independent measure)
            provenance: Origin tracking dict
        
        Returns:
            New Observation instance
        """
        return cls(
            observation_identity=f"observation:{uuid.uuid4().hex[:24]}",
            modality=modality,
            source_sensor=source_sensor,
            timestamp_utc=timestamp_utc or __import__('time').time(),
            observation_payload=payload,
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
            provenance=provenance or {"origin": "system"},
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert observation to dictionary for serialization."""
        return {
            "observation_identity": self.observation_identity,
            "modality": self.modality,
            "source_sensor": self.source_sensor,
            "timestamp_utc": self.timestamp_utc,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Observation":
        """Create observation from dictionary."""
        return cls(
            observation_identity=data.get("observation_identity", str(uuid.uuid4())),
            modality=data.get("modality", ""),
            source_sensor=data.get("source_sensor", ""),
            timestamp_utc=float(data.get("timestamp_utc", __import__('time').time())),
            observation_payload=b"",
            confidence=float(data.get("confidence", 1.0)),
            uncertainty=float(data.get("uncertainty", 0.0)),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# OBSERVATION SESSION - Grouped observations under a common context
# =============================================================================


@dataclass(frozen=True)
class ObservationSession:
    """
    Groups observations produced under a common context.
    
    Fields:
        session_identity:      Unique identifier for this session
        
        modality:              Primary modality of this session
        sensor:                Sensor identity (or list if multi-sensor)
        
        temporal_scope_start_utc: Start time of observation window
        temporal_scope_end_utc:   End time of observation window
        
        environment:           Contextual environment description
        
        observation_count:     Number of observations in this session
        
        confidence:            Confidence in the session grouping
        uncertainty:           Uncertainty about session boundaries
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    session_identity: str
    
    # Acquisition context
    modality: str                      # Primary modality
    sensor: str                        # Sensor identity
    temporal_scope_start_utc: float   # Start of window
    temporal_scope_end_utc: float     # End of window
    
    # Context
    environment: str = ""              # Environment description
    
    observation_count: int = 0         # Number of observations
    
    # Quality metrics (required)
    confidence: float = 1.0            # Session grouping confidence (0.0-1.0)
    uncertainty: float = 0.0           # Uncertainty about boundaries
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate observation session."""
        if not self.session_identity:
            raise ValueError("session_identity is required")
        if not self.temporal_scope_start_utc > 0 or not self.temporal_scope_end_utc > 0:
            raise ValueError("Temporal scope timestamps must be positive")
    
    @property
    def duration_sec(self) -> float:
        """Get session duration in seconds."""
        return self.temporal_scope_end_utc - self.temporal_scope_start_utc
    
    @classmethod
    def create(
        cls,
        modality: str,
        sensor: str,
        temporal_scope_start_utc: float,
        temporal_scope_end_utc: float,
        environment: str = "",
        observation_count: int = 0,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "ObservationSession":
        """Create a new observation session."""
        return cls(
            session_identity=f"observation_session:{uuid.uuid4().hex[:24]}",
            modality=modality,
            sensor=sensor,
            temporal_scope_start_utc=temporal_scope_start_utc,
            temporal_scope_end_utc=temporal_scope_end_utc,
            environment=environment,
            observation_count=observation_count,
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_identity": self.session_identity,
            "modality": self.modality,
            "sensor": self.sensor,
            "temporal_scope_start_utc": self.temporal_scope_start_utc,
            "temporal_scope_end_utc": self.temporal_scope_end_utc,
            "environment": self.environment,
            "observation_count": self.observation_count,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


# =============================================================================
# OBSERVATION SOURCE - Where does this observation come from?
# =============================================================================


@dataclass(frozen=True)
class ObservationSource:
    """
    Describes the source of observations.
    
    Fields:
        source_identity:       Unique identifier for this source
        
        source_kind:           What kind of source is this?
        
        sensor_identity:       Which sensor captures from this source?
        sensor_revision:       Revision of the sensor configuration
        
        acquisition_pipeline:  Description of the capture pipeline
        
        environment:           Environment context for observations
        
        reliability:           How reliable is this source? (0.0-1.0)
        
        confidence:            Confidence in this source description
        uncertainty:           Uncertainty about source capabilities
        
        provenance:            Origin tracking
    """
    
    # Identity (required)
    source_identity: str
    
    # Source kind (required)
    source_kind: ObservationSourceKind
    
    # Sensor info
    sensor_identity: str
    sensor_revision: int = 1
    
    # Capture description
    acquisition_pipeline: str = ""
    
    # Context
    environment: str = ""
    
    # Quality metrics
    reliability: float = 1.0           # Source reliability (0.0-1.0)
    
    confidence: float = 1.0            # Confidence in source description (0.0-1.0)
    uncertainty: float = 0.0           # Uncertainty about capabilities
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate observation source."""
        if not self.source_identity:
            raise ValueError("source_identity is required")
        if not 0.0 <= self.reliability <= 1.0:
            raise ValueError(f"Reliability must be 0.0-1.0, got {self.reliability}")
    
    @classmethod
    def create(
        cls,
        source_kind: ObservationSourceKind,
        sensor_identity: str,
        sensor_revision: int = 1,
        acquisition_pipeline: str = "",
        environment: str = "",
        reliability: float = 1.0,
    ) -> "ObservationSource":
        """Create a new observation source."""
        return cls(
            source_identity=f"observation_source:{uuid.uuid4().hex[:24]}",
            source_kind=source_kind,
            sensor_identity=sensor_identity,
            sensor_revision=sensor_revision,
            acquisition_pipeline=acquisition_pipeline,
            environment=environment,
            reliability=max(0.0, min(1.0, float(reliability))),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert source to dictionary."""
        return {
            "source_identity": self.source_identity,
            "source_kind": self.source_kind.value,
            "sensor_identity": self.sensor_identity,
            "sensor_revision": self.sensor_revision,
            "acquisition_pipeline": self.acquisition_pipeline,
            "environment": self.environment,
            "reliability": self.reliability,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


__all__ = [
    "ObservationSourceKind",
    "ObservationType",
    "Observation",
    "ObservationSession",
    "ObservationSource",
]