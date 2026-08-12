# Core Performance Policies
# ==========================

"""
Performance policy implementations for Gordon runtime Phase 3.7.18-I.

This module provides explicit policy types for:
    - Batching: Batch formation and triggering policies
    - Caching: Cache capacity and invalidation policies  
    - Backpressure: Backpressure signal propagation policies
    - Load Shedding: Work shedding under overload
    - Autoscaling: Scale-out/scale-in thresholds
    - Isolation: Multi-runtime performance isolation

All policy types are:
    - Immutable (frozen dataclasses)
    - Runtime-scoped
    - Bounded (explicit limits)
    - Observable (diagnostic snapshots)
    - Deterministic (stable ordering where required)

Policy owners:
    - PerformanceManager owns policy evaluation and decision production
    - Resource, scheduler, queue owners enforce policies
    - No policy can bypass canonical authorities

Usage:
    from gordon.components.core.performance import PerformanceManager
    from gordon.components.core.performance.policies import BatchingPolicy
    
    manager = PerformanceManager(runtime_id="runtime_1")
    
    # Configure batching for model inference
    batch_policy = BatchingPolicy(
        max_batch_size=32,
        max_delay_seconds=0.05,
        trigger="size_or_time"
    )
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum, auto
import uuid
import time


# =============================================================================
# BATCHING POLICIES
# =============================================================================

class BatchTrigger(Enum):
    """Triggers for batch formation."""
    SIZE = "size"           # Trigger when batch reaches size threshold
    TIME = "time"           # Trigger after max delay regardless of size
    SIZE_OR_TIME = "size_or_time"  # Either condition triggers
    EXPLICIT = "explicit"   # Manual trigger only


class BatchDeadlineBehavior(Enum):
    """How to handle deadline violations."""
    FAIL_FAST = "fail_fast"         # Fail immediately if deadline exceeded
    WAIT_FOR_COMPLETE = "wait_for_complete"  # Wait for all items
    PARTIAL_RESULTS = "partial_results"  # Return partial results
    DROP_OLD = "drop_old"           # Drop oldest pending items


@dataclass(frozen=True)
class BatchingPolicy:
    """
    Policy for batching work items.
    
    Batching improves throughput by combining multiple requests into one
    operation. However, it must not violate individual deadlines or fairness.
    
    Bounds enforced:
        - max_batch_size: hard limit on batch size
        - min_batch_size: minimum before triggering (allows wait)
        - max_delay_seconds: maximum time to wait for batch formation
        - deadline_behavior: how to handle deadline violations
    """
    
    policy_id: str
    runtime_id: str
    
    # Size constraints
    min_batch_size: int = 1           # Minimum items before considering trigger
    max_batch_size: int = 32          # Hard limit (bound!)
    
    # Time constraints
    max_delay_seconds: float = 0.1    # Maximum wait time for batch formation
    
    # Trigger mode
    trigger: BatchTrigger = BatchTrigger.SIZE_OR_TIME
    
    # Deadline handling
    deadline_behavior: BatchDeadlineBehavior = BatchDeadlineBehavior.FAIL_FAST
    
    # Priority interaction (for fairness)
    priority_boost_percent: float = 5.0  # Boost priority during batching
    
    @classmethod
    def default_for_model_inference(cls, runtime_id: str) -> "BatchingPolicy":
        """Create a reasonable policy for model inference."""
        return cls(
            policy_id=f"model_batch_{uuid.uuid4().hex[:8]}",
            runtime_id=runtime_id,
            min_batch_size=1,
            max_batch_size=64,
            max_delay_seconds=0.1,  # 100ms max delay
            trigger=BatchTrigger.TIME,
            deadline_behavior=BatchDeadlineBehavior.PARTIAL_RESULTS,
        )
    
    @classmethod
    def default_for_telemetry(cls, runtime_id: str) -> "BatchingPolicy":
        """Create a reasonable policy for telemetry batching."""
        return cls(
            policy_id=f"telemetry_batch_{uuid.uuid4().hex[:8]}",
            runtime_id=runtime_id,
            min_batch_size=10,
            max_batch_size=1000,
            max_delay_seconds=30.0,  # Up to 30 seconds for telemetry
            trigger=BatchTrigger.SIZE_OR_TIME,
            deadline_behavior=BatchDeadlineBehavior.DROP_OLD,
        )


@dataclass(frozen=True)
class BatchRequest:
    """A request to form a batch."""
    request_id: str
    runtime_id: str
    
    # Work items (typically small, homogeneous)
    item_count: int
    estimated_total_size_bytes: int = 0
    
    # Priority context
    priority_class: str = "standard"
    
    submitted_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class Batch:
    """A formed batch ready for execution."""
    batch_id: str
    runtime_id: str
    
    # Metadata
    policy_id: str
    created_at_utc: float
    triggered_at_utc: Optional[float] = None
    
    # Items in batch
    item_count: int
    items: Tuple[str, ...]  # Item IDs (references to actual work)
    
    # Timing constraints
    deadline_utc: Optional[float] = None
    max_wait_remaining_seconds: float = 0.0


@dataclass(frozen=True)
class BatchResult:
    """Result of batch execution."""
    result_id: str
    runtime_id: str
    
    batch_id: str
    items_completed: int
    items_failed: int
    items_partial: int
    
    total_duration_seconds: float
    per_item_latencies: Tuple[float, ...] = field(default_factory=tuple)
    
    success: bool  # Was the overall batch successful?
    
    # Diagnostics
    queue_wait_seconds: float = 0.0
    execution_start_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class BatchSnapshot:
    """Immutable snapshot of batching state."""
    snapshot_id: str
    runtime_id: str
    
    timestamp_utc: float
    
    # Active batches
    active_batches: int = 0
    pending_items: int = 0
    
    # Statistics (last window)
    batches_formed: int = 0
    items_batched: int = 0
    average_batch_size: float = 0.0


# =============================================================================
# CACHE POLICIES
# =============================================================================

# Re-export BackpressureLevel from main module for convenience
BackpressureLevel = None  # Will be set by import in __init__.py

class CacheReplacementPolicy(Enum):
    """Cache entry replacement policies."""
    LRU = "lru"             # Least Recently Used
    LFU = "lfu"             # Least Frequently Used
    FIFO = "fifo"           # First In, First Out
    TTL = "ttl"             # Time To Live (entries expire)
    RANDOM = "random"       # Random eviction


class CacheConsistencyModel(Enum):
    """Cache consistency guarantees."""
    STRONG = "strong"               # Always consistent
    EVENTUAL = "eventual"           # Eventually consistent
    READ_YOUR_WRITES = "read_your_writes"  # Read your own writes only


@dataclass(frozen=True)
class CachePolicy:
    """
    Policy for a specific cache instance.
    
    Every cache MUST have an explicit policy with bounded capacity.
    No unbounded caches are permitted.
    """
    
    policy_id: str
    runtime_id: str
    
    # Capacity (hard bounds!)
    max_size_bytes: int  # Total cache size limit
    max_entry_count: int = 10000  # Maximum entries (bound!)
    
    # Replacement
    replacement_policy: CacheReplacementPolicy = CacheReplacementPolicy.LRU
    
    # TTL settings
    default_ttl_seconds: float = 300.0  # 5 minutes default
    max_ttl_seconds: float = 86400.0    # 24 hours absolute max
    
    # Consistency
    consistency_model: CacheConsistencyModel = CacheConsistencyModel.EVENTUAL
    
    # Statistics collection
    collect_statistics: bool = True
    
    @property
    def is_bounded(self) -> bool:
        """Check if cache has bounded capacity."""
        return self.max_size_bytes > 0 and self.max_entry_count > 0


@dataclass(frozen=True)
class CacheSnapshot:
    """Immutable snapshot of cache state."""
    snapshot_id: str
    runtime_id: str
    
    timestamp_utc: float
    
    # Size
    current_size_bytes: int
    max_size_bytes: int
    entry_count: int
    max_entry_count: int
    
    # Statistics (if enabled)
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    ttl_expiration_count: int = 0
    
    @property
    def hit_ratio(self) -> float:
        """Calculate cache hit ratio."""
        total = self.hit_count + self.miss_count
        if total == 0:
            return 1.0  # No requests yet, assume healthy
        return self.hit_count / total


# =============================================================================
# BACKPRESSURE POLICIES
# =============================================================================

@dataclass(frozen=True)
class BackpressurePolicy:
    """
    Policy for backpressure signal propagation.
    
    Defines thresholds and actions when pressure is detected.
    
    Levels (from task 25):
        - NONE: No backpressure
        - LOW: Light throttling
        - MODERATE: Noticeable slowdown
        - HIGH: Significant throttling
        - CRITICAL: Emergency reduction
        - SATURATED: Queue overflow imminent
    """
    
    policy_id: str
    runtime_id: str
    
    # Thresholds (percent utilization triggers different levels)
    low_threshold_percent: float = 50.0
    moderate_threshold_percent: float = 70.0
    high_threshold_percent: float = 85.0
    critical_threshold_percent: float = 95.0
    saturated_threshold_percent: float = 100.0
    
    # Actions at each level
    low_actions: Tuple[str, ...] = field(default_factory=tuple)  # e.g., "reduce_batch_size"
    moderate_actions: Tuple[str, ...] = field(default_factory=lambda: ("throttle",))
    high_actions: Tuple[str, ...] = field(default_factory=lambda: ("reduce_concurrency", "reduce_batch_size"))
    critical_actions: Tuple[str, ...] = field(default_factory=lambda: ("reject_retryable",))
    
    # Propagation
    upstream_propagation: bool = True  # Propagate to upstream producers?
    
    @classmethod
    def default_policy(cls, runtime_id: str) -> "BackpressurePolicy":
        """Create a reasonable default backpressure policy."""
        return cls(
            policy_id=f"backpressure_{uuid.uuid4().hex[:8]}",
            runtime_id=runtime_id,
            low_threshold_percent=50.0,
            moderate_threshold_percent=70.0,
            high_threshold_percent=85.0,
            critical_threshold_percent=95.0,
            saturated_threshold_percent=100.0,
        )


@dataclass(frozen=True)
class BackpressureSignal:
    """Signal that backpressure should be applied."""
    signal_id: str
    runtime_id: str
    
    level: str  # NONE, LOW, MODERATE, HIGH, CRITICAL, SATURATED
    domain: str  # Which domain is under pressure
    
    reason: str  # Why backpressure was applied
    timestamp_utc: float = field(default_factory=time.time)
    
    recommended_actions: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# LOAD SHEDDING POLICIES
# =============================================================================

class LoadSheddingEligibility(Enum):
    """Which work classes are eligible for shedding."""
    NONE = "none"                   # No shedding (critical system)
    BACKGROUND_ONLY = "background_only"
    OPTIONAL = "optional"
    ALL_NON_CRITICAL = "all_non_critical"


@dataclass(frozen=True)
class LoadSheddingPolicy:
    """
    Policy for shedding work under overload.
    
    Shedding is explicit - never silent. It only sheds work that hasn't
    been accepted yet (not currently executing tasks).
    """
    
    policy_id: str
    runtime_id: str
    
    # Eligible classes
    eligible_classes: Tuple[str, ...] = field(default_factory=lambda: ("background", "optional"))
    
    # Ineligible (always protected)
    ineligible_critical: bool = True  # Never shed critical work
    
    # Selection criteria
    priority_threshold: int = 500     # Shed work with priority above this
    max_age_seconds: float = 30.0     # Shed work older than this
    
    # Response behavior
    rejection_response: str = "retry_later"
    retry_after_seconds: int = 60
    
    # Accounting (for observability)
    track_shedding_count: bool = True


@dataclass(frozen=True)
class LoadSheddingDecision:
    """Decision to shed specific work."""
    decision_id: str
    runtime_id: str
    
    work_class: str
    reason: str  # Why this was selected for shedding
    
    timestamp_utc: float = field(default_factory=time.time)
    
    should_retry: bool = True
    retry_after_seconds: int = 60


# =============================================================================
# AUTOSCALING POLICIES
# =============================================================================

@dataclass(frozen=True)
class AutoscalingPolicy:
    """
    Policy for automatic scaling of workers/resources.
    
    Must define bounds to prevent unbounded growth.
    """
    
    policy_id: str
    runtime_id: str
    
    # Bounds (hard limits!)
    min_capacity: int = 1              # Minimum workers/instances
    max_capacity: int = 64             # Maximum workers/instances (bound!)
    
    # Scaling triggers (percent thresholds)
    scale_out_threshold_percent: float = 80.0   # Scale out when > this
    scale_in_threshold_percent: float = 30.0    # Scale in when < this
    
    # Hysteresis and cooldown
    hysteresis_percent: float = 10.0  # Prevent oscillation
    scale_out_cooldown_seconds: float = 60.0   # Wait after scale out
    scale_in_cooldown_seconds: float = 300.0   # Wait after scale in (longer!)
    
    # Warmup and scale latency
    worker_warmup_seconds: float = 5.0    # Time for new worker to be ready
    scale_latency_seconds: float = 10.0   # Total time to scale
    
    @property
    def scale_out_upper_bound(self) -> float:
        """Upper bound for scale-out trigger."""
        return self.scale_out_threshold_percent + self.hysteresis_percent
    
    @property
    def scale_in_lower_bound(self) -> float:
        """Lower bound for scale-in trigger."""
        return max(0.0, self.scale_in_threshold_percent - self.hysteresis_percent)


@dataclass(frozen=True)
class ScalingDecision:
    """A scaling action decision."""
    decision_id: str
    runtime_id: str
    
    action: str  # "scale_out", "scale_in", "noop"
    
    current_capacity: int
    target_capacity: int
    
    reason: str
    timestamp_utc: float = field(default_factory=time.time)
    
    # Verification
    verified: bool = False


# =============================================================================
# ISOLATION POLICIES (multi-runtime)
# =============================================================================

@dataclass(frozen=True)
class PerformanceIsolationPolicy:
    """
    Policy for isolating performance between multiple runtimes.
    
    Ensures Runtime A cannot starve Runtime B of resources.
    """
    
    policy_id: str
    runtime_id: str
    
    # Resource quotas (per runtime)
    cpu_quota_percent: float = 100.0
    memory_quota_bytes: int = 1024 * 1024 * 1024  # 1GB default
    network_quota_bytes_per_sec: int = 100 * 1024 * 1024  # 100MB/s
    
    # Fairness
    min_share_percent: float = 50.0  # Minimum guaranteed share
    max_borrow_percent: float = 150.0  # Can borrow up to this much from others
    
    # Priority interaction
    high_priority_boost_percent: float = 20.0


# =============================================================================
# PERFORMANCE OBJECTIVE POLICIES
# =============================================================================

@dataclass(frozen=True)
class ObjectiveEvaluationPolicy:
    """
    Policy for evaluating performance objectives.
    
    Defines how measurements are aggregated and compared to targets.
    """
    
    policy_id: str
    runtime_id: str
    
    # Aggregation window
    window_seconds: float = 60.0
    
    # Percentile calculation
    min_samples_for_percentiles: int = 10
    
    # Evaluation frequency
    evaluation_interval_seconds: float = 30.0
    
    # Tolerance for status reporting
    warning_deviation_percent: float = 20.0
    critical_deviation_percent: float = 50.0


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Batching
    "BatchTrigger",
    "BatchDeadlineBehavior",
    "BatchingPolicy",
    "BatchRequest",
    "Batch",
    "BatchResult",
    "BatchSnapshot",
    
    # Caching
    "CacheReplacementPolicy",
    "CacheConsistencyModel",
    "CachePolicy",
    "CacheSnapshot",
    
    # Backpressure
    "BackpressurePolicy",
    "BackpressureSignal",
    
    # Load Shedding
    "LoadSheddingEligibility",
    "LoadSheddingPolicy",
    "LoadSheddingDecision",
    
    # Autoscaling
    "AutoscalingPolicy",
    "ScalingDecision",
    
    # Isolation
    "PerformanceIsolationPolicy",
    
    # Objectives
    "ObjectiveEvaluationPolicy",
]