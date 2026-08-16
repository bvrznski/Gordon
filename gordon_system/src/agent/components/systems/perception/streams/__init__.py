# Perception Streams - Phase 3.11.8 Canonical Semantic Streaming Architecture
# ==============================================================================

"""
Perception Streams: Semantic transport layer for immutable perceptual observations.

This module implements the canonical semantic stream architecture for all Perception
subsystems as specified in Phase 3.11.8.

Perception Systems own:
    - acquisition
    - preprocessing
    - feature extraction
    - detection
    - segmentation
    - recognition
    - tracking
    - localization
    - alignment
    - calibration

Perception Streams own:
    - publication
    - ordering
    - transport
    - replay
    - checkpointing
    - subscriptions
    - delivery
    - observability

Architectural Position:
    Sensor → Perception System → Percept → Perception Stream → Networks → Capabilities → Systems

Perception Streams transport immutable perceptual observations.

They never answer: What should be believed? What should be remembered?
                 What action should be taken?

They always answer:
    - What has been perceived?
    - When?
    - By whom?
    - At what confidence?
    - Under which context?
    - From which modality?
    - With which provenance?
    - Under which temporal ordering?
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import time
import uuid

# Import core stream infrastructure (Phase 3.11.x)
from gordon_system.src.agent.components.core.streams import (
    StreamId,
    StreamKind,
    StreamRecordId,
    StreamGenerationId,
    StreamRecord,
    StreamCommit,
    StreamPosition,
    ProducerId,
    CorrelationId,
    ArtifactReference,
    ArtifactTypeId,
    RecordType,
    RecordStatus,
    StreamRecordBuilder,
    CommitAuthority,
)
from gordon_system.src.agent.components.core.streams import dataclass_replace

# =============================================================================
# PERCEPT RECORD TYPES - Immutable Semantic Records
# =============================================================================


class PerceptRecordKind(Enum):
    """Categories of percept records."""
    FRAME_ACQUIRED = "frame_acquired"         # Visual/audio frame captured
    OBJECT_DETECTED = "object_detected"       # Object detected in scene
    SPEECH_DECODED = "speech_decoded"         # Speech converted to text
    CONSOLE_EVENT = "console_event"           # Console/terminal event
    ENVIRONMENTAL_EVENT = "environmental_event"  # Environmental sensor reading
    SENSOR_CALIBRATED = "sensor_calibrated"   # Sensor calibration update
    FEATURE_EXTRACTED = "feature_extracted"   # Feature vector extracted
    TRANSLATION_COMPLETED = "translation_completed"  # Translation result


class TemporalWindow(Enum):
    """Temporal window classification for percepts."""
    IMMEDIATE = "immediate"           # Real-time capture (ms)
    SHORT_TERM = "short_term"         # Recent history (seconds)
    MEDIUM_TERM = "medium_term"       # Recent session (minutes)
    LONG_TERM = "long_term"           # Extended period (hours/days)


class Modality(Enum):
    """Sensory modalities supported by perception streams."""
    VISION = "vision"
    AUDITION = "audition"
    SPEECH = "speech"
    CONSOLE = "console"
    ENVIRONMENTAL = "environmental"
    INTERNAL_SENSOR = "internal_sensor"
    INTERMODAL = "intermodal"
    TRANSLATION = "translation"


@dataclass(frozen=True)
class PerceptId:
    """Unique identifier for a percept."""
    value: str
    
    @classmethod
    def generate(cls) -> "PerceptId":
        """Generate a new unique percept ID."""
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_stream_position(
        cls,
        stream_id: StreamId,
        position: StreamPosition
    ) -> "PerceptId":
        """Create percept ID from stream position."""
        return cls(
            value=f"percept:{stream_id.value}:{position.generation_id.value}:{position.sequence_number}"
        )


@dataclass(frozen=True)
class CoordinateFrame:
    """Reference frame for spatial coordinates."""
    name: str
    origin: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    orientation: Tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0)  # quaternion


@dataclass(frozen=True)
class PerceptRecordMetadata:
    """Metadata for a percept record."""
    modality: Modality
    coordinate_frame: Optional[CoordinateFrame] = None
    temporal_window: TemporalWindow = TemporalWindow.IMMEDIATE
    confidence: float = 1.0
    uncertainty: float = 0.0
    source_reference: Optional[str] = None


@dataclass(frozen=True)
class PerceptProvenance:
    """Provenance information for a percept."""
    acquisition_time_utc: float
    publication_time_utc: float
    preprocessing_steps: Tuple[str, ...] = field(default_factory=tuple)
    feature_extraction_steps: Tuple[str, ...] = field(default_factory=tuple)
    detection_method: Optional[str] = None


# =============================================================================
# PERCEPT RECORD - Immutable Semantic Unit for Perception
# =============================================================================

@dataclass(frozen=True)
class PerceptRecord:
    """
    Immutable percept record representing an observation from the perception system.
    
    A percept record contains:
        - Identity (percept_id, stream position)
        - Observation (what was perceived)
        - Context (confidence, uncertainty, provenance)
        - Temporal information (when perceived)
    
    Percepts are immutable after creation - new percepts represent new observations.
    """
    
    # Identity
    percept_id: PerceptId
    record_id: StreamRecordId
    stream_id: StreamId
    
    # Modality and type
    modality: Modality
    record_kind: PerceptRecordKind
    
    # Timestamps (distinct temporal semantics)
    acquisition_time_utc: float  # When sensor captured the input
    publication_time_utc: float = field(default_factory=time.time)  # When record was published
    
    # Temporal ordering
    generation_id: StreamGenerationId
    sequence_number: int
    
    # Observation payload
    observation: Dict[str, Any]  # The actual perceptual data
    
    # Context and confidence
    confidence: float = 1.0       # Confidence in the perception (0.0 to 1.0)
    uncertainty: float = 0.0      # Estimated uncertainty of the observation
    
    # Spatial reference (optional)
    coordinate_frame: Optional[CoordinateFrame] = None
    
    # Temporal window
    temporal_window: TemporalWindow = TemporalWindow.IMMEDIATE
    
    # Provenance
    provenance: PerceptProvenance
    
    # Semantic context
    correlation_id: Optional[CorrelationId] = None  # Groups related percepts
    
    # Artifact reference (for large payloads)
    artifact_reference: Optional[ArtifactReference] = None
    
    @classmethod
    def create_builder(
        cls,
        stream_id: StreamId,
        generation_id: StreamGenerationId,
        modality: Modality,
    ) -> "PerceptRecordBuilder":
        """Create a new percept record builder."""
        return PerceptRecordBuilder(stream_id, generation_id, modality)
    
    @property
    def position(self) -> StreamPosition:
        """Get the stream position of this percept."""
        return StreamPosition(
            stream_id=self.stream_id,
            generation_id=self.generation_id,
            sequence_number=self.sequence_number
        )
    
    def with_correlation(self, correlation_id: CorrelationId) -> "PerceptRecord":
        """Return a copy with correlation ID set."""
        return dataclass_replace(self, correlation_id=correlation_id)
    
    def to_stream_record(
        self,
        record_kind: PerceptRecordKind = PerceptRecordKind.FRAME_ACQUIRED
    ) -> StreamRecord:
        """Convert to generic stream record for transport."""
        payload = {
            "percept_id": self.percept_id.value,
            "modality": self.modality.value,
            "record_kind": record_kind.value,
            "observation": self.observation,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "provenance": {
                "acquisition_time_utc": self.provenance.acquisition_time_utc,
                "publication_time_utc": self.provenance.publication_time_utc,
                "preprocessing_steps": list(self.provenance.preprocessing_steps),
                "feature_extraction_steps": list(self.provenance.feature_extraction_steps),
            },
        }
        
        return StreamRecord(
            record_id=self.record_id,
            status=RecordStatus.COMMITTED,
            sequence_number=self.sequence_number,
            generation_id=self.generation_id,
            stream_id=self.stream_id,
            event_time_utc=self.acquisition_time_utc,
            created_at_utc=self.publication_time_utc,
            payload=payload,
            artifact_reference=self.artifact_reference,
        )


# =============================================================================
# PERCEPT RECORD BUILDER - Mutable Construction
# =============================================================================

class PerceptRecordBuilder:
    """
    Mutable builder for constructing percept records.
    
    Usage:
        builder = PerceptRecordBuilder(stream_id, generation_id, modality)
        builder.set_observation(data)
        builder.set_confidence(0.95)
        builder.set_correlation(correlation_id)
        percept = builder.build()
    """
    
    def __init__(self, stream_id: StreamId, generation_id: StreamGenerationId, modality: Modality):
        self.stream_id = stream_id
        self.generation_id = generation_id
        self.modality = modality
        
        # Percept-specific fields
        self.percept_id: Optional[PerceptId] = None
        self.record_kind: PerceptRecordKind = PerceptRecordKind.FRAME_ACQUIRED
        self.acquisition_time_utc: float = 0.0  # Will be set in build()
        self.observation: Dict[str, Any] = {}
        self.confidence: float = 1.0
        self.uncertainty: float = 0.0
        self.coordinate_frame: Optional[CoordinateFrame] = None
        self.temporal_window: TemporalWindow = TemporalWindow.IMMEDIATE
        
        # Provenance
        self.preprocessing_steps: Tuple[str, ...] = ()
        self.feature_extraction_steps: Tuple[str, ...] = ()
        self.detection_method: Optional[str] = None
        
        # Correlation
        self.correlation_id: Optional[CorrelationId] = None
        
        # Internal state
        self._built: bool = False
    
    def set_percept_id(self, percept_id: PerceptId) -> "PerceptRecordBuilder":
        """Set the percept ID."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.percept_id = percept_id
        return self
    
    def set_record_kind(self, record_kind: PerceptRecordKind) -> "PerceptRecordBuilder":
        """Set the record kind (type of observation)."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.record_kind = record_kind
        return self
    
    def set_observation(self, observation: Dict[str, Any]) -> "PerceptRecordBuilder":
        """Set the perceptual observation data."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.observation = dict(observation)
        return self
    
    def set_acquisition_time(self, utc_time: float) -> "PerceptRecordBuilder":
        """Set the acquisition timestamp (when sensor captured input)."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.acquisition_time_utc = utc_time
        return self
    
    def set_confidence(self, confidence: float) -> "PerceptRecordBuilder":
        """Set the confidence level (0.0 to 1.0)."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.confidence = max(0.0, min(1.0, confidence))
        return self
    
    def set_uncertainty(self, uncertainty: float) -> "PerceptRecordBuilder":
        """Set the estimated uncertainty."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.uncertainty = max(0.0, uncertainty)
        return self
    
    def set_coordinate_frame(self, frame: CoordinateFrame) -> "PerceptRecordBuilder":
        """Set the spatial coordinate frame reference."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.coordinate_frame = frame
        return self
    
    def set_temporal_window(self, window: TemporalWindow) -> "PerceptRecordBuilder":
        """Set the temporal window classification."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.temporal_window = window
        return self
    
    def add_preprocessing_step(self, step: str) -> "PerceptRecordBuilder":
        """Add a preprocessing step to provenance."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.preprocessing_steps = (*self.preprocessing_steps, step)
        return self
    
    def add_feature_extraction_step(self, step: str) -> "PerceptRecordBuilder":
        """Add a feature extraction step to provenance."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.feature_extraction_steps = (*self.feature_extraction_steps, step)
        return self
    
    def set_detection_method(self, method: str) -> "PerceptRecordBuilder":
        """Set the detection/identification method used."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.detection_method = method
        return self
    
    def set_correlation(self, correlation_id: CorrelationId) -> "PerceptRecordBuilder":
        """Set correlation ID for grouping related percepts."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.correlation_id = correlation_id
        return self
    
    def build(self) -> PerceptRecord:
        """
        Build the immutable percept record.
        
        This consumes the builder - it cannot be reused after this call.
        """
        if self._built:
            raise ValueError("Cannot build again from built builder")
        
        # Generate IDs if not set
        percept_id = self.percept_id or PerceptId.generate()
        record_id = StreamRecordId(self.generation_id, 0)  # Will be assigned at commit
        
        # Create provenance
        provenance = PerceptProvenance(
            acquisition_time_utc=self.acquisition_time_utc,
            publication_time_utc=time.time(),
            preprocessing_steps=self.preprocessing_steps,
            feature_extraction_steps=self.feature_extraction_steps,
            detection_method=self.detection_method,
        )
        
        percept = PerceptRecord(
            percept_id=percept_id,
            record_id=record_id,
            stream_id=self.stream_id,
            modality=self.modality,
            record_kind=self.record_kind,
            acquisition_time_utc=self.acquisition_time_utc,
            publication_time_utc=time.time(),
            generation_id=self.generation_id,
            sequence_number=0,  # Will be assigned at commit
            observation=dict(self.observation),
            confidence=self.confidence,
            uncertainty=self.uncertainty,
            coordinate_frame=self.coordinate_frame,
            temporal_window=self.temporal_window,
            provenance=provenance,
            correlation_id=self.correlation_id,
        )
        
        self._built = True
        return percept


# =============================================================================
# STREAM IDENTIFIERS - Perception Stream ID Utilities
# =============================================================================

def make_vision_stream_id() -> StreamId:
    """Create vision stream identifier."""
    return StreamId.from_parts("perception", "sensory-visual")


def make_audition_stream_id() -> StreamId:
    """Create audition stream identifier."""
    return StreamId.from_parts("perception", "sensory-auditory")


def make_speech_stream_id() -> StreamId:
    """Create speech stream identifier."""
    return StreamId.from_parts("perception", "speech-decoding")


def make_console_stream_id() -> StreamId:
    """Create console stream identifier."""
    return StreamId.from_parts("perception", "console-events")


def make_environmental_stream_id() -> StreamId:
    """Create environmental stream identifier."""
    return StreamId.from_parts("perception", "environmental-sensors")


def make_internal_sensor_stream_id() -> StreamId:
    """Create internal sensor stream identifier."""
    return StreamId.from_parts("perception", "internal-sensors")


def make_intermodal_stream_id() -> StreamId:
    """Create intermodal synchronization stream identifier."""
    return StreamId.from_parts("perception", "intermodal-synchronization")


def make_translation_stream_id() -> StreamId:
    """Create translation stream identifier."""
    return StreamId.from_parts("perception", "translation-results")


def get_modality_for_stream(stream_id: StreamId) -> Optional[Modality]:
    """Determine modality from stream ID."""
    name = stream_id.value
    if "visual" in name or "vision" in name:
        return Modality.VISION
    elif "auditory" in name or "audition" in name:
        return Modality.AUDITION
    elif "speech" in name:
        return Modality.SPEECH
    elif "console" in name:
        return Modality.CONSOLE
    elif "environmental" in name:
        return Modality.ENVIRONMENTAL
    elif "internal" in name:
        return Modality.INTERNAL_SENSOR
    elif "intermodal" in name:
        return Modality.INTERMODAL
    elif "translation" in name:
        return Modality.TRANSLATION
    return None


# =============================================================================
# SYNCHRONIZATION INFRASTRUCTURE - Multi-Modal Alignment
# =============================================================================

@dataclass(frozen=True)
class SynchronizationMarker:
    """Temporal synchronization marker for cross-modal alignment."""
    sync_time_utc: float  # Reference time for synchronization
    stream_positions: Dict[StreamId, StreamPosition]  # Position in each modality stream
    correlation_id: Optional[CorrelationId] = None  # Links related percepts


@dataclass(frozen=True)
class FrameGroup:
    """Group of percepts captured at approximately the same time."""
    group_id: str
    capture_time_utc: float
    members: Tuple[PerceptRecord, ...]
    synchronization_quality: float = 1.0  # 0.0 to 1.0


@dataclass(frozen=True)
class CausalReference:
    """Causal reference between percepts across modalities."""
    cause_percept_id: PerceptId
    effect_percept_id: PerceptId
    temporal_offset_ms: float  # Time difference in milliseconds
    confidence: float = 1.0


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core types
    "PerceptRecord",
    "PerceptRecordKind",
    "Modality",
    "CoordinateFrame",
    "TemporalWindow",
    
    # Identity
    "PerceptId",
    
    # Provenance
    "PerceptProvenance",
    
    # Builder
    "PerceptRecordBuilder",
    
    # Stream identifiers
    "make_vision_stream_id",
    "make_audition_stream_id",
    "make_speech_stream_id",
    "make_console_stream_id",
    "make_environmental_stream_id",
    "make_internal_sensor_stream_id",
    "make_intermodal_stream_id",
    "make_translation_stream_id",
    "get_modality_for_stream",
    
    # Synchronization
    "SynchronizationMarker",
    "FrameGroup",
    "CausalReference",
]