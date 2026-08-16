# Modality Capability - Phase 5.2 Declarative Evidence Classes
# =============================================================

"""
ModalityCapability: A declarative declaration of one observable class of evidence.

A capability declares what kind of evidence a modality can produce, without
implying that it is currently permitted to acquire that evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# CAPABILITY KIND - Types of capabilities a modality may declare
# =============================================================================


class CapabilityKind(Enum):
    """
    Kinds of capabilities that can be declared by modalities.
    
    Capabilities represent declarative evidence classes. Possessing a capability
    does not imply permission to use it, nor does it guarantee availability.
    """
    
    # Sensory capabilities
    CAPTURE_IMAGE = "capture_image"             # Capture static images
    CAPTURE_VIDEO = "capture_video"             # Capture video streams
    CAPTURE_AUDIO = "capture_audio"             # Capture audio
    CAPTURE_DEPTH = "capture_depth"             # Capture depth information
    CAPTURE_TACTILE = "capture_tactile"         # Capture tactile data
    CAPTURE_MOTION = "capture_motion"           # Track motion vectors
    
    # Digital capabilities - observation only (no mutation)
    OBSERVE_CONSOLE_STREAM = "observe_console_stream"
    OBSERVE_COMMAND_EXECUTION = "observe_command_execution"
    OBSERVE_PROCESS_LIFECYCLE = "observe_process_lifecycle"
    OBSERVE_FILESYSTEM_EVENTS = "observe_filesystem_events"
    OBSERVE_NETWORK_STATE = "observe_network_state"
    OBSERVE_KERNEL_EVENTS = "observe_kernel_events"
    OBSERVE_WINDOW_STATE = "observe_window_state"
    OBSERVE_CLIPBOARD_STATE = "observe_clipboard_state"
    OBSERVE_EDITOR_STATE = "observe_editor_state"
    OBSERVE_BROWSER_STATE = "observe_browser_state"
    OBSERVE_API_REQUESTS = "observe_api_requests"
    
    # Derived capabilities
    EXTRACT_FEATURES = "extract_features"       # Extract structured features
    GENERATE_PERCEPT = "generate_percept"       # Generate percepts from signals


# =============================================================================
# CAPABILITY SCOPE - Scope of observation for a capability
# =============================================================================


class CapabilityScope(Enum):
    """
    Scope of observation for a capability.
    
    Scope defines the breadth of what can be observed, separate from permission
    to access specific instances.
    """
    
    SELF = "self"                       # Only own processes/resources
    USER = "user"                       # All resources owned by current user
    PROCESS_TREE = "process_tree"       # Current process tree
    CONTAINER = "container"             # Container scope
    NAMESPACE = "namespace"             # Namespace scope
    HOST_SUMMARY = "host_summary"       # Host-level summaries only
    HOST_DETAILED = "host_detailed"     # Detailed host observation


# =============================================================================
# CAPABILITY - Declarative evidence class
# =============================================================================


@dataclass(frozen=True)
class ModalityCapability:
    """
    A declarative declaration of one observable evidence class.
    
    Capabilities remain declarative. Possessing a capability does not imply
    permission to use it, nor does it guarantee availability.
    
    Fields:
        capability_identity:  Unique identifier for this capability
        
        kind:                 Capability kind (CAPTURE_IMAGE, OBSERVE_CONSOLE_STREAM, etc.)
        
        scope:                Observation scope (SELF, USER, HOST_SUMMARY, etc.)
        
        description:          Human-readable description of what is observable
        
        inputs:               Expected input types (signal kinds)
        outputs:              Output types (observation, signal, feature, percept kinds)
        
        required_sandbox:     Minimum sandbox level required
        recommended_sandbox:  Recommended sandbox level for safe operation
        
        revision:             Capability version number
        provenance:           Origin tracking
    """
    
    # Core identity (required)
    capability_identity: str            # Globally unique identifier
    
    kind: str                           # CapabilityKind value as string
    
    scope: str = "self"                 # Observation scope
    description: str = ""               # Human-readable description
    
    # Input/Output specifications
    inputs: Tuple[str, ...] = field(default_factory=tuple)      # Signal kinds
    outputs: Tuple[str, ...] = field(default_factory=tuple)     # Observation kinds
    
    # Sandbox requirements
    required_sandbox: str = "NONE"      # NONE, PROCESS, USER, etc.
    recommended_sandbox: str = "PROCESS"
    
    revision: int = 1
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    @property
    def is_sensory(self) -> bool:
        """Check if this capability is for sensory observation."""
        return self.kind.startswith(("CAPTURE_", "OBSERVE_")) and any(
            x in self.kind for x in ["IMAGE", "VIDEO", "AUDIO", "DEPTH", "TACTILE"]
        )
    
    @property
    def is_digital(self) -> bool:
        """Check if this capability is for digital observation."""
        return not self.is_sensory
    
    @classmethod
    def create(
        cls,
        kind: str,
        identity: Optional[str] = None,
        scope: str = "self",
        description: str = "",
        inputs: Tuple[str, ...] = (),
        outputs: Tuple[str, ...] = ("observation", "signal"),
        required_sandbox: str = "NONE",
        recommended_sandbox: str = "PROCESS",
    ) -> "ModalityCapability":
        """
        Create a new capability instance.
        
        Args:
            kind: Capability kind string (CAPTURE_IMAGE, etc.)
            identity: Unique identifier (auto-generated if None)
            scope: Observation scope
            description: Human-readable description
            inputs: Expected input types
            outputs: Output types
            required_sandbox: Minimum sandbox level
            recommended_sandbox: Recommended sandbox level
            
        Returns:
            New ModalityCapability instance
        """
        return cls(
            capability_identity=identity or f"capability:{kind}:{scope}",
            kind=kind,
            scope=scope,
            description=description,
            inputs=inputs,
            outputs=outputs,
            required_sandbox=required_sandbox,
            recommended_sandbox=recommended_sandbox,
            revision=1,
        )
    
    def is_compatible_with_sandbox(self, sandbox: str) -> bool:
        """Check if the given sandbox level meets this capability's requirements."""
        # Define sandbox hierarchy
        sandbox_levels = {
            "NONE": 0,
            "PROCESS": 1,
            "USER": 2,
            "CONTAINER": 3,
            "NAMESPACE": 4,
            "VM": 5,
            "STRICT": 6,
        }
        
        required_level = sandbox_levels.get(self.required_sandbox, 0)
        given_level = sandbox_levels.get(sandbox, 0)
        
        return given_level >= required_level


# =============================================================================
# CAPABILITY SET - A collection of capabilities
# =============================================================================


@dataclass(frozen=True)
class CapabilitySet:
    """
    A set of capabilities supported by a modality.
    
    Fields:
        capability_identity:   Set identifier
        capabilities:          Tuple of individual capabilities
        revision:              Version number
    """
    
    capability_set_identity: str        # Globally unique identifier
    capabilities: Tuple[ModalityCapability, ...] = field(default_factory=tuple)
    revision: int = 1
    
    def has_capability(self, kind: str) -> bool:
        """Check if this set contains a capability of the given kind."""
        return any(c.kind == kind for c in self.capabilities)
    
    def get_capability(self, kind: str) -> Optional[ModalityCapability]:
        """Get a specific capability from this set."""
        for cap in self.capabilities:
            if cap.kind == kind:
                return cap
        return None
    
    def get_all_outputs(self) -> Tuple[str, ...]:
        """Get all unique output kinds from capabilities in this set."""
        outputs = set()
        for cap in self.capabilities:
            outputs.update(cap.outputs)
        return tuple(outputs)
    
    def requires_sandbox_at_least(self, sandbox: str) -> bool:
        """Check if any capability requires at least the given sandbox level."""
        for cap in self.capabilities:
            if not cap.is_compatible_with_sandbox(sandbox):
                return False
        return True


# =============================================================================
# EXPORTS
# =============================================================================

__all__: list[str] = [
    # Enums
    "CapabilityKind",
    "CapabilityScope",
    
    # Dataclasses
    "ModalityCapability",
    "CapabilitySet",
]