# Platform Foundations - Phase 3.32.1
# =====================================
#
# This module defines the philosophical and architectural foundations of the Gordon
# Core Platform Architecture.
#
# ARCHITECTURAL PHILOSOPHY:
# ------------------------
# The Gordon runtime must be completely independent from any specific operating system,
# hardware platform, or vendor implementation. This independence is achieved through
# explicit architectural contracts that abstract away platform-specific details.
#
# ABSTRACTION PHILOSOPHY:
# ----------------------
# Every platform concern is separated into distinct architectural layers:
#   - Platform: The top-level abstraction providing all services
#   - Operating System: Process, thread, file, IPC management
#   - Hardware: CPU, memory, devices, accelerators
#   - Runtime: Execution context, lifecycle, scheduling
#
# PORTABILITY PHILOSOPHY:
# ----------------------
# Platform implementations are swappable. Changing the underlying OS or hardware
# shall never require changes to Core subsystems.
#
# TERMINOLOGY:
# -----------
# Platform           - The top-level abstraction providing services
# Operating System   - Abstraction for process/thread/filesystem/IPC APIs
# Kernel             - Not directly accessible; OS provides kernel abstractions
# Runtime            - Execution context within a platform instance
# Process            - Unit of execution with its own resources
# Thread             - Unit of scheduling within a process
# Filesystem         - Hierarchical data storage abstraction
# Device             - Hardware peripheral or virtual device
# Driver             - Implementation layer between OS and hardware
# Accelerator        - Specialized compute hardware (GPU, TPU, etc.)
#
# ARCHITECTURAL BOUNDARIES:
# -------------------------
# Platform boundaries are explicitly defined. Subsystems NEVER interact with
# platform implementations directly.

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol, Optional, Dict, Any, Tuple


class PlatformPhilosophy(Enum):
    """
    Core philosophical principles of Gordon Platform Architecture.
    
    P-PHILOS-001: Runtime independence from OS/Hardware
        The runtime shall execute on any platform without modification.
    
    P-PHILOS-002: One canonical abstraction
        There is exactly ONE Platform Architecture. No alternatives.
    
    P-PHILOS-003: Complete encapsulation
        All platform-specific code is isolated behind contracts.
    
    P-PHILOS-004: Replaceable implementations
        Platform implementations are swappable at runtime.
    
    P-PHILOS-005: Deterministic capability discovery
        Capabilities are discovered once, then immutable.
    """
    
    RUNTIME_INDEPENDENCE = auto()
    CANONICAL_ABSTRACTION = auto()
    COMPLETE_ENCAPSULATION = auto()
    REPLACEABLE_IMPLEMENTATIONS = auto()
    DETERMINISTIC_DISCOVERY = auto()


class AbstractionType(Enum):
    """
    Types of abstractions in the platform hierarchy.
    
    A-ABS-001: Platform is the top-level abstraction
    A-ABS-002: OS provides system services abstraction
    A-ABS-003: Hardware provides device abstraction
    A-ABS-004: Runtime provides execution context abstraction
    """
    
    PLATFORM = "platform"
    OPERATING_SYSTEM = "os"
    HARDWARE = "hardware"
    RUNTIME = "runtime"
    PROCESS = "process"
    THREAD = "thread"
    FILESYSTEM = "filesystem"
    DEVICE = "device"
    NETWORKING = "networking"
    IPC = "ipc"


class OwnershipType(Enum):
    """
    Types of ownership in the platform hierarchy.
    
    OWN-001: Platform owns all subsystems
    OWN-002: Subsystems own resources they manage
    OWN-003: No cyclic ownership relationships
    """
    
    PLATFORM = "platform"
    SUBSYSTEM = "subsystem"
    RESOURCE = "resource"


# =============================================================================
# Platform Identity
# =============================================================================


@dataclass(frozen=True)
class PlatformIdentity:
    """
    Unique identifier for a platform instance.
    
    INVARIANTS:
        PI-INV-001: Platform identity is immutable
        PI-INV-002: Platform identity is globally unique
        PI-INV-003: Platform identity includes vendor information
    
    THREAD SAFETY:
        Immutable dataclass ensures thread safety.
    """
    
    # Unique identifier for this platform instance
    _id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Vendor/organization name (e.g., "Gordon", "Custom")
    vendor: str = "Gordon"
    
    # Platform family (e.g., "cloud", "edge", "embedded")
    family: str = "general-purpose"
    
    # Build version
    version: str = "3.32.0"
    
    @property
    def id(self) -> str:
        """Get platform ID."""
        return self._id
    
    def __repr__(self) -> str:
        return f"PlatformIdentity({self.id}, vendor={self.vendor!r}, family={self.family!r})"


@dataclass(frozen=True)
class PlatformDescriptor:
    """
    Complete descriptor of platform capabilities.
    
    INVARIANTS:
        PD-INV-001: Descriptor is immutable
        PD-INV-002: All capabilities are discoverable
        PD-INV-003: Capabilities cannot be added after creation
    
    THREAD SAFETY:
        Immutable dataclass ensures thread safety.
    """
    
    # Platform identity this descriptor describes
    platform_id: PlatformIdentity
    
    # Operating system information
    operating_system: str = "unknown"
    kernel_version: str = "unknown"
    os_architecture: str = "unknown"
    os_abi: str = "unknown"
    
    # Hardware profile
    cpu_count: int = 1
    total_memory_bytes: int = 0
    has_gpu: bool = False
    gpu_device_count: int = 0
    
    # Runtime environment
    runtime_name: str = "python"
    runtime_version: str = "3.11"
    
    # Capability inventory (features this platform supports)
    capabilities: Tuple[str, ...] = field(default_factory=tuple)
    
    def get_capability(self, capability_name: str) -> bool:
        """Check if platform has a specific capability."""
        return capability_name in self.capabilities
    
    def requires_capability(self, *capability_names: str) -> bool:
        """
        Check if all required capabilities are present.
        
        Args:
            capability_names: Names of required capabilities
            
        Returns:
            True if all requirements are met
        """
        return all(cap in self.capabilities for cap in capability_names)


@dataclass(frozen=True)
class PlatformLifecycle:
    """
    Manages platform lifecycle phases.
    
    LIFECYCLE PHASES:
        1. Discovery - Identify available capabilities
        2. Capability Enumeration - List all discoverable features
        3. Compatibility Validation - Check if requirements are met
        4. Initialization - Set up platform services
        5. Registration - Register with runtime registry
        6. Activation - Start accepting requests
        7. Operational - Platform is active and serving requests
        8. Monitoring - Continuously monitor health
        9. Maintenance - Perform updates/reconfigurations
        10. Deactivation - Stop accepting new requests
        11. Shutdown - Clean up resources
        12. Removal - Remove from registry
    
    INVARIANTS:
        PL-INV-001: Lifecycle transitions are strictly ordered
        PL-INV-002: No backward transitions
        PL-INV-003: Each phase has validation requirements
    
    THREAD SAFETY:
        Immutable state after each transition.
    """
    
    class Phase(Enum):
        """Platform lifecycle phases."""
        DISCOVERY = "discovery"
        ENUMERATION = "enumeration"
        VALIDATION = "validation"
        INITIALIZATION = "initialization"
        REGISTRATION = "registration"
        ACTIVATION = "activation"
        OPERATIONAL = "operational"
        MONITORING = "monitoring"
        MAINTENANCE = "maintenance"
        DEACTIVATION = "deactivation"
        SHUTDOWN = "shutdown"
        REMOVAL = "removal"
    
    # Current lifecycle phase
    current_phase: Phase = Phase.DISCOVERY
    
    # Timestamps for each phase transition (phase -> timestamp)
    _phase_timestamps: Dict[str, float] = field(default_factory=dict)
    
    def transition_to(self, new_phase: Phase) -> PlatformLifecycle:
        """
        Create a new lifecycle instance with the updated phase.
        
        Args:
            new_phase: Target phase for transition
            
        Returns:
            New PlatformLifecycle instance
        """
        import time
        return PlatformLifecycle(
            current_phase=new_phase,
            _phase_timestamps={**self._phase_timestamps, new_phase.value: time.time()},
        )
    
    def is_before(self, phase: Phase) -> bool:
        """Check if current phase is before the given phase."""
        phases = list(PlatformLifecycle.Phase)
        return phases.index(self.current_phase) < phases.index(phase)
    
    def is_after(self, phase: Phase) -> bool:
        """Check if current phase is after the given phase."""
        phases = list(PlatformLifecycle.Phase)
        return phases.index(self.current_phase) > phases.index(phase)
    
    def has_reached(self, phase: Phase) -> bool:
        """Check if current phase is at or after the given phase."""
        return self.is_after(phase) or self.current_phase == phase
    
    @property
    def is_operational(self) -> bool:
        """Check if platform is in operational state."""
        return self.current_phase == PlatformLifecycle.Phase.OPERATIONAL
    
    @property
    def is_shutdown(self) -> bool:
        """Check if platform has been shut down."""
        return self.current_phase == PlatformLifecycle.Phase.SHUTDOWN


# =============================================================================
# Capability Discovery Interface
# =============================================================================


class CapabilityProvider(Protocol):
    """
    Protocol for providers of platform capabilities.
    
    INVARIANTS:
        CP-INV-001: All capabilities must be discoverable
        CP-INV-002: Capabilities are immutable once discovered
        CP-INV-003: No duplicate capability identifiers
    """
    
    def get_capability_names(self) -> Tuple[str, ...]:
        """Get names of all available capabilities."""
        ...
    
    def get_capability_info(self, name: str) -> Dict[str, Any]:
        """
        Get detailed information about a capability.
        
        Args:
            name: Capability name
            
        Returns:
            Dictionary with capability details
        """
        ...
    
    def has_capability(self, name: str) -> bool:
        """Check if a capability is available."""
        ...


# =============================================================================
# Platform Contract Interface
# =============================================================================


class PlatformContract(Protocol):
    """
    Protocol for platform contract implementations.
    
    All platform abstractions must implement this contract.
    
    INVARIANTS:
        PC-INV-001: Contract methods are pure (no side effects on immutable data)
        PC-INV-002: All operations validate inputs
        PC-INV-003: All errors are well-defined and recoverable
    
    SUBTYPES MUST SATISFY:
        - OSAbstractionContract
        - ProcessManagementContract
        - ThreadManagementContract
        - FilesystemAccessContract
        - HardwareAccessorContract
        - ComputeProviderContract
        - IPCInterfaceContract
    """
    
    def get_identity(self) -> PlatformIdentity:
        """Get the platform identity."""
        ...
    
    def get_descriptor(self) -> PlatformDescriptor:
        """Get the platform descriptor with capabilities."""
        ...
    
    def validate_compatibility(self, requirements: Dict[str, Any]) -> bool:
        """
        Validate that this contract meets given requirements.
        
        Args:
            requirements: Dictionary of required features
            
        Returns:
            True if compatible
        """
        ...


__all__ = [
    # Philosophy
    "PlatformPhilosophy",
    
    # Abstraction types
    "AbstractionType",
    
    # Ownership
    "OwnershipType",
    
    # Identity
    "PlatformIdentity",
    
    # Descriptor
    "PlatformDescriptor",
    
    # Lifecycle
    "PlatformLifecycle",
    
    # Protocols
    "CapabilityProvider",
    "PlatformContract",
]