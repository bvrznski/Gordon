# Core Runtime Monitoring Events
# ==============================

"""
Events for runtime health, integrity, and observation changes.

Provides:
- HealthChanged: General health status change
- HealthDegraded: Health entered degraded state
- HealthRecovered: Health recovered from degradation
- IntegrityVerified: Integrity verification passed
- IntegrityViolationDetected: Integrity violation found
- RuntimeTruthUpdated: Truth version changed
- HeartbeatLost/Restored: Heartbeat signal changes
- WatchdogTriggered/Cleared: Watchdog activity
- RuntimeAnomalyDetected: General anomaly detection
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto
import uuid
import time


# =============================================================================
# EVENT TYPE ENUMERATION
# =============================================================================


class MonitoringEventType(Enum):
    """Types of monitoring events."""
    
    # Health events
    HEALTH_CHANGED = "health_changed"
    HEALTH_DEGRADED = "health_degraded" 
    HEALTH_RECOVERED = "health_recovered"
    HEALTH_FAILED = "health_failed"
    
    # Integrity events
    INTEGRITY_VERIFIED = "integrity_verified"
    INTEGRITY_VIOLATION_DETECTED = "integrity_violation_detected"
    INTEGRITY_DEGRADED = "integrity_degraded"
    
    # Truth events
    RUNTIME_TRUTH_UPDATED = "runtime_truth_updated"
    
    # Heartbeat events  
    HEARTBEAT_LOST = "heartbeat_lost"
    HEARTBEAT_RESTORED = "heartbeat_restored"
    
    # Watchdog events
    WATCHDOG_TRIGGERED = "watchdog_triggered"
    WATCHDOG_CLEARED = "watchdog_cleared"
    
    # Anomaly events
    RUNTIME_ANOMALY_DETECTED = "runtime_anomaly_detected"


# =============================================================================
# EVENT SEVERITY
# =============================================================================


class EventSeverity(Enum):
    """Event severity levels."""
    
    TRACE = "trace"       # Internal details (rarely logged)
    DEBUG = "debug"       # Detailed information for troubleshooting  
    INFO = "info"         # Notable events
    NOTICE = "notice"     # Important milestones
    WARNING = "warning"   # Potential issues
    ERROR = "error"       # Actual errors requiring attention
    CRITICAL = "critical" # System-impacting conditions


# =============================================================================
# RUNTIME MONITORING EVENT (BASE)
# =============================================================================


@dataclass(frozen=True)
class RuntimeMonitoringEvent:
    """
    Base class for all runtime monitoring events.
    
    Events are immutable and observational. They never become authorities.
    """
    
    event_id: str             # Unique identifier
    event_type: MonitoringEventType
    
    runtime_id: str           # Which runtime this is about
    
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    sequence_number: int = 0
    subject: Optional[str] = None
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    reason: Optional[str] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_important(self) -> bool:
        """Check if this event requires attention."""
        return self.severity in (EventSeverity.WARNING, EventSeverity.ERROR, EventSeverity.CRITICAL)
    
    @property
    def severity(self) -> EventSeverity:
        """Determine event severity based on type."""
        # Critical events
        if self.event_type in (
            MonitoringEventType.HEALTH_FAILED,
            MonitoringEventType.INTEGRITY_VIOLATION_DETECTED
        ):
            return EventSeverity.CRITICAL
        
        # Error-level events
        if self.event_type in (
            MonitoringEventType.RUNTIME_TRUTH_UPDATED,
            MonitoringEventType.WATCHDOG_TRIGGERED,
            MonitoringEventType.RUNTIME_ANOMALY_DETECTED
        ):
            return EventSeverity.ERROR
        
        # Warning-level events
        if self.event_type in (
            MonitoringEventType.HEALTH_DEGRADED,
            MonitoringEventType.HEARTBEAT_LOST,
            MonitoringEventType.INTEGRITY_DEGRADED
        ):
            return EventSeverity.WARNING
        
        # Notice-level events
        if self.event_type in (
            MonitoringEventType.HEALTH_RECOVERED,
            MonitoringEventType.HEARTBEAT_RESTORED,
            MonitoringEventType.WATCHDOG_CLEARED
        ):
            return EventSeverity.NOTICE
        
        # Info-level events
        return EventSeverity.INFO
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp_utc": self.timestamp_utc,
            "runtime_id": self.runtime_id,
            "sequence_number": self.sequence_number,
            "subject": self.subject,
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "reason": self.reason,
        }


# =============================================================================
# HEALTH EVENTS
# =============================================================================


@dataclass(frozen=True)
class HealthChanged(RuntimeMonitoringEvent):
    """
    A health status change event.
    
    Emitted when a subject's overall health changes, regardless of direction.
    """
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        subject: str,
        previous_status: Optional[str],
        new_status: str,
        reason: Optional[str] = None
    ) -> "HealthChanged":
        """Create a health changed event."""
        return cls(
            event_id=f"health_event_{uuid.uuid4().hex[:12]}",
            event_type=MonitoringEventType.HEALTH_CHANGED,
            runtime_id=runtime_id,
            subject=subject,
            previous_status=previous_status,
            new_status=new_status,
            reason=reason
        )


@dataclass(frozen=True)
class HealthDegraded(RuntimeMonitoringEvent):
    """
    A health degradation event.
    
    Emitted when a subject's health enters the degraded state.
    """
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        subject: str,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> "HealthDegraded":
        """Create a health degraded event."""
        return cls(
            event_id=f"health_event_{uuid.uuid4().hex[:12]}",
            event_type=MonitoringEventType.HEALTH_DEGRADED,
            runtime_id=runtime_id,
            subject=subject,
            previous_status="healthy",  # Usually degrade from healthy
            new_status="degraded",
            reason=reason or "Health degraded",
            extra_data=details or {}
        )


@dataclass(frozen=True)
class HealthRecovered(RuntimeMonitoringEvent):
    """
    A health recovery event.
    
    Emitted when a subject's health recovers from degraded/unhealthy state.
    """
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        subject: str,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> "HealthRecovered":
        """Create a health recovered event."""
        return cls(
            event_id=f"health_event_{uuid.uuid4().hex[:12]}",
            event_type=MonitoringEventType.HEALTH_RECOVERED,
            runtime_id=runtime_id,
            subject=subject,
            previous_status="degraded",  # Usually recover from degraded
            new_status="healthy",
            reason=reason or "Health recovered",
            extra_data=details or {}
        )


# =============================================================================
# INTEGRITY EVENTS
# =============================================================================


@dataclass(frozen=True)
class IntegrityVerified(RuntimeMonitoringEvent):
    """
    An integrity verification success event.
    
    Emitted when a subject's integrity passes all checks.
    """
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        subject: str,
        details: Optional[Dict[str, Any]] = None
    ) -> "IntegrityVerified":
        """Create an integrity verified event."""
        return cls(
            event_id=f"integrity_event_{uuid.uuid4().hex[:12]}",
            event_type=MonitoringEventType.INTEGRITY_VERIFIED,
            runtime_id=runtime_id,
            subject=subject,
            new_status="verified",
            extra_data=details or {}
        )


@dataclass(frozen=True)
class IntegrityViolationDetected(RuntimeMonitoringEvent):
    """
    An integrity violation detection event.
    
    Emitted when a subject has an architectural violation.
    """
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        subject: str,
        domain: Optional[str] = None,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> "IntegrityViolationDetected":
        """Create an integrity violation detected event."""
        return cls(
            event_id=f"integrity_event_{uuid.uuid4().hex[:12]}",
            event_type=MonitoringEventType.INTEGRITY_VIOLATION_DETECTED,
            runtime_id=runtime_id,
            subject=subject,
            previous_status="verified",  # Usually violated from verified
            new_status="violated",
            reason=reason or f"Integrity violation detected in {domain or 'unknown domain'}",
            extra_data=details or {}
        )


# =============================================================================
# RUNTIME TRUTH EVENTS
# =============================================================================


@dataclass(frozen=True)
class RuntimeTruthUpdated(RuntimeMonitoringEvent):
    """
    A runtime truth version update event.
    
    Emitted when the canonical truth aggregation updates to a new version.
    """
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        version_sequence: int,
        snapshot_summary: Optional[Dict[str, Any]] = None
    ) -> "RuntimeTruthUpdated":
        """Create a runtime truth updated event."""
        return cls(
            event_id=f"truth_event_{uuid.uuid4().hex[:12]}",
            event_type=MonitoringEventType.RUNTIME_TRUTH_UPDATED,
            runtime_id=runtime_id,
            previous_status=str(version_sequence - 1) if version_sequence > 0 else None,
            new_status=str(version_sequence),
            reason="Truth version updated",
            extra_data={
                "version": version_sequence,
                "snapshot_summary": snapshot_summary or {}
            }
        )


# =============================================================================
# HEARTBEAT EVENTS
# =============================================================================


@dataclass(frozen=True)
class HeartbeatLost(RuntimeMonitoringEvent):
    """
    A heartbeat loss event.
    
    Emitted when a registered heartbeat source loses its signal.
    """
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        source_id: str,
        missed_count: int = 1,
        details: Optional[Dict[str, Any]] = None
    ) -> "HeartbeatLost":
        """Create a heartbeat lost event."""
        return cls(
            event_id=f"heartbeat_event_{uuid.uuid4().hex[:12]}",
            event_type=MonitoringEventType.HEARTBEAT_LOST,
            runtime_id=runtime_id,
            subject=source_id,
            previous_status="active",
            new_status="lost",
            reason=f"Heartbeat lost after {missed_count} missed signals",
            extra_data=details or {}
        )


@dataclass(frozen=True)
class HeartbeatRestored(RuntimeMonitoringEvent):
    """
    A heartbeat restoration event.
    
    Emitted when a lost heartbeat source recovers its signal.
    """
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        source_id: str,
        recovery_reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> "HeartbeatRestored":
        """Create a heartbeat restored event."""
        return cls(
            event_id=f"heartbeat_event_{uuid.uuid4().hex[:12]}",
            event_type=MonitoringEventType.HEARTBEAT_RESTORED,
            runtime_id=runtime_id,
            subject=source_id,
            previous_status="lost",
            new_status="active",
            reason=recovery_reason or "Heartbeat signal restored",
            extra_data=details or {}
        )


# =============================================================================
# WATCHDOG EVENTS
# =============================================================================


@dataclass(frozen=True)
class WatchdogTriggered(RuntimeMonitoringEvent):
    """
    A watchdog trigger event.
    
    Emitted when a watchdog detects an anomaly.
    """
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        watchdog_name: str,
        check_name: Optional[str] = None,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> "WatchdogTriggered":
        """Create a watchdog triggered event."""
        return cls(
            event_id=f"watchdog_event_{uuid.uuid4().hex[:12]}",
            event_type=MonitoringEventType.WATCHDOG_TRIGGERED,
            runtime_id=runtime_id,
            subject=watchdog_name,
            previous_status="normal",
            new_status="triggered",
            reason=reason or f"Watchdog {watchdog_name} detected anomaly in {check_name or 'unknown check'}",
            extra_data=details or {}
        )


@dataclass(frozen=True)
class WatchdogCleared(RuntimeMonitoringEvent):
    """
    A watchdog clear event.
    
    Emitted when a triggered watchdog condition is resolved.
    """
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        watchdog_name: str,
        resolution_reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> "WatchdogCleared":
        """Create a watchdog cleared event."""
        return cls(
            event_id=f"watchdog_event_{uuid.uuid4().hex[:12]}",
            event_type=MonitoringEventType.WATCHDOG_CLEARED,
            runtime_id=runtime_id,
            subject=watchdog_name,
            previous_status="triggered",
            new_status="normal",
            reason=resolution_reason or f"Watchdog {watchdog_name} condition cleared",
            extra_data=details or {}
        )


# =============================================================================
# ANOMALY EVENTS
# =============================================================================


@dataclass(frozen=True)
class RuntimeAnomalyDetected(RuntimeMonitoringEvent):
    """
    A general runtime anomaly detection event.
    
    Emitted when the monitoring system detects an unexpected behavior pattern
    that doesn't fit other categories.
    """
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        anomaly_type: str,
        subject: Optional[str] = None,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> "RuntimeAnomalyDetected":
        """Create a runtime anomaly detected event."""
        return cls(
            event_id=f"anomaly_event_{uuid.uuid4().hex[:12]}",
            event_type=MonitoringEventType.RUNTIME_ANOMALY_DETECTED,
            runtime_id=runtime_id,
            subject=subject,
            previous_status="unknown",
            new_status="anomaly_detected",
            reason=reason or f"Runtime anomaly detected: {anomaly_type}",
            extra_data={
                "anomaly_type": anomaly_type,
                **(details or {})
            }
        )


# =============================================================================
# EVENT AGGREGATOR
# =============================================================================


class EventAggregator:
    """
    Aggregates monitoring events for analysis and reporting.
    
    Provides:
    - Event storage with bounded history
    - Event filtering by type, severity, time range
    - Summary statistics
    """
    
    def __init__(self, max_events: int = 1000):
        """Initialize the aggregator."""
        self._max_events = max_events
        self._events: List[RuntimeMonitoringEvent] = []
        self._lock = None  # Will be initialized when needed
    
    def _get_lock(self):
        """Get or initialize lock for thread safety."""
        import threading
        if self._lock is None:
            self._lock = threading.RLock()
        return self._lock
    
    def add_event(self, event: RuntimeMonitoringEvent) -> None:
        """Add an event to the aggregator."""
        import dataclasses
        
        lock = self._get_lock()
        with lock:
            # Assign sequence number - need to handle frozen dataclass
            if not self._events or event.runtime_id != self._events[-1].runtime_id:
                new_sequence_number = 0
            else:
                new_sequence_number = self._events[-1].sequence_number + 1
            
            # Create a new event with the sequence number set
            # Use dataclasses.replace since RuntimeMonitoringEvent is frozen
            try:
                updated_event = dataclasses.replace(event, sequence_number=new_sequence_number)
            except (TypeError, ValueError):
                # If replace fails (e.g., field doesn't exist), just use the original
                updated_event = event
            
            self._events.append(updated_event)
            
            # Limit history size
            if len(self._events) > self._max_events:
                self._events = self._events[-self._max_events:]
    
    def get_events(
        self,
        runtime_id: Optional[str] = None,
        event_type: Optional[MonitoringEventType] = None,
        since_timestamp: Optional[float] = None
    ) -> List[RuntimeMonitoringEvent]:
        """Get events with optional filtering."""
        lock = self._get_lock()
        with lock:
            results = list(self._events)
            
            if runtime_id is not None:
                results = [e for e in results if e.runtime_id == runtime_id]
            
            if event_type is not None:
                results = [e for e in results if e.event_type == event_type]
            
            if since_timestamp is not None:
                results = [e for e in results if e.timestamp_utc >= since_timestamp]
            
            return results
    
    def get_events_by_severity(
        self,
        severity: EventSeverity
    ) -> List[RuntimeMonitoringEvent]:
        """Get events matching a specific severity level."""
        lock = self._get_lock()
        with lock:
            return [e for e in self._events if e.severity == severity]
    
    def get_summary(self, runtime_id: Optional[str] = None) -> Dict[str, int]:
        """Get event count summary by type."""
        lock = self._get_lock()
        with lock:
            events = self._events
            if runtime_id is not None:
                events = [e for e in events if e.runtime_id == runtime_id]
            
            summary: Dict[str, int] = {}
            for event in events:
                key = f"{event.event_type.value}_{event.severity.value}"
                summary[key] = summary.get(key, 0) + 1
            
            return summary


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Event type enum
    "MonitoringEventType",
    
    # Severity levels
    "EventSeverity",
    
    # Base event class
    "RuntimeMonitoringEvent",
    
    # Health events
    "HealthChanged",
    "HealthDegraded", 
    "HealthRecovered",
    
    # Integrity events
    "IntegrityVerified",
    "IntegrityViolationDetected",
    
    # Truth events
    "RuntimeTruthUpdated",
    
    # Heartbeat events
    "HeartbeatLost",
    "HeartbeatRestored",
    
    # Watchdog events
    "WatchdogTriggered",
    "WatchdogCleared",
    
    # Anomaly events
    "RuntimeAnomalyDetected",
    
    # Utilities
    "EventAggregator",
]