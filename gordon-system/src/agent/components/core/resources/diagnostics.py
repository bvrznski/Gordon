# Core ResourceManager Diagnostics
# ================================
"""
Diagnostic snapshots for observability and debugging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import time


@dataclass(frozen=True)
class ResourceReport:
    """
    Complete diagnostic report for a runtime's resource state.
    
    Used for observability dashboards and debugging.
    """
    runtime_id: str
    
    # State info
    inventory_version: int
    accounting_version: int
    
    # Counts
    resource_count: int
    allocation_count: int
    lease_count: int
    reservation_count: int
    
    # Capacity summary (per domain)
    capacity_summary: Dict[str, float] = field(default_factory=dict)  # domain -> free_capacity
    
    # Active resources by category
    active_reservations: List[Dict[str, Any]] = field(default_factory=list)
    active_allocations: List[Dict[str, Any]] = field(default_factory=list)
    active_leases: List[Dict[str, Any]] = field(default_factory=list)
    
    # Issues
    ownership_conflicts: int = 0
    pressure_levels: Dict[str, str] = field(default_factory=dict)  # domain -> level
    quota_violations: int = 0
    
    reclaimable_resources: int = 0
    leaks_detected: List[Dict[str, Any]] = field(default_factory=list)
    orphaned_resources: List[Dict[str, Any]] = field(default_factory=list)
    
    corruption_findings: List[Dict[str, Any]] = field(default_factory=list)
    split_brain_findings: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timing
    generated_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class EventLogSnapshot:
    """
    Snapshot of resource-related events.
    
    Used for debugging and audit trails.
    """
    runtime_id: str
    
    event_count: int
    events: List[Dict[str, Any]]  # Bounded list of recent events


@dataclass(frozen=True)
class ResourceManagerDiagnostics:
    """
    Diagnostic snapshot for ResourceManager.
    
    Provides a comprehensive view of the resource management state.
    """
    runtime_id: str
    
    state_version: int
    resource_count: int
    allocation_count: int
    lease_count: int
    reservation_count: int
    
    capacity_snapshot: Optional[Dict[str, Any]] = None  # Simplified snapshot
    
    event_count: int = 0


class ResourceManagerDiagnosticsCollector:
    """
    Collector for ResourceManager diagnostics.
    
    Aggregates information from all resource management components.
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # Event log (bounded)
        self._events: List[Dict[str, Any]] = []
        self._max_events = 1000
    
    def record_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Record a diagnostic event."""
        with self._lock:
            self._events.append({
                "timestamp_utc": time.time(),
                "event_type": event_type,
                "payload": dict(payload),
            })
            
            if len(self._events) > self._max_events:
                self._events = self._events[-self._max_events:]
    
    def get_report(self) -> ResourceReport:
        """Generate a diagnostic report."""
        with self._lock:
            return ResourceReport(
                runtime_id=self._runtime_id,
                inventory_version=0,  # Would come from ResourceManager
                accounting_version=0,  # Would come from CapacityModel
                resource_count=0,
                allocation_count=0,
                lease_count=0,
                reservation_count=0,
                generated_at_utc=time.time(),
            )
    
    def get_event_log(self) -> EventLogSnapshot:
        """Get current event log snapshot."""
        with self._lock:
            return EventLogSnapshot(
                runtime_id=self._runtime_id,
                event_count=len(self._events),
                events=list(self._events[-100:]),  # Last 100 events
            )


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "ResourceReport",
    "EventLogSnapshot",
    "ResourceManagerDiagnostics",
    "ResourceManagerDiagnosticsCollector",
]