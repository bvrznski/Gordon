# Vision Stream - Phase 3.11.8 Perception Streams
# ==============================================================================

"""
Vision Stream: Semantic transport for visual perceptual observations.

The Vision Stream transports immutable visual observations from the perception
system to networks, capabilities, and systems. It preserves temporal ordering,
confidence metrics, provenance, and coordinate frame information.

Architecture:
    Visual Sensor → Preprocessor → Feature Extractor → Detector → Vision Stream
                                                        ↓
                                               Networks (Workspace/Salience/Executive)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import time

# Import core stream infrastructure
from gordon_system.src.agent.components.core.streams import (
    StreamId,
    StreamGenerationId,
    StreamRecord,
    StreamCommit,
    StreamPosition,
    ProducerId,
    CorrelationId,
    ArtifactReference,
)

# Import perception streams core types
from .__init__ import (
    Modality,
    PerceptId,
    CoordinateFrame,
    TemporalWindow,
    PerceptProvenance,
    PerceptRecordKind,
    make_vision_stream_id,
    PerceptRecord,
)


class VisualPerceptKind(Enum):
    """Types of visual percepts."""
    FRAME_ACQUIRED = "frame_acquired"           # Raw frame capture
    OBJECT_DETECTED = "object_detected"         # Object detection result
    SEGMENTATION_RESULT = "segmentation_result" # Segmentation mask
    FEATURE_EXTRACTED = "feature_extracted"     # Feature vector
    FACE_RECOGNIZED = "face_recognized"         # Face recognition result
    DEPTH_ESTIMATED = "depth_estimated"         # Depth map
    MOTION_TRACKED = "motion_tracked"           # Motion tracking


@dataclass(frozen=True)
class VisualPerceptData:
    """
    Data specific to visual perception observations.
    
    This contains modalities-specific fields while the base PerceptRecord
    handles generic semantic transport.
    """
    
    frame_id: Optional[str] = None  # Unique frame identifier
    camera_source: Optional[str] = None  # Camera ID or source reference
    
    # Detection data (if applicable)
    bounding_box: Optional[Tuple[float, float, float, float]] = None  # x, y, w, h
    class_label: Optional[str] = None
    detection_confidence: Optional[float] = None
    
    # Feature data (if applicable)
    feature_vector: Optional[List[float]] = None
    feature_dimension: Optional[int] = None
    
    # Tracking data (if applicable)
    track_id: Optional[int] = None  # Object tracking ID
    position_3d: Optional[Tuple[float, float, float]] = None  # World coordinates


@dataclass(frozen=True)
class VisionStreamConfig:
    """Configuration for the vision stream."""
    stream_id: StreamId = field(default_factory=make_vision_stream_id)
    
    # Retention policy
    max_records: int = 10_000
    retention_seconds: int = 3600  # 1 hour
    
    # Default coordinate frame
    default_coordinate_frame: CoordinateFrame = field(
        default_factory=lambda: CoordinateFrame(name="world", origin=(0.0, 0.0, 0.0))
    )
    
    # Temporal window for new records
    default_temporal_window: TemporalWindow = TemporalWindow.IMMEDIATE


# =============================================================================
# VISION STREAM PUBLISHER
# =============================================================================

class VisionStreamPublisher:
    """
    Publisher for visual percept observations to the vision stream.
    
    Usage:
        publisher = VisionStreamPublisher()
        
        # Publish a frame acquisition
        await publisher.publish_frame(
            frame_data=frame_bytes,
            camera_source="camera_1",
            coordinate_frame=CoordinateFrame(name="world")
        )
        
        # Publish detection results
        await publisher.publish_detection(
            frame_id=frame_id,
            bounding_box=(x, y, w, h),
            class_label="person",
            confidence=0.95
        )
    """
    
    def __init__(self, config: Optional[VisionStreamConfig] = None):
        self.config = config or VisionStreamConfig()
        self._current_generation_id: Optional[StreamGenerationId] = None
    
    async def initialize(self) -> StreamGenerationId:
        """Initialize the publisher and get the current generation."""
        # In a real implementation, this would connect to the stream registry
        self._current_generation_id = StreamGenerationId(
            stream_id=self.config.stream_id,
            number=1
        )
        return self._current_generation_id
    
    async def publish_frame(
        self,
        frame_data: Any,  # Frame buffer or reference
        camera_source: Optional[str] = None,
        timestamp_utc: Optional[float] = None,
        coordinate_frame: Optional[CoordinateFrame] = None,
        correlation_id: Optional[CorrelationId] = None,
    ) -> StreamCommit:
        """
        Publish a frame acquisition event.
        
        Args:
            frame_data: The frame data (bytes, file path, or artifact reference)
            camera_source: ID of the camera that captured this frame
            timestamp_utc: When the frame was captured
            coordinate_frame: Spatial reference frame for observations
            correlation_id: Links related percepts across modalities
        
        Returns:
            StreamCommit containing the published record
        """
        acquisition_time = timestamp_utc or time.time()
        
        percept_data = VisualPerceptData(
            camera_source=camera_source,
            bounding_box=None,
        )
        
        return await self._publish_percept(
            kind=VisualPerceptKind.FRAME_ACQUIRED,
            observation={"frame_data_ref": str(frame_data)},
            acquisition_time=acquisition_time,
            coordinate_frame=coordinate_frame or self.config.default_coordinate_frame,
            correlation_id=correlation_id,
            percept_data=percept_data,
        )
    
    async def publish_detection(
        self,
        frame_id: str,
        bounding_box: Tuple[float, float, float, float],
        class_label: str,
        confidence: float,
        timestamp_utc: Optional[float] = None,
        track_id: Optional[int] = None,
        correlation_id: Optional[CorrelationId] = None,
    ) -> StreamCommit:
        """
        Publish an object detection result.
        
        Args:
            frame_id: ID of the frame this detection applies to
            bounding_box: (x, y, width, height) in normalized coordinates
            class_label: Detected object class
            confidence: Detection confidence (0.0 to 1.0)
            timestamp_utc: When detection was made
            track_id: Object tracking ID if applicable
            correlation_id: Links to related percepts
        
        Returns:
            StreamCommit containing the published record
        """
        acquisition_time = timestamp_utc or time.time()
        
        percept_data = VisualPerceptData(
            frame_id=frame_id,
            bounding_box=bounding_box,
            class_label=class_label,
            detection_confidence=confidence,
            track_id=track_id,
        )
        
        return await self._publish_percept(
            kind=VisualPerceptKind.OBJECT_DETECTED,
            observation={
                "frame_id": frame_id,
                "bounding_box": bounding_box,
                "class_label": class_label,
                "detection_confidence": confidence,
                **({"track_id": track_id} if track_id is not None else {}),
            },
            acquisition_time=acquisition_time,
            coordinate_frame=self.config.default_coordinate_frame,
            correlation_id=correlation_id,
            percept_data=percept_data,
        )
    
    async def _publish_percept(
        self,
        kind: VisualPerceptKind,
        observation: Dict[str, Any],
        acquisition_time: float,
        coordinate_frame: CoordinateFrame,
        correlation_id: Optional[CorrelationId],
        percept_data: VisualPerceptData,
    ) -> StreamCommit:
        """Internal method to publish a percept record."""
        if self._current_generation_id is None:
            raise RuntimeError("Publisher not initialized. Call initialize() first.")
        
        # Create provenance
        provenance = PerceptProvenance(
            acquisition_time_utc=acquisition_time,
            publication_time_utc=time.time(),
            preprocessing_steps=("color_conversion", "normalization"),
            feature_extraction_steps=tuple(),  # Will be filled by pipeline steps
            detection_method=kind.value,
        )
        
        # Create percept record (would be integrated with core stream infrastructure)
        percept = PerceptRecord(
            percept_id=PerceptId.generate(),
            record_id=None,  # Assigned at commit
            stream_id=self.config.stream_id,
            modality=Modality.VISION,
            record_kind=PerceptRecordKind.OBJECT_DETECTED if kind == VisualPerceptKind.OBJECT_DETECTED else PerceptRecordKind.FRAME_ACQUIRED,
            acquisition_time_utc=acquisition_time,
            publication_time_utc=time.time(),
            generation_id=self._current_generation_id,
            sequence_number=0,  # Assigned at commit
            observation=observation,
            confidence=percept_data.detection_confidence or 1.0,
            uncertainty=1.0 - (percept_data.detection_confidence or 0.0),
            coordinate_frame=coordinate_frame,
            temporal_window=self.config.default_temporal_window,
            provenance=provenance,
            correlation_id=correlation_id,
        )
        
        # In a real implementation, this would:
        # 1. Build the record with proper IDs
        # 2. Commit to stream registry
        # 3. Return commit result
        
        return StreamCommit(
            commit_id=None,  # Would be generated by core infrastructure
            stream_id=self.config.stream_id,
            generation_id=self._current_generation_id,
            records=(),  # Would contain the actual records
            committed_at_utc=time.time(),
            commit_hash="",
            record_count=0,
        )


# =============================================================================
# VISION STREAM SUBSCRIBER
# =============================================================================

class VisionStreamSubscriber:
    """
    Subscriber for visual percept observations from the vision stream.
    
    Usage:
        subscriber = VisionStreamSubscriber()
        
        # Subscribe from beginning
        records = await subscriber.subscribe(from_position=None)
        
        # Or subscribe from a specific position (e.g., after checkpoint recovery)
        records = await subscriber.subscribe(from_position=checkpoint.position)
    """
    
    def __init__(self, config: Optional[VisionStreamConfig] = None):
        self.config = config or VisionStreamConfig()
        self._current_generation_id: Optional[StreamGenerationId] = None
        self._last_position: Optional[StreamPosition] = None
    
    async def initialize(self) -> StreamGenerationId:
        """Initialize the subscriber and get the current generation."""
        self._current_generation_id = StreamGenerationId(
            stream_id=self.config.stream_id,
            number=1
        )
        return self._current_generation_id
    
    async def subscribe(
        self,
        from_position: Optional[StreamPosition] = None,
        to_position: Optional[StreamPosition] = None,
    ) -> Tuple[PerceptRecord, ...]:
        """
        Subscribe to visual percept observations.
        
        Args:
            from_position: Start position (inclusive), or None for beginning
            to_position: End position (exclusive), or None for all
        
        Returns:
            Tuple of visual percept records in order
        """
        # In a real implementation, this would:
        # 1. Query the stream storage for records in the specified range
        # 2. Transform raw StreamRecords into PerceptRecords
        # 3. Return them
        
        return ()
    
    def get_checkpoint(self) -> Optional[StreamPosition]:
        """Get current subscription position for checkpointing."""
        return self._last_position
    
    async def update_position(self, new_position: StreamPosition) -> None:
        """Update the subscriber's position (for checkpointing)."""
        self._last_position = new_position


# =============================================================================
# SYNCHRONIZATION UTILITIES
# ==============================================================================

def create_synchronization_marker(
    sync_time_utc: float,
    visual_position: Optional[StreamPosition] = None,
    audio_position: Optional[StreamPosition] = None,
) -> "SynchronizationMarker":
    """
    Create a synchronization marker for cross-modal alignment.
    
    This marker can be used to correlate visual observations with auditory
    observations that occurred at approximately the same time.
    
    Args:
        sync_time_utc: Reference time for synchronization
        visual_position: Position in visual stream (if available)
        audio_position: Position in audition stream (if available)
    
    Returns:
        SynchronizationMarker for aligning modalities
    """
    from .__init__ import SynchronizationMarker
    
    positions = {}
    if visual_position is not None:
        positions[make_vision_stream_id()] = visual_position
    if audio_position is not None:
        # Import audition stream ID
        positions["perception:sensory-auditory"] = audio_position
    
    return SynchronizationMarker(
        sync_time_utc=sync_time_utc,
        stream_positions=positions,
    )


def group_frame_percepts(
    percepts: Tuple[PerceptRecord, ...],
    max_temporal_offset_ms: float = 100.0,
) -> Tuple["FrameGroup", ...]:
    """
    Group percepts captured within a temporal window.
    
    Args:
        percepts: Percepts to group (should be sorted by acquisition time)
        max_temporal_offset_ms: Maximum time difference for grouping (milliseconds)
    
    Returns:
        Tuple of frame groups
    """
    from .__init__ import FrameGroup
    
    if not percepts:
        return ()
    
    groups = []
    current_group = [percepts[0]]
    group_start_time = percepts[0].acquisition_time_utc
    
    for percept in percepts[1:]:
        time_diff_ms = (percept.acquisition_time_utc - group_start_time) * 1000
        
        if time_diff_ms <= max_temporal_offset_ms:
            current_group.append(percept)
        else:
            # Finalize current group
            groups.append(FrameGroup(
                group_id=str(len(groups)),
                capture_time_utc=group_start_time,
                members=tuple(current_group),
                synchronization_quality=1.0 - (time_diff_ms / max_temporal_offset_ms) * 0.5,
            ))
            
            # Start new group
            current_group = [percept]
            group_start_time = percept.acquisition_time_utc
    
    # Finalize last group
    if current_group:
        groups.append(FrameGroup(
            group_id=str(len(groups)),
            capture_time_utc=group_start_time,
            members=tuple(current_group),
            synchronization_quality=1.0,
        ))
    
    return tuple(groups)