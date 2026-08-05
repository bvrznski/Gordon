# Runtime Monitor - Observability and Health Authority
# ====================================================

"""
Runtime monitor for observing model runtime behavior.

This module provides:
- Inference metrics tracking
- Queue metrics observation
- Resource metrics monitoring
- Health status reporting

Architecture Principle: Monitoring is observational only.
"""

from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Optional,
)
from enum import Enum, auto
import time


# =============================================================================
# HEALTH STATES
# =============================================================================


class HealthStatus(Enum):
    """Health status of a runtime component."""
    
    UNKNOWN = "unknown"         # Not yet checked
    STARTING = "starting"       # Initializing
    HEALTHY = "healthy"         # Operating normally
    DEGRADED = "degraded"       # Operating with reduced capability
    UNHEALTHY = "unhealthy"     # Failing to operate
    RECOVERING = "recovering"   # Attempting recovery
    STOPPING = "stopping"       # Shutting down
    STOPPED = "stopped"         # Stopped


# =============================================================================
# METRICS DATA TYPES
# =============================================================================


@dataclass(frozen=True)
class InferenceMetrics:
    """
    Immutable record of inference metrics.
    
    Metrics are observational - they do NOT affect runtime behavior.
    """
    
    total_requests: int             # Total inference requests processed
    successful_requests: int        # Successfully completed requests
    
    # Timing (in milliseconds)
    average_latency_ms: float       # Average request latency
    p50_latency_ms: float           # 50th percentile latency
    p95_latency_ms: float           # 95th percentile latency
    p99_latency_ms: float           # 99th percentile latency
    
    # Rate metrics
    requests_per_second: float      # Current RPS
    
    # Failure metrics
    failed_requests: int = 0        # Failed requests
    cancelled_requests: int = 0     # Cancelled requests
    
    @property
    def success_rate(self) -> float:
        """Return success rate as percentage."""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100


@dataclass(frozen=True)
class QueueMetrics:
    """
    Immutable record of queue metrics.
    
    Metrics are observational - they do NOT affect runtime behavior.
    """
    
    pending_count: int              # Requests waiting in queue
    active_count: int               # Requests currently processing
    
    # Capacity
    queue_size_limit: int           # Maximum queue capacity
    max_pending_seen: int = 0       # Peak pending count observed
    
    # Timing
    average_wait_ms: float = 0.0    # Average time in queue
    longest_wait_ms: float = 0.0    # Longest wait observed
    
    @property
    def utilization_percent(self) -> float:
        """Return queue utilization as percentage."""
        if self.queue_size_limit == 0:
            return 0.0
        return (self.pending_count / self.queue_size_limit) * 100


@dataclass(frozen=True)
class ResourceMetrics:
    """
    Immutable record of resource metrics.
    
    Metrics are observational - they do NOT affect runtime behavior.
    """
    
    # VRAM metrics
    vram_total_bytes: int           # Total available VRAM
    vram_allocated_bytes: int       # Currently allocated VRAM
    
    @property
    def vram_utilization_percent(self) -> float:
        """Return VRAM utilization as percentage."""
        if self.vram_total_bytes == 0:
            return 0.0
        return (self.vram_allocated_bytes / self.vram_total_bytes) * 100
    
    # RAM metrics
    ram_total_bytes: int            # Total available RAM
    ram_allocated_bytes: int        # Currently allocated RAM
    
    @property
    def ram_utilization_percent(self) -> float:
        """Return RAM utilization as percentage."""
        if self.ram_total_bytes == 0:
            return 0.0
        return (self.ram_allocated_bytes / self.ram_total_bytes) * 100


@dataclass(frozen=True)
class HealthReport:
    """
    Immutable health report.
    
    Contains status of all monitored components.
    """
    
    timestamp: float                # When report was generated
    
    runtime_status: HealthStatus    # Overall runtime health
    model_load_status: HealthStatus # Model loading system health
    queue_status: HealthStatus      # Inference queue health
    resource_status: HealthStatus   # Resource allocator health
    
    # Detailed component statuses
    components: Dict[str, HealthStatus] = field(default_factory=dict)
    
    @property
    def is_healthy(self) -> bool:
        """Check if runtime is healthy."""
        unhealthy_states = {
            HealthStatus.UNHEALTHY,
            HealthStatus.RECOVERING,
            HealthStatus.STOPPING,
            HealthStatus.STOPPED,
        }
        
        all_statuses = list(self.components.values()) + [
            self.runtime_status,
            self.model_load_status,
            self.queue_status,
            self.resource_status,
        ]
        
        return not any(status in unhealthy_states for status in all_statuses)


# =============================================================================
# RUNTIME MONITOR
# =============================================================================


class RuntimeMonitor:
    """
    Canonical runtime monitoring authority.
    
    This is the SINGLE canonical authority for observing model runtime behavior.
    
    Responsibilities:
        - Track inference metrics (latency, throughput, success rate)
        - Monitor queue state (pending, active, capacity)
        - Observe resource usage (VRAM, RAM utilization)
        - Report health status
    
    Does NOT:
        - Change runtime behavior
        - Modify runtime state
        - Make scheduling decisions
    
    Architecture Invariants:
        - Exactly ONE monitor instance exists
        - Monitoring is passive/observational only
        - No side effects from monitoring operations
    """
    
    def __init__(self):
        """Initialize the runtime monitor."""
        # Metrics storage
        self._inference_metrics: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cancelled_requests": 0,
            "latencies_ms": [],
            "start_times": [],
        }
        
        self._queue_metrics: Dict[str, Any] = {
            "pending_count": 0,
            "active_count": 0,
            "queue_limit": 10000,
            "max_seen_pending": 0,
            "wait_times_ms": [],
        }
        
        self._resource_metrics: Dict[str, int] = {
            "vram_total_bytes": 16 * 1024 * 1024 * 1024,  # 16 GB default
            "vram_allocated_bytes": 0,
            "ram_total_bytes": 32 * 1024 * 1024 * 1024,   # 32 GB default
            "ram_allocated_bytes": 0,
        }
        
        # Health tracking
        self._component_health: Dict[str, HealthStatus] = {
            "runtime": HealthStatus.STARTING,
            "model_loader": HealthStatus.UNKNOWN,
            "inference_queue": HealthStatus.UNKNOWN,
            "resource_allocator": HealthStatus.UNKNOWN,
        }
        
        # Statistics
        self._peak_vram_allocated = 0
        self._peak_ram_allocated = 0
        
        self._lock = __import__("threading").Lock()
    
    # -------------------------------------------------------------------------
    # Inference metrics (observational)
    # -------------------------------------------------------------------------
    
    def record_inference_request(self, success: bool = True) -> None:
        """Record an inference request."""
        with self._lock:
            self._inference_metrics["total_requests"] += 1
            
            if success:
                self._inference_metrics["successful_requests"] += 1
            else:
                self._inference_metrics["failed_requests"] += 1
    
    def record_inference_latency(self, latency_ms: float) -> None:
        """Record inference latency."""
        with self._lock:
            latencies = self._inference_metrics["latencies_ms"]
            latencies.append(latency_ms)
            
            # Keep only last 1000 for statistics
            if len(latencies) > 1000:
                latencies.pop(0)
    
    def record_request_cancelled(self) -> None:
        """Record a cancelled request."""
        with self._lock:
            self._inference_metrics["cancelled_requests"] += 1
    
    # -------------------------------------------------------------------------
    # Queue metrics (observational)
    # -------------------------------------------------------------------------
    
    def update_queue_pending(self, count: int) -> None:
        """Update pending queue count."""
        with self._lock:
            self._queue_metrics["pending_count"] = count
            self._queue_metrics["max_seen_pending"] = max(
                self._queue_metrics["max_seen_pending"],
                count
            )
    
    def update_queue_active(self, count: int) -> None:
        """Update active queue count."""
        with self._lock:
            self._queue_metrics["active_count"] = count
    
    def record_queue_wait_time(self, wait_ms: float) -> None:
        """Record a request's wait time in queue."""
        with self._lock:
            wait_times = self._queue_metrics["wait_times_ms"]
            wait_times.append(wait_ms)
            
            # Keep only last 1000 for statistics
            if len(wait_times) > 1000:
                wait_times.pop(0)
    
    # -------------------------------------------------------------------------
    # Resource metrics (observational)
    # -------------------------------------------------------------------------
    
    def update_vram_allocated(self, bytes_allocated: int) -> None:
        """Update VRAM allocation."""
        with self._lock:
            self._resource_metrics["vram_allocated_bytes"] = bytes_allocated
            self._peak_vram_allocated = max(
                self._peak_vram_allocated,
                bytes_allocated
            )
    
    def update_ram_allocated(self, bytes_allocated: int) -> None:
        """Update RAM allocation."""
        with self._lock:
            self._resource_metrics["ram_allocated_bytes"] = bytes_allocated
            self._peak_ram_allocated = max(
                self._peak_ram_allocated,
                bytes_allocated
            )
    
    # -------------------------------------------------------------------------
    # Health reporting (observational)
    # -------------------------------------------------------------------------
    
    def set_component_health(self, component_id: str, status: HealthStatus) -> None:
        """Set health status for a component."""
        with self._lock:
            self._component_health[component_id] = status
    
    def set_runtime_status(self, status: HealthStatus) -> None:
        """Set overall runtime status."""
        self.set_component_health("runtime", status)
    
    # -------------------------------------------------------------------------
    # Report generation (observational)
    # -------------------------------------------------------------------------
    
    def get_inference_metrics(self) -> InferenceMetrics:
        """
        Get current inference metrics.
        
        Returns:
            InferenceMetrics with current values
        """
        with self._lock:
            latencies = self._inference_metrics["latencies_ms"]
            
            if latencies:
                sorted_latencies = sorted(latencies)
                
                return InferenceMetrics(
                    total_requests=self._inference_metrics["total_requests"],
                    successful_requests=self._inference_metrics["successful_requests"],
                    failed_requests=self._inference_metrics["failed_requests"],
                    cancelled_requests=self._inference_metrics["cancelled_requests"],
                    average_latency_ms=sum(latencies) / len(latencies),
                    p50_latency_ms=sorted_latencies[len(sorted_latencies) // 2],
                    p95_latency_ms=sorted_latencies[int(len(sorted_latencies) * 0.95)],
                    p99_latency_ms=sorted_latencies[int(len(sorted_latencies) * 0.99)],
                    requests_per_second=self._inference_metrics["total_requests"] / (
                        (time.time() - self._inference_metrics.get("first_request", time.time()))
                        if "first_request" in self._inference_metrics else 1.0
                    ),
                )
            
            return InferenceMetrics(
                total_requests=self._inference_metrics["total_requests"],
                successful_requests=self._inference_metrics["successful_requests"],
                failed_requests=self._inference_metrics["failed_requests"],
                cancelled_requests=self._inference_metrics["cancelled_requests"],
                average_latency_ms=0.0,
                p50_latency_ms=0.0,
                p95_latency_ms=0.0,
                p99_latency_ms=0.0,
                requests_per_second=0.0,
            )
    
    def get_queue_metrics(self) -> QueueMetrics:
        """
        Get current queue metrics.
        
        Returns:
            QueueMetrics with current values
        """
        with self._lock:
            wait_times = self._queue_metrics["wait_times_ms"]
            
            avg_wait = (
                sum(wait_times) / len(wait_times)
                if wait_times else 0.0
            )
            
            return QueueMetrics(
                pending_count=self._queue_metrics["pending_count"],
                active_count=self._queue_metrics["active_count"],
                queue_size_limit=self._queue_metrics["queue_limit"],
                max_pending_seen=self._queue_metrics["max_seen_pending"],
                average_wait_ms=avg_wait,
                longest_wait_ms=max(wait_times) if wait_times else 0.0,
            )
    
    def get_resource_metrics(self) -> ResourceMetrics:
        """
        Get current resource metrics.
        
        Returns:
            ResourceMetrics with current values
        """
        with self._lock:
            return ResourceMetrics(
                vram_total_bytes=self._resource_metrics["vram_total_bytes"],
                vram_allocated_bytes=self._resource_metrics["vram_allocated_bytes"],
                ram_total_bytes=self._resource_metrics["ram_total_bytes"],
                ram_allocated_bytes=self._resource_metrics["ram_allocated_bytes"],
            )
    
    def get_health_report(self) -> HealthReport:
        """
        Get current health report.
        
        Returns:
            HealthReport with all component statuses
        """
        with self._lock:
            # Determine overall status based on components
            component_health = dict(self._component_health)
            
            # Get worst status
            status_priority = {
                HealthStatus.HEALTHY: 0,
                HealthStatus.DEGRADED: 1,
                HealthStatus.UNKNOWN: 2,
                HealthStatus.STARTING: 3,
                HealthStatus.RECOVERING: 4,
                HealthStatus.UNHEALTHY: 5,
                HealthStatus.STOPPING: 6,
                HealthStatus.STOPPED: 7,
            }
            
            worst_status = max(
                component_health.values(),
                key=lambda s: status_priority.get(s, 10)
            )
            
            return HealthReport(
                timestamp=time.time(),
                runtime_status=component_health.get("runtime", HealthStatus.UNKNOWN),
                model_load_status=component_health.get("model_loader", HealthStatus.UNKNOWN),
                queue_status=component_health.get("inference_queue", HealthStatus.UNKNOWN),
                resource_status=component_health.get("resource_allocator", HealthStatus.UNKNOWN),
                components=component_health,
            )


__all__ = [
    # Enums
    "HealthStatus",
    # Dataclasses
    "InferenceMetrics",
    "QueueMetrics",
    "ResourceMetrics",
    "HealthReport",
    # Monitor
    "RuntimeMonitor",
]