# Core Platform Architecture - Phase 3.32
# =========================================
#
# This module provides the canonical Platform, Operating System & Hardware Abstraction
# Architecture for Gordon Core.
#
# ARCHITECTURAL VISION:
# --------------------
# The Gordon runtime shall execute independently of any particular operating system,
# hardware platform, accelerator vendor, kernel interface, runtime library, or
# deployment target. Platform-specific behavior shall be isolated behind explicit
# architectural contracts. Every subsystem—including execution, scheduling, resources,
# communication, persistence, security, observability, perception, cognition—shall
# interact with the underlying platform exclusively through this architecture.
#
# ARCHITECTURAL PRINCIPLES:
# ------------------------
# 1. ONE CANONICAL PLATFORM ABSTRACTION: One and only one Platform Architecture exists
#    throughout the repository. All subsystems MUST use it exclusively.
#
# 2. COMPLETE OS ABSTRACTION: No subsystem shall invoke operating-system APIs directly.
#    All OS interactions go through canonical contracts.
#
# 3. COMPLETE HARDWARE ABSTRACTION: Hardware access is always through capability-based
#    interfaces, never through vendor-specific APIs.
#
# 4. DETERMINISTIC CAPABILITY DISCOVERY: Platform capabilities are discovered once,
#    then remain immutable for the runtime lifetime.
#
# 5. REPLACEABLE IMPLEMENTATIONS: Platform implementations shall be swappable without
#    affecting Core subsystems.
#
# 6. ONE-WAY DEPENDENCY: Subsystems consume platform contracts; they never implement them.

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Import for type checking only
    from .foundations import (
        PlatformIdentity,
        PlatformDescriptor,
        PlatformLifecycle,
    )
    from .os_abstraction import (
        OSAbstraction,
        ProcessManagement,
        ThreadManagement,
        FilesystemAccess,
        IPCInterface,
        NetworkingInterface,
    )
    from .hardware_abstraction import (
        HardwareDescriptor,
        CPUInfo,
        MemoryInfo,
        DeviceDescriptor,
        AcceleratorInfo,
    )
    from .compute_abstraction import (
        ComputeProvider,
        ComputeCapability,
        ExecutionMode,
        AcceleratorSelector,
    )
    from .platform_discovery import PlatformDiscovery, PlatformInventory
    from .driver_integration import DriverContract, NativeAdapter

# =============================================================================
# PHASE 3.32.1 - PLATFORM FOUNDATIONS
# =============================================================================

from .foundations import (
    PlatformIdentity,
    PlatformDescriptor,
    PlatformLifecycle,
)

# =============================================================================
# PHASE 3.32.3 - OPERATING SYSTEM ABSTRACTION
# =============================================================================

from .os_abstraction import (
    OSAbstraction,
    ProcessManagement,
    ThreadManagement,
    FilesystemAccess,
    IPCInterface,
    NetworkingInterface,
)

# =============================================================================
# PHASE 3.32.4 - PROCESS & RUNTIME ABSTRACTION
# =============================================================================

from .process_runtime import (
    RuntimeContext,
    ProcessContext,
    ProcessSpec,
    ChildProcessHandle,
    RuntimeInstance,
    ExecutionEnvironment,
)

# =============================================================================
# PHASE 3.32.5 - THREAD & EXECUTION ABSTRACTION
# =============================================================================

from .thread_execution import (
    ThreadDescriptor,
    ExecutionContext,
    ThreadAffinity,
    ThreadGroup,
    ExecutionPool,
)

# =============================================================================
# PHASE 3.32.6 - FILESYSTEM & STORAGE ABSTRACTION
# =============================================================================

from .filesystem_abstraction import (
    FileSystemType,
    PathElement,
    FilePath,
    DirectoryPath,
    FileHandle,
    FilePermissions,
    AtomicWriteOperation,
    StorageProvider,
)

# =============================================================================
# PHASE 3.32.7 - DEVICE & HARDWARE ABSTRACTION
# =============================================================================

from .hardware_abstraction import (
    HardwareDescriptor,
    CPUInfo,
    MemoryInfo,
    DeviceDescriptor,
    AcceleratorInfo,
)

# =============================================================================
# PHASE 3.32.8 - COMPUTE & ACCELERATOR ARCHITECTURE
# =============================================================================

from .compute_abstraction import (
    ComputeProvider,
    ComputeCapability,
    ExecutionMode,
    AcceleratorSelector,
)

# =============================================================================
# PHASE 3.32.9 - NETWORKING & IPC ABSTRACTION
# =============================================================================

from .networking_ipc import (
    SocketAddress,
    ConnectionEndpoint,
    MessageQueueDescriptor,
    SharedMemoryRegion,
    IPCChannel,
    NetworkInterface,
    NetworkTopology,
)

# =============================================================================
# PHASE 3.32.10 - CLOCK, TIMER & POWER INTEGRATION
# =============================================================================

from .power_clock_integration import (
    ClockInterface,
    TimerDescriptor,
    PowerState,
    PowerDomain,
    ThermalState,
)

# =============================================================================
# PHASE 3.32.11 - PLATFORM RESOURCE DISCOVERY
# =============================================================================

from .platform_discovery import PlatformDiscovery, PlatformInventory

# =============================================================================
# PHASE 3.32.12 - DRIVER & NATIVE INTEGRATION
# =============================================================================

from .driver_integration import DriverContract, NativeAdapter

# =============================================================================
# PHASE 3.32.13 - COMPATIBILITY & FEATURE NEGOTIATION
# =============================================================================

from .compatibility_negotiation import (
    FeatureNegotiator,
    CapabilityMatcher,
    VersionCompatibility,
)

# =============================================================================
# PHASE 3.32.14 - PLATFORM SECURITY BOUNDARIES
# =============================================================================

from .security_boundaries import (
    SandboxBoundary,
    PrivilegeLevel,
    PermissionValidator,
    SecureDeviceAccess,
)

# =============================================================================
# PHASE 3.32.15 - PLATFORM OBSERVABILITY & DIAGNOSTICS
# =============================================================================

from .observability_diagnostics import (
    PlatformDiagnostics,
    HardwareDiagnostic,
    CompatibilityDiagnostic,
    ResourceDiagnostic,
)

# =============================================================================
# EXPOSE CANONICAL INTERFACE
# =============================================================================


class Platform:
    """
    Canonical Platform Interface for Gordon Core.
    
    This is the ONE source of platform abstraction. Every subsystem shall use this
    interface exclusively to interact with the underlying platform.
    
    INVARIANTS:
        P-INV-001: All platform access goes through Platform interface
        P-INV-002: No direct OS API calls outside Platform implementations
        P-INV-003: No vendor-specific hardware access outside Platform implementations
        P-INV-004: Platform is immutable during runtime lifetime
    """
    
    def __init__(self):
        self._identity = PlatformIdentity()
        self._descriptor = PlatformDescriptor(self._identity)
        self._lifecycle = PlatformLifecycle()
        
        # Initialize all platform abstraction layers
        self._os_abstraction = OSAbstraction(self._identity, self._descriptor)
        self._process_runtime = None  # Initialized on demand
        self._thread_execution = None  # Initialized on demand
        self._filesystem = None  # Initialized on demand
        self._hardware = HardwareDescriptor()
        self._compute = ComputeProvider(self._hardware)
        self._networking = IPCInterface()
        self._power_clock = ClockInterface()
        self._discovery = PlatformDiscovery()
        
        # Initialize platform from discovery
        self._initialize_platform_from_discovery()
    
    def _initialize_platform_from_discovery(self) -> None:
        """Initialize platform state from discovery results."""
        inventory = self._discovery.discover_full_inventory()
        self._hardware = inventory.hardware
        self._compute = ComputeProvider(self._hardware)
        
        # Initialize optional components based on availability
        if inventory.has_filesystem:
            self._filesystem = FileSystemAccess(inventory.filesystem_info)
        if inventory.has_process_management:
            self._process_runtime = RuntimeContext()
        if inventory.has_thread_management:
            self._thread_execution = ExecutionContext()
    
    @property
    def identity(self) -> PlatformIdentity:
        """Get platform identity."""
        return self._identity
    
    @property
    def descriptor(self) -> PlatformDescriptor:
        """Get platform descriptor with all capabilities."""
        return self._descriptor
    
    @property
    def lifecycle(self) -> PlatformLifecycle:
        """Get platform lifecycle manager."""
        return self._lifecycle
    
    @property
    def os_abstraction(self) -> OSAbstraction:
        """Get operating system abstraction interface."""
        return self._os_abstraction
    
    @property
    def process_runtime(self) -> RuntimeContext:
        """Get runtime context for process management."""
        if self._process_runtime is None:
            raise RuntimeError("Process management not available on this platform")
        return self._process_runtime
    
    @property
    def thread_execution(self) -> ExecutionContext:
        """Get execution context for thread management."""
        if self._thread_execution is None:
            raise RuntimeError("Thread execution not available on this platform")
        return self._thread_execution
    
    @property
    def filesystem(self) -> FileSystemAccess:
        """Get filesystem access interface."""
        if self._filesystem is None:
            raise RuntimeError("Filesystem access not available on this platform")
        return self._filesystem
    
    @property
    def hardware(self) -> HardwareDescriptor:
        """Get hardware descriptor."""
        return self._hardware
    
    @property
    def compute(self) -> ComputeProvider:
        """Get compute provider interface."""
        return self._compute
    
    @property
    def networking(self) -> IPCInterface:
        """Get IPC/networking interface."""
        return self._networking
    
    @property
    def power_clock(self) -> ClockInterface:
        """Get clock/power integration interface."""
        return self._power_clock
    
    @property
    def discovery(self) -> PlatformDiscovery:
        """Get platform discovery interface."""
        return self._discovery
    
    def get_platform_inventory(self) -> PlatformInventory:
        """Get complete platform inventory."""
        return self._discovery.discover_full_inventory()
    
    def validate_compatibility(self, requirements: dict) -> bool:
        """
        Validate that current platform meets given requirements.
        
        Args:
            requirements: Dictionary of required features/capabilities
            
        Returns:
            True if all requirements are met
        """
        inventory = self._discovery.discover_full_inventory()
        return inventory.matches_requirements(requirements)
    
    def get_diagnostics(self) -> dict:
        """Get platform diagnostics."""
        return PlatformDiagnostics().collect_all_diagnostics()


__all__ = [
    # Phase 3.32.1 - Foundations
    "PlatformIdentity",
    "PlatformDescriptor",
    "PlatformLifecycle",
    
    # Phase 3.32.3 - OS Abstraction
    "OSAbstraction",
    "ProcessManagement",
    "ThreadManagement",
    "FilesystemAccess",
    "IPCInterface",
    "NetworkingInterface",
    
    # Phase 3.32.4 - Process & Runtime
    "RuntimeContext",
    "ProcessContext",
    "ProcessSpec",
    "ChildProcessHandle",
    "RuntimeInstance",
    "ExecutionEnvironment",
    
    # Phase 3.32.5 - Thread & Execution
    "ThreadDescriptor",
    "ExecutionContext",
    "ThreadAffinity",
    "ThreadGroup",
    "ExecutionPool",
    
    # Phase 3.32.6 - Filesystem
    "FileSystemType",
    "PathElement",
    "FilePath",
    "DirectoryPath",
    "FileHandle",
    "FilePermissions",
    "AtomicWriteOperation",
    "StorageProvider",
    
    # Phase 3.32.7 - Hardware
    "HardwareDescriptor",
    "CPUInfo",
    "MemoryInfo",
    "DeviceDescriptor",
    "AcceleratorInfo",
    
    # Phase 3.32.8 - Compute
    "ComputeProvider",
    "ComputeCapability",
    "ExecutionMode",
    "AcceleratorSelector",
    
    # Phase 3.32.9 - Networking & IPC
    "SocketAddress",
    "ConnectionEndpoint",
    "MessageQueueDescriptor",
    "SharedMemoryRegion",
    "IPCChannel",
    "NetworkInterface",
    "NetworkTopology",
    
    # Phase 3.32.10 - Power & Clock
    "ClockInterface",
    "TimerDescriptor",
    "PowerState",
    "PowerDomain",
    "ThermalState",
    
    # Phase 3.32.11 - Discovery
    "PlatformDiscovery",
    "PlatformInventory",
    
    # Phase 3.32.12 - Drivers
    "DriverContract",
    "NativeAdapter",
    
    # Phase 3.32.13 - Compatibility
    "FeatureNegotiator",
    "CapabilityMatcher",
    "VersionCompatibility",
    
    # Phase 3.32.14 - Security
    "SandboxBoundary",
    "PrivilegeLevel",
    "PermissionValidator",
    "SecureDeviceAccess",
    
    # Phase 3.32.15 - Diagnostics
    "PlatformDiagnostics",
    "HardwareDiagnostic",
    "CompatibilityDiagnostic",
    "ResourceDiagnostic",
    
    # Main interface
    "Platform",
]