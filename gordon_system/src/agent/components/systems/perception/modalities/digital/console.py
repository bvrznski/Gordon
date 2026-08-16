# Console Modality - Phase 5.2 Terminal Stream Observation
# ========================================================

"""
Console Modality: Observes rendered textual interaction streams.

Canonical inputs:
    stdout
    stderr
    terminal output
    interactive prompts
    ANSI streams

Canonical outputs:
    console Observations
    text Features
    prompt Percepts
    output-block Percepts
    diagnostic Events

Console observes presentation. It does not own command execution semantics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time


# =============================================================================
# CONSOLE OBSERVATION - Raw terminal stream observation
# =============================================================================


@dataclass(frozen=True)
class ConsoleObservation:
    """
    Raw terminal output observation.
    
    Fields:
        identity:            Unique identifier for this observation
        
        timestamp_utc:       When observed
        
        source_type:         stdout, stderr, prompt, response
        
        text:                Rendered text content
        
        encoding:            Character encoding (UTF-8, ASCII, etc.)
        
        is_ansi_stream:      True if contains ANSI escape codes
        
        quality:             Quality score 0.0-1.0
        
        provenance:          Origin tracking
    """
    
    # Core identity (required)
    identity: str                       # Unique observation ID
    
    timestamp_utc: float                # When observed
    
    source_type: str = "stdout"         # stdout, stderr, prompt, response
    
    text: str = ""                      # Rendered text content
    
    encoding: str = "UTF-8"             # Character encoding
    
    is_ansi_stream: bool = False        # Contains ANSI escape codes?
    
    quality: float = 1.0                # Quality score 0.0-1.0
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if observation has minimal required data."""
        return (
            len(self.identity) > 0 and
            self.timestamp_utc > 0.0
        )
    
    @classmethod
    def from_text(
        cls,
        text: str,
        source_type: str = "stdout",
        timestamp_utc: Optional[float] = None,
        is_ansi_stream: bool = False,
        encoding: str = "UTF-8",
        quality: float = 1.0,
    ) -> "ConsoleObservation":
        """
        Create a ConsoleObservation from text.
        
        Args:
            text: Terminal output text
            source_type: Source (stdout, stderr, prompt, response)
            timestamp_utc: Observation timestamp (default: now)
            is_ansi_stream: Contains ANSI escape codes?
            encoding: Character encoding
            quality: Quality score 0.0-1.0
            
        Returns:
            New ConsoleObservation instance
        """
        return cls(
            identity=f"cons_obs:{time.time_ns()}",
            timestamp_utc=timestamp_utc or time.time(),
            source_type=source_type,
            text=text,
            encoding=encoding,
            is_ansi_stream=is_ansi_stream,
            quality=quality,
        )


# =============================================================================
# TEXT FEATURE - Text-level feature extracted from console output
# =============================================================================


@dataclass(frozen=True)
class TextFeature:
    """
    Text feature extracted from console output.
    
    Examples: prompts, command patterns, error messages
    
    Fields:
        identity:         Unique identifier
        
        modality:         "console"
        
        time_start_sec:   Start time in seconds relative to session start
        duration_sec:     Feature duration in seconds
        
        text_pattern:     Identified text pattern (e.g., PROMPT, ERROR)
        confidence:       0.0-1.0
        
        supporting_observation_id: Source observation reference
        
        provenance:       Origin tracking
    """
    
    # Core identity (required)
    identity: str                       # Unique feature ID
    
    modality: str = "console"           # Modality identifier
    
    time_start_sec: float = 0.0         # Start time in session
    duration_sec: float = 0.0           # Duration in seconds
    
    text_pattern: str = ""              # Pattern (PROMPT, ERROR, etc.)
    confidence: float = 1.0             # Confidence score
    
    supporting_observation_id: Optional[str] = None
    
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
# CONSOLE PERCEPT - Console-level percept representation
# =============================================================================


@dataclass(frozen=True)
class ConsolePercept:
    """
    Console-level percept derived from observations.
    
    Examples: prompts, output blocks, command responses
    
    Fields:
        identity:          Unique identifier
        
        modality:          "console"
        
        percept_type:      prompt, output_block, response, etc.
        
        text:              Perceived text
        confidence:        0.0-1.0
        
        console_features:  References to contributing features
        
        provenance:        Origin tracking
    """
    
    # Core identity (required)
    identity: str                       # Unique percept ID
    
    modality: str = "console"           # Modality identifier
    
    percept_type: str = "prompt"        # prompt, output_block, response, etc.
    
    text: str = ""                      # Perceived text
    confidence: float = 1.0             # Confidence score
    
    console_features: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if percept has minimal required data."""
        return (
            len(self.identity) > 0 and
            self.confidence >= 0.0 and
            self.confidence <= 1.0
        )


# =============================================================================
# CONSOLE EVENT - Console event representation
# =============================================================================


@dataclass(frozen=True)
class ConsoleEvent:
    """
    Event in console stream (prompt changes, output completion, etc.)
    
    Types: PROMPT_RECEIVED, OUTPUT_STARTED, OUTPUT_COMPLETED
    
    Fields:
        identity:          Unique identifier
        
        modality:          "console"
        
        event_type:        Type of event
        
        timestamp_utc:     When event occurred
        duration_sec:      Event duration (0 for instantaneous)
        
        confidence:        0.0-1.0
        
        provenance:        Origin tracking
    """
    
    # Core identity (required)
    identity: str                       # Unique event ID
    
    modality: str = "console"           # Modality identifier
    
    event_type: str = "output_started"  # PROMPT_RECEIVED, OUTPUT_STARTED, etc.
    
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
# CONSOLE MODALITY - Console modality implementation
# =============================================================================


@dataclass(frozen=True)
class ConsoleModality:
    """
    Console Modality implementation.
    
    Implements the canonical perception contract for console stream observation.
    
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
        capabilities: Tuple[str, ...] = ("observe_console_stream",),
        permissions: Tuple[str, ...] = (),
        sandbox_profile: str = "NONE",
        calibration_state: str = "uncalibrated",
    ) -> "ConsoleModality":
        """
        Create a new ConsoleModality instance.
        
        Args:
            identity: Unique identifier (auto-generated if None)
            capabilities: Supported capability identifiers
            permissions: Effective permission set
            sandbox_profile: Active sandbox profile
            calibration_state: Calibration state
            
        Returns:
            New ConsoleModality instance
        """
        return cls(
            identity=identity or f"console:{time.time_ns()}",
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
    "ConsoleObservation",
    "TextFeature",
    "ConsolePercept",
    "ConsoleEvent",
    
    # Modality class
    "ConsoleModality",
]