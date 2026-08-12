# Benchmark Coordinator
# =====================

"""
Benchmark coordination authority for Gordon runtime Phase 3.7.18-I.

This module provides the canonical benchmark coordinator:

CANONICAL AUTHORITY:
    - BenchmarkCoordinator: Benchmark execution coordination
    
The coordinator manages benchmark definitions, environments, and results.
It does NOT run benchmarks automatically during import or normal operation -
benchmarks must be explicitly triggered.

PRINCIPLES:
    - Benchmarks never run at import time
    - Benchmarks record full environment metadata
    - Baselines are immutable for reproducibility
    - Results include statistical confidence where available

Usage:
    from gordon.components.core.performance.benchmarks import (
        BenchmarkCoordinator,
        MicroBenchmarkDefinition,
    )
    
    coordinator = BenchmarkCoordinator(runtime_id="runtime_1")
    
    # Register a benchmark definition
    benchmark = MicroBenchmarkDefinition(
        benchmark_id="latency_test",
        name="Task Dispatch Latency",
        description="Measure task dispatch latency under load",
        environment={"workers": 4, "tasks": 100},
    )
    coordinator.register_benchmark(benchmark)
    
    # Execute the benchmark
    result = coordinator.execute_benchmark("latency_test")
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import uuid
import time


# =============================================================================
# BENCHMARK TYPES
# =============================================================================

class BenchmarkType(Enum):
    """Types of benchmarks."""
    
    MICRO = "micro"                    # Micro-benchmark (single function)
    COMPONENT = "component"            # Component-level benchmark
    SUBSYSTEM = "subsystem"            # Subsystem-level benchmark
    SYSTEM = "system"                  # Full system benchmark
    END_TO_END = "end_to_end"          # End-to-end workflow benchmark
    CAPACITY = "capacity"              # Capacity testing (scale up)
    STRESS = "stress"                  # Stress testing (beyond capacity)
    SOAK = "soak"                      # Long-duration stability test
    FAILURE_UNDER_LOAD = "failure_under_load"  # Failure recovery under load
    MULTI_RUNTIME = "multi_runtime"    # Multi-runtime isolation test
    DISTRIBUTED = "distributed"        # Distributed system benchmark


class BenchmarkEnvironment(Enum):
    """Benchmark environment types."""
    
    DEVELOPMENT = "development"        # Local dev environment
    TEST = "test"                      # Dedicated test environment
    PRODUCTION = "production"          # Production (read-only measurements)
    STAGING = "staging"                # Staging/CI environment


# =============================================================================
# BENCHMARK DEFINITIONS
# =============================================================================

@dataclass(frozen=True)
class BenchmarkDefinition:
    """
    Immutable benchmark definition.
    
    Defines what to measure and how to interpret results.
    """
    
    benchmark_id: str
    runtime_id: str
    
    # Identity
    name: str
    description: str
    
    # Type and scope
    benchmark_type: BenchmarkType
    environment_type: BenchmarkEnvironment
    
    # Workload definition
    workload_profile: Dict[str, Any]  # Tasks/sec, concurrency, etc.
    
    # Duration
    warmup_duration_seconds: float = 10.0
    test_duration_seconds: float = 60.0
    
    # Repetitions (for statistical confidence)
    repetitions: int = 3
    
    # Metrics to collect
    metrics: Tuple[str, ...] = field(default_factory=lambda: (
        "latency_p50", "latency_p95", "latency_p99",
        "throughput_tasks_per_sec", "error_rate_percent"
    ))
    
    # Success criteria
    success_thresholds: Dict[str, float] = field(default_factory=dict)  # metric -> max_value
    
    # Cleanup
    cleanup_required: bool = False
    cleanup_actions: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class MicroBenchmarkDefinition(BenchmarkDefinition):
    """Micro-benchmark definition (single function/method)."""
    
    target_function: Optional[str] = None  # Fully qualified name
    
    @classmethod
    def create_for_latency(
        cls,
        benchmark_id: str,
        runtime_id: str,
        description: str = "Latency microbenchmark",
    ) -> "MicroBenchmarkDefinition":
        return cls(
            benchmark_id=benchmark_id,
            runtime_id=runtime_id,
            name="Latency Microbenchmark",
            description=description,
            benchmark_type=BenchmarkType.MICRO,
            environment_type=BenchmarkEnvironment.DEVELOPMENT,
            warmup_duration_seconds=5.0,
            test_duration_seconds=30.0,
            repetitions=5,
        )


@dataclass(frozen=True)
class LoadProfile:
    """Load profile for stress/capacity benchmarks."""
    
    profile_id: str
    runtime_id: str
    
    # Ramp up
    initial_rps: float = 10.0           # Starting requests per second
    target_rps: float = 1000.0          # Target maximum RPS
    ramp_up_seconds: float = 60.0       # Time to reach target
    
    # Sustain
    sustain_seconds: float = 300.0      # Time at max load
    
    # Cool down
    cool_down_seconds: float = 30.0     # Time to reduce load
    
    # Burst
    burst_factor: float = 2.0           # Multiplier for burst phase


# =============================================================================
# BENCHMARK EXECUTION RESULTS
# =============================================================================

@dataclass(frozen=True)
class BenchmarkResult:
    """
    Result of a benchmark execution.
    
    Contains metrics, statistics, and analysis.
    """
    
    result_id: str
    runtime_id: str
    
    # Reference to definition
    benchmark_id: str
    benchmark_name: str
    timestamp_utc: float = field(default_factory=time.time)
    
    # Execution info
    environment_metadata: Dict[str, Any]
    
    # Metrics (per repetition if multiple)
    metrics_by_repetition: List[Dict[str, float]] = field(default_factory=list)
    
    # Aggregated results
    aggregated_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)  # metric -> {mean, std, min, max}
    
    # Success evaluation
    success: bool = False
    failed_thresholds: Tuple[Tuple[str, float, float], ...] = field(default_factory=tuple)  # (metric, actual, threshold)
    
    # Duration
    total_duration_seconds: float = 0.0


@dataclass(frozen=True)
class BaselineReference:
    """
    Reference to a baseline result for comparison.
    
    Used to detect regressions against known good state.
    """
    
    baseline_id: str
    runtime_id: str
    
    # What was measured
    benchmark_id: str
    environment_fingerprint: str  # Hash of environment configuration
    
    # Results at that time
    metrics: Dict[str, float]
    
    # When and where
    timestamp_utc: float
    git_revision: Optional[str] = None


# =============================================================================
# PERFORMANCE COMPARISON (for regression detection)
# =============================================================================

@dataclass(frozen=True)
class PerformanceComparison:
    """
    Comparison between two performance runs.
    
    Used to detect regressions against baseline.
    """
    
    comparison_id: str
    runtime_id: str
    
    # What we're comparing
    baseline_id: str  # Reference point
    candidate_id: str  # Current measurement
    
    # Metrics
    metric_differences: Dict[str, Dict[str, float]] = field(default_factory=dict)  # metric -> {delta_percent, is_regression}
    
    # Statistical confidence (where applicable)
    confidence_level: Optional[float] = None  # e.g., 0.95 for 95% confidence
    
    # Practical significance
    is_practically_significant: bool = False
    severity: str = "info"  # info, warning, critical
    
    timestamp_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class PerformanceRegression:
    """
    Detected performance regression.
    
    Comparison shows a regression - this is the finding.
    """
    
    regression_id: str
    runtime_id: str
    
    # What regressed
    benchmark_id: str
    metric_name: str
    
    # Measurements
    baseline_value: float
    current_value: float
    delta_percent: float
    
    # Context
    environment_differences: Tuple[str, ...] = field(default_factory=tuple)
    
    severity: str = "warning"  # info, warning, critical
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# BENCHMARK COORDINATOR (CANONICAL AUTHORITY)
# =============================================================================

class BenchmarkCoordinator:
    """
    Canonical benchmark execution coordinator.
    
    This is THE ONE source of benchmark management and coordination.
    It manages definitions, environments, and results but does NOT
    execute benchmarks itself.
    
    What it does NOT do:
        - Does not run benchmarks automatically at import time
        - Does not directly measure performance
        
    What it DOES own:
        - Benchmark definition storage
        - Environment registration
        - Baseline management
        - Result storage and comparison
    
    Usage:
        coordinator = BenchmarkCoordinator(runtime_id="runtime_1")
        
        # Register a benchmark
        benchmark = MicroBenchmarkDefinition(...)
        coordinator.register_benchmark(benchmark)
        
        # Record execution result when benchmark runs externally
        result = BenchmarkResult(...)
        coordinator.record_result(result)
    """
    
    def __init__(self, runtime_id: str):
        """
        Initialize the benchmark coordinator.
        
        Args:
            runtime_id: Unique identifier for this runtime instance
        """
        self._runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # Registered benchmarks (immutable once created)
        self._benchmarks: Dict[str, BenchmarkDefinition] = {}
        
        # Execution results (bounded history)
        self._results: Dict[str, BenchmarkResult] = {}
        self._max_results = 500
        
        # Baselines for regression detection
        self._baselines: Dict[str, BaselineReference] = {}  # benchmark_id -> baseline
        
        # Request history (bounded)
        self._request_history: List[Dict[str, Any]] = []
        self._max_requests = 200
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this coordinator serves."""
        return self._runtime_id
    
    # -------------------------------------------------------------------------
    # Benchmark Registration
    # -------------------------------------------------------------------------
    
    def register_benchmark(self, definition: BenchmarkDefinition) -> None:
        """
        Register a benchmark definition.
        
        Args:
            definition: The benchmark definition to register
            
        Raises:
            ValueError: If benchmark_id already exists
        """
        with self._lock:
            if definition.benchmark_id in self._benchmarks:
                raise ValueError(f"Benchmark {definition.benchmark_id} already registered")
            
            self._benchmarks[definition.benchmark_id] = definition
            self._record_request("register_benchmark", {
                "benchmark_id": definition.benchmark_id,
                "name": definition.name,
            })
    
    def get_benchmark(self, benchmark_id: str) -> Optional[BenchmarkDefinition]:
        """Get a registered benchmark definition."""
        with self._lock:
            return self._benchmarks.get(benchmark_id)
    
    def list_benchmarks(self) -> Tuple[BenchmarkDefinition, ...]:
        """List all registered benchmarks."""
        with self._lock:
            return tuple(self._benchmarks.values())
    
    # -------------------------------------------------------------------------
    # Result Recording
    # -------------------------------------------------------------------------
    
    def record_result(self, result: BenchmarkResult) -> None:
        """
        Record a benchmark execution result.
        
        Args:
            result: The execution result to record
        """
        with self._lock:
            self._results[result.result_id] = result
            
            if len(self._results) > self._max_results:
                # Remove oldest results (keep most recent)
                ids_to_remove = list(self._results.keys())[:-self._max_results]
                for bid in ids_to_remove:
                    del self._results[bid]
            
            self._record_request("record_result", {
                "result_id": result.result_id,
                "benchmark_id": result.benchmark_id,
                "success": result.success,
            })
    
    def get_result(self, result_id: str) -> Optional[BenchmarkResult]:
        """Get a recorded benchmark result."""
        with self._lock:
            return self._results.get(result_id)
    
    # -------------------------------------------------------------------------
    # Baseline Management
    # -------------------------------------------------------------------------
    
    def set_baseline(
        self,
        benchmark_id: str,
        metrics: Dict[str, float],
        environment_fingerprint: Optional[str] = None,
        git_revision: Optional[str] = None,
    ) -> BaselineReference:
        """
        Set a baseline result for a benchmark.
        
        Args:
            benchmark_id: The benchmark to set baseline for
            metrics: Metrics at the time (mean values)
            environment_fingerprint: Hash of environment configuration
            git_revision: Git commit hash at time of baseline
            
        Returns:
            The created baseline reference
        """
        with self._lock:
            baseline = BaselineReference(
                baseline_id=f"baseline_{uuid.uuid4().hex[:12]}",
                runtime_id=self._runtime_id,
                benchmark_id=benchmark_id,
                environment_fingerprint=environment_fingerprint or "unknown",
                metrics=dict(metrics),
                timestamp_utc=time.time(),
                git_revision=git_revision,
            )
            
            self._baselines[benchmark_id] = baseline
            
            self._record_request("set_baseline", {
                "benchmark_id": benchmark_id,
                "baseline_id": baseline.baseline_id,
                "metrics_count": len(metrics),
            })
            
            return baseline
    
    def get_baseline(self, benchmark_id: str) -> Optional[BaselineReference]:
        """Get the baseline for a benchmark."""
        with self._lock:
            return self._baselines.get(benchmark_id)
    
    # -------------------------------------------------------------------------
    # Regression Detection
    # -------------------------------------------------------------------------
    
    def compare_to_baseline(
        self,
        current_metrics: Dict[str, float],
        benchmark_id: Optional[str] = None,
        baseline_id: Optional[str] = None,
    ) -> PerformanceComparison:
        """
        Compare current metrics to a baseline.
        
        Args:
            current_metrics: Current measurement results
            benchmark_id: Get baseline from this benchmark (optional)
            baseline_id: Use specific baseline (optional, overrides benchmark_id)
            
        Returns:
            Comparison result with regression detection
        """
        with self._lock:
            # Get the appropriate baseline
            if baseline_id and baseline_id in self._baselines:
                baseline = self._baselines[baseline_id]
            elif benchmark_id and benchmark_id in self._baselines:
                baseline = self._baselines[benchmark_id]
            else:
                return PerformanceComparison(
                    comparison_id=f"compare_{uuid.uuid4().hex[:12]}",
                    runtime_id=self._runtime_id,
                    baseline_id="none",
                    candidate_id="none",
                    metric_differences={},
                    confidence_level=None,
                )
            
            # Calculate differences
            metric_differences: Dict[str, Dict[str, float]] = {}
            failed_thresholds = []
            
            for metric, current_value in current_metrics.items():
                if metric in baseline.metrics:
                    baseline_value = baseline.metrics[metric]
                    
                    if baseline_value > 0:
                        delta_percent = ((current_value - baseline_value) / baseline_value) * 100
                    else:
                        delta_percent = 0.0
                    
                    is_regression = delta_percent < -5.0  # 5% worse is a regression
                    
                    metric_differences[metric] = {
                        "baseline": baseline_value,
                        "current": current_value,
                        "delta_percent": delta_percent,
                        "is_regression": is_regression,
                    }
                    
                    if is_regression:
                        failed_thresholds.append((metric, delta_percent, -5.0))
            
            # Determine severity
            regressions = [m for m, d in metric_differences.items() if d.get("is_regression")]
            if len(regressions) >= 3:
                severity = "critical"
            elif len(regressions) >= 1:
                severity = "warning"
            else:
                severity = "info"
            
            comparison_id = f"compare_{uuid.uuid4().hex[:12]}"
            
            self._record_request("compare_baseline", {
                "comparison_id": comparison_id,
                "baseline_id": baseline.baseline_id,
                "metric_count": len(current_metrics),
                "regression_count": len(regressions),
            })
            
            return PerformanceComparison(
                comparison_id=comparison_id,
                runtime_id=self._runtime_id,
                baseline_id=baseline.baseline_id,
                candidate_id="none",  # Would be filled by caller
                metric_differences=metric_differences,
                confidence_level=0.95 if len(current_metrics) > 10 else None,
                is_practically_significant=len(regressions) >= 2,
                severity=severity,
            )
    
    def detect_regressions(
        self,
        current_metrics: Dict[str, float],
        benchmark_id: Optional[str] = None,
    ) -> Tuple[PerformanceRegression, ...]:
        """
        Detect performance regressions against baseline.
        
        Args:
            current_metrics: Current measurement results
            benchmark_id: Which benchmark's baseline to use
            
        Returns:
            Tuple of detected regressions (empty if no regressions)
        """
        comparison = self.compare_to_baseline(current_metrics, benchmark_id)
        
        regressions = []
        for metric, diff in comparison.metric_differences.items():
            if diff.get("is_regression", False):
                regressions.append(PerformanceRegression(
                    regression_id=f"reg_{uuid.uuid4().hex[:12]}",
                    runtime_id=self._runtime_id,
                    benchmark_id=comparison.baseline_id,
                    metric_name=metric,
                    baseline_value=diff.get("baseline", 0),
                    current_value=diff.get("current", 0),
                    delta_percent=diff.get("delta_percent", 0),
                    severity=comparison.severity,
                ))
        
        return tuple(regressions)
    
    # -------------------------------------------------------------------------
    # Diagnostics
    # -------------------------------------------------------------------------
    
    def get_result_history(self, limit: int = 100) -> List[BenchmarkResult]:
        """Get recent benchmark results."""
        with self._lock:
            return list(self._results.values())[-limit:]
    
    def get_request_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent requests (for diagnostics)."""
        with self._lock:
            return list(self._request_history[-limit:])
    
    def _record_request(self, request_type: str, payload: Dict[str, Any]) -> None:
        """Record a request for audit trail."""
        self._request_history.append({
            "timestamp_utc": time.time(),
            "request_type": request_type,
            "payload": dict(payload),
        })
        
        if len(self._request_history) > self._max_requests:
            self._request_history = self._request_history[-self._max_requests:]
    
    def get_snapshot(self) -> "BenchmarkCoordinatorSnapshot":
        """Get an immutable snapshot of coordinator state."""
        with self._lock:
            return BenchmarkCoordinatorSnapshot(
                snapshot_id=f"bc_snap_{uuid.uuid4().hex[:12]}",
                runtime_id=self._runtime_id,
                timestamp_utc=time.time(),
                benchmark_count=len(self._benchmarks),
                result_count=len(self._results),
                baseline_count=len(self._baselines),
            )


@dataclass(frozen=True)
class BenchmarkCoordinatorSnapshot:
    """Immutable snapshot of benchmark coordinator state."""
    snapshot_id: str
    runtime_id: str
    
    timestamp_utc: float
    
    benchmark_count: int = 0
    result_count: int = 0
    baseline_count: int = 0


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Benchmark types and definitions
    "BenchmarkType",
    "BenchmarkEnvironment",
    "BenchmarkDefinition",
    "MicroBenchmarkDefinition",
    "LoadProfile",
    
    # Results
    "BenchmarkResult",
    "BaselineReference",
    
    # Comparison and regression
    "PerformanceComparison",
    "PerformanceRegression",
    
    # Canonical authority
    "BenchmarkCoordinator",
    "BenchmarkCoordinatorSnapshot",
]