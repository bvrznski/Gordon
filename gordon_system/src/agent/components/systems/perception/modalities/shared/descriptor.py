# Modality Descriptor - Phase 5.2 Discovery and Capability Declaration
# ====================================================================

"""
ModalityDescriptor: A static declaration of a modality's capabilities,
requirements, and compatibility information.

The descriptor enables discovery of modalities without activation, allowing
higher-level systems to understand what each modality can do before deciding
whether to activate it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# OBSERVATION KIND - Types of observations a modality produces
# =============================================================================


class ObservationKind(Enum):
    """
    Kinds of observations a modality can produce.
    
    Each observation kind represents a different category of evidence that
    can be acquired from the environment.
    """
    
    # Canonical perception kinds (Phase 5.2)
    OBSERVATION = "observation"     # Raw evidence from sensor interaction
    SIGNAL = "signal"               # Measured sensor output
    FEATURE = "feature"             # Structured property computed from signal
    PERCEPT = "percept"             # Modality-independent representation
    SCENE = "scene"                 # Coherent collection of percepts
    EVENT = "event"                 # Meaningful transition between states
    
    # Extended observation kinds
    COMMAND = "command"             # Shell command execution
    PROCESS = "process"             # Process state and lifecycle
    FILESYSTEM_EVENT = "filesystem_event"
    NETWORK_EVENT = "network_event"
    KERNEL_EVENT = "kernel_event"


# =============================================================================
# SIGNAL KIND - Types of signals a modality processes
# =============================================================================


class SignalKind(Enum):
    """
    Kinds of signals a modality can process.
    
    Signals are the raw measurable outputs from sensors or input channels.
    """
    
    # Sensory signal kinds
    VISUAL = "visual"               # Light, images, video frames
    AUDIO = "audio"                 # Sound waves, audio streams
    TACTILE = "tactile"             # Contact, pressure, texture
    ACCELERATION = "acceleration"   # Linear acceleration
    ROTATIONAL = "rotational"       # Angular velocity, rotation
    
    # Digital signal kinds
    TERMINAL_OUTPUT = "terminal_output"
    COMMAND_LINE = "command_line"
    EVENT_STREAM = "event_stream"
    METADATA = "metadata"


# =============================================================================
# FEATURE KIND - Types of features a modality extracts
# =============================================================================


class FeatureKind(Enum):
    """
    Kinds of features a modality can compute from signals.
    
    Features are structured properties that reduce signal complexity without
    yet identifying semantic objects.
    """
    
    # Visual features
    EDGE = "edge"
    CORNER = "corner"
    CONTOUR = "contour"
    TEXTURE = "texture"
    MOTION_VECTOR = "motion_vector"
    DEPTH_MAP = "depth_map"
    COLOR_HISTOGRAM = "color_histogram"
    
    # Audio features
    SPECTRAL = "spectral"
    MFCC = "mfcc"
    ZEROCROSSING = "zerocrossing"
    ENERGY = "energy"
    
    # Textual features
    TOKEN = "token"
    SYNTAX_TREE = "syntax_tree"
    SEMANTIC_EMBEDDING = "semantic_embedding"
    
    # Process features
    RESOURCE_USAGE = "resource_usage"
    LIFECYCLE_STATE = "lifecycle_state"
    PARENT_CHILD_RELATIONSHIP = "parent_child_relationship"


# =============================================================================
# PERCEPT KIND - Types of percepts a modality produces
# =============================================================================


class PerceptKind(Enum):
    """
    Kinds of percepts a modality can produce.
    
    Percepts are modality-independent semantic representations derived from
    observations, signals, and features.
    """
    
    VISUAL_OBJECT = "visual_object"
    AUDIO_EVENT = "audio_event"
    SPEECH_UTTERANCE = "speech_utterance"
    CONSOLE_OUTPUT = "console_output"
    COMMAND_EXECUTION = "command_execution"
    PROCESS_STATE = "process_state"
    FILESYSTEM_CHANGE = "filesystem_change"
    NETWORK_ACTIVITY = "network_activity"


# =============================================================================
# SANDBOX LEVEL - Sandboxing intensity levels
# =============================================================================


class SandboxLevel(Enum):
    """
    Levels of sandboxing applied to a modality.
    
    Higher sandbox levels restrict what the modality can observe but provide
    stronger isolation guarantees.
    """
    
    NONE = "none"               # No sandboxing (full access)
    PROCESS = "process"         # Process-level isolation
    USER = "user"               # User-level isolation
    CONTAINER = "container"     # Container-level isolation
    NAMESPACE = "namespace"     # Namespace-level isolation
    VIRTUAL_MACHINE = "vm"      # Virtual machine isolation
    REMOTE = "remote"           # Remote observation only
    STRICT = "strict"           # Maximum restriction


# =============================================================================
# COMPATIBILITY - Platform and dependency compatibility
# =============================================================================


@dataclass(frozen=True)
class Compatibility:
    """
    Platform and environment compatibility requirements.
    
    Fields:
        min_python_version:  Minimum Python version required
        platform_support:    List of supported platforms (linux, darwin, win32)
        dependencies:        Required external packages
        optional_dependencies: Optional packages that enhance functionality
    """
    
    min_python_version: str = "3.10"
    platform_support: Tuple[str, ...] = ("linux", "darwin")
    dependencies: Tuple[str, ...] = field(default_factory=tuple)
    optional_dependencies: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# ACTIVATION MODES - Supported activation modes for this modality
# =============================================================================


class ActivationMode(Enum):
    """
    Modes of activation supported by a modality.
    
    A modality may support multiple activation modes and choose the most
    appropriate one based on configuration or runtime conditions.
    """
    
    CONTINUOUS = "continuous"
    PERIODIC = "periodic"
    EVENT_DRIVEN = "event_driven"
    ON_DEMAND = "on_demand"
    SESSION_BOUND = "session_bound"
    POLICY_TRIGGERED = "policy_triggered"
    MANUAL = "manual"


# =============================================================================
# MODALITY DESCRIPTOR - Static modality capabilities and requirements
# =============================================================================


@dataclass(frozen=True)
class ModalityDescriptor:
    """
    Static descriptor for a Perception Modality.
    
    The descriptor enables discovery without activation, allowing higher-level
    systems to understand what each modality can do before deciding whether
    to activate it.
    
    Fields:
        modality_identity:      Unique identifier for this modality kind
        
        family:                 SENSORY or DIGITAL classification
        
        modality_kind:          Canonical kind (VISION, CONSOLE, etc.)
        
        # Capabilities
        supported_observation_kinds:  Kinds of observations produced
        supported_signal_kinds:       Kinds of signals processed
        supported_feature_kinds:      Kinds of features computed
        supported_percept_kinds:      Kinds of percepts produced
        
        # Requirements
        required_permissions:   Permissions needed to activate this modality
        supported_sandbox_profiles: Sandbox profiles this modality supports
        platform_requirements:  Environment requirements
        
        # Configuration
        activation_modes:       Supported activation modes
        default_activation_mode: Mode used by default
        compatibility:          Platform and dependency requirements
        
        revision:               Descriptor version number
        provenance:             Origin tracking
    """
    
    # Core identity (required)
    modality_identity: str              # Globally unique identifier
    
    family: str                         # "sensory" or "digital"
    modality_kind: str                  # "vision", "console", etc.
    
    # Capabilities - what this modality CAN do
    supported_observation_kinds: Tuple[str, ...] = field(default_factory=tuple)
    supported_signal_kinds: Tuple[str, ...] = field(default_factory=tuple)
    supported_feature_kinds: Tuple[str, ...] = field(default_factory=tuple)
    supported_percept_kinds: Tuple[str, ...] = field(default_factory=tuple)
    
    # Requirements - what this modality NEEDS
    required_permissions: Tuple[str, ...] = field(default_factory=tuple)
    supported_sandbox_profiles: Tuple[str, ...] = ("NONE", "PROCESS", "USER")
    platform_requirements: Tuple[str, ...] = ("linux", "darwin", "win32")
    
    # Configuration
    activation_modes: Tuple[str, ...] = (
        "on_demand",
        "event_driven",
        "continuous"
    )
    default_activation_mode: str = "on_demand"
    
    compatibility: Compatibility = field(default_factory=Compatibility)
    
    revision: int = 1
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    @property
    def is_sensory(self) -> bool:
        """Check if this is a sensory modality."""
        return self.family == "sensory"
    
    @property
    def is_digital(self) -> bool:
        """Check if this is a digital modality."""
        return self.family == "digital"
    
    @classmethod
    def create(
        cls,
        modality_kind: str,
        family: str = "digital",
        identity: Optional[str] = None,
    ) -> "ModalityDescriptor":
        """
        Create a new modality descriptor.
        
        Args:
            modality_kind: Which kind of modality (vision, console, etc.)
            family: SENSORY or DIGITAL
            identity: Unique identifier (auto-generated if None)
            
        Returns:
            New ModalityDescriptor with defaults
        """
        return cls(
            modality_identity=identity or f"descriptor:{modality_kind}",
            family=family,
            modality_kind=modality_kind,
            supported_observation_kinds=("observation", "signal", "feature"),
            supported_signal_kinds=("raw",),
            supported_feature_kinds=("structured",),
            supported_percept_kinds=("percept",),
            required_permissions=(),
            revision=1,
        )
    
    def supports_observation(self, kind: str) -> bool:
        """Check if this modality can produce observations of the given kind."""
        return kind in self.supported_observation_kinds
    
    def supports_signal(self, kind: str) -> bool:
        """Check if this modality can process signals of the given kind."""
        return kind in self.supported_signal_kinds
    
    def supports_feature(self, kind: str) -> bool:
        """Check if this modality can compute features of the given kind."""
        return kind in self.supported_feature_kinds
    
    def supports_percept(self, kind: str) -> bool:
        """Check if this modality can produce percepts of the given kind."""
        return kind in self.supported_percept_kinds
    
    def is_compatible_with_platform(self, platform: str) -> bool:
        """Check if this modality is compatible with the given platform."""
        return platform in self.platform_requirements


# =============================================================================
# EXPORTS
# =============================================================================

__all__: list[str] = [
    # Enums
    "ObservationKind",
    "SignalKind",
    "FeatureKind",
    "PerceptKind",
    "SandboxLevel",
    "ActivationMode",
    
    # Dataclasses
    "Compatibility",
    "ModalityDescriptor",
]