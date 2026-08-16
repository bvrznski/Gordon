# Perception Signal - Phase 5.2 Measured Sensor Output
# =====================================================

"""
Perception Signal: The measurable output of a sensing mechanism.

A Signal is the measurable output of a sensor or input channel. Signals possess:
- origin
- timestamp
- quality
- modality

Signals contain no semantics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import time
import uuid


@dataclass(frozen=True)
class Signal:
    """
    Measured output from a sensor or input channel.
    
    Signals possess:
        origin:        Source of the signal (sensor identifier)
        timestamp_utc: When the signal was captured
        quality:       Quality score 0.0-1.0
        modality:      Type of signal (vision, audio, etc.)
        
    Signals contain no semantics.
    """
    
    # Core signal data
    origin: str              # Sensor identifier
    timestamp_utc: float     # When captured
    
    modality: str            # vision, audio, speech, console, etc.
    raw_data: bytes          # Raw sensor output
    
    # Signal properties
    quality: float = 1.0    # Quality score (0.0-1.0)
    sampling_rate: Optional[float] = None  # Samples per second (if applicable)
    resolution: Optional[str] = None       # Resolution description (e.g., "640x480")
    
    # Calibration
    calibration_data: Dict[str, float] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if signal has minimal required data."""
        return (
            len(self.origin) > 0 and
            self.timestamp_utc > 0.0 and
            len(self.modality) > 0
        )
    
    @classmethod
    def from_data(
        cls,
        raw_data: bytes,
        modality: str,
        origin: str = "system",
        timestamp_utc: Optional[float] = None,
        quality: float = 1.0,
        sampling_rate: Optional[float] = None,
        resolution: Optional[str] = None,
        calibration_data: Optional[Dict[str, float]] = None,
    ) -> "Signal":
        """
        Create a Signal from raw data.
        
        Args:
            raw_data: Raw sensor output
            modality: Type of signal
            origin: Sensor identifier
            timestamp_utc: When captured (default: now)
            quality: Quality score 0.0-1.0
            sampling_rate: Samples per second (optional)
            resolution: Resolution description (optional)
            calibration_data: Calibration parameters (optional)
            
        Returns:
            New Signal instance
        """
        return cls(
            origin=origin,
            timestamp_utc=timestamp_utc or time.time(),
            modality=modality,
            raw_data=raw_data,
            quality=quality,
            sampling_rate=sampling_rate,
            resolution=resolution,
            calibration_data=calibration_data or {},
        )


class SignalBuilder:
    """
    Mutable builder for constructing signals.
    
    Usage:
        sig = (SignalBuilder()
            .set_modality("vision")
            .set_origin("camera_front")
            .set_raw_data(data)
            .build())
    """
    
    def __init__(self):
        self._origin: str = "system"
        self._timestamp_utc: float = time.time()
        self._modality: str = "unknown"
        self._raw_data: bytes = b""
        self._quality: float = 1.0
        self._sampling_rate: Optional[float] = None
        self._resolution: Optional[str] = None
        self._calibration_data: Dict[str, float] = {}
    
    def set_origin(self, origin: str) -> "SignalBuilder":
        """Set the signal origin (sensor ID)."""
        self._origin = origin
        return self
    
    def set_timestamp_utc(self, timestamp: float) -> "SignalBuilder":
        """Set capture timestamp."""
        self._timestamp_utc = timestamp
        return self
    
    def set_modality(self, modality: str) -> "SignalBuilder":
        """Set signal modality type."""
        self._modality = modality
        return self
    
    def set_raw_data(self, data: bytes) -> "SignalBuilder":
        """Set raw sensor data."""
        self._raw_data = data
        return self
    
    def set_quality(self, quality: float) -> "SignalBuilder":
        """Set quality score 0.0-1.0."""
        if not 0.0 <= quality <= 1.0:
            raise ValueError(f"Quality must be 0.0-1.0, got {quality}")
        self._quality = quality
        return self
    
    def set_sampling_rate(self, rate: float) -> "SignalBuilder":
        """Set sampling rate in Hz."""
        self._sampling_rate = rate
        return self
    
    def set_resolution(self, resolution: str) -> "SignalBuilder":
        """Set resolution description (e.g., '640x480')."""
        self._resolution = resolution
        return self
    
    def add_calibration_point(self, key: str, value: float) -> "SignalBuilder":
        """Add a calibration data point."""
        self._calibration_data[key] = value
        return self
    
    def set_calibration_data(self, data: Dict[str, float]) -> "SignalBuilder":
        """Set all calibration data."""
        self._calibration_data = data
        return self
    
    def build(self) -> Signal:
        """Build an immutable Signal."""
        if not self._raw_data and len(self._modality) == 0:
            raise ValueError("raw_data or modality is required")
        return Signal(
            origin=self._origin,
            timestamp_utc=self._timestamp_utc,
            modality=self._modality,
            raw_data=self._raw_data,
            quality=self._quality,
            sampling_rate=self._sampling_rate,
            resolution=self._resolution,
            calibration_data=dict(self._calibration_data),
        )


__all__ = [
    "Signal",
    "SignalBuilder",
]