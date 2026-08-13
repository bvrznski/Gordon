# Phase 3.11.14 - Cross-Stream Correlation Observability
# =========================================================

"""
Observability Module for Cross-Stream Correlation & Causation Architecture.

Provides passive monitoring and diagnostics for relationship operations.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum, auto
import time


# =============================================================================
# OBSERVATION TYPES
# =============================================================================


class ObservationType(Enum):
    """Types of observable events."""
    EDGE_CREATED = "edge_created"
    EDGE_READ = "edge_read"
    TRAVERSAL_STARTED = "traversal_started"
    TRAVERSAL_COMPLETED = "traversal_completed"
    GRAPH_SNAPSHOTTED = "graph_snapshotted"
    INTEGRITY_VERIFIED = "integrity_verified"
    AUTHORIZATION_REQUESTED = "authorization_requested"
    EPISODE_CREATED = "episode_created"


@dataclass(frozen=True)
class Observation:
    """
    One observation of a relationship graph operation.
    
    Passive monitoring - never modifies state.
    """
    timestamp_utc: float
    observation_type: ObservationType
    
    # Context
    edge_id: Optional[str] = None
    record_id: Optional[str] = None
    
    # Metrics
    duration_seconds: Optional[float] = None
    record_count: int = 0
    
    # Result
    success: bool = True
    error_message: Optional[str] = None


class RelationshipObservabilityReporter:
    """
    Passive observability reporter for relationship graph operations.
    
    Records observations without modifying the graph state.
    """

    def __init__(self, max_observations: int = 10_000):
        self.max_observations = max_observations
        self.observations: List[Observation] = []
        self._start_time_utc = time.time()
    
    def record_edge_created(
        self,
        edge_id: str,
        duration_seconds: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> Observation:
        """Record an edge creation observation."""
        obs = Observation(
            timestamp_utc=time.time(),
            observation_type=ObservationType.EDGE_CREATED,
            edge_id=edge_id,
            duration_seconds=duration_seconds,
            success=success,
            error_message=error_message
        )
        self._add_observation(obs)
        return obs
    
    def record_edge_read(
        self,
        edge_id: str,
        record_count: int = 1,
    ) -> Observation:
        """Record an edge read observation."""
        obs = Observation(
            timestamp_utc=time.time(),
            observation_type=ObservationType.EDGE_READ,
            edge_id=edge_id,
            record_count=record_count,
        )
        self._add_observation(obs)
        return obs
    
    def record_traversal_started(self, source_id: str) -> Observation:
        """Record a traversal start."""
        obs = Observation(
            timestamp_utc=time.time(),
            observation_type=ObservationType.TRAVERSAL_STARTED,
            record_id=source_id,
        )
        self._add_observation(obs)
        return obs
    
    def record_traversal_completed(
        self,
        source_id: str,
        edge_count: int,
        path_count: int,
        duration_seconds: float,
    ) -> Observation:
        """Record a traversal completion."""
        obs = Observation(
            timestamp_utc=time.time(),
            observation_type=ObservationType.TRAVERSAL_COMPLETED,
            record_id=source_id,
            record_count=edge_count,
            duration_seconds=duration_seconds,
        )
        self._add_observation(obs)
        return obs
    
    def _add_observation(self, obs: Observation) -> None:
        """Add an observation (with rotation if at capacity)."""
        if len(self.observations) >= self.max_observations:
            self.observations.pop(0)
        self.observations.append(obs)
    
    def get_observations_since(
        self,
        since_utc: float,
        observation_type: Optional[ObservationType] = None,
    ) -> List[Observation]:
        """Get observations from after a given time."""
        result = [o for o in self.observations if o.timestamp_utc >= since_utc]
        
        if observation_type:
            result = [o for o in result if o.observation_type == observation_type]
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics."""
        now = time.time()
        
        # Count by type
        type_counts: Dict[str, int] = {}
        success_count = 0
        error_count = 0
        total_duration = 0.0
        
        for obs in self.observations:
            key = obs.observation_type.value
            type_counts[key] = type_counts.get(key, 0) + 1
            
            if obs.success:
                success_count += 1
            else:
                error_count += 1
            
            if obs.duration_seconds is not None:
                total_duration += obs.duration_seconds
        
        return {
            "total_observations": len(self.observations),
            "since_start_seconds": now - self._start_time_utc,
            "by_type": type_counts,
            "success_count": success_count,
            "error_count": error_count,
            "total_duration_seconds": total_duration,
        }


# =============================================================================
# METRICS
# =============================================================================


@dataclass(frozen=True)
class RelationshipMetrics:
    """
    Aggregated metrics for relationship graph operations.
    """
    timestamp_utc: float
    
    # Counts
    edge_count: int = 0
    correlation_edge_count: int = 0
    causation_edge_count: int = 0
    episode_membership_count: int = 0
    
    # Operations
    edges_created_total: int = 0
    edges_read_total: int = 0
    traversals_started: int = 0
    traversals_completed: int = 0
    
    # Performance
    avg_edge_creation_ms: float = 0.0
    avg_traversal_duration_ms: float = 0.0
    
    # Errors
    authorization_denied_count: int = 0
    integrity_verification_failed_count: int = 0


class RelationshipMetricsCollector:
    """
    Collects and aggregates relationship metrics.
    
    Used for monitoring and alerting on graph operations.
    """

    def __init__(self):
        self.metrics_history: List[RelationshipMetrics] = []
        self._current_metrics: Optional[RelationshipMetrics] = None
        self._start_time_utc = time.time()
        self._edge_creation_times: List[float] = []
        self._traversal_durations: List[float] = []
    
    def start_edge_creation(self) -> float:
        """Start timing an edge creation."""
        return time.time()
    
    def record_edge_created(self, duration_seconds: float) -> None:
        """Record completed edge creation."""
        self._edge_creation_times.append(duration_seconds)
        if len(self._edge_creation_times) > 10_000:
            self._edge_creation_times.pop(0)
    
    def start_traversal(self) -> float:
        """Start timing a traversal."""
        return time.time()
    
    def record_traversal_completed(self, duration_seconds: float) -> None:
        """Record completed traversal."""
        self._traversal_durations.append(duration_seconds)
        if len(self._traversal_durations) > 10_000:
            self._traversal_durations.pop(0)
    
    def snapshot_metrics(self) -> RelationshipMetrics:
        """Create a metrics snapshot."""
        now = time.time()
        
        avg_edge_creation = (
            sum(self._edge_creation_times) / len(self._edge_creation_times)
            if self._edge_creation_times else 0.0
        )
        avg_traversal = (
            sum(self._traversal_durations) / len(self._traversal_durations)
            if self._traversal_durations else 0.0
        )
        
        metrics = RelationshipMetrics(
            timestamp_utc=now,
            edges_created_total=len(self._edge_creation_times),
            traversals_started=len(self._traversal_durations),
            avg_edge_creation_ms=avg_edge_creation * 1000,
            avg_traversal_duration_ms=avg_traversal * 1000,
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all collected metrics."""
        return {
            "history_length": len(self.metrics_history),
            "start_time_utc": self._start_time_utc,
            "last_snapshot": (
                self.metrics_history[-1].timestamp_utc
                if self.metrics_history else None
            ),
        }


# =============================================================================
# DIAGNOSTICS
# =============================================================================


class DiagnosticCategory(Enum):
    """Categories of diagnostic information."""
    GRAPH_INTEGRITY = "graph_integrity"
    EDGE_VALIDATION = "edge_validation"
    TRAVERSAL_PERFORMANCE = "traversal_performance"
    AUTHORIZATION = "authorization"
    MEMORY_USAGE = "memory_usage"


@dataclass(frozen=True)
class DiagnosticReport:
    """
    Diagnostic report for relationship graph.
    """
    timestamp_utc: float
    
    category: DiagnosticCategory
    severity: str  # info, warning, error
    
    title: str
    description: str
    recommendations: Tuple[str, ...] = field(default_factory=tuple)


class RelationshipDiagnostics:
    """
    Diagnostics for relationship graph operations.
    
    Provides health checks and problem identification.
    """

    def __init__(self):
        self.reports: List[DiagnosticReport] = []
        self._last_graph_integrity_check: Optional[float] = None
    
    def check_graph_integrity(self, edge_count: int) -> DiagnosticReport:
        """Check overall graph integrity."""
        self._last_graph_integrity_check = time.time()
        
        if edge_count == 0:
            return DiagnosticReport(
                timestamp_utc=self._last_graph_integrity_check,
                category=DiagnosticCategory.GRAPH_INTEGRITY,
                severity="info",
                title="Empty Graph",
                description="Relationship graph has no edges yet.",
                recommendations=("Add correlation edges between records",)
            )
        
        if edge_count > 1_000_000:
            return DiagnosticReport(
                timestamp_utc=self._last_graph_integrity_check,
                category=DiagnosticCategory.GRAPH_INTEGRITY,
                severity="warning",
                title="Large Graph",
                description=f"Graph has {edge_count} edges. Consider snapshotting.",
                recommendations=("Create graph snapshot", "Consider archival")
            )
        
        return DiagnosticReport(
            timestamp_utc=self._last_graph_integrity_check,
            category=DiagnosticCategory.GRAPH_INTEGRITY,
            severity="info",
            title="Healthy Graph",
            description=f"Graph integrity verified with {edge_count} edges.",
        )
    
    def get_all_reports(self) -> List[DiagnosticReport]:
        """Get all diagnostic reports."""
        return list(self.reports)
    
    def clear_reports(self) -> None:
        """Clear stored reports (for test purposes)."""
        self.reports.clear()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Observation types
    "ObservationType",
    "Observation",
    
    # Observability reporter
    "RelationshipObservabilityReporter",
    
    # Metrics
    "RelationshipMetrics",
    "RelationshipMetricsCollector",
    
    # Diagnostics
    "DiagnosticCategory",
    "DiagnosticReport",
    "RelationshipDiagnostics",
]