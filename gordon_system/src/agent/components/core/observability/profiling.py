# Core Profiling Framework
# =========================

"""
Profiling, diagnostics, and performance analysis for Gordon Core.

This module provides:
- CPU, memory, and I/O profiling
- Latency and bottleneck detection
- Capacity planning hooks
- Performance regression detection
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, ContextManager
from enum import Enum, auto
import time
import uuid
import threading


# =============================================================================
# PROFILE TYPES
# =============================================================================

class ProfileType(Enum):
    """Types of profiling to perform."""
    
    CPU = "cpu"              # CPU instruction-level profiling
    MEMORY = "memory"        # Memory allocation and usage
    IO = "io"                # I/O operations (file, network)
    GPU = "gpu"              # GPU utilization and memory
    ALLOCATION = "allocation"  # Object allocation tracking
    TIMING = "timing"        # Function timing and call stacks


@dataclass(frozen=True)
class ProfileDefinition:
    """
    Definition for a profiling session.
    
    Specifies what to profile and how long to collect.
    """
    
    # Required fields (no defaults) - must come first
    profile_type: ProfileType = ProfileType.CPU  # Type of profiling to perform (default CPU)
    name: str = "unnamed_profile"                  # Human-readable name
    
    # Optional fields with defaults - must come after required fields
    definition_id: str = field(default_factory=lambda: f"profile_{uuid.uuid4().hex[:8]}")  # Definition identifier
    duration_seconds: float = 60.0  # Default 1 minute
    sample_rate_hz: float = 100.0   # Samples per second
    process_name_filter: Optional[str] = None  # Filter by process name
    thread_id_filter: Optional[int] = None     # Filter by thread ID


# =============================================================================
# PROFILE SESSION
# =============================================================================

@dataclass(frozen=True)
class ProfileSession:
    """
    A single profiling session.
    
    Contains all collected profile data for a time window.
    """
    
    session_id: str
    definition_id: str
    
    # Timing
    start_time_utc: float
    end_time_utc: float
    
    # Collected samples
    samples: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        """Get session duration."""
        return self.end_time_utc - self.start_time_utc
    
    @property
    def sample_count(self) -> int:
        """Get number of samples collected."""
        return len(self.samples)


# =============================================================================
# FLAME GRAPH DATA
# =============================================================================

@dataclass(frozen=True)
class FlameGraphNode:
    """
    A node in a flame graph.
    
    Represents one frame in the call stack with timing data.
    """
    
    name: str                  # Function name
    self_time_seconds: float   # Time spent directly in this function
    total_time_seconds: float  # Total time (including children)
    call_count: int            # Number of times called
    
    children: List["FlameGraphNode"] = field(default_factory=list)


@dataclass(frozen=True)
class FlameGraph:
    """
    Flame graph representation of profiling data.
    
    Shows the call stack hierarchy with timing information.
    """
    
    session_id: str
    root_nodes: List[FlameGraphNode]
    
    total_time_seconds: float
    
    @property
    def max_depth(self) -> int:
        """Get maximum call stack depth."""
        if not self.root_nodes:
            return 0
        
        def get_depth(node: FlameGraphNode, current_depth: int = 1) -> int:
            if not node.children:
                return current_depth
            return max(
                get_depth(child, current_depth + 1)
                for child in node.children
            )
        
        return max(get_depth(node) for node in self.root_nodes)


# =============================================================================
# PROFILING DATA COLLECTOR
# =============================================================================

class ProfileCollector(ABC):
    """
    Abstract base class for profile data collectors.
    
    Each collector is responsible for gathering a specific type of profiling data.
    """
    
    @abstractmethod
    def start(self) -> None:
        """Start collecting profiling data."""
        ...
    
    @abstractmethod
    def stop(self) -> None:
        """Stop collecting profiling data."""
        ...
    
    @abstractmethod
    def get_samples(self) -> List[Dict[str, Any]]:
        """Get collected samples."""
        ...


# =============================================================================
# CPU PROFILER
# =============================================================================

class CpuProfiler(ProfileCollector):
    """
    CPU profiler using sampling.
    
    Collects function call stack samples at regular intervals.
    """
    
    def __init__(
        self,
        sample_rate_hz: float = 100.0,
        max_samples: int = 10000,
    ) -> None:
        self._sample_rate = sample_rate_hz
        self._max_samples = max_samples
        
        self._running = False
        self._samples: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
    
    def start(self) -> None:
        """Start CPU profiling."""
        self._running = True
        self._samples.clear()
    
    def stop(self) -> None:
        """Stop CPU profiling."""
        self._running = False
    
    def get_samples(self) -> List[Dict[str, Any]]:
        """Get collected stack samples."""
        with self._lock:
            return list(self._samples)
    
    def sample_stack(self) -> Dict[str, Any]:
        """
        Collect a single stack sample.
        
        Returns:
            Dictionary with stack information
        """
        import traceback
        
        # Get current call stack
        stack = traceback.format_stack()
        
        return {
            "timestamp_utc": time.time(),
            "thread_id": threading.current_thread().ident,
            "stack": stack,
            "sample_type": "cpu",
        }
    
    def record_sample(self, sample: Dict[str, Any]) -> None:
        """Record a sample."""
        with self._lock:
            if len(self._samples) >= self._max_samples:
                self._samples.pop(0)
            
            self._samples.append(sample)


# =============================================================================
# MEMORY PROFILER
# =============================================================================

class MemoryProfiler(ProfileCollector):
    """
    Memory profiler tracking allocation patterns.
    
    Monitors memory usage over time.
    """
    
    def __init__(
        self,
        sample_rate_hz: float = 10.0,  # Less frequent than CPU profiling
        max_samples: int = 5000,
    ) -> None:
        self._sample_rate = sample_rate_hz
        self._max_samples = max_samples
        
        self._running = False
        self._samples: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
    
    def start(self) -> None:
        """Start memory profiling."""
        self._running = True
    
    def stop(self) -> None:
        """Stop memory profiling."""
        self._running = False
    
    def get_samples(self) -> List[Dict[str, Any]]:
        """Get collected memory samples."""
        with self._lock:
            return list(self._samples)
    
    def sample_memory(self) -> Dict[str, Any]:
        """
        Collect a single memory sample.
        
        Returns:
            Dictionary with memory usage information
        """
        import gc
        import sys
        
        # Get object counts by type
        gc.collect()
        obj_counts: Dict[str, int] = {}
        for obj in gc.get_objects():
            type_name = type(obj).__name__
            obj_counts[type_name] = obj_counts.get(type_name, 0) + 1
        
        return {
            "timestamp_utc": time.time(),
            "thread_id": threading.current_thread().ident,
            "object_count_by_type": obj_counts,
            "gc_collected": gc.garbage,
            "sample_type": "memory",
        }
    
    def record_sample(self, sample: Dict[str, Any]) -> None:
        """Record a sample."""
        with self._lock:
            if len(self._samples) >= self._max_samples:
                self._samples.pop(0)
            
            self._samples.append(sample)


# =============================================================================
# PROFILING SESSION MANAGER
# =============================================================================

class ProfilingSessionManager:
    """
    Manager for profiling sessions.
    
    Coordinates multiple profile collectors and creates profiling reports.
    """
    
    def __init__(
        self,
        runtime_id: Optional[str] = None,
    ) -> None:
        import uuid
        
        self._runtime_id = runtime_id or str(uuid.uuid4())
        
        # Active sessions by session ID
        self._sessions: Dict[str, ProfileSession] = {}
        
        # Collectors for each profile type
        self._collectors: Dict[ProfileType, ProfileCollector] = {
            ProfileType.CPU: CpuProfiler(),
            ProfileType.MEMORY: MemoryProfiler(),
        }
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime identifier."""
        return self._runtime_id
    
    def start_session(
        self,
        definition: Optional[ProfileDefinition] = None,
    ) -> str:
        """
        Start a new profiling session.
        
        Args:
            definition: Profile definition (uses defaults if not provided)
            
        Returns:
            Session ID
        """
        definition = definition or ProfileDefinition()
        
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        # Get start time
        start_time = time.time()
        
        # Start collectors
        for collector in self._collectors.values():
            collector.start()
        
        # Store session info (will be completed when stopped)
        self._sessions[session_id] = ProfileSession(
            session_id=session_id,
            definition_id=definition.definition_id,
            start_time_utc=start_time,
            end_time_utc=start_time,  # Will be updated on stop
            samples=[],
        )
        
        return session_id
    
    def stop_session(self, session_id: str) -> Optional[ProfileSession]:
        """
        Stop a profiling session.
        
        Args:
            session_id: ID of the session to stop
            
        Returns:
            Completed profile session, or None if not found
        """
        session = self._sessions.get(session_id)
        if session is None:
            return None
        
        # Get end time and collect samples from all collectors
        end_time = time.time()
        
        all_samples: List[Dict[str, Any]] = []
        for collector in self._collectors.values():
            all_samples.extend(collector.stop())
        
        completed_session = ProfileSession(
            session_id=session_id,
            definition_id=session.definition_id,
            start_time_utc=session.start_time_utc,
            end_time_utc=end_time,
            samples=all_samples,
        )
        
        # Store the completed session
        self._sessions[session_id] = completed_session
        
        return completed_session
    
    def get_session(self, session_id: str) -> Optional[ProfileSession]:
        """Get a profiling session by ID."""
        return self._sessions.get(session_id)
    
    def generate_flame_graph(
        self,
        session_id: str,
    ) -> Optional[FlameGraph]:
        """
        Generate a flame graph from a profiling session.
        
        Args:
            session_id: ID of the profiling session
            
        Returns:
            Flame graph, or None if session not found
        """
        session = self.get_session(session_id)
        if session is None:
            return None
        
        # Aggregate samples into call stack data
        # This would analyze all collected stack traces and build the flame graph
        
        root_nodes: List[FlameGraphNode] = []
        
        return FlameGraph(
            session_id=session_id,
            root_nodes=root_nodes,
            total_time_seconds=session.duration_seconds,
        )
    
    def get_all_sessions(self) -> List[ProfileSession]:
        """Get all completed profiling sessions."""
        return list(self._sessions.values())


# =============================================================================
# PERFORMANCE ANALYSIS
# =============================================================================

@dataclass(frozen=True)
class BottleneckAnalysis:
    """
    Analysis of a performance bottleneck.
    
    Describes the location, cause, and impact of a bottleneck.
    """
    
    # Location - required fields without defaults must come first
    component: str           # Which component is affected
    measured_latency_seconds: float  # Actual measured latency (required, no default)
    
    # Optional fields with defaults - must come after required fields
    function_name: Optional[str] = None  # Specific function (if known)
    expected_latency_seconds: float = 0.1  # Expected threshold
    severity: str = "warning"  # info, warning, critical
    affected_requests: int = 1
    analysis_id: str = field(default_factory=lambda: f"bottleneck_{uuid.uuid4().hex[:8]}")  # Analysis identifier
    recommendations: List[str] = field(default_factory=list)  # Recommendations for fixing bottleneck


@dataclass(frozen=True)
class CapacityAnalysis:
    """
    Analysis of capacity constraints.
    
    Evaluates current usage against limits and forecasts.
    """
    
    # Resource being analyzed - required fields without defaults must come first
    resource_type: str      # e.g., "cpu", "memory", "queue"
    current_usage_percent: float
    
    # Optional fields with defaults - must come after required fields
    analysis_id: str = field(default_factory=lambda: f"capacity_{uuid.uuid4().hex[:8]}")  # Analysis identifier
    hard_limit_percent: float = 100.0
    warning_threshold_percent: float = 80.0
    projected_utilization_1h: Optional[float] = None
    projected_utilization_24h: Optional[float] = None


# =============================================================================
# PERFORMANCE REGRESSION DETECTION
# =============================================================================

@dataclass(frozen=True)
class PerformanceBaseline:
    """
    Baseline metrics for regression detection.
    
    Stores historical performance data for comparison.
    """
    
    baseline_id: str
    metric_name: str
    
    # Historical values
    samples: List[float]
    
    @property
    def mean(self) -> float:
        """Get mean of samples."""
        if not self.samples:
            return 0.0
        return sum(self.samples) / len(self.samples)
    
    @property
    def std_dev(self) -> float:
        """Get standard deviation of samples."""
        if len(self.samples) < 2:
            return 0.0
        
        mean = self.mean
        variance = sum((x - mean) ** 2 for x in self.samples) / len(self.samples)
        return variance ** 0.5


class RegressionDetector:
    """
    Detector for performance regressions.
    
    Compares current metrics against baselines to detect regressions.
    """
    
    def __init__(
        self,
        runtime_id: str,
        std_threshold: float = 2.0,  # 2 standard deviations
    ) -> None:
        self.runtime_id = runtime_id
        self._std_threshold = std_threshold
        
        # Baselines by metric name
        self._baselines: Dict[str, PerformanceBaseline] = {}
    
    def record_baseline(
        self,
        metric_name: str,
        values: List[float],
    ) -> None:
        """
        Record a baseline for a metric.
        
        Args:
            metric_name: Name of the metric
            values: Historical samples to use as baseline
        """
        self._baselines[metric_name] = PerformanceBaseline(
            baseline_id=f"baseline_{uuid.uuid4().hex[:8]}",
            metric_name=metric_name,
            samples=values,
        )
    
    def detect_regression(
        self,
        metric_name: str,
        current_value: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Check if a value indicates a regression.
        
        Args:
            metric_name: Name of the metric
            current_value: Current measurement
            
        Returns:
            Regression info if detected, None otherwise
        """
        baseline = self._baselines.get(metric_name)
        if baseline is None:
            return None
        
        mean = baseline.mean
        std_dev = baseline.std_dev
        
        # Check if outside threshold
        if std_dev <= 0:
            return None
        
        deviation = (current_value - mean) / std_dev
        
        if abs(deviation) > self._std_threshold:
            is_regression = current_value > mean  # Higher is worse for latency
            
            return {
                "metric_name": metric_name,
                "current_value": current_value,
                "baseline_mean": mean,
                "deviation_std": deviation,
                "is_regression": is_regression,
            }
        
        return None


# =============================================================================
# PROFILING CONTEXT MANAGER
# =============================================================================

class ProfiledBlock(ContextManager):
    """
    Context manager for profiling a code block.
    
    Usage:
        with profiler.block("operation_name"):
            # Code to profile
            pass
    
    Records timing and can be used to build flame graphs.
    """
    
    def __init__(
        self,
        profiler: "PerformanceProfiler",
        operation_name: str,
    ) -> None:
        self._profiler = profiler
        self._operation_name = operation_name
        self._start_time: Optional[float] = None
    
    def __enter__(self) -> "ProfiledBlock":
        self._start_time = time.monotonic()
        return self
    
    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> bool:
        if self._start_time is not None:
            duration = time.monotonic() - self._start_time
            self._profiler.record_timing(self._operation_name, duration)
        
        return False  # Don't suppress exceptions


# =============================================================================
# PERFORMANCE PROFILER
# =============================================================================

class PerformanceProfiler:
    """
    Performance profiler for timing and analysis.
    
    Tracks operation timings and detects performance issues.
    """
    
    def __init__(
        self,
        runtime_id: Optional[str] = None,
    ) -> None:
        import uuid
        
        self._runtime_id = runtime_id or str(uuid.uuid4())
        
        # Timing data
        self._timings: Dict[str, List[float]] = {}
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime identifier."""
        return self._runtime_id
    
    def record_timing(
        self,
        operation_name: str,
        duration_seconds: float,
    ) -> None:
        """
        Record a timing measurement.
        
        Args:
            operation_name: Name of the operation
            duration_seconds: How long it took
        """
        if operation_name not in self._timings:
            self._timings[operation_name] = []
        
        # Keep last 1000 measurements per operation
        while len(self._timings[operation_name]) >= 1000:
            self._timings[operation_name].pop(0)
        
        self._timings[operation_name].append(duration_seconds)
    
    def block(
        self,
        operation_name: str,
    ) -> ProfiledBlock:
        """
        Get a context manager for profiling a code block.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Context manager that records timing on exit
        """
        return ProfiledBlock(self, operation_name)
    
    def get_timing_stats(
        self,
        operation_name: str,
    ) -> Optional[Dict[str, float]]:
        """Get timing statistics for an operation."""
        timings = self._timings.get(operation_name)
        if not timings:
            return None
        
        sorted_timings = sorted(timings)
        
        return {
            "count": len(timings),
            "min": min(timings),
            "max": max(timings),
            "avg": sum(timings) / len(timings),
            "p50": sorted_timings[len(sorted_timings) // 2],
            "p95": sorted_timings[int(len(sorted_timings) * 0.95)],
            "p99": sorted_timings[int(len(sorted_timings) * 0.99)],
        }


__all__ = [
    # Profile types
    "ProfileType",
    "ProfileDefinition",
    
    # Sessions and data
    "ProfileSession",
    "FlameGraphNode",
    "FlameGraph",
    "ProfileCollector",
    
    # Profilers
    "CpuProfiler",
    "MemoryProfiler",
    "ProfilingSessionManager",
    
    # Analysis
    "BottleneckAnalysis",
    "CapacityAnalysis",
    
    # Regression detection
    "PerformanceBaseline",
    "RegressionDetector",
    
    # Performance profiler
    "ProfiledBlock",
    "PerformanceProfiler",
]