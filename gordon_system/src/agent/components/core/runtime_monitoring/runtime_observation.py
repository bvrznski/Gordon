# Core Runtime Observation Coordinator
# ====================================

"""
Runtime observation coordination for health, integrity, and truth publication.

Provides:
- RuntimeObservationCoordinator: Orchestrates the monitoring pipeline
- Measurement orchestration
- Scheduling evaluations
- Runtime truth aggregation and publication
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum, auto
import uuid
import time
import asyncio
import threading

# Import monitoring components
from .health import HealthManager, HealthEvaluation, HealthDomain, HealthStatus
from .integrity import IntegrityManager, IntegrityEvaluation, IntegrityDomain, IntegrityStatus
from .heartbeat import HeartbeatManager, WatchdogSystem, WatchdogConfig, WatchdogPolicy, Watchdog
from ..runtime_state.runtime_truth import RuntimeTruth, RuntimeTruthPublisher, RuntimeTruthSnapshot

# =============================================================================
# OBSERVATION PIPELINE STAGES
# =============================================================================


class PipelineStage(Enum):
    """Stages of the observation pipeline."""
    
    MEASUREMENT = "measurement"           # Raw data collection
    NORMALIZATION = "normalization"       # Data standardization
    EVALUATION = "evaluation"             # Status assessment
    AGGREGATION = "aggregation"           # Result consolidation
    HEALTH_ASSESSMENT = "health_assessment"     # Health evaluation
    INTEGRITY_ASSESSMENT = "integrity_assessment"  # Integrity evaluation
    CAPABILITY_ASSESSMENT = "capability_assessment"  # Capability determination
    RUNTIME_TRUTH = "runtime_truth"       # Truth publication
    DIAGNOSTICS = "diagnostics"           # Diagnostic generation
    EVENTS = "events"                     # Event emission


# =============================================================================
# OBSERVATION RESULT
# =============================================================================


@dataclass(frozen=True)
class ObservationResult:
    """
    Result of an observation pipeline stage.
    
    Results are immutable and preserve provenance through the pipeline.
    """
    
    # Identifiers
    result_id: str              # Unique identifier for this result
    
    # Pipeline info
    runtime_id: str             # Which runtime was observed
    pipeline_stage: PipelineStage  # Which stage produced this result
    
    # Content
    success: bool               # Did the stage complete successfully?
    
    # Data
    data: Dict[str, Any] = field(default_factory=dict)  # Stage-specific results
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: float = field(default_factory=time.time)
    
    @property
    def duration_seconds(self) -> float:
        """Get the duration of this stage."""
        return self.completed_at_utc - self.started_at_utc
    
    @classmethod
    def success_result(
        cls,
        runtime_id: str,
        pipeline_stage: PipelineStage,
        data: Optional[Dict[str, Any]] = None
    ) -> "ObservationResult":
        """Create a successful result."""
        return cls(
            result_id=f"obs_result_{uuid.uuid4().hex[:12]}",
            runtime_id=runtime_id,
            pipeline_stage=pipeline_stage,
            success=True,
            data=data or {}
        )
    
    @classmethod
    def failure_result(
        cls,
        runtime_id: str,
        pipeline_stage: PipelineStage,
        error_message: Optional[str] = None
    ) -> "ObservationResult":
        """Create a failed result."""
        return cls(
            result_id=f"obs_result_{uuid.uuid4().hex[:12]}",
            runtime_id=runtime_id,
            pipeline_stage=pipeline_stage,
            success=False,
            data={"error": error_message or "Unknown error"} if error_message else {}
        )


# =============================================================================
# RUNTIME OBSERVATION COORDINATOR
# =============================================================================


class RuntimeObservationCoordinator:
    """
    Canonical coordinator for runtime observation pipeline.
    
    This orchestrates the complete monitoring flow:
    
        Observation Pipeline:
            Measurement → Normalization → Evaluation → Aggregation
                ↓
            Health Assessment → Integrity Assessment → Capability Assessment
                ↓
            Runtime Truth → Diagnostics → Events
    
    The coordinator owns:
        - Measurement orchestration  
        - Scheduling evaluations
        - Coordinating health and integrity assessments
        - Publishing runtime truth
        - Event generation
    
    Invariants:
        1. HealthManager remains independent authority
        2. IntegrityManager remains independent authority
        3. RuntimeTruth aggregates but never owns subsystem state
        4. All outputs are immutable and typed
    """
    
    def __init__(
        self,
        runtime_id: str,
        health_manager: Optional[HealthManager] = None,
        integrity_manager: Optional[IntegrityManager] = None,
        heartbeat_manager: Optional[HeartbeatManager] = None,
        watchdog_system: Optional[WatchdogSystem] = None
    ):
        """
        Initialize the RuntimeObservationCoordinator.
        
        Args:
            runtime_id: Unique identifier for this runtime instance
            health_manager: HealthManager instance (creates one if not provided)
            integrity_manager: IntegrityManager instance (creates one if not provided)
            heartbeat_manager: HeartbeatManager instance (creates one if not provided)
            watchdog_system: WatchdogSystem instance (creates one if not provided)
        """
        self._runtime_id = runtime_id
        
        # Create or use provided managers
        self._health_manager = health_manager or HealthManager(runtime_id=runtime_id)
        self._integrity_manager = integrity_manager or IntegrityManager(runtime_id=runtime_id)
        self._heartbeat_manager = heartbeat_manager or HeartbeatManager(runtime_id=runtime_id)
        self._watchdog_system = watchdog_system or WatchdogSystem(runtime_id=runtime_id)
        
        # Runtime truth
        self._truth = RuntimeTruth(runtime_id=runtime_id)
        self._truth_publisher = RuntimeTruthPublisher()
        
        # Pipeline state
        self._lock = threading.RLock()
        self._pipeline_results: List[ObservationResult] = []
        
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this coordinator serves."""
        return self._runtime_id
    
    @property
    def health_manager(self) -> HealthManager:
        """Get the health manager instance."""
        return self._health_manager
    
    @property
    def integrity_manager(self) -> IntegrityManager:
        """Get the integrity manager instance."""
        return self._integrity_manager
    
    @property
    def heartbeat_manager(self) -> HeartbeatManager:
        """Get the heartbeat manager instance."""
        return self._heartbeat_manager
    
    # -------------------------------------------------------------------------
    # Observation Pipeline (main entry point)
    # -------------------------------------------------------------------------
    
    async def run_pipeline(
        self,
        health_checks: Optional[Dict[HealthDomain, Callable[[str], Any]]] = None,
        integrity_checks: Optional[Dict[IntegrityDomain, Callable[[str], Any]]] = None,
        timeout_seconds: float = 60.0
    ) -> "ObservationPipelineResult":
        """
        Run the complete observation pipeline.
        
        Pipeline stages:
            1. Measurement - Collect raw observations
            2. Health Assessment - Evaluate health status
            3. Integrity Assessment - Evaluate integrity status
            4. Capability Assessment - Determine available capabilities
            5. Runtime Truth - Publish aggregated truth
            6. Diagnostics - Generate diagnostic reports
            7. Events - Emit monitoring events
            
        Args:
            health_checks: Dict of HealthDomain -> check function for health
            integrity_checks: Dict of IntegrityDomain -> check function for integrity
            timeout_seconds: Maximum time for entire pipeline
            
        Returns:
            Immutable ObservationPipelineResult with all stages' results
        """
        start_time = time.monotonic()
        
        # Collect all results
        all_results: List[ObservationResult] = []
        
        try:
            # Stage 1: Health Assessment
            health_result = await self._evaluate_health(
                health_checks or {},
                timeout_seconds / 3
            )
            all_results.append(health_result)
            
            if not health_result.success:
                # If health evaluation failed, still continue with other stages
                pass

            # Stage 2: Integrity Assessment  
            integrity_result = await self._evaluate_integrity(
                integrity_checks or {},
                timeout_seconds / 3
            )
            all_results.append(integrity_result)
            
            if not integrity_result.success:
                # If integrity evaluation failed, still continue
                pass

            # Stage 3: Capability Assessment (derived from health + integrity)
            capability_result = self._assess_capability(health_result, integrity_result)
            all_results.append(capability_result)
            
            # Stage 4: Runtime Truth
            truth_result = await self._publish_truth()
            all_results.append(truth_result)
            
            # Stage 5: Diagnostics
            diagnostics_result = self._generate_diagnostics(all_results)
            all_results.append(diagnostics_result)
            
        except asyncio.TimeoutError:
            # Pipeline timed out - record failure
            timeout_result = ObservationResult.failure_result(
                runtime_id=self._runtime_id,
                pipeline_stage=PipelineStage.RUNTIME_TRUTH,
                error_message="Pipeline execution timed out"
            )
            all_results.append(timeout_result)
        
        pipeline_duration = time.monotonic() - start_time
        
        return ObservationPipelineResult.create(
            runtime_id=self._runtime_id,
            results=all_results,
            total_duration_seconds=pipeline_duration
        )
    
    async def _evaluate_health(
        self,
        domain_checks: Dict[HealthDomain, Callable[[str], Any]],
        timeout_seconds: float
    ) -> ObservationResult:
        """Execute health assessment stage."""
        try:
            # Execute health evaluation
            evaluation = await self._health_manager.evaluate(
                subject=self._runtime_id,
                domain_checks=domain_checks,
                timeout_seconds=timeout_seconds
            )
            
            return ObservationResult.success_result(
                runtime_id=self._runtime_id,
                pipeline_stage=PipelineStage.HEALTH_ASSESSMENT,
                data={
                    "evaluation": evaluation.to_dict() if hasattr(evaluation, 'to_dict') else {},
                    "status": evaluation.overall_status.value,
                }
            )
            
        except Exception as e:
            return ObservationResult.failure_result(
                runtime_id=self._runtime_id,
                pipeline_stage=PipelineStage.HEALTH_ASSESSMENT,
                error_message=f"Health evaluation failed: {type(e).__name__}: {str(e)}"
            )
    
    async def _evaluate_integrity(
        self,
        domain_checks: Dict[IntegrityDomain, Callable[[str], Any]],
        timeout_seconds: float
    ) -> ObservationResult:
        """Execute integrity assessment stage."""
        try:
            # Execute integrity evaluation
            evaluation = await self._integrity_manager.evaluate(
                subject=self._runtime_id,
                domain_checks=domain_checks,
                timeout_seconds=timeout_seconds
            )
            
            return ObservationResult.success_result(
                runtime_id=self._runtime_id,
                pipeline_stage=PipelineStage.INTEGRITY_ASSESSMENT,
                data={
                    "evaluation": evaluation.to_dict() if hasattr(evaluation, 'to_dict') else {},
                    "status": evaluation.overall_status.value,
                }
            )
            
        except Exception as e:
            return ObservationResult.failure_result(
                runtime_id=self._runtime_id,
                pipeline_stage=PipelineStage.INTEGRITY_ASSESSMENT,
                error_message=f"Integrity evaluation failed: {type(e).__name__}: {str(e)}"
            )
    
    def _assess_capability(
        self,
        health_result: ObservationResult,
        integrity_result: ObservationResult
    ) -> ObservationResult:
        """Execute capability assessment stage."""
        # Determine overall status from health and integrity
        if not health_result.success or not integrity_result.success:
            return ObservationResult.failure_result(
                runtime_id=self._runtime_id,
                pipeline_stage=PipelineStage.CAPABILITY_ASSESSMENT,
                error_message="Cannot assess capability - underlying assessments failed"
            )
        
        # Extract statuses from results
        health_status = HealthStatus.UNKNOWN
        if "status" in health_result.data:
            try:
                health_status = HealthStatus(health_result.data["status"])
            except (ValueError, KeyError):
                pass
        
        integrity_status = IntegrityStatus.UNKNOWN
        if "status" in integrity_result.data:
            try:
                integrity_status = IntegrityStatus(integrity_result.data["status"])
            except (ValueError, KeyError):
                pass
        
        # Capability is determined by health and integrity
        # A system with degraded health but verified integrity may still have reduced capability
        can_handle_work = (
            health_status in (HealthStatus.HEALTHY,) and
            integrity_status == IntegrityStatus.VERIFIED
        )
        
        return ObservationResult.success_result(
            runtime_id=self._runtime_id,
            pipeline_stage=PipelineStage.CAPABILITY_ASSESSMENT,
            data={
                "health_status": health_status.value,
                "integrity_status": integrity_status.value,
                "can_handle_work": can_handle_work,
                "can_accept_admission": can_handle_work,
            }
        )
    
    async def _publish_truth(self) -> ObservationResult:
        """Execute runtime truth publication stage."""
        try:
            # Get latest health and integrity evaluations
            health_eval = self._health_manager.get_evaluation(self._runtime_id)
            integrity_eval = self._integrity_manager.get_evaluation(self._runtime_id)
            
            # Update runtime truth with current status
            if health_eval:
                self._truth.update_health(
                    subject=self._runtime_id,
                    status=health_eval.overall_status.value
                )
            
            if integrity_eval:
                self._truth.update_integrity(
                    subject=self._runtime_id, 
                    status=integrity_eval.overall_status.value
                )
            
            # Take truth snapshot and get sequence number from current_version
            version_num = self._truth.current_version.sequence_number
            snapshot = self._truth.take_snapshot()
            
            return ObservationResult.success_result(
                runtime_id=self._runtime_id,
                pipeline_stage=PipelineStage.RUNTIME_TRUTH,
                data={
                    "version": version_num,
                    "snapshot": snapshot.to_dict() if hasattr(snapshot, 'to_dict') else str(snapshot),
                    "overall_health": self._truth.overall_health_status,
                    "overall_integrity": self._truth.overall_integrity_status,
                }
            )
            
        except Exception as e:
            return ObservationResult.failure_result(
                runtime_id=self._runtime_id,
                pipeline_stage=PipelineStage.RUNTIME_TRUTH,
                error_message=f"Truth publication failed: {type(e).__name__}: {str(e)}"
            )
    
    def _generate_diagnostics(
        self,
        results: List[ObservationResult]
    ) -> ObservationResult:
        """Execute diagnostics generation stage."""
        # Count failures
        failure_count = sum(1 for r in results if not r.success)
        
        return ObservationResult.success_result(
            runtime_id=self._runtime_id,
            pipeline_stage=PipelineStage.DIAGNOSTICS,
            data={
                "total_stages": len(results),
                "successful_stages": sum(1 for r in results if r.success),
                "failed_stages": failure_count,
                "pipeline_results": [r.to_dict() if hasattr(r, 'to_dict') else str(r) for r in results],
            }
        )
    
    # -------------------------------------------------------------------------
    # Watchdog Operations
    # -------------------------------------------------------------------------
    
    def register_watchdog(
        self,
        name: str,
        check_interval_seconds: float = 10.0,
        timeout_seconds: float = 30.0,
        policy: WatchdogPolicy = WatchdogPolicy.ALERT
    ) -> None:
        """Register a watchdog with the coordinator."""
        config = WatchdogConfig.create(
            name=name,
            check_interval_seconds=check_interval_seconds,
            timeout_seconds=timeout_seconds,
            policy=policy
        )
        
        watchdog = Watchdog(config=config, runtime_id=self._runtime_id)
        self._watchdog_system.register_watchdog(watchdog)
    
    def any_watchdogs_triggered(self) -> bool:
        """Check if any watchdogs are currently triggered."""
        return self._watchdog_system.any_triggered()
    
    # -------------------------------------------------------------------------
    # Query Methods
    # -------------------------------------------------------------------------
    
    def get_truth_snapshot(self) -> Optional[Any]:
        """Get the latest runtime truth snapshot."""
        return self._truth.get_latest_snapshot()


# =============================================================================
# OBSERVATION PIPELINE RESULT
# =============================================================================


@dataclass(frozen=True)
class ObservationPipelineResult:
    """
    Result of a complete observation pipeline execution.
    
    Contains all stages' results and overall success/failure status.
    """
    
    # Identifiers
    result_id: str              # Unique identifier for this pipeline run
    
    # Context
    runtime_id: str             # Which runtime was observed
    
    # Pipeline info
    started_at_utc: float       # When pipeline started
    completed_at_utc: float     # When pipeline completed
    
    # Results by stage
    results: Tuple[ObservationResult, ...] = field(default_factory=tuple)
    
    @property
    def success(self) -> bool:
        """Check if all stages succeeded."""
        return all(r.success for r in self.results)
    
    @property
    def total_duration_seconds(self) -> float:
        """Get the total duration of pipeline execution."""
        return self.completed_at_utc - self.started_at_utc
    
    def get_result_by_stage(self, stage: PipelineStage) -> Optional[ObservationResult]:
        """Get result for a specific pipeline stage."""
        for r in self.results:
            if r.pipeline_stage == stage:
                return r
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            "result_id": self.result_id,
            "runtime_id": self.runtime_id,
            "started_at_utc": self.started_at_utc,
            "completed_at_utc": self.completed_at_utc,
            "total_duration_seconds": self.total_duration_seconds,
            "success": self.success,
            "results_by_stage": {
                r.pipeline_stage.value: r.to_dict() if hasattr(r, 'to_dict') else str(r)
                for r in self.results
            },
        }
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        results: List[ObservationResult],
        total_duration_seconds: float = 0.0
    ) -> "ObservationPipelineResult":
        """Create a pipeline result from stage results."""
        
        if not results:
            return cls(
                result_id=f"pipeline_result_{uuid.uuid4().hex[:12]}",
                runtime_id=runtime_id,
                started_at_utc=time.time(),
                completed_at_utc=time.time(),
                results=tuple()
            )
        
        return cls(
            result_id=f"pipeline_result_{uuid.uuid4().hex[:12]}",
            runtime_id=runtime_id,
            started_at_utc=min(r.started_at_utc for r in results),
            completed_at_utc=max(r.completed_at_utc for r in results),
            results=tuple(results)
        )


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Pipeline stages
    "PipelineStage",
    
    # Result types
    "ObservationResult",
    "ObservationPipelineResult",
    
    # Coordinator
    "RuntimeObservationCoordinator",
]