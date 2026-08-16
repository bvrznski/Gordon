# Perception Observation - Phase 5.2 Raw Evidence
# ================================================

"""
Perception Observation: Raw evidence from sensor interaction.

An Observation is the smallest externally grounded interaction between Gordon
and its environment. Observations are raw evidence, not interpretation.

Observation Laws:
    OBSERVATION-LAW-001: Observations represent externally grounded evidence only
    OBSERVATION-LAW-002: Observations never infer semantic meaning
    OBSERVATION-LAW-003: Observations preserve acquisition timestamps
    OBSERVATION-LAW-004: Observations preserve acquisition provenance
    OBSERVATION-LAW-005: Observations remain immutable after acquisition
    OBSERVATION-LAW-006: Observations remain reproducible when replayed
    OBSERVATION-LAW-007: Observation history remains inspectable
    OBSERVATION-LAW-008: Observation acquisition remains deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class Observation:
    """
    Raw evidence from a sensor interaction.
    
    Properties:
        identity:          Unique identifier for this observation
        timestamp_utc:     When the observation was acquired
        modality:          Modality of the sensor (vision, audio, etc.)
        sensor_id:         ID of the sensor that captured this
        signal_data:       Raw signal data (bytes, pixels, etc.)
        quality:           Quality score 0.0-1.0
        duration_sec:      Duration of observation in seconds
        
        provenance:        Complete origin tracking
    """
    
    identity: str                      # Unique identifier
    timestamp_utc: float               # When acquired
    
    modality: str                      # vision, audio, speech, console, etc.
    sensor_id: str                     # ID of the capturing sensor
    signal_data: bytes                 # Raw signal data
    
    quality: float = 1.0              # Quality score (0.0-1.0)
    duration_sec: float = 0.0         # Duration in seconds
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if observation has minimal required data."""
        return (
            len(self.identity) > 0 and
            self.timestamp_utc > 0.0 and
            len(self.modality) > 0 and
            len(self.sensor_id) > 0
        )
    
    @classmethod
    def from_signal(
        cls,
        signal_data: bytes,
        modality: str,
        sensor_id: str,
        timestamp_utc: Optional[float] = None,
        duration_sec: float = 0.0,
        quality: float = 1.0,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> "Observation":
        """
        Create an observation from raw signal data.
        
        Args:
            signal_data: Raw sensor output
            modality: Modality type (vision, audio, etc.)
            sensor_id: Which sensor captured this
            timestamp_utc: When it was captured (default: now)
            duration_sec: How long the observation lasted
            quality: Quality score 0.0-1.0
            provenance: Origin tracking dict
            
        Returns:
            New Observation instance
        """
        return cls(
            identity=f"obs:{uuid.uuid4().hex[:24]}",
            timestamp_utc=timestamp_utc or time.time(),
            modality=modality,
            sensor_id=sensor_id,
            signal_data=signal_data,
            quality=quality,
            duration_sec=duration_sec,
            provenance=provenance or {"origin": "system"},
        )


class ObservationBuilder:
    """
    Mutable builder for constructing observations.
    
    Usage:
        obs = (ObservationBuilder()
            .set_modality("vision")
            .set_sensor_id("camera_front")
            .set_signal_data(data)
            .build())
    """
    
    def __init__(self):
        self._identity: str = f"obs:{uuid.uuid4().hex[:24]}"
        self._timestamp_utc: float = time.time()
        self._modality: str = "unknown"
        self._sensor_id: str = "system"
        self._signal_data: bytes = b""
        self._quality: float = 1.0
        self._duration_sec: float = 0.0
        self._provenance: Dict[str, Any] = {"origin": "system"}
    
    def set_identity(self, identity: str) -> "ObservationBuilder":
        """Set the observation ID."""
        self._identity = identity
        return self
    
    def set_timestamp_utc(self, timestamp: float) -> "ObservationBuilder":
        """Set acquisition timestamp."""
        self._timestamp_utc = timestamp
        return self
    
    def set_modality(self, modality: str) -> "ObservationBuilder":
        """Set the sensor modality."""
        self._modality = modality
        return self
    
    def set_sensor_id(self, sensor_id: str) -> "ObservationBuilder":
        """Set the sensor ID."""
        self._sensor_id = sensor_id
        return self
    
    def set_signal_data(self, data: bytes) -> "ObservationBuilder":
        """Set raw signal data."""
        self._signal_data = data
        return self
    
    def set_quality(self, quality: float) -> "ObservationBuilder":
        """Set quality score 0.0-1.0."""
        if not 0.0 <= quality <= 1.0:
            raise ValueError(f"Quality must be 0.0-1.0, got {quality}")
        self._quality = quality
        return self
    
    def set_duration_sec(self, duration: float) -> "ObservationBuilder":
        """Set observation duration in seconds."""
        self._duration_sec = duration
        return self
    
    def set_provenance(self, provenance: Dict[str, Any]) -> "ObservationBuilder":
        """Set provenance tracking data."""
        self._provenance = provenance
        return self
    
    def build(self) -> Observation:
        """Build an immutable Observation."""
        if not self._signal_data and len(self._modality) == 0:
            raise ValueError("signal_data or modality is required")
        return Observation(
            identity=self._identity,
            timestamp_utc=self._timestamp_utc,
            modality=self._modality,
            sensor_id=self._sensor_id,
            signal_data=self._signal_data,
            quality=self._quality,
            duration_sec=self._duration_sec,
            provenance=dict(self._provenance),
        )