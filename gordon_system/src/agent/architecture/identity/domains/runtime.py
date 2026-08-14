# Runtime, Process & Boot-Session Identities - Phase 3.19.3
# =============================================================

"""
Runtime, Process, and Boot-Session identity types.

Every Gordon runtime instance must possess:
    - Application Identity (which application is running)
    - Runtime Instance Identity (this specific instance)
    - Boot Session Identity (current boot session, restart detection)
    
RUNTIME IDENTITY HIERARCHY:
    ApplicationIdentity     - Which application
        └── RuntimeInstanceId   - This instance
            ├── BootSessionId       - Current boot session
            └── ProcessId           - OS process identifier
            
INVARIANTS:
    RT-001: Application identity never changes during execution
    RT-002: Runtime instance identity is unique across restarts
    RT-003: Boot session identity changes on every restart
    RT-004: No two instances share the same runtime identity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import uuid
import time as _time_module


# =============================================================================
# APPLICATION IDENTITY
# =============================================================================


@dataclass(frozen=True)
class ApplicationIdentity:
    """
    Canonical identity for a Gordon application.
    
    The application identity identifies which application is running,
    independent of instance or session.
    
    INVARIANTS:
        APP-001: Application identity is immutable and never changes
        APP-002: Each unique application has its own distinct ID
        APP-003: Application IDs are globally unique
        
    PARAMETERS:
        name          - Human-readable application name
        version       - Application version string
        build_id      - Build identifier (git commit, timestamp, etc.)
        namespace     - Namespace for multi-tenant deployments
    """
    
    name: str
    version: str = "1.0.0"
    build_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    namespace: Optional[str] = None
    
    @classmethod
    def from_string(cls, value: str) -> "ApplicationIdentity":
        """Parse an application identity string."""
        parts = value.split(":")
        
        if len(parts) < 2:
            raise ValueError(f"Invalid ApplicationIdentity format: {value}")
        
        name = parts[0]
        version = parts[1] if len(parts) > 1 else "1.0.0"
        
        return cls(
            name=name,
            version=version,
            namespace=parts[2] if len(parts) > 2 else None,
        )
    
    def to_string(self) -> str:
        """Serialize to canonical string representation."""
        parts = [self.name, self.version]
        if self.namespace:
            parts.append(self.namespace)
        return ":".join(parts)
    
    @property
    def is_production(self) -> bool:
        """Check if this is a production build."""
        return "prod" in (self.namespace or "").lower()
    
    @property
    def is_stable(self) -> bool:
        """Check if version indicates stable release."""
        try:
            major, minor, patch = self.version.split(".")
            # Stable if patch >= 0 and not containing dev/rc/alpha/beta
            return "dev" not in self.version.lower() and "rc" not in self.version.lower()
        except ValueError:
            return False


# =============================================================================
# RUNTIME INSTANCE IDENTITY
# =============================================================================


@dataclass(frozen=True)
class RuntimeInstanceId:
    """
    Canonical identity for a runtime instance.
    
    Each time Gordon starts, it receives a new unique runtime instance ID.
    
    INVARIANTS:
        RTI-001: Every runtime has exactly one instance ID
        RTI-002: Instance IDs are globally unique across all processes
        RTI-003: Instance ID never changes during execution lifetime
        RTI-004: No two instances share the same ID (even across restarts)
        
    PARAMETERS:
        value         - The actual UUID string
        created_at    - When this instance was created
    """
    
    value: str = field(default_factory=lambda: f"rt_{uuid.uuid4().hex[:20]}")
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def generate(cls) -> "RuntimeInstanceId":
        """Generate a new runtime instance ID."""
        return cls()
    
    @classmethod
    def from_string(cls, value: str) -> "RuntimeInstanceId":
        """Parse a string into RuntimeInstanceId."""
        if not value.startswith("rt_"):
            raise ValueError(f"Invalid RuntimeInstanceId format: {value}")
        return cls(value=value)
    
    def to_string(self) -> str:
        """Serialize to canonical string representation."""
        return self.value
    
    @property
    def age_seconds(self) -> float:
        """Return how long this instance has been running (in seconds)."""
        return _time_module.monotonic() - self.created_at_utc


# =============================================================================
# BOOT SESSION IDENTITY  
# =============================================================================


@dataclass(frozen=True)
class BootSessionId:
    """
    Canonical identifier for a boot session.
    
    A boot session represents one complete execution cycle of Gordon.
    Every restart creates a new boot session.
    
    INVARIANTS:
        BS-001: Every boot session has exactly one ID
        BS-002: Session IDs are unique per process lifetime  
        BS-003: Old sessions are invalidated on restart
        BS-004: BootSessionId changes on every Gordon startup
        
    PARAMETERS:
        value         - The actual UUID string
        created_at    - When the session was started
    """
    
    value: str = field(default_factory=lambda: f"bs_{uuid.uuid4().hex[:20]}")
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def generate(cls) -> "BootSessionId":
        """Generate a new boot session ID."""
        return cls()
    
    @classmethod
    def from_string(cls, value: str) -> "BootSessionId":
        """Parse a string into BootSessionId."""
        if not value.startswith("bs_"):
            raise ValueError(f"Invalid BootSessionId format: {value}")
        return cls(value=value)
    
    def to_string(self) -> str:
        """Serialize to canonical string representation."""
        return self.value
    
    @property
    def session_duration_seconds(self) -> float:
        """Return current session duration in seconds."""
        return _time_module.monotonic() - self.created_at_utc


# =============================================================================
# PROCESS IDENTITY
# =============================================================================


@dataclass(frozen=True)
class ProcessId:
    """
    Canonical identity for an OS process.
    
    While not all Gordon components run in separate processes,
    some do (e.g., worker processes, distributed nodes).
    
    INVARIANTS:
        PROC-001: Every process has exactly one process ID
        PROC-002: Process IDs are unique within their namespace
        PROC-003: PID can change on restart (new process)
        
    PARAMETERS:
        pid           - OS process identifier
        parent_pid    - Parent process identifier (if any)
    """
    
    pid: int = field(default_factory=lambda: hash(uuid.uuid4()) & 0xFFFFFFFF)
    parent_pid: Optional[int] = None
    
    @classmethod
    def current(cls) -> "ProcessId":
        """Get the current process ID."""
        import os
        return cls(pid=os.getpid())
    
    @classmethod
    def from_string(cls, value: str) -> "ProcessId":
        """Parse a string into ProcessId."""
        parts = value.split(":")
        pid = int(parts[0])
        parent_pid = int(parts[1]) if len(parts) > 1 else None
        return cls(pid=pid, parent_pid=parent_pid)
    
    def to_string(self) -> str:
        """Serialize to canonical string representation."""
        if self.parent_pid is not None:
            return f"{self.pid}:{self.parent_pid}"
        return str(self.pid)


# =============================================================================
# RUNTIME IDENTITY GROUP
# =============================================================================


@dataclass(frozen=True)
class RuntimeIdentityGroup:
    """
    Container for all runtime identities of a single Gordon execution.
    
    This groups together the application, instance, boot session, and process
    identities that belong to one complete runtime execution.
    
    INVARIANTS:
        RIG-001: All contained identities are consistent with each other
        RIG-002: Application identity is immutable across all instances
        RIG-003: Runtime instance ID changes on every restart
        
    PARAMETERS:
        application      - Which application is running
        instance         - This specific instance
        boot_session     - Current boot session
        process          - OS process information (if applicable)
    """
    
    application: ApplicationIdentity
    instance: RuntimeInstanceId
    boot_session: BootSessionId
    process: Optional[ProcessId] = None
    
    @property
    def runtime_id(self) -> str:
        """Get a combined runtime identifier string."""
        parts = [
            self.application.name,
            self.instance.value,
            self.boot_session.value,
        ]
        return ":".join(parts)
    
    @classmethod
    def create(cls, application_name: str = "gordon") -> "RuntimeIdentityGroup":
        """Create a new runtime identity group."""
        return cls(
            application=ApplicationIdentity(name=application_name),
            instance=RuntimeInstanceId.generate(),
            boot_session=BootSessionId.generate(),
            process=None,
        )
    
    def is_new_boot(self, other: "RuntimeIdentityGroup") -> bool:
        """
        Check if this represents a new boot session compared to other.
        
        Returns True if boot_session differs (indicates restart).
        """
        return self.boot_session.value != other.boot_session.value


# =============================================================================
# IDENTITY REGISTRY FOR RUNTIME
# =============================================================================


class RuntimeIdentityRegistry:
    """
    Registry for runtime identities within a Gordon execution context.
    
    Provides utilities for identity lookup, validation, and lifecycle
    management of runtime identities.
    
    INVARIANTS:
        RIR-001: No duplicate runtime instance IDs
        RIR-002: Boot session is consistent across all entities in same boot
        RIR-003: Application identity is constant across all instances
        
    METHODS:
        register_instance()   - Register a new runtime instance
        get_instance()        - Look up an instance by ID
        validate_boot_session()- Check if identity belongs to current boot
        clear_stale()         - Remove expired registrations
    """
    
    def __init__(self):
        self._instances: dict[str, RuntimeInstanceId] = {}
        self._boot_sessions: dict[str, BootSessionId] = {}
        self._applications: dict[str, ApplicationIdentity] = {}
    
    def register_instance(self, instance: RuntimeInstanceId) -> bool:
        """Register a runtime instance."""
        if instance.value in self._instances:
            return False
        self._instances[instance.value] = instance
        return True
    
    def get_instance(self, value: str) -> Optional[RuntimeInstanceId]:
        """Look up an instance by its ID."""
        return self._instances.get(value)
    
    def validate_boot_session(
        self,
        boot_session_id: BootSessionId,
    ) -> bool:
        """Check if the given boot session is currently active."""
        return boot_session_id.value in self._boot_sessions
    
    def register_boot_session(self, session: BootSessionId) -> None:
        """Register a boot session as active."""
        self._boot_sessions[session.value] = session
    
    def clear_stale(self, max_age_seconds: float = 3600.0) -> int:
        """
        Remove expired instance registrations.
        
        Returns count of removed entries.
        """
        current_time = _time_module.monotonic()
        stale = [
            key
            for key, instance in self._instances.items()
            if current_time - instance.created_at_utc > max_age_seconds
        ]
        for key in stale:
            del self._instances[key]
        return len(stale)


__all__ = [
    "ApplicationIdentity",
    "RuntimeInstanceId", 
    "BootSessionId",
    "ProcessId",
    "RuntimeIdentityGroup",
    "RuntimeIdentityRegistry",
]