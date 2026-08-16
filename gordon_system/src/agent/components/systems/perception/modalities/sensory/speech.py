# Speech Modality - Phase 5.2 Spoken Language Perception
# =====================================================

"""
Speech Modality: Specializes auditory evidence into structured spoken-language
observations.

Canonical inputs:
    microphones
    audio streams  
    recorded speech

Canonical outputs:
    phonetic Features
    word candidates
    utterance Percepts
    speaker-turn Events
    transcription projections

Speech does not own:
    semantic interpretation
    dialogue reasoning
    speaker identity truth
    intention recognition
    language generation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time


# =============================================================================
# SPEECH OBSERVATION - Raw speech evidence
# =============================================================================


@dataclass(frozen=True)
class SpeechObservation:
    """
    Raw speech evidence from an audio stream.
    
    Fields:
        identity:            Unique identifier for this observation
        
        timestamp_utc:       When captured
        
        audio_observation_id: Reference to source acoustic observation
        
        duration_sec:        Observation duration in seconds
        
        quality:             Quality score 0.0-1.0
        
        provenance:          Origin tracking
    """
    
    # Core identity (required)
    identity: str                       # Unique observation ID
    
    timestamp_utc: float                # When captured
    
    audio_observation_id: Optional[str] = None  # Source acoustic obs reference
    
    duration_sec: float = 0.0           # Duration in seconds
    
    quality: float = 1.0                # Quality score 0.0-1.0
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if observation has minimal required data."""
        return (
            len(self.identity) > 0 and
            self.timestamp_utc > 0.0 and
            self.duration_sec >= 0.0
        )
    
    @classmethod
    def from_audio_reference(
        cls,
        audio_observation_id: str,
        duration_sec: float = 0.0,
        timestamp_utc: Optional[float] = None,
        quality: float = 1.0,
    ) -> "SpeechObservation":
        """
        Create a SpeechObservation referencing an acoustic observation.
        
        Args:
            audio_observation_id: Source acoustic observation ID
            duration_sec: Duration in seconds
            timestamp_utc: Capture timestamp (default: now)
            quality: Quality score 0.0-1.0
            
        Returns:
            New SpeechObservation instance
        """
        return cls(
            identity=f"spch_obs:{time.time_ns()}",
            timestamp_utc=timestamp_utc or time.time(),
            audio_observation_id=audio_observation_id,
            duration_sec=duration_sec,
            quality=quality,
        )


# =============================================================================
# PHONETIC FEATURE - Phonetic-level feature
# =============================================================================


@dataclass(frozen=True)
class PhoneticFeature:
    """
    Phonetic-level feature extracted from speech.
    
    Examples: phonemes, phones, prosodic features
    
    Fields:
        identity:         Unique identifier
        
        modality:         "speech"
        
        time_start_sec:   Start time in seconds
        duration_sec:     Feature duration in seconds
        
        phoneme:          Phoneme symbol (e.g., "a", "b", "t")
        confidence:       0.0-1.0
        
        acoustic_features: References to contributing features
        
        provenance:       Origin tracking
    """
    
    # Core identity (required)
    identity: str                       # Unique feature ID
    
    modality: str = "speech"            # Modality identifier
    
    time_start_sec: float = 0.0         # Start time in seconds
    duration_sec: float = 0.0           # Duration in seconds
    
    phoneme: str = ""                   # Phoneme symbol
    confidence: float = 1.0             # Confidence score
    
    acoustic_features: Tuple[str, ...] = field(default_factory=tuple)
    
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
# WORD CANDIDATE - Word-level hypothesis
# =============================================================================


@dataclass(frozen=True)
class WordCandidate:
    """
    Word-level word hypothesis from speech processing.
    
    Fields:
        identity:         Unique identifier
        
        modality:         "speech"
        
        time_start_sec:   Start time in seconds
        duration_sec:     Duration in seconds
        
        word:             Word text (hypothesis)
        confidence:       0.0-1.0
        
        alternatives:     Alternative words with scores
        
        provenance:       Origin tracking
    """
    
    # Core identity (required)
    identity: str                       # Unique candidate ID
    
    modality: str = "speech"            # Modality identifier
    
    time_start_sec: float = 0.0         # Start time in seconds
    duration_sec: float = 0.0           # Duration in seconds
    
    word: str = ""                      # Word text (hypothesis)
    confidence: float = 1.0             # Confidence score
    
    alternatives: Dict[str, float] = field(default_factory=dict)  # word -> score
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if candidate has minimal required data."""
        return (
            len(self.identity) > 0 and
            self.time_start_sec >= 0.0 and
            0.0 <= self.confidence <= 1.0
        )


# =============================================================================
# UTTERANCE PERCEPT - Complete utterance representation
# =============================================================================


@dataclass(frozen=True)
class UtterancePercept:
    """
    Complete utterance representation from speech processing.
    
    Fields:
        identity:          Unique identifier
        
        modality:          "speech"
        
        words:             Word candidates in order
        
        speaker_id:        Speaker identifier (if known)
        start_time_sec:    Start time in seconds
        end_time_sec:      End time in seconds
        
        confidence:        0.0-1.0
        
        provenance:        Origin tracking
    """
    
    # Core identity (required)
    identity: str                       # Unique percept ID
    
    modality: str = "speech"            # Modality identifier
    
    words: Tuple[WordCandidate, ...] = field(default_factory=tuple)  # In order
    
    speaker_id: Optional[str] = None    # Speaker identifier
    start_time_sec: float = 0.0         # Start time in seconds
    end_time_sec: float = 0.0           # End time in seconds
    
    confidence: float = 1.0             # Confidence score
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if percept has minimal required data."""
        return (
            len(self.identity) > 0 and
            self.start_time_sec >= 0.0 and
            self.end_time_sec >= self.start_time_sec and
            0.0 <= self.confidence <= 1.0
        )


# =============================================================================
# SPEECH EVENT - Speech event representation
# =============================================================================


@dataclass(frozen=True)
class SpeechEvent:
    """
    Event in speech stream (turn changes, pauses, etc.)
    
    Types: START_TURN, END_TURN, PAUSE, UTTERANCE_COMPLETE
    
    Fields:
        identity:          Unique identifier
        
        modality:          "speech"
        
        event_type:        START_TURN, END_TURN, PAUSE, etc.
        
        timestamp_utc:     When event occurred
        duration_sec:      Event duration (0 for instantaneous)
        
        confidence:        0.0-1.0
        
        provenance:        Origin tracking
    """
    
    # Core identity (required)
    identity: str                       # Unique event ID
    
    modality: str = "speech"            # Modality identifier
    
    event_type: str = "utterance_complete"  # START_TURN, END_TURN, PAUSE, etc.
    
    timestamp_utc: float = 0.0          # When event occurred
    duration_sec: float = 0.0           # Event duration (0 for instantaneous)
    
    confidence: float = 1.0             # Confidence score
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if event has minimal required data."""
        return (
            len(self.identity) > 0 and
            self.timestamp_utc >= 0.0 and
            0.0 <= self.confidence <= 1.0
        )


# =============================================================================
# SPEECH MODALITY - Speech modality implementation
# =============================================================================


@dataclass(frozen=True)
class SpeechModality:
    """
    Speech Modality implementation.
    
    Implements the canonical perception contract for spoken-language observation.
    
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
        capabilities: Tuple[str, ...] = ("transcribe_speech",),
        permissions: Tuple[str, ...] = (),
        sandbox_profile: str = "NONE",
        calibration_state: str = "uncalibrated",
    ) -> "SpeechModality":
        """
        Create a new SpeechModality instance.
        
        Args:
            identity: Unique identifier (auto-generated if None)
            capabilities: Supported capability identifiers
            permissions: Effective permission set
            sandbox_profile: Active sandbox profile
            calibration_state: Calibration state
            
        Returns:
            New SpeechModality instance
        """
        return cls(
            identity=identity or f"speech:{time.time_ns()}",
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
    "SpeechObservation",
    "PhoneticFeature",
    "WordCandidate",
    "UtterancePercept",
    "SpeechEvent",
    
    # Modality class
    "SpeechModality",
]