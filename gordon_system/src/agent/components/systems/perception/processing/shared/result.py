# Perception Processing Result - Phase 5.2.2
# ===========================================

"""
Processing Result: The outcome of a processing request.

A ProcessingResult represents what was actually produced by processing,
distinguishing between success, failure, and various degradation modes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# PROCESSING STATUS - Where is the processing in its lifecycle?
# =============================================================================


class ProcessingStatus(Enum):
    """
    Status of a processing operation.
    
    States:
        REQUESTED:     Request submitted, not yet validated
        VALIDATING:    Validating input and configuration
        READY:         Ready to execute
        PROCESSING:    Actively executing stages
        DEGRADED:      Executing with reduced capabilities
        COMPLETED:     All stages completed successfully
        REJECTED:      Input rejected before processing
        FAILED:        Processing failed before completion
        SUSPENDED:     Paused, awaiting intervention
    """
    
    REQUESTED = "requested"
    VALIDATING = "validating"
    READY = "ready"
    PROCESSING = "processing"
    DEGRADED = "degraded"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"
    SUSPENDED = "suspended"


# =============================================================================
# PROCESSING OUTCOME - What was the final result?
# =============================================================================


class ProcessingOutcome(Enum):
    """
    Outcome category for processing.
    
    Outcomes:
        SUCCESS:         All stages completed successfully
        DEGRADED:        Completed with reduced capabilities
        PARTIAL:         Some stages completed, others failed
        REJECTED:        Input was rejected before processing
        FAILED:          Processing failed before completion
    """
    
    SUCCESS = "success"
    DEGRADED = "degraded"
    PARTIAL = "partial"
    REJECTED = "rejected"
    FAILED = "failed"


# =============================================================================
# PROCESSING RESULT - Output of a processing operation
# =============================================================================


@dataclass(frozen=True)
class PerceptionProcessingResult:
    """
    Result of a perception processing operation.
    
    Fields:
        request_reference:     Reference to the original request
        output_artifacts:      Processed artifacts produced
        applied_stages:        Which stages were executed
        transformation_records: Records of all transformations applied
        confidence_effects:    Summary of confidence changes
        uncertainty_effects:   Summary of uncertainty changes
        information_loss:      Summarized information loss
        findings:              Processing observations
        limitations:           Known limitations of this result
        diagnostics:           Diagnostic information for debugging
        status:                Execution status
        outcome:               Outcome category
    """
    
    request_reference: str                 # Reference to original request
    
    output_artifacts: Tuple[Any, ...] = field(default_factory=tuple)  # Processed artifacts
    
    applied_stages: Tuple[str, ...] = field(default_factory=tuple)
    
    transformation_records: Tuple["ProcessingTransformationRecord", ...] = field(default_factory=tuple)
    
    confidence_effects: Tuple[str, ...] = field(default_factory=tuple)  # Effect descriptions
    uncertainty_effects: Tuple[str, ...] = field(default_factory=tuple)
    
    information_loss: Optional["ProcessingInformationLoss"] = None  # aggregate loss
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    diagnostics: Dict[str, Any] = field(default_factory=dict)  # Timing, stage results, etc.
    
    status: ProcessingStatus = ProcessingStatus.REQUESTED
    outcome: ProcessingOutcome = ProcessingOutcome.PARTIAL
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_success(self) -> bool:
        """Check if processing completed successfully."""
        return self.status == ProcessingStatus.COMPLETED and self.outcome == ProcessingOutcome.SUCCESS
    
    @property
    def is_degraded(self) -> bool:
        """Check if processing was degraded."""
        return self.status in (ProcessingStatus.COMPLETED, ProcessingStatus.DEGRADED) and self.outcome == ProcessingOutcome.DEGRADED
    
    @property
    def is_failure(self) -> bool:
        """Check if processing failed."""
        return self.status in (ProcessingStatus.FAILED, ProcessingStatus.REJECTED)
    
    @classmethod
    def success(
        cls,
        request_reference: str,
        output_artifacts: Tuple[Any, ...],
        applied_stages: Tuple[str, ...],
        transformation_records: Optional[Tuple["ProcessingTransformationRecord", ...]] = None,
        confidence_effects: Optional[Tuple[str, ...]] = None,
        uncertainty_effects: Optional[Tuple[str, ...]] = None,
        information_loss: Optional["ProcessingInformationLoss"] = None,  # noqa
    ) -> "PerceptionProcessingResult":
        """
        Create a successful processing result.
        
        Args:
            request_reference: Reference to original request
            output_artifacts: Processed artifacts produced
            applied_stages: Which stages executed
            transformation_records: Transformation trace (optional)
            confidence_effects: Confidence change descriptions (optional)
            uncertainty_effects: Uncertainty change descriptions (optional)
            information_loss: Aggregate information loss (optional)
            
        Returns:
            New successful PerceptionProcessingResult
        """
        return cls(
            request_reference=request_reference,
            output_artifacts=output_artifacts,
            applied_stages=applied_stages,
            transformation_records=transformation_records or tuple(),
            confidence_effects=confidence_effects or tuple(),
            uncertainty_effects=uncertainty_effects or tuple(),
            information_loss=information_loss,
            findings=("Processing completed successfully",),
            limitations=(),
            diagnostics={},
            status=ProcessingStatus.COMPLETED,
            outcome=ProcessingOutcome.SUCCESS,
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
                "status": ProcessingStatus.COMPLETED.value,
            },
        )
    
    @classmethod
    def degraded(
        cls,
        request_reference: str,
        output_artifacts: Tuple[Any, ...],
        applied_stages: Tuple[str, ...],
        limitations: Tuple[str, ...],
        transformation_records: Optional[Tuple["ProcessingTransformationRecord", ...]] = None,
    ) -> "PerceptionProcessingResult":
        """
        Create a degraded processing result.
        
        Args:
            request_reference: Reference to original request
            output_artifacts: Processed artifacts produced
            applied_stages: Which stages executed
            limitations: Known limitations of this result
            transformation_records: Transformation trace (optional)
            
        Returns:
            New degraded PerceptionProcessingResult
        """
        return cls(
            request_reference=request_reference,
            output_artifacts=output_artifacts,
            applied_stages=applied_stages,
            transformation_records=transformation_records or tuple(),
            findings=("Processing completed with limitations",),
            limitations=limitations,
            diagnostics={
                "degradation_reasons": [str(l) for l in limitations],
            },
            status=ProcessingStatus.COMPLETED,
            outcome=ProcessingOutcome.DEGRADED,
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
                "status": ProcessingStatus.DEGRADED.value,
            },
        )
    
    @classmethod
    def failed(
        cls,
        request_reference: str,
        failure_message: str,
        affected_stages: Optional[Tuple[str, ...]] = None,
    ) -> "PerceptionProcessingResult":
        """
        Create a failed processing result.
        
        Args:
            request_reference: Reference to original request
            failure_message: Description of what went wrong
            affected_stages: Which stages were affected (optional)
            
        Returns:
            New failed PerceptionProcessingResult
        """
        return cls(
            request_reference=request_reference,
            findings=(failure_message,),
            limitations=(f"Stage(s) {' '.join(affected_stages or [])} failed",),
            diagnostics={
                "failure": failure_message,
                "failed_stages": list(affected_stages or []),
            },
            status=ProcessingStatus.FAILED,
            outcome=ProcessingOutcome.FAILED,
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
                "status": ProcessingStatus.FAILED.value,
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "request_reference": self.request_reference,
            "output_artifacts_count": len(self.output_artifacts),
            "applied_stages": list(self.applied_stages),
            "transformation_records_count": len(self.transformation_records),
            "confidence_effects": list(self.confidence_effects),
            "uncertainty_effects": list(self.uncertainty_effects),
            "information_loss": self.information_loss.to_dict() if self.information_loss else None,
            "findings": list(self.findings),
            "limitations": list(self.limitations),
            "diagnostics": dict(self.diagnostics),
            "status": self.status.value,
            "outcome": self.outcome.value,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptionProcessingResult":
        """Create result from dictionary."""
        return cls(
            request_reference=data.get("request_reference", ""),
            output_artifacts=tuple(data.get("output_artifacts", [])),
            applied_stages=tuple(data.get("applied_stages", [])),
            transformation_records=tuple(),
            status=ProcessingStatus(data.get("status", "requested")),
            outcome=ProcessingOutcome(data.get("outcome", "partial")),
        )
