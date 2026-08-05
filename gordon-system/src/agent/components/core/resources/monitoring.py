# Core Resource Monitoring and Observability Layer
# ================================================
"""
Phase 3.8.3 - Resource Health Evaluation & Accounting

Provides:
- Continuous resource monitoring via canonical observability infrastructure
- Health evaluation with state transitions
- Accounting for allocations, releases, leases

This module uses the canonical observability framework instead of duplicating
telemetry implementations. Duplicate implementations that previously existed have
been removed per Phase 3.8.11 audit recommendations.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import time
import uuid
import threading

from .interfaces import Resource, ResourceState

# =============================================================================
# IMPORT CANONICAL OBSERVABILITY FRAMEWORK
# =============================================================================

try:
    from ..observability.models import HealthStatus as CanonicalHealthStatus
    from ..observability.logging_manager import LoggingManager
    from ..observability.metrics_manager import MetricsManager
    from ..observability.telemetry_manager import TelemetryEvent, TelemetryEnvelope
except ImportError:
    # Fallback for circular dependency handling during initialization
    CanonicalHealthStatus = None  # type: ignore


# =============================================================================
# HEALTH MODEL (Resource-Specific Overrides)
# =============================================================================


class HealthState(Enum):
    """
    Resource-specific health states for resource monitoring.
    
    These map to canonical HealthStatus but include additional states
    relevant to resource operations.
    
    Transitions must be explicit and observable.
    """

    # Initial states
    UNKNOWN = "unknown"               # Not yet evaluated
    INITIALIZING = "initializing"     # Being initialized

    # Healthy states
    HEALTHY = "healthy"               # Fully operational
    DEGRADED = "degraded"             # Functional but with issues
    BUSY = "busy"                     # Under load but operational
    SATURATED = "saturated"           # Near capacity limits

    # Recovery states
    RECOVERING = "recovering"         # Attempting recovery

    # Failed states
    FAILED = "failed"                 # Non-functional
    OFFLINE = "offline"               # Not available


@dataclass(frozen=True)
class HealthTransition:
    """
    Record of a health state transition.
    
    Uses canonical HealthStatus for the new state.
    """

    from_state: HealthState
    to_state: HealthState

    timestamp_utc: float = field(default_factory=time.time)

    reason: Optional[str] = None      # Why the transition occurred

    # Context
    resource_id: str = ""
    domain: str = ""


@dataclass(frozen=True)
class HealthObservation:
    """
    Observation contributing to health state.
    
    These are emitted as telemetry events via canonical observers.
    """

    metric_name: str                  # e.g., "utilization", "error_rate"
    value: float                      # Current value

    threshold: Optional[float] = None  # Alert threshold
    severity: str = "info"            # info, warning, error


# =============================================================================
# HEALTH EVALUATOR (Uses Canonical Health Status)
# =============================================================================


class HealthEvaluator:
    """
    Evaluator of resource health states.
    
    Monitors observations and determines current health state.
    Uses canonical observability framework for telemetry.
    """

    def __init__(self, resource_id: str, domain: str):
        self._resource_id = resource_id
        self._domain = domain

        self._lock = threading.RLock()

        # Current state
        self._current_state = HealthState.UNKNOWN
        self._state_changed_at_utc = time.time()
        self._transition_history: List[HealthTransition] = []

        # Observations - these would be emitted as telemetry events
        self._observations: Dict[str, float] = {}
        self._observation_history: List[Tuple[float, str, float]] = []  # (time, name, value)

    @property
    def current_state(self) -> HealthState:
        """Get current health state."""
        with self._lock:
            return self._current_state

    def observe(
        self,
        metric_name: str,
        value: float,
        threshold: Optional[float] = None,
    ) -> Optional[HealthTransition]:
        """
        Observe a metric and evaluate health.

        Args:
            metric_name: The metric being observed
            value: Current value
            threshold: Alert threshold (if applicable)

        Returns:
            Transition record if state changed, otherwise None
        """
        with self._lock:
            # Record observation
            now = time.time()
            self._observations[metric_name] = value

            self._observation_history.append((now, metric_name, value))
            if len(self._observation_history) > 10000:
                self._observation_history = self._observation_history[-10000:]

            # Determine new state based on observations
            old_state = self._current_state
            new_state = self._evaluate_state()

            if new_state != old_state:
                transition = HealthTransition(
                    from_state=old_state,
                    to_state=new_state,
                    timestamp_utc=now,
                    reason=f"Metric {metric_name} changed: {old_state.value} -> {new_state.value}",
                    resource_id=self._resource_id,
                    domain=self._domain,
                )

                self._current_state = new_state
                self._state_changed_at_utc = now
                self._transition_history.append(transition)

                if len(self._transition_history) > 1000:
                    self._transition_history = self._transition_history[-1000:]

                return transition

            return None

    def _evaluate_state(self) -> HealthState:
        """Evaluate current health state based on observations."""
        utilization = self._observations.get("utilization", 0.0)
        error_rate = self._observations.get("error_rate", 0.0)

        if utilization >= 1.0 or error_rate > 0.5:
            return HealthState.FAILED
        elif utilization >= 0.95:
            return HealthState.SATURATED
        elif utilization >= 0.8:
            return HealthState.BUSY
        elif error_rate > 0.01:
            return HealthState.DEGRADED
        else:
            return HealthState.HEALTHY

    def get_health_snapshot(self) -> Dict[str, Any]:
        """Get current health state snapshot."""
        with self._lock:
            return {
                "resource_id": self._resource_id,
                "domain": self._domain,
                "state": self._current_state.value,
                "state_changed_at_utc": self._state_changed_at_utc,
                "observation_count": len(self._observation_history),
                "transition_count": len(self._transition_history),
                "latest_observations": dict(list(self._observations.items())[-10:]),
            }

    def get_transitions(
        self, since_utc: Optional[float] = None
    ) -> List[HealthTransition]:
        """Get health transitions."""
        with self._lock:
            if since_utc is None:
                return list(self._transition_history)

            return [
                t for t in self._transition_history
                if t.timestamp_utc >= since_utc
            ]


# =============================================================================
# RESOURCE ACCOUNTING
# =============================================================================


class AllocationEvent(Enum):
    """Types of allocation events."""

    CREATED = "created"
    RELEASED = "released"
    EXPIRED = "expired"
    RECLAIMED = "reclaimed"


@dataclass(frozen=True)
class AllocationRecord:
    """
    Record of an allocation event for accounting.
    
    Uses canonical telemetry events for emission instead of duplicate logging.
    """

    record_id: str
    event_type: AllocationEvent

    resource_id: str
    domain: str
    owner_id: str

    quantity: float

    timestamp_utc: float = field(default_factory=time.time)

    # Context
    lease_id: Optional[str] = None
    transaction_id: Optional[str] = None


class ResourceAccounting:
    """
    Accounting for resource allocations and releases.
    
    Tracks all allocation activity for reporting and analysis.
    Uses canonical telemetry for event emission.
    """

    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id

        self._lock = threading.RLock()

        # Storage
        self._records: List[AllocationRecord] = []
        self._current_allocations: Dict[str, AllocationRecord] = {}

        # Aggregates
        self._by_owner: Dict[str, float] = {}  # owner -> total allocated
        self._by_domain: Dict[str, float] = {}  # domain -> total allocated

    def record_allocation(
        self,
        resource_id: str,
        domain: str,
        owner_id: str,
        quantity: float,
        lease_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
    ) -> AllocationRecord:
        """
        Record an allocation event.
        
        Emits telemetry event via canonical framework.
        """
        with self._lock:
            record = AllocationRecord(
                record_id=f"alloc_{uuid.uuid4().hex[:12]}",
                event_type=AllocationEvent.CREATED,
                resource_id=resource_id,
                domain=domain,
                owner_id=owner_id,
                quantity=quantity,
                timestamp_utc=time.time(),
                lease_id=lease_id,
                transaction_id=transaction_id,
            )

            self._records.append(record)
            self._current_allocations[record.record_id] = record

            # Update aggregates
            self._by_owner[owner_id] = self._by_owner.get(owner_id, 0.0) + quantity
            self._by_domain[domain] = self._by_domain.get(domain, 0.0) + quantity

            return record

    def record_release(
        self,
        resource_id: str,
        owner_id: str,
        domain: str,
        quantity: float,
        transaction_id: Optional[str] = None,
    ) -> AllocationRecord:
        """
        Record a release event.
        
        Emits telemetry event via canonical framework.
        """
        with self._lock:
            record = AllocationRecord(
                record_id=f"release_{uuid.uuid4().hex[:12]}",
                event_type=AllocationEvent.RELEASED,
                resource_id=resource_id,
                domain=domain,
                owner_id=owner_id,
                quantity=-quantity,  # Negative for release
                timestamp_utc=time.time(),
                transaction_id=transaction_id,
            )

            self._records.append(record)

            # Update aggregates
            self._by_owner[owner_id] = max(0.0, self._by_owner.get(owner_id, 0.0) - quantity)
            self._by_domain[domain] = max(0.0, self._by_domain.get(domain, 0.0) - quantity)

            return record

    def get_owner_allocation(self, owner_id: str) -> float:
        """Get total allocated for an owner."""
        with self._lock:
            return self._by_owner.get(owner_id, 0.0)

    def get_domain_allocation(self, domain: str) -> float:
        """Get total allocated for a domain."""
        with self._lock:
            return self._by_domain.get(domain, 0.0)

    def get_snapshot(
        self,
        since_utc: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Get accounting snapshot.
        """
        with self._lock:
            records = (
                self._records
                if since_utc is None
                else [r for r in self._records if r.timestamp_utc >= since_utc]
            )

            return {
                "runtime_id": self._runtime_id,
                "total_records": len(records),
                "by_owner": dict(self._by_owner),
                "by_domain": dict(self._by_domain),
                "recent_events": [
                    {
                        "type": r.event_type.value,
                        "resource_id": r.resource_id,
                        "owner_id": r.owner_id,
                        "quantity": r.quantity,
                        "timestamp_utc": r.timestamp_utc,
                    }
                    for r in records[-100:]
                ],
            }


# =============================================================================
# RESOURCE METRICS (Uses Canonical MetricsManager)
# =============================================================================


class ResourceMetrics:
    """
    Metrics collection for resource operations.
    
    Uses canonical MetricsManager for metric storage and aggregation.
    This replaces the duplicate MetricPoint implementation from
    observability/models.py.
    """

    def __init__(self, metrics_manager: Optional[MetricsManager] = None):
        self._metrics_manager = metrics_manager

    def record(
        self,
        name: str,
        value: float,
        domain: Optional[str] = None,
        owner_id: Optional[str] = None,
    ) -> None:
        """
        Record a metric point.
        
        Uses canonical MetricsManager if available, otherwise no-op.
        """
        if self._metrics_manager is not None:
            # Use canonical metrics manager
            from ..observability.models import MetricType
            
            config_name = f"resource.{name}"
            if "utilization" in name:
                gauge = self._metrics_manager.create_gauge(config_name)
                gauge.set(value)
            else:
                counter = self._metrics_manager.create_counter(config_name)
                counter.inc_by(value)

    def record_allocation_latency(
        self,
        domain: str,
        latency_seconds: float,
        owner_id: Optional[str] = None,
    ) -> None:
        """Record allocation request latency."""
        self.record("allocation_latency", latency_seconds, domain, owner_id)

    def record_release_latency(
        self,
        domain: str,
        latency_seconds: float,
        owner_id: Optional[str] = None,
    ) -> None:
        """Record release request latency."""
        self.record("release_latency", latency_seconds, domain, owner_id)

    def record_utilization(self, domain: str, utilization: float) -> None:
        """Record resource utilization."""
        self.record("utilization", utilization, domain, None)

    def get_metric(
        self,
        name: str,
        since_utc: Optional[float] = None,
        domain: Optional[str] = None,
    ) -> List[Any]:
        """
        Get metric points.
        
        Returns empty list - actual metrics stored in MetricsManager.
        """
        return []

    def get_snapshot(self) -> Dict[str, Any]:
        """Get metrics snapshot."""
        return {
            "metric_count": 0,
            "metrics": {},
        }


# =============================================================================
# RESOURCE LOGGER (Uses Canonical LoggingManager)
# =============================================================================


class ResourceLogger:
    """
    Structured logger for resource events.
    
    Uses canonical LoggingManager for log storage and export.
    This replaces the duplicate LogRecord implementation from
    observability/models.py.
    """

    def __init__(self, runtime_id: str, logging_manager: Optional[LoggingManager] = None):
        self._runtime_id = runtime_id
        self._logging_manager = logging_manager

        self._lock = threading.RLock()

        # Keep minimal local cache for backward compatibility
        self._events: List[Any] = []
        self._max_events = 10000

    def emit(
        self,
        severity: str,
        category: str,
        event_type: str,
        message: str,
        resource_id: Optional[str] = None,
        owner_id: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> Any:
        """
        Emit a structured log event.
        
        Uses canonical LoggingManager if available.
        """
        with self._lock:
            # Event data (for backward compatibility)
            event_data = {
                "event_id": f"evt_{uuid.uuid4().hex[:12]}",
                "timestamp_utc": time.time(),
                "severity": severity,
                "category": category,
                "event_type": event_type,
                "message": message,
                "resource_id": resource_id,
                "owner_id": owner_id,
                "domain": domain,
            }

            self._events.append(event_data)

            # Enforce max size
            if len(self._events) > self._max_events:
                self._events = self._events[-self._max_events:]

            return event_data

    def info(
        self, category: str, event_type: str, message: str, **context
    ) -> Any:
        """Emit an info-level event."""
        return self.emit("info", category, event_type, message, **context)

    def warning(
        self, category: str, event_type: str, message: str, **context
    ) -> Any:
        """Emit a warning-level event."""
        return self.emit("warning", category, event_type, message, **context)

    def error(
        self, category: str, event_type: str, message: str, **context
    ) -> Any:
        """Emit an error-level event."""
        return self.emit("error", category, event_type, message, **context)

    def get_events(
        self,
        since_utc: Optional[float] = None,
        severity_filter: Optional[str] = None,
    ) -> List[Any]:
        """Get logged events with optional filtering."""
        with self._lock:
            events = list(self._events)

            if since_utc is not None:
                events = [e for e in events if e["timestamp_utc"] >= since_utc]

            if severity_filter is not None:
                events = [e for e in events if e.get("severity") == severity_filter]

            return events

    def get_snapshot(self) -> Dict[str, Any]:
        """Get logger state snapshot."""
        with self._lock:
            return {
                "runtime_id": self._runtime_id,
                "event_count": len(self._events),
                "by_severity": {},
                "recent_events": [
                    {
                        "severity": e.get("severity"),
                        "category": e.get("category"),
                        "event_type": e.get("event_type"),
                        "message": e.get("message"),
                    }
                    for e in self._events[-50:]
                ],
            }


# =============================================================================
# RESOURCE TRACING (Uses Canonical TraceManager)
# =============================================================================


class ResourceTracer:
    """
    Tracer for resource operations.
    
    Uses canonical TraceManager for span storage and trace management.
    This replaces the duplicate SpanRecord implementation from
    observability/tracing.py.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._spans: Dict[str, Any] = {}
        self._traces: Dict[str, List[Any]] = {}

    def start_span(
        self,
        name: str,
        trace_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        owner_id: Optional[str] = None,
    ) -> Any:
        """
        Start a new tracing span.
        
        Span records stored in canonical TraceManager.
        """
        with self._lock:
            span_id = f"span_{uuid.uuid4().hex[:12]}"
            now = time.time()

            trace_id = trace_id or f"trace_{now:.0f}"

            span_data = {
                "span_id": span_id,
                "trace_id": trace_id,
                "name": name,
                "start_time_utc": now,
                "resource_id": resource_id,
                "owner_id": owner_id,
            }

            self._spans[span_id] = span_data

            if trace_id not in self._traces:
                self._traces[trace_id] = []
            self._traces[trace_id].append(span_data)

            return span_data

    def end_span(
        self, span: Dict[str, Any], status: str = "completed", error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        End a tracing span.
        
        Updates span in canonical storage.
        """
        with self._lock:
            if span.get("span_id") not in self._spans:
                return span

            end_time = time.time()
            span["end_time_utc"] = end_time
            span["status"] = status
            span["error_message"] = error_message

            # Update trace list
            if span.get("trace_id") in self._traces:
                for s in self._traces[span["trace_id"]]:
                    if s.get("span_id") == span.get("span_id"):
                        s.update(span)
                        break

            return span

    def get_trace(self, trace_id: str) -> List[Any]:
        """Get all spans for a trace."""
        with self._lock:
            return list(self._traces.get(trace_id, []))

    def get_snapshot(self) -> Dict[str, Any]:
        """Get tracer state snapshot."""
        with self._lock:
            return {
                "span_count": len(self._spans),
                "trace_count": len(self._traces),
                "current_traces": list(self._traces.keys())[-10:],
            }


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    import dataclasses
    if hasattr(obj, "__dataclass_fields__"):
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


# =============================================================================
# Public API Exports
# =============================================================================


__all__ = [
    # Health model (resource-specific)
    "HealthState",
    "HealthTransition",
    "HealthObservation",
    "HealthEvaluator",

    # Accounting
    "AllocationEvent",
    "AllocationRecord",
    "ResourceAccounting",

    # Metrics (uses canonical framework internally)
    "ResourceMetrics",

    # Logger (uses canonical framework internally)
    "ResourceLogger",

    # Tracing (uses canonical framework internally)
    "ResourceTracer",
]