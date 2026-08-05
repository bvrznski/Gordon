# Core Capability Management Infrastructure
# =========================================
"""
Capability resolution system.

Provides:
- Multi-state capability tracking
- Implementation, enabled, available, ready, active states
- Dependency management
- Configuration interaction

Phase 3.7.14: Configuration, Policy, Feature Flags & Runtime Reconfiguration
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    Any,
    Optional,
    List,
    Tuple,
)
from enum import Enum
import time


# =============================================================================
# Capability IDs
# =============================================================================

@dataclass(frozen=True)
class CapabilityId:
    """Unique identifier for a capability."""
    value: str
    
    @classmethod
    def generate(cls) -> "CapabilityId":
        import uuid
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "CapabilityId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# Capability States
# =============================================================================

class CapabilityState(Enum):
    """
    Capability state values.
    
    These states are distinct and must not be collapsed into a single boolean:
    
    - IMPLEMENTED: Code exists for this capability
    - CONFIGURED: Configuration has been provided
    - ENABLED: Feature flags/authorities allow this capability
    - AVAILABLE: All dependencies satisfied, ready to use
    - HEALTHY: No known issues with the capability
    - READY: Ready to accept work/requests
    - ADMITTED: Permitted in current admission window
    - ACTIVE: Currently processing work
    - DEGRADED: Working but with reduced capacity/fidelity
    - UNAVAILABLE: Cannot be used at this time
    """
    
    # Implementation states
    IMPLEMENTED = "implemented"
    NOT_IMPLEMENTED = "not_implemented"
    
    # Configuration states
    CONFIGURED = "configured"
    MISSING_CONFIGURATION = "missing_configuration"
    
    # Authority states
    ENABLED = "enabled"
    DISABLED = "disabled"
    
    # Availability states
    AVAILABLE = "available"
    DEPENDENCY_MISSING = "dependency_missing"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    
    # Health states
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    
    # Readiness states
    READY = "ready"
    NOT_READY = "not_ready"
    
    # Admission states
    ADMITTED = "admitted"
    REJECTED = "rejected"
    
    # Active states
    ACTIVE = "active"
    INACTIVE = "inactive"


# =============================================================================
# Capability Descriptor
# =============================================================================

@dataclass(frozen=True)
class CapabilityDescriptor:
    """
    A capability descriptor with full metadata.
    
    This is the authoritative description of what a capability provides.
    """
    
    capability_id: CapabilityId
    name: str
    domain: str  # e.g., "scheduling", "recovery"
    
    # Implementation details
    provider_class: Optional[str] = None  # Fully qualified class name
    implementation_version: str = "1.0.0"
    
    # Requirements
    dependencies: Tuple[CapabilityId, ...] = field(default_factory=tuple)
    config_keys: Tuple[str, ...] = field(default_factory=tuple)  # Config keys this needs
    
    # Configuration constraints
    requires_feature_flag: Optional[str] = None
    minimum_resource_quantity: float = 0.0
    
    # Lifecycle
    lifecycle_stage: str = "development"  # development, preview, GA, deprecated, removed
    
    # Metadata
    version: int = 1
    owner: Optional[str] = None
    created_at: float = field(default_factory=time.monotonic)
    
    # Deprecation
    deprecation_notice: Optional[str] = None


# =============================================================================
# Capability Status
# =============================================================================

@dataclass(frozen=True)
class CapabilityStatus:
    """
    Current status of a capability.
    
    Captures all relevant state for decision-making about the capability.
    """
    
    capability_id: str
    timestamp: float = field(default_factory=time.monotonic)
    
    # Core states (as distinct booleans, not collapsed into one value)
    implemented: bool = False
    configured: bool = False
    enabled: bool = False
    available: bool = False
    healthy: bool = True  # Default to healthy if not explicitly unhealthy
    ready: bool = False
    admitted: bool = False
    active: bool = False
    
    # State transitions (for debugging)
    state_changed_at: float = field(default_factory=time.monotonic)
    
    # Resource usage (optional metrics)
    resource_used: Optional[float] = None
    capacity_used: Optional[float] = None
    
    # Error information (if not healthy/available)
    error_message: Optional[str] = None


# =============================================================================
# Capability Resolution
# =============================================================================

@dataclass(frozen=True)
class CapabilityResolution:
    """
    Result of capability resolution for a runtime.
    
    Shows which capabilities are available and their states.
    """
    
    runtime_id: str
    timestamp: float = field(default_factory=time.monotonic)
    
    # All known capabilities
    capabilities_by_id: Dict[str, CapabilityDescriptor] = field(default_factory=dict)
    
    # Status by capability
    statuses_by_id: Dict[str, CapabilityStatus] = field(default_factory=dict)
    
    # Resolution metadata
    resolved_version: int = 1
    resolution_round: int = 0
    
    @property
    def active_count(self) -> int:
        """Return count of capabilities that are active."""
        return sum(1 for s in self.statuses_by_id.values() if s.active)
    
    @property
    def available_count(self) -> int:
        """Return count of capabilities that are available."""
        return sum(1 for s in self.statuses_by_id.values() if s.available)


# =============================================================================
# Capability Snapshot
# =============================================================================

@dataclass(frozen=True)
class CapabilitySnapshot:
    """
    Snapshot of capability state at a point in time.
    
    Used for:
    - Drift detection (compare to effective config)
    - Rollback support
    - Historical analysis
    - Multi-runtime isolation
    """
    
    snapshot_id: str
    runtime_id: str
    effective_config_version: int
    
    # Capability states at snapshot time
    capability_statuses: Dict[str, CapabilityStatus]
    
    applied_version: Optional[int] = None
    created_at: float = field(default_factory=time.monotonic)
    
    def is_current(self) -> bool:
        return self.applied_version is None or self.applied_version == self.effective_config_version


# =============================================================================
# Capability Manager
# =============================================================================

class CapabilityManager:
    """
    Manages capability state for a runtime.
    
    Provides:
    - Multi-state capability tracking (not just boolean)
    - State change notification
    - Dependency resolution
    
    Invariants:
    - One canonical authority per runtime
    - States are distinct and not collapsed
    - State changes are versioned and tracked
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._capabilities: Dict[str, CapabilityDescriptor] = {}  # id -> descriptor
        self._statuses: Dict[str, CapabilityStatus] = {}  # id -> status
        self._lock = __import__("threading").Lock()
        self._resolution_version = 1
        self._round = 0
    
    @property
    def runtime_id(self) -> str:
        return self._runtime_id
    
    def register_capability(self, descriptor: CapabilityDescriptor) -> None:
        """Register a capability definition."""
        with self._lock:
            self._capabilities[descriptor.capability_id.value] = descriptor
            
            # Initialize status with defaults
            self._statuses[descriptor.capability_id.value] = CapabilityStatus(
                capability_id=descriptor.capability_id.value,
                implemented=True,  # If we have the descriptor, it's implemented
                configured=False,  # May need config first
                enabled=False,
                available=False,
                healthy=True,
                ready=False,
            )
    
    def set_configured(self, capability_id: str) -> None:
        """Mark a capability as configured."""
        with self._lock:
            if capability_id in self._statuses:
                status = self._statuses[capability_id]
                self._statuses[capability_id] = dataclass_replace(status, configured=True)
    
    def set_enabled(self, capability_id: str) -> None:
        """Mark a capability as enabled."""
        with self._lock:
            if capability_id in self._statuses:
                status = self._statuses[capability_id]
                self._statuses[capability_id] = dataclass_replace(status, enabled=True)
    
    def set_available(self, capability_id: str) -> None:
        """Mark a capability as available (all dependencies satisfied)."""
        with self._lock:
            if capability_id in self._statuses:
                status = self._statuses[capability_id]
                self._statuses[capability_id] = dataclass_replace(status, available=True)
    
    def set_ready(self, capability_id: str) -> None:
        """Mark a capability as ready."""
        with self._lock:
            if capability_id in self._statuses:
                status = self._statuses[capability_id]
                self._statuses[capability_id] = dataclass_replace(status, ready=True)
    
    def set_active(self, capability_id: str) -> None:
        """Mark a capability as active."""
        with self._lock:
            if capability_id in self._statuses:
                status = self._statuses[capability_id]
                self._statuses[capability_id] = dataclass_replace(status, active=True)
    
    def set_error(self, capability_id: str, message: str) -> None:
        """Mark a capability as having an error."""
        with self._lock:
            if capability_id in self._statuses:
                status = self._statuses[capability_id]
                self._statuses[capability_id] = dataclass_replace(
                    status,
                    healthy=False,
                    available=False,
                    ready=False,
                    active=False,
                    error_message=message
                )
    
    def get_status(self, capability_id: str) -> Optional[CapabilityStatus]:
        """Get the current status of a capability."""
        return self._statuses.get(capability_id)
    
    def get_all_statuses(self) -> Dict[str, CapabilityStatus]:
        """Get all capability statuses."""
        with self._lock:
            return dict(self._statuses)
    
    def resolve_capabilities(self) -> CapabilityResolution:
        """
        Resolve all capabilities and return current resolution.
        
        This is called to compute the effective capability state after
        configuration changes or other events.
        """
        with self._lock:
            self._round += 1
            
            # Build status map
            statuses = {}
            for cap_id, descriptor in self._capabilities.items():
                status = self._statuses.get(cap_id)
                
                if not status:
                    # Not registered - mark as not implemented
                    status = CapabilityStatus(
                        capability_id=cap_id,
                        implemented=False,
                        configured=False,
                        enabled=False,
                        available=False,
                        healthy=True,
                        ready=False,
                    )
                
                statuses[cap_id] = status
            
            self._resolution_version += 1
            
            return CapabilityResolution(
                runtime_id=self._runtime_id,
                timestamp=time.monotonic(),
                capabilities_by_id=dict(self._capabilities),
                statuses_by_id=statuses,
                resolved_version=self._resolution_version,
                resolution_round=self._round
            )
    
    def get_snapshot(self, effective_config_version: int) -> CapabilitySnapshot:
        """Create a snapshot of current capability state."""
        import uuid
        
        with self._lock:
            return CapabilitySnapshot(
                snapshot_id=str(uuid.uuid4()),
                runtime_id=self._runtime_id,
                effective_config_version=effective_config_version,
                capability_statuses=dict(self._statuses),
                applied_version=None,
                created_at=time.monotonic()
            )
    
    def get_capability_count(self) -> int:
        """Return total number of registered capabilities."""
        with self._lock:
            return len(self._capabilities)


# =============================================================================
# Dataclass helper (for frozen dataclasses)
def dataclass_replace(instance: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass.
    
    Helper for Python < 3.12 compatibility.
    """
    import copy
    new_instance = copy.copy(instance)
    for key, value in kwargs.items():
        object.__setattr__(new_instance, key, value)
    return new_instance


# =============================================================================
# Public API exports
# =============================================================================

__all__ = [
    # IDs
    "CapabilityId",
    
    # States
    "CapabilityState",
    
    # Descriptors and Statuses
    "CapabilityDescriptor",
    "CapabilityStatus",
    "CapabilityResolution",
    
    # Snapshot
    "CapabilitySnapshot",
    
    # Manager
    "CapabilityManager",
    
    # Utilities
    "dataclass_replace",
]