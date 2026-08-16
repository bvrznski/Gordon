# Perception Integration Result - Phase 5.2.3
# ===========================================

"""
Integration Result: The outcome of an integration request.

A PerceptionIntegrationResult represents what was actually produced by integration,
distinguishing between success, failure, and various degradation modes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# INTEGRATION STATUS - Where is the integration in its lifecycle?
# =============================================================================


class IntegrationStatus(Enum):
    """
    Status of an integration operation.
    
    States:
        REQUESTED:      Request submitted, not yet validated
        COLLECTING:     Collecting eligible source artifacts
        ALIGNMENT_VALIDATED: Reference system alignment verified
        CORRESPONDENCE_EVALUATING: Evaluating intermodal correspondences
        TEMPORAL_BINDING: Binding artifacts in time
        SPATIAL_BINDING: Binding artifacts in space
        FUSING:         Constructing integrated artifacts
        PARTIAL:        Completed with partial results
        AMBIGUOUS:      Multiple plausible structures remain
        CONFLICTED:     Conflicting evidence detected
        COMPLETED:      Integration completed successfully
        REJECTED:       Request rejected before integration
        FAILED:         Integration failed before completion
        SUSPENDED:      Paused, awaiting intervention
    """
    
    REQUESTED = "requested"
    COLLECTING = "collecting"
    ALIGNMENT_VALIDATED = "alignment_validated"
    CORRESPONDENCE_EVALUATING = "correspondence_evaluating"
    TEMPORAL_BINDING = "temporal_binding"
    SPATIAL_BINDING = "spatial_binding"
    FUSING = "fusing"
    PARTIAL = "partial"
    AMBIGUOUS = "ambiguous"
    CONFLICTED = "conflicted"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"
    SUSPENDED = "suspended"


# =============================================================================
# INTEGRATION OUTCOME - What was the final result?
# =============================================================================


class IntegrationOutcome(Enum):
    """
    Outcome category for integration.
    
    Outcomes:
        SUCCESS:         All stages completed successfully
        PARTIAL:         Some stages completed, others failed
        AMBIGUOUS:       Multiple materially plausible structures remain
        CONFLICTED:      Conflicting evidence detected, no fusion
        REJECTED:        Request rejected before integration
        FAILED:          Integration failed before completion
    """
    
    SUCCESS = "success"
    PARTIAL = "partial"
    AMBIGUOUS = "ambiguous"
    CONFLICTED = "conflicted"
    REJECTED = "rejected"
    FAILED = "failed"


# =============================================================================
# CORRESPONDENCE RECORD - What correspondences were found?
# =============================================================================


@dataclass(frozen=True)
class CorrespondenceRecord:
    """
    Record of an intermodal correspondence evaluation.
    
    Fields:
        correspondence_identity: Unique identifier
        participating_artifact_ids: Which artifacts correspond?
        correspondence_kind: What kind of correspondence?
        supporting_evidence: Evidence for the correspondence
        conflicting_evidence: Evidence against the correspondence
        temporal_compatibility: How compatible in time?
        spatial_compatibility: How compatible in space?
        confidence: Confidence in this correspondence
        alternatives: Alternative correspondences considered
    """
    
    correspondence_identity: str
    participating_artifact_ids: Tuple[str, ...]
    correspondence_kind: str  # e.g., "same_entity_candidate"
    
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    conflicting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    
    temporal_compatibility: float = 1.0   # 0.0-1.0
    spatial_compatibility: float = 1.0    # 0.0-1.0
    
    confidence: float = 1.0               # 0.0-1.0
    alternatives: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# BINDING RECORD - What bindings were created?
# =============================================================================


@dataclass(frozen=True)
class BindingRecord:
    """
    Record of a temporal or spatial binding.
    
    Fields:
        binding_identity: Unique identifier
        bound_artifact_ids: Which artifacts are bound together?
        binding_window: Temporal/spatial window for the binding
        confidence: Confidence in this binding
        alternatives: Alternative bindings considered
    """
    
    binding_identity: str
    bound_artifact_ids: Tuple[str, ...]
    binding_window: Dict[str, Any]  # time range or spatial region
    
    confidence: float = 1.0     # 0.0-1.0
    alternatives: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# FUSION RECORD - What fusion was performed?
# =============================================================================


@dataclass(frozen=True)
class FusionRecord:
    """
    Record of a fusion operation.
    
    Fields:
        fusion_identity: Unique identifier
        source_artifact_ids: Which artifacts were fused?
        fusion_strategy: Strategy used for fusion
        integrated_fields: Which fields were integrated?
        preserved_conflicts: Conflicts that remain unresolved
        confidence: Confidence in the fused artifact
    """
    
    fusion_identity: str
    source_artifact_ids: Tuple[str, ...]
    fusion_strategy: str  # e.g., "complementary", "corroborative"
    
    integrated_fields: Tuple[str, ...] = field(default_factory=tuple)
    preserved_conflicts: Tuple[str, ...] = field(default_factory=tuple)
    
    confidence: float = 1.0     # 0.0-1.0
    
    provenance: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# PERCEPTION INTEGRATION RESULT - Output of an integration operation
# =============================================================================


@dataclass(frozen=True)
class PerceptionIntegrationResult:
    """
    Result of a perception integration operation.
    
    Fields:
        request_reference:     Reference to the original request
        integrated_artifacts:  Integrated artifacts produced (references only)
        correspondence_records: Records of all correspondences evaluated
        binding_records:       Records of all bindings created
        fusion_records:        Records of all fusion operations
        preserved_conflicts:   Conflicts that remain unresolved
        confidence:            Overall integration confidence
        uncertainty:           Known limitations
        limitations:           Known limitations of this result
        diagnostics:           Diagnostic information for debugging
        status:                Execution status
        outcome:               Outcome category
    """
    
    request_reference: str                 # Reference to original request
    
    integrated_artifacts: Tuple[str, ...] = field(default_factory=tuple)  # Artifact IDs
    
    correspondence_records: Tuple[CorrespondenceRecord, ...] = field(default_factory=tuple)
    binding_records: Tuple[BindingRecord, ...] = field(default_factory=tuple)
    fusion_records: Tuple[FusionRecord, ...] = field(default_factory=tuple)
    
    preserved_conflicts: Tuple[str, ...] = field(default_factory=tuple)  # Conflict descriptions
    
    confidence: float = 1.0     # 0.0-1.0
    uncertainty: float = 0.0    # 0.0-1.0 known limitations
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    diagnostics: Dict[str, Any] = field(default_factory=dict)  # Timing, stage results, etc.
    
    status: IntegrationStatus = IntegrationStatus.REQUESTED
    outcome: IntegrationOutcome = IntegrationOutcome.PARTIAL
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_success(self) -> bool:
        """Check if integration completed successfully."""
        return self.status == IntegrationStatus.COMPLETED and self.outcome == IntegrationOutcome.SUCCESS
    
    @property
    def is_partial(self) -> bool:
        """Check if integration was partial."""
        return self.outcome == IntegrationOutcome.PARTIAL or self.status == IntegrationStatus.PARTIAL
    
    @property
    def is_ambiguous(self) -> bool:
        """Check if integration result is ambiguous."""
        return self.outcome == IntegrationOutcome.AMBIGUOUS or self.status == IntegrationStatus.AMBIGUOUS
    
    @property
    def is_conflicted(self) -> bool:
        """Check if conflicting evidence was detected."""
        return self.outcome == IntegrationOutcome.CONFLICTED or self.status == IntegrationStatus.CONFLICTED
    
    @property
    def is_failure(self) -> bool:
        """Check if integration failed."""
        return self.status in (IntegrationStatus.FAILED, IntegrationStatus.REJECTED)
    
    @classmethod
    def success(
        cls,
        request_reference: str,
        integrated_artifact_ids: Tuple[str, ...],
        correspondence_records: Optional[Tuple[CorrespondenceRecord, ...]] = None,
        binding_records: Optional[Tuple[BindingRecord, ...]] = None,
        fusion_records: Optional[Tuple[FusionRecord, ...]] = None,
    ) -> "PerceptionIntegrationResult":
        """
        Create a successful integration result.
        
        Args:
            request_reference: Reference to original request
            integrated_artifact_ids: IDs of integrated artifacts produced
            correspondence_records: Correspondence evaluation records (optional)
            binding_records: Binding records (optional)
            fusion_records: Fusion operation records (optional)
            
        Returns:
            New successful PerceptionIntegrationResult
        """
        return cls(
            request_reference=request_reference,
            integrated_artifacts=integrated_artifact_ids,
            correspondence_records=correspondence_records or tuple(),
            binding_records=binding_records or tuple(),
            fusion_records=fusion_records or tuple(),
            confidence=1.0,
            uncertainty=0.0,
            findings=("Integration completed successfully",),
            status=IntegrationStatus.COMPLETED,
            outcome=IntegrationOutcome.SUCCESS,
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
                "status": IntegrationStatus.COMPLETED.value,
            },
        )
    
    @classmethod
    def partial(
        cls,
        request_reference: str,
        integrated_artifact_ids: Tuple[str, ...],
        missing_artifact_count: int,
        limitations: Tuple[str, ...],
    ) -> "PerceptionIntegrationResult":
        """
        Create a partial integration result.
        
        Args:
            request_reference: Reference to original request
            integrated_artifact_ids: IDs of successfully integrated artifacts
            missing_artifact_count: Number of artifacts that could not be integrated
            limitations: Known limitations of this result
            
        Returns:
            New partial PerceptionIntegrationResult
        """
        return cls(
            request_reference=request_reference,
            integrated_artifacts=integrated_artifact_ids,
            confidence=0.5,  # Reduced for partial results
            uncertainty=0.3,  # Increased due to missing evidence
            limitations=limitations,
            diagnostics={
                "missing_evidence_count": missing_artifact_count,
                "partial_reasons": [str(l) for l in limitations],
            },
            status=IntegrationStatus.PARTIAL,
            outcome=IntegrationOutcome.PARTIAL,
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
                "status": IntegrationStatus.PARTIAL.value,
            },
        )
    
    @classmethod
    def ambiguous(
        cls,
        request_reference: str,
        integrated_artifact_ids: Tuple[str, ...],
        plausible_structures: int,
        alternatives: Tuple[str, ...],
    ) -> "PerceptionIntegrationResult":
        """
        Create an ambiguous integration result.
        
        Args:
            request_reference: Reference to original request
            integrated_artifact_ids: IDs of artifacts that could be integrated
            plausible_structures: Number of materially plausible alternative structures
            alternatives: Descriptions of alternative interpretations
            
        Returns:
            New ambiguous PerceptionIntegrationResult
        """
        return cls(
            request_reference=request_reference,
            integrated_artifacts=integrated_artifact_ids,
            confidence=0.3,  # Lower due to ambiguity
            uncertainty=0.5,  # Higher due to multiple possibilities
            diagnostics={
                "plausible_structures": plausible_structures,
                "alternative_interpretations": list(alternatives),
            },
            status=IntegrationStatus.AMBIGUOUS,
            outcome=IntegrationOutcome.AMBIGUOUS,
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
                "status": IntegrationStatus.AMBIGUOUS.value,
            },
        )
    
    @classmethod
    def failed(
        cls,
        request_reference: str,
        failure_message: str,
        affected_stages: Optional[Tuple[str, ...]] = None,
    ) -> "PerceptionIntegrationResult":
        """
        Create a failed integration result.
        
        Args:
            request_reference: Reference to original request
            failure_message: Description of what went wrong
            affected_stages: Which stages were affected (optional)
            
        Returns:
            New failed PerceptionIntegrationResult
        """
        return cls(
            request_reference=request_reference,
            findings=(failure_message,),
            limitations=(f"Stage(s) {' '.join(affected_stages or [])} failed",),
            diagnostics={
                "failure": failure_message,
                "failed_stages": list(affected_stages or []),
            },
            status=IntegrationStatus.FAILED,
            outcome=IntegrationOutcome.FAILED,
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
                "status": IntegrationStatus.FAILED.value,
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "request_reference": self.request_reference,
            "integrated_artifacts_count": len(self.integrated_artifacts),
            "correspondence_records_count": len(self.correspondence_records),
            "binding_records_count": len(self.binding_records),
            "fusion_records_count": len(self.fusion_records),
            "preserved_conflicts": list(self.preserved_conflicts),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "limitations": list(self.limitations),
            "diagnostics": dict(self.diagnostics),
            "status": self.status.value,
            "outcome": self.outcome.value,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptionIntegrationResult":
        """Create result from dictionary."""
        return cls(
            request_reference=data.get("request_reference", ""),
            integrated_artifacts=tuple(data.get("integrated_artifacts", [])),
            status=IntegrationStatus(data.get("status", "requested")),
            outcome=IntegrationOutcome(data.get("outcome", "partial")),
        )