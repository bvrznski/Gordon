# Core Performance Architecture
# =============================
"""
Phase 3.7.18-I - Performance, Throughput, Latency, Scalability & Efficiency.

This module provides the canonical performance architecture for Gordon:

CANONICAL AUTHORITIES:
    - PerformanceManager: Runtime-wide performance authority
    - PerformanceMeasurementCoordinator: Measurement coordination
    - PerformancePolicyEngine: Policy evaluation
    - CapacityPlanner: Capacity forecasting and planning
    - BottleneckAnalyzer: Bottleneck detection and analysis
    - BenchmarkCoordinator: Benchmark execution coordination

KEY PRINCIPLES:
    - Exactly one canonical authority per responsibility
    - No hidden worker pools or unbounded queues
    - Performance decisions never override correctness, safety, or integrity
    - All bounds are explicit and enforceable
    - Latency uses monotonic time, not wall-clock
    - Throughput counts completed work only
    - Tail latency must be observable (not averaged)

ARCHITECTURAL DISTINCTIONS:
    latency:        elapsed time for one operation or stage
    throughput:     completed work per unit of time
    capacity:       maximum supported concurrent or aggregate load
    utilization:    proportion of available capacity currently used
    efficiency:     useful work relative to consumed resources
    scalability:    ability to increase capacity through additional resources

USAGE:
    from gordon.components.core.performance import PerformanceManager
    
    manager = PerformanceManager(runtime_id="runtime_1")
    
    # Register a performance domain
    domain = manager.register_domain(
        domain_id="task_execution",
        owner_id="scheduler",
        objectives=[...]
    )
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum, auto
import time
import uuid

# Import new authorities from separate modules (Phase 3.7.18-I additions)
from .engine import (
    PerformancePolicyEngine,
    OverloadDecision,
    BackpressureDecision as EngineBackpressureDecision,
    LoadSheddingDecision as EngineLoadSheddingDecision,
    ScalingDecision as EngineScalingDecision,
)

from .capacity_planner import (
    CapacityPlanner,
    CapacityForecast as PlannerCapacityForecast,
    CapacityHeadroom as PlannerCapacityHeadroom,
    CapacityReserve,
    CapacityRecommendation,
    CapacityGap,
    CapacityProjection,
    CapacityRequirement,
    CapacityPlannerSnapshot,
)

from .bottlenecks import (
    BottleneckAnalyzer,
    BottleneckType,
    BottleneckSeverity,
    BottleneckEvidence,
    BottleneckFinding,
    OptimizationProposal,
    BottleneckAnalysisResult,
    ContentionAnalysisResult as BottleneckContentionAnalysisResult,
    BottleneckAnalyzerSnapshot,
)

from .benchmarks import (
    BenchmarkCoordinator,
    BenchmarkType,
    BenchmarkEnvironment,
    BenchmarkDefinition,
    MicroBenchmarkDefinition,
    LoadProfile,
    BenchmarkResult,
    BaselineReference,
    PerformanceComparison,
    PerformanceRegression,
    BenchmarkCoordinatorSnapshot,
)

# Import policies module
from .policies import (
    BatchTrigger,
    BatchDeadlineBehavior,
    BatchingPolicy,
    BatchRequest,
    Batch,
    BatchResult,
    BatchSnapshot,
    
    CacheReplacementPolicy,
    CacheConsistencyModel,
    CachePolicy,
    CacheSnapshot,
    
    BackpressureLevel,  # Also in policies
    BackpressureSignal,  # Also in policies  
    BackpressurePolicy,  # Also in policies
    
    LoadSheddingEligibility,
    LoadSheddingDecision as PolicyLoadSheddingDecision,
    AutoscalingPolicy,
    ScalingDecision as PolicyScalingDecision,
    PerformanceIsolationPolicy,
    
    ObjectiveEvaluationPolicy,
)

# NOTE: We don't re-export existing capacity types to avoid circular dependencies.
# Instead we define our own compatible snapshot types that can be extended later.
# The actual capacity tracking is owned by ResourceManager.

# Re-export core artifacts for convenience (deferred imports)
# Note: We define our own snapshot types inline to avoid circular dependencies.
# The actual capacity tracking is owned by ResourceManager.

# =============================================================================
# PERFORMANCE DOMAINS
# =============================================================================

class PerformanceDomain(Enum):
    """
    Canonical performance domains in the runtime.
    
    Each domain tracks its own metrics, objectives, and capacity:
        - RUNTIME: Overall runtime overhead and coordination
        - SCHEDULER: Task scheduling decisions and latency
        - EXECUTOR: Task execution time and throughput
        - WORKER: Worker pool utilization and task handling
        - QUEUE: Queue residence time and backpressure
        - TASK_LIFECYCLE: Task state transitions
        - CPU: CPU utilization and context switching
        - MEMORY: Memory usage, allocation rate, GC pauses
        - GPU: GPU utilization and VRAM
        - STORAGE: Filesystem I/O latency and throughput
        - NETWORK: Network round-trip and bandwidth
        - IPC: Inter-process communication latency
        - SERIALIZATION: Serialization/deserialization time
        - PERSISTENCE: Checkpoint and journal operations
        - EVENT_BUS: Event dispatch latency
        - TELEMETRY: Telemetry overhead and sampling
        - MODEL_INFERENCE: Model first-token and inter-token latency
        - TOOL_INVOCATION: Tool call latency
        - PLUGIN_INVOCATION: Plugin call latency
    """
    
    RUNTIME = "runtime"
    SCHEDULER = "scheduler"
    EXECUTOR = "executor"
    WORKER = "worker"
    QUEUE = "queue"
    TASK_LIFECYCLE = "task_lifecycle"
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"
    IPC = "ipc"
    SERIALIZATION = "serialization"
    PERSISTENCE = "persistence"
    EVENT_BUS = "event_bus"
    TELEMETRY = "telemetry"
    MODEL_INFERENCE = "model_inference"
    TOOL_INVOCATION = "tool_invocation"
    PLUGIN_INVOCATION = "plugin_invocation"


# =============================================================================
# PERFORMANCE OBJECTIVES
# =============================================================================

class ObjectiveStatus(Enum):
    """Status of a performance objective."""
    ACTIVE = "active"
    MET = "met"
    BREACHED = "breached"
    DEGRADED = "degraded"
    OBSOLETE = "obsolete"


@dataclass(frozen=True)
class PerformanceObjectiveId:
    """Unique identifier for a performance objective."""
    value: str
    
    @classmethod
    def generate(cls) -> "PerformanceObjectiveId":
        return cls(value=f"obj_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PerformanceTarget:
    """
    A performance target value with tolerance.
    
    Example: latency_p99 < 50ms ± 5ms
    """
    target_value: float
    tolerance_positive: float = 0.0
    tolerance_negative: float = 0.0
    
    @property
    def min_acceptable(self) -> float:
        return self.target_value - self.tolerance_negative
    
    @property
    def max_acceptable(self) -> float:
        return self.target_value + self.tolerance_positive


@dataclass(frozen=True)
class PerformanceConstraint:
    """
    A hard constraint on performance.
    
    Unlike targets, constraints are hard limits that must never be exceeded.
    """
    limit_value: float
    direction: str  # "<", "<=", ">", ">="
    
    def is_satisfied(self, measured: float) -> bool:
        """Check if measured value satisfies the constraint."""
        if self.direction in ("<", "<="):
            return measured <= self.limit_value
        elif self.direction in (">", ">="):
            return measured >= self.limit_value
        return True


@dataclass(frozen=True)
class PerformanceObjective:
    """
    A measurable performance objective.
    
    Every objective defines:
        - Scope: What it measures (domain, stage, etc.)
        - Workload: Under what conditions
        - Measurement window: How long to aggregate
        - Target: The desired value with tolerance
        - Authority: Who owns enforcement
        - Evaluation method: How to compute from measurements
    
    Example:
        Objective(
            objective_id=PerformanceObjectiveId.generate(),
            domain=PerformanceDomain.SCHEDULER,
            metric_name="latency_p95",
            target=PerformanceTarget(target_value=0.1, tolerance_positive=0.02),
            window_seconds=60.0,
            owner_id="scheduler",
            severity="warning"
        )
    """
    
    objective_id: PerformanceObjectiveId
    domain: PerformanceDomain
    
    # Metric specification
    metric_name: str  # e.g., "latency_p99", "throughput_tasks_per_sec"
    
    # Target definition
    target: PerformanceTarget
    constraint: Optional[PerformanceConstraint] = None
    
    # Context
    window_seconds: float = 60.0
    owner_id: str = ""  # Who is responsible for meeting this objective
    
    # Evaluation
    severity: str = "warning"  # "info", "warning", "critical"
    
    @property
    def status(self, measured_value: Optional[float] = None) -> ObjectiveStatus:
        """
        Determine objective status based on measured value.
        
        Args:
            measured_value: Current measurement (if not provided, returns ACTIVE)
            
        Returns:
            Status indicating if met, breached, degraded, etc.
        """
        if measured_value is None:
            return ObjectiveStatus.ACTIVE
        
        target = self.target
        constraint = self.constraint
        
        # Check hard constraint first
        if constraint and not constraint.is_satisfied(measured_value):
            return ObjectiveStatus.BREACHED
        
        # Check tolerance-based status
        min_acceptable = target.min_acceptable
        max_acceptable = target.max_acceptable
        
        if min_acceptable <= measured_value <= max_acceptable:
            return ObjectiveStatus.MET
        
        if measured_value > max_acceptable:
            return ObjectiveStatus.DEGRADED
        
        return ObjectiveStatus.BREACHED


@dataclass(frozen=True)
class PerformanceObjectiveReport:
    """
    Report on performance objective status.
    
    Generated when objectives are evaluated against measurements.
    """
    
    report_id: str
    objective_id: PerformanceObjectiveId
    domain: PerformanceDomain
    metric_name: str
    
    # Evaluation results
    measured_value: float
    target_value: float
    deviation_percent: float
    
    status: ObjectiveStatus
    evaluation_timestamp_utc: float = field(default_factory=time.time)
    
    # Context
    window_start_utc: Optional[float] = None
    window_end_utc: Optional[float] = None
    sample_count: int = 0
    
    # Recommendations
    recommended_actions: List[str] = field(default_factory=list)


# =============================================================================
# PERFORMANCE BUDGETS
# =============================================================================

class BudgetKind(Enum):
    """Types of budgets that can be tracked."""
    LATENCY = "latency"
    CPU = "cpu"
    GPU = "gpu"
    MEMORY = "memory"
    VRAM = "vram"
    STORAGE = "storage"
    NETWORK = "network"
    SERIALIZATION = "serialization"
    TELEMETRY = "telemetry"
    RETRY = "retry"
    QUEUE_WAITING = "queue_waiting"
    CONTEXT_SWITCH = "context_switch"


class BudgetScope(Enum):
    """Scope at which a budget is enforced."""
    RUNTIME = "runtime"       # Per runtime instance
    TASK_TYPE = "task_type"   # Per task type/class
    OWNER = "owner"           # Per owner/tenant
    QUEUE = "queue"           # Per queue


@dataclass(frozen=True)
class BudgetConsumption:
    """Current consumption state of a budget."""
    consumed: float
    limit: float
    remaining: float
    
    @property
    def utilization_percent(self) -> float:
        if self.limit <= 0:
            return 0.0
        return (self.consumed / self.limit) * 100


class BudgetStatus(Enum):
    """Status of a budget."""
    WITHIN_LIMIT = "within_limit"
    WARNING_THRESHOLD = "warning_threshold"      # > 80%
    CRITICAL_THRESHOLD = "critical_threshold"   # > 95%
    EXCEEDED = "exceeded"


@dataclass(frozen=True)
class PerformanceBudget:
    """
    A bounded performance budget.
    
    Budgets are enforced or reported at runtime scope. They are NOT
    automatic capacity limiters - they're measurement and tracking first.
    
    Example: A latency budget of 100ms per task for the next hour.
    """
    
    budget_id: str
    kind: BudgetKind
    
    # Scope
    scope: BudgetScope
    scope_id: str  # e.g., "runtime_1", "task_type_inference"
    
    # Limits
    limit_value: float
    window_seconds: float = 3600.0  # Default 1 hour
    
    # Warning thresholds (percentages of limit)
    warning_threshold_percent: float = 80.0
    critical_threshold_percent: float = 95.0
    
    # Tracking
    current_consumption: float = 0.0
    created_at_utc: float = field(default_factory=time.time)
    
    def consume(self, amount: float) -> "PerformanceBudget":
        """Return a new budget with increased consumption."""
        return PerformanceBudget(
            budget_id=self.budget_id,
            kind=self.kind,
            scope=self.scope,
            scope_id=self.scope_id,
            limit_value=self.limit_value,
            window_seconds=self.window_seconds,
            warning_threshold_percent=self.warning_threshold_percent,
            critical_threshold_percent=self.critical_threshold_percent,
            current_consumption=min(self.current_consumption + amount, self.limit_value),
            created_at_utc=self.created_at_utc,
        )
    
    def get_status(self) -> BudgetStatus:
        """Get current budget status."""
        utilization = (self.current_consumption / max(self.limit_value, 1)) * 100
        
        if utilization >= self.critical_threshold_percent:
            return BudgetStatus.CRITICAL_THRESHOLD
        elif utilization >= self.warning_threshold_percent:
            return BudgetStatus.WARNING_THRESHOLD
        elif utilization > 100:
            return BudgetStatus.EXCEEDED
        else:
            return BudgetStatus.WITHIN_LIMIT
    
    def get_consumption(self) -> BudgetConsumption:
        """Get detailed consumption info."""
        remaining = max(0.0, self.limit_value - self.current_consumption)
        return BudgetConsumption(
            consumed=self.current_consumption,
            limit=self.limit_value,
            remaining=remaining,
        )


@dataclass(frozen=True)
class BudgetViolation:
    """
    Record of a budget being exceeded.
    
    Used for auditing and analysis, not automatic enforcement.
    """
    
    violation_id: str
    budget_id: str
    kind: BudgetKind
    scope: str
    excess_amount: float
    timestamp_utc: float = field(default_factory=time.time)
    window_start_utc: Optional[float] = None
    window_end_utc: Optional[float] = None


@dataclass(frozen=True)
class BudgetSnapshot:
    """
    Snapshot of budget states at a point in time.
    
    Used for diagnostics and historical analysis.
    """
    
    snapshot_id: str
    runtime_id: str
    timestamp_utc: float
    
    budgets: Dict[str, PerformanceBudget] = field(default_factory=dict)


# =============================================================================
# LATENCY MODEL
# =============================================================================

@dataclass(frozen=True)
class LatencyMeasurement:
    """
    Single latency measurement with full context.
    
    Usage:
        # Record a latency at each stage
        start = time.monotonic()
        
        # ... operation ...
        
        latency = time.monotonic() - start
        
        measurement = LatencyMeasurement(
            duration_seconds=latency,
            stage="dispatch",
            task_id=task_id,
            runtime_id=runtime_id,
            monotonic_start=start
        )
    """
    
    duration_seconds: float  # Elapsed time (always positive)
    
    # Context
    stage: str  # e.g., "admission", "queue", "dispatch", "execution"
    domain: PerformanceDomain
    
    # Task identity
    task_id: Optional[str] = None
    runtime_id: str = ""
    correlation_id: Optional[str] = None  # For tracing
    
    # Timing (monotonic)
    monotonic_start: float = field(default_factory=time.monotonic)
    monotonic_end: float = field(default_factory=time.monotonic)
    
    @property
    def is_valid(self) -> bool:
        """Check if measurement is valid."""
        return self.duration_seconds >= 0 and self.stage != ""


@dataclass(frozen=True)
class LatencyPercentile:
    """
    A latency percentile value.
    
    Example: p99 latency = 50ms
    """
    
    percentile: float  # e.g., 99.0 for p99
    latency_seconds: float
    
    @classmethod
    def from_milliseconds(cls, percentile: float, ms: float) -> "LatencyPercentile":
        """Create a percentile with milliseconds input."""
        return cls(percentile=percentile, latency_seconds=ms / 1000.0)


@dataclass(frozen=True)
class LatencyDistribution:
    """
    Summary of latency distribution.
    
    Computes percentiles from measurements using bounded storage.
    """
    
    sample_count: int
    min_latency_seconds: float
    max_latency_seconds: float
    
    # Percentiles
    p50_latency: Optional[LatencyPercentile] = None
    p90_latency: Optional[LatencyPercentile] = None
    p95_latency: Optional[LatencyPercentile] = None
    p99_latency: Optional[LatencyPercentile] = None
    
    # Mean (for reference, but not primary metric)
    mean_latency_seconds: float = 0.0


@dataclass(frozen=True)
class LatencyBudget:
    """
    Budget for latency measurements.
    
    Defines acceptable latency ranges for different stages.
    """
    
    budget_id: str
    domain: PerformanceDomain
    
    # Per-stage limits
    admission_limit_ms: Optional[float] = None  # Total time to first task execution
    queue_limit_ms: Optional[float] = None      # Time spent in queue
    dispatch_limit_ms: Optional[float] = None   # Dispatch latency
    execution_limit_ms: Optional[float] = None  # Task execution time
    
    @property
    def most_constrained_stage(self) -> Optional[str]:
        """Get the stage with tightest constraint."""
        stages = [
            ("admission", self.admission_limit_ms),
            ("queue", self.queue_limit_ms),
            ("dispatch", self.dispatch_limit_ms),
            ("execution", self.execution_limit_ms),
        ]
        # Return first constrained stage
        for name, limit in stages:
            if limit is not None and limit < 100:  # Less than 100ms
                return name
        return None


@dataclass(frozen=True)
class LatencySnapshot:
    """
    Immutable snapshot of latency measurements.
    
    Used for reporting and analysis. Never mutated after creation.
    """
    
    snapshot_id: str
    runtime_id: str
    
    timestamp_utc: float
    window_start_utc: Optional[float] = None
    window_end_utc: Optional[float] = None
    
    # Per-stage latencies
    stage_latencies: Dict[str, LatencyDistribution] = field(default_factory=dict)
    
    # Summary
    total_sample_count: int = 0


# =============================================================================
# THROUGHPUT MODEL
# =============================================================================

@dataclass(frozen=True)
class ThroughputMeasurement:
    """
    Throughput measurement over a time window.
    
    Counts completed work per unit time. Does NOT count queued,
    failed, or partial work.
    """
    
    # Unit counts
    completed_count: int
    failed_count: int = 0  # Explicitly track failures
    partial_count: int = 0  # Partial results (e.g., partial responses)
    
    # Time window
    window_start_utc: float
    window_end_utc: float
    
    @property
    def duration_seconds(self) -> float:
        """Get window duration."""
        return self.window_end_utc - self.window_start_utc
    
    @property
    def throughput_per_second(self) -> float:
        """Calculate throughput (completed work per second)."""
        if self.duration_seconds <= 0:
            return 0.0
        return self.completed_count / self.duration_seconds


@dataclass(frozen=True)
class ThroughputRate:
    """
    A rate of throughput with units.
    
    Example: 100 tasks/second, 50 tokens/second
    """
    
    value_per_second: float
    unit_name: str  # e.g., "tasks", "tokens", "events"
    window_seconds: float


@dataclass(frozen=True)
class ThroughputWindow:
    """
    A rolling window for throughput measurement.
    
    Tracks throughput over sliding time windows with bounded storage.
    """
    
    window_id: str
    duration_seconds: float = 60.0
    
    # Rolling measurements (bounded to last N windows)
    _measurements: List[ThroughputMeasurement] = field(default_factory=list, repr=False)


@dataclass(frozen=True)
class ThroughputTarget:
    """
    Target throughput that must be met.
    
    Example: System must process at least 100 tasks/second
    """
    
    target_per_second: float
    tolerance_negative: float = 0.0  # Can dip below by this much
    window_seconds: float = 60.0
    
    @property
    def min_acceptable_per_second(self) -> float:
        return self.target_per_second - self.tolerance_negative


@dataclass(frozen=True)
class ThroughputSnapshot:
    """
    Snapshot of throughput measurements.
    
    Used for performance analysis and capacity planning.
    """
    
    snapshot_id: str
    runtime_id: str
    
    timestamp_utc: float
    
    # Current rates
    current_rate_per_second: float = 0.0
    average_rate_per_second: float = 0.0
    min_rate_per_second: float = 0.0
    max_rate_per_second: float = 0.0
    
    # Unit type (for context)
    unit_name: str = "tasks"
    
    # Target comparison
    target_per_second: Optional[float] = None
    target_met: bool = False


# =============================================================================
# CAPACITY MODEL (extensions to existing capacity.py)
# =============================================================================

@dataclass(frozen=True)
class CapacityObservation:
    """
    Observation of current capacity state.
    
    More detailed than CapacitySnapshot, includes timing and context.
    """
    
    snapshot_id: str
    runtime_id: str
    
    timestamp_utc: float
    
    # Domain observations
    domain_observations: Dict[str, "DomainCapacitySnapshot"] = field(default_factory=dict)
    
    # Derived metrics
    overall_utilization: float = 0.0
    most_saturated_domain: Optional[str] = None


@dataclass(frozen=True)
class CapacityBreakpoint:
    """
    Point at which capacity constraints are triggered.
    
    Example: Queue occupancy reaches 95% and backpressure activates.
    """
    
    breakpoint_id: str
    domain: str
    threshold_percent: float
    
    # What happens at this breakpoint
    action: str  # e.g., "activate_backpressure", "reject_new"
    
    created_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class CapacityHeadroom:
    """
    Available headroom before saturation.
    
    Headroom = free capacity / total capacity
    """
    
    domain: str
    total_capacity: float
    used_capacity: float
    
    @property
    def free_capacity(self) -> float:
        return self.total_capacity - self.used_capacity
    
    @property
    def headroom_percent(self) -> float:
        if self.total_capacity <= 0:
            return 100.0
        return (self.free_capacity / self.total_capacity) * 100
    
    @property
    def utilization_percent(self) -> float:
        if self.total_capacity <= 0:
            return 0.0
        return (self.used_capacity / self.total_capacity) * 100


@dataclass(frozen=True)
class CapacityForecast:
    """
    Forecast of future capacity needs.
    
    Based on historical trends and projected workload.
    """
    
    forecast_id: str
    runtime_id: str
    
    # Time horizon
    window_start_utc: float
    window_end_utc: float
    
    # Forecasts per domain
    forecasts: Dict[str, "CapacityProjection"] = field(default_factory=dict)


@dataclass(frozen=True)
class CapacityProjection:
    """
    Projected capacity usage over time.
    
    For a single resource domain.
    """
    
    domain: str
    
    # Timeline of projections
    timestamps_utc: List[float] = field(default_factory=list)
    projected_usage: List[float] = field(default_factory=list)


@dataclass(frozen=True)
class CapacitySnapshot:
    """
    Canonical capacity snapshot (extends resources.capacity.CapacitySnapshot).
    
    Includes runtime-specific context.
    """
    
    # Base fields from resources.capacity
    runtime_id: str
    version: int
    timestamp_utc: float
    domain_snapshots: Dict[str, "DomainCapacitySnapshot"]
    
    # Additional performance context
    saturation_percentile: float = 0.0  # P95/P99 of utilization across domains


# =============================================================================
# UTILIZATION MODEL
# =============================================================================

@dataclass(frozen=True)
class UtilizationMeasurement:
    """
    Measurement of resource utilization.
    
    Usage: 0.0 (idle) to 1.0 (fully saturated)
    """
    
    domain: str
    utilization_percent: float
    
    # Timestamps
    measurement_time_utc: float = field(default_factory=time.time)
    
    # Sample context
    sample_count: int = 1


@dataclass(frozen=True)
class UtilizationSnapshot:
    """
    Snapshot of utilization across all tracked domains.
    
    Used for performance analysis and overload detection.
    """
    
    snapshot_id: str
    runtime_id: str
    
    timestamp_utc: float
    
    # Per-domain utilization
    domain_utilization: Dict[str, float] = field(default_factory=dict)
    
    # Summary statistics
    average_utilization: float = 0.0
    max_utilization: float = 0.0
    most_saturated_domain: Optional[str] = None


# =============================================================================
# EFFICIENCY MODEL
# =============================================================================

@dataclass(frozen=True)
class EfficiencyReport:
    """
    Report on resource efficiency.
    
    Compares useful work to consumed resources.
    """
    
    report_id: str
    runtime_id: str
    
    timestamp_utc: float
    
    # Metrics
    tasks_completed: int = 0
    total_resource_seconds: float = 0.0
    
    # Derived metrics
    @property
    def efficiency_score(self) -> float:
        """Calculate efficiency (tasks per resource-second)."""
        if self.total_resource_seconds <= 0:
            return 0.0
        return self.tasks_completed / self.total_resource_seconds


# =============================================================================
# CONTENTION MODEL
# =============================================================================

@dataclass(frozen=True)
class ContentionObservation:
    """
    Observation of resource contention.
    
    Tracks wait times and blocking behavior.
    """
    
    observation_id: str
    domain: str
    
    # Measurements
    total_wait_seconds: float = 0.0
    contention_count: int = 0
    sample_count: int = 1
    
    # Timestamps
    window_start_utc: float = field(default_factory=time.time)
    window_end_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ContentionAnalysis:
    """
    Analysis of contention patterns.
    
    Identifies bottlenecks and blocking points.
    """
    
    analysis_id: str
    runtime_id: str
    
    timestamp_utc: float
    
    # Findings
    most_contentious_domain: Optional[str] = None
    average_wait_seconds: float = 0.0
    
    recommendations: List[str] = field(default_factory=list)


# =============================================================================
# OVERLOAD STATE MACHINE
# =============================================================================

class OverloadState(Enum):
    """
    Runtime overload states.
    
    Transition flow:
        NORMAL → BUSY → SATURATED → OVERLOADED → CRITICAL → COLLAPSING
        
    Backpressure and load shedding activate at different thresholds.
    """
    
    NORMAL = "normal"           # No pressure
    BUSY = "busy"               # Elevated load, but within bounds
    SATURATED = "saturated"     # Near capacity, backpressure active
    OVERLOADED = "overloaded"   # Exceeding safe limits
    CRITICAL = "critical"       # Critical failure risk
    COLLAPSING = "collapsing"   # Imminent collapse - emergency only


# =============================================================================
# DEGRADATION MODES
# =============================================================================

class DegradationMode(Enum):
    """
    Explicit degradation modes under overload.
    
    Each mode defines reduced functionality while maintaining core guarantees.
    """
    
    NONE = "none"                      # Full capability
    REDUCED_CONCURRENCY = "reduced_concurrency"  # Fewer parallel operations
    BACKGROUND_PAUSED = "background_paused"      # Only critical work
    OPTIONAL_TELEMETRY_REDUCED = "optional_telemetry_reduced"   # Minimal telemetry
    LOCAL_ONLY = "local_only"          # No remote calls
    CONTROL_PLANE_ONLY = "control_plane_only"   # System management only
    HIGH_PRIORITY_ONLY = "high_priority_only"   # Critical priority only


@dataclass(frozen=True)
class DegradationRecord:
    """
    Record of entering a degradation mode.
    
    Includes when and why degradation was triggered.
    """
    
    record_id: str
    runtime_id: str
    
    from_mode: DegradationMode
    to_mode: DegradationMode
    
    trigger: str  # e.g., "queue_occupancy > 95%"
    
    timestamp_utc: float = field(default_factory=time.time)
    
    recovery_plan: Optional[str] = None  # How to recover


# =============================================================================
# BACKPRESSURE SIGNALS
# =============================================================================

class BackpressureLevel(Enum):
    """
    Levels of backpressure that can be applied.
    
    From NONE (no pressure) to SATURATED (queue overflow imminent).
    """
    
    NONE = "none"              # No backpressure
    LOW = "low"                # Light throttling
    MODERATE = "moderate"      # Noticeable slowdown
    HIGH = "high"              # Significant throttling
    CRITICAL = "critical"      # Emergency reduction
    SATURATED = "saturated"    # Queue will overflow


@dataclass(frozen=True)
class BackpressureSignal:
    """
    Signal that backpressure should be applied.
    
    Sent from queues/schedulers to upstream components.
    """
    
    signal_id: str
    runtime_id: str
    
    level: BackpressureLevel
    domain: PerformanceDomain
    
    reason: str  # Why backpressure was applied
    
    timestamp_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class BackpressurePolicy:
    """
    Policy for applying backpressure.
    
    Defines how and when to reduce load under pressure.
    """
    
    policy_id: str
    runtime_id: str
    
    # Triggers (percent utilization triggers different levels)
    moderate_threshold_percent: float = 70.0
    high_threshold_percent: float = 85.0
    critical_threshold_percent: float = 95.0
    
    # Actions at each level
    moderate_actions: List[str] = field(default_factory=list)  # e.g., ["reduce_batch_size"]
    high_actions: List[str] = field(default_factory=list)
    critical_actions: List[str] = field(default_factory=list)


# =============================================================================
# LOAD SHEDDING DECISIONS
# =============================================================================

@dataclass(frozen=True)
class LoadSheddingPolicy:
    """
    Policy for shedding work under overload.
    
    Defines which work can be safely dropped and when.
    """
    
    policy_id: str
    runtime_id: str
    
    # Eligible work classes for shedding
    eligible_work_classes: List[str] = field(default_factory=list)  # e.g., ["background", "optional"]
    ineligible_critical: bool = True  # Never shed critical work
    
    # Selection criteria
    priority_threshold: int = 500  # Lower = higher priority, shed above this
    deadline_threshold_seconds: float = 30.0  # Shed work with long deadlines
    
    # Response behavior
    rejection_response: str = "retry_later"  # What to tell caller
    retry_after_seconds: int = 60


@dataclass(frozen=True)
class LoadSheddingDecision:
    """
    Decision to shed specific work.
    
    Always explicit - never silent.
    """
    
    decision_id: str
    runtime_id: str
    
    task_id: str
    work_class: str  # e.g., "background", "optional"
    
    reason: str  # Why shedding was chosen
    
    timestamp_utc: float = field(default_factory=time.time)
    
    # Response to caller
    should_retry: bool = True
    retry_after_seconds: int = 60


# =============================================================================
# PERFORMANCE MANAGER (CANONICAL AUTHORITY)
# =============================================================================

class PerformanceManager:
    """
    Canonical runtime-wide performance authority.
    
    This is THE ONE source of truth for all performance-related state within
    a runtime. All performance measurements, objectives, and policies are
    coordinated through this manager.
    
    PerformanceManager does NOT:
        - Schedule tasks or allocate resources directly
        - Create worker pools or queues
        - Make admission decisions
        - Mutate arbitrary component state
        
    PerformanceManager DOES own:
        - Performance domain registration
        - Performance objectives (tracking, evaluation)
        - Performance budgets (tracking consumption)
        - Performance snapshots and history
        - Bottleneck findings
        - Regression findings
        - Capacity reports
        - Runtime-scoped performance state
    
    Usage:
        manager = PerformanceManager(runtime_id="runtime_1")
        
        # Register a domain
        domain = manager.register_domain(
            domain_id="task_execution",
            owner_id="scheduler"
        )
        
        # Record measurements
        measurement = LatencyMeasurement(duration_seconds=0.05, ...)
        manager.record_latency(measurement)
        
        # Get snapshot for diagnostics
        snapshot = manager.get_performance_snapshot()
    """
    
    def __init__(self, runtime_id: str):
        """
        Initialize the PerformanceManager.
        
        Args:
            runtime_id: Unique identifier for this runtime instance
        """
        self._runtime_id = runtime_id
        
        # Lock for thread safety (synchronous implementation)
        self._lock = __import__("threading").RLock()
        
        # State
        self._domains: Dict[str, "PerformanceDomainInfo"] = {}
        self._objectives: Dict[PerformanceObjectiveId, PerformanceObjective] = {}
        self._budgets: Dict[str, PerformanceBudget] = {}
        
        # Measurements (bounded histories)
        self._latency_measurements: List[LatencyMeasurement] = []
        self._throughput_measurements: List[ThroughputMeasurement] = []
        self._capacity_snapshots: List[CapacitySnapshot] = []
        
        # Overload state
        self._overload_state = OverloadState.NORMAL
        
        # History (bounded)
        self._history_entries: List[Dict[str, Any]] = []
        self._max_history = 1000
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this manager serves."""
        return self._runtime_id
    
    def register_domain(
        self,
        domain_id: str,
        owner_id: str,
        objectives: Optional[List[PerformanceObjective]] = None,
    ) -> "PerformanceDomainInfo":
        """
        Register a new performance domain.
        
        Args:
            domain_id: Unique identifier for the domain
            owner_id: Who owns this domain (for ownership tracking)
            objectives: Initial objectives for this domain
            
        Returns:
            The registered domain info
        """
        with self._lock:
            if domain_id in self._domains:
                raise ValueError(f"Domain {domain_id} already registered")
            
            domain_info = PerformanceDomainInfo(
                domain_id=domain_id,
                owner_id=owner_id,
                objectives={o.objective_id: o for o in (objectives or [])},
            )
            
            self._domains[domain_id] = domain_info
            
            # Record event
            self._record_event("domain_registered", {
                "domain_id": domain_id,
                "owner_id": owner_id,
                "objective_count": len(objectives or []),
            })
            
            return domain_info
    
    def register_objective(self, objective: PerformanceObjective) -> None:
        """Register a performance objective."""
        with self._lock:
            self._objectives[objective.objective_id] = objective
            self._record_event("objective_registered", {
                "objective_id": str(objective.objective_id),
                "domain": objective.domain.value,
                "metric_name": objective.metric_name,
            })
    
    def update_budget_consumption(
        self,
        budget_id: str,
        amount: float,
        timestamp_utc: Optional[float] = None,
    ) -> PerformanceBudget:
        """
        Update a budget's consumption.
        
        Args:
            budget_id: The budget to update
            amount: Amount consumed (positive)
            timestamp_utc: When consumption occurred
            
        Returns:
            Updated budget state
        """
        with self._lock:
            if budget_id not in self._budgets:
                # Create new budget if not exists (for convenience)
                self._budgets[budget_id] = PerformanceBudget(
                    budget_id=budget_id,
                    kind=BudgetKind.LATENCY,
                    scope=BudgetScope.RUNTIME,
                    scope_id=self._runtime_id,
                    limit_value=1000.0,  # Default
                )
            
            budget = self._budgets[budget_id]
            updated_budget = budget.consume(amount)
            self._budgets[budget_id] = updated_budget
            
            return updated_budget
    
    def record_latency(self, measurement: LatencyMeasurement) -> None:
        """
        Record a latency measurement.
        
        Args:
            measurement: The latency measurement to record
        """
        with self._lock:
            # Enforce bounded history
            if len(self._latency_measurements) >= 10000:
                # Keep recent, discard oldest
                self._latency_measurements = self._latency_measurements[-5000:]
            
            self._latency_measurements.append(measurement)
            
            self._record_event("latency_recorded", {
                "stage": measurement.stage,
                "domain": measurement.domain.value,
                "duration_seconds": measurement.duration_seconds,
            })
    
    def record_throughput(self, measurement: ThroughputMeasurement) -> None:
        """Record a throughput measurement."""
        with self._lock:
            if len(self._throughput_measurements) >= 1000:
                self._throughput_measurements = self._throughput_measurements[-500:]
            
            self._throughput_measurements.append(measurement)
    
    def record_capacity_snapshot(self, snapshot: CapacitySnapshot) -> None:
        """Record a capacity snapshot for history."""
        with self._lock:
            if len(self._capacity_snapshots) >= 100:
                self._capacity_snapshots = self._capacity_snapshots[-50:]
            
            self._capacity_snapshots.append(snapshot)
    
    def update_overload_state(self, new_state: OverloadState, reason: str = "") -> None:
        """
        Update the runtime's overload state.
        
        Args:
            new_state: The new overload state
            reason: Why the state changed (for auditing)
        """
        with self._lock:
            old_state = self._overload_state
            if old_state != new_state:
                self._overload_state = new_state
                
                self._record_event("overload_state_changed", {
                    "from_state": old_state.value,
                    "to_state": new_state.value,
                    "reason": reason,
                })
    
    def enter_degradation(self, mode: DegradationMode, reason: str) -> DegradationRecord:
        """
        Enter a degradation mode under overload.
        
        Args:
            mode: The degradation mode to enter
            reason: Why degradation was triggered
            
        Returns:
            Record of the degradation event
        """
        with self._lock:
            record = DegradationRecord(
                record_id=f"deg_{uuid.uuid4().hex[:16]}",
                runtime_id=self._runtime_id,
                from_mode=DegradationMode.NONE,  # Simplified - track from state
                to_mode=mode,
                trigger=reason,
            )
            
            self._record_event("degradation_entered", {
                "mode": mode.value,
                "trigger": reason,
            })
            
            return record
    
    def get_performance_snapshot(self) -> "PerformanceSnapshot":
        """
        Get an immutable snapshot of current performance state.
        
        Used for diagnostics and monitoring.
        """
        with self._lock:
            # Calculate latency distribution from recent measurements
            if self._latency_measurements:
                durations = [m.duration_seconds for m in self._latency_measurements]
                min_lat = min(durations)
                max_lat = max(durations)
                
                # Sort for percentiles (simplified calculation)
                sorted_durations = sorted(durations)
                p50_idx = int(len(sorted_durations) * 0.50)
                p90_idx = int(len(sorted_durations) * 0.90)
                p95_idx = int(len(sorted_durations) * 0.95)
                p99_idx = int(len(sorted_durations) * 0.99)
                
                latency_dist = LatencyDistribution(
                    sample_count=len(durations),
                    min_latency_seconds=min_lat,
                    max_latency_seconds=max_lat,
                    p50_latency=LatencyPercentile.from_milliseconds(50, sorted_durations[p50_idx] * 1000) if p50_idx < len(sorted_durations) else None,
                    p90_latency=LatencyPercentile.from_milliseconds(90, sorted_durations[p90_idx] * 1000) if p90_idx < len(sorted_durations) else None,
                    p95_latency=LatencyPercentile.from_milliseconds(95, sorted_durations[p95_idx] * 1000) if p95_idx < len(sorted_durations) else None,
                    p99_latency=LatencyPercentile.from_milliseconds(99, sorted_durations[p99_idx] * 1000) if p99_idx < len(sorted_durations) else None,
                    mean_latency_seconds=sum(durations) / len(durations),
                )
            else:
                latency_dist = LatencyDistribution(
                    sample_count=0,
                    min_latency_seconds=0.0,
                    max_latency_seconds=0.0,
                )
            
            return PerformanceSnapshot(
                snapshot_id=f"perf_{uuid.uuid4().hex[:16]}",
                runtime_id=self._runtime_id,
                timestamp_utc=time.time(),
                domain_states={k: v.to_dict() for k, v in self._domains.items()},
                objective_count=len(self._objectives),
                budget_count=len(self._budgets),
                latency_distribution=latency_dist,
                overload_state=self._overload_state,
            )
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get diagnostic information about performance state."""
        with self._lock:
            return {
                "runtime_id": self._runtime_id,
                "domain_count": len(self._domains),
                "objective_count": len(self._objectives),
                "budget_count": len(self._budgets),
                "overload_state": self._overload_state.value,
                "latency_measurement_count": len(self._latency_measurements),
                "history_entry_count": len(self._history_entries),
            }
    
    def _record_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Record an internal event (bounded)."""
        self._history_entries.append({
            "timestamp_utc": time.time(),
            "event_type": event_type,
            "payload": dict(payload),
        })
        
        if len(self._history_entries) > self._max_history:
            self._history_entries = self._history_entries[-self._max_history:]


@dataclass(frozen=True)
class PerformanceDomainInfo:
    """Information about a registered performance domain."""
    
    domain_id: str
    owner_id: str
    
    objectives: Dict[PerformanceObjectiveId, PerformanceObjective] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "domain_id": self.domain_id,
            "owner_id": self.owner_id,
            "objective_count": len(self.objectives),
        }


@dataclass(frozen=True)
class PerformanceSnapshot:
    """
    Immutable snapshot of performance state.
    
    Used for diagnostics, monitoring, and historical analysis.
    """
    
    snapshot_id: str
    runtime_id: str
    
    timestamp_utc: float
    
    # State
    domain_states: Dict[str, Any] = field(default_factory=dict)
    objective_count: int = 0
    budget_count: int = 0
    
    # Metrics
    latency_distribution: LatencyDistribution = field(
        default_factory=lambda: LatencyDistribution(sample_count=0, min_latency_seconds=0.0, max_latency_seconds=0.0)
    )
    
    overload_state: OverloadState = OverloadState.NORMAL


# =============================================================================
# MEASUREMENT COORDINATOR
# =============================================================================

class PerformanceMeasurementCoordinator:
    """
    Coordinates measurement collection and normalization.
    
    Owner of:
        - Measurement registration
        - Measurement scheduling (when to collect)
        - Metric normalization (units, scales)
        - Latency measurement timing
        - Throughput counting
        
    Does NOT own:
        - The actual measurement sources
        - Storage or persistence
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # Registered measurements
        self._registered_measurements: Dict[str, "MeasurementRegistration"] = {}
        
        # Normalization rules
        self._normalization_rules: Dict[str, Callable[[float], float]] = {}
    
    def register_measurement(
        self,
        measurement_id: str,
        domain: PerformanceDomain,
        metric_name: str,
        unit: str,
    ) -> "MeasurementRegistration":
        """Register a new measurement type."""
        with self._lock:
            registration = MeasurementRegistration(
                measurement_id=measurement_id,
                runtime_id=self._runtime_id,
                domain=domain,
                metric_name=metric_name,
                unit=unit,
                registered_at_utc=time.time(),
            )
            
            self._registered_measurements[measurement_id] = registration
            return registration
    
    def normalize_measurement(self, measurement_id: str, raw_value: float) -> float:
        """Apply normalization rules to a raw measurement."""
        with self._lock:
            rule = self._normalization_rules.get(measurement_id)
            if rule is None:
                return raw_value  # No normalization
            return rule(raw_value)
    
    def get_registered_measurements(self) -> List["MeasurementRegistration"]:
        """Get all registered measurement types."""
        with self._lock:
            return list(self._registered_measurements.values())


@dataclass(frozen=True)
class MeasurementRegistration:
    """
    Registration of a measurement type.
    
    Defines what is being measured and how to interpret it.
    """
    
    measurement_id: str
    runtime_id: str
    
    domain: PerformanceDomain
    metric_name: str
    unit: str
    
    registered_at_utc: float


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Domain types
    "PerformanceDomain",
    
    # Objectives and targets
    "PerformanceObjectiveId",
    "PerformanceTarget",
    "PerformanceConstraint",
    "PerformanceObjective",
    "PerformanceObjectiveReport",
    "ObjectiveStatus",
    
    # Budgets
    "BudgetKind",
    "BudgetScope",
    "PerformanceBudget",
    "BudgetConsumption",
    "BudgetStatus",
    "BudgetViolation",
    "BudgetSnapshot",
    
    # Latency
    "LatencyMeasurement",
    "LatencyDistribution",
    "LatencyPercentile",
    "LatencyBudget",
    "LatencySnapshot",
    
    # Throughput
    "ThroughputMeasurement",
    "ThroughputRate",
    "ThroughputWindow",
    "ThroughputTarget",
    "ThroughputSnapshot",
    
    # Capacity (extended)
    "CapacityObservation",
    "CapacityBreakpoint",
    "CapacityHeadroom",
    "CapacityForecast",
    "CapacityProjection",
    
    # Utilization
    "UtilizationMeasurement",
    "UtilizationSnapshot",
    
    # Efficiency
    "EfficiencyReport",
    
    # Contention
    "ContentionObservation",
    "ContentionAnalysis",
    
    # Overload state machine
    "OverloadState",
    
    # Degradation
    "DegradationMode",
    "DegradationRecord",
    
    # Backpressure
    "BackpressureLevel",
    "BackpressureSignal",
    "BackpressurePolicy",
    
    # Load shedding
    "LoadSheddingPolicy",
    "LoadSheddingDecision",
    
    # Canonical authorities
    "PerformanceManager",
    "PerformanceMeasurementCoordinator",
    
    # Policy Engine (new in 3.7.18-I)
    "PerformancePolicyEngine",
    "OverloadDecision",
    "BackpressureDecision",
    "LoadSheddingDecision",
    "ScalingDecision",
    
    # Capacity Planner (new in 3.7.18-I)
    "CapacityPlanner",
    "CapacityForecast",
    "CapacityHeadroom",
    "CapacityReserve",
    "CapacityRecommendation",
    "CapacityGap",
    "CapacityProjection",
    "CapacityRequirement",
    "CapacityPlannerSnapshot",
    
    # Bottleneck Analyzer (new in 3.7.18-I)
    "BottleneckAnalyzer",
    "BottleneckType",
    "BottleneckSeverity",
    "BottleneckEvidence",
    "BottleneckFinding",
    "OptimizationProposal",
    "BottleneckAnalysisResult",
    "ContentionAnalysisResult",
    "BottleneckAnalyzerSnapshot",
    
    # Benchmark Coordinator (new in 3.7.18-I)
    "BenchmarkCoordinator",
    "BenchmarkType",
    "BenchmarkEnvironment",
    "BenchmarkDefinition",
    "MicroBenchmarkDefinition",
    "LoadProfile",
    "BenchmarkResult",
    "BaselineReference",
    "PerformanceComparison",
    "PerformanceRegression",
    "BenchmarkCoordinatorSnapshot",
    
    # Policies module exports
    "BatchTrigger",
    "BatchDeadlineBehavior",
    "BatchingPolicy",
    "BatchRequest",
    "Batch",
    "BatchResult",
    "BatchSnapshot",
    
    "CacheReplacementPolicy",
    "CacheConsistencyModel",
    "CachePolicy",
    "CacheSnapshot",
    
    "BackpressureLevel",  # Also in policies
    "BackpressureSignal",  # Also in policies
    "BackpressurePolicy",  # Also in policies
    
    "LoadSheddingEligibility",
    "LoadSheddingPolicy",  # Also in policies
    "LoadSheddingDecision",  # Also in policies
    
    "AutoscalingPolicy",
    "ScalingDecision",  # Also in policies
    "PerformanceIsolationPolicy",
    
    "ObjectiveEvaluationPolicy",
]
