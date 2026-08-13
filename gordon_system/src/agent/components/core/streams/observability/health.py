# Stream Health Layer - Phase 3.11.16
# =====================================

"""
Canonical Stream Health implementation.

Health is PASSIVE stream state reporting:
- It NEVER modifies execution flow
- It NEVER triggers recovery or remediation
- It ONLY reports current health status

Supported health states:
- Healthy: Normal operation
- Degraded: Operational under limitations
- Congested: High backpressure detected
- Recovering: Currently recovering from failure
- Replaying: Currently replaying historical records
- Idle: No activity detected
- Paused: Manually paused
- Failed: In failed state
- Unknown: State cannot be determined
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time

# =============================================================================
# STREAM HEALTH STATUS
# =============================================================================


class StreamHealthStatus(Enum):
    """
    Canonical stream health status.
    
    These are PASSIVE observations of state. They never trigger changes.
    """
    HEALTHY = "healthy"             # Normal operation
    DEGRADED = "degraded"           # Operational under limitations
    CONGESTED = "congested"         # High backpressure detected
    RECOVERING = "recovering"       # Currently recovering from failure
    REPLAYING = "replaying"         # Currently replaying historical records
    IDLE = "idle"                   # No activity detected (may be normal)
    PAUSED = "paused"               # Manually paused
    FAILED = "failed"               # In failed state
    UNKNOWN = "unknown"             # State cannot be determined


# =============================================================================
# STREAM HEALTH STATE
# =============================================================================


@dataclass(frozen=True)
class StreamHealthState:
    """
    Immutable health state for a stream.
    
    Represents the complete health picture at a point in time.
    Used for monitoring and read-only inspection.
    """
    
    # Identity
    stream_id: str                  # Which stream?
    snapshot_id: str                # Unique snapshot ID
    
    # Timestamps
    captured_at_utc: float          # When state was captured
    
    # Status
    status: StreamHealthStatus      # Current health status
    
    # Metrics for context
    backlog_size: int = 0           # Unprocessed records
    queue_depth: int = 0            # Current queue size
    cursor_lag_records: int = 0     # Position difference between cursors
    
    # Rate metrics (per second)
    publication_rate: float = 0.0
    subscription_rate: float = 0.0
    replay_rate: float = 0.0
    
    # Resource utilization (percentage 0-100)
    storage_utilization_percent: float = 0.0
    memory_utilization_percent: float = 0.0
    
    # Backpressure and failures
    backpressure_active: bool = False
    integrity_failures_total: int = 0
    
    # Lifecycle context
    lifecycle_state: str = "active"         # e.g., "active", "paused", "draining"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "stream_id": self.stream_id,
            "snapshot_id": self.snapshot_id,
            "captured_at_utc": self.captured_at_utc,
            "status": self.status.value,
            "backlog_size": self.backlog_size,
            "queue_depth": self.queue_depth,
            "cursor_lag_records": self.cursor_lag_records,
            "publication_rate": self.publication_rate,
            "subscription_rate": self.subscription_rate,
            "replay_rate": self.replay_rate,
            "storage_utilization_percent": self.storage_utilization_percent,
            "memory_utilization_percent": self.memory_utilization_percent,
            "backpressure_active": self.backpressure_active,
            "integrity_failures_total": self.integrity_failures_total,
            "lifecycle_state": self.lifecycle_state,
        }


# =============================================================================
# STREAM HEALTH REPORT
# =============================================================================


@dataclass(frozen=True)
class StreamHealthReport:
    """
    Immutable health report for a stream.
    
    Contains all health information along with diagnostic context.
    Used for reporting and read-only inspection.
    """
    
    # Identity
    report_id: str                  # Unique ID for this report
    
    # Timestamps
    created_at_utc: float           # When report was generated
    period_start_utc: Optional[float] = None  # Report period start (if applicable)
    period_end_utc: Optional[float] = None    # Report period end (if applicable)
    
    # Stream context
    stream_id: str                  # Which stream?
    
    # Health state snapshot
    state: StreamHealthState        # Current health state
    
    # Summary statistics
    total_publications: int = 0
    total_subscriptions: int = 0
    active_replays: int = 0
    active_checkpoints: int = 0
    
    # Rate metrics (per second)
    publication_rate: float = 0.0
    subscription_rate: float = 0.0
    replay_rate: float = 0.0
    
    # Level metrics
    backlog_size: int = 0
    queue_depth: int = 0
    
    # Resource utilization (percentage 0-100)
    storage_utilization_percent: float = 0.0
    memory_utilization_percent: float = 0.0
    
    # Health indicators
    backpressure_active: bool = False
    integrity_failures_total: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "report_id": self.report_id,
            "created_at_utc": self.created_at_utc,
            "period_start_utc": self.period_start_utc,
            "period_end_utc": self.period_end_utc,
            "stream_id": self.stream_id,
            "state": self.state.to_dict(),
            "total_publications": self.total_publications,
            "total_subscriptions": self.total_subscriptions,
            "active_replays": self.active_replays,
            "active_checkpoints": self.active_checkpoints,
            "publication_rate": self.publication_rate,
            "subscription_rate": self.subscription_rate,
            "replay_rate": self.replay_rate,
            "backlog_size": self.backlog_size,
            "queue_depth": self.queue_depth,
            "storage_utilization_percent": self.storage_utilization_percent,
            "memory_utilization_percent": self.memory_utilization_percent,
            "backpressure_active": self.backpressure_active,
            "integrity_failures_total": self.integrity_failures_total,
        }


# =============================================================================
# STREAM HEALTH SNAPSHOT
# =============================================================================


@dataclass(frozen=True)
class StreamHealthSnapshot:
    """
    Immutable health snapshot of multiple streams.
    
    Contains health information for a collection of streams at a point in time.
    Used for system-wide health monitoring and read-only inspection.
    """
    
    # Timestamps
    captured_at_utc: float = field(default_factory=time.time)
    
    # Health states by stream
    stream_states: Dict[str, StreamHealthState] = field(default_factory=dict)
    
    # Summary statistics
    total_streams: int = 0
    healthy_count: int = 0
    degraded_count: int = 0
    congested_count: int = 0
    
    def __post_init__(self):
        """Post-initialization to set computed fields."""
        if self.stream_states:
            object.__setattr__(self, 'total_streams', len(self.stream_states))
            
            healthy = sum(1 for s in self.stream_states.values() 
                         if s.status == StreamHealthStatus.HEALTHY)
            degraded = sum(1 for s in self.stream_states.values() 
                          if s.status == StreamHealthStatus.DEGRADED)
            congested = sum(1 for s in self.stream_states.values() 
                           if s.status == StreamHealthStatus.CONGESTED)
            
            object.__setattr__(self, 'healthy_count', healthy)
            object.__setattr__(self, 'degraded_count', degraded)
            object.__setattr__(self, 'congested_count', congested)

    def get_stream_health(self, stream_id: str) -> Optional[StreamHealthState]:
        """Get health state for a specific stream."""
        return self.stream_states.get(stream_id)

    def filter_by_status(
        self,
        status: StreamHealthStatus
    ) -> Dict[str, StreamHealthState]:
        """Filter streams by health status."""
        return {
            sid: state for sid, state in self.stream_states.items()
            if state.status == status
        }

    @classmethod
    def create_empty(cls) -> "StreamHealthSnapshot":
        """Create an empty snapshot."""
        return cls()


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_stream_health_state(
    stream_id: str,
    status: StreamHealthStatus = StreamHealthStatus.HEALTHY,
    backlog_size: int = 0,
) -> StreamHealthState:
    """
    Create a new health state for a stream.
    
    Args:
        stream_id: Which stream
        status: Health status
        backlog_size: Current backlog size
        
    Returns:
        Immutable StreamHealthState instance
    """
    return StreamHealthState(
        stream_id=stream_id,
        snapshot_id=f"health-{time.monotonic_ns()}-{hash(stream_id) % 1000:04d}",
        captured_at_utc=time.time(),
        status=status,
        backlog_size=backlog_size,
    )


def create_stream_health_report(
    stream_id: str,
    state: StreamHealthState,
) -> StreamHealthReport:
    """
    Create a health report for a stream.
    
    Args:
        stream_id: Which stream
        state: Current health state
        
    Returns:
        Immutable StreamHealthReport instance
    """
    return StreamHealthReport(
        report_id=f"report-{time.monotonic_ns()}-{hash(stream_id) % 1000:04d}",
        created_at_utc=time.time(),
        stream_id=stream_id,
        state=state,
    )


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Simple dataclass replace implementation for frozen dataclasses."""
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) 
                      for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Status and state
    "StreamHealthStatus",
    "StreamHealthState",
    
    # Reports
    "StreamHealthReport",
    
    # Snapshots
    "StreamHealthSnapshot",
    
    # Factory functions
    "create_stream_health_state",
    "create_stream_health_report",
    "dataclass_replace",
]