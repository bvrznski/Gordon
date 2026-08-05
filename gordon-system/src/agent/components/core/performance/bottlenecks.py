# Bottleneck Analyzer
# ===================

"""
Bottleneck detection and analysis authority for Gordon runtime Phase 3.7.18-I.

This module provides deterministic bottleneck detection:

CANONICAL AUTHORITIES:
    - BottleneckAnalyzer: Bottleneck detection and analysis
    
The analyzer identifies performance bottlenecks without mutating runtime state.
It produces findings with evidence that other authorities can act upon.

PRINCIPLES:
    - Deterministic (stable ordering for reproducibility)
    - Evidence-based (always include supporting data)
    - Non-mutating (reports findings, doesn't change behavior)
    - Actionable (recommendations are clear and specific)

Usage:
    from gordon.components.core.performance import BottleneckAnalyzer
    
    analyzer = BottleneckAnalyzer(runtime_id="runtime_1")
    
    # Analyze current state
    findings = analyzer.analyze(
        latency_measurements=measurements,
        queue_states=queues,
        worker_utilization=workers
    )
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import uuid
import time


# =============================================================================
# BOTTLENECK FINDING TYPES
# =============================================================================

class BottleneckType(Enum):
    """Types of bottlenecks that can be detected."""
    
    QUEUE_SATURATION = "queue_saturation"           # Queue backing up
    WORKER_CONTENTION = "worker_contention"         # Workers overwhelmed
    CPU_SATURATION = "cpu_saturation"               # CPU at limit
    MEMORY_PRESSURE = "memory_pressure"             # Memory pressure high
    GPU_SATURATION = "gpu_saturation"               # GPU at limit
    VRAM_PRESSURE = "vram_pressure"                 # VRAM at limit
    IO_BOTTLENECK = "io_bottleneck"                 # Storage/network I/O
    SERIALIZATION = "serialization"                 # Serialization overhead
    CONTENTION_LOCK = "contention_lock"             # Lock contention
    CONTEXT_SWITCH = "context_switch"               # Excessive context switching
    CACHE_MISSED = "cache_missed"                   # Cache inefficiency
    NETWORK_LATENCY = "network_latency"             # Network delay
    MODEL_INFERENCE = "model_inference"             # Model execution


class BottleneckSeverity(Enum):
    """Severity of a bottleneck finding."""
    
    LOW = "low"         # Noticeable but acceptable
    MEDIUM = "medium"   # Should be addressed soon
    HIGH = "high"       # Impacting performance significantly
    CRITICAL = "critical"  # Requires immediate attention


@dataclass(frozen=True)
class BottleneckEvidence:
    """
    Evidence supporting a bottleneck finding.
    
    Includes measurements, thresholds, and calculations that justify the finding.
    """
    
    evidence_id: str
    
    # Measurement values
    measured_value: float
    threshold_value: float
    
    # Context
    domain: str
    measurement_type: str  # e.g., "queue_depth", "utilization_percent"
    
    # How we calculated this
    calculation_method: str
    
    # Time context
    window_start_utc: float
    window_end_utc: float


# =============================================================================
# BOTTLENECK FINDING (CANONICAL ARTIFACT)
# =============================================================================

@dataclass(frozen=True)
class BottleneckFinding:
    """
    A bottleneck finding with full evidence.
    
    This is the OUTPUT of analysis - an immutable record that says:
    "I found a bottleneck in [domain] because [evidence]."
    """
    
    finding_id: str
    runtime_id: str
    
    # Finding metadata
    finding_type: BottleneckType
    severity: BottleneckSeverity
    
    # Location
    domain: str  # e.g., "task_queue", "worker_pool", "cpu"
    
    # Impact assessment
    estimated_impact_percent: float  # How much performance is affected?
    affected_stages: Tuple[str, ...] = field(default_factory=tuple)  # Which stages are impacted
    
    # Evidence
    evidence: Tuple[BottleneckEvidence, ...]
    
    # Recommendation
    recommendation: str  # What should be done?
    recommended_actions: Tuple[str, ...] = field(default_factory=tuple)
    
    timestamp_utc: float = field(default_factory=time.time)
    
    # Analysis metadata
    analysis_algorithm: str = "baseline"
    analysis_version: str = "1.0.0"


@dataclass(frozen=True)
class OptimizationProposal:
    """
    Proposed optimization based on bottleneck findings.
    
    Contains specific, actionable recommendations with expected benefits.
    """
    
    proposal_id: str
    runtime_id: str
    
    # What we found
    bottleneck_ids: Tuple[str, ...]
    
    # Proposed change
    proposed_action: str  # e.g., "increase worker pool size by 25%"
    
    # Expected outcome
    expected_improvement_percent: float
    confidence: str = "medium"  # low, medium, high
    
    # Constraints
    requires_restart: bool = False
    requires_config_change: bool = True
    risk_level: str = "low"  # low, medium, high
    
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# BOTTLENECK ANALYZER (CANONICAL AUTHORITY)
# =============================================================================

class BottleneckAnalyzer:
    """
    Canonical bottleneck detection and analysis authority.
    
    This is THE ONE source of bottleneck findings. It analyzes current state
    and produces immutable findings with evidence.
    
    What it does NOT do:
        - Does not resize pools or change runtime behavior
        - Does not trigger scaling actions directly
        
    What it DOES own:
        - Bottleneck detection algorithms
        - Evidence collection and analysis
        - Finding production (immutable artifacts)
        - Optimization proposals
    
    Usage:
        analyzer = BottleneckAnalyzer(runtime_id="runtime_1")
        
        # Analyze current state
        findings = analyzer.analyze(
            latency_measurements=measurements,
            queue_states=queues,
            worker_utilization=workers
        )
    """
    
    def __init__(self, runtime_id: str):
        """
        Initialize the bottleneck analyzer.
        
        Args:
            runtime_id: Unique identifier for this runtime instance
        """
        self._runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # Configuration thresholds (configurable)
        self._queue_saturation_threshold: float = 85.0
        self._worker_contention_threshold: float = 90.0
        self._cpu_saturated_threshold: float = 95.0
        self._memory_pressure_threshold: float = 90.0
        
        # History (bounded)
        self._findings_history: List[Dict[str, Any]] = []
        self._max_findings = 1000
        self._request_history: List[Dict[str, Any]] = []
        self._max_requests = 500
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this analyzer serves."""
        return self._runtime_id
    
    # -------------------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------------------
    
    def set_thresholds(
        self,
        queue_saturation: Optional[float] = None,
        worker_contention: Optional[float] = None,
        cpu_saturated: Optional[float] = None,
        memory_pressure: Optional[float] = None,
    ) -> None:
        """
        Set detection thresholds.
        
        Args:
            queue_saturation: Queue occupancy threshold for saturation
            worker_contention: Worker utilization threshold for contention
            cpu_saturated: CPU utilization at which we consider saturated
            memory_pressure: Memory usage percentage threshold
        """
        with self._lock:
            if queue_saturation is not None:
                self._queue_saturation_threshold = queue_saturation
            if worker_contention is not None:
                self._worker_contention_threshold = worker_contention
            if cpu_saturated is not None:
                self._cpu_saturated_threshold = cpu_saturated
            if memory_pressure is not None:
                self._memory_pressure_threshold = memory_pressure
    
    # -------------------------------------------------------------------------
    # Analysis Methods
    # -------------------------------------------------------------------------
    
    def analyze(
        self,
        latency_measurements: Optional[List[Dict[str, Any]]] = None,
        queue_states: Optional[Dict[str, Dict[str, float]]] = None,
        worker_utilization: Optional[Dict[str, float]] = None,
        cpu_percentages: Optional[Dict[str, float]] = None,
        memory_usage_bytes: Optional[float] = None,
        total_memory_bytes: Optional[float] = None,
    ) -> "BottleneckAnalysisResult":
        """
        Analyze current state for bottlenecks.
        
        Args:
            latency_measurements: Latency measurements with stage breakdowns
            queue_states: Queue states (occupancy, capacity)
            worker_utilization: Worker pool utilization percentages
            cpu_percentages: CPU usage per core/domain
            memory_usage_bytes: Current memory usage
            total_memory_bytes: Total available memory
            
        Returns:
            Analysis result with findings and recommendations
        """
        with self._lock:
            findings = []
            
            # 1. Check queue saturation
            if queue_states:
                for domain, state in queue_states.items():
                    occupancy = state.get("occupancy", 0)
                    capacity = state.get("capacity", 0)
                    
                    if capacity > 0 and occupancy / capacity > self._queue_saturation_threshold / 100:
                        findings.append(self._create_queue_saturation_finding(
                            domain=domain,
                            occupancy=occupancy,
                            capacity=capacity,
                        ))
            
            # 2. Check worker contention
            if worker_utilization:
                for domain, utilization in worker_utilization.items():
                    if utilization > self._worker_contention_threshold:
                        findings.append(self._create_worker_contention_finding(
                            domain=domain,
                            utilization_percent=utilization,
                        ))
            
            # 3. Check CPU saturation
            if cpu_percentages:
                for domain, percent in cpu_percentages.items():
                    if percent > self._cpu_saturated_threshold:
                        findings.append(self._create_cpu_saturation_finding(
                            domain=domain,
                            cpu_percent=percent,
                        ))
            
            # 4. Check memory pressure
            if total_memory_bytes and memory_usage_bytes:
                mem_percent = (memory_usage_bytes / total_memory_bytes) * 100
                if mem_percent > self._memory_pressure_threshold:
                    findings.append(self._create_memory_pressure_finding(
                        domain="system",
                        used_bytes=memory_usage_bytes,
                        total_bytes=total_memory_bytes,
                        percent=mem_percent,
                    ))
            
            # Sort by severity (critical first)
            findings.sort(key=lambda f: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(f.severity.value, 4))
            
            # Generate optimization proposals from findings
            proposals = self._generate_proposals(findings)
            
            result_id = f"bn_result_{uuid.uuid4().hex[:12]}"
            
            self._record_analysis(result_id, {
                "finding_count": len(findings),
                "severity_breakdown": {s.value: sum(1 for f in findings if f.severity == s) for s in BottleneckSeverity},
            })
            
            return BottleneckAnalysisResult(
                result_id=result_id,
                runtime_id=self._runtime_id,
                timestamp_utc=time.time(),
                findings=tuple(findings),
                proposals=tuple(proposals),
            )
    
    def analyze_latency_stage(self, stage_name: str, measurements: List[float]) -> Optional[BottleneckFinding]:
        """
        Analyze a specific latency stage for bottlenecks.
        
        Args:
            stage_name: Name of the stage (e.g., "dispatch", "execution")
            measurements: Latency measurements in seconds
            
        Returns:
            Finding if bottleneck detected, None otherwise
        """
        if not measurements:
            return None
        
        # Calculate percentiles
        sorted_measurements = sorted(measurements)
        n = len(sorted_measurements)
        
        p95_idx = int(n * 0.95) if n > 1 else 0
        p99_idx = int(n * 0.99) if n > 1 else 0
        
        p95_latency = sorted_measurements[min(p95_idx, n - 1)]
        p99_latency = sorted_measurements[min(p99_idx, n - 1)]
        
        # Check if tail latency is concerning (> 1 second)
        threshold_seconds = 1.0
        if p99_latency > threshold_seconds:
            return BottleneckFinding(
                finding_id=f"bn_lat_{uuid.uuid4().hex[:12]}",
                runtime_id=self._runtime_id,
                finding_type=BottleneckType.NETWORK_LATENCY,  # Generic for latency issues
                severity=BottleneckSeverity.HIGH if p99_latency > threshold_seconds * 2 else BottleneckSeverity.MEDIUM,
                domain=stage_name,
                estimated_impact_percent=min(100.0, (p99_latency / max(p95_latency, 0.01)) * 10),
                affected_stages=(stage_name,),
                evidence=(
                    BottleneckEvidence(
                        evidence_id=f"evid_{uuid.uuid4().hex[:8]}",
                        measured_value=p99_latency,
                        threshold_value=threshold_seconds,
                        domain=stage_name,
                        measurement_type="latency_p99",
                        calculation_method="percentile_calculation",
                        window_start_utc=time.time() - 60.0,  # Last minute
                        window_end_utc=time.time(),
                    ),
                ),
                recommendation=f"Reduce p99 latency from {p99_latency:.3f}s to below {threshold_seconds}s threshold",
                recommended_actions=("optimize_stage", "add_concurrency"),
            )
        
        return None
    
    def identify_hot_path(self, measurements: List[Dict[str, Any]], top_n: int = 5) -> Tuple[str, ...]:
        """
        Identify the most frequently executed or latency-critical paths.
        
        Args:
            measurements: Measurements with stage names and latencies
            top_n: Number of hot paths to return
            
        Returns:
            List of stage names identified as hot paths
        """
        # Calculate aggregate metrics per stage
        stage_stats: Dict[str, Dict[str, Any]] = {}
        
        for m in measurements:
            stage = m.get("stage", "unknown")
            
            if stage not in stage_stats:
                stage_stats[stage] = {
                    "count": 0,
                    "total_latency": 0.0,
                    "latencies": [],
                }
            
            stats = stage_stats[stage]
            stats["count"] += 1
            latency = m.get("duration_seconds", 0)
            stats["total_latency"] += latency
            stats["latencies"].append(latency)
        
        # Score each stage by frequency and latency contribution
        scored_stages: List[Tuple[str, float]] = []
        
        for stage, stats in stage_stats.items():
            avg_latency = stats["total_latency"] / max(stats["count"], 1)
            # Higher score = more frequent AND higher latency
            score = stats["count"] * (1 + avg_latency)
            scored_stages.append((stage, score))
        
        # Sort by score (descending) and return top N
        scored_stages.sort(key=lambda x: x[1], reverse=True)
        
        return tuple(s[0] for s in scored_stages[:top_n])
    
    def analyze_contention(self, contention_events: List[Dict[str, Any]]) -> "ContentionAnalysisResult":
        """
        Analyze resource contention patterns.
        
        Args:
            contention_events: Events with wait times and domains
            
        Returns:
            Contention analysis result
        """
        # Group events by domain
        by_domain: Dict[str, List[float]] = {}
        
        for event in contention_events:
            domain = event.get("domain", "unknown")
            wait_time = event.get("wait_seconds", 0)
            
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(wait_time)
        
        # Find most contentious domain
        most_contentious = None
        max_avg_wait = 0.0
        
        for domain, waits in by_domain.items():
            avg_wait = sum(waits) / len(waits) if waits else 0
            if avg_wait > max_avg_wait:
                max_avg_wait = avg_wait
                most_contentious = domain
        
        return ContentionAnalysisResult(
            analysis_id=f"cont_analysis_{uuid.uuid4().hex[:12]}",
            runtime_id=self._runtime_id,
            timestamp_utc=time.time(),
            by_domain=by_domain,
            most_contentious_domain=most_contentious,
            max_avg_wait_seconds=max_avg_wait,
        )
    
    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------
    
    def _create_queue_saturation_finding(
        self,
        domain: str,
        occupancy: int,
        capacity: int,
    ) -> BottleneckFinding:
        """Create a queue saturation finding."""
        saturation_percent = (occupancy / max(capacity, 1)) * 100
        
        return BottleneckFinding(
            finding_id=f"bn_q_{uuid.uuid4().hex[:12]}",
            runtime_id=self._runtime_id,
            finding_type=BottleneckType.QUEUE_SATURATION,
            severity=BottleneckSeverity.CRITICAL if saturation_percent > 95 else (
                BottleneckSeverity.HIGH if saturation_percent > 85 else BottleneckSeverity.MEDIUM
            ),
            domain=domain,
            estimated_impact_percent=min(100.0, saturation_percent - 70),
            affected_stages=("enqueue", "dequeue"),
            evidence=(
                BottleneckEvidence(
                    evidence_id=f"evid_{uuid.uuid4().hex[:8]}",
                    measured_value=saturation_percent,
                    threshold_value=self._queue_saturation_threshold,
                    domain=domain,
                    measurement_type="queue_occupancy_percent",
                    calculation_method="occupancy_capacity_ratio",
                    window_start_utc=time.time() - 60.0,
                    window_end_utc=time.time(),
                ),
            ),
            recommendation=f"Queue at {saturation_percent:.1f}% capacity. Consider increasing capacity or adding consumers.",
            recommended_actions=("increase_queue_capacity", "add_consumers"),
        )
    
    def _create_worker_contention_finding(
        self,
        domain: str,
        utilization_percent: float,
    ) -> BottleneckFinding:
        """Create a worker contention finding."""
        return BottleneckFinding(
            finding_id=f"bn_w_{uuid.uuid4().hex[:12]}",
            runtime_id=self._runtime_id,
            finding_type=BottleneckType.WORKER_CONTENTION,
            severity=BottleneckSeverity.HIGH if utilization_percent > 95 else BottleneckSeverity.MEDIUM,
            domain=domain,
            estimated_impact_percent=min(100.0, utilization_percent - 70),
            affected_stages=("task_dispatch", "worker_execution"),
            evidence=(
                BottleneckEvidence(
                    evidence_id=f"evid_{uuid.uuid4().hex[:8]}",
                    measured_value=utilization_percent,
                    threshold_value=self._worker_contention_threshold,
                    domain=domain,
                    measurement_type="worker_utilization_percent",
                    calculation_method="active_workers_total_workers_ratio",
                    window_start_utc=time.time() - 60.0,
                    window_end_utc=time.time(),
                ),
            ),
            recommendation=f"Workers at {utilization_percent:.1f}% utilization. Consider scaling pool.",
            recommended_actions=("scale_out_workers", "optimize_task_duration"),
        )
    
    def _create_cpu_saturation_finding(
        self,
        domain: str,
        cpu_percent: float,
    ) -> BottleneckFinding:
        """Create a CPU saturation finding."""
        return BottleneckFinding(
            finding_id=f"bn_cpu_{uuid.uuid4().hex[:12]}",
            runtime_id=self._runtime_id,
            finding_type=BottleneckType.CPU_SATURATION,
            severity=BottleneckSeverity.CRITICAL if cpu_percent > 98 else (
                BottleneckSeverity.HIGH if cpu_percent > 95 else BottleneckSeverity.MEDIUM
            ),
            domain=domain,
            estimated_impact_percent=min(100.0, cpu_percent - 70),
            affected_stages=("all_execution", "scheduling", "dispatch"),
            evidence=(
                BottleneckEvidence(
                    evidence_id=f"evid_{uuid.uuid4().hex[:8]}",
                    measured_value=cpu_percent,
                    threshold_value=self._cpu_saturated_threshold,
                    domain=domain,
                    measurement_type="cpu_utilization_percent",
                    calculation_method="cpu_time_total_time_ratio",
                    window_start_utc=time.time() - 60.0,
                    window_end_utc=time.time(),
                ),
            ),
            recommendation=f"CPU at {cpu_percent:.1f}%. Consider load balancing or scaling.",
            recommended_actions=("scale_out", "optimize_cpu_intensive_tasks"),
        )
    
    def _create_memory_pressure_finding(
        self,
        domain: str,
        used_bytes: float,
        total_bytes: float,
        percent: float,
    ) -> BottleneckFinding:
        """Create a memory pressure finding."""
        return BottleneckFinding(
            finding_id=f"bn_mem_{uuid.uuid4().hex[:12]}",
            runtime_id=self._runtime_id,
            finding_type=BottleneckType.MEMORY_PRESSURE,
            severity=BottleneckSeverity.CRITICAL if percent > 95 else (
                BottleneckSeverity.HIGH if percent > 90 else BottleneckSeverity.MEDIUM
            ),
            domain=domain,
            estimated_impact_percent=min(100.0, percent - 70),
            affected_stages=("allocation", "gc_pause", "serialization"),
            evidence=(
                BottleneckEvidence(
                    evidence_id=f"evid_{uuid.uuid4().hex[:8]}",
                    measured_value=percent,
                    threshold_value=self._memory_pressure_threshold,
                    domain=domain,
                    measurement_type="memory_utilization_percent",
                    calculation_method="used_total_ratio",
                    window_start_utc=time.time() - 60.0,
                    window_end_utc=time.time(),
                ),
            ),
            recommendation=f"Memory at {percent:.1f}%. Consider increasing capacity or reducing allocations.",
            recommended_actions=("increase_memory", "optimize_memory_usage"),
        )
    
    def _generate_proposals(self, findings: List[BottleneckFinding]) -> Tuple[OptimizationProposal, ...]:
        """Generate optimization proposals from findings."""
        proposals = []
        
        for finding in findings:
            if finding.finding_type == BottleneckType.QUEUE_SATURATION:
                proposals.append(OptimizationProposal(
                    proposal_id=f"prop_q_{uuid.uuid4().hex[:8]}",
                    runtime_id=self._runtime_id,
                    bottleneck_ids=(finding.finding_id,),
                    proposed_action=f"Increase queue capacity for {finding.domain}",
                    expected_improvement_percent=25.0,
                    confidence="medium",
                    requires_restart=False,
                    requires_config_change=True,
                    risk_level="low",
                ))
            elif finding.finding_type in (BottleneckType.WORKER_CONTENTION, BottleneckType.CPU_SATURATION):
                proposals.append(OptimizationProposal(
                    proposal_id=f"prop_scale_{uuid.uuid4().hex[:8]}",
                    runtime_id=self._runtime_id,
                    bottleneck_ids=(finding.finding_id,),
                    proposed_action="Scale out workers by 25%",
                    expected_improvement_percent=30.0,
                    confidence="high",
                    requires_restart=False,
                    requires_config_change=True,
                    risk_level="medium",
                ))
            elif finding.finding_type == BottleneckType.MEMORY_PRESSURE:
                proposals.append(OptimizationProposal(
                    proposal_id=f"prop_mem_{uuid.uuid4().hex[:8]}",
                    runtime_id=self._runtime_id,
                    bottleneck_ids=(finding.finding_id,),
                    proposed_action="Increase memory allocation by 50%",
                    expected_improvement_percent=20.0,
                    confidence="medium",
                    requires_restart=False,
                    requires_config_change=True,
                    risk_level="low",
                ))
        
        return tuple(proposals)
    
    # -------------------------------------------------------------------------
    # History and Diagnostics
    # -------------------------------------------------------------------------
    
    def _record_analysis(self, result_id: str, payload: Dict[str, Any]) -> None:
        """Record an analysis for audit trail."""
        self._findings_history.append({
            "timestamp_utc": time.time(),
            "result_id": result_id,
            "payload": dict(payload),
        })
        
        if len(self._findings_history) > self._max_findings:
            self._findings_history = self._findings_history[-self._max_findings:]
    
    def get_findings_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent analysis results."""
        with self._lock:
            return list(self._findings_history[-limit:])
    
    def get_snapshot(self) -> "BottleneckAnalyzerSnapshot":
        """Get an immutable snapshot of analyzer state."""
        with self._lock:
            return BottleneckAnalyzerSnapshot(
                snapshot_id=f"bn_snap_{uuid.uuid4().hex[:12]}",
                runtime_id=self._runtime_id,
                timestamp_utc=time.time(),
                threshold_queue_saturation=self._queue_saturation_threshold,
                threshold_worker_contention=self._worker_contention_threshold,
                threshold_cpu_saturated=self._cpu_saturated_threshold,
                threshold_memory_pressure=self._memory_pressure_threshold,
            )


# =============================================================================
# ANALYSIS RESULTS
# =============================================================================

@dataclass(frozen=True)
class BottleneckAnalysisResult:
    """
    Result of bottleneck analysis.
    
    Contains all findings and recommendations from an analysis run.
    """
    
    result_id: str
    runtime_id: str
    
    timestamp_utc: float
    
    findings: Tuple[BottleneckFinding, ...]
    proposals: Tuple[OptimizationProposal, ...]
    
    @property
    def has_findings(self) -> bool:
        """Check if any bottlenecks were found."""
        return len(self.findings) > 0
    
    @property
    def critical_count(self) -> int:
        """Count of critical severity findings."""
        return sum(1 for f in self.findings if f.severity == BottleneckSeverity.CRITICAL)
    
    @property
    def high_count(self) -> int:
        """Count of high severity findings."""
        return sum(1 for f in self.findings if f.severity == BottleneckSeverity.HIGH)


@dataclass(frozen=True)
class ContentionAnalysisResult:
    """
    Result of contention analysis.
    
    Shows which resources are causing the most wait time.
    """
    
    analysis_id: str
    runtime_id: str
    
    timestamp_utc: float
    
    by_domain: Dict[str, List[float]]
    
    most_contentious_domain: Optional[str] = None
    max_avg_wait_seconds: float = 0.0


@dataclass(frozen=True)
class BottleneckAnalyzerSnapshot:
    """
    Immutable snapshot of bottleneck analyzer state.
    """
    
    snapshot_id: str
    runtime_id: str
    
    timestamp_utc: float
    
    threshold_queue_saturation: float
    threshold_worker_contention: float
    threshold_cpu_saturated: float
    threshold_memory_pressure: float


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Finding types
    "BottleneckType",
    "BottleneckSeverity",
    
    # Artifacts
    "BottleneckEvidence",
    "BottleneckFinding",
    "OptimizationProposal",
    
    # Analysis results
    "BottleneckAnalysisResult",
    "ContentionAnalysisResult",
    
    # Canonical authority
    "BottleneckAnalyzer",
    "BottleneckAnalyzerSnapshot",
]