# Phase 3.11.13 - Stage Admission Implementation
# ==============================================
"""
Stage admission policies and evaluation logic.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import time

from . import (
    StageAdmissionId,
    StageInputSnapshot,
    InputSnapshotId,
    StageAdmissionContext,
    StageAdmissionResult,
    AdmissionDecision,
)


@dataclass
class StageAdmissionEvaluator:
    """
    Evaluator for stage admission decisions.
    
    Admission determines whether a stage may proceed with one selected input
    snapshot. This is distinct from stream admission (which determines if a
    record enters the stream) and activation admission (which determines if an
    activation may proceed).
    """
    
    # Configuration
    trust_threshold: float = 0.5
    max_input_records: int = 100
    require_all_streams: bool = True
    
    def evaluate_admission(
        self,
        snapshot: StageInputSnapshot,
        context: Optional[StageAdmissionContext] = None,
    ) -> StageAdmissionResult:
        """
        Evaluate whether the stage may proceed with the given input snapshot.
        
        Args:
            snapshot: The input selection result to evaluate
            context: Optional execution context (cycle state, resources)
            
        Returns:
            Admission decision with reason and optional conditions
        """
        admission_id = StageAdmissionId.generate()
        created_at = time.time()
        
        # Check basic requirements
        if not snapshot.selected_records:
            return StageAdmissionResult(
                admission_id=admission_id,
                stage_id=snapshot.stage_id,
                cycle_id=snapshot.cycle_id,
                decision=AdmissionDecision.WAIT,
                reason="No selected records available for stage consumption",
                input_snapshot_id=snapshot.snapshot_id.value,
                admitted_at_utc=created_at,
                wait_condition="awaiting_records_from_streams",
            )
        
        # Check record count bounds
        if len(snapshot.selected_records) > self.max_input_records:
            return StageAdmissionResult(
                admission_id=admission_id,
                stage_id=snapshot.stage_id,
                cycle_id=snapshot.cycle_id,
                decision=AdmissionDecision.REJECT,
                reason=f"Record count {len(snapshot.selected_records)} exceeds maximum {self.max_input_records}",
                input_snapshot_id=snapshot.snapshot_id.value,
                admitted_at_utc=created_at,
            )
        
        # Check stream count bounds if required
        stream_ids = snapshot.stream_ids
        if self.require_all_streams and len(stream_ids) < 1:
            return StageAdmissionResult(
                admission_id=admission_id,
                stage_id=snapshot.stage_id,
                cycle_id=snapshot.cycle_id,
                decision=AdmissionDecision.WAIT,
                reason="No streams have records available",
                input_snapshot_id=snapshot.snapshot_id.value,
                admitted_at_utc=created_at,
            )
        
        # Check resource availability if context provided
        if context:
            result = self._check_resource_availability(
                snapshot=snapshot,
                context=context,
            )
            if not result.is_admitted():
                return result
        
        # All checks passed - admit the stage
        return StageAdmissionResult(
            admission_id=admission_id,
            stage_id=snapshot.stage_id,
            cycle_id=snapshot.cycle_id,
            decision=AdmissionDecision.ADMIT,
            reason="Stage input is valid and resources available",
            input_snapshot_id=snapshot.snapshot_id.value,
            admitted_at_utc=created_at,
        )
    
    def _check_resource_availability(
        self,
        snapshot: StageInputSnapshot,
        context: StageAdmissionContext,
    ) -> StageAdmissionResult:
        """Check if required resources are available for stage execution."""
        # Check network availability
        if context.network_availability is not None:
            # If specific networks are required and none are available, wait
            pass  # Network-specific admission handled by activation phase
        
        # Check capability availability
        if context.capability_availability is not None:
            # Capabilities will be checked during activation planning
            pass
        
        return StageAdmissionResult(
            admission_id=StageAdmissionId.generate(),
            stage_id=snapshot.stage_id,
            cycle_id=snapshot.cycle_id,
            decision=AdmissionDecision.ADMIT,
            reason="Resources available",
            input_snapshot_id=snapshot.snapshot_id.value,
            admitted_at_utc=time.time(),
        )
    
    def evaluate_degraded_admission(
        self,
        snapshot: StageInputSnapshot,
        context: Optional[StageAdmissionContext] = None,
    ) -> StageAdmissionResult:
        """
        Evaluate whether the stage may proceed in degraded mode.
        
        Degraded admission occurs when some optional resources are unavailable
        but the stage can still make progress with available inputs.
        """
        admission_id = StageAdmissionId.generate()
        
        # Check if we have at least minimum required records
        if not snapshot.selected_records:
            return StageAdmissionResult(
                admission_id=admission_id,
                stage_id=snapshot.stage_id,
                cycle_id=snapshot.cycle_id,
                decision=AdmissionDecision.SKIP,
                reason="No records available even for degraded mode",
                input_snapshot_id=snapshot.snapshot_id.value,
                admitted_at_utc=time.time(),
            )
        
        # Determine what's missing
        degradation_details = {}
        
        if context and context.network_availability:
            unavailable_networks = [
                n for n, available in context.network_availability.items()
                if not available
            ]
            if unavailable_networks:
                degradation_details["unavailable_networks"] = unavailable_networks
        
        return StageAdmissionResult(
            admission_id=admission_id,
            stage_id=snapshot.stage_id,
            cycle_id=snapshot.cycle_id,
            decision=AdmissionDecision.ADMIT_DEGRADED,
            reason="Stage admitted in degraded mode with partial resources",
            input_snapshot_id=snapshot.snapshot_id.value,
            admitted_at_utc=time.time(),
            degradation_details=degradation_details,
        )


@dataclass
class AdmissionPolicy:
    """
    Policy configuration for stage admission.
    
    This is a configuration object, not executable logic. It defines
    constraints that the evaluator enforces.
    """
    
    # Resource bounds
    max_input_records: int = 100
    min_required_streams: int = 1
    optional_streams_allowed: bool = True
    
    # Quality thresholds
    trust_threshold: float = 0.5
    freshness_window_seconds: float = 30.0
    
    # Policy behavior
    fail_on_missing_optional: bool = False  # If False, admit in degraded mode
    require_all_streams: bool = False
    
    def to_evaluator(self) -> StageAdmissionEvaluator:
        """Create an evaluator from this policy."""
        return StageAdmissionEvaluator(
            trust_threshold=self.trust_threshold,
            max_input_records=self.max_input_records,
            require_all_streams=self.require_all_streams,
        )


# =============================================================================
# Multi-Layer Admission
# =============================================================================


@dataclass
class LayeredAdmissionResult:
    """
    Result of multi-layer admission evaluation.
    
    Each layer (stream, stage, activation) has its own admission decision.
    This result tracks all layers together for a complete picture.
    """
    
    stream_admission: Optional[bool] = None  # Does record pass stream admission?
    stream_reason: str = ""
    
    stage_admission: bool = False  # Does snapshot pass stage admission?
    stage_reason: str = ""
    
    activation_admission: bool = False  # Can activation proceed?
    activation_reason: str = ""
    
    overall_decision: AdmissionDecision = AdmissionDecision.WAIT
    
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_fully_admitted(self) -> bool:
        """Check if all admission layers passed."""
        return (
            self.stream_admission is not False and  # None or True means ok
            self.stage_admission and
            self.activation_admission
        )


# =============================================================================
# Admission State Machine
# =============================================================================


class AdmissionTransition(Enum):
    """Transitions in the admission state machine."""
    REQUESTED = "requested"
    EVALUATING = "evaluating"
    STREAM_ADMITTED = "stream_admitted"
    STAGE_ADMITTED = "stage_admitted"
    ADMISSION_GRANTED = "admission_granted"
    WAITING = "waiting"
    REJECTED = "rejected"


class AdmissionState(Enum):
    """States in the admission state machine."""
    INITIAL = "initial"           # Request received, not yet evaluated
    STREAM_CHECK = "stream_check"  # Evaluating stream-level admission
    STAGE_CHECK = "stage_check"   # Evaluating stage-level admission
    ACTIVE = "active"             # Fully admitted and active
    WAITING = "waiting"           # Waiting for more inputs/resources
    REJECTED = "rejected"         # Admission rejected