# Audition Modality - Phase 5.2 Acoustic Perception
# ===============================================

"""
Audition Modality: Observes non-linguistic and pre-linguistic acoustic evidence.

Canonical inputs:
    microphones
    audio streams  
    recorded audio
    simulated sound

Canonical outputs:
    acoustic Observations
    waveform Signals
    spectral Features
    sound Percepts
    acoustic Scenes
    auditory Events

Audition does not own language interpretation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time


# =============================================================================
# ACOUSTIC OBSERVATION - Raw audio evidence
# =============================================================================


@dataclass(frozen=True)
class AcousticObservation:
    """
    Raw acoustic evidence from a microphone or audio stream.
    
    Fields:
        identity:            Unique identifier for this observation
        
        timestamp_utc:       When captured
        
        sample_rate_hz:      Samples per second
        num_channels:        Mono=1, Stereo=2, etc.
        duration_sec:        Observation duration in seconds
        
        waveform_data:       Raw audio samples (PCM format)
        
        quality:             Quality score 0.0-1.0
        
        calibration_offset_ms: Time offset from calibration reference
        
        provenance:          Origin tracking
    """
    
    # Core identity (required)
    identity: str                       # Unique observation ID
    
    timestamp_utc: float                # When captured
    
    sample_rate_hz: int = 44100         # Samples per second
    num_channels: int = 1               # Mono=1, Stereo=2
    duration_sec: float = 0.0           # Duration in seconds
    
    waveform_data: bytes = b""          # Raw audio samples (PCM)
    
    quality: float = 1.0                # Quality score 0.0-1.0
    
    calibration_offset_ms: float = 0.0  # Time offset from reference
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if observation has minimal required data."""
        return (
            len(self.identity) > 0 and
            self.timestamp_utc > 0.0 and
            self.sample_rate_hz > 0 and
            self.duration_sec >= 0.0
        )
    
    @classmethod
    def from_audio_data(
        cls,
        waveform_data: bytes,
        sample_rate_hz: int = 44100,
        num_channels: int = 1,
        duration_sec: float = 0.0,
        timestamp_utc: Optional[float] = None,
        quality: float = 1.0,
    ) -> "AcousticObservation":
        """
        Create an AcousticObservation from audio data.
        
        Args:
            waveform_data: Raw PCM audio samples
            sample_rate_hz: Samples per second
            num_channels: Number of channels
            duration_sec: Duration in seconds
            timestamp_utc: Capture timestamp (default: now)
            quality: Quality score 0.0-1.0
            
        Returns:
            New AcousticObservation instance
        """
        return cls(
            identity=f"aud_obs:{time.time_ns()}",
            timestamp_utc=timestamp_utc or time.time(),
            sample_rate_hz=sample_rate_hz,
            num_channels=num_channels,
            duration_sec=duration_sec,
            waveform_data=waveform_data,
            quality=quality,
        )


# =============================================================================
# AUDIO SIGNAL - Processed audio signal representation
# =============================================================================


@dataclass(frozen=True)
class AudioSignal:
    """
    Processed audio signal representation.
    
    Examples: waveform, spectrogram, MFCC features
    
    Fields:
        identity:          Unique identifier
        
        modality:          "audition"
        
        signal_type:       waveform, spectrogram, mfcc, etc.
        
        frequency_range_hz: Frequency range (min, max)
        amplitude_db:      Amplitude in decibels
        
        confidence:        0.0-1.0
        
        supporting_observation_id: Source observation reference
        
        provenance:        Origin tracking
    """
    
    # Core identity (required)
    identity: str                       # Unique signal ID
    
    modality: str = "audition"          # Modality identifier
    
    signal_type: str = "waveform"       # waveform, spectrogram, mfcc, etc.
    
    frequency_range_hz: Tuple[float, float] = field(default=(0.0, 20000.0))
    amplitude_db: float = 0.0           # Amplitude in dB
    
    confidence: float = 1.0             # Confidence score
    
    supporting_observation_id: Optional[str] = None
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if signal has minimal required data."""
        return (
            len(self.identity) > 0 and
            0.0 <= self.confidence <= 1.0
        )


# =============================================================================
# ACOUSTIC FEATURE - Extracted acoustic feature
# =============================================================================


@dataclass(frozen=True)
class AcousticFeature:
    """
    Acoustic feature extracted from an observation.
    
    Examples: frequency peaks, temporal patterns, amplitude modulations
    
    Fields:
        identity:         Unique identifier
        
        modality:         "audition"
        
        time_start_sec:   Start time in seconds
        duration_sec:     Feature duration in seconds
        
        frequency_hz:     Center frequency or range
        amplitude_db:     Amplitude in decibels
        
        confidence:       0.0-1.0
        
        descriptor:       Feature descriptor (string/vector)
        
        provenance:       Origin tracking
    """
    
    # Core identity (required)
    identity: str                       # Unique feature ID
    
    modality: str = "audition"          # Modality identifier
    
    time_start_sec: float = 0.0         # Start time in seconds
    duration_sec: float = 0.0           # Duration in seconds
    
    frequency_hz: float = 1000.0        # Center frequency
    amplitude_db: float = 0.0           # Amplitude in dB
    
    confidence: float = 1.0             # Confidence score
    
    descriptor: str = ""                # Feature descriptor
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if feature has minimal required data."""
        return (
            len(self.identity) > 0 and
            self.time_start_sec >= 0.0 and
            0.0 <= self.confidence <= 1.0
        )


# =============================================================================
# AUDIO PERCEPT - Modality-independent acoustic representation
# =============================================================================


@dataclass(frozen=True)
class AudioPercept:
    """
    Modality-independent acoustic representation.
    
    Examples: sounds, sound events, acoustic scenes
    
    Fields:
        identity:          Unique identifier
        
        modality:          "audition"
        
        percept_type:      sound, event, scene, etc.
        
        location:          Spatial position (azimuth, elevation)
        confidence:        0.0-1.0
        
        acoustic_features: References to contributing features
        
        provenance:        Origin tracking
    """
    
    # Core identity (required)
    identity: str                       # Unique percept ID
    
    modality: str = "audition"          # Modality identifier
    
    percept_type: str = "sound"         # sound, event, scene, etc.
    
    location: Tuple[float, float] = field(default=(0.0, 0.0))  # (azimuth, elevation)
    confidence: float = 1.0             # Confidence score
    
    acoustic_features: Tuple[str, ...] = field(default_factory=tuple)  # Feature refs
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if percept has minimal required data."""
        return (
            len(self.identity) > 0 and
            0.0 <= self.confidence <= 1.0
        )


# =============================================================================
# AUDITION MODALITY - Audition modality implementation
# =============================================================================


@dataclass(frozen=True)
class AuditionModality:
    """
    Audition Modality implementation.
    
    Implements the canonical perception contract for acoustic observation.
    
    Fields:
        identity:           Unique modality identifier
        
        capabilities:       Supported capability identifiers
        
        permissions:        Effective permission set
        
        sandbox_profile:    Active sandbox profile
        
        calibration_state:  Current calibration state
        
        health:             Operational health status
    """
    
    # Core identity (required)
    identity: str                       # Modality unique ID
    
    capabilities: Tuple[str, ...] = field(default_factory=tuple)
    
    permissions: Tuple[str, ...] = field(default_factory=tuple)
    
    sandbox_profile: str = "NONE"
    
    calibration_state: str = "uncalibrated"
    
    health: Dict[str, Any] = field(default_factory=dict)  # Health metrics
    
    @property
    def is_active(self) -> bool:
        """Check if modality is active."""
        return self.health.get("is_available", False)
    
    @classmethod
    def create(
        cls,
        identity: Optional[str] = None,
        capabilities: Tuple[str, ...] = ("capture_audio", "stream_audio"),
        permissions: Tuple[str, ...] = (),
        sandbox_profile: str = "NONE",
        calibration_state: str = "uncalibrated",
    ) -> "AuditionModality":
        """
        Create a new AuditionModality instance.
        
        Args:
            identity: Unique identifier (auto-generated if None)
            capabilities: Supported capability identifiers
            permissions: Effective permission set
            sandbox_profile: Active sandbox profile
            calibration_state: Calibration state
            
        Returns:
            New AuditionModality instance
        """
        return cls(
            identity=identity or f"audition:{time.time_ns()}",
            capabilities=capabilities,
            permissions=permissions,
            sandbox_profile=sandbox_profile,
            calibration_state=calibration_state,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: list[str] = [
    # Dataclasses
    "AcousticObservation",
    "AudioSignal",
    "AcousticFeature",
    "AudioPercept",
    
    # Modality class
    "AuditionModality",
]