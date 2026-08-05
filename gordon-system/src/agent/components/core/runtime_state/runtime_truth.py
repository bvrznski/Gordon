# Core Runtime Truth Publication System
# ======================================

"""
Runtime truth publication for observability.

Provides:
- RuntimeTruth: The canonical aggregation of all observations
- RuntimeTruthSnapshot: Immutable point-in-time snapshots  
- RuntimeTruthVersion: Version tracking for truth evolution
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import uuid
import time
import threading

# =============================================================================
# RUNTIME TRUTH VERSION
# =============================================================================


@dataclass(frozen=True)
class RuntimeTruthVersion:
    """
    A version of runtime truth.
    
    Each version represents a complete snapshot of truth at a moment in time,
    with version numbers increasing monotonically.
    """
    
    # Identifiers
    version_id: str          # Unique identifier for this version
    
    # Version number (monotonic)
    sequence_number: int     # Sequential version number
    
    # Timestamps  
    created_at_utc: float    # When this version was created
    monotonic_time: float    # For ordering versions
    
    # Previous version (for chaining)
    previous_version_id: Optional[str] = None  # Link to prior version
    
    def next(self) -> "RuntimeTruthVersion":
        """Create the next version in sequence."""
        return RuntimeTruthVersion(
            version_id=f"truth_ver_{uuid.uuid4().hex[:12]}",
            sequence_number=self.sequence_number + 1,
            created_at_utc=time.time(),
            monotonic_time=time.monotonic(),
            previous_version_id=self.version_id
        )


# =============================================================================
# RUNTIME TRUTH SNAPSHOT
# =============================================================================


@dataclass(frozen=True)
class RuntimeTruthSnapshot:
    """
    An immutable snapshot of runtime truth at a moment in time.
    
    Snapshots are used for:
    - Historical analysis and comparison
    - Debugging and audit trails
    - Deterministic replay
    
    They capture the complete state of truth at a point in time.
    """
    
    # Identifiers
    snapshot_id: str         # Unique identifier
    version_id: str          # Which truth version this represents
    
    # Timestamps
    captured_at_utc: float   # When snapshot was taken
    monotonic_time: float    # For ordering snapshots
    
    # Truth content (aggregated observations)
    health_status: Dict[str, Any] = field(default_factory=dict)
    integrity_status: Dict[str, Any] = field(default_factory=dict)
    heartbeat_status: Dict[str, Any] = field(default_factory=dict)
    
    # Summary statistics
    total_subjects: int = 0
    healthy_count: int = 0
    verified_count: int = 0
    
    @property
    def is_consistent(self) -> bool:
        """Check if this snapshot shows consistent state."""
        # No failures means consistent
        return self.healthy_count == self.total_subjects and self.total_subjects > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            "snapshot_id": self.snapshot_id,
            "version_id": self.version_id,
            "captured_at_utc": self.captured_at_utc,
            "total_subjects": self.total_subjects,
            "healthy_count": self.healthy_count,
            "verified_count": self.verified_count,
        }
    
    @classmethod
    def create(
        cls,
        version: RuntimeTruthVersion,
        health_status: Dict[str, Any],
        integrity_status: Dict[str, Any],
        heartbeat_status: Dict[str, Any]
    ) -> "RuntimeTruthSnapshot":
        """Create a new truth snapshot."""
        
        total = len(health_status) + len(integrity_status)
        healthy = sum(1 for v in health_status.values() if v.get("status") == "healthy")
        verified = sum(1 for v in integrity_status.values() if v.get("status") == "verified")
        
        return cls(
            snapshot_id=f"truth_snap_{uuid.uuid4().hex[:12]}",
            version_id=version.version_id,
            captured_at_utc=time.time(),
            monotonic_time=time.monotonic(),
            health_status=dict(health_status),
            integrity_status=dict(integrity_status),
            heartbeat_status=dict(heartbeat_status),
            total_subjects=total,
            healthy_count=healthy,
            verified_count=verified
        )


# =============================================================================
# RUNTIME TRUTH (CANONICAL AGGREGATION)
# =============================================================================


class RuntimeTruth:
    """
    Canonical aggregation of all runtime observations.
    
    This is THE ONE source of aggregated truth for runtime state. It owns:
    
    - Aggregates health, integrity, heartbeat, and other observation data
    - Produces immutable snapshots at each version
    - Tracks evolution of truth over time
    
    Runtime Truth Invariants:
        1. Truth aggregates observations (never replaces subsystem ownership)
        2. Truth is immutable per version (new versions create new state)
        3. Truth never owns runtime state directly  
        4. Truth is observational only (no direct mutation capability)
        5. Truth preserves provenance for all aggregated data
    """
    
    def __init__(self, runtime_id: str):
        """
        Initialize the RuntimeTruth system.
        
        Args:
            runtime_id: Unique identifier for this runtime instance
        """
        self._runtime_id = runtime_id
        
        # Core state
        self._lock = threading.RLock()
        
        # Current version
        self._current_version = RuntimeTruthVersion(
            version_id=f"truth_ver_{uuid.uuid4().hex[:12]}",
            sequence_number=0,
            created_at_utc=time.time(),
            monotonic_time=time.monotonic()
        )
        
        # Truth content (aggregated observations)
        self._health_status: Dict[str, Any] = {}
        self._integrity_status: Dict[str, Any] = {}
        self._heartbeat_status: Dict[str, Any] = {}
        
        # History of snapshots
        self._snapshots: List[RuntimeTruthSnapshot] = []
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this truth serves."""
        return self._runtime_id
    
    @property
    def current_version(self) -> RuntimeTruthVersion:
        """Get the current truth version."""
        with self._lock:
            return self._current_version
    
    # -------------------------------------------------------------------------
    # Truth Update Operations
    # -------------------------------------------------------------------------
    
    def update_health(
        self,
        subject: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> RuntimeTruthVersion:
        """
        Update health status for a subject.
        
        Args:
            subject: Entity being updated (ID, component name, etc.)
            status: Health status string (healthy, degraded, unhealthy, failed)
            details: Additional status details
            
        Returns:
            New truth version after update
        """
        with self._lock:
            # Update health status
            self._health_status[subject] = {
                "status": status,
                "updated_at_utc": time.time(),
                "details": details or {}
            }
            
            # Create next version and update current version
            new_version = self._current_version.next()
            self._current_version = new_version
            
            return new_version
    
    def update_integrity(
        self,
        subject: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> RuntimeTruthVersion:
        """
        Update integrity status for a subject.
        
        Args:
            subject: Entity being updated
            status: Integrity status string (verified, degraded, violated)
            details: Additional status details
            
        Returns:
            New truth version after update
        """
        with self._lock:
            # Update integrity status
            self._integrity_status[subject] = {
                "status": status,
                "updated_at_utc": time.time(),
                "details": details or {}
            }
            
            # Create next version and update current version
            new_version = self._current_version.next()
            self._current_version = new_version
            
            return new_version
    
    def update_heartbeat(
        self,
        source_id: str,
        is_active: bool,
        details: Optional[Dict[str, Any]] = None
    ) -> RuntimeTruthVersion:
        """
        Update heartbeat status for a source.
        
        Args:
            source_id: Heartbeat source identifier
            is_active: Whether the source is currently active
            details: Additional status details
            
        Returns:
            New truth version after update
        """
        with self._lock:
            # Update heartbeat status
            self._heartbeat_status[source_id] = {
                "is_active": is_active,
                "updated_at_utc": time.time(),
                "details": details or {}
            }
            
            # Create next version and update current version
            new_version = self._current_version.next()
            self._current_version = new_version
            
            return new_version
    
    # -------------------------------------------------------------------------
    # Snapshot Operations
    # -------------------------------------------------------------------------
    
    def take_snapshot(self) -> RuntimeTruthSnapshot:
        """
        Take a snapshot of current truth state.
        
        Returns:
            Immutable RuntimeTruthSnapshot with complete state at moment
        """
        with self._lock:
            # Create snapshot from current version
            snapshot = RuntimeTruthSnapshot.create(
                version=self._current_version,
                health_status=dict(self._health_status),
                integrity_status=dict(self._integrity_status),
                heartbeat_status=dict(self._heartbeat_status)
            )
            
            self._snapshots.append(snapshot)
            
            return snapshot
    
    def get_latest_snapshot(self) -> Optional[RuntimeTruthSnapshot]:
        """Get the most recent snapshot, if any."""
        with self._lock:
            if self._snapshots:
                return self._snapshots[-1]
            return None
    
    # -------------------------------------------------------------------------
    # Query Operations
    # -------------------------------------------------------------------------
    
    def get_health_status(self, subject: str) -> Optional[Dict[str, Any]]:
        """Get health status for a subject."""
        with self._lock:
            return self._health_status.get(subject)
    
    def get_integrity_status(self, subject: str) -> Optional[Dict[str, Any]]:
        """Get integrity status for a subject."""
        with self._lock:
            return self._integrity_status.get(subject)
    
    def get_heartbeat_status(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get heartbeat status for a source."""
        with self._lock:
            return self._heartbeat_status.get(source_id)
    
    # -------------------------------------------------------------------------
    # Status Aggregation
    # -------------------------------------------------------------------------
    
    @property
    def overall_health_status(self) -> str:
        """
        Get aggregated health status across all subjects.
        
        Priority: FAILED > UNHEALTHY > DEGRADED > HEALTHY
        """
        with self._lock:
            if not self._health_status:
                return "unknown"
            
            statuses = [v.get("status", "") for v in self._health_status.values()]
            
            for status in ("failed", "unhealthy", "degraded"):
                if status in statuses:
                    return status
            
            return "healthy"
    
    @property
    def overall_integrity_status(self) -> str:
        """
        Get aggregated integrity status across all subjects.
        
        Priority: VIOLATED > DEGRADED > VERIFIED
        """
        with self._lock:
            if not self._integrity_status:
                return "unknown"
            
            statuses = [v.get("status", "") for v in self._integrity_status.values()]
            
            for status in ("violated", "degraded"):
                if status in statuses:
                    return status
            
            return "verified"


# =============================================================================
# RUNTIME TRUTH PUBLISHER
# =============================================================================


class RuntimeTruthPublisher:
    """
    Publisher for runtime truth updates.
    
    Subsystems can subscribe to truth updates to stay informed of changes.
    """
    
    def __init__(self):
        """Initialize the publisher."""
        self._subscribers: List[callable] = []
        self._lock = threading.RLock()
    
    def subscribe(self, callback: callable) -> None:
        """Subscribe to truth updates."""
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)
    
    def unsubscribe(self, callback: callable) -> bool:
        """Unsubscribe from truth updates."""
        with self._lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)
                return True
            return False
    
    def publish(
        self,
        runtime_id: str,
        version: RuntimeTruthVersion,
        snapshot: Optional[RuntimeTruthSnapshot] = None
    ) -> None:
        """Publish a truth update to all subscribers."""
        with self._lock:
            for callback in list(self._subscribers):
                try:
                    callback(runtime_id, version, snapshot)
                except Exception:
                    pass  # Don't let subscriber errors affect main flow
    
    def clear_subscribers(self) -> None:
        """Remove all subscribers."""
        with self._lock:
            self._subscribers.clear()


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Versioning
    "RuntimeTruthVersion",
    
    # Snapshots  
    "RuntimeTruthSnapshot",
    
    # Authorities
    "RuntimeTruth",
    
    # Publishing
    "RuntimeTruthPublisher",
]